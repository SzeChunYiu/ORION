"""P1/P3 reader surfaces must resolve to one bounded active authority each."""

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
PAPERS = {
    "P1": ROOT / "papers" / "paper-01-recursive-epistemic-reconstruction",
    "P3": ROOT / "papers" / "paper-03-global-knowledge-portrait",
}
EXPECTED_TERMINALS = {
    "P1": (
        "P1_WIDER_ARCHITECTURE_CLAIM_SUPPORTED__"
        "BOUNDED_EXACT_HETEROGENEOUS_CONTRACTS__A3_CANNOT_CHECK"
    ),
    "P3": (
        "P3_WIDER_SCIENTIFIC_COMPATIBILITY_CLAIM_SUPPORTED__"
        "BOUNDED_EXACT_STRUCTURED_CONTRACTS__A3_CANNOT_CHECK"
    ),
}
EXPECTED_PACKAGE_TERMINALS = {
    "P1": "BOUNDED_MECHANICAL_CLAIM_SUPPORTED__CURRENT_PACKAGE_NOT_SUBMISSION_READY",
    "P3": "SCOPED_STRUCTURED_INTEGRATION_RETAINED__CURRENT_PACKAGE_NOT_SUBMISSION_READY",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _record(paper_id: str) -> dict:
    return json.loads(
        (PAPERS[paper_id] / f"{paper_id}_ACTIVE_CLAIM_AUTHORITY_V1.json").read_text(
            encoding="utf-8"
        )
    )


def test_records_transcribe_existing_terminals_and_bind_every_source() -> None:
    for paper_id, paper in PAPERS.items():
        record = _record(paper_id)
        assert record["schema"] == "ACTIVE_CLAIM_AUTHORITY_V1"
        assert record["paper_id"] == paper_id
        assert record["active_terminal"] == EXPECTED_TERMINALS[paper_id]
        assert record["primary_endpoint"] == record["active_terminal"]
        assert record["provenance"]["kind"] == "LANE_TRANSCRIPTION_PENDING_AUTHOR_DESIGNATION"
        assert record["lifecycle_state"] == "ACTIVE_TRANSCRIBED_NOT_AUTHOR_DESIGNATED"
        assert record["external_validation"] == "CANNOT_CHECK"

        source = record["provenance"]["transcribed_from"]
        source_path = ROOT / source["artifact"]
        assert _sha256(source_path) == source["sha256"]
        source_line = source_path.read_text(encoding="utf-8").splitlines()[source["line"] - 1]
        assert record["active_terminal"] in source_line

        for binding in record["evidence_bindings"].values():
            artifact = ROOT / binding["artifact"]
            assert artifact.is_file(), binding
            assert _sha256(artifact) == binding["sha256"], binding["artifact"]

        readiness = record["submission_readiness"]
        assert readiness["state"] == "NOT_SUBMISSION_READY"
        assert readiness["terminal"] == EXPECTED_PACKAGE_TERMINALS[paper_id]
        manifest = ROOT / readiness["artifact"]
        assert _sha256(manifest) == readiness["sha256"]
        manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
        assert manifest_data["package_status"] == "SUPERSEDED"
        assert manifest_data["package_authority"]["current_submission_authorized"] is False


def test_reader_surfaces_are_digest_aligned_to_v1() -> None:
    records = {record.paper: record for record in audit_alignment(ROOT)}
    for paper in PAPERS.values():
        record = records[paper.name]
        assert not record.disagreeing, record.cited
        assert not record.unbound, record.cited
        assert set(record.cited) >= {"manuscript", "readiness"}
        assert all(versions == {"1"} for versions in record.cited.values())


def test_v1_is_the_only_non_stale_authority_for_each_paper() -> None:
    chains = authority_chains(ROOT / "papers")
    for paper in PAPERS.values():
        assert chains[paper.name]["active"].endswith("_V1.json")
        assert chains[paper.name]["superseded"] == []
    assert audit_staleness(ROOT).exit_code == STALENESS_PASS


def test_primary_endpoints_are_declared_and_distinct() -> None:
    report = audit_endpoints(ROOT)
    selected = {
        endpoint.paper: endpoint
        for endpoint in report.endpoints
        if endpoint.paper in {paper.name for paper in PAPERS.values()}
    }
    assert set(selected) == {paper.name for paper in PAPERS.values()}
    for paper_id, paper in PAPERS.items():
        endpoint = selected[paper.name]
        assert endpoint.terminal == EXPECTED_TERMINALS[paper_id]
        assert endpoint.source == f"{paper_id}_ACTIVE_CLAIM_AUTHORITY_V1.json"
    assert len({endpoint.terminal for endpoint in selected.values()}) == 2
    assert report.collisions == {}


def test_each_readme_designates_exactly_one_current_pointer_of_each_kind() -> None:
    records = {record.paper: record for record in audit_pointers(ROOT)}
    for paper_id, paper in PAPERS.items():
        record = records[paper.name]
        assert record.counts == {"manuscript": 1, "authority": 1, "readiness": 1}
        assert record.names["manuscript"] == ("manuscript/main.tex",)
        assert record.names["authority"] == (f"{paper_id}_ACTIVE_CLAIM_AUTHORITY_V1.json",)
        assert record.names["readiness"] == ("JOURNAL_READINESS.md",)
        assert not record.ambiguous
        assert not record.absent
        assert set(
            record.names["manuscript"] + record.names["authority"] + record.names["readiness"]
        ) <= set(record.designated)


def test_p3_readiness_fails_closed_on_the_superseded_package() -> None:
    readiness = (PAPERS["P3"] / "JOURNAL_READINESS.md").read_text(encoding="utf-8")
    readme = (PAPERS["P3"] / "README.md").read_text(encoding="utf-8")
    expected = EXPECTED_PACKAGE_TERMINALS["P3"]
    assert expected in readiness
    assert expected in readme
    assert "**Current terminal:** `PEER_REVIEW_READY`" not in readiness
    assert "`ORION-P3 = PEER_REVIEW_READY`" not in readiness
    assert "**Status:** `PEER_REVIEW_READY`" not in readme
