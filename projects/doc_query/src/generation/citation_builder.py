from __future__ import annotations

from src.models.citation import CitationRecord
from src.models.retrieval import RetrievedChunk


def build_citations(
    retrieved_chunks: list[RetrievedChunk],
    used_chunk_ranks: list[int],
    snippet_length: int = 300
) -> list[CitationRecord]:
    if not retrieved_chunks or not used_chunk_ranks:
        return []
    
    chunk_by_rank = {chunk.rank: chunk for chunk in retrieved_chunks}
    citations: list[CitationRecord] = []

    for rank in used_chunk_ranks:
        chunk = chunk_by_rank.get(rank)

        if chunk is None:
            continue

        citations.append(
            CitationRecord(
                chunk_id=chunk.chunk_id,
                filename=chunk.filename,
                page_number=chunk.page_number,
                section_title=chunk.section_title,
                snippet=chunk.text[:snippet_length].strip(),
                rank=chunk.rank
            )
        )

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_citations: list[CitationRecord] = []

    for citation in citations:
        if citation.chunk_id in seen:
            continue

        seen.add(citation.chunk_id)
        unique_citations.append(citation)

    return unique_citations