from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from shared.llm_client import LLMClient, ChatMessage
from shared.prompts.v1.contract_summary_prompt import SYSTEM_PROMPT, USER_TEMPLATE
from shared.utils.json_utils import safe_parse_json

@dataclass(frozen=True)
class AnalysisResult:
    raw_text: str
    parsed: Optional[Dict[str, Any]]
    error: Optional[str]
    provider: str
    model: str


def analyze_contract_test(
    contract_text: str,
    *,
    max_output_tokens: int = 1500
) -> AnalysisResult:
    '''
    Single-pass contract extraction (text mode)
    '''
    client = LLMClient()

    user_prompt = USER_TEMPLATE.substitute(contract_text=contract_text)

    messages = [
        ChatMessage(role='system', content=SYSTEM_PROMPT),
        ChatMessage(role='user', content=user_prompt)
    ]

    resp = client.generate(messages=messages, max_tokens=max_output_tokens)

    parsed, error = safe_parse_json(resp.text)

    return AnalysisResult(
        raw_text=resp.text,
        parsed=parsed if isinstance(parsed, dict) else None,
        error=error,
        provider=resp.provider,
        model=resp.model
    )
