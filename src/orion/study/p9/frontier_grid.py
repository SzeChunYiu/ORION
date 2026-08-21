"""The prospective S*(k,q) / C*(k,q) frontier grid for P9-U-T3.

``P9-U-T3`` asks that a scale/compute crossing be *on-grid and prospectively
defined*. Its ledger blocker says the grid "is not prospectively defined, so a
crossing could not be shown to be on-grid rather than fitted", and its unblock
says to "freeze the relational-complexity x representation x model-scale x
inference-budget grid before outcomes, and preserve any null cell rather than
fitting an exponent post hoc".

This module is that grid, plus the estimator and crossing rule that read a
frontier off it. It is deliberately written while **no cell has an outcome**:
that is what makes the definition a prediction. A grid written after a crossing
is visible is a drawing of the crossing.

Protocol: ``papers/paper-09-structured-epistemic-learning/protocol/
P9_U_T3_FRONTIER_GRID_FREEZE_2026-08-21.md`` and its JSON twin. The runner
recomputes the twin's parameter digest from its own constants and refuses to run
on a mismatch.

The verdict is three-valued (:class:`orion.programme.records.Outcome`), and the
state it returns today is ``CANNOT_CHECK`` with the denominator printed: 0 of
1344 declared cells have been executed. No open-weight checkpoint is present in
this repository and this environment's proxy refuses outbound ``CONNECT`` to
external providers, so the grid cannot be executed here. Substituting a
classical-learner capacity ladder for a model-scale ladder would be a weaker
proxy wearing the name ``S*``; this module refuses to do that and says so.

Two vacuity rules are in the type rather than beside it:

* a cell missing from an outcome file makes the whole grid ``CANNOT_CHECK`` --
  silent absence is exactly how a null cell gets dropped;
* a fully executed grid in which no crossing test had two uncensored frontiers
  is ``CANNOT_CHECK``, not ``PASS``. A crossing rate over an empty set of
  evaluable tests is ``n/0``.

Run it::

    python -m orion.study.p9.frontier_grid --repo-root . --output <result>.json
    python -m orion.study.p9.frontier_grid --repo-root . --outcomes <cells>.json
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scipy.stats import fisher_exact

from orion.programme.records import Outcome
from orion.study.p1_causal.necessity_statistics import holm_many
from orion.transfer.v2.canonical import content_digest

RESULT_SCHEMA_VERSION = "orion.p9.ut3-frontier-grid-status.v1"
OUTCOME_SCHEMA_VERSION = "P9.UT3FrontierGridOutcomes.v1"

FREEZE_DOCUMENT = (
    "papers/paper-09-structured-epistemic-learning/protocol/"
    "P9_U_T3_FRONTIER_GRID_FREEZE_2026-08-21.md"
)
FREEZE_TWIN = (
    "papers/paper-09-structured-epistemic-learning/protocol/"
    "P9_U_T3_FRONTIER_GRID_FREEZE_2026-08-21.json"
)

GATE_SERVED = "P9-U-T3"

CLAIM_SCOPE = (
    "DECLARATION_ONLY. This module defines a grid and the rules for reading S* and C* off it. "
    "It executes no cell, and no result over it licenses any statement about a crossing until "
    "cells carry outcomes."
)

# ---------------------------------------------------------------------------
# Axes. Every level below is frozen by the protocol document.
# ---------------------------------------------------------------------------

#: Relational complexity: the number of comparison coordinates that must be
#: jointly examined to decide an instance's label.
K_LEVELS: tuple[int, ...] = (1, 2, 4, 8)

REPRESENTATIONS: tuple[str, ...] = (
    "FLAT_TEXT_SERIALIZATION",
    "REVERSIBLE_INDEXED_SERIALIZATION",
    "TYPED_TUPLE_SET",
    "TYPED_GRAPH_STATE",
    "QUERY_MATCHED_INTERFACE",
    "LENGTH_ONLY_CONTROL",
    "ARCHITECTURE_PRIOR_CONTROL",
)

#: Model family -> its scale ladder, ascending. ``S*`` may only take a value on
#: its family's ladder; there is no interpolation between ladder points.
SCALE_LADDERS: Mapping[str, tuple[str, ...]] = {
    "QWEN2_5": ("0.5B", "1.5B", "3B", "7B"),
    "LLAMA3_2": ("1B", "3B"),
}

#: Inference budget in sampled decodes per instance, aggregated by majority vote.
INFERENCE_BUDGETS: tuple[int, ...] = (1, 4, 16, 64)

DOMAIN_BLOCKS: tuple[str, ...] = ("FORMAL_RELATIONAL", "NON_FORMAL_PROCEDURAL")

#: Verified quality targets at which a frontier is read. Not a cell axis.
Q_TARGETS: tuple[float, ...] = (0.70, 0.85, 0.95)

#: The sample budget is held fixed. ``N*`` is explicitly out of scope for T3.
FIXED_SAMPLE_BUDGET = 4

CELL_KEY_FORMAT = "k{k}|{representation}|{family}|{scale}|C{budget}|{block}"

CELL_STATUSES: tuple[str, ...] = (
    "EXECUTED",
    "NOT_RUN",
    "INFEASIBLE_RESOURCE",
    "INFEASIBLE_CONTEXT",
)

RIGHT_CENSORED = "RIGHT_CENSORED"

HOLM_ALPHA = 0.05

#: Cap on how many crossings are written into a result file. The census counts
#: are complete; only the per-crossing detail is truncated.
CROSSING_REPORT_LIMIT = 64

EXPONENT_RULE = (
    "OLS of log(1 - Q) on log(S) within one (k, R, F, C, B) series with at least 3 EXECUTED "
    "points, reported with residual standard deviation and R-squared, as a secondary description "
    "only. It may never define S*, fill a censored frontier, or declare a crossing."
)

VERDICT_NO_CELL_EXECUTED = "T3_GRID_DECLARED_NO_CELL_EXECUTED"
VERDICT_GRID_INCOMPLETE = "T3_GRID_INCOMPLETE"
VERDICT_NO_EVALUABLE_TEST = "T3_NO_EVALUABLE_CROSSING_TEST"
VERDICT_OFF_GRID = "T3_OFF_GRID_CROSSING_CLAIMED"
VERDICT_ON_GRID = "T3_CROSSINGS_ON_GRID"

ENVIRONMENT_BOUNDARY = {
    "open_weight_checkpoint_present": False,
    "outbound_provider_access": "proxy returns 403 to CONNECT for external providers",
    "grid_executable_here": False,
    "surrogate_refused": (
        "a classical-learner capacity ladder is not a model-scale ladder; naming one S* would be "
        "a weaker proxy presented as the measurement"
    ),
}

TERMINAL_DISPOSITION = (
    "P9-U-T3 remains BLOCKED. This freeze removes only the first half of its blocker -- the grid "
    "now exists and exists before any outcome. The gate also requires a crossing that is on-grid, "
    "which requires cells with outcomes, of which there are none."
)


def declared_cells() -> tuple[str, ...]:
    """Every cell key of the frozen grid, in a deterministic order."""

    keys: list[str] = []
    for k in K_LEVELS:
        for representation in REPRESENTATIONS:
            for family in sorted(SCALE_LADDERS):
                for scale in SCALE_LADDERS[family]:
                    for budget in INFERENCE_BUDGETS:
                        for block in DOMAIN_BLOCKS:
                            keys.append(
                                CELL_KEY_FORMAT.format(
                                    k=k,
                                    representation=representation,
                                    family=family,
                                    scale=scale,
                                    budget=budget,
                                    block=block,
                                )
                            )
    return tuple(keys)


DECLARED_CELL_COUNT = (
    len(K_LEVELS)
    * len(REPRESENTATIONS)
    * sum(len(ladder) for ladder in SCALE_LADDERS.values())
    * len(INFERENCE_BUDGETS)
    * len(DOMAIN_BLOCKS)
)


FROZEN_PARAMETERS: dict[str, Any] = {
    "record": "P9_U_T3_FRONTIER_GRID_FREEZE",
    "freeze_document": FREEZE_DOCUMENT,
    "gate_served": GATE_SERVED,
    "claim_scope": CLAIM_SCOPE,
    "axes": {
        "k_relational_complexity": list(K_LEVELS),
        "representations": list(REPRESENTATIONS),
        "scale_ladders": {family: list(ladder) for family, ladder in sorted(SCALE_LADDERS.items())},
        "inference_budgets": list(INFERENCE_BUDGETS),
        "domain_blocks": list(DOMAIN_BLOCKS),
        "quality_targets": list(Q_TARGETS),
        "fixed_sample_budget": FIXED_SAMPLE_BUDGET,
        "sample_budget_frontier_in_scope": False,
    },
    "cell_key_format": CELL_KEY_FORMAT,
    "cell_statuses": list(CELL_STATUSES),
    "declared_cell_count": DECLARED_CELL_COUNT,
    "estimators": {
        "scale_frontier": "min ladder point with Q >= q, else RIGHT_CENSORED",
        "compute_frontier": "min inference budget with Q >= q, else RIGHT_CENSORED",
        "on_grid_rule": "a frontier value must be a declared ladder point whose cell status is EXECUTED",
        "interpolation_permitted": False,
        "extrapolation_permitted": False,
        "non_monotone_policy": "flag NON_MONOTONE, report the first crossing point, never smooth",
    },
    "crossing_rule": {
        "requires_both_frontiers_on_grid": True,
        "test": "Fisher exact two-sided on paired per-instance verified counts at the comparator frontier",
        "multiplicity": "Holm-Bonferroni over every crossing test evaluated",
        "alpha": HOLM_ALPHA,
        "null_cells_preserved": True,
        "missing_cell_policy": "any declared cell absent from the outcome file makes the grid CANNOT_CHECK",
    },
    "exponent_rule": EXPONENT_RULE,
    "quality_source": "Q = n_verified_correct / n_items, computed by the runner, never read from the file",
    "verdicts": {
        "no_cell_executed": VERDICT_NO_CELL_EXECUTED,
        "grid_incomplete": VERDICT_GRID_INCOMPLETE,
        "no_evaluable_crossing_test": VERDICT_NO_EVALUABLE_TEST,
        "off_grid": VERDICT_OFF_GRID,
        "on_grid": VERDICT_ON_GRID,
    },
    "outcome_schema": OUTCOME_SCHEMA_VERSION,
}


def frozen_digest() -> str:
    return content_digest(FROZEN_PARAMETERS)


class FreezeViolation(RuntimeError):
    """Raised when the runner's constants no longer match the frozen record."""


def verify_against_twin(repo_root: Path) -> dict[str, Any]:
    """Compare the runner's own parameter digest with the frozen twin's."""

    twin_path = repo_root / FREEZE_TWIN
    if not twin_path.exists():
        raise FreezeViolation(f"freeze twin missing: {twin_path}")
    twin = json.loads(twin_path.read_text(encoding="utf-8"))
    recorded = twin.get("parameters_sha256")
    computed = frozen_digest()
    if recorded != computed:
        raise FreezeViolation(
            "runner parameters do not match the frozen record: "
            f"recorded {recorded}, computed {computed}"
        )
    return {"parameters_sha256": computed, "freeze_twin": FREEZE_TWIN}


# ---------------------------------------------------------------------------
# Cell outcomes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CellOutcome:
    """One grid cell's outcome.

    ``quality`` is a property computed from the counts rather than a stored
    field: a cell that reports a quality it did not compute from its own
    denominator is exactly the number this programme keeps finding.
    """

    key: str
    status: str
    n_items: int | None
    n_verified_correct: int | None

    def __post_init__(self) -> None:
        if self.status not in CELL_STATUSES:
            raise ValueError(f"{self.key}: unknown cell status {self.status!r}")
        if self.status == "EXECUTED":
            if self.n_items is None or self.n_verified_correct is None:
                raise ValueError(f"{self.key}: an EXECUTED cell must carry its counts")
            if self.n_items <= 0:
                raise ValueError(f"{self.key}: an EXECUTED cell must have a positive denominator")
            if not 0 <= self.n_verified_correct <= self.n_items:
                raise ValueError(f"{self.key}: verified count outside its denominator")
        elif self.n_items is not None or self.n_verified_correct is not None:
            raise ValueError(
                f"{self.key}: a {self.status} cell must omit counts; a number attached to a cell "
                "that did not run is the failure this contract exists to prevent"
            )

    @property
    def executed(self) -> bool:
        return self.status == "EXECUTED"

    @property
    def quality(self) -> float | None:
        """``Q`` for this cell, or ``None`` when the cell did not run."""

        if not self.executed:
            return None
        assert self.n_items is not None and self.n_verified_correct is not None
        return self.n_verified_correct / self.n_items

    def as_json(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "status": self.status,
            "n_items": self.n_items,
            "n_verified_correct": self.n_verified_correct,
            "quality": self.quality,
        }


class OutcomeFileError(ValueError):
    """Raised when an outcome file does not satisfy the frozen contract."""


@dataclass(frozen=True)
class ClaimedCrossing:
    """A crossing an experimenter asserts, to be checked against the ladder.

    The runner never invents an off-grid crossing, so a check that only looked at
    the runner's own readings could never fail. This type is the denominator of
    the off-grid check: the crossings a result *claims*, which the runner then
    re-reads from the executed cells.
    """

    axis: str
    target: float
    k: int
    family: str
    budget: int
    block: str
    faster: str
    slower: str
    scale: str | None = None

    def as_json(self) -> dict[str, Any]:
        return {
            "axis": self.axis,
            "target": self.target,
            "k": self.k,
            "family": self.family,
            "budget": self.budget,
            "block": self.block,
            "faster": self.faster,
            "slower": self.slower,
            "scale": self.scale,
        }


def load_outcomes(path: Path) -> tuple[dict[str, CellOutcome], tuple[ClaimedCrossing, ...]]:
    """Read an outcome file, checking its schema and its parameter digest."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != OUTCOME_SCHEMA_VERSION:
        raise OutcomeFileError(
            f"{path}: expected schema {OUTCOME_SCHEMA_VERSION}, got {payload.get('schema')!r}"
        )
    recorded = payload.get("parameters_sha256")
    if recorded != frozen_digest():
        raise OutcomeFileError(
            f"{path}: outcome file was produced against a different grid "
            f"({recorded} vs {frozen_digest()})"
        )
    cells = payload.get("cells")
    if not isinstance(cells, Mapping):
        raise OutcomeFileError(f"{path}: 'cells' must be an object")
    out: dict[str, CellOutcome] = {}
    for key, value in cells.items():
        if not isinstance(value, Mapping):
            raise OutcomeFileError(f"{path}: cell {key!r} is not an object")
        out[str(key)] = CellOutcome(
            key=str(key),
            status=str(value.get("status")),
            n_items=value.get("n_items"),
            n_verified_correct=value.get("n_verified_correct"),
        )

    raw_claims = payload.get("claimed_crossings", [])
    if not isinstance(raw_claims, Sequence) or isinstance(raw_claims, (str, bytes)):
        raise OutcomeFileError(f"{path}: 'claimed_crossings' must be an array")
    claims: list[ClaimedCrossing] = []
    for item in raw_claims:
        if not isinstance(item, Mapping):
            raise OutcomeFileError(f"{path}: every claimed crossing must be an object")
        claims.append(
            ClaimedCrossing(
                axis=str(item.get("axis", "S")),
                target=float(item["target"]),
                k=int(item["k"]),
                family=str(item["family"]),
                budget=int(item.get("budget", INFERENCE_BUDGETS[0])),
                block=str(item["block"]),
                faster=str(item["faster"]),
                slower=str(item["slower"]),
                scale=None if item.get("scale") is None else str(item["scale"]),
            )
        )
    return out, tuple(claims)


def cell_key(
    *, k: int, representation: str, family: str, scale: str, budget: int, block: str
) -> str:
    return CELL_KEY_FORMAT.format(
        k=k,
        representation=representation,
        family=family,
        scale=scale,
        budget=budget,
        block=block,
    )


# ---------------------------------------------------------------------------
# Frontiers
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Frontier:
    """One ``S*`` or ``C*`` reading, with the series it was read from."""

    axis: str
    series_id: str
    target: float
    value: str
    on_grid: bool
    non_monotone: bool
    series: tuple[tuple[str, float | None, str], ...]

    def as_json(self) -> dict[str, Any]:
        return {
            "axis": self.axis,
            "series_id": self.series_id,
            "target": self.target,
            "value": self.value,
            "on_grid": self.on_grid,
            "non_monotone": self.non_monotone,
            "series": [
                {"point": point, "quality": quality, "status": status}
                for point, quality, status in self.series
            ],
        }


def read_frontier(
    *,
    axis: str,
    series_id: str,
    ladder: Sequence[str],
    outcomes: Mapping[str, CellOutcome],
    keys: Sequence[str],
    target: float,
) -> Frontier:
    """Read the first ladder point reaching ``target``, or ``RIGHT_CENSORED``.

    No interpolation and no fitted form: the frontier is a ladder point that was
    executed, or it does not exist.
    """

    if len(ladder) != len(keys):
        raise ValueError(f"{series_id}: {len(keys)} keys for a ladder of {len(ladder)}")
    series: list[tuple[str, float | None, str]] = []
    first_reaching: str | None = None
    for point, key in zip(ladder, keys, strict=True):
        outcome = outcomes.get(key)
        if outcome is None:
            series.append((point, None, "MISSING"))
            continue
        series.append((point, outcome.quality, outcome.status))
        quality = outcome.quality
        if quality is not None and quality >= target and first_reaching is None:
            first_reaching = point
    non_monotone = False
    if first_reaching is not None:
        seen = False
        for point, quality, _status in series:
            if point == first_reaching:
                seen = True
                continue
            if seen and quality is not None and quality < target:
                non_monotone = True
    value = first_reaching if first_reaching is not None else RIGHT_CENSORED
    return Frontier(
        axis=axis,
        series_id=series_id,
        target=target,
        value=value,
        on_grid=first_reaching is not None,
        non_monotone=non_monotone,
        series=tuple(series),
    )


def scale_frontier(
    outcomes: Mapping[str, CellOutcome],
    *,
    k: int,
    representation: str,
    family: str,
    budget: int,
    block: str,
    target: float,
) -> Frontier:
    ladder = SCALE_LADDERS[family]
    keys = [
        cell_key(
            k=k,
            representation=representation,
            family=family,
            scale=scale,
            budget=budget,
            block=block,
        )
        for scale in ladder
    ]
    return read_frontier(
        axis="S",
        series_id=f"S*|k{k}|{representation}|{family}|C{budget}|{block}",
        ladder=ladder,
        outcomes=outcomes,
        keys=keys,
        target=target,
    )


def compute_frontier(
    outcomes: Mapping[str, CellOutcome],
    *,
    k: int,
    representation: str,
    family: str,
    scale: str,
    block: str,
    target: float,
) -> Frontier:
    ladder = tuple(str(budget) for budget in INFERENCE_BUDGETS)
    keys = [
        cell_key(
            k=k,
            representation=representation,
            family=family,
            scale=scale,
            budget=budget,
            block=block,
        )
        for budget in INFERENCE_BUDGETS
    ]
    return read_frontier(
        axis="C",
        series_id=f"C*|k{k}|{representation}|{family}|{scale}|{block}",
        ladder=ladder,
        outcomes=outcomes,
        keys=keys,
        target=target,
    )


# ---------------------------------------------------------------------------
# Crossings
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CrossingTest:
    """One ordered representation pair tested for a frontier crossing."""

    axis: str
    context: str
    target: float
    faster: str
    slower: str
    faster_frontier: Frontier
    slower_frontier: Frontier
    evaluable: bool
    crossed: bool
    p_value: float | None
    detail: str

    def as_json(self) -> dict[str, Any]:
        return {
            "axis": self.axis,
            "context": self.context,
            "target": self.target,
            "faster": self.faster,
            "slower": self.slower,
            "evaluable": self.evaluable,
            "crossed": self.crossed,
            "p_value": self.p_value,
            "detail": self.detail,
            "faster_frontier": self.faster_frontier.as_json(),
            "slower_frontier": self.slower_frontier.as_json(),
        }


def _ladder_index(axis: str, family: str, value: str) -> int:
    ladder = (
        SCALE_LADDERS[family] if axis == "S" else tuple(str(b) for b in INFERENCE_BUDGETS)
    )
    return ladder.index(value)


def evaluate_crossing(
    *,
    axis: str,
    context: str,
    family: str,
    target: float,
    faster: str,
    slower: str,
    faster_frontier: Frontier,
    slower_frontier: Frontier,
    outcomes: Mapping[str, CellOutcome],
    comparison_keys: tuple[str, str] | None,
) -> CrossingTest:
    """Decide whether ``faster`` crosses ``slower``, with the denominator stated.

    A test is *evaluable* only when both frontiers are on-grid. Anything else is
    ``NO_CROSSING_DETECTABLE`` and is preserved as a null result rather than
    dropped: a crossing rate computed only over pairs where a crossing happened
    to be readable is a statistic about which cells were readable.
    """

    if not (faster_frontier.on_grid and slower_frontier.on_grid):
        return CrossingTest(
            axis=axis,
            context=context,
            target=target,
            faster=faster,
            slower=slower,
            faster_frontier=faster_frontier,
            slower_frontier=slower_frontier,
            evaluable=False,
            crossed=False,
            p_value=None,
            detail=(
                "NO_CROSSING_DETECTABLE: "
                f"{faster} frontier {faster_frontier.value}, {slower} frontier "
                f"{slower_frontier.value}; a censored frontier is not a frontier"
            ),
        )
    faster_index = _ladder_index(axis, family, faster_frontier.value)
    slower_index = _ladder_index(axis, family, slower_frontier.value)
    if faster_index >= slower_index:
        return CrossingTest(
            axis=axis,
            context=context,
            target=target,
            faster=faster,
            slower=slower,
            faster_frontier=faster_frontier,
            slower_frontier=slower_frontier,
            evaluable=True,
            crossed=False,
            p_value=None,
            detail=(
                f"no crossing: {faster} reaches the target at {faster_frontier.value}, "
                f"{slower} at {slower_frontier.value}"
            ),
        )
    p_value: float | None = None
    if comparison_keys is not None:
        left = outcomes.get(comparison_keys[0])
        right = outcomes.get(comparison_keys[1])
        if left is not None and right is not None and left.executed and right.executed:
            assert left.n_items is not None and left.n_verified_correct is not None
            assert right.n_items is not None and right.n_verified_correct is not None
            table = [
                [left.n_verified_correct, left.n_items - left.n_verified_correct],
                [right.n_verified_correct, right.n_items - right.n_verified_correct],
            ]
            p_value = float(fisher_exact(table, alternative="two-sided")[1])
    return CrossingTest(
        axis=axis,
        context=context,
        target=target,
        faster=faster,
        slower=slower,
        faster_frontier=faster_frontier,
        slower_frontier=slower_frontier,
        evaluable=True,
        crossed=True,
        p_value=p_value,
        detail=(
            f"crossing: {faster} reaches the target at {faster_frontier.value}, "
            f"{slower} only at {slower_frontier.value}"
        ),
    )


def apply_holm(tests: Sequence[CrossingTest]) -> dict[str, Any]:
    """Holm-Bonferroni over every crossing test that produced a p-value."""

    indexed = [(index, test) for index, test in enumerate(tests) if test.p_value is not None]
    if not indexed:
        return {
            "family_size": 0,
            "alpha": HOLM_ALPHA,
            "significant": [],
            "note": (
                "no crossing test produced a p-value; there is no family to correct and no "
                "significance claim is available"
            ),
        }
    holm = holm_many([test.p_value for _index, test in indexed], alpha=HOLM_ALPHA)
    passed = holm["passes_by_input"]
    assert isinstance(passed, list)
    return {
        "family_size": len(indexed),
        "alpha": HOLM_ALPHA,
        "significant": [
            tests[index].context
            for (index, _test), ok in zip(indexed, passed, strict=True)
            if ok
        ],
        "holm": holm,
    }


# ---------------------------------------------------------------------------
# Assessment
# ---------------------------------------------------------------------------


def audit_claimed_crossings(
    claims: Sequence[ClaimedCrossing], outcomes: Mapping[str, CellOutcome]
) -> dict[str, Any]:
    """Re-read every crossing a result claims, off the executed ladder points.

    The denominator is the number of crossings claimed. It is reported whether it
    is zero or not: an off-grid check over an empty claim set has not held, it has
    not been exercised, and this function says which.
    """

    rows: list[dict[str, Any]] = []
    for claim in claims:
        if claim.axis == "S":
            frontier_faster = scale_frontier(
                outcomes,
                k=claim.k,
                representation=claim.faster,
                family=claim.family,
                budget=claim.budget,
                block=claim.block,
                target=claim.target,
            )
            frontier_slower = scale_frontier(
                outcomes,
                k=claim.k,
                representation=claim.slower,
                family=claim.family,
                budget=claim.budget,
                block=claim.block,
                target=claim.target,
            )
        elif claim.axis == "C":
            if claim.scale is None:
                rows.append(
                    {
                        "claim": claim.as_json(),
                        "on_grid": False,
                        "reason": "a C* claim must name the scale it was read at",
                    }
                )
                continue
            frontier_faster = compute_frontier(
                outcomes,
                k=claim.k,
                representation=claim.faster,
                family=claim.family,
                scale=claim.scale,
                block=claim.block,
                target=claim.target,
            )
            frontier_slower = compute_frontier(
                outcomes,
                k=claim.k,
                representation=claim.slower,
                family=claim.family,
                scale=claim.scale,
                block=claim.block,
                target=claim.target,
            )
        else:
            rows.append(
                {
                    "claim": claim.as_json(),
                    "on_grid": False,
                    "reason": f"unknown frontier axis {claim.axis!r}",
                }
            )
            continue

        if not (frontier_faster.on_grid and frontier_slower.on_grid):
            rows.append(
                {
                    "claim": claim.as_json(),
                    "on_grid": False,
                    "reason": (
                        f"{claim.faster} frontier {frontier_faster.value}, {claim.slower} "
                        f"frontier {frontier_slower.value}; a censored frontier cannot carry a "
                        "crossing, and filling it would be a fitted value"
                    ),
                    "faster_frontier": frontier_faster.as_json(),
                    "slower_frontier": frontier_slower.as_json(),
                }
            )
            continue

        faster_index = _ladder_index(claim.axis, claim.family, frontier_faster.value)
        slower_index = _ladder_index(claim.axis, claim.family, frontier_slower.value)
        if faster_index >= slower_index:
            rows.append(
                {
                    "claim": claim.as_json(),
                    "on_grid": False,
                    "reason": (
                        f"the ladder does not carry this crossing: {claim.faster} reaches the "
                        f"target at {frontier_faster.value} and {claim.slower} at "
                        f"{frontier_slower.value}"
                    ),
                    "faster_frontier": frontier_faster.as_json(),
                    "slower_frontier": frontier_slower.as_json(),
                }
            )
            continue

        rows.append(
            {
                "claim": claim.as_json(),
                "on_grid": True,
                "reason": (
                    f"read at declared, executed ladder points {frontier_faster.value} < "
                    f"{frontier_slower.value}"
                ),
                "faster_frontier": frontier_faster.as_json(),
                "slower_frontier": frontier_slower.as_json(),
            }
        )

    off_grid = [row for row in rows if not row["on_grid"]]
    return {
        "claims_checked": len(rows),
        "claims_off_grid": len(off_grid),
        "exercised": bool(rows),
        "note": (
            "no crossing was claimed, so the off-grid check had no opportunity to fire; that is "
            "CANNOT_CHECK for this check, not a pass"
            if not rows
            else f"{len(rows) - len(off_grid)} of {len(rows)} claimed crossings are on-grid"
        ),
        "rows": rows,
    }


def assess_grid(
    outcomes: Mapping[str, CellOutcome],
    claimed_crossings: Sequence[ClaimedCrossing] = (),
) -> dict[str, Any]:
    """Score the frozen grid against an outcome map. Three-valued."""

    declared = declared_cells()
    declared_set = set(declared)
    present = {key: value for key, value in outcomes.items() if key in declared_set}
    missing = sorted(declared_set - set(present))
    undeclared = sorted(set(outcomes) - declared_set)
    executed = sorted(key for key, value in present.items() if value.executed)

    census = {
        "declared_cells": len(declared),
        "cells_with_an_outcome": len(present),
        "cells_missing_from_outcome_file": len(missing),
        "cells_executed": len(executed),
        "undeclared_cells_in_outcome_file": len(undeclared),
        "status_counts": {
            status: sum(1 for value in present.values() if value.status == status)
            for status in CELL_STATUSES
        },
    }

    payload: dict[str, Any] = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "record": "P9_U_T3_FRONTIER_GRID_STATUS",
        "gate_served": GATE_SERVED,
        "freeze_document": FREEZE_DOCUMENT,
        "parameters_sha256": frozen_digest(),
        "claim_scope": CLAIM_SCOPE,
        "environment_boundary": dict(ENVIRONMENT_BOUNDARY),
        "terminal_disposition": TERMINAL_DISPOSITION,
        "census": census,
        "sample_of_declared_cells": list(declared[:8]),
    }

    if undeclared:
        payload["undeclared_cells"] = undeclared[:32]

    if not executed:
        payload["verdict"] = VERDICT_NO_CELL_EXECUTED
        payload["outcome"] = Outcome.CANNOT_CHECK.value
        payload["detail"] = (
            f"0 of {len(declared)} declared cells have been executed, so there is no surface to "
            "read a frontier off. The grid is defined and its definition precedes every outcome, "
            "which is what P9-U-T3 asks of the definition; the gate itself needs the cells."
        )
        payload["crossing_census"] = {
            "tests_declared": 0,
            "tests_evaluable": 0,
            "crossings_found": 0,
        }
        payload["crossings_found"] = []
        payload["claimed_crossing_audit"] = audit_claimed_crossings(claimed_crossings, present)
        return payload

    if missing:
        payload["verdict"] = VERDICT_GRID_INCOMPLETE
        payload["outcome"] = Outcome.CANNOT_CHECK.value
        payload["missing_cells"] = missing[:32]
        payload["detail"] = (
            f"{len(missing)} of {len(declared)} declared cells are absent from the outcome file. "
            "A cell that is silently absent is a null cell that has been dropped, and the grid "
            "cannot be scored while any is."
        )
        payload["crossing_census"] = {
            "tests_declared": 0,
            "tests_evaluable": 0,
            "crossings_found": 0,
        }
        payload["crossings_found"] = []
        payload["claimed_crossing_audit"] = audit_claimed_crossings(claimed_crossings, present)
        return payload

    frontiers: list[Frontier] = []
    tests: list[CrossingTest] = []
    for target in Q_TARGETS:
        for k in K_LEVELS:
            for block in DOMAIN_BLOCKS:
                for family in sorted(SCALE_LADDERS):
                    for budget in INFERENCE_BUDGETS:
                        read = {
                            representation: scale_frontier(
                                present,
                                k=k,
                                representation=representation,
                                family=family,
                                budget=budget,
                                block=block,
                                target=target,
                            )
                            for representation in REPRESENTATIONS
                        }
                        frontiers.extend(read.values())
                        for faster in REPRESENTATIONS:
                            for slower in REPRESENTATIONS:
                                if faster == slower:
                                    continue
                                slower_frontier = read[slower]
                                comparison_keys = None
                                if slower_frontier.on_grid:
                                    comparison_keys = (
                                        cell_key(
                                            k=k,
                                            representation=faster,
                                            family=family,
                                            scale=slower_frontier.value,
                                            budget=budget,
                                            block=block,
                                        ),
                                        cell_key(
                                            k=k,
                                            representation=slower,
                                            family=family,
                                            scale=slower_frontier.value,
                                            budget=budget,
                                            block=block,
                                        ),
                                    )
                                tests.append(
                                    evaluate_crossing(
                                        axis="S",
                                        context=(
                                            f"S*|q{target}|k{k}|{family}|C{budget}|{block}|"
                                            f"{faster}>{slower}"
                                        ),
                                        family=family,
                                        target=target,
                                        faster=faster,
                                        slower=slower,
                                        faster_frontier=read[faster],
                                        slower_frontier=slower_frontier,
                                        outcomes=present,
                                        comparison_keys=comparison_keys,
                                    )
                                )

    evaluable = [test for test in tests if test.evaluable]
    crossed = [test for test in evaluable if test.crossed]

    payload["crossings_found"] = [item.as_json() for item in crossed[:CROSSING_REPORT_LIMIT]]
    payload["crossing_census"] = {
        "tests_declared": len(tests),
        "tests_evaluable": len(evaluable),
        "tests_not_evaluable_censored_frontier": len(tests) - len(evaluable),
        "crossings_found": len(crossed),
        "frontiers_read": len(frontiers),
        "frontiers_right_censored": sum(1 for item in frontiers if not item.on_grid),
        "non_monotone_series": sum(1 for item in frontiers if item.non_monotone),
        "crossings_reported_in_this_file": min(len(crossed), CROSSING_REPORT_LIMIT),
    }
    payload["multiplicity"] = apply_holm(tests)
    audit = audit_claimed_crossings(claimed_crossings, present)
    payload["claimed_crossing_audit"] = audit

    if audit["claims_off_grid"]:
        payload["verdict"] = VERDICT_OFF_GRID
        payload["outcome"] = Outcome.FAIL.value
        payload["detail"] = (
            f"{audit['claims_off_grid']} of {audit['claims_checked']} claimed crossings do not "
            "rest on two declared, executed ladder points"
        )
        return payload

    if not evaluable:
        payload["verdict"] = VERDICT_NO_EVALUABLE_TEST
        payload["outcome"] = Outcome.CANNOT_CHECK.value
        payload["detail"] = (
            f"every declared cell is accounted for, but 0 of {len(tests)} crossing tests had two "
            "uncensored frontiers. A crossing rate over zero evaluable tests is n/0."
        )
        return payload

    payload["verdict"] = VERDICT_ON_GRID
    payload["outcome"] = Outcome.PASS.value
    payload["detail"] = (
        f"{len(crossed)} crossings over {len(evaluable)} evaluable tests, every frontier read at a "
        "declared, executed ladder point. A crossing count of zero is a result, not a failure. "
        f"The off-grid check saw {audit['claims_checked']} claimed crossings."
    )
    return payload


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Declare and score the P9-U-T3 prospective S*/C* frontier grid."
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--outcomes",
        type=Path,
        help="an outcome file for the declared cells; omit while none exists",
    )
    parser.add_argument(
        "--print-digest",
        action="store_true",
        help="print the runner's frozen parameter digest and exit without running",
    )
    parser.add_argument(
        "--print-cells",
        action="store_true",
        help="print every declared cell key and exit without running",
    )
    parser.add_argument(
        "--skip-twin-check",
        action="store_true",
        help="skip the freeze-twin digest check (only for minting the twin)",
    )
    args = parser.parse_args(list(argv))

    if args.print_digest:
        print(frozen_digest())
        return 0
    if args.print_cells:
        for key in declared_cells():
            print(key)
        return 0

    if not args.skip_twin_check:
        verify_against_twin(args.repo_root)

    if args.outcomes is not None:
        outcomes, claims = load_outcomes(args.outcomes)
    else:
        outcomes, claims = {}, ()
    payload = assess_grid(outcomes, claims)
    payload["outcomes_file"] = str(args.outcomes) if args.outcomes is not None else None

    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")

    outcome = Outcome(payload["outcome"])
    if outcome is Outcome.PASS:
        return 0
    return 3 if outcome is Outcome.FAIL else 4


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(__import__("sys").argv[1:]))


__all__ = [
    "CELL_STATUSES",
    "CLAIM_SCOPE",
    "DECLARED_CELL_COUNT",
    "DOMAIN_BLOCKS",
    "FREEZE_DOCUMENT",
    "FREEZE_TWIN",
    "FROZEN_PARAMETERS",
    "INFERENCE_BUDGETS",
    "K_LEVELS",
    "Q_TARGETS",
    "REPRESENTATIONS",
    "RIGHT_CENSORED",
    "SCALE_LADDERS",
    "VERDICT_GRID_INCOMPLETE",
    "VERDICT_NO_CELL_EXECUTED",
    "VERDICT_NO_EVALUABLE_TEST",
    "VERDICT_OFF_GRID",
    "VERDICT_ON_GRID",
    "CROSSING_REPORT_LIMIT",
    "CellOutcome",
    "ClaimedCrossing",
    "CrossingTest",
    "Frontier",
    "FreezeViolation",
    "OutcomeFileError",
    "apply_holm",
    "audit_claimed_crossings",
    "assess_grid",
    "cell_key",
    "compute_frontier",
    "declared_cells",
    "frozen_digest",
    "load_outcomes",
    "main",
    "read_frontier",
    "scale_frontier",
    "evaluate_crossing",
    "verify_against_twin",
]
