from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from agent import generate_answer


ROOT = Path(__file__).resolve().parent
WEB_DIR = ROOT / "web"

app = FastAPI(title="AI Atlas")
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    messages: List[ChatMessage] = Field(default_factory=list)
    provider: str = "auto"
    model: str = "chat-latest"
    style: str = "balanced"
    top_k: int = 4


@app.get("/", response_class=HTMLResponse)
def home() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.post("/api/chat")
def chat(request: ChatRequest) -> Dict[str, Any]:
    history = [message.model_dump() for message in request.messages]
    result = generate_answer(
        question=request.question,
        history=history,
        provider=request.provider,
        model=request.model,
        style=request.style,
        top_k=request.top_k,
    )
    return {
        "answer": result["answer"],
        "context": result.get("context", ""),
        "sources": result.get("sources", []),
        "provider": result.get("provider", "fallback"),
        "model": result.get("model", request.model),
    }


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}
