from __future__ import annotations

from typing import Any, Dict, Optional

from src.core.tools.registry import ToolRegistry
from src.core.agent.agent_loop import AgentLoop
from src.core.agent.tracer import Tracer

from src.adapters.llm.provider import LLMProvider, GeminiChatClient
from src.adapters.tools.clause_extractor import ClauseExtractorTool
from src.adapters.tools.risk_heuristics import RiskHeuristicsTool
from src.adapters.tools.risk_rubric_gemini import RiskRubricGeminiTool


def build_agent() -> tuple[AgentLoop, Tracer]:
    tools = ToolRegistry()
    tools.register(ClauseExtractorTool())
    tools.register(RiskHeuristicsTool())
    tools.register(RiskRubricGeminiTool())

    tracer = Tracer()
    client = GeminiChatClient()
    llm = LLMProvider(client=client)
    agent = AgentLoop(llm=llm, tools=tools, tracer=tracer)

    return agent, tracer


async def analyze_text(contract_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    agent, tracer = build_agent()

    try:

        result = agent.run(contract_text=contract_text)
        result['run_id'] = tracer.run_id
        return result
    
    except Exception:
        pass

    finally:
        tracer.flush()

    

