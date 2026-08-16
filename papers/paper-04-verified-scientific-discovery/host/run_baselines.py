#!/usr/bin/env python3
"""Gold-blind deterministic mechanism baselines for P4.

The input is the same opaque candidate-visible manifest used by the ORION arm.
No attack family, expected terminal, custody class, or protected gold is accepted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any, Callable

PANEL_BASELINE_IDS = (
    "provenanceguard-style-source-routing",
    "attributionbench-multisource-attribution",
    "fire-iterative-retrieve-or-verify",
    "claimbench-sciclaimhunt-scientific-evidence",
    "provenai-citation-fidelity-influence",
    "rewardhackingagents-search-contamination",
)
EXTRA_BASELINE_IDS = (
    "citation-presence-format",
    "pooled-evidence-nli-support",
    "claim-level-auditability-provenance",
)


def _read_cases(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            raw = json.loads(line)
            if set(raw) != {"case_id", "candidate_visible"}:
                raise ValueError("baseline manifest may contain only case_id and candidate_visible")
            rows.append(raw)
    return rows


def _assigned(view: dict[str, Any]) -> dict[str, Any] | None:
    assigned = view.get("claim", {}).get("assigned_evidence_id")
    for item in view.get("evidence", []):
        if isinstance(item, dict) and item.get("evidence_id") == assigned:
            return item
    return None


def _content_valid(item: dict[str, Any] | None) -> bool:
    if item is None:
        return False
    content = item.get("content")
    if not isinstance(content, str):
        return False
    actual = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return (
        actual == item.get("content_hash") == item.get("declared_content_hash")
        and item.get("provenance_hash") == item.get("declared_provenance_hash")
    )


def _source_match(item: dict[str, Any] | None) -> bool:
    return bool(item and item.get("source_id") == item.get("assigned_source_id"))


def _support_token(view: dict[str, Any]) -> str:
    token = view.get("claim", {}).get("support_token")
    return token if isinstance(token, str) else ""


def _supports(view: dict[str, Any], item: dict[str, Any] | None) -> bool:
    token = _support_token(view)
    return bool(item and token and f"SUPPORT::{token}" in str(item.get("content", "")))


def _contradicts(view: dict[str, Any], item: dict[str, Any] | None) -> bool:
    token = _support_token(view)
    return bool(item and token and f"CONTRADICT::{token}" in str(item.get("content", "")))


def _pool(view: dict[str, Any]) -> list[dict[str, Any]]:
    values = []
    for key in ("evidence", "retrieval_pool"):
        for item in view.get(key, []):
            if isinstance(item, dict) and item not in values:
                values.append(item)
    return values


def _pooled_support(view: dict[str, Any]) -> bool:
    return any(_supports(view, item) for item in _pool(view))


def _pooled_contradiction(view: dict[str, Any]) -> bool:
    return any(_contradicts(view, item) for item in _pool(view))


def _influence(view: dict[str, Any], item: dict[str, Any] | None) -> bool:
    used = view.get("behavioral_trace", {}).get("used_evidence_ids", [])
    return bool(item and isinstance(used, list) and item.get("evidence_id") in used)


def _contaminated(view: dict[str, Any]) -> bool:
    return any(
        isinstance(item, dict) and item.get("benchmark_gold_visible") is True
        for item in view.get("search_trace", [])
    )


def _protected_access(view: dict[str, Any]) -> bool:
    return any(
        isinstance(item, dict)
        and (
            item.get("scope") == "PROTECTED"
            or "/protected/" in str(item.get("path", ""))
            or str(item.get("path", "")).startswith("protected/")
        )
        for item in view.get("access_requests", [])
    )


def _posthoc_or_compromised(view: dict[str, Any]) -> bool:
    answer_round = view.get("answer", {}).get("created_round", 1)
    checker_round = view.get("checker", {}).get("created_round", 0)
    frozen_round = view.get("evaluator", {}).get("frozen_round", 0)
    return (
        view.get("evaluator", {}).get("integrity") != "INTACT"
        or checker_round > answer_round
        or frozen_round > answer_round
    )


def _support_label(supported: bool, contradicted: bool) -> str:
    if supported:
        return "SUPPORTED"
    if contradicted:
        return "CONTRADICTED"
    return "INSUFFICIENT"


def _result(
    case_id: str,
    system_id: str,
    *,
    terminal: str,
    claim_prediction: bool,
    source_prediction: bool,
    support_prediction: str,
    conflation: bool,
    substitution: bool,
    tamper: bool,
    contamination: bool,
    resource_units: float,
    started_ns: int,
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "system_id": system_id,
        "authority_terminal": terminal,
        "claim_correct_prediction": claim_prediction,
        "source_attribution_prediction": source_prediction,
        "support_prediction": support_prediction,
        "conflation_detected": conflation,
        "substitution_detected": substitution,
        "tamper_leakage_detected": tamper,
        "search_contamination_detected": contamination,
        "reason_codes": [],
        "resource_units": resource_units,
        "latency_seconds": (time.perf_counter_ns() - started_ns) / 1_000_000_000,
    }


def _provenanceguard(case_id: str, view: dict[str, Any]) -> dict[str, Any]:
    t = time.perf_counter_ns(); item = _assigned(view)
    content = _content_valid(item); source = _source_match(item); sup = _supports(view, item); con = _contradicts(view, item)
    terminal = "CANNOT_CHECK" if item is None else ("PROMOTE" if content and source and sup else "BLOCK")
    return _result(case_id, PANEL_BASELINE_IDS[0], terminal=terminal, claim_prediction=sup, source_prediction=source, support_prediction=_support_label(sup, con), conflation=not source if item else False, substitution=not content if item else False, tamper=False, contamination=False, resource_units=5.0, started_ns=t)


def _attribution(case_id: str, view: dict[str, Any]) -> dict[str, Any]:
    t = time.perf_counter_ns(); item = _assigned(view); source = _source_match(item); sup = _pooled_support(view); con = _pooled_contradiction(view)
    terminal = "CANNOT_CHECK" if not _pool(view) else ("PROMOTE" if source and sup else "BLOCK")
    return _result(case_id, PANEL_BASELINE_IDS[1], terminal=terminal, claim_prediction=sup, source_prediction=source, support_prediction=_support_label(sup, con), conflation=not source if item else False, substitution=False, tamper=False, contamination=False, resource_units=3.0, started_ns=t)


def _fire(case_id: str, view: dict[str, Any]) -> dict[str, Any]:
    t = time.perf_counter_ns(); item = _assigned(view); candidates = [ev for ev in _pool(view) if _content_valid(ev) and _supports(view, ev)]
    sup = bool(candidates); con = _pooled_contradiction(view); source = _source_match(item)
    terminal = "CANNOT_CHECK" if not _pool(view) else ("PROMOTE" if sup else "BLOCK")
    return _result(case_id, PANEL_BASELINE_IDS[2], terminal=terminal, claim_prediction=sup, source_prediction=source, support_prediction=_support_label(sup, con), conflation=False, substitution=bool(item and not _content_valid(item)), tamper=False, contamination=False, resource_units=6.0, started_ns=t)


def _claimbench(case_id: str, view: dict[str, Any]) -> dict[str, Any]:
    t = time.perf_counter_ns(); pool = _pool(view); sup = _pooled_support(view); con = _pooled_contradiction(view)
    terminal = "CANNOT_CHECK" if not pool else ("PROMOTE" if sup else "BLOCK")
    return _result(case_id, PANEL_BASELINE_IDS[3], terminal=terminal, claim_prediction=sup, source_prediction=True, support_prediction=_support_label(sup, con), conflation=False, substitution=False, tamper=False, contamination=False, resource_units=4.0, started_ns=t)


def _provenai(case_id: str, view: dict[str, Any]) -> dict[str, Any]:
    t = time.perf_counter_ns(); item = _assigned(view); content = _content_valid(item); source = _source_match(item); sup = _supports(view, item); con = _contradicts(view, item); influence = _influence(view, item)
    terminal = "CANNOT_CHECK" if item is None else ("PROMOTE" if content and source and sup and influence else "BLOCK")
    return _result(case_id, PANEL_BASELINE_IDS[4], terminal=terminal, claim_prediction=sup, source_prediction=source, support_prediction=_support_label(sup, con), conflation=not source if item else False, substitution=not content if item else False, tamper=False, contamination=False, resource_units=5.0, started_ns=t)


def _reward(case_id: str, view: dict[str, Any]) -> dict[str, Any]:
    t = time.perf_counter_ns(); pool = _pool(view); sup = _pooled_support(view); con = _pooled_contradiction(view); contam = _contaminated(view); tamper = _protected_access(view) or _posthoc_or_compromised(view)
    terminal = "CANNOT_CHECK" if not pool else ("BLOCK" if contam or tamper else ("PROMOTE" if sup else "BLOCK"))
    return _result(case_id, PANEL_BASELINE_IDS[5], terminal=terminal, claim_prediction=sup, source_prediction=True, support_prediction=_support_label(sup, con), conflation=False, substitution=False, tamper=tamper, contamination=contam, resource_units=5.0, started_ns=t)


def _citation(case_id: str, view: dict[str, Any]) -> dict[str, Any]:
    t = time.perf_counter_ns(); item = _assigned(view); present = bool(item and item.get("evidence_id") and item.get("url")); sup = bool(item); terminal = "PROMOTE" if present else "CANNOT_CHECK"
    return _result(case_id, EXTRA_BASELINE_IDS[0], terminal=terminal, claim_prediction=sup, source_prediction=True, support_prediction="SUPPORTED" if sup else "INSUFFICIENT", conflation=False, substitution=False, tamper=False, contamination=False, resource_units=1.0, started_ns=t)


def _pooled(case_id: str, view: dict[str, Any]) -> dict[str, Any]:
    t = time.perf_counter_ns(); pool = _pool(view); sup = _pooled_support(view); con = _pooled_contradiction(view); terminal = "CANNOT_CHECK" if not pool else ("PROMOTE" if sup else "BLOCK")
    return _result(case_id, EXTRA_BASELINE_IDS[1], terminal=terminal, claim_prediction=sup, source_prediction=True, support_prediction=_support_label(sup, con), conflation=False, substitution=False, tamper=False, contamination=False, resource_units=2.0, started_ns=t)


def _auditability(case_id: str, view: dict[str, Any]) -> dict[str, Any]:
    t = time.perf_counter_ns(); item = _assigned(view); content = _content_valid(item); sup = _supports(view, item); con = _contradicts(view, item); influence = _influence(view, item); terminal = "CANNOT_CHECK" if item is None else ("PROMOTE" if content and sup and influence else "BLOCK")
    return _result(case_id, EXTRA_BASELINE_IDS[2], terminal=terminal, claim_prediction=sup, source_prediction=True, support_prediction=_support_label(sup, con), conflation=False, substitution=not content if item else False, tamper=False, contamination=False, resource_units=5.0, started_ns=t)


RUNNERS: tuple[Callable[[str, dict[str, Any]], dict[str, Any]], ...] = (
    _provenanceguard, _attribution, _fire, _claimbench, _provenai, _reward,
    _citation, _pooled, _auditability,
)


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("manifest", type=Path); parser.add_argument("output", type=Path); args = parser.parse_args()
    cases = _read_cases(args.manifest)
    with args.output.open("w", encoding="utf-8") as handle:
        for row in cases:
            for runner in RUNNERS:
                handle.write(json.dumps(runner(row["case_id"], row["candidate_visible"]), sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
