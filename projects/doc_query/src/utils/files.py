import json
from pathlib import Path

from src.config import get_settings
from src.models.chunk import ChunkRecord


def load_all_processed_chunks() -> list[ChunkRecord]:
    settings = get_settings()
    processed_dir = settings.paths.processed_data_dir

    if not processed_dir.exists():
        return []
    
    chunks: list[ChunkRecord] = []

    for path in processed_dir.glob('doc_*.json'):
        payload = json.loads(path.read_text(encoding='utf-8'))

        for chunk_data in payload.get('chunks', []):
            chunks.append(ChunkRecord(**chunk_data))

    return chunks