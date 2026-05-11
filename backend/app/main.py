"""
FastAPI Application Factory
============================
Creates and configures the FastAPI application with:
- CORS middleware
- Routers
- Startup lifespan (pre-warms vector store)
- Exception handlers
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.api import chat, health
from app.services.vector_store import vector_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    log = get_logger("lifespan")
    log.info("SHL Recommender API starting up...")

    # Pre-warm the vector store (loads index into memory)
    try:
        vector_store.initialize()
        log.info("Vector store initialized successfully")
    except Exception as e:
        log.error(f"Vector store initialization failed: {e}")
        log.warning("Starting without pre-warmed vector store - first request will be slow")

    yield  # Application runs here

    log.info("SHL Recommender API shutting down...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    # Configure logging first
    configure_logging()
    log = get_logger("app_factory")

    app = FastAPI(
        title="SHL Assessment Recommender API",
        description=(
            "Conversational AI system for discovering the right SHL assessments. "
            "Powered by LangChain and semantic search."
        ),
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ─── CORS Middleware ───────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    # ─── Exception Handlers ───────────────────────────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        log.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred."},
        )

    # ─── Routers ──────────────────────────────────────────────────────────────
    app.include_router(health.router, tags=["Health"])
    app.include_router(chat.router, tags=["Chat"])

    log.info(f"App created. LLM: {settings.llm_provider} | VectorDB: {settings.vector_db}")
    return app


# Create the app instance
app = create_app()
