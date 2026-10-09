# Upchar Care Agent

Powered by Google Gemini (free tier available). The default model is `gemini-2.5-flash`; if it is unavailable, pick a current Gemini Flash model in AI Studio and set `MODEL_NAME` in `.env`.

A tool-using appointment assistant built to learn and demonstrate the skills in the AI Engineer (Agentic AI) JD.

| JD requirement | Where it lives |
|---|---|
| LangGraph agent, tool calling, state / memory | `agent.py` (`create_react_agent`, `MemorySaver`, thread ids) |
| MCP server + client, tool discovery, input validation | `mcp_server.py` (FastMCP), `agent.py` (`MultiServerMCPClient`) |
| FastAPI backend, Pydantic | `api.py` |
| Observability (traces, token use, latency) | Langfuse via `get_callbacks()` in `agent.py` |
| Evals + regression tests | `evals/run_evals.py`, `evals/eval_cases.json` |
| Guardrails (prompt injection, missing info, no medical advice) | system prompt + eval cases |
| Database knowledge | SQLite in `db.py` |

## Setup
```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # add your GOOGLE_API_KEY from https://aistudio.google.com/apikey (and optional Langfuse keys)
python db.py                # seed the database
```
Free-tier note: if you see rate-limit (429) errors, increase `EVAL_DELAY` in `.env` or wait a minute and re-run.
Library APIs change fast. If an import fails, check the current LangGraph / langchain-mcp-adapters / Langfuse docs and adjust.

## Run
```bash
uvicorn api:app --reload                      # chat API, docs at http://127.0.0.1:8000/docs
python -m evals.run_evals --save-baseline     # first eval run
python -m evals.run_evals                     # later runs show regressions vs baseline
```

## 3-day plan
**Day 1: make it work.** Install, seed DB, run the API, chat with it in `/docs`. Read every file until you can explain the flow: request, graph loop, MCP tool call, DB, reply.
**Day 2: observe and evaluate.** Create a free Langfuse account, add keys, open a trace and find the tool calls, tokens and latency. Run the evals, read the failures, then fix the prompt or tool descriptions and re-run.
**Day 3: improve and document.** Add 5 more eval cases of your own, add one improvement from the list below, push to GitHub with this README, and note your before/after eval numbers.

## Improvements (pick at least one, these are your interview talking points)
- Human-in-the-loop approval before `book_appointment` / `cancel_appointment` (LangGraph `interrupt`).
- Retry and error-handling middleware around tool calls.
- Swap SQLite for PostgreSQL (you already know it).
- LLM-as-a-judge eval for reply quality.
- Dockerfile and a GitHub Actions workflow that runs the evals.
- A simple RAG tool over clinic FAQs (embeddings + vector search, building on your Fashion Recommender work).

## Questions to be able to answer
1. What happens in one agent loop iteration? (model call, tool call decision, tool result, repeat)
2. Why MCP instead of hard-coding functions as tools?
3. How does `thread_id` give the agent memory?
4. How do your evals score tool selection vs task completion, and what did your first run get wrong?
5. What did you change after seeing the failures, and did the score improve?

## Resume bullets (fill in ONLY after you run it and have real numbers)
**Project: Upchar Care Agent** | Python, LangGraph, MCP, FastAPI, Langfuse | Month 2026
- Built an appointment-booking agent with LangGraph that discovers and calls tools from a custom MCP server (doctor lookup, slot availability, booking, cancellation) backed by a SQL database, with thread-based conversational memory.
- Exposed the agent through a FastAPI service and traced runs with Langfuse to inspect tool calls, token usage and latency.
- Created a 20-case evaluation suite measuring tool selection, argument accuracy and task completion (including prompt-injection and missing-information cases); improved pass rate from X% to Y% by refining prompts and tool descriptions.
