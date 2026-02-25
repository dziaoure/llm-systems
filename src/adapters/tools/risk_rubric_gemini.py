from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict

from google import genai

from src.core.tools.base import ToolSpec


def _extract_json_object(text: str) -> Dict[str, Any]:
    '''
        Best effort JSON extractor:
        - Strips ```json fences
        - If extra prose exists, extracts the first {...} block
    '''
    t = text.strip()

    # Strip fenced blocks if present
    if t.startswith('```'):
        t = re.sub(r"^```(?:json)?\s*", "", t, flags=re.IGNORECASE)
        t = re.sub(r"\s*```$", "", t)

    # Try direct parse
    try:

        return json.loads(t)
    
    except Exception:
        pass

    # Extract first JSON object
    m = re.search(r"\{.*\}", t, flags=re.DOTALL)

    if not m:
        raise ValueError('No JSON object found in model output')
    
    return json.loads(m.group(0))



@dataclass
class RiskRubricGeminiTool:
    spec = ToolSpec(
        name='score_risk_rubric',
        description=(
            'Scores contract risk using an LLM rubric based on extracted clauses. '
            'Returns a consistent JSON risk report (score/level/flags/rationales/recommended_Edits)'
        ),
        input_schema={
            'type': 'object',
            'properties': {
                'clauses': { 'type': 'object' },
                'content': {
                    'type': 'object',
                    'description': 'Optional context like party_role (ventor/customer), jurisdiction, contract_type'
                }
            },
            'required': ['clauses']
        }
    )

    def __post_init__(self) -> None:
        api_key = os.getenv('GEMINI_API_KEY')

        if not api_key:
            raise RuntimeError('GEMINI_API_KEY ebvironment variable not set')
            
        self.model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        self.client = genai.Client(api_key=api_key)


    def run(self, args: Dict[str, Any]) -> Dict[str, Any]:
        clauses: Dict[str, str] = args.get('clauses') or {}
        context: Dict[str, Any] = args.get('context') or {}

        # Normalize null/None to ''
        clauses = { k: (v or '') for k,v in clauses.items() }

        rubric_prompt = self._build_prompt(clauses=clauses, context=context)

        # First attempt
        text = self.client.models.generate_content(
            model=self.model,
            contents=[{ 'role': 'user', 'parts': [{'text': rubric_prompt}]}],
            config={'temperature': 0.2 }
        ).text

        try:

            obj = _extract_json_object(text)
            return self._validate_and_normalize(obj)
        
        except Exception:
            # One repair attempt
            repair_prompt = (
                'Your previous output was not valid JSON matching the required schema. '
                'Return ONLY a single valid JSON object with the exact keys specified. '
                'No markdown, no commentary.\n\n'
                f'PREVIOUS OUTPUT:\n{text}\n\n'
                'Now return the corrected JSON:'
            )

            text2 = self.client.models.generate_content(
                model=self.model,
                contents=[{'role': 'user', 'parts': [{'text': repair_prompt}]}],
                config={ 'temperature': 0.2}
            ).text

            obj2 = _extract_json_object(text2)
            return self._validate_and_normalize(obj2)
        
    
    def _build_prompt(self, clauses: Dict[str, str], context: Dict[str, Any]) -> str:
        # Keep it explicit and enforce a stable schema
        return (
            "You are a contract risk analyst. Score risk using a strict rubric.\n"
            "You MUST return VALID JSON ONLY. No markdown.\n\n"
            "RUBRIC (0-100 risk score):\n"
            "- Liability: unlimited liability, no cap, broad damages -> higher risk.\n"
            "- Termination: for convenience without notice, one-sided termination -> higher risk.\n"
            "- Payment: slow terms (Net 60/90), unclear invoicing, late fee absence -> moderate risk.\n"
            "- IP: broad assignment of all work product, unclear pre-existing IP -> moderate/high risk.\n"
            "- Confidentiality: missing/weak terms -> moderate risk.\n"
            "- Indemnity: defend + any/all claims + no carveouts -> higher risk.\n"
            "- Governing law / venue: unusual or one-sided forum -> moderate risk.\n\n"
            "OUTPUT SCHEMA (return exactly these keys):\n"
            "{\n"
            '  "risk_score": number,\n'
            '  "risk_level": "low"|"medium"|"high",\n'
            '  "risk_flags": string[],\n'
            '  "rationale_by_clause": { "<clause_type>": string },\n'
            '  "recommended_edits": string[],\n'
            '  "assumptions": string[]\n'
            "}\n\n"
            f"CONTEXT:\n{json.dumps(context)}\n\n"
            f"EXTRACTED_CLAUSES:\n{json.dumps(clauses)}\n\n"
            "Rules:\n"
            "- Base your rationales ONLY on the extracted clauses provided.\n"
            "- If a clause is empty/missing, say so in rationale and add an assumption.\n"
            "- Keep recommended_edits actionable and short (bullet-like strings).\n"
        )

    def _validate_and_normalize(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        # Minimal validation + normalization (keep it robust)
        score = obj.get('risk_score')

        if not isinstance(score, (int, float)):
            raise ValueError("risk_score must be a number.")
        
        score = max(0, min(100, float(score)))

        level = obj.get('risk_level')
        
        if level not in ('low', 'medium', 'high'):
            # derive if model deviates
            level = 'low' if score < 20 else 'medium' if score < 50 else 'high'

        flags = obj.get('risk_flags') or []

        if not isinstance(flags, list):
            flags = []

        rationale = obj.get('rationale_by_clause') or {}
        
        if not isinstance(rationale, dict):
            rationale = {}

        edits = obj.get('recommended_edits') or []
        
        if not isinstance(edits, list):
            edits = []

        assumptions = obj.get('assumptions') or []
        
        if not isinstance(assumptions, list):
            assumptions = []

        return {
            'risk_score': score,
            'risk_level': level,
            'risk_flags': [str(x) for x in flags],
            'rationale_by_clause': {str(k): str(v) for k, v in rationale.items()},
            'recommended_edits': [str(x) for x in edits],
            'assumptions': [str(x) for x in assumptions],
        }

