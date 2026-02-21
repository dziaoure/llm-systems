from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional

ROle = Literal['system', 'user', 'assistant']

@dataclass(frozen=True)
class ChatMessage:
    role: ROle
    content: str


@dataclass(frozen=True)
class LLMResponse:
    text: str
    provider: str
    model: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None

