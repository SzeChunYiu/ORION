from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / "research/claim_expansion/p1/gpt_r1/run_ard_exact_pilot.py"
EXPECTED = ROOT / "research/claim_expansion/p1/gpt_r1/ARD_EXPECTED_EXACT_RESULT_V1.json"


def _load_module():
    spec = importlib.util.spec_from_file_location("p1_u_ard_exact_pilot", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Python 3.12 dataclasses resolve postponed string annotations through
    # sys.modules while a class is being decorated.  Register the module before
    # executing it, exactly as the normal import machinery does.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_frozen_ard_exact_pilot_matches_independent_reconstruction() -> None:
    module = _load_module()
    report = module.build_report()
    expected = json.loads(EXPECTED.read_text())

    assert report["template_count"] == expected["distinct_template_count"] == 40
    assert report["remints_per_template"] == expected["remints_per_template"] == 12
    assert report["concrete_episode_count"] == expected["concrete_episode_count"] == 480
    assert report["remints_are_independent_n"] is False

    for system, exp in expected["expected_summary"].items():
        got = report["summary"][system]
        assert got["template_grs"] == exp["template_grs"]
        assert got["false_high_level"] == exp["false_high_level"]
        assert got["missed_high_level"] == exp["missed_high_level"]
        assert got["mean_cost"] == exp["mean_cost"]

    assert report["ard_minus_b3_grs"] == expected["expected_ard_minus_b3_grs"] == 0.25
    assert report["domain_effects"] == expected["expected_domain_effects"]
    assert report["gates"] == expected["expected_gates"]
    assert report["terminal"] == expected["expected_terminal"] == "ARD_EXACT_MECHANISM_POSITIVE"


def test_ard_positive_is_non_authorizing_and_remints_are_not_repeat_inflation() -> None:
    module = _load_module()
    report = module.build_report()

    assert report["authority"] == {
        "general_p1_u_superiority": False,
        "runtime_registration": False,
        "adoption_or_merge": False,
    }
    assert report["remints_are_independent_n"] is False
    assert all(report["gates"].values())


def test_non_identifiable_templates_fail_closed() -> None:
    module = _load_module()
    report = module.build_report()
    rows = [r for r in report["templates"] if r["family"] == "NON_IDENTIFIABLE"]
    assert len(rows) == 5
    for row in rows:
        assert row["correct_terminal"] == "UNRESOLVED"
        assert (
            row["systems"]["P1_ARD_HORIZON2_SCIENTIFIC_RESPONSIBILITY"]["decision"]
            == "UNRESOLVED"
        )
        assert row["systems"]["P1_ARD_HORIZON2_SCIENTIFIC_RESPONSIBILITY"]["grs"] == 1
        assert row["systems"]["B3_ONE_STEP_DECISION_VOI"]["grs"] == 0


def test_ard_matches_full_information_policy_ceiling_on_every_template() -> None:
    module = _load_module()
    report = module.build_report()
    for row in report["templates"]:
        ard = row["systems"]["P1_ARD_HORIZON2_SCIENTIFIC_RESPONSIBILITY"]
        ceiling = row["systems"]["CEILING_HORIZON2_FULL_SCIENTIFIC_ORACLE"]
        assert ard["decision"] == ceiling["decision"]
        assert ard["grs"] == ceiling["grs"]
        assert ard["cost"] == ceiling["cost"]
