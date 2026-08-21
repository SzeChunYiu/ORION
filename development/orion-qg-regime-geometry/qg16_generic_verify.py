#!/usr/bin/env python3
"""Independent generic-ORION verification for QG-16.

No production R6I/P10 module is imported. Phase-free Pauli algebra, local
resource vectors, global support<=2 core counts, rational controls and facets
are reconstructed independently.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "artifacts/orion-qg-qg16-r6i-support1-phase.json"
PROTOCOL = ROOT / "development/orion-qg-regime-geometry/QG16_R6I_SUPPORT1_PHASE_PROTOCOL_V1.md"
V6_RECEIPT = ROOT / "development/orion-qg-regime-geometry/QG9_V6_PROTECTED_RUN_RECEIPT_2026-08-21.json"
OUT = ROOT / "artifacts/orion-qg-qg16-generic-verification.json"
TOKEN = "ORIONQG_QG16_GENERIC="

VEC = {0: (0, 0), 1: (1, 0), 2: (1, 1), 3: (0, 1)}
INV = {v: k for k, v in VEC.items()}
BASES = tuple((a, b) for a in (1, 2, 3) for b in (1, 2, 3) if a != b)


def canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def mul(a: int, b: int) -> int:
    av, bv = VEC[a], VEC[b]
    return INV[(av[0] ^ bv[0], av[1] ^ bv[1])]


def symp(a: int, b: int) -> int:
    av, bv = VEC[a], VEC[b]
    return (av[0] * bv[1] + av[1] * bv[0]) & 1


def wt(a: int) -> int:
    return int(a != 0)


def resource_vectors():
    rows = []
    witnesses = {}
    for a, b in itertools.product(range(4), repeat=2):
        if a == b == 0 or symp(a, b):
            continue
        r = (a, b, mul(a, b))
        active = tuple(k for k in range(3) if r[k])
        if len(active) != 2:
            raise AssertionError((a, b, r))
        for p in itertools.product(range(4), repeat=3):
            old = sum(wt(mul(p[k], r[k])) for k in range(3))
            new = sum(wt(p[k]) for k in range(3))
            dr = new - old
            for central in range(3):
                v = (int(central in active), len(active) - int(central in active), dr)
                rows.append(v)
                witnesses.setdefault(v, {"a": a, "b": b, "targets": list(p), "central": central})
    vectors = sorted(set(rows))
    worst = []
    for v in vectors:
        has_worse = any(
            w != v
            and w[0] <= v[0]
            and w[1] <= v[1]
            and w[2] >= v[2]
            and (w[0] < v[0] or w[1] < v[1] or w[2] > v[2])
            for w in vectors
        )
        if not has_worse:
            worst.append(v)
    return len(rows), vectors, sorted(worst), witnesses


def alignment():
    n = 0
    mx = -999
    frame_ok = True
    for old in BASES:
        ro = (old[0], old[1], mul(*old))
        for new in BASES:
            rn = (new[0], new[1], mul(*new))
            for p in itertools.product(range(4), repeat=3):
                for central in range(3):
                    m = [4, 4, 4]
                    m[central] = 2
                    frame_ok &= sum(m[k] * wt(ro[k]) for k in range(3)) == 10
                    frame_ok &= sum(m[k] * wt(rn[k]) for k in range(3)) == 10
                    do = sum(wt(mul(p[k], ro[k])) for k in range(3))
                    dn = sum(wt(mul(p[k], rn[k])) for k in range(3))
                    mx = max(mx, dn - do)
                    n += 1
    return n, mx, frame_ok


def local_string_weight(s):
    return sum(int(x != 0) for x in s)


def string_symp(a, b):
    return sum(symp(x, y) for x, y in zip(a, b)) & 1


def support2_core_counts():
    expected = {1: 6, 2: 120, 3: 666, 4: 1968}
    rows = {}
    all_one = True
    for n in range(1, 5):
        strings = [s for s in itertools.product(range(4), repeat=n) if any(s) and local_string_weight(s) <= 2]
        pairs = [(a, b) for a in strings for b in strings if string_symp(a, b) == 1]
        hist = {}
        for a, b in pairs:
            k = sum(int(symp(a[q], b[q]) == 1) for q in range(n))
            hist[k] = hist.get(k, 0) + 1
            all_one &= k == 1
        rows[n] = {"count": len(pairs), "expected": expected[n], "hist": hist}
    return rows, all_one


def facets(worst):
    out = []
    for rc, rn, dr in worst:
        out.append({"t_c": rc, "t_nc": rn, "t_tag": 0, "t_r": -(dr + 3)})
        out.append({"t_c": rc, "t_nc": rn, "t_tag": -2, "t_r": -dr})
    return sorted(out, key=lambda d: (d["t_c"], d["t_nc"], d["t_tag"], d["t_r"]))


def margin(c, t):
    return sum(Fraction(c[k]) * t[k] for k in ("t_c", "t_nc", "t_tag", "t_r"))


def controls(fs):
    pts = {
        "O0": {"t_nc": Fraction(4), "t_c": Fraction(2), "t_tag": Fraction(2), "t_r": Fraction(1)},
        "O_in": {"t_nc": Fraction(5), "t_c": Fraction(3), "t_tag": Fraction(2), "t_r": Fraction(1)},
        "O_tag_out": {"t_nc": Fraction(4), "t_c": Fraction(2), "t_tag": Fraction(5, 2), "t_r": Fraction(1)},
        "O_restore_out": {"t_nc": Fraction(4), "t_c": Fraction(2), "t_tag": Fraction(2), "t_r": Fraction(5, 4)},
        "O_nc_out": {"t_nc": Fraction(3, 2), "t_c": Fraction(3, 2), "t_tag": Fraction(1), "t_r": Fraction(1)},
    }
    return {
        name: {
            "inside": all(margin(f, p) >= 0 for f in fs),
            "strict": all(margin(f, p) > 0 for f in fs),
            "boundary": any(margin(f, p) == 0 for f in fs) and all(margin(f, p) >= 0 for f in fs),
            "margins": [(margin(f, p).numerator, margin(f, p).denominator) for f in fs],
        }
        for name, p in pts.items()
    }


def main() -> int:
    a = json.loads(RESULT.read_text())
    u = dict(a)
    observed = u.pop("result_digest", None)
    digest = observed == hashlib.sha256(canonical(u).encode()).hexdigest()
    nr, allv, worst, witnesses = resource_vectors()
    na, ma, fa = alignment()
    core_rows, core_one = support2_core_counts()
    fs = facets(worst)
    cs = controls(fs)
    prod_fs = a.get("full_cone_coefficients_ge_zero", [])
    checks = {
        "schema": a.get("schema") == "ORION.QG.QG16.R6ISupport1Phase.v1",
        "result_digest": digest,
        "protocol_hash": a.get("protocol_sha256") == hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "parent_v6_protected": json.loads(V6_RECEIPT.read_text()).get("terminal") == "QG9_RANK2_ALL_N_SUPPORT1_SUFFICIENCY_MACHINE_CHECKED",
        "resource_domain_1728": nr == 1728 and a["commuting_deletion_resources"]["domain_size"] == nr,
        "resource_vectors_exact": worst == [(0, 2, 2), (1, 1, 2)] and a["commuting_deletion_resources"]["worst_vectors"] == [list(x) for x in worst],
        "facet_set_exact": prod_fs == fs,
        "alignment_6912_max3": na == 6912 and ma == 3 and fa and a["core_alignment_resources"]["max_delta_restore"] == 3,
        "support2_counts": all(core_rows[n]["count"] == core_rows[n]["expected"] for n in core_rows) and a["support2_core_audit"]["all_pair_counts_match"] is True,
        "one_anti_core": core_one and a["support2_core_audit"]["every_pair_exactly_one_anti_core"] is True,
        "O0_inside_boundary": cs["O0"]["inside"] and cs["O0"]["boundary"] and a["controls"]["O0"]["inside"] is True and a["controls"]["O0"]["on_boundary"] is True,
        "Oin_inside": cs["O_in"]["strict"] and a["controls"]["O_in"]["strict_interior"] is True,
        "outside_controls": all(not cs[x]["inside"] and a["controls"][x]["inside"] is False for x in ("O_tag_out", "O_restore_out", "O_nc_out")),
        "outside_semantics": a.get("outside_cone_semantics") == "THIS_PROOF_CERTIFICATE_DOES_NOT_APPLY__NOT_SUPPORT2_REQUIRED",
        "sharpness_open": a.get("global_phase_boundary_sharpness") == "OPEN",
        "support_inside_one": a.get("support_bound_inside_cone") == 1 and a.get("intrinsic_support_number_inside_cone") == 1,
        "authority_ceiling": a.get("novelty_authority") is False and a.get("physical_quantum_advantage_claim") is False,
    }
    decision = "ACCEPT_SUPPORT1_PHASE" if a.get("terminal") == "QG16_R6I_OBJECTIVE_INDEXED_SUPPORT1_CONE_ALL_N_MACHINE_CHECKED" and all(checks.values()) else "REJECT"
    out = {
        "schema": "ORION.QG.QG16.GenericVerification.v1",
        "issue": "SzeChunYiu/ORION#811",
        "decision": decision,
        "checks": checks,
        "all_checks": all(checks.values()),
        "independent_worst_vectors": [list(x) for x in worst],
        "independent_facets": fs,
        "independent_controls": cs,
        "terminal": a.get("terminal"),
        "novelty_authority": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canonical(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
