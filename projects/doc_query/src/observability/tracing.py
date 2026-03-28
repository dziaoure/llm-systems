from __future__ import annotations

import json
from pathlib import Path

from src.config import get_settings
from src.models.query import QueryTrace

TRACE_FILENAME = 'query_trace.jsonl'


def get_trace_path() -> Path:
    settings = get_settings()
    settings.paths.logs_dir.mkdir(parents=True, exist_ok=True)
    return settings.paths.logs_dir / TRACE_FILENAME


def persist_query_trace(trace: QueryTrace) -> None:
    trace_path = get_trace_path()
    
    with trace_path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(trace.model_dump(mode='json'), ensure_ascii=False) + '\n')

