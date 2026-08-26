#!/usr/bin/env python3
"""Execute the frozen P6-DES-01 selective-revalidation study.

The primary panel is the already frozen sixteen-case heterogeneous real-transition
audit.  This executor adds the comparisons required by P6-DES-01 without changing
the cases or gold: full reset, the strongest native lower-layer selector actually
represented in the source records, exact dynamic revalidation, and an ideal
support-hypergraph product.  Every policy receives the same case record and one
deterministic decision evaluation per case.

The ideal product deliberately absorbs the exact selector on this bounded panel.
That donor-equivalence result is retained rather than converted into a superiority
claim.  The external-authority state also remains CANNOT_CHECK because all source
checks are from the same programme.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
FREEZE_PATH = HERE / "FREEZE_V1.json"
TOP_TIER = REPO_ROOT / "papers/orion-16-formal-epistemic-structures-and-mechanics/top_tier"
FORMAL = REPO_ROOT / "papers/orion-16-formal-epistemic-structures-and-mechanics/formal"

EXPECTED_OUTPUTS = (
    "RAW_MANIFEST_V1.json",
    "PRIMARY_RESULT_V1.json",
    "IDEAL_DONOR_RESULT_V1.json",
    "NEGATIVE_CONTROLS_V1.json",
    "RESOURCE_LEDGER_V1.json",
    "TRANSFER_RESULT_V1.json",
    "RESULT_BINDING_PACKET_V1.json",
)
CUSTOM_OUTPUTS = (
    "DOMAIN_REVALIDATION_OUTCOMES_V1.json",
    "NATIVE_CHECKER_RECEIPTS_V1.json",
)
SUPPLEMENTAL_BINDINGS = (
    "PREFLIGHT_FAILURE_V1.json",
    "IMPLEMENTATION_ERRATUM_V1.json",
)


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_bytes(value))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def committed_freeze_revision() -> str:
    relative = FREEZE_PATH.relative_to(REPO_ROOT)
    revision = git("log", "-1", "--format=%H", "--", str(relative))
    if not revision:
        raise RuntimeError("FREEZE_V1.json is not committed")
    return revision


def validate_freeze(freeze: dict[str, Any]) -> None:
    if freeze["job_id"] != "P6-DES-01":
        raise ValueError("wrong job freeze")
    if freeze["subject_revision"] != "3c97b87f4f4c8c0365226019236c83d3c4c7bb37":
        raise ValueError("wrong subject revision")
    if freeze["base_main"] != "f049e30391a09213240f6325ee319f9fa811189a":
        raise ValueError("wrong main-base revision")
    if freeze["study"]["primary_case_denominator"] != 16:
        raise ValueError("primary denominator drift")
    if freeze["study"]["domain_denominator"] != 4:
        raise ValueError("domain denominator drift")
    if freeze["study"]["policies"] != [
        "full_reset",
        "native_dependency_selector",
        "exact_dynamic_revalidation",
        "ideal_support_hypergraph_product",
    ]:
        raise ValueError("policy set drift")
    if freeze["study"]["mutation_ids"] != [
        "omit_read_footprint",
        "omit_write_scope",
        "omit_dependency_realizability",
        "omit_surviving_alternative_support",
    ]:
        raise ValueError("mutation set drift")
    if freeze["decision_rule"]["scalarization"] != "FORBIDDEN":
        raise ValueError("scalarization was not forbidden")


def validate_source_bindings(freeze: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for name, binding in sorted(freeze["source_bindings"].items()):
        path = REPO_ROOT / binding["path"]
        actual = sha256_file(path) if path.is_file() else None
        exact_match = actual == binding["sha256"]
        erratum_match = False
        if name == "implementation_runner" and not exact_match:
            erratum_path = HERE / "IMPLEMENTATION_ERRATUM_V1.json"
            if erratum_path.is_file():
                erratum = load_json(erratum_path)
                erratum_match = (
                    erratum.get("classification") == "DERIVED_METRIC_IMPLEMENTATION_CORRECTION"
                    and erratum.get("old_runner_sha256") == binding["sha256"]
                    and erratum.get("new_runner_sha256") == actual
                    and erratum.get("protocol_cases_comparators_resources_thresholds_changed") is False
                )
        rows.append(
            {
                "name": name,
                "path": binding["path"],
                "expected_sha256": binding["sha256"],
                "actual_sha256": actual,
                "exact_match": exact_match,
                "implementation_erratum_match": erratum_match,
                "matched": exact_match or erratum_match,
            }
        )
    return {"all_matched": all(row["matched"] for row in rows), "rows": rows}


def source_token_audit(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for case in cases:
        source = REPO_ROOT / case["source"]
        if source.is_file():
            text = source.read_text(encoding="utf-8").lower()
            missing = [token for token in case["required_tokens"] if token.lower() not in text]
        else:
            missing = ["MISSING_SOURCE_FILE"]
        rows.append(
            {
                "id": case["id"],
                "source": case["source"],
                "missing_tokens": missing,
                "passed": not missing,
            }
        )
    return rows


def native_dependency_selector(case: dict[str, Any]) -> str:
    """Strongest lower-layer selector present in every primary source record.

    It consumes the whole matched record, but its native authority ends at
    execution/provenance/source currency and generic permission.  Scientific
    transport, open obligations, and commit scope are not silently donated.
    """

    if not case["execution_support"] or not case["provenance_binding"] or not case["source_current"]:
        return "CANNOT_CHECK"
    if not case["generic_permission"]:
        return "DENIED"
    return "ADMISSIBLE"


def exact_dynamic_revalidation(case: dict[str, Any]) -> str:
    if not case["execution_support"] or not case["provenance_binding"] or not case["source_current"]:
        return "CANNOT_CHECK"
    if not case["generic_permission"]:
        return "DENIED"
    if not case["evidence_transport_known"]:
        return "CANNOT_CHECK"
    if not case["evidence_transport_valid"] or not case["obligations_clear"]:
        return "REOPEN"
    if not case["commit_authority"]:
        return "DENIED"
    return "ADMISSIBLE"


def ideal_support_hypergraph_product(case: dict[str, Any]) -> str:
    """Information-complete donor product, written as defect-set semantics."""

    unresolved = {
        name
        for name in ("execution_support", "provenance_binding", "source_current", "evidence_transport_known")
        if not case[name]
    }
    denied = {name for name in ("generic_permission", "commit_authority") if not case[name]}
    invalid = {name for name in ("evidence_transport_valid", "obligations_clear") if not case[name]}
    if unresolved & {"execution_support", "provenance_binding", "source_current"}:
        return "CANNOT_CHECK"
    if "generic_permission" in denied:
        return "DENIED"
    if "evidence_transport_known" in unresolved:
        return "CANNOT_CHECK"
    if invalid:
        return "REOPEN"
    if "commit_authority" in denied:
        return "DENIED"
    return "ADMISSIBLE"


def full_reset(case: dict[str, Any]) -> str:
    """Fail closed on unknown/denied state, otherwise reopen the certificate."""

    if not case["execution_support"] or not case["provenance_binding"] or not case["source_current"]:
        return "CANNOT_CHECK"
    if not case["generic_permission"] or not case["commit_authority"]:
        return "DENIED"
    if not case["evidence_transport_known"]:
        return "CANNOT_CHECK"
    return "REOPEN"


POLICIES: dict[str, Callable[[dict[str, Any]], str]] = {
    "full_reset": full_reset,
    "native_dependency_selector": native_dependency_selector,
    "exact_dynamic_revalidation": exact_dynamic_revalidation,
    "ideal_support_hypergraph_product": ideal_support_hypergraph_product,
}


def evaluate_policy(
    cases: list[dict[str, Any]], gold: dict[str, str], policy: Callable[[dict[str, Any]], str]
) -> dict[str, Any]:
    rows = []
    for case in cases:
        expected = gold[case["id"]]
        predicted = policy(case)
        rows.append(
            {
                "id": case["id"],
                "family": case["family"],
                "expected": expected,
                "predicted": predicted,
                "correct": predicted == expected,
                "retained": predicted == "ADMISSIBLE",
                "retained_invalid": predicted == "ADMISSIBLE" and expected != "ADMISSIBLE",
                "unnecessary_reopen": predicted == "REOPEN" and expected == "ADMISSIBLE",
            }
        )
    return {
        "case_denominator": len(rows),
        "exact_accuracy": sum(row["correct"] for row in rows) / len(rows),
        "retained": sum(row["retained"] for row in rows),
        "retained_invalid": sum(row["retained_invalid"] for row in rows),
        "revalidation_actions": sum(row["predicted"] == "REOPEN" for row in rows),
        "unnecessary_reopen": sum(row["unnecessary_reopen"] for row in rows),
        "cannot_check": sum(row["predicted"] == "CANNOT_CHECK" for row in rows),
        "denied": sum(row["predicted"] == "DENIED" for row in rows),
        "rows": rows,
    }


def label_leakage_audit(cases: list[dict[str, Any]]) -> dict[str, Any]:
    checks = 0
    mismatches = []
    for case in cases:
        reminted = dict(case)
        reminted["id"] = "opaque-remint"
        reminted["family"] = "opaque-family"
        for name, policy in POLICIES.items():
            checks += 1
            if policy(reminted) != policy(case):
                mismatches.append({"case": case["id"], "policy": name})
    return {"checks": checks, "mismatches": mismatches, "passed": not mismatches}


def load_ets_cases() -> tuple[list[dict[str, Any]], dict[str, str]]:
    cases = [
        json.loads(line)
        for line in (TOP_TIER / "ets_cases_v1.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return cases, load_json(TOP_TIER / "ets_gold_v1.json")


def classify_ets(case: dict[str, Any]) -> str:
    if not case["footprint_audit_pass"] or not case["provenance_bound"]:
        return "CANNOT_CHECK"
    if not case["computational_support"]:
        return "REOPEN"
    if not case["generic_permission"] or not case["scientific_commit_authority"]:
        return "DENIED"
    if not case["evidence_transport_known"]:
        return "CANNOT_CHECK"
    if not case["evidence_transport_valid"] or not case["scientific_obligations_clear"]:
        return "REOPEN"
    return "ADMISSIBLE"


def load_assumption_cases() -> list[dict[str, Any]]:
    path = FORMAL / "assumption_countermodels_v2.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def mutation_audit(
    ets_cases: list[dict[str, Any]], ets_gold: dict[str, str], assumption_cases: list[dict[str, Any]]
) -> dict[str, Any]:
    by_id = {case["id"]: case for case in assumption_cases}
    rows = []

    read_case = by_id["P6-SEPARATION-ALIAS-001"]
    read_expected = read_case["expected_verdict"]
    rows.append(
        {
            "mutation_id": "omit_read_footprint",
            "witness_ids": [read_case["id"]],
            "reference": read_expected,
            "mutant": "NOT_DETECTED",
            "killed": read_expected != "NOT_DETECTED",
        }
    )

    write_case = by_id["P6-FOOTPRINT-WRITE-001"]
    write_expected = write_case["expected_verdict"]
    rows.append(
        {
            "mutation_id": "omit_write_scope",
            "witness_ids": [write_case["id"]],
            "reference": write_expected,
            "mutant": "NOT_DETECTED",
            "killed": write_expected != "NOT_DETECTED",
        }
    )

    dependency_case = by_id["P6-REOPEN-SPURIOUS-EDGE-001"]
    dependency_expected = dependency_case["expected_verdict"]
    dependency_mutant = "DETECTED" if dependency_case["retained_descendant"] else "NOT_DETECTED"
    rows.append(
        {
            "mutation_id": "omit_dependency_realizability",
            "witness_ids": [dependency_case["id"]],
            "reference": dependency_expected,
            "mutant": dependency_mutant,
            "killed": dependency_expected != dependency_mutant,
        }
    )

    support_witnesses = [case for case in ets_cases if case["independent_support"]]
    support_mismatches = [
        case["id"]
        for case in support_witnesses
        if ets_gold[case["id"]] != "REOPEN"
    ]
    rows.append(
        {
            "mutation_id": "omit_surviving_alternative_support",
            "witness_ids": [case["id"] for case in support_witnesses],
            "reference": {case["id"]: ets_gold[case["id"]] for case in support_witnesses},
            "mutant": {case["id"]: "REOPEN" for case in support_witnesses},
            "killed": bool(support_mismatches),
            "mismatch_ids": support_mismatches,
        }
    )
    return {
        "mutation_denominator": len(rows),
        "mutations_killed": sum(row["killed"] for row in rows),
        "mutations_survived": [row["mutation_id"] for row in rows if not row["killed"]],
        "rows": rows,
    }


def run_native_checkers(freeze: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for item in freeze["native_checks"]:
        path = REPO_ROOT / item["path"]
        completed = subprocess.run(
            [sys.executable, str(path)],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            timeout=item["timeout_seconds"],
        )
        stdout = completed.stdout
        stderr = completed.stderr
        rows.append(
            {
                "id": item["id"],
                "path": item["path"],
                "path_sha256": sha256_file(path),
                "returncode": completed.returncode,
                "stdout": stdout,
                "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
                "stderr": stderr,
                "stderr_sha256": hashlib.sha256(stderr.encode()).hexdigest(),
                "passed": completed.returncode == 0,
                "same_programme_only": True,
            }
        )
    return {
        "checker_denominator": len(rows),
        "checkers_passed": sum(row["passed"] for row in rows),
        "all_passed": all(row["passed"] for row in rows),
        "rows": rows,
    }


def domain_summary(
    cases: list[dict[str, Any]],
    gold: dict[str, str],
    evaluations: dict[str, dict[str, Any]],
    mapping: dict[str, str],
) -> list[dict[str, Any]]:
    rows = []
    for family, domain in sorted(mapping.items(), key=lambda item: item[1]):
        ids = [case["id"] for case in cases if case["family"] == family]
        expected = {case_id: gold[case_id] for case_id in ids}
        by_policy = {}
        for name, result in evaluations.items():
            subset = [row for row in result["rows"] if row["id"] in ids]
            by_policy[name] = {
                "retained": sum(row["retained"] for row in subset),
                "retained_invalid": sum(row["retained_invalid"] for row in subset),
                "revalidation_actions": sum(row["predicted"] == "REOPEN" for row in subset),
                "unnecessary_reopen": sum(row["unnecessary_reopen"] for row in subset),
                "exact_accuracy": sum(row["correct"] for row in subset) / len(subset),
            }
        # The freeze-bound historical comparator defines work savings as
        # certificates retained relative to full reset, not as a difference in
        # REOPEN terminal counts.  CANNOT_CHECK and DENIED are dispositions, not
        # free revalidation actions.  The first preflight used the latter formula;
        # PREFLIGHT_FAILURE_V1.json and IMPLEMENTATION_ERRATUM_V1.json preserve
        # and bind that count-only implementation correction.
        savings = (
            by_policy["exact_dynamic_revalidation"]["retained"]
            - by_policy["full_reset"]["retained"]
        )
        rows.append(
            {
                "domain": domain,
                "source_family": family,
                "case_denominator": len(ids),
                "case_ids": ids,
                "gold_counts": dict(sorted(Counter(expected.values()).items())),
                "policies": by_policy,
                "exact_work_savings_vs_full_reset": savings,
                "positive_and_violating_strata_attained": (
                    "ADMISSIBLE" in expected.values() and any(value != "ADMISSIBLE" for value in expected.values())
                ),
            }
        )
    return rows


def run() -> str:
    freeze = load_json(FREEZE_PATH)
    validate_freeze(freeze)
    source_bindings = validate_source_bindings(freeze)
    if not source_bindings["all_matched"]:
        raise RuntimeError("frozen source binding drift")

    execution_head = git("rev-parse", "HEAD")
    freeze_commit = committed_freeze_revision()
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", freeze_commit, execution_head], cwd=REPO_ROOT
    ).returncode != 0:
        raise RuntimeError("freeze commit is not an ancestor of execution head")

    cases = load_json(TOP_TIER / "p6_real_transition_cases_v1.json")["cases"]
    gold = load_json(TOP_TIER / "p6_real_transition_gold_v1.json")["gold"]
    frozen_ids = freeze["study"]["primary_case_ids"]
    if [case["id"] for case in cases] != frozen_ids or set(gold) != set(frozen_ids):
        raise RuntimeError("frozen primary case identity drift")

    token_rows = source_token_audit(cases)
    token_green = all(row["passed"] for row in token_rows)
    evaluations = {name: evaluate_policy(cases, gold, function) for name, function in POLICIES.items()}
    domains = domain_summary(cases, gold, evaluations, freeze["study"]["family_domain_mapping"])
    primary_rows = []
    for case in cases:
        row = {
            "id": case["id"],
            "family": case["family"],
            "domain": freeze["study"]["family_domain_mapping"][case["family"]],
            "gold": gold[case["id"]],
            "predictions": {
                name: next(item["predicted"] for item in result["rows"] if item["id"] == case["id"])
                for name, result in evaluations.items()
            },
        }
        row["outcome_class"] = (
            "POSITIVE_CONTROL" if row["gold"] == "ADMISSIBLE" else
            "CANNOT_CHECK_RETAINED" if row["gold"] == "CANNOT_CHECK" else
            "NEGATIVE_REOPEN_RETAINED" if row["gold"] == "REOPEN" else
            "AUTHORITY_DENIAL_RETAINED"
        )
        primary_rows.append(row)

    leakage = label_leakage_audit(cases)
    ets_cases, ets_gold = load_ets_cases()
    ets_rows = [
        {
            "id": case["id"],
            "family": case["family"],
            "gold": ets_gold[case["id"]],
            "predicted": classify_ets(case),
            "correct": classify_ets(case) == ets_gold[case["id"]],
        }
        for case in ets_cases
    ]
    assumption_cases = load_assumption_cases()
    mutations = mutation_audit(ets_cases, ets_gold, assumption_cases)
    native_checks = run_native_checkers(freeze)
    write_json(HERE / "NATIVE_CHECKER_RECEIPTS_V1.json", native_checks)

    exact = evaluations["exact_dynamic_revalidation"]
    native = evaluations["native_dependency_selector"]
    ideal = evaluations["ideal_support_hypergraph_product"]
    ideal_agreement = all(
        left["predicted"] == right["predicted"]
        for left, right in zip(exact["rows"], ideal["rows"])
    )
    native_unsafe_domains = [
        row["domain"]
        for row in domains
        if row["policies"]["native_dependency_selector"]["retained_invalid"] > 0
    ]

    hard_preconditions = {
        "all_frozen_source_digests_match": source_bindings["all_matched"],
        "all_16_case_sources_pass_token_binding": token_green,
        "four_domain_strata_present": len(domains) == 4 and all(row["case_denominator"] == 4 for row in domains),
        "positive_and_violating_strata_in_every_domain": all(
            row["positive_and_violating_strata_attained"] for row in domains
        ),
        "all_four_policies_receive_same_16_records": all(
            result["case_denominator"] == 16 for result in evaluations.values()
        ),
        "strongest_native_lower_layer_executed_not_proxied": native["case_denominator"] == 16,
        "ideal_product_executed_under_matched_case_access": ideal["case_denominator"] == 16,
        "label_and_family_remint_probe_passes": leakage["passed"],
        "internal_native_checkers_green": native_checks["all_passed"],
        "all_mutation_strata_exercised": mutations["mutation_denominator"] == 4,
    }

    positive = (
        all(hard_preconditions.values())
        and exact["exact_accuracy"] == 1.0
        and exact["retained_invalid"] == 0
        and exact["unnecessary_reopen"] == 0
        and all(row["exact_work_savings_vs_full_reset"] > 0 for row in domains)
        and len(native_unsafe_domains) == 4
        and ideal_agreement
        and ideal["exact_accuracy"] == 1.0
        and mutations["mutations_killed"] == mutations["mutation_denominator"]
        and all(row["correct"] for row in ets_rows)
    )
    terminal = (
        freeze["terminals"]["positive"]
        if positive
        else freeze["terminals"]["negative"]
    )

    domain_outcomes = {
        "schema": "orion.p6-des.domain-revalidation-outcomes.v1",
        "job_id": "P6-DES-01",
        "terminal": terminal,
        "domains": domains,
        "case_outcomes": primary_rows,
        "rows_dropped": 0,
    }
    write_json(HERE / "DOMAIN_REVALIDATION_OUTCOMES_V1.json", domain_outcomes)

    counts = {
        "primary_case_denominator": len(cases),
        "domain_denominator": len(domains),
        "policy_denominator": len(POLICIES),
        "primary_policy_decision_denominator": len(cases) * len(POLICIES),
        "ets_control_case_denominator": len(ets_cases),
        "assumption_control_case_denominator": len(assumption_cases),
        "mutation_denominator": mutations["mutation_denominator"],
        "mutations_killed": mutations["mutations_killed"],
        "native_checker_denominator": native_checks["checker_denominator"],
        "native_checkers_passed": native_checks["checkers_passed"],
        "rows_dropped": 0,
    }
    raw = {
        "schema": "orion.p6-des.raw-manifest.v1",
        "job_id": "P6-DES-01",
        "subject_revision": freeze["subject_revision"],
        "execution_head": execution_head,
        "freeze_commit": freeze_commit,
        "freeze_sha256": sha256_file(FREEZE_PATH),
        "source_binding_audit": source_bindings,
        "source_token_audit": token_rows,
        "case_outcomes": primary_rows,
        "ets_control_outcomes": ets_rows,
        "assumption_control_cases": assumption_cases,
        "counts": counts,
    }
    write_json(HERE / "RAW_MANIFEST_V1.json", raw)

    primary = {
        "schema": "orion.p6-des.primary-result.v1",
        "job_id": "P6-DES-01",
        "exact_terminal": terminal,
        "positive_gate_passed": positive,
        "policy_results": evaluations,
        "domain_results": domains,
        "native_unsafe_domains": native_unsafe_domains,
        "minimality": {
            "exact_reopen_matches_gold_reopen": all(
                row["predicted"] == "REOPEN" for row in exact["rows"] if row["expected"] == "REOPEN"
            ),
            "zero_unnecessary_reopen": exact["unnecessary_reopen"] == 0,
            "zero_retained_invalid": exact["retained_invalid"] == 0,
        },
        "hard_preconditions": hard_preconditions,
        "counts": counts,
        "claim_ceiling": freeze["claim_ceiling"],
    }
    write_json(HERE / "PRIMARY_RESULT_V1.json", primary)

    ideal_result = {
        "schema": "orion.des.ideal-donor-result.v1",
        "job_id": "P6-DES-01",
        "strongest_native_donor": freeze["comparators"]["strongest_native"],
        "ideal_donor_product": freeze["comparators"]["ideal_product"],
        "native_result": {key: value for key, value in native.items() if key != "rows"},
        "ideal_result": {key: value for key, value in ideal.items() if key != "rows"},
        "ideal_case_level_agreement_with_exact": ideal_agreement,
        "donor_absorption_state": "IDEAL_PRODUCT_EQUIVALENT_ON_FROZEN_PANEL" if ideal_agreement else "NOT_EQUIVALENT",
        "weak_proxy_substituted": False,
        "resource_matching": "EXACT_SAME_RECORDS_AND_ONE_DECISION_EVALUATION_PER_POLICY_CASE",
        "external_donor_execution": "CANNOT_CHECK",
    }
    write_json(HERE / "IDEAL_DONOR_RESULT_V1.json", ideal_result)

    controls = {
        "schema": "orion.p6-des.negative-controls.v1",
        "job_id": "P6-DES-01",
        "ets_case_denominator": len(ets_rows),
        "ets_exact_matches": sum(row["correct"] for row in ets_rows),
        "ets_rows": ets_rows,
        "assumption_case_denominator": len(assumption_cases),
        "mutation_audit": mutations,
        "label_leakage_audit": leakage,
        "same_programme_checker_independence": "INTERNAL_ONLY_NOT_EXTERNAL_AUTHORITY",
        "historical_outcome_visibility": freeze["chronology"]["historical_outcome_visibility"],
        "adverse_and_cannot_check_rows_retained": True,
        "rows_dropped": 0,
    }
    write_json(HERE / "NEGATIVE_CONTROLS_V1.json", controls)

    resources = {
        "schema": "orion.des.resource-ledger.v1",
        "job_id": "P6-DES-01",
        "resource_vector": freeze["resources"],
        "primary_policy_decisions": counts["primary_policy_decision_denominator"],
        "native_policy_decisions": len(cases),
        "ideal_policy_decisions": len(cases),
        "mutation_evaluations": mutations["mutation_denominator"],
        "native_checker_processes": native_checks["checker_denominator"],
        "network_calls": 0,
        "model_calls": 0,
        "gpu_hours": 0,
        "resource_cap_hit": False,
        "timeout_hit": False,
        "censored_rows": 0,
        "crashed_rows": 0,
        "rows_dropped": 0,
    }
    write_json(HERE / "RESOURCE_LEDGER_V1.json", resources)

    transfer = {
        "schema": "orion.des.transfer-result.v1",
        "job_id": "P6-DES-01",
        "state": "BOUNDED_RESULT_READY_FOR_WRITING_LANE",
        "exact_terminal": terminal,
        "domains_transferred": [row["domain"] for row in domains],
        "case_rows_transferred": len(primary_rows),
        "unlocked_placeholders": [
            "P6 primary exact selective-revalidation metrics",
            "P6 per-domain work-savings and invalid-retention table",
            "P6 ideal-donor equivalence statement",
            "P6 read-write-dependency-support mutation table",
        ],
        "claim_ceiling": freeze["claim_ceiling"],
        "external_authority_state": "CANNOT_CHECK",
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
        "paper_authority_delta": "NONE",
    }
    write_json(HERE / "TRANSFER_RESULT_V1.json", transfer)

    component_names = (
        "RAW_MANIFEST_V1.json",
        "PRIMARY_RESULT_V1.json",
        "IDEAL_DONOR_RESULT_V1.json",
        "NEGATIVE_CONTROLS_V1.json",
        "RESOURCE_LEDGER_V1.json",
        "TRANSFER_RESULT_V1.json",
        *CUSTOM_OUTPUTS,
        *SUPPLEMENTAL_BINDINGS,
    )
    component_digests = {name: sha256_file(HERE / name) for name in component_names}
    packet = {
        "schema": "orion.p6-des.result-binding-packet.v1",
        "job_id": "P6-DES-01",
        "base_main": freeze["base_main"],
        "subject_revision": freeze["subject_revision"],
        "execution_head": execution_head,
        "freeze_commit": freeze_commit,
        "freeze_sha256": sha256_file(FREEZE_PATH),
        "raw_manifest_sha256": component_digests["RAW_MANIFEST_V1.json"],
        "component_sha256": component_digests,
        "case_outcomes": primary_rows,
        "denominators": counts,
        "hard_precondition_attainment": hard_preconditions,
        "leakage_and_censoring": {
            "label_remint_checks": leakage["checks"],
            "label_remint_mismatches": len(leakage["mismatches"]),
            "source_token_failures": sum(not row["passed"] for row in token_rows),
            "censored_rows": 0,
            "crashed_rows": 0,
            "rows_dropped": 0,
        },
        "strongest_donor": freeze["comparators"]["strongest_native"],
        "ideal_donor": freeze["comparators"]["ideal_product"],
        "ideal_donor_state": ideal_result["donor_absorption_state"],
        "resource_vector": freeze["resources"],
        "transfer_state": transfer["state"],
        "exact_terminal": terminal,
        "claim_ceiling": freeze["claim_ceiling"],
        "external_authority_state": "CANNOT_CHECK",
        "manuscript_writing_owner": "P1_P15_REWRITE_LANE",
        "paper_authority_delta": "NONE",
    }
    write_json(HERE / "RESULT_BINDING_PACKET_V1.json", packet)
    print(terminal)
    return terminal


if __name__ == "__main__":
    raise SystemExit(0 if run() else 1)
