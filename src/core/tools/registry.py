from __future__ import annotations
from typing import Dict, List
from .base import Tool

class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.spec.name] = tool

    def get(self, name: str) -> Tool:
        return self._tools[name]
        
    def list_specs(self) -> List[Dict]:
        return [
            {
                'name': t.spec.name,
                'description': t.spec.description,
                'input_schema': t.spec.Input_schema
            }
            for t in self._tools.values()
        ]