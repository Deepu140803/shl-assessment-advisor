"""
Health Check Router
===================
Exposes GET /health endpoint.
"""

from fastapi import APIRouter
from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health() -> HealthResponse:
    """Returns service health status."""
    return HealthResponse(status="ok")
