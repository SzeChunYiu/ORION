from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from orion_research_harness.campaign_control import decide_campaign, manifest_digest, validate_manifest
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.domains.orion_qg.paper_c_c2_pair_value import (
    PAPER_C_C2_PAIR_VALUE_CAMPAIGN_MANIFEST,
)


def _state(positive: str = "YES") -> CampaignState:
    manifest = PAPER_C_C2_PAIR_VALUE_CAMPAIGN_MANIFEST
    observations = {
        "PAPER_C_C2_SOURCE_DIGEST": "YES",
        "PAPER_C_C2_GENERIC_DIGEST": "YES",
        "PAPER_C_C2_POSITIVE": positive,
        "PAPER_C_C2_GATES": "YES",
        "PAPER_C_C2_GENERIC": "YES",
        "PAPER_C_C2_PAIR_SAME": "YES",
        "PAPER_C_C2_LOCAL_COMPLETE": "YES",
        "PAPER_C_C2_DIRECT": "YES",
        "PAPER_C_C2_UNBOUNDED": "YES",
        "PAPER_C_C2_VALUE_FALSE": "YES",
        "PAPER_C_C2_OPTIMIZER_FALSE": "YES",
        "PAPER_C_C2_PARENT": "YES",
        "PAPER_C_C2_SCOPE": "YES",
        "PAPER_C_C2_NO_NOVELTY": "YES",
        "PAPER_C_C2_NO_PHYSICAL": "YES",
    }
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


def _analyzer():
    root = Path(__file__).resolve().parents[3]
    path = root / "research" / "extensions" / "orion-qg" / "paper_c_c2_pair_value_separation.py"
    spec = importlib.util.spec_from_file_location("paper_c_c2_pair_value_separation", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _dual_harness():
    root = Path(__file__).resolve().parents[3]
    path = (
        root
        / "development"
        / "orion-qg-regime-geometry"
        / "run_paper_c_c2_dual_harness.py"
    )
    spec = importlib.util.spec_from_file_location("run_paper_c_c2_dual_harness", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_paper_c_c2_manifest_validates_and_preserves_scope() -> None:
    validate_manifest(PAPER_C_C2_PAIR_VALUE_CAMPAIGN_MANIFEST)
    text = repr(PAPER_C_C2_PAIR_VALUE_CAMPAIGN_MANIFEST)
    assert PAPER_C_C2_PAIR_VALUE_CAMPAIGN_MANIFEST["protected_refs"] == []
    assert "FROZEN_STRUCTURAL_GRAMMAR_CONSTRUCTION_ONLY" in text
    assert "novelty_authority': True" not in text
    assert "physical_quantum_advantage_claim': True" not in text


def test_paper_c_c2_native_accepts_only_complete_bounded_evidence() -> None:
    decision = decide_campaign(_state(), PAPER_C_C2_PAIR_VALUE_CAMPAIGN_MANIFEST)
    assert decision.responsibility["identified_hypothesis_id"] == "RESP:ACCEPT"
    assert decision.selected_id == "REV:ACCEPT"


def test_paper_c_c2_native_rejects_refuted_source() -> None:
    decision = decide_campaign(_state("NO"), PAPER_C_C2_PAIR_VALUE_CAMPAIGN_MANIFEST)
    assert decision.responsibility["identified_hypothesis_id"] == "RESP:REJECT"
    assert decision.selected_id == "REV:REJECT"


def test_paper_c_c2_local_pair_fiber_and_partition_maxima_are_exact() -> None:
    proof = _analyzer().proof_ledger()
    assert proof["all_checks"] is True
    assert proof["local_partition_census_A"]["max_sum_U"] == 12
    assert proof["local_partition_census_B"]["max_sum_U"] == 10
    assert proof["pair_information_A"] == proof["pair_information_B"]


def test_paper_c_c2_full_t1_t2_optimization_matches_scalable_formula() -> None:
    direct = _analyzer().direct_exact_checks()
    assert direct["all_checks"] is True
    assert [(row["A_delta"], row["B_delta"]) for row in direct["rows"]] == [(10, 9), (22, 19)]


def test_paper_c_c2_dual_harness_cleans_workspaces_after_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    harness = _dual_harness()
    created: list[Path] = []

    def fake_mkdtemp(*, prefix: str, dir: str) -> str:
        assert dir == "/tmp"
        path = tmp_path / prefix
        path.mkdir()
        created.append(path)
        return str(path)

    def fail_run(*_args: object) -> int:
        raise RuntimeError("injected failure after workspace creation")

    monkeypatch.setattr(harness.tempfile, "mkdtemp", fake_mkdtemp)
    monkeypatch.setattr(harness, "_run", fail_run)
    with pytest.raises(RuntimeError, match="injected failure"):
        harness.main()

    assert len(created) == 2
    assert all(not path.exists() for path in created)
