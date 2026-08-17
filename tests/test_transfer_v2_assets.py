"""LOCAL_ENGINEERING_ONLY: #136 structural-transfer substrate.

Not scientific cross-domain transfer evidence for #286.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from orion.transfer.v2.manifest import load_and_validate_manifest
from orion.transfer.v2.portfolio import build_portfolio
from orion.transfer.v2.models import problem_signature_from_payload
from orion.transfer.v2.registry import TransferRegistry

ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "research" / "verified-structural-transfer-v2"


def test_all_five_v2_manifests_validate_and_remain_outcome_blind():
    manifests = sorted((ASSET_ROOT / "manifests").glob("ORION-P*.json"))
    assert len(manifests) == 5
    for path in manifests:
        payload, digest = load_and_validate_manifest(path)
        assert digest.startswith("sha256:")
        assert payload["status"] == "V2_FUTURE_STUDY"
        assert payload["outcome_accessed"] is False
        assert payload["execution_authority"] == "NONE"
        assert payload["v1_protocol_mutated"] is False
        assert payload["local_evidence_authority"] == "LOCAL_ENGINEERING_ONLY"
        assert payload["requires_new_protocol_version"] is True


def test_v2_schema_assets_are_well_formed_json_schema_objects():
    expected = {
        "PROBLEM_SIGNATURE_SCHEMA_V2.json",
        "ALGORITHM_CELL_SCHEMA_V2.json",
        "TRANSFER_RECEIPT_SCHEMA_V2.json",
        "PORTFOLIO_RECEIPT_SCHEMA_V2.json",
        "PAPER_V2_MANIFEST_SCHEMA_V1.json",
    }
    paths = {path.name: path for path in (ASSET_ROOT / "schemas").glob("*.json")}
    assert set(paths) == expected
    for path in paths.values():
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["$schema"].endswith("2020-12/schema")
        assert payload["type"] == "object"
        assert payload["additionalProperties"] is False
        assert payload["required"]


def test_known_answer_catalog_roundtrips_and_selects_five_cells():
    registry = TransferRegistry.load(ASSET_ROOT / "fixtures" / "CANDIDATE_CATALOG_V2.json")
    target = problem_signature_from_payload(
        json.loads((ASSET_ROOT / "fixtures" / "KNOWN_ANSWER_TARGET_V2.json").read_text(encoding="utf-8"))
    )
    evidence = json.loads((ASSET_ROOT / "fixtures" / "KNOWN_ANSWER_EVIDENCE_V2.json").read_text(encoding="utf-8"))
    receipt = build_portfolio(target, registry, evidence)
    receipt.verify()
    assert len(receipt.decisions) == 5
    assert len(receipt.selected_cell_ids) == 5


def test_cli_portfolio_is_deterministic(tmp_path: Path):
    args = [
        sys.executable,
        "-m",
        "orion.transfer.v2",
        "portfolio",
        "--catalog",
        str(ASSET_ROOT / "fixtures" / "CANDIDATE_CATALOG_V2.json"),
        "--target",
        str(ASSET_ROOT / "fixtures" / "KNOWN_ANSWER_TARGET_V2.json"),
        "--evidence",
        str(ASSET_ROOT / "fixtures" / "KNOWN_ANSWER_EVIDENCE_V2.json"),
    ]
    first = subprocess.check_output(args, cwd=ROOT, text=True)
    second = subprocess.check_output(args, cwd=ROOT, text=True)
    assert first == second
    assert json.loads(first)["portfolio_version"] == "ORION_TRANSFER_PORTFOLIO_V2"


def test_cli_manifest_validator_reports_valid():
    output = subprocess.check_output(
        [
            sys.executable,
            "-m",
            "orion.transfer.v2",
            "validate-manifest",
            "--manifest",
            str(ASSET_ROOT / "manifests" / "ORION-P5.json"),
        ],
        cwd=ROOT,
        text=True,
    )
    payload = json.loads(output)
    assert payload["valid"] is True
    assert payload["manifest"]["paper_id"] == "ORION-P5"
