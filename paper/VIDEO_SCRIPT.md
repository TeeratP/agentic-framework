# Submission video — shot list (target ≤ 2:30)

Mandatory demo video for EMNLP 2026 System Demonstrations. Reviewers often watch
**muted**, so every point must be legible on screen: large fonts (≥ 24 pt for
captions), high-contrast, code zoomed so it is readable, and a burned-in caption
on every shot. No reliance on narration.

Total budget: **150 s** (30 + 75 + 30 + 15).

---

## Shot 1 — The problem (0:00–0:30, 30 s)

**On screen:** a raw-LangGraph RAG-QA pipeline running in a terminal. It makes
the retrieval + answer model calls, then, several seconds in, crashes with a red
traceback: `KeyError: 'passages'`.

**Caption (persistent):**
> LLM pipelines fail *after* the model runs. A miswired state key = a runtime
> KeyError — tokens, latency, and tool side effects already spent.

**Beats:**
- 0:00 title card: *"pttai — build-time dataflow validation for LLM pipelines."*
- 0:08 show the graph runs, spinner on the model call.
- 0:20 the traceback lands. Freeze-frame + red box around `KeyError: 'passages'`.
- Caption sting: *"The bug existed at build time. It cost N model calls to find."*

## Shot 2 — The playground (0:30–1:45, 75 s)

**On screen:** the browser playground (the paper's Figure 2).

**Beats:**
- 0:30 paste a **working** RAG-QA `pttai` snippet. Submit. Green: the compiled
  LangGraph diagram renders + the `summary()` table (reads / writes / available
  keys per node). Caption: *"Clean build → the compiled LangGraph."*
- 1:00 edit **one** thing on camera: reorder so the answer node reads
  `passages` before the retriever runs. Submit.
- 1:10 the diagram redraws from the pre-compile wiring with the **offending node
  painted red** and the exact error attached:
  `reads computed key 'passages' but no upstream node produces it`.
  Caption (big): *"Rejected at BUILD time. Zero model calls."*
- 1:30 show the "model calls: 0" indicator; contrast callout to Shot 1's crash.
  Caption: *"Same bug. Caught before anything ran."*

## Shot 3 — The numbers (1:45–2:15, 30 s)

**On screen:** a single static results slide (readable, muted-friendly).

**Slide content (verbatim, matches the paper / repo):**
- **13 / 13** differentiating bug classes caught at build time
- **0** false positives on 19 valid pipelines
- **15 → 0** wasted model calls across the 15-item bug benchmark
- **~60% less code** (113 vs 281 lines over 12 pipelines) — *a side effect*
- Compiles to a native LangGraph `StateGraph`; build overhead within noise

Caption: *"False-positive-free by construction — hard errors come only from the
may-analysis."*

## Shot 4 — Install + link (2:15–2:30, 15 s)

**On screen:** terminal + repo URL.
- `pip install -e .` (or the published package name)
- `github.com/TeeratP/agentic-framework`  ·  live demo link
- Caption: *"Try the playground. MIT licensed."*

---

### Production notes
- Record the playground at 1080p, browser zoom ~125% so DSL + error are legible.
- Keep the red-node moment on screen ≥ 4 s — it is the whole demo.
- All numbers on the results slide are the measured values in `eval/`
  (`bugbench/results.csv`, `loc_results.csv`, `overhead.py`); do not round the
  60% up. The LLM-generation headline number is intentionally **not** shown —
  it awaits a keyed run (see paper §5).
