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
import re
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
        declared = entry["schema"]
        observed = detected_schema(payload)
        if (
            entry["transform_id"] == "des-coverage-v1"
            and observed is not None
            and observed != declared
        ):
            raise ValueError(
                f"{entry['id']} declared schema mismatch: "
                f"catalog={declared!r}, source={observed!r}"
            )
        records.append(
            {
                "id": entry["id"],
                "paper": entry["paper"],
                "path": entry["path"],
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
                "declared_schema": declared,
                "detected_schema": observed,
                "role": entry["role"],
                "authority_tier": entry["authority_tier"],
                "transform_id": entry["transform_id"],
                "fields": entry["fields"],
            }
        )
    return records, payloads


def evidence_snapshot(root: Path, sources: list[dict[str, Any]]) -> dict[str, Any]:
    """Return a stable evidence identity derived only from registered source bytes.

    A commit or tree identifier would be self-referential when embedded in a
    committed generated file.  The source-set digest instead binds the exact
    scientific inputs without depending on the generated output's future Git
    identity or on the local Python environment.
    """

    identity_keys = ("bytes", "declared_schema", "id", "path", "sha256")
    identity = [{key: source[key] for key in identity_keys} for source in sources]
    canonical = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "schema": "orion.visualization.evidence-source-set.v1",
        "source_catalog_sha256": sha256(root / "visualization/source_catalog.json"),
        "source_count": len(sources),
        "source_set_sha256": hashlib.sha256(canonical).hexdigest(),
    }


def planned_observed_from_ledger(ledger: dict[str, Any], paper: str) -> tuple[int, int]:
    item = next(row for row in ledger["papers"] if row["paper"] == paper)
    text = " ".join(str(value) for value in item.get("allowed", []))
    match = re.search(r"planned\s+(\d+)\s+versus\s+observed\s+(\d+)", text, re.IGNORECASE)
    if not match:
        raise ValueError(f"{paper} ledger lacks exact planned/observed denominator")
    return int(match.group(1)), int(match.group(2))


def historical_chain_counts(text: str) -> tuple[int, int]:
    match = re.search(r"all\s+(\d+)\s+ordered pairs compose to\s+(\d+)\s+distinct state", text)
    if not match:
        raise ValueError("P8 receipt lacks exact historical chain/distinct-state counts")
    return int(match.group(1)), int(match.group(2))


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


def gate_states(metrics: dict[str, Any]) -> list[dict[str, str]]:
    p7 = metrics["P7"]
    p9 = metrics["P9"]
    p12 = metrics["P12"]
    p15 = metrics["P15"]
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
        "P7": (
            "FAIL",
            f"programme execution invalidated by {p7['planned_cases']}/{p7['observed_cases']} planned/observed denominator drift",
        ),
        "P8": ("BOUNDED_PASS", "mechanized calculus and representative-pair internal audit"),
        "P9": (
            "CANNOT_CHECK",
            f"{p9['cannot_check_rows']} protected-gold cell is CANNOT_CHECK; the append-only replay failure terminal remains recorded",
        ),
        "P10": ("CANNOT_CHECK", "prospective H1-H6 outcome was not executed"),
        "P11": ("FAIL", "query-family primary terminal is GATE_NOT_MET"),
        "P12": (
            "BOUNDED_PASS",
            f"equal-action complementarity is bounded; forward-time deployability is {p12['forward_time_state']}",
        ),
        "P13": ("BOUNDED_PASS", "registered randomized finite-world comparison"),
        "P14": ("BOUNDED_PASS", "28 internally authored governance-contract cases"),
        "P15": (
            "MIXED",
            f"{p15['authorized_count']} receipt-level AUTHORIZED_SCIENCE dispositions and {p15['cannot_check_count']} CANNOT_CHECK",
        ),
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


def anomalies(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    p2_gate = metrics["P2"]["gate"]
    p3_false_split = metrics["P3"]["primary_comparisons"]["false_split_orion_minus_exact"]
    p4 = metrics["P4"]
    p5 = metrics["P5"]
    p6 = metrics["P6"]
    p7 = metrics["P7"]
    p8 = metrics["P8"]
    p9 = metrics["P9"]
    p10 = metrics["P10"]
    p11 = metrics["P11"]
    p12 = metrics["P12"]
    p13 = metrics["P13"]
    p14 = metrics["P14"]
    p15 = metrics["P15"]

    p4x = next(row for row in p4["arms"] if row["arm"] == "P4_X")
    p4_ideal = next(row for row in p4["arms"] if row["arm"] == "B3_IDEAL_TYPED_PRODUCT")
    p5_served = sorted({model for row in p5["arms"] for model in row["served_models"]})
    p9_cannot_check = next(row for row in p9["rows"] if row["protected_gold"] == "CANNOT_CHECK")
    p13_negative = p13["historical_negative"]
    p14_external = p14["external_pilot"]
    p15_compromise = p15["full_key_compromise"]
    rows = [
        {
            "paper": "P2",
            "severity": "FAIL",
            "kind": "frozen_gate",
            "source_id": "p2_trec_covid",
            "source_ids": ["p2_trec_covid"],
            "finding": (
                f"Overall gate is {p2_gate['overall']} although nDCG@10 improves: recall noninferiority CI lower bound "
                f"{p2_gate['criteria']['recall_noninferiority']['bootstrap_ci95'][0]:.5f} crosses the "
                f"{p2_gate['criteria']['recall_noninferiority']['margin']:.2f} margin and reads rise "
                f"{p2_gate['criteria']['cost_reduction']['reads_vs_comparator_pct']:.1f}%."
            ),
        },
        {
            "paper": "P3",
            "severity": "NULL",
            "kind": "zero_delta",
            "source_id": "p3_confirmatory",
            "source_ids": ["p3_confirmatory"],
            "finding": (
                f"The false-split comparison is exactly {p3_false_split['candidate_minus_baseline']:g} on "
                f"{int(p3_false_split['n'])} deterministic cases; a zero delta is not a necessity proof."
            ),
        },
        {
            "paper": "P4",
            "severity": "BOUNDARY",
            "kind": "ideal_tie",
            "source_id": "p4_protected",
            "source_ids": ["p4_protected"],
            "finding": (
                f"P4-X ties the ideal typed product at {int(p4x['accuracy'] * p4['case_count'])}/"
                f"{p4['case_count']} versus {int(p4_ideal['accuracy'] * p4['case_count'])}/"
                f"{p4['case_count']}; this locates a factorization boundary rather than superiority over the ideal."
            ),
        },
        {
            "paper": "P5",
            "severity": "ADVERSE",
            "kind": "execution_identity_drift",
            "source_id": "p5_attribution",
            "source_ids": ["p5_attribution"],
            "finding": f"The requested model was {p5['requested_model']} but the arms report served model(s) {', '.join(p5_served)}.",
        },
        {
            "paper": "P6",
            "severity": "BOUNDARY",
            "kind": "replication_multiplier",
            "source_id": "p6_certificate_lifting",
            "source_ids": ["p6_certificate_lifting"],
            "finding": (
                f"The {p6['state_evaluations']} evaluations include a donor multiplier of "
                f"{p6['donor_axis']['multiplier']}; read_by_liftable={str(p6['donor_axis']['read_by_liftable']).lower()}."
            ),
        },
        {
            "paper": "P7",
            "severity": "FAIL",
            "kind": "denominator_drift",
            "source_id": "portfolio_claim_ledger",
            "source_ids": ["portfolio_claim_ledger"],
            "finding": (
                f"The programme preserves an invalid run with {p7['planned_cases']} planned versus "
                f"{p7['observed_cases']} observed cases; it supports no empirical transport claim."
            ),
        },
        {
            "paper": "P8",
            "severity": "BOUNDARY",
            "kind": "state_multiplicity",
            "source_id": "p8_chain_calculus",
            "source_ids": ["p8_chain_calculus"],
            "finding": (
                f"The historical {p8['historical_chain_count']} chains collapse to "
                f"{p8['historical_distinct_states']} distinct state; the representative-pair calculus audit is the informative evidence."
            ),
        },
        {
            "paper": "P9",
            "severity": "CANNOT_CHECK",
            "kind": "missing_gold",
            "source_id": "p9_diagnostic",
            "source_ids": ["p9_diagnostic", "p9_replay_revival"],
            "finding": (
                f"The {p9_cannot_check['domain']} {p9_cannot_check['task']} task has protected_gold=CANNOT_CHECK. "
                f"A separate revival receipt retains {p9['replay_boundary']['failure_terminal']} while recording "
                "archive-matched replay consistency restoration; neither fact authorizes the frozen scientific successor."
            ),
        },
        {
            "paper": "P10",
            "severity": "CANNOT_CHECK",
            "kind": "not_executed",
            "source_id": "p10_prospective",
            "source_ids": ["p10_prospective"],
            "finding": (
                f"H1-H6 is prospective with minimum_total_tasks={p10['design']['minimum_total_tasks']} and "
                f"outcome_accessed={str(p10['outcome_accessed']).lower()}; no prospective result exists."
            ),
        },
        {
            "paper": "P11",
            "severity": "FAIL",
            "kind": "gate_not_met",
            "source_id": "p11_query_phase",
            "source_ids": ["p11_query_phase"],
            "finding": (
                f"Support counts are LINEAR {p11['support_counts']['LINEAR']}/10, RBF "
                f"{p11['support_counts']['RBF']}/10 and KNN {p11['support_counts']['KNN']}/10; "
                f"the primary terminal is {p11['terminal']}."
            ),
        },
        {
            "paper": "P12",
            "severity": "CANNOT_CHECK",
            "kind": "forward_time_boundary",
            "source_id": "p12_signal_complementarity",
            "source_ids": ["p12_signal_complementarity", "p12_active_authority"],
            "finding": (
                f"The {len(p12['families'])}-family equal-action result is bounded; active authority records "
                f"forward_time_deployability={p12['forward_time_state']} and "
                f"public-data campaign_executed={str(p12['public_data_campaign_executed']).lower()}."
            ),
        },
        {
            "paper": "P13",
            "severity": "ADVERSE",
            "kind": "historical_negative_retained",
            "source_id": "p13_composed_safety",
            "source_ids": ["p13_composed_safety", "p13_historical_boundary"],
            "finding": (
                f"The {len(p13['arms'])}-arm/{len(p13['worlds'])}-world composed result does not erase the "
                f"P13A receipt's retained terminal {p13_negative['terminal']}: observed max deviation "
                f"{p13_negative['observed_max_deviation']:.8f} exceeds its {p13_negative['registered_threshold']:.2f} threshold."
            ),
        },
        {
            "paper": "P14",
            "severity": "NOT_AUTHORITY",
            "kind": "authored_panel",
            "source_id": "p14_governance",
            "source_ids": ["p14_governance", "p14_external_pilot"],
            "finding": (
                f"The {p14['case_count']}-case P14C panel is internally authored; the separate "
                f"{p14_external['packets']}-packet pilot analytics remain {p14_external['authority_status']} "
                f"because {p14_external['reason']}"
            ),
        },
        {
            "paper": "P15",
            "severity": "MIXED",
            "kind": "honest_non_authorization",
            "source_id": "p15_workflows",
            "source_ids": ["p15_workflows", "p15_active_authority"],
            "finding": (
                f"Workflow receipts contain {p15['authorized_count']} AUTHORIZED_SCIENCE dispositions and "
                f"{p15['cannot_check_count']} CANNOT_CHECK. Separately, full key compromise records "
                f"{p15_compromise['signature_detections']} signature-layer detections and "
                f"{p15_compromise['false_promotions']} false promotions."
            ),
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
        "case_count": int(p4["case_count"]),
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

    ledger = payload["portfolio_claim_ledger"]
    p6 = payload["p6_certificate_lifting"]
    p7 = payload["p7_closure_carrying"]
    p7_planned, p7_observed = planned_observed_from_ledger(ledger, "P7")
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
        "planned_cases": p7_planned,
        "observed_cases": p7_observed,
    }

    p8 = payload["p8_chain_calculus"]
    p8_chain_count, p8_distinct_states = historical_chain_counts(p8["what_the_169_costs"])
    metrics["P8"] = {
        "chain_ladder": [
            {"length": index + 1, "outcome": row["outcome"], "name": row["name"]}
            for index, row in enumerate(p8["chain_ladder"]["results"])
        ],
        "chain_bound": p8["chain_ladder"]["bound"],
        "representative_pairs_checked": p8["composition_soundness"]["representative_pairs_checked"],
        "unsound_pairs": p8["composition_soundness"]["unsound_pairs"],
        "historical_chain_count": p8_chain_count,
        "historical_distinct_states": p8_distinct_states,
    }

    p9 = payload["p9_diagnostic"]
    p9_replay = payload["p9_replay_revival"]
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
        "replay_boundary": {
            "negative": p9_replay["NR-06"]["negative"],
            "archived_accuracy": finite(
                p9_replay["NR-06"]["retest"]["agreement"]["typed_serialized_bag_accuracy"],
                "P9 archived replay accuracy",
            ),
            "locked_reproduction_accuracy": finite(
                re.search(r"locked reproduction\s+([0-9.]+)", p9_replay["NR-06"]["negative"])[1],
                "P9 locked reproduction accuracy",
            ),
            "archive_matched_all_configs": bool(
                p9_replay["NR-06"]["retest"]["agreement"]["all_selected_configs_match"]
            ),
            "failure_terminal": p9_replay["NR-06"]["replay_failure_terminal"],
            "boundary": p9_replay["NR-06"]["boundary"],
            "lane_verdict": p9_replay["lane_verdicts"]["NR-06"],
        },
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
    p12_authority = payload["p12_active_authority"]
    if len(p12["core"]["families"]) != 32:
        raise ValueError("P12 expected 32 independent family blocks")
    metrics["P12"] = {
        "families": p12["core"]["families"],
        "summary": p12["summary"],
        "terminal": p12["terminal"],
        "forward_time_state": p12_authority["price_aware_successor_leaf"][
            "forward_time_deployability"
        ],
        "public_data_campaign_executed": bool(
            p12_authority["stopgo_campaign_leaf"]["campaign_executed"]
        ),
        "external_public_benchmark_status": p12_authority["external_public_benchmark_status"],
    }

    p13 = payload["p13_composed_safety"]
    p13_historical = payload["p13_historical_boundary"]
    metrics["P13"] = {
        "arms": [{"arm": arm, **values} for arm, values in sorted(p13["summary"]["arms"].items())],
        "worlds": [
            {"world": world, **values}
            for world, values in sorted(p13["summary"]["unverified_by_world"].items())
        ],
        "terminal": p13["terminal"],
        "authority_boundary": p13["core"]["authority_boundary"],
        "historical_negative": p13_historical["historical_negative_retained"],
    }

    p14 = payload["p14_governance"]
    p14_external = payload["p14_external_pilot"]
    if int(p14["case_count"]) != 28:
        raise ValueError("P14 expected 28 internally authored cases")
    metrics["P14"] = {
        "arms": [{"arm": arm, **values} for arm, values in sorted(p14["summary"].items())],
        "ablations": [
            {"ablation": arm, **values} for arm, values in sorted(p14["ablations"].items())
        ],
        "case_count": 28,
        "claim_authority": p14["claim_authority"],
        "external_pilot": {
            "authority_status": p14_external["authority_status_all"],
            "promotion_status": p14_external["co_primary_promotion_condition"]["status"],
            "reason": p14_external["co_primary_promotion_condition"]["reason"],
            "packets": int(p14_external["suite"]["packets"]),
        },
    }

    p15 = payload["p15_workflows"]
    p15_authority = payload["p15_active_authority"]
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
        "full_key_compromise": {
            "signature_detections": int(
                p15_authority["bounded_findings"]["full_key_compromise_signature_detections"]
            ),
            "false_promotions": int(
                p15_authority["bounded_findings"]["full_key_compromise_false_promotions"]
            ),
            "boundary": p15_authority["full_key_compromise_boundary"],
            "promotion_allowed": bool(p15_authority["promotion_allowed"]),
        },
    }

    return metrics


def exact_count(value: Any, label: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{label} is a boolean, not a count")
    number = finite(value, label)
    if number < 0 or not number.is_integer():
        raise ValueError(f"{label} is not a non-negative integer count")
    return int(number)


def nested(payload: dict[str, Any], path: str) -> Any:
    value: Any = payload
    for part in path.split("."):
        if part == "length":
            if not isinstance(value, list):
                raise ValueError(f"{path} requests length of a non-list")
            value = len(value)
        else:
            if not isinstance(value, dict) or part not in value:
                raise KeyError(f"missing registered field {path}")
            value = value[part]
    return value


def normalize_des_execution(payloads: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize the frozen #1332 execution packets without pooling estimands.

    Planned, observed, and valid are coverage counts within each paper's own
    registered unit.  They are not performance scores, and their absolute
    magnitudes are never compared across papers.
    """

    mapping = {
        "P1": ("denominators.planned_run_cell_denominator", "denominators.run_cells_executed", "denominators.run_cells_executed", "run cells", "CANNOT_CHECK"),
        "P2": ("denominators.case_policy_rows_expected", "denominators.case_policy_rows_retained", "denominators.case_policy_rows_retained", "topic-policy rows", "BOUNDED_PUBLIC_EXECUTION"),
        "P3": ("scheduled_cell_denominator", "executed_cell_denominator", "executed_cell_denominator", "evaluation cells", "CANNOT_CHECK"),
        "P4": ("arm_case_denominator", "mechanically_executed_arm_cases", "externally_terminal_scored_cases", "arm-cases", "CANNOT_CHECK_EXTERNAL_SCORE"),
        "P5": ("denominators.planned_run_cell_denominator", "denominators.run_cells_executed", "denominators.run_cells_executed", "run cells", "CANNOT_CHECK"),
        "P6": ("denominators.primary_case_denominator", "case_outcomes.length", "case_outcomes.length", "transition cases", "BOUNDED_INTERNAL_VALID"),
        "P7": ("planned_case_denominator", "observed_generated_case_denominator", "valid_case_denominator", "generated cases", "INVALID"),
        "P8": ("case_denominator", "executed_case_denominator", "executed_case_denominator", "replay cases", "BOUNDED_INTERNAL_REPLAY"),
        "P9": ("denominators.planned_cell_denominator", "denominators.cells_executed", "denominators.cells_executed", "execution cells", "CANNOT_CHECK"),
        "P10": ("denominators.planned_run_cell_denominator", "denominators.run_cells_executed", "denominators.run_cells_executed", "run cells", "CANNOT_CHECK"),
        "P11": ("acquisition_requirement_denominator", "resource_vector.acquisition_requirements_checked", "bound_requirements", "acquisition requirements", "CANNOT_CHECK"),
        "P12": ("denominators.clean_license_cases_planned", "denominators.clean_license_cases_executed", "denominators.clean_license_cases_executed", "clean-license cases", "CANNOT_CHECK"),
        "P13": ("denominators.planner_cell_denominator", "denominators.executed_planner_cell_denominator", "denominators.executed_planner_cell_denominator", "planner cells", "BOUNDED_PARTIAL_INTERNAL"),
        "P14": ("acquisition_artifact_denominator", "resource_vector.acquisition_artifacts_checked", "present_artifacts", "acquisition artifacts", "CANNOT_CHECK"),
        "P15": ("denominators.planned_run_cell_denominator", "denominators.run_cells_executed", "denominators.run_cells_executed", "run cells", "CANNOT_CHECK"),
    }
    rows: list[dict[str, Any]] = []
    for index in range(1, 16):
        paper = f"P{index}"
        source_id = f"p{index}_des_packet"
        payload = payloads[source_id]
        planned_path, observed_path, valid_path, unit, status = mapping[paper]
        planned = exact_count(nested(payload, planned_path), f"{paper} planned")
        observed = exact_count(nested(payload, observed_path), f"{paper} observed")
        valid = exact_count(nested(payload, valid_path), f"{paper} valid")
        if not 0 <= valid <= observed <= planned:
            raise ValueError(f"{paper} violates valid <= observed <= planned")
        authority_delta = payload.get(
            "paper_authority_delta",
            payload.get("computation_session_paper_authority_delta"),
        )
        if authority_delta != "NONE":
            raise ValueError(f"{paper} must retain paper authority delta NONE")
        if payload.get("external_authority_state") != "CANNOT_CHECK":
            raise ValueError(f"{paper} must retain external authority CANNOT_CHECK")
        claim_ceiling = payload.get("claim_ceiling")
        claim_ceiling_source_id = source_id
        if claim_ceiling is None:
            ledger_rows = [
                row
                for row in payloads["portfolio_claim_ledger"]["papers"]
                if row.get("job_id") == payload["job_id"]
            ]
            if len(ledger_rows) != 1:
                raise ValueError(f"{paper} lacks one claim-ceiling ledger binding")
            ledger_row = ledger_rows[0]
            if ledger_row.get("terminal") != payload["exact_terminal"]:
                raise ValueError(f"{paper} claim-ceiling ledger terminal mismatch")
            claim_ceiling = ledger_row.get("writing_class")
            claim_ceiling_source_id = "portfolio_claim_ledger"
        if not isinstance(claim_ceiling, str) or not claim_ceiling.strip():
            raise ValueError(f"{paper} claim ceiling must be a non-empty string")
        rows.append(
            {
                "paper": paper,
                "paper_id": paper,
                "job_id": payload["job_id"],
                "planned": planned,
                "observed": observed,
                "valid": valid,
                "unit": unit,
                "planned_path": planned_path,
                "observed_path": observed_path,
                "valid_path": valid_path,
                "status": status,
                "terminal": payload["exact_terminal"],
                "external_authority_state": payload["external_authority_state"],
                "paper_authority_delta": authority_delta,
                "claim_ceiling": claim_ceiling,
                "claim_ceiling_source_id": claim_ceiling_source_id,
                "source_id": source_id,
            }
        )
    return rows


def normalize_framework_mechanics(payloads: dict[str, Any]) -> dict[str, Any]:
    collision = payloads["des_collision_atlas"]
    update = payloads["des_update_algebra"]
    correspondence = payloads["des_projection_correspondence"]
    witnesses = payloads["des_projection_witnesses"]
    census = payloads["des_census_packet"]

    laws = [
        {
            "law": law,
            "pass": exact_count(counts["PASS"], f"{law} PASS"),
            "fail": exact_count(counts["FAIL"], f"{law} FAIL"),
        }
        for law, counts in sorted(update["laws"].items())
    ]
    mutations = [
        {
            "mutation": row["mutation_id"],
            "cases": exact_count(row["cases"], f"{row['mutation_id']} cases"),
            "detections": exact_count(
                row["detections"], f"{row['mutation_id']} detections"
            ),
            "killed": bool(row["killed"]),
        }
        for row in update["mutation_results"]
    ]
    occurrences = census["occurrence_denominators"]
    classified = exact_count(occurrences["classified_occurrences"], "classified occurrences")
    unclassified = exact_count(
        occurrences["unclassified_occurrences"], "unclassified occurrences"
    )
    total = exact_count(occurrences["occurrences"], "occurrences")
    if classified + unclassified != total:
        raise ValueError("census classified and unclassified counts do not close")

    return {
        "collision": {
            "state_count": exact_count(collision["finite_class"]["case_count"], "collision states"),
            "all_state_pairs": exact_count(collision["denominators"]["all_state_pairs"], "all state pairs"),
            "same_terminal_pairs": exact_count(collision["denominators"]["same_legacy_terminal_pairs"], "same-terminal pairs"),
            "different_action_pairs": exact_count(collision["denominators"]["different_action_collision_pairs"], "different-action pairs"),
            "terminal_action_counts": collision["label_action_counts"],
            "minimum_collision_hamming_distance": exact_count(collision["minimum_collision_hamming_distance"], "minimum collision distance"),
            "terminal": collision["terminal"],
            "claim_ceiling": collision["authority_ceiling"],
            "source_id": "des_collision_atlas",
        },
        "update_algebra": {
            "states": exact_count(update["finite_class"]["states"], "update states"),
            "event_instances": exact_count(update["finite_class"]["event_instances"], "event instances"),
            "laws": laws,
            "law_failures": sum(row["fail"] for row in laws),
            "mutations": mutations,
            "mutation_count": len(mutations),
            "mutations_killed": sum(row["killed"] for row in mutations),
            "terminal": update["terminal"],
            "claim_ceiling": update["claim_ceiling"],
            "paper_authority_delta": update["paper_authority_delta"],
            "source_id": "des_update_algebra",
        },
        "projection": {
            "state_cases": exact_count(correspondence["state_case_denominator"], "projection states"),
            "row_denominator": exact_count(correspondence["projection_row_denominator"], "projection rows"),
            "matched_rows": exact_count(correspondence["matched_projection_rows"], "matched projection rows"),
            "mismatch_count": len(correspondence["mismatches"]),
            "surface_results": correspondence["surface_results"],
            "noninjective_groups": exact_count(witnesses["group_count"], "noninjective groups"),
            "all_reachable_groups_noninjective": bool(witnesses["all_reachable_groups_noninjective"]),
            "action_divergent_groups": exact_count(witnesses["groups_with_action_divergence"], "action-divergent groups"),
            "unresolved_semantics_retained": bool(correspondence["unresolved_semantics_retained"]),
            "terminal": correspondence["terminal"],
            "authority": correspondence["authority"],
            "source_ids": ["des_projection_correspondence", "des_projection_witnesses"],
        },
        "census": {
            "tracked_entries": exact_count(occurrences["tracked_entries"], "tracked entries"),
            "parsed_text_files": exact_count(occurrences["parsed_text_files"], "parsed text files"),
            "retained_excluded_files": exact_count(occurrences["retained_excluded_files"], "retained excluded files"),
            "occurrences": total,
            "classified_occurrences": classified,
            "unclassified_occurrences": unclassified,
            "unique_labels": exact_count(occurrences["unique_labels"], "unique labels"),
            "family_counts": {
                key.removeprefix("family_"): exact_count(value, key)
                for key, value in occurrences.items()
                if key.startswith("family_")
            },
            "folds": census["transfer"]["folds"],
            "held_out_fold": exact_count(census["transfer"]["held_out_fold"], "held-out fold"),
            "held_out_classification_rate": finite(census["transfer"]["held_out_classification_rate"], "held-out classification rate"),
            "likely_text_cap_censored_count": exact_count(census["censoring_results"]["likely_text_cap_censored_count"], "text-cap censored count"),
            "likely_text_unreadable_count": exact_count(census["censoring_results"]["likely_text_unreadable_count"], "unreadable count"),
            "terminal": census["exact_terminal"],
            "claim_ceiling": census["claim_ceiling"],
            "source_id": "des_census_packet",
        },
    }


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
    snapshot = evidence_snapshot(root, sources)
    atlas = {
        "schema": SCHEMA,
        "authority_boundary": AUTHORITY_BOUNDARY,
        "evidence_snapshot": snapshot,
        "paper_states": normalize_paper_states(ledger),
        "gate_states": gate_states(metrics),
        "framework": framework(),
        "des_execution": normalize_des_execution(payloads),
        "framework_mechanics": normalize_framework_mechanics(payloads),
        "metrics": metrics,
        "metric_records": flat_metric_records(metrics),
        "anomalies": anomalies(metrics),
        "sources": sources,
        "notes": [
            "Incompatible units are not pooled across papers.",
            "Finite witnesses, hashes, tests, and same-owner replay are not external authority.",
            "Interactive outputs are presentation-only and inherit this claim ceiling.",
            "Frozen DES execution coverage is a separate layer; attempted, valid, and externally authoritative are not synonyms.",
        ],
    }
    manifest = {
        "schema": "orion.visualization.source-manifest.v1",
        "authority_boundary": AUTHORITY_BOUNDARY,
        "evidence_snapshot": snapshot,
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
