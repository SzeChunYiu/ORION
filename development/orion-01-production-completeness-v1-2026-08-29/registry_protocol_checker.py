#!/usr/bin/env python3
"""Independent pre-execution checker for the ORION-01 successor protocol.

This checker validates the prospectively frozen protocol and confirms that no
source-instance or exact-compute result has leaked into the pre-execution
identity. It imports only Python's standard library and never imports PyZX or
ORION production code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent
IDENTITY = "orion-01-production-completeness-v1-2026-08-29"
CURRENT_TERMINAL = "PROTOCOL_FROZEN__NO_OUTCOME"
OLD_TERMINAL = "CANNOT_CHECK_MOVE_COMPLETENESS"
SOURCE_PREFIX = "dade7d46"

REQUIRED_FILES = (
    "README.md",
    "QUESTION.md",
    "PROTOCOL.json",
    "CORPUS_MANIFEST.json",
    "SOURCE_COMPLETE_MOVE_GRAMMAR.json",
    "REGISTRY_COMPLETENESS_THEOREM.md",
    "EXPECTED_TERMINALS.json",
    "ADVERSE_AND_CANNOT_CHECK.jsonl",
    "CLAIM_DISPOSITION.md",
    "registry_protocol_checker.py",
)

PREEXECUTION_FORBIDDEN_FILES = (
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


def load_object(name: str) -> dict[str, Any]:
    value = json.loads((ROOT / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{name} must contain a JSON object")
    return value


def sha256_file(name: str) -> str:
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings(item)


def protocol_terminal_references(protocol: dict[str, Any]) -> set[str]:
    references = {protocol["current_terminal"]}
    references.update(protocol["source_resolution"]["required_match_count"] * [])
    references.update(protocol["ordered_phases"][0]["failure_terminals"])

    for phase in protocol["ordered_phases"]:
        for key in (
            "entry",
            "success_terminal",
            "failure_terminal",
            "permitted_positive_terminal",
            "permitted_null_terminal",
            "permitted_adverse_terminal",
        ):
            value = phase.get(key)
            if isinstance(value, str):
                references.add(value)
        for key in ("requires", "failure_terminals"):
            value = phase.get(key, [])
            require(isinstance(value, list), f"phase field {key} must be a list")
            references.update(item for item in value if isinstance(item, str))

    source_failures = {
        "SOURCE_PREFIX_UNRESOLVED",
        "SOURCE_PREFIX_AMBIGUOUS",
        "SOURCE_OBJECT_NOT_COMMIT",
        "CANNOT_RESOLVE_SOURCE",
    }
    references.update(source_failures)
    return references


def check_required_files() -> dict[str, Any]:
    missing = [name for name in REQUIRED_FILES if not (ROOT / name).is_file()]
    require(not missing, "missing protocol files: " + ", ".join(missing))
    return {
        "name": "required_protocol_files",
        "status": "PASS",
        "files": len(REQUIRED_FILES),
    }


def check_no_outcome_leakage() -> dict[str, Any]:
    present = [name for name in PREEXECUTION_FORBIDDEN_FILES if (ROOT / name).exists()]
    require(
        not present,
        "pre-execution identity contains forbidden result artifacts: "
        + ", ".join(present),
    )
    return {
        "name": "preexecution_outcome_leakage",
        "status": "PASS",
        "forbidden_files_absent": len(PREEXECUTION_FORBIDDEN_FILES),
    }


def check_protocol_identity(protocol: dict[str, Any]) -> dict[str, Any]:
    require(protocol["schema"] == "ORION.ORION01.ProductionCompletenessProtocol.v1", "unexpected protocol schema")
    require(protocol["protocol_identity"] == IDENTITY, "protocol identity mismatch")
    require(protocol["current_terminal"] == CURRENT_TERMINAL, "protocol is not outcome-free")
    require(protocol["source_resolution"]["commit_prefix"] == SOURCE_PREFIX, "source prefix mismatch")
    require(protocol["source_resolution"]["required_match_count"] == 1, "source match count is not uniquely frozen")
    require(protocol["source_resolution"]["required_full_object_name_length"] == 40, "full commit length is not 40")
    require(protocol["source_resolution"]["floating_ref_permitted"] is False, "floating source ref is permitted")
    require(protocol["source_resolution"]["semantic_testing_before_resolution_permitted"] is False, "semantic testing may precede source resolution")

    old = protocol["old_execution"]
    require(old["pull_request"] == 1602, "old PR binding changed")
    require(old["terminal"] == OLD_TERMINAL, "old adverse terminal changed")
    require(old["all_eight_tasks_hit_cap"] is True, "old cap-eight fact changed")
    require(old["role"] == "DERIVATION_AND_ADVERSE_EVIDENCE_ONLY", "old run gained successor authority")
    require(old["may_be_reinterpreted_as_positive"] is False, "old run may be reinterpreted")
    require(old["may_be_extended_under_same_identity"] is False, "old cap may be extended under same identity")

    phases = protocol["ordered_phases"]
    require([phase["phase"] for phase in phases] == list(range(6)), "protocol phases are not exactly 0 through 5")
    require(phases[0]["entry"] == CURRENT_TERMINAL, "phase 0 entry mismatch")
    require(phases[4]["requires"] == ["REGISTRY_COMPLETE"], "exact-compute protocol is not gated by REGISTRY_COMPLETE")
    require(phases[4]["fresh_identity_required"] is True, "phase 4 does not require a fresh identity")
    require(phases[4]["fresh_budget_required"] is True, "phase 4 does not require a fresh budget")
    require(phases[4]["outcome_blind_freeze_required"] is True, "phase 4 is not outcome-blind")

    gate = protocol["pre_result_gate"]
    require(gate["old_round3_artifacts_may_satisfy_gate"] is False, "old artifacts may satisfy the new gate")
    require("EXACT_COMPUTE_RESULT.json" in gate["forbidden_before_registry_terminal"], "exact result is not registry-gated")

    authority = protocol["authority"]
    require(all(authority[key] is False for key in ("external_peer_review", "external_replication", "submission_authority")), "protocol overstates external authority")
    require(authority["scientific_authority_delta_at_freeze"] == "NONE", "protocol freeze claims a scientific outcome")
    return {
        "name": "protocol_identity_and_gates",
        "status": "PASS",
        "phases": len(phases),
    }


def check_corpus_and_grammar(corpus: dict[str, Any], grammar: dict[str, Any]) -> dict[str, Any]:
    require(corpus["protocol_identity"] == IDENTITY, "corpus identity mismatch")
    require(grammar["protocol_identity"] == IDENTITY, "grammar identity mismatch")
    require(corpus["upstream"]["commit_prefix"] == SOURCE_PREFIX, "corpus prefix mismatch")
    require(corpus["upstream"]["required_unique_full_commit"] is True, "corpus does not require unique full commit")
    require(corpus["upstream"]["floating_ref_permitted"] is False, "corpus permits floating refs")
    require(corpus["current_state"]["full_commit"] is None, "source was populated before the frozen resolution receipt")
    require(corpus["current_state"]["semantic_testing_started"] is False, "semantic testing already started")
    require(corpus["current_state"]["terminal"] == CURRENT_TERMINAL, "corpus current terminal mismatch")

    require(grammar["status"] == "PROSPECTIVELY_FROZEN__INSTANCE_NOT_DISCHARGED", "grammar claims an instance outcome")
    require(grammar["current_instance"]["resolved_source_commit"] is None, "grammar contains a resolved source outcome")
    require(grammar["current_instance"]["registry_terminal"] is None, "grammar contains a registry outcome")
    require(grammar["current_instance"]["protocol_terminal"] == CURRENT_TERMINAL, "grammar current terminal mismatch")
    require(grammar["extensional_equivalence"]["small_random_agreement_sufficient"] is False, "random agreement can prove equivalence")
    require(grammar["distinguishing_basis"]["random_or_fuzz_only_sufficient"] is False, "fuzzing alone can prove separation")
    require(grammar["distinguishing_basis"]["bounded_size_only_sufficient_without_small_model_theorem"] is False, "bounded size alone can prove separation")
    require(grammar["completeness_ledger"]["unassigned_instance_permitted"] is False, "unassigned move instances are permitted")
    require(grammar["completeness_ledger"]["duplicate_assignment_permitted"] is False, "duplicate class assignment is permitted")
    return {
        "name": "corpus_and_extensional_grammar",
        "status": "PASS",
        "mutation_sink_kinds": len(grammar["mutation_root_discovery"]["mutation_sinks"]),
        "counterexample_types": len(grammar["counterexample_schema"]["permitted_types"]),
    }


def check_terminal_system(protocol: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    require(expected["protocol_identity"] == IDENTITY, "terminal identity mismatch")
    require(expected["terminal_set_frozen_before_execution"] is True, "terminal set was not prospectively frozen")
    require(expected["current_terminal"] == CURRENT_TERMINAL, "terminal file current state mismatch")

    rows = expected["terminals"]
    names = [row["terminal"] for row in rows]
    require(len(names) == len(set(names)), "duplicate terminal names")
    terminal_set = set(names)
    require(CURRENT_TERMINAL in terminal_set, "current terminal is undeclared")
    require(OLD_TERMINAL not in terminal_set, "old terminal was promoted into the successor terminal set")

    forbidden = set(expected["forbidden_as_successor_terminal"])
    require(OLD_TERMINAL in forbidden, "old terminal is not explicitly forbidden")
    require(not terminal_set.intersection(forbidden), "forbidden terminal appears as a successor terminal")

    references = protocol_terminal_references(protocol)
    missing = sorted(references - terminal_set)
    require(not missing, "protocol references undeclared terminals: " + ", ".join(missing))

    for transition in expected["transition_rules"]:
        require(transition["from"] in terminal_set, "transition source is undeclared")
        require(set(transition["to_any_of"]).issubset(terminal_set), "transition target is undeclared")

    require(any(row["terminal"] == "REGISTRY_COMPLETE" and row["class"] == "PRIMARY_SUCCESS" for row in rows), "registry success terminal is missing")
    require(any(row["terminal"] == "REGISTRY_INCOMPLETE_COUNTEREXAMPLE" and row["class"] == "PRIMARY_ADVERSE" for row in rows), "registry counterexample terminal is missing")
    require(any(row["terminal"] == "NO_MATERIAL_CONSEQUENCE_WITHIN_FROZEN_DOMAIN" and row["class"] == "PRIMARY_NULL" for row in rows), "material null terminal is missing")
    return {
        "name": "terminal_set_and_transitions",
        "status": "PASS",
        "terminals": len(terminal_set),
        "protocol_references": len(references),
    }


def check_theorem_and_claim_text() -> dict[str, Any]:
    theorem = (ROOT / "REGISTRY_COMPLETENESS_THEOREM.md").read_text(encoding="utf-8")
    claim = (ROOT / "CLAIM_DISPOSITION.md").read_text(encoding="utf-8")
    question = (ROOT / "QUESTION.md").read_text(encoding="utf-8")
    for obligation in ("O1", "O2", "O3", "O4", "O5", "O6"):
        require(obligation in theorem, f"theorem omits {obligation}")
    for marker in (
        CURRENT_TERMINAL,
        "source instance obligations open",
        "REGISTRY_INCOMPLETE_COUNTEREXAMPLE",
        "quotient preservation",
    ):
        require(marker.lower() in theorem.lower(), f"theorem omits marker: {marker}")
    require(CURRENT_TERMINAL in claim, "claim disposition does not preserve no-outcome terminal")
    require("Conditional theorem proved; source instance open" in claim, "claim disposition obscures conditional status")
    require("A larger enumeration is not itself a contribution" in question, "question permits cap-only promotion")
    require("The old terminal `CANNOT_CHECK_MOVE_COMPLETENESS` can be upgraded retrospectively" in question, "question omits old-terminal exclusion")
    return {
        "name": "theorem_and_claim_boundaries",
        "status": "PASS",
        "obligations": 6,
    }


def check_adverse_ledger() -> dict[str, Any]:
    rows = []
    for line_number, line in enumerate((ROOT / "ADVERSE_AND_CANNOT_CHECK.jsonl").read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        require(isinstance(value, dict), f"adverse row {line_number} is not an object")
        rows.append(value)
    require(len(rows) == 2, "adverse ledger must contain exactly Round 2 and Round 3 rows")
    require({row["round"] for row in rows} == {2, 3}, "adverse ledger rounds mismatch")
    for row in rows:
        require(row["protocol_identity"] == IDENTITY, "adverse identity mismatch")
        require(row["terminal"] == OLD_TERMINAL, "adverse terminal changed")
        require(row["successor_role"] == "DERIVATION_AND_ADVERSE_EVIDENCE_ONLY", "old evidence gained successor authority")
        require(row["may_discharge_source_resolution"] is False, "old evidence may discharge source resolution")
        require(row["may_discharge_registry_completeness"] is False, "old evidence may discharge registry completeness")
        require(row["may_authorize_old_cap_increase"] is False, "old evidence may authorize cap increase")
    round3 = next(row for row in rows if row["round"] == 3)
    require(round3["task_indices"] == list(range(8)), "Round 3 task indices changed")
    require(round3["all_tasks_hit_frozen_cap"] is True, "Round 3 cap-eight fact changed")
    require(round3["aggregate_sha256"] == "7e26974b9afab27abb88a27b7c2c5ba058e6d351f0d2f8428c4fa8e50acada31", "Round 3 aggregate hash changed")
    return {
        "name": "adverse_and_cannot_check_ledger",
        "status": "PASS",
        "rows": len(rows),
    }


def run_checks() -> dict[str, Any]:
    protocol = load_object("PROTOCOL.json")
    corpus = load_object("CORPUS_MANIFEST.json")
    grammar = load_object("SOURCE_COMPLETE_MOVE_GRAMMAR.json")
    expected = load_object("EXPECTED_TERMINALS.json")

    checks = [
        check_required_files(),
        check_no_outcome_leakage(),
        check_protocol_identity(protocol),
        check_corpus_and_grammar(corpus, grammar),
        check_terminal_system(protocol, expected),
        check_theorem_and_claim_text(),
        check_adverse_ledger(),
    ]
    require(all(check["status"] == "PASS" for check in checks), "not all checks passed")

    hashed_inputs = {
        name: sha256_file(name)
        for name in REQUIRED_FILES
        if name != "registry_protocol_checker.py"
    }
    return {
        "schema": "ORION.ORION01.RegistryProtocolCheck.v1",
        "protocol_identity": IDENTITY,
        "implementation_independent": True,
        "imports_orion": False,
        "imports_pyzx": False,
        "source_instance_executed": False,
        "checks": checks,
        "input_sha256": hashed_inputs,
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
