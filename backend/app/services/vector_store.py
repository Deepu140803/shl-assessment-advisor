"""
Vector Store Service
====================
Handles semantic search over the SHL catalog using FAISS or ChromaDB.
Supports embedding generation, top-k retrieval, and reranking.
"""

import json
import os
import numpy as np
from pathlib import Path
from typing import Optional
from app.core.config import settings
from app.core.logging import get_logger
from app.models.schemas import CatalogEntry

log = get_logger(__name__)


class VectorStoreService:
    """
    Manages vector search over the SHL assessment catalog.
    Lazy-loads the index on first query.
    """

    def __init__(self):
        self._index = None          # FAISS index or Chroma collection
        self._catalog: list[dict] = []
        self._texts: list[str] = []
        self._embed_fn = None       # Callable: list[str] → list[list[float]]
        self._initialized = False

    # ─── Initialization ───────────────────────────────────────────────────────

    def initialize(self) -> None:
        """Load catalog, build embedding function, and load vector index."""
        if self._initialized:
            return

        log.info("Initializing vector store service...")

        # 1. Load embedding function
        self._embed_fn = self._build_embed_fn()

        # 2. Load or build vector index
        if settings.vector_db == "chroma":
            self._load_chroma()
        else:
            self._load_faiss()

        self._initialized = True
        log.info(f"Vector store ready. {len(self._catalog)} assessments indexed.")

    def _build_embed_fn(self):
        """Build embedding callable based on settings."""
        if settings.embedding_provider == "openai" and settings.openai_api_key:
            from openai import OpenAI
            client = OpenAI(api_key=settings.openai_api_key)
            model = settings.embedding_model

            def openai_embed(texts: list[str]) -> list[list[float]]:
                response = client.embeddings.create(model=model, input=texts)
                return [e.embedding for e in response.data]

            log.info(f"Using OpenAI embeddings: {model}")
            return openai_embed
        else:
            # Local fallback using sentence-transformers
            try:
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer("all-MiniLM-L6-v2")
                log.info("Using local SentenceTransformer: all-MiniLM-L6-v2")

                def local_embed(texts: list[str]) -> list[list[float]]:
                    return model.encode(texts, convert_to_numpy=True).tolist()

                return local_embed
            except ImportError:
                log.error("No embedding provider available. Install sentence-transformers or set OPENAI_API_KEY.")
                raise RuntimeError("No embedding provider configured")

    def _load_faiss(self) -> None:
        """Load FAISS index and catalog from disk."""
        try:
            import faiss
        except ImportError:
            log.error("faiss-cpu not installed")
            raise

        index_dir = Path(settings.faiss_index_path)
        index_file = index_dir / "index.faiss"
        catalog_file = index_dir / "catalog.json"
        texts_file = index_dir / "texts.json"

        if not index_file.exists():
            log.warning(f"FAISS index not found at {index_file}. Building from catalog...")
            self._build_faiss_from_catalog()
            return

        self._index = faiss.read_index(str(index_file))
        with open(catalog_file, "r", encoding="utf-8") as f:
            self._catalog = json.load(f)
        with open(texts_file, "r", encoding="utf-8") as f:
            self._texts = json.load(f)

        log.info(f"FAISS index loaded: {self._index.ntotal} vectors")

    def _build_faiss_from_catalog(self) -> None:
        """Build FAISS index directly from catalog JSON (no pre-built index)."""
        import faiss

        catalog_path = Path(settings.catalog_json_path)
        if not catalog_path.exists():
            log.warning("Catalog JSON not found, using built-in fallback catalog")
            self._catalog = self._get_fallback_catalog()
        else:
            with open(catalog_path, "r", encoding="utf-8") as f:
                self._catalog = json.load(f)

        self._texts = [self._to_embedding_text(item) for item in self._catalog]

        log.info(f"Building FAISS index for {len(self._catalog)} assessments...")
        embeddings = self._embed_fn(self._texts)
        arr = np.array(embeddings, dtype=np.float32)

        # Normalize
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        arr = arr / (norms + 1e-9)

        dim = arr.shape[1]
        self._index = faiss.IndexFlatIP(dim)
        self._index.add(arr)

        # Persist
        index_dir = Path(settings.faiss_index_path)
        index_dir.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(index_dir / "index.faiss"))
        with open(index_dir / "catalog.json", "w") as f:
            json.dump(self._catalog, f, indent=2)
        with open(index_dir / "texts.json", "w") as f:
            json.dump(self._texts, f, indent=2)

        log.info("FAISS index built and saved.")

    def _load_chroma(self) -> None:
        """Load ChromaDB collection."""
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
        except ImportError:
            log.error("chromadb not installed")
            raise

        client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False)
        )

        try:
            self._index = client.get_collection("shl_assessments")
            log.info(f"ChromaDB loaded: {self._index.count()} entries")

            # Load catalog for metadata
            catalog_path = Path(settings.catalog_json_path)
            if catalog_path.exists():
                with open(catalog_path) as f:
                    self._catalog = json.load(f)
        except Exception as e:
            log.error(f"ChromaDB collection not found: {e}. Run generate_embeddings.py first.")
            raise

    # ─── Search ───────────────────────────────────────────────────────────────

    def search(self, query: str, top_k: Optional[int] = None) -> list[dict]:
        """
        Semantic search over the catalog.
        Returns list of catalog entries with 'score' field.
        """
        if not self._initialized:
            self.initialize()

        k = top_k or settings.top_k_retrieval
        query_embed = self._embed_fn([query])[0]

        if settings.vector_db == "chroma":
            return self._search_chroma(query_embed, k)
        else:
            return self._search_faiss(query_embed, k)

    def _search_faiss(self, query_embed: list[float], k: int) -> list[dict]:
        """Search FAISS index."""
        query_arr = np.array([query_embed], dtype=np.float32)
        norm = np.linalg.norm(query_arr)
        query_arr = query_arr / (norm + 1e-9)

        scores, indices = self._index.search(query_arr, min(k, len(self._catalog)))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self._catalog):
                continue
            entry = dict(self._catalog[idx])
            entry["score"] = float(score)
            results.append(entry)

        return results

    def _search_chroma(self, query_embed: list[float], k: int) -> list[dict]:
        """Search ChromaDB collection."""
        result = self._index.query(
            query_embeddings=[query_embed],
            n_results=min(k, self._index.count()),
            include=["documents", "metadatas", "distances"],
        )

        results = []
        for doc, meta, dist in zip(
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        ):
            entry = dict(meta)
            entry["description"] = doc
            entry["score"] = 1.0 - dist  # Convert distance to similarity
            results.append(entry)

        return results

    def rerank(self, results: list[dict], query: str) -> list[dict]:
        """
        Simple reranking: boost results where query terms appear in name/skills.
        Returns top RERANK_TOP_K results.
        """
        query_lower = query.lower()
        query_terms = set(query_lower.split())

        for r in results:
            boost = 0.0
            name_lower = r.get("name", "").lower()
            skills = " ".join(r.get("skills_measured", [])).lower()
            desc = r.get("description", "").lower()

            # Exact name match bonus
            for term in query_terms:
                if term in name_lower:
                    boost += 0.15
                if term in skills:
                    boost += 0.08
                if term in desc:
                    boost += 0.03

            r["rerank_score"] = r.get("score", 0.5) + boost

        # Sort by rerank score
        results.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
        return results[: settings.rerank_top_k]

    # ─── Utilities ────────────────────────────────────────────────────────────

    def get_all(self) -> list[dict]:
        """Return all catalog entries."""
        if not self._initialized:
            self.initialize()
        return self._catalog

    @staticmethod
    def _to_embedding_text(item: dict) -> str:
        """Build embedding text from a catalog item dict."""
        skills = ", ".join(item.get("skills_measured", []))
        return (
            f"Assessment: {item['name']}\n"
            f"Category: {item.get('category', 'General')}\n"
            f"Test Type: {item.get('test_type_full', item.get('test_type', 'K'))}\n"
            f"Description: {item.get('description', '')}\n"
            f"Skills Measured: {skills}\n"
            f"Duration: {item.get('duration', 'Not specified')}"
        )

    @staticmethod
    def _get_fallback_catalog() -> list[dict]:
        """Minimal fallback catalog when no JSON exists."""
        fallback_path = Path(__file__).parent.parent.parent / "data" / "shl_catalog.json"
        if fallback_path.exists():
            with open(fallback_path) as f:
                return json.load(f)
        return []


# Singleton
vector_store = VectorStoreService()
