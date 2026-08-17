"""Self-application of ScientificNoveltyCertificate.v1 to ORION P1–P5 residuals."""

from orion.novelty import NoveltyFinalState, SCHEMA_ID, apply_orion_residuals, seal_certificate


ALLOWED_SELF_STATES = {
    NoveltyFinalState.NOVELTY_NARROWED,
    NoveltyFinalState.ALREADY_SOLVED,
    NoveltyFinalState.CANNOT_CHECK,
}


def test_self_application_covers_p1_through_p5_and_programme_residuals():
    certificates = apply_orion_residuals()
    claim_ids = {cert.claim_id for cert in certificates}
    assert claim_ids >= {
        "orion:P1:#278",
        "orion:P2:#279",
        "orion:P3:#280",
        "orion:P4:#281",
        "orion:P5:#282",
        "orion:GP:#285",
        "orion:TX:#286",
    }
    for cert in certificates:
        assert cert.schema_id == SCHEMA_ID
        assert cert.hostile_already_solved_route is not None
        assert cert.absorption_decisions
        assert cert.smallest_residual
        assert cert.final_state in NoveltyFinalState
        assert cert.final_state is not NoveltyFinalState.NOVELTY_SUPPORTED
        assert cert.final_state in ALLOWED_SELF_STATES
        assert len(cert.content_hash) == 64
        assert cert.search_snapshot.snapshot_date


def test_self_application_never_uses_llm_score_as_authority():
    for cert in apply_orion_residuals():
        assert cert.llm_novelty_score is None
        assert cert.llm_proposed_state is None
        resealed = seal_certificate(cert.to_draft())
        assert resealed.final_state is cert.final_state
        assert resealed.content_hash == cert.content_hash


def test_p1_p5_dispositions_are_explicit():
    by_id = {cert.claim_id: cert for cert in apply_orion_residuals()}
    p1 = by_id["orion:P1:#278"]
    p2 = by_id["orion:P2:#279"]
    p3 = by_id["orion:P3:#280"]
    p4 = by_id["orion:P4:#281"]
    p5 = by_id["orion:P5:#282"]
    assert p1.final_state is NoveltyFinalState.CANNOT_CHECK
    assert p2.final_state is NoveltyFinalState.CANNOT_CHECK
    assert p3.final_state is NoveltyFinalState.NOVELTY_NARROWED
    assert p4.final_state is NoveltyFinalState.NOVELTY_NARROWED
    assert p5.final_state is NoveltyFinalState.NOVELTY_NARROWED
    assert by_id["orion:GP:#285"].final_state is NoveltyFinalState.CANNOT_CHECK
    assert by_id["orion:TX:#286"].final_state is NoveltyFinalState.CANNOT_CHECK
    for cert in (p1, p2, p3, p4, p5):
        dispositions = {decision.disposition.value for decision in cert.absorption_decisions}
        assert dispositions <= {"ADOPT", "ADAPT", "COMPOSE", "DEFER", "REJECT"}
        assert dispositions


def test_archived_index_matches_sealed_hashes():
    import json
    from pathlib import Path

    index = json.loads(
        Path("research/novelty/self-application/INDEX.json").read_text(encoding="utf-8")
    )
    by_id = {cert.claim_id: cert for cert in apply_orion_residuals()}
    assert {row["claim_id"] for row in index["certificates"]} == set(by_id)
    for row in index["certificates"]:
        cert = by_id[row["claim_id"]]
        assert cert.content_hash == row["content_hash"]
        assert cert.final_state.value == row["final_state"]
        assert cert.snapshot_hash == row["snapshot_hash"]

