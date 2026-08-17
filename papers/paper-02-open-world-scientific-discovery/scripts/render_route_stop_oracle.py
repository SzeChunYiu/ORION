#!/usr/bin/env python3
"""Render/check the complete-gold O1 route-stop FP/FN publication table."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1]
SOURCE = PAPER / "evidence" / "offline_results" / "ROUTE_STOP_ORACLE_V1.json"
OUTPUT = PAPER / "evidence" / "offline_results" / "TABLE_P2-S1_route_stop_oracle.md"

ORDER = (
    "orion_full",
    "protocol_driven_systematic_review",
    "bm25_keyword",
    "dense_retrieval",
    "sparse_dense_hybrid",
    "one_pass_rag",
    "agentic_single_route",
    "adaptive_multiroute_exploratory",
    "no_route_independence_check",
    "no_question_conditioned_read_ledger",
    "route_stop_can_close_task",
    "no_unavailable_route_open_state",
    "coverage_diagnostic_controls_stopping",
    "no_content_identity_dedup",
)

LABELS = {
    "orion_full": "ORION full",
    "protocol_driven_systematic_review": "Protocol-driven SLR",
    "bm25_keyword": "BM25 / keyword",
    "dense_retrieval": "Dense retrieval",
    "sparse_dense_hybrid": "Sparse+dense hybrid",
    "one_pass_rag": "One-pass RAG",
    "agentic_single_route": "Agentic single route",
    "adaptive_multiroute_exploratory": "Adaptive multiroute (exploratory)",
    "no_route_independence_check": "No route-independence check",
    "no_question_conditioned_read_ledger": "No question-conditioned read ledger",
    "route_stop_can_close_task": "Route stop can close task",
    "no_unavailable_route_open_state": "No unavailable-route open state",
    "coverage_diagnostic_controls_stopping": "Coverage diagnostic controls stopping",
    "no_content_identity_dedup": "No content-identity dedup",
}


def _rate(value: float | None) -> str:
    return "CANNOT_CHECK" if value is None else f"{value:.4f}"


def _frozen_binding() -> tuple[str, int]:
    """The authority and task count the run manifest binds this paper to.

    Read from the manifest rather than hardcoded, so the guard keeps checking that
    the table came from the committed frozen run instead of checking that the run is
    still the size it was when the guard was written.
    """

    payload = json.loads(
        (PAPER / "protocol" / "OFFLINE_RUN_MANIFEST_V1.json").read_text(encoding="utf-8")
    )
    return (
        str(payload["analysis_authority"]["status"]),
        int(payload["dataset_binding"]["tasks"]),
    )


def render(data: dict) -> str:
    if data.get("schema_version") != "orion.p2.offline-route-stop-oracle.v1":
        raise ValueError("unexpected route-stop oracle schema")
    authority, n_tasks = _frozen_binding()
    if data.get("analysis_authority") != authority or data.get("n_tasks") != n_tasks:
        raise ValueError(
            "route-stop table must come from the run the manifest binds "
            f"({authority}, {n_tasks} tasks); this projection reports "
            f"{data.get('analysis_authority')!r} over {data.get('n_tasks')!r} tasks"
        )

    lines = [
        "# Table P2-S1 — Complete-gold route-stop oracle replay",
        "",
        f"**Authority:** `{authority}`; {n_tasks} frozen tasks. Deterministic repeat seeds were checked for identical route/stop traces and collapsed within task before counting denominators.",
        "",
        "| System | Route-stop events | FP | FP rate | Routes reaching oracle exhaustion | FN | FN rate | Attempts after exhaustion |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    systems = data["systems"]
    if set(systems) != set(ORDER):
        raise ValueError("route-stop table system set drifted")
    for system_id in ORDER:
        row = systems[system_id]
        lines.append(
            "| {label} | {events} | {fp} | {fp_rate} | {exhausted} | {fn} | {fn_rate} | {after} |".format(
                label=LABELS[system_id],
                events=row["route_stop_events"],
                fp=row["route_stop_false_positive_count"],
                fp_rate=_rate(row["route_stop_false_positive_rate"]),
                exhausted=row["routes_reaching_oracle_exhaustion"],
                fn=row["route_stop_false_negative_count"],
                fn_rate=_rate(row["route_stop_false_negative_rate"]),
                after=row["attempts_after_exhaustion_total"],
            )
        )

    restricted = data["orion_full_by_route"]["RESTRICTED"]
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "O1 defines a route-stop false positive as a declared route stop while at least one previously unfound gold identity remains reachable on that route and at least one route-call budget unit remains. It defines a route-stop false negative as **more than one** attempt after the gold-defined oracle exhaustion point; one confirming attempt is explicitly allowed.",
            "",
            f"Full ORION records 1 O1 route-stop FP in 100 route-stop events (0.0100) and 0 FN over 99 routes that reach oracle exhaustion. The single FP is the frozen unavailable `RESTRICTED` case. That route has {restricted['routes_reaching_oracle_exhaustion']} exhaustible task-routes and {restricted['attempts_after_exhaustion_total']} total post-exhaustion attempts: exactly one allowed confirming attempt on each of the 19 non-censored tasks, so none is an FN.",
            "",
            "The route-level FP does **not** become a task-level false closure: O4 opens an unresolved obligation for the unavailable restricted route, and full ORION returns `CANNOT_CHECK` instead of asserting task completeness. This is the intended separation between route stopping and task stopping.",
            "",
            f"Source record digest: `{data['source_record_digest_sha256']}`  ",
            f"Source rich-artifact hash-list digest: `{data['source_raw_artifact_hash_list_digest_sha256']}`",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not args.write and not args.check:
        args.check = True

    content = render(json.loads(SOURCE.read_text(encoding="utf-8")))
    if args.write:
        OUTPUT.write_text(content, encoding="utf-8")
        print(f"wrote {OUTPUT.relative_to(PAPER)}")
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content:
            print("route-stop oracle table drifted", file=sys.stderr)
            return 1
        print("route-stop oracle table matches the frozen O1 projection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
