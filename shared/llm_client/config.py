from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class LLMConfig:
    provider: str
    model: str
    temperature: float

    @staticmethod
    def from_env() -> "LLMConfig":
        provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()
        model = os.getenv("LLM_MODEL", "gpt-40-mini").strip()
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
        
        return LLMConfig(
            provider=provider,
            model=model,
            temperature=temperature
        )
    
def require_env(name: str) -> str:
    v = os.getenv(name)

    if not v or not v.strip():
        return RuntimeError(f'Missing required env var: {name}')

    return v.strip()
