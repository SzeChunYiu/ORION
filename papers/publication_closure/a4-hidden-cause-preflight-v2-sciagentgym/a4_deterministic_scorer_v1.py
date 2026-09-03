#!/usr/bin/env python3
"""A4 deterministic scoring layer over SciAgentGym refine traces.

House rule enforced here: an LLM-adjudicated agreement is never gold. The gym's
refine evaluation records, per sub-question, a ``status`` and a ``match_type``.
This layer admits ONLY deterministic match types as success, demotes any
LLM-adjudicated positive to ``CANNOT_CHECK_LLM_ADJUDICATED``, and treats every
mismatch (including the gym's ``manual_and_llm_failed``) as failure.

Frozen rules (machine twin: A4_SCORING_AND_PARTITION_FREEZE_V1.json):
- DETERMINISTIC_MATCH_TYPES = {"exact", "rounded"} — structural equality and
  the gym's fixed numeric-rounding comparison; both are code-defined in the
  pinned gym commit, no model in the loop.
- sub-question SUCCESS  <=> status == "match" and match_type deterministic;
- sub-question CANNOT_CHECK <=> status == "match" and match_type NOT
  deterministic (LLM or unknown adjudication);
- otherwise FAILURE;
- case deterministic_score = successes / (successes + failures)  (CANNOT_CHECK
  excluded from the denominator and reported separately);
- case strict_success <=> zero failures, zero CANNOT_CHECK, >=1 sub-question.

Usage:
  a4_deterministic_scorer_v1.py TRACE.json [TRACE2.json ...]
  a4_deterministic_scorer_v1.py --self-test
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

DETERMINISTIC_MATCH_TYPES = frozenset({"exact", "rounded"})


def score_trace(trace: dict) -> dict:
    details = trace.get("evaluation_details") or {}
    succ = fail = cc = 0
    cc_paths, fail_paths = [], []
    for path, row in sorted(details.items()):
        if not isinstance(row, dict):
            fail += 1
            fail_paths.append(path)
            continue
        status = row.get("status")
        mt = row.get("match_type")
        if status == "match" and mt in DETERMINISTIC_MATCH_TYPES:
            succ += 1
        elif status == "match":
            cc += 1
            cc_paths.append(path)
        else:
            fail += 1
            fail_paths.append(path)
    denom = succ + fail
    return {
        "schema": "ORION.A4.DeterministicScore.v1",
        "case_id": trace.get("id"),
        "model": trace.get("model"),
        "subquestions": len(details),
        "success": succ,
        "failure": fail,
        "cannot_check_llm_adjudicated": cc,
        "cannot_check_paths": cc_paths,
        "deterministic_score": (succ / denom) if denom else 0.0,
        "strict_success": bool(details) and fail == 0 and cc == 0,
        "extraction_success": trace.get("answer_extraction_success"),
        "gym_reported_score": trace.get("evaluation_score"),
    }


def self_test() -> None:
    base = {
        "id": "t", "model": "m", "answer_extraction_success": True,
        "evaluation_score": 0.5,
        "evaluation_details": {
            "a": {"status": "match", "match_type": "exact"},
            "b": {"status": "match", "match_type": "rounded"},
            "c": {"status": "mismatch", "match_type": "manual_and_llm_failed"},
        },
    }
    r = score_trace(base)
    assert (r["success"], r["failure"], r["cannot_check_llm_adjudicated"]) == (2, 1, 0)
    assert abs(r["deterministic_score"] - 2 / 3) < 1e-12 and not r["strict_success"]

    # hostile: an LLM-accepted match must NOT count as success
    llm = json.loads(json.dumps(base))
    llm["evaluation_details"]["c"] = {"status": "match", "match_type": "llm_matched"}
    r2 = score_trace(llm)
    assert r2["success"] == 2 and r2["cannot_check_llm_adjudicated"] == 1
    assert not r2["strict_success"], "LLM-adjudicated match leaked into strict success"
    assert abs(r2["deterministic_score"] - 1.0) < 1e-12  # CC out of denominator

    # hostile: unknown match_type on a match is CANNOT_CHECK, not success
    unk = json.loads(json.dumps(base))
    unk["evaluation_details"]["a"] = {"status": "match", "match_type": "semantic_v2"}
    r3 = score_trace(unk)
    assert r3["success"] == 1 and r3["cannot_check_llm_adjudicated"] == 1

    # hostile: empty details is never strict success
    assert not score_trace({"evaluation_details": {}})["strict_success"]

    print("A4_SCORER_SELF_TEST_GREEN")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("traces", nargs="*", type=Path)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
        return 0
    for p in a.traces:
        print(json.dumps(score_trace(json.loads(p.read_text())), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
