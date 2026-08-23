"""Fixtures for the Phase-4 programme scaffolding tests.

The central fixture is ``clean_state``: a well-formed programme on which every
anti-collapse check must return ``PASS``. Asserting the no-alarm case matters as
much as asserting the alarm — a battery that fires on a healthy programme gets
switched off, and a switched-off battery detects nothing at all.

Nothing here is real programme content. Every value is a fixture, and the
package under test holds no populated state of its own.
"""

from __future__ import annotations

from hashlib import sha256

import pytest

from orion.programme.method_knowledge import (
    ApplicabilityBoundary,
    CausalSupportLink,
    ImplementationIdentity,
    MethodKnowledgeRecord,
    TransferEvidence,
)
from orion.programme.object_knowledge import ObjectKnowledgeRecord
from orion.programme.programme_state import EXTERNAL_CUSTODY, EpochSnapshot, ProgrammeState
from orion.programme.records import (
    ObjectAuthority,
    Outcome,
    ProvenanceBinding,
    RouteAvailability,
)
from orion.programme.search_universe_knowledge import (
    BlindSpotTest,
    CoverageObligation,
    ReopenRule,
    RouteState,
    SearchUniverseKnowledgeRecord,
)


_LEGACY_P11_P14_PLACEHOLDER_TESTS = {
    "tests/unit/programme/test_superiority_gates.py::test_p11_to_p14_directories_exist_with_a_readme",
    "tests/unit/programme/test_superiority_gates.py::test_p11_to_p14_add_no_manuscript_that_would_collide_with_pr_715",
}


def pytest_collection_modifyitems(config, items) -> None:
    """Retire exactly two #715-era placeholder assertions after canonical paper PRs exist.

    Their coverage is replaced by ``test_p11_p14_publication_transition.py``,
    which accepts either an honest placeholder or a complete canonical package.
    """

    del config
    for item in items:
        if item.nodeid in _LEGACY_P11_P14_PLACEHOLDER_TESTS:
            item.add_marker(
                pytest.mark.skip(
                    reason=(
                        "superseded by state-aware P11-P14 publication-transition guard; "
                        "#771-#774 individually supersede draft #715 ownership"
                    )
                )
            )


def digest_of(label: str) -> str:
    """A deterministic stand-in SHA-256 for fixture bindings."""

    return sha256(label.encode("utf-8")).hexdigest()


@pytest.fixture
def provenance() -> ProvenanceBinding:
    return ProvenanceBinding(
        source_id="s-1",
        source_uri="https://example.invalid/paper",
        source_family="arxiv",
        source_version="v3",
        content_sha256=digest_of("source-1-v3"),
        retrieved_at_epoch=0,
    )


@pytest.fixture
def object_record(provenance: ProvenanceBinding) -> ObjectKnowledgeRecord:
    return ObjectKnowledgeRecord(
        object_id="obj-1",
        referent_id="ref-1",
        claim_id="claim-1",
        claim_text="the measured quantity is bounded above",
        record_version=1,
        evidence_ids=("ev-1",),
        provenance=(provenance,),
        depends_on_coordinates=("K.CLAIM.obj-1", "W.ROUTE_KIND.literature"),
        authority=ObjectAuthority.VERIFIED,
        search_universe_record_id="uni-1",
        method_record_ids=("m-a",),
    )


@pytest.fixture
def search_universe() -> SearchUniverseKnowledgeRecord:
    return SearchUniverseKnowledgeRecord(
        universe_id="uni-1",
        universe_version=1,
        active_domain_ids=("d-physics", "d-statistics"),
        routes=(
            RouteState("r-1", "literature", "arxiv", RouteAvailability.AVAILABLE),
            RouteState("r-2", "registry", "journal", RouteAvailability.AVAILABLE),
        ),
        representation_ids=("repr-graph",),
        obligations=(
            CoverageObligation(
                obligation_id="ob-1",
                source_family="arxiv",
                domain_id="d-physics",
                required_route_kind_ids=("literature",),
                discharged=True,
                discharging_evidence_ids=("ev-1",),
            ),
        ),
        blind_spot_tests=(
            BlindSpotTest("bs-1", "held-out domain probe", Outcome.PASS),
        ),
        reopen_rules=(
            ReopenRule("rr-1", "NEW_DOMAIN_DISCOVERED", "W", "reopen on a new domain"),
        ),
        saturation_claimed=True,
        saturation_basis_digest=digest_of("saturation-basis"),
    )


@pytest.fixture
def method_record() -> MethodKnowledgeRecord:
    return MethodKnowledgeRecord(
        method_id="m-a",
        method_version="1.0.0",
        implementation=ImplementationIdentity(
            module_path="orion.example.method_a",
            source_sha256=digest_of("method-a-source"),
            protocol_id="PROTO.method-a.v1",
            protocol_document_digest=digest_of("method-a-protocol"),
        ),
        applicability=(
            ApplicabilityBoundary(
                boundary_id="ab-1",
                assumption="samples are exchangeable",
                violated_when="ordering carries signal",
                checked=Outcome.PASS,
            ),
        ),
        causal_support=(
            CausalSupportLink(
                link_id="cs-1",
                failure_class="F-A",
                attributed_stage="ENTRY_EXECUTION",
                intervention_id="I-1",
                evidence_ids=("ev-2",),
            ),
        ),
        transfer_evidence=(
            TransferEvidence(
                evidence_id="te-replay",
                kind="REPLAY",
                epoch_id="epoch-0",
                evaluator_artifact_hash=digest_of("evaluator"),
                outcome=Outcome.PASS,
            ),
            TransferEvidence(
                evidence_id="te-fresh",
                kind="FRESH_TRANSFER",
                epoch_id="epoch-1",
                evaluator_artifact_hash=digest_of("evaluator"),
                outcome=Outcome.PASS,
                independently_verified=True,
                evaluator_outside_candidate_custody=True,
            ),
        ),
        known_failure_classes=("F-A",),
        negative_history_entry_ids=("nh-1",),
        negative_history_chain_digest=digest_of("negative-history-chain"),
    )


def _epoch(sequence: int) -> EpochSnapshot:
    return EpochSnapshot(
        epoch_id=f"epoch-{sequence}",
        sequence=sequence,
        protected_metric=0.70 + 0.04 * sequence,
        fresh_transfer_metric=0.60 + 0.03 * sequence,
        worst_family_metric=0.52 + 0.02 * sequence,
        evaluator_artifact_hash=digest_of("evaluator"),
        evaluator_custody=EXTERNAL_CUSTODY,
        selected_method_ids=(("m-a",), ("m-b",))[sequence],
        evaluated_method_ids=("m-a", "m-b"),
        source_family_evidence_counts=(
            ("arxiv", 5 + sequence),
            ("journal", 4 + sequence),
            ("preprint", 3 + sequence),
        ),
        negative_history_entry_ids=tuple(f"nh-{i}" for i in range(1, sequence + 2)),
        rejected_result_ids=tuple(f"rej-{i}" for i in range(1, sequence + 2)),
        cycle_failure_interventions=((("F-A", "I-1"),), (("F-B", "I-2"),))[sequence],
        protected_evidence_present=True,
        conclusion_claimed=True,
    )


@pytest.fixture
def epochs() -> tuple[EpochSnapshot, ...]:
    return (_epoch(0), _epoch(1))


@pytest.fixture
def clean_state(
    epochs: tuple[EpochSnapshot, ...],
    object_record: ObjectKnowledgeRecord,
    search_universe: SearchUniverseKnowledgeRecord,
    method_record: MethodKnowledgeRecord,
) -> ProgrammeState:
    return ProgrammeState(
        programme_id="prog-1",
        epochs=epochs,
        object_records=(object_record,),
        search_universe=search_universe,
        method_records=(method_record,),
        current_source_versions=(("s-1", "v3"),),
        internal_source_families=("orion-internal",),
        source_family_share_ceiling=0.5,
        min_epochs_for_trend=2,
    )
