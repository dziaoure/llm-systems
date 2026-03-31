from __future__ import annotations

import sys

import tempfile
from pathlib import Path
from typing import Any

import streamlit as st

# Ensure repo root is on `sys.path` so `import shared` works
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import get_settings
from src.ingest.pipeline import ingest_paths
from src.services.ingest_service import IngestService
from src.schemas.ingest import IngestRequest
from src.schemas.query import QueryRequest, QueryResponse
from src.models.citation import CitationRecord
from src.models.retrieval import RetrievedChunk
from src.services.query_service import QueryService


TOP_K = 5
MIN_SCORE = None

st.set_page_config(page_title="DocQuery", layout="centered")

def load_css():
    css_path = Path(__file__).resolve().parents[2] / 'styles' / "main.css"

    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html = True)

load_css()

def init_session_state() -> None:
    if 'ingested' not in st.session_state:
        st.session_state.ingested = False

    if 'last_ingestion_summary' not in st.session_state:
        st.session_state.last_ingestion_summary = None

    if 'last_response' not in st.session_state:
        st.session_state.last_response = None


def save_uploaded_files(uploaded_files: list[Any]) -> list[Path]:
    saved_paths: list[Path] = []

    for uploaded_file in uploaded_files:
        suffix = Path(uploaded_file.name).suffix or '.txt'

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            saved_paths.append(Path(tmp.name))

    return saved_paths


def render_header() -> None:
    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        image_path = PROJECT_ROOT / 'images/search-icon.png'
        st.image(image_path, width=120)

    st.title("DocQuery")

    caption_html = """
        <p style="text-align: center;color:#fff; opacity:0.65; margin-top: 0;">
        Ask questions. Get answers. See the source.
        </p>
        <p style="text-align: center;color:#fff; opacity:0.65; margin-top: 0;">
        Upload documents and ask questions. DocQuery retrieves relevant sections, reranks them, and generates verified answers with citations.
        </p>
        <p style="text-align: center;color:#fff; opacity:0.65; margin-top: 0;">
            Powered by Gemini 2.5 Flash
        </p>
        """
    st.markdown(caption_html, unsafe_allow_html=True)


def render_sidebar() -> tuple[list[Any], str]:
    with st.sidebar:
        st.header('Documents')

        uploaded_files = st.file_uploader(
            'Upload PDF or text documents',
            type=['pdf', 'txt', 'md'],
            accept_multiple_files=True
        )

        st.markdown('---')
        st.header('Examples')

        sample_questions = [
            'What are the parties in this agreement?',
            'What is the effective date of the agreement?',
            'What is considered confidential information?',
            'How long do confidentiality obligations survive?',
            'What law governs this agreement?'
        ]

        selected_question = st.selectbox(
            'Try a sample question',
            options=[''] + sample_questions,
            index=0
        )

        st.markdown("---")
        st.header("System Architecture")

        with st.expander("View Architecture"):
            st.markdown(
                """
                **LLM System Overview**

                - **LLM:** Gemini 2.5 Flash  
                - **Embeddings:** Gemini embedding-001 (768-dim)  
                - **Vector Store:** FAISS  
                - **Retrieval:** Top-K Semantic Search  
                - **Reranking:** Semantic Reranker  
                - **Chunking:** Fixed-size chunks with overlap  
                - **Backend API:** FastAPI  
                - **Frontend UI:** Streamlit  
                - **Logging:** Request logging + latency tracking  
                        """
            )

    return uploaded_files, selected_question


def render_ingestion_section(uploaded_files: list[Any]) -> None:
    st.subheader('1. Upload Documents')

    if uploaded_files:
        st.write('Uploaded files:')

        for file in uploaded_files:
            st.markdown(f'- `{file.name}`')

    else:
        st.info('Upload one or more PDF, TXT, or MD files to begin')

    ingest_clicked = st.button(
        'Ingest Document(s)',
        disabled=not uploaded_files
    )

    if ingest_clicked:
        try:

            with st.spinner('Ingesting documents...'):
                temp_paths = save_uploaded_files(uploaded_files)
                ingest_service = IngestService()

                file_paths = [str(path) for path in temp_paths]
                summary = ingest_service.ingest(IngestRequest(paths=file_paths))

            st.session_state.ingested = True
            st.session_state.last_ingestion_summary = summary

            num_docs = summary.get('documents_ingested', len(uploaded_files)) if isinstance(summary, dict) else len(uploaded_files)
            st.success(f'Successfully ingested {num_docs} document(s).')

        except Exception as exc:
            st.session_state.ingested = False
            st.error(f'Ingestion failed: {exc}')

    summary = st.session_state.last_ingestion_summary

    if summary:
        with st.expander('Ingestion Summary'):
            st.json(summary)


def render_query_section(selected_question: str) -> None:
    st.subheader('2. Ask a Question')

    default_question = selected_question if selected_question else ''
    question = st.text_input(
        'Enter your question',
        value=default_question,
        placeholder='Ask something about the uploaded documents'
    )

    ask_clicked = st.button(
        'Ask DocQuery',
        disabled=not st.session_state.ingested or not question.strip()
    )

    if ask_clicked:
        try:
            with st.spinner('Retrieving evidence and generating answer...'):
                service = QueryService()
                response = service.query(
                    QueryRequest(
                        question=question.strip(),
                        top_k=TOP_K,
                        min_score=MIN_SCORE,
                        return_snippets=True
                    )
                )

                st.session_state.last_response = response

        except Exception as exc:
            st.error(f'Query failed: {exc}')

    if not st.session_state.ingested:
        st.warning('Please ingest your documents before asking a question.')


def render_answer_section(response: QueryResponse | None) -> None:
    st.subheader('3. Answer and Sources')

    if not response:
        st.info('Your answer will appear here after you ask a question.')
        return
    
    answer = response.answer or 'No answer available'
    grounded = response.grounded
    latency_ms = response.latency_ms
    reason_if_unanswered = response.reason_if_unanswered

    st.markdown('### Answer')
    st.write(answer)
    st.write(' ')

    col1, col2 = st.columns(2)
    with col1:
        st.metric('Answer verified', 'Yes' if grounded else 'No')

    with col2:
        st.metric('Latency (ms)', f'{latency_ms:.0f}')

    if reason_if_unanswered:
        st.warning('Insufficient Evidence' if reason_if_unanswered == 'insufficient_evidence' else 'N/A')

    render_citations(response)
    render_retrieved_chunks(response)
    render_raw_response(response)


def render_citations(response: QueryResponse) -> None:
    st.markdown('### Citations')

    citations: list[CitationRecord] = response.citations

    if not citations:
        st.info('No citations were returned')
        return
    
    for citation in citations:
        filename = citation.filename if citation.filename else 'Unknown'
        page_number = citation.page_number if citation.page_number else 'N/A'
        rank = citation.rank if citation.rank else 'N/A'
        section_title = citation.section_title if citation.section_title else 'N/A'
        snippet = citation.snippet if citation.snippet else ''

        header = f'**{filename}** - page {page_number} - rank {rank}'

        if section_title:
            header += f' - {section_title}'

        st.markdown(header)

        if snippet:
            st.caption(snippet)


def render_retrieved_chunks(response: QueryResponse) -> None:
    with st.expander('Retrieved Chunks', expanded=False):
        retrieved_chunks: list[RetrievedChunk] = response.retrieved_chunks

        if not retrieved_chunks:
            st.write('No chunks retrieved.')
            return
        
        for chunk in retrieved_chunks:
            chunk_id = chunk.chunk_id
            filename = chunk.filename
            page_number = chunk.page_number
            rank = chunk.page_number
            score = chunk.score
            text = chunk.text

            st.markdown(
                f'**Rank {rank}** | `{chunk_id}` | **{filename}** | '
                f'page {page_number} | score {score:.3f}'
            )

            st.code(text, language='text')

def render_raw_response(response: QueryResponse) -> None:
    with st.expander('Raw Response JSON', expanded=False):
        st.json(response)


def main() -> None:
    settings = get_settings()
    _ = settings

    init_session_state()
    render_header()

    uploaded_files, selected_question = render_sidebar()

    # Ingestion section
    render_ingestion_section(uploaded_files)
    st.markdown('---')
    
    # Query section
    render_query_section(selected_question)

    # Answer section
    render_answer_section(st.session_state.last_response)

if __name__ == '__main__':
    main()