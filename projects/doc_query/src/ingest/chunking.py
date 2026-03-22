from src.models.chunk import ChunkRecord
from src.utils.ids import make_chunk_id


def chunk_text(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
    min_chunk_chars: int
) -> list[dict]:
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk_text_value = text[start:end].strip()

        if len(chunk_text_value) >= min_chunk_chars:
            chunks.append({
                'text': chunk_text_value,
                'start_char': start,
                'end_char': end
            })

        if end >= text_length:
            break

        start = max(end - chunk_overlap, start + 1)
    
    return chunks


def build_chunk_records(
    document_id: str,
    filename: str,
    pages: list[dict],
    chunk_size: int,
    chunk_overlap: int,
    min_chunk_chars: int
) -> list[ChunkRecord]:
    records: list[ChunkRecord] = []
    chunk_index = 0

    for page in pages:
        page_number = page.get('page_number')
        page_text = page.get('text', '')

        page_chunks = chunk_text(
            text=page_text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            min_chunk_chars=min_chunk_chars
        )

        for page_chunk in page_chunks:
            records.append(
                ChunkRecord(
                    chunk_id=make_chunk_id(document_id, chunk_index),
                    document_id=document_id,
                    filename=filename,
                    text=page_chunk['text'],
                    chunk_index=chunk_index,
                    page_number=page_number,
                    section_title=None,
                    token_count=None,
                    start_char=page_chunk['start_char'],
                    end_char=page_chunk['end_char'],
                    metadata={}
                )
            )
            chunk_index += 1

    return records