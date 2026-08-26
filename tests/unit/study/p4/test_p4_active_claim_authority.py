"""P4 has one bounded current claim without erasing adverse authority states."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / "papers/paper-04-verified-scientific-discovery"
AUTHORITY = PAPER / "P4_ACTIVE_CLAIM_AUTHORITY_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _strict_record() -> dict:
    def reject_duplicates(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"duplicate JSON object key: {key}")
            value[key] = item
        return value

    return json.loads(AUTHORITY.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicates)


def test_p4_active_terminal_is_transcribed_not_promoted() -> None:
    record = _strict_record()
    assert record["active_terminal"] == (
        "P4_WIDER_SCIENTIFIC_PROMOTION_AUTHORITY_SUPPORTED__"
        "BOUNDED_EXACT_HETEROGENEOUS_CONTRACTS__A3_CANNOT_CHECK"
    )
    assert record["provenance"]["kind"] == "LANE_TRANSCRIPTION_PENDING_AUTHOR_DESIGNATION"
    assert record["lifecycle_state"] == "ACTIVE_TRANSCRIBED_NOT_AUTHOR_DESIGNATED"
    assert record["external_validation"] == "CANNOT_CHECK"
    assert record["promotion_allowed"] is False


def test_p4_has_one_primary_endpoint_and_retains_axis_boundaries() -> None:
    record = _strict_record()
    endpoint = record["primary_endpoint"]
    assert endpoint["endpoint_id"] == "P4.H1.FALSE_AUTHORITY_PROMOTION_RATE"
    assert endpoint["role"] == "SOLE_PRIMARY_OUTCOME_IN_CURRENT_MANUSCRIPT"
    assert endpoint["bounded_protected_v2_observation"] == {
        "governed_pipeline": "0/360",
        "strongest_frozen_mechanism_proxy": "180/360",
        "paired_effect": -0.5,
        "paired_ci95": [-0.553, -0.447],
    }
    distinctions = record["retained_distinctions"]
    assert distinctions["attainability"]["status"] == "FORMAL_CONDITION_ONLY"
    assert distinctions["p4_h3_v2"]["status"] == "NOT_SUPPORTED"
    assert distinctions["p4_h3_v3"]["status"] == "SUPPORTED_FOR_EXACT_AXIS_ONLY"
    assert distinctions["naturalistic_external_panel"]["status"] == "CANNOT_CHECK"
    assert "Nine of ten" in distinctions["p4_h3_v3"]["boundary"]


def test_p4_protected_audit_cannot_be_promoted_to_external_gold() -> None:
    limits = _strict_record()["protected_audit_limits"]
    assert "diagnostic-only" in limits["excluded_live_arm"]
    disposition = limits["p4_des_01"]
    assert disposition["terminal"] == "EXTERNAL_PROMOTION_TERMINAL_GOLD_UNAVAILABLE"
    assert disposition["registered_arm_cases"] == 1500
    assert disposition["mechanically_executed_arm_cases"] == 900
    assert disposition["unavailable_arm_cases"] == 600
    assert disposition["externally_terminal_scored_cases"] == 0


def test_p4_all_reader_visible_sources_are_content_bound() -> None:
    record = _strict_record()
    for binding in record["evidence_bindings"].values():
        artifact = ROOT / binding["artifact"]
        assert artifact.is_file(), binding
        assert binding["sha256"] == _sha(artifact), binding
    source = record["provenance"]["transcribed_from"]
    assert source["sha256"] == _sha(ROOT / source["artifact"])


def test_p4_readme_has_unambiguous_current_pointers() -> None:
    text = (PAPER / "README.md").read_text(encoding="utf-8")
    assert text.count("**Current science manuscript:** `manuscript/main.tex`") == 1
    assert text.count("**Current authority:** `P4_ACTIVE_CLAIM_AUTHORITY_V1.json`") == 1
    assert text.count("**Current readiness:** `CURRENT_JOURNAL_READINESS_V1.md`") == 1
    assert set(re.findall(r"P4_ACTIVE_CLAIM_AUTHORITY_V\d+\.json", text)) == {
        "P4_ACTIVE_CLAIM_AUTHORITY_V1.json"
    }


def test_p4_readiness_versions_current_state_without_mutating_v2() -> None:
    historical = PAPER / "JOURNAL_READINESS.md"
    current = PAPER / "CURRENT_JOURNAL_READINESS_V1.md"
    assert _sha(historical) == "3d9a461eceaf8be410de4852beed70d26a74f0861698ffd0b094347b03ba0126"
    text = current.read_text(encoding="utf-8")
    assert "**Current terminal:** `CANNOT_CHECK`" in text
    assert "**Current lifecycle:** `CURRENT_PACKAGE_NOT_SUBMISSION_READY`" in text
    assert "P4_ACTIVE_CLAIM_AUTHORITY_V1.json" in text
    assert "JOURNAL_READINESS.md" in text
    assert "historical protected-V2" in text


def test_p4_scaffolding_manifest_cannot_claim_peer_review_ready() -> None:
    manifest = json.loads((PAPER / "journal_package/MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["package_status"] == "SCAFFOLDING"
    assert manifest["declared_paper_terminal"] == (
        "CANNOT_CHECK__CURRENT_PACKAGE_NOT_SUBMISSION_READY"
    )
