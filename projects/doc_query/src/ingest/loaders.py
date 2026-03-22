from pathlib import Path

from markdown import markdown
from pypdf import PdfReader

from src.constants import DEFAULT_TEXT_ENCODING, SUPPORTED_FILE_TYPES


def is_supported_file(file_path: Path) -> bool:
    return Path(file_path).suffix.lower() in SUPPORTED_FILE_TYPES


def load_document(file_path: str) -> dict:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f'File not found: {file_path}')
    
    suffix = path.suffix.lower()

    if suffix not in SUPPORTED_FILE_TYPES:
        raise ValueError(f'Unsupported file type: {suffix}')
    
    if suffix == '.pdf':
        return _load_pdf(path)
    
    if suffix == '.txt':
        return _load_txt(path)
    
    if suffix == '.md':
        return _load_md(path)
    
    raise ValueError(f'No loader implemented for file type: {suffix}')


def _load_pdf(path: Path)-> dict:
    reader = PdfReader(str(path))
    pages = []

    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ''
        pages.append({
            'page_number': i,
            'text': text
        })

    return {
        'file_path': str(path),
        'filename': path.name,
        'file_type': path.suffix.lower(),
        'title': path.stem,
        'pages': pages
    }


def _load_text(path: Path) -> dict:
    text = path.read_text(encoding=DEFAULT_TEXT_ENCODING)

    return {
        'file_path': str(path),
        'filename': path.name,
        'file_type': path.suffix.lower(),
        'title': path.stem,
        'pages': [
            {
                'page_number': None,
                'text': text
            }
        ]
    }


def _load_md(path: Path) -> dict:
    raw_text = path.read_text(encoding=DEFAULT_TEXT_ENCODING)

    # Simple strategy: preserve readable markdown-derived text
    html = markdown(raw_text)
    text = _strip_html_tags(html)

    return  {
        'file_path': str(path),
        'filename': path.name,
        'file_type': path.suffix.lower(),
        'title': path.stem,
        'pages': [
            {
                'page_number': None,
                'text': text
            }
        ]
    }


def _strip_html_tags(html: str) -> str:
    import re

    text = re.sub(f'<[^>]+>', ' ', html)
    return text