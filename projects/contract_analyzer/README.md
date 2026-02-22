# Contract Analyzer

![App Screenshot](../images/contract-analyzer-screenshot.jpg)

An LLM-powered structured contract analysis system for PDF and text inputs.

Extracts key parties, effective dates, termination clauses, risk flags, and confidence scores using a production-style LLM pipeline with guardrails and fallback strategies.

---

## Overview

This project demonstrates a real-world LLM system design for structured information extraction from legal contracts.

It supports:
- PDF ingestion with text extraction
- Text-mode input
- Single-pass structured extraction for short documents
- Map-Reduce summarization for longer contracts
- Schema validation and structured JSON output
- Risk flag detection with severity scoring
- Graceful fallback logic
- Downloadable sample contracts for demo

The system is designed to be reliable, extensible, and production-ready.


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

### Run:
Run the following command from the `llm-systems` root folder
```
streamlit run projects/contract_analyzer/app/main.py
```

