from __future__ import annotations

import pytest

from orion.knowledge.identity import (
    IdentityScheme,
    ReadDecision,
    ReadReceipt,
    SourceIdentity,
    canonical_source_id,
    decide_read,
    merge_identities,
)

SCHEMA = "claim-extraction-v0"
FRAME = "frame:saturation-stopping-rules"
DIGEST = "a" * 64


# --- canonical identity: where deduplication actually happens -------------


@pytest.mark.parametrize(
    "raw",
    [
        "10.1038/s41586-021-03819-3",
        "10.1038/S41586-021-03819-3",
        "doi:10.1038/s41586-021-03819-3",
        "https://doi.org/10.1038/s41586-021-03819-3",
        "  https://doi.org/10.1038/S41586-021-03819-3  ",
    ],
)
def test_every_way_of_writing_one_doi_collapses_to_one_key(raw: str) -> None:
    identity = canonical_source_id(raw)
    assert identity.scheme is IdentityScheme.DOI
    assert str(identity) == "doi:10.1038/s41586-021-03819-3"


@pytest.mark.parametrize(
    "raw",
    [
        "arXiv:2301.00001",
        "arxiv:2301.00001v3",
        "https://arxiv.org/abs/2301.00001v3",
        "https://arxiv.org/pdf/2301.00001v3.pdf",
        "2301.00001",
    ],
)
def test_arxiv_versions_are_renditions_of_one_work_not_separate_works(raw: str) -> None:
    """v1 and v3 are the same paper. Forking identity on version would inflate
    every coverage count by however many revisions we happened to retrieve."""

    identity = canonical_source_id(raw)
    assert identity.scheme is IdentityScheme.ARXIV
    assert identity.value == "2301.00001"
    assert str(identity) == "arxiv:2301.00001"


def test_the_version_is_kept_rather_than_discarded() -> None:
    assert canonical_source_id("arxiv:2301.00001v3").version == "3"
    assert canonical_source_id("arxiv:2301.00001").version == ""


def test_old_style_arxiv_ids_are_recognised() -> None:
    identity = canonical_source_id("hep-th/9901001v2")
    assert identity.scheme is IdentityScheme.ARXIV
    assert identity.value == "hep-th/9901001"
    assert identity.version == "2"


def test_openalex_and_url_and_local_schemes_are_distinguished() -> None:
    assert canonical_source_id("https://openalex.org/W2741809807").scheme is IdentityScheme.OPENALEX
    assert canonical_source_id("https://example.org/paper").scheme is IdentityScheme.URL
    assert canonical_source_id("local:deadbeef").scheme is IdentityScheme.LOCAL


def test_an_unrecognised_identifier_is_typed_not_guessed() -> None:
    identity = canonical_source_id("some free text")
    assert identity.scheme is IdentityScheme.UNKNOWN
    assert not identity.is_resolvable


def test_an_empty_identifier_is_refused() -> None:
    with pytest.raises(ValueError):
        canonical_source_id("   ")


# --- merging: one work reached by several routes --------------------------


def test_a_work_found_by_three_routes_is_counted_once() -> None:
    """Heterogeneous search must not look like knowledge growth."""

    merged = merge_identities(
        (
            SourceIdentity("doi:10.1/x", aliases=("arxiv:2301.00001",), title="A paper"),
            SourceIdentity("arxiv:2301.00001", aliases=("openalex:W1",)),
            SourceIdentity("doi:10.1/other", title="Different work"),
        )
    )
    assert len(merged) == 2
    combined = next(item for item in merged if "doi:10.1/x" in item.keys)
    assert combined.keys == {"doi:10.1/x", "arxiv:2301.00001", "openalex:W1"}
    assert combined.title == "A paper"


def test_merging_is_transitive_across_disjoint_pairs() -> None:
    """A-B and B-C must yield one group, not two."""

    merged = merge_identities(
        (
            SourceIdentity("a", aliases=("b",)),
            SourceIdentity("c", aliases=("b",)),
        )
    )
    assert len(merged) == 1
    assert merged[0].keys == {"a", "b", "c"}


def test_unrelated_works_are_not_merged() -> None:
    merged = merge_identities(
        (SourceIdentity("a", aliases=("x",)), SourceIdentity("b", aliases=("y",)))
    )
    assert len(merged) == 2


# --- the read decision: not re-reading, without over-claiming coverage ----


def _receipt(**overrides) -> ReadReceipt:
    fields = {
        "source_id": "arxiv:2301.00001",
        "content_digest": DIGEST,
        "schema_version": SCHEMA,
        "frame_id": FRAME,
    }
    fields.update(overrides)
    return ReadReceipt(**fields)


def test_an_unseen_source_must_be_read() -> None:
    assert decide_read("arxiv:2301.00001", DIGEST, SCHEMA, FRAME, ()) is ReadDecision.UNSEEN


def test_an_exact_prior_read_is_a_cache_hit() -> None:
    assert (
        decide_read("arxiv:2301.00001", DIGEST, SCHEMA, FRAME, (_receipt(),))
        is ReadDecision.ALREADY_READ
    )


def test_a_revised_paper_is_re_read() -> None:
    assert (
        decide_read("arxiv:2301.00001", "b" * 64, SCHEMA, FRAME, (_receipt(),))
        is ReadDecision.CONTENT_CHANGED
    )


def test_a_new_extraction_schema_forces_re_extraction() -> None:
    assert (
        decide_read("arxiv:2301.00001", DIGEST, "claim-extraction-v1", FRAME, (_receipt(),))
        is ReadDecision.NEW_SCHEMA
    )


def test_reading_for_a_different_question_is_not_covered_by_the_old_read() -> None:
    """The failure this exists to prevent: believing a paper is covered because
    it was skimmed for an unrelated question."""

    assert (
        decide_read("arxiv:2301.00001", DIGEST, SCHEMA, "frame:novelty-metrics", (_receipt(),))
        is ReadDecision.NEW_FRAME
    )


def test_the_whole_receipt_set_is_considered_not_the_first_match() -> None:
    """A source read under several frames has several receipts; stopping at the
    first would report a re-read that is not needed."""

    receipts = (
        _receipt(frame_id="frame:other"),
        _receipt(frame_id=FRAME),
    )
    assert (
        decide_read("arxiv:2301.00001", DIGEST, SCHEMA, FRAME, receipts)
        is ReadDecision.ALREADY_READ
    )


def test_another_sources_receipts_never_satisfy_this_one() -> None:
    assert (
        decide_read("doi:10.1/x", DIGEST, SCHEMA, FRAME, (_receipt(),))
        is ReadDecision.UNSEEN
    )


@pytest.mark.parametrize(
    "raw", ["arXiv:2305", "arxiv:not-an-id", "https://arxiv.org/abs/12345", "arxiv:2301.1"]
)
def test_a_declared_scheme_does_not_excuse_a_malformed_identifier(raw: str) -> None:
    """Found by running the parser over the real bibliographies, not fixtures.

    The DOI path already validated shape; the arXiv path did not, so a label
    was enough to mint an identity. An unresolvable key that looks valid is
    worse than an unknown one, because it reads as covered.
    """

    assert canonical_source_id(raw).scheme is IdentityScheme.UNKNOWN
