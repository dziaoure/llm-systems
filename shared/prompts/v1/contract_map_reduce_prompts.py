from string import Template

MAP_SYSTEM = """
    You are a contract analysis assistant.
    Summarize ONLY the information explicitly present in the text.
    Return plain text (no JSON).
""".strip()

MAP_USER = Template("""
    Summarize the following contract chunk. Focus on:
    - Parties
    - Dates
    - Termination terms
    - Liability / indemnity / payment / confidentiality highlights
    - Any obvious risks

    ---BEGIN CHUNK---
    $chunk
    ---END CHUNK---

    Return a concise bullet list.
""".strip())

REDUCE_SYSTEM = """
    You are a contract analysis assistant.
    You will be given multiple chunk summaries from a contract.
    Return ONLY valid JSON. No markdown. No backticks.
    If unknown, set null.
""".strip()

REDUCE_USER = Template("""
    Combine the following chunk summaries into a single structured contract analysis.

    ---BEGIN CHUNK SUMMARIES---
    $summaries
    ---END CHUNK SUMMARIES---

    Return JSON in this format:

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
    "confidence": "low" | "medium" | "high"
    }
""".strip())
