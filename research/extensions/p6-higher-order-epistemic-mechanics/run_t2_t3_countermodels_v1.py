#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from orion.self_orion.revision_gate import assess_revision_gate
from orion.transfer.v2.epistemic_responsibility import (
    assess_responsibility,
    build_responsibility_hypothesis,
)
from orion.transfer.v2.higher_order_epistemic_mechanics import (
    ObligationState,
    assess_mechanic,
    build_mechanic,
)
from orion.transfer.v2.interface_adequacy import (
    InterfaceCheckState,
    assess_interface_adequacy,
    build_interface_check,
)

ROOT = Path(__file__).resolve().parent
PANEL = ROOT / "T2_T3_COUNTERMODELS_V1.json"
SUMMARY = ROOT / "T2_T3_COUNTERMODEL_SUMMARY_V1.json"


def _hypothesis(name: str, expected: dict[str, tuple[str, ...]]):
    return build_responsibility_hypothesis(
        hypothesis_id=name,
        claim_id="claim:t2t3",
        expected_observations=expected,
        support_evidence_ids=(f"evidence:{name}",),
    )


def _responsibility(kind: str):
    if kind == "responsibility_ambiguous":
        hypotheses = (
            _hypothesis("left", {"probe": ("SAME",)}),
            _hypothesis("right", {"probe": ("SAME",)}),
        )
        return assess_responsibility(hypotheses, observed_outcomes={"probe": "SAME"})
    if kind == "responsibility_identified":
        hypotheses = (
            _hypothesis("interface-gap", {"probe": ("INTERFACE",)}),
            _hypothesis("model-gap", {"probe": ("MODEL",)}),
        )
        return assess_responsibility(hypotheses, observed_outcomes={"probe": "INTERFACE"})
    if kind == "responsibility_unresolved":
        hypotheses = (
            _hypothesis(
                "interface-gap",
                {"probe": ("INTERFACE",), "confirm": ("STILL_INTERFACE",)},
            ),
        )
        return assess_responsibility(hypotheses, observed_outcomes={"probe": "INTERFACE"})
    if kind == "responsibility_no_survivor":
        hypotheses = (
            _hypothesis("left", {"probe": ("A",)}),
            _hypothesis("right", {"probe": ("B",)}),
        )
        return assess_responsibility(hypotheses, observed_outcomes={"probe": "C"})
    raise ValueError(kind)


def _interface(state: InterfaceCheckState):
    return assess_interface_adequacy(
        (
            build_interface_check(
                check_id="interface-check",
                scope="FRAME",
                state=state,
                evidence_ids=("evidence:interface",),
                required=True,
            ),
        )
    )


def _gate(kind: str):
    responsibility = _responsibility("responsibility_identified")
    narrow = build_mechanic(
        mechanic_id="repair-interface",
        claim_id="claim:t2t3",
        kind="INTERFACE_REPAIR",
        write_coordinates=("F",),
        hard_requirements=("diagnostic",),
        preservation_obligations=("preserve:model", "preserve:objective"),
    )
    broad = build_mechanic(
        mechanic_id="rewrite-model",
        claim_id="claim:t2t3",
        kind="MODEL_REVISION",
        write_coordinates=("F", "M"),
        hard_requirements=("diagnostic",),
        preservation_obligations=("preserve:objective",),
    )
    mechanics = (narrow, broad)
    obligations = {"diagnostic": ObligationState.SATISFIED}
    assessments = tuple(
        assess_mechanic(mechanic, obligation_states=obligations)
        for mechanic in mechanics
    )
    if kind == "gate_narrow_interface":
        return assess_revision_gate(
            responsibility=responsibility,
            interface=_interface(InterfaceCheckState.FAIL),
            mechanics=mechanics,
            assessments=assessments,
            responsibility_bindings={"interface-gap": ("repair-interface", "rewrite-model")},
            interface_repair_mechanic_ids=("repair-interface",),
            interface_coordinates=("F",),
        )
    if kind == "gate_no_broad_fallback":
        return assess_revision_gate(
            responsibility=responsibility,
            interface=_interface(InterfaceCheckState.FAIL),
            mechanics=mechanics,
            assessments=assessments,
            responsibility_bindings={"interface-gap": ("rewrite-model",)},
            interface_repair_mechanic_ids=(),
            interface_coordinates=("F",),
        )
    if kind == "gate_adequate_minimum":
        return assess_revision_gate(
            responsibility=responsibility,
            interface=_interface(InterfaceCheckState.PASS),
            mechanics=mechanics,
            assessments=assessments,
            responsibility_bindings={"interface-gap": ("repair-interface", "rewrite-model")},
            interface_repair_mechanic_ids=("repair-interface",),
            interface_coordinates=("F",),
        )
    raise ValueError(kind)


def evaluate(case: dict[str, object]) -> tuple[str, str | None]:
    kind = str(case["kind"])
    if kind.startswith("responsibility_"):
        report = _responsibility(kind)
        return report.status.value, report.identified_hypothesis_id
    if kind == "interface_failure":
        report = _interface(InterfaceCheckState.FAIL)
        return report.status.value, None
    if kind == "interface_unresolved":
        report = _interface(InterfaceCheckState.UNRESOLVED)
        return report.status.value, None
    report = _gate(kind)
    return report.status.value, report.selected_mechanic_id


def run(panel: dict[str, object]) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for case in panel["cases"]:
        actual_status, actual_selected = evaluate(case)
        expected_status = str(case["expected_status"])
        expected_selected = case.get("expected_selected")
        passed = actual_status == expected_status and actual_selected == expected_selected
        rows.append(
            {
                "id": case["id"],
                "kind": case["kind"],
                "expected_status": expected_status,
                "actual_status": actual_status,
                "expected_selected": expected_selected,
                "actual_selected": actual_selected,
                "pass": passed,
            }
        )
    n_pass = sum(bool(row["pass"]) for row in rows)
    return {
        "result_version": "P6_T2_T3_COUNTERMODEL_SUMMARY_V1",
        "protocol_id": panel["protocol_id"],
        "n_cases": len(rows),
        "n_pass": n_pass,
        "accuracy": n_pass / len(rows),
        "rows": rows,
        "terminal": panel["expected_terminal"] if n_pass == len(rows) else "T2_T3_COUNTERMODEL_FAILURE",
        "claim_ceiling": panel["claim_ceiling"],
        "grants_scientific_authority": False,
        "grants_self_orion_adoption": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    panel = json.loads(PANEL.read_text())
    result = run(panel)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        SUMMARY.write_text(text)
    if args.check:
        if not SUMMARY.exists() or SUMMARY.read_text() != text:
            raise SystemExit("T2/T3 countermodel summary drift")
    if not args.write and not args.check:
        print(text, end="")


if __name__ == "__main__":
    main()
