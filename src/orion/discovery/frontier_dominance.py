"""Finite reference semantics for ORION scientific frontier dominance.

The module distinguishes three questions that ordinary benchmark comparisons
frequently collapse:

1. Does a candidate preserve every success already available to the registered
   donor envelope under matched information and resources?
2. Does it strictly reach at least one scientifically admissible target that no
   registered donor reaches under that contract?
3. Is the apparent residual still present after semantic donor absorption,
   hidden-consequence testing, and Pareto resource accounting?

All results are class-relative and non-authorizing.  In particular, no local
calculation grants external novelty, scientific adoption, or paper authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from itertools import combinations
from math import isfinite
from typing import Hashable, Mapping, Sequence


Number = int | float | str | Fraction


def _ordered(values: Sequence[str] | set[str]) -> tuple[str, ...]:
    return tuple(sorted({str(value) for value in values}))


def _fraction(value: Number) -> Fraction:
    if isinstance(value, Fraction):
        result = value
    elif isinstance(value, float):
        if not isfinite(value):
            raise ValueError("resource values must be finite")
        result = Fraction(str(value))
    else:
        result = Fraction(value)
    if result < 0:
        raise ValueError("resource values must be non-negative")
    return result


@dataclass(frozen=True)
class ResourceVector:
    """A named, non-negative vector cost with exact rational arithmetic."""

    values: tuple[tuple[str, Fraction], ...]

    @classmethod
    def from_mapping(cls, values: Mapping[str, Number]) -> "ResourceVector":
        if not values:
            raise ValueError("resource vector must contain at least one dimension")
        rows: list[tuple[str, Fraction]] = []
        for name, value in values.items():
            key = str(name)
            if not key:
                raise ValueError("resource dimensions must be non-empty")
            rows.append((key, _fraction(value)))
        if len({name for name, _ in rows}) != len(rows):
            raise ValueError("resource dimensions must be unique")
        return cls(tuple(sorted(rows)))

    @property
    def dimensions(self) -> tuple[str, ...]:
        return tuple(name for name, _ in self.values)

    def as_dict(self) -> dict[str, Fraction]:
        return dict(self.values)

    def _require_same_dimensions(self, other: "ResourceVector") -> None:
        if self.dimensions != other.dimensions:
            raise ValueError(
                "resource vectors require identical named dimensions: "
                f"{self.dimensions!r} != {other.dimensions!r}"
            )

    def weakly_dominates(self, other: "ResourceVector") -> bool:
        """Return True when this vector costs no more in every dimension."""

        self._require_same_dimensions(other)
        right = other.as_dict()
        return all(value <= right[name] for name, value in self.values)

    def strictly_dominates(self, other: "ResourceVector") -> bool:
        self._require_same_dimensions(other)
        return self.weakly_dominates(other) and self != other

    def add(self, other: "ResourceVector") -> "ResourceVector":
        self._require_same_dimensions(other)
        right = other.as_dict()
        return ResourceVector(
            tuple((name, value + right[name]) for name, value in self.values)
        )

    def scalar_cost(self, prices: Mapping[str, Number]) -> Fraction:
        """Compute an explicitly supplied scalarization.

        Hidden scalarization is intentionally impossible: every dimension must
        receive a non-negative price and no extra price may be supplied.
        """

        if set(prices) != set(self.dimensions):
            raise ValueError("price vector must cover exactly the resource dimensions")
        return sum(
            (value * _fraction(prices[name]) for name, value in self.values),
            start=Fraction(0),
        )


class ClosureClass(str, Enum):
    DONOR_CLOSURE = "DONOR_CLOSURE"
    FRONTIER = "FRONTIER"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ComparisonContract:
    contract_id: str
    task_ids: tuple[str, ...]
    information_contract_id: str
    resource_contract_id: str
    evaluator_id: str
    same_candidate_visible_information: bool
    same_tool_access: bool
    donor_first_refusal: bool
    frozen_before_outcomes: bool

    def verify(self) -> None:
        if not all(
            (
                self.contract_id,
                self.information_contract_id,
                self.resource_contract_id,
                self.evaluator_id,
            )
        ):
            raise ValueError("comparison contract identities must be non-empty")
        if not self.task_ids or len(set(self.task_ids)) != len(self.task_ids):
            raise ValueError("comparison task identities must be non-empty and unique")

    @property
    def matched_and_frozen(self) -> bool:
        return all(
            (
                self.same_candidate_visible_information,
                self.same_tool_access,
                self.donor_first_refusal,
                self.frozen_before_outcomes,
            )
        )


@dataclass(frozen=True)
class TaskOutcome:
    task_id: str
    closure_class: ClosureClass
    correct: bool
    scientifically_admissible: bool
    false_promotion: bool
    resources: ResourceVector
    held_out: bool = False
    counterfactual: bool = False

    @property
    def valid_success(self) -> bool:
        return self.correct and self.scientifically_admissible and not self.false_promotion


@dataclass(frozen=True)
class SystemProfile:
    system_id: str
    outcomes: Mapping[str, TaskOutcome]

    def verify(self, task_ids: Sequence[str]) -> None:
        if not self.system_id:
            raise ValueError("system profile requires a non-empty identity")
        expected = set(task_ids)
        actual = set(self.outcomes)
        if expected != actual:
            raise ValueError(
                f"system {self.system_id!r} task mismatch: "
                f"missing={sorted(expected-actual)}, extra={sorted(actual-expected)}"
            )
        for task_id, outcome in self.outcomes.items():
            if outcome.task_id != task_id:
                raise ValueError("outcome identity must match its mapping key")


@dataclass(frozen=True)
class FrontierDominanceReport:
    candidate_id: str
    donor_ids: tuple[str, ...]
    task_ids: tuple[str, ...]
    matched_contract: bool
    donor_conservativity_violations: tuple[str, ...]
    calibration_violations: tuple[str, ...]
    resource_violations: tuple[str, ...]
    strict_frontier_win_ids: tuple[str, ...]
    held_out_frontier_win_ids: tuple[str, ...]
    counterfactual_frontier_win_ids: tuple[str, ...]
    unknown_frontier_ids: tuple[str, ...]

    @property
    def donor_conservative(self) -> bool:
        return not self.donor_conservativity_violations

    @property
    def calibration_noninferior(self) -> bool:
        return not self.calibration_violations

    @property
    def resource_noninferior(self) -> bool:
        return not self.resource_violations

    @property
    def frontier_dominant(self) -> bool:
        return all(
            (
                self.matched_contract,
                self.donor_conservative,
                self.calibration_noninferior,
                self.resource_noninferior,
                bool(self.strict_frontier_win_ids),
            )
        )

    @property
    def triangulated_frontier_dominant(self) -> bool:
        return all(
            (
                self.frontier_dominant,
                bool(self.held_out_frontier_win_ids),
                bool(self.counterfactual_frontier_win_ids),
            )
        )

    @property
    def grants_external_novelty_authority(self) -> bool:
        return False

    @property
    def grants_paper_authority(self) -> bool:
        return False


def _check_task_metadata(
    candidate: SystemProfile,
    donors: Sequence[SystemProfile],
    task_ids: Sequence[str],
) -> None:
    for task_id in task_ids:
        expected = candidate.outcomes[task_id]
        for donor in donors:
            actual = donor.outcomes[task_id]
            if (
                actual.closure_class != expected.closure_class
                or actual.held_out != expected.held_out
                or actual.counterfactual != expected.counterfactual
            ):
                raise ValueError(
                    f"task metadata mismatch for {task_id!r} between candidate and donor"
                )


def assess_frontier_dominance(
    candidate: SystemProfile,
    donors: Sequence[SystemProfile],
    *,
    contract: ComparisonContract,
) -> FrontierDominanceReport:
    """Assess strong donor-envelope frontier dominance.

    The criterion is intentionally non-compensatory.  A frontier win cannot
    compensate for regression on a donor-closure task, worse false promotion,
    unmatched access, or a resource regression against every successful donor.
    """

    contract.verify()
    if not donors:
        raise ValueError("frontier dominance requires at least one registered donor")
    donor_ids = tuple(sorted(donor.system_id for donor in donors))
    if len(set(donor_ids)) != len(donor_ids):
        raise ValueError("donor identities must be unique")
    task_ids = tuple(contract.task_ids)
    candidate.verify(task_ids)
    for donor in donors:
        donor.verify(task_ids)
    _check_task_metadata(candidate, donors, task_ids)

    conservativity: list[str] = []
    calibration: list[str] = []
    resource: list[str] = []
    frontier: list[str] = []
    held_out: list[str] = []
    counterfactual: list[str] = []
    unknown: list[str] = []

    for task_id in task_ids:
        cand = candidate.outcomes[task_id]
        donor_rows = [donor.outcomes[task_id] for donor in donors]
        donor_successes = [row for row in donor_rows if row.valid_success]

        if cand.closure_class is ClosureClass.DONOR_CLOSURE and donor_successes:
            if not cand.valid_success:
                conservativity.append(task_id)
            elif not any(cand.resources.weakly_dominates(row.resources) for row in donor_successes):
                resource.append(task_id)

        # Strongest-donor calibration envelope: if any donor avoids false
        # promotion on a case, a claimed dominance result may not false-promote.
        if cand.false_promotion and any(not row.false_promotion for row in donor_rows):
            calibration.append(task_id)

        if cand.closure_class is ClosureClass.FRONTIER:
            if cand.valid_success and not donor_successes:
                frontier.append(task_id)
                if cand.held_out:
                    held_out.append(task_id)
                if cand.counterfactual:
                    counterfactual.append(task_id)
        elif cand.closure_class is ClosureClass.UNKNOWN:
            unknown.append(task_id)

    return FrontierDominanceReport(
        candidate_id=candidate.system_id,
        donor_ids=donor_ids,
        task_ids=task_ids,
        matched_contract=contract.matched_and_frozen,
        donor_conservativity_violations=tuple(conservativity),
        calibration_violations=tuple(calibration),
        resource_violations=tuple(resource),
        strict_frontier_win_ids=tuple(frontier),
        held_out_frontier_win_ids=tuple(held_out),
        counterfactual_frontier_win_ids=tuple(counterfactual),
        unknown_frontier_ids=tuple(unknown),
    )


class NoveltyLayer(str, Enum):
    QUESTION = "QUESTION"
    ONTOLOGY = "ONTOLOGY"
    REPRESENTATION = "REPRESENTATION"
    MECHANISM = "MECHANISM"
    METHOD = "METHOD"
    INSTRUMENT = "INSTRUMENT"
    VALIDATION = "VALIDATION"
    ORGANIZATION = "ORGANIZATION"


@dataclass(frozen=True)
class SemanticAtom:
    atom_id: str
    layer: NoveltyLayer
    equivalence_class_id: str

    def verify(self) -> None:
        if not self.atom_id or not self.equivalence_class_id:
            raise ValueError("semantic atoms require identity and equivalence class")


@dataclass(frozen=True)
class SemanticEdge:
    edge_id: str
    input_atom_ids: tuple[str, ...]
    output_atom_id: str
    relation_type: str
    equivalence_class_id: str

    def verify(self, atom_ids: set[str]) -> None:
        if not all((self.edge_id, self.output_atom_id, self.relation_type, self.equivalence_class_id)):
            raise ValueError("semantic edges require complete identities")
        if not self.input_atom_ids:
            raise ValueError("semantic edge requires at least one input atom")
        if not set(self.input_atom_ids).issubset(atom_ids) or self.output_atom_id not in atom_ids:
            raise ValueError("semantic edge references an unregistered atom")


@dataclass(frozen=True)
class DonorExplanation:
    donor_ids: tuple[str, ...]
    covered_atom_ids: tuple[str, ...]
    covered_edge_ids: tuple[str, ...]

    def verify(self, atom_ids: set[str], edge_ids: set[str]) -> None:
        if not self.donor_ids or any(not value for value in self.donor_ids):
            raise ValueError("donor explanation requires at least one donor identity")
        if not set(self.covered_atom_ids).issubset(atom_ids):
            raise ValueError("donor explanation covers an unregistered atom")
        if not set(self.covered_edge_ids).issubset(edge_ids):
            raise ValueError("donor explanation covers an unregistered edge")


@dataclass(frozen=True)
class ResidualFamily:
    donor_ids: tuple[str, ...]
    residual_atom_ids: tuple[str, ...]
    residual_edge_ids: tuple[str, ...]
    layer_counts: tuple[tuple[str, int], ...]

    @property
    def empty(self) -> bool:
        return not self.residual_atom_ids and not self.residual_edge_ids

    @property
    def interaction_only(self) -> bool:
        return not self.residual_atom_ids and bool(self.residual_edge_ids)


def _residual_subset(left: ResidualFamily, right: ResidualFamily) -> bool:
    return set(left.residual_atom_ids).issubset(right.residual_atom_ids) and set(
        left.residual_edge_ids
    ).issubset(right.residual_edge_ids)


def minimal_residual_families(
    atoms: Sequence[SemanticAtom],
    edges: Sequence[SemanticEdge],
    explanations: Sequence[DonorExplanation],
) -> tuple[ResidualFamily, ...]:
    """Return every inclusion-minimal semantic residual after donor absorption."""

    if not atoms:
        raise ValueError("candidate semantics require at least one atom")
    atom_by_id: dict[str, SemanticAtom] = {}
    for atom in atoms:
        atom.verify()
        if atom.atom_id in atom_by_id:
            raise ValueError("duplicate semantic atom identity")
        atom_by_id[atom.atom_id] = atom
    atom_ids = set(atom_by_id)

    edge_ids: set[str] = set()
    for edge in edges:
        edge.verify(atom_ids)
        if edge.edge_id in edge_ids:
            raise ValueError("duplicate semantic edge identity")
        edge_ids.add(edge.edge_id)

    if not explanations:
        explanations = (DonorExplanation(("NO_REGISTERED_DONOR",), (), ()),)

    rows: list[ResidualFamily] = []
    for explanation in explanations:
        explanation.verify(atom_ids, edge_ids)
        residual_atoms = tuple(sorted(atom_ids - set(explanation.covered_atom_ids)))
        residual_edges = tuple(sorted(edge_ids - set(explanation.covered_edge_ids)))
        counts: dict[str, int] = {layer.value: 0 for layer in NoveltyLayer}
        for atom_id in residual_atoms:
            counts[atom_by_id[atom_id].layer.value] += 1
        counts["INTERACTION_EDGE"] = len(residual_edges)
        rows.append(
            ResidualFamily(
                donor_ids=_ordered(explanation.donor_ids),
                residual_atom_ids=residual_atoms,
                residual_edge_ids=residual_edges,
                layer_counts=tuple(sorted(counts.items())),
            )
        )

    unique: dict[tuple[tuple[str, ...], tuple[str, ...]], ResidualFamily] = {}
    for row in rows:
        key = (row.residual_atom_ids, row.residual_edge_ids)
        previous = unique.get(key)
        if previous is None or row.donor_ids < previous.donor_ids:
            unique[key] = row
    candidates = list(unique.values())
    minimal = [
        row
        for row in candidates
        if not any(
            other != row
            and _residual_subset(other, row)
            and (
                set(other.residual_atom_ids) != set(row.residual_atom_ids)
                or set(other.residual_edge_ids) != set(row.residual_edge_ids)
            )
            for other in candidates
        )
    ]
    return tuple(
        sorted(
            minimal,
            key=lambda row: (
                len(row.residual_atom_ids) + len(row.residual_edge_ids),
                row.residual_atom_ids,
                row.residual_edge_ids,
                row.donor_ids,
            ),
        )
    )


def donor_expansion_is_residual_monotone(
    old_residuals: Sequence[ResidualFamily],
    new_residuals: Sequence[ResidualFamily],
) -> bool:
    """Check the expected non-expansion law after adding donor explanations.

    Every new minimal residual must be contained in at least one old residual.
    The function is a checker; the theorem requires that the new explanation
    family genuinely extends the old one rather than replacing it.
    """

    if not old_residuals or not new_residuals:
        raise ValueError("residual monotonicity requires non-empty families")
    return all(any(_residual_subset(new, old) for old in old_residuals) for new in new_residuals)


@dataclass(frozen=True)
class IdentifyingExperiment:
    experiment_id: str
    distinguished_pair_ids: tuple[str, ...]
    cost: ResourceVector

    def verify(self, pair_ids: set[str]) -> None:
        if not self.experiment_id:
            raise ValueError("experiment requires a non-empty identity")
        if not set(self.distinguished_pair_ids).issubset(pair_ids):
            raise ValueError("experiment distinguishes an unregistered alternative pair")


@dataclass(frozen=True)
class ExperimentPortfolio:
    experiment_ids: tuple[str, ...]
    total_cost: ResourceVector


def pareto_minimum_identifying_portfolios(
    alternative_pair_ids: Sequence[str],
    experiments: Sequence[IdentifyingExperiment],
) -> tuple[ExperimentPortfolio, ...]:
    """Enumerate exact Pareto-minimum identifying portfolios in a finite class."""

    pairs = set(_ordered(set(alternative_pair_ids)))
    if not pairs:
        raise ValueError("at least one alternative pair is required")
    if not experiments:
        raise ValueError("at least one experiment is required")
    by_id: dict[str, IdentifyingExperiment] = {}
    for experiment in experiments:
        experiment.verify(pairs)
        if experiment.experiment_id in by_id:
            raise ValueError("duplicate experiment identity")
        by_id[experiment.experiment_id] = experiment
    dimensions = next(iter(by_id.values())).cost.dimensions
    for experiment in by_id.values():
        if experiment.cost.dimensions != dimensions:
            raise ValueError("all experiment costs require identical dimensions")

    identifying: list[ExperimentPortfolio] = []
    ordered_experiments = tuple(sorted(by_id))
    for size in range(1, len(ordered_experiments) + 1):
        for subset in combinations(ordered_experiments, size):
            covered: set[str] = set()
            total: ResourceVector | None = None
            for experiment_id in subset:
                row = by_id[experiment_id]
                covered.update(row.distinguished_pair_ids)
                total = row.cost if total is None else total.add(row.cost)
            if covered == pairs and total is not None:
                identifying.append(ExperimentPortfolio(subset, total))
    if not identifying:
        return ()

    pareto: list[ExperimentPortfolio] = []
    for row in identifying:
        dominated = False
        for other in identifying:
            if other == row:
                continue
            if other.total_cost.weakly_dominates(row.total_cost) and (
                other.total_cost != row.total_cost
                or set(other.experiment_ids) < set(row.experiment_ids)
            ):
                dominated = True
                break
        if not dominated:
            pareto.append(row)
    return tuple(sorted(pareto, key=lambda row: (row.total_cost.values, row.experiment_ids)))


def select_scalarized_portfolios(
    portfolios: Sequence[ExperimentPortfolio],
    *,
    prices: Mapping[str, Number],
) -> tuple[ExperimentPortfolio, ...]:
    """Select minima only after the caller supplies an explicit price vector."""

    if not portfolios:
        return ()
    costs = [(row.total_cost.scalar_cost(prices), row) for row in portfolios]
    minimum = min(cost for cost, _ in costs)
    return tuple(row for cost, row in costs if cost == minimum)


def minimal_superiority_destroying_mutations(
    strict_frontier_win_ids: Sequence[str],
    surviving_win_ids_by_removed_atom_set: Mapping[tuple[str, ...], Sequence[str]],
) -> tuple[tuple[str, ...], ...]:
    """Return inclusion-minimal residual-atom deletions destroying all frontier wins.

    The caller supplies independently executed deletion mutations.  A row maps
    the exact removed atom set to the strict-frontier wins that still survive.
    This function does not infer causal necessity from the unmutated candidate.
    """

    wins = set(_ordered(set(strict_frontier_win_ids)))
    if not wins:
        raise ValueError("at least one strict frontier win is required")
    destructive: set[frozenset[str]] = set()
    for removed_raw, surviving_raw in surviving_win_ids_by_removed_atom_set.items():
        removed = frozenset(str(value) for value in removed_raw)
        if not removed or any(not value for value in removed):
            raise ValueError("mutation atom identities must be non-empty")
        surviving = set(str(value) for value in surviving_raw)
        if not surviving.issubset(wins):
            raise ValueError("mutation reports an unregistered frontier win")
        if not surviving:
            destructive.add(removed)
    minimal = [row for row in destructive if not any(other < row for other in destructive)]
    return tuple(sorted((tuple(sorted(row)) for row in minimal), key=lambda row: (len(row), row)))


def fair_dovetail_schedule(
    generator_ids: Sequence[str], *, max_stage: int
) -> tuple[tuple[str, int], ...]:
    """Return the diagonal fair schedule over generator/program-index pairs.

    At stage ``s`` every pair ``(generator_index, program_index)`` with sum
    ``s`` is scheduled.  Consequently every finite pair appears by a finite
    stage.  This is relative completeness of scheduling, not a guarantee that
    the generator language contains a useful discovery.
    """

    generators = tuple(str(value) for value in generator_ids)
    if not generators or any(not value for value in generators):
        raise ValueError("generator identities must be non-empty")
    if len(set(generators)) != len(generators):
        raise ValueError("generator identities must be unique")
    if max_stage <= 0:
        raise ValueError("max_stage must be positive")
    rows: list[tuple[str, int]] = []
    for stage in range(max_stage):
        for generator_index in range(min(stage, len(generators) - 1) + 1):
            program_index = stage - generator_index
            rows.append((generators[generator_index], program_index))
    return tuple(rows)


__all__ = [
    "ClosureClass",
    "ComparisonContract",
    "DonorExplanation",
    "ExperimentPortfolio",
    "FrontierDominanceReport",
    "IdentifyingExperiment",
    "NoveltyLayer",
    "ResidualFamily",
    "ResourceVector",
    "SemanticAtom",
    "SemanticEdge",
    "SystemProfile",
    "TaskOutcome",
    "assess_frontier_dominance",
    "donor_expansion_is_residual_monotone",
    "fair_dovetail_schedule",
    "minimal_residual_families",
    "minimal_superiority_destroying_mutations",
    "pareto_minimum_identifying_portfolios",
    "select_scalarized_portfolios",
]
