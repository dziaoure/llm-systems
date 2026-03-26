from __future__ import annotations

from src.models.retrieval import RetrievedChunk


def format_context(chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return 'No supporting context was retrieved'
    
    parts: list[str] = []

    for chunk in chunks:
        header = (
            f'[Chunk {chunk.rank}] '
            f'Source={chunk.filename}'
            f', Page={chunk.page_number if chunk.page_number is not None else "N/A"}'
        )
        parts.append(f'{header}\n{chunk.text}')

    return '\n\n'.join(parts)


def build_grounded_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    context = format_context(chunks)

    return f"""
    You are DocQuery, a grounded document question-answering assistant.

    Answer the user's question using ONLY the provided context chunks below.
    Do not use outside knowledge.
    If the context is insufficient, say so clearly.
    Return ONLY valid JSON.
    Do not wrap the JSON in markdown fences.

    Required JSON schema:
    {{
        "answer": "string",
        "grounded": true or false,
        "used_chuk=nk_ranks": [integer, ...],
        "reason_if_unanswered": "string or null"
    }}

    Rules:
    - grounded=true only if the answer is directly supported by the context.
    - If the context does not contain enough evidence, return:
      - a short refusal-style answer,
      - grounded=false,
      - used_chunk_ranks=[]
      - reason_if_unanswered="insufficient_evidence"
    - used_chunk_ranks must reference only the chunk numbers shown in the context.
    - Keep the answer concise and factual

    User question:
    {question}

    Context:
    {context}
    """.strip()