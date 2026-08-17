import hashlib
import json

import pytest

from orion.benchmarks.authority_external import (
    FROZEN_AUTHORITY_BASELINE_IDS,
    AuthorityBenchmarkMetrics,
    AuthorityBenchmarkPanel,
    AuthoritySystemObservation,
)
from orion.benchmarks.authority_external_io import (
    load_authority_benchmark_panel,
    write_authority_benchmark_panel,
)


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode()).hexdigest()


def _metrics():
    return AuthorityBenchmarkMetrics(
        claim_correct=10,
        claim_total=10,
        source_attribution_correct=10,
        source_attribution_total=10,
        support_contradiction_tp=10,
        support_contradiction_fp=0,
        support_contradiction_fn=0,
        conflation_detected=10,
        conflation_total=10,
        substitution_detected=10,
        substitution_total=10,
        tamper_leakage_detected=10,
        tamper_leakage_total=10,
        false_promotions=0,
        promotion_opportunities=10,
        correct_cannot_check=10,
        cannot_check_opportunities=10,
        false_negative_count=0,
        clean_positive_total=3,
        resource_units=10.0,
        latency_seconds=3.0,
    )


def _observation(system_id: str):
    return AuthoritySystemObservation(
        system_id=system_id,
        metrics=_metrics(),
        evidence_artifact_id=f"artifact:{system_id}",
        evidence_artifact_hash=_digest(f"artifact:{system_id}"),
        subject_revision_hash=_digest("subject"),
        evaluator_artifact_hash=_digest("evaluator"),
        evaluation_epoch_id="epoch:frozen",
        split_id="split:heldout",
        producer_process_lineage_hash=_digest(f"producer:{system_id}"),
        verifier_process_lineage_hash=_digest(f"verifier:{system_id}"),
        evaluator_frozen_before_candidate=True,
        fresh_split=True,
    )


def _panel():
    return AuthorityBenchmarkPanel(
        panel_id="authority:panel:v1",
        subject_revision_hash=_digest("subject"),
        evaluator_artifact_hash=_digest("evaluator"),
        evaluation_epoch_id="epoch:frozen",
        resource_budget_units=12.0,
        orion=_observation("orion"),
        baselines=tuple(_observation(item) for item in FROZEN_AUTHORITY_BASELINE_IDS),
    )


def test_authority_benchmark_panel_roundtrips_and_binds_counts(tmp_path):
    panel = _panel()
    path = tmp_path / "authority-panel.json"
    write_authority_benchmark_panel(panel, path)
    loaded = load_authority_benchmark_panel(path)
    assert loaded == panel
    assert loaded.artifact_hash == panel.artifact_hash


def test_authority_benchmark_panel_rejects_metric_tampering(tmp_path):
    panel = _panel()
    path = tmp_path / "authority-panel.json"
    write_authority_benchmark_panel(panel, path)
    raw = json.loads(path.read_text())
    raw["orion"]["metrics"]["false_promotions"] = 1
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="artifact hash mismatch"):
        load_authority_benchmark_panel(path)


def test_authority_benchmark_panel_rejects_baseline_identity_rewrite(tmp_path):
    panel = _panel()
    path = tmp_path / "authority-panel.json"
    write_authority_benchmark_panel(panel, path)
    raw = json.loads(path.read_text())
    raw["frozen_baseline_ids"][0] = "strawman-baseline"
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="frozen baseline"):
        load_authority_benchmark_panel(path)
