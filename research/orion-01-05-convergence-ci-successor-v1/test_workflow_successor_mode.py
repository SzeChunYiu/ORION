import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/orion-01-05-convergence-v1.yml"
MANIFEST = ROOT / "research/orion-01-05-convergence-v1/DONOR_MANIFEST_V1.json"
FROZEN_BASE = "b1e65d4445a9b2ef5aa44f7adc2838f968f84ff1"


def test_workflow_uses_strict_diff_only_for_the_frozen_v1_event() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "github.event.before" in workflow
    assert f'if [[ "$PR_BASE_SHA" == "{FROZEN_BASE}" ]]; then' in workflow
    assert '--check-diff --event-base "$PR_BASE_SHA"' in workflow
    assert "Revalidate the immutable V1 subject on successor events" in workflow
    assert (
        "research/orion-01-05-convergence-ci-successor-v1/"
        "test_workflow_successor_mode.py"
    ) in workflow


def test_manifest_explicitly_rebinds_the_operational_workflow() -> None:
    payload = WORKFLOW.read_bytes()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    row = next(
        item
        for item in manifest["files"]
        if item["destination"] == ".github/workflows/orion-01-05-convergence-v1.yml"
    )
    assert row["bytes"] == len(payload)
    assert row["sha256"] == hashlib.sha256(payload).hexdigest()
    assert row["source"]["operational_successor"] == (
        "research/orion-01-05-convergence-ci-successor-v1/STATUS.json"
    )
