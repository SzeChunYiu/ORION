import pytest

from orion.core.claims import ClaimAuthority
from orion.core.contributions import (
    AssimilationOutcome,
    KnowledgeContribution,
    MappingRelation,
    ReferentBinding,
    ReferentResolution,
    RepresentationMapping,
)
from orion.core.method import MethodState
from orion.core.problem import Problem
from orion.core.residuals import ResidualKind
from orion.core.search import RetrievedItem
from orion.core.search_universe import SearchUniverseState
from orion.core.state import KnowledgeState, OrionState
from orion.engine.operators.absorb import AbsorbOperator
from orion.engine.operators.reconstruct import ReconstructOperator
from orion.engine.operators.search import SearchBatch
from orion.providers.verification.base import VerificationResult


class ContributionReasoner:
    def __init__(self, contributions):
        self.contributions = contributions

    def interpret(self, item, problem, state):
        del problem, state
        return self.contributions[item.item_id]


class ReconstructionReasoner:
    def reconstruct(self, problem, state):
        del problem, state
        return "integrated portrait"


class RecordingVerifier:
    def __init__(self, *, passed=False):
        self.passed = passed
        self.calls = []

    def verify(self, contribution, item):
        self.calls.append((contribution.contribution_id, item.item_id))
        if self.passed:
            return VerificationResult(True, (f"cert:{contribution.contribution_id}",))
        return VerificationResult(False, reason="not independently verified")


def _state():
    return OrionState(
        knowledge=KnowledgeState(),
        search_universe=SearchUniverseState(),
        method=MethodState(method_version="test"),
    )


def _item(item_id):
    return RetrievedItem(
        item_id=item_id,
        content=f"content for {item_id}",
        source_uri=f"https://example.test/{item_id}",
        domain_ids=("source-domain",),
    )


def _contribution(item_id, outcome, **kwargs):
    return KnowledgeContribution(
        contribution_id=f"contribution:{item_id}",
        text=f"interpretation of {item_id}",
        assimilation=outcome,
        evidence_ids=(item_id,),
        **kwargs,
    )


def _absorb(contributions, *, verifier=None):
    verifier = verifier or RecordingVerifier()
    operator = AbsorbOperator(ContributionReasoner(contributions), verifier)
    items = tuple(_item(item_id) for item_id in contributions)
    result = operator.run(Problem("p", "question"), _state(), SearchBatch((), items))
    return result, verifier


def test_already_known_and_equivalent_views_keep_projections_without_duplicate_claims_or_widening_w():
    contributions = {
        "e1": _contribution(
            "e1",
            AssimilationOutcome.ALREADY_KNOWN,
            discovered_domain_ids=("should-not-open",),
            representation_ids=("should-not-map",),
        ),
        "e2": _contribution(
            "e2",
            AssimilationOutcome.EQUIVALENT_VIEW,
            discovered_domain_ids=("also-closed",),
        ),
    }
    result, verifier = _absorb(contributions)

    assert result.state.knowledge.claims == ()
    assert result.state.knowledge.source_projection_ids == (
        "projection:contribution:e1",
        "projection:contribution:e2",
    )
    assert result.state.search_universe.candidate_domain_ids == ()
    assert result.state.search_universe.representation_ids == ()
    assert verifier.calls == []


def test_unresolved_contribution_stays_projection_and_opens_context_gap_without_claim():
    result, verifier = _absorb(
        {"e1": _contribution("e1", AssimilationOutcome.UNRESOLVED)}
    )

    assert result.state.knowledge.claims == ()
    assert len(result.state.knowledge.source_projections) == 1
    assert [item.kind for item in result.state.knowledge.residuals] == [
        ResidualKind.CONTEXT_GAP
    ]
    assert verifier.calls == []


def test_contradiction_is_integrated_as_source_projection_and_opens_residual_without_authority_laundering():
    result, verifier = _absorb(
        {
            "e1": _contribution(
                "e1",
                AssimilationOutcome.CONTRADICTS_EXISTING,
                contradicts_claim_ids=("claim:incumbent",),
            )
        }
    )

    claim = result.state.knowledge.claims[0]
    assert claim.authority is ClaimAuthority.SOURCE_PROJECTION
    assert claim.contradicts_claim_ids == ("claim:incumbent",)
    assert any(
        item.kind is ResidualKind.CONTRADICTION
        for item in result.state.knowledge.residuals
    )
    assert verifier.calls == [("contribution:e1", "e1")]
    assert not result.transition.authority_increase


def test_verified_integrated_claim_requires_existing_verifier_certificate_path():
    verifier = RecordingVerifier(passed=True)
    result, _ = _absorb(
        {"e1": _contribution("e1", AssimilationOutcome.NEW_MECHANISM)},
        verifier=verifier,
    )

    claim = result.state.knowledge.claims[0]
    assert claim.authority is ClaimAuthority.VERIFIED
    assert claim.certificate_ids == ("cert:contribution:e1",)
    assert result.transition.authority_increase
    assert result.transition.scientific_authority_certificate_ids == (
        "cert:contribution:e1",
    )


def test_search_universe_gap_can_widen_w_and_records_source_context():
    result, _ = _absorb(
        {
            "e1": _contribution(
                "e1",
                AssimilationOutcome.EXPOSES_SEARCH_UNIVERSE_GAP,
                discovered_domain_ids=("measurement-science",),
                representation_ids=("source:calibration-frame",),
                context_ids=("population:clinical",),
            )
        }
    )

    assert result.state.search_universe.candidate_domain_ids == (
        "measurement-science",
    )
    assert result.state.search_universe.representation_ids == (
        "source:calibration-frame",
    )
    projection = result.state.knowledge.source_projections[0]
    assert "problem:p" in projection.context_ids
    assert "population:clinical" in projection.context_ids
    assert "domain:source-domain" in projection.context_ids
    assert any(
        item.kind is ResidualKind.SEARCH_COVERAGE_FAILURE
        for item in result.state.knowledge.residuals
    )


def test_ambiguous_referent_opens_context_gap_even_for_otherwise_benign_facet():
    result, _ = _absorb(
        {
            "e1": _contribution(
                "e1",
                AssimilationOutcome.COMPLEMENTARY_FACET,
                referent_bindings=(
                    ReferentBinding(
                        mention="performance",
                        resolution=ReferentResolution.AMBIGUOUS,
                        context_id="metric-context",
                    ),
                ),
            )
        }
    )

    assert any(
        item.kind is ResidualKind.CONTEXT_GAP
        for item in result.state.knowledge.residuals
    )


def test_incompatible_representation_mapping_is_persisted_and_opens_representation_failure():
    mapping = RepresentationMapping(
        mapping_id="map:1",
        source_representation_id="source:effect-size",
        target_representation_id="orion:effect-size",
        relation=MappingRelation.INCOMPATIBLE,
        evidence_ids=("e1",),
    )
    result, _ = _absorb(
        {
            "e1": _contribution(
                "e1",
                AssimilationOutcome.NEW_REPRESENTATION,
                representation_mappings=(mapping,),
            )
        }
    )

    assert result.state.knowledge.representation_mapping_ids == ("map:1",)
    assert "source:effect-size" in result.state.search_universe.representation_ids
    assert "orion:effect-size" in result.state.search_universe.representation_ids
    assert any(
        item.kind is ResidualKind.REPRESENTATION_FAILURE
        for item in result.state.knowledge.residuals
    )


def test_orion_native_mapping_must_remain_recoverable_to_source_projection():
    with pytest.raises(ValueError, match="recoverable"):
        RepresentationMapping(
            mapping_id="map:bad",
            source_representation_id="source:x",
            target_representation_id="orion:x",
            relation=MappingRelation.EQUIVALENT,
            evidence_ids=("e1",),
            recoverable=False,
        )


def test_reconstruction_preserves_projection_mapping_and_authority_lineage():
    mapping = RepresentationMapping(
        mapping_id="map:1",
        source_representation_id="source:x",
        target_representation_id="orion:x",
        relation=MappingRelation.EQUIVALENT,
        evidence_ids=("e1",),
    )
    verifier = RecordingVerifier(passed=True)
    absorbed, _ = _absorb(
        {
            "e1": _contribution(
                "e1",
                AssimilationOutcome.NEW_REPRESENTATION,
                representation_mappings=(mapping,),
            )
        },
        verifier=verifier,
    )
    reconstructed = ReconstructOperator(ReconstructionReasoner()).run(
        Problem("p", "question"), absorbed.state
    )
    portrait = reconstructed.output

    assert portrait.claim_ids == ("contribution:e1",)
    assert portrait.verified_claim_ids == ("contribution:e1",)
    assert portrait.source_projection_ids == ("projection:contribution:e1",)
    assert portrait.representation_mapping_ids == ("map:1",)
