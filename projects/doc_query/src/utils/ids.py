import hashlib
from pathlib import Path


def make_document_id(file_path: str) -> str:
    normalized = str(Path(file_path).as_posix()).encode('utf-8')
    digest = hashlib.sha1(normalized).hexdigest()[:8]
    return f'doc{digest}'


def make_chunk_id(document_id: str, chunk_index: int) -> str:
    return f'{document_id}_chunk_{chunk_index:04d}'


def make_request_id() -> str:
    import uuid

    return f'req_{uuid.uuid4().hex[:12]}'
