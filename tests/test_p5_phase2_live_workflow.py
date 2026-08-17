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


def test_live_phase2_workflow_has_minimum_copilot_permission() -> None:
    text = _workflow_text()
    assert "permissions:\n  contents: read\n  copilot-requests: write" in text
    assert "COPILOT_GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}" in text
    assert "models: read" not in text


def test_live_phase2_workflow_probes_models_before_subject_and_study_execution() -> None:
    text = _workflow_text()
    assert "npm install -g @github/copilot" in text
    assert "node-version: '22'" in text
    version_pos = text.index("ORION_COPILOT_CLI_VERSION")
    probe_pos = text.index("report = probe_copilot_model_pair(")
    subject_pos = text.index("subject = attest_repository_subject")
    provider_pos = text.index("stack, provider_mode = build_phase2_auto_provider_stack_from_env")
    packet_pos = text.index("packet = build_frozen_live_trial_packet(preflight)")
    run_pos = text.index("report = harness.runner.run(packet)")
    assert version_pos < probe_pos < subject_pos < provider_pos < packet_pos < run_pos
    assert "COPILOT_MODEL_PROBE_SAFE_SUMMARY.json" in text
    assert "ORION_COPILOT_MODEL_PROBE_HASH" in text
    assert "ORION_PHASE2_COPILOT_REASONER_MODEL" in text
    assert "ORION_PHASE2_COPILOT_EVALUATOR_MODEL" in text
    assert "gpt-5.2" not in text
    assert "gpt-5.4" not in text


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


def test_live_phase2_workflow_rejects_partial_private_lane_and_records_provider_identities() -> None:
    text = _workflow_text()
    assert "Partial private provider configuration is forbidden" in text
    assert "present == ${#names[@]}" in text
    assert "present == 0" in text
    assert "build_phase2_auto_provider_stack_from_env" in text
    assert "provider_mode" in text
    assert "reasoner_identity" in text
    assert "verifier_identity" in text
    assert "model_probe_hash" in text


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
    assert "No credential values are printed." in text
    assert "if loaded.grants_self_promotion:" in text
    assert "live_trial_exposed_self_promotion" in text
    assert "issue_8_gate" in text


def test_live_phase2_trigger_documents_issue_chain_and_authority_boundary() -> None:
    text = TRIGGER.read_text(encoding="utf-8")
    assert "#8 -> #76 -> #102" in text
    assert "no workflow result grants self-merge" in text
