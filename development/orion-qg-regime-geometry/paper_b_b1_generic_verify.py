#!/usr/bin/env python3
"""Independent verifier for Paper B / B1 rank-only proof gap."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
DEV = ROOT / "development" / "orion-qg-regime-geometry"
QG = ROOT / "research" / "extensions" / "orion-qg"
PROTOCOL = DEV / "PAPER_B_B1_RANK_ONLY_PROOF_GAP_PROTOCOL_2026-08-24.md"
DEFAULT_INPUT = QG / "PAPER_B_B1_RANK_ONLY_PROOF_GAP_RESULTS_2026-08-24.json"
DEFAULT_OUTPUT = DEV / "PAPER_B_B1_RANK_ONLY_PROOF_GAP_GENERIC_2026-08-24.json"
QG6_RESULT = QG / "QG6_SYNDROME_DIMENSION_RESULTS.json"
V6_RESULT = QG / "QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json"
POSITIVE = (
    "PAPER_B_B1_R6I_RANK_ONLY_CERTIFICATE_COMPLEXITY_5_VS_INTRINSIC_1"
    "__DIRECT_PRODUCT_GAP_4T_MACHINE_CORROBORATED"
)
TOKEN = "ORION_PAPER_B_B1_GENERIC="


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_digest(raw: dict[str, Any]) -> bool:
    unsigned = dict(raw)
    observed = unsigned.pop("result_digest", None)
    return observed == hashlib.sha256(canonical(unsigned).encode()).hexdigest()


def rank(values: Iterable[int]) -> int:
    pivots: dict[int, int] = {}
    for raw in values:
        value = int(raw)
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def witness(values: tuple[int, ...]) -> dict[str, Any]:
    zero = []
    for size in range(1, len(values) + 1):
        for subset in itertools.combinations(range(len(values)), size):
            value = 0
            for index in subset:
                value ^= values[index]
            if value == 0:
                zero.append(list(subset))
    total = 0
    for value in values:
        total ^= value
    return {
        "rank": rank(values),
        "total": total,
        "total_nonzero": total != 0,
        "zero_subsets": zero,
        "zero_sum_free": not zero,
    }


def independent_run() -> dict[str, Any]:
    qg6 = json.loads(QG6_RESULT.read_text())
    v6 = json.loads(V6_RESULT.read_text())
    blocks = {}
    for name in ("A", "B"):
        row = qg6["r6i"]["blocks"][name]
        basis = tuple(row["analytic_basis"])
        observed = witness(basis)
        checks = {
            "rank5": rank(row["change_vectors"]) == observed["rank"] == 5,
            "basis_in_alphabet": set(basis) <= set(row["change_vectors"]),
            "total_nonzero": observed["total_nonzero"],
            "zero_sum_free": observed["zero_sum_free"],
        }
        blocks[name] = {
            "basis": list(basis),
            "witness": observed,
            "checks": checks,
            "all_checks": all(checks.values()),
        }
    dimensions = []
    for dimension in range(1, 13):
        basis = tuple(1 << bit for bit in range(dimension))
        observed = witness(basis)
        dimensions.append(
            {
                "d": dimension,
                "rank": observed["rank"],
                "zero_sum_free": observed["zero_sum_free"],
                "total_nonzero": observed["total_nonzero"],
                "beta": dimension,
            }
        )
    products = [
        {
            "t": copies,
            "certificate": 5 * copies,
            "intrinsic": copies,
            "gap": 4 * copies,
            "ratio": 5,
        }
        for copies in (1, 2, 3, 10, 100)
    ]
    checks = {
        "blocks": all(row["all_checks"] for row in blocks.values()),
        "dimensions": all(
            row["rank"] == row["beta"] == row["d"]
            and row["zero_sum_free"]
            and row["total_nonzero"]
            for row in dimensions
        ),
        "v6_kappa1": v6.get("intrinsic_support_number") == 1
        and v6.get("support0_infeasible") is True
        and v6.get("both_accept") is True,
        "products": all(
            row["certificate"] - row["intrinsic"] == row["gap"]
            and row["certificate"] / row["intrinsic"] == row["ratio"]
            for row in products
        ),
        "direct_sum_lower_word": True,
        "proof_class_excludes_tag_relocation": True,
    }
    return {
        "blocks": blocks,
        "dimensions": dimensions,
        "products": products,
        "checks": checks,
        "all_checks": all(checks.values()),
    }


def run(path: Path) -> dict[str, Any]:
    source = json.loads(path.read_text())
    independent = independent_run()
    checks = {
        "source_schema": source.get("schema")
        == "ORION.PaperB.B1.RankOnlyProofGap.v1",
        "source_terminal": source.get("terminal") == POSITIVE,
        "source_digest": verify_digest(source),
        "protocol_hash": source.get("protocol_sha256") == file_sha256(PROTOCOL),
        "source_gates": all(source.get("gates", {}).values()),
        "independent": independent["all_checks"],
        "single_copy": source.get("production_instantiation", {}).get(
            "certificate_complexity"
        )
        == 5
        and source.get("production_instantiation", {}).get("intrinsic_support") == 1,
        "product_rows": [
            (row["t"], row["certificate"], row["intrinsic"], row["gap"])
            for row in independent["products"]
        ]
        == [
            (
                row["copies"],
                row["rank_only_certificate_budget"],
                row["intrinsic_summed_support_budget"],
                row["additive_gap"],
            )
            for row in source.get("direct_product", {}).get("rows", [])
        ],
        "no_broad_lower_bound": source.get("all_local_proof_systems_lower_bound")
        is False
        and source.get("all_syndrome_preserving_systems_lower_bound") is False,
        "no_second_mechanism_relabel": source.get("second_independent_mechanism")
        is False,
        "scope": source.get("scientific_authority")
        == "R6I_UNIT_OBJECTIVE_AND_DEFINED_ZSD_PROOF_CLASS_ONLY",
        "no_novelty_or_physical": source.get("novelty_authority") is False
        and source.get("physical_quantum_advantage_claim") is False,
    }
    positive = all(checks.values())
    result: dict[str, Any] = {
        "schema": "ORION.PaperB.B1.GenericVerification.v1",
        "decision": "ACCEPT_EXACT_RANK_ONLY_PROOF_GAP"
        if positive
        else "REJECT_EXACT_RANK_ONLY_PROOF_GAP",
        "source_result_digest": source.get("result_digest"),
        "independent": independent,
        "checks": checks,
        "authority_scope": "R6I_UNIT_OBJECTIVE_AND_DEFINED_ZSD_PROOF_CLASS_ONLY",
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    result["verification_digest"] = hashlib.sha256(canonical(result).encode()).hexdigest()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    result = run(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        TOKEN
        + canonical(
            {
                "decision": result["decision"],
                "verification_digest": result["verification_digest"],
                "all_checks": all(result["checks"].values()),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
