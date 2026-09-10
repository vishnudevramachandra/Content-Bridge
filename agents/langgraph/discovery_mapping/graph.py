"""Wiring the graph: state schema, nodes, edges, checkpointer.

=== LangGraph concept: the state schema ===
Every LangGraph graph is parameterized by a `State` type — usually a
`TypedDict` — that declares every key any node is allowed to read or write.
It's the graph's contract, checked at graph-build time, not just a loose
"pass a dict around" convention.

Most keys here use LangGraph's default merge behavior: a node's return
value for a key *overwrites* whatever was there. `resolutions` and
`residue` are the two exceptions, and it's an important exception: because
`resolve_mapping_task` runs many times in parallel (once per `Send`, all in
the same superstep), multiple parallel branches try to write to both keys
at once — each task can produce some fully-resolved rows (`resolutions`)
and some genuinely ambiguous, still-open cases (`residue`) at the same
time. Without telling LangGraph how to combine those writes, it raises an
`InvalidUpdateError` rather than silently picking one and dropping the rest.
`Annotated[list[dict], operator.add]` is that instruction: "when several
branches update this key in the same step, concatenate the lists." This is
the same reducer mechanism LangGraph uses for chat-message history
(`add_messages`) — we're just using a plainer one (`operator.add`) for a
plain list.
"""

from __future__ import annotations

import operator
from contextlib import contextmanager
from typing import Annotated, TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph

from . import discovery, mapping
from .config import DB_PATH


class PipelineState(TypedDict):
    wp_schema: dict
    wp_ambiguous_fields: list[str]

    strapi_schemas: dict
    strapi_uids: dict
    strapi_ambiguous_fields: list[str]

    mapping_tasks: list[dict]
    resolutions: Annotated[list[dict], operator.add]
    residue: Annotated[list[dict], operator.add]


@contextmanager
def build_graph():
    """=== LangGraph concept: StateGraph, nodes, and edges ===

    `StateGraph(PipelineState)` starts an empty graph typed to that state.
    `add_node(name, fn)` registers a callable under a name other nodes/edges
    can refer to; the function itself (see discovery.py, mapping.py) knows
    nothing about the graph it's part of.

    Edges describe *control flow*, separately from the node functions:

    - `add_edge(START, "discover_wordpress")` and
      `add_edge(START, "discover_strapi")` both leaving `START` is how you
      fan OUT to independent parallel work in LangGraph — there's no special
      "parallel" API, you just give two nodes the same predecessor.
    - `add_edge("discover_wordpress", "plan_mapping_tasks")` and the
      matching edge from `discover_strapi` both pointing at
      `plan_mapping_tasks` is the fan-IN: LangGraph runs `plan_mapping_tasks`
      only once both discovery branches have completed (it waits for all
      pending predecessors within the step before advancing), not once per
      incoming edge.
    - `add_conditional_edges("plan_mapping_tasks", mapping.route_mapping_tasks, [...])`
      is different from a plain edge: instead of a fixed next node, LangGraph
      calls `route_mapping_tasks(state)` and uses its return value — here,
      either the literal string "summarize" or a list of `Send(...)`
      objects — to decide what runs next, per current state. The third
      argument is just the declared set of possible destinations, used for
      graph validation/visualization, not routing itself.
    """
    graph = StateGraph(PipelineState)

    graph.add_node("discover_wordpress", discovery.discover_wordpress)
    graph.add_node("discover_strapi", discovery.discover_strapi)
    graph.add_node("plan_mapping_tasks", mapping.plan_mapping_tasks)
    graph.add_node("resolve_mapping_task", mapping.resolve_mapping_task)
    graph.add_node("summarize", lambda state: {})

    graph.add_edge(START, "discover_wordpress")
    graph.add_edge(START, "discover_strapi")
    graph.add_edge("discover_wordpress", "plan_mapping_tasks")
    graph.add_edge("discover_strapi", "plan_mapping_tasks")

    graph.add_conditional_edges(
        "plan_mapping_tasks",
        mapping.route_mapping_tasks,
        ["resolve_mapping_task", "summarize"],
    )
    graph.add_edge("resolve_mapping_task", "summarize")
    graph.add_edge("summarize", END)

    """=== LangGraph concept: the checkpointer ===

    `compile(checkpointer=...)` is what turns a graph definition into
    something that persists its state after every superstep, keyed by a
    `thread_id` you supply at invoke time. Without a checkpointer, `invoke`
    runs start-to-finish in memory and nothing survives the call. With one:

    - the same `thread_id` can be resumed later (crash recovery, human-in-
      the-loop pauses) picking up from the last completed step;
    - `graph.get_state(config)` lets you inspect exactly what a given thread
      last looked like.

    `SqliteSaver` is one concrete backend for this — it stores checkpoints
    as rows in a SQLite file, which is why `run.py` can point it at the same
    `mapping_rules.db` file our own cache lives in without conflict: the
    checkpointer creates and owns its own tables (`checkpoints`,
    `checkpoint_writes`, ...), entirely separate from `mapping_rules`. See
    README.md for why that separation is a real design point, not just a
    cost-saving on files.

    `build_graph` is itself a context manager (`@contextmanager` above) so
    the SQLite connection `SqliteSaver.from_conn_string` opens gets closed
    deterministically — `with build_graph() as app: ...` in run.py — rather
    than leaked for the life of the process.
    """
    with SqliteSaver.from_conn_string(str(DB_PATH)) as checkpointer:
        yield graph.compile(checkpointer=checkpointer)
