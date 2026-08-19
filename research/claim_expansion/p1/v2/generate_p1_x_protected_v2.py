from __future__ import annotations

import hashlib
import json
import sys
from collections.abc import Iterable
from typing import Any

AUTHORITY = "PROTECTED_GOLD_V2__HARNESS_ONLY"
GENERATOR_ID = "P1_X_PROTECTED_GENERATOR_V2"
NAMESPACE = "P1_X_PROTECTED_V2_REPLICATION_2026-08-19"

DOMAINS: dict[str, dict[str, str]] = {
    "SOFTWARE_DEBUGGING": {"local": "EXECUTION_ENVIRONMENT_REVISION", "high": "METHOD_BASIS_REVISION", "alt": "QUESTION_OBJECTIVE_REVISION", "external": "EVALUATOR_AUTHORITY_REVISION"},
    "SCIENTIFIC_RETRIEVAL": {"local": "EVIDENCE_REVISION", "high": "QUESTION_OBJECTIVE_REVISION", "alt": "METHOD_BASIS_REVISION", "external": "EXECUTION_ENVIRONMENT_REVISION"},
    "SEMANTIC_INTEGRATION": {"local": "MODEL_SELECTION_REVISION", "high": "REPRESENTATION_REGIME_REVISION", "alt": "EVIDENCE_REVISION", "external": "EVALUATOR_AUTHORITY_REVISION"},
    "EVIDENCE_VERIFICATION": {"local": "EVIDENCE_REVISION", "high": "METHOD_BASIS_REVISION", "alt": "EVALUATOR_AUTHORITY_REVISION", "external": "EVALUATOR_AUTHORITY_REVISION"},
    "MODEL_EXPERIMENT_DESIGN": {"local": "PARAMETER_REVISION", "high": "MODEL_CLASS_EXPANSION", "alt": "REPRESENTATION_REGIME_REVISION", "external": "EXPERIMENT_MEASUREMENT_REVISION"},
}

ARCHETYPES = (
    "NARROW_REPAIR_SUFFICIENT",
    "HIGH_LEVEL_REVISION_NECESSARY",
    "INCOMPARABLE_MINIMA",
    "DIAGNOSIS_NOT_PRESCRIPTION",
    "EXTERNAL_EVALUATOR_MEASUREMENT_RESPONSIBILITY",
    "LOCAL_SUCCESS_PRESERVATION_FAILURE",
    "REOPEN_SCOPE_MISMATCH",
    "CLEAN_OR_INSUFFICIENT_EVIDENCE_CONTROL",
)

HIGH_LEVEL = {"MODEL_CLASS_EXPANSION", "REPRESENTATION_REGIME_REVISION", "QUESTION_OBJECTIVE_REVISION", "METHOD_BASIS_REVISION"}


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _revision_id(case_id: str, candidate_class: str) -> str:
    return f"{case_id}:{candidate_class}"


def _default_scope(case_id: str, candidate_class: str) -> list[str]:
    return [f"{case_id}:root", f"{case_id}:dependent"] if candidate_class in HIGH_LEVEL else []


def _terminal(candidate_class: str) -> str:
    return "REVISE_HIGH_LEVEL" if candidate_class in HIGH_LEVEL else "REPAIR_LOCAL"


def _seed_rotated(classes: list[str], seed: str) -> list[str]:
    if not classes:
        return []
    offset = int(seed[:8], 16) % len(classes)
    return classes[offset:] + classes[:offset]


def build_case(domain: str, archetype: str, replicate: int) -> dict[str, Any]:
    if domain not in DOMAINS or archetype not in ARCHETYPES or replicate not in range(1, 11):
        raise ValueError((domain, archetype, replicate))
    mapping = DOMAINS[domain]
    local, high, alt, external = mapping["local"], mapping["high"], mapping["alt"], mapping["external"]
    classes = _unique((local, high, alt, external))
    case_id = f"P1X-V2-PROTECTED-{domain}-{archetype}-R{replicate:02d}"
    seed = _sha256(f"{NAMESPACE}:{case_id}")
    root, dependent = f"{case_id}:root", f"{case_id}:dependent"
    unrelated, sibling = f"{case_id}:unrelated", f"{case_id}:sibling"
    exact_scope = [root, dependent]
    holdout = replicate >= 9

    edges: list[list[str]] = []
    if local != high:
        edges.append([local, high])
    if alt not in {local, high}:
        edges.append([alt, high])

    proposal_classes = _seed_rotated(list(classes), seed)
    proposals = []
    for candidate_class in proposal_classes:
        scope = _default_scope(case_id, candidate_class)
        if archetype == "REOPEN_SCOPE_MISMATCH" and candidate_class == high:
            scope = [root, dependent, unrelated] if int(seed[-1], 16) % 2 else [root]
        proposals.append({
            "revision_id": _revision_id(case_id, candidate_class),
            "candidate_class": candidate_class,
            "proposed_reopen_set": scope,
            "declared_protected_invariants": [sibling],
        })

    evaluations = {
        candidate_class: {
            "revision_id": _revision_id(case_id, candidate_class),
            "candidate_class": candidate_class,
            "restores_target": False,
            "preserves_invariants": True,
            "observed_reopen_set": _default_scope(case_id, candidate_class),
            "authorized": True,
        }
        for candidate_class in classes
    }
    alternatives: list[dict[str, str]] = []

    def add(candidate_class: str, status: str) -> None:
        alternatives.append({
            "revision_id": _revision_id(case_id, candidate_class),
            "candidate_class": candidate_class,
            "counterfactual_test_id": f"{case_id}:cf:{candidate_class}",
            "candidate_visible_status": status,
        })

    causal: list[str] = []
    best: list[str] = []
    justified: list[str] = []
    ambiguity = "UNIQUE_MINIMUM"
    terminal = "REPAIR_LOCAL"
    discriminator_status = "NOT_NEEDED"

    if archetype == "NARROW_REPAIR_SUFFICIENT":
        causal = best = justified = [local]
        terminal = _terminal(local)
        add(local, "SUCCEEDED"); add(high, "SUCCEEDED")
        evaluations[local]["restores_target"] = True; evaluations[high]["restores_target"] = True
    elif archetype == "HIGH_LEVEL_REVISION_NECESSARY":
        causal = best = justified = [high]
        terminal = _terminal(high)
        add(local, "FAILED"); add(high, "SUCCEEDED")
        evaluations[high]["restores_target"] = True
    elif archetype == "INCOMPARABLE_MINIMA":
        causal = best = justified = _unique((local, alt))
        ambiguity = "INCOMPARABLE_MINIMA"
        discriminator_status = "AVAILABLE" if int(seed[:2], 16) % 2 else "UNAVAILABLE"
        terminal = "REQUEST_DISCRIMINATOR" if discriminator_status == "AVAILABLE" else "UNRESOLVED"
        add(local, "CANNOT_CHECK"); add(alt, "CANNOT_CHECK")
        evaluations[local]["restores_target"] = True; evaluations[alt]["restores_target"] = True
    elif archetype == "DIAGNOSIS_NOT_PRESCRIPTION":
        causal = [high]; best = justified = [local]
        terminal = _terminal(local)
        add(high, "SUCCEEDED"); add(local, "SUCCEEDED")
        evaluations[high]["restores_target"] = True; evaluations[local]["restores_target"] = True
    elif archetype == "EXTERNAL_EVALUATOR_MEASUREMENT_RESPONSIBILITY":
        causal = best = justified = [external]
        terminal = _terminal(external)
        add(external, "SUCCEEDED"); evaluations[external]["restores_target"] = True
    elif archetype == "LOCAL_SUCCESS_PRESERVATION_FAILURE":
        causal = [high]; best = justified = [alt]
        terminal = _terminal(alt)
        add(high, "SUCCEEDED"); add(alt, "SUCCEEDED")
        evaluations[high]["restores_target"] = True; evaluations[high]["preserves_invariants"] = False
        evaluations[alt]["restores_target"] = True
    elif archetype == "REOPEN_SCOPE_MISMATCH":
        causal = best = justified = [high]
        terminal = _terminal(high)
        add(local, "FAILED"); add(high, "SUCCEEDED")
        evaluations[high]["restores_target"] = True; evaluations[high]["observed_reopen_set"] = exact_scope
    elif archetype == "CLEAN_OR_INSUFFICIENT_EVIDENCE_CONTROL":
        for evaluation in evaluations.values():
            evaluation["authorized"] = False
        if int(seed[-2:], 16) % 2:
            ambiguity = "NO_REVISION_NEEDED"; terminal = "NO_CHANGE"; add(local, "UNTESTED")
        else:
            ambiguity = "INSUFFICIENT_EVIDENCE"; terminal = "CANNOT_CHECK"
            add(local, "CANNOT_CHECK"); add(high, "CANNOT_CHECK")

    if holdout and archetype not in {"INCOMPARABLE_MINIMA", "EXTERNAL_EVALUATOR_MEASUREMENT_RESPONSIBILITY", "CLEAN_OR_INSUFFICIENT_EVIDENCE_CONTROL"} and external not in justified:
        if not any(item["candidate_class"] == external for item in alternatives):
            add(external, "SUCCEEDED")
        evaluations[external]["restores_target"] = True
        evaluations[external]["authorized"] = False

    exact_reopen = exact_scope if terminal == "REVISE_HIGH_LEVEL" else []
    unknown: list[str] = []
    if terminal == "CANNOT_CHECK":
        unknown = [f"{case_id}:missing_required_evidence"]
    elif terminal == "UNRESOLVED":
        unknown = [f"{case_id}:required_discriminator_unavailable"]

    return {
        "case_id": case_id,
        "domain": domain,
        "archetype": archetype,
        "generator_id": f"{GENERATOR_ID}:{'HOLDOUT' if holdout else 'STANDARD'}",
        "seed_commitment": seed,
        "candidate_visible": {
            "anomaly": f"V2 protected {archetype.lower()} anomaly in {domain.lower()}.",
            "trajectory": [f"{case_id}:observe", f"{case_id}:diagnose"],
            "evidence": [f"{case_id}:evidence:{seed[8:20]}"],
            "unknown_or_unavailable": unknown,
            "candidate_revisions": [_revision_id(case_id, c) for c in proposal_classes],
            "revision_proposals": proposals,
            "discriminator_status": discriminator_status,
        },
        "protected_gold": {
            "causal_responsibility_set": causal,
            "best_intervention_set": best,
            "scientifically_justified_revision_set": justified,
            "revision_evaluations": list(evaluations.values()),
            "ambiguity_state": ambiguity,
            "correct_terminal": terminal,
            "exact_reopen_set": exact_reopen,
            "provenance_commitment": _sha256(f"{seed}:PROTECTED_GOLD_V2"),
        },
        "revision_classes": classes,
        "invasiveness_edges": edges,
        "registered_narrower_alternatives": alternatives,
        "protected_invariants": [sibling],
        "dependency_edges": [[root, dependent]],
        "budget": {"max_interventions": 3, "max_tool_calls": 8, "notes": "V2 protected matched budget"},
    }


def generate_cases() -> list[dict[str, Any]]:
    return [build_case(domain, archetype, replicate) for domain in DOMAINS for archetype in ARCHETYPES for replicate in range(1, 11)]


def generate_bundle() -> dict[str, Any]:
    cases = generate_cases()
    return {"schema_version": "P1_X_PROTECTED_CASES_V2", "authority": AUTHORITY, "generator_id": GENERATOR_ID, "case_count": len(cases), "cases": cases}


def main() -> int:
    json.dump(generate_bundle(), sys.stdout, sort_keys=True, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
