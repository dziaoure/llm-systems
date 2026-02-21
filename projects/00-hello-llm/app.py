from __future__ import annotations

import os
import sys
from pathlib import Path
import streamlit as st

# --- Fix imports when runing `streamlit` from `/app`
PROJECT_ROOT = Path(__file__).resolve().parents[2] # projects/00-hello-llm/app.py -> repo root

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.llm_client import LLMClient, ChatMessage
from shared.prompts.v1.contract_summary_prompt import SYSTEM_PROMPT, USER_TEMPLATE
from shared.utils.json_utils import safe_parse_json


st.set_page_config(page_title="LLM Smoke Test", layout="centered")

st.title("LLM Smoke Test")
st.caption('Quick health-check for Gemini/OpenAI/Claude + unified client wrapper')

provider = st.selectbox('Provider', ['gemini', 'openai', 'anthropic'], index=0)
model = st.text_input('Model', value=os.getenv('LLM_MODEL', 'gemini-2.5-flash'))
temperature = st.slider('Temperature', 0.0, 1.0, float(os.getenv('LLM_TEMPERATURE', '0.2')), 0.05)

prompt = st.text_area(
    'Prompt',
    value='',
    height=120
)

if st.button('Generate'):
    os.environ['LLM_PROVIDER'] = provider
    os.environ['LLM_MODEL'] = model
    os.environ['LLM_TEMPERATURE'] = str(temperature)

    client = LLMClient()

    messages=[
        ChatMessage(role='system', content=SYSTEM_PROMPT),
        ChatMessage(
            role='user', 
            content=USER_TEMPLATE.substitute(contract_text=prompt)
        )
    ]

    with st.spinner('Caling the model...'):
        resp = client.generate(messages, max_tokens=1500)
        parsed_json, error = safe_parse_json(resp.text)

    st.subheader("Raw Output")
    st.code(resp.text)

    if error:
        st.error(f"JSON parsing error: {error}")
    else:
        st.subheader('Parsed JSON')
        st.json(parsed_json)

    st.subheader('Metadata')
    st.json(
        {
            'provider': resp.provider,
            'model': resp.model,
            'input_tokens': resp.input_tokens,
            'output_tokens': resp.output_tokens
        }
    )