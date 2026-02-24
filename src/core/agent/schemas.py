from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ToolCall:
    name: str
    args: Dict[str, Any]



@dataclass
class AgentResponse:
    status: str     # 'final' | 'tool_call' | 'error'
    final_answer: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    risk_summary: Optional[Dict[str, Any]] = None
    extracted_clauses: Optional[Dict[str, str]] = None
    confidence: Optional[float] = None