from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

# Ensure repo root is on `sys.path` so `import shared` works
REPO_ROOT = Path(__file__).resolve().parents[3]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from projects.contract_analyzer.core.analyze import analyze_contract_text

# Default settings for PDF mode
MAX_PAGES = 20
CHUNK_SIZE = 3500
OVERLAP = 300
MAP_MAX_TOKENS = 4000
REDUCE_MAX_TOKENS = 4000
TEXT_MAX_TOKENS = 4000

# Default settings for Text mode
MAX_CHARS = 10_000

st.set_page_config(page_title="Contract Analyzer", layout="centered")

def load_css():
    css_path = Path(__file__).resolve().parents[2] / 'styles' / "main.css"

    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html = True)

load_css()

col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    image_path = Path(__file__).resolve().parents[2] / 'images/contract-icon.png'
    st.image(image_path, width=120)

st.title("Contract Analyzer")

caption_html = """
    <p style="text-align: center;color:#fff; opacity:0.65; margin-top: 0;">
    LLM System - Structured Text Extraction - PDF and Text Modes
    </p>
    <p style="text-align: center;color:#fff; opacity:0.65; margin-top: 0;">
        Powered by Gemini 2.5 Flash • Single-Pass + Map-Reduce Fallback
    </p>
    """
st.markdown(caption_html, unsafe_allow_html=True)
st.markdown('---')

mode = st.radio('Input Mode', ['PDF', 'Text'], horizontal=True)
st.write('')

if mode == 'PDF':
    uploaded = st.file_uploader('Upload a contract PDF', type='pdf')

    if st.button('Analyze PDF', disabled=uploaded is None):
        pdf_bytes = uploaded.read()
        
        from projects.contract_analyzer.core.analyze import analyze_contract_pdf

        with st.spinner('Extracting and analyzinng PDF...'):
            result = analyze_contract_pdf(
                pdf_bytes=pdf_bytes,
                max_pages=MAX_PAGES,
                chunk_size=CHUNK_SIZE,
                overlap=OVERLAP,
                map_max_tokens=MAP_MAX_TOKENS,
                reduce_max_tokens=REDUCE_MAX_TOKENS
            )

        st.markdown('---')
        st.subheader('Parsed JSON')

        if result.error:
            st.error(result.error)
            st.subheader('Raw Output(debug)')
            st.code(result.raw_text)
        else:
            st.json(result.parsed)

        st.subheader('Metadata')
        st.json({ 
            'Provider': 'Gemini',
            'Model': result.model,
            'Mode': 'Single-Pass'
        })

    # Add sample PDF files for quick reference
    caption_html = """
        <p style="color: #fff; margin-top: 50px;padding-top: 20px;font-size:21px;border-top:1px solid rgba(255, 255, 255, 0.4);">
        Try these sample contracts
        </p>
    """
    st.markdown(caption_html, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        with open('docs/sample_contracts/sample-nda.pdf', 'rb') as f:
            st.download_button(
                'Download Sample NDA',
                data=f,
                file_name='sample-nda.pdf',
                mime='application/pdf'
            )
    with col2:
        with open('docs/sample_contracts/sample-business-agreement.pdf', 'rb') as f:
            st.download_button(
                'Download Sample Business Agreement',
                data=f,
                file_name='sample-business-agreement.pdf',
                mime='application/pdf'
            )

if mode == 'Text':
    default_text = (
        "This agreement is made between ABC Corp and XYZ LLC effective January 1, 2024.\n"
        "Either party may terminate with 30 days notice.\n"
        "Liability is unlimited."
    )

    contract_text = st.text_area("Contract Text", value=default_text, height=180)
    #st.write(f"Characters: {len(contract_text):,} / {MAX_CHARS:,}")

    run_disabled = (len(contract_text) == 0 ) or (len(contract_text) > MAX_CHARS)

    if len(contract_text) > MAX_CHARS:
        st.error(f"Contract is too long for single-text extraction. Please keep the lengt under {MAX_CHARS} characters. ")

    if st.button('Analyze', disabled=run_disabled):
        with st.spinner('Analyzing...'):
            result = analyze_contract_text(
                contract_text=contract_text, 
                max_output_tokens=TEXT_MAX_TOKENS
            )

        st.subheader('Parsed JSON')

        if result.error:
            st.error(result.error)
            st.subheader("Raw Ouptut (debug)")
            st.code(result.raw_text)
        else:
            st.json(result.parsed)

        st.subheader('Metadata')
        st.json({
            'Provider': 'Gemini',
            'Model': result.model
        })
        

