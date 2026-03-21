from typing import Any
from pydantic import BaseModel, Field

class ChunkRecord(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    text: str = Field(min_length=1)
    chunk_index: int = Field(ge=0)
    page_number: int | None = None
    section_title: str | None = None
    token_count: int | None = Field(default=None, ge=0)
    start_char: int | None = Field(default=None, ge=0)
    end_char: int | None = Field(default=None, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)