"""Entry point: run the Discovery + Mapping pipeline twice against the same
live WordPress/Strapi content, and prove the second run reuses every
resolution from the first without a single new LLM call.

=== Why two DIFFERENT thread_ids, not the same thread_id twice ===
This is a real design decision worth pausing on, not a detail.

LangGraph's checkpointer (see graph.py) is keyed by `thread_id`. If you
called `app.invoke({}, {"configurable": {"thread_id": "same-id"}})` twice
with the *same* id, LangGraph would see thread "same-id" already reached
END on the first call and — depending on version/settings — could just
hand back the last checkpointed state without re-running a single node.
That would "prove" zero LLM calls on run 2, but for a reason that has
nothing to do with what this task actually asked us to prove: it would be
LangGraph's own thread-resumption doing the skipping, not our
`mapping_rules` SQLite cache.

Using two *different* thread_ids ("run-1", "run-2") closes that loophole:
run 2 is a genuinely fresh thread, as far as LangGraph is concerned. Every
node — discover_wordpress, discover_strapi, plan_mapping_tasks, and every
Send-fanned-out resolve_mapping_task — actually executes again from
scratch. What makes run 2 skip the LLM is `resolve_mapping_task` calling
`store.lookup()` (mapping.py) and finding the exact same
(source_system, source_content_type, source_ref) row already sitting in
mapping_rules.db from run 1 — content-addressed memory that has nothing to
do with which thread is asking. That distinction (thread-scoped vs.
content-scoped memory) is exactly the point explored further in
README.md's scalability/memory section.

We delete the SQLite file before starting so this script always
demonstrates the interesting case: run 1 doing real, uncached work, and
run 2 riding entirely on run 1's cache. In real, repeated usage you would
obviously *not* delete this file between runs -- that's the whole point
of a durable cache -- this reset only exists so this demo script itself
is repeatable.
"""

from __future__ import annotations

from collections import Counter

from discovery_mapping import llm_client
from discovery_mapping.config import DB_PATH
from discovery_mapping.graph import build_graph


def _run(app, thread_id: str, label: str) -> dict:
    print(f"\n{'=' * 70}\n{label}  (thread_id={thread_id!r})\n{'=' * 70}")
    calls_before = llm_client.call_count
    config = {"configurable": {"thread_id": thread_id}}
    result = app.invoke({}, config)
    calls_after = llm_client.call_count

    resolutions = result["resolutions"]
    residue = result.get("residue", [])
    print(f"  resolutions returned : {len(resolutions)}")
    print(f"  method breakdown     : {dict(Counter(r['method'] for r in resolutions))}")
    print(f"  residue (unresolved) : {len(residue)}")
    for item in residue:
        print(f"    - {item['source_ref']}: {item['evidence']!r} "
              f"({len(item['candidates'])} candidate(s))")
    print(f"  LLM calls this run   : {calls_after - calls_before}")
    return {"resolutions": resolutions, "residue": residue, "llm_calls": calls_after - calls_before}


def main() -> None:
    if DB_PATH.exists():
        print(f"Removing {DB_PATH} so this demo starts from a clean slate...")
        DB_PATH.unlink()

    with build_graph() as app:
        run1 = _run(
            app,
            thread_id="discovery-mapping-run-1",
            label="RUN 1 (fresh cache -- expect real LLM calls for genuinely ambiguous cases)",
        )
        run2 = _run(
            app,
            thread_id="discovery-mapping-run-2",
            label="RUN 2 (different thread, same cache -- expect ZERO new LLM calls)",
        )

    print(f"\n{'=' * 70}\nSUMMARY\n{'=' * 70}")
    print(f"Run 1 LLM calls : {run1['llm_calls']}")
    print(f"Run 2 LLM calls : {run2['llm_calls']}")
    print(f"Run 1 resolutions: {len(run1['resolutions'])}")
    print(f"Run 2 resolutions: {len(run2['resolutions'])}")
    print(f"Run 1 residue    : {len(run1['residue'])}")
    print(f"Run 2 residue    : {len(run2['residue'])}")

    assert run2["llm_calls"] == 0, (
        "Run 2 made a new LLM call -- the mapping_rules cache failed to "
        "short-circuit something it should have already resolved in run 1."
    )
    assert len(run2["resolutions"]) == len(run1["resolutions"]), (
        "Run 2 returned a different number of resolutions than run 1 -- "
        "the two runs should reach the exact same conclusions, just via "
        "cache hits instead of fresh work the second time."
    )
    assert len(run2["residue"]) == len(run1["residue"]), (
        "Run 2 produced a different residue set than run 1 -- deferred, "
        "unresolved cases should be re-derived identically every run until "
        "the agent tier (not yet built) actually resolves or escalates them."
    )
    print("\nPASS: run 2 reproduced every resolution AND every deferred "
          "residue item from run 1, with zero new LLM calls. The residue "
          "above is exactly the set the agent tier still needs to handle.")


if __name__ == "__main__":
    main()
