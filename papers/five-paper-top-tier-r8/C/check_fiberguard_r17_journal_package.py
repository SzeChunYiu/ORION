#!/usr/bin/env python3
"""Fail-closed checker for the FiberGuard R17 journal synthesis."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "ORION.FiberGuard.JournalPackage.R17.v1"
TERMINAL = "C_INTERNAL_THEORY_AND_MANUSCRIPT_COMPLETE__EXTERNAL_JOURNAL_GATES_OPEN"
SOURCE_PARENT = "00cbeeec87027b3510e91d4ee0a68cca6ac3476c"

REQUIRED_CLAIMS = {
    "C.T1",
    "C.T2",
    "C.T3",
    "C.T4",
    "C.T5",
    "C.T6",
    "C.T7",
    "C.T8",
    "C.T9",
    "C.E1",
    "C.E2",
    "C.E3",
    "C.E4",
    "C.E5",
    "C.E6",
    "C.E7",
    "C.S1",
    "C.X1",
    "C.X2",
    "C.X3",
    "C.X4",
    "C.X5",
}

EXPECTED_FULL_HASHES = {
    "R11": "7c0778836101d5fe44b024e302c3fc0848faf5a994fc1e51b80831d82fd5e652",
    "R14": "2a31fd86f51df52190c646deea140d34536aa8c3e77edfb6ca8fb95c22ea6f07",
    "R15": "bf5605831990322dcdbb11862c310e53ea15401fe37fa6852cdace575163baaf",
    "R16": "ba44da6354a0d8934d09898042d554638f631232fc6e337bd1ace904dafcb60e",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(text: str, fragment: str, label: str) -> None:
    if fragment not in text:
        raise ValueError(f"missing {label}: {fragment!r}")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} is not a JSON object")
    return value


def audit(root: Path) -> dict[str, Any]:
    manuscript_path = root / "MANUSCRIPT_C_R17_FIBERGUARD.md"
    ledger_path = root / "CLAIM_LEDGER_C_R17.json"
    prior_path = root / "PRIOR_ART_MATRIX_C_R17.md"
    gate_path = root / "JOURNAL_GATE_C_R17.md"
    paths = (manuscript_path, ledger_path, prior_path, gate_path)
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(path)

    manuscript = manuscript_path.read_text(encoding="utf-8")
    prior = prior_path.read_text(encoding="utf-8")
    gate = gate_path.read_text(encoding="utf-8")
    ledger = load_json(ledger_path)

    if ledger.get("schema") != "ORION.FiberGuard.ClaimLedger.R17.v1":
        raise ValueError("unexpected claim-ledger schema")
    if ledger.get("source_parent") != SOURCE_PARENT:
        raise ValueError("claim ledger is not bound to the R16 evidence parent")
    if ledger.get("canonical_manuscript") != (
        "papers/five-paper-top-tier-r8/C/MANUSCRIPT_C_R17_FIBERGUARD.md"
    ):
        raise ValueError("canonical manuscript path mismatch")

    claims = ledger.get("claims")
    if not isinstance(claims, list):
        raise ValueError("claims must be a list")
    ids = [claim.get("id") for claim in claims]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate claim id")
    if set(ids) != REQUIRED_CLAIMS:
        raise ValueError(
            f"claim denominator mismatch: missing={sorted(REQUIRED_CLAIMS-set(ids))}, "
            f"extra={sorted(set(ids)-REQUIRED_CLAIMS)}"
        )
    by_id = {claim["id"]: claim for claim in claims}
    if by_id["C.X1"]["status"] != "REFUTED_BY_R16":
        raise ValueError("learned-selector superiority refutation was lost")
    if by_id["C.X2"]["status"] != "REFUTED_AS_AN_INFERENCE_BY_R14":
        raise ValueError("generalization refutation was lost")
    if by_id["C.E5"]["status"] != "TWO_OF_THREE_VERIFIED":
        raise ValueError("R15 adverse-domain denominator was changed")
    if by_id["C.X4"]["status"] != "OPEN" or by_id["C.X5"]["status"] != "OPEN":
        raise ValueError("external authority was silently closed")

    ceiling = ledger.get("authority_ceiling", {})
    if ceiling.get("journal_authority") is not False:
        raise ValueError("journal authority must remain false")
    if ceiling.get("external_replication") != "CANNOT_CHECK":
        raise ValueError("external replication must remain CANNOT_CHECK")
    if ceiling.get("top_tier_readiness") != (
        "INTERNAL_THEORY_AND_MANUSCRIPT_COMPLETE__EXTERNAL_GATES_OPEN"
    ):
        raise ValueError("top-tier readiness boundary drift")

    evidence = ledger.get("evidence_roots", {})
    for tranche, expected in EXPECTED_FULL_HASHES.items():
        observed = evidence.get(tranche, {}).get("full_result_sha256")
        if observed != expected:
            raise ValueError(f"{tranche} full-result hash mismatch: {observed} != {expected}")

    r14 = load_json(root / "FIBERGUARD_ASLIB_TRANSFER_R14_RESULTS_SUMMARY.json")
    r15 = load_json(root / "FIBERGUARD_MULTIDOMAIN_R15_RESULTS_SUMMARY.json")
    r16 = load_json(root / "FIBERGUARD_LEARNED_COMPARATOR_R16_RESULTS_SUMMARY.json")
    if r14["scientific_terminal"] != (
        "FROZEN_R14_ROBUST_TRANSFER_GATE_FAIL__MEAN_EXCESS_IMPROVES"
    ):
        raise ValueError("R14 adverse terminal drift")
    if r15["portfolio"]["scientific_terminal"] != (
        "C_MULTIDOMAIN_CATASTROPHE_TAIL_VALUE_TWO_OF_THREE"
    ):
        raise ValueError("R15 two-of-three terminal drift")
    if r15["portfolio"]["scenario_pass_count"] != 2:
        raise ValueError("R15 denominator drift")
    if r16["portfolio"]["terminal_histogram"] != {
        "C_LEARNED_AND_FIBERGUARD_MIXED_NO_DOMINANCE": 1,
        "C_RF_REGRESSION_DOMINATES_FIBERGUARD": 2,
    }:
        raise ValueError("R16 comparator terminal drift")

    required_manuscript = {
        "abstract hybrid thesis": "learned runtime models may provide the operational action map",
        "R14 adverse result": "R14 refutes strict robust transfer",
        "R15 denominator": "fails on both splits in MiniZinc/CSP",
        "R16 comparator loss": "random-forest regression dominates the exact robust cell action",
        "same-oracle baseline": "same statewise oracle baseline",
        "tail limitation": "not a distribution-free CVaR guarantee",
        "authority limitation": "does not claim external replication",
    }
    for label, fragment in required_manuscript.items():
        require(manuscript, fragment, label)

    required_prior = (
        "AutoFolio",
        "SUNNY-AS2",
        "Run2Survive",
        "Feature-Budgeted Random Forest",
        "FiberGuard does **not** claim as new",
    )
    for fragment in required_prior:
        require(prior, fragment, "prior-art boundary")

    required_gates = (
        "Independent theorem review",
        "Independent reproduction",
        "Strong comparator",
        "Domain split authority",
        "Novelty adjudication",
        "Manuscript audit",
        "may not be labeled submission-ready",
    )
    for fragment in required_gates:
        require(gate, fragment, "journal gate")

    return {
        "schema": SCHEMA,
        "terminal": TERMINAL,
        "source_parent": SOURCE_PARENT,
        "claim_count": len(claims),
        "theorem_claim_count": sum(claim["id"].startswith("C.T") for claim in claims),
        "empirical_claim_count": sum(claim["id"].startswith("C.E") for claim in claims),
        "refuted_or_open_boundary_count": sum(claim["id"].startswith("C.X") for claim in claims),
        "files": {
            str(path.relative_to(root)): {
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in paths
        },
        "preserved_terminals": {
            "R14": r14["scientific_terminal"],
            "R15": r15["portfolio"]["scientific_terminal"],
            "R16": r16["portfolio"]["terminal_histogram"],
        },
        "authority": ceiling,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.root)
    payload = canonical_json(result) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(TERMINAL, f"claims={result['claim_count']}", f"sha256={hashlib.sha256(payload.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
