"""P14A's governance benchmark, registered so its negative can be asked what it measured.

The shipped generator is loaded and driven, never re-implemented: ``main()``'s
aggregation is replayed here with the sampling support lifted out as a parameter
and every other line of it --- the case generator, the gold adjudication, the
nine arms, the seven gates, the terminal expression --- taken from
``papers/orion-24-orion-rse/run_p14a_controlled_governance_v1.py`` itself.
:func:`shipped_bench` reproduces the committed
``full_result_sha256`` byte for byte, so a failure reported from here is about
P14A and not about a local fixture written to fail.

Three questions are asked of it, in the vocabulary the programme already has.

Does the ORION arm differ from the answer key?
:func:`orion_arm_divergence` is
:func:`orion.programme.refutation_capacity.divergence_of` pointed at
``policy("ORION_RSE_FULL", c)`` with ``gold`` as the reference.

Could the gates have gone the other way? :func:`gate_reaches` runs each of the
seven against a register of worlds the frozen protocol admits, and
:func:`terminal_reach` intersects the readings to count how many terminals the
conjunction could ever print.

Was the instrument capable of a positive at all? :func:`bench_responsiveness`
runs the same emitter over sampling supports the protocol does *not* admit,
where the discriminator is prevalent, and asks whether the terminal moves. It
does. That separation --- responsive emitter, unreachable pass region --- is the
whole finding, and it is recorded under
``research/failures/2026-08-unattainable-gate-predetermined-terminal/``.
"""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Any, Hashable, Mapping, Sequence

import numpy as np

from orion.programme.gate_attainability import (
    AdmissibleWorld,
    GateDirection,
    GateReach,
    GateRole,
    PreregisteredGate,
    StatisticSupport,
    TerminalReach,
    ThresholdPanel,
    ThresholdReach,
    assess_threshold_panel,
    assess_threshold_support,
    measure_gate_attainability,
    measure_terminal_reach,
)
from orion.programme.refutation_capacity import (
    AxisSensitivity,
    ModelPoint,
    TheoryDivergence,
    axis_sensitivity,
    divergence_of,
)
from orion.programme.terminal_responsiveness import (
    ReceiptResponsiveness,
    WithholdingCase,
    measure_receipt_responsiveness,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
P14A_SCRIPT = REPO_ROOT / "papers/orion-24-orion-rse/run_p14a_controlled_governance_v1.py"
P14A_RECEIPT = (
    REPO_ROOT / "papers/orion-24-orion-rse/P14A_CONTROLLED_GOVERNANCE_RESULT_RECEIPT_V1.json"
)

#: The terminal the shipped receipt publishes.
SHIPPED_TERMINAL = "P14A_CONTROLLED_GOVERNANCE_SUPERIORITY_GATE_NOT_MET"

#: The terminal the generator's other branch would print. Live code, unreachable
#: under the protocol's own sampling support --- which is the finding.
POSITIVE_TERMINAL = "P14A_CONTROLLED_GOVERNANCE_SUPERIORITY_SUPPORTED"

#: The shipped receipt's own ``full_result_sha256``. The fidelity anchor.
SHIPPED_RESULT_DIGEST = "3ac625b799eeb00acee68deecb45ab9ae771b977dbf6303a0795cb80057a28fe"

#: The eight family rates, in the order ``main()`` draws them. The order is
#: load-bearing: it fixes the generator's RNG stream, and reproducing the shipped
#: digest depends on drawing them exactly here.
SUPPORT_KEYS: tuple[str, ...] = (
    "positive",
    "bad_evidence",
    "unfrozen",
    "nonidentifiable",
    "donor",
    "interaction",
    "history",
    "new_evidence",
)

#: The sampling ranges the frozen protocol declares, transcribed from ``main()``.
#: This is the reachable set the attainability question is asked over.
SHIPPED_SUPPORT: Mapping[str, tuple[float, float]] = {
    "positive": (0.35, 0.65),
    "bad_evidence": (0.05, 0.18),
    "unfrozen": (0.05, 0.18),
    "nonidentifiable": (0.04, 0.14),
    "donor": (0.10, 0.28),
    "interaction": (0.08, 0.22),
    "history": (0.08, 0.22),
    "new_evidence": (0.25, 0.65),
}

#: The fixed mixture every family draw is averaged against, transcribed from
#: ``main()``'s ``base``. Halving the family's own draw toward this is what keeps
#: the realized rates inside a band roughly half the declared width, and it is
#: half of why the discriminator cannot get common enough to clear a gate.
BASE_MIXTURE: Mapping[str, float] = {
    "positive": 0.50,
    "bad_evidence": 0.10,
    "unfrozen": 0.10,
    "nonidentifiable": 0.08,
    "donor": 0.18,
    "interaction": 0.15,
    "history": 0.15,
    "new_evidence": 0.45,
}

#: The eight case facts, in the order ``make_case`` writes them.
FACT_FIELDS: tuple[str, ...] = (
    "positive",
    "evidence_integrity",
    "frozen",
    "identifiable",
    "donor_owned",
    "interaction_only",
    "live_negative_history",
    "material_new_evidence",
)

#: Which family rate governs each fact, and whether the rate is the probability
#: of the fact or of its negation. ``bad_evidence`` is the chance integrity
#: *fails*, so the three integrity-style facts read their rate inverted.
FACT_RATE: Mapping[str, str] = {
    "positive": "positive",
    "evidence_integrity": "bad_evidence",
    "frozen": "unfrozen",
    "identifiable": "nonidentifiable",
    "donor_owned": "donor",
    "interaction_only": "interaction",
    "live_negative_history": "history",
    "material_new_evidence": "new_evidence",
}
INVERTED_FACTS = frozenset({"evidence_integrity", "frozen", "identifiable"})

#: The one fact state, of the 144 ``make_case`` can emit, on which the strongest
#: rule baseline and the full contract disagree. Both failing gates are its
#: frequency, so the whole P14A comparison is the prevalence of this one point.
DISCRIMINATING_STATE: Mapping[str, bool] = {
    "positive": True,
    "evidence_integrity": True,
    "frozen": True,
    "identifiable": True,
    "donor_owned": False,
    "interaction_only": False,
    "live_negative_history": True,
    "material_new_evidence": False,
}

#: The four rule baselines the generator selects its comparator from.
BASELINE_ARMS: tuple[str, ...] = (
    "RAW_POSITIVE",
    "REFLECTION_CHECKLIST",
    "DONOR_AWARE_REVIEW",
    "MULTI_REVIEW",
)
ABLATION_ARMS: tuple[str, ...] = (
    "ABLATE_DONOR",
    "ABLATE_FREEZE",
    "ABLATE_INTERACTION",
    "ABLATE_NEGATIVE_HISTORY",
)
ARMS: tuple[str, ...] = BASELINE_ARMS + ("ORION_RSE_FULL",) + ABLATION_ARMS

_TALLY_KEYS: tuple[str, ...] = (
    "false_promote",
    "supported_total",
    "supported_promoted",
    "correct",
    "n",
    "history_cases",
    "history_correct",
)


def _load(path: Path, module_name: str) -> ModuleType:
    """Import a shipped script by path without putting it on the import graph."""

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    # Registered before execution so anything defined inside resolves its own
    # module, which `spec_from_file_location` alone does not arrange.
    sys.modules.setdefault(module_name, module)
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=None)
def bench_module() -> ModuleType:
    """The shipped P14A generator.

    Loaded rather than copied so ``gold``, ``policy`` and ``make_case`` below are
    the functions that produced the committed receipt. Executing the file runs
    only its constants and definitions --- ``main()`` sits behind a
    ``__name__`` guard and would write into ``papers/`` if it were called.
    """

    return _load(P14A_SCRIPT, "orion_p14a_controlled_governance")


def shipped_receipt() -> dict[str, Any]:
    return json.loads(P14A_RECEIPT.read_text())


@dataclass(frozen=True)
class BenchInput:
    """One run of the P14A benchmark: a sampling support, and the seed drawn from it.

    The support is a tuple of triples rather than a mapping so the input is
    hashable and the bench can be memoized --- each run costs 8,000 cases across
    nine arms, and the attainability register scores every gate in every world.
    """

    support: tuple[tuple[str, float, float], ...]
    seed: int

    @classmethod
    def of(
        cls, support: Mapping[str, tuple[float, float]] | None = None, *, seed: int | None = None
    ) -> "BenchInput":
        ranges = SHIPPED_SUPPORT if support is None else support
        module = bench_module()
        return cls(
            support=tuple((key, float(ranges[key][0]), float(ranges[key][1])) for key in SUPPORT_KEYS),
            seed=module.SEED if seed is None else seed,
        )

    def with_ranges(self, **ranges: tuple[float, float]) -> "BenchInput":
        """The same input with some sampling ranges replaced and nothing else moved."""

        updated = dict(self.as_ranges())
        updated.update(ranges)
        return BenchInput.of(updated, seed=self.seed)

    def as_ranges(self) -> dict[str, tuple[float, float]]:
        return {key: (low, high) for key, low, high in self.support}


@lru_cache(maxsize=None)
def shipped_input() -> BenchInput:
    """The input that produced the committed receipt.

    A function rather than a module constant so importing this module does not
    read anything out of ``papers/``; the paper lane edits that tree.
    """

    return BenchInput.of()


@lru_cache(maxsize=None)
def bench(run: BenchInput) -> dict[str, Any]:
    """Replay ``main()``'s aggregation with the sampling support as a parameter.

    Every decision is delegated to the shipped module: ``make_case`` draws the
    facts (and consumes the RNG stream exactly as it does in the committed run,
    which short-circuits three draws whenever ``positive`` is false), ``gold``
    adjudicates, ``policy`` answers for each arm. Only the eight uniform ranges
    are ours, and at :data:`SHIPPED_SUPPORT` the emitted payload hashes to
    :data:`SHIPPED_RESULT_DIGEST`.
    """

    module = bench_module()
    ranges = run.as_ranges()
    rng = np.random.default_rng(run.seed)
    totals = {arm: dict.fromkeys(_TALLY_KEYS, 0) for arm in ARMS}
    families: list[dict[str, Any]] = []
    budget_receipts = {arm: module.BUDGET_CHECKS for arm in ARMS}
    for index in range(module.N_FAMILIES):
        sampled = {key: float(rng.uniform(*ranges[key])) for key in SUPPORT_KEYS}
        rates = {key: 0.5 * sampled[key] + 0.5 * BASE_MIXTURE[key] for key in BASE_MIXTURE}
        local = {arm: dict.fromkeys(_TALLY_KEYS, 0) for arm in ARMS}
        gold_counts = {label: 0 for label in module.GOLDS}
        for _ in range(module.N):
            case = module.make_case(rng, rates)
            label = module.gold(case)
            gold_counts[label] += 1
            is_hist = bool(
                case["positive"]
                and case["live_negative_history"]
                and case["evidence_integrity"]
                and case["frozen"]
                and case["identifiable"]
                and (not case["donor_owned"])
                and (not case["interaction_only"])
            )
            for arm in ARMS:
                pred = module.policy(arm, case)
                promote = pred == "SUPPORTED_RESIDUAL"
                row = local[arm]
                row["n"] += 1
                row["false_promote"] += int(promote and label != "SUPPORTED_RESIDUAL")
                row["supported_total"] += int(label == "SUPPORTED_RESIDUAL")
                row["supported_promoted"] += int(promote and label == "SUPPORTED_RESIDUAL")
                row["correct"] += int(pred == label)
                row["history_cases"] += int(is_hist)
                row["history_correct"] += int(is_hist and pred == label)
        metrics = {}
        for arm, row in local.items():
            for key, value in row.items():
                totals[arm][key] += value
            metrics[arm] = _rates_of(row)
        families.append(
            {"family": index, "rates": rates, "gold_counts": gold_counts, "metrics": metrics}
        )

    summary = {
        arm: {**_rates_of(row), "decision_budget_checks": budget_receipts[arm]}
        for arm, row in totals.items()
    }
    strongest = max(BASELINE_ARMS, key=lambda arm: summary[arm]["disposition_accuracy"])
    gates = {gate.gate_id: gate.satisfied_by(READINGS[gate.gate_id](summary)) for gate in GATES}
    terminal = POSITIVE_TERMINAL if all(gates.values()) else SHIPPED_TERMINAL
    payload = {
        "schema": "ORION.P14A.ResearchGovernanceDecisionBench.v1",
        "protocol": "P14A_HIDDEN_GOLD_GOVERNANCE_PROTOCOL_V1.md",
        "seed": run.seed,
        "families": families,
        "summary": summary,
        "strongest_non_orion_baseline": strongest,
        "gates": gates,
        "terminal": terminal,
    }
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    return {**payload, "result_sha256": hashlib.sha256(text.encode()).hexdigest()}


def _rates_of(row: Mapping[str, int]) -> dict[str, float]:
    """The four endpoint rates, with ``main()``'s empty-denominator conventions kept.

    ``1.0`` for an empty denominator is the generator's choice, not this
    module's. It is exactly the substitution
    :mod:`orion.programme.guard_exercise` refuses, and it is reproduced verbatim
    because changing it would change the digest the fidelity anchor pins.
    """

    return {
        "false_promotion_rate": row["false_promote"] / row["n"],
        "useful_discovery_recall": (
            row["supported_promoted"] / row["supported_total"] if row["supported_total"] else 1.0
        ),
        "disposition_accuracy": row["correct"] / row["n"],
        "history_reopen_accuracy": (
            row["history_correct"] / row["history_cases"] if row["history_cases"] else 1.0
        ),
    }


def shipped_bench() -> dict[str, Any]:
    return bench(shipped_input())


def _strongest(summary: Mapping[str, Any]) -> str:
    return max(BASELINE_ARMS, key=lambda arm: summary[arm]["disposition_accuracy"])


def _ablations_worse(summary: Mapping[str, Any]) -> float:
    full = summary["ORION_RSE_FULL"]
    return float(
        sum(
            1
            for arm in ABLATION_ARMS
            if summary[arm]["false_promotion_rate"] > 0.0
            or summary[arm]["disposition_accuracy"] < full["disposition_accuracy"]
        )
    )


#: Each gate's statistic, read off a run's ``summary``. Counts and rates rather
#: than the generator's booleans: a gate reported as ``false`` says nothing about
#: how far from the threshold the run landed, and the distance is the finding.
READINGS: Mapping[str, Any] = {
    "full_zero_false_promotion": lambda s: s["ORION_RSE_FULL"]["false_promotion_rate"],
    "full_useful_discovery_recall_one": lambda s: s["ORION_RSE_FULL"]["useful_discovery_recall"],
    "strongest_baseline_false_promotion_ge_0_05": lambda s: s[_strongest(s)][
        "false_promotion_rate"
    ],
    "accuracy_gain_ge_0_08": lambda s: s["ORION_RSE_FULL"]["disposition_accuracy"]
    - s[_strongest(s)]["disposition_accuracy"],
    "each_ablation_worse": _ablations_worse,
    "history_reopen_exact": lambda s: s["ORION_RSE_FULL"]["history_reopen_accuracy"],
    "matched_decision_budget": lambda s: float(
        len({s[arm]["decision_budget_checks"] for arm in ARMS})
    ),
}

#: The seven preregistered gates, transcribed from the protocol's positive
#: terminal. The thresholds are the frozen ones; nothing here is relaxed.
GATES: tuple[PreregisteredGate, ...] = (
    PreregisteredGate(
        gate_id="full_zero_false_promotion",
        reads="ORION_RSE_FULL false promotion rate",
        threshold=0.0,
        direction=GateDirection.AT_MOST,
    ),
    PreregisteredGate(
        gate_id="full_useful_discovery_recall_one",
        reads="ORION_RSE_FULL useful discovery recall",
        threshold=1.0,
    ),
    PreregisteredGate(
        gate_id="strongest_baseline_false_promotion_ge_0_05",
        reads="strongest non-ORION baseline false promotion rate",
        threshold=0.05,
        role=GateRole.PRECONDITION,
    ),
    PreregisteredGate(
        gate_id="accuracy_gain_ge_0_08",
        reads="ORION_RSE_FULL disposition accuracy minus the strongest baseline's",
        threshold=0.08,
    ),
    PreregisteredGate(
        gate_id="each_ablation_worse",
        reads="registered ablations that add a false promotion or a disposition error",
        threshold=4.0,
    ),
    PreregisteredGate(
        gate_id="history_reopen_exact",
        reads="ORION_RSE_FULL retained-negative / reopen accuracy",
        threshold=1.0,
    ),
    PreregisteredGate(
        gate_id="matched_decision_budget",
        reads="distinct decision-budget receipts across the nine arms",
        threshold=1.0,
        direction=GateDirection.AT_MOST,
    ),
)


def fact_space() -> tuple[ModelPoint, ...]:
    """Every assignment of the eight case facts: the space the policies are rules over."""

    return tuple(
        dict(zip(FACT_FIELDS, bits)) for bits in itertools.product((False, True), repeat=8)
    )


def reachable_states() -> tuple[ModelPoint, ...]:
    """The 144 states ``make_case`` can actually emit.

    ``donor_owned``, ``interaction_only`` and ``live_negative_history`` are drawn
    as ``positive and rng.random() < rate``, so a null observation forces all
    three false and 112 of the 256 assignments never occur. Measuring the arms
    over the full cube would credit them for states the benchmark cannot present.
    """

    return tuple(
        state
        for state in fact_space()
        if state["positive"]
        or not (
            state["donor_owned"] or state["interaction_only"] or state["live_negative_history"]
        )
    )


def arm_rule(arm: str) -> Any:
    """The shipped ``policy`` for one arm, as a rule over a fact state."""

    module = bench_module()
    return lambda point: module.policy(arm, dict(point))


def gold_rule() -> Any:
    module = bench_module()
    return lambda point: module.gold(dict(point))


def orion_arm_divergence() -> TheoryDivergence:
    """How far the graded ORION arm departs from the gold that grades it.

    ``policy("ORION_RSE_FULL", c)`` is ``return gold(c)``. The measurement is
    reported rather than the source line because the number is what composes:
    zero divergent points is
    :class:`orion.study.p3.treatment_contrast.TreatmentContrast`'s identity arm,
    and it is why three of the seven gates read a constant.
    """

    return divergence_of(
        arm_rule("ORION_RSE_FULL"),
        theory_id="ORION_RSE_FULL",
        reference=gold_rule(),
        space=fact_space(),
    )


def arm_error_states() -> dict[str, tuple[int, ...]]:
    """Indices, into :func:`reachable_states`, where each arm disagrees with gold."""

    gold = gold_rule()
    states = reachable_states()
    return {
        arm: tuple(
            index for index, state in enumerate(states) if arm_rule(arm)(state) != gold(state)
        )
        for arm in ARMS
    }


def baseline_error_nesting() -> bool:
    """True when one baseline's mistakes are a subset of every other's.

    The reason ``strongest_non_orion_baseline`` is not a comparison: the four
    rule baselines are nested refinements, so whichever one has the smallest
    error set wins the ``max`` for every family mixture with positive support,
    and the selection has no way to land anywhere else.
    """

    errors = {arm: set(indices) for arm, indices in arm_error_states().items()}
    smallest = min(BASELINE_ARMS, key=lambda arm: len(errors[arm]))
    return all(errors[smallest] <= errors[arm] for arm in BASELINE_ARMS)


def contrast_axis_sensitivity() -> tuple[AxisSensitivity, ...]:
    """Per-axis sensitivity of "the strongest baseline and the full contract disagree".

    Every axis moves the contrast on at most one sibling pair, because the
    contrast is one point of the space: the eight facts have to line up exactly
    for the two arms to differ at all.
    """

    errors = arm_error_states()
    orion = arm_rule("ORION_RSE_FULL")
    strongest = arm_rule(min(BASELINE_ARMS, key=lambda arm: len(errors[arm])))

    def contrast(point: ModelPoint) -> bool:
        return strongest(point) != orion(point)

    states = reachable_states()
    return tuple(axis_sensitivity(axis, reference=contrast, space=states) for axis in FACT_FIELDS)


def realized_rates(support: Mapping[str, tuple[float, float]], *, corner: str) -> dict[str, float]:
    """The family rate vector at one corner of a sampling support.

    ``main()`` mixes each family's draw half-and-half with :data:`BASE_MIXTURE`,
    so the reachable rates are a band around the base, not the declared range.
    """

    if corner not in {"low", "high"}:
        raise ValueError("a support corner is 'low' or 'high'")
    index = 0 if corner == "low" else 1
    return {key: 0.5 * support[key][index] + 0.5 * BASE_MIXTURE[key] for key in SUPPORT_KEYS}


def discriminator_prevalence(rates: Mapping[str, float]) -> float:
    """Probability of :data:`DISCRIMINATING_STATE` under one family rate vector.

    The eight facts are independent Bernoulli draws, so this is a product --- and
    since each factor is monotone in a different parameter, the supremum over a
    support box is attained at a corner and :func:`discriminator_supremum` can
    read it off without a search.
    """

    probability = 1.0
    for fact in FACT_FIELDS:
        rate = rates[FACT_RATE[fact]]
        fires = DISCRIMINATING_STATE[fact] ^ (fact in INVERTED_FACTS)
        probability *= rate if fires else 1.0 - rate
    return probability


def discriminator_supremum(support: Mapping[str, tuple[float, float]] | None = None) -> float:
    """Largest prevalence the discriminating state can take anywhere in a support."""

    ranges = SHIPPED_SUPPORT if support is None else support
    low = realized_rates(ranges, corner="low")
    high = realized_rates(ranges, corner="high")
    best = {
        key: (high[key] if _raises_prevalence(key) else low[key]) for key in SUPPORT_KEYS
    }
    return discriminator_prevalence(best)


def discriminator_infimum(support: Mapping[str, tuple[float, float]] | None = None) -> float:
    ranges = SHIPPED_SUPPORT if support is None else support
    low = realized_rates(ranges, corner="low")
    high = realized_rates(ranges, corner="high")
    worst = {key: (low[key] if _raises_prevalence(key) else high[key]) for key in SUPPORT_KEYS}
    return discriminator_prevalence(worst)


def _raises_prevalence(key: str) -> bool:
    """True when a larger rate makes the discriminating state more likely."""

    fact = next(name for name in FACT_FIELDS if FACT_RATE[name] == key)
    return DISCRIMINATING_STATE[fact] ^ (fact in INVERTED_FACTS)


def _skewed_support(share: float) -> dict[str, tuple[float, float]]:
    """The slice of each declared range that most favours the discriminator.

    ``share=0.0`` is the extremal corner, ``1.0`` the whole declared range. A
    draw anywhere in the returned box is a draw the frozen protocol permits, so
    an unattainable gate here is unattainable for the protocol.
    """

    out: dict[str, tuple[float, float]] = {}
    for key, (low, high) in SHIPPED_SUPPORT.items():
        span = (high - low) * share
        out[key] = (high - span, high) if _raises_prevalence(key) else (low, low + span)
    return out


def declared_worlds() -> tuple[AdmissibleWorld, ...]:
    """Runs the frozen P14A protocol admits, spanning its declared sampling support.

    The register has to be defensible in both directions. Too narrow and an
    unattainable gate is an artifact of the worlds nobody registered; one world
    outside the freeze and the gate is widened rather than measured. These five
    are the shipped draw, an alternate seed, and three nested sub-boxes of the
    declared ranges ending at the extremal corner --- every one of them a rate
    vector ``rng.uniform`` can return.
    """

    return (
        AdmissibleWorld(
            world_id="shipped-seed-draw",
            admits="the committed run: the declared ranges at seed 2026082114",
            payload=shipped_input(),
        ),
        AdmissibleWorld(
            world_id="alternate-seed-draw",
            admits="the declared ranges at another seed; the protocol fixes one seed but "
            "nothing about the benchmark distinguishes it",
            payload=BenchInput.of(seed=20260821),
        ),
        AdmissibleWorld(
            world_id="declared-range-upper-half",
            admits="each family rate drawn from the half of its declared range that "
            "favours the retained-negative discriminator",
            payload=BenchInput.of(_skewed_support(0.5)),
        ),
        AdmissibleWorld(
            world_id="declared-range-top-decile",
            admits="each family rate drawn from the most favourable tenth of its declared "
            "range; an unlikely draw, not an inadmissible one",
            payload=BenchInput.of(_skewed_support(0.1)),
        ),
        AdmissibleWorld(
            world_id="declared-range-corner",
            admits="every family pinned at the endpoint of its declared range that "
            "maximises the discriminator; the closure of the support, and an upper "
            "bound on every interior draw",
            payload=BenchInput.of(_skewed_support(0.0)),
        ),
    )


def gate_reaches() -> tuple[GateReach, ...]:
    """Each preregistered gate, measured against the worlds the protocol admits."""

    worlds = declared_worlds()
    return tuple(
        measure_gate_attainability(
            lambda run, gate_id=gate.gate_id: READINGS[gate_id](bench(run)["summary"]),
            gate=gate,
            worlds=worlds,
        )
        for gate in GATES
    )


def terminal_reach() -> TerminalReach:
    """How many terminals P14A's conjunction could print over its own support."""

    return measure_terminal_reach(gate_reaches(), label="P14A controlled governance terminal")


#: The two gates whose statistic the protocol's own declared sampling support
#: bounds. They are the two that failed, and they are one quantity: the strongest
#: baseline's only mistake is :data:`DISCRIMINATING_STATE`, so its false-promotion
#: rate and the full contract's accuracy gain over it are the same number.
#:
#: The other five read the arm sitting in the graded slot rather than the
#: benchmark, so a sampling-support interval would report a constant for them and
#: call it a ceiling. Their reach is measured over the world register in
#: :func:`gate_reaches` instead.
SUPPORT_BOUNDED_GATES: tuple[str, ...] = (
    "strongest_baseline_false_promotion_ge_0_05",
    "accuracy_gain_ge_0_08",
)


def declared_statistic_support() -> StatisticSupport:
    """The interval P14A's discriminator prevalence can occupy, before any seed is drawn.

    Everything this needs existed at freeze time: eight declared uniform ranges,
    the half-and-half mix with ``base``, and the eight independent Bernoulli
    draws in ``make_case``. Each factor of the product is monotone in a different
    declared parameter, so the extrema sit at corners of the box and the bound is
    exact rather than sampled.
    """

    return StatisticSupport(
        statistic=(
            "prevalence of the one fact state on which the strongest rule baseline and the "
            "full contract disagree, over the eight sampling ranges the frozen protocol "
            "declares"
        ),
        infimum=discriminator_infimum(),
        supremum=discriminator_supremum(),
        derivation=(
            "make_case draws the eight facts as independent Bernoulli variables whose rates "
            "are 0.5*sampled + 0.5*base; the state's prevalence is therefore a product of "
            "eight factors, each monotone in a different declared uniform, so its extrema "
            "over the declared box are attained at corners and are computed exactly by "
            "discriminator_infimum/discriminator_supremum without running the benchmark"
        ),
    )


def threshold_reaches() -> tuple[ThresholdReach, ...]:
    """P14A's two support-bounded thresholds against the interval they were frozen over."""

    support = declared_statistic_support()
    by_id = {gate.gate_id: gate for gate in GATES}
    return tuple(
        assess_threshold_support(by_id[gate_id], support=support)
        for gate_id in SUPPORT_BOUNDED_GATES
    )


def threshold_panel() -> ThresholdPanel:
    """The pre-run verdict: could P14A's two aggregate thresholds ever have been met?

    This is the check that would have cost a sentence at freeze time. It needs no
    seed, no run and no register of worlds --- only the thresholds and the
    protocol's own bound on the quantity they read --- and it returns ``FAIL``
    with margins of ``-0.007674`` and ``-0.037674``.
    """

    return assess_threshold_panel(
        threshold_reaches(), label="P14A aggregate superiority thresholds"
    )


#: Sampling supports the frozen protocol does **not** admit, in which the
#: retained-negative discriminator is common enough that the preregistered
#: ``0.08`` accuracy gap is not out of reach. They are the capability
#: measurement: if the terminal moves here, the emitter is a function of its run
#: and the published negative is about the reachable set, not about the branch.
def capability_cases() -> tuple[WithholdingCase, ...]:
    """Worlds in which the full contract should win, and the receipt should say so.

    Every one is registered because a reader can agree the positive terminal is
    warranted there: the disposition only the full contract can make is more
    common than the gap the protocol asks it to open. Sampling supports that
    raise the discriminator but leave it under ``0.08`` are not withholding
    cases --- the gate is correctly unmet in them --- and they are reported
    without a verdict by :func:`capability_curve`.
    """

    base = shipped_input()
    return (
        WithholdingCase(
            case_id="retained-negative-common",
            withholds="live negative history on nearly every positive and almost no "
            "material new discriminator; the one disposition the strongest baseline "
            "cannot make becomes ordinary",
            payload=base.with_ranges(history=(0.85, 0.95), new_evidence=(0.0, 0.05)),
        ),
        WithholdingCase(
            case_id="clean-packets-with-live-history",
            withholds="clean, identifiable, prospectively frozen packets whose only defect "
            "is an unreopened negative history; the governance contract's own case",
            payload=base.with_ranges(
                positive=(0.80, 0.95),
                bad_evidence=(0.0, 0.03),
                unfrozen=(0.0, 0.03),
                nonidentifiable=(0.0, 0.03),
                donor=(0.0, 0.05),
                interaction=(0.0, 0.05),
                history=(0.55, 0.75),
                new_evidence=(0.02, 0.10),
            ),
        ),
        WithholdingCase(
            case_id="balanced-retained-negative-strata",
            withholds="the retained-negative disposition carried by most cases, which is "
            "what P14B's successor protocol arranges by stratifying instead of "
            "leaving prevalence to an independent Bernoulli mixture",
            payload=base.with_ranges(
                positive=(0.9, 1.0),
                bad_evidence=(0.0, 0.02),
                unfrozen=(0.0, 0.02),
                nonidentifiable=(0.0, 0.02),
                donor=(0.0, 0.02),
                interaction=(0.0, 0.02),
                history=(0.9, 1.0),
                new_evidence=(0.0, 0.02),
            ),
        ),
    )


#: Sampling supports between the freeze and the capability register, ordered by
#: how prevalent they make the discriminator. Reported as data rather than as a
#: verdict: they are the dose curve that locates the ``0.08`` threshold relative
#: to the declared support's ceiling of ``0.042326``.
def capability_curve() -> tuple[tuple[str, float, float, str], ...]:
    """``(world, prevalence supremum, realized statistic, terminal)`` in increasing order."""

    base = shipped_input()
    ladder = {
        "declared-support": {},
        "material-reopening-rare": {"new_evidence": (0.02, 0.10)},
        "live-negative-history-common": {"history": (0.55, 0.75)},
        "history-common-and-reopening-rare": {
            "history": (0.55, 0.75),
            "new_evidence": (0.02, 0.10),
        },
    }
    rows = [
        (
            name,
            discriminator_supremum(base.with_ranges(**ranges).as_ranges()),
            receipt(base.with_ranges(**ranges))["strongest_baseline_false_promotion"],
            receipt(base.with_ranges(**ranges))["terminal"],
        )
        for name, ranges in ladder.items()
    ]
    rows += [
        (
            case.case_id,
            discriminator_supremum(case.payload.as_ranges()),
            receipt(case.payload)["strongest_baseline_false_promotion"],
            receipt(case.payload)["terminal"],
        )
        for case in capability_cases()
    ]
    return tuple(sorted(rows, key=lambda row: row[1]))


#: The receipt fields traced as evidence: the two quantities the failing gates
#: read, plus the two the passing ones do. They are what separates "the emitter
#: was never perturbed" from "it was perturbed and its terminal did not care".
RECEIPT_EVIDENCE: tuple[str, ...] = (
    "strongest_baseline_false_promotion",
    "accuracy_gain",
    "full_false_promotion",
    "full_history_reopen_accuracy",
)


def receipt(run: BenchInput) -> dict[str, Hashable]:
    """One run, flattened to the scalars a reader takes off the published receipt."""

    result = bench(run)
    summary = result["summary"]
    return {
        "terminal": result["terminal"],
        "strongest_non_orion_baseline": result["strongest_non_orion_baseline"],
        "strongest_baseline_false_promotion": READINGS[
            "strongest_baseline_false_promotion_ge_0_05"
        ](summary),
        "accuracy_gain": READINGS["accuracy_gain_ge_0_08"](summary),
        "full_false_promotion": READINGS["full_zero_false_promotion"](summary),
        "full_history_reopen_accuracy": READINGS["history_reopen_exact"](summary),
    }


def bench_responsiveness() -> ReceiptResponsiveness:
    """Whether the terminal is a function of the run at all, over inadmissible worlds.

    This is the half of the measurement that clears the generator. P8's terminal
    was a literal and no input moved it; P14A's moves, which is why the finding
    is about the preregistered support and not about the emitter.
    """

    return measure_receipt_responsiveness(
        receipt,
        label="P14A controlled governance receipt",
        baseline=shipped_input(),
        verdict_field="terminal",
        evidence_fields=RECEIPT_EVIDENCE,
        cases=capability_cases(),
    )


def seed_sweep(seeds: Sequence[int]) -> tuple[float, ...]:
    """The failing gates' statistic under repeated draws of the frozen protocol.

    Only the discriminator's realized frequency is computed: the two failing
    gates are both exactly that number, because the full contract is the gold
    function and the strongest baseline's only mistakes are this one state.
    """

    module = bench_module()
    out: list[float] = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        hits = 0
        for _ in range(module.N_FAMILIES):
            sampled = {key: float(rng.uniform(*SHIPPED_SUPPORT[key])) for key in SUPPORT_KEYS}
            rates = {key: 0.5 * sampled[key] + 0.5 * BASE_MIXTURE[key] for key in BASE_MIXTURE}
            for _ in range(module.N):
                if module.gold(module.make_case(rng, rates)) == "RETAIN_NEGATIVE":
                    hits += 1
        out.append(hits / (module.N_FAMILIES * module.N))
    return tuple(out)


__all__ = [
    "ABLATION_ARMS",
    "ARMS",
    "BASELINE_ARMS",
    "BASE_MIXTURE",
    "DISCRIMINATING_STATE",
    "FACT_FIELDS",
    "GATES",
    "POSITIVE_TERMINAL",
    "READINGS",
    "RECEIPT_EVIDENCE",
    "SHIPPED_RESULT_DIGEST",
    "SHIPPED_SUPPORT",
    "SHIPPED_TERMINAL",
    "SUPPORT_KEYS",
    "BenchInput",
    "arm_error_states",
    "arm_rule",
    "baseline_error_nesting",
    "bench",
    "bench_module",
    "bench_responsiveness",
    "capability_cases",
    "capability_curve",
    "contrast_axis_sensitivity",
    "declared_worlds",
    "discriminator_infimum",
    "discriminator_prevalence",
    "discriminator_supremum",
    "fact_space",
    "gate_reaches",
    "gold_rule",
    "orion_arm_divergence",
    "reachable_states",
    "realized_rates",
    "receipt",
    "seed_sweep",
    "shipped_bench",
    "shipped_input",
    "shipped_receipt",
    "terminal_reach",
    "SUPPORT_BOUNDED_GATES",
    "declared_statistic_support",
    "threshold_panel",
    "threshold_reaches",
]
