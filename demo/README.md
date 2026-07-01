# pttai playground (interactive demo)

A one-command local playground for the pttai `>`-DSL. Paste a snippet, click
**Build + Validate**, and see:

1. **The compiled LangGraph** — rendered as a mermaid node/edge diagram from
   `graph.compiled_graph.get_graph().draw_mermaid()`. Gradio ships mermaid.js, so
   the diagram renders in-browser with no network.
2. **The build-time dataflow validator** — the `graph.summary()` table (each
   node's reads / writes / available keys) plus every `ValidationReport` issue.
   When the pasted graph is **broken**, `AgenticGraph(...)` raises a
   `GraphValidationError` *at construction*, and the demo shows that error — the
   whole point: bugs caught **before** you ever invoke the graph.

## Run

```bash
pip install -r demo/requirements.txt
python demo/app.py
```

Then open the printed local URL. **No `OPENAI_API_KEY` needed** — building,
validating, and visualizing a graph never call a model, and `get_llm()` returns
an offline fake so the nodes construct.

## What to try

- **Load working example** → a sentiment router (`DecisionNode` → two handlers).
  You get the branching diagram and a green validator report.
- **Load BROKEN example** → a read-before-write (`write` reads `plan` before
  `planner` produces it). The build fails and the validator error is shown
  instead of a diagram. Raw LangGraph would compile this and only blow up at
  runtime. Edit the working example to introduce your own bugs (a dangling
  `decision["x"]` with no `>` handler, a duplicate `name=`, a write to an
  undeclared key) and watch the validator catch each one.

## Security

This demo **`exec`s the code you paste** in-process. It is a **local developer
demo, not a public deployment** — do not expose it on an untrusted network or
accept snippets from untrusted users.
