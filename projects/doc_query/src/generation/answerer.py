from __future__ import annotations

import os
from time import perf_counter

from google import genai

from src.config import get_settings
from src.generation.guardrails import extract_json_object, validate_generation_payload
from src.generation.prompts import build_grounded_prompt
from src.models.query import AnswerRecord
from src.models.retrieval import RetrievedChunk


class Answerer:
    def __init__(self) -> None:
        self.settings = get_settings()
        api_key = os.getenv(self.settings.models.api_key_env_var)

        if not api_key:
            raise ValueError(
                f'Missing API key in environment variable: {self.settings.models.api_key_env_var}'
            )
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = self.settings.models.generation_model

    def answer(
        self,
        question: str,
        retrieved_chunks: list[RetrievedChunk]
    ) -> tuple[AnswerRecord, list[int]]:
        start_time = perf_counter()

        if not retrieved_chunks:
            latency_ms = (perf_counter() - start_time) * 1000
            answer_record = AnswerRecord(
                question=question,
                answer='I could not find enough support in the indexed documents to answer that confidently',
                grounded=False,
                citations=[],
                reason_if_unanswered='insufficient_evidence',
                retrieved_chunks=[],
                latency_ms=latency_ms
            )

            return answer_record, []
        
        prompt = build_grounded_prompt(question, retrieved_chunks)

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )

        raw_text = response.text or ''
        payload = validate_generation_payload(extract_json_object(raw_text))

        latency_ms = (perf_counter() - start_time) * 1000

        answer_record = AnswerRecord(
            question=question,
            answer=payload['answer'].strip(),
            grounded=payload['grounded'],
            citations=[],
            reason_if_unanswered=payload['reason_if_unanswered'],
            retrieved_chunks=retrieved_chunks,
            latency_ms=latency_ms
        )

        return answer_record, payload['used_chunk_ranks']