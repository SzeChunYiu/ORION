from __future__ import annotations

import hashlib
from typing import Any

DOMAINS = (
    "LITERATURE_CLAIM",
    "COMPUTATIONAL_RESULT",
    "STATISTICAL_INFERENCE",
    "FORMAL_VERIFICATION",
    "MEASUREMENT_DATASET_CLAIM",
)
ARCHETYPES = (
    "CLEAN_AUTHORIZED",
    "WRONG_ARTIFACT_VERSION",
    "CLAIM_SCOPE_OVERREACH",
    "STALE_EPOCH",
    "PROVENANCE_DEPENDENCY_BROKEN",
    "EVALUATOR_CUSTODY_COMPROMISED",
    "CORRELATED_EVIDENCE_DOUBLE_COUNT",
    "ACTION_AUTHORIZED_SCIENTIFIC_PROMOTION_UNRESOLVED",
)
GENERATOR_ID = "P4_X_PROTECTED_GENERATOR_V1"


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def build_case(domain: str, archetype: str, variant: int) -> dict[str, Any]:
    if domain not in DOMAINS or archetype not in ARCHETYPES or variant not in range(1, 11):
        raise ValueError((domain, archetype, variant))
    case_id = f"P4X-PROT-{domain}-{archetype}-V{variant:02d}"
    x: dict[str, Any] = {
        "claim_supported": True,
        "provenance_valid": True,
        "checker_admissible": True,
        "evaluator_custody_valid": True,
        "artifact_version_match": True,
        "claim_scope_match": True,
        "epoch_fresh": True,
        "evidence_independence_valid": True,
        "scientific_obligation_resolved": True,
        "action_authorized": True,
        "soft_confidence": 0.98,
        "non_load_bearing_latency_sla_met": True,
    }
    terminal = "PROMOTE"
    if archetype == "WRONG_ARTIFACT_VERSION":
        x["artifact_version_match"] = False; terminal = "BLOCK"
    elif archetype == "CLAIM_SCOPE_OVERREACH":
        x["claim_scope_match"] = False; terminal = "BLOCK"
    elif archetype == "STALE_EPOCH":
        x["epoch_fresh"] = False; terminal = "CANNOT_CHECK"
    elif archetype == "PROVENANCE_DEPENDENCY_BROKEN":
        x["provenance_valid"] = False; terminal = "BLOCK"
    elif archetype == "EVALUATOR_CUSTODY_COMPROMISED":
        x["evaluator_custody_valid"] = False; terminal = "BLOCK"
    elif archetype == "CORRELATED_EVIDENCE_DOUBLE_COUNT":
        x["evidence_independence_valid"] = False; terminal = "CANNOT_CHECK"
    elif archetype == "ACTION_AUTHORIZED_SCIENTIFIC_PROMOTION_UNRESOLVED":
        x["scientific_obligation_resolved"] = False; terminal = "CANNOT_CHECK"
    if variant in (9, 10):
        x["non_load_bearing_latency_sla_met"] = False
    return {
        "case_id": case_id,
        "domain": domain,
        "archetype": archetype,
        "generator_id": GENERATOR_ID,
        "seed_commitment": _sha(f"{case_id}:P4X_PROTECTED_V1"),
        "candidate_visible": x,
        "protected_gold": {
            "task_terminal": terminal,
            "provenance_commitment": _sha(f"{case_id}:PROTECTED_GOLD:{terminal}"),
        },
    }


def generate_cases() -> list[dict[str, Any]]:
    return [build_case(d, a, v) for d in DOMAINS for a in ARCHETYPES for v in range(1, 11)]
