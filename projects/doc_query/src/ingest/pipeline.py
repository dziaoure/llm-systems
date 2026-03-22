import json
from pathlib import Path

from src.config import Settings
from src.ingest.catalog import upsert_document_record
from src.ingest.chunking import build_chunk_records
from src.ingest.cleaning import clean_pages
from src.ingest.loaders import load_document
from src.models.document import DocumentRecord
from src.utils.ids import make_document_id


def ingest_file(file_path: str, settings: Settings) -> tuple[DocumentRecord, list]:
    loaded = load_document(file_path)
    cleaned_pages = clean_pages(loaded['pages'])

    document_id = make_document_id(file_path)

    chunks = build_chunk_records(
        document_id=document_id,
        filename=loaded['filename'],
        pages=cleaned_pages,
        chunk_size=settings.chunking.chunk_size,
        chunk_overlap=settings.chunking.chunk_overlap,
        min_chunk_chars=settings.chunking.min_chunk_chars
    )

    document = DocumentRecord(
        document_id=document_id,
        filename=loaded['filename'],
        file_path=loaded['file_path'],
        file_type=loaded['file_type'],
        title=loaded['title'],
        num_pages=len(cleaned_pages) if loaded['file_type'] == '.pdf' else None,
        num_chunks=len(chunks),
        metadata={}
    )

    processed_path = _save_processed_document(document, chunks, settings)
    upsert_document_record(document, processed_path)

    return document, chunks


def ingest_paths(file_paths: list[str], settings: Settings) -> tuple[list[DocumentRecord], list]:
    documents = []
    all_chunks = []

    for file_path in file_paths:
        document, chunks = ingest_file(file_path, settings)
        documents.append(document)
        all_chunks.extend(chunks)

    return documents, all_chunks


def _save_processed_document(document: DocumentRecord, chunks: list, settings: Settings) -> str:
    settings.paths.processed_data_dir.mkdir(parents=True, exist_ok=True)

    output_path = settings.paths.processed_data_dir / f'{document.document_id}.json'

    payload = {
        'document': document.model_dump(mode='json'),
        'chunks': [chunk.model_dump(mode='json') for chunk in chunks]
    }

    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )

    return str(output_path)