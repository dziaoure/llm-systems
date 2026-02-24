from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Any, Dict, List
from src.core.tools.base import ToolSpec

@dataclass
class ClauseExtractorTool:
    spec = ToolSpec(
        name='extract_clauses',
        description='Extracts common contract clauses from raw contract text (tarmination, payment, liability, cpnfdentiality, governing_law, IP, indemnity).',
        input_schema={
            'type': 'object',
            'properties': {
                'contract_text': { 'type': 'string'},
                'clauses_types': {
                    'type': 'array',
                    'items': { 'type': 'string'},
                    'default': [
                        'termination',
                        'payment',
                        'liability',
                        'confidentiality',
                        'governing_law',
                        'ip',
                        'indemnity'
                    ]
                },
                'required': ['contract_text']
            }
        }
    )

    def run(self, args: Dict[str, Any]) -> Dict[str, Any]:
        text = args['contract_text']
        clause_typees: List[str] = args.get('clause_types') or self.spec.input_schema['properties']['clause_types']['default']

        patterns = {
            'termination': r'(termination|term and termination|terminate)\b(.|\n){0,1200}',
            'payment': r'(fees|payment|compensation|invoic|billing)\b(.|\n){0,1200}',
            'liability': r'(limitation of liability|liability)\b(.|\n){0,1200}',
            'confidentiality': r'(confidential|non[- ]disclosure|nda)\b(.|\n){0,1200}',
            'governing_law': r'(governing law|jurisdiction|venue)\b(.|\n){0,1200}',
            'ip': r'(intellectual property|ownership|license)\b(.|\n){0,1200}',
            'indemnity': r'(indemnif|hold harmless)\b(.|\n){0,1200}',
        }

        extracted = {}

        for c in clause_typees:
            pat = patterns.get(c)

            if not pat:
                continue

            m = re.search(pat, text, flags=re.IGNORECASE)
            extracted[c] = (m.group(0).strip()[:1500] if m else '')

        return {
            'clauses': extracted,
            'found': [k for k,v in extracted.items() if v]
        }
