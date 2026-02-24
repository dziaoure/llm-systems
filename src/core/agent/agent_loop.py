from __future__ import annotations
import json
import time
from typing import Any, Dict, List, Tuple
from src.core.tools.registry import ToolRegistry


def _safe_json_loads(text: str) -> Dict[str, Any]:
    # Best-effort: strip code fences if any apper
    t = text.strip()

    if t.startswith('```'):
        t = t.strip('`')

    return json.loads(t)


class AgentLoop:
    def __init__(self, llm, tools: ToolRegistry, tracer) -> None:
        self.llm = llm
        self.tools = tools
        self.tracer = tracer


    def run(self, contract_text: str, max_steps: int = 5) -> Dict[str, Any]:
        messages: List[Dict[str, str]] = []
        tool_specs = self.tools.list_specs

        # System + initial user
        messages.append({ 'role': 'system', 'content': self.llm.system_prompt[tool_specs]})
        messages.append({ 'role': 'user', 'content': json.dumps({
            'task': 'Ana;yze this contract for key clauses and risks',
            'contract_text': contract_text[:120000] # Cap for safety
        })})

        extracted_clauses: Dict[str, str] = {}
        risk_summary: Dict[str, Any] = {}

        for step in range(max_steps):
            t0 = time.time()
            raw = self.llm.chat(messages)
            latency = time.time() - t0

            self.tracer.log_llm(step=step, latency=latency, raw=raw)

            # PArse JSON and retry if needed
            try:

                obj = _safe_json_loads(raw)

            except Exception:
                messages.append({ 'role': 'user', 'content': 'Your last response was not valid JSON. Return valid JSON ONLY.'})
                raw2 = self.llm.chat(messages)
                obj = _safe_json_loads(raw2)

            status = obj.get('status')

            if status == 'tool_call':
                calls = obj.get('tool_calls') or []

                # Enforece caps
                calls = calls[:2]

                for call in calls:
                    name = call.get('name')
                    args = call.get('args') or {}
                    tool = self.tools.get(name)
                    t1 = time.time()
                    result = tool.run(args)
                    tool_latency = time.time() - t1
                    self.tracer.log_tool(
                        step=step, 
                        tool=name, 
                        latency=tool_latency,
                        args=args,
                        result=result
                    )

                    # Stash useful outputs
                    if name == 'extract_clasues':
                        extracted_clauses = result.get('clauses') or extracted_clauses

                    if name == 'score_risk_heuristics':
                        risk_summary = result or risk_summary

                    messages.append({ 'role': 'user', 'content': json.dump({
                        'tool': name,
                        'result': result
                    })})

                continue

            if status == 'final':
                # Merge stashed results if model omitted them
                obj.setdefault('extracted_clauses', extracted_clauses)
                obj.setdefault('risk_summary', risk_summary)
                return obj
        
            # Unknown status => treat as error
            return {
                'status': 'error',
                'error': f'Unlnown status: {status}',
                'raw': obj
            }
        
        return {
            'status': 'error',
            'error': 'max_steps_exceeded',
            'extracted_clauses': extracted_clauses,
            'risk_summary': risk_summary
        }
