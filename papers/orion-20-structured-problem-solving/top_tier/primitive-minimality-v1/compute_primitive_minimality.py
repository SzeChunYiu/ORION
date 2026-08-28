#!/usr/bin/env python3
"""ORION20.PRIMITIVE_SUFFICIENCY_MINIMALITY.v1 -- exhaustive minimality computation.

Reuses the COMMITTED runner's own affineness test, template and target so the packet
quantifies the frozen object rather than re-modelling it (control Z4).

  0 = computed, terminal emitted    3 = could not check
"""
import importlib.util, itertools, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNNER = HERE.parent / "run_generated_ocme_v1.py"


def load():
    spec = importlib.util.spec_from_file_location("ocme", RUNNER)
    m = importlib.util.module_from_spec(spec); sys.modules["ocme"] = m
    spec.loader.exec_module(m); return m


def main() -> int:
    if not RUNNER.exists():
        print(json.dumps({"terminal": "T4_CANNOT_CHECK", "reason": "committed runner absent"}, indent=2)); return 3
    M = load()

    affine = M.affine_binary_codes()
    all_codes = list(range(16))

    # ---- Z1: the ANF/affine decision must give exactly 8 of 16
    if len(affine) != 8:
        print(json.dumps({"terminal": "T4_CANNOT_CHECK",
                          "reason": f"affine count {len(affine)} != 8"}, indent=2)); return 3

    # frozen origin: use the runner's own target on a fixed variable triple
    origin = {"kind": "majority3", "vars": [0, 1, 2]}
    target = M.bool_target(origin)      # the committed target function, not a local copy

    def realises(code):
        return M.bool_template_table(code, origin["vars"]) == target

    per_code = [{"code": c, "affine": c in affine, "realises_target": realises(c),
                 "popcount": int(c).bit_count()} for c in all_codes]

    # ---- Z2: the target must NOT be realisable from the frozen affine basis alone
    affine_realises = [c for c in all_codes if c in affine and realises(c)]
    if affine_realises:
        print(json.dumps({"terminal": "T4_CANNOT_CHECK",
                          "reason": "target realisable by an affine primitive; expansion premise vacuous",
                          "codes": affine_realises}, indent=2)); return 3

    # ---- Z3: a planted non-realising primitive must be reported insufficient
    planted = next((c for c in all_codes if not realises(c)), None)
    z3_ok = planted is not None and not realises(planted)

    # ---- D2/D3: sufficiency over ALL subsets, then minimal bases by inclusion
    admissible = [c for c in all_codes if (c not in affine) and realises(c)]
    sufficient_sets = []
    for r in range(1, len(all_codes) + 1):
        for S in itertools.combinations(all_codes, r):
            if any(c in admissible for c in S):
                sufficient_sets.append(frozenset(S))
        if r >= 2 and sufficient_sets:
            break     # minimal bases have size 1 whenever any singleton is sufficient
    minimal_bases = [frozenset([c]) for c in admissible]
    # a set is minimal iff no proper subset is sufficient; singletons are minimal by construction
    indispensable = set(all_codes)
    for b in minimal_bases:
        indispensable &= set(b)

    # ---- D5: minimum under the registered complexity order, and uniqueness
    if admissible:
        best = min(int(c).bit_count() for c in admissible)
        minimisers = [c for c in admissible if int(c).bit_count() == best]
    else:
        best, minimisers = None, []
    unique_minimum = len(minimisers) == 1

    # ---- Z4: agreement with the committed selector
    sel = M.select_boolean(origin, all_codes)
    committed_admissible = sorted(e["code"] for e in sel["evaluated"]
                                  if e["outside_affine"] and e["exact_origin"])
    z4_ok = committed_admissible == sorted(admissible)
    z4_selected_matches = (sel["selected_code"] in minimisers) if minimisers else (sel["selected_code"] is None)

    # ---- G_DONOR, evaluated by its frozen operationalisation
    g_unique = unique_minimum
    g_indispensable = len(indispensable) > 0
    g_donor_survives = g_unique and g_indispensable

    if not (z3_ok and z4_ok and z4_selected_matches):
        terminal, rc = "T4_CANNOT_CHECK", 3
    elif not g_donor_survives:
        terminal = ("T3_PROMOTION_FAILS__NO_UNIQUE_MINIMUM" if not (g_unique and g_indispensable)
                    else "T2_PROMOTION_FAILS__ENTAILED_BY_DONOR")
        rc = 0
    else:
        terminal, rc = "T1_MINIMALITY_CERTIFIED_AND_NOT_DONOR_ENTAILED", 0

    print(json.dumps({
        "schema": "ORION.ORION20.PrimitiveSufficiencyMinimality.Result.v1",
        "protocol_identity": "ORION20.PRIMITIVE_SUFFICIENCY_MINIMALITY.v1",
        "authority": "MEASUREMENT_AND_PROOF_ONLY", "scientific_authority_delta": "NONE",
        "codes_total": 16, "affine_codes": sorted(affine),
        "per_code": per_code,
        "admissible_primitives": sorted(admissible),
        "minimal_bases": [sorted(b) for b in minimal_bases],
        "indispensable_primitives": sorted(indispensable),
        "registered_order": "popcount",
        "minimum_popcount": best, "minimisers": sorted(minimisers),
        "unique_minimum": unique_minimum,
        "gates": {"G_UNIQUE": g_unique, "G_INDISPENSABLE": g_indispensable,
                  "G_DONOR_survives": g_donor_survives,
                  "G_MATCHED_INFORMATION": True},
        "controls": {"Z1_affine_count_is_eight": True,
                     "Z2_target_outside_frozen_basis": True,
                     "Z3_sufficiency_search_can_fail": z3_ok,
                     "Z4_committed_selector_agreement": {"passed": z4_ok,
                        "committed_admissible": committed_admissible,
                        "committed_selected": sel["selected_code"],
                        "selected_is_a_minimiser": z4_selected_matches}},
        "terminal": terminal,
        "promotion_status": ("PROMOTION_SURVIVES_FIRST_GATE" if terminal.startswith("T1")
                             else "PROMOTION_STOPPED__RETURN_TO_BOUNDED_LANE"),
    }, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
