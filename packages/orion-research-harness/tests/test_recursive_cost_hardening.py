from __future__ import annotations

from orion.core.problem_tree import DiscriminatorKind, DiscriminatorSpec, ResidualAtom
from orion.core.residuals import Responsibility
from orion.engine.residual_recursion import ResidualRecursionPlanner


def _atom(atom_id: str, kind: DiscriminatorKind, declared_cost: float) -> ResidualAtom:
    return ResidualAtom(
        atom_id=atom_id,
        question=f"Does {atom_id} settle the atom?",
        responsibility=Responsibility.METHOD,
        discriminator=DiscriminatorSpec(
            discriminator_id=f"disc:{atom_id}",
            kind=kind,
            question=f"Run {atom_id} discriminator.",
            success_criterion="Return a decision-separating result.",
            expected_cost_units=declared_cost,
        ),
    )


def test_model_declared_cost_cannot_promote_experiment_ahead_of_dominance() -> None:
    dominance = _atom("dominance", DiscriminatorKind.DOMINANCE_PROOF, 999.0)
    experiment = _atom("experiment", DiscriminatorKind.EXPERIMENT, 0.0)
    ordered = ResidualRecursionPlanner.order_atoms((experiment, dominance))
    assert tuple(item.atom_id for item in ordered) == ("dominance", "experiment")


def test_declared_cost_only_orders_within_same_discriminator_class() -> None:
    slow_exact = _atom("slow-exact", DiscriminatorKind.EXACT_COMPUTATION, 10.0)
    fast_exact = _atom("fast-exact", DiscriminatorKind.EXACT_COMPUTATION, 1.0)
    ordered = ResidualRecursionPlanner.order_atoms((slow_exact, fast_exact))
    assert tuple(item.atom_id for item in ordered) == ("fast-exact", "slow-exact")
