from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

class DocumentRecord(BaseModel):
    document_id: str
    filename: str
    file_path: str
    file_type: str
    title: str | None = None
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    num_pages: int | None = None
    num_chunks: int = Field(default=0, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)