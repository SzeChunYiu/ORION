#!/usr/bin/env python3
"""Run the additive P6–P8 V2 assumption/benchmark regression suite.

This standard-library runner is intentionally supplementary to the larger V1
finite enumerators already present in the candidate-paper programme.  It binds
focused theorem-assumption countermodels and machine-readable P7/P8 benchmark
contracts to executable validators, unit tests, and content hashes.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Iterable, Mapping

ROOT = Path(__file__).resolve().parent
#: The paper packages were promoted out of papers/candidates/ into papers/;
#: this runner stays behind as shared cross-paper apparatus, so the suite
#: paths below resolve against the papers/ directory one level up.
PAPERS = ROOT.parent

SUITES: tuple[dict[str, str], ...] = (
    {
        "name": "P6",
        "checker": "orion-16-formal-epistemic-structures-and-mechanics/formal/check_assumption_regressions_v2.py",
        "tests": "orion-16-formal-epistemic-structures-and-mechanics/formal/test_assumption_regressions_v2.py",
        "cases": "orion-16-formal-epistemic-structures-and-mechanics/formal/assumption_countermodels_v2.jsonl",
        "validator": "validate_countermodel_case",
    },
    {
        "name": "P7",
        "checker": "orion-17-epistemic-navigation-open-worlds/formal/check_benchmark_contracts_v2.py",
        "tests": "orion-17-epistemic-navigation-open-worlds/formal/test_benchmark_contracts_v2.py",
        "cases": "orion-17-epistemic-navigation-open-worlds/benchmark/instances_v1.jsonl",
        "validator": "validate_benchmark_case",
    },
    {
        "name": "P8",
        "checker": "orion-18-epistemic-authority-autonomous-science/formal/check_benchmark_contracts_v2.py",
        "tests": "orion-18-epistemic-authority-autonomous-science/formal/test_benchmark_contracts_v2.py",
        "cases": "orion-18-epistemic-authority-autonomous-science/benchmark/authority_cases_v1.jsonl",
        "validator": "validate_authority_case",
    },
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_module(path: Path, logical_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(logical_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[logical_name] = module
    spec.loader.exec_module(module)
    return module


def run_unit_tests(test_path: Path) -> tuple[int, str]:
    completed = subprocess.run(
        [sys.executable, test_path.name],
        cwd=test_path.parent,
        check=False,
        capture_output=True,
        text=True,
    )
    combined = (completed.stdout + "\n" + completed.stderr).strip()
    match = re.search(r"Ran\s+(\d+)\s+tests?", combined)
    if completed.returncode != 0 or match is None:
        raise RuntimeError(f"unit tests failed for {test_path}:\n{combined}")
    return int(match.group(1)), combined


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            line = raw.strip()
            if not line:
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: expected JSON object")
            value["__line__"] = line_number
            cases.append(value)
    return cases


def validate_cases(
    path: Path,
    validator: Callable[[Mapping[str, object]], tuple[bool, str]],
) -> list[dict[str, Any]]:
    cases = read_jsonl(path)
    identifiers: set[str] = set()
    for case in cases:
        identifier = str(case.get("id", ""))
        if not identifier:
            raise ValueError(f"{path}:{case['__line__']}: missing non-empty id")
        if identifier in identifiers:
            raise ValueError(f"{path}:{case['__line__']}: duplicate id {identifier}")
        identifiers.add(identifier)
        clean_case = {key: value for key, value in case.items() if key != "__line__"}
        valid, reason = validator(clean_case)
        if not valid:
            raise ValueError(f"{path}:{case['__line__']} ({identifier}): {reason}")
    return cases


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def suite_level_contracts(name: str, cases: list[dict[str, Any]]) -> dict[str, Any]:
    if name == "P6":
        kinds = {str(case["kind"]) for case in cases}
        verdicts = Counter(str(case["expected_verdict"]) for case in cases)
        require(
            kinds
            == {
                "stale_certification",
                "undeclared_write",
                "nonseparated_composition",
                "authority_escalation",
                "recursive_cycle",
                "self_authorization",
            },
            f"P6 hostile kinds incomplete: {sorted(kinds)}",
        )
        require(verdicts["DETECTED"] > 0 and verdicts["NOT_DETECTED"] > 0, "P6 needs positive and negative controls")
        return {"kinds": sorted(kinds), "expected_verdicts": dict(sorted(verdicts.items()))}

    if name == "P7":
        families = {str(case["family"]) for case in cases}
        terminals = Counter(str(case["expected_terminal"]) for case in cases)
        required_families = {
            "hidden_useful_branch",
            "unknown_coverage",
            "censored_route",
            "deceptive_route_diversity",
            "dead_end_revisit",
            "topology_change",
            "unnecessary_reframe",
        }
        require(required_families.issubset(families), f"P7 benchmark families incomplete: {sorted(families)}")
        require(any(bool(case["negative_control"]) for case in cases), "P7 requires a harmful/unnecessary-reframe negative control")
        require(
            any(
                str(case["domain"]) != "retrieval"
                and bool(case.get("gold", {}).get("non_retrieval_transfer", False))
                for case in cases
            ),
            "P7 requires an explicit non-retrieval transfer case",
        )
        require(
            {"TASK_STOP", "ROUTE_STOP", "REFRAME", "CANNOT_CHECK"}.issubset(terminals),
            f"P7 terminal coverage incomplete: {sorted(terminals)}",
        )
        return {"families": sorted(families), "expected_terminals": dict(sorted(terminals.items()))}

    if name == "P8":
        domains = {str(case["domain"]) for case in cases}
        expected_domains = {"REFRAME", "SEARCH_STOP", "MAP_MERGE", "ASSERT", "SELF_MODIFY"}
        verdicts = Counter(str(case["expected_verdict"]) for case in cases)
        require(domains == expected_domains, f"P8 domain coverage incomplete: {sorted(domains)}")
        clean_domains = {
            str(case["domain"])
            for case in cases
            if bool(case["clean_authorized"])
            and str(case["source_signal_domain"]) == str(case["domain"])
        }
        require(clean_domains == expected_domains, "P8 deny-all control failed: every domain needs a clean same-domain authorization")
        standard_pairs = {"REFRAME-001", "SEARCH-001", "MAP-001", "ASSERT-001", "SELF-001"}
        for pair_id in standard_pairs:
            pair = [case for case in cases if str(case["pair_id"]) == pair_id]
            require(len(pair) == 2, f"P8 pair {pair_id} must contain exactly two cases")
            require(any(bool(case["clean_authorized"]) for case in pair), f"P8 pair {pair_id} lacks an authorized case")
            require(any(not bool(case["clean_authorized"]) for case in pair), f"P8 pair {pair_id} lacks a blocked case")
        require(
            {"AUTHORIZED", "REJECT", "UNAUTHORIZED", "CANNOT_CHECK"}.issubset(verdicts),
            f"P8 terminal coverage incomplete: {sorted(verdicts)}",
        )
        require(
            any(
                str(case["source_signal_domain"]) != str(case["domain"])
                and bool(case.get("registered_coercions"))
                and str(case["expected_verdict"]) == "AUTHORIZED"
                for case in cases
            ),
            "P8 requires a clean authorized cross-domain coercion control",
        )
        laundering_cases = [case for case in cases if str(case["id"]).startswith("P8-LAUNDER-")]
        require(len(laundering_cases) >= 5, "P8 requires at least five explicit laundering attacks")
        return {
            "domains": sorted(domains),
            "expected_verdicts": dict(sorted(verdicts.items())),
            "laundering_cases": len(laundering_cases),
        }

    raise ValueError(f"unknown suite {name}")


def build_receipt() -> dict[str, Any]:
    suite_results: dict[str, Any] = {}
    input_paths: list[Path] = [Path(__file__).resolve()]
    total_tests = 0
    total_checks = 0
    total_cases = 0

    for suite in SUITES:
        name = suite["name"]
        checker_path = PAPERS / suite["checker"]
        test_path = PAPERS / suite["tests"]
        cases_path = PAPERS / suite["cases"]
        input_paths.extend((checker_path, test_path, cases_path))

        module = load_module(checker_path, f"orion_{name.lower()}_v2_checker")
        unit_test_count, _ = run_unit_tests(test_path)
        raw_checks = module.run_checks()
        require(bool(raw_checks.get("all_passed")), f"{name} structural checks failed: {raw_checks}")
        named_checks = {key: value for key, value in raw_checks.items() if key != "all_passed"}
        require(all(value is True for value in named_checks.values()), f"{name} contains a non-true structural check")

        validator = getattr(module, suite["validator"])
        cases = validate_cases(cases_path, validator)
        coverage = suite_level_contracts(name, cases)

        suite_results[name] = {
            "unit_tests": unit_test_count,
            "named_structural_checks": len(named_checks),
            "machine_readable_cases": len(cases),
            "coverage": coverage,
            "status": "PASS",
        }
        total_tests += unit_test_count
        total_checks += len(named_checks)
        total_cases += len(cases)

    # Repo-relative keys: the inputs now straddle papers/ (the promoted paper
    # packages) and papers/candidates/ (this runner), so no single one of those
    # directories can anchor every hash entry.
    repo_root = ROOT.parent.parent
    file_hashes = {
        str(path.relative_to(repo_root)): sha256_file(path)
        for path in sorted(set(input_paths), key=lambda item: str(item.relative_to(repo_root)))
    }
    aggregate_material = "".join(f"{path}\0{digest}\n" for path, digest in sorted(file_hashes.items()))
    aggregate_hash = hashlib.sha256(aggregate_material.encode("utf-8")).hexdigest()

    return {
        "schema": "orion.p6_p8_assumption_regression_receipt.v2",
        "authority": "LOCAL_DETERMINISTIC_SUPPORT_ONLY",
        "environment": {
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
            "platform": platform.platform(),
        },
        "suites": suite_results,
        "totals": {
            "unit_tests": total_tests,
            "named_structural_checks": total_checks,
            "machine_readable_cases": total_cases,
        },
        "artifact_sha256": file_hashes,
        "artifact_set_sha256": aggregate_hash,
        "all_passed": True,
        "nonclaims": [
            "Finite checks do not prove unrestricted theorems.",
            "Reference-policy oracles do not establish live-agent efficacy.",
            "No result authorizes novelty, empirical superiority, flagship promotion, or peer-review readiness.",
        ],
    }


def render_markdown(receipt: Mapping[str, Any]) -> str:
    totals = receipt["totals"]
    lines = [
        "# P6–P8 assumption and benchmark regression results V2",
        "",
        "**Authority:** `LOCAL_DETERMINISTIC_SUPPORT_ONLY`  ",
        f"**Artifact-set SHA-256:** `{receipt['artifact_set_sha256']}`",
        "",
        "This focused additive suite complements the larger V1 finite enumerators. It executes theorem-assumption countermodels for P6 and outcome-bearing benchmark contracts for P7/P8. It uses only the Python standard library and makes no network, model, judge, or LLM API call.",
        "",
        "## Executed result",
        "",
        f"- unit tests: **{totals['unit_tests']}**;",
        f"- named structural checks: **{totals['named_structural_checks']}**;",
        f"- machine-readable hostile/negative-control cases: **{totals['machine_readable_cases']}**;",
        "- aggregate terminal: **PASS**.",
        "",
        "| Suite | Unit tests | Structural checks | Frozen cases | Terminal |",
        "|---|---:|---:|---:|---|",
    ]
    for name in ("P6", "P7", "P8"):
        row = receipt["suites"][name]
        lines.append(
            f"| {name} | {row['unit_tests']} | {row['named_structural_checks']} | {row['machine_readable_cases']} | `{row['status']}` |"
        )
    lines.extend(
        [
            "",
            "## What V2 adds",
            "",
            "- **P6:** positive and negative controls for path-realizable reopening minimality, declared write footprints, separation, authority escalation, recursive cycles, self-authorization, and history-aware commutation.",
            "- **P7:** eight frozen cases spanning hidden branches, unknown/censored coverage, deceptive route diversity, dead-end revisit, required and harmful topology change, and a non-retrieval experimental-design transfer case.",
            "- **P8:** paired clean/blocked cases across all five domains, five explicit laundering attacks, `CANNOT_CHECK`, and a clean authorized cross-domain coercion control so deny-all policies cannot pass.",
            "",
            "## Reproduction",
            "",
            "```bash",
            "python papers/candidates/run_assumption_regressions_v2.py \\",
            "  --json-output papers/candidates/ASSUMPTION_REGRESSION_RESULTS_V2.json \\",
            "  --markdown-output papers/candidates/ASSUMPTION_REGRESSION_RESULTS_V2.md",
            "```",
            "",
            "## Claim boundary",
            "",
        ]
    )
    for nonclaim in receipt["nonclaims"]:
        lines.append(f"- {nonclaim}")
    lines.append("")
    return "\n".join(lines)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)

    receipt = build_receipt()
    rendered_json = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    rendered_markdown = render_markdown(receipt)

    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(rendered_json, encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(rendered_markdown, encoding="utf-8")
    if not args.json_output and not args.markdown_output:
        sys.stdout.write(rendered_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
