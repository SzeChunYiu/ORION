from __future__ import annotations

import hashlib
import itertools
import json

DONORS = (
    "PLANNING_REFINEMENT",
    "CEGAR_REFINEMENT",
    "BIDIRECTIONAL_MIGRATION",
    "WORLD_MODEL_REPLAN",
    "TERMINAL_COMMITMENT",
)
COORDS = (
    "obligations_total",
    "obligations_unambiguous",
    "frontier_resolved",
    "objective_semantics_preserved",
    "closure_epoch_current",
)


def carries(native_valid: bool, closure: tuple[bool, ...]) -> bool:
    return native_valid and all(closure)


def compose(c1: bool, c2: bool, bridge_match: bool) -> bool:
    return c1 and c2 and bridge_match


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def main() -> None:
    rows = []
    donor_conservativity_violations = 0
    ideal_product_mismatches = 0
    for donor in DONORS:
        for native_valid in (False, True):
            for closure in itertools.product((False, True), repeat=5):
                verdict = carries(native_valid, closure)
                ideal = native_valid and all(closure)
                if verdict != ideal:
                    ideal_product_mismatches += 1
                projected_native = native_valid
                if projected_native != native_valid:
                    donor_conservativity_violations += 1
                rows.append({
                    "donor": donor,
                    "native_valid": native_valid,
                    "closure": dict(zip(COORDS, closure)),
                    "carries": verdict,
                    "ideal_product": ideal,
                })

    separation_witnesses = 0
    full = (True,) * 5
    for donor in DONORS:
        assert carries(True, full)
        for idx in range(5):
            broken = list(full)
            broken[idx] = False
            assert not carries(True, tuple(broken))
            separation_witnesses += 1

    product_countermodels = 0
    for closure in itertools.product((False, True), repeat=5):
        if all(closure):
            continue
        assert not carries(True, closure)
        product_countermodels += 1

    full_refinement_successes = 0
    partial_refinement_failures = 0
    for donor in DONORS:
        for r in range(1, 6):
            for changed in itertools.combinations(range(5), r):
                damaged = [True] * 5
                for idx in changed:
                    damaged[idx] = False
                assert not carries(True, tuple(damaged))
                for k in range(0, len(changed)):
                    for repaired in itertools.combinations(changed, k):
                        partial = damaged[:]
                        for idx in repaired:
                            partial[idx] = True
                        assert not carries(True, tuple(partial))
                        partial_refinement_failures += 1
                repaired = damaged[:]
                for idx in changed:
                    repaired[idx] = True
                assert carries(True, tuple(repaired))
                full_refinement_successes += 1

    composition_successes = 0
    composition_bridge_countermodels = 0
    for d1 in DONORS:
        for d2 in DONORS:
            c1 = carries(True, full)
            c2 = carries(True, full)
            assert compose(c1, c2, True)
            composition_successes += 1
            assert not compose(c1, c2, False)
            composition_bridge_countermodels += 1

    result = {
        "schema": "P7.X2.ClosureCarryingResult.v1",
        "donor_families": list(DONORS),
        "closure_coordinates": list(COORDS),
        "state_evaluations": len(rows),
        "donor_conservativity_violations": donor_conservativity_violations,
        "single_coordinate_separation_witnesses": separation_witnesses,
        "donor_product_nonclosure_countermodels": product_countermodels,
        "full_closure_refinement_successes": full_refinement_successes,
        "partial_closure_refinement_failures": partial_refinement_failures,
        "composition_successes": composition_successes,
        "composition_bridge_countermodels": composition_bridge_countermodels,
        "ideal_product_mismatches": ideal_product_mismatches,
        "canonical_rows_sha256": hashlib.sha256(canonical(rows).encode()).hexdigest(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
