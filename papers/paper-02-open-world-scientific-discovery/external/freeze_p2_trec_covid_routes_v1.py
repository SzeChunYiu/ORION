#!/usr/bin/env python3
"""Freeze the TREC-COVID topic -> route-probe mapping, before any arm is scored.

This is the artifact whose absence made the ORION arm CANNOT_CHECK in
P2_TREC_COVID_EXTERNAL_BASELINES_V1.json. It is written and committed on its
own, ahead of scoring, so the mapping cannot be adjusted once an arm's number
is known.

Route availability is a property of the corpus, not a knob:

  LEXICAL        available   probe = the topic's keyword query
  REFORMULATION  available   probes = the topic's question and narrative
  SEMANTIC       available   probe = the topic's question, scored distributionally
  CITATION       UNAVAILABLE BEIR trec-covid ships no reference edges
  RESTRICTED     UNAVAILABLE there is no gated provider for this corpus

The two unavailable routes are recorded as unavailable rather than dropped.
ORION's plan computes ``complete = not saw_unavailable and not
budget_exhausted``, so an honest unavailability is exactly what the arm is
supposed to notice. Fabricating citation edges or a restricted provider to
make the routes appear available would manufacture the thing being measured.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

DATA = Path.home() / "orion-work/trec/trec-covid"
OUT = Path(__file__).resolve().parent / "P2_TREC_COVID_ROUTE_FREEZE_V3.json"

AVAILABLE = {
    "LEXICAL": ["keyword"],
    "REFORMULATION": ["question", "narrative"],
    "SEMANTIC": ["question"],
}
UNAVAILABLE = {
    "CITATION": "BEIR trec-covid ships no reference edges; no citation graph exists to probe",
    "RESTRICTED": "no gated provider exists for this corpus",
}

#: Matched across every arm. max_route_calls sits below the 4 probes x 3 routes
#: an exhaustive prober would spend, so route allocation and stopping stay the
#: thing under measurement rather than a formality.
BUDGET = {
    "max_route_calls": 6,
    # V2 set this to 20. The first route returns a depth-100 posting and the
    # policy reads until the cap, so LEXICAL alone consumed the entire read
    # budget; the session then stays closed and every later route stopped with
    # budget_exhausted. Every arm degenerated to a single route, which is the
    # one thing this comparison must not do.
    #
    # The principle, stated rather than tuned: the budget must let each
    # AVAILABLE route be probed and its results read, so that what binds is
    # route allocation -- the quantity under measurement -- and not read
    # starvation on whichever route happens to run first. Three routes are
    # available here, so the per-route allowance of 20 is multiplied by three.
    "max_reads": 60,
    "max_tool_calls": 40,
    # V1 set this to 0 to mean "no model budget". Budget.__post_init__ rejects
    # anything below 1, so V1 could not be constructed and no arm ever ran on
    # it. 1 is the smallest value the harness accepts and carries the same
    # meaning: every arm here is deterministic and spends no model tokens, so
    # this dimension cannot bind. If some future arm did spend one, it would
    # exhaust immediately, which is the correct behaviour for a no-model study.
    "max_model_tokens": 1,
    "max_wallclock_seconds": 600.0,
}
POSTING_DEPTH = 100


def main() -> int:
    qpath = DATA / "queries.jsonl"
    if not qpath.is_file():
        print(f"P2_ROUTE_FREEZE_CANNOT_CHECK: {qpath} not found")
        return 3
    topics = []
    for line in qpath.open():
        row = json.loads(line)
        meta = row.get("metadata") or {}
        forms = {
            "question": row.get("text", "").strip(),
            "keyword": (meta.get("query") or "").strip(),
            "narrative": (meta.get("narrative") or "").strip(),
        }
        missing = [k for k, v in forms.items() if not v]
        topics.append(
            {
                "topic": row["_id"],
                "probe_text": forms,
                "missing_forms": missing,
                "routes": {r: [p for p in ps if forms.get(p)] for r, ps in AVAILABLE.items()},
            }
        )
    topics.sort(key=lambda t: int(t["topic"]))

    freeze = {
        "schema": "P2.TrecCovidRouteFreeze.v3",
        "supersedes": {
            "artifact": "P2_TREC_COVID_ROUTE_FREEZE_V2.json",
            "sha256": "1b1fca4008c9ed54bc27feff658972fbb68d8c86d38db47e267f8d0ae45a7e56",
            "reason": (
                "V2 froze max_reads=20. A depth-100 posting let the first route "
                "consume the whole read budget, closing the session, so every "
                "later route stopped with budget_exhausted and all four arms "
                "degenerated to one route -- the comparison could not occur. No "
                "arm was ever scored against V2. V1 and V2 are retained as "
                "historical freezes, not deleted."
            ),
        },
        "purpose": "topic -> route-probe mapping, frozen before any arm is scored",
        "corpus": "BEIR trec-covid",
        "available_routes": AVAILABLE,
        "unavailable_routes": UNAVAILABLE,
        "budget": BUDGET,
        "posting_depth": POSTING_DEPTH,
        "scoring": {
            "lexical_and_reformulation": "Okapi BM25, orion.study.p2.baselines tokenizer and IDF",
            "semantic": "orion.study.p2.baselines.HashedDistributionalScorer",
        },
        "topics": topics,
        "topic_count": len(topics),
    }
    body = json.dumps(freeze, indent=2, sort_keys=True) + "\n"
    OUT.write_text(body)
    digest = hashlib.sha256(body.encode()).hexdigest()
    print(f"topics frozen: {len(topics)}")
    print(f"topics missing a query form: {sum(1 for t in topics if t['missing_forms'])}")
    print(f"available routes: {sorted(AVAILABLE)}   unavailable: {sorted(UNAVAILABLE)}")
    print(f"wrote {OUT}")
    print(f"FREEZE_SHA256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
