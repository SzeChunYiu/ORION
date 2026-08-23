from __future__ import annotations

from pathlib import Path
import runpy


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "research" / "self-orion-v3" / "run_confirmatory_preflight_v1.py"
V1 = ROOT / "research" / "self-orion-v3" / "BASELINE_STRUCTURAL_BINDINGS_V1.json"


def _namespace() -> dict[str, object]:
    return runpy.run_path(str(SCRIPT))


def test_default_command_uses_superseding_v2_baselines_and_reports_eight_local_bindings() -> None:
    namespace = _namespace()
    assert namespace["DEFAULT_BASELINES"].name == "BASELINE_STRUCTURAL_BINDINGS_V2.json"

    result = namespace["derive"]()
    blockers = set(result["blockers"])
    assert result["status"] == "CANNOT_CHECK"
    assert blockers == {
        "subject_revision_unbound_or_invalid",
        "protected_suite_commitment_unbound_or_invalid",
        "candidate_packet_sha256_unbound_or_invalid",
        "final_split_sha256_unbound_or_invalid",
        "evaluator_sha256_unbound_or_invalid",
        "evaluation_epoch_unbound",
        "baseline_config_sha256_unbound_or_invalid",
        "fresh_transfer_evaluator_sha256_unbound_or_invalid",
    }
    assert result["authorizes_execution"] is False
    assert result["grants_scientific_authority"] is False
    assert result["grants_p5_peer_review_ready"] is False


def test_historical_v1_baseline_set_remains_explicitly_replayable() -> None:
    namespace = _namespace()
    result = namespace["derive"](baseline_path=V1)
    blockers = set(result["blockers"])
    assert "baseline_binding_not_confirmatory:m_open_only:CANNOT_CHECK" in blockers
    assert result["status"] == "CANNOT_CHECK"
    assert result["authorizes_execution"] is False
