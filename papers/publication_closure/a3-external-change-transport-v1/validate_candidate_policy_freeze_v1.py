#!/usr/bin/env python3
"""Validate the frozen A3 candidate policy identity without executing predictions.

Checks, in order:
1. the freeze document's schema, flags, parameter-freeness and custody claims;
2. every bound SHA-256 against the live bytes of the bound files;
3. the frozen executable's own hostile self-test;
4. parameter-freeness of the executable by AST inspection (no RNG, no env
   reads, no file or network access, no run-time-resolved numerics);
5. verbatim conformance of the candidate decision rule to the frozen transport
   law's rule_three_valued over every premise-status assignment, with a
   mutated-rule control proving the conformance test has teeth.

This validator never computes a prediction for a real cluster.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import ast
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FREEZE = HERE / "A3_CANDIDATE_POLICY_FREEZE_V1.json"
TRANSPORT_LAW = ROOT / "papers/orion-23-responsibility-carrying-state/transport-law-v1/check_transport_law.py"
STATUSES = ("UNCHANGED", "ENTAILED", "CONTRADICTED", "UNKNOWN")
FORBIDDEN_MODULE_IMPORTS = {"random", "numpy", "sklearn", "torch", "openai", "requests", "urllib"}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def check_freeze_document() -> dict[str, Any]:
    doc = json.loads(FREEZE.read_text(encoding="utf-8"))
    if doc.get("schema") != "ORION.A3.CandidatePolicyFreeze.v1":
        raise ValueError("freeze schema mismatch")
    if doc.get("artifact_class") != "FROZEN_BEFORE_PROTECTED_PREDICTIONS_AND_GOLD":
        raise ValueError("freeze artifact class mismatch")
    if doc.get("grants_scientific_authority") is not False:
        raise ValueError("freeze must not grant scientific authority")
    identity = doc.get("candidate_policy_identity", {})
    if identity.get("free_parameters") != []:
        raise ValueError("candidate policy must have zero free parameters")
    if identity.get("run_time_resolution") != "NONE":
        raise ValueError("candidate policy must resolve nothing at run time")
    if identity.get("terminal_alphabet") != ["REUSE", "REOPEN", "CANNOT_CHECK"]:
        raise ValueError("candidate terminal alphabet mismatch")
    flags = doc.get("flags", {})
    if any(value is not False for value in flags.values()):
        raise ValueError(f"freeze flags must all be false: {flags}")
    bindings = doc.get("scientific_lineage_bound_verbatim", {})
    if set(bindings) != {
        "transport_law_theory", "transport_law_checker", "transport_law_result",
        "execution_and_analysis_freeze", "noncandidate_baselines_module", "rocrate_normalization",
    }:
        raise ValueError("scientific lineage binding set mismatch")
    for name, binding in bindings.items():
        path = ROOT / binding["path"]
        if not path.is_file():
            raise ValueError(f"bound file missing: {binding['path']}")
        observed = sha256_file(path)
        if observed != binding["sha256"]:
            raise ValueError(f"bound file digest mismatch for {name}: {binding['path']}")
    executable = ROOT / identity["executable"]
    if not executable.is_file():
        raise ValueError("candidate executable missing")
    if sha256_file(executable) != identity["executable_sha256"]:
        raise ValueError("candidate executable digest mismatch")
    if doc.get("validator") != "papers/publication_closure/a3-external-change-transport-v1/validate_candidate_policy_freeze_v1.py":
        raise ValueError("freeze validator self-binding mismatch")
    return doc


def check_parameter_free(source: str) -> None:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in FORBIDDEN_MODULE_IMPORTS:
                    raise ValueError(f"forbidden import in candidate executable: {alias.name}")
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in FORBIDDEN_MODULE_IMPORTS:
                raise ValueError(f"forbidden import in candidate executable: {node.module}")
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "environ":
            raise ValueError("candidate executable reads environment variables")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"open", "eval", "exec", "input"}:
            raise ValueError(f"candidate executable calls {node.func.id}()")
        if isinstance(node, ast.Name) and node.id == "globals":
            raise ValueError("candidate executable touches globals()")


def check_transport_law_conformance(candidate: Any, law: Any) -> dict[str, Any]:
    checked = 0
    for k in (1, 2, 3, 4):
        for combo in itertools.product(STATUSES, repeat=k):
            statuses = [{"path": f"p{i}", "status": s} for i, s in enumerate(combo)]
            got = candidate.decide(statuses)
            want = law.rule_three_valued(combo)
            want = {"REVOKE": "REOPEN"}.get(want, want)
            if got != want:
                raise ValueError(f"candidate diverges from frozen transport law at {combo}: {got} != {want}")
            checked += 1

    def mutated(statuses: list[dict[str, Any]]) -> str:
        values = [row["status"] for row in statuses]
        if "UNKNOWN" in values:
            return "CANNOT_CHECK"
        if "CONTRADICTED" in values:
            return "REOPEN"
        return "REUSE"

    divergence = 0
    for k in (1, 2):
        for combo in itertools.product(STATUSES, repeat=k):
            statuses = [{"path": f"p{i}", "status": s} for i, s in enumerate(combo)]
            if mutated(statuses) != candidate.decide(statuses):
                divergence += 1
    if divergence == 0:
        raise ValueError("conformance control has no teeth: mutated rule was indistinguishable")
    return {"status_assignments_checked": checked, "mutant_rule_divergence_cases": divergence}


def self_test() -> dict[str, Any]:
    doc = check_freeze_document()
    candidate = load_module("a3_candidate_policy_v1", ROOT / doc["candidate_policy_identity"]["executable"])
    law = load_module("a3_transport_law_checker_v1", TRANSPORT_LAW)
    policy_result = candidate.self_test()
    if policy_result.get("decision") != "GREEN":
        raise ValueError("candidate policy self-test is not GREEN")
    check_parameter_free((ROOT / doc["candidate_policy_identity"]["executable"]).read_text(encoding="utf-8"))
    conformance = check_transport_law_conformance(candidate, law)
    forbidden = doc["candidate_visible_record_contract"]["forbidden_fields"]
    if not set(forbidden) <= set(candidate.FORBIDDEN_VISIBLE_FIELDS):
        raise ValueError("freeze visible-record contract weaker than the executable")
    return {
        "decision": "GREEN",
        "policy_id": doc["candidate_policy_identity"]["policy_id"],
        "executable_sha256": doc["candidate_policy_identity"]["executable_sha256"],
        "lineage_bindings_verified": len(doc["scientific_lineage_bound_verbatim"]),
        "policy_self_test": policy_result,
        "transport_law_conformance": conformance,
        "real_cluster_prediction_computed": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if not args.self_test:
        ap.error("this validator is self-test only; it never touches cluster data")
    result = self_test()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
