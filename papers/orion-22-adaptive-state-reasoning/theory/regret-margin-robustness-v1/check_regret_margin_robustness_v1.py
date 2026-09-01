#!/usr/bin/env python3
"""Independent exact regression for ORION22.REGRET_MARGIN_ROBUSTNESS.v1."""
from fractions import Fraction
from itertools import product


def unique_optimum_and_margin(losses):
    floor = min(losses)
    winners = [i for i, loss in enumerate(losses) if loss == floor]
    if len(winners) != 1:
        return None
    winner = winners[0]
    margin = min(loss - floor for i, loss in enumerate(losses) if i != winner)
    return winner, margin


def main():
    systems = 0
    perturbations = 0
    for n_actions in range(2, 5):
        for losses in product(range(5), repeat=n_actions):
            result = unique_optimum_and_margin(losses)
            if result is None:
                continue
            winner, margin = result
            epsilon = Fraction(margin, 2) - Fraction(1, 4)
            assert epsilon >= 0

            # For a box of independent perturbations, every pairwise gap is
            # affine in the perturbations, so extrema occur at box corners.
            for signs in product((-1, 1), repeat=n_actions):
                perturbed = [Fraction(losses[i]) + signs[i] * epsilon for i in range(n_actions)]
                assert perturbed[winner] < min(
                    perturbed[i] for i in range(n_actions) if i != winner
                )
                perturbations += 1

            runner_up = min(
                (i for i in range(n_actions) if i != winner), key=lambda i: losses[i]
            )
            half = Fraction(margin, 2)
            tie = [Fraction(loss) for loss in losses]
            tie[winner] += half
            tie[runner_up] -= half
            assert tie[winner] == tie[runner_up]

            beyond = half + Fraction(1, 4)
            inverted = [Fraction(loss) for loss in losses]
            inverted[winner] += beyond
            inverted[runner_up] -= beyond
            assert inverted[runner_up] < inverted[winner]
            systems += 1

    print(
        "ORION22_REGRET_MARGIN_ROBUSTNESS_V1_PASS "
        f"unique_optimum_systems={systems} box_corner_perturbations={perturbations} "
        "sharp_tie_controls=PASS sharp_inversion_controls=PASS"
    )


if __name__ == "__main__":
    main()
