from pydantic import BaseModel, Field


class CitationRecord(BaseModel):
    chunk_id: str
    filename: str
    page_number: int | None = None
    section_title: str | None = None
    snippet: str = Field(min_length=1)
    rank: int = Field(ge=0)