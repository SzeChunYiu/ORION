from __future__ import annotations

from orion.novelty.certificate import CertificateDraft
from orion.novelty.types import MechanismOverlap, NoveltyFinalState

ABSORBING_OVERLAPS = {MechanismOverlap.IDENTICAL, MechanismOverlap.FUNCTIONAL_EQUIVALENT}


def _residual_absorbed(draft: CertificateDraft) -> bool:
    residual = draft.smallest_residual.strip()
    if not residual:
        return True
    claimed_ids = {atom.mechanism_id for atom in draft.claimed_mechanism_decomposition}
    absorbing = {
        record.mechanism_id
        for record in draft.overlap_classifications
        if record.classification in ABSORBING_OVERLAPS
    }
    if claimed_ids and claimed_ids <= absorbing:
        return True
    hostile = draft.hostile_already_solved_route
    if hostile is not None and hostile.findings and hostile.residual_changed and not residual:
        return True
    return False


def decide_final_state(draft: CertificateDraft) -> tuple[NoveltyFinalState, tuple[str, ...]]:
    """Compute the certificate final state.

    An LLM novelty score, LLM-proposed state, or confidence value may be
    recorded on the draft. None of them can set or override the final state.
    """

    reasons: list[str] = []
    if draft.llm_novelty_score is not None or draft.llm_proposed_state is not None:
        reasons.append("recorded LLM novelty score/proposal is evidence, not authority")
    if draft.confidence is not None:
        reasons.append("confidence is not an authority input")

    hostile = draft.hostile_already_solved_route
    if hostile is None or not hostile.executed:
        reasons.append("hostile already-solved route missing or not executed")
        return NoveltyFinalState.CANNOT_CHECK, tuple(reasons)

    if draft.inaccessible_material_sources:
        reasons.append("inaccessible sources could materially absorb the claim")
        return NoveltyFinalState.CANNOT_CHECK, tuple(reasons)

    saturation = draft.saturation.report()
    if saturation.missing_routes:
        reasons.append("required search routes incomplete")
        reasons.extend(saturation.reasons)
        return NoveltyFinalState.CANNOT_CHECK, tuple(reasons)
    if not saturation.stop_rule_satisfied:
        reasons.append("search saturation stop rule not satisfied")
        reasons.extend(saturation.reasons)
        return NoveltyFinalState.CANNOT_CHECK, tuple(reasons)

    if _residual_absorbed(draft):
        reasons.append("hostile/function search absorbed the claimed mechanism")
        return NoveltyFinalState.ALREADY_SOLVED, tuple(reasons)

    original = draft.original_claim_text.strip()
    residual = draft.smallest_residual.strip()
    if original != residual:
        reasons.append("nearest-work absorption shrinks the claim to a smaller residual")
        return NoveltyFinalState.NOVELTY_NARROWED, tuple(reasons)

    if not draft.residual_implementation_evidence:
        reasons.append("residual is not evidenced in implementation or protocol")
        return NoveltyFinalState.CANNOT_CHECK, tuple(reasons)
    if not draft.discriminating_experiment.executed:
        reasons.append("discriminating experiment has not been executed")
        return NoveltyFinalState.CANNOT_CHECK, tuple(reasons)

    reasons.append(
        "residual survived hostile search with executed discriminator and implementation evidence"
    )
    return NoveltyFinalState.NOVELTY_SUPPORTED, tuple(reasons)
