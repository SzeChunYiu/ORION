"""P11G's hostile tree decoder, registered so its defeat can be asked what it measured.

The shipped runner is loaded and driven, never re-implemented:
``papers/paper-11-state-as-computation/run_p11g_deterministic_tree_decoder_v1.py``
supplies the seed, the cells, the training grid, the parity bank and the
per-query estimator seeds, and :func:`measure` replays its RNG stream draw for
draw with only the decoder, its resource envelope and the columns it is shown
lifted out as parameters. :func:`shipped_scientific_sha256` reproduces the
committed payload digest before any claim below is transcribed, and
:func:`shipped_curves_match` checks every published curve value, so a failure
reported from here is about P11G and not about a local fixture written to fail.

Three questions are asked of it, in the vocabulary the programme already has.

Could the attack have won? :func:`gate_reaches` runs P11G's four scientific
gates against a register of worlds the frozen protocol admits --- fresh data
seeds, which is the whole reachable set once the cells, the grid and the
estimator are pinned --- using
:func:`orion.programme.gate_attainability.measure_gate_attainability`. Every one
of them comes back ``THRESHOLD_UNCONDITIONAL``: the gates hold in every
admissible world, so the attack had no reachable win and
:func:`terminal_reach` reports one reachable terminal.

Was the arm incapable, or was it merely placed where it could not win?
:func:`attack_responsiveness` runs the same gates over worlds the protocol does
*not* admit --- the same 96-tree ExtraTrees decoder shown a bank of 5, 10 and 25
columns instead of 2,380 --- and the terminal moves. That separation, a
responsive emitter whose losing region lies outside its own preregistration, is
the same pair :mod:`orion.study.p14.governance_gates` reports for P14A, read
through the attacker instead of the defender.

Did the register contain an arm that wins? ``P11C_STRONGER_DECODER_ATTACK_
PROTOCOL_V1.md`` froze three universal-state arms and the rule that combines
them --- "the earliest threshold reached by any of the three universal-state
arms" --- and then timed out, after which each successor gated on one arm alone.
:func:`best_of_arms_gate` applies that frozen rule to P11G's own frozen data and
:func:`arm_axis` reports the decoder-arm axis with
:func:`orion.programme.refutation_capacity.axis_sensitivity`: the terminal is a
function of which arm was carried forward.

The failure class is recorded under
``research/failures/2026-08-unwinnable-attack-predetermined-survival/``.
"""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import sys
import warnings
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Sequence

import numpy as np

from orion.programme.gate_attainability import (
    AdmissibleWorld,
    GateDirection,
    GateReach,
    PreregisteredGate,
    TerminalReach,
    measure_gate_attainability,
    measure_terminal_reach,
)
from orion.programme.refutation_capacity import AxisSensitivity, ModelPoint, axis_sensitivity
from orion.programme.terminal_responsiveness import (
    ReceiptResponsiveness,
    WithholdingCase,
    measure_receipt_responsiveness,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
PAPER_DIR = REPO_ROOT / "papers/paper-11-state-as-computation"
P11G_RUNNER = PAPER_DIR / "run_p11g_deterministic_tree_decoder_v1.py"
P11G_RECEIPT = PAPER_DIR / "P11G_DETERMINISTIC_TREE_DECODER_RESULT_V1.json"
P11C_PROTOCOL = PAPER_DIR / "P11C_STRONGER_DECODER_ATTACK_PROTOCOL_V1.md"

#: The scientific payload digest P11G publishes twice in its own receipt. The
#: fidelity anchor: :func:`shipped_scientific_sha256` reproduces it by re-running
#: the shipped pipeline, so the numbers below are P11G's own.
SHIPPED_SCIENTIFIC_SHA256 = "a2b0c33ce3c39e54ca1aa400a2b7d52d019fc4503f6cd5eb726c7b8bbe79a7cc"

#: The terminal the shipped receipt publishes, and the one its other branch prints.
SHIPPED_TERMINAL = "P11G_DETERMINISTIC_TREE_DECODER_GAP_SUPPORTED"
NOT_MET_TERMINAL = "P11G_DETERMINISTIC_TREE_DECODER_GAP_NOT_MET"

#: The arm P11G's two hostile gates read.
REPORTED_ARM = "UNIVERSAL_EXTRA_TREES"

#: The defence: L2 logistic regression on the query's compiled components only.
DEFENCE_ARM = "COMPILED_L2"

#: The three universal-state arms ``P11C_STRONGER_DECODER_ATTACK_PROTOCOL_V1.md``
#: froze together with its best-of-arms combination rule. P11D and P11E carried
#: ``UNIVERSAL_L1`` forward; P11G carried ``UNIVERSAL_EXTRA_TREES``; nothing ran
#: ``UNIVERSAL_L2`` against a terminal.
REGISTERED_UNIVERSAL_ARMS = ("UNIVERSAL_L2", "UNIVERSAL_L1", "UNIVERSAL_EXTRA_TREES")

#: The same tree decoder on the compiled components. Not an attack --- it removes
#: the treatment instead of attacking it --- and it is what separates the part of
#: the published ``n=64`` gap that is the change of decoder family from the part
#: that is the change of state.
DECODER_CONTROL_ARM = "COMPILED_EXTRA_TREES"

ALL_ARMS = REGISTERED_UNIVERSAL_ARMS + (DEFENCE_ARM, DECODER_CONTROL_ARM)

#: Mean test accuracy a curve must reach for its training size to count as a
#: threshold, transcribed from the runner's ``threshold()``.
TARGET_ACCURACY = 0.95

#: The training size every ``n=64`` gate reads, and the smallest registered one.
GATE_TRAIN_SIZE = 64

#: The registered size the hostile threshold gate compares against. The gate is
#: satisfied when the attack reaches nothing strictly below it.
GATE_THRESHOLD_SIZE = 256

#: Registered sizes strictly below :data:`GATE_THRESHOLD_SIZE`. Fitting is
#: confined to these because every one of P11G's four scientific gates reads the
#: curve at ``n=64`` or asks whether the target was reached by ``n=128``; the RNG
#: stream is still replayed over the whole frozen grid.
GATE_TRAIN_SIZES = (64, 128)


class P11GFidelityError(AssertionError):
    """Raised when the shipped runner no longer produces the receipt it published."""


@dataclass(frozen=True)
class AttackSpec:
    """One run of P11G's pipeline: which decoder, how much of it, and shown what.

    Only ``seed`` varies inside the freeze. ``n_trees``, ``max_features`` and
    ``bank_columns`` are pinned by the protocol at ``96``, ``"sqrt"`` and the
    complete parity bank, and moving them registers a world the protocol does not
    admit --- which is the capability question, not the attainability one.
    """

    seed: int
    arm: str = REPORTED_ARM
    n_trees: int = 96
    max_features: str | float | None = "sqrt"
    bank_columns: int | None = None
    """Nuisance columns shown alongside the query's active ones. ``None`` is the
    complete universal bank, which is what the frozen protocol specifies."""

    def __post_init__(self) -> None:
        if self.arm not in ALL_ARMS:
            raise ValueError(f"unregistered arm {self.arm}")
        if self.n_trees < 1:
            raise ValueError("an ensemble needs at least one tree")
        if self.bank_columns is not None and self.bank_columns < 0:
            raise ValueError("a nuisance column count cannot be negative")

    def as_json(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "arm": self.arm,
            "n_trees": self.n_trees,
            "max_features": str(self.max_features),
            "bank_columns": self.bank_columns,
        }


@dataclass(frozen=True)
class CellReading:
    """One cell of one run: the attack's curve, the defence's, and the laundering count."""

    cell: tuple[int, int, int]
    universal_dimension: int
    attack: tuple[tuple[int, float], ...]
    defence: tuple[tuple[int, float], ...]
    laundering_failures: int

    def attack_at(self, size: int) -> float:
        return dict(self.attack)[size]

    def defence_at(self, size: int) -> float:
        return dict(self.defence)[size]

    @property
    def censored_attack_threshold(self) -> int:
        """Smallest registered size reaching the target, censored at :data:`GATE_THRESHOLD_SIZE`.

        P11C's own wording: ``NOT_REACHED`` counts as beyond the largest grid
        point "only for the directional gate and never as an extrapolated
        numeric threshold". Censoring says exactly that and nothing more, so a
        curve that reaches the target at 256, at 1024 or nowhere at all are one
        value here --- which is the only thing the gate distinguishes.
        """

        for size, value in self.attack:
            if value >= TARGET_ACCURACY:
                return size
        return GATE_THRESHOLD_SIZE

    @property
    def best_attack_below_gate(self) -> float:
        """The attack's best mean accuracy at a registered size below the gate."""

        return max(value for _, value in self.attack)

    @property
    def delta64(self) -> float:
        return self.defence_at(GATE_TRAIN_SIZE) - self.attack_at(GATE_TRAIN_SIZE)

    def as_json(self) -> dict[str, Any]:
        return {
            "cell": list(self.cell),
            "universal_dimension": self.universal_dimension,
            "attack": {str(size): value for size, value in self.attack},
            "defence": {str(size): value for size, value in self.defence},
            "laundering_failures": self.laundering_failures,
            "censored_attack_threshold": self.censored_attack_threshold,
            "delta64": self.delta64,
        }


@lru_cache(maxsize=1)
def p11g_module() -> ModuleType:
    """Import the shipped runner under its own name, without executing its ``main``."""

    if not P11G_RUNNER.exists():  # pragma: no cover - a missing paper is a repo-layout fault
        raise FileNotFoundError(f"P11G runner not found at {P11G_RUNNER}")
    spec = importlib.util.spec_from_file_location("orion_p11g_shipped_runner", P11G_RUNNER)
    if spec is None or spec.loader is None:  # pragma: no cover - importlib contract
        raise ImportError(f"cannot load {P11G_RUNNER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    # ``papers/`` belongs to the paper lane and this audit only reads from it.
    # Executing a source file normally leaves a ``__pycache__`` beside it, so
    # bytecode writing is suppressed for the duration of the load.
    previously = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previously
    return module


@lru_cache(maxsize=1)
def shipped_receipt() -> dict[str, Any]:
    return json.loads(P11G_RECEIPT.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def shipped_scientific_sha256() -> str:
    """Re-run P11G's one-run pipeline and digest its canonical bytes."""

    module = p11g_module()
    return hashlib.sha256(
        module.canonical_text(module.scientific_payload()).encode("utf-8")
    ).hexdigest()


def require_fidelity() -> str:
    """Refuse to transcribe a claim about P11G before the shipped runner reproduces it."""

    digest = shipped_scientific_sha256()
    if digest != SHIPPED_SCIENTIFIC_SHA256:
        raise P11GFidelityError(
            f"P11G scientific payload digests to {digest}, not the published "
            f"{SHIPPED_SCIENTIFIC_SHA256}; the shipped runner has moved under this audit"
        )
    return digest


def _nuisance_columns(
    bank_size: int, active: Sequence[int], cell_index: int, keep: int
) -> list[int]:
    """The query's active columns plus ``keep`` deterministically drawn nuisance ones."""

    pool = [column for column in range(bank_size) if column not in set(active)]
    drawn = np.random.default_rng(777 + 13 * cell_index).choice(
        len(pool), size=min(keep, len(pool)), replace=False
    )
    return list(active) + [pool[int(index)] for index in drawn]


def _model(spec: AttackSpec, *, tree_seed: int, linear_seed: int):
    from sklearn.ensemble import ExtraTreesClassifier
    from sklearn.linear_model import LogisticRegression

    if spec.arm in (REPORTED_ARM, DECODER_CONTROL_ARM):
        return ExtraTreesClassifier(
            n_estimators=spec.n_trees,
            max_features=spec.max_features,
            random_state=tree_seed,
            n_jobs=1,
        )
    if spec.arm == "UNIVERSAL_L1":
        # ``penalty="l1"`` is what P11C froze and what P11D and P11E executed.
        # Reproducing the registered arm matters more than the spelling.
        return LogisticRegression(
            C=0.1, penalty="l1", solver="liblinear", max_iter=1000, random_state=linear_seed
        )
    return LogisticRegression(C=1.0, solver="liblinear", max_iter=1000, random_state=linear_seed)


def measure(spec: AttackSpec) -> tuple[CellReading, ...]:
    """Replay P11G's frozen data stream and score ``spec``'s arm and the defence on it.

    The whole training grid is drawn whatever sizes are fitted, because the RNG
    stream is shared across cells: truncating the grid changes the second cell's
    queries and test set, so a curve measured on a short grid is a curve about a
    different experiment. Only the fitting is confined to
    :data:`GATE_TRAIN_SIZES`, which is every size P11G's four scientific gates
    read.
    """

    return _measure(spec)


@lru_cache(maxsize=256)
def _measure(spec: AttackSpec) -> tuple[CellReading, ...]:
    module = p11g_module()
    readings: list[CellReading] = []
    rng = np.random.default_rng(spec.seed)

    for cell_index, (d, s, r) in enumerate(module.CELLS):
        subsets = list(itertools.combinations(range(d), s))
        bank_size = len(subsets)
        queries = [
            rng.choice(bank_size, size=r, replace=False).tolist()
            for _ in range(module.N_QUERIES)
        ]
        test_x = rng.choice((-1, 1), size=(module.N_TEST, d)).astype(np.int8)
        test_bank = module.bank(test_x, subsets)

        test_y: list[np.ndarray] = []
        laundering = 0
        for active in queries:
            values = test_bank[:, active]
            signed = np.where(values.sum(axis=1) > 0, 1, -1).astype(np.int8)
            test_y.append((signed > 0).astype(np.int8))
            for column in range(r):
                if np.array_equal(values[:, column], signed):
                    laundering += 1
                if np.array_equal(values[:, column], -signed):
                    laundering += 1

        attack: list[tuple[int, float]] = []
        defence: list[tuple[int, float]] = []
        for size in module.TRAIN_SIZES:
            train_x = rng.choice((-1, 1), size=(size, d)).astype(np.int8)
            if size not in GATE_TRAIN_SIZES:
                continue
            train_bank = module.bank(train_x, subsets)
            attack_scores: list[float] = []
            defence_scores: list[float] = []
            for query_index, active in enumerate(queries):
                labels = (train_bank[:, active].sum(axis=1) > 0).astype(np.int8)
                # The runner derives every estimator's ``random_state`` from its
                # module-level ``SEED``, so a fresh-seed run of the same protocol
                # moves them with it. Offsetting the runner's own functions is
                # that formula evaluated at this world's seed, and it is zero at
                # the shipped seed.
                offset = spec.seed - module.SEED
                tree_seed = module.tree_seed(cell_index, query_index, size) + offset
                linear_seed = module.compiled_seed(cell_index, query_index, size) + offset
                if spec.arm in (DECODER_CONTROL_ARM, DEFENCE_ARM):
                    columns: Any = list(active)
                elif spec.bank_columns is None:
                    columns = slice(None)
                else:
                    columns = _nuisance_columns(bank_size, active, cell_index, spec.bank_columns)
                attack_scores.append(
                    _fit(
                        _model(spec, tree_seed=tree_seed, linear_seed=linear_seed),
                        train_bank[:, columns],
                        labels,
                        test_bank[:, columns],
                        test_y[query_index],
                    )
                )
                defence_scores.append(
                    _fit(
                        _model(
                            replace(spec, arm=DEFENCE_ARM),
                            tree_seed=tree_seed,
                            linear_seed=linear_seed,
                        ),
                        train_bank[:, active],
                        labels,
                        test_bank[:, active],
                        test_y[query_index],
                    )
                )
            attack.append((size, float(np.mean(attack_scores))))
            defence.append((size, float(np.mean(defence_scores))))

        readings.append(
            CellReading(
                cell=(d, s, r),
                universal_dimension=bank_size,
                attack=tuple(attack),
                defence=tuple(defence),
                laundering_failures=laundering,
            )
        )
    return tuple(readings)


def _fit(model, train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray, test_y) -> float:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model.fit(train_x, train_y)
        return float(model.score(test_x, test_y))


#: P11G's four scientific gates, each stated as the quantity its runner compares.
#:
#: The two hostile gates are read on the attack's own accuracy lattice rather
#: than through the runner's boolean, so an unreachable win reports a distance
#: instead of a ``true``. The readings are exact, not approximations of the
#: runner's expressions: a mean of three test accuracies over 4,096 points is a
#: multiple of ``1/12288``, and neither ``0.95`` nor ``0.20`` is one, so no
#: attainable value can land on a boundary where ``AT_MOST`` and ``<`` disagree.
GATES: tuple[PreregisteredGate, ...] = (
    PreregisteredGate(
        gate_id="no_answer_laundering",
        reads="active components equal to or negating the signed label on the protected test set",
        threshold=0.0,
        direction=GateDirection.AT_MOST,
    ),
    PreregisteredGate(
        gate_id="compiled_by_64",
        reads="the compiled arm's smallest mean test accuracy at n=64 over the protected cells",
        threshold=TARGET_ACCURACY,
        direction=GateDirection.AT_LEAST,
    ),
    PreregisteredGate(
        gate_id="tree_threshold_ge_256",
        reads="the attack arm's best mean test accuracy at a registered size below n=256, "
        "over the protected cells",
        threshold=TARGET_ACCURACY,
        direction=GateDirection.AT_MOST,
    ),
    PreregisteredGate(
        gate_id="delta64_ge_0_20",
        reads="the smallest compiled-minus-attack mean accuracy at n=64 over the protected cells",
        threshold=0.20,
        direction=GateDirection.AT_LEAST,
    ),
)

#: Each gate's statistic, read off a run. Keyed by ``gate_id``.
READINGS: dict[str, Callable[[tuple[CellReading, ...]], float]] = {
    "no_answer_laundering": lambda cells: float(sum(c.laundering_failures for c in cells)),
    "compiled_by_64": lambda cells: min(c.defence_at(GATE_TRAIN_SIZE) for c in cells),
    "tree_threshold_ge_256": lambda cells: max(c.best_attack_below_gate for c in cells),
    "delta64_ge_0_20": lambda cells: min(c.delta64 for c in cells),
}


def gate_values(spec: AttackSpec) -> dict[str, float]:
    """Every gate's statistic in one world."""

    cells = measure(spec)
    return {gate.gate_id: READINGS[gate.gate_id](cells) for gate in GATES}


def gate_booleans(spec: AttackSpec) -> dict[str, bool]:
    """The four gates as the runner would write them, from this module's readings."""

    values = gate_values(spec)
    return {gate.gate_id: gate.satisfied_by(values[gate.gate_id]) for gate in GATES}


def terminal_of(spec: AttackSpec) -> str:
    """P11G's terminal expression, recomputed on one world's scientific gates.

    The two replay gates are omitted deliberately. They are properties of the
    executable rather than of the decoder --- they are what the P11F correction
    was about --- and they are ``true`` in every world this module registers,
    so including them would change no verdict and would misreport what the
    scientific gates alone decide.
    """

    return SHIPPED_TERMINAL if all(gate_booleans(spec).values()) else NOT_MET_TERMINAL


def receipt(spec: AttackSpec) -> dict[str, Any]:
    """A P11G-shaped receipt for one world: the terminal plus the numbers behind it."""

    cells = measure(spec)
    values = gate_values(spec)
    return {
        "terminal": terminal_of(spec),
        "gates": gate_booleans(spec),
        "attack_best_below_gate": values["tree_threshold_ge_256"],
        "smallest_delta64": values["delta64_ge_0_20"],
        "censored_attack_thresholds": tuple(c.censored_attack_threshold for c in cells),
    }


#: Fields of :func:`receipt` that are measurements rather than the verdict. They
#: are what separates an emitter that was never perturbed from one that was
#: perturbed and did not care.
RECEIPT_EVIDENCE = (
    "attack_best_below_gate",
    "smallest_delta64",
    "censored_attack_thresholds",
)


def shipped_spec() -> AttackSpec:
    """P11G exactly as frozen: its own seed, its own arm, its own resource envelope."""

    return AttackSpec(seed=p11g_module().SEED)


def shipped_curves_match() -> bool:
    """Whether the replay reproduces every curve value the receipt publishes at n=64,128."""

    published = shipped_receipt()["scientific_payload"]["cells"]
    for reading, cell in zip(measure(shipped_spec()), published):
        if list(reading.cell) != cell["cell"]:
            return False
        for size in GATE_TRAIN_SIZES:
            if reading.attack_at(size) != cell["curves"][REPORTED_ARM][str(size)]:
                return False
            if reading.defence_at(size) != cell["curves"][DEFENCE_ARM][str(size)]:
                return False
    return True


#: Fresh data seeds. The protocol says "fresh data seed: 2026082120" and pins
#: every other degree of freedom --- cells, queries per cell, training grid, test
#: size, tree count, split rule, ``n_jobs``, every estimator's ``random_state``
#: --- so the seed is the reachable set, and these are draws from it rather than
#: perturbations of it.
ADMISSIBLE_SEED_OFFSETS = (0, 1, 2, 3, 4, 5)


def admissible_worlds() -> tuple[AdmissibleWorld, ...]:
    """Runs the frozen P11G protocol admits.

    The register has to be defensible in both directions: too narrow and an
    unreachable gate is an artifact of the worlds nobody registered, one world
    outside the freeze and the gate is widened rather than measured. Everything
    P11G pins is held; only the data seed moves, which is the one thing its own
    protocol declares fresh, and the estimator ``random_state`` values move with
    it exactly as the runner's own ``tree_seed`` and ``compiled_seed`` derive
    them from ``SEED``.
    """

    base = p11g_module().SEED
    worlds = [
        AdmissibleWorld(
            world_id="shipped-seed",
            admits="the committed run: the frozen protocol at its own published seed",
            payload=AttackSpec(seed=base),
        )
    ]
    worlds += [
        AdmissibleWorld(
            world_id=f"fresh-seed-{base + offset}",
            admits="the frozen protocol at another fresh data seed; the protocol fixes one "
            "and nothing in the construction distinguishes it",
            payload=AttackSpec(seed=base + offset),
        )
        for offset in ADMISSIBLE_SEED_OFFSETS
        if offset
    ]
    return tuple(worlds)


def gate_reaches(worlds: Sequence[AdmissibleWorld] | None = None) -> tuple[GateReach, ...]:
    """Each scientific gate, measured against the worlds the protocol admits."""

    register = tuple(admissible_worlds() if worlds is None else worlds)
    return tuple(
        measure_gate_attainability(
            lambda spec, gate_id=gate.gate_id: READINGS[gate_id](measure(spec)),
            gate=gate,
            worlds=register,
        )
        for gate in GATES
    )


def terminal_reach(worlds: Sequence[AdmissibleWorld] | None = None) -> TerminalReach:
    """How many terminals P11G's conjunction could print over its own reachable set."""

    return measure_terminal_reach(gate_reaches(worlds), label="P11G tree-decoder terminal")


def closest_refuting_margin(reach: GateReach) -> float:
    """The registered world that came nearest to bringing this gate down.

    ``GateReach.attainment_margin`` reports the world closest to *satisfying*,
    which is the number an unattainable gate needs. An unconditional gate needs
    the mirror: the smallest margin in the register is how close the attack ever
    got, and it is the number that says a survival was never in doubt.
    """

    return min(item.margin for item in reach.readings)


def capability_cases() -> tuple[WithholdingCase, ...]:
    """Worlds in which the registered attack should win, and the receipt should say so.

    Banks the frozen protocol does **not** admit: the same 96-tree ExtraTrees
    decoder shown the query's active components plus a handful of nuisance
    columns instead of the complete parity bank. They are the capability
    measurement --- if the terminal moves here, the arm is a working decoder
    that was placed where it could not win, rather than one that cannot decode.

    Each is registered because a reader can agree the positive terminal is not
    warranted there: a bank of 5, 10 or 25 columns is not the universal state
    P11 reports 91x-1820x representation ratios for, so a low-sample
    accessibility advantage certified against it would be certifying the choice
    of decoder family rather than the placement of the state. Banks large enough
    that the attack correctly loses are not withholding cases; they are reported
    without a verdict by :func:`nuisance_ladder`.
    """

    base = shipped_spec()
    return (
        WithholdingCase(
            case_id="compiled-columns-only",
            withholds="the attack decoder is shown exactly the components the compiler "
            "emits, so the representation is equalised and only the decoder family differs",
            payload=replace(base, bank_columns=0),
        ),
        WithholdingCase(
            case_id="active-plus-5-nuisance",
            withholds="a bank of ten columns; the compilation ratio the paper claims its "
            "advantage from is absent, so no accessibility gap should be certified",
            payload=replace(base, bank_columns=5),
        ),
        WithholdingCase(
            case_id="active-plus-20-nuisance",
            withholds="a bank of twenty-five columns, still four orders of magnitude short "
            "of the registered universal dimension",
            payload=replace(base, bank_columns=20),
        ),
    )


def attack_responsiveness() -> ReceiptResponsiveness:
    """Whether the terminal is a function of the run at all, over inadmissible worlds.

    This is the half that clears the emitter, and it is why the finding is about
    the frozen bank rather than about the arm: shrink the bank the attack must
    search and the same conjunction prints the other terminal.
    """

    return measure_receipt_responsiveness(
        receipt,
        label="P11G tree-decoder receipt",
        baseline=shipped_spec(),
        verdict_field="terminal",
        evidence_fields=RECEIPT_EVIDENCE,
        cases=capability_cases(),
    )


#: Nuisance-column counts for the capability curve. Not a register of verdicts:
#: the point is the monotone discovery cost, which is the mechanism P11 claims.
NUISANCE_LADDER = (0, 5, 20, 50, 100, 300, 1000, None)


def nuisance_ladder(steps: Sequence[int | None] = NUISANCE_LADDER) -> tuple[dict[str, Any], ...]:
    """The attack's ``n=64`` accuracy as the bank it must search grows."""

    base = shipped_spec()
    rows: list[dict[str, Any]] = []
    for keep in steps:
        spec = replace(base, bank_columns=keep)
        rows.append(
            {
                "nuisance_columns": keep,
                "terminal": terminal_of(spec),
                "cells": [
                    {
                        "cell": list(reading.cell),
                        "attack_at_64": reading.attack_at(GATE_TRAIN_SIZE),
                        "delta64": reading.delta64,
                    }
                    for reading in measure(spec)
                ],
            }
        )
    return tuple(rows)


def registered_pool(seed: int | None = None) -> dict[str, tuple[CellReading, ...]]:
    """All three P11C universal arms, plus the defence, on one frozen data stream."""

    base = shipped_spec() if seed is None else replace(shipped_spec(), seed=seed)
    return {arm: measure(replace(base, arm=arm)) for arm in REGISTERED_UNIVERSAL_ARMS}


def best_of_arms_thresholds(seed: int | None = None) -> tuple[int, ...]:
    """P11C's frozen rule: the earliest threshold reached by any universal arm, per cell.

    Censored at :data:`GATE_THRESHOLD_SIZE`, which is all the gate reads.
    """

    pool = registered_pool(seed)
    cells = len(pool[REPORTED_ARM])
    return tuple(
        min(pool[arm][index].censored_attack_threshold for arm in REGISTERED_UNIVERSAL_ARMS)
        for index in range(cells)
    )


def best_of_arms_gate(seed: int | None = None) -> bool:
    """P11G's hostile threshold gate, read through the pool P11C registered."""

    return all(threshold >= GATE_THRESHOLD_SIZE for threshold in best_of_arms_thresholds(seed))


def terminal_under_arm(arm: str, seed: int | None = None) -> str:
    """P11G's terminal with ``arm`` in the universal slot, on P11G's own data."""

    base = shipped_spec() if seed is None else replace(shipped_spec(), seed=seed)
    return terminal_of(replace(base, arm=arm))


def arm_axis(seed: int | None = None) -> AxisSensitivity:
    """How much of P11G's terminal is the choice of registered arm.

    P6's donor axis was inert, so every count it multiplied was a relabelling.
    This is the same instrument reading the other way: an axis the terminal
    depends on, present in the published receipt with exactly one value.
    """

    space: list[ModelPoint] = [{"decoder_arm": arm} for arm in REGISTERED_UNIVERSAL_ARMS]
    return axis_sensitivity(
        "decoder_arm",
        reference=lambda point: terminal_under_arm(str(point["decoder_arm"]), seed),
        space=space,
    )


def decoder_family_share() -> tuple[dict[str, Any], ...]:
    """Split P11G's published ``n=64`` gap into its decoder half and its state half.

    P11G moves the representation and the learner at once: L2 logistic regression
    on ``r`` compiled columns against ExtraTrees on the full bank. Holding the
    decoder at ExtraTrees and moving only the representation gives the part of
    the gap the paper's placement claim can carry.
    """

    reported = measure(shipped_spec())
    control = measure(replace(shipped_spec(), arm=DECODER_CONTROL_ARM))
    rows: list[dict[str, Any]] = []
    for attack, same_decoder in zip(reported, control):
        published = attack.delta64
        decoder = same_decoder.delta64
        rows.append(
            {
                "cell": list(attack.cell),
                "published_gap_at_64": published,
                "decoder_family_gap_at_64": decoder,
                "representation_gap_at_64": published - decoder,
                "decoder_family_share": decoder / published if published else None,
            }
        )
    return tuple(rows)


def seed_sweep(seeds: Sequence[int]) -> tuple[dict[str, Any], ...]:
    """The four scientific gates under repeated draws of the frozen protocol."""

    rows: list[dict[str, Any]] = []
    for seed in seeds:
        spec = AttackSpec(seed=seed)
        rows.append(
            {
                "seed": seed,
                "values": gate_values(spec),
                "gates": gate_booleans(spec),
                "terminal": terminal_of(spec),
            }
        )
    return tuple(rows)


__all__ = [
    "ADMISSIBLE_SEED_OFFSETS",
    "ALL_ARMS",
    "DECODER_CONTROL_ARM",
    "DEFENCE_ARM",
    "GATES",
    "GATE_THRESHOLD_SIZE",
    "GATE_TRAIN_SIZE",
    "GATE_TRAIN_SIZES",
    "NOT_MET_TERMINAL",
    "NUISANCE_LADDER",
    "P11C_PROTOCOL",
    "P11G_RECEIPT",
    "P11G_RUNNER",
    "READINGS",
    "RECEIPT_EVIDENCE",
    "REGISTERED_UNIVERSAL_ARMS",
    "REPORTED_ARM",
    "SHIPPED_SCIENTIFIC_SHA256",
    "SHIPPED_TERMINAL",
    "TARGET_ACCURACY",
    "AttackSpec",
    "CellReading",
    "P11GFidelityError",
    "admissible_worlds",
    "arm_axis",
    "attack_responsiveness",
    "best_of_arms_gate",
    "best_of_arms_thresholds",
    "capability_cases",
    "closest_refuting_margin",
    "decoder_family_share",
    "gate_booleans",
    "gate_reaches",
    "gate_values",
    "measure",
    "nuisance_ladder",
    "p11g_module",
    "receipt",
    "registered_pool",
    "require_fidelity",
    "seed_sweep",
    "shipped_curves_match",
    "shipped_receipt",
    "shipped_scientific_sha256",
    "shipped_spec",
    "terminal_of",
    "terminal_reach",
    "terminal_under_arm",
]
