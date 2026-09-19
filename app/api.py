from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.rag.pipeline import NaiveRAGPipeline
from src.security.access_control import ALL_ROLES
from src.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="Banking RAG Copilot API",
    description="AI-powered knowledge assistant for banking operations",
    version="1.0.0"
)


class AskRequest(BaseModel):
    question: str
    role: Optional[str] = "public"
    top_k: Optional[int] = 5


class CitationResponse(BaseModel):
    source_file: str
    chunk_index: int
    similarity_score: Optional[float]

class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[str]
    citations: list[dict]
    grounding_score: float
    is_grounded: bool


_pipelines: dict = {}

def get_pipeline(role: str, top_k: int) -> NaiveRAGPipeline:
    key = (role, top_k)
    if key not in _pipelines:
        logger.info(f"Creating new pipeline for role='{role}', top_k={top_k}")
        _pipelines[key] = NaiveRAGPipeline(top_k=top_k, role=role)
    return _pipelines[key]


@app.get("/health")
def health():
    return {"status": "ok", "service": "banking-rag-copilot"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    if request.role not in ALL_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role '{request.role}'. Valid roles: {ALL_ROLES}"
        )

    pipeline = get_pipeline(request.role, request.top_k)
    result   = pipeline.ask(request.question)

    grounding = result.get("grounding", {})

    return AskResponse(
        question=result["question"],
        answer=result["answer"],
        sources=result["sources"],
        citations=result.get("citations", []),
        grounding_score=grounding.get("score", 0.0),
        is_grounded=grounding.get("is_grounded", False),
    )




