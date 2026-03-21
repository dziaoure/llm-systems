from src.schemas.ingest import IngestRequest, IngestResponse

class IngestService:
    def ingest(self, request: IngestRequest) -> IngestResponse:
        raise NotImplementedError('IngestService.ingest is not yet implemented')