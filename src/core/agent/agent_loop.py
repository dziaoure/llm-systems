from __future__ import annotations
import json
import re
import time
from typing import Any, Dict, List, Tuple
from src.core.tools.registry import ToolRegistry


def _safe_json_loads(text: str) -> Dict[str, Any]:
    """
    Robust JSON extraction:
    - Strips ```json fences
    - Extracts first valid JSON object
    - Handles leading/trailing prose
    """

    if not text or not text.strip():
        raise ValueError("Empty model response.")

    t = text.strip()

    # Remove fenced blocks like ```json ... ```
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*", "", t, flags=re.IGNORECASE)
        t = re.sub(r"\s*```$", "", t)

    # Try direct parse first
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        pass

    # Extract first {...} block
    match = re.search(r"\{.*\}", t, flags=re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model output.")

    candidate = match.group(0)

    return json.loads(candidate)


def _normalize_clauses(clauses: Dict) -> Dict:
    if not clauses:
        return {}
    
    return { k: (v or '') for k,v in clauses.items()}


class AgentLoop:
    def __init__(self, llm, tools: ToolRegistry, tracer) -> None:
        self.llm = llm
        self.tools = tools
        self.tracer = tracer


    def run(self, contract_text: str, max_steps: int = 5) -> Dict[str, Any]:
        messages: List[Dict[str, str]] = []
        tool_specs = self.tools.list_specs()

        # System + initial user
        messages.append({ 'role': 'system', 'content': self.llm.system_prompt(tool_specs)})
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

            self.tracer.log_llm(step=step, latency_s=latency, raw=raw)

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
                        latency_s=tool_latency,
                        args=args,
                        result=result
                    )

                    # Stash useful outputs
                    if name == 'extract_clasues':
                        extracted_clauses = result.get('clauses') or extracted_clauses

                    if name == 'score_risk_heuristics':
                        risk_summary = result or risk_summary

                    if name == 'score_risk_rubric':
                        risk_summary = result or risk_summary

                    messages.append({ 'role': 'user', 'content': json.dumps({
                        'tool': name,
                        'result': result
                    })})

                continue

            if status == 'final':
                # Merge stashed results if model omitted them
                obj['extracted_clauses'] = _normalize_clauses(extracted_clauses or obj.get('extracted_clauses') or {})
                obj['risk_summary'] = risk_summary or obj.get('risk_summary') or {}
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
