from dataclasses import replace

import pytest

from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.p8_method_authority import (
    AuthorityCoordinate,
    AuthorityState,
    CapabilityKind,
    CapabilityOutput,
    CoercionDecision,
    DefeaterKind,
    ProvenanceClass,
    apply_decision,
    authority_record,
    coerce,
    provenance,
    revoke,
)


def d(x):
    return content_digest({"x": x})


def record():
    p = provenance(
        method_id="m",
        provenance_class=ProvenanceClass.INVENTED_METHOD_CANDIDATE,
        subject_digest=d("subject"),
        source_ids=("donor",),
        generator_id="p10",
        generator_version="v1",
        evidence_digest=d("prov"),
    )
    return authority_record(p)


def test_illicit_blocked_coercion_is_non_mutating():
    r = record()
    legal = coerce(
        CapabilityOutput(CapabilityKind.P4_VERIFICATION, d("subject"), d("valid")),
        AuthorityCoordinate.VALIDITY,
    )
    supported = apply_decision(r, legal)
    illicit = coerce(
        CapabilityOutput(CapabilityKind.P10_GENERATION, d("subject"), d("gen")),
        AuthorityCoordinate.VALIDITY,
    )
    assert illicit.state is AuthorityState.BLOCKED
    with pytest.raises(ValueError, match="non-mutating"):
        apply_decision(supported, illicit)
    assert supported.state(AuthorityCoordinate.VALIDITY) is AuthorityState.SUPPORTED


def test_hand_built_illegal_supported_decision_is_rejected():
    illicit = coerce(
        CapabilityOutput(CapabilityKind.P10_GENERATION, d("subject"), d("gen")),
        AuthorityCoordinate.NOVELTY,
    )
    forged = replace(illicit, state=AuthorityState.SUPPORTED)
    with pytest.raises(ValueError, match="not legal"):
        forged.verify()


def test_cross_subject_decision_cannot_authorize_another_record():
    r = record()
    decision = coerce(
        CapabilityOutput(CapabilityKind.P4_VERIFICATION, d("other-subject"), d("e")),
        AuthorityCoordinate.VALIDITY,
    )
    with pytest.raises(ValueError, match="subject does not match"):
        apply_decision(r, decision)


def test_revocation_requires_content_bound_defeater_evidence():
    r = record()
    with pytest.raises(ValueError, match="content-bound defeater"):
        revoke(r, defeater=DefeaterKind.PRIOR_ART, evidence_digest="")
    with pytest.raises(ValueError, match="content-bound defeater"):
        revoke(r, defeater=DefeaterKind.PRIOR_ART, evidence_digest="prior-art")


def test_bound_revocation_remains_forward_only():
    r = record()
    novel = coerce(
        CapabilityOutput(CapabilityKind.NOVELTY_REVIEW, d("subject"), d("novel")),
        AuthorityCoordinate.NOVELTY,
    )
    before = apply_decision(r, novel)
    after = revoke(before, defeater=DefeaterKind.PRIOR_ART, evidence_digest=d("prior-art"))
    before.verify(); after.verify()
    assert before.state(AuthorityCoordinate.NOVELTY) is AuthorityState.SUPPORTED
    assert after.state(AuthorityCoordinate.NOVELTY) is AuthorityState.BLOCKED
    assert after.predecessor_digest == before.digest
