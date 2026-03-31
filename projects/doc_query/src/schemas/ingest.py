from pydantic import BaseModel, Field, field_validator

class IngestRequest(BaseModel):
    paths: list[str] = Field(min_length=1)
    rebuild_index: bool = False

    @field_validator('paths')
    @classmethod
    def validate_paths(cls, value: list[str]) -> list[str]:
        cleaned = [p.strip() for p in value if p.strip()]

        if not cleaned:
            raise ValueError('paths must contain at least one non-empty path')
        
        return cleaned
    

class IngestResponse(BaseModel):
    success: bool
    documents_ingested: int = Field(ge=0)
    chunks_created: int = Field(ge=0)
    index_path: str | None = None
    message: str