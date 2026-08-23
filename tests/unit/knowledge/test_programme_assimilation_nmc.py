import runpy
from dataclasses import replace
from pathlib import Path

from orion.knowledge.mechanism_assimilation import (
    AssimilationAuthority,
    AssumptionStatus,
    HostileFindingKind,
    assess_assimilation,
)


def _drafts():
    ns = runpy.run_path(
        str(Path("research/assimilation-programme-v1/PROGRAMME_ASSIMILATION_EXPERIMENT_V1.py"))
    )
    return ns["_adopt"](), ns["_adapt"](), ns["_compose"]()


def _kinds(draft):
    return {finding.kind for finding in assess_assimilation(draft)}


def test_round_b_existing_hostile_vocabulary_catches_all_programme_mutations() -> None:
    adopt, adapt, compose = _drafts()

    rebrand = replace(
        adopt,
        claim=replace(adopt.claim, orion_name="ORION renamed preservation", delta=""),
    )
    first = adapt.mechanism.assumptions[0]
    dropped = replace(first, status=AssumptionStatus.DROPPED, justification="")
    lost_assumption = replace(
        adapt,
        mechanism=replace(
            adapt.mechanism,
            assumptions=(dropped,) + adapt.mechanism.assumptions[1:],
        ),
    )
    escalated = replace(
        adapt,
        claim=replace(adapt.claim, orion_authority=AssimilationAuthority.GENERAL),
    )
    fake_compose = replace(
        compose,
        claim=replace(compose.claim, composition_evidence=()),
    )
    no_structure = replace(adopt, structural_receipt_id="")

    assert HostileFindingKind.REBRANDING in _kinds(rebrand)
    assert HostileFindingKind.LOST_ASSUMPTIONS in _kinds(lost_assumption)
    assert HostileFindingKind.AUTHORITY_ESCALATION in _kinds(escalated)
    assert HostileFindingKind.FAKE_COMPOSITION in _kinds(fake_compose)
    assert HostileFindingKind.MISSING_STRUCTURAL_RECEIPT in _kinds(no_structure)
