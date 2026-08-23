"""Typed active authority for P10's unexecuted maximum-claim manuscript."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any

SCHEMA = "ORION.P10.ActiveClaimAuthority.v1"
ACTIVE_TERMINAL = "P10_PROSPECTIVE_PROTOCOL_ONLY"

REPO_ROOT = Path(__file__).resolve().parents[4]
PAPER = REPO_ROOT / "papers/paper-10-structured-problem-solving"
MANUSCRIPT = PAPER / "manuscript/main.tex"
HYPOTHESES = PAPER / "manuscript/sections/11-primary-hypotheses.tex"
STATUS = PAPER / "manuscript/sections/16-claim-ladder-and-status.tex"
PREDECESSOR_AUTHORITY = REPO_ROOT / "papers/orion-learning-machine/LOCAL_CLOSURE_AUTHORITY.json"
PROTOCOL = PAPER / "protocol/P10_H1_H6_PROTOCOL_FREEZE_V1.json"


def _binding(path: Path) -> dict[str, str]:
    return {
        "artifact": str(path.relative_to(REPO_ROOT)),
        "sha256": sha256(path.read_bytes()).hexdigest(),
    }


def build_active_claim_authority() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "paper_id": "P10",
        "active_terminal": ACTIVE_TERMINAL,
        "execution_authorized": False,
        "execution_blocker": "P10_FULL_FROZEN_DONOR_EVALUATOR_INPUTS_ABSENT",
        "lifecycle_state": "PROSPECTIVE_PROTOCOL_FROZEN_INPUTS_ABSENT",
        "scientific_result_state": "NO_P10_PROTECTED_RESULT",
        "active_empirical_claim": None,
        "promotion_allowed": False,
        "hypotheses": {
            hypothesis: "PROSPECTIVE_NOT_EXECUTED"
            for hypothesis in ("H1", "H2", "H3", "H4", "H5", "H6")
        },
        "evidence_bindings": {
            "manuscript": _binding(MANUSCRIPT),
            "hypotheses": _binding(HYPOTHESES),
            "claim_ladder_status": _binding(STATUS),
            "prospective_protocol": _binding(PROTOCOL),
            "shared_predecessor_authority": _binding(PREDECESSOR_AUTHORITY),
        },
        "predecessor_boundary": {
            "authority": "LOCAL_REPRODUCIBLE_CORE_ONLY",
            "use": "IMPLEMENTATION_AND_REPRODUCTION_INPUT_ONLY",
            "does_not_discharge": ["H1", "H2", "H3", "H4", "H5", "H6"],
        },
        "forbidden_states": [
            "CANNOT_CHECK_AS_HYPOTHESIS_OUTCOME",
            "FAIL_AS_HYPOTHESIS_OUTCOME",
            "P10_SUPERIORITY_SUPPORTED",
            "METHOD_SPACE_EXPANSION_SUPPORTED",
        ],
        "promotion_requirements": [
            "prospectively_frozen_p10_protocol",
            "native_verifier_backed_execution",
            "strong_donor_complete_comparators",
            "independently_witnessed_ocme_case",
            "protected_cross_domain_replication",
            "external_review_custody",
        ],
    }


__all__ = ["ACTIVE_TERMINAL", "SCHEMA", "build_active_claim_authority"]
