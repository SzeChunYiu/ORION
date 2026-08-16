import random

import pytest

from orion.knowledge.multires_memory import (
    MemoryView,
    MemoryViewKind,
    MemoryViewVerdict,
    SourcePin,
    canonical_source_closure,
    validate_memory_view,
)


def canonical(record_id: str, payload_hash: str | None = None, *, certs=()):
    return MemoryView(record_id, payload_hash or f"hash-{record_id}", MemoryViewKind.CANONICAL, authority_certificates=tuple(certs))


def pin(view: MemoryView) -> SourcePin:
    return SourcePin(view.record_id, view.payload_hash)


def test_canonical_leaf_is_valid_and_is_its_own_source_root():
    raw = canonical("raw")
    report = validate_memory_view("raw", [raw])
    assert report.verdict == MemoryViewVerdict.VALID_CANONICAL
    assert report.canonical_root_ids == ("raw",)


def test_lossy_view_is_rehydratable_not_self_reconstructing():
    raw = canonical("raw")
    view = MemoryView("summary", "hash-summary", MemoryViewKind.DERIVED_LOSSY, source_pins=(pin(raw),), transform_id="summarize-v1", erasure_tags=("exact-wording",))
    report = validate_memory_view("summary", [view, raw])
    assert report.verdict == MemoryViewVerdict.SOURCE_REHYDRATABLE
    assert report.canonical_root_ids == ("raw",)


def test_lossy_view_cannot_claim_exact_reconstruction():
    raw = canonical("raw")
    with pytest.raises(ValueError, match="lossy views cannot claim exact reconstruction"):
        MemoryView("summary", "hash-summary", MemoryViewKind.DERIVED_LOSSY, source_pins=(pin(raw),), transform_id="summarize-v1", erasure_tags=("detail",), reconstruction_verified=True, reconstruction_witness_id="witness")


def test_dangling_stale_and_cyclic_sources_fail_closed():
    dangling = MemoryView("view", "hash-view", MemoryViewKind.DERIVED_LOSSLESS, source_pins=(SourcePin("missing", "hash-missing"),), transform_id="normalize-v1")
    assert validate_memory_view("view", [dangling]).verdict == MemoryViewVerdict.INVALID
    raw = canonical("raw", "current")
    stale = MemoryView("stale", "hash-stale", MemoryViewKind.DERIVED_LOSSLESS, source_pins=(SourcePin("raw", "old"),), transform_id="normalize-v1")
    assert "source_hash_mismatch:raw" in validate_memory_view("stale", [raw, stale]).issues
    a = MemoryView("a", "hash-a", MemoryViewKind.DERIVED_LOSSLESS, source_pins=(SourcePin("b", "hash-b"),), transform_id="t")
    b = MemoryView("b", "hash-b", MemoryViewKind.DERIVED_LOSSLESS, source_pins=(SourcePin("a", "hash-a"),), transform_id="t")
    assert "source_cycle" in validate_memory_view("a", [a, b]).issues


def test_multilevel_view_reports_complete_canonical_closure():
    a, b = canonical("a"), canonical("b")
    mid = MemoryView("mid", "hash-mid", MemoryViewKind.DERIVED_LOSSY, source_pins=(pin(a), pin(b)), transform_id="summarize-v1", erasure_tags=("verbatim",))
    top = MemoryView("top", "hash-top", MemoryViewKind.DERIVED_LOSSY, source_pins=(pin(mid),), transform_id="abstract-v1", erasure_tags=("detail",), required_canonical_ids=("a", "b"))
    assert canonical_source_closure("top", [top, b, mid, a]) == ("a", "b")


def test_derived_view_cannot_mint_authority_but_may_preserve_it():
    raw = canonical("raw", certs=("SOURCE_SPAN_SUPPORT",))
    escalated = MemoryView("bad", "hash-bad", MemoryViewKind.DERIVED_LOSSLESS, source_pins=(pin(raw),), transform_id="normalize-v1", authority_certificates=("SOURCE_SPAN_SUPPORT", "MECHANISM_ANCESTRY_SUPPORTED"))
    assert "authority_escalation:MECHANISM_ANCESTRY_SUPPORTED" in validate_memory_view("bad", [raw, escalated]).issues
    preserved = MemoryView("ok", "hash-ok", MemoryViewKind.DERIVED_LOSSLESS, source_pins=(pin(raw),), transform_id="normalize-v1", authority_certificates=("SOURCE_SPAN_SUPPORT",))
    assert validate_memory_view("ok", [raw, preserved]).valid


def test_contradiction_side_cannot_be_silently_dropped():
    side_a = canonical("side-a")
    view = MemoryView("summary", "hash-summary", MemoryViewKind.DERIVED_LOSSY, source_pins=(pin(side_a),), transform_id="contrast-v1", erasure_tags=("verbatim",), required_canonical_ids=("side-a", "side-b"))
    report = validate_memory_view("summary", [side_a, view])
    assert report.verdict == MemoryViewVerdict.INVALID
    assert "required_canonical_unreachable:side-b" in report.issues


def test_verified_lossless_regeneration_requires_witness():
    raw = canonical("raw")
    view = MemoryView("normalized", "hash-normalized", MemoryViewKind.DERIVED_LOSSLESS, source_pins=(pin(raw),), transform_id="normalize-v1", reconstruction_verified=True, reconstruction_witness_id="replay-test")
    assert validate_memory_view("normalized", [raw, view]).verdict == MemoryViewVerdict.REGENERATION_VERIFIED


def test_negative_history_root_remains_reachable():
    old = canonical("old-refutation")
    current = canonical("current")
    view = MemoryView("overview", "hash-overview", MemoryViewKind.DERIVED_LOSSY, source_pins=(pin(current), pin(old)), transform_id="overview-v1", erasure_tags=("verbatim",), required_canonical_ids=("old-refutation",))
    assert "old-refutation" in validate_memory_view("overview", [view, current, old]).canonical_root_ids


def test_validation_is_deterministic_under_registry_permutation():
    a, b = canonical("a"), canonical("b")
    view = MemoryView("view", "hash-view", MemoryViewKind.DERIVED_LOSSY, source_pins=(pin(b), pin(a)), transform_id="summary-v1", erasure_tags=("detail",))
    expected = validate_memory_view("view", [a, b, view])
    for seed in range(10):
        rows = [a, b, view]
        random.Random(seed).shuffle(rows)
        actual = validate_memory_view("view", rows)
        assert actual.verdict == expected.verdict
        assert actual.canonical_root_ids == expected.canonical_root_ids


def test_duplicate_record_identity_is_rejected():
    raw = canonical("raw")
    with pytest.raises(ValueError, match="duplicate memory view record_id"):
        validate_memory_view("raw", [raw, raw])
