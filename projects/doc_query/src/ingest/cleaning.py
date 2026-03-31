import re

def clean_text(text: str) -> str:
    if not text:
        return ''
    
    cleaned = text.replace('\x00', ' ')
    cleaned = cleaned.replace('\r\n', '\n').replace('\r', '\n')
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    cleaned = re.sub(r' ?\n ?', '\n', cleaned)
    cleaned = cleaned.strip()

    return cleaned


def clean_pages(pages: list[dict]) -> list[dict]:
    cleaned_pages = []

    for page in pages:
        cleaned_text = clean_text(page.get('text', ''))

        if cleaned_text:
            cleaned_pages.append({
                'page_number': page.get('page_number'),
                'text': cleaned_text
            })

    return cleaned_pages
