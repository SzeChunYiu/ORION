#!/usr/bin/env python3
"""Independent checker for ORION14.MINIMAL_PROMOTION_REDUCT.v1.

INDEPENDENCE CONTRACT
---------------------
No ORION-14 module is imported -- not run_method_authority_bench.py, not
orion.transfer.v2.p4_method_authority. The bench corpus is read as DATA and the
reduct is recomputed from the discernibility definition.

SCOPE GATE
----------
The deep-upgrade note (PR #1617) asks for a minimal promotion reduct over the
frozen 400 cases behind ORION-14.X.EXACT.400.PROMOTION_RELATION. That per-case
coordinate table is NOT committed: no 350-450 row JSONL and no 400-length array
exists anywhere under the paper. This checker therefore reports that gate
explicitly and computes the reduct on the corpus that IS committed -- the
10-case method-authority bench. The two must not be confused.

Checks
    A. Ternary encoding is load-bearing -- binarizing prior_art_found collapses
       `null` (could not check) into `false` (checked, found nothing) and
       destroys the reduct entirely.
    B. Exact reduct, core and never-used coordinates on the committed bench.
    C. Scope gate -- assert the 400-case table is absent rather than assuming it.
    D. Negative controls.

Exit codes
    0 pass    2 fail    3 CANNOT_CHECK
"""
from __future__ import annotations
import itertools, json, sys
from pathlib import Path

PACKET = Path(__file__).resolve().parent.parent
PAPER = PACKET.parents[1]
BENCH = PAPER / "method_authority_extension/METHOD_AUTHORITY_BENCH_V1.json"

ABSENT_OR_UNKNOWN = 2          # third value: CANNOT_CHECK / not recorded


def load():
    d = json.loads(BENCH.read_text())
    cases = d["cases"]
    setk = sorted({k for c in cases for k in c.get("settings", {})})
    coords = sorted({x for c in cases for x in c.get("required_coordinates", [])})
    feat = setk + ["req:" + c for c in coords]
    return cases, setk, coords, feat


def encode(cases, setk, coords, ternary: bool):
    def val(s, k):
        if k not in s:
            return ABSENT_OR_UNKNOWN if ternary else 0
        v = s[k]
        if v is None:
            return ABSENT_OR_UNKNOWN if ternary else 0
        return int(bool(v))
    rows = []
    for c in cases:
        s = c.get("settings", {})
        req = set(c.get("required_coordinates", []))
        vec = tuple(val(s, k) for k in setk) + tuple(int(x in req) for x in coords)
        rows.append((vec, bool(c["expected_promotable"]), c["case_id"]))
    return rows


def sufficient(rows, sub):
    seen = {}
    for vec, y, _ in rows:
        key = tuple(vec[j] for j in sub)
        if key in seen and seen[key] != y:
            return False
        seen[key] = y
    return True


def reducts(rows, n_feat):
    suff = [s for r in range(n_feat + 1)
            for s in itertools.combinations(range(n_feat), r)
            if sufficient(rows, list(s))]
    if not suff:
        return None, [], []
    k = min(len(s) for s in suff)
    minimal = [s for s in suff if not any(set(t) < set(s) for t in suff)]
    core = sorted(set.intersection(*(set(s) for s in minimal)))
    return k, minimal, core


def collision(rows):
    seen = {}
    for vec, y, cid in rows:
        if vec in seen and seen[vec][0] != y:
            return [seen[vec][1], cid]
        seen.setdefault(vec, (y, cid))
    return None


def main() -> int:
    try:
        if not BENCH.is_file():
            raise FileNotFoundError(str(BENCH))
        cases, setk, coords, feat = load()

        # C. scope gate -- is the 400-case table present anywhere?
        big = []
        for p in PAPER.rglob("*.jsonl"):
            n = sum(1 for line in p.read_text().splitlines() if line.strip())
            if 350 <= n <= 450:
                big.append(str(p.relative_to(PAPER)))
        gate = {
            "requested_by_1617": "minimal promotion reduct over the frozen 400 cases",
            "four_hundred_case_table_committed": bool(big),
            "candidate_files_found": big,
            "consequence": ("Upgrade A cannot be executed as specified; the reduct "
                            "below is computed on the committed 10-case bench and is "
                            "NOT the 400-case study"),
        }

        # A. ternary vs binary
        rows_t = encode(cases, setk, coords, ternary=True)
        rows_b = encode(cases, setk, coords, ternary=False)
        k_t, min_t, core_t = reducts(rows_t, len(feat))
        k_b, _, _ = reducts(rows_b, len(feat))
        coll_b = collision(rows_b)
        ternary_matters = (k_t is not None and k_b is None and coll_b is not None)

        # D. negative controls
        controls = {
            "binarising_cannot_check_destroys_the_reduct": {
                "pass": ternary_matters,
                "binary_collision": coll_b},
            "full_feature_set_is_sufficient_under_ternary": {
                "pass": sufficient(rows_t, list(range(len(feat))))},
            "empty_set_is_not_sufficient": {
                "pass": not sufficient(rows_t, [])},
        }
        controls_ok = all(v["pass"] for v in controls.values())
    except Exception as exc:                                    # noqa: BLE001
        print(json.dumps({"status": "CANNOT_CHECK",
                          "error": f"{type(exc).__name__}: {exc}"}, indent=2))
        return 3

    never = [feat[j] for j in range(len(feat)) if all(j not in s for s in min_t)]
    report = {
        "schema": "ORION.ORION14.PromotionReduct.CheckerReport.v1",
        "successor_id": "ORION14.MINIMAL_PROMOTION_REDUCT.v1",
        "independence": "no ORION-14 module imported; bench read as data; reduct recomputed",
        "scope_gate_400_case_table": gate,
        "corpus_actually_analysed": {
            "path": str(BENCH.relative_to(PAPER.parent.parent)),
            "cases": len(cases),
            "promotable": sum(1 for c in cases if c["expected_promotable"]),
            "features": len(feat),
        },
        "check_A_ternary_encoding_is_load_bearing": {
            "k_star_ternary": k_t,
            "k_star_binary": k_b,
            "binary_collision_pair": coll_b,
            "reading": ("prior_art_found: null means the novelty search could not run; "
                        "false means it ran and found nothing. Binarising merges them "
                        "and no sufficient feature set survives at all."),
        },
        "check_B_reduct": {
            "k_star": k_t,
            "reducts": [[feat[j] for j in s] for s in min_t],
            "core_in_every_reduct": [feat[j] for j in core_t],
            "never_in_any_reduct": never,
        },
        "check_D_negative_controls": controls,
        "status": "PASS" if controls_ok else "FAIL",
    }
    (PACKET / "RESULT.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("status", "scope_gate_400_case_table", "corpus_actually_analysed",
                       "check_A_ternary_encoding_is_load_bearing", "check_B_reduct",
                       "check_D_negative_controls")}, indent=2))
    return 0 if controls_ok else 2


if __name__ == "__main__":
    sys.exit(main())
