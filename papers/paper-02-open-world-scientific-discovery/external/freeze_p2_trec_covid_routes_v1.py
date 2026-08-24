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
OUT = Path(__file__).resolve().parent / "P2_TREC_COVID_ROUTE_FREEZE_V1.json"

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
    "max_reads": 20,
    "max_tool_calls": 40,
    "max_model_tokens": 0,
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
        "schema": "P2.TrecCovidRouteFreeze.v1",
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
