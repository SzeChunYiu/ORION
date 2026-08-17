from __future__ import annotations

from orion.study.p3_obstruction_certificate import (
    FALSIFIER_IDS,
    apply_falsifier,
    example_hard_certificate,
    verify_certificate,
)


def _artifacts() -> dict[str, bytes]:
    return {
        "source-a": b"local view A; attribution=author:a; referent=entity-1",
        "source-b": b"local view B; attribution=author:b; referent=entity-2",
    }


def test_honest_certificate_verifies() -> None:
    artifacts = _artifacts()
    certificate = example_hard_certificate(artifacts)
    verdict = verify_certificate(certificate, artifacts)
    assert verdict.ok is True
    assert verdict.status == "HARD"
    assert verdict.blockers == ()
    assert certificate.content_hash
    assert len(certificate.content_hash) == 64


def test_all_required_falsifiers_are_present() -> None:
    required = {
        "source_content_substitution",
        "attribution_swap",
        "missing_preservation_condition",
        "actually_valid_transform",
        "missing_anchor",
        "corrupted_cycle",
        "ingestion_order_change",
        "equivalent_views_represented_differently",
    }
    assert set(FALSIFIER_IDS) == required


def test_certificate_falsifiers_reject_or_are_order_invariant() -> None:
    artifacts = _artifacts()
    certificate = example_hard_certificate(artifacts)
    for name in FALSIFIER_IDS:
        result = apply_falsifier(name, certificate, artifacts)
        if name == "ingestion_order_change":
            original, swapped = result
            assert original == swapped
            continue
        assert result.ok is False
        assert result.blockers
