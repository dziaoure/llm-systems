from string import Template


SYSTEM_PROMPT = """
    You are a contract analysis assistant.

    Your task is to extract structured information from contracts.
    You must return valid JSON only.
    Do not include explanations outside the JSON object.
    If a field is unknown, set it to null.
""".strip()

USER_TEMPLATE = Template("""
Analyze the following contract text and extract structured data.

---BEGIN CONTRACT---
$contract_text
---END CONTRACT---

Return JSON in the following format:

{
    "executive_summary": string,
    "key_parties": [string],
    "effective_date": string | null,
    "termination_clause": string | null,
    "risk_flags": [
        {
            "type": string,
            "severity": "low" | "medium" | "high",
            "explanation": string
        }
    ],
    "confidence": string
}
""".strip())
