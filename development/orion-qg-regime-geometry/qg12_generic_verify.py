#!/usr/bin/env python3
"""Independent QG-12 verifier: rebuild SixLCU evaluator without importing qg4."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
PROTOCOL_PATH = REPO_ROOT / "development" / "orion-qg-regime-geometry" / "QG12_SIXLCU_P0_THEOREM_PROTOCOL_V1.md"
NOVELTY_PATH = REPO_ROOT / "development" / "orion-qg-regime-geometry" / "QG12_NOVELTY_THREAT_FREEZE_2026-08-21.md"
DEFAULT_INPUT = REPO_ROOT / "artifacts" / "orion-qg-qg12-sixlcu-p0-theorem.json"
DEFAULT_OUTPUT = REPO_ROOT / "artifacts" / "orion-qg-qg12-generic-verification.json"
TOKEN_PREFIX = "ORIONQG_QG12_GENERIC_VERIFY="
DS = {1: 0, 2: 0, 3: 1, 4: 2, 5: 4, 6: 6}


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_digest(raw: dict[str, Any]) -> bool:
    observed = raw.get("result_digest")
    unsigned = dict(raw)
    unsigned.pop("result_digest", None)
    return observed == hashlib.sha256(canonical(unsigned).encode()).hexdigest()


def bbits(m: int) -> int:
    return (m - 1).bit_length()


def partitions6():
    rows = []
    def rec(i: int, rgs: list[int], mx: int) -> None:
        if i == 6:
            blocks = [[] for _ in range(mx + 1)]
            for idx, label in enumerate(rgs):
                blocks[label].append(idx)
            rows.append(tuple(tuple(block) for block in blocks))
            return
        for label in range(mx + 2):
            rec(i + 1, [*rgs, label], max(mx, label))
    rec(1, [0], 0)
    return rows


PARTS = partitions6()
if len(PARTS) != 203:
    raise AssertionError(len(PARTS))


def term_wt(code: int, n: int) -> int:
    return sum(1 for q in range(n) if (code >> (2*q)) & 3)


def subset_tables(codes, n: int):
    weights = [term_wt(c, n) for c in codes]
    sw = [0] * 64
    for mask in range(1, 64):
        low = mask & -mask
        sw[mask] = sw[mask ^ low] + weights[low.bit_length()-1]
    wf = [0] * 64
    for q in range(n):
        letters = [(code >> (2*q)) & 3 for code in codes]
        for mask in range(1, 64):
            idxs = [i for i in range(6) if (mask >> i) & 1]
            v = letters[idxs[0]]
            if v and all(letters[i] == v for i in idxs):
                wf[mask] += 1
    return weights, sw, wf


def partition_cost(part, sw, wf) -> int:
    k = len(part)
    flag = 1 if k >= 2 else 0
    sizes = [len(block) for block in part]
    bs = [bbits(m) for m in sizes]
    prep = (0 if k == 1 else 2*k - 3) + sum(
        (m-1)*(1+flag) + DS[m] for m in sizes if m >= 2
    )
    width = (k if k >= 2 else 0) + max(bs)
    select = 0
    for block, m, b in zip(part, sizes, bs, strict=True):
        mask = sum(1 << i for i in block)
        B = flag + b + 1
        select += (flag + 1) * wf[mask] + B * (sw[mask] - m*wf[mask])
    return select + prep + width


def independent_eval(codes, n: int) -> tuple[bool, bool, int, int]:
    weights, sw, wf = subset_tables(codes, n)
    W = sum(weights)
    c_u = 2*W + 15
    c_f = min(partition_cost(part, sw, wf) for part in PARTS)

    pair_masks = [sum(1 << x for x in pair) for pair in itertools.combinations(range(6), 2)]
    g2 = {mask: 4*wf[mask] - sw[mask] for mask in pair_masks}
    maxg2 = max(g2.values())
    best2 = max(
        g2[a] + g2[b] + 1
        for a, b in itertools.combinations(pair_masks, 2)
        if not (a & b)
    )
    best3 = max(
        g2[a] + g2[b] + g2[c] + 2
        for a, b, c in itertools.combinations(pair_masks, 3)
        if not (a&b or a&c or b&c) and (a|b|c) == 63
    )
    p0 = maxg2 <= 0 and best2 <= 0 and best3 <= 0
    label = c_f == c_u
    return p0, label, c_f, c_u


def derive_shape_table() -> dict[str, Any]:
    data: dict[str, set[tuple]] = {}
    for part in PARTS:
        sizes = tuple(sorted((len(b) for b in part), reverse=True))
        name = "+".join(map(str, sizes))
        k = len(part)
        flag = 1 if k >= 2 else 0
        bs = [bbits(m) for m in sizes]
        prep = (0 if k == 1 else 2*k-3) + sum((m-1)*(1+flag)+DS[m] for m in sizes if m>=2)
        width = (k if k>=2 else 0) + max(bs)
        if k == 1:
            row = ("single", prep+width)
        else:
            coeffs = tuple(sorted((m, (flag+bbits(m)+1)*m-(flag+1), -bbits(m)) for m in sizes))
            row = (15-(prep+width), coeffs)
        data.setdefault(name, set()).add(row)
    return {name: sorted(rows, key=repr) for name, rows in sorted(data.items())}


def complete_regression() -> dict[str, Any]:
    mismatches = []
    n1 = n2 = 0
    digest = hashlib.sha256()
    for codes in itertools.product((1,2,3), repeat=6):
        p0, label, cf, cu = independent_eval(codes, 1)
        n1 += 1
        digest.update(canonical([1,list(codes),p0,label,cf,cu]).encode())
        if p0 != label and len(mismatches) < 50:
            mismatches.append({"n":1,"codes":list(codes),"p0":p0,"label":label,"C_F":cf,"C_U":cu})
    for codes in itertools.combinations_with_replacement(range(1,16), 6):
        p0, label, cf, cu = independent_eval(codes, 2)
        n2 += 1
        digest.update(canonical([2,list(codes),p0,label,cf,cu]).encode())
        if p0 != label and len(mismatches) < 50:
            mismatches.append({"n":2,"codes":list(codes),"p0":p0,"label":label,"C_F":cf,"C_U":cu})
    return {
        "n1_count": n1, "n2_count": n2,
        "mismatches": mismatches, "zero_mismatches": not mismatches,
        "result_sha256": digest.hexdigest(),
    }


def run(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text())
    shapes = derive_shape_table()
    regression = complete_regression()
    analyzer_reg = raw.get("blind_complete_regression", {})
    checks = {
        "schema": raw.get("schema") == "ORION.QG.QG12.SixLCUP0Theorem.v1",
        "base": raw.get("base_revision") == "318d1cbbec451170448bb8e126c7ab50801930ce",
        "protocol_hash": raw.get("protocol_sha256") == sha256_file(PROTOCOL_PATH),
        "novelty_hash": raw.get("novelty_threat_sha256") == sha256_file(NOVELTY_PATH),
        "result_digest": verify_digest(raw),
        "partition_count_203": len(PARTS) == 203,
        "shape_count_11": len(shapes) == 11,
        "shape_table_matches_analyzer": set(shapes) == set(raw.get("production_gain_decomposition", {}).get("shapes", {})),
        "n1_complete": regression["n1_count"] == analyzer_reg.get("n1_count") == 729,
        "n2_complete": regression["n2_count"] == analyzer_reg.get("n2_count") == 38760,
        "independent_zero_mismatches": regression["zero_mismatches"],
        "analyzer_zero_mismatches": analyzer_reg.get("zero_mismatches") is True,
        "theorem_string": raw.get("theorem") == "For every admitted six-term Pauli batch at every n in frozen SixLCU: C_F == C_U iff P0",
        "all_analyzer_gates": all(raw.get("gates", {}).values()),
        "no_novelty_authority": raw.get("novelty_authority") is False,
        "no_physical_advantage": raw.get("physical_quantum_advantage_claim") is False,
    }
    decision = "ACCEPT" if all(checks.values()) else "REJECT"
    return {
        "schema": "ORION.QG.QG12.GenericVerification.v1",
        "decision": decision,
        "checks": checks,
        "independent_shape_table": shapes,
        "independent_complete_regression": regression,
        "source_result_digest": raw.get("result_digest"),
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }


def main(argv=None) -> int:
    p=argparse.ArgumentParser(); p.add_argument("--input",default=str(DEFAULT_INPUT)); p.add_argument("--output",default=str(DEFAULT_OUTPUT)); a=p.parse_args(argv)
    result=run(Path(a.input)); out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(TOKEN_PREFIX+canonical({"decision":result["decision"],"path":str(out)})); return 0


if __name__ == "__main__": raise SystemExit(main())
