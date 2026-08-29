#!/usr/bin/env python3
"""Independent finite regression for ORION18.AUTHORITY_CUT_IDENTIFIABILITY.v1."""
from itertools import product


def fibre_constant(labels, observations):
    seen = {}
    for label, obs in zip(labels, observations):
        if obs in seen and seen[obs] != label:
            return False
        seen[obs] = label
    return True


def classifier_exists(labels, observations):
    values = sorted(set(observations))
    position = {value: i for i, value in enumerate(values)}
    for outputs in product((0, 1), repeat=len(values)):
        if all(outputs[position[obs]] == label for label, obs in zip(labels, observations)):
            return True
    return False


def main():
    checked = 0
    for n_worlds in range(1, 5):
        for labels in product((0, 1), repeat=n_worlds):
            for observations in product(range(3), repeat=n_worlds):
                assert fibre_constant(labels, observations) == classifier_exists(labels, observations)
                checked += 1

    # Canonical control-cut counterexample: bytes identical, governance differs.
    labels = (1, 0)
    observations = ("same-internal-transcript", "same-internal-transcript")
    assert not fibre_constant(labels, observations)
    assert not classifier_exists(labels, observations)

    # An exogenous observable can remove this particular mixed fibre.  This is
    # an identifiability control only; it does not assert scientific validity.
    observations_with_external_edge = ("same|external-A", "same|internal-control")
    assert fibre_constant(labels, observations_with_external_edge)
    assert classifier_exists(labels, observations_with_external_edge)

    print(
        "ORION18_AUTHORITY_CUT_IDENTIFIABILITY_V1_PASS "
        f"finite_systems={checked} mixed_fibre_control=PASS exogenous_edge_control=PASS"
    )


if __name__ == "__main__":
    main()
