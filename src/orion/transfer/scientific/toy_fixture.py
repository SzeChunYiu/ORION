"""Known-answer toy fixture for hostile refusal and mechanic ablation.

LOCAL_ENGINEERING_ONLY. These scores are not scientific transfer outcomes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from orion.transfer.scientific.objects import (
    SCHEMA_VERSION,
    ProblemSignatureV3,
    build_transfer_object,
    ScientificTransferObject,
)

TARGET_SIGNATURE = ProblemSignatureV3(
    signature_id="sig:retrieval-isolate",
    family_id="retrieval_stopping",
    surface_domain="scientific-retrieval-stopping",
    hidden_state="latent-responsible-component",
    observability="partial-probeable",
    actions=("probe", "abstain"),
    ground_truth_class="protected",
    dependence=0.6,
    authority_risk=0.8,
    nonstationarity=0.2,
    reversibility=0.9,
)


def _base_fields(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "object_id": "cell:active-discriminator:debugging",
        "problem_signature": {
            "signature_id": "sig:debug-isolate",
            "family_id": "debugging",
            "surface_domain": "software-failure-diagnosis",
            "hidden_state": "latent-responsible-component",
            "observability": "partial-probeable",
            "actions": ["probe", "abstain"],
            "ground_truth_class": "protected",
            "dependence": 0.6,
            "authority_risk": 0.8,
            "nonstationarity": 0.2,
            "reversibility": 0.9,
        },
        "io_contract": {
            "inputs": ["failure-report", "component-graph"],
            "outputs": ["responsibility-hypothesis"],
            "observables": ["probe-outcome"],
        },
        "obligations": ["distinguish-responsibility-before-repair"],
        "assumptions": ["probes_are_reversible", "components_are_separable"],
        "preconditions": ["probe_tool_available"],
        "transformation_steps": ["active_discriminator", "probe", "update-hypothesis"],
        "failure_modes": ["non-diagnosable-overlap"],
        "verification_hooks": ["held-out-component-isolation"],
        "falsifiers": ["discriminator-separates-toy-components"],
        "authority_boundaries": {
            "may_grant": ["inspection-license"],
            "may_not_grant": ["publication-authority", "target-label-access"],
        },
        "cost_requirements": {"context_budget": 4, "tools_required": ["probe"]},
        "evidence_level": "LOCAL_ENGINEERING_ONLY",
        "source_evidence_identities": ["artifact:debug-toy-v1"],
        "target_compatibility_tests": ["assumption:probes_are_reversible"],
        "forbidden_transfers": ["copy-source-patch-into-target"],
    }
    payload.update(overrides)
    return payload


def positive_source_object() -> ScientificTransferObject:
    return build_transfer_object(**_base_fields())


def ablated_source_object() -> ScientificTransferObject:
    return build_transfer_object(
        **_base_fields(
            object_id="cell:active-discriminator:debugging:ablated",
            transformation_steps=["probe", "update-hypothesis"],
        )
    )


def nl_insight_baseline() -> ScientificTransferObject:
    return build_transfer_object(
        **_base_fields(
            object_id="cell:nl-insight:debugging",
            transformation_steps=["apply-abstract-advice"],
            verification_hooks=["anecdote-sounds-general"],
            falsifiers=["nl-insight-has-no-executable-hook"],
        )
    )


def different_terms_source_object() -> ScientificTransferObject:
    signature = {
        "signature_id": "sig:grid-fault",
        "family_id": "debugging",
        "surface_domain": "grid-fault-clearing",
        "hidden_state": "unknown-breaker",
        "observability": "meter-only",
        "actions": ["isolate", "restore"],
        "ground_truth_class": "protected",
        "dependence": 0.6,
        "authority_risk": 0.8,
        "nonstationarity": 0.2,
        "reversibility": 0.9,
    }
    return build_transfer_object(
        **_base_fields(
            object_id="cell:active-discriminator:grid",
            problem_signature=signature,
        )
    )


def target_evidence(**overrides: Any) -> dict[str, Any]:
    source = positive_source_object()
    evidence: dict[str, Any] = {
        "assumptions": {name: True for name in source.assumptions},
        "preconditions": {name: True for name in source.preconditions},
        "falsifiers": {name: True for name in source.falsifiers},
        "evidence_fresh": True,
        "available_tools": ["probe"],
        "falsifier_integrity": True,
        "provenance": ["LOCAL_ENGINEERING_ONLY:toy"],
    }
    for key, value in overrides.items():
        if key in {"assumptions", "preconditions", "falsifiers"} and isinstance(value, Mapping):
            merged = dict(evidence[key])
            merged.update(value)
            evidence[key] = merged
        else:
            evidence[key] = value
    return evidence


@dataclass(frozen=True)
class HostileCase:
    kind: str
    source: ScientificTransferObject
    target: ProblemSignatureV3
    evidence: dict[str, Any]


def negative_transfer_cases() -> tuple[HostileCase, ...]:
    source = positive_source_object()
    target = TARGET_SIGNATURE
    return (
        HostileCase(
            kind="same_terms_incompatible_assumptions",
            source=source,
            target=target,
            evidence=target_evidence(assumptions={"probes_are_reversible": False}),
        ),
        HostileCase(
            kind="omitted_precondition",
            source=source,
            target=target,
            evidence=target_evidence(preconditions={"probe_tool_available": None}),
        ),
        HostileCase(
            kind="stale_source_evidence",
            source=source,
            target=target,
            evidence=target_evidence(evidence_fresh=False),
        ),
        HostileCase(
            kind="unavailable_tool",
            source=source,
            target=target,
            evidence=target_evidence(available_tools=[]),
        ),
        HostileCase(
            kind="corrupted_falsifier",
            source=source,
            target=target,
            evidence=target_evidence(falsifier_integrity=False),
        ),
    )


def hostile_cases() -> tuple[HostileCase, ...]:
    return negative_transfer_cases() + (
        HostileCase(
            kind="different_terms_same_mechanic",
            source=different_terms_source_object(),
            target=TARGET_SIGNATURE,
            evidence=target_evidence(),
        ),
    )


@dataclass(frozen=True)
class ToyIsolateWorld:
    components: tuple[str, ...] = ("A", "B", "C")
    failing: str = "B"

    def mechanic_gain(self) -> float:
        return 1.0 - (1.0 / len(self.components))


def score_world(world: ToyIsolateWorld, *, steps: tuple[str, ...]) -> float:
    if "active_discriminator" in steps:
        return 1.0
    return 1.0 / len(world.components)
