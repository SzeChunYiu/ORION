#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3] / "publication_closure"
sys.path.insert(0, str(ROOT))
from tier_a_analysis_common_v1 import bootstrap_mean_interval, mean, require_disjoint  # noqa: E402

DOMAINS = ("EARTH_ENVIRONMENT", "LIFE_BIOMEDICAL", "SCIENTIFIC_SOFTWARE", "PHYSICAL_ENGINEERING")
MECHANISMS = tuple(f"M{i}_{name}" for i, name in enumerate((
    "ABSTRACT_TO_FULLTEXT", "EARLIER_TO_LATER_VERSION", "PROTOCOL_TO_RESULTS",
    "ARTICLE_TO_CORRECTION", "ARTICLE_TO_DATA_DOCUMENTATION", "ARTICLE_TO_CODE_RELEASE",
    "CONFERENCE_ABSTRACT_TO_FULL_PAPER", "ARTICLE_TO_LICENSED_SUPPLEMENT",
), 1))
ARMS = (
    "CANDIDATE", "C1_CALIBRATED_THREEWAY_NLI", "C2_SCIENTIFIC_EVIDENCE_ESCALATION",
    "C3_PROVENANCE_AWARE_VERIFIER", "C4_INFORMATION_EQUIVALENT_TYPED_DONOR",
)
TERMINALS = ("ResolvedTrue", "ResolvedFalse", "CannotCheck")


def validate_row(row: dict[str, Any]) -> None:
    required = ("cluster_id", "split", "domain", "mechanism", "source_family_id", "gold_restricted", "gold_resolving", "outputs", "nuisance_probe_status")
    missing = [k for k in required if k not in row]
    if missing:
        raise ValueError(f"missing fields: {missing}")
    if row["split"] not in ("primary", "replication"):
        raise ValueError("bad split")
    if row["domain"] not in DOMAINS or row["mechanism"] not in MECHANISMS:
        raise ValueError("bad domain/mechanism")
    if row["gold_restricted"] != "CannotCheck":
        raise ValueError("restricted gold must be CannotCheck")
    if row["gold_resolving"] not in ("ResolvedTrue", "ResolvedFalse", "CANNOT_CHECK_GOLD"):
        raise ValueError("bad resolving gold")
    if row["nuisance_probe_status"] not in ("PASS", "FAIL", "CANNOT_CHECK"):
        raise ValueError("bad nuisance probe status")
    outputs = row["outputs"]
    if not isinstance(outputs, dict) or set(outputs) != set(ARMS):
        raise ValueError("outputs must contain exactly CANDIDATE and C1-C4")
    for arm in ARMS:
        rec = outputs[arm]
        if not isinstance(rec, dict) or set(rec) != {"restricted", "resolving"}:
            raise ValueError(f"bad output record for {arm}")
        if rec["restricted"] not in TERMINALS or rec["resolving"] not in TERMINALS:
            raise ValueError(f"terminal-interface violation for {arm}")
    if outputs["CANDIDATE"] != outputs["C4_INFORMATION_EQUIVALENT_TYPED_DONOR"]:
        raise ValueError("C4 information-equivalent donor mismatch")


def joint_success(row: dict[str, Any], arm: str) -> int | None:
    if row["gold_resolving"] == "CANNOT_CHECK_GOLD":
        return None
    out = row["outputs"][arm]
    return int(out["restricted"] == "CannotCheck" and out["resolving"] == row["gold_resolving"])


def rate(rows: list[dict[str, Any]], arm: str) -> float | None:
    vals = [v for r in rows if (v := joint_success(r, arm)) is not None]
    return mean(vals) if vals else None


def contrast(rows: list[dict[str, Any]], arm: str) -> list[float]:
    vals = []
    for r in rows:
        a = joint_success(r, "CANDIDATE")
        b = joint_success(r, arm)
        if a is not None and b is not None:
            vals.append(float(a - b))
    return vals


def _cell_counts(rows: list[dict[str, Any]], split: str) -> dict[str, int]:
    c = Counter(f"{r['domain']}|{r['mechanism']}" for r in rows if r["split"] == split)
    return {f"{d}|{m}": c[f"{d}|{m}"] for d in DOMAINS for m in MECHANISMS}


def analyze(payload: dict[str, Any], *, resamples: int = 10_000) -> dict[str, Any]:
    if payload.get("schema") != "ORION.A5.NaturalisticPanelResultInput.v1":
        raise ValueError("wrong schema")
    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise ValueError("rows must be list")
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("row must be object")
        validate_row(row)
        if row["cluster_id"] in seen:
            raise ValueError(f"duplicate cluster: {row['cluster_id']}")
        seen.add(row["cluster_id"])
    primary = [r for r in rows if r["split"] == "primary"]
    repl = [r for r in rows if r["split"] == "replication"]
    require_disjoint((r["source_family_id"] for r in primary), (r["source_family_id"] for r in repl), "source_family_id")
    pc = _cell_counts(rows, "primary")
    rc = _cell_counts(rows, "replication")
    quota_ok = len(primary) == 768 and len(repl) == 256 and all(v == 24 for v in pc.values()) and all(v == 8 for v in rc.values())

    primary_rates = {arm: rate(primary, arm) for arm in ARMS}
    repl_rates = {arm: rate(repl, arm) for arm in ARMS}
    adjudicated_primary = sum(r["gold_resolving"] != "CANNOT_CHECK_GOLD" for r in primary)
    adjudicated_repl = sum(r["gold_resolving"] != "CANNOT_CHECK_GOLD" for r in repl)
    undetermined = Counter(f"{r['domain']}|{r['mechanism']}" for r in rows if r["gold_resolving"] == "CANNOT_CHECK_GOLD")
    nuisance = Counter(r["nuisance_probe_status"] for r in rows)

    primary_contrasts: dict[str, Any] = {}
    repl_contrasts: dict[str, Any] = {}
    for arm in ARMS[1:]:
        pv = contrast(primary, arm)
        rv = contrast(repl, arm)
        if pv:
            plo, phi = bootstrap_mean_interval(pv, f"A5|primary|{arm}", resamples)
            primary_contrasts[arm] = {"mean": mean(pv), "ci95": [plo, phi], "n": len(pv)}
        else:
            primary_contrasts[arm] = {"mean": None, "ci95": None, "n": 0}
        if rv:
            rlo, rhi = bootstrap_mean_interval(rv, f"A5|replication|{arm}", resamples)
            repl_contrasts[arm] = {"mean": mean(rv), "ci95": [rlo, rhi], "n": len(rv)}
        else:
            repl_contrasts[arm] = {"mean": None, "ci95": None, "n": 0}

    domain_rates = {
        d: {arm: rate([r for r in primary if r["domain"] == d], arm) for arm in ARMS}
        for d in DOMAINS
    }
    mechanism_rates = {
        m: {arm: rate([r for r in primary if r["mechanism"] == m], arm) for arm in ARMS}
        for m in MECHANISMS
    }
    resolved_rates = [x for x in primary_rates.values() if x is not None]
    resolution = max(resolved_rates) - min(resolved_rates) if resolved_rates else 0.0

    c4_primary = primary_contrasts["C4_INFORMATION_EQUIVALENT_TYPED_DONOR"]
    c4_repl = repl_contrasts["C4_INFORMATION_EQUIVALENT_TYPED_DONOR"]
    c4_tie = c4_primary["mean"] in (0.0, None) and c4_repl["mean"] in (0.0, None)
    restricted_false_resolution = {
        arm: mean(int(r["outputs"][arm]["restricted"] != "CannotCheck") for r in primary) if primary else None
        for arm in ARMS
    }
    resolving_correct = {}
    for arm in ARMS:
        vals = [int(r["outputs"][arm]["resolving"] == r["gold_resolving"]) for r in primary if r["gold_resolving"] != "CANNOT_CHECK_GOLD"]
        resolving_correct[arm] = mean(vals) if vals else None

    nonc4 = ARMS[1:4]
    if not quota_ok or adjudicated_primary == 0 or adjudicated_repl == 0:
        diagnostic = "CANNOT_CHECK_PANEL_OR_GOLD"
    elif not c4_tie:
        diagnostic = "INVALID_C4_INFORMATION_PARITY"
    elif resolution == 0:
        diagnostic = "NO_PANEL_RESOLUTION"
    elif nuisance["FAIL"]:
        diagnostic = "NUISANCE_PROBE_FAILURE"
    else:
        candidate_p = primary_rates["CANDIDATE"] or 0.0
        strongest_p = max(primary_rates[a] or 0.0 for a in nonc4)
        candidate_r = repl_rates["CANDIDATE"] or 0.0
        strongest_r = max(repl_rates[a] or 0.0 for a in nonc4)
        if candidate_p <= strongest_p:
            diagnostic = "DONOR_EQUIVALENT_NULL"
        elif (candidate_p - strongest_p) * (candidate_r - strongest_r) <= 0:
            diagnostic = "REPLICATION_DISAGREEMENT"
        else:
            heterogeneous = False
            for rates in domain_rates.values():
                if (rates["CANDIDATE"] or 0.0) <= max(rates[a] or 0.0 for a in nonc4):
                    heterogeneous = True
            for rates in mechanism_rates.values():
                if (rates["CANDIDATE"] or 0.0) <= max(rates[a] or 0.0 for a in nonc4):
                    heterogeneous = True
            diagnostic = "HETEROGENEOUS_DOMAIN_OR_MECHANISM" if heterogeneous else "BOUNDED_POSITIVE_CONTRAST"

    return {
        "schema": "ORION.A5.NaturalisticPanelAnalysisResult.v1",
        "quota_ok": quota_ok,
        "primary_cell_counts": pc,
        "replication_cell_counts": rc,
        "adjudicated_primary_n": adjudicated_primary,
        "adjudicated_replication_n": adjudicated_repl,
        "undetermined_cells": dict(sorted(undetermined.items())),
        "nuisance_probe_status_counts": dict(sorted(nuisance.items())),
        "primary_arm_rates": primary_rates,
        "replication_arm_rates": repl_rates,
        "primary_candidate_contrasts": primary_contrasts,
        "replication_candidate_contrasts": repl_contrasts,
        "primary_domain_rates": domain_rates,
        "primary_mechanism_rates": mechanism_rates,
        "panel_resolution": resolution,
        "restricted_state_false_resolution_rate": restricted_false_resolution,
        "resolving_state_correct_resolution_rate": resolving_correct,
        "c4_exact_tie": c4_tie,
        "diagnostic_terminal": diagnostic,
    }


def _fixture() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    n = 0
    for split, per in (("primary", 24), ("replication", 8)):
        for domain in DOMAINS:
            for mechanism in MECHANISMS:
                for _ in range(per):
                    cid = f"{split}-{n}"
                    candidate = {"restricted": "CannotCheck", "resolving": "ResolvedTrue"}
                    rows.append({
                        "cluster_id": cid,
                        "split": split,
                        "domain": domain,
                        "mechanism": mechanism,
                        "source_family_id": f"source-{cid}",
                        "gold_restricted": "CannotCheck",
                        "gold_resolving": "ResolvedTrue",
                        "outputs": {
                            "CANDIDATE": dict(candidate),
                            "C1_CALIBRATED_THREEWAY_NLI": {"restricted": "ResolvedTrue", "resolving": "ResolvedTrue"},
                            "C2_SCIENTIFIC_EVIDENCE_ESCALATION": {"restricted": "ResolvedTrue", "resolving": "ResolvedTrue"},
                            "C3_PROVENANCE_AWARE_VERIFIER": {"restricted": "ResolvedTrue", "resolving": "ResolvedTrue"},
                            "C4_INFORMATION_EQUIVALENT_TYPED_DONOR": dict(candidate),
                        },
                        "nuisance_probe_status": "PASS",
                    })
                    n += 1
    return {"schema": "ORION.A5.NaturalisticPanelResultInput.v1", "rows": rows}


def self_test() -> dict[str, Any]:
    payload = _fixture()
    result = analyze(payload, resamples=64)
    assert result["quota_ok"] is True
    assert result["c4_exact_tie"] is True
    assert result["panel_resolution"] > 0
    assert result["diagnostic_terminal"] == "BOUNDED_POSITIVE_CONTRAST"
    bad = _fixture()
    bad["rows"][0]["outputs"]["C4_INFORMATION_EQUIVALENT_TYPED_DONOR"]["resolving"] = "ResolvedFalse"
    try:
        analyze(bad, resamples=16)
    except ValueError as exc:
        assert "C4" in str(exc)
    else:
        raise AssertionError("C4 mismatch mutant was not rejected")
    return {"decision": "GREEN", "rows": len(payload["rows"]), "diagnostic": result["diagnostic_terminal"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
        return 0
    if args.input is None:
        parser.error("input JSON required unless --self-test")
    result = analyze(json.loads(args.input.read_text(encoding="utf-8")))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
