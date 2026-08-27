"""Issue #8 packet-to-workflow binding is CANNOT_CHECK until a fail-closed gate merges.

The published LIVE_TRIAL_PACKET_V1.json and the merged Phase-2 live workflow
name two different task registries. Issue #277 owns making the preflight fail
closed; this test does not edit that module and does not elect a canonical
registry. It only proves the divergence is detected and recorded.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from orion.self_orion.live_packet import PROTOCOL_PATH, load_packet_document
from orion.self_orion.phase2_preflight import DEEP_TARGET_TASK, WIDE_LITERATURE_TASK

REPO_ROOT = Path(__file__).resolve().parents[3]
RECEIPT_PATH = (
    REPO_ROOT
    / "papers"
    / "orion-15-self-orion"
    / "evidence"
    / "ISSUE8_PACKET_EXECUTION_BINDING_RECEIPT.json"
)
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "p5_phase2_live_execution.yml"
RUNBOOK_PATH = (
    REPO_ROOT
    / "papers"
    / "orion-15-self-orion"
    / "protocol"
    / "ISSUE8_LIVE_TRIAL_RUNBOOK.md"
)
TRIGGER_PATH = (
    REPO_ROOT
    / "papers"
    / "orion-15-self-orion"
    / "phase2"
    / "LIVE_EXECUTION_TRIGGER.txt"
)


def _artifact_hash(payload: dict[str, object]) -> str:
    body = {key: value for key, value in payload.items() if key != "artifact_hash"}
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _git_blob_sha(path: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{path.relative_to(REPO_ROOT).as_posix()}"],
        cwd=REPO_ROOT,
        text=True,
    ).strip()


def observed_packet_workflow_divergence() -> dict[str, object]:
    packet = load_packet_document(PROTOCOL_PATH)
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    packet_task_ids = tuple(sorted(str(task["task_id"]) for task in packet["tasks"]))
    workflow_task_ids = tuple(
        sorted((WIDE_LITERATURE_TASK.task_id, DEEP_TARGET_TASK.task_id))
    )
    loads_published_packet = any(
        token in workflow
        for token in (
            "LIVE_TRIAL_PACKET_V1.json",
            "load_packet_document",
            "PROTOCOL_PATH",
            "orion.self_orion.live_packet",
        )
    )
    rebuilds_from_preflight = "build_frozen_live_trial_packet(preflight)" in workflow
    passes_frozen_packet = (
        "frozen_packet=" in workflow or "from_packet_document" in workflow
    )
    packet_budget = float(packet["resource_limits"]["budget_units"])
    if "|| '32' }}" not in workflow:
        raise AssertionError("workflow default resource budget is no longer 32")
    workflow_budget = 32.0
    packet_reasoner_env = next(
        provider["identity"]["model_env_var"]
        for provider in packet["providers"]
        if provider["role"] == "reasoner"
    )
    return {
        "packet_task_ids": list(packet_task_ids),
        "workflow_task_ids": list(workflow_task_ids),
        "packet_epoch": packet["evaluation_epoch_id"],
        "packet_baseline_id": packet["matched_baseline"]["baseline_id"],
        "packet_budget": packet_budget,
        "packet_reasoner_env": packet_reasoner_env,
        "packet_corpus_revision": packet["corpus_revision"],
        "packet_fingerprint": packet["packet_fingerprint"],
        "loads_published_packet": loads_published_packet,
        "passes_frozen_packet": passes_frozen_packet,
        "rebuilds_from_preflight": rebuilds_from_preflight,
        "workflow_budget": workflow_budget,
        "workflow_reasoner_env": "ORION_PHASE2_REASONER_MODEL",
        "divergent": packet_task_ids != workflow_task_ids,
    }


def test_published_packet_and_workflow_registry_diverge_and_are_detected():
    observed = observed_packet_workflow_divergence()
    assert observed["divergent"] is True
    assert observed["packet_task_ids"] == [
        "P5.LIVE.DEEP.flat-round-without-lineage",
        "P5.LIVE.WIDE.stopping-rule-source-families",
    ]
    assert observed["workflow_task_ids"] == [
        "phase2:deep:mos2-screening-exciton",
        "phase2:wide:microglia-complement-cross-disease",
    ]
    assert observed["loads_published_packet"] is False
    assert observed["passes_frozen_packet"] is False
    assert observed["rebuilds_from_preflight"] is True
    assert observed["packet_corpus_revision"] == "UNBOUND"
    assert observed["packet_budget"] == 24.0
    assert observed["workflow_budget"] == 32.0
    assert observed["packet_reasoner_env"] == "ORION_P5_REASONER_MODEL"
    assert observed["workflow_reasoner_env"] == "ORION_PHASE2_REASONER_MODEL"


def test_binding_receipt_is_cannot_check_and_elects_no_registry():
    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    observed = observed_packet_workflow_divergence()

    assert receipt["schema"] == "orion.p5.issue8-packet-execution-binding-receipt.v1"
    assert receipt["issue"] == "SzeChunYiu/ORION#8"
    assert receipt["status"] == "CANNOT_CHECK"
    assert receipt["empirical_authority"] == "CANNOT_CHECK"
    assert receipt["failure_class"] == "FROZEN_ARTIFACT_NOT_CONSULTED_BY_EXECUTION"
    assert receipt["canonical_registry_elected"] is False
    assert receipt["live_trial_launched"] is False
    assert receipt["outcome_accessed"] is False
    assert receipt["artifact_hash"] == _artifact_hash(receipt)

    assert receipt["frozen_packet"]["task_ids"] == observed["packet_task_ids"]
    assert receipt["frozen_packet"]["packet_fingerprint"] == observed["packet_fingerprint"]
    assert receipt["frozen_packet"]["corpus_revision"] == "UNBOUND"
    assert receipt["workflow_registry"]["task_ids"] == observed["workflow_task_ids"]
    assert receipt["workflow_registry"]["loads_published_packet"] is False
    assert receipt["workflow_registry"]["passes_frozen_packet"] is False
    assert receipt["fail_closed_gate"]["status"] == "merged_on_origin_main"
    assert "issue-277-fail-closed-preflight-gate-unmerged" not in receipt["blocked_on"]
    assert (
        receipt["workflow_registry"]["packet_constructor"]
        == "orion.self_orion.phase2_preflight.build_frozen_live_trial_packet"
    )

    # Equality of the two id lists would still not authorize a silent election.
    if not observed["divergent"]:
        raise AssertionError(
            "registries now agree; rewrite the receipt with an explicit binding "
            "attestation rather than inferring canonicity from equality"
        )

    assert receipt["divergence"]["wide_task_id"][0] in observed["packet_task_ids"]
    assert receipt["divergence"]["wide_task_id"][1] in observed["workflow_task_ids"]
    assert receipt["divergence"]["deep_task_id"][0] in observed["packet_task_ids"]
    assert receipt["divergence"]["deep_task_id"][1] in observed["workflow_task_ids"]
    assert "electing live_packet.py or phase2_preflight.py" in " ".join(
        receipt["does_not_authorize"]
    )


def test_receipt_keeps_its_historical_blob_identity_and_current_drift_is_explicit():
    """A later provider-lane edit did not retroactively rewrite the receipt.

    The receipt observed workflow blob ``8bbc...`` at commit ``5a9a...``. The
    open-weight provider change in ``61ab033c`` moved the workflow to ``4be3...``
    without making it load or pass the frozen packet. Treat the old blob as the
    historical observation and pin the current unbound tree separately; equating
    the two would either erase provenance or silently bless a registry.
    """

    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert receipt["frozen_packet"]["blob_sha"] == _git_blob_sha(PROTOCOL_PATH)
    assert receipt["observed_at_commit"] == "5a9a35b53b7f01000ed5f001c16da9492212549b"
    assert receipt["workflow_registry"]["workflow_blob_sha"] == (
        "8bbc5884cde50dc84bb8f3b477cfdb29fe9845f9"
    )
    current_workflow_blob = _git_blob_sha(WORKFLOW_PATH)
    assert current_workflow_blob == "d42f55fae071aec38d4ce34773f4d80e494bae44"
    assert current_workflow_blob != receipt["workflow_registry"]["workflow_blob_sha"]
    assert receipt["workflow_registry"]["preflight_blob_sha"] == _git_blob_sha(
        REPO_ROOT / "src" / "orion" / "self_orion" / "phase2_preflight.py"
    )

    observed = observed_packet_workflow_divergence()
    assert observed["divergent"] is True
    assert observed["loads_published_packet"] is False
    assert observed["passes_frozen_packet"] is False


def test_runbook_forbids_unbound_launch_and_silent_registry_election():
    text = RUNBOOK_PATH.read_text(encoding="utf-8")
    trigger = TRIGGER_PATH.read_text(encoding="utf-8")
    assert "CANNOT_CHECK" in text
    assert "UNBOUND_EXECUTION_REPORT" in text
    assert "LIVE_EXECUTION_TRIGGER.txt" in text
    assert "does not choose which registry" in text
    assert "#277" in text
    assert "frozen_packet" in text
    assert "phase2_preflight.py" in text
    assert "#8 -> #76 -> #102" in trigger
    assert "no workflow result grants self-merge" in trigger
