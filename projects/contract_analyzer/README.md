# Contract Analyzer

![App Screenshot](../images/contract-analyzer-screenshot.jpg)


---

## Overview

Contract Analyzer is a production-style LLM system that analyzes contract text using a tool-driven workflow:
**clause extraction → rubric-based risk scoring → structured recommendations.**

It ships with two entrypoints:
- **Streamlit UI**: (PDF/text extraction + interactive review)
- **FastAPI service**: (POST /analyze for integration)


## Features:
- Single-pass and Map-Reduce processing
- Adaptive fallback logic
- Structured JSON extraction
- Risk flag detection with severity scoring
- Production-ready UI
- Gemini-powered agent loop with multi-step orchestration
- Tooling layer (clause extraction + risk rubric scorer)
- Rubric-based risk scoring with rationale, assumptions, and recommended edits
- Strict JSON output with robust parsing + retry safeguards
- FastAPI service (POST /analyze, GET /health) + Swagger docs
- CLI interface for local testing and batch workflows


## System Architecture

The pipeline adapts dynamically based on document size:

### 1. PDF Extraction
- Extract text from uploaded PDF using pypdf
- Validate extraction quality
- Guard against empty / malformed inputs

### 2. Processing Strategy Selection

If document length ≤ `SINGLE_PASS_THRESHOLD` (15,000 chars):
- Single-pass structured extraction

If document length > threshold:
- Map step: chunk + summarize
- Reduce step: structured synthesis

### 3. Fallback:
- If Map output is insufficient, revert to single-pass mode


## Output Schema

The system returns validated structured JSON:

```
{
  "executive_summary": "string",
  "key_parties": ["string"],
  "effective_date": "string | null",
  "termination_clause": "string | null",
  "risk_flags": [
    {
      "type": "string",
      "severity": "low | medium | high",
      "explanation": "string"
    }
  ],
  "confidence": "low | medium | high"
}
```

## Model Configuration
- Provider: **Gemini**
- Model: `gemini-2.5-flash`
- Max output tokens: 1200–1500
- Single-pass threshold: 15,000 characters

The architecture is provider-agnostic and can be extended to support OpenAI or Anthropic APIs.


## Guardrails & Reliability Features
- Input validation before model invocation
- Adaptive strategy selection (Single-pass vs Map-Reduce)
- Fallback logic if chunk summaries fail
- Structured JSON parsing with error handling
- Confidence scoring included in output
- Metadata reporting (provider + model)

This prevents common LLM failure modes such as:
- Empty responses
- Incomplete chunk summaries
- JSON drift
- Over-tokenization


## UI Features
- Clean dark-mode interface
- PDF and Text input modes
- Drag-and-drop file upload
- Syntax-highlighted structured output
- Model metadata display
- Downloadable sample NDA and business agreement


## Local Setup
```
git clone <repo-url>
cd llm-systems
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Create `.env`:
First, create the `.env` file by running the following command:

```
cp .env.example .env
```
Next, add you `GEMINI_API_KEY` to the `.env` file.

```
GEMINI_API_KEY='your_api_key_here'
```

## Run It
### Streamlit (UI)
Run the following command from the `llm-systems` root folder:

```
streamlit run projects/contract_analyzer/app/main.py
```

### FastAPI (API)
First, start the server:

```
uvicorn src.app.server:app --reload --host 0.0.0.0 --port 8000
```

Next, make an API request:
```
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "contract_text": "Limitation of Liability: Vendor shall have unlimited liability. This Agreement may be terminated for convenience without notice.",
    "context": {"party_role":"vendor","jurisdiction":"California, USA","contract_type":"Software Services Agreement"}
  }'
```

