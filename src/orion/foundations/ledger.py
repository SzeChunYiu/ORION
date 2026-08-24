"""Machine-readable ownership and authority ledger for the local theorem tranche."""

from __future__ import annotations

from typing import Any, Sequence

from .theorems import TheoremResult

BASE_COMMIT = "eba4a67e8607cdef96a2bb038d685a9a5d548599"
BRANCH = "codex/orion-foundations-v2-local-derivations"

OWNER_MAP: dict[str, list[str]] = {
    "OSTC-T0": ["P14", "FOUNDATIONS"],
    "OSTC-T1": ["P1-P15"],
    "OSTC-T2": ["P3", "P4", "P6", "P8", "P13", "P15"],
    "OSTC-T3": ["P4", "P9", "P13"],
    "OSTC-T4": ["P6", "P8", "P15"],
    "OSTC-T5": ["P6", "P7", "P8"],
    "OSTC-T6": ["FOUNDATIONS"],
    "OSTC-T7": ["FOUNDATIONS"],
    "OSTC-T8": ["P1-P15"],
    "OSTC-T9": ["P3", "P4", "P6", "P8", "P13", "P15"],
    "OSTC-T10": ["P6", "P7", "P8", "P13", "P15"],
    "OSTC-T11": ["P6", "P8", "P13", "P15"],
    "OSTC-T12": ["P2", "P7"],
    "OSTC-T13": ["P3", "P6", "P7", "P13"],
    "OSTC-T14": ["P1", "P9", "P10", "P12"],
    "OSTC-T15": ["P10"],
    "OSTC-T16": ["P11"],
    "OSTC-T17": ["P12"],
    "OSTC-T18": ["P11", "P13"],
    "OSTC-T19": ["P5"],
    "OSTC-T20": ["P15"],
    "OSTC-T21": ["P1", "P5", "P14"],
    "OSTC-T22": ["P10", "P15"],
    "OSTC-T23": ["P1-P15"],
    "OSTC-GUARD-NO-ANSWER-LAUNDERING": ["P3", "P4", "P9", "P11", "P12"],
}

REMAINING_GATE: dict[str, str] = {
    "OSTC-T7": "proof-assistant normalization for a richer recursive workflow class",
    "OSTC-T8": "large countermodel mining and minimality in multiple domains",
    "OSTC-T12": "probabilistic coverage laws and real acquisition campaigns",
    "OSTC-T13": "large regime graphs, coherence laws, and naturalistic transport",
    "OSTC-T14": "real intervention-response campaigns across models and domains",
    "OSTC-T15": "native verifier-backed expansion with strong donor first refusal",
    "OSTC-T16": "prospective real phase diagrams with learned state construction",
    "OSTC-T17": "regret bounds and public stop/go execution under price and shift",
    "OSTC-T18": "external responsibility families and real safe-reuse studies",
    "OSTC-T19": "protected external adoption custody",
    "OSTC-T20": "production fault injection and cross-site custody evaluation",
    "OSTC-T21": "longitudinal governed evolution under external authority",
}


def build_theorem_ledger(
    results: Sequence[TheoremResult],
    receipt_core_sha256: str,
) -> dict[str, Any]:
    missing = sorted({result.theorem_id for result in results} - OWNER_MAP.keys())
    if missing:
        raise ValueError(f"theorem ownership missing for {missing}")
    return {
        "schema_version": "orion.foundations.theorem-ledger.v1",
        "issue": 1220,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "receipt_core_sha256": receipt_core_sha256,
        "p1_rr1_coordination": "UNTOUCHED",
        "entries": [
            {
                "theorem_id": result.theorem_id,
                "statement": result.statement,
                "owners": OWNER_MAP[result.theorem_id],
                "local_status": result.status,
                "local_proof_class": (
                    "CONSTRUCTIVE_FINITE_DERIVATION_AND_EXECUTABLE_CHECK"
                ),
                "authority_ceiling": "LOCAL_FINITE_DERIVATION_ONLY",
                "paper_authority_delta": "NONE",
                "remaining_gate": REMAINING_GATE.get(
                    result.theorem_id,
                    (
                        "independent proof-assistant reconstruction and prospective "
                        "cross-domain falsification"
                    ),
                ),
            }
            for result in results
        ],
    }
