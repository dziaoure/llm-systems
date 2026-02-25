from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Protocol


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_schema: Dict[str, Any]


class Tool(Protocol):
    spec: ToolSpec

    def run(self, args: Dict[str, Any]) -> Dict[str, Any]: ...
    