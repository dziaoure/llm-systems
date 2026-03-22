from src.models.citation import CitationRecord
from src.retrieval.retriever import Retriever
from src.schemas.query import QueryRequest, QueryResponse


class QueryService:
    def __init__(self) -> None:
        self.retriever = Retriever()


    def query(self, request: QueryRequest) -> QueryResponse:
        retrieved_chunks = self.retriever.retrieve(
            question=request.question,
            top_k=request.top_k,
            min_score=request.min_score
        )

        citations = [
            CitationRecord(
                chunk_id=chunk.chunk_id,
                filename=chunk.filename,
                page_number=chunk.page_number,
                section_title=chunk.section_title,
                snippet=chunk.text[:300],
                rank=chunk.rank
            )
            for chunk in retrieved_chunks
        ]

        answer = (
            'Retrieval completed successsfully. Genertion will be added later.'
            if retrieved_chunks
            else 'No sufficiently relevant supporting chunks were found.'
        )

        return QueryResponse(
            question=request.question,
            answer=answer,
            grounded=bool(retrieved_chunks),
            citations=citations,
            reason_if_unanswered=None if retrieved_chunks else 'insufficient_evidence',
            retrieved_chunks=retrieved_chunks if request.return_snippets else [],
            latency_ms=0.0
        )