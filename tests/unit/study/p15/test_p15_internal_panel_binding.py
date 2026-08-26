"""P15 internal-panel evidence binding and failure ledger stay bounded."""

from __future__ import annotations

import json
from hashlib import sha1
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / "papers/orion-25-orion-research-harness"
BINDING = PAPER / "P15_INTERNAL_PANEL_EVIDENCE_BINDING_V1.json"
FAILURE_LEDGER = PAPER / "P15_FAILURE_LEDGER_V1.md"


def _git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode()
    return sha1(header + payload).hexdigest()


def test_binding_classifies_internal_unit_test_evidence_only() -> None:
    binding = json.loads(BINDING.read_text(encoding="utf-8"))
    assert binding["evidence_class"] == "INTERNAL_UNIT_TEST_EVIDENCE"
    assert binding["status"] == "SUPPORTED_INTERNAL_PANEL"
    assert binding["population_inference"] is False
    assert binding["consolidation"]["decision_id"] == "D8"
    assert binding["consolidation"]["with"] == "Q3"
    assert binding["scientific_authority_delta"] == "NONE"
    assert "POPULATION_INFERENCE" in binding["forbidden_promotions"]
    assert "EXTERNAL_REPLICATION" in binding["forbidden_promotions"]


def test_p15b_label_is_recorded_as_having_no_distinct_artifact() -> None:
    binding = json.loads(BINDING.read_text(encoding="utf-8"))
    assert binding["issue_label"] == "P15B"
    assert binding["label_repository_status"] == "NO_DISTINCT_ARTIFACT"
    assert "none was invented" in binding["label_note"]


def test_bound_layers_match_files_and_the_v3_authority() -> None:
    binding = json.loads(BINDING.read_text(encoding="utf-8"))
    v3 = json.loads((PAPER / "P15_ACTIVE_CLAIM_AUTHORITY_V3.json").read_text(encoding="utf-8"))
    layers = binding["bound_result_layers"]
    assert set(layers) == set(v3["result_authority"])
    for key, record in layers.items():
        path = ROOT / record["artifact"]
        assert path.is_file(), key
        assert record["git_blob_sha"] == _git_blob_sha(path)
        assert record["git_blob_sha"] == v3["result_authority"][key]["git_blob_sha"]


def test_failure_ledger_retains_blocked_and_adverse_entries() -> None:
    text = FAILURE_LEDGER.read_text(encoding="utf-8")
    assert "P15A_ACQUISITION_BLOCKED_NO_SCIENTIFIC_RESULT" in text
    assert "6 attempts, 0 detections" in text
    assert "CHAIN_AS_SCIENCE" in text
    assert "6/6" in text
    assert "12" in text
    assert "Retained-run policy" in text
    assert "never deleted" in text
    assert "manuscript/chapters/02-threat-model.tex" in text


def test_claim_ledger_correction_points_at_the_binding_and_v3() -> None:
    text = (PAPER / "CLAIM_EVIDENCE_LEDGER.md").read_text(encoding="utf-8")
    assert "P15_ACTIVE_CLAIM_AUTHORITY_V3.json" in text
    assert "P15_BOUNDED_SEI_PROVENANCE_ATTESTATION_EARNED" in text
    assert "SUPPORTED_INTERNAL_PANEL / population_inference:false" in text
    assert "NO_DISTINCT_ARTIFACT" in text
    assert "P15_FAILURE_LEDGER_V1.md" in text
