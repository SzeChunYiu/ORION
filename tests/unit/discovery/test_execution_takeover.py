import copy
import importlib
import os
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "research/orion-discovery-v3/EXECUTION_TAKEOVER_MANIFEST_V1.json"


def _takeover_api():
    try:
        return importlib.import_module("orion.discovery.execution_takeover")
    except ModuleNotFoundError as exc:
        pytest.fail(f"the execution takeover module is missing: {exc}")


def test_v3_workflow_installs_project_dependencies_before_hostile_suite() -> None:
    workflow = (ROOT / ".github/workflows/orion-discovery-v3.yml").read_text()

    install_at = workflow.find("python -m pip install -e .")
    hostile_at = workflow.find("python -m pytest -q tests/unit/discovery/test_frontier_dominance.py")

    assert install_at >= 0, "the V3 workflow must install ORION's declared dependencies"
    assert install_at < hostile_at, "project dependencies must be installed before test collection"


def test_canonical_takeover_manifest_is_valid_but_not_pretended_ready() -> None:
    api = _takeover_api()

    assert MANIFEST.exists(), "the newer 13-job queue needs a canonical machine-readable manifest"
    manifest = api.load_manifest(MANIFEST)
    api.validate_manifest(manifest)

    assert len(manifest["jobs"]) == 13
    assert api.ready_job_ids(manifest) == ()


def test_manifest_rejects_duplicate_canonical_job_identities() -> None:
    api = _takeover_api()
    manifest = api.load_manifest(MANIFEST)
    manifest["jobs"].append(copy.deepcopy(manifest["jobs"][0]))

    with pytest.raises(api.ManifestError, match="duplicate canonical job id"):
        api.validate_manifest(manifest)


def test_manifest_rejects_false_exact_aliases() -> None:
    api = _takeover_api()
    manifest = api.load_manifest(MANIFEST)
    predecessor = manifest["jobs"][0]["predecessors"][0]
    predecessor["relationship"] = "EXACT_ALIAS"
    predecessor["scientific_question_sha256"] = "0" * 64

    with pytest.raises(api.ManifestError, match="exact alias question hash mismatch"):
        api.validate_manifest(manifest)


def test_takeover_checker_reports_blocked_queue_without_pretending_execution() -> None:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / "src")

    completed = subprocess.run(
        [sys.executable, "scripts/check_orion_execution_takeover.py"],
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == (
        "ORION_DISCOVERY_V3_TAKEOVER_VALID jobs=13 ready=0 blocked=13"
    )
