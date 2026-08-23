from pathlib import Path

from orion.programme.q_series_content_binding import (
    BINDING_SCHEMA,
    git_blob_sha1,
    inspect_q_series_content_binding,
    require_q_series_content_binding,
)
from orion.registry import Q_SERIES_SYNC_EPOCH


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_git_blob_sha1_matches_known_empty_blob():
    assert git_blob_sha1(b"") == "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"


def test_canonical_q_series_publication_bytes_match_recursive_v3_binding():
    report = inspect_q_series_content_binding(REPO_ROOT)
    assert report.sync_epoch == Q_SERIES_SYNC_EPOCH
    assert report.files_bound >= 35
    assert report.drifted_paths == ()
    assert report.missing_paths == ()
    assert report.clean is True
    require_q_series_content_binding(REPO_ROOT)
    payload = report.as_json()
    assert payload["schema"] == BINDING_SCHEMA
    assert payload["grants_scientific_authority"] is False
    assert payload["grants_novelty_authority"] is False
    assert payload["predicts_journal_acceptance"] is False
