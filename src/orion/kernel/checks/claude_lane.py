"""Lane `claude` — V0 dimension-level discriminating checks.

Boundary, stated before any predicate: these are **form-level** discriminators.
They verify that an answered dimension carries the *shape* of a step-specific
contract — declarative, structurally typed, and distinct from the universal
default envelopes — and they must reject the host battery (empty / junk /
envelope) plus their declared near-miss negatives to be admitted at all. They
do not and cannot verify that a contract is *true of the world*; truth-level
verification belongs to executable benchmarks and remains an explicitly open
coordinate. `VERIFIED` under these checks therefore means: evidence-resolved
content whose form an independent lane audited — not established step validity.

The seed-state exclusion is derived, not hand-listed: at import these checks
capture every (mechanic, entry) pair the pre-answer program already carries —
universal envelopes and curated candidate formulations alike — and a predicate
only counts content *beyond* that seed. Without this, a check would judge the
cell's accumulated state rather than what answers added, so a junk record
landing on a cell with good pre-existing content would ride that content to
VERIFIED. `test_no_raw_default_cell_passes_any_check` pins the property to CI
against the real decomposition.

Lane rule these checks inherit from the gate: they can never verify records
from lane `claude`; they exist to audit the other lanes' answers, exactly as
the other lanes' checks audit ours.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

from orion.mechanics.model import MechanicCell, MechanicDimension
from orion.mechanics.program import current_program_cells

from ..gate import DiscriminatingCheck

LANE = "claude"

_TYPED_TOKEN = re.compile(r"\b[A-Z][A-Z0-9]{2,}(?:_[A-Z0-9]+)+\b")
_FORMAL_MARKERS = ("=", "->", "iff", " AND ", " NOT ", "superset", "lattice", "partial order", "product order")
_STATE_MARKERS = ("<", "ledger", "log", "append-only", "frozen", "DAG", "derived view", "immutable")
_VERIF_MARKERS = ("certificate", "replay", "attestation", "independent", "frozen", "content-bound")

_FIELD_BY_DIMENSION: dict[MechanicDimension, str] = {
    MechanicDimension.TRANSITION_MODEL: "transition_semantics",
    MechanicDimension.MATHEMATICS: "mathematical_semantics",
    MechanicDimension.STATE: "state_ids",
    MechanicDimension.OBSERVABILITY: "observable_ids",
    MechanicDimension.VERIFICATION: "verification_contracts",
    MechanicDimension.FAILURE: "failure_signatures",
}

_FAILURE_SIGNATURE = re.compile(r"^failure:[A-Za-z0-9_.]+:[a-z0-9-]+\s+-\s+\S")


def _seed_entries() -> dict[MechanicDimension, frozenset[tuple[str, str]]]:
    """Every (mechanic, entry) pair the pre-answer program already carries.

    The driver rebuilds cells from code as the seed of every run, so the seed
    captured at import time is exactly the state answers land on. Content that
    was already present before any answer can never satisfy a check.
    """

    seed_cells = current_program_cells()
    return {
        dimension: frozenset(
            (cell.mechanic_id, str(item))
            for cell in seed_cells
            for item in getattr(cell, field)
        )
        for dimension, field in _FIELD_BY_DIMENSION.items()
    }


_SEED = _seed_entries()

_SEED_FALSIFIERS: frozenset[tuple[str, str]] = frozenset(
    (cell.mechanic_id, str(item))
    for cell in current_program_cells()
    for item in cell.falsifiers
)


def _is_preexisting(
    dimension: MechanicDimension, cell: MechanicCell, item: str
) -> bool:
    return (cell.mechanic_id, item) in _SEED[dimension]


def _declarative(text: str) -> bool:
    stripped = text.strip()
    return bool(stripped) and not stripped.endswith("?") and "xxxxx" not in stripped


def _step_specific(
    dimension: MechanicDimension, cell: MechanicCell, items: Iterable[str]
) -> tuple[str, ...]:
    return tuple(
        item
        for item in items
        if _declarative(item) and not _is_preexisting(dimension, cell, item)
    )


def _transition_contract(cell: MechanicCell) -> bool:
    fresh = _step_specific(
        MechanicDimension.TRANSITION_MODEL, cell, cell.transition_semantics
    )
    return any(len(item) >= 40 and _TYPED_TOKEN.search(item) for item in fresh)


def _mathematics_contract(cell: MechanicCell) -> bool:
    fresh = _step_specific(
        MechanicDimension.MATHEMATICS, cell, cell.mathematical_semantics
    )
    return any(
        len(item) >= 60 and any(marker in item for marker in _FORMAL_MARKERS)
        for item in fresh
    )


def _state_contract(cell: MechanicCell) -> bool:
    fresh = _step_specific(MechanicDimension.STATE, cell, cell.state_ids)
    return any(
        len(item) >= 30 and any(marker in item for marker in _STATE_MARKERS)
        for item in fresh
    )


def _observability_contract(cell: MechanicCell) -> bool:
    fresh = _step_specific(MechanicDimension.OBSERVABILITY, cell, cell.observable_ids)
    concrete = [item for item in fresh if ("(" in item or "-" in item) and len(item) >= 12]
    return len(concrete) >= 3


def _verification_contract(cell: MechanicCell) -> bool:
    fresh = _step_specific(
        MechanicDimension.VERIFICATION, cell, cell.verification_contracts
    )
    return any(
        len(item) >= 40 and any(marker in item for marker in _VERIF_MARKERS)
        for item in fresh
    )


def _failure_contract(cell: MechanicCell) -> bool:
    """Step-specific failure content: typed signatures plus a fresh falsifier.

    A failure answer must name concrete modes in the `failure:<mechanic>:<mode>`
    grammar (not restate that failures exist) and supply at least one falsifier
    beyond the seed state, since a mode without a falsifier is unfalsifiable
    self-description.
    """

    fresh_signatures = _step_specific(
        MechanicDimension.FAILURE, cell, cell.failure_signatures
    )
    fresh_falsifiers = tuple(
        item
        for item in cell.falsifiers
        if _declarative(item)
        and len(item) >= 40
        and (cell.mechanic_id, item) not in _SEED_FALSIFIERS
    )
    return bool(fresh_falsifiers) and any(
        _FAILURE_SIGNATURE.match(item) for item in fresh_signatures
    )


def _fixture(mechanic_id: str, **fields) -> MechanicCell:
    return MechanicCell(
        mechanic_id=mechanic_id,
        purpose="check fixture",
        scope="check admissibility",
        **fields,
    )


# Near-miss negatives: plausible assurance prose that carries no contract
# structure. The battery already covers empty/junk/envelope; these cover the
# "confident but contentless" register a generator reaches for under pressure.
_NEAR_MISS_PROSE = "this step is implemented carefully and behaves correctly in all tested scenarios"


def _seed_layer_negative(dimension: MechanicDimension, field: str) -> MechanicCell:
    """A real seed cell, verbatim: what every cell holds before answers land.

    This is the fourth attack the battery does not cover: program cells already
    hold seed-layer text, so a check must not be satisfiable by content that
    predates the answer it would verify.
    """

    donor = next(
        cell for cell in current_program_cells() if getattr(cell, field)
    )
    return _fixture(donor.mechanic_id, **{field: getattr(donor, field)})


CHECKS: tuple[DiscriminatingCheck, ...] = (
    DiscriminatingCheck(
        check_id="claude.form.transition_model.v0",
        dimension=MechanicDimension.TRANSITION_MODEL,
        lane=LANE,
        predicate=_transition_contract,
        positive_fixture=_fixture(
            "fixture.transition",
            transition_semantics=(
                "typed outcomes ROUTE_CONTINUE | ROUTE_SWITCH | ROUTE_BUDGET_STOP; deterministic given (route id, per-item deltas, remaining budget)",
            ),
        ),
        negative_fixtures=(
            _fixture("nearmiss.transition", transition_semantics=(_NEAR_MISS_PROSE,)),
            _seed_layer_negative(MechanicDimension.TRANSITION_MODEL, "transition_semantics"),
        ),
        frozen_at_round=0,
    ),
    DiscriminatingCheck(
        check_id="claude.form.mathematics.v0",
        dimension=MechanicDimension.MATHEMATICS,
        lane=LANE,
        predicate=_mathematics_contract,
        positive_fixture=_fixture(
            "fixture.mathematics",
            mathematical_semantics=(
                "Contradict_l(Ci,Cj) = Overlap(Ci,Cj) AND Align_l(Ci,Cj) AND NOT Compat_l(Ci,Cj); alignment failure is typed, never a contradiction",
            ),
        ),
        negative_fixtures=(
            _fixture(
                "nearmiss.mathematics",
                mathematical_semantics=(
                    _NEAR_MISS_PROSE + " and the underlying mathematics is standard and straightforward here",
                ),
            ),
            _seed_layer_negative(MechanicDimension.MATHEMATICS, "mathematical_semantics"),
        ),
        frozen_at_round=0,
    ),
    DiscriminatingCheck(
        check_id="claude.form.state.v0",
        dimension=MechanicDimension.STATE,
        lane=LANE,
        predicate=_state_contract,
        positive_fixture=_fixture(
            "fixture.state",
            state_ids=("immutable-episode-log (canonical root; frozen before interpretation)",),
        ),
        negative_fixtures=(
            _fixture("nearmiss.state", state_ids=("internal working data used by the step",)),
            _seed_layer_negative(MechanicDimension.STATE, "state_ids"),
        ),
        frozen_at_round=0,
    ),
    DiscriminatingCheck(
        check_id="claude.form.observability.v0",
        dimension=MechanicDimension.OBSERVABILITY,
        lane=LANE,
        predicate=_observability_contract,
        positive_fixture=_fixture(
            "fixture.observability",
            observable_ids=(
                "prior-failure-present-in-bound-universe (bool)",
                "rejection-witness-id (which witness rejected a retrieved item)",
                "mandatory-atom-dropped-by-context-budget (bool)",
            ),
        ),
        negative_fixtures=(
            _fixture("nearmiss.observability", observable_ids=("progress", "status", "quality")),
            _seed_layer_negative(MechanicDimension.OBSERVABILITY, "observable_ids"),
        ),
        frozen_at_round=0,
    ),
    DiscriminatingCheck(
        check_id="claude.form.failure.v0",
        dimension=MechanicDimension.FAILURE,
        lane=LANE,
        predicate=_failure_contract,
        positive_fixture=_fixture(
            "fixture.failure",
            failure_signatures=(
                "failure:fixture.failure:false-impossibility-certificate - a repairable local defect is relabelled as proof that no solution can work",
            ),
            falsifiers=(
                "a single false certificate on a case where a licensing witness demonstrably exists refutes the mechanism",
            ),
        ),
        negative_fixtures=(
            _fixture(
                "nearmiss.failure",
                failure_signatures=("this step can fail if something goes wrong",),
                falsifiers=("more testing would reveal problems",),
            ),
            _fixture(
                "nearmiss.failure.unfalsifiable",
                failure_signatures=(
                    "failure:nearmiss.failure.unfalsifiable:mode-without-falsifier - a typed mode with no way to be wrong",
                ),
            ),
            _seed_layer_negative(MechanicDimension.FAILURE, "failure_signatures"),
        ),
        frozen_at_round=0,
    ),
    DiscriminatingCheck(
        check_id="claude.form.verification.v0",
        dimension=MechanicDimension.VERIFICATION,
        lane=LANE,
        predicate=_verification_contract,
        positive_fixture=_fixture(
            "fixture.verification",
            verification_contracts=(
                "promotion requires a content-bound certificate issued outside the challenger path, naming exact candidate and approving process",
            ),
        ),
        negative_fixtures=(
            _fixture("nearmiss.verification", verification_contracts=("the results were checked and look good",)),
            _seed_layer_negative(MechanicDimension.VERIFICATION, "verification_contracts"),
        ),
        frozen_at_round=0,
    ),
)
