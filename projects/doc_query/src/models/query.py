from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from src.models.citation import CitationRecord
from src.models.retrieval import RetrievedChunk


class AnswerRecord(BaseModel):
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)
    grounded: bool
    cirations: list[CitationRecord] = Field(default_factory=list)
    reason_if_unanswered: str | None = None
    retrieved_chunk: list[RetrievedChunk] = Field(default_factory=list)
    latency_ms: float = Field(default=0.0, ge=0.0)


class QueryTrace(BaseModel):
    request_id: str
    timestampt: datetime = Field(default_factory=datetime.utcnow)
    question: str = Field(min_length=1)
    retrieved_chunk_ids: list[str] = Field(default_factory=list)
    retrieved_scores: list[float] = Field(default_factory=list)
    grounded: bool
    citations: list[CitationRecord] = Field(default_factory=list)
    latency_ms: float = Field(default=0.0, ge=0.0)
    prompt_version: str = 'v1'
    metadata: dict[str, Any] = Field(default_factory=dict)
    