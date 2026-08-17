from __future__ import annotations

from copy import deepcopy

from orion.study.p5.negative_history_chain import (
    build_negative_history_chain,
    verify_negative_history_chain,
)
from orion.study.p5.v2_evidence import content_digest


ROOT = "a" * 64


def _manifest() -> dict:
    return {
        "schema_version": "fixture",
        "run_id": "run-1",
        "negative_history_root_hash": ROOT,
    }


def _record(index: int) -> dict:
    return {
        "result_id": f"result-{index}",
        "system_id": "orion-v2",
        "episode_id": "episode-1",
        "seed": 7,
        "candidate_id": "candidate-1",
        "stage": ("STATIC", "REPLAY", "FRESH", "PROTECTED")[index],
        "sequence_index": index,
        "negative_history_digest": content_digest({"negative-history": index}),
    }


def _archive() -> dict:
    records = [_record(index) for index in range(4)]
    archive = {"finalized": False, "records": records, "final_negative_history_hash": None}
    chain = build_negative_history_chain(_manifest(), archive)
    archive["finalized"] = True
    archive["final_negative_history_hash"] = chain["final_chain_hash"]
    return archive


def _chain(archive: dict) -> dict:
    return build_negative_history_chain(_manifest(), archive)


def _verify(document: dict, archive: dict, expected: str | None = None) -> tuple[str, ...]:
    return verify_negative_history_chain(
        document,
        _manifest(),
        archive,
        expected_document_hash=expected or document["document_hash"],
    )


def test_exact_host_selected_chain_and_final_tip_verify() -> None:
    archive = _archive()
    document = _chain(archive)
    assert _verify(document, archive) == ()
    assert archive["final_negative_history_hash"] == document["final_chain_hash"]


def test_arbitrary_syntactic_final_hash_is_rejected() -> None:
    archive = _archive()
    document = _chain(archive)
    archive["final_negative_history_hash"] = "f" * 64
    errors = _verify(document, archive)
    assert "finalized archive final_negative_history_hash is not the verified chain tip" in errors


def test_deletion_and_truncation_are_rejected_even_after_chain_recompute() -> None:
    archive = _archive()
    original = _chain(archive)
    shortened = deepcopy(archive)
    shortened["records"].pop(1)
    replacement = build_negative_history_chain(_manifest(), shortened)
    shortened["final_negative_history_hash"] = replacement["final_chain_hash"]

    errors = _verify(replacement, shortened, expected=original["document_hash"])
    assert "negative-history document identity mismatch" in errors


def test_reordering_is_rejected_by_host_selected_document_hash() -> None:
    archive = _archive()
    original = _chain(archive)
    reordered = deepcopy(archive)
    reordered["records"][1], reordered["records"][2] = (
        reordered["records"][2],
        reordered["records"][1],
    )
    replacement = build_negative_history_chain(_manifest(), reordered)
    reordered["final_negative_history_hash"] = replacement["final_chain_hash"]

    errors = _verify(replacement, reordered, expected=original["document_hash"])
    assert "negative-history document identity mismatch" in errors


def test_link_fork_or_substitution_is_rejected() -> None:
    archive = _archive()
    document = _chain(archive)
    document["links"][2]["previous_chain_hash"] = "e" * 64
    errors = _verify(document, archive)
    assert any(error.startswith("negative-history document_hash mismatch") for error in errors)
    assert any("link 2 mismatch:previous_chain_hash" in error for error in errors)


def test_stale_root_replay_is_rejected() -> None:
    archive = _archive()
    document = _chain(archive)
    manifest = _manifest()
    manifest["negative_history_root_hash"] = "b" * 64
    errors = verify_negative_history_chain(
        document,
        manifest,
        archive,
        expected_document_hash=document["document_hash"],
    )
    assert "negative-history root hash mismatch" in errors
    assert "negative-history genesis mismatch" in errors


def test_record_digest_substitution_is_rejected_without_rewriting_host_chain() -> None:
    archive = _archive()
    document = _chain(archive)
    archive["records"][0]["negative_history_digest"] = "c" * 64
    errors = _verify(document, archive)
    assert any("link 0 mismatch:negative_history_digest" in error for error in errors)


def test_chain_document_is_non_authorizing_by_construction() -> None:
    archive = _archive()
    document = _chain(archive)
    assert "empirical_authority" not in document
    assert "grants_phase2_closure" not in document
    assert "grants_governed_self_orion" not in document
