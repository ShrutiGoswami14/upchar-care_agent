"""FastAPI wrapper. Run: uvicorn api:app --reload   then open http://127.0.0.1:8000/docs"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel, Field

import db
from agent import build_agent, run_agent

state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.reset()
    state["agent"] = await build_agent()
    yield


app = FastAPI(title="Upchar Care Agent", lifespan=lifespan)


@app.get("/")
def root():
    return {
        "message": "Welcome to Upchar Care Agent",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    thread_id: str = "default"


class ChatResponse(BaseModel):
    reply: str
    tools_used: list[dict]


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    reply, calls = await run_agent(state["agent"], req.message, req.thread_id)
    return ChatResponse(reply=reply, tools_used=[{"tool": n, "args": a} for n, a in calls])


@app.get("/health")
def health():
    return {"status": "ok"}
