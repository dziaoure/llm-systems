from __future__ import annotations

import json
from typing import Any


def extract_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace('json', '', 1).strip()

    try:

        return json.loads(cleaned)
    
    except json.JSONDecodeError:
        start = cleaned.find('{')
        end = cleaned.rfind('}')

        if start == -1 or end == -1 or end <= start:
            raise ValueError('Model response did not contain valid JSON')
        
        candidate = cleaned[start:end + 1]
        return json.loads(candidate)
    

def validate_generation_payload(payload: dict[str, Any]) -> dict[str, Any]:
    required_keys = {
        'answer',
        'grounded',
        'used_chunk_ranks',
        'reason_if_unanswered'
    }

    missing = required_keys - payload.keys()

    if missing:
        raise ValueError(f'Missing keys in generation payload: {sorted(missing)}')
    
    if not isinstance(payload['answer'], str) or not payload['answer'].strip():
        raise ValueError('Field "answer" must be a non-empty string')
    
    if not isinstance(payload['grounded'], bool):
        raise ValueError('Field "grounded" must be a boolean')
    
    if not isinstance(payload['used_chunk_ranks'], list):
        raise ValueError('Field "used_chunk_ranls must be a list')
    
    if not all(isinstance(rank, int) for rank in payload['used_chunk_ranks']):
        raise ValueError('All used_chunk_ranks must be integers')
    
    reason = payload['reason_if_unanswered']

    if reason is not None and not isinstance(reason, str):
        raise ValueError('Field "reason_if_unanswered" must be a string or null')
    
    return payload