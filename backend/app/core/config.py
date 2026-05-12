"""
Application configuration using Pydantic Settings.
Reads from environment variables or .env file.
"""

from pydantic import BaseSettings
from pydantic import Field
from typing import Literal, List
import os


class Settings(BaseSettings):
    """Central settings object for the entire application."""

    # ─── LLM Provider ────────────────────────────────────────────────────────
    llm_provider: Literal["openai", "groq", "gemini", "openrouter"] = Field(
        default="groq", description="Which LLM provider to use"
    )

    # OpenAI
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o-mini")

    # Groq
    groq_api_key: str = Field(default="", description="Groq API key")
    groq_model: str = Field(default="llama3-70b-8192")

    # Gemini
    google_api_key: str = Field(default="", description="Google API key")
    gemini_model: str = Field(default="gemini-1.5-flash")

    # OpenRouter
    openrouter_api_key: str = Field(default="", description="OpenRouter API key")
    openrouter_model: str = Field(default="meta-llama/llama-3-70b-instruct")

    # ─── Embeddings ───────────────────────────────────────────────────────────
    embedding_provider: Literal["openai", "local"] = Field(default="openai")
    embedding_model: str = Field(default="text-embedding-3-small")

    # ─── Vector DB ────────────────────────────────────────────────────────────
    vector_db: Literal["faiss", "chroma"] = Field(default="faiss")
    chroma_persist_dir: str = Field(default="./data/chroma")

    # ─── Data Paths ───────────────────────────────────────────────────────────
    catalog_json_path: str = Field(default="./data/shl_catalog.json")
    faiss_index_path: str = Field(default="./data/faiss_index")

    # ─── App Settings ─────────────────────────────────────────────────────────
    max_turns: int = Field(default=8)
    top_k_retrieval: int = Field(default=10)
    rerank_top_k: int = Field(default=5)
    log_level: str = Field(default="INFO")

    # ─── CORS ─────────────────────────────────────────────────────────────────
    cors_origins: str = Field(default="http://localhost:5173,http://localhost:3000")

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Singleton instance
settings = Settings()
