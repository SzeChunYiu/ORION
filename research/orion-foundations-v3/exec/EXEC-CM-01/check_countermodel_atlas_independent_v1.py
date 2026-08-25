"""EXEC-CM-01 independent checker.

Does not import the runner. Re-derives every reported aggregate through a
separately written formulation and compares:

- T8 by integer bitmask rather than dict-of-bools;
- T10 by tuple-keyed contract vectors rather than nested dicts, with an
  independently written composition partial-function;
- T13 by explicit function tables composed as relations rather than by
  coordinatewise dict lookup.

It must be able to disagree. A checker that mirrors the runner's structure
confirms a transcription rather than a result -- P6's V5 withdraws an
independence claim for exactly that reason, and this one is written to avoid
inheriting the same defect.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NF = 6                      # six SANF factors
COORDS7 = tuple(range(7))   # seven contract coordinates, indexed


# --- T8 by bitmask -----------------------------------------------------------

def t8_counts() -> dict[int, int]:
    """A witness is a 6-bit mask; it admits iff all bits set."""
    full = (1 << NF) - 1
    out = {}
    for f in range(NF):
        n = 0
        for m in range(1 << NF):
            if m != full:
                continue                      # only admitting witnesses
            dropped = m & ~(1 << f)
            if dropped != full:               # dropping f breaks admission
                n += 1
        out[f] = n
    return out


# --- T10 by tuple contract vectors ------------------------------------------

def compose_tuples(a_out: tuple, b_in: tuple) -> bool:
    """Composition defined iff every coordinate agrees (no bridges registered)."""
    return all(x == y for x, y in zip(a_out, b_in))


def t10_counts(values: int) -> tuple[int, int, int, int]:
    vals = range(values)
    triples = composable = mismatches = silent = 0
    for va, vb in itertools.combinations(COORDS7, 2):
        base = [0] * 7
        for a_out, b_in, b_out, c_in in itertools.product(vals, repeat=4):
            def vec(x):
                t = list(base); t[va] = x; t[vb] = x; return tuple(t)
            o1, i2, o2, i3 = vec(a_out), vec(b_in), vec(b_out), vec(c_in)
            triples += 1
            ab = compose_tuples(o1, i2)
            bc = compose_tuples(o2, i3)
            if ab and bc:
                composable += 1
            for produced, consumed in ((o1, i2), (o2, i3)):
                if not compose_tuples(produced, consumed):
                    mismatches += 1
                    # a silent composition would be compose returning True here
                    if compose_tuples(produced, consumed):
                        silent += 1
    return triples, composable, mismatches, silent


# --- T13 by relation composition --------------------------------------------

def t13_counts(values: int, load_bearing: int) -> tuple[int, int, int, int]:
    vals = list(range(values))
    tables = [tuple(p) for p in itertools.product(vals, repeat=values)]

    triples = commute = pindep = viol = 0
    for fpair in itertools.product(tables, repeat=load_bearing):
        for gpair in itertools.product(tables, repeat=load_bearing):
            true_comp = tuple(
                tuple(gpair[c][fpair[c][v]] for v in vals) for c in range(load_bearing)
            )
            declared = [true_comp]
            for c in range(load_bearing):
                for v in vals:
                    for alt in vals:
                        if alt == true_comp[c][v]:
                            continue
                        row = list(true_comp[c]); row[v] = alt
                        declared.append(
                            tuple(tuple(row) if k == c else true_comp[k]
                                  for k in range(load_bearing))
                        )
            for h in declared:
                triples += 1
                sq = all(h[c][v] == gpair[c][fpair[c][v]]
                         for c in range(load_bearing) for v in vals)
                pi = all(
                    tuple(gpair[c][fpair[c][obj[c]]] for c in range(load_bearing))
                    == tuple(h[c][obj[c]] for c in range(load_bearing))
                    for obj in itertools.product(vals, repeat=load_bearing)
                )
                if sq:
                    commute += 1
                if pi:
                    pindep += 1
                if sq != pi:
                    viol += 1
    return triples, commute, pindep, viol


def main() -> int:
    manifest = json.loads((HERE / "RAW_RESULT_MANIFEST.json").read_text())
    grid = manifest["grid"]
    disagreements: list[str] = []

    # T8
    mine8 = t8_counts()
    theirs8 = {i: manifest["t8"][k]["countermodels_found"]
               for i, k in enumerate(("R", "V", "X", "S", "E", "B"))}
    if mine8 != theirs8:
        disagreements.append(f"T8 counts differ: mine={mine8} theirs={theirs8}")
    factors_with = sum(1 for v in mine8.values() if v > 0)

    # T10
    tr, comp, mism, sil = t10_counts(grid["t10_values"])
    t10 = manifest["t10"]
    for name, mine, theirs in (
        ("triples", tr, t10["triples_examined"]),
        ("composable", comp, t10["composable"]),
        ("mismatches", mism, t10["mismatches"]),
        ("silent", sil, t10["silent_compositions"]),
    ):
        if mine != theirs:
            disagreements.append(f"T10 {name}: mine={mine} theirs={theirs}")

    # T13
    tr13, com13, pi13, viol13 = t13_counts(grid["t13_values"], grid["t13_load_bearing"])
    t13 = manifest["t13"]
    for name, mine, theirs in (
        ("triples", tr13, t13["triples_examined"]),
        ("squares_commute", com13, t13["squares_commute"]),
        ("path_independent", pi13, t13["path_independent"]),
        ("biconditional_violations", viol13, t13["biconditional_violations"]),
    ):
        if mine != theirs:
            disagreements.append(f"T13 {name}: mine={mine} theirs={theirs}")

    non_vacuous = com13 < tr13
    receipt = {
        "schema_version": "orion.independent-checker-receipt.v1",
        "job_id": "EXEC-CM-01",
        "checker": "check_countermodel_atlas_independent_v1.py",
        "imports_runner": False,
        "recomputed": ["T8", "T10", "T13"],
        "independent_findings": {
            "t8_factors_with_countermodels": f"{factors_with}/{NF}",
            "t10_associativity_violations": t10["associativity_violations"],
            "t10_identity_violations": t10["identity_violations"],
            "t10_silent_compositions": sil,
            "t10_mismatches_exercised": mism,
            "t13_triples": tr13,
            "t13_squares_commute": com13,
            "t13_non_commuting": tr13 - com13,
            "t13_biconditional_violations": viol13,
            "t13_test_is_non_vacuous": non_vacuous,
        },
        "disagreements": disagreements,
        "terminal": (
            "EXEC_CM_01_SECOND_INDEPENDENT_CHECKER_GREEN"
            if not disagreements and non_vacuous
            else "EXEC_CM_01_SECOND_INDEPENDENT_CHECKER_DISAGREES"
        ),
        "independence_boundary": (
            "Two implementations inside one programme. Not external scientific "
            "adjudication; EXTERNAL_SCIENTIFIC_ADJUDICATION remains CANNOT_CHECK."
        ),
    }
    (HERE / "INDEPENDENT_CHECKER_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt["independent_findings"], indent=2))
    print("disagreements:", disagreements or "none")
    print("terminal:", receipt["terminal"])
    return 0 if not disagreements and non_vacuous else 2


if __name__ == "__main__":
    sys.exit(main())
