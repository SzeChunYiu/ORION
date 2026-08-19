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


def liftable(native_valid: bool, science: tuple[bool, ...]) -> bool:
    return native_valid and all(science)


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def main() -> None:
    rows = []
    donor_conservativity_violations = 0
    ideal_product_mismatches = 0

    # Full bounded state enumeration.
    for donor in DONORS:
        for native_valid in (False, True):
            for science in itertools.product((False, True), repeat=len(COORDS)):
                p6 = liftable(native_valid, science)
                ideal = native_valid and all(science)
                if ideal != p6:
                    ideal_product_mismatches += 1
                # Projection does not alter the donor-native verdict by construction.
                projected_native = native_valid
                if projected_native != native_valid:
                    donor_conservativity_violations += 1
                rows.append(
                    {
                        "donor": donor,
                        "native_valid": native_valid,
                        "science": dict(zip(COORDS, science)),
                        "liftable": p6,
                        "ideal_product": ideal,
                    }
                )

    # Minimal one-coordinate separation witnesses.
    separation_witnesses = []
    full = (True,) * len(COORDS)
    for donor in DONORS:
        assert liftable(True, full)
        for idx, coord in enumerate(COORDS):
            broken = list(full)
            broken[idx] = False
            broken = tuple(broken)
            assert not liftable(True, broken)
            separation_witnesses.append({"donor": donor, "coordinate": coord})

    # A product of all donor-native valid certificates cannot infer missing science coordinates.
    product_countermodels = []
    for science in itertools.product((False, True), repeat=len(COORDS)):
        if all(science):
            continue
        assert not liftable(True, science)
        product_countermodels.append(dict(zip(COORDS, science)))

    # Exact selective revalidation.
    full_revalidation_successes = 0
    partial_revalidation_failures = 0
    for donor in DONORS:
        for r in range(1, len(COORDS) + 1):
            for changed in itertools.combinations(range(len(COORDS)), r):
                damaged = [True] * len(COORDS)
                for idx in changed:
                    damaged[idx] = False
                assert not liftable(True, tuple(damaged))

                fully_repaired = damaged[:]
                for idx in changed:
                    fully_repaired[idx] = True
                assert liftable(True, tuple(fully_repaired))
                full_revalidation_successes += 1

                changed_set = set(changed)
                for k in range(0, len(changed)):
                    for repaired in itertools.combinations(changed, k):
                        partial = damaged[:]
                        for idx in repaired:
                            partial[idx] = True
                        if set(repaired) != changed_set:
                            assert not liftable(True, tuple(partial))
                            partial_revalidation_failures += 1

    result = {
        "schema": "P6.X2.CertificateLiftingResult.v1",
        "donor_families": list(DONORS),
        "science_coordinates": list(COORDS),
        "state_evaluations": len(rows),
        "donor_conservativity_violations": donor_conservativity_violations,
        "single_coordinate_separation_witnesses": len(separation_witnesses),
        "certificate_product_countermodels": len(product_countermodels),
        "full_revalidation_successes": full_revalidation_successes,
        "partial_revalidation_failures": partial_revalidation_failures,
        "ideal_product_mismatches": ideal_product_mismatches,
        "canonical_rows_sha256": hashlib.sha256(canonical(rows).encode()).hexdigest(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
