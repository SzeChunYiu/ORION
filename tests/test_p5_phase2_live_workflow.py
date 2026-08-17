from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "p5_phase2_live_execution.yml"
TRIGGER = (
    ROOT
    / "papers"
    / "paper-05-self-orion"
    / "phase2"
    / "LIVE_EXECUTION_TRIGGER.txt"
)


def _workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_live_phase2_workflow_is_main_push_only() -> None:
    text = _workflow_text()
    assert "push:" in text
    assert "branches: [main]" in text
    assert "pull_request:" not in text
    assert "workflow_dispatch:" not in text
    assert "persist-credentials: false" in text


def test_live_phase2_workflow_uses_canonical_frozen_identities() -> None:
    text = _workflow_text()
    assert "protocol_id='phase2-shadow-closure-v1'" in text
    assert "baseline_id='simple-llm-retrieval-baseline-v1'" in text
    assert "P5.phase2-shadow-live.v1" not in text
    assert "baseline_id='simple-llm-retrieval-v1'" not in text


def test_live_phase2_workflow_persists_replayable_binding_before_run() -> None:
    text = _workflow_text()
    write_pos = text.index("write_phase2_binding(preflight, binding_path)")
    packet_pos = text.index("packet = build_frozen_live_trial_packet(preflight)")
    run_pos = text.index("report = harness.runner.run(packet)")
    assert write_pos < packet_pos < run_pos
    assert "loaded_binding = load_phase2_binding(binding_path)" in text
    assert "loaded_binding != preflight" in text
    assert "PHASE2_CLOSURE_BINDING.json" in text


def test_live_phase2_workflow_is_secret_safe_and_non_promoting() -> None:
    text = _workflow_text()
    for name in (
        "OPENAI_API_KEY",
        "ORION_PROTECTED_VERIFIER_URL",
        "ORION_PROTECTED_VERIFIER_TOKEN",
        "ORION_PROTECTED_VERIFIER_ARTIFACT_HASH",
        "ORION_PHASE2_EVALUATION_EPOCH_ID",
    ):
        assert name in text
    assert "values are not printed" in text
    assert "if loaded.grants_self_promotion:" in text
    assert "live_trial_exposed_self_promotion" in text
    assert "issue_8_gate" in text


def test_live_phase2_trigger_documents_issue_chain_and_authority_boundary() -> None:
    text = TRIGGER.read_text(encoding="utf-8")
    assert "#8 -> #76 -> #102" in text
    assert "no workflow result grants self-merge" in text
