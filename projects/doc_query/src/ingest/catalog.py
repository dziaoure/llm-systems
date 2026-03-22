import json
from pathlib import Path

from src.config import get_settings
from src.models.document import DocumentRecord

CATALOG_FILENAME = 'catalog.json'


def get_catalog_path() -> Path:
    settings = get_settings()
    settings.paths.processed_data_dir.mkdir(parents=True, exist_ok=True)
    return settings.paths.processed_data_dir / CATALOG_FILENAME


def load_catalog() -> dict:
    catalog_path = get_catalog_path()

    if not catalog_path.exists():
        return { 'documents': []}
    
    return json.loads(catalog_path.read_text(encoding='utf-8'))


def save_catalog(catalog: dict) -> None:
    catalog_path = get_catalog_path()
    catalog_path.write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )


def upsert_document_record(document: DocumentRecord, processed_path: str) -> None:
    catalog = load_catalog()
    documents = catalog.get('documents', [])

    new_entry = {
        'document_id': document.document_id,
        'filename': document.filename,
        'file_path': document.file_path,
        'file_type': document.file_type,
        'title': document.title,
        'ingested_at': document.ingested_at.isoformat(),
        'num_pages': document.num_pages,
        'num_chunks': document.num_chunks,
        'processed_path': processed_path,
        'metadata': document.metadata
    }

    existing_index = next(
        (i for i, d in enumerate(documents) if d['document_id'] == document.document_id),
        None
    )

    if existing_index is None:
        documents.append(new_entry)
    else:
        documents[existing_index] = new_entry

    catalog['documents'] = documents
    save_catalog(catalog)