from __future__ import annotations

from typing import Optional
from io import BytesIO
from pypdf import PdfReader

def extract_text_from_pdf_bytes(pdf_bytes: bytes, *, max_pages: Optional[int] = None) -> str:
    stream = BytesIO(pdf_bytes)
    reader = PdfReader(stream)

    texts = []
    num_pages = len(reader.pages)
    limit = num_pages if max_pages is None else min(max_pages, num_pages)

    for i in range(limit):
        page = reader.pages[i]
        page_text = page.extract_text() or ''

        if page_text.strip():
            texts.append(page_text)
    
    return '\n'.join(texts).strip()

