from __future__ import annotations

from src.config import get_settings
from src.models.retrieval import RetrievedChunk
from src.retrieval.embeddings import EmbeddingClient
from src.retrieval.vector_store import FaissVectorStore
from src.retrieval.reranker import RerankerChunk, rerank_chunks, expand_with_neighbors


class Retriever:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.embedding_client = EmbeddingClient()
        self.vector_store = FaissVectorStore()


    def retrieve(
        self,
        question: str,
        top_k: int | None = None
    ) -> list[RetrievedChunk]:
        if not question or not question.strip():
            raise ValueError('Question must not be empty')
        
        effective_top_k = top_k or self.settings.retrieval.default_top_k
        effective_top_k = min(effective_top_k, self.settings.retrieval.max_top_k)

        initial_top_k = self.settings.retrieval.default_initial_top_k
        initial_top_k = min(initial_top_k, self.settings.retrieval.max_top_k)

        # Step 1: Embed query
        query_vector = self.embedding_client.embed_query(question)

        # Step 2: Initial retrieval (recall stage)
        scores, indices = self.vector_store.search(query_vector, initial_top_k)

        # Step 3: Build `RetrievedChunk` objects`
        metadata = self.vector_store.load_metadata()
        chunks = metadata.get('chunks', [])

        retrieved_chunks: list[RetrievedChunk] = []

        if len(indices) == 0 or len(indices[0]) == 0:
            return retrieved_chunks
        
        for score, idx in zip(scores[0], indices[0]):
            chunk_data = chunks[idx]['chunk']

            retrieved_chunks.append(
                RetrievedChunk(
                    chunk_id=chunk_data['chunk_id'],
                    document_id=chunk_data['document_id'],
                    filename=chunk_data.get('filename', 'unknown'),
                    text=chunk_data['text'],
                    score=float(score),
                    rank=chunk_data['chunk_index'],
                    page_number=chunk_data['page_number'],
                    section_title=chunk_data.get('section_title', 'N/A'),
                    metadata=chunk_data.get('metadata', {})
                )
            )

        # Step 4: Rerank
        reranked: list[RerankerChunk] = rerank_chunks(question, retrieved_chunks)

        # Step 5: Select final chunks for LLM
        final_top_k = self.settings.retrieval.default_final_top_k
        selected: list[RerankerChunk] = reranked[:final_top_k]

        # Expand the selection to include neighbors
        expanded_selection: list[RerankerChunk] = expand_with_neighbors(selected, reranked)

        # Step 6: Reorder by document order
        expanded_selection = sorted(
            expanded_selection,
            key=lambda c: (
                c.metadata.get('page') if c.metadata.get('page') is not None else 0,
                c.metadata.get('chunk_index', 0)
            )
        )

        top_chunks: list[RetrievedChunk] = []

        for i, chunk in enumerate(expanded_selection, start=1):
            top_chunks.append(
                RetrievedChunk(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    filename=chunk.source,
                    text=chunk.text,
                    score=chunk.final_score,
                    rank=i,
                    page_number=chunk.page_number,
                    section_title=chunk.section_title,
                    metadata=chunk.metadata
                )
            )

        return top_chunks