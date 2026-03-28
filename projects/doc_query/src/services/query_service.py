from __future__ import annotations

from src.generation.answerer import Answerer
from src.generation.citation_builder import build_citations
from src.models.query import QueryTrace
from src.observability.logging import get_logger
from src.observability.tracing import persist_query_trace
from src.retrieval.retriever import Retriever
from src.schemas.query import QueryRequest, QueryResponse
from src.utils.ids import make_request_id


class QueryService:
    def __init__(self) -> None:
        self.retriever = Retriever()
        self.answerer = Answerer()
        self.logger = get_logger('docquery.query')


    def query(self, request: QueryRequest) -> QueryResponse:
        request_id = make_request_id()
        self.logger.info('Starting query request_id=%s question=%s', request_id, request.question)

        retrieved_chunks = self.retriever.retrieve(
            question=request.question,
            top_k=request.top_k,
            min_score=request.min_score
        )

        answer_record, used_chunk_ranks = self.answerer.answer(
            question=request.question,
            retrieved_chunks=retrieved_chunks
        )

        citations = build_citations(
            retrieved_chunks=retrieved_chunks,
            used_chunk_ranks=used_chunk_ranks
        )

        answer_record.cirations = citations

        trace = QueryTrace(
            request_id=request_id,
            question=request.question,
            retrieved_chunk_ids=[chunk.chunk_id for chunk in retrieved_chunks],
            retrieval_scores=[chunk.score for chunk in retrieved_chunks],
            grounded=answer_record.grounded,
            citations=citations,
            latency_ms=answer_record.latency_ms,
            prompt_version='v1',
            metadata={'used_chunk_ranks': used_chunk_ranks}
        )

        persist_query_trace(trace)

        self.logger.info(
            'Completed query request_id=%s grounded=%s citations=%d latency_ms=%.2f',
            request_id,
            answer_record.grounded,
            len(citations),
            answer_record.latency_ms
        )

        return QueryResponse(
            question=answer_record.question,
            answer=answer_record.answer,
            grounded=answer_record.grounded,
            citations=citations,
            reason_if_unanswered=answer_record.reason_if_unanswered,
            retrieved_chunks=retrieved_chunks if request.return_snippets else [],
            latency_ms=answer_record.latency_ms
        )