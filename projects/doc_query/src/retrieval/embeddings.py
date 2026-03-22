from __future__ import annotations

import os
from typing import Sequence

import numpy as np
import google.genai as genai

from src.config import get_settings


class EmbeddingClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        api_key = os.getenv(self.settings.models.api_key_env_var)

        if not api_key:
            raise ValueError(
                f'Missing API key in environment variable: {self.settings.models.api_key_env_var}'
            )
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = self.settings.models.embedding_model
        self.embedding_dimension = self.settings.models.embedding_dimension

    def embed_text(self, text: str) -> np.ndarray:
        if not text or not text.strip():
            raise ValueError('Cannot embed empty text')
        
        response = self.client.models.embed_content(
            model=self.model_name,
            contents=text
        )

        vector = np.array(response.embeddings[0].values, dtype=np.float32)
        return normalize_vector(vector)
    

    def embed_query(self, query: str) -> np.ndarray:
        if not query or not query.strip():
            raise ValueError('Cannot embed empty query')
        
        response = self.client.models.embed_content(
            model=self.model_name,
            contents=query
        )

        vector = np.array(response.embeddings[0].values, dtype=np.float32)
        return normalize_vector(vector)
    

    def embed_texts(self, texts: Sequence[str]) -> np.ndarray:
        vectors = [self.embed_text(text) for text in texts]

        if not vectors:
            return np.empty((0, self.embedding_dimension), dtype=np.float32)
        
        return np.vstack(vectors)
    

    def get_embedding_dimension(self) -> int:
        test_vector = self.embed_text('test')
        return test_vector.shape[0]
    

def normalize_vector(vector: np.array) -> np.ndarray:
    norm = np.linalg.norm(vector)

    if norm == 0:
        return vector
    
    return vector / norm