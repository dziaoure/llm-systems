from pydantic import BaseModel, Field


class EvalRequest(BaseModel):
    dataset_path: str
    top_k: int = Field(default=5, ge=1, le=10)
    max_examples: int | None = Field(default=None, ge=1)


class EvalResponse(BaseModel):
    num_examples: int = Field(ge=0)
    grounded_rate: float = Field(ge=0.0, le=1.0)
    citation_rate: float = Field(ge=0.0, le=1.0)
    refusal_rate: float = Field(ge=0.0, le=0.0)
    avg_latency_ms: float = Field(ge=0.0, le=1.0)
    summary: str
    