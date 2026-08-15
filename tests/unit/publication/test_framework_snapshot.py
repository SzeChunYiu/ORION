import json
from pathlib import Path

from orion.registry import CORE_OPERATOR_IDS, CORE_STATE_COORDINATES, FRAMEWORK_VERSION, PAPER_SYNC_EPOCH


def test_paper_framework_snapshot_matches_runtime_registry():
    snapshot_path = Path("papers/FRAMEWORK_SNAPSHOT.json")
    snapshot = json.loads(snapshot_path.read_text())
    assert snapshot["framework_version"] == FRAMEWORK_VERSION
    assert snapshot["paper_sync_epoch"] == PAPER_SYNC_EPOCH
    assert tuple(snapshot["state_coordinates"]) == CORE_STATE_COORDINATES
    assert tuple(snapshot["core_operator_ids"]) == CORE_OPERATOR_IDS
