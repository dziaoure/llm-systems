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

from projects.contract_analyzer.core.analyze import analyze_contract_test

st.set_page_config(page_title="Contract Analyzer", layout="centered")

st.title("Contract Analyzer")
st.caption("LLM System - Structured extraction - Text Mode")

MAX_CHARS = 10_000

default_text = (
    "This agreement is made between ABC Corp and XYZ LLC effective January 1, 2024.\n"
    "Either party may terminate with 30 days notice.\n"
    "Liability is unlimited."
)

contract_text = st.text_area("Contract Text", value=default_text, height=180)
st.write(f"Charactes: {len(contract_text):,} / {MAX_CHARS:,}")

max_output_tokens = st.slider(
    'Max Output Tokens',
    min_value=400,
    max_value=1500,
    value=1500,
    step=100
)

run_disabled = (len(contract_text) == 0 ) or (len(contract_text) > MAX_CHARS)

if len(contract_text) > MAX_CHARS:
    st.error(f"Contract is too long for single-text extraction. Please keep the lengt under {MAX_CHARS} characters. ")

if st.button('Analyze', disabled=run_disabled):
    with st.spinner('Analyzing...'):
        result = analyze_contract_test(
            contract_text=contract_text, 
            max_output_tokens=max_output_tokens
        )

    st.subheader('Parsed JSON')

    if result.error:
        st.error(result.error)
        st.subheader("Raw Ouptut (debug)")
        st.code(result.raw_text)
    else:
        st.json(result.parsed)

    st.subheader('Metadata')
    st.json({'provider': result.provider, 'model': result.model})

    # Save artifacts for deugging and protfolio screenshots
    artifacts_dir = REPO_ROOT / 'docs' / 'artificats'
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    (artifacts_dir / f'contract_analyzer_raw_{ts}.txt').write_text(result.raw_text, encoding='utf-8')

    if result.parsed:
        (artifacts_dir / f'contract_analyzer_parsed_{ts}.json').write_text(
            json.dumps(result.parsed, indent=2),
            encoding='utf-8'
        )

    st.success('Saved artifacts to "docs/artifacts/" folder')