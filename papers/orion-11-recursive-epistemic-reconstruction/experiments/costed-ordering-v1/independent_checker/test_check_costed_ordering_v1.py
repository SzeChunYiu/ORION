#!/usr/bin/env python3
"""Validation of the independent checker against synthetic traces.

Two obligations, weighted equally:

  FIRES   -- each defect the checker claims to catch produces the right
             fault class, the right terminal and exit code 3.
  SILENT  -- a clean trace produces exit 0, an empty fault list, an empty
             refusal-class list and only the documented benign warning. A
             checker that cries wolf on its first real run gets switched off,
             so the no-alarm case is asserted, not assumed.

Also asserted explicitly, because it is the distinction the whole instrument
rests on: an UNFAVOURABLE terminal exits 0. Falsified is a checked result,
not an error.

Run directly (`python3 test_check_costed_ordering_v1.py`) or under pytest.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

from independent_checker import _constants as K  # noqa: E402
from independent_checker import _faults as F  # noqa: E402
from independent_checker import _test_fixtures as FX  # noqa: E402
from independent_checker import check_costed_ordering_v1 as CHECK  # noqa: E402
from independent_checker import _terminal as T  # noqa: E402

PACKET = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TERMINALS = os.path.join(PACKET, "EXPECTED_TERMINALS.json")
FAST = ["--resamples", "400", "--seed-probes", "0", "--quiet"]

BENIGN_WARNINGS = {"OPTIONAL_ARM_ABSENT"}


def run(rows, extra=None, traces_name="raw_traces.jsonl"):
    """Run the checker over `rows`; return (exit_code, report)."""
    with tempfile.TemporaryDirectory() as tmp:
        traces = os.path.join(tmp, traces_name)
        if rows is not None:
            FX.write_jsonl(traces, rows)
        out = os.path.join(tmp, "report.json")
        argv = [traces, "--terminals", TERMINALS, "--out", out] + FAST + list(extra or [])
        code = CHECK.main(argv)
        with open(out, "r", encoding="utf-8") as handle:
            return code, json.load(handle)


def assert_fires(report, code, fault_class, expected_terminal=...):
    assert code == K.EXIT_CANNOT_CHECK, f"expected exit 3, got {code}"
    assert report["status"] == "CANNOT_CHECK", report["status"]
    assert fault_class in report["refusal_classes"], (
        f"expected fault {fault_class}, got {report['refusal_classes']}"
    )
    if expected_terminal is not ...:
        assert report["terminal"] == expected_terminal, report["terminal"]


# ---------------------------------------------------------------- SILENT --


def test_clean_trace_raises_no_alarm():
    code, report = run(FX.clean_rows())
    assert code == K.EXIT_CHECKED, (code, report["refusal_classes"], report["faults"])
    assert report["status"] == "CHECKED"
    assert report["faults"] == [], report["faults"]
    assert report["refusal_classes"] == [], report["refusal_classes"]
    seen = {w["warning_class"] for w in report["warnings"]}
    assert seen <= BENIGN_WARNINGS, f"unexpected warnings: {seen - BENIGN_WARNINGS}"
    assert report["independence"]["independent"] is True
    assert report["terminal"] == T.T_SUPPORTED, report["decision"]["selection_reasoning"]
    assert report["decision"]["gate_states"] == {
        "G1": "PASS",
        "G2": "PASS",
        "G3": "PASS",
        "G4": "PASS",
        "G5": "PASS",
        "G6": "PASS",
        "G7": "PASS",
    }, report["decision"]["gate_states"]


def test_clean_trace_with_optional_arm_present():
    code, report = run(FX.clean_rows(include_optional_arm=True))
    assert code == K.EXIT_CHECKED
    assert report["faults"] == []
    assert report["warnings"] == [], report["warnings"]


def test_a4_trace_schema_spelling_is_accepted_not_refused():
    rows = FX.clean_rows(a4_spelling="violate_A4_nonnegative_cost")
    code, report = run(rows)
    assert code == K.EXIT_CHECKED, report["refusal_classes"]
    assert report["faults"] == []
    assert any("violate_A4" in d for d in report["protocol_defects"])
    assert K.STRATUM_A4 in report["analysis"]["strata_present"]


def test_terminal_is_always_drawn_from_the_frozen_set():
    with open(TERMINALS, "r", encoding="utf-8") as handle:
        frozen = {t["id"] for t in json.load(handle)["terminals"]}
    for rows in (FX.clean_rows(), FX.clean_rows(pc_forbidden_outside_ratio_aligned=False)):
        _, report = run(rows)
        assert report["terminal"] in frozen, report["terminal"]


# ------------------------------------------------- EXIT-CODE SEMANTICS --


def test_unfavourable_terminal_exits_zero():
    """Theorem C's predicted falsification is a CHECKED result, not an error."""
    rows = FX.clean_rows(pc_forbidden_outside_ratio_aligned=False)
    code, report = run(rows)
    assert code == K.EXIT_CHECKED, (code, report["refusal_classes"])
    assert report["terminal"] == T.T_PC_BASELINE, report["decision"]
    assert report["terminal_class"] == "UNFAVOURABLE__PRIMARY_PREDICTED"
    assert report["decision"]["gate_states"]["G3"] == "PASS"
    assert report["decision"]["gate_states"]["G6"] == "FAIL"
    assert "G6 dominates G3" in " ".join(report["decision"]["selection_reasoning"])


def test_forbidden_mutation_on_a3_holding_stratum_is_a_checked_failure():
    rows = FX.mutate(
        FX.clean_rows(),
        FX.find(K.ARM_ORION, K.STRATUM_THEOREM_VALID),
        lambda r: r.update(forbidden_high_level_mutation=True),
    )
    code, report = run(rows)
    assert code == K.EXIT_CHECKED
    assert report["terminal"] == T.T_FORBIDDEN
    assert report["decision"]["gate_states"]["G2"] == "FAIL"


def test_forbidden_mutation_only_where_a3_is_violated_does_not_fail_g2():
    rows = FX.mutate(
        FX.clean_rows(),
        FX.find(K.ARM_ORION, K.STRATUM_A3),
        lambda r: r.update(forbidden_high_level_mutation=True),
    )
    code, report = run(rows)
    assert code == K.EXIT_CHECKED
    g2 = report["analysis"]["gates"]["G2"]["components"]
    assert g2["terminal_a3_scoped_pass"] is True
    assert g2["literal_every_stratum_pass"] is False
    assert report["decision"]["gate_states"]["G2"] == "PASS"


# ----------------------------------------------------------------- FIRES --


def test_fires_on_non_decomposing_row():
    rows = FX.mutate(
        FX.clean_rows(),
        FX.find(K.ARM_ORION),
        lambda r: r["cost"].update(total=r["cost"]["total"] + 0.25),
    )
    code, report = run(rows)
    assert_fires(
        report, code, F.FAULT_UNDECOMPOSABLE_COST, "CANNOT_CHECK__COST_TRACE_UNDECOMPOSABLE"
    )


def test_fires_on_actions_disagreeing_with_components():
    def break_actions(row):
        row["actions"][0]["cost"] += 0.5
        row["actions"].append(
            {
                "step": 99,
                "kind": "inspection",
                "level": 0,
                "target": "phantom",
                "cost_component": "inspection",
                "cost": -0.5,
            }
        )

    rows = FX.mutate(FX.clean_rows(), FX.find(K.ARM_FAITHFUL), break_actions)
    code, report = run(rows)
    # The phantom action is itself negative, which the accounting rejects first.
    assert code == K.EXIT_CANNOT_CHECK
    assert report["refusal_classes"], report["refusal_classes"]

    rows = FX.mutate(
        FX.clean_rows(),
        FX.find(K.ARM_FAITHFUL),
        lambda r: r["actions"][0].update(cost=r["actions"][0]["cost"] + 0.5)
        or r["actions"][1].update(cost=r["actions"][1]["cost"] - 0.5),
    )
    code, report = run(rows)
    assert_fires(
        report,
        code,
        F.FAULT_ACTIONS_DISAGREE_WITH_COMPONENTS,
        "CANNOT_CHECK__COST_TRACE_UNDECOMPOSABLE",
    )


def test_fires_on_negative_cost_component():
    rows = FX.mutate(
        FX.clean_rows(),
        FX.find(K.ARM_ORION, K.STRATUM_A4),
        lambda r: r["cost"].update(reopening=-0.2, total=r["cost"]["total"] - 0.4),
    )
    code, report = run(rows)
    assert_fires(report, code, F.FAULT_NEGATIVE_COST_COMPONENT)


def test_fires_on_missing_actions():
    rows = FX.mutate(FX.clean_rows(), FX.find(K.ARM_ORION), lambda r: r.pop("actions"))
    code, report = run(rows)
    assert code == K.EXIT_CANNOT_CHECK
    assert F.FAULT_MALFORMED_TRACE in report["refusal_classes"]


def test_fires_on_missing_gate_consumed_arm():
    rows = [r for r in FX.clean_rows() if r["arm_id"] != K.ARM_FAITHFUL]
    code, report = run(rows)
    assert_fires(report, code, F.FAULT_MISSING_GATE_CONSUMED_ARM)
    blocked = report["faults"][0]["examples"][0]["gates_blocked"]
    assert set(blocked) == {"G1", "G3", "G5"}, blocked


def test_fires_on_broken_pairing():
    rows = FX.clean_rows()
    victim = next(r for r in rows if r["arm_id"] == K.ARM_GLOBAL_FLAT)
    rows = [r for r in rows if not (r["arm_id"] == victim["arm_id"] and r["world_id"] == victim["world_id"])]
    code, report = run(rows)
    assert code == K.EXIT_CANNOT_CHECK
    assert {F.FAULT_ARM_COVERAGE, F.FAULT_PAIRING_INCOMPLETE} & set(report["refusal_classes"])


def test_fires_on_contaminated_row():
    for key, value in (
        ("G3", {"passed": True}),
        ("terminal", "H_SUPPORTED__SAFETY_PRICED_LEVEL_ORDERING"),
        ("bootstrap_ci_high", 0.71),
        ("g6_pass", False),
    ):
        rows = FX.mutate(FX.clean_rows(), FX.find(K.ARM_ORION), lambda r: r.update({key: value}))
        code, report = run(rows)
        assert_fires(report, code, F.FAULT_CONTAMINATED_ROW)
        assert report["terminal"] is None
        assert report["terminal_status"] == F.NO_FROZEN_TERMINAL


def test_fires_on_both_a4_spellings_in_one_file():
    rows = FX.clean_rows()
    for row in rows:
        if row["stratum"] == K.STRATUM_A4 and row["world_id"].endswith("000"):
            row["stratum"] = "violate_A4_nonnegative_cost"
    code, report = run(rows)
    assert_fires(report, code, F.FAULT_STRATUM_ALIAS_COLLISION)


def test_fires_on_duplicate_world_arm_row():
    rows = FX.clean_rows()
    rows.append(dict(rows[0]))
    code, report = run(rows)
    assert_fires(report, code, F.FAULT_DUPLICATE_ROW)


def test_fires_on_oracle_outside_its_registered_strata():
    rows = FX.clean_rows()
    stray = dict(next(r for r in rows if r["arm_id"] == K.ARM_ORACLE))
    stray["stratum"] = K.STRATUM_A1
    stray["world_id"] = f"w_{K.STRATUM_A1}_000"
    rows.append(stray)
    code, report = run(rows)
    assert_fires(report, code, F.FAULT_ORACLE_PLACEMENT)


def test_fires_on_missing_oracle_with_its_own_frozen_terminal():
    rows = [r for r in FX.clean_rows() if r["arm_id"] != K.ARM_ORACLE]
    code, report = run(rows)
    assert_fires(report, code, F.FAULT_DP_ORACLE_INFEASIBLE, "CANNOT_CHECK__DP_ORACLE_INFEASIBLE")


def test_fires_on_g7_instrument_fault_and_refuses_to_invent_a_terminal():
    rows = FX.mutate(
        FX.clean_rows(),
        FX.find(K.ARM_PC_GREEDY, K.STRATUM_RATIO_ALIGNED),
        lambda r: r["actions"][0].update(target="divergent_class")
        or r["actions"][0].update(cost=r["actions"][0]["cost"] + 0.3)
        or r["cost"].update(
            inspection=r["cost"]["inspection"] + 0.3, total=r["cost"]["total"] + 0.3
        ),
    )
    code, report = run(rows)
    assert_fires(report, code, F.FAULT_G7_INSTRUMENT, None)
    assert report["terminal_status"] == F.NO_FROZEN_TERMINAL
    assert "EXPECTED_TERMINALS.json enumerates no CANNOT_CHECK terminal" in " ".join(
        report["decision"]["selection_reasoning"]
    )


def test_fires_on_inconsistent_budget_flag():
    rows = FX.mutate(
        FX.clean_rows(), FX.find(K.ARM_ORION), lambda r: r.update(budget_exceeded=True)
    )
    code, report = run(rows)
    assert_fires(report, code, F.FAULT_BUDGET_FLAG_INCONSISTENT)


def test_fires_on_missing_trace_file():
    code, report = run(None)
    assert_fires(report, code, F.FAULT_MISSING_TRACE)


def test_fires_on_malformed_jsonl():
    with tempfile.TemporaryDirectory() as tmp:
        traces = os.path.join(tmp, "raw_traces.jsonl")
        with open(traces, "w", encoding="utf-8") as handle:
            handle.write('{"world_id": "w1", broken\n')
        out = os.path.join(tmp, "report.json")
        code = CHECK.main([traces, "--terminals", TERMINALS, "--out", out] + FAST)
        with open(out, "r", encoding="utf-8") as handle:
            report = json.load(handle)
    assert_fires(report, code, F.FAULT_MALFORMED_TRACE)


# --------------------------------------------------------------- COMPARE --


def _result_from(report, **overrides):
    analysis = report["analysis"]
    result = {
        "terminal": report["terminal"],
        "gates": {
            gid: {"passed": gate["passed"]} for gid, gate in analysis["gates"].items()
        },
        "comparisons": {
            name: {"ratio": c["pooled"]["ratio"], "n_matched": c["pooled"]["n_matched"]}
            for name, c in analysis["comparisons"].items()
        },
    }
    result.update(overrides)
    return result


def test_compare_agreement_exits_zero():
    rows = FX.clean_rows()
    _, report = run(rows)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "RESULT_V1.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(_result_from(report), handle)
        code, out = run(rows, extra=["--compare", path])
    assert code == K.EXIT_CHECKED, out["comparison"]["disagreeing_fields"]
    assert out["comparison"]["n_disagreements"] == 0, out["comparison"]["disagreeing_fields"]
    assert out["comparison"]["n_fields_comparable"] > 0


def test_compare_disagreement_exits_two_and_reports_every_field():
    rows = FX.clean_rows()
    _, report = run(rows)
    bad = _result_from(report, terminal=T.T_COST_RATIO)
    bad["gates"]["G6"]["passed"] = not bad["gates"]["G6"]["passed"]
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "RESULT_V1.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(bad, handle)
        code, out = run(rows, extra=["--compare", path])
    assert code == K.EXIT_DISAGREEMENT, code
    assert out["terminal"] == T.T_DISAGREEMENT
    fields = out["comparison"]["disagreeing_fields"]
    assert "terminal" in fields and "gates.G6.passed" in fields, fields
    assert out["comparison"]["n_disagreements"] >= 2


def test_compare_flags_an_unreproducible_anchor_claim():
    rows = FX.clean_rows()
    _, report = run(rows)
    claim = _result_from(report, anchor_reproduction_gate={"passed": True})
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "RESULT_V1.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(claim, handle)
        code, out = run(rows, extra=["--compare", path])
    assert code == K.EXIT_DISAGREEMENT
    assert "anchor_reproduction_gate" in out["comparison"]["disagreeing_fields"]


def test_anchor_gate_is_reported_unmeasured_never_passed():
    _, report = run(FX.clean_rows())
    anchor = report["analysis"]["anchor_reproduction_gate"]
    assert anchor["counted_as_pass"] is False
    assert anchor["status"].startswith("CANNOT_CHECK__")
    assert any("anchor" in d.lower() for d in report["protocol_defects"])


def test_seed_probe_detects_nothing_on_a_deterministic_fixture():
    with tempfile.TemporaryDirectory() as tmp:
        traces = FX.write_jsonl(os.path.join(tmp, "raw_traces.jsonl"), FX.clean_rows())
        out = os.path.join(tmp, "report.json")
        code = CHECK.main(
            [traces, "--terminals", TERMINALS, "--out", out,
             "--resamples", "400", "--seed-probes", "3", "--quiet"]
        )
        with open(out, "r", encoding="utf-8") as handle:
            report = json.load(handle)
    assert code == K.EXIT_CHECKED
    probe = report["bootstrap"]["seed_stability_probe"]
    assert probe["probed"] is True and probe["seed_sensitive"] is False, probe


def test_seed_sensitive_verdict_is_refused_not_silently_reported():
    """PROTOCOL freezes no seed, so a seed-dependent verdict is not measured."""
    rows = FX.noisy_rows(scale=0.74, noise=0.12)
    with tempfile.TemporaryDirectory() as tmp:
        traces = FX.write_jsonl(os.path.join(tmp, "raw_traces.jsonl"), rows)
        out = os.path.join(tmp, "report.json")
        code = CHECK.main(
            [traces, "--terminals", TERMINALS, "--out", out,
             "--resamples", "400", "--seed-probes", "6", "--quiet"]
        )
        with open(out, "r", encoding="utf-8") as handle:
            report = json.load(handle)
    assert_fires(report, code, F.FAULT_SEED_SENSITIVE_VERDICT)
    probe = report["bootstrap"]["seed_stability_probe"]
    assert probe["seed_sensitive"] is True
    assert len(probe["distinct_terminals"]) > 1, probe
    assert any("seed" in d.lower() for d in report["protocol_defects"])


def test_variance_alone_does_not_trigger_the_seed_probe():
    """The probe must fire on an unstable VERDICT, not merely on noisy data."""
    rows = FX.noisy_rows(scale=0.70, noise=0.12)
    with tempfile.TemporaryDirectory() as tmp:
        traces = FX.write_jsonl(os.path.join(tmp, "raw_traces.jsonl"), rows)
        out = os.path.join(tmp, "report.json")
        code = CHECK.main(
            [traces, "--terminals", TERMINALS, "--out", out,
             "--resamples", "400", "--seed-probes", "6", "--quiet"]
        )
        with open(out, "r", encoding="utf-8") as handle:
            report = json.load(handle)
    assert code == K.EXIT_CHECKED, report["refusal_classes"]
    assert report["faults"] == []
    probe = report["bootstrap"]["seed_stability_probe"]
    assert probe["seed_sensitive"] is False, probe
    ci = report["analysis"]["gates"]["G3"]["components"]["bootstrap"]
    assert ci["ci_low"] < ci["ci_high"], "fixture should carry real variance"


def test_g3_scope_sensitivity_is_surfaced_as_a_protocol_defect():
    _, report = run(FX.clean_rows())
    g3 = report["analysis"]["gates"]["G3"]["components"]
    assert g3["decision_scope"] == list(K.THEOREM_VALID_STRATA)
    assert g3["scope_sensitive"] is True
    assert g3["sensitivity_all_strata"]["point"]["ratio"] is not None
    assert any("G3 fixes no stratum scope" in d for d in report["protocol_defects"])


def test_cli_exit_codes_propagate_through_a_real_process():
    """Exit codes are the interface; assert them from an actual process."""
    import subprocess

    script = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "check_costed_ordering_v1.py")
    cases = [
        (FX.clean_rows(), None, K.EXIT_CHECKED),
        (FX.clean_rows(pc_forbidden_outside_ratio_aligned=False), None, K.EXIT_CHECKED),
        (
            FX.mutate(
                FX.clean_rows(),
                FX.find(K.ARM_ORION),
                lambda r: r["cost"].update(total=r["cost"]["total"] + 0.25),
            ),
            None,
            K.EXIT_CANNOT_CHECK,
        ),
    ]
    for rows, _unused, expected in cases:
        with tempfile.TemporaryDirectory() as tmp:
            traces = FX.write_jsonl(os.path.join(tmp, "raw_traces.jsonl"), rows)
            out = os.path.join(tmp, "report.json")
            proc = subprocess.run(
                [sys.executable, script, traces, "--terminals", TERMINALS,
                 "--out", out, "--resamples", "400", "--seed-probes", "0", "--quiet"],
                capture_output=True, text=True,
            )
        assert proc.returncode == expected, (proc.returncode, expected, proc.stderr[-400:])

    # exit 2 needs a disagreeing result alongside a checkable trace
    rows = FX.clean_rows()
    _, report = run(rows)
    with tempfile.TemporaryDirectory() as tmp:
        traces = FX.write_jsonl(os.path.join(tmp, "raw_traces.jsonl"), rows)
        result = os.path.join(tmp, "RESULT_V1.json")
        with open(result, "w", encoding="utf-8") as handle:
            json.dump({"terminal": T.T_COST_RATIO}, handle)
        out = os.path.join(tmp, "report.json")
        proc = subprocess.run(
            [sys.executable, script, traces, "--terminals", TERMINALS, "--out", out,
             "--compare", result, "--resamples", "400", "--seed-probes", "0", "--quiet"],
            capture_output=True, text=True,
        )
    assert proc.returncode == K.EXIT_DISAGREEMENT, (proc.returncode, proc.stderr[-400:])


def test_checker_imports_nothing_forbidden():
    _, report = run(FX.clean_rows())
    assert report["independence"]["independent"] is True
    assert report["independence"]["offending_modules"] == []


def main() -> int:
    tests = [(n, o) for n, o in sorted(globals().items()) if n.startswith("test_") and callable(o)]
    failures = []
    for name, fn in tests:
        try:
            fn()
        except AssertionError as exc:
            failures.append((name, f"AssertionError: {exc}"))
            print(f"FAIL {name}: {exc}")
        except Exception as exc:  # noqa: BLE001
            failures.append((name, f"{type(exc).__name__}: {exc}"))
            print(f"ERROR {name}: {type(exc).__name__}: {exc}")
        else:
            print(f"ok   {name}")
    print(f"\n{len(tests) - len(failures)}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
