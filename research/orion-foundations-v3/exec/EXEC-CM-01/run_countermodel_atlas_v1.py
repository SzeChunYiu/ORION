"""EXEC-CM-01 -- countermodel atlas over typed workflow graphs, supports and regime paths.

Tests OSTC-T8, T10 and T13 by total enumeration over the grid declared in
EXECUTION_PROTOCOL.json, which was frozen before this file existed.

The models are deliberately small and total rather than large and sampled. The
estimands are existence (T8) and universal (T10, T13) claims, and a total
enumeration answers those exactly; a sample would only bound them.
"""

from __future__ import annotations

import itertools
import json
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent

# The six SANF witness factors. A witness admits only when all six hold.
FACTORS = ("R", "V", "X", "S", "E", "B")

# The seven contract coordinates T10 requires to match (or be bridged) for two
# certificates to compose.
COORDS = ("object", "content", "responsibility", "scope", "epoch", "authority", "blocker")


# ---------------------------------------------------------------- T8

def admits(w: dict[str, bool]) -> bool:
    """A witness admits exactly when all six factors hold (T7 completeness)."""
    return all(w[f] for f in FACTORS)


def t8_atlas() -> dict:
    """For each factor: does a matched countermodel exist where it alone fails?

    A matched countermodel for factor f is a pair (w, w') with w admitting,
    w' differing from w only in f, and w' not admitting. Existence per factor is
    the estimand; the count is reported but is not the claim.
    """
    out = {}
    all_true = {f: True for f in FACTORS}
    for f in FACTORS:
        found = 0
        minimal = None
        # enumerate every witness; hold all others fixed and drop f
        for bits in itertools.product((False, True), repeat=len(FACTORS)):
            w = dict(zip(FACTORS, bits))
            if not admits(w):
                continue
            wp = dict(w)
            wp[f] = False
            if not admits(wp):
                found += 1
                if minimal is None:
                    minimal = {"admitting": w, "counter": wp, "dropped": f}
        out[f] = {
            "models_examined": 2 ** len(FACTORS),
            "countermodels_found": found,
            "minimal_witness": minimal,
        }
    del all_true
    return out


# ---------------------------------------------------------------- T10

def compose(c1: dict, c2: dict, bridges: frozenset) -> dict | None:
    """Compose two certificates, or return None with a typed reason.

    Composition is defined exactly when every produced/consumed coordinate pair
    matches or is related by a registered bridge. A mismatch must produce a typed
    countermodel -- never a coerced composition.
    """
    for k in COORDS:
        produced, consumed = c1["out"][k], c2["in"][k]
        if produced == consumed:
            continue
        if (k, produced, consumed) in bridges:
            continue
        return None
    return {
        "in": dict(c1["in"]),
        "out": dict(c2["out"]),
        "trace": c1["trace"] + c2["trace"],
        "blockers": sorted(set(c1["blockers"]) | set(c2["blockers"])),
    }


def _cert(i: dict, o: dict, trace: tuple, blockers: tuple = ()) -> dict:
    return {"in": i, "out": o, "trace": list(trace), "blockers": list(blockers)}


def t10_atlas(values: int = 3) -> dict:
    """Associativity, identity, and no-silent-composition over certificate triples."""
    vals = list(range(values))
    # A compact certificate: every coordinate carries a value in/out. To keep the
    # enumeration total we vary two coordinates and hold the rest fixed, then
    # rotate which two vary across the coordinate pairs.
    bridges: frozenset = frozenset()
    triples = assoc_viol = ident_viol = 0
    composable = mismatches = silent = 0
    examples: list[dict] = []

    varying_pairs = list(itertools.combinations(COORDS, 2))
    for va, vb in varying_pairs:
        fixed = {k: 0 for k in COORDS}
        for a_out, b_in, b_out, c_in in itertools.product(vals, repeat=4):
            def mk(io_a, io_b):
                i = dict(fixed); o = dict(fixed)
                i[va], i[vb] = io_a
                o[va], o[vb] = io_b
                return i, o

            i1, o1 = mk((0, 0), (a_out, a_out))
            i2, o2 = mk((b_in, b_in), (b_out, b_out))
            i3, o3 = mk((c_in, c_in), (0, 0))
            c1 = _cert(i1, o1, ("t1",))
            c2 = _cert(i2, o2, ("t2",))
            c3 = _cert(i3, o3, ("t3",))
            triples += 1

            ab = compose(c1, c2, bridges)
            bc = compose(c2, c3, bridges)
            left = compose(ab, c3, bridges) if ab else None
            right = compose(c1, bc, bridges) if bc else None

            # associativity where both sides are defined
            if left is not None and right is not None:
                composable += 1
                if left != right:
                    assoc_viol += 1
                    if len(examples) < 3:
                        examples.append({"kind": "associativity", "left": left, "right": right})
            elif (left is None) != (right is None):
                # one grouping composes and the other does not: also an
                # associativity failure, in the definedness rather than the value
                assoc_viol += 1
                if len(examples) < 3:
                    examples.append({"kind": "definedness", "left": left, "right": right})

            # mismatch must be typed, i.e. compose() returns None rather than a value
            for x, y in ((c1, c2), (c2, c3)):
                agree = all(
                    x["out"][k] == y["in"][k] or (k, x["out"][k], y["in"][k]) in bridges
                    for k in COORDS
                )
                got = compose(x, y, bridges)
                if not agree:
                    mismatches += 1
                    if got is not None:
                        silent += 1
                        if len(examples) < 3:
                            examples.append({"kind": "silent_composition", "x": x, "y": y})

            # identity laws
            idc = _cert(dict(o1), dict(o1), ())
            if compose(c1, idc, bridges) != c1 or compose(_cert(dict(i1), dict(i1), ()), c1, bridges) != c1:
                ident_viol += 1
                if len(examples) < 3:
                    examples.append({"kind": "identity", "cert": c1})

    return {
        "triples_examined": triples,
        "composable": composable,
        "associativity_violations": assoc_viol,
        "identity_violations": ident_viol,
        "mismatches": mismatches,
        "silent_compositions": silent,
        "examples": examples,
    }


# ---------------------------------------------------------------- T13

def transport(obj: dict, morph: dict) -> dict:
    """Apply a regime morphism coordinatewise."""
    return {k: morph.get(k, {}).get(v, v) for k, v in obj.items()}


def t13_atlas(values: int = 3, load_bearing: int = 2) -> dict:
    """Path-independence iff every load-bearing coordinate square commutes.

    The declared composite is enumerated INDEPENDENTLY of g and f. An earlier
    draft built it as g o f coordinatewise, which made the commuting-square test
    vacuously true and the biconditional unfalsifiable -- it would have reported
    zero violations on any theory whatsoever. The theorem is about whether a
    *declared* transport T_{g o f} agrees with T_g o T_f, so the declared one has
    to be free to disagree.

    The class of declared composites is total over {g o f} union its single-point
    perturbations: exactly the neighbourhood in which the biconditional can fail
    by one coordinate value, which is the minimal witness the theorem predicts.
    """
    coords = COORDS[:load_bearing]
    vals = list(range(values))
    maps = [dict(zip(vals, p)) for p in itertools.product(vals, repeat=values)]

    triples = pi = commute = fwd_viol = bwd_viol = 0
    minimal = None

    for fm in itertools.product(maps, repeat=load_bearing):
        f = {c: m for c, m in zip(coords, fm)}
        for gm in itertools.product(maps, repeat=load_bearing):
            g = {c: m for c, m in zip(coords, gm)}
            true_comp = {c: {v: g[c][f[c][v]] for v in vals} for c in coords}

            declared = [true_comp]
            for c in coords:
                for v in vals:
                    for alt in vals:
                        if alt == true_comp[c][v]:
                            continue
                        pert = {k: dict(m) for k, m in true_comp.items()}
                        pert[c][v] = alt
                        declared.append(pert)

            for h in declared:
                triples += 1
                squares_commute = all(
                    h[c][v] == g[c][f[c][v]] for c in coords for v in vals
                )
                path_independent = True
                for combo in itertools.product(vals, repeat=load_bearing):
                    obj = dict(zip(coords, combo))
                    if transport(transport(obj, f), g) != transport(obj, h):
                        path_independent = False
                        break
                if squares_commute:
                    commute += 1
                if path_independent:
                    pi += 1
                if squares_commute and not path_independent:
                    fwd_viol += 1
                    if minimal is None:
                        minimal = {"kind": "commutes_but_path_dependent", "f": f, "g": g, "h": h}
                if path_independent and not squares_commute:
                    bwd_viol += 1
                    if minimal is None:
                        minimal = {"kind": "path_independent_but_square_fails", "f": f, "g": g, "h": h}

    return {
        "triples_examined": triples,
        "squares_commute": commute,
        "path_independent": pi,
        "biconditional_violations": fwd_viol + bwd_viol,
        "forward_violations": fwd_viol,
        "backward_violations": bwd_viol,
        "minimal_witness": minimal,
    }


# ---------------------------------------------------------------- donor

def donor_atlas() -> dict:
    """Information-equivalent donor: same bits, no factor typing.

    Per the issue's discipline this should TIE on admitting decisions. A donor
    win would indicate hidden information or resource asymmetry, not superiority.
    """
    compared = agree = donor_wins = witness_wins = 0
    for bits in itertools.product((False, True), repeat=len(FACTORS)):
        w = dict(zip(FACTORS, bits))
        witness = admits(w)
        donor = sum(bits) == len(FACTORS)  # same information, untyped
        compared += 1
        if witness == donor:
            agree += 1
        elif donor and not witness:
            donor_wins += 1
        else:
            witness_wins += 1
    return {
        "decisions_compared": compared,
        "agreements": agree,
        "donor_wins": donor_wins,
        "witness_wins": witness_wins,
    }


def main() -> None:
    t0 = time.time()
    grid = {"factors": len(FACTORS), "coords": len(COORDS), "t10_values": 3,
            "t13_values": 3, "t13_load_bearing": 2, "seed": 20260825}
    t8 = t8_atlas()
    t10 = t10_atlas(values=grid["t10_values"])
    t13 = t13_atlas(values=grid["t13_values"], load_bearing=grid["t13_load_bearing"])
    donor = donor_atlas()
    elapsed = round(time.time() - t0, 3)

    manifest = {
        "schema_version": "orion.raw-result-manifest.v1",
        "job_id": "EXEC-CM-01",
        "grid": grid,
        "t8": t8,
        "t10": t10,
        "t13": t13,
        "donor": donor,
        "totals": {
            "models_enumerated": (2 ** len(FACTORS)) * len(FACTORS)
            + t10["triples_examined"] + t13["triples_examined"],
            "wallclock_seconds": elapsed,
        },
    }
    (HERE / "RAW_RESULT_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({k: manifest[k] for k in ("grid", "donor", "totals")}, indent=2))
    print("t8 factors with countermodels:",
          sum(1 for v in t8.values() if v["countermodels_found"] > 0), "/", len(FACTORS))
    print("t10 assoc_viol=", t10["associativity_violations"],
          "ident_viol=", t10["identity_violations"],
          "silent=", t10["silent_compositions"], "of", t10["mismatches"], "mismatches")
    print("t13 biconditional_violations=", t13["biconditional_violations"],
          "(fwd", t13["forward_violations"], "bwd", t13["backward_violations"], ")")


if __name__ == "__main__":
    main()
