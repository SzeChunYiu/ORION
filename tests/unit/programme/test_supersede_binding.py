"""The reconciliation must satisfy the baseline's conditions, not merely run."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

import pytest

from orion.programme.supersede_binding import (
    SupersedeRefused, apply, parse_sums, plan,
)

NOW = datetime(2026, 8, 28, 12, 0, 0, tzinfo=timezone.utc)


def _paper(tmp_path, body=b"original\n"):
    root = tmp_path
    d = root / "papers" / "orion-xx-example"
    d.mkdir(parents=True)
    m = d / "MANUSCRIPT.md"
    m.write_bytes(body)
    stable = b"stable\n"
    other = d / "UNCHANGED.md"
    other.write_bytes(stable)
    sums = d / "SHA256SUMS"
    sums.write_text(
        f"{hashlib.sha256(body).hexdigest()}  papers/orion-xx-example/MANUSCRIPT.md\n"
        f"{hashlib.sha256(stable).hexdigest()}  papers/orion-xx-example/UNCHANGED.md\n"
    )
    return root, d, m, sums


def test_a_hash_only_rewrite_is_refused(tmp_path):
    """Nothing moved -> there is no supersession, only a manifest refresh."""
    root, _d, _m, sums = _paper(tmp_path)
    with pytest.raises(SupersedeRefused, match="nothing moved"):
        plan(root, sums, reason="tidy up", authority_reference="#1")


def test_a_reconciliation_without_a_reason_is_refused(tmp_path):
    root, _d, m, sums = _paper(tmp_path)
    m.write_bytes(b"corrected\n")
    with pytest.raises(SupersedeRefused, match="requires a stated reason"):
        plan(root, sums, reason="   ", authority_reference="#1")


def test_a_reconciliation_without_an_authority_reference_is_refused(tmp_path):
    root, _d, m, sums = _paper(tmp_path)
    m.write_bytes(b"corrected\n")
    with pytest.raises(SupersedeRefused, match="authority reference"):
        plan(root, sums, reason="remove unsupported claim", authority_reference="")


def test_a_missing_file_is_a_deletion_not_a_digest_to_refresh(tmp_path):
    root, _d, m, sums = _paper(tmp_path)
    m.unlink()
    with pytest.raises(SupersedeRefused, match="absent on disk"):
        plan(root, sums, reason="remove unsupported claim", authority_reference="#1")


def test_the_historical_closure_is_retained(tmp_path):
    root, d, m, sums = _paper(tmp_path)
    before = parse_sums(sums)
    m.write_bytes(b"corrected\n")
    sup = plan(root, sums, reason="remove unsupported claim", authority_reference="#1634")
    rec = json.loads(apply(root, sup, now=NOW).read_text())
    # every pre-change digest survives the change
    assert rec["historical_render_closure"] == before
    assert rec["replacement_digests"]["papers/orion-xx-example/MANUSCRIPT.md"] == \
        hashlib.sha256(b"corrected\n").hexdigest()


def test_current_submission_authority_is_denied(tmp_path):
    root, _d, m, sums = _paper(tmp_path)
    m.write_bytes(b"corrected\n")
    sup = plan(root, sums, reason="remove unsupported claim", authority_reference="#1634")
    rec = json.loads(apply(root, sup, now=NOW).read_text())
    assert rec["current_submission_authority"] is False
    assert rec["scientific_authority_delta"] == "NONE"


def test_only_moved_paths_are_reported_as_moved(tmp_path):
    root, _d, m, sums = _paper(tmp_path)
    m.write_bytes(b"corrected\n")
    sup = plan(root, sums, reason="remove unsupported claim", authority_reference="#1634")
    assert sup.moved_paths == ("papers/orion-xx-example/MANUSCRIPT.md",)
    assert json.loads(apply(root, sup, now=NOW).read_text())["unchanged_path_count"] == 1


def test_the_manifest_describes_its_files_afterwards(tmp_path):
    """The whole point: the paper stops drifting."""
    root, d, m, sums = _paper(tmp_path)
    m.write_bytes(b"corrected\n")
    sup = plan(root, sums, reason="remove unsupported claim", authority_reference="#1634")
    apply(root, sup, now=NOW)
    for rel, digest in parse_sums(sums).items():
        assert hashlib.sha256((root / rel).read_bytes()).hexdigest() == digest


def test_history_is_never_overwritten(tmp_path):
    root, _d, m, sums = _paper(tmp_path)
    m.write_bytes(b"corrected\n")
    sup = plan(root, sums, reason="remove unsupported claim", authority_reference="#1634")
    apply(root, sup, now=NOW)
    m.write_bytes(b"corrected again\n")
    sup2 = plan(root, sums, reason="second correction", authority_reference="#1634")
    with pytest.raises(SupersedeRefused, match="refusing to overwrite history"):
        apply(root, sup2, now=NOW)
