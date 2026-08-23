"""Hostile tests for the P1-U-T3 pre-outcome guard repairs.

Each test is written to go red when its repair is reverted; the mutation used to
check that is named in the docstring and recorded in
``research/claim_expansion/p1/claude_t3/MUTATION_CHECKS_V1.md``.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
EVAL_PATH = ROOT / "research" / "claim_expansion" / "p1" / "gpt_r6" / "evaluate_native.py"


def load_eval():
    spec = importlib.util.spec_from_file_location("p1_u_t3_eval", EVAL_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------
# Repair 1 — class noninferiority must see the control class
# --------------------------------------------------------------------------


def test_class_strata_are_filed_under_each_members_own_gold_class():
    """Mutation: file both members under ``pair["adverse_class"]`` again."""
    e = load_eval()
    pairs, unresolved = e.fixed_corpus()
    result = e.evaluate(pairs, unresolved)

    member = result["class_episode_differences_by_gold_class"]
    counts = result["class_episode_counts_by_gold_class"]

    assert e.CONTROL in member, "the matched-control gold class must be its own stratum"
    assert counts[e.CONTROL] == 22
    assert e.UNRESOLVED in member
    assert counts[e.UNRESOLVED] == 4
    assert set(member) == e.SUBSTANTIVE | {e.CONTROL, e.UNRESOLVED}
    assert sum(counts.values()) == 48
    assert result["guard_verdicts"]["class_noninferiority"]["control_stratum_evaluated"] is True
    assert result["guard_verdicts"]["class_noninferiority"]["n_strata_member_level"] == 8


def test_class_noninferiority_is_a_conjunction_and_cannot_be_looser_than_before():
    """The repaired check must fail whenever either component fails.

    Mutation: drop the member-level conjunct.
    """
    e = load_eval()
    pairs, unresolved = e.fixed_corpus()
    result = e.evaluate(pairs, unresolved)
    guard = result["guard_verdicts"]["class_noninferiority"]
    assert result["checks"]["class_noninferiority"] == (
        guard["pair_level_by_adverse_class"] and guard["member_level_by_own_gold_class"]
    )
    # A conjunction is never looser than its retained conjunct.
    if not guard["pair_level_by_adverse_class"]:
        assert result["checks"]["class_noninferiority"] is False


def test_a_comparator_that_only_wins_on_controls_now_fails_the_class_guard():
    """The failure mode the broken guard could not express.

    A comparator that is perfect on the 22 matched controls and useless on the
    adverse members leaves every pair-level class mean non-negative -- the
    pre-repair guard sees nothing -- while the control gold class loses 14 of 22
    episodes outright. The repaired conjunction must fail.

    Mutation: drop the member-level conjunct from ``checks["class_noninferiority"]``.
    """
    e = load_eval()
    real_b3 = e._b3

    def only_wins_on_controls(episode):
        row = dict(real_b3(episode))
        gold = str(episode["gold_class"])
        if gold == e.CONTROL:
            row["choice"] = e.CONTROL          # always right on controls
        elif gold == e.UNRESOLVED:
            row["choice"] = e.CONTROL          # always wrong elsewhere
        else:
            row["choice"] = e.UNRESOLVED
        return row

    e._b3 = only_wins_on_controls
    try:
        pairs, unresolved = e.fixed_corpus()
        result = e.evaluate(pairs, unresolved)
    finally:
        e._b3 = real_b3

    guard = result["guard_verdicts"]["class_noninferiority"]
    floor = guard["floor"]
    assert guard["pair_level_by_adverse_class"] is True
    assert all(value >= floor for value in result["class_pair_differences"].values())
    assert result["class_episode_differences_by_gold_class"][e.CONTROL] < floor
    assert guard["member_level_by_own_gold_class"] is False
    assert result["checks"]["class_noninferiority"] is False


def test_pair_level_class_statistics_were_not_rebased_by_the_repair():
    """The three other frozen checks that read ``class_means`` must be untouched."""
    e = load_eval()
    pairs, unresolved = e.fixed_corpus()
    result = e.evaluate(pairs, unresolved)
    # pair-level strata are the six adverse classes only, one row per pair
    assert set(result["class_pair_differences"]) == e.SUBSTANTIVE
    assert result["guard_verdicts"]["class_noninferiority"]["n_strata_pair_level"] == 6


# --------------------------------------------------------------------------
# Repair 2 — the domain margin, restated
# --------------------------------------------------------------------------


def test_domain_margin_is_restated_as_the_zero_loss_rule_it_actually_is():
    """Mutation: rename ``domain_zero_loss`` back to ``domain_noninferiority``
    and drop the equivalence assertion."""
    e = load_eval()
    pairs, unresolved = e.fixed_corpus()
    result = e.evaluate(pairs, unresolved)
    guard = result["guard_verdicts"]["domain_margin"]

    assert "domain_zero_loss" in result["checks"]
    assert "domain_noninferiority" not in result["checks"]
    assert guard["restatement_is_verdict_identical"] is True
    assert guard["governing_verdict"] == guard["frozen_floor_verdict"]
    assert result["checks"]["domain_zero_loss"] == guard["governing_verdict"]


def test_the_frozen_floor_cannot_be_a_margin_on_this_corpus():
    e = load_eval()
    pairs, unresolved = e.fixed_corpus()
    result = e.evaluate(pairs, unresolved)
    guard = result["guard_verdicts"]["domain_margin"]

    assert guard["n_strata"] == 26
    assert guard["stratum_size_histogram"] == {"1": 4, "2": 22}
    assert guard["min_stratum_size_for_the_floor_to_admit_one_lost_episode"] == 10
    assert guard["any_stratum_large_enough"] is False
    # arithmetic, restated as a test rather than as prose
    floor = guard["frozen_floor"]
    for size in (1, 2):
        assert -1.0 / size < floor


def test_widened_stratifier_sensitivity_is_reported_and_invents_no_grouping():
    e = load_eval()
    pairs, unresolved = e.fixed_corpus()
    result = e.evaluate(pairs, unresolved)
    sens = result["guard_verdicts"]["domain_margin"]["sensitivity_widened_stratifier"]

    assert sens["counts"] == {
        "CONTROL": 22,
        "HIGH_LEVEL_ADVERSE": 7,
        "LOWER_LEVEL_ADVERSE": 15,
        "UNRESOLVED": 4,
    }
    # even the widest already-frozen partition leaves -0.10 a zero-loss rule
    # in two of its four strata
    assert sorted(sens["strata_where_floor_admits_one_lost_episode"]) == [
        "CONTROL",
        "LOWER_LEVEL_ADVERSE",
    ]
    assert "verdict_at_frozen_floor" in sens
    assert "verdict_at_zero_loss" in sens


# --------------------------------------------------------------------------
# Repair 3 — the leakage guard fails closed and knows about pair role
# --------------------------------------------------------------------------


def test_leakage_audit_fails_closed_on_absent_empty_and_malformed_records():
    """Mutation: ``payloads = native.get("request_payloads", [])`` again."""
    e = load_eval()
    tokens = e.forbidden_tokens(episode_id="R5-SEARCH-P1-A", gold_class="SEARCH_OR_EVIDENCE")

    for payload in (None, [], (), {}, "", 0):
        verdict = e.leakage_audit(payload, tokens)
        assert verdict.status == e.LeakageVerdict.CANNOT_CHECK, payload
        assert verdict.status != e.LeakageVerdict.PASS

    clean = e.leakage_audit([{"task": "diagnose", "user": "nothing identifying"}], tokens)
    assert clean.status == e.LeakageVerdict.PASS


def test_leakage_verdict_refuses_a_two_valued_reading():
    """Mutation: return ``None`` for CANNOT_CHECK instead of a verdict object."""
    e = load_eval()
    verdict = e.leakage_audit(None, {"x": "y"})
    with pytest.raises(TypeError, match="three-valued"):
        bool(verdict)
    with pytest.raises(TypeError, match="three-valued"):
        _ = not verdict
    with pytest.raises(TypeError, match="three-valued"):
        _ = int(not verdict)
    # the trap the mutation would open
    assert (not None) is True


def test_pair_role_is_a_forbidden_token():
    """Mutation: drop the role category from ``forbidden_tokens``."""
    e = load_eval()
    adverse = e.forbidden_tokens(episode_id="R5-SEARCH-P1-A", gold_class="SEARCH_OR_EVIDENCE")
    control = e.forbidden_tokens(episode_id="R5-SEARCH-P1-C", gold_class=e.CONTROL)
    unres = e.forbidden_tokens(episode_id="R5-UNRES-P1-U", gold_class=e.UNRESOLVED)

    for tokens in (adverse, control, unres):
        assert "pair_role" in set(tokens.values())
    assert adverse["R5-SEARCH-P1-A"] == "episode_id_and_pair_role"
    assert control["R5-SEARCH-P1-C"] == "episode_id_and_pair_role"
    assert unres["R5-UNRES-P1-U"] == "episode_id_and_pair_role"

    # a payload that leaks only the structural role assignment must FAIL
    verdict = e.leakage_audit([{"task": "diagnose", "user": '{"pair_role": "control"}'}], adverse)
    assert verdict.status == e.LeakageVerdict.FAIL
    assert any(hit["category"] == "pair_role" for hit in verdict.hits)


def test_ordinary_domain_use_of_the_word_control_is_not_a_false_positive():
    """The two frozen control dossiers using 'quality-control' / 'positive-control'
    must not trip the guard; the role stays covered by the episode-id token."""
    e = load_eval()
    tokens = e.forbidden_tokens(episode_id="R5-MEAS-P1-C", gold_class=e.CONTROL)
    payload = [
        {
            "task": "diagnose",
            "user": json.dumps(
                {"scope": "a silica-microsphere calibration with a quality-control range"}
            ),
        }
    ]
    assert e.leakage_audit(payload, tokens).status == e.LeakageVerdict.PASS


def test_cannot_check_is_not_pass_at_the_roll_up():
    e = load_eval()
    pairs, unresolved = e.fixed_corpus()
    result = e.evaluate(pairs, unresolved)
    guard = result["guard_verdicts"]["candidate_metadata_leakage"]
    assert guard["n_audited_episode_arms"] == 96
    assert result["checks"]["no_candidate_metadata_leakage"] == (
        guard["status"] == e.LeakageVerdict.PASS
    )
    assert set(guard["status_counts"]) <= {"PASS", "FAIL", "CANNOT_CHECK"}


def test_the_repaired_leakage_guard_finds_the_leak_it_was_named_for():
    """This is the finding, pinned. The frozen core embeds the episode id -- and
    therefore the -A/-C/-U pair role -- in every root problem_id, so every
    episode/arm leaks role to the candidate provider boundary."""
    e = load_eval()
    pairs, unresolved = e.fixed_corpus()
    result = e.evaluate(pairs, unresolved)
    guard = result["guard_verdicts"]["candidate_metadata_leakage"]

    assert guard["status"] == e.LeakageVerdict.FAIL
    assert guard["status_counts"] == {"FAIL": 96}
    assert guard["hit_categories"]["episode_id_and_pair_role"] == 96
    assert result["checks"]["no_candidate_metadata_leakage"] is False
    assert result["terminal"] == "P1_R6_NATIVE_PRIMARY_NOT_SUPPORTED"


def test_the_leak_is_available_but_the_frozen_host_does_not_exploit_it():
    """Severity bound for the finding above, measured rather than asserted.

    The frozen deterministic provider keys only off ``problem.scope`` and the
    retrieved item content, so anonymising the episode id changes no ARD choice.
    The leak is therefore *available* and not *exploited by this host* -- which
    is a property of the host, not of the protocol, and the campaign's own next
    step is a changed, semantic host.
    """
    e = load_eval()
    pairs, _ = e.fixed_corpus()
    changed = 0
    total = 0
    for pair in pairs:
        note = str(pair["pair_evidence"]["source_claim"])
        for member in ("adverse", "control"):
            episode = dict(pair[member])
            anonymised = dict(episode)
            anonymised["id"] = "EPISODE-XXXX"
            total += 1
            changed += int(
                e.NATIVE.run_native_ard(episode, evidence_note=note)["choice"]
                != e.NATIVE.run_native_ard(anonymised, evidence_note=note)["choice"]
            )
    assert total == 44
    assert changed == 0


def test_payload_recorder_changes_no_scored_field():
    """The recording wrapper must append and delegate, nothing else."""
    e = load_eval()
    pairs, _ = e.fixed_corpus()
    ep = pairs[0]["adverse"]
    note = str(pairs[0]["pair_evidence"]["source_claim"])

    plain = e.NATIVE.run_native_ard(ep, evidence_note=note)
    with e.record_provider_payloads() as sink:
        recorded = e.NATIVE.run_native_ard(ep, evidence_note=note)

    assert len(sink) > 0
    ignore = {"root", "probe_executions", "digest"}
    assert {k: v for k, v in plain.items() if k not in ignore} == {
        k: v for k, v in recorded.items() if k not in ignore
    }
    assert plain["choice"] == recorded["choice"]
    # and the class attribute is restored afterwards
    core = e.NATIVE._CORE
    assert core.FrozenNativeProviderHost.__call__.__qualname__.startswith(
        "FrozenNativeProviderHost"
    )


def test_payloads_can_be_re_audited_from_the_sink_with_a_corrected_token_set():
    """The predecessor kept only a digest, so a leakage finding could never be
    re-audited. Mutation: drop ``payload_sink``."""
    e = load_eval()
    pairs, unresolved = e.fixed_corpus()
    sink: dict[str, list[dict[str, str]]] = {}
    e.evaluate(pairs, unresolved, payload_sink=sink)
    assert len(sink) == 96
    key = "R5-SEARCH-P1-A::ORION_NATIVE_ARD"
    assert key in sink
    reaudit = e.leakage_audit(sink[key], {"R5-SEARCH-P1-A": "episode_id_and_pair_role"})
    assert reaudit.status == e.LeakageVerdict.FAIL
