from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
MODULE = ROOT / "research" / "claim_expansion" / "p1" / "gpt_r7" / "candidate_view.py"


def _load():
    spec = importlib.util.spec_from_file_location("p1_r7_candidate_view", MODULE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _episode(module):
    return module.CandidateVisibleEpisode(
        opaque_episode_handle="ep-7f3c",
        dossier="A scientific system exhibits a protected failure under the registered conditions.",
        source_evidence=(module.EvidenceObject("ev-a1", "Source-grounded visible evidence."),),
        probe_handles=("probe-02", "probe-91"),
        action_handles=("action-13", "action-88"),
    )


def test_candidate_payload_contains_only_the_frozen_visible_contract():
    module = _load()
    payload = _episode(module).payload()
    assert set(payload) == {
        "opaque_episode_handle",
        "dossier",
        "source_evidence",
        "probe_handles",
        "action_handles",
    }
    blob = _episode(module).to_bytes().decode("utf-8")
    for forbidden in (
        "gold_class",
        "causal_family",
        "pair_role",
        "source_id",
        "query_id",
        "evaluator_disposition",
        "protected_outcome",
    ):
        assert forbidden not in blob


def test_every_arm_receives_the_same_payload_digest_independent_of_arm_order():
    module = _load()
    episode = _episode(module)
    first = module.arm_visibility_receipt(episode, ["ORION", "B3", "EXTERNAL"])
    second = module.arm_visibility_receipt(episode, ["EXTERNAL", "ORION", "B3"])
    assert first == second
    assert len(set(first["payload_digest_by_arm"].values())) == 1
    module.assert_arm_visibility_equal(first)


def test_arm_specific_evidence_byte_fails_the_visibility_gate():
    module = _load()
    receipt = module.arm_visibility_receipt(_episode(module), ["ORION", "B3"])
    receipt["payload_digest_by_arm"]["ORION"] = "sha256:" + "0" * 64
    receipt["all_arm_payload_digests_equal"] = False
    with pytest.raises(ValueError, match="differs across arms"):
        module.assert_arm_visibility_equal(receipt)


def test_probe_bank_is_opaque_metered_and_transcript_complete():
    module = _load()
    bank = module.GuardedProbeBank({"probe-02": "SUPPORT", "probe-91": "REFUTE"}, limit=1)
    assert bank.handles == ("probe-02", "probe-91")
    assert bank.request("probe-91") == "REFUTE"
    with pytest.raises(module.ProbeBudgetExceeded):
        bank.request("probe-02")
    assert [row["status"] for row in bank.transcript] == ["REVEALED", "BUDGET_EXCEEDED"]


def test_unknown_probe_is_not_silently_interpreted_as_no_evidence():
    module = _load()
    bank = module.GuardedProbeBank({"probe-02": "SUPPORT"}, limit=1)
    with pytest.raises(module.UnknownProbeHandle):
        bank.request("gold-measurement-probe")
    assert bank.transcript[-1]["status"] == "UNKNOWN"
