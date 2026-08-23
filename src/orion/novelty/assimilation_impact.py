"""Bind #318 mechanism assimilation to #287 novelty authority.

A material donor absorption can make an already-sealed novelty certificate stale.  The
safe response is not to edit the certificate in place or to guess a narrower residual;
it is to emit a content-addressed impact receipt that says whether the certificate must
be re-assessed.  Until re-assessment is completed, the effective novelty state is
``CANNOT_CHECK``.

This module deliberately never upgrades novelty and never grants authority.  It is a
small bridge between two existing receipt systems:

* ``MechanismAssimilationReceipt.v1`` records what was taken from a donor (#318).
* ``ScientificNoveltyCertificate.v1`` records the scoped novelty residual (#287).

The bridge makes material absorption observable to the novelty layer rather than
allowing a previously sealed certificate to remain silently current.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from orion.knowledge.mechanism_assimilation import (
    AssimilationVerdict,
    MechanismAssimilationReceipt,
)
from orion.knowledge.nearest_work import AbsorptionDisposition
from orion.novelty.certificate import ScientificNoveltyCertificate
from orion.novelty.hashing import sha256_canonical
from orion.novelty.types import NoveltyFinalState

SCHEMA_ID = "orion.assimilation-novelty-impact.v1"

_MATERIAL_DISPOSITIONS = {
    AbsorptionDisposition.ADOPT,
    AbsorptionDisposition.ADAPT,
    AbsorptionDisposition.COMPOSE,
}


class AssimilationNoveltyImpactState(str, Enum):
    """Whether an assimilation can leave the current novelty certificate untouched."""

    NO_MATERIAL_IMPACT = "NO_MATERIAL_IMPACT"
    REASSESS_REQUIRED = "REASSESS_REQUIRED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class AssimilationNoveltyImpactReceipt:
    schema_id: str
    certificate_hash: str
    assimilation_hash: str
    affected_mechanic_ids: tuple[str, ...]
    state: AssimilationNoveltyImpactState
    prior_final_state: NoveltyFinalState
    effective_final_state: NoveltyFinalState
    reasons: tuple[str, ...]
    content_hash: str = field(default="")

    @property
    def grants_authority(self) -> str:
        return "NONE"

    @property
    def self_authorizing(self) -> bool:
        return False


def _certificate_mechanic_ids(certificate: ScientificNoveltyCertificate) -> set[str]:
    ids = {atom.mechanism_id for atom in certificate.claimed_mechanism_decomposition}
    for decision in certificate.absorption_decisions:
        ids.update(decision.target_mechanic_ids)
    return ids


def assess_assimilation_novelty_impact(
    certificate: ScientificNoveltyCertificate,
    assimilation: MechanismAssimilationReceipt,
) -> AssimilationNoveltyImpactReceipt:
    """Compute whether ``certificate`` remains current after ``assimilation``.

    Rules are intentionally one-way:

    * blocked or uncheckable assimilation never upgrades novelty;
    * DEFER/REJECT cannot materially rewrite a novelty residual;
    * an admitted ADOPT/ADAPT/COMPOSE that touches a certificate mechanic makes the
      certificate stale and forces effective ``CANNOT_CHECK`` until re-sealed;
    * admitted material absorption outside the certificate's mechanic surface is
      recorded but does not invalidate that certificate.
    """

    if not certificate.content_hash.strip():
        raise ValueError("novelty certificate must be content-addressed")
    if not assimilation.content_hash.strip():
        raise ValueError("assimilation receipt must be content-addressed")

    prior_state = NoveltyFinalState(certificate.final_state)
    target_ids = set(assimilation.claim.target_mechanic_ids)
    affected = tuple(sorted(_certificate_mechanic_ids(certificate) & target_ids))
    reasons: list[str] = []

    if assimilation.verdict is AssimilationVerdict.BLOCKED:
        state = AssimilationNoveltyImpactState.CANNOT_CHECK
        effective = NoveltyFinalState.CANNOT_CHECK
        reasons.append("assimilation is BLOCKED; novelty cannot treat the donor absorption as settled")
    elif assimilation.verdict is AssimilationVerdict.CANNOT_CHECK:
        state = AssimilationNoveltyImpactState.CANNOT_CHECK
        effective = NoveltyFinalState.CANNOT_CHECK
        reasons.append("assimilation is CANNOT_CHECK; novelty remains fail-closed until donor absorption is settled")
    elif assimilation.disposition not in _MATERIAL_DISPOSITIONS:
        state = AssimilationNoveltyImpactState.NO_MATERIAL_IMPACT
        effective = prior_state
        reasons.append(f"{assimilation.disposition.value} does not materially absorb a donor mechanism")
    elif affected:
        state = AssimilationNoveltyImpactState.REASSESS_REQUIRED
        effective = NoveltyFinalState.CANNOT_CHECK
        reasons.append(
            "admitted material absorption touches certificate mechanics: " + ", ".join(affected)
        )
        reasons.append("the prior novelty certificate is stale until its residual is re-assessed and re-sealed")
    else:
        state = AssimilationNoveltyImpactState.NO_MATERIAL_IMPACT
        effective = prior_state
        reasons.append("admitted material absorption does not touch this certificate's mechanic surface")

    receipt = AssimilationNoveltyImpactReceipt(
        schema_id=SCHEMA_ID,
        certificate_hash=certificate.content_hash,
        assimilation_hash=assimilation.content_hash,
        affected_mechanic_ids=affected,
        state=state,
        prior_final_state=prior_state,
        effective_final_state=effective,
        reasons=tuple(reasons),
    )
    return AssimilationNoveltyImpactReceipt(
        **{**receipt.__dict__, "content_hash": sha256_canonical(receipt)}
    )


def assert_certificate_current_after_assimilation(
    certificate: ScientificNoveltyCertificate,
    assimilation: MechanismAssimilationReceipt,
) -> AssimilationNoveltyImpactReceipt:
    """Return the impact receipt or fail whenever effective novelty is no longer current."""

    receipt = assess_assimilation_novelty_impact(certificate, assimilation)
    if receipt.state is AssimilationNoveltyImpactState.REASSESS_REQUIRED:
        raise ValueError(
            "material donor absorption invalidated the current novelty certificate; re-assessment required"
        )
    if receipt.state is AssimilationNoveltyImpactState.CANNOT_CHECK:
        raise ValueError(
            "donor assimilation is unsettled; current novelty certificate cannot be relied on"
        )
    return receipt


__all__ = [
    "AssimilationNoveltyImpactReceipt",
    "AssimilationNoveltyImpactState",
    "SCHEMA_ID",
    "assess_assimilation_novelty_impact",
    "assert_certificate_current_after_assimilation",
]
