from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .rag_chatbot import RAGChatbot


app = FastAPI(title="AITruthGuard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    query: str
    k: int | None = 5


class AskResponse(BaseModel):
    answer: str
    confidence: float
    top_news: list
    top_index: list


bot = None


@app.on_event("startup")
def on_startup() -> None:
    global bot
    bot = RAGChatbot()


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    try:
        out = bot.ask(req.query, k=req.k or 5)
        return AskResponse(**out)
    except Exception as e:
        # Bubble up as JSON 500 with message
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root() -> dict:
    return {"status": "ok", "endpoints": ["GET /health", "POST /ask"]}


@app.get("/health")
def health() -> dict:
    from .config import load_config
    cfg = load_config()
    return {
        "ok": True,
        "has_news_api": bool(cfg.news_api_key),
        "has_gemini": bool(cfg.gemini_api_key),
        "env_path": cfg.env_path or None,
    }


