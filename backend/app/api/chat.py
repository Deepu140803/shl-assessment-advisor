"""
Chat API Router
===============
Exposes POST /chat endpoint.
"""

from fastapi import APIRouter, HTTPException, Request
from app.models.schemas import ChatRequest, ChatResponse
from app.services.agent import run_agent
from app.core.logging import get_logger

log = get_logger(__name__)
router = APIRouter()


@router.post("/chat", response_model=ChatResponse, summary="Conversational SHL assessment recommendation")
async def chat(request: ChatRequest, req: Request) -> ChatResponse:
    """
    Process a conversational message and return SHL assessment recommendations.

    - Accepts full conversation history (stateless API).
    - Returns agent reply, optional recommendations, and end-of-conversation flag.
    - Recommendations are empty [] while gathering context.
    - Recommendations contain 1-10 items when ready to recommend.
    """
    client_ip = req.client.host if req.client else "unknown"
    log.info(
        "chat_request",
        client_ip=client_ip,
        num_messages=len(request.messages),
        last_user_msg=next(
            (m.content[:100] for m in reversed(request.messages) if m.role == "user"),
            ""
        ),
    )

    try:
        response = await run_agent(request.messages)
        log.info(
            "chat_response",
            num_recommendations=len(response.recommendations),
            end_of_conversation=response.end_of_conversation,
        )
        return response

    except ValueError as e:
        log.error(f"Validation error in chat: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        log.error(f"Unexpected error in chat: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred. Please try again."
        )
