import hashlib
import json

import pytest

from orion.core.solution import SolutionStatus
from orion.self_orion.live_trial import (
    ResearchTrialKind,
    RetrievedItemSnapshot,
    SearchObservation,
    ShadowLiveTrialReport,
    TrialTaskComparison,
)
from orion.self_orion.trial_io import (
    load_shadow_live_trial_report,
    write_shadow_live_trial_report,
)


def _report() -> ShadowLiveTrialReport:
    comparison = TrialTaskComparison(
        task_id="phase2:wide:test",
        kind=ResearchTrialKind.WIDE_LITERATURE,
        orion_status=SolutionStatus.SOLVED_VERIFIED,
        orion_evidence_count=1,
        orion_residual_count=0,
        orion_resource_units=2.0,
        baseline_solved=True,
        baseline_evidence_count=1,
        baseline_residual_count=0,
        baseline_resource_units=2.0,
        resource_matched=True,
        required_evidence_recovered=True,
        root_episode_id=None,
        mechanic_episode_ids=(),
        search_observations=(
            SearchObservation(
                query_id="q1",
                query_text="query",
                route_id="route",
                route_kind="CURRENT_VOCABULARY",
                domain_hint=None,
                limit=1,
                items=(
                    RetrievedItemSnapshot(
                        item_id="e1",
                        content="original evidence bytes",
                        source_uri="https://example.org/e1",
                        domain_ids=("test",),
                    ),
                ),
            ),
        ),
        solution_evidence_ids=("e1",),
        absorbed_evidence_ids=("e1",),
    )
    return ShadowLiveTrialReport(
        packet_id="packet",
        packet_fingerprint="fingerprint",
        comparisons=(comparison,),
        all_resource_matched=True,
        all_failures_recordable=True,
        wide_task_count=1,
        deep_task_count=0,
        boundary="shadow-only",
    )


def _document_hash(raw: dict[str, object]) -> str:
    payload = dict(raw)
    payload.pop("document_hash", None)
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def test_live_replay_recomputes_evidence_artifact_hash(tmp_path):
    report = _report()
    path = tmp_path / "live.json"
    write_shadow_live_trial_report(report, path)

    loaded = load_shadow_live_trial_report(path)
    assert loaded.evidence_artifact_hash == report.evidence_artifact_hash


def test_live_replay_rejects_raw_trace_edit_even_with_rewritten_document_hash(tmp_path):
    report = _report()
    path = tmp_path / "live.json"
    write_shadow_live_trial_report(report, path)

    raw = json.loads(path.read_text())
    raw["comparisons"][0]["search_observations"][0]["items"][0]["content"] = (
        "post-hoc substituted evidence bytes"
    )
    raw["document_hash"] = _document_hash(raw)
    path.write_text(json.dumps(raw))

    with pytest.raises(ValueError, match="evidence artifact hash mismatch"):
        load_shadow_live_trial_report(path)
