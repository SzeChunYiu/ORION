#!/usr/bin/env python3
"""QG-13 V2: prospectively mine combined R6I deletion edits."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
ORION_Q = REPO_ROOT / "research" / "extensions" / "orion-q"
sys.path.insert(0, str(ORION_Q))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa: E402

BASE = "3202e52371d018b5f6547ed44490f089400d8485"
ISSUE = "SzeChunYiu/ORION#777"
DEFAULT_OUTPUT = REPO_ROOT / "artifacts" / "orion-qg-qg13v2-combined-edit.json"
TOKEN = "ORIONQG_QG13V2_COMBINED_EDIT="
ACTIONS = ("A", "B", "AB")


def canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest_payload(v: dict[str, Any]) -> str:
    u = dict(v)
    u.pop("result_digest", None)
    return hashlib.sha256(canonical(u).encode()).hexdigest()


def wt(a: int) -> int:
    return int(r6i._LW[a])


def mul(a: int, b: int) -> int:
    return int(r6i._MUL[a, b])


def sy(a: int, b: int) -> int:
    return int(r6i._SYMP[a, b])


def syn5(r0: int, r1: int, s0: int, s1: int) -> int:
    return (
        (sy(r0, r1) << 4)
        | (sy(s0, r0) << 3)
        | (sy(s1, r0) << 2)
        | (sy(s0, r1) << 1)
        | sy(s1, r1)
    )


def apply_action(r0: int, r1: int, action: str) -> tuple[int, int]:
    if action == "A":
        return 0, r1
    if action == "B":
        return r0, 0
    if action == "AB":
        return 0, 0
    raise ValueError(action)


def deleted_count(r0: int, r1: int, nr0: int, nr1: int) -> int:
    return int(r0 != 0 and nr0 == 0) + int(r1 != 0 and nr1 == 0)


def local_cost(r0: int, r1: int, p0: int, p1: int, p2: int, central: int) -> int:
    r2 = mul(r0, r1)
    m = [4, 4, 4]
    m[central] = 2
    return (
        m[0] * wt(r0)
        + m[1] * wt(r1)
        + m[2] * wt(r2)
        + wt(mul(p0, r0))
        + wt(mul(p1, r1))
        + wt(mul(p2, r2))
    )


def option_code(vals: tuple[int, ...]) -> int:
    code = 0
    for v in vals:
        code = (code << 2) | int(v)
    return code


def production_signature_binding() -> dict[str, Any]:
    """Bind five-bit formula to production 10-bit _DELTA on block A."""
    checked = 0
    failures: list[dict[str, Any]] = []
    for r0, r1, s0, s1 in itertools.product(range(4), repeat=4):
        old10 = int(r6i._DELTA[option_code((r0, r1, 0, 0, s0, s1))])
        old5 = syn5(r0, r1, s0, s1)
        for action in ACTIONS:
            nr0, nr1 = apply_action(r0, r1, action)
            if deleted_count(r0, r1, nr0, nr1) == 0:
                continue
            new10 = int(r6i._DELTA[option_code((nr0, nr1, 0, 0, s0, s1))])
            d10 = old10 ^ new10
            d5 = old5 ^ syn5(nr0, nr1, s0, s1)
            reconstructed = (
                (((d10 >> 0) & 1) << 4)
                | (((d10 >> 6) & 1) << 3)
                | (((d10 >> 7) & 1) << 2)
                | (((d10 >> 8) & 1) << 1)
                | ((d10 >> 9) & 1)
            )
            duplicate_ok = (
                ((d10 >> 2) & 1) == ((d10 >> 6) & 1)
                and ((d10 >> 3) & 1) == ((d10 >> 7) & 1)
                and ((d10 >> 4) & 1) == ((d10 >> 8) & 1)
                and ((d10 >> 5) & 1) == ((d10 >> 9) & 1)
                and ((d10 >> 1) & 1) == 0
            )
            checked += 1
            if reconstructed != d5 or not duplicate_ok:
                failures.append(
                    {
                        "r": [r0, r1],
                        "s": [s0, s1],
                        "action": action,
                        "delta10": d10,
                        "formula_delta5": d5,
                        "reconstructed_delta5": reconstructed,
                        "duplicate_ok": duplicate_ok,
                    }
                )
    return {
        "checked": checked,
        "failures": failures[:20],
        "failure_count": len(failures),
        "all_exact": not failures,
    }


def action_resource_table() -> dict[str, Any]:
    stats: dict[tuple[str, int], dict[str, Any]] = {}
    rows = 0
    for r0, r1, s0, s1, p0, p1, p2, central in itertools.product(
        range(4), range(4), range(4), range(4),
        range(4), range(4), range(4), range(3)
    ):
        old_s = syn5(r0, r1, s0, s1)
        old_c = local_cost(r0, r1, p0, p1, p2, central)
        for action in ACTIONS:
            nr0, nr1 = apply_action(r0, r1, action)
            dc = deleted_count(r0, r1, nr0, nr1)
            if dc == 0:
                continue
            sig = old_s ^ syn5(nr0, nr1, s0, s1)
            delta = local_cost(nr0, nr1, p0, p1, p2, central) - old_c
            key = (action, sig)
            rec = stats.setdefault(
                key,
                {
                    "action": action,
                    "signature": sig,
                    "count": 0,
                    "min_delta": 10**9,
                    "max_delta": -(10**9),
                    "max_witness": None,
                },
            )
            rec["count"] += 1
            rec["min_delta"] = min(rec["min_delta"], delta)
            if delta > rec["max_delta"]:
                rec["max_delta"] = delta
                rec["max_witness"] = {
                    "r": [r0, r1],
                    "s": [s0, s1],
                    "p": [p0, p1, p2],
                    "central": central,
                    "delta": delta,
                    "deleted_letters": dc,
                }
            rows += 1
    ordered = [stats[k] for k in sorted(stats)]
    return {
        "enumerated_action_rows": rows,
        "action_signature_classes": len(ordered),
        "rows": ordered,
    }


def pair_safety(resource: dict[str, Any]) -> dict[str, Any]:
    by = {(r["action"], r["signature"]): r for r in resource["rows"]}
    pairs: list[dict[str, Any]] = []
    safe_keys: set[tuple[str, str, int]] = set()
    unsafe: list[dict[str, Any]] = []
    for (a, sig), ra in sorted(by.items()):
        for (b, sig2), rb in sorted(by.items()):
            if sig != sig2:
                continue
            worst = int(ra["max_delta"]) + int(rb["max_delta"])
            row = {
                "action_a": a,
                "action_b": b,
                "signature": sig,
                "worst_total_delta": worst,
                "max_a": int(ra["max_delta"]),
                "max_b": int(rb["max_delta"]),
            }
            pairs.append(row)
            if worst <= 0:
                safe_keys.add((a, b, sig))
            else:
                row["witness_a"] = ra["max_witness"]
                row["witness_b"] = rb["max_witness"]
                unsafe.append(row)
    return {
        "syndrome_cancelling_pair_classes": len(pairs),
        "globally_safe_pair_classes": len(safe_keys),
        "unsafe_pair_classes": len(unsafe),
        "unsafe_verbatim": unsafe[:20],
        "safe_keys": [list(k) for k in sorted(safe_keys)],
    }


def has_zero_sum_subset(values: list[int]) -> bool:
    n = len(values)
    for mask in range(1, 1 << n):
        x = 0
        for i in range(n):
            if (mask >> i) & 1:
                x ^= values[i]
        if x == 0:
            return True
    return False


def accepted_total(s: int) -> bool:
    alpha = (s >> 4) & 1
    l0 = 2 * ((s >> 3) & 1) + ((s >> 2) & 1)
    l1 = 2 * ((s >> 1) & 1) + (s & 1)
    return alpha == 1 and l0 in (1, 2, 3) and l1 in (1, 2, 3) and l0 != l1


def structural_record(r0: int, r1: int, s0: int, s1: int) -> dict[str, Any]:
    syn = syn5(r0, r1, s0, s1)
    coincidence = r0 == r1 and r0 != 0
    alpha = sy(r0, r1)
    n0 = None
    n1 = None
    c = None
    if r0 != 0 and not coincidence:
        n0 = (alpha << 2) | (sy(s0, r0) << 1) | sy(s1, r0)
    if r1 != 0 and not coincidence:
        n1 = (alpha << 2) | (sy(s0, r1) << 1) | sy(s1, r1)
    if coincidence:
        c = (sy(s0, r0) << 1) | sy(s1, r0)
    actions = []
    for action in ACTIONS:
        nr0, nr1 = apply_action(r0, r1, action)
        if deleted_count(r0, r1, nr0, nr1) == 0:
            continue
        actions.append(
            {
                "action": action,
                "signature": syn ^ syn5(nr0, nr1, s0, s1),
                "del0": int(r0 != 0 and nr0 == 0),
                "del1": int(r1 != 0 and nr1 == 0),
            }
        )
    return {
        "syndrome": syn,
        "support0": int(r0 != 0),
        "support1": int(r1 != 0),
        "coincidence": coincidence,
        "n0": n0,
        "n1": n1,
        "c": c,
        "actions": actions,
    }


def build_types() -> list[dict[str, Any]]:
    unique: dict[str, dict[str, Any]] = {}
    for vals in itertools.product(range(4), repeat=4):
        rec = structural_record(*vals)
        key = canonical(rec)
        if key not in unique:
            unique[key] = {"record": rec, "representative": list(vals)}
    return [unique[k] for k in sorted(unique)]


def old_irreducible(pattern: tuple[int, ...], types: list[dict[str, Any]]) -> bool:
    n0: list[int] = []
    n1: list[int] = []
    c: list[int] = []
    for i in pattern:
        r = types[i]["record"]
        if r["n0"] is not None:
            n0.append(int(r["n0"]))
        if r["n1"] is not None:
            n1.append(int(r["n1"]))
        if r["c"] is not None:
            c.append(int(r["c"]))
    return (
        not has_zero_sum_subset(n0)
        and not has_zero_sum_subset(n1)
        and not has_zero_sum_subset(c)
    )


def find_safe_move(pattern: tuple[int, ...], types: list[dict[str, Any]], safe: set[tuple[str, str, int]]) -> dict[str, Any] | None:
    rs = [types[i]["record"] for i in pattern]
    s0 = sum(r["support0"] for r in rs)
    s1 = sum(r["support1"] for r in rs)
    before = (max(s0, s1), s0 + s1)
    for i, j in itertools.combinations(range(5), 2):
        for a in rs[i]["actions"]:
            for b in rs[j]["actions"]:
                if a["signature"] != b["signature"]:
                    continue
                key = (a["action"], b["action"], int(a["signature"]))
                rkey = (b["action"], a["action"], int(a["signature"]))
                if key not in safe and rkey not in safe:
                    continue
                ns0 = s0 - int(a["del0"]) - int(b["del0"])
                ns1 = s1 - int(a["del1"]) - int(b["del1"])
                after = (max(ns0, ns1), ns0 + ns1)
                if after < before:
                    return {
                        "columns": [i, j],
                        "actions": [a["action"], b["action"]],
                        "signature": int(a["signature"]),
                        "before_supports": [s0, s1],
                        "after_supports": [ns0, ns1],
                    }
    return None


def obstruction_census(pair_info: dict[str, Any]) -> dict[str, Any]:
    safe = {tuple(x) for x in pair_info["safe_keys"]}
    types = build_types()
    accepted = irreducible = support5 = covered = 0
    first_obstruction = None
    first_covered = None
    for pattern in itertools.combinations_with_replacement(range(len(types)), 5):
        total = 0
        for i in pattern:
            total ^= int(types[i]["record"]["syndrome"])
        if not accepted_total(total):
            continue
        accepted += 1
        if not old_irreducible(pattern, types):
            continue
        irreducible += 1
        sup0 = sum(types[i]["record"]["support0"] for i in pattern)
        sup1 = sum(types[i]["record"]["support1"] for i in pattern)
        if max(sup0, sup1) != 5:
            continue
        support5 += 1
        move = find_safe_move(pattern, types, safe)
        if move is None:
            if first_obstruction is None:
                first_obstruction = {
                    "pattern_indices": list(pattern),
                    "supports": [sup0, sup1],
                    "total_syndrome": total,
                    "columns": [
                        {
                            "type_index": i,
                            "representative": types[i]["representative"],
                            "record": types[i]["record"],
                        }
                        for i in pattern
                    ],
                }
        else:
            covered += 1
            if first_covered is None:
                first_covered = {"pattern_indices": list(pattern), "move": move}
    return {
        "structural_type_count": len(types),
        "accepted_five_column_patterns": accepted,
        "qg1_irreducible_patterns": irreducible,
        "support5_irreducible_patterns": support5,
        "covered_by_globally_safe_e2": covered,
        "uncovered_support5_patterns": support5 - covered,
        "first_obstruction": first_obstruction,
        "first_covered": first_covered,
    }


def run() -> dict[str, Any]:
    binding = production_signature_binding()
    resource = action_resource_table()
    pairs = pair_safety(resource)
    census = obstruction_census(pairs)

    if not binding["all_exact"]:
        terminal = "QG13V2_SEMANTIC_QUOTIENT_INCOMPLETE"
    elif pairs["globally_safe_pair_classes"] == 0:
        terminal = "QG13V2_RESOURCE_COUNTEREXAMPLE"
    elif census["support5_irreducible_patterns"] > 0 and census["uncovered_support5_patterns"] == 0:
        terminal = "QG13V2_SUPPORT4_CANDIDATE"
    elif census["uncovered_support5_patterns"] > 0:
        terminal = "QG13V2_MINIMAL_COMBINED_EDIT_OBSTRUCTION"
    else:
        terminal = "QG13V2_CANNOT_CHECK"

    result: dict[str, Any] = {
        "schema": "ORION.QG.QG13V2.CombinedEdit.v1",
        "issue": ISSUE,
        "base_revision": BASE,
        "terminal": terminal,
        "edit_grammar": ["A", "B", "AB"],
        "production_signature_binding": binding,
        "action_resource_table": resource,
        "pair_safety": pairs,
        "obstruction_census": census,
        "parent_receipts_opened_during_synthesis": False,
        "chemistry_sources_read": False,
        "protected_subject_read": False,
        "network_access": False,
        "new_theorem_authority": False,
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    result["result_digest"] = digest_payload(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    result = run()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TOKEN + canonical({
        "terminal": result["terminal"],
        "result_digest": result["result_digest"],
        "support5": result["obstruction_census"]["support5_irreducible_patterns"],
        "covered": result["obstruction_census"]["covered_by_globally_safe_e2"],
        "uncovered": result["obstruction_census"]["uncovered_support5_patterns"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
