"""
Structured logging setup using structlog.
Provides JSON logs in production, pretty logs in development.
"""

import logging
import structlog
from app.core.config import settings


def configure_logging() -> None:
    """Configure structlog for the application."""

    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Standard library logging configuration
    logging.basicConfig(
        format="%(message)s",
        level=log_level,
    )

    # Structlog processors pipeline
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),  # Pretty in dev; swap to JSONRenderer in prod
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__):
    """Get a structlog logger instance."""
    return structlog.get_logger(name)
