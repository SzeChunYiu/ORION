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


def test_live_phase2_workflow_is_main_push_only_and_read_only() -> None:
    text = _workflow_text()
    assert "push:" in text
    assert "branches: [main]" in text
    assert "pull_request:" not in text
    assert "workflow_dispatch:" not in text
    assert "persist-credentials: false" in text
    assert "permissions:\n  contents: read" in text
    assert "copilot-requests" not in text
    assert "models: read" not in text


def test_open_weight_runtime_and_models_are_exactly_content_pinned() -> None:
    text = _workflow_text()
    assert "ORION_LLAMA_RUNTIME_RELEASE_TAG: b10218" in text
    assert "ORION_LLAMA_RUNTIME_COMMIT: de699957b92f490efebad149665b0dccf127eaff" in text
    assert "78ec7a1964710918030e85c132a0995b10b07e4f43001bdf54fe0fd48d1eb85b" in text
    assert "ORION_OPEN_WEIGHT_REASONER_REVISION: 02938d9fe88f34a3a9960128b5092f20940e7553" in text
    assert "50961d9b7d3b89e46be230528fc66d38bbdda8ac3748323dd34f129a714124fc" in text
    assert "ORION_OPEN_WEIGHT_EVALUATOR_REVISION: 0f0ce936387870522d587f83d01d404e9d726b33" in text
    assert "77665ea4815999596525c636fbeb56ba8b080b46ae85efef4f0d986a139834d7" in text
    assert "Qwen2.5-1.5B-Instruct-Q4_K_M.gguf" in text
    assert "SmolLM2-1.7B-Instruct-Q4_K_M.gguf" in text


def test_download_hash_verification_precedes_subject_and_outcome_access() -> None:
    text = _workflow_text()
    asset_pos = text.index("echo \"$ORION_LLAMA_RUNTIME_ASSET_SHA256  $archive\" | sha256sum -c -")
    reasoner_pos = text.index("echo \"$ORION_OPEN_WEIGHT_REASONER_SHA256  $reasoner\" | sha256sum -c -")
    evaluator_pos = text.index("echo \"$ORION_OPEN_WEIGHT_EVALUATOR_SHA256  $evaluator\" | sha256sum -c -")
    subject_pos = text.index("subject = attest_repository_subject")
    packet_pos = text.index("packet = build_frozen_live_trial_packet(preflight)")
    run_pos = text.index("report = harness.runner.run(packet)")
    assert asset_pos < reasoner_pos < evaluator_pos < subject_pos < packet_pos < run_pos
    assert "OPEN_WEIGHT_RUNTIME_SAFE_SUMMARY.json" in text
    assert "ORION_OPEN_WEIGHT_FREEZE_HASH" in text


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


def test_live_phase2_workflow_rejects_partial_private_lane_and_records_open_weight_identities() -> None:
    text = _workflow_text()
    assert "Partial private provider configuration is forbidden" in text
    assert "present == ${#names[@]}" in text
    assert "present == 0" in text
    assert "build_phase2_open_weight_provider_stack" in text
    assert "provider_mode" in text
    assert "reasoner_identity" in text
    assert "verifier_identity" in text
    assert "external_freeze_hash" in text
    assert "github-hosted-open-weight-llama-cpp" in text


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
