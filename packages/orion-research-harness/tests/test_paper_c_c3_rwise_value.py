from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from orion_research_harness.campaign_control import (
    decide_campaign,
    manifest_digest,
    validate_manifest,
)
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.domains.orion_qg.paper_c_c3_rwise_value import (
    PAPER_C_C3_RWISE_VALUE_CAMPAIGN_MANIFEST,
)


def _state(positive: str = "YES") -> CampaignState:
    manifest = PAPER_C_C3_RWISE_VALUE_CAMPAIGN_MANIFEST
    observations = {
        key: "YES"
        for key in (
            "PAPER_C_C3_SOURCE_DIGEST",
            "PAPER_C_C3_GENERIC_DIGEST",
            "PAPER_C_C3_POSITIVE",
            "PAPER_C_C3_GATES",
            "PAPER_C_C3_GENERIC",
            "PAPER_C_C3_DIRECT",
            "PAPER_C_C3_TENSOR_FALSE",
            "PAPER_C_C3_UNBOUNDED",
            "PAPER_C_C3_NO_OPTIMIZER_RELABEL",
            "PAPER_C_C3_PARENTS",
            "PAPER_C_C3_SCOPE",
            "PAPER_C_C3_NO_NOVELTY",
            "PAPER_C_C3_NO_PHYSICAL",
        )
    }
    observations["PAPER_C_C3_POSITIVE"] = positive
    return CampaignState.create(
        campaign_id=manifest["campaign_id"],
        claim_id=manifest["claim_id"],
        phase_id="D0",
        cycle_index=1,
        manifest_digest=manifest_digest(manifest),
        observations=observations,
        active_hard_obligations=(),
        protected_refs=(),
        authority_ceiling=manifest["authority_ceiling"],
    )


def _load(relative: str, name: str):
    root = Path(__file__).resolve().parents[3]
    path = root / relative
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_paper_c_c3_manifest_validates_and_preserves_scope() -> None:
    validate_manifest(PAPER_C_C3_RWISE_VALUE_CAMPAIGN_MANIFEST)
    text = repr(PAPER_C_C3_RWISE_VALUE_CAMPAIGN_MANIFEST)
    assert PAPER_C_C3_RWISE_VALUE_CAMPAIGN_MANIFEST["protected_refs"] == []
    assert "FROZEN_STRUCTURAL_GRAMMAR_CONSTRUCTION_ONLY" in text
    assert "novelty_authority': True" not in text
    assert "physical_quantum_advantage_claim': True" not in text


def test_paper_c_c3_native_accepts_only_complete_bounded_evidence() -> None:
    decision = decide_campaign(_state(), PAPER_C_C3_RWISE_VALUE_CAMPAIGN_MANIFEST)
    assert decision.responsibility["identified_hypothesis_id"] == "RESP:ACCEPT"
    assert decision.selected_id == "REV:ACCEPT"


def test_paper_c_c3_native_rejects_refuted_source() -> None:
    decision = decide_campaign(_state("NO"), PAPER_C_C3_RWISE_VALUE_CAMPAIGN_MANIFEST)
    assert decision.responsibility["identified_hypothesis_id"] == "RESP:REJECT"
    assert decision.selected_id == "REV:REJECT"


def test_paper_c_c3_m5_tensor_and_value_gap_are_exact() -> None:
    analyzer = _load(
        "research/extensions/orion-qg/paper_c_c3_rwise_value_separation.py",
        "paper_c_c3_rwise_value_separation",
    )
    a_codes, qubits = analyzer.construct(5, 1, "A")
    b_codes, b_qubits = analyzer.construct(5, 1, "B")
    assert qubits == b_qubits == 180
    assert analyzer.interaction_tensor(a_codes, qubits, 3) == analyzer.interaction_tensor(
        b_codes, b_qubits, 3
    )
    assert analyzer.parameters(5, 1)["gap"] == 19


def test_paper_c_c3_dual_harness_cleans_workspaces_after_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    harness = _load(
        "development/orion-qg-regime-geometry/run_paper_c_c3_dual_harness.py",
        "run_paper_c_c3_dual_harness",
    )
    created: list[Path] = []

    def fake_mkdtemp(*, prefix: str, dir: str) -> str:
        assert dir == "/tmp"
        path = tmp_path / prefix
        path.mkdir()
        created.append(path)
        return str(path)

    def fail_run(*_args: object) -> int:
        raise RuntimeError("injected failure")

    monkeypatch.setattr(harness.tempfile, "mkdtemp", fake_mkdtemp)
    monkeypatch.setattr(harness, "_run", fail_run)
    with pytest.raises(RuntimeError, match="injected failure"):
        harness.main()
    assert len(created) == 2
    assert all(not path.exists() for path in created)

