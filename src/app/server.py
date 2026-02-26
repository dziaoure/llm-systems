from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
import time

from src.app.analyze import analyze_text


app = FastAPI(
    title='Contract Analyzer API',
    version='1.0.0',
    description='Tool-using Gemini agent fro contract clause extraction and risk scoring'
)

class AnalyzeRequest(BaseModel):
    contract_text: str = Field(..., min_length=1, description='Raw contract text')
    context: Optional[Dict[str, Any]] = Field(
        defualt=None,
        description='Optional context: party_role, jurisdiction, contract_type, etc.'
    )


class AnalyzeResponse(BaseModel):
    status: str
    final_answer: Optional[str] = None
    risk_summary: Optional[Dict[str, Any]] = None
    extracted_clauses: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    error: Optional[str] = None


@app.get('/health')
def health() -> Dict[str, str]:
    return { 'status': 'Ok'}

@app.post('/analyze', response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest) -> Dict[str, Any]:
    return analyze_text(req.contract_text, context=req.context)


@app.middleware('http')
async def log_request(request: Request, call_next):
    start = time.time()
    response = call_next(request)
    duration = time.time() - start
    print(f'{request.method} {request.url.path} - {duration:0.3f}s')

    return response