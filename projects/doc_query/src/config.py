from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.constants import (
    APP_NAME,
    EVAL_DIR,
    INDEX_DIR,
    LOGS_DIR,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR
)

class AppSettings(BaseModel):
    name: str = APP_NAME
    environment: str = 'dev'
    debug: bool = True
    log_level: str = 'INFO'


class PathSettings(BaseModel):
    raw_data_dir: Path = RAW_DATA_DIR
    processed_data_dir: Path = PROCESSED_DATA_DIR
    index_dir: Path = INDEX_DIR
    logs_dir: Path = LOGS_DIR
    eval_dir: Path = EVAL_DIR


class ChunkingSettings(BaseModel):
    chunk_size: int = Field(default=800, ge=100)
    chunk_overlap: int = Field(default=120, ge=0)
    min_chunk_chars: int = Field(default=100, ge=1)

    @model_validator(mode='after')
    def validate_chnking(self) -> 'ChunkingSettings':
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError('`chunk_overlap` mut be small than `chunk_size`')
        return self
    
class RetrievalSettings(BaseModel):
    default_top_k: int = Field(default=5, ge=1)
    max_top_k: int = Field(default=10, ge=1)
    min_similarity_threshold: float = Field(default=0.25, ge=0.0, le=1.0)

    @model_validator(mode='after')
    def validate_retrieval(self) -> 'RetrievalSettings':
        if self.default_top_k > self.max_top_k:
            raise ValueError('`default_top_k` cannt be greater than `max_top_k`')
        
        return self
    
class ModelSettings(BaseModel):
    generation_model: str = 'gemini-2.5-flash'
    embedding_model: str = 'models/text-embeddings-004'
    api_key_env_var: str = 'GEMINI_API_KEY'


class PromptSettings(BaseModel):
    prompt_version: str = 'v1'
    max_context_chunks: int = Field(default=5, ge=1)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_prefix='DOCQUERY_',
        extra='ignore'
    )

    app: AppSettings = AppSettings()
    paths: PathSettings = PathSettings()
    chunking: ChunkingSettings = ChunkingSettings()
    retrieval: RetrievalSettings = RetrievalSettings()
    models: ModelSettings = ModelSettings()
    prompts: PromptSettings = PromptSettings()

    @field_validator('app')
    @classmethod
    def validate_app_settings(cls, value: AppSettings) -> AppSettings:
        allowed = {'dev', 'test', 'prod'}

        if value.environment not in allowed:
            raise ValueError(f'Environment must be one of {allowed}')
        
        return value
    
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()