from __future__ import annotations
from typing import List


def chunk_text(text: str, *, chunk_size: int = 3500, overlap: int = 300) -> List[str]:
    '''
    Simple character chunker
    '''
    text = text.strip()

    if not text:
        return []
    
    chunks = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)
        
        if end == n:
            break

        start = max(0, end - overlap)

    return chunks