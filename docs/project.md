# Project status & working notes

Living companion to [CLAUDE.md](../CLAUDE.md). CLAUDE.md holds the stable architecture; this file holds everything that changes — setup, dependencies, how to verify work, current status, rough edges, and the roadmap.

The **Status** and **Recent changes** sections at the bottom are auto-maintained by the post-commit hook (`.githooks/post-commit`) via headless Claude. You can also edit them by hand — the hook only refreshes those two sections.

## Setup & running

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

- Requires `OPENAI_API_KEY` in `.env` (loaded via `python-dotenv`'s `load_dotenv()`).
- **No test suite, no linter, no build step.** Verification is manual — `test.ipynb` is the scratchpad and the de-facto usage example.

## Dependencies & gotchas

- `test.ipynb` imports `langchain_ollama` (`ChatOllama`), which is **not** in `requirements.txt`. Either `pip install langchain-ollama` or stick to the `ChatOpenAI` line.
- Dependencies are pinned in `requirements.txt` (LangGraph 0.2.60, LangChain 0.3.x, langchain-openai, Pydantic 2.x).

## Verifying changes

There are no automated tests. After changing framework code, re-run the relevant cells in `test.ipynb` to confirm graphs still build (`AgenticGraph(...)`) and invoke (`graph.invoke({'messages': [...], 'log': []})`). Inspect `state['log']` for the per-node trace.

## Current status & rough edges

- **InputNode interrupt resumption is incomplete.** `InputNode.__call__` uses LangGraph's `interrupt()`, but `AgenticGraph.compile()` is called with `checkpointer=None` in `__init__`, so resuming after an interrupt needs extra wiring before it works end-to-end. (See `TODO.md` — "Human Node".)
- `AgenticState.messages` is annotated `List[str]` but actually holds LangChain message objects; the annotation is aspirational, not enforced.

## Roadmap

From `TODO.md`:
- Human/Input node — make input a separate, resumable step rather than a blocking interrupt.
- RAG tools — currently stubbed/commented in `tools/rag_tool.py`.
- Configurable input/output fields per node.
- Conversation memory (`ConversationChain` / `ConversationSummaryMemory`).
- LangSmith integration.
- TTS and STT nodes.

## Status

<!-- AUTO-MAINTAINED by .githooks/post-commit — keep this a 1-3 sentence summary -->
Early-stage framework. Latest tracked work: `InputNode` added for human-in-the-loop, plus state/import cleanup (commit ecc40bb).

## Recent changes

<!-- AUTO-MAINTAINED by .githooks/post-commit — newest first, max 15 bullets -->
- ecc40bb 2026-06-17 — Add InputNode for human-in-the-loop and clean up state/imports
