import json
from pathlib import Path

from orion.registry import (
    CORE_OPERATOR_IDS,
    CORE_STATE_COORDINATES,
    FRAMEWORK_VERSION,
    MECHANICS_SUBSTRATE_IDS,
    PAPER_SYNC_EPOCH,
    Q3_HARNESS_PUBLICATION_CONTRACT_ID,
    Q_SERIES_CANONICAL_MANUSCRIPTS,
    Q_SERIES_PAPER_IDS,
    Q_SERIES_PUBLICATION_SPEC_ID,
    Q_SERIES_SYNC_EPOCH,
)


def test_paper_framework_snapshot_matches_runtime_registry():
    snapshot_path = Path("papers/FRAMEWORK_SNAPSHOT.json")
    snapshot = json.loads(snapshot_path.read_text())
    assert snapshot["framework_version"] == FRAMEWORK_VERSION
    assert snapshot["paper_sync_epoch"] == PAPER_SYNC_EPOCH
    assert snapshot["q_series_publication_spec_id"] == Q_SERIES_PUBLICATION_SPEC_ID
    assert snapshot["q_series_sync_epoch"] == Q_SERIES_SYNC_EPOCH
    assert tuple(snapshot["q_series_paper_ids"]) == Q_SERIES_PAPER_IDS
    assert tuple(snapshot["q_series_canonical_manuscripts"]) == Q_SERIES_CANONICAL_MANUSCRIPTS
    assert snapshot["q3_harness_publication_contract_id"] == Q3_HARNESS_PUBLICATION_CONTRACT_ID
    assert tuple(snapshot["state_coordinates"]) == CORE_STATE_COORDINATES
    assert tuple(snapshot["core_operator_ids"]) == CORE_OPERATOR_IDS
    assert tuple(snapshot["mechanics_substrate_ids"]) == MECHANICS_SUBSTRATE_IDS
