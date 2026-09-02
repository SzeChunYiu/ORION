#!/usr/bin/env python3
"""O3CS1: bounded exhaustive certificate for the ORION-03 rung-1 Construction B
(cap-to-seed simulation) on the paper's own frozen definition space.

Frozen by development/orion-03-cap-seed-simulation-2026-09-03/
O3CS1_PROTOCOL_V1.md BEFORE any registered-grid document pair was evaluated.

Target construction (FORMAL_SEPARATION_ATTEMPT_20260902.md, Step B, verbatim
semantics): every capped rule (A_r -> h_r, K_r) is simulated exactly by adding
a fresh seed claim c_r with sigma(c_r) = K_r and replacing the rule by
(A_r + {c_r} -> h_r, Lambda); c_r is never refuted; all other claims, seeds,
rules, and refutations are unchanged. The prose claims equality of the
Q-coordinates of the two least fixed points by simultaneous induction; this
study machine-checks the claim's conclusions (baseline regime, refutation-clamp
regime, retraction preservation) on every canonical document in the registered
bounded grid.

Imported frozen machinery only (no math copied):
- papers/orion-03-typed-merge-falsification/evidence_license_evaluator.py
  (validate_document, evaluate_document, least_fixed_point via
  evaluate_document; ValidationError)

Documentation-level authority only: no expressiveness claim, no ledger change,
no widening of the frozen V3 surface.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = REPO_ROOT / "papers" / "orion-03-typed-merge-falsification"
sys.path.insert(0, str(PAPER_DIR))

import evidence_license_evaluator as ev  # noqa: E402

LANE_DIR = REPO_ROOT / "development" / "orion-03-cap-seed-simulation-2026-09-03"
PROTOCOL_PATH = LANE_DIR / "O3CS1_PROTOCOL_V1.md"
SCHEMA_ID = "ORION.ORION03.CapSeedSimulationBoundedExhaustive.v1"

# Machinery pinned at registration (2026-09-03, origin/main 4f2a223ae).
EVALUATOR_RELATIVE_PATH = "papers/orion-03-typed-merge-falsification/evidence_license_evaluator.py"
EXPECTED_EVALUATOR_SHA256 = "82ecb77dcdbce97d3980152d5053a166227d6a0403d11f021a6f478108b1b86a"

FORBIDDEN_IMPORT_SUBSTRINGS: Tuple[str, ...] = (
    "numpy",
    "scipy",
    "pandas",
    "requests",
    "urllib",
    "socket",
    "http",
    "qiskit",
    "openfermion",
    "cirq",
    "pyscf",
)

# Registered grid: (L = |licenses|, n = |claims|, m = |rules|).
# Full cross product except the single registered corner cut (L=3, n=3, m=2),
# which projects to 58,094,592 canonical documents and exceeds the registered
# enumeration cap; the cut is registered in the protocol, not chosen at runtime.
GRID_CELLS: Tuple[Tuple[int, int, int], ...] = tuple(
    (L, n, m)
    for L in (1, 2, 3)
    for n in (1, 2, 3)
    for m in range(0, 3)
    if not (L == 3 and n == 3 and m == 2)
)

# Adversarial control cells (construction boundary probe: seed claim refuted).
CONTROL_CELLS: Tuple[Tuple[int, int, int], ...] = ((1, 2, 1), (2, 2, 1))

ENUMERATION_CAP = 4_000_000

TERMINAL_VERIFIED = "O3_CS1_CAP_SEED_SIMULATION_VERIFIED__BOUNDED_EXHAUSTIVE_ALL_QUESTIONS"
TERMINAL_REFUTED = "O3_CS1_SIMULATION_REFUTED__COUNTEREXAMPLE_RECORDED"
TERMINAL_CANNOT_CHECK = "O3_CS1_CANNOT_CHECK__GRID_OVER_ENUMERATION_CAP"

AUTHORITY = (
    "BOUNDED_DOCUMENTATION_LEVEL_CERTIFICATE_ONLY__NO_EXPRESSIVENESS_CLAIM"
    "_NO_LEDGER_CHANGE_NO_WIDENING_OF_FROZEN_V3_SURFACE"
)


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head_revision() -> str:
    completed = subprocess.run(
        ["/usr/bin/git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"git rev-parse failed: {completed.stderr.strip()}")
    return completed.stdout.strip()


def check_import_gate() -> Dict[str, Any]:
    """AST-inspect this driver's actual imports; reject instrument dependencies."""
    source = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    modules: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.append(node.module)
    offenders = sorted(
        module
        for module in modules
        for forbidden in FORBIDDEN_IMPORT_SUBSTRINGS
        if forbidden in module.lower()
    )
    if offenders:
        raise RuntimeError(f"anti-instrument import gate failed: {offenders}")
    return {
        "forbidden_substrings": list(FORBIDDEN_IMPORT_SUBSTRINGS),
        "found_imports": sorted(modules),
        "passed": True,
    }


def assert_evaluator_digest() -> Dict[str, Any]:
    observed = sha256_file(PAPER_DIR / "evidence_license_evaluator.py")
    if observed != EXPECTED_EVALUATOR_SHA256:
        raise RuntimeError(
            "frozen evaluator digest drift: "
            f"expected {EXPECTED_EVALUATOR_SHA256}, observed {observed}"
        )
    return {
        "module": EVALUATOR_RELATIVE_PATH,
        "sha256": observed,
        "digest_pinned_at_registration": True,
    }


def machinery_controls() -> Dict[str, Any]:
    """Controls that could have failed: the frozen contract must reject bad docs."""
    probes: Dict[str, bool] = {}
    duplicate_claims = {
        "version": "1.0",
        "licenses": ["l0"],
        "claims": [
            {"id": "q0", "seeds": ["l0"]},
            {"id": "q0", "seeds": []},
        ],
        "rules": [],
        "refutations": [],
    }
    try:
        ev.validate_document(duplicate_claims)
        probes["duplicate_claim_id_rejected"] = False
    except ev.ValidationError:
        probes["duplicate_claim_id_rejected"] = True
    unknown_head = {
        "version": "1.0",
        "licenses": ["l0"],
        "claims": [{"id": "q0", "seeds": []}],
        "rules": [{"id": "r0", "body": ["q0"], "head": "qX", "cap": []}],
        "refutations": [],
    }
    try:
        ev.validate_document(unknown_head)
        probes["unknown_rule_head_rejected"] = False
    except ev.ValidationError:
        probes["unknown_rule_head_rejected"] = True
    failed = [name for name, ok in probes.items() if not ok]
    if failed:
        raise RuntimeError(f"machinery control probes failed: {failed}")
    return probes


def rule_space(licenses: Sequence[str], claims: Sequence[str]) -> List[Tuple[Tuple[str, ...], str, Tuple[str, ...]]]:
    """All well-formed rules: nonempty body subset, head in claims, cap subset."""
    bodies = sorted(
        tuple(sorted(combo))
        for size in range(1, len(claims) + 1)
        for combo in itertools.combinations(claims, size)
    )
    caps = sorted(
        tuple(sorted(subset))
        for subset in itertools.chain.from_iterable(
            itertools.combinations(sorted(licenses), size)
            for size in range(0, len(licenses) + 1)
        )
    )
    return sorted(
        (body, head, cap) for body in bodies for head in claims for cap in caps
    )


def planned_documents(licenses: int, claims: int, rules: int) -> int:
    per_rule = (2**claims - 1) * claims * 2**licenses
    combos = 1 if rules == 0 else comb_with_replacement(per_rule, rules)
    return (2**licenses) ** claims * combos * 2**claims


def comb_with_replacement(n: int, k: int) -> int:
    numerator = 1
    for offset in range(k):
        numerator = numerator * (n + offset)
    denominator = 1
    for value in range(1, k + 1):
        denominator *= value
    return numerator // denominator


def enumerate_documents(
    licenses: Sequence[str], claims: Sequence[str], rules: int
) -> Iterator[Dict[str, Any]]:
    """Yield every canonical document for one grid cell, exactly once.

    Rule multisets are enumerated with combinations_with_replacement over the
    sorted rule space, so rule-order permutations are not revisited; rule ids
    are assigned in the canonical multiset order.
    """
    space = rule_space(licenses, claims)
    seed_choices = [
        sorted(subset)
        for subset in itertools.chain.from_iterable(
            itertools.combinations(sorted(licenses), size)
            for size in range(0, len(licenses) + 1)
        )
    ]
    refutation_sets = [
        sorted(subset)
        for subset in itertools.chain.from_iterable(
            itertools.combinations(list(claims), size)
            for size in range(0, len(claims) + 1)
        )
    ]
    for seed_map in itertools.product(seed_choices, repeat=len(claims)):
        claim_records = [
            {"id": claim, "seeds": list(seed_map[index])}
            for index, claim in enumerate(claims)
        ]
        for combo in itertools.combinations_with_replacement(space, rules):
            rule_records = [
                {
                    "id": f"r{k}",
                    "body": list(body),
                    "head": head,
                    "cap": list(cap),
                }
                for k, (body, head, cap) in enumerate(combo)
            ]
            for refuted in refutation_sets:
                yield {
                    "version": "1.0",
                    "licenses": sorted(licenses),
                    "claims": claim_records,
                    "rules": rule_records,
                    "refutations": list(refuted),
                }


def simulate(document: Mapping[str, Any], licenses: Sequence[str]) -> Dict[str, Any]:
    """Construction B, verbatim: one fresh unrefuted seed per capped rule.

    For each rule r = (A_r -> h_r, K_r): add fresh claim c_r with
    sigma(c_r) = K_r; replace the rule by (A_r + {c_r} -> h_r, Lambda).
    Original claims, seeds, other rules, and refutations unchanged
    (c_r never refuted).
    """
    claims = [dict(record) for record in document["claims"]]
    rules: List[Dict[str, Any]] = []
    for index, rule in enumerate(document["rules"]):
        seed_id = f"cs1_seed_r{index}"
        claims.append({"id": seed_id, "seeds": list(rule["cap"])})
        rules.append(
            {
                "id": rule["id"],
                "body": sorted(list(rule["body"]) + [seed_id]),
                "head": rule["head"],
                "cap": sorted(licenses),
            }
        )
    return {
        "version": "1.0",
        "licenses": sorted(licenses),
        "claims": claims,
        "rules": rules,
        "refutations": list(document["refutations"]),
    }


def simulate_refuted_seed(
    document: Mapping[str, Any], licenses: Sequence[str]
) -> Dict[str, Any]:
    """Adversarial control variant: Construction B but the FIRST seed claim is
    added to the refutation set (c_r in R), violating the construction's
    boundary condition. Registered probe only; no registered claim either way.
    """
    variant = simulate(document, licenses)
    if variant["rules"]:
        variant["refutations"] = sorted(
            list(variant["refutations"]) + ["cs1_seed_r0"]
        )
    return variant


def restrict_labels(
    labels: Mapping[str, Sequence[str]], claims: Sequence[str]
) -> Dict[str, List[str]]:
    return {claim: sorted(labels[claim]) for claim in sorted(claims)}


def restrict_retracted(
    retracted: Iterable[Mapping[str, str]], claims: Sequence[str]
) -> List[Dict[str, str]]:
    keep = set(claims)
    return [
        {"claim": entry["claim"], "license": entry["license"]}
        for entry in sorted(retracted, key=lambda e: (e["claim"], e["license"]))
        if entry["claim"] in keep
    ]


def compare_pair(
    original: Mapping[str, Any], simulated: Mapping[str, Any], claims: Sequence[str]
) -> Optional[str]:
    """Return the first failed question id, or None when all pass."""
    if restrict_labels(original["baseline_labels"], claims) != restrict_labels(
        simulated["baseline_labels"], claims
    ):
        return "rq1_baseline_q_coordinate_lfp_preservation"
    if restrict_labels(original["final_labels"], claims) != restrict_labels(
        simulated["final_labels"], claims
    ):
        return "rq2_final_refutation_regime_q_coordinate_lfp_preservation"
    if restrict_retracted(original["retracted"], claims) != restrict_retracted(
        simulated["retracted"], claims
    ):
        return "rq3_retracted_pairs_q_preservation"
    return None


def run_cell(cell: Tuple[int, int, int], collect_control: bool) -> Dict[str, Any]:
    L, n, m = cell
    licenses = [f"l{index}" for index in range(L)]
    claims = [f"q{index}" for index in range(n)]
    planned = planned_documents(L, n, m)
    actual = 0
    failures: List[Dict[str, Any]] = []
    control_breaks = 0
    control_holds = 0
    for document in enumerate_documents(licenses, claims, m):
        actual += 1
        simulated = simulate(document, licenses)
        original_eval = ev.evaluate_document(document)
        simulated_eval = ev.evaluate_document(simulated)
        failed = compare_pair(original_eval, simulated_eval, claims)
        if failed is not None:
            failures.append(
                {
                    "failed_question": failed,
                    "document": document,
                    "simulated_document": simulated,
                    "original_evaluation": original_eval,
                    "simulated_evaluation": simulated_eval,
                }
            )
            if len(failures) >= 1:
                break
        if collect_control:
            variant = simulate_refuted_seed(document, licenses)
            variant_eval = ev.evaluate_document(variant)
            variant_failed = compare_pair(original_eval, variant_eval, claims)
            if variant_failed is None:
                control_holds += 1
            else:
                control_breaks += 1
    drift = planned - actual
    # A failure stops the cell early (drift > 0 is then the recorded stop
    # position, not an enumeration defect). Without a failure the cell must
    # have been enumerated exhaustively.
    if drift != 0 and not failures:
        raise RuntimeError(
            f"enumeration drift in cell {cell}: planned {planned}, actual {actual}"
        )
    return {
        "cell": {"licenses": L, "claims": n, "rules": m},
        "planned_documents": planned,
        "actual_documents": actual,
        "enumeration_drift": drift,
        "failures": failures,
        "control": {"q_equality_breaks": control_breaks, "q_equality_holds": control_holds}
        if collect_control
        else None,
    }


def build_result() -> Dict[str, Any]:
    import_gate = check_import_gate()
    machinery = assert_evaluator_digest()
    controls = machinery_controls()

    planned_total = sum(planned_documents(L, n, m) for L, n, m in GRID_CELLS)
    if planned_total > ENUMERATION_CAP:
        # Registered honest terminal: the registered grid projects over the cap.
        result: Dict[str, Any] = {
            "schema": SCHEMA_ID,
            "study": "O3CS1",
            "base_revision": git_head_revision(),
            "protocol_sha256": sha256_file(PROTOCOL_PATH),
            "machinery": machinery,
            "import_gate": import_gate,
            "machinery_controls": controls,
            "registered_grid": [
                {
                    "licenses": L,
                    "claims": n,
                    "rules": m,
                    "planned_documents": planned_documents(L, n, m),
                }
                for L, n, m in GRID_CELLS
            ],
            "planned_total": planned_total,
            "enumeration_cap": ENUMERATION_CAP,
            "terminal": TERMINAL_CANNOT_CHECK,
            "authority": AUTHORITY,
            "authority_flags": {
                "novelty_authority": False,
                "physical_quantum_advantage_claim": False,
                "scientific_authority_delta": "NONE",
            },
        }
        result["result_digest"] = sha256_text(canonical(result))
        return result

    cell_reports = []
    actual_total = 0
    failure: Optional[Dict[str, Any]] = None
    control_totals = {"q_equality_breaks": 0, "q_equality_holds": 0}
    for cell in GRID_CELLS:
        report = run_cell(cell, collect_control=cell in CONTROL_CELLS)
        cell_reports.append({key: report[key] for key in ("cell", "planned_documents", "actual_documents", "enumeration_drift")})
        actual_total += report["actual_documents"]
        if report["control"] is not None:
            control_totals["q_equality_breaks"] += report["control"]["q_equality_breaks"]
            control_totals["q_equality_holds"] += report["control"]["q_equality_holds"]
        if report["failures"]:
            failure = report["failures"][0]
            failure["cell"] = report["cell"]
            break

    if actual_total > ENUMERATION_CAP:
        raise RuntimeError(
            f"enumeration cap breached at runtime: {actual_total} > {ENUMERATION_CAP}"
        )

    question_tallies = {
        question: {
            "documents_checked": actual_total,
            "documents_failed": 1
            if failure is not None and failure["failed_question"] == question
            else 0,
        }
        for question in (
            "rq1_baseline_q_coordinate_lfp_preservation",
            "rq2_final_refutation_regime_q_coordinate_lfp_preservation",
            "rq3_retracted_pairs_q_preservation",
        )
    }

    terminal = TERMINAL_VERIFIED if failure is None else TERMINAL_REFUTED

    result = {
        "schema": SCHEMA_ID,
        "study": "O3CS1",
        "base_revision": git_head_revision(),
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "machinery": machinery,
        "import_gate": import_gate,
        "machinery_controls": controls,
        "registered_grid": [
            {
                "licenses": L,
                "claims": n,
                "rules": m,
                "planned_documents": planned_documents(L, n, m),
            }
            for L, n, m in GRID_CELLS
        ],
        "enumeration": {
            "planned_total": planned_total,
            "actual_total": actual_total,
            "enumeration_cap": ENUMERATION_CAP,
            "cap_respected": actual_total <= ENUMERATION_CAP,
            "cells_reported_before_stop": len(cell_reports),
        },
        "questions": question_tallies,
        "adversarial_control_refuted_seed": {
            "cells": [{"licenses": L, "claims": n, "rules": m} for L, n, m in CONTROL_CELLS],
            "documents": control_totals["q_equality_breaks"] + control_totals["q_equality_holds"],
            **control_totals,
        },
        "terminal": terminal,
        "authority": AUTHORITY,
        "authority_flags": {
            "novelty_authority": False,
            "physical_quantum_advantage_claim": False,
            "scientific_authority_delta": "NONE",
        },
    }
    if failure is not None:
        result["counterexample"] = failure
    result["result_digest"] = sha256_text(canonical(result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=LANE_DIR / "O3CS1_RESULTS.json",
        help="canonical result JSON path",
    )
    args = parser.parse_args()
    result = build_result()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(payload, encoding="utf-8")
    print(f"O3CS1_TERMINAL={result['terminal']}")
    print(f"O3CS1_RESULT_JSON={args.output}")
    print(f"O3CS1_RESULT_DIGEST={result['result_digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
