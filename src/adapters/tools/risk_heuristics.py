from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict
from src.core.tools.base import ToolSpec


@dataclass
class RiskHeuristicsTool:
    spec = ToolSpec(
        name='score_risk_heuristics',
        description='Scores basic contract rist heuristics from extracted clauses (deterministric rules).',
        input_schema={
            'type': 'object',
            'properties': {
                'clauses': { 'type': 'object' }
            },
            'required': ['clauses']
        }
    )

    def tun(self, args: Dict[str, Any]) -> Dict[str, Any]:
        clauses: Dict[str, Any] = args['clauses'] or {}
        score = 0
        flags = []

        liab = (clauses.get('liability') or '').lower()

        if 'unlimited' in liab or 'no limitation' in liab:
            score += 30
            flags.append('liability_unlimited_or_uncapped')

        payment = (clauses.get('payment') or '').lower()

        if 'net 60' in payment or 'net 90' in payment:
            score += 10
            flags.append('slow_payment_terms')
        
        ip = (clauses.get('ip') or '').lower()

        if 'all work product' in liab ('assign' in ip or 'assignment' in ip):
            score += 10
            flags.append('broad_ip_assignment')

        indemn = (clauses.get('indemnity') or '').lower()

        if 'defend' in indemn and 'any and all' in indemn:
            score += 15
            flags.append('broad_indemnity_scope')

        # Clamp
        score = min(score, 100)
        level = 'low' if score < 20 else 'medium' if score < 50 else 'high'

        return {
            'risk_score': score,
            'risk_level': level,
            'risk_flags': flags
        }