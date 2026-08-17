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

PRECISION_TIERS = (
    ("TIER_A_full", 1068),
    ("TIER_B_committed", 385),
    ("TIER_C_reduced", 171),
    ("TIER_D_minimum_inferential", 97),
)


def _expected_authority(n_tasks: int) -> str:
    for name, required in PRECISION_TIERS:
        if n_tasks >= required:
            return name
    return "DESCRIPTIVE_ONLY"


def _rate(value: float | None) -> str:
    return "CANNOT_CHECK" if value is None else f"{value:.4f}"


def render(data: dict) -> str:
    if data.get("schema_version") != "orion.p2.offline-route-stop-oracle.v1":
        raise ValueError("unexpected route-stop oracle schema")
    n_tasks = data.get("n_tasks")
    if not isinstance(n_tasks, int) or isinstance(n_tasks, bool) or n_tasks < 1:
        raise ValueError("route-stop table requires a positive integer n_tasks")
    expected_authority = _expected_authority(n_tasks)
    if data.get("analysis_authority") != expected_authority:
        raise ValueError(
            "route-stop authority does not match the frozen precision tiers: "
            f"n={n_tasks} requires {expected_authority}"
        )

    lines = [
        "# Table P2-S1 — Complete-gold route-stop oracle replay",
        "",
        f"**Authority:** `{expected_authority}`; {n_tasks} frozen tasks. Deterministic repeat seeds were checked for identical route/stop traces and collapsed within task before counting denominators. The authority is an achieved precision tier, not a promoted primary claim.",
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

    orion = systems["orion_full"]
    restricted = data["orion_full_by_route"]["RESTRICTED"]
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "O1 defines a route-stop false positive as a declared route stop while at least one previously unfound gold identity remains reachable on that route and at least one route-call budget unit remains. It defines a route-stop false negative as **more than one** attempt after the gold-defined oracle exhaustion point; one confirming attempt is explicitly allowed.",
            "",
            f"Full ORION records {orion['route_stop_false_positive_count']} O1 route-stop FP in {orion['route_stop_events']} route-stop events ({orion['route_stop_false_positive_rate']:.4f}) and {orion['route_stop_false_negative_count']} FN over {orion['routes_reaching_oracle_exhaustion']} routes that reach oracle exhaustion. On the `RESTRICTED` route, {restricted['route_stop_false_positive_count']} stops are false positives, {restricted['routes_reaching_oracle_exhaustion']} task-routes reach oracle exhaustion, and {restricted['attempts_after_exhaustion_total']} post-exhaustion attempts are retained.",
            "",
            "A route-level FP does **not** automatically become a task-level false closure: O4 keeps unresolved unavailable-route evidence open, and full ORION may return `CANNOT_CHECK` instead of asserting task completeness. This is the intended separation between route stopping and task stopping.",
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
