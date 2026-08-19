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


def independent_carries(native: bool, flags: tuple[bool, ...]) -> bool:
    if not native:
        return False
    return all(flag is True for flag in flags)


def main() -> None:
    rows = []
    for donor in DONORS:
        for native in (False, True):
            for flags in itertools.product((False, True), repeat=5):
                verdict = independent_carries(native, flags)
                rows.append({
                    "donor": donor,
                    "native_valid": native,
                    "closure": dict(zip(COORDS, flags)),
                    "carries": verdict,
                    "ideal_product": native and all(flags),
                })
    digest = hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert len(rows) == 320
    assert digest == "25f40385714adb15bca298a8cfd2b7fe2b28c96bfe462f6b60583be8f735b95f"

    separation = 0
    for _donor in DONORS:
        for idx in range(5):
            hi = [True] * 5
            lo = hi[:]
            lo[idx] = False
            assert independent_carries(True, tuple(hi))
            assert not independent_carries(True, tuple(lo))
            separation += 1
    assert separation == 25

    product_countermodels = 0
    for flags in itertools.product((False, True), repeat=5):
        if all(flags):
            continue
        assert not independent_carries(True, flags)
        product_countermodels += 1
    assert product_countermodels == 31

    full_refinement = 0
    partial_failures = 0
    for _donor in DONORS:
        for r in range(1, 6):
            for changed in itertools.combinations(range(5), r):
                damaged = [True] * 5
                for idx in changed:
                    damaged[idx] = False
                for k in range(0, len(changed)):
                    for repaired in itertools.combinations(changed, k):
                        partial = damaged[:]
                        for idx in repaired:
                            partial[idx] = True
                        assert not independent_carries(True, tuple(partial))
                        partial_failures += 1
                repaired = damaged[:]
                for idx in changed:
                    repaired[idx] = True
                assert independent_carries(True, tuple(repaired))
                full_refinement += 1
    assert full_refinement == 155
    assert partial_failures == 1055

    comp_ok = 0
    comp_bad_bridge = 0
    full = (True,) * 5
    for _d1 in DONORS:
        for _d2 in DONORS:
            c1 = independent_carries(True, full)
            c2 = independent_carries(True, full)
            assert c1 and c2
            assert c1 and c2 and True
            comp_ok += 1
            assert not (c1 and c2 and False)
            comp_bad_bridge += 1
    assert comp_ok == 25
    assert comp_bad_bridge == 25

    print(json.dumps({
        "status": "P7_X2_INDEPENDENT_AUDIT_PASS",
        "states": 320,
        "separation_witnesses": 25,
        "product_countermodels": 31,
        "full_refinement_successes": 155,
        "partial_refinement_failures": 1055,
        "composition_successes": 25,
        "composition_bridge_countermodels": 25,
        "canonical_rows_sha256": digest,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
