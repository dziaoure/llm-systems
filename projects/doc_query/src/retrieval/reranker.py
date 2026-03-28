from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any, Dict, List

from src.models.retrieval import RetrievedChunk


STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'if', 'then', 'of', 'in', 'on', 'to',
    'for', 'with', 'by', 'at', 'from', 'is', 'are', 'was', 'were', 'be', 'as',
    'this', 'that', 'these', 'those', 'what', 'which', 'who', 'whom', 'when',
    'where', 'why', 'how', 'it', 'its', 'into', 'about', 'under', 'over'
}

@dataclass
class RerankerChunk:
    chunk_id: str
    document_id: str
    text: str
    source: str
    page_number: int
    section_title: str
    semantic_score: float
    keyword_score: float
    exact_match_score: float
    #heading_bonus: float
    position_bonus: float
    final_score: float
    metadata: Dict[str, Any]


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'\s+', '', text)
    return text.strip()


def tokenize(text: str) -> List[str]:
    text = normalize_text(text)
    tokens = re.findall(f'\b[a-z0-9]+\b', text)
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 1]


def keyword_overlap_score(query: str, chunk_text: str) -> float:
    q_tokens = set(tokenize(query))
    c_tokens = set(tokenize(chunk_text))

    if not q_tokens:
        return 0.0
    
    overlap = q_tokens.intersection(c_tokens)
    return len(overlap) / len(q_tokens)


def exact_match_score(query: str, chunk_text: str) -> float:
    query_norm = normalize_text(query)
    chunk_norm = normalize_text(chunk_text)

    if query_norm in chunk_norm:
        return 1.0
    
    query_tokens = tokenize(query)

    if len(query_tokens) >= 2:
        for i in range(len(query_tokens) - 1):
            phrase = ' '.join(query_tokens[i:i + 2])

            if phrase in chunk_norm:
                return 0.6
            
    return 0.0


def position_bonus(metadata: Dict[str, Any]) -> float:
    chunk_index = metadata.get('chunk_index')

    if chunk_index is None:
        return 0.0
    
    return max(0.0, 1.0 - (chunk_index / 2.0))


def min_max_normalize(values: List[float]) -> List[float]:
    if not values:
        return []
    
    min_v = min(values)
    max_v = max(values)

    if math.isclose(min_v, max_v):
        return [1.0 for _ in values]
    
    return [(v - min_v) / (max_v - min_v) for v in values]


def rerank_chunks(query: str, chunks: List[RetrievedChunk]) -> List[RerankerChunk]:
    if not chunks:
        return []
    
    semantic_scores = [chunk.score for chunk in chunks]
    semantic_scores = min_max_normalize(semantic_scores)

    reranked: List[RetrievedChunk] = []

    for chunk, semantic_score in zip(chunks, semantic_scores):
        kw_score = keyword_overlap_score(query, chunk.text)
        ex_score = exact_match_score(query, chunk.text)
        p_bonus = position_bonus(chunk.metadata)

        final_score = (
            0.65 * semantic_score +
            0.25 * kw_score +
            0.05 * ex_score +
            0.05 * p_bonus
        )

        reranked.append(
            RerankerChunk(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                text=chunk.text,
                source=chunk.filename,
                page_number=chunk.page_number,
                section_title=chunk.section_title,
                semantic_score=semantic_score,
                keyword_score=kw_score,
                exact_match_score=ex_score,
                position_bonus=p_bonus,
                final_score=final_score,
                metadata=chunk.metadata
            )
        )

    reranked.sort(key=lambda c: c.final_score, reverse=True)
    return reranked