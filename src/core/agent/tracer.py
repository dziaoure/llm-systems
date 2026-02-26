from __future__ import annotations
import json, os, time, uuid
from typing import Any, Dict

class Tracer:
    def __init__(self, log_path: str = 'logs/runs.json') -> None:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        self.log_path = log_path
        self.run_id = str(uuid.uuid4())
        self.events = []


    def log_llm(self, step: int, latency_s: float, raw: str) -> None:
        self.events.append({
            'type': 'llm',
            'run_idd': self.run_id,
            'step': step,
            'latency_s': latency_s,
            'raw': raw,
            'ts': time.time()
        })

    def log_tool(self, step: int, tool: str, latency_s: float, args: Dict[str, Any], result: Dict[str, Any]) -> None:
        self.events.append({
            'type': 'tool',
            'run_id': self.run_id,
            'step': step,
            'tool': tool,
            'latency_s': latency_s,
            'args': args,
            'result': result,
            'ts': time.time()
        })

    def flush(self) -> None:
        with open(self.log_path, 'a', encoding='utf-8') as f:
            for e in self.events:
                f.write(json.dumps(e) + '\n')

        self.events.clear()