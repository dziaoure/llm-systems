from pathlib import Path

from src.config import get_settings
from src.ingest.pipeline import ingest_paths
from src.schemas.ingest import IngestRequest, IngestResponse
from src.retrieval.vector_store import FaissVectorStore
from src.retrieval.embeddings import EmbeddingClient
from src.utils.files import load_all_processed_chunks


class IngestService:

    def __int__(self) -> None:
        self.settings = get_settings()
        self.embedding_client = EmbeddingClient()
        self.vector_store = FaissVectorStore()

    def ingest(self, request: IngestRequest) -> IngestResponse:
        valid_paths = [str(Path(path)) for path in request.paths]

        documents, chunks = ingest_paths(valid_paths, self.settings)

        all_chunks = load_all_processed_chunks()
        all_texts = [chunk.text for chunk in all_chunks]
        embeddings = self.embedding_client.embed_texts(all_texts)
        self.vector_store.rebuild(all_chunks, embeddings)

        return IngestResponse(
            success=True,
            documents_ingested=len(documents),
            chunks_created=len(chunks),
            index_path=str(self.settings.paths.processed_data_dir),
            message=(
                f'Ingested {len(documents)} document(s) and created {len(chunks)} chunk(s), '
                f'and rebuilt vector index with {len(all_chunks)} total chunks'
            )
        )