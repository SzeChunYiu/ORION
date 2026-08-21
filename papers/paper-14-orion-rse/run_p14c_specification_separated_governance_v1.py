from __future__ import annotations

import hashlib
import json
from pathlib import Path

CASES = Path(__file__).with_name("P14C_ADJUDICATION_CASES_V1.json")
OUT = Path(__file__).with_name("P14C_SPECIFICATION_SEPARATED_RESULT_V1.json")

PRIVATE_KEYS = {"case_id", "stratum", "gold_disposition", "rationale"}


def facts_only(case: dict[str, object]) -> dict[str, bool]:
    facts = {k: v for k, v in case.items() if k not in PRIVATE_KEYS}
    if "gold_disposition" in facts:
        raise AssertionError("gold leaked into policy input")
    return {k: bool(v) for k, v in facts.items()}


def full_policy(c: dict[str, bool]) -> str:
    if not c["evidence_integrity"] or not c["frozen_protocol"] or not c["identifiable"]:
        return "CANNOT_CHECK"
    if not c["positive"]:
        return "NEGATIVE"
    if c["donor_owned"]:
        return "SUBSUMED"
    if c["interaction_only"]:
        return "INTERACTION_ONLY"
    if c["live_negative_history"] and not c["material_new_evidence"]:
        return "RETAIN_NEGATIVE"
    return "SUPPORTED_RESIDUAL"


def raw_positive(c: dict[str, bool]) -> str:
    return "SUPPORTED_RESIDUAL" if c["positive"] else "NEGATIVE"


def reflection(c: dict[str, bool]) -> str:
    if not c["evidence_integrity"] or not c["frozen_protocol"] or not c["identifiable"]:
        return "CANNOT_CHECK"
    return "SUPPORTED_RESIDUAL" if c["positive"] else "NEGATIVE"


def donor_aware(c: dict[str, bool]) -> str:
    x = reflection(c)
    if x == "SUPPORTED_RESIDUAL" and c["donor_owned"]:
        return "SUBSUMED"
    return x


def multi_review(c: dict[str, bool]) -> str:
    x = donor_aware(c)
    if x == "SUPPORTED_RESIDUAL" and c["interaction_only"]:
        return "INTERACTION_ONLY"
    return x


def ablated(c: dict[str, bool], field: str) -> str:
    d = dict(c)
    if field in {"evidence_integrity", "frozen_protocol", "identifiable"}:
        d[field] = True
    elif field in {"donor_owned", "interaction_only", "live_negative_history"}:
        d[field] = False
    else:
        raise AssertionError(field)
    return full_policy(d)


def score(cases: list[dict[str, object]], predictor) -> dict[str, float | int]:
    n = len(cases)
    correct = false_promote = supported_total = supported_promoted = 0
    retain_total = retain_correct = reopen_total = reopen_correct = 0
    for case in cases:
        gold = str(case["gold_disposition"])
        pred = predictor(facts_only(case))
        correct += int(pred == gold)
        false_promote += int(pred == "SUPPORTED_RESIDUAL" and gold != "SUPPORTED_RESIDUAL")
        supported_total += int(gold == "SUPPORTED_RESIDUAL")
        supported_promoted += int(pred == "SUPPORTED_RESIDUAL" and gold == "SUPPORTED_RESIDUAL")
        if case["stratum"] == "RETAIN_NEGATIVE":
            retain_total += 1
            retain_correct += int(pred == gold)
        if case["stratum"] == "SUPPORTED_REOPEN":
            reopen_total += 1
            reopen_correct += int(pred == gold)
    return {
        "n": n,
        "disposition_accuracy": correct / n,
        "false_promotion_rate": false_promote / n,
        "useful_discovery_recall": supported_promoted / supported_total,
        "retain_negative_accuracy": retain_correct / retain_total,
        "supported_reopen_accuracy": reopen_correct / reopen_total,
    }


def main() -> None:
    payload = json.loads(CASES.read_text(encoding="utf-8"))
    cases = list(payload["cases"])
    if len(cases) != 28:
        raise AssertionError("expected 28 frozen adjudication cases")

    arms = {
        "RAW_POSITIVE": raw_positive,
        "REFLECTION_CHECKLIST": reflection,
        "DONOR_AWARE_REVIEW": donor_aware,
        "MULTI_REVIEW": multi_review,
        "ORION_RSE_FULL": full_policy,
        "ABLATE_EVIDENCE_INTEGRITY": lambda c: ablated(c, "evidence_integrity"),
        "ABLATE_FREEZE": lambda c: ablated(c, "frozen_protocol"),
        "ABLATE_IDENTIFIABILITY": lambda c: ablated(c, "identifiable"),
        "ABLATE_DONOR": lambda c: ablated(c, "donor_owned"),
        "ABLATE_INTERACTION": lambda c: ablated(c, "interaction_only"),
        "ABLATE_NEGATIVE_HISTORY": lambda c: ablated(c, "live_negative_history"),
    }
    summary = {name: score(cases, fn) for name, fn in arms.items()}
    baselines = ("RAW_POSITIVE", "REFLECTION_CHECKLIST", "DONOR_AWARE_REVIEW", "MULTI_REVIEW")
    strongest = max(baselines, key=lambda a: float(summary[a]["disposition_accuracy"]))
    full = summary["ORION_RSE_FULL"]
    ablation_names = tuple(a for a in arms if a.startswith("ABLATE_"))
    gates = {
        "full_accuracy_one": full["disposition_accuracy"] == 1.0,
        "full_zero_false_promotion": full["false_promotion_rate"] == 0.0,
        "full_discovery_recall_one": full["useful_discovery_recall"] == 1.0,
        "retain_and_reopen_exact": full["retain_negative_accuracy"] == 1.0 and full["supported_reopen_accuracy"] == 1.0,
        "strongest_baseline_false_promotion_ge_0_10": summary[strongest]["false_promotion_rate"] >= 0.10,
        "accuracy_advantage_ge_0_10": full["disposition_accuracy"] - summary[strongest]["disposition_accuracy"] >= 0.10,
        "every_ablation_worse": all(summary[a]["disposition_accuracy"] < full["disposition_accuracy"] for a in ablation_names),
        "gold_stripped_from_policy_input": all("gold_disposition" not in facts_only(c) for c in cases),
    }
    terminal = (
        "P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_SUPPORTED"
        if all(gates.values())
        else "P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_GATE_NOT_MET"
    )
    result = {
        "schema": "ORION.P14C.SpecificationSeparatedGovernance.v1",
        "protocol": "P14C_SPECIFICATION_SEPARATED_GOVERNANCE_PROTOCOL_V1.md",
        "adjudication_spec": "P14C_ADJUDICATION_CASES_V1.json",
        "case_count": len(cases),
        "strongest_non_orion_baseline": strongest,
        "summary": summary,
        "gates": gates,
        "terminal": terminal,
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    OUT.write_text(text, encoding="utf-8")
    print(json.dumps({
        "terminal": terminal,
        "strongest": strongest,
        "full": full,
        "strongest_metrics": summary[strongest],
        "gates": gates,
        "sha256": hashlib.sha256(text.encode()).hexdigest(),
    }, indent=2, sort_keys=True))
    if terminal != "P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_SUPPORTED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
