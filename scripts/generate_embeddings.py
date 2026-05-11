"""
Embedding Pipeline
==================
Generates embeddings for the SHL catalog and stores them in FAISS or ChromaDB.

Usage:
    python scripts/generate_embeddings.py
"""

import json
import sys
import os
import logging
from pathlib import Path
import numpy as np

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def load_catalog(json_path: str) -> list[dict]:
    """Load catalog from JSON file."""
    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"Catalog not found at {json_path}. Run scrape_catalog.py first.")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    log.info(f"Loaded {len(data)} assessments from {json_path}")
    return data


def catalog_to_texts(catalog: list[dict]) -> list[str]:
    """Convert catalog entries to rich text for embedding."""
    texts = []
    for item in catalog:
        skills = ", ".join(item.get("skills_measured", []))
        text = (
            f"Assessment: {item['name']}\n"
            f"Category: {item.get('category', 'General')}\n"
            f"Test Type: {item.get('test_type_full', item.get('test_type', 'K'))}\n"
            f"Description: {item.get('description', '')}\n"
            f"Skills Measured: {skills}\n"
            f"Duration: {item.get('duration', 'Not specified')}"
        )
        texts.append(text)
    return texts


def build_faiss_index(texts: list[str], catalog: list[dict], output_dir: str, embedding_fn):
    """Build and save a FAISS index."""
    try:
        import faiss
    except ImportError:
        log.error("faiss-cpu not installed. Run: pip install faiss-cpu")
        raise

    log.info(f"Generating embeddings for {len(texts)} assessments...")
    embeddings = embedding_fn(texts)
    embeddings_array = np.array(embeddings, dtype=np.float32)

    # Normalize for cosine similarity
    norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
    embeddings_array = embeddings_array / (norms + 1e-9)

    # Create FAISS index (Inner Product = cosine similarity after normalization)
    dim = embeddings_array.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings_array)

    # Save
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(output_path / "index.faiss"))

    # Save catalog alongside index for retrieval
    with open(output_path / "catalog.json", "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    with open(output_path / "texts.json", "w", encoding="utf-8") as f:
        json.dump(texts, f, indent=2, ensure_ascii=False)

    log.info(f"FAISS index saved to {output_path}/index.faiss")
    log.info(f"Index contains {index.ntotal} vectors of dimension {dim}")


def build_chroma_index(texts: list[str], catalog: list[dict], persist_dir: str, embedding_fn):
    """Build and save a ChromaDB index."""
    try:
        import chromadb
        from chromadb.config import Settings as ChromaSettings
    except ImportError:
        log.error("chromadb not installed. Run: pip install chromadb")
        raise

    client = chromadb.PersistentClient(
        path=persist_dir,
        settings=ChromaSettings(anonymized_telemetry=False)
    )

    # Drop existing collection
    try:
        client.delete_collection("shl_assessments")
    except Exception:
        pass

    collection = client.create_collection(
        name="shl_assessments",
        metadata={"hnsw:space": "cosine"}
    )

    log.info(f"Generating embeddings for {len(texts)} assessments...")
    embeddings = embedding_fn(texts)

    ids = [f"assessment_{i}" for i in range(len(texts))]
    metadatas = [
        {
            "name": item["name"],
            "url": item.get("url", ""),
            "test_type": item.get("test_type", "K"),
            "test_type_full": item.get("test_type_full", ""),
            "duration": item.get("duration", "") or "",
            "category": item.get("category", "") or "",
        }
        for item in catalog
    ]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    log.info(f"ChromaDB collection saved to {persist_dir}")
    log.info(f"Collection contains {collection.count()} entries")


def get_openai_embedding_fn(api_key: str, model: str):
    """Returns a batch embedding function using OpenAI."""
    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    def embed(texts: list[str]) -> list[list[float]]:
        response = client.embeddings.create(model=model, input=texts)
        return [e.embedding for e in response.data]

    return embed


def get_local_embedding_fn():
    """Returns a local sentence-transformers embedding function."""
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        log.info("Using local SentenceTransformer: all-MiniLM-L6-v2")

        def embed(texts: list[str]) -> list[list[float]]:
            return model.encode(texts, convert_to_numpy=True).tolist()

        return embed
    except ImportError:
        raise ImportError("sentence-transformers not installed. Run: pip install sentence-transformers")


def main():
    # Load environment
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / "backend" / ".env")

    catalog_path = os.getenv("CATALOG_JSON_PATH", "./data/shl_catalog.json")
    vector_db = os.getenv("VECTOR_DB", "faiss")
    faiss_path = os.getenv("FAISS_INDEX_PATH", "./data/faiss_index")
    chroma_path = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "openai")
    embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    openai_key = os.getenv("OPENAI_API_KEY", "")

    # Resolve relative paths
    base = Path(__file__).parent.parent
    if not Path(catalog_path).is_absolute():
        catalog_path = str(base / catalog_path.lstrip("./"))

    catalog = load_catalog(catalog_path)
    texts = catalog_to_texts(catalog)

    # Get embedding function
    if embedding_provider == "openai" and openai_key:
        log.info(f"Using OpenAI embeddings: {embedding_model}")
        embed_fn = get_openai_embedding_fn(openai_key, embedding_model)
    else:
        log.info("Using local sentence-transformers embeddings")
        embed_fn = get_local_embedding_fn()

    # Build index
    if vector_db == "chroma":
        if not Path(chroma_path).is_absolute():
            chroma_path = str(base / chroma_path.lstrip("./"))
        build_chroma_index(texts, catalog, chroma_path, embed_fn)
    else:
        if not Path(faiss_path).is_absolute():
            faiss_path = str(base / faiss_path.lstrip("./"))
        build_faiss_index(texts, catalog, faiss_path, embed_fn)

    log.info("Embedding pipeline complete!")


if __name__ == "__main__":
    main()
