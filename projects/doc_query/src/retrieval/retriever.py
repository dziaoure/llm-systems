from __future__ import annotations

from src.config import get_settings
from src.models.retrieval import RetrievedChunk
from src.retrieval.embeddings import EmbeddingClient
from src.retrieval.vector_store import FaissVectorStore


class Retriever:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.embedding_client = EmbeddingClient()
        self.vector_store = FaissVectorStore()


    def retrieve(
        self,
        question: str,
        top_k: int | None = None,
        min_score: float | None = None
    ) -> list[RetrievedChunk]:
        if not question or not question.strip():
            raise ValueError('Question must not be empty')
        
        effective_top_k = top_k or self.settings.retrieval.default_top_k
        effective_top_k = min(effective_top_k, self.settings.retrieval.max_top_k)

        effective_min_score = (
            min_score
            if min_score is not None
            else self.settings.retrieval.min_similarity_threshold
        )

        query_vector = self.embedding_client.embed_query(question)
        scores, indices = self.vector_store.search(query_vector, effective_top_k)
        metadata = self.vector_store.load_metadata()
        chunks = metadata.get('chunks', [])

        results: list[RetrievedChunk] = []

        if len(indices) == 0 or len(indices[0]) == 0:
            return results
        
        for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), start=1):
            if idx < 0:
                continue

            if idx >= len(chunks):
                continue

            if score < effective_min_score:
                continue

            chunk_payload = chunks[idx]['chunk']

            results.append(
                RetrievedChunk(
                    chunk_id=chunk_payload['chunk_id'],
                    document_id=chunk_payload['document_id'],
                    filename=chunk_payload['filename'],
                    text=chunk_payload['text'],
                    score=float(score),
                    rank=rank,
                    page_number=chunk_payload.get('page_number'),
                    section_title=chunk_payload.get('section_title'),
                    metadata=chunk_payload.get('metadata', {})
                )
            )

        return results