from pathlib import Path

APP_NAME = 'DocQuery'

SUPPORTED_FILE_TYPES = {'.pdf', '.txt', '.md'}
DEFAULT_TEXT_ENCODING = 'utf-8'

FALLBACK_SECTION_TITLE = 'Unknown Section'

DEFAULT_PAGE_NUMBER = None

DATA_DIR = Path('data')
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
INDEX_DIR = DATA_DIR / 'index'
EVAL_DIR = DATA_DIR / 'eval'

LOGS_DIR = Path('logs')