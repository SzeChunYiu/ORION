#!/usr/bin/env python3
"""Independent verifier for QG-13 V2 combined-edit mining."""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
ANALYZER = REPO_ROOT / "artifacts" / "orion-qg-qg13v2-combined-edit.json"
OUTPUT = REPO_ROOT / "artifacts" / "orion-qg-qg13v2-generic-verification.json"
TOKEN = "ORIONQG_QG13V2_GENERIC="
ACTIONS = ("A", "B", "AB")


def canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def wt(a: int) -> int:
    return 0 if a == 0 else 1


def mul(a: int, b: int) -> int:
    return a ^ b


def sy(a: int, b: int) -> int:
    return int(a != 0 and b != 0 and a != b)


def syn5(r0: int, r1: int, s0: int, s1: int) -> int:
    return (
        (sy(r0, r1) << 4)
        | (sy(s0, r0) << 3)
        | (sy(s1, r0) << 2)
        | (sy(s0, r1) << 1)
        | sy(s1, r1)
    )


def apply_action(r0: int, r1: int, action: str) -> tuple[int, int]:
    return (0, r1) if action == "A" else ((r0, 0) if action == "B" else (0, 0))


def local_cost(r0: int, r1: int, p0: int, p1: int, p2: int, central: int) -> int:
    rs = (r0, r1, mul(r0, r1))
    m = [4, 4, 4]
    m[central] = 2
    ps = (p0, p1, p2)
    return sum(m[k] * wt(rs[k]) + wt(mul(ps[k], rs[k])) for k in range(3))


def action_table():
    stats = {}
    rows = 0
    for r0, r1, s0, s1, p0, p1, p2, central in itertools.product(
        range(4), range(4), range(4), range(4), range(4), range(4), range(4), range(3)
    ):
        old_s = syn5(r0, r1, s0, s1)
        old_c = local_cost(r0, r1, p0, p1, p2, central)
        for action in ACTIONS:
            nr0, nr1 = apply_action(r0, r1, action)
            if nr0 == r0 and nr1 == r1:
                continue
            sig = old_s ^ syn5(nr0, nr1, s0, s1)
            delta = local_cost(nr0, nr1, p0, p1, p2, central) - old_c
            key = (action, sig)
            rec = stats.setdefault(key, {"count": 0, "min": 10**9, "max": -(10**9)})
            rec["count"] += 1
            rec["min"] = min(rec["min"], delta)
            rec["max"] = max(rec["max"], delta)
            rows += 1
    return stats, rows


def pair_table(stats):
    safe = set()
    total = unsafe = 0
    for (a, s), ra in sorted(stats.items()):
        for (b, t), rb in sorted(stats.items()):
            if s != t:
                continue
            total += 1
            if ra["max"] + rb["max"] <= 0:
                safe.add((a, b, s))
            else:
                unsafe += 1
    return safe, total, unsafe


def zs(vals):
    for mask in range(1, 1 << len(vals)):
        x = 0
        for i, v in enumerate(vals):
            if (mask >> i) & 1:
                x ^= v
        if x == 0:
            return True
    return False


def accepting(s):
    a = (s >> 4) & 1
    l0 = 2 * ((s >> 3) & 1) + ((s >> 2) & 1)
    l1 = 2 * ((s >> 1) & 1) + (s & 1)
    return a == 1 and l0 in (1, 2, 3) and l1 in (1, 2, 3) and l0 != l1


def structural(r0, r1, s0, s1):
    syn = syn5(r0, r1, s0, s1)
    cflag = r0 == r1 and r0 != 0
    alpha = sy(r0, r1)
    n0 = None if r0 == 0 or cflag else ((alpha << 2) | (sy(s0, r0) << 1) | sy(s1, r0))
    n1 = None if r1 == 0 or cflag else ((alpha << 2) | (sy(s0, r1) << 1) | sy(s1, r1))
    cc = None if not cflag else ((sy(s0, r0) << 1) | sy(s1, r0))
    acts = []
    for action in ACTIONS:
        nr0, nr1 = apply_action(r0, r1, action)
        if nr0 == r0 and nr1 == r1:
            continue
        acts.append({
            "action": action,
            "signature": syn ^ syn5(nr0, nr1, s0, s1),
            "d0": int(r0 != 0 and nr0 == 0),
            "d1": int(r1 != 0 and nr1 == 0),
        })
    return {
        "syn": syn,
        "s0": int(r0 != 0),
        "s1": int(r1 != 0),
        "n0": n0,
        "n1": n1,
        "c": cc,
        "acts": acts,
    }


def types():
    u = {}
    for vals in itertools.product(range(4), repeat=4):
        r = structural(*vals)
        k = canonical(r)
        if k not in u:
            u[k] = {"r": r, "rep": list(vals)}
    return [u[k] for k in sorted(u)]


def irreducible(pat, ts):
    n0, n1, c = [], [], []
    for i in pat:
        r = ts[i]["r"]
        if r["n0"] is not None: n0.append(r["n0"])
        if r["n1"] is not None: n1.append(r["n1"])
        if r["c"] is not None: c.append(r["c"])
    return not zs(n0) and not zs(n1) and not zs(c)


def safe_move(pat, ts, safe):
    rs = [ts[i]["r"] for i in pat]
    s0 = sum(r["s0"] for r in rs); s1 = sum(r["s1"] for r in rs)
    before = (max(s0, s1), s0 + s1)
    for i, j in itertools.combinations(range(5), 2):
        for a in rs[i]["acts"]:
            for b in rs[j]["acts"]:
                if a["signature"] != b["signature"]: continue
                sig = a["signature"]
                if (a["action"], b["action"], sig) not in safe and (b["action"], a["action"], sig) not in safe:
                    continue
                ns0 = s0 - a["d0"] - b["d0"]; ns1 = s1 - a["d1"] - b["d1"]
                if (max(ns0, ns1), ns0 + ns1) < before:
                    return True
    return False


def census(safe):
    ts = types()
    accepted = irr = support5 = covered = 0
    first = None
    for pat in itertools.combinations_with_replacement(range(len(ts)), 5):
        total = 0
        for i in pat: total ^= ts[i]["r"]["syn"]
        if not accepting(total): continue
        accepted += 1
        if not irreducible(pat, ts): continue
        irr += 1
        a = sum(ts[i]["r"]["s0"] for i in pat); b = sum(ts[i]["r"]["s1"] for i in pat)
        if max(a, b) != 5: continue
        support5 += 1
        if safe_move(pat, ts, safe):
            covered += 1
        elif first is None:
            first = {"pattern_indices": list(pat), "supports": [a, b], "representatives": [ts[i]["rep"] for i in pat]}
    return {
        "type_count": len(ts), "accepted": accepted, "irreducible": irr,
        "support5": support5, "covered": covered, "uncovered": support5-covered,
        "first_obstruction": first,
    }


def main():
    a = json.loads(ANALYZER.read_text())
    u = dict(a); observed = u.pop("result_digest")
    digest_ok = observed == hashlib.sha256(canonical(u).encode()).hexdigest()
    stats, action_rows = action_table()
    safe, pair_count, unsafe = pair_table(stats)
    c = census(safe)
    ar = a["action_resource_table"]
    pc = a["pair_safety"]
    ac = a["obstruction_census"]
    checks = {
        "schema": a.get("schema") == "ORION.QG.QG13V2.CombinedEdit.v1",
        "digest": digest_ok,
        "formula_action_rows": action_rows == ar.get("enumerated_action_rows"),
        "action_signature_classes": len(stats) == ar.get("action_signature_classes"),
        "pair_count": pair_count == pc.get("syndrome_cancelling_pair_classes"),
        "safe_pair_count": len(safe) == pc.get("globally_safe_pair_classes"),
        "unsafe_pair_count": unsafe == pc.get("unsafe_pair_classes"),
        "type_count": c["type_count"] == ac.get("structural_type_count"),
        "accepted": c["accepted"] == ac.get("accepted_five_column_patterns"),
        "irreducible": c["irreducible"] == ac.get("qg1_irreducible_patterns"),
        "support5": c["support5"] == ac.get("support5_irreducible_patterns"),
        "covered": c["covered"] == ac.get("covered_by_globally_safe_e2"),
        "uncovered": c["uncovered"] == ac.get("uncovered_support5_patterns"),
        "first_obstruction_pattern": (c["first_obstruction"] or {}).get("pattern_indices") == (ac.get("first_obstruction") or {}).get("pattern_indices"),
        "no_parent_open": a.get("parent_receipts_opened_during_synthesis") is False,
        "no_authority": a.get("new_theorem_authority") is False and a.get("novelty_authority") is False,
        "no_sensitive_access": a.get("chemistry_sources_read") is False and a.get("protected_subject_read") is False and a.get("network_access") is False,
    }
    decision = "ACCEPT" if all(checks.values()) else "REJECT"
    out = {
        "schema": "ORION.QG.QG13V2.GenericVerification.v1",
        "decision": decision,
        "checks": checks,
        "independent": {
            "action_rows": action_rows,
            "action_signature_classes": len(stats),
            "pair_classes": pair_count,
            "safe_pair_classes": len(safe),
            "unsafe_pair_classes": unsafe,
            "census": c,
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canonical({"decision": decision, "checks_all": all(checks.values()), "uncovered": c["uncovered"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
