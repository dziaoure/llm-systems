from __future__ import annotations
import sys, json
from src.core.tools.registry import ToolRegistry
from src.adapters.tools.clause_extractor import ClauseExtractorTool
from src.adapters.tools.risk_heuristics import RiskHeuristicsTool
from src.adapters.llm.provider import LLMProvider, GeminiChatClient
from src.adapters.tools.risk_rubric_gemini import RiskRubricGeminiTool
from src.core.agent.agent_loop import AgentLoop
from src.core.agent.tracer import Tracer


class DummyClient:
    def chat(self, messages):
        raise RuntimeError('Wire up a real client')
    

def main():
    if len(sys.argv) < 2:
        print('Usage: python -m src.app.cli <path_to_contract_text>')
        sys.exit(1)

    path = sys.argv[1]
    contract_text = open(path, 'r', encoding='utf-8').read()

    tools = ToolRegistry()
    tools.register(ClauseExtractorTool())
    tools.register(RiskHeuristicsTool())

    gemini_risk_rubric = RiskRubricGeminiTool()
    tools.register(gemini_risk_rubric)

    tracer = Tracer()

    client = GeminiChatClient()
    llm = LLMProvider(client=client)
    agent = AgentLoop(llm=llm, tools=tools, tracer=tracer)

    result = agent.run(contract_text=contract_text)
    tracer.flush()

    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()