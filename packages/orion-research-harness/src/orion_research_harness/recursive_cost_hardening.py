from __future__ import annotations

from orion.core.problem_tree import DiscriminatorKind
from orion.engine import residual_recursion as _recursion


_KIND_PRECEDENCE = {
    DiscriminatorKind.DOMINANCE_PROOF: 0,
    DiscriminatorKind.FORMAL_PROOF: 1,
    DiscriminatorKind.EXACT_COMPUTATION: 2,
    DiscriminatorKind.DONOR_SEARCH: 3,
    DiscriminatorKind.HOSTILE_TEST: 4,
    DiscriminatorKind.RETRIEVAL: 5,
    DiscriminatorKind.MEASUREMENT: 6,
    DiscriminatorKind.INTERACTION_TEST: 7,
    DiscriminatorKind.EXPERIMENT: 8,
    DiscriminatorKind.CANNOT_CHECK: 99,
}


def _solver_owned_order(atoms):
    """Order by frozen discriminator class, then declared within-class cost.

    The semantic reasoner may estimate cost, but it cannot promote an experiment ahead
    of a proof/obstruction by reporting a convenient number. That makes shortcut
    scheduling controller-owned rather than prompt-owned.
    """

    return tuple(
        sorted(
            atoms,
            key=lambda atom: (
                _KIND_PRECEDENCE[atom.discriminator.kind],
                float(atom.discriminator.expected_cost_units),
                atom.atom_id,
            ),
        )
    )


def install_recursive_cost_hardening() -> None:
    _recursion.ResidualRecursionPlanner.order_atoms = staticmethod(_solver_owned_order)
    _recursion.ProblemRecursionPlanner.order_atoms = staticmethod(_solver_owned_order)
    _recursion._solver_owned_shortcut_order_installed = True


install_recursive_cost_hardening()


__all__ = ["install_recursive_cost_hardening"]
