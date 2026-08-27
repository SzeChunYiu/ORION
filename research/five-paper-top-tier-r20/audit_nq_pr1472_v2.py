#!/usr/bin/env python3
"""Exact-subject, noncircular authority audit for NQ PR #1472.

Documentation may state conditional consequences such as D3=25.  Circularity is
reported only when executable replay inputs, pruning, denominators, or acceptance
rules depend on those consequences.  Numerical promotion otherwise requires the
complete registered denominators and externally checked proof objects.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any

TARGET_PR = 1472
MATRIX_DENOMINATOR = 98_622
CANDIDATE_DENOMINATOR = 230_983


def run(*args: str, cwd: Path) -> str:
    return subprocess.check_output(args, cwd=cwd, text=True).strip()


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def walk(value: Any, path: str = ""):
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}/{key}"
            yield child_path, child
            yield from walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}/{index}"
            yield child_path, child
            yield from walk(child, child_path)


def normalized(value: Any) -> str:
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    return str(value).strip().upper()


def affirmative(value: Any) -> bool:
    return value is True or normalized(value) in {
        "PASS",
        "TRUE",
        "VERIFIED",
        "ALL_VERIFIED",
        "COMPLETE",
        "SUCCESS",
        "GREEN",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    changed = run("git", "diff", "--name-only", f"{args.base}...{args.head}", cwd=args.repo).splitlines()
    nq_files = sorted(
        path
        for path in changed
        if "/NQ/" in path
        or "davenport" in path.lower()
        or "zero-sum" in path.lower()
        or "cr-b" in path.lower()
        or "cr_b" in path.lower()
    )

    receipts: list[dict[str, Any]] = []
    scalars: list[tuple[str, Any, str]] = []
    executable_circular_inputs: list[dict[str, str]] = []
    declared_assumption_dependencies: list[dict[str, Any]] = []
    parse_failures: list[dict[str, str]] = []

    outcome_pattern = re.compile(
        r"(?:D_?3\s*\(?C_?5\^?3\)?\s*=\s*25|D3_25|completion|factorization)",
        re.IGNORECASE,
    )
    executable_dependency = re.compile(
        r"(?:import|from|open|read_text|read_bytes|json\.load|load|include|source|cat)"
        r".{0,180}(?:D3_25|completion|factorization|invariant_kernel)",
        re.IGNORECASE | re.DOTALL,
    )
    acceptance_dependency = re.compile(
        r"(?:if|assert|require|accept|prun|filter|denominator|candidate)"
        r".{0,180}(?:D_?3.{0,30}25|D3_25|completion|factorization)",
        re.IGNORECASE | re.DOTALL,
    )

    for relative in nq_files:
        path = args.repo / relative
        if not path.is_file() or path.stat().st_size > 50_000_000:
            continue
        suffix = path.suffix.lower()
        text = path.read_text(errors="replace")
        if suffix in {".py", ".sh", ".yml", ".yaml", ".rs", ".jl", ".cpp", ".cc", ".c"}:
            for name, pattern in (
                ("executable_outcome_file_dependency", executable_dependency),
                ("executable_acceptance_dependency", acceptance_dependency),
            ):
                if pattern.search(text):
                    executable_circular_inputs.append({"path": relative, "pattern": name})
        if suffix != ".json":
            continue
        try:
            value = json.loads(text)
        except Exception as exc:
            parse_failures.append({"path": relative, "error": type(exc).__name__})
            continue
        hits: list[dict[str, Any]] = []
        for key_path, child in walk(value):
            key = key_path.rsplit("/", 1)[-1].lower()
            if not isinstance(child, (dict, list)) and key in {
                "full_census_executed",
                "independent_replay_authority",
                "scientific_authority",
                "matrix_count",
                "matrix_denominator",
                "candidate_count",
                "candidate_denominator",
                "external_proof_check",
                "external_proof_checker",
                "all_unsat_proofs_verified",
                "positive_witnesses_verified",
                "normalization_partition_verified",
                "terminal",
                "result_terminal",
                "authority_terminal",
                "d2",
                "d3",
                "d_2",
                "d_3",
            }:
                hits.append({"path": key_path, "value": child})
                scalars.append((key_path.lower(), child, relative))
            if key in {
                "assumption",
                "assumptions",
                "pruning_rule",
                "candidate_filter",
                "acceptance_rule",
                "replay_inputs",
                "proof_inputs",
                "denominator_rule",
            }:
                encoded = canonical(child)
                if outcome_pattern.search(encoded):
                    declared_assumption_dependencies.append(
                        {"path": relative, "json_path": key_path, "value": child}
                    )
        receipts.append(
            {
                "path": relative,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "hits": hits,
            }
        )

    def any_key(keys: set[str], predicate) -> bool:
        return any(
            any(path.endswith("/" + key) for key in keys) and predicate(value)
            for path, value, _ in scalars
        )

    full_census = any_key({"full_census_executed"}, affirmative)
    matrix_complete = any(
        any(path.endswith("/" + key) for key in {"matrix_count", "matrix_denominator"})
        and int(value) == MATRIX_DENOMINATOR
        for path, value, _ in scalars
        if isinstance(value, (int, float)) or str(value).isdigit()
    )
    candidate_complete = any(
        any(path.endswith("/" + key) for key in {"candidate_count", "candidate_denominator"})
        and int(value) == CANDIDATE_DENOMINATOR
        for path, value, _ in scalars
        if isinstance(value, (int, float)) or str(value).isdigit()
    )
    normalization = any_key({"normalization_partition_verified"}, affirmative)
    external_proofs = any_key(
        {"external_proof_check", "all_unsat_proofs_verified"}, affirmative
    )
    positive_witnesses = any_key({"positive_witnesses_verified"}, affirmative)
    typed_replay_pass = any(
        "terminal" in path
        and "PASS" in normalized(value)
        and ("NQ" in normalized(value) or "REPLAY" in normalized(value) or "CR_B" in normalized(value))
        for path, value, _ in scalars
    )
    circular = bool(executable_circular_inputs or declared_assumption_dependencies)
    pass_gate = all(
        [
            full_census,
            matrix_complete,
            candidate_complete,
            normalization,
            external_proofs,
            positive_witnesses,
            typed_replay_pass,
        ]
    ) and not circular

    result = {
        "schema": "ORION.NQ.PR1472ExactSubjectAudit.R20.v2",
        "target_pr": TARGET_PR,
        "base_sha": args.base,
        "head_sha": args.head,
        "changed_files": changed,
        "nq_changed_files": nq_files,
        "json_receipts": receipts,
        "parse_failures": parse_failures,
        "executable_circular_inputs": executable_circular_inputs,
        "declared_assumption_dependencies": declared_assumption_dependencies,
        "documentation_may_state_post_terminal_D3_25_consequences": True,
        "gates": {
            "full_census_executed_true": full_census,
            "matrix_denominator_98622_present": matrix_complete,
            "candidate_denominator_230983_present": candidate_complete,
            "normalization_partition_verified": normalization,
            "external_unsat_proofs_verified": external_proofs,
            "positive_witnesses_verified": positive_witnesses,
            "typed_NQ_replay_PASS_present": typed_replay_pass,
            "replay_inputs_independent_of_D3_25_consequences": not circular,
        },
        "terminal": (
            "NQ_PR1472_FULL_REPLAY_SUBJECT_PASS"
            if pass_gate
            else "NQ_PR1472_NOT_FULL_REPLAY_AUTHORITY"
        ),
        "authority": {
            "D2_D3_numerical_authority": pass_gate,
            "D4_authority": False,
            "conditional_structure_may_be_reported_post_terminal": True,
            "external_independence": False,
            "novelty": False,
            "journal_authority": False,
        },
    }
    payload = canonical(result) + "\n"
    args.output.write_text(payload)
    print(result["terminal"], hashlib.sha256(payload.encode()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
