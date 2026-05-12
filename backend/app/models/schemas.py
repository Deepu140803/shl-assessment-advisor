"""
Pydantic models for API request/response validation.
Strict schema adherence as per project spec.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal


# ─── Message Models ───────────────────────────────────────────────────────────

class Message(BaseModel):
    """A single chat message."""
    role: Literal["user", "assistant", "system"]
    content: str


# ─── Recommendation Models ────────────────────────────────────────────────────

class AssessmentRecommendation(BaseModel):
    """A single SHL assessment recommendation."""
    name: str = Field(description="Assessment name")
    url: str = Field(description="SHL product page URL")
    test_type: str = Field(description="Test type code (e.g. K, A, B, P, S, etc.)")
    description: Optional[str] = Field(default=None, description="Brief description")
    duration: Optional[str] = Field(default=None, description="Estimated duration")
    skills_measured: Optional[List[str]] = Field(
        default=None,
        description="Skills the test measures"
    )
    confidence_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Retrieval confidence score 0-1"
    )


# ─── Request Models ───────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    """Incoming chat request with full conversation history."""
    messages: List[Message]

    class Config:
        schema_extra = {
            "example": {
                "messages": [
                    {
                        "role": "user",
                        "content": "I need to hire a Java developer"
                    }
                ]
            }
        }


# ─── Response Models ──────────────────────────────────────────────────────────

class ChatResponse(BaseModel):
    """Chat response with optional recommendations."""
    reply: str = Field(description="Agent's text reply")

    recommendations: List[AssessmentRecommendation] = Field(
        default_factory=list,
        description="SHL assessment recommendations"
    )

    end_of_conversation: bool = Field(
        default=False,
        description="True when the conversation is complete"
    )

    class Config:
        schema_extra = {
            "example": {
                "reply": "Based on your requirements, here are the best SHL assessments:",
                "recommendations": [
                    {
                        "name": "Java 8 (New)",
                        "url": "https://www.shl.com/solutions/products/product-catalog/view/java-8-new/",
                        "test_type": "K",
                        "description": "Assesses Java 8 programming skills",
                        "duration": "45 minutes",
                        "skills_measured": [
                            "Java",
                            "OOP",
                            "Collections"
                        ],
                        "confidence_score": 0.92
                    }
                ],
                "end_of_conversation": False
            }
        }


# ─── Health Check ─────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"


# ─── Catalog Models ───────────────────────────────────────────────────────────

class CatalogEntry(BaseModel):
    """A single SHL catalog entry."""
    name: str
    url: str
    description: str
    test_type: str

    test_type_full: Optional[str] = None

    skills_measured: List[str] = Field(default_factory=list)

    duration: Optional[str] = None

    category: Optional[str] = None

    languages: Optional[List[str]] = Field(default_factory=list)

    def to_embedding_text(self) -> str:
        """Produce a rich text representation for embedding."""
        parts = [
            f"Assessment: {self.name}",
            f"Category: {self.category or 'General'}",
            f"Test Type: {self.test_type_full or self.test_type}",
            f"Description: {self.description}",
        ]

        if self.skills_measured:
            parts.append(
                f"Skills Measured: {', '.join(self.skills_measured)}"
            )

        if self.duration:
            parts.append(f"Duration: {self.duration}")

        return "\n".join(parts)