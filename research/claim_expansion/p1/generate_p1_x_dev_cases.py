from __future__ import annotations

import hashlib
import json
import sys
from collections.abc import Iterable
from typing import Any

DEV_AUTHORITY = "NON_AUTHORIZING_DEV"
GENERATOR_ID = "P1_X_DEV_GENERATOR_V1"

DOMAINS: dict[str, dict[str, str]] = {
    "SOFTWARE_DEBUGGING": {
        "local": "EXECUTION_ENVIRONMENT_REVISION",
        "high": "METHOD_BASIS_REVISION",
        "alt": "QUESTION_OBJECTIVE_REVISION",
        "external": "EVALUATOR_AUTHORITY_REVISION",
    },
    "SCIENTIFIC_RETRIEVAL": {
        "local": "EVIDENCE_REVISION",
        "high": "QUESTION_OBJECTIVE_REVISION",
        "alt": "METHOD_BASIS_REVISION",
        "external": "EXECUTION_ENVIRONMENT_REVISION",
    },
    "SEMANTIC_INTEGRATION": {
        "local": "MODEL_SELECTION_REVISION",
        "high": "REPRESENTATION_REGIME_REVISION",
        "alt": "EVIDENCE_REVISION",
        "external": "EVALUATOR_AUTHORITY_REVISION",
    },
    "EVIDENCE_VERIFICATION": {
        "local": "EVIDENCE_REVISION",
        "high": "METHOD_BASIS_REVISION",
        "alt": "EVALUATOR_AUTHORITY_REVISION",
        "external": "EVALUATOR_AUTHORITY_REVISION",
    },
    "MODEL_EXPERIMENT_DESIGN": {
        "local": "PARAMETER_REVISION",
        "high": "MODEL_CLASS_EXPANSION",
        "alt": "EXPERIMENT_MEASUREMENT_REVISION",
        "external": "EXPERIMENT_MEASUREMENT_REVISION",
    },
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

EPISTEMIC_HIGH_LEVEL = {
    "MODEL_CLASS_EXPANSION",
    "REPRESENTATION_REGIME_REVISION",
    "QUESTION_OBJECTIVE_REVISION",
    "METHOD_BASIS_REVISION",
}


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _revision_id(case_id: str, candidate_class: str) -> str:
    return f"{case_id}:{candidate_class}"


def _default_scope(case_id: str, candidate_class: str) -> list[str]:
    if candidate_class in EPISTEMIC_HIGH_LEVEL:
        return [f"{case_id}:root", f"{case_id}:dependent"]
    return []


def build_dev_case(domain: str, archetype: str, variant: int) -> dict[str, Any]:
    if domain not in DOMAINS:
        raise ValueError(f"unknown domain: {domain}")
    if archetype not in ARCHETYPES:
        raise ValueError(f"unknown archetype: {archetype}")
    if variant not in range(1, 6):
        raise ValueError(f"dev variant must be 1..5: {variant}")

    mapping = DOMAINS[domain]
    local = mapping["local"]
    high = mapping["high"]
    alt = mapping["alt"]
    external = mapping["external"]
    revision_classes = _unique((local, high, alt, external))

    case_id = f"P1X-DEV-{domain}-{archetype}-V{variant:02d}"
    root = f"{case_id}:root"
    dependent = f"{case_id}:dependent"
    unrelated = f"{case_id}:unrelated"
    sibling = f"{case_id}:sibling"
    exact_high_scope = [root, dependent]

    invasiveness_edges: list[list[str]] = []
    if local != high:
        invasiveness_edges.append([local, high])
    if alt not in {local, high}:
        invasiveness_edges.append([alt, high])

    proposals = []
    for candidate_class in revision_classes:
        proposed_scope = _default_scope(case_id, candidate_class)
        if archetype == "REOPEN_SCOPE_MISMATCH" and candidate_class == high:
            proposed_scope = [root] if variant % 2 else [root, dependent, unrelated]
        proposals.append(
            {
                "revision_id": _revision_id(case_id, candidate_class),
                "candidate_class": candidate_class,
                "proposed_reopen_set": proposed_scope,
                "declared_protected_invariants": [sibling],
            }
        )

    evaluations = {
        candidate_class: {
            "revision_id": _revision_id(case_id, candidate_class),
            "candidate_class": candidate_class,
            "restores_target": False,
            "preserves_invariants": True,
            "observed_reopen_set": _default_scope(case_id, candidate_class),
            "authorized": True,
        }
        for candidate_class in revision_classes
    }

    alternatives: list[dict[str, str]] = []

    def add_alternative(candidate_class: str, status: str) -> None:
        alternatives.append(
            {
                "revision_id": _revision_id(case_id, candidate_class),
                "candidate_class": candidate_class,
                "counterfactual_test_id": f"{case_id}:cf:{candidate_class}",
                "candidate_visible_status": status,
            }
        )

    causal: list[str] = []
    best: list[str] = []
    justified: list[str] = []
    ambiguity = "UNIQUE_MINIMUM"
    terminal = "REPAIR_LOCAL"

    if archetype == "NARROW_REPAIR_SUFFICIENT":
        causal = [local]
        best = [local]
        justified = [local]
        add_alternative(local, "SUCCEEDED")
        add_alternative(high, "SUCCEEDED")
        evaluations[local]["restores_target"] = True
        evaluations[high]["restores_target"] = True

    elif archetype == "HIGH_LEVEL_REVISION_NECESSARY":
        causal = [high]
        best = [high]
        justified = [high]
        terminal = "REVISE_HIGH_LEVEL"
        add_alternative(local, "FAILED")
        add_alternative(high, "SUCCEEDED")
        evaluations[high]["restores_target"] = True

    elif archetype == "INCOMPARABLE_MINIMA":
        causal = _unique((local, alt))
        best = _unique((local, alt))
        justified = _unique((local, alt))
        ambiguity = "INCOMPARABLE_MINIMA"
        terminal = "REQUEST_DISCRIMINATOR"
        add_alternative(local, "CANNOT_CHECK")
        add_alternative(alt, "CANNOT_CHECK")
        evaluations[local]["restores_target"] = True
        evaluations[alt]["restores_target"] = True

    elif archetype == "DIAGNOSIS_NOT_PRESCRIPTION":
        causal = [high]
        best = [local]
        justified = [local]
        add_alternative(high, "SUCCEEDED")
        add_alternative(local, "SUCCEEDED")
        evaluations[high]["restores_target"] = True
        evaluations[local]["restores_target"] = True

    elif archetype == "EXTERNAL_EVALUATOR_MEASUREMENT_RESPONSIBILITY":
        causal = [external]
        best = [external]
        justified = [external]
        add_alternative(external, "SUCCEEDED")
        evaluations[external]["restores_target"] = True
        # This archetype must not force mutation of scientific content merely to improve a score.
        terminal = "REPAIR_LOCAL"

    elif archetype == "LOCAL_SUCCESS_PRESERVATION_FAILURE":
        causal = [high]
        best = [alt]
        justified = [alt]
        add_alternative(high, "SUCCEEDED")
        add_alternative(alt, "SUCCEEDED")
        evaluations[high]["restores_target"] = True
        evaluations[high]["preserves_invariants"] = False
        evaluations[alt]["restores_target"] = True
        terminal = "REVISE_HIGH_LEVEL" if alt in EPISTEMIC_HIGH_LEVEL else "REPAIR_LOCAL"

    elif archetype == "REOPEN_SCOPE_MISMATCH":
        causal = [high]
        best = [high]
        justified = [high]
        terminal = "REVISE_HIGH_LEVEL"
        add_alternative(local, "FAILED")
        add_alternative(high, "SUCCEEDED")
        evaluations[high]["restores_target"] = True
        evaluations[high]["observed_reopen_set"] = exact_high_scope

    elif archetype == "CLEAN_OR_INSUFFICIENT_EVIDENCE_CONTROL":
        for evaluation in evaluations.values():
            evaluation["authorized"] = False
        if variant % 2 == 0:
            ambiguity = "NO_REVISION_NEEDED"
            terminal = "NO_CHANGE"
            add_alternative(local, "UNTESTED")
        else:
            ambiguity = "INSUFFICIENT_EVIDENCE"
            terminal = "CANNOT_CHECK"
            add_alternative(local, "CANNOT_CHECK")
            add_alternative(high, "CANNOT_CHECK")

    if terminal == "REVISE_HIGH_LEVEL":
        exact_reopen_set = exact_high_scope
    else:
        exact_reopen_set = []

    unknowns = []
    if terminal in {"CANNOT_CHECK", "REQUEST_DISCRIMINATOR"}:
        unknowns = [f"{case_id}:missing_discriminator"]

    return {
        "case_id": case_id,
        "domain": domain,
        "archetype": archetype,
        "generator_id": GENERATOR_ID,
        "seed_commitment": _sha256(f"{case_id}:DEV_NON_AUTHORIZING"),
        "candidate_visible": {
            "anomaly": f"Development-only {archetype.lower()} anomaly in {domain.lower()}.",
            "trajectory": [f"{case_id}:observe", f"{case_id}:diagnose"],
            "evidence": [f"{case_id}:evidence:{variant}"],
            "unknown_or_unavailable": unknowns,
            "candidate_revisions": [
                _revision_id(case_id, candidate_class) for candidate_class in revision_classes
            ],
            "revision_proposals": proposals,
        },
        "protected_gold": {
            "causal_responsibility_set": causal,
            "best_intervention_set": best,
            "scientifically_justified_revision_set": justified,
            "revision_evaluations": list(evaluations.values()),
            "ambiguity_state": ambiguity,
            "correct_terminal": terminal,
            "exact_reopen_set": exact_reopen_set,
            "provenance_commitment": _sha256(f"{case_id}:GOLD:DEV_ONLY"),
        },
        "revision_classes": revision_classes,
        "invasiveness_edges": invasiveness_edges,
        "registered_narrower_alternatives": alternatives,
        "protected_invariants": [sibling],
        "dependency_edges": [[root, dependent]],
        "budget": {
            "max_interventions": 3,
            "max_tool_calls": 8,
            "notes": "development-only matched budget",
        },
    }


def generate_dev_cases() -> list[dict[str, Any]]:
    return [
        build_dev_case(domain, archetype, variant)
        for domain in DOMAINS
        for archetype in ARCHETYPES
        for variant in range(1, 6)
    ]


def generate_dev_bundle() -> dict[str, Any]:
    cases = generate_dev_cases()
    return {
        "schema_version": "P1_X_DEV_CASES_V1",
        "authority": DEV_AUTHORITY,
        "generator_id": GENERATOR_ID,
        "case_count": len(cases),
        "cases": cases,
    }


def main() -> int:
    json.dump(generate_dev_bundle(), sys.stdout, sort_keys=True, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
