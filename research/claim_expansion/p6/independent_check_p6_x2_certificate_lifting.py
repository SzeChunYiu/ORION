from __future__ import annotations

import hashlib
import itertools
import json

DONORS = ("POE", "PCE", "PCAA", "WORKFLOW_SIGNATURE", "CERTIFIED_PURITY")
COORDS = (
    "claim_content_binding",
    "measurement_semantics",
    "evidence_semantics",
    "inferential_obligation",
    "scientific_epoch",
)


def independent_lift(native_valid: bool, flags: tuple[bool, ...]) -> bool:
    if not native_valid:
        return False
    for flag in flags:
        if flag is not True:
            return False
    return True


def main() -> None:
    rows = []
    for donor in DONORS:
        for native in (False, True):
            for flags in itertools.product((False, True), repeat=5):
                verdict = independent_lift(native, flags)
                rows.append(
                    {
                        "donor": donor,
                        "native_valid": native,
                        "science": dict(zip(COORDS, flags)),
                        "liftable": verdict,
                        "ideal_product": native and all(flags),
                    }
                )

    digest = hashlib.sha256(
        json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert len(rows) == 320
    assert digest == "e1e3c48bcefea3750d952c6b0ff37ac660a2e21f9823fdfdeb50bb62e819ff93"

    separation = 0
    for _donor in DONORS:
        for idx in range(5):
            hi = [True] * 5
            lo = hi[:]
            lo[idx] = False
            assert independent_lift(True, tuple(hi))
            assert not independent_lift(True, tuple(lo))
            separation += 1
    assert separation == 25

    product_countermodels = 0
    for flags in itertools.product((False, True), repeat=5):
        if all(flags):
            continue
        assert not independent_lift(True, flags)
        product_countermodels += 1
    assert product_countermodels == 31

    full_revalidation = 0
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
                        assert not independent_lift(True, tuple(partial))
                        partial_failures += 1
                repaired = damaged[:]
                for idx in changed:
                    repaired[idx] = True
                assert independent_lift(True, tuple(repaired))
                full_revalidation += 1
    assert full_revalidation == 155
    assert partial_failures == 1055

    # Independence is claimed by `imports_primary_checker: false`, which copying
    # satisfies. `independent_lift` is an early-return spelling of the primary's
    # `native_valid and all(science)`, and the row payload's `ideal_product` is
    # that same expression inline -- so `ideal_product_mismatches` is 0 for every
    # theory of lifting, and the two implementations agree on all 320 points
    # because they are the same rule. Not importing a checker is not the same as
    # not being it, and agreement is not evidence of independence.
    #
    # The only thing here that would notice a wrong theory is the stored-digest
    # assertion above, which is agreement with a constant. Both facts are now
    # reported rather than left for a reader to infer. See
    # research/failures/2026-08-unfalsifiable-check-zero-refutation-capacity/.
    ideal_product_divergence = sum(
        1 for row in rows if row["liftable"] != row["ideal_product"]
    )
    independence_demonstrated = ideal_product_divergence > 0

    print(json.dumps({
        "status": (
            "P6_X2_INDEPENDENT_AUDIT_PASS" if independence_demonstrated
            else "P6_X2_INDEPENDENT_AUDIT_CANNOT_CHECK"
        ),
        "independence_status": (
            "DEMONSTRATED" if independence_demonstrated else "CANNOT_CHECK"
        ),
        "independence_cannot_check_reason": None if independence_demonstrated else (
            "independent_lift and the row payload's ideal_product agree on all "
            f"{len(rows)} points because both spell the primary's rule; "
            "imports_primary_checker=false records an import that did not happen, "
            "not a rule that was written twice"
        ),
        "ideal_product_mismatches": (
            ideal_product_divergence if independence_demonstrated else None
        ),
        "sole_wrong_theory_detector": "assert digest == <stored constant>",
        "states": 320,
        "separation_witnesses": 25,
        "product_countermodels": 31,
        "full_revalidation_successes": 155,
        "partial_revalidation_failures": 1055,
        "canonical_rows_sha256": digest,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
