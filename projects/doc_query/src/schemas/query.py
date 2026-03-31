from pydantic import BaseModel, Field, field_validator

from src.models.citation import CitationRecord
from src.models.retrieval import RetrievedChunk

class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=10)
    min_score: float | None = Field(default=None, ge=0.0, le=1.0)
    return_snippets: bool = True

    @field_validator('question')
    @classmethod
    def validate_question(cls, value: str) -> str:
        cleaned = value.strip()

        if not cleaned:
            raise ValueError('question mut not be empty')
        
        return cleaned
    

class QueryResponse(BaseModel):
    question: str
    answer: str
    grounded: bool
    citations: list[CitationRecord] = Field(default_factory=list)
    reason_if_unanswered: str | None = None
    retrieved_chunks: list[RetrievedChunk] = Field(default_factory=list)
    latency_ms: float = Field(default=0.0, ge=0.0)