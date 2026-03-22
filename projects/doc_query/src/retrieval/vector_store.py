from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from src.config import get_settings
from src.models.chunk import ChunkRecord


class FaissVectorStore:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.index_path = self.settings.paths.faiss_index_path
        self.metadata_path = self.settings.paths.index_metadata_path
        self.dimension = self.settings.models.embedding_dimension

        self.index_path.parent.mkdir(parents=True, exist_ok=True)

    def create_index(self) -> faiss.Index:
        return faiss.IndexFlatIP(self.dimension)
    

    def load_or_create_index(self) -> faiss.Index:
        if self.index_path.exists():
            return faiss.read_index(str(self.index_path))
        
        return self.create_index()
    

    def save_index(self, index: faiss.Index) -> None:
        faiss.write_index(index, str(self.index_path))

    
    def load_metadata(self) -> dict[str, Any]:
        if not self.metadata_path.exists():
            return {
                'dimension': self.dimension,
                'count': 0,
                'chunks': []
            }
        
        return json.loads(self.metadata_path.read_text(encoding='utf-8'))
    

    def save_metadata(self, metadata: dict[str, Any]) -> None:
        self.metadata_path.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )


    def rebuild(
        self,
        chunks: list[ChunkRecord],
        embeddings: np.ndarray
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError('chunks and embeddings must have tje same length')
        
        if embeddings.shape[1] != self.dimension:
            raise ValueError(
                f'Embedding dimension mismatch: expected {self.dimension}, got {embeddings.shape[1]}'
            )
        
        index = self.create_index()

        if len(embeddings) > 0:
            index.add(embeddings.astype(np.float32))

        metadata = {
            'dimension': self.dimension,
            'count': len(chunks),
            'chunks': [
                {
                    'faiss_id': i,
                    'chunk': chunk.model_dump(mode='json')
                }
                for i, chunk in enumerate(chunks)
            ]
        }

        self.save_index(index)
        self.save_metadata(metadata)


    def search(self, query_vector: np.ndarray, top_k: int) -> tuple[np.ndarray, np.ndarray]:
        index = self.load_or_create_index()

        if index.ntotal == 0:
            return (
                np.ndarray([[]], dtype=np.float32),
                np.ndarray([[]], dtype=np.int64)
            )
        
        query_matrix = np.expand_dims(query_vector.astype(np.float32), axis=0)
        scores, indices = index.search(query_matrix, top_k)
        return scores, indices