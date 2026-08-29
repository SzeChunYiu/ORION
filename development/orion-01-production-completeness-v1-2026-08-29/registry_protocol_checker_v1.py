#!/usr/bin/env python3
"""Canonical independent checker for the ORION-01 successor protocol freeze.

This program validates only the prospectively frozen, pre-execution protocol.
It imports no ORION or PyZX code and refuses source-instance/result artifacts
while the protocol terminal is PROTOCOL_FROZEN__NO_OUTCOME.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
IDENTITY = "orion-01-production-completeness-v1-2026-08-29"
CURRENT = "PROTOCOL_FROZEN__NO_OUTCOME"
OLD = "CANNOT_CHECK_MOVE_COMPLETENESS"
PREFIX = "dade7d46"

REQUIRED = (
    "README.md",
    "QUESTION.md",
    "PROTOCOL.json",
    "CORPUS_MANIFEST.json",
    "SOURCE_COMPLETE_MOVE_GRAMMAR.json",
    "REGISTRY_COMPLETENESS_THEOREM.md",
    "EXPECTED_TERMINALS.json",
    "ADVERSE_AND_CANNOT_CHECK.jsonl",
    "CLAIM_DISPOSITION.md",
    "registry_protocol_checker_v1.py",
)

FUTURE_ONLY = (
    "SOURCE_RESOLUTION_RECEIPT.json",
    "SOURCE_FILE_MANIFEST.jsonl",
    "ENVIRONMENT_RECEIPT.json",
    "PRODUCTION_ENTRY_ROOTS.json",
    "SOURCE_BOUNDARY_RECEIPT.json",
    "MUTATION_ROOTS.json",
    "CALL_GRAPH_CLOSURE.json",
    "UNRESOLVED_DYNAMIC_EDGES.json",
    "MOVE_INSTANCES.jsonl",
    "CANONICAL_EFFECT_CLASSES.jsonl",
    "DISTINGUISHING_BASIS_RECEIPT.json",
    "MOVE_INSTANCE_COVERAGE.json",
    "EQUIVALENCE_COVERAGE.json",
    "REGISTRY_COMPLETENESS_RECEIPT.json",
    "REGISTRY_COUNTEREXAMPLE.json",
    "EXACT_COMPUTE_PROTOCOL_V1.json",
    "EXACT_COMPUTE_RESULT.json",
)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def object_file(name: str) -> dict[str, Any]:
    value = json.loads((ROOT / name).read_text(encoding="utf-8"))
    need(isinstance(value, dict), f"{name} must be a JSON object")
    return value


def file_sha256(name: str) -> str:
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()


def phase_terminal_references(protocol: dict[str, Any]) -> set[str]:
    refs = {protocol["current_terminal"]}
    scalar_keys = (
        "entry",
        "success_terminal",
        "failure_terminal",
        "permitted_positive_terminal",
        "permitted_null_terminal",
        "permitted_adverse_terminal",
    )
    list_keys = ("requires", "failure_terminals")
    for phase in protocol["ordered_phases"]:
        for key in scalar_keys:
            value = phase.get(key)
            if isinstance(value, str):
                refs.add(value)
        for key in list_keys:
            value = phase.get(key, [])
            need(isinstance(value, list), f"phase {phase['phase']} field {key} is not a list")
            refs.update(item for item in value if isinstance(item, str))
    refs.add("CANNOT_RESOLVE_SOURCE")
    return refs


def check_files() -> dict[str, Any]:
    missing = [name for name in REQUIRED if not (ROOT / name).is_file()]
    need(not missing, "missing protocol files: " + ", ".join(missing))
    leaked = [name for name in FUTURE_ONLY if (ROOT / name).exists()]
    need(not leaked, "future-only artifacts leaked into protocol freeze: " + ", ".join(leaked))
    return {
        "name": "required_files_and_no_outcome_leakage",
        "status": "PASS",
        "required_files": len(REQUIRED),
        "future_only_files_absent": len(FUTURE_ONLY),
    }


def check_protocol(protocol: dict[str, Any]) -> dict[str, Any]:
    need(protocol["schema"] == "ORION.ORION01.ProductionCompletenessProtocol.v1", "protocol schema mismatch")
    need(protocol["protocol_identity"] == IDENTITY, "protocol identity mismatch")
    need(protocol["current_terminal"] == CURRENT, "protocol is not outcome-free")

    source = protocol["source_resolution"]
    need(source["repository"] == "Quantomatic/pyzx", "upstream repository changed")
    need(source["commit_prefix"] == PREFIX, "source prefix changed")
    need(source["required_match_count"] == 1, "source resolution is not unique")
    need(source["required_object_type"] == "commit", "source object type is not commit")
    need(source["required_full_object_name_length"] == 40, "full commit length is not 40")
    need(source["floating_ref_permitted"] is False, "floating source ref is permitted")
    need(source["semantic_testing_before_resolution_permitted"] is False, "semantic testing may precede resolution")

    old = protocol["old_execution"]
    need(old["pull_request"] == 1602, "old PR binding changed")
    need(old["terminal"] == OLD, "old terminal changed")
    need(old["all_eight_tasks_hit_cap"] is True, "cap-eight fact changed")
    need(old["role"] == "DERIVATION_AND_ADVERSE_EVIDENCE_ONLY", "old run gained successor authority")
    need(old["may_be_reinterpreted_as_positive"] is False, "old run may be positive")
    need(old["may_be_extended_under_same_identity"] is False, "old cap may be extended")

    phases = protocol["ordered_phases"]
    need([row["phase"] for row in phases] == list(range(6)), "phases are not exactly 0 through 5")
    need(phases[0]["entry"] == CURRENT, "phase 0 entry mismatch")
    need(phases[4]["requires"] == ["REGISTRY_COMPLETE"], "phase 4 is not registry-gated")
    for key in ("fresh_identity_required", "fresh_budget_required", "outcome_blind_freeze_required"):
        need(phases[4][key] is True, f"phase 4 does not require {key}")

    gate = protocol["pre_result_gate"]
    need(gate["old_round3_artifacts_may_satisfy_gate"] is False, "old artifacts may satisfy successor gate")
    need("EXACT_COMPUTE_RESULT.json" in gate["forbidden_before_registry_terminal"], "exact result is not registry-gated")

    authority = protocol["authority"]
    need(authority["external_peer_review"] is False, "external review overstated")
    need(authority["external_replication"] is False, "external replication overstated")
    need(authority["submission_authority"] is False, "submission authority overstated")
    need(authority["scientific_authority_delta_at_freeze"] == "NONE", "protocol freeze claims a result")
    return {"name": "protocol_identity_order_and_gates", "status": "PASS", "phases": len(phases)}


def check_corpus_and_grammar(corpus: dict[str, Any], grammar: dict[str, Any]) -> dict[str, Any]:
    need(corpus["protocol_identity"] == IDENTITY, "corpus identity mismatch")
    need(grammar["protocol_identity"] == IDENTITY, "grammar identity mismatch")
    upstream = corpus["upstream"]
    need(upstream["repository"] == "Quantomatic/pyzx", "corpus repository changed")
    need(upstream["commit_prefix"] == PREFIX, "corpus prefix changed")
    need(upstream["required_unique_full_commit"] is True, "corpus does not require unique commit")
    need(upstream["floating_ref_permitted"] is False, "corpus permits a floating ref")

    state = corpus["current_state"]
    need(state["full_commit"] is None, "full commit populated before resolution receipt")
    need(state["source_file_manifest"] is None, "source manifest populated before resolution receipt")
    need(state["semantic_testing_started"] is False, "semantic testing already started")
    need(state["terminal"] == CURRENT, "corpus terminal mismatch")

    need(grammar["status"] == "PROSPECTIVELY_FROZEN__INSTANCE_NOT_DISCHARGED", "grammar claims an outcome")
    instance = grammar["current_instance"]
    need(instance["resolved_source_commit"] is None, "grammar embeds a source outcome")
    need(instance["mutation_roots"] is None, "grammar embeds mutation-root results")
    need(instance["move_instances"] is None, "grammar embeds move-instance results")
    need(instance["canonical_effect_classes"] is None, "grammar embeds class results")
    need(instance["registry_terminal"] is None, "grammar embeds a registry terminal")
    need(instance["protocol_terminal"] == CURRENT, "grammar terminal mismatch")

    equivalence = grammar["extensional_equivalence"]
    basis = grammar["distinguishing_basis"]
    ledger = grammar["completeness_ledger"]
    need(equivalence["small_random_agreement_sufficient"] is False, "small random agreement can prove equivalence")
    need(basis["random_or_fuzz_only_sufficient"] is False, "fuzzing alone can prove separation")
    need(basis["bounded_size_only_sufficient_without_small_model_theorem"] is False, "bounded size alone can prove separation")
    need(ledger["duplicate_assignment_permitted"] is False, "duplicate class assignments permitted")
    need(ledger["unassigned_instance_permitted"] is False, "unassigned move instances permitted")
    need(ledger["orphan_class_permitted"] is False, "orphan classes permitted")
    return {
        "name": "source_corpus_and_extensional_grammar",
        "status": "PASS",
        "mutation_sink_kinds": len(grammar["mutation_root_discovery"]["mutation_sinks"]),
        "counterexample_types": len(grammar["counterexample_schema"]["permitted_types"]),
    }


def check_terminals(protocol: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    need(expected["protocol_identity"] == IDENTITY, "terminal identity mismatch")
    need(expected["terminal_set_frozen_before_execution"] is True, "terminal set not prospectively frozen")
    need(expected["current_terminal"] == CURRENT, "terminal file current state mismatch")
    rows = expected["terminals"]
    names = [row["terminal"] for row in rows]
    terminal_set = set(names)
    need(len(names) == len(terminal_set), "duplicate terminal names")
    need(CURRENT in terminal_set, "current terminal undeclared")
    need(OLD not in terminal_set, "old terminal promoted into successor terminal set")
    forbidden = set(expected["forbidden_as_successor_terminal"])
    need(OLD in forbidden, "old terminal not explicitly forbidden")
    need(not terminal_set.intersection(forbidden), "forbidden terminal declared as successor outcome")

    refs = phase_terminal_references(protocol)
    missing = sorted(refs - terminal_set)
    need(not missing, "protocol references undeclared terminals: " + ", ".join(missing))
    for edge in expected["transition_rules"]:
        need(edge["from"] in terminal_set, "transition source undeclared")
        need(set(edge["to_any_of"]).issubset(terminal_set), "transition target undeclared")

    row_by_name = {row["terminal"]: row for row in rows}
    need(row_by_name["REGISTRY_COMPLETE"]["class"] == "PRIMARY_SUCCESS", "registry success class mismatch")
    need(row_by_name["REGISTRY_INCOMPLETE_COUNTEREXAMPLE"]["class"] == "PRIMARY_ADVERSE", "registry counterexample class mismatch")
    need(row_by_name["NO_MATERIAL_CONSEQUENCE_WITHIN_FROZEN_DOMAIN"]["class"] == "PRIMARY_NULL", "material null class mismatch")
    return {
        "name": "terminal_set_and_transitions",
        "status": "PASS",
        "terminals": len(terminal_set),
        "protocol_references": len(refs),
    }


def check_text_boundaries() -> dict[str, Any]:
    theorem = (ROOT / "REGISTRY_COMPLETENESS_THEOREM.md").read_text(encoding="utf-8").lower()
    question = (ROOT / "QUESTION.md").read_text(encoding="utf-8").lower()
    claims = (ROOT / "CLAIM_DISPOSITION.md").read_text(encoding="utf-8").lower()
    for obligation in ("o1", "o2", "o3", "o4", "o5", "o6"):
        need(obligation in theorem, f"theorem omits {obligation.upper()}")
    for marker in (
        "source instance obligations open",
        "registry_incomplete_counterexample",
        "quotient preservation",
        CURRENT.lower(),
    ):
        need(marker in theorem, f"theorem omits marker: {marker}")
    need("a larger enumeration is not itself a contribution" in question, "question permits cap-only promotion")
    need("cannot_check_move_completeness" in question, "question omits old terminal")
    need("upgraded retrospectively" in question, "question omits retrospective-upgrade exclusion")
    need("conditional theorem proved; source instance open" in claims, "claims obscure conditional status")
    need(CURRENT.lower() in claims, "claims omit no-outcome terminal")
    return {"name": "theorem_question_and_claim_boundaries", "status": "PASS", "obligations": 6}


def check_adverse_ledger() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate((ROOT / "ADVERSE_AND_CANNOT_CHECK.jsonl").read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        need(isinstance(value, dict), f"adverse row {line_number} is not an object")
        rows.append(value)
    need(len(rows) == 2, "adverse ledger must contain Round 2 and Round 3")
    need({row["round"] for row in rows} == {2, 3}, "adverse rounds changed")
    for row in rows:
        need(row["protocol_identity"] == IDENTITY, "adverse identity mismatch")
        need(row["terminal"] == OLD, "adverse terminal changed")
        need(row["successor_role"] == "DERIVATION_AND_ADVERSE_EVIDENCE_ONLY", "old evidence gained authority")
        need(row["may_discharge_source_resolution"] is False, "old evidence may discharge source resolution")
        need(row["may_discharge_registry_completeness"] is False, "old evidence may discharge registry completeness")
        need(row["may_authorize_old_cap_increase"] is False, "old evidence may authorize cap increase")
    round3 = next(row for row in rows if row["round"] == 3)
    need(round3["task_indices"] == list(range(8)), "Round 3 task indices changed")
    need(round3["all_tasks_hit_frozen_cap"] is True, "Round 3 cap-eight fact changed")
    need(round3["aggregate_sha256"] == "7e26974b9afab27abb88a27b7c2c5ba058e6d351f0d2f8428c4fa8e50acada31", "Round 3 aggregate hash changed")
    return {"name": "adverse_and_cannot_check_ledger", "status": "PASS", "rows": len(rows)}


def run_checks() -> dict[str, Any]:
    protocol = object_file("PROTOCOL.json")
    corpus = object_file("CORPUS_MANIFEST.json")
    grammar = object_file("SOURCE_COMPLETE_MOVE_GRAMMAR.json")
    expected = object_file("EXPECTED_TERMINALS.json")
    checks = [
        check_files(),
        check_protocol(protocol),
        check_corpus_and_grammar(corpus, grammar),
        check_terminals(protocol, expected),
        check_text_boundaries(),
        check_adverse_ledger(),
    ]
    need(all(row["status"] == "PASS" for row in checks), "not all protocol checks passed")
    inputs = {name: file_sha256(name) for name in REQUIRED if name != "registry_protocol_checker_v1.py"}
    return {
        "schema": "ORION.ORION01.RegistryProtocolCheck.v1",
        "protocol_identity": IDENTITY,
        "implementation_independent": True,
        "imports_orion": False,
        "imports_pyzx": False,
        "source_instance_executed": False,
        "checks": checks,
        "input_sha256": inputs,
        "all_passed": True,
        "terminal": "PROTOCOL_FREEZE_VALIDATED__NO_SOURCE_OUTCOME",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_checks()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
