"""pttai interactive demo — paste DSL, see the compiled LangGraph + validator.

A local Gradio playground for the pttai `>` DSL. You paste/edit a small pttai
snippet; on submit it is ``exec``'d in a namespace that exposes the pttai public
API plus ``get_llm()`` (the offline fake model from ``examples/_llm.py``), the
resulting ``AgenticGraph`` is found, and two things are rendered:

  1. the **compiled LangGraph** as a mermaid node/edge diagram
     (``graph.compiled_graph.get_graph().draw_mermaid()`` — Gradio ships
     mermaid.js, so the fenced ```mermaid block renders client-side, offline); and
  2. the **build-time dataflow validator** output — the ``summary()`` table and
     every ``ValidationReport`` issue, OR, when the graph is broken, the
     ``GraphValidationError`` raised *at construction* (before any invoke).

No OPENAI_API_KEY needed: building + validating + visualizing a graph never
calls a model. ``get_llm()`` returns an offline fake so nodes construct.

    pip install -r demo/requirements.txt
    python demo/app.py

SECURITY: this ``exec``'s the pasted code. It is a LOCAL developer demo, not a
public deployment. Do not expose it on an untrusted network.
"""

import io
import os
import sys
import traceback

# Make `import pttai` (repo root) and `from _llm import get_llm` (examples/) work
# regardless of the cwd the demo is launched from.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "examples"))

import gradio as gr


# --- prefilled examples ----------------------------------------------------

WORKING_EXAMPLE = '''\
# Sentiment router: a DecisionNode picks the branch, each choice has a handler.
classify = DecisionNode(
    name="classify", llm=get_llm(),
    node_prompt="Classify the sentiment of the message.",
    choices=["positive", "negative"],
)
praise    = AgentNode(name="praise",    llm=get_llm(), node_prompt="Thank the happy customer.")
apologize = AgentNode(name="apologize", llm=get_llm(), node_prompt="Apologize to the unhappy customer.")

classify["positive"] > praise        # wire each choice to its handler
classify["negative"] > apologize

graph = AgenticGraph(start_node=classify, end_nodes={praise, apologize})
'''

BROKEN_EXAMPLE = '''\
# BROKEN on purpose: `write` reads the scalar key `plan`, but the only node that
# writes `plan` (`planner`) runs AFTER it. That is a read-before-write — a
# guaranteed runtime KeyError in raw LangGraph. pttai's validator FAILS the
# build here, before you ever invoke the graph.
write = AgentNode(
    name="write", llm=get_llm(),
    node_prompt="Write the essay using this plan: {plan}.",
    reads=["plan"], writes=["messages"],
)
planner = AgentNode(
    name="planner", llm=get_llm(),
    node_prompt="Produce a plan for the essay.",
    reads=["messages"], writes={"plan": str},
)

write > planner                       # planner (the producer of `plan`) runs LAST
graph = AgenticGraph(start_node=write, end_nodes={planner})
'''


def _namespace() -> dict:
    """A fresh exec namespace exposing the pttai public API + get_llm()."""
    import pttai
    from _llm import get_llm
    from pttai.validation import GraphValidationError

    ns = {"get_llm": get_llm, "GraphValidationError": GraphValidationError}
    for name in pttai.__all__:
        ns[name] = getattr(pttai, name)
    return ns


def build_and_report(code: str):
    """exec the snippet, find the AgenticGraph, return (mermaid_md, validator_md)."""
    from pttai import AgenticGraph
    from pttai.validation import GraphValidationError

    ns = _namespace()
    try:
        exec(code, ns)
    except GraphValidationError as e:
        # THE POINT: the build-time validator rejected the graph before invoke.
        val = (
            "### Build FAILED — the validator caught errors *before* invoke\n\n"
            "```\n" + str(e) + "\n```\n\n"
            "*Raw LangGraph would have compiled this and only failed at runtime.*"
        )
        mer = "_No diagram: the graph never compiled — the build-time validator rejected it._"
        return mer, val
    except Exception:
        tb = traceback.format_exc()
        return (
            "_No diagram: the snippet raised._",
            "### Error running snippet\n\n```\n" + tb + "\n```",
        )

    graphs = [v for v in ns.values() if isinstance(v, AgenticGraph)]
    if not graphs:
        return (
            "_No `AgenticGraph` found._",
            "Bind your graph to a variable, e.g. `graph = AgenticGraph(start_node=..., end_nodes={...})`.",
        )
    graph = graphs[-1]

    # (i) compiled LangGraph -> mermaid
    try:
        mermaid = graph.compiled_graph.get_graph().draw_mermaid()
        mer = "### Compiled LangGraph\n\n```mermaid\n" + mermaid + "\n```"
    except Exception as e:
        mer = "_Could not render mermaid: " + repr(e) + "_"

    # (ii) validator: summary() table + report issues
    report = graph.validate()
    buf = io.StringIO()
    graph.summary(file=buf)  # explicit file: summary()'s default binds the
                             # original sys.stdout, so redirect_stdout misses it
    status = "OK" if report.ok else "ERRORS"
    val = (
        f"### Validator: {status} — {len(report.errors)} error(s), "
        f"{len(report.warnings)} warning(s)\n\n"
        "```\n" + buf.getvalue().rstrip() + "\n```"
    )
    if report.issues:
        val += "\n\n**Issues:**\n\n```\n" + "\n".join(str(i) for i in report.issues) + "\n```"
    return mer, val


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="pttai playground") as demo:
        gr.Markdown(
            "# pttai playground\n"
            "Paste a pttai `>`-DSL snippet, then **Build + Validate**. You get the "
            "**compiled LangGraph** diagram and the **build-time validator** output — "
            "read-before-write, dangling choices, and duplicate names are caught "
            "*before* you ever invoke. `get_llm()` is an offline fake, so **no API key** "
            "is needed."
        )
        with gr.Row():
            with gr.Column(scale=1):
                code = gr.Code(value=WORKING_EXAMPLE, language="python", label="pttai DSL", lines=20)
                with gr.Row():
                    load_ok = gr.Button("Load working example")
                    load_bad = gr.Button("Load BROKEN example", variant="stop")
                run = gr.Button("Build + Validate", variant="primary")
            with gr.Column(scale=1):
                mermaid_out = gr.Markdown(label="Compiled graph")
                validator_out = gr.Markdown(label="Validator")

        run.click(build_and_report, inputs=code, outputs=[mermaid_out, validator_out])
        load_ok.click(lambda: WORKING_EXAMPLE, outputs=code)
        load_bad.click(lambda: BROKEN_EXAMPLE, outputs=code)
    return demo


if __name__ == "__main__":
    build_ui().launch()
