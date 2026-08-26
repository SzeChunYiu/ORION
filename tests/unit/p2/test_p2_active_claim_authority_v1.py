"""P2's bounded endpoint and current-package boundary must remain aligned."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from orion.programme.authority_alignment import audit_repository as audit_alignment
from orion.programme.authority_staleness import (
    EXIT_PASS as STALENESS_PASS,
    audit_repository as audit_staleness,
    authority_chains,
)
from orion.programme.primary_endpoint import audit_repository as audit_endpoints
from orion.programme.readme_pointers import audit_repository as audit_pointers


ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "paper-02-open-world-scientific-discovery"
AUTHORITY = PAPER / "P2_ACTIVE_CLAIM_AUTHORITY_V1.json"
ACTIVE_ENDPOINT = "P2_NARROWED"
PACKAGE_TERMINAL = "P2_NARROWED_RETAINED__CURRENT_PACKAGE_NOT_SUBMISSION_READY"
SWIFT_TERMINAL = (
    "P2_SWIFT_V3_CROSS_REVIEW_CONTROLLER_FAILS_ONE_OR_MORE_PUBLIC_"
    "DEVELOPMENT_GATES_REQUIRES_SUCCESSOR"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _record() -> dict:
    return json.loads(AUTHORITY.read_text(encoding="utf-8"))


def test_authority_transcribes_the_bounded_endpoint_and_binds_sources() -> None:
    record = _record()
    assert record["schema"] == "ACTIVE_CLAIM_AUTHORITY_V1"
    assert record["paper_id"] == "P2"
    assert record["active_terminal"] == ACTIVE_ENDPOINT
    assert record["primary_endpoint"] == ACTIVE_ENDPOINT
    assert record["provenance"]["kind"] == "LANE_TRANSCRIPTION_PENDING_AUTHOR_DESIGNATION"
    assert record["lifecycle_state"] == "ACTIVE_TRANSCRIBED_NOT_AUTHOR_DESIGNATED"
    assert record["external_validation"] == "CANNOT_CHECK"

    source = record["provenance"]["transcribed_from"]
    source_path = ROOT / source["artifact"]
    assert _sha256(source_path) == source["sha256"]
    line = source_path.read_text(encoding="utf-8").splitlines()[source["line"] - 1]
    assert ACTIVE_ENDPOINT in line

    for binding in record["evidence_bindings"].values():
        artifact = ROOT / binding["artifact"]
        assert artifact.is_file(), binding
        assert _sha256(artifact) == binding["sha256"], binding["artifact"]

    readiness = record["submission_readiness"]
    assert readiness["state"] == "NOT_SUBMISSION_READY"
    assert readiness["terminal"] == PACKAGE_TERMINAL
    manifest = ROOT / readiness["artifact"]
    assert _sha256(manifest) == readiness["sha256"]
    manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
    assert manifest_data["declared_paper_terminal"] == PACKAGE_TERMINAL
    assert manifest_data["package_status"] == "SUPERSEDED"
    assert manifest_data["package_authority"]["current_submission_authorized"] is False


def test_adverse_u4_transport_and_censoring_boundaries_are_preserved() -> None:
    record = _record()
    boundaries = "\n".join(record["adverse_and_open_boundaries"])
    assert SWIFT_TERMINAL in boundaries
    assert "u4 was better on both endpoints in all five reviews" in boundaries
    assert "CANNOT_CHECK_STRONG_DONOR_OR_TRANSFER_BINDING_UNAVAILABLE" in boundaries
    assert "unavailable routes" in boundaries
    assert "resource censoring" in boundaries
    assert "external superiority CANNOT_CHECK" in boundaries


def test_manuscript_and_current_readiness_are_digest_aligned_to_v1() -> None:
    records = {record.paper: record for record in audit_alignment(ROOT)}
    record = records[PAPER.name]
    assert not record.disagreeing, record.cited
    assert not record.unbound, record.cited
    assert set(record.cited) >= {"manuscript", "readiness"}
    assert all(versions == {"1"} for versions in record.cited.values())


def test_v1_is_the_only_non_stale_p2_authority() -> None:
    chain = authority_chains(ROOT / "papers")[PAPER.name]
    assert chain["active"] == "P2_ACTIVE_CLAIM_AUTHORITY_V1.json"
    assert chain["superseded"] == []
    assert audit_staleness(ROOT).exit_code == STALENESS_PASS


def test_p2_has_one_declared_primary_endpoint() -> None:
    report = audit_endpoints(ROOT)
    endpoint = next(item for item in report.endpoints if item.paper == PAPER.name)
    assert endpoint.terminal == ACTIVE_ENDPOINT
    assert endpoint.source == "P2_ACTIVE_CLAIM_AUTHORITY_V1.json"
    assert report.collisions == {}


def test_readme_designates_one_current_manuscript_authority_and_readiness() -> None:
    record = next(item for item in audit_pointers(ROOT) if item.paper == PAPER.name)
    assert record.counts == {"manuscript": 1, "authority": 1, "readiness": 1}
    assert record.names["manuscript"] == ("manuscript/main.tex",)
    assert record.names["authority"] == ("P2_ACTIVE_CLAIM_AUTHORITY_V1.json",)
    assert record.names["readiness"] == ("JOURNAL_READINESS.md",)
    assert not record.ambiguous
    assert not record.absent
    assert set(
        record.names["manuscript"] + record.names["authority"] + record.names["readiness"]
    ) <= set(record.designated)


def test_current_readiness_fails_closed_while_historical_attestation_is_retained() -> None:
    readiness = (PAPER / "JOURNAL_READINESS.md").read_text(encoding="utf-8")
    readme = (PAPER / "README.md").read_text(encoding="utf-8")
    historical = (PAPER / "evidence" / "PEER_REVIEW_READY_BOUNDED_V2.md").read_text(
        encoding="utf-8"
    )
    assert PACKAGE_TERMINAL in readiness
    assert PACKAGE_TERMINAL in readme
    assert "**Current terminal:** `ORION-P2 = PEER_REVIEW_READY`" not in readiness
    assert "`ORION-P2 = PEER_REVIEW_READY` on the narrowed claim" not in readiness
    assert "Historical terminal recorded at the time" in historical
    assert "ORION-P2 = PEER_REVIEW_READY" in historical
