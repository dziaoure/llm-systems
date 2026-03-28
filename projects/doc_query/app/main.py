from __future__ import annotations

from fastapi import FastAPI, HTTPException

from src.config import get_settings
from src.ingest.catalog import list_document_entries
from src.observability.logging import get_logger
from src.schemas.ingest import IngestRequest, IngestResponse
from src.schemas.query import QueryRequest, QueryResponse
from src.services.ingest_service import IngestService
from src.services.query_service import QueryService


settings = get_settings()
logger = get_logger('docquery.api')

app = FastAPI(
    title='DocQuery API',
    description='Ask questions. Get answers. See the source.',
    version='1.0.0'
)

ingest_service = IngestService()
query_service = QueryService()


@app.get('/health')
def health() -> dict:
    return {
        'status': 'ok',
        'app': settings.app.name,
        'environment': settings.app.environment
    }

@app.get('/documents')
def list_documents() -> dict:
    return {'documents': list_document_entries()}

@app.post('/ingest', response_model=IngestResponse)
def ingest_documents(request: IngestRequest) -> IngestResponse:
    try:
        
        return ingest_service.ingest(request)
    
    except Exception as exc:
        logger.exception('Ingestion failed: %s', exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    

@app.post('/query', response_model=QueryResponse)
def query_documents(request: QueryRequest) -> QueryResponse:
    try:

        return query_service.query(request)
    
    except Exception as exc:
        logger.exception('Query failed: %s', exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
