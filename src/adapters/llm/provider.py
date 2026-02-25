from __future__ import annotations
import json
from typing import Any, Dict, List

class LLMProvider:
    def __init__(self, client) -> None:
        self.client = client
    
    def system_prompt(self, tool_specs: List[Dict]) -> str:
        from src.core.agent.prompts import SYSTEM_PROMPT
        return SYSTEM_PROMPT + '\n\nTOOLS:\n' + json.dumps(tool_specs)
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        return self.client.chat(messages)