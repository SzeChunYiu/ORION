#!/usr/bin/env python3
"""Corrected-metric run. Protocol: REPAIR_DIAGNOSIS_V1.md, frozen before this ran.

check_repair_v1.py used a coordinate-sensitive vacuity list that predated the repair's
new coordinate, and so convicted the legitimate transport route along with the attack.
That receipt stands; this is a separate, separately declared check.

The metric here is run against BOTH classifiers. Against the unrepaired one it must still
find the attack, or it has defined the problem away.
"""
from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SUBJECT = (
    ROOT
    / "papers/orion-16-formal-epistemic-structures-and-mechanics/top_tier"
    / "check_real_transition_audit_independent_v1.py"
)
CASES = SUBJECT.parent / "p6_real_transition_cases_v1.json"
GOLD = SUBJECT.parent / "p6_real_transition_gold_v1.json"
PROTOCOL = HERE / "REPAIR_DIAGNOSIS_V1.md"
EXPECTED_SUBJECT_SHA = "698f49ca952f59ec015ff50aafec9f78a44c4a17481723dcede4a3b5e4c8c4db"

FIELDS = (
    "execution_support",
    "provenance_binding",
    "source_current",
    "evidence_transport_known",
    "evidence_transport_valid",
    "obligations_clear",
    "generic_permission",
    "commit_authority",
)
NEW = "transport_vacuous"
TRANSPORT = ("evidence_transport_known", "evidence_transport_valid")


def vacuously_satisfiable(coord: str, dest: dict) -> bool:
    """State-sensitive vacuity. See REPAIR_DIAGNOSIS_V1.md."""
    if coord == "obligations_clear":
        return True  # O_h = emptyset is always an available re-grounding
    if coord in TRANSPORT:
        return bool(dest[NEW])  # vacuous exactly when the route transports nothing
    return False


def main() -> int:
    got = hashlib.sha256(SUBJECT.read_bytes()).hexdigest()
    if got != EXPECTED_SUBJECT_SHA:
        raise RuntimeError(f"subject changed since freeze: {got}")
    spec = importlib.util.spec_from_file_location("orion16_rta", SUBJECT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    classify = module.classify

    def repaired(c: dict) -> str:
        return "CANNOT_CHECK" if c.get(NEW, False) else classify(c)

    states = [
        {**dict(zip(FIELDS, b)), NEW: v}
        for b in itertools.product((False, True), repeat=8)
        for v in (False, True)
    ]
    ALL = FIELDS + (NEW,)

    def scan(fn):
        verdicts = [fn(s) for s in states]
        amp, obligations_only = [], 0
        for i, a in enumerate(states):
            if verdicts[i] != "CANNOT_CHECK":
                continue
            for j, b in enumerate(states):
                if verdicts[j] != "ADMISSIBLE":
                    continue
                delta = [f for f in ALL if a[f] != b[f]]
                if not delta or any(a[f] and not b[f] for f in delta):
                    continue
                if all(vacuously_satisfiable(f, b) for f in delta):
                    amp.append({"flips": delta, "dest_transport_vacuous": b[NEW]})
                    if delta == ["obligations_clear"]:
                        obligations_only += 1
        return amp, obligations_only

    amp_unrepaired, obl_unrepaired = scan(classify)
    amp_repaired, obl_repaired = scan(repaired)

    cases = json.loads(CASES.read_text(encoding="utf-8"))["cases"]
    gold = json.loads(GOLD.read_text(encoding="utf-8"))["gold"]
    gold_broken = [
        {"id": c["id"], "got": repaired({**{f: bool(c[f]) for f in FIELDS}, NEW: False}), "gold": gold[c["id"]]}
        for c in cases
        if repaired({**{f: bool(c[f]) for f in FIELDS}, NEW: False}) != gold[c["id"]]
    ]

    holds = {
        "P1_metric_still_detects_attack_unrepaired": len(amp_unrepaired) > 0,
        "P2_zero_amplifying_after_repair": len(amp_repaired) == 0,
        "P3_gold_preserved": not gold_broken,
        "P4_no_obligations_only_edge": obl_unrepaired == 0 and obl_repaired == 0,
    }
    failed = [k for k, v in holds.items() if not v]

    payload = {
        "schema": "A6.AmplificationRepairCheck.v2",
        "supersedes_metric_of": "check_repair_v1.py (coordinate-sensitive vacuity list)",
        "prior_receipt_stands": "REPAIR_RESULT_V1.json records P1 failing and is not edited",
        "subject": str(SUBJECT.relative_to(ROOT)),
        "subject_sha256": got,
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "metric": "state-sensitive vacuity: transport coords vacuous iff dest transport_vacuous",
        "states_enumerated": len(states),
        "amplifying_edges_unrepaired": len(amp_unrepaired),
        "amplifying_edges_repaired": len(amp_repaired),
        "obligations_only_edges_unrepaired": obl_unrepaired,
        "obligations_only_edges_repaired": obl_repaired,
        "all_unrepaired_edges_use_vacuous_transport": all(
            e["dest_transport_vacuous"] for e in amp_unrepaired
        ),
        "gold_verdicts_checked": len(cases),
        "gold_broken": gold_broken,
        "predictions": holds,
        "predictions_failed": failed,
        "predicates_not_evaluated": [
            "whether transport_vacuous can be misreported — it can; the repair relocates "
            "trust onto a fact of the derivation rather than removing trust",
            "whether the repair is sound over ORION-16's full formal core rather than this "
            "eight-coordinate audit classifier",
            "whether the VACUOUS reading is the papers' intended one, which is argued in "
            "../A6_AMPLIFICATION_COUNTEREXAMPLE_V1.md and not proved",
        ],
        "scientific_authority_delta": "NONE",
        "verdict": "REPAIR_HOLDS_UNDER_CORRECTED_METRIC_WITH_CONTROL"
        if not failed
        else "REPAIR_UNSETTLED__" + ",".join(failed),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["receipt_sha256"] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
