from typing import Any
from pydantic import BaseModel, Field

class RetrievedChunk(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    text: str = Field(min_length=1)
    score: float
    rank: int = Field(ge=1)
    page_number: int | None = None
    section_title: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)