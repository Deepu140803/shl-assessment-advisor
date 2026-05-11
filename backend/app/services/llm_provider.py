"""
LLM Provider Service
====================
Abstraction layer supporting OpenAI, Groq, Gemini, and OpenRouter.
Returns a LangChain-compatible chat model.
"""

from functools import lru_cache
from langchain_core.language_models.chat_models import BaseChatModel
from app.core.config import settings
from app.core.logging import get_logger

log = get_logger(__name__)


@lru_cache(maxsize=1)
def get_llm() -> BaseChatModel:
    """
    Build and return the configured LLM.
    Result is cached so the model is only instantiated once.
    """
    provider = settings.llm_provider
    log.info(f"Initializing LLM provider: {provider}")

    if provider == "openai":
        return _build_openai()
    elif provider == "groq":
        return _build_groq()
    elif provider == "gemini":
        return _build_gemini()
    elif provider == "openrouter":
        return _build_openrouter()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}. Choose: openai, groq, gemini, openrouter")


def _build_openai() -> BaseChatModel:
    """OpenAI ChatGPT models."""
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY not set")
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0.3,
        max_tokens=1024,
    )


def _build_groq() -> BaseChatModel:
    """Groq ultra-fast inference."""
    if not settings.groq_api_key:
        raise ValueError("GROQ_API_KEY not set")
    from langchain_groq import ChatGroq
    return ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        temperature=0.3,
        max_tokens=1024,
    )


def _build_gemini() -> BaseChatModel:
    """Google Gemini models."""
    if not settings.google_api_key:
        raise ValueError("GOOGLE_API_KEY not set")
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=0.3,
        max_output_tokens=1024,
    )


def _build_openrouter() -> BaseChatModel:
    """OpenRouter - unified API for many models."""
    if not settings.openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY not set")
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=settings.openrouter_model,
        api_key=settings.openrouter_api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.3,
        max_tokens=1024,
        default_headers={
            "HTTP-Referer": "https://shl-recommender.app",
            "X-Title": "SHL Assessment Recommender",
        },
    )
