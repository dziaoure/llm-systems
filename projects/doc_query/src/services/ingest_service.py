from pathlib import Path

from src.config import get_settings
from src.ingest.pipeline import ingest_paths
from src.schemas.ingest import IngestRequest, IngestResponse

class IngestService:

    def __int__(self) -> None:
        self.settings = get_settings()

    def ingest(self, request: IngestRequest) -> IngestResponse:
        valid_paths = [str(Path(path)) for path in request.paths]

        documents, chunks = ingest_paths(valid_paths, self.settings)

        return IngestResponse(
            success=True,
            documents_ingested=len(documents),
            chunks_created=len(chunks),
            index_path=str(self.settings.paths.processed_data_dir),
            message=f'Ingested {len(documents)} document(s) and created {len(chunks)} chunk(s).'
        )