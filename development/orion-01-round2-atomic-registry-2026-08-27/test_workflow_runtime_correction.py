from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ACTIVE_WORKFLOW = ROOT / ".github/workflows/orion01-round2-atomic-registry.yml"
ARCHIVED_WORKFLOW = HERE / "historical/orion01-round2-atomic-registry.original.yml"
CI_REQUIREMENTS = HERE / "requirements-ci.txt"
CORRECTION = HERE / "WORKFLOW_RUNTIME_CORRECTION_V1.json"
RESULT = HERE / "ORION01_ROUND2_ATOMIC_RESULTS.json"
PACKAGE_MANIFEST = HERE / "PACKAGE_MANIFEST_R2.json"

ORIGINAL_WORKFLOW_SHA256 = "a88ad02bafa4f382dc398cce418e35ac38df11a241e760133cbc189449cf4c19"
ORIGINAL_WORKFLOW_BYTES = 6262
RESULT_SHA256 = "db1253e52a44741613abb9217eb4a865d190c3948abdab9f8fbd344ada035efd"
PYZX_COMMIT = "dade7d46f193635bbdaefd8fcde837f9449fddc5"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_original_workflow_is_preserved_and_package_manifest_remains_verifiable() -> None:
    correction = json.loads(CORRECTION.read_text())
    manifest = json.loads(PACKAGE_MANIFEST.read_text())

    assert ARCHIVED_WORKFLOW.stat().st_size == ORIGINAL_WORKFLOW_BYTES
    assert _sha(ARCHIVED_WORKFLOW) == ORIGINAL_WORKFLOW_SHA256
    assert correction["original_workflow"] == {
        "bytes": ORIGINAL_WORKFLOW_BYTES,
        "path": ARCHIVED_WORKFLOW.relative_to(ROOT).as_posix(),
        "sha256": ORIGINAL_WORKFLOW_SHA256,
    }

    workflow_entries = [
        entry for entry in manifest["entries"] if entry["sha256"] == ORIGINAL_WORKFLOW_SHA256
    ]
    assert workflow_entries == [correction["original_workflow"]]


def test_runtime_correction_does_not_change_the_scientific_outcome() -> None:
    correction = json.loads(CORRECTION.read_text())
    result = json.loads(RESULT.read_text())

    assert _sha(RESULT) == RESULT_SHA256
    assert result["outcome"]["terminal"] == "CANNOT_CHECK_MOVE_COMPLETENESS"
    assert correction["failed_ci_run_id"] == 33154940099
    assert correction["scientific_authority_delta"] == "NONE"
    assert correction["paper_freeze_authority"] is False
    assert correction["submission_authority"] is False
    assert correction["top_tier_authority"] is False
    assert correction["original_outcome_terminal"] == "CANNOT_CHECK_MOVE_COMPLETENESS"


def test_corrected_workflow_uses_a_minimal_pinned_verifier_runtime() -> None:
    correction = json.loads(CORRECTION.read_text())
    workflow = ACTIVE_WORKFLOW.read_text()
    requirements = CI_REQUIREMENTS.read_text().splitlines()

    assert _sha(ACTIVE_WORKFLOW) == correction["active_workflow"]["sha256"]
    assert ACTIVE_WORKFLOW.stat().st_size == correction["active_workflow"]["bytes"]
    assert _sha(CI_REQUIREMENTS) == correction["ci_requirements"]["sha256"]
    assert CI_REQUIREMENTS.stat().st_size == correction["ci_requirements"]["bytes"]
    assert "requirements-ci.txt" in workflow
    assert "requirements-lock.txt" not in workflow
    assert "--no-deps" in workflow
    assert PYZX_COMMIT in workflow
    assert "ORION-01 dependency custody" in workflow
    assert "shared replay dependency custody violation" in workflow
    assert "src/*|packages/*|pyproject.toml" in workflow
    assert "Paper-1 lane scope violation" not in workflow
    assert not any(line.startswith("blist==") for line in requirements)

    declared = {line for line in requirements if line and not line.startswith("#")}
    assert declared == {
        "lark==1.3.1",
        "numpy==2.4.6",
        "pyperclip==1.11.0",
        "pytest==8.4.2",
        "ruff==0.16.5",
        "tqdm==4.70.0",
        "typing_extensions==4.16.0",
    }
