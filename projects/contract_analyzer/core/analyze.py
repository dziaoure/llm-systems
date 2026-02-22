from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from shared.llm_client import LLMClient, ChatMessage
from shared.prompts.v1.contract_summary_prompt import SYSTEM_PROMPT, USER_TEMPLATE
from shared.utils.chunking import chunk_text
from shared.utils.json_utils import safe_parse_json
from shared.utils.pdf_utils import extract_text_from_pdf_bytes
from shared.prompts.v1.contract_map_reduce_prompts import MAP_SYSTEM, MAP_USER, REDUCE_SYSTEM, REDUCE_USER

SINGLE_PASS_THRESHOLD = 15_000

@dataclass(frozen=True)
class AnalysisResult:
    raw_text: str
    parsed: Optional[Dict[str, Any]]
    error: Optional[str]
    provider: str
    model: str


def analyze_contract_text(
    contract_text: str,
    *,
    max_output_tokens: int = 4000
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


def analyze_contract_pdf(
        pdf_bytes: bytes,
        *,
        max_pages: int = 25,
        chunk_size: int = 3500,
        overlap: int = 300,
        map_max_tokens: int = 4000,
        reduce_max_tokens: int = 4000
) -> AnalysisResult:
    '''
    PDF Pipeline
    PDF -> text -> chunks -> map summaries -> reduce to final JSON
    '''
    contract_text = extract_text_from_pdf_bytes(pdf_bytes=pdf_bytes, max_pages=max_pages)

    if not contract_text:
        return AnalysisResult(
            raw_text='',
            parsed=None,
            error='No text could be extracted from the PDF (it may be scanned)',
            provider='gemini',
            model='unknown'
        )
    
    # Guardrail: if extraction is too small, fail loudly
    if len(contract_text.strip()) < 300:
        return AnalysisResult(
            raw_text="",
            parsed=None,
            error="Extracted text is too short. PDF may be scanned or extraction failed.",
            provider="gemini",
            model="unknown",
        )

    # For short docs (like NDAs), skip map-reduce entirely.
    # Pick a threshold that fits your model/context comfortably.
    if len(contract_text) <= SINGLE_PASS_THRESHOLD:
        return analyze_contract_text(contract_text, max_output_tokens=4000)

    chunks = chunk_text(contract_text, chunk_size=chunk_size, overlap=overlap)

    if not chunks:
        return AnalysisResult(
            raw='',
            parsed=None,
            error='PDF text extraction return empty chunks',
            provider='gemini',
            model='unknown'
        )
    
    client = LLMClient()

    # MAP
    chunk_summaries = []

    for idx, ch in enumerate(chunks, start=1):
        msgs = [
            ChatMessage(role='system', content=MAP_SYSTEM),
            ChatMessage(role='user', content=MAP_USER.substitute(chunk=ch))
        ]
        r = client.generate(msgs, max_tokens=map_max_tokens)
        chunk_summaries.append(f'CHUNK {idx}:\n{r.text.strip()}')

    summaries_text = '\n\n'.join(chunk_summaries)

    # REDUCE (Structured JSON)
    reduce_msgs = [
        ChatMessage(role='system', content=REDUCE_SYSTEM),
        ChatMessage(role='user', content=REDUCE_USER.substitute(summaries=summaries_text))
    ]
    resp = client.generate(reduce_msgs, max_tokens=reduce_max_tokens)

    parsed, err = safe_parse_json(resp.text)

    return AnalysisResult(
        raw_text=resp.text,
        parsed=parsed if isinstance(parsed, dict) else None,
        error=err,
        provider=resp.provider,
        model=resp.model
    )
