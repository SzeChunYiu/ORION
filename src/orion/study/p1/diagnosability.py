"""Is the responsibility for a residual *distinguishable* from the evidence at hand?

**ADDITIVE ONLY — P1 V1 is untouched.** Nothing in this module or in
``licensing`` modifies the frozen ORION-P1 V1 surface. ``PROTOCOL_V1.json``
(frozen at ``P1.hidden-formulation.v1.1``), ``cases.py``, ``contradiction.py``,
``observation.py``, the V1 results under ``papers/.../results/`` and the two
suite fingerprints they are bound to all remain exactly as they were. This
module is read-only with respect to every one of them: it consumes
``PublicView`` and the existing mechanical detector and writes nothing back.
No V1 number is recomputed, re-scored or re-reported here.

Why this exists
---------------

``NEAREST_WORK_MATRIX_V2.md`` records that after absorbing 33 neighbouring
mechanisms the only surviving Paper-I claim is a *licensing relation*: the type
of the diagnosed responsibility is what grants or withholds permission to
rewrite the formulation. Every neighbour (ARTS, Iris, MAST, Who&When) produces
a **descriptive label** for a failure; none attaches a **permission** to it.

A permission attached to a label is only as good as the label. So before
``licensing`` may issue anything, this module has to answer a prior question
the descriptive systems never have to ask: *given what has actually been
observed, are the responsibility classes distinguishable at all?* When they are
not, that is a **reported state** with a name — never a low-confidence guess
dressed up as an answer. This is the same discipline as
``kernel.hard_gates.HardGateState.CANNOT_CHECK`` and EA-Graph's ``unprovable``:
"nobody could tell" and "we can tell, and it is X" call for different actions,
and collapsing them destroys exactly the distinction that makes the gate worth
having.

What is deliberately *not* claimed
----------------------------------

The posterior below is a transparent counting model, not an inference engine.
It has one free structural constant — the prior carries the mass of exactly one
ignorant observation, spread uniformly over the hypothesis space — and every
decision threshold is *derived* from that constant and the size of the space
rather than chosen:

* a class is diagnosed only if it is the **unique** argmax, and
* its mass must exceed the mass of everything else combined.

No threshold in this module was selected by evaluating against P1 gold. There
is nothing here to tune: "more probable than all alternatives together" is a
statement about the posterior, not a knob.

Determinism
-----------

Evidence is canonically ordered (by id) and each item's supported classes are
canonically ordered (by ``Responsibility`` declaration order) at construction,
so two differently-ordered constructions of the same evidence set produce
byte-identical payloads. No set or frozenset is ever iterated into a payload.
Floats are rounded to a fixed precision and negative zero is normalised away.
"""

from __future__ import annotations

import hashlib
import math
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from enum import Enum

from orion.core.residuals import Responsibility
from orion.kernel.store import canonical_bytes

#: Additive V2 surface (issue #136): unconsumed by design until separately
#: execution-frozen. Being imported by a V1-frozen module is the defect here,
#: not being unconsumed — `orion.adoption` checks that direction.
ADOPTION_BOUNDARY = "V2_ADDITIVE"

SCHEMA_VERSION = "orion.p1.v2.diagnosability.v1"

# Decimal places every float in a payload is rounded to before serialisation.
# Byte-identity across machines is the requirement; six places is well inside
# the reproducible range of the arithmetic performed here and well outside the
# resolution any downstream decision uses.
PRECISION = 6

# The prior carries the weight of exactly one ignorant observation, spread
# uniformly over the hypothesis space. This is the single structural constant of
# the model and it is the reason the decision rules below need no thresholds:
# evidence must outweigh one unit of ignorance, and that unit is defined here.
PRIOR_TOTAL_MASS = 1.0

# The decisive boundary ``w = 1 - 2/n`` is generally not representable in
# binary floating point, so a posterior computed exactly at the derived floor
# can land a few ulp above one half. Confidence must come from evidence, not
# from rounding error, so the majority comparison absorbs float representation
# noise. The guard is orders of magnitude below any real evidence increment
# (the smallest increment the algebra distinguishes at ``PRECISION`` moves the
# posterior by roughly ``10**-PRECISION / 4``).
_HALF_REPRESENTATION_GUARD = 64.0 * sys.float_info.epsilon

# Canonical ordering for every serialisation and every summation. Declaration
# order, not alphabetical, so the payload reads in the taxonomy's own order.
ALL_RESPONSIBILITIES: tuple[Responsibility, ...] = tuple(Responsibility)
_RESPONSIBILITY_INDEX = {item: index for index, item in enumerate(ALL_RESPONSIBILITIES)}


# --------------------------------------------------------------------------
# Authority classes
# --------------------------------------------------------------------------


class AuthorityClass(str, Enum):
    """The coarse grouping over ``Responsibility`` that decides authority.

    The licensing invariant is stated over *these*, not over the eleven
    responsibilities: EVIDENCE and EXECUTION may never license a formulation or
    search-universe mutation, FORMULATION and SEARCH_UNIVERSE may license
    exactly one coordinate each, and METHOD may license nothing at all because
    method revision is a governed Self-ORION transition rather than a Paper-I
    operation.

    ``Responsibility`` stays the unit of the posterior (the paper's
    "responsibility class") because the licence has to name a *coordinate*, and
    the coordinate is only recoverable at that resolution. This enum is the
    quantifier the invariant ranges over.
    """

    EVIDENCE = "EVIDENCE"
    EXECUTION = "EXECUTION"
    FORMULATION = "FORMULATION"
    SEARCH_UNIVERSE = "SEARCH_UNIVERSE"
    METHOD = "METHOD"


# Total by construction; `test_licensing` asserts the totality, so a
# `Responsibility` member added later cannot silently fall into a permissive
# default. There is no `.get(...)` fallback anywhere in this module.
AUTHORITY_CLASS_BY_RESPONSIBILITY: dict[Responsibility, AuthorityClass] = {
    Responsibility.QUESTION: AuthorityClass.FORMULATION,
    Responsibility.REPRESENTATION: AuthorityClass.FORMULATION,
    Responsibility.DECOMPOSITION: AuthorityClass.FORMULATION,
    Responsibility.INTERFACE: AuthorityClass.FORMULATION,
    Responsibility.MEASUREMENT: AuthorityClass.FORMULATION,
    Responsibility.EVALUATOR: AuthorityClass.FORMULATION,
    # The suite labels a hidden *parent domain* SEARCH and a mis-scoped lookup
    # ROUTING; both move the active-domain set, which is the search universe.
    Responsibility.SEARCH: AuthorityClass.SEARCH_UNIVERSE,
    Responsibility.ROUTING: AuthorityClass.SEARCH_UNIVERSE,
    Responsibility.METHOD: AuthorityClass.METHOD,
    Responsibility.EVIDENCE: AuthorityClass.EVIDENCE,
    Responsibility.EXECUTION: AuthorityClass.EXECUTION,
}

# The two classes the licensing invariant permits to mutate W or M. Written as
# a named set because it is the thing the invariant quantifies over.
MUTATION_BEARING_CLASSES: frozenset[AuthorityClass] = frozenset(
    {AuthorityClass.FORMULATION, AuthorityClass.SEARCH_UNIVERSE}
)


def authority_class_of(responsibility: Responsibility) -> AuthorityClass:
    """Classify a responsibility, refusing rather than defaulting.

    A ``KeyError`` here means the taxonomy grew and this table did not. That is
    a defect to fix, not a case to fall through: an unclassified responsibility
    with a permissive default is precisely how an evidence diagnosis would
    acquire a rewrite licence.
    """

    try:
        return AUTHORITY_CLASS_BY_RESPONSIBILITY[responsibility]
    except KeyError as error:  # pragma: no cover - guarded by a totality test
        raise ValueError(
            f"{responsibility!r} has no authority class; the table is incomplete"
        ) from error


# --------------------------------------------------------------------------
# Numeric helpers
# --------------------------------------------------------------------------


def _rounded(value: float) -> float:
    """Round for serialisation and normalise ``-0.0`` to ``0.0``.

    ``-0.0`` serialises as ``-0.0`` and would break byte-identity between two
    runs that reached the same number by different summation orders.
    """

    return round(value, PRECISION) + 0.0


def shannon_entropy(masses: Sequence[float]) -> float:
    """Entropy in bits. Zero-mass outcomes contribute nothing, by convention."""

    total = 0.0
    for mass in masses:
        if mass > 0.0:
            total -= mass * math.log2(mass)
    return total


def minimum_decisive_weight(space_size: int) -> float:
    """The evidence weight at which one observation alone diagnoses a class.

    Derived, not chosen. With a prior of ``PRIOR_TOTAL_MASS`` spread uniformly
    over ``n`` classes, a single item of weight ``w`` supporting one class gives
    that class ``(w + 1/n) / (w + 1)``, which exceeds one half exactly when
    ``w > 1 - 2/n``.

    For ``n == 2`` the bound is ``0``: with only two hypotheses on the table any
    positive evidence is decisive, which is a true statement about a two-way
    question and a reason not to pose one.
    """

    if space_size < 2:
        raise ValueError("a hypothesis space smaller than two decides nothing")
    return PRIOR_TOTAL_MASS - (2.0 * PRIOR_TOTAL_MASS) / float(space_size)


# --------------------------------------------------------------------------
# Evidence
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class EvidenceItem:
    """One observation, and which responsibility classes it speaks for.

    ``supports`` may name more than one class. That is not a defect: the
    boundary rules in ``contradiction`` genuinely cannot separate INTERFACE from
    DECOMPOSITION on public text, and an item that says so raises entropy
    instead of manufacturing a choice.

    ``weight`` is the strength of the observation in ``[0, 1]``. It is *not* a
    probability and is not normalised across items; it is the amount of
    counting-mass the observation contributes, against a prior worth one unit.
    """

    evidence_id: str
    supports: tuple[Responsibility, ...]
    weight: float
    source: str = "observation"
    citation: str = ""

    def __post_init__(self) -> None:
        if not self.evidence_id.strip():
            raise ValueError("an evidence item needs an id")
        if not self.supports:
            raise ValueError(
                f"{self.evidence_id}: evidence that supports no class is not evidence"
            )
        if not 0.0 <= self.weight <= 1.0:
            raise ValueError(
                f"{self.evidence_id}: weight {self.weight!r} is outside [0, 1]"
            )
        if not self.source.strip():
            raise ValueError(f"{self.evidence_id}: evidence must name its source")
        # Canonicalise so two permutations of the same evidence are the same
        # object for every downstream purpose, including serialisation.
        canonical = tuple(
            sorted(dict.fromkeys(self.supports), key=_RESPONSIBILITY_INDEX.__getitem__)
        )
        object.__setattr__(self, "supports", canonical)

    @property
    def authority_classes(self) -> tuple[AuthorityClass, ...]:
        return tuple(
            dict.fromkeys(authority_class_of(item) for item in self.supports)
        )

    def to_payload(self) -> dict:
        return {
            "evidence_id": self.evidence_id,
            "supports": [item.value for item in self.supports],
            "weight": _rounded(self.weight),
            "source": self.source,
            "citation": self.citation,
        }


def evidence_fingerprint(evidence: Sequence[EvidenceItem]) -> str:
    """Content hash of an evidence set, order-independent.

    A posterior is only interpretable against the evidence it was computed
    from. ``licensing`` binds a licence to this digest for the same reason
    ``hard_gates`` binds an observation to a contract fingerprint: otherwise a
    decision can be replayed against evidence that was edited afterwards.
    """

    payloads = sorted(
        (item.to_payload() for item in evidence), key=lambda item: item["evidence_id"]
    )
    return hashlib.sha256(canonical_bytes(payloads)).hexdigest()


# --------------------------------------------------------------------------
# Probes
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Probe:
    """An action that would produce discriminating evidence, and its reach.

    ``discriminates`` is the set of classes the probe can tell apart. A probe
    that discriminates nothing is the **blind probe** negative control: its
    expected information gain is exactly zero, by the arithmetic rather than by
    a special case.

    ``reliability`` is ``P(the probe reports r | r is the responsibility)`` for
    ``r`` inside its reach. Outside its reach the probe reports nothing, which
    is itself informative — a probe with chance reliability still separates "in
    reach" from "out of reach".
    """

    probe_id: str
    discriminates: tuple[Responsibility, ...] = ()
    reliability: float = 1.0
    cost: int = 1
    description: str = ""

    def __post_init__(self) -> None:
        if not self.probe_id.strip():
            raise ValueError("a probe needs an id")
        if not 0.0 < self.reliability <= 1.0:
            raise ValueError(
                f"{self.probe_id}: reliability {self.reliability!r} is outside (0, 1]"
            )
        if self.cost < 1:
            raise ValueError(f"{self.probe_id}: a probe costs at least one unit")
        canonical = tuple(
            sorted(
                dict.fromkeys(self.discriminates), key=_RESPONSIBILITY_INDEX.__getitem__
            )
        )
        object.__setattr__(self, "discriminates", canonical)

    @property
    def blind(self) -> bool:
        return not self.discriminates

    def observe(self, observed: Responsibility | None) -> EvidenceItem | None:
        """Turn a probe outcome into evidence, refusing an out-of-scope claim.

        ``None`` is the inconclusive outcome and yields no evidence — a probe
        that saw nothing must not be recorded as having seen something weak.
        A probe reporting a class outside its declared reach is a malformed
        instrument, not a weak reading, and is refused up front.
        """

        if observed is None:
            return None
        if observed not in self.discriminates:
            raise ValueError(
                f"{self.probe_id}: reported {observed.value}, which is outside its "
                "declared reach"
            )
        return EvidenceItem(
            evidence_id=f"probe:{self.probe_id}",
            supports=(observed,),
            weight=self.reliability,
            source=f"probe:{self.probe_id}",
            citation=self.description,
        )

    def to_payload(self) -> dict:
        return {
            "probe_id": self.probe_id,
            "discriminates": [item.value for item in self.discriminates],
            "reliability": _rounded(self.reliability),
            "cost": self.cost,
            "description": self.description,
            "blind": self.blind,
        }


# --------------------------------------------------------------------------
# Posterior
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ResponsibilityPosterior:
    """A distribution over responsibility classes, and what produced it."""

    hypothesis_space: tuple[Responsibility, ...]
    masses: tuple[tuple[Responsibility, float], ...]
    entropy_bits: float
    max_entropy_bits: float
    evidence_fingerprint: str

    def mass(self, responsibility: Responsibility) -> float:
        for item, value in self.masses:
            if item is responsibility:
                return value
        return 0.0

    @property
    def ranked(self) -> tuple[tuple[Responsibility, float], ...]:
        """Highest mass first, ties broken by declaration order.

        The tie-break is only for display: every decision rule below treats a
        tie as a tie and refuses, so nothing rides on which member of a tied set
        appears first.
        """

        return tuple(
            sorted(
                self.masses,
                key=lambda item: (-item[1], _RESPONSIBILITY_INDEX[item[0]]),
            )
        )

    @property
    def normalized_entropy(self) -> float:
        if self.max_entropy_bits <= 0.0:
            return 0.0
        return _rounded(self.entropy_bits / self.max_entropy_bits)

    def to_payload(self) -> dict:
        return {
            "hypothesis_space": [item.value for item in self.hypothesis_space],
            "masses": [[item.value, _rounded(value)] for item, value in self.masses],
            "entropy_bits": _rounded(self.entropy_bits),
            "max_entropy_bits": _rounded(self.max_entropy_bits),
            "normalized_entropy": self.normalized_entropy,
            "evidence_fingerprint": self.evidence_fingerprint,
        }


class DiagnosabilityState(str, Enum):
    """What the evidence supports, as a state rather than as a confidence.

    Six outcomes, and five of them are refusals with different remedies. That
    is the point: "the evidence set is malformed", "nothing was observed",
    "two observations disagree", "the observations do not separate these
    classes" and "the observations lean but do not carry" call for five
    different next actions, and a single scalar confidence would erase all of
    them.
    """

    INADMISSIBLE = "INADMISSIBLE"
    NO_EVIDENCE = "NO_EVIDENCE"
    CONFLICTING = "CONFLICTING"
    INDISTINGUISHABLE = "INDISTINGUISHABLE"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    DIAGNOSABLE = "DIAGNOSABLE"


@dataclass(frozen=True)
class DiagnosabilityReport:
    """The full diagnosis attempt, including why it failed when it did."""

    state: DiagnosabilityState
    posterior: ResponsibilityPosterior | None
    diagnosed: Responsibility | None
    reasons: tuple[str, ...] = ()
    indistinguishable_classes: tuple[Responsibility, ...] = ()
    conflicting_evidence_ids: tuple[str, ...] = ()
    evidence_fingerprint: str = ""

    @property
    def authority_class(self) -> AuthorityClass | None:
        if self.diagnosed is None:
            return None
        return authority_class_of(self.diagnosed)

    def to_payload(self) -> dict:
        return {
            "schema_version": SCHEMA_VERSION,
            "state": self.state.value,
            "diagnosed": self.diagnosed.value if self.diagnosed else "",
            "authority_class": (
                self.authority_class.value if self.authority_class else ""
            ),
            "reasons": list(self.reasons),
            "indistinguishable_classes": [
                item.value for item in self.indistinguishable_classes
            ],
            "conflicting_evidence_ids": list(self.conflicting_evidence_ids),
            "evidence_fingerprint": self.evidence_fingerprint,
            "posterior": self.posterior.to_payload() if self.posterior else None,
        }


def _admissibility_failures(
    evidence: Sequence[EvidenceItem], space: tuple[Responsibility, ...]
) -> tuple[str, ...]:
    """Settle admissibility before any mass is computed.

    Deliberately the same ordering discipline as ``evaluate_hard_gates``: a
    malformed question is refused before its numbers are consulted, because an
    inadmissible measurement is not a low measurement.

    The rule that matters is the last one. A caller who narrows the hypothesis
    space to exclude a class its own evidence points at would get a posterior
    concentrated on whatever remains — certainty manufactured by the shape of
    the question rather than by anything observed. That is refused outright.
    A narrowed space that still contains everything the evidence names is
    admissible; it inflates confidence, but it cannot move the argmax to a class
    no observation supports, which is what the licensing invariant depends on.
    """

    failures: list[str] = []
    if len(space) < 2:
        failures.append("hypothesis_space_degenerate")
    if len(set(space)) != len(space):
        failures.append("hypothesis_space_has_duplicates")
    seen: set[str] = set()
    for item in evidence:
        if item.evidence_id in seen:
            failures.append(f"duplicate_evidence_id:{item.evidence_id}")
        seen.add(item.evidence_id)
    allowed = set(space)
    for item in evidence:
        outside = [c.value for c in item.supports if c not in allowed]
        if outside:
            failures.append(
                f"evidence_outside_hypothesis_space:{item.evidence_id}:"
                + ",".join(sorted(outside))
            )
    return tuple(dict.fromkeys(failures))


def build_posterior(
    evidence: Sequence[EvidenceItem],
    *,
    space: tuple[Responsibility, ...] = ALL_RESPONSIBILITIES,
) -> ResponsibilityPosterior:
    """Counting model: one unit of prior ignorance plus the evidence mass.

    ``unnormalised(r) = PRIOR_TOTAL_MASS/n + sum over evidence of
    weight/len(supports) for the items that support r``.

    Splitting an item's weight across the classes it supports is what makes an
    item that cannot separate INTERFACE from DECOMPOSITION contribute to the
    pair without deciding between them.

    Evidence is summed in ``evidence_id`` order so that two differently-ordered
    constructions of the same set produce bit-identical masses.
    """

    ordered = sorted(evidence, key=lambda item: item.evidence_id)
    per_class = PRIOR_TOTAL_MASS / float(len(space))
    unnormalised = {item: per_class for item in space}
    for item in ordered:
        share = item.weight / float(len(item.supports))
        for responsibility in item.supports:
            unnormalised[responsibility] += share
    total = sum(unnormalised[item] for item in space)
    masses = tuple((item, unnormalised[item] / total) for item in space)
    return ResponsibilityPosterior(
        hypothesis_space=tuple(space),
        masses=masses,
        entropy_bits=shannon_entropy([value for _, value in masses]),
        max_entropy_bits=math.log2(len(space)),
        evidence_fingerprint=evidence_fingerprint(ordered),
    )


def _decisive_ids(
    evidence: Sequence[EvidenceItem], space_size: int
) -> tuple[EvidenceItem, ...]:
    """Items strong enough to diagnose a single class on their own.

    The bound comes from ``minimum_decisive_weight``, so it moves with the size
    of the hypothesis space and was not picked. An item that supports several
    classes is never decisive: it cannot single out one of them however strong
    it is.
    """

    floor = minimum_decisive_weight(space_size)
    return tuple(
        item
        for item in sorted(evidence, key=lambda entry: entry.evidence_id)
        if len(item.supports) == 1 and item.weight > floor
    )


def assess_diagnosability(
    evidence: Sequence[EvidenceItem],
    *,
    space: tuple[Responsibility, ...] = ALL_RESPONSIBILITIES,
) -> DiagnosabilityReport:
    """Decide whether the responsibility is distinguishable, and say why not.

    Order of checks, most specific first: inadmissible, then nothing observed,
    then observations that contradict one another, then observations that do
    not separate, then observations that lean without carrying. Only the last
    branch produces a diagnosis.
    """

    frozen = tuple(evidence)
    failures = _admissibility_failures(frozen, space)
    if failures:
        return DiagnosabilityReport(
            state=DiagnosabilityState.INADMISSIBLE,
            posterior=None,
            diagnosed=None,
            reasons=failures,
            evidence_fingerprint=evidence_fingerprint(frozen),
        )

    posterior = build_posterior(frozen, space=space)
    fingerprint = posterior.evidence_fingerprint

    if not frozen:
        return DiagnosabilityReport(
            state=DiagnosabilityState.NO_EVIDENCE,
            posterior=posterior,
            diagnosed=None,
            reasons=("no_observation_supports_any_class",),
            evidence_fingerprint=fingerprint,
        )

    # Conflict: two individually decisive observations pointing at different
    # authority classes. Checked before the tie test because a contradiction and
    # an ambiguity have different remedies — one is a reason to distrust an
    # instrument, the other a reason to run a probe.
    decisive = _decisive_ids(frozen, len(space))
    classes_seen: dict[AuthorityClass, list[str]] = {}
    for item in decisive:
        classes_seen.setdefault(item.authority_classes[0], []).append(item.evidence_id)
    if len(classes_seen) > 1:
        conflicting = tuple(
            evidence_id
            for authority in sorted(classes_seen, key=lambda entry: entry.value)
            for evidence_id in sorted(classes_seen[authority])
        )
        return DiagnosabilityReport(
            state=DiagnosabilityState.CONFLICTING,
            posterior=posterior,
            diagnosed=None,
            reasons=(
                "decisive_observations_disagree:"
                + ",".join(sorted(item.value for item in classes_seen)),
            ),
            conflicting_evidence_ids=conflicting,
            evidence_fingerprint=fingerprint,
        )

    ranked = posterior.ranked
    top_mass = ranked[0][1]
    tied = tuple(item for item, value in ranked if value >= top_mass - 10.0**-PRECISION)
    if len(tied) > 1:
        return DiagnosabilityReport(
            state=DiagnosabilityState.INDISTINGUISHABLE,
            posterior=posterior,
            diagnosed=None,
            reasons=(
                "classes_not_separated_by_available_evidence:"
                + ",".join(item.value for item in tied),
            ),
            indistinguishable_classes=tied,
            evidence_fingerprint=fingerprint,
        )

    # The derived confidence rule: the diagnosed class must be more probable
    # than every alternative combined. No threshold is chosen; this is a
    # statement about the posterior.
    if top_mass <= 0.5 + _HALF_REPRESENTATION_GUARD:
        return DiagnosabilityReport(
            state=DiagnosabilityState.LOW_CONFIDENCE,
            posterior=posterior,
            diagnosed=None,
            reasons=(
                f"top_class_does_not_outweigh_the_alternatives:{_rounded(top_mass)}",
            ),
            evidence_fingerprint=fingerprint,
        )

    return DiagnosabilityReport(
        state=DiagnosabilityState.DIAGNOSABLE,
        posterior=posterior,
        diagnosed=ranked[0][0],
        reasons=(f"unique_argmax_outweighs_alternatives:{_rounded(top_mass)}",),
        evidence_fingerprint=fingerprint,
    )


# --------------------------------------------------------------------------
# Probe value
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ProbeValue:
    """What one probe would be worth against the current posterior."""

    probe_id: str
    expected_information_gain_bits: float
    prior_entropy_bits: float
    expected_posterior_entropy_bits: float
    cost: int
    blind: bool

    @property
    def gain_per_cost(self) -> float:
        return _rounded(self.expected_information_gain_bits / float(self.cost))

    def to_payload(self) -> dict:
        return {
            "probe_id": self.probe_id,
            "expected_information_gain_bits": _rounded(
                self.expected_information_gain_bits
            ),
            "prior_entropy_bits": _rounded(self.prior_entropy_bits),
            "expected_posterior_entropy_bits": _rounded(
                self.expected_posterior_entropy_bits
            ),
            "cost": self.cost,
            "blind": self.blind,
            "gain_per_cost": self.gain_per_cost,
        }


def _probe_likelihood(
    probe: Probe, truth: Responsibility, outcome: Responsibility | None
) -> float:
    """``P(outcome | truth)`` under the declared instrument model.

    Inside the probe's reach the correct report has probability
    ``reliability`` and the remaining mass is spread uniformly over the other
    reachable classes *and* the inconclusive outcome. Outside its reach the
    probe reports inconclusive with certainty — which is why a probe that
    reaches nothing is worth exactly nothing, and why a probe with chance
    reliability is still worth something when the space is wider than its
    reach.
    """

    reach = probe.discriminates
    if truth not in reach:
        return 1.0 if outcome is None else 0.0
    if outcome is truth:
        return probe.reliability
    return (1.0 - probe.reliability) / float(len(reach))


def expected_information_gain(posterior: ResponsibilityPosterior, probe: Probe) -> float:
    """Mutual information between the probe's report and the responsibility.

    Computed exactly by enumeration over the outcome space
    ``discriminates + {inconclusive}``; there is no sampling and no
    approximation, so the value is reproducible to the bit.
    """

    outside = [item for item in probe.discriminates if item not in posterior.hypothesis_space]
    if outside:
        raise ValueError(
            f"{probe.probe_id}: reaches {[item.value for item in outside]}, which is "
            "outside the hypothesis space the posterior was built over"
        )
    prior = posterior.masses
    outcomes: list[Responsibility | None] = [*probe.discriminates, None]
    expected = 0.0
    for outcome in outcomes:
        joint = [
            mass * _probe_likelihood(probe, item, outcome) for item, mass in prior
        ]
        evidence_mass = sum(joint)
        if evidence_mass <= 0.0:
            continue
        conditional = [value / evidence_mass for value in joint]
        expected += evidence_mass * shannon_entropy(conditional)
    return posterior.entropy_bits - expected


def rank_probes(
    posterior: ResponsibilityPosterior, probes: Iterable[Probe]
) -> tuple[ProbeValue, ...]:
    """Every probe's value, best first, ties broken by id for determinism."""

    values = []
    for probe in probes:
        gain = expected_information_gain(posterior, probe)
        values.append(
            ProbeValue(
                probe_id=probe.probe_id,
                expected_information_gain_bits=gain,
                prior_entropy_bits=posterior.entropy_bits,
                expected_posterior_entropy_bits=posterior.entropy_bits - gain,
                cost=probe.cost,
                blind=probe.blind,
            )
        )
    return tuple(
        sorted(
            values,
            key=lambda item: (
                -_rounded(item.expected_information_gain_bits),
                item.probe_id,
            ),
        )
    )


__all__ = [
    "ALL_RESPONSIBILITIES",
    "AUTHORITY_CLASS_BY_RESPONSIBILITY",
    "MUTATION_BEARING_CLASSES",
    "PRECISION",
    "PRIOR_TOTAL_MASS",
    "SCHEMA_VERSION",
    "AuthorityClass",
    "DiagnosabilityReport",
    "DiagnosabilityState",
    "EvidenceItem",
    "Probe",
    "ProbeValue",
    "ResponsibilityPosterior",
    "assess_diagnosability",
    "authority_class_of",
    "build_posterior",
    "evidence_fingerprint",
    "expected_information_gain",
    "minimum_decisive_weight",
    "rank_probes",
    "shannon_entropy",
]
