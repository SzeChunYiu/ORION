"""P14E's published positive: P14A's unchanged thresholds on a benchmark where
they are attainable, under the specification separation P14B lacked.

Every number pinned here was read off the shipped artifacts
``papers/paper-14-orion-rse/P14E_ADJUDICATION_RULES_V1.json``,
``run_p14e_specification_separated_superiority_v1.py`` and
``P14E_SUPERIORITY_RESULT_V1.json``, or produced by driving that runner's own
``Adjudicator``, ``full_policy`` and ``facts_only``.
"""

from __future__ import annotations

import importlib.util
import itertools
import json
from pathlib import Path

PAPER_DIR = Path(__file__).parents[4] / "papers" / "paper-14-orion-rse"
RUNNER_PATH = PAPER_DIR / "run_p14e_specification_separated_superiority_v1.py"
RULES_PATH = PAPER_DIR / "P14E_ADJUDICATION_RULES_V1.json"
RESULT_PATH = PAPER_DIR / "P14E_SUPERIORITY_RESULT_V1.json"

COMMITTED_CORE_SHA256 = "9950c27c2eebf885dda8b958c9446c5a8d70746788718209c517059ef9140795"
COMMITTED_RESULT_SHA256 = "410db4554585e5ce9b6f94b01cc92d7f116f9fd693b60bca2e1ac1eeb4f51679"
TERMINAL = "P14E_SPECIFICATION_SEPARATED_SUPERIORITY_SUPPORTED"


def runner_module():
    spec = importlib.util.spec_from_file_location("p14e_runner", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def committed_result() -> dict:
    return json.loads(RESULT_PATH.read_text(encoding="utf-8"))


def test_committed_result_terminal_and_gates():
    result = committed_result()
    assert result["terminal"] == TERMINAL
    assert result["strongest_non_orion_baseline"] == "MULTI_REVIEW"
    assert all(result["gates"].values())
    assert result["replay"]["byte_identical"] is True


def test_build_core_reproduces_committed_digest():
    import hashlib

    module = runner_module()
    core = module.build_core()
    # Runtime identity is receipt metadata, not a scientific input. Rebuild the
    # scientific core locally, then normalize only that metadata to the frozen
    # execution environment before checking the exact committed digest.
    core["environment"] = committed_result()["core"]["environment"]
    text = module.canonical_text(core)
    assert hashlib.sha256(text.encode()).hexdigest() == COMMITTED_CORE_SHA256


def test_p14a_thresholds_unchanged_and_met():
    """The two P14A bars, verbatim, read on P14E's summary."""
    summary = committed_result()["core"]["summary"]
    full = summary["ORION_RSE_FULL"]
    strongest = summary["MULTI_REVIEW"]
    assert full["disposition_accuracy"] - strongest["disposition_accuracy"] >= 0.08
    assert strongest["false_promotion_rate"] >= 0.05
    assert full["false_promotion_rate"] == 0.0
    assert full["useful_discovery_recall"] == 1.0


def test_generation_audit_clean():
    audit = committed_result()["core"]["generation_audit"]
    assert audit["remint_violations"] == 0
    assert audit["determinism_violations"] == 0
    assert audit["gold_stratum_violations"] == 0
    assert audit["pinned_violations"] == 0
    assert audit["gold_leak_checks"] == committed_result()["core"]["design"]["total_cases"] == 6720


def test_interpreter_agrees_with_independent_policy_everywhere():
    """Circularity control: on all 2^8 fact combinations, the interpreted rule
    table and the independently written policy issue the same disposition."""
    module = runner_module()
    adjudicator = module.Adjudicator(json.loads(RULES_PATH.read_text(encoding="utf-8")))
    names = list(module.FACTS)
    for combo in itertools.product((False, True), repeat=len(names)):
        facts = dict(zip(names, combo))
        assert adjudicator.adjudicate(facts) == module.full_policy(facts), facts


def test_facts_only_strips_private_keys():
    module = runner_module()
    case = {"stratum": "NEGATIVE", "case_id": "NG-00", **dict.fromkeys(module.FACTS, False),
            "gold_disposition": "NEGATIVE", "rationale": "x"}
    view = module.facts_only(case)
    assert set(view) == set(module.FACTS)
    assert module.facts_only({"gold_disposition": "NEGATIVE", "positive": True}) == {"positive": True}


def test_historical_negatives_retained_verbatim():
    """P14E appends authority; it never edits the parents' dispositions."""
    receipt = json.loads(
        (PAPER_DIR / "P14A_CONTROLLED_GOVERNANCE_RESULT_RECEIPT_V1.json").read_text(encoding="utf-8")
    )
    assert receipt["terminal"] == "P14A_CONTROLLED_GOVERNANCE_SUPERIORITY_GATE_NOT_MET"
    assert receipt["gates"]["accuracy_gain_ge_0_08"] is False
    assert receipt["gates"]["strongest_baseline_false_promotion_ge_0_05"] is False
