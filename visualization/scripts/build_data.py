#!/usr/bin/env python3
"""Build the normalized ORION P1-P15 visualization dataset.

This extractor deliberately names every transformation.  It never fills a
missing source, and it never turns receipt integrity into external authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path
from typing import Any


SCHEMA = "orion.visualization.evidence-atlas.v1"
AUTHORITY_BOUNDARY = "REPOSITORY_RECEIPTS_ONLY__NO_EXTERNAL_AUTHORITY_DELTA"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def finite(value: Any, label: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{label} is not finite")
    return number


def detected_schema(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None
    for key in ("schema", "schema_version", "campaign_id", "record"):
        if key in payload:
            return str(payload[key])
    return None


def git_value(root: Path, *args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), *args], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def source_manifest(
    root: Path, catalog: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records: list[dict[str, Any]] = []
    payloads: dict[str, Any] = {}
    for entry in catalog["sources"]:
        path = root / entry["path"]
        if not path.is_file():
            raise FileNotFoundError(f"CANNOT_CHECK missing registered source: {entry['path']}")
        payload: Any = None
        if path.suffix == ".json":
            payload = read_json(path)
            payloads[entry["id"]] = payload
        records.append(
            {
                "id": entry["id"],
                "paper": entry["paper"],
                "path": entry["path"],
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
                "declared_schema": entry["schema"],
                "detected_schema": detected_schema(payload),
                "role": entry["role"],
                "authority_tier": entry["authority_tier"],
                "transform_id": entry["transform_id"],
                "fields": entry["fields"],
            }
        )
    return records, payloads


def normalize_paper_states(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    titles = {
        "P1": "Recursive Epistemic Reconstruction",
        "P2": "Open-World Scientific Knowledge Discovery",
        "P3": "Global Knowledge Portrait",
        "P4": "Verified Scientific Discovery",
        "P5": "Self-ORION",
        "P6": "Formal Epistemic Structures and Mechanics",
        "P7": "Epistemic Navigation in Open Worlds",
        "P8": "Epistemic Authority for Autonomous Science",
        "P9": "Structured Epistemic Learning",
        "P10": "Structured Problem Solving",
        "P11": "State as Computation",
        "P12": "Adaptive State-Reasoning Co-Design",
        "P13": "Responsibility-Carrying State",
        "P14": "ORION-RSE",
        "P15": "ORION Research Harness",
    }
    rows: list[dict[str, Any]] = []
    for item in ledger["papers"]:
        paper = item["paper"]
        terminal = item["terminal"]
        writing_class = item["writing_class"]
        terminal_upper = terminal.upper()
        if "INVALID" in terminal_upper:
            state = "FAIL"
        elif any(
            marker in terminal_upper
            for marker in (
                "CANNOT_CHECK",
                "UNAVAILABLE",
                "ABSENT",
                "NOT_RUN",
                "NOT_EXECUTED",
                "NOT_CONTENT_BOUND",
                "BLOCKED",
            )
        ):
            state = "CANNOT_CHECK"
        elif any(marker in terminal_upper for marker in ("SUPPORTED", "STRICTLY_EXTENDS", "BEATS")):
            state = "BOUNDED_PASS"
        else:
            state = "UNKNOWN"
        rows.append(
            {
                "paper": paper,
                "paper_id": paper,
                "title": titles[paper],
                "job_id": item["job_id"],
                "terminal": terminal,
                "status": state,
                "writing_class": writing_class,
                "state": state,
                "authority": "CANNOT_CHECK_EXTERNAL",
                "claim_ceiling": writing_class,
                "allowed": item.get("allowed", []),
                "forbidden": item.get("forbidden", []),
                "source_id": "portfolio_claim_ledger",
            }
        )
    if [row["paper"] for row in rows] != [f"P{i}" for i in range(1, 16)]:
        raise ValueError("portfolio claim ledger does not contain canonical P1-P15 order")
    return rows


def gate_states() -> list[dict[str, str]]:
    bounded = {
        "P1": (
            "BOUNDED_PASS",
            "confirmatory arm result; separate protected programme remains unavailable",
        ),
        "P2": ("FAIL", "frozen TREC-COVID recall/cost gate failed"),
        "P3": ("BOUNDED_PASS", "32 deterministic confirmatory cases"),
        "P4": ("BOUNDED_PASS", "400 exact heterogeneous contracts; ideal typed product ties"),
        "P5": ("ADVERSE", "24 authored cases per arm with requested/served model drift"),
        "P6": ("BOUNDED_PASS", "complete finite certificate-lifting state space"),
        "P7": ("FAIL", "programme execution invalidated by planned/observed denominator drift"),
        "P8": ("BOUNDED_PASS", "mechanized calculus and representative-pair internal audit"),
        "P9": (
            "CANNOT_CHECK",
            "one protected-gold cell is CANNOT_CHECK and replay discrepancy remains",
        ),
        "P10": ("CANNOT_CHECK", "prospective H1-H6 outcome was not executed"),
        "P11": ("FAIL", "query-family primary terminal is GATE_NOT_MET"),
        "P12": (
            "BOUNDED_PASS",
            "equal-action complementarity is bounded; forward-time successor not established",
        ),
        "P13": ("BOUNDED_PASS", "registered randomized finite-world comparison"),
        "P14": ("BOUNDED_PASS", "28 internally authored governance-contract cases"),
        "P15": ("MIXED", "three authorized workflows and one honest CANNOT_CHECK"),
    }
    rows: list[dict[str, str]] = []
    for paper in [f"P{i}" for i in range(1, 16)]:
        state, reason = bounded[paper]
        rows.extend(
            [
                {
                    "paper": paper,
                    "gate": "registered_source",
                    "state": "PASS",
                    "reason": "source path and digest registered",
                },
                {"paper": paper, "gate": "bounded_result", "state": state, "reason": reason},
                {
                    "paper": paper,
                    "gate": "external_authority",
                    "state": "CANNOT_CHECK",
                    "reason": "no visualization receipt creates independent external authority",
                },
            ]
        )
    return rows


def anomalies() -> list[dict[str, str]]:
    rows = [
        {
            "paper": "P2",
            "severity": "FAIL",
            "kind": "frozen_gate",
            "source_id": "p2_trec_covid",
            "finding": "Overall gate fails although nDCG@10 improves: recall noninferiority CI crosses the margin and reads rise 175.7%.",
        },
        {
            "paper": "P3",
            "severity": "NULL",
            "kind": "zero_delta",
            "source_id": "p3_confirmatory",
            "finding": "The false-split comparison is exactly zero on 32 deterministic cases; a zero delta is not a necessity proof.",
        },
        {
            "paper": "P4",
            "severity": "BOUNDARY",
            "kind": "ideal_tie",
            "source_id": "p4_protected",
            "finding": "P4-X ties the ideal typed product at 400/400; this locates a factorization boundary rather than superiority over the ideal.",
        },
        {
            "paper": "P5",
            "severity": "ADVERSE",
            "kind": "execution_identity_drift",
            "source_id": "p5_attribution",
            "finding": "The requested model was glm-5.2 but both arms report served model glm-5.3.",
        },
        {
            "paper": "P6",
            "severity": "BOUNDARY",
            "kind": "replication_multiplier",
            "source_id": "p6_certificate_lifting",
            "finding": "The 320 evaluations include a donor multiplier of five; the receipt says the liftability rule does not read that axis.",
        },
        {
            "paper": "P7",
            "severity": "FAIL",
            "kind": "denominator_drift",
            "source_id": "portfolio_claim_ledger",
            "finding": "The programme preserves an invalid run with 738 planned versus 736 observed cases; it supports no empirical transport claim.",
        },
        {
            "paper": "P8",
            "severity": "BOUNDARY",
            "kind": "state_multiplicity",
            "source_id": "p8_chain_calculus",
            "finding": "The historical 169 chains collapse to one distinct state; the representative-pair calculus audit is the informative evidence.",
        },
        {
            "paper": "P9",
            "severity": "CANNOT_CHECK",
            "kind": "missing_gold",
            "source_id": "p9_diagnostic",
            "finding": "The digits accessibility task has protected_gold=CANNOT_CHECK; it must not be scored as correct or incorrect.",
        },
        {
            "paper": "P10",
            "severity": "CANNOT_CHECK",
            "kind": "not_executed",
            "source_id": "p10_prospective",
            "finding": "H1-H6 is prospective and outcome-blind; the full frozen donor/evaluator inputs are absent.",
        },
        {
            "paper": "P11",
            "severity": "FAIL",
            "kind": "gate_not_met",
            "source_id": "p11_query_phase",
            "finding": "Support counts are LINEAR 3/10, RBF 5/10 and KNN 5/10; the primary terminal is GATE_NOT_MET.",
        },
        {
            "paper": "P12",
            "severity": "CANNOT_CHECK",
            "kind": "forward_time_boundary",
            "source_id": "p12_signal_complementarity",
            "finding": "The bounded equal-action result does not discharge the protected forward-time/non-flat successor claim.",
        },
        {
            "paper": "P13",
            "severity": "ADVERSE",
            "kind": "historical_negative_retained",
            "source_id": "p13_composed_safety",
            "finding": "The composed finite-world positive result does not erase the earlier controlled-sufficiency-debt negative boundary.",
        },
        {
            "paper": "P14",
            "severity": "NOT_AUTHORITY",
            "kind": "authored_panel",
            "source_id": "p14_governance",
            "finding": "The 28-case P14C panel is internally authored; external pilot analytics explicitly remain NOT_AUTHORITY.",
        },
        {
            "paper": "P15",
            "severity": "MIXED",
            "kind": "honest_non_authorization",
            "source_id": "p15_workflows",
            "finding": "Three workflow receipts authorize bounded science; the native-Lean workflow remains CANNOT_CHECK because the scientific contract is absent.",
        },
    ]
    for index, row in enumerate(rows, start=1):
        row["paper_id"] = row["paper"]
        row["anomaly_id"] = f"A{index:02d}-{row['paper']}"
        row["status"] = row["severity"]
        row["summary"] = row["finding"]
        row["explanation"] = row["finding"]
    return rows


def flat_metric_records(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    """Project nested paper payloads into unit-preserving numeric rows.

    This is a presentation index only.  It never pools rows or computes a
    cross-paper score; each record keeps its paper, source, exact metric and
    within-source case/arm identifier.
    """

    source_by_paper = {
        "P1": "p1_primary",
        "P2": "p2_trec_covid",
        "P3": "p3_confirmatory",
        "P4": "p4_protected",
        "P5": "p5_attribution",
        "P6": "p6_certificate_lifting",
        "P7": "p7_closure_carrying",
        "P8": "p8_chain_calculus",
        "P9": "p9_diagnostic",
        "P10": "p10_prospective",
        "P11": "p11_query_phase",
        "P12": "p12_signal_complementarity",
        "P13": "p13_composed_safety",
        "P14": "p14_governance",
        "P15": "p15_workflows",
    }
    records: list[dict[str, Any]] = []

    def add(paper: str, metric: str, value: Any, unit: str, *, status: str, **labels: Any) -> None:
        if isinstance(value, bool) or value is None:
            return
        number = finite(value, f"{paper}.{metric}")
        records.append(
            {
                "paper": paper,
                "paper_id": paper,
                "metric": metric,
                "name": labels.get("name", labels.get("arm", labels.get("case_id", metric))),
                "value": number,
                "unit": unit,
                "status": status,
                "source_id": source_by_paper[paper],
                **labels,
            }
        )

    for row in metrics["P1"]["arms"]:
        for metric in (
            "protected_root_task_success_rate",
            "hidden_shift_protected_root_task_success_rate",
            "mean_dependency_reopen_f1",
            "mean_spent_budget",
            "negative_control_unnecessary_high_level_reframe_rate",
        ):
            add(
                "P1",
                metric,
                row[metric],
                "rate" if "rate" in metric or "f1" in metric else "budget units",
                status="BOUNDED_PASS",
                arm=row["arm"],
            )
    for row in metrics["P2"]["arms"]:
        for metric, unit in (
            ("recall_at_100", "rate"),
            ("ndcg_at_10", "rate"),
            ("mean_reads", "reads"),
            ("mean_route_calls", "calls"),
        ):
            add("P2", metric, row[metric], unit, status="FAIL", arm=row["arm"])
    for row in metrics["P3"]["systems"]:
        add("P3", row["metric"], row["rate"], "rate", status="BOUNDED_PASS", arm=row["system"])
    for row in metrics["P4"]["arms"]:
        add("P4", "accuracy", row["accuracy"], "rate", status="BOUNDED_PASS", arm=row["arm"])
        add(
            "P4",
            "false_promotions",
            row["false_promotions"],
            "cases",
            status="BOUNDED_PASS",
            arm=row["arm"],
        )
    for row in metrics["P5"]["arms"]:
        add("P5", "accuracy", row["accuracy"], "rate", status="ADVERSE", arm=row["arm"])
        add("P5", "macro_f1", row["macro_f1"], "rate", status="ADVERSE", arm=row["arm"])
    for paper in ("P6", "P7"):
        state = "BOUNDED_PASS" if paper == "P6" else "FAIL"
        for metric, value in metrics[paper]["counts"].items():
            add(paper, metric, value, "finite evaluations", status=state, case_id=metric)
        add(
            paper,
            "distinct_state_evaluations",
            metrics[paper]["distinct_state_evaluations"],
            "distinct states",
            status=state,
        )
    add(
        "P8",
        "representative_pairs_checked",
        metrics["P8"]["representative_pairs_checked"],
        "pairs",
        status="BOUNDED_PASS",
    )
    add("P8", "unsound_pairs", metrics["P8"]["unsound_pairs"], "pairs", status="BOUNDED_PASS")
    add(
        "P8",
        "historical_distinct_states",
        metrics["P8"]["historical_distinct_states"],
        "distinct states",
        status="BOUNDARY",
    )
    for row in metrics["P9"]["rows"]:
        add(
            "P9",
            "predicted_protected_quality",
            row["predicted_protected_quality"],
            "rate",
            status="CANNOT_CHECK" if row["protected_gold"] == "CANNOT_CHECK" else "BOUNDED_PASS",
            case_id=row["task"],
            name=row["domain"],
        )
    for key, value in metrics["P10"]["design"].items():
        add("P10", key, value, "planned cases", status="CANNOT_CHECK", case_id=key)
    for row in metrics["P11"]["queries"]:
        add(
            "P11",
            "compiled_minus_universal_delta",
            row["delta"],
            "balanced-accuracy difference",
            status="BOUNDED_PASS" if row["quality_supported"] else "FAIL",
            case_id=row["query"],
            name=row["family"],
        )
    for row in metrics["P12"]["families"]:
        add(
            "P12",
            "delta_vs_stronger_one_signal",
            row["delta_vs_stronger_one_signal"],
            "allocation-rate difference",
            status="BOUNDED_PASS",
            case_id=row["family_rng_block"],
            name=f"sigma={row['sigma']}",
        )
    for row in metrics["P13"]["arms"]:
        for metric, unit in (
            ("verified_correct_rate", "rate"),
            ("unsafe_reuse_rate", "rate"),
            ("unnecessary_reopen_rate", "rate"),
            ("mean_cost", "cost units"),
        ):
            add("P13", metric, row[metric], unit, status="BOUNDED_PASS", arm=row["arm"])
    for row in metrics["P14"]["arms"]:
        for metric, value in row.items():
            if metric != "arm":
                add("P14", metric, value, "rate", status="BOUNDED_PASS", arm=row["arm"])
    add(
        "P15",
        "authorized_workflows",
        metrics["P15"]["authorized_count"],
        "workflows",
        status="BOUNDED_PASS",
    )
    add(
        "P15",
        "cannot_check_workflows",
        metrics["P15"]["cannot_check_count"],
        "workflows",
        status="CANNOT_CHECK",
    )
    return records


def build_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    metrics: dict[str, Any] = {}

    p1 = payload["p1_primary"]
    metrics["P1"] = {
        "arms": [
            {
                "arm": arm,
                **{
                    key: finite(values[key], f"P1.{arm}.{key}")
                    for key in (
                        "protected_root_task_success_rate",
                        "hidden_shift_protected_root_task_success_rate",
                        "mean_dependency_reopen_f1",
                        "mean_spent_budget",
                        "negative_control_unnecessary_high_level_reframe_rate",
                        "protected_sibling_regression_rate",
                        "forbidden_high_level_mutation_rate",
                    )
                },
            }
            for arm, values in sorted(p1["arm_summary"].items())
        ],
        "hidden_shift_intervals": [
            {
                "parent": row["parent"],
                "difference": finite(row["difference"], "P1 difference"),
                "ci95_low": finite(row["ci95_low"], "P1 ci low"),
                "ci95_high": finite(row["ci95_high"], "P1 ci high"),
                "n": int(row["n"]),
            }
            for row in p1["analysis"]["h1_hidden_shift"]
        ],
        "gates": p1["analysis"]["gates"],
    }

    p2 = payload["p2_trec_covid"]
    if len(p2["per_topic"]) != 50:
        raise ValueError("P2 expected 50 topics")
    metrics["P2"] = {
        "arms": [{"arm": arm, **values} for arm, values in sorted(p2["arms_macro"].items())],
        "gate": p2["pass_gate_verdict"],
        "topic_count": len(p2["per_topic"]),
    }

    p3 = payload["p3_confirmatory"]
    if int(p3["case_count"]) != 32:
        raise ValueError("P3 expected 32 deterministic cases")
    p3_rows = []
    for system, values in sorted(p3["pooled"]["systems"].items()):
        for metric, estimate in sorted(values.items()):
            p3_rows.append({"system": system, "metric": metric, **estimate})
    metrics["P3"] = {
        "systems": p3_rows,
        "primary_comparisons": p3["pooled"]["primary_comparisons"],
        "case_count": 32,
    }

    p4 = payload["p4_protected"]
    if int(p4["case_count"]) != 400:
        raise ValueError("P4 expected 400 cases")
    metrics["P4"] = {
        "arms": [
            {
                "arm": arm,
                "accuracy": finite(value, f"P4 {arm}"),
                "false_promotions": int(p4["false_promotions"][arm]),
            }
            for arm, value in sorted(p4["accuracy"].items())
        ],
        "p4x_minus_b1": p4["p4x_minus_b1"],
        "bootstrap_95_ci": p4["bootstrap_95_ci"],
        "claim_ceiling": p4["claim_ceiling"],
    }

    p5 = payload["p5_attribution"]
    metrics["P5"] = {
        "requested_model": p5["requested_model"],
        "arms": [
            {
                "arm": arm,
                "n": int(values["n"]),
                "accuracy": finite(values["accuracy"], f"P5 {arm} accuracy"),
                "macro_f1": finite(values["standard_macro_f1"], f"P5 {arm} F1"),
                "served_models": values["served_models"],
            }
            for arm, values in sorted(p5["arms"].items())
        ],
    }

    p6 = payload["p6_certificate_lifting"]
    p7 = payload["p7_closure_carrying"]
    metrics["P6"] = {
        "coordinates": p6["science_coordinates"],
        "state_evaluations": p6["state_evaluations"],
        "distinct_state_evaluations": p6["donor_axis"]["distinct_state_evaluations"],
        "counts": {
            "full_success": p6["full_revalidation_successes"],
            "partial_failure": p6["partial_revalidation_failures"],
            "countermodels": p6["certificate_product_countermodels"],
            "separation_witnesses": p6["single_coordinate_separation_witnesses"],
        },
        "donor_axis": p6["donor_axis"],
        "terminal": p6["terminal"],
    }
    metrics["P7"] = {
        "coordinates": p7["closure_coordinates"],
        "state_evaluations": p7["state_evaluations"],
        "distinct_state_evaluations": p7["donor_axis"]["distinct_state_evaluations"],
        "counts": {
            "full_success": p7["full_closure_refinement_successes"],
            "partial_failure": p7["partial_closure_refinement_failures"],
            "countermodels": p7["donor_product_nonclosure_countermodels"],
            "separation_witnesses": p7["single_coordinate_separation_witnesses"],
        },
        "donor_axis": p7["donor_axis"],
        "terminal": p7["terminal"],
        "programme_execution_state": "INVALID_EXECUTION_RETAINED",
        "planned_cases": 738,
        "observed_cases": 736,
    }

    p8 = payload["p8_chain_calculus"]
    metrics["P8"] = {
        "chain_ladder": [
            {"length": index + 1, "outcome": row["outcome"], "name": row["name"]}
            for index, row in enumerate(p8["chain_ladder"]["results"])
        ],
        "chain_bound": p8["chain_ladder"]["bound"],
        "representative_pairs_checked": p8["composition_soundness"]["representative_pairs_checked"],
        "unsound_pairs": p8["composition_soundness"]["unsound_pairs"],
        "historical_chain_count": 169,
        "historical_distinct_states": 1,
    }

    p9 = payload["p9_diagnostic"]
    if len(p9["rows"]) != 5:
        raise ValueError("P9 expected five diagnostic tasks")
    metrics["P9"] = {
        "rows": p9["rows"],
        "diagnosis_scored_correct": sum(
            bool(row["diagnosis_correct"])
            for row in p9["rows"]
            if row["protected_gold"] != "CANNOT_CHECK"
        ),
        "scored_rows": sum(row["protected_gold"] != "CANNOT_CHECK" for row in p9["rows"]),
        "cannot_check_rows": sum(row["protected_gold"] == "CANNOT_CHECK" for row in p9["rows"]),
        "generic_correct": sum(bool(row["generic_correct"]) for row in p9["rows"]),
        "generic_false_compute_escalations": sum(
            bool(row["generic_false_compute_escalation"]) for row in p9["rows"]
        ),
    }

    p10 = payload["p10_prospective"]
    metrics["P10"] = {
        "design": p10["design"],
        "checks": p10["checks"],
        "all_checks_pass": p10["all_checks_pass"],
        "outcome_accessed": p10["outcome_accessed"],
        "state": "PROSPECTIVE_NOT_EXECUTED",
    }

    p11 = payload["p11_query_phase"]
    if len(p11["query_results"]) != 30:
        raise ValueError("P11 expected 30 query results")
    metrics["P11"] = {
        "queries": [
            {"query": key, "family": key.split(":", 1)[0], **values}
            for key, values in sorted(p11["query_results"].items())
        ],
        "support_counts": p11["support_counts"],
        "terminal": p11["terminal"],
        "row_count": p11["row_count"],
    }

    p12 = payload["p12_signal_complementarity"]
    if len(p12["core"]["families"]) != 32:
        raise ValueError("P12 expected 32 independent family blocks")
    metrics["P12"] = {
        "families": p12["core"]["families"],
        "summary": p12["summary"],
        "terminal": p12["terminal"],
        "forward_time_state": "CANNOT_CHECK",
    }

    p13 = payload["p13_composed_safety"]
    metrics["P13"] = {
        "arms": [{"arm": arm, **values} for arm, values in sorted(p13["summary"]["arms"].items())],
        "worlds": [
            {"world": world, **values}
            for world, values in sorted(p13["summary"]["unverified_by_world"].items())
        ],
        "terminal": p13["terminal"],
        "authority_boundary": p13["core"]["authority_boundary"],
    }

    p14 = payload["p14_governance"]
    if int(p14["case_count"]) != 28:
        raise ValueError("P14 expected 28 internally authored cases")
    metrics["P14"] = {
        "arms": [{"arm": arm, **values} for arm, values in sorted(p14["summary"].items())],
        "ablations": [
            {"ablation": arm, **values} for arm, values in sorted(p14["ablations"].items())
        ],
        "case_count": 28,
        "claim_authority": p14["claim_authority"],
    }

    p15 = payload["p15_workflows"]
    if len(p15["receipts"]) != 4:
        raise ValueError("P15 expected four workflow receipts")
    lifecycle_fields = [
        "spawn_ok",
        "host_ok",
        "exit_zero",
        "output_complete",
        "reaped",
        "cleanup_complete",
        "invocation_match",
        "input_digest_match",
        "result_digest_match",
        "fresh",
        "coverage_complete",
        "replay_match",
        "scientific_contract_valid",
        "claim_authority",
    ]
    metrics["P15"] = {
        "workflows": [
            {
                "id": row["id"],
                "expected_disposition": row["expected_disposition"],
                **{field: bool(row[field]) for field in lifecycle_fields},
            }
            for row in p15["receipts"]
        ],
        "authorized_count": sum(
            row["expected_disposition"] == "AUTHORIZED_SCIENCE" for row in p15["receipts"]
        ),
        "cannot_check_count": sum(
            row["expected_disposition"] == "CANNOT_CHECK" for row in p15["receipts"]
        ),
    }

    return metrics


def framework() -> dict[str, Any]:
    groups = {
        "P1": "state",
        "P2": "discovery",
        "P3": "portrait",
        "P4": "authority",
        "P5": "self-revision",
        "P6": "certificate",
        "P7": "closure",
        "P8": "authority calculus",
        "P9": "structured learning",
        "P10": "problem solving",
        "P11": "state computation",
        "P12": "adaptive reasoning",
        "P13": "responsibility state",
        "P14": "governance",
        "P15": "research harness",
    }
    edges = [
        ("P1", "P2", "state informs search"),
        ("P2", "P3", "sources become portraits"),
        ("P3", "P4", "portraits enter authority"),
        ("P4", "P5", "authority constrains revision"),
        ("P4", "P6", "authority certificates"),
        ("P6", "P7", "certificates carry closure"),
        ("P7", "P8", "closure composes authority"),
        ("P8", "P9", "authority bounds learning"),
        ("P9", "P10", "diagnosis guides search"),
        ("P1", "P11", "state as a resource"),
        ("P11", "P12", "resource-aware adaptation"),
        ("P12", "P13", "actions carry responsibility"),
        ("P13", "P14", "responsibility enters governance"),
        ("P8", "P15", "receipts carry authority"),
        ("P14", "P15", "governance executes in harness"),
    ]
    return {
        "nodes": [{"paper": paper, "role": role} for paper, role in groups.items()],
        "edges": [
            {
                "source": source,
                "target": target,
                "label": label,
                "semantics": "conceptual_dependency_not_causal_effect",
            }
            for source, target, label in edges
        ],
    }


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def build(root: Path, atlas_path: Path, manifest_path: Path) -> None:
    catalog = read_json(root / "visualization/source_catalog.json")
    sources, payloads = source_manifest(root, catalog)
    ledger = payloads["portfolio_claim_ledger"]
    metrics = build_metrics(payloads)
    atlas = {
        "schema": SCHEMA,
        "authority_boundary": AUTHORITY_BOUNDARY,
        "subject_commit": git_value(root, "rev-parse", "HEAD"),
        "paper_states": normalize_paper_states(ledger),
        "gate_states": gate_states(),
        "framework": framework(),
        "metrics": metrics,
        "metric_records": flat_metric_records(metrics),
        "anomalies": anomalies(),
        "sources": sources,
        "notes": [
            "Incompatible units are not pooled across papers.",
            "Finite witnesses, hashes, tests, and same-owner replay are not external authority.",
            "Interactive outputs are presentation-only and inherit this claim ceiling.",
        ],
    }
    manifest = {
        "schema": "orion.visualization.source-manifest.v1",
        "authority_boundary": AUTHORITY_BOUNDARY,
        "subject_commit": git_value(root, "rev-parse", "HEAD"),
        "subject_tree": git_value(root, "rev-parse", "HEAD^{tree}"),
        "source_catalog_sha256": sha256(root / "visualization/source_catalog.json"),
        "source_count": len(sources),
        "sources": sources,
    }
    atomic_json(atlas_path, atlas)
    atomic_json(manifest_path, manifest)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=repo_root())
    parser.add_argument("--atlas", type=Path)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    atlas = args.atlas or root / "visualization/data/derived/atlas.json"
    manifest = args.manifest or root / "visualization/data/manifests/source_manifest.json"
    build(root, atlas, manifest)
    print(f"WROTE {atlas}")
    print(f"WROTE {manifest}")
    print(f"SCIENTIFIC_AUTHORITY={AUTHORITY_BOUNDARY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
