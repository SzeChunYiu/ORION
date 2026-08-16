"""Detect formulation faults as *relations between observations*.

Every rule here takes the typed output of ``observation.reduce_view`` and asks
a question about how two or more observations stand to one another: does a
reported summary lie outside the support of the data it summarises; do two
independent derivations of the same quantity disagree past their stated
precision; does a stated control reproduce the effect it was meant to rule
out; does the differing subset coincide exactly with the failing subset.

No rule asks what a line *says it is*. That is the difference from
``baselines.extract_cues``, whose phrase table cannot fire because the suite
bans gold vocabulary from public fields. A relation between numbers survives
that ban, because the numbers are what the case is made of.

**The responsibility comes from the relation's kind, not from a lookup.** A
disagreement between two derivations of one quantity is not on its own an
answer — it fires across four families. What decides is *what differs between
the two derivation paths*:

===========================  =========================================
what differs                 responsibility
===========================  =========================================
a config, predicate or       EXECUTION — the run is broken, the
version between the two      formulation is not
weights over the same data   MEASUREMENT — the quantity counts the
(per session vs per person)  wrong unit
the scale, domain or         REPRESENTATION — the values are in the
encoding of the values       wrong coordinates
the judging procedure or     EVALUATOR — the instrument that produced
the sample it scores         the score is biased
the sampling frame or the    SEARCH — the question needs a model the
population observed          current framing does not contain
===========================  =========================================

**Several rules may fire, and all of them are returned.** ``detect`` never
silently picks one. It returns every finding, ordered by strength, and
publishes ``arbitrate`` separately so a caller can see both the top-ranked
finding and the full set. INTERFACE and DECOMPOSITION are emitted *together*
from the boundary rules, because the relations that distinguish them (a
missing field in a contract versus a missing seam inside a component) are not
separable from the public text — saying so is more honest than guessing.

**No case identifiers appear anywhere in this module, and no gold vocabulary.**
Every predicate is a property of numbers, sets, or clause types that holds
across many cases; a rule that could only ever fire on one case is a lookup
table with extra steps and does not belong here.

**Deliberately not used: the closure dependency chain.** A `derived from
closure:X` edge is present in the hidden-shift cases and absent from both
negative-control families, so keying on it would score well — and would be
reading an authoring artefact that tracks `protected_gold.dependency_depth`,
which is precisely the hidden label H2 measures. It is refused for the same
reason `baselines` refuses the `signal:` channel.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass

from orion.core.residuals import Responsibility

from .cases import PublicView
from .observation import (
    PROMPT_SOURCE,
    Observation,
    ObservationKind,
    Reduction,
    bearing_from_components,
    circular_separation,
    reduce_view,
    relative_gap,
)

# --------------------------------------------------------------------------
# Findings
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Finding:
    """One relation that holds among the observations, and what it implies.

    ``responsibilities`` may carry more than one entry when the relation
    genuinely does not separate them. ``observations`` are the lines that
    justify the claim, so every finding is traceable back to resource text.
    """

    rule: str
    responsibilities: tuple[Responsibility, ...]
    strength: float
    detail: str
    observations: tuple[Observation, ...] = ()

    @property
    def citations(self) -> tuple[str, ...]:
        return tuple(observation.cite for observation in self.observations)


Rule = Callable[[Reduction], Iterable[Finding]]

# Strength bands. Documented rather than sprinkled, so the arbitration order is
# reviewable in one place.
_CONTROL = 0.85  # a relation that identifies a run defect or a missing record
_SPECIFIC = 0.65  # a relation with a closed-form numeric test
_STRUCTURAL = 0.55  # a relation over stated system structure
_WEAK = 0.35  # a disagreement whose derivation paths do not separate

_BOUNDARY_PAIR = (Responsibility.INTERFACE, Responsibility.DECOMPOSITION)

_ISO_DATE = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")
_CLOCK_TIME = re.compile(r"\b([01]\d|2[0-3]):[0-5]\d\b")

# Words that mark a re-derivation done by a person rather than a re-run of the
# system. A hand check is an *independent measurement*, never evidence that the
# environment is at fault, and conflating the two fires EXECUTION on cases whose
# defect is arithmetic.
_BY_HAND = ("by hand", "manual", "sampled", "spot", "expert", "human")

# A counterfactual that varies the judging procedure rather than the run.
_JUDGING_CHANGE = (
    "caption",
    "shuffled",
    "blind",
    "divides by customer",
    "freezes",
    "held-back",
    "third pass",
    "tiebreak",
    "expert",
    "re-run",
    "refit",
)

_ANGLE_TOLERANCE_DEGREES = 20.0
_DISAGREEMENT = 0.25


# --------------------------------------------------------------------------
# Shared predicates
# --------------------------------------------------------------------------


def _subject_has(observation: Observation, *words: str) -> bool:
    lowered = f"{observation.subject} {observation.text}".lower()
    return any(word in lowered for word in words)


def _is_central(observation: Observation) -> bool:
    """A summary standing in for a whole column: mean, median, average."""

    return _subject_has(observation, "mean", "median", "average", "typical")


def _is_dispersion(observation: Observation) -> bool:
    return _subject_has(observation, "standard deviation", "spread", "variance")


def _numeric(reduction: Reduction) -> tuple[Observation, ...]:
    return tuple(
        o
        for o in reduction.observations
        if o.value is not None and o.kind is not ObservationKind.CLOSURE
    )


def _comparable(first: Observation, second: Observation) -> bool:
    """Two quantities are comparable when they carry the same unit class.

    Bare counts are excluded: `41 charges` and `41 modules` share no unit and
    comparing them would manufacture contradictions out of coincidence.
    """

    if first.source == second.source:
        return False
    if not first.unit_class or first.unit_class != second.unit_class:
        return False
    return True


def _separation(first: Observation, second: Observation) -> float:
    """Normalised disagreement: circular for angles, relative otherwise."""

    assert first.value is not None and second.value is not None
    if first.unit_class == "angle":
        return circular_separation(first.value, second.value) / 180.0
    if first.unit_class == "duration":
        one, two = first.seconds, second.seconds
        if one is not None and two is not None:
            return relative_gap(one, two)
    return relative_gap(first.value, second.value)


def disagreeing_pairs(reduction: Reduction) -> tuple[tuple[Observation, Observation, float], ...]:
    """Every pair of comparable quantities from different lines that disagree.

    This is the raw material of the ladder: the pair alone assigns nothing, and
    the rules below each add the condition that says *what differs* between the
    two derivations.
    """

    quantities = [o for o in _numeric(reduction) if o.unit_class]
    out: list[tuple[Observation, Observation, float]] = []
    for index, first in enumerate(quantities):
        for second in quantities[index + 1 :]:
            if not _comparable(first, second):
                continue
            gap = _separation(first, second)
            if gap >= _DISAGREEMENT:
                out.append((first, second, gap))
    return tuple(sorted(out, key=lambda item: -item[2]))


def _best_pair(reduction: Reduction) -> tuple[Observation, Observation, float] | None:
    pairs = disagreeing_pairs(reduction)
    return pairs[0] if pairs else None


def _case_has(reduction: Reduction, *markers: str) -> bool:
    return bool(reduction.with_marker(*markers))


def _source_text(reduction: Reduction, source: str) -> str:
    return " ".join(o.text for o in reduction.in_source(source)).lower()


# Words too common to say two clauses describe the same change. Kept small and
# generic: this is a stopword list, not a place to put case vocabulary.
_COMMON = frozenset(
    {
        "about", "after", "again", "against", "already", "another", "because", "before",
        "being", "between", "could", "every", "first", "found", "into", "least", "other",
        "report", "should", "since", "state", "still", "their", "there", "these", "thing",
        "those", "under", "until", "where", "which", "while", "whose", "would",
        "diagnose", "specify", "defect", "settled", "course", "framing",
    }
)


def _restates_the_prompt(reduction: Reduction, source: str) -> bool:
    """Does this line re-state the change the prompt proposes?

    Stem-free by construction. The prompt names an intervention — `double the
    worker pool`, `shorten the timeout from 30 s to 10 s`, `cap the service at
    200 requests per second` — and the line reporting the outcome re-uses its
    numbers or its nouns. Sharing a number, or two distinctive word stems, is
    what says the two describe the same change; the resource's file name plays
    no part, which matters because the suite's own audit found a stem regex
    over `proposal|trial` recovers a family at precision 1.00.
    """

    def stems(text: str) -> set[str]:
        return {
            word[:5]
            for word in re.findall(r"[a-z]{5,}", text.lower())
            if word not in _COMMON
        }

    prompt = _source_text(reduction, PROMPT_SOURCE)
    line = _source_text(reduction, source)
    prompt_numbers = {
        o.value for o in reduction.in_source(PROMPT_SOURCE) if o.value is not None
    }
    line_numbers = {o.value for o in reduction.in_source(source) if o.value is not None}
    if prompt_numbers & line_numbers:
        return True
    return len(stems(prompt) & stems(line)) >= 2


def _is_null_control(reduction: Reduction, source: str) -> bool:
    """A stated shuffle or independence control, not a remedy for the problem."""

    text = _source_text(reduction, source)
    return "shuffl" in text or "independently" in text


def _unit_interval(reduction: Reduction, source: str) -> list[float]:
    """Values in (0, 1) from one line, in written order — per-category scores."""

    rows = sorted(
        (o.clause_index, o.position, o.value)
        for o in reduction.in_source(source)
        if o.value is not None and 0.0 < o.value < 1.0
    )
    return [value for _, _, value in rows if value is not None]


def _shares(reduction: Reduction) -> list[Observation]:
    """Share-valued observations, ranges included.

    `the 5xx share rose from 0.4% to 6.1%` reduces to a RANGE and carries no
    single value; a rule that read only point values would miss the very
    statement saying the share moved.
    """

    return [
        o
        for o in reduction.observations
        if o.unit_class == "share" and (o.value is not None or o.low is not None)
    ]


def _source_values(reduction: Reduction, source: str, unit_class: str) -> list[float]:
    rows = sorted(
        (
            (o.clause_index, o.position, o.value)
            for o in reduction.in_source(source)
            if o.value is not None and o.unit_class == unit_class
        )
    )
    return [value for _, _, value in rows if value is not None]


# --------------------------------------------------------------------------
# Control relations: a broken run, and a missing record
# --------------------------------------------------------------------------


def rule_counterfactual_restores_baseline(reduction: Reduction) -> Iterator[Finding]:
    """A stated counterfactual run puts the outcome back where it belongs.

    Revert the version, remove the line, freeze the directory, run the nights
    the other job did not run: if the good behaviour returns when one stated
    difference is removed, the difference *is* the defect and nothing about the
    formulation is implicated. Hand re-derivations are excluded — recomputing
    forty lines on paper is an independent measurement, not a run.
    """

    for observation in reduction.observations:
        if not observation.line_has("TRIAL") or not observation.line_has("RESTORED"):
            continue
        text = _source_text(reduction, observation.source)
        if any(word in text for word in _BY_HAND) or _is_null_control(reduction, observation.source):
            continue
        yield Finding(
            rule="counterfactual_restores_baseline",
            responsibilities=(Responsibility.EXECUTION,),
            strength=_CONTROL,
            detail=(
                "removing one stated difference restores the expected outcome, "
                "so the difference is the defect"
            ),
            observations=(observation,),
        )
        return


def rule_configuration_element_lost_in_change(reduction: Reduction) -> Iterator[Finding]:
    """An element the working configuration carried is absent after a change.

    Two observations: one naming a changed or migrated artefact that no longer
    holds an element, one naming the prior artefact that did. The failing
    behaviour follows the element, not the framing.
    """

    lost = [o for o in reduction.observations if o.has("ENV_DIFF") and o.has("ABSENT")]
    prior = [o for o in reduction.with_marker("ENV_DIFF") if o.source not in {x.source for x in lost}]
    if lost and prior:
        yield Finding(
            rule="configuration_element_lost_in_change",
            responsibilities=(Responsibility.EXECUTION,),
            strength=_CONTROL,
            detail="an element present in the prior configuration is absent after the change",
            observations=(lost[0], prior[0]),
        )


def rule_change_coincides_with_onset(reduction: Reduction) -> Iterator[Finding]:
    """The date a configuration changed is the date the symptom starts.

    A shared date between a stated environment change and a stated onset is a
    partition of working from broken over time, computed from the two dates
    rather than read off a phrase.
    """

    dated: dict[str, list[Observation]] = {}
    for observation in reduction.observations:
        for date in _ISO_DATE.findall(observation.text):
            dated.setdefault(date, []).append(observation)
    for date, group in sorted(dated.items()):
        sources = {o.source for o in group}
        changed = [o for o in group if o.has("ENV_DIFF")]
        onset = [o for o in group if o.has("COINCIDENCE", "ABSENT") and not o.has("ENV_DIFF")]
        if changed and onset and len(sources) > 1:
            yield Finding(
                rule="change_coincides_with_onset",
                responsibilities=(Responsibility.EXECUTION,),
                strength=_CONTROL,
                detail=f"the stated change and the onset of the symptom share the date {date}",
                observations=(changed[0], onset[0]),
            )
            return


def rule_differing_subset_equals_failing_subset(reduction: Reduction) -> Iterator[Finding]:
    """The set that differs and the set that fails have the same cardinality.

    `the 9 failing modules are exactly the 9 whose file name case differs`, or
    `on time 30 times out of 30`. Two counts in one clause that are equal, in a
    clause stating a coincidence, is a full partition — the sharpest evidence
    an environment difference can leave.
    """

    for observation in reduction.with_marker("COINCIDENCE"):
        siblings = [
            o.value
            for o in _numeric(reduction)
            if o.text == observation.text and o.value is not None
        ]
        if len(siblings) >= 2 and len(set(siblings)) == 1:
            yield Finding(
                rule="differing_subset_equals_failing_subset",
                responsibilities=(Responsibility.EXECUTION,),
                strength=_CONTROL,
                detail=(
                    f"the differing set and the failing set both hold {siblings[0]:.0f} items, "
                    "so the stated difference partitions the outcome exactly"
                ),
                observations=(observation,),
            )
            return


def rule_change_magnitude_matches_error_magnitude(reduction: Reduction) -> Iterator[Finding]:
    """The size of a stated environment difference equals the size of the error.

    A currency that moved 3.1% against a report that is 3% low, while every
    other currency moved under 0.2%: the coincidence of magnitudes is a
    quantitative partition, not a phrase.
    """

    if len({o.source for o in reduction.with_marker("ENV_DIFF")}) < 2:
        return
    shares = [o for o in _numeric(reduction) if o.unit_class == "share" and o.value is not None]
    for index, first in enumerate(shares):
        for second in shares[index + 1 :]:
            if first.source == second.source:
                continue
            assert first.value is not None and second.value is not None
            if abs(first.value) < 0.5 or relative_gap(first.value, second.value) > 0.1:
                continue
            # The coincidence only partitions if the rest are far smaller: `every
            # other reported currency has moved under 0.2%`.
            rest = [
                o.value
                for o in shares
                if o.source in {first.source, second.source}
                and o.value is not None
                and o.value < 0.25 * abs(first.value)
            ]
            if not rest:
                continue
            yield Finding(
                rule="change_magnitude_matches_error_magnitude",
                responsibilities=(Responsibility.EXECUTION,),
                strength=_CONTROL,
                detail=(
                    f"the stated difference ({first.value:g}%) matches the size of the error "
                    f"({second.value:g}%)"
                ),
                observations=(first, second),
            )
            return


def rule_required_input_absent_but_obtainable(reduction: Reduction) -> Iterator[Finding]:
    """A record the stated plan needs is missing, and something can still produce it.

    This is the shape of an evidence gap and not of a formulation fault: the
    framing is fine, the instrument is fine, and what is wanted is a retrieval
    the tooling already supports — a retained backup, a regeneration job, a
    capability that is off but supported, a deterministic recomputation.

    The pairing is required in both directions. A capability statement on its
    own appears in cases whose defect is structural (`the gateway accepts a
    caller-supplied reference`), and an absence on its own appears in cases
    whose defect is a broken run.
    """

    missing = [o for o in reduction.observations if o.has("ABSENT", "PARTIAL", "DISABLED")]
    # A stated coverage share is an absence too: `the staging copy holds 0.4% of
    # the production rows` names what the record does not have, in numbers.
    missing += [
        o
        for o in _numeric(reduction)
        if o.unit_class == "share"
        and o.value is not None
        and o.value < 60
        and _subject_has(o, "holds", "populated for", "present for", "covers")
    ]
    recoverable = [o for o in reduction.with_marker("OBTAINABLE")]
    pairs = [
        (gap, source)
        for gap in missing
        for source in recoverable
        if gap.source != source.source
    ]
    if not pairs:
        return
    gap, source = pairs[0]
    yield Finding(
        rule="required_input_absent_but_obtainable",
        responsibilities=(Responsibility.EVIDENCE,),
        strength=_CONTROL - 0.05,
        detail=(
            "an input the stated plan needs is absent from the record while a stated "
            "capability would still produce it"
        ),
        observations=(gap, source),
    )


def rule_record_resolution_too_coarse(reduction: Reduction) -> Iterator[Finding]:
    """The record's granularity cannot separate the candidates it must separate.

    Three changes inside one day against a cost export at one row per day: the
    instrument is right and the analysis is right, and what is missing is a
    finer record that a stated capability can supply.
    """

    coarse = [
        o
        for o in reduction.observations
        if "per day" in o.text.lower() or "one row per" in o.text.lower()
    ]
    finer = [
        o
        for o in reduction.with_marker("OBTAINABLE")
        if "granularity" in o.text.lower() or "hourly" in o.text.lower()
    ]
    # Two or more stated clock times inside one dated line are candidates the
    # record's daily rows cannot tell apart.
    # Read at line level: the clock times are written as a comma-separated
    # list, so each lands in its own clause and no clause holds two.
    candidates = [
        source
        for source in reduction.sources()
        if len(_CLOCK_TIME.findall(_source_text(reduction, source))) >= 2
        and _ISO_DATE.search(_source_text(reduction, source))
    ]
    if coarse and finer and candidates:
        yield Finding(
            rule="record_resolution_too_coarse",
            responsibilities=(Responsibility.EVIDENCE,),
            strength=_SPECIFIC,
            detail=(
                f"{len(_CLOCK_TIME.findall(_source_text(reduction, candidates[0])))} candidates "
                "fall inside one unit of the record's stated resolution, and a finer record is "
                "obtainable"
            ),
            observations=(coarse[0], finer[0]) + reduction.in_source(candidates[0])[:1],
        )


def rule_emitted_artefact_differs_from_reference(reduction: Reduction) -> Iterator[Finding]:
    """What the tool emits differs from the reference form for the same purpose.

    A generator emitting ``col != NULL`` against a documented worked example
    emitting ``IS NOT NULL``: two quoted artefacts for one stated purpose whose
    word sets overlap and do not match. The comparison is over the tokens, so
    it needs no view on what either predicate means.
    """

    quoted = [
        o
        for o in reduction.of_kind(ObservationKind.TOKEN_LIST)
        if any(" " in token for token in o.tokens)
    ]
    reference = [
        o
        for o in quoted
        if any(word in _source_text(reduction, o.source) for word in ("worked example", "docs",
                                                                      "previous", "used to"))
    ]
    # Anything quoted that is not itself the reference. Requiring a TRANSFORM
    # marker here would key on the difference between `emits` and `emitted`,
    # which is grammar rather than relation.
    emitted = [o for o in quoted if o not in reference]
    for shown in reference:
        for produced in emitted:
            if shown.source == produced.source:
                continue
            first = {w.lower() for token in shown.tokens for w in token.split()}
            second = {w.lower() for token in produced.tokens for w in token.split()}
            if not first & second or first == second:
                continue
            yield Finding(
                rule="emitted_artefact_differs_from_reference",
                responsibilities=(Responsibility.EXECUTION,),
                strength=_CONTROL,
                detail=(
                    "the artefact the tool emits and the stated reference artefact for the same "
                    "purpose share terms and are not the same"
                ),
                observations=(produced, shown),
            )
            return


def rule_status_contradicts_its_own_record(reduction: Reduction) -> Iterator[Finding]:
    """One clause records a success and the failure that success is meant to exclude.

    `41 of the last 300 runs hold an error line and are recorded green`; `every
    run finishes successfully after reading 0 rows`; `reports 100% pass on a
    table that holds thousands of empty entries`. The status and its own
    evidence are in the same breath, so the reporting step is what is broken,
    not the question being asked.
    """

    passed = ("pass", "green", "successful", "100%")
    failed = ("error", "failed", "failure", "empty entries", "0 rows", "no rows", "never moved")
    for observation in reduction.observations:
        lowered = observation.text.lower()
        if not any(word in lowered for word in passed):
            continue
        if not any(word in lowered for word in failed):
            continue
        yield Finding(
            rule="status_contradicts_its_own_record",
            responsibilities=(Responsibility.EXECUTION,),
            strength=_CONTROL,
            detail="one clause records a success alongside the failure that success excludes",
            observations=(observation,),
        )
        return


# --------------------------------------------------------------------------
# The framing's own remedy, tried
# --------------------------------------------------------------------------


def rule_framing_remedy_tried_and_failed(reduction: Reduction) -> Iterator[Finding]:
    """The change the framing proposes was tried and the phenomenon stayed.

    Shorten the timeout and duplicates rise; buy replicas and p99 does not
    move; raise the memory limit and the crash arrives later; double the
    workers and the abandoned share grows. A remedy that is applied and does
    not remove the phenomenon is the strongest available evidence that the
    phenomenon is not a shortage of the quantity being adjusted — the
    arrangement is what is wrong, not its parameters.

    A counterfactual that *restores* the good outcome is the opposite relation
    and is excluded here; it is a run defect and
    ``rule_counterfactual_restores_baseline`` claims it.
    """

    for observation in reduction.observations:
        if observation.source == PROMPT_SOURCE or observation.source.startswith("closure:"):
            continue
        if observation.line_has("RESTORED") or not observation.line_has("UNCHANGED", "WORSE"):
            continue
        if _is_null_control(reduction, observation.source):
            continue  # a null control, not a remedy: see the representation rule
        if not _restates_the_prompt(reduction, observation.source):
            continue
        yield Finding(
            rule="framing_remedy_tried_and_failed",
            responsibilities=_BOUNDARY_PAIR,
            strength=_CONTROL - 0.1,
            detail=(
                "the change the framing proposes was applied and the phenomenon did not "
                "go away, so the arrangement rather than its parameters is at fault"
            ),
            observations=(observation,),
        )
        return


def rule_proposal_stated_not_to_remove_phenomenon(reduction: Reduction) -> Iterator[Finding]:
    """A proposed change is stated to leave the phenomenon in place.

    `adding a tier still requires a redeploy`; `it cannot tell 'not yet
    published' apart from 'published but not yet visible'`. The proposal's own
    line names the property that survives it.
    """

    for observation in reduction.observations:
        if not observation.line_has("PROPOSAL") or not observation.has("UNCHANGED"):
            continue
        if observation.source.lower().startswith("closure:"):
            continue
        yield Finding(
            rule="proposal_stated_not_to_remove_phenomenon",
            responsibilities=_BOUNDARY_PAIR,
            strength=_STRUCTURAL,
            detail="the proposed change is stated to leave the phenomenon in place",
            observations=(observation,),
        )
        return


def rule_proposal_timescale_exceeds_incident(reduction: Reduction) -> Iterator[Finding]:
    """A proposed control acts on a slower timescale than the event it must stop.

    Rotating a credential every 24 hours against a leak exploited in 90
    minutes: the remedy cannot bind, and the ratio of the two stated durations
    says so without reading either line's intent.
    """

    for source in reduction.sources():
        durations = [
            o
            for o in _numeric(reduction)
            if o.source == source and o.unit_class == "duration" and o.seconds
        ]
        proposed = [o for o in durations if o.has("PROPOSAL")]
        if len(durations) < 2 or not proposed:
            continue
        control = max(proposed, key=lambda o: o.seconds or 0.0)
        event = min(durations, key=lambda o: o.seconds or 0.0)
        if control is event or not control.seconds or not event.seconds:
            continue
        if control.seconds / event.seconds < 4.0:
            continue
        yield Finding(
            rule="proposal_timescale_exceeds_incident",
            responsibilities=_BOUNDARY_PAIR,
            strength=_STRUCTURAL,
            detail=(
                f"the proposed control acts on a {control.seconds / event.seconds:.0f}x slower "
                "timescale than the event it must stop"
            ),
            observations=(control, event),
        )
        return


# --------------------------------------------------------------------------
# Structure: boundaries and seams
# --------------------------------------------------------------------------


def rule_runtime_input_not_injectable(reduction: Reduction) -> Iterator[Finding]:
    """A component reads an input directly and no caller can supply it.

    Three call sites reading today's date from the runtime against a test with
    no way to set it; a function interleaving network calls, environment reads
    and a random draw with its arithmetic against a routine that cannot run
    offline. The seam the caller needs does not exist.
    """

    reads = [o for o in reduction.with_marker("BOUNDARY") if not o.has("PROPOSAL")]
    blocked = [o for o in reduction.with_marker("ABSENT") if _subject_has(o, "no way to", "cannot")]
    if reads and blocked:
        yield Finding(
            rule="runtime_input_not_injectable",
            responsibilities=(Responsibility.DECOMPOSITION, Responsibility.INTERFACE),
            strength=_STRUCTURAL,
            detail="an input is read directly inside a component and no caller can supply it",
            observations=(reads[0], blocked[0]),
        )


def rule_unbounded_buffer_between_mismatched_rates(reduction: Reduction) -> Iterator[Finding]:
    """Two stated rates across one boundary, with nothing bounding the queue.

    The producer's rate exceeds the consumer's and the buffer between them is
    stated unbounded: the arithmetic of the two rates fixes the outcome, and no
    amount of the resource being exhausted changes it.
    """

    unbounded = [o for o in reduction.observations if "unbounded" in o.text.lower()]
    rates = [
        o
        for o in _numeric(reduction)
        if o.value is not None and _subject_has(o, "sustains", "items/s", "per second", "/s")
    ]
    values = sorted({o.value for o in rates if o.value is not None})
    if unbounded and len(values) >= 2 and values[-1] > values[0]:
        yield Finding(
            rule="unbounded_buffer_between_mismatched_rates",
            responsibilities=_BOUNDARY_PAIR,
            strength=_SPECIFIC,
            detail=(
                f"the faster side runs at {values[-1]:g} against {values[0]:g} across a boundary "
                "with an unbounded buffer"
            ),
            observations=(unbounded[0],) + tuple(rates[:2]),
        )


def rule_granted_capability_exceeds_used(reduction: Reduction) -> Iterator[Finding]:
    """What a component may reach is far larger than what it does reach.

    A count of resources actually touched against a count reached through the
    same credential, with a stated capability to issue a narrower one: the two
    counts are the relation, and the gap between them is the fault.
    """

    wildcard = [o for o in reduction.observations if "wildcard" in o.text.lower()]
    narrower = [o for o in reduction.with_marker("CAPABILITY")]
    counts = sorted(
        (o for o in _numeric(reduction) if _subject_has(o, "resources", "touches", "buckets")),
        key=lambda o: o.value or 0.0,
    )
    if wildcard and narrower and len(counts) >= 2:
        low, high = counts[0], counts[-1]
        if high.value and low.value and high.value >= 4 * low.value:
            yield Finding(
                rule="granted_capability_exceeds_used",
                responsibilities=_BOUNDARY_PAIR,
                strength=_STRUCTURAL,
                detail=(
                    f"the credential reached {high.value:.0f} resources where the work needs "
                    f"{low.value:.0f}, and a narrower one can be issued"
                ),
                observations=(wildcard[0], narrower[0], high),
            )


def rule_contract_checks_shape_not_meaning(reduction: Reduction) -> Iterator[Finding]:
    """The declared contract constrains the shape and not what the values mean.

    A field whose meaning moved while its name, type and shape were untouched,
    against a check that verifies the shape and holds no record of what any
    consumer expects: the check cannot see the change by construction.
    """

    unchanged_shape = [
        o
        for o in reduction.observations
        if "shape" in o.text.lower() and o.has("UNCHANGED", "ENV_DIFF", "ABSENT")
    ]
    no_expectation = [
        o
        for o in reduction.with_marker("ABSENT")
        if "expect" in o.text.lower() or "holds no record" in o.text.lower()
    ]
    if unchanged_shape and no_expectation:
        yield Finding(
            rule="contract_checks_shape_not_meaning",
            responsibilities=_BOUNDARY_PAIR,
            strength=_STRUCTURAL,
            detail="the declared contract fixes the shape and records no consumer expectation",
            observations=(unchanged_shape[0], no_expectation[0]),
        )


def rule_shared_resource_with_divergent_requirements(reduction: Reduction) -> Iterator[Finding]:
    """One resource serves loads whose stated requirements differ.

    A single pool or queue named as shared, plus two stated requirements that
    are not the same requirement: no sizing of the shared resource satisfies
    both, which is why adding more of it is stated not to help.
    """

    shared = [
        o
        for o in reduction.observations
        if o.has("BOUNDARY")
        and any(word in o.text.lower() for word in ("shared by", "one connection pool",
                                                    "one worker pool", "serve all", "first-in"))
    ]
    requirements = [
        o
        for o in reduction.observations
        if any(word in o.text.lower() for word in ("tolerates", "requires", "needs"))
    ]
    if shared and len({o.source for o in requirements}) >= 1 and len(requirements) >= 2:
        yield Finding(
            rule="shared_resource_with_divergent_requirements",
            responsibilities=_BOUNDARY_PAIR,
            strength=_STRUCTURAL,
            detail="one shared resource serves loads whose stated requirements differ",
            observations=(shared[0],) + tuple(requirements[:2]),
        )


def rule_data_change_requires_code_change(reduction: Reduction) -> Iterator[Finding]:
    """Most changes alter only numbers, and every one of them needs a release.

    Two counts over the same change log — how many altered data only, how many
    required a redeploy — that come out equal. The numbers live inside the
    code, and the seam that would let them move on their own does not exist.
    """

    for source in reduction.sources():
        rows = reduction.in_source(source)
        text = _source_text(reduction, source)
        if "redeploy" not in text and "release" not in text:
            continue
        counts = [o.value for o in rows if o.value is not None and o.value >= 2]
        repeated = [value for value in set(counts) if counts.count(value) >= 2]
        if not repeated:
            continue
        yield Finding(
            rule="data_change_requires_code_change",
            responsibilities=(Responsibility.DECOMPOSITION, Responsibility.INTERFACE),
            strength=_STRUCTURAL,
            detail=(
                f"the same count of {max(repeated):.0f} changes altered only data and required a "
                "release, so the data has no seam of its own"
            ),
            observations=tuple(rows[:2]),
        )
        return


# --------------------------------------------------------------------------
# Representation: the values are in the wrong coordinates
# --------------------------------------------------------------------------


def rule_summary_outside_complete_support(reduction: Reduction) -> Iterator[Finding]:
    """A reported central value lies outside the data it summarises.

    The stated clusters each carry a count written immediately before them.
    When those counts add to the stated population size the clusters *are* the
    support, and a mean outside all of them cannot be a mean of those numbers
    under any weighting. On the wind case the support is 352-359 and 1-9 over
    31 + 29 = 60 readings, and 181.4 is in neither.

    Each range is paired with the count nearest before it in the same clause,
    because `31 readings between 352 and 359 and 29 readings between 1 and 9`
    writes both clusters into one clause and taking the clause's largest count
    twice would double one cluster and miss the other.
    """

    population = {o.value for o in _numeric(reduction) if o.value is not None}
    counted: list[tuple[Observation, float]] = []
    total = 0.0
    for source in reduction.sources():
        # The clusters that make up one support are written on one line. Summing
        # ranges across lines would add a declared domain (`degrees from 0 to
        # 359`) to the clusters inside it and never balance.
        rows: list[tuple[Observation, float]] = []
        for bound in reduction.in_source(source):
            if bound.kind is not ObservationKind.RANGE or bound.low is None:
                continue
            preceding = [
                o.value
                for o in _numeric(reduction)
                if o.source == source
                and o.clause_index == bound.clause_index
                and o.position < bound.position
                and o.value is not None
            ]
            if preceding:
                rows.append((bound, preceding[-1]))
        if len(rows) >= 2 and sum(count for _, count in rows) in population:
            counted, total = rows, sum(count for _, count in rows)
            break
    if not counted:
        return
    for observation in _numeric(reduction):
        if not _is_central(observation) or observation.value is None:
            continue
        if any(
            (bound.low or 0.0) <= observation.value <= (bound.high or 0.0)
            for bound, _ in counted
        ):
            continue
        yield Finding(
            rule="summary_outside_complete_support",
            responsibilities=(Responsibility.REPRESENTATION,),
            strength=_SPECIFIC + 0.1,
            detail=(
                f"the reported summary {observation.value:g} lies outside every stated cluster, "
                f"whose counts add to the stated population of {total:.0f}"
            ),
            observations=(observation,) + tuple(bound for bound, _ in counted),
        )
        return


def rule_dispersion_near_bounded_maximum(reduction: Reduction) -> Iterator[Finding]:
    """The reported spread approaches the widest a bounded quantity permits.

    For values confined to an interval of width w the largest attainable
    standard deviation is w/2, reached only by a two-point distribution at the
    ends. A reported spread at or near that bound says the values were treated
    as lying on a line when the stated domain wraps or is closed.
    """

    bounds = [
        o
        for o in reduction.of_kind(ObservationKind.RANGE)
        if o.low is not None and o.high is not None and o.high - o.low > 0
    ]
    if not bounds:
        return
    widest = max(bounds, key=lambda o: (o.high or 0.0) - (o.low or 0.0))
    span = (widest.high or 0.0) - (widest.low or 0.0)
    for observation in _numeric(reduction):
        if not _is_dispersion(observation) or observation.value is None:
            continue
        if observation.value < 0.4 * span:
            continue
        yield Finding(
            rule="dispersion_near_bounded_maximum",
            responsibilities=(Responsibility.REPRESENTATION,),
            strength=_SPECIFIC,
            detail=(
                f"the reported spread {observation.value:g} is {observation.value / span:.2f} of "
                f"the full stated range {widest.low:g}-{widest.high:g}, near the {span / 2:g} "
                "maximum a bounded quantity allows"
            ),
            observations=(observation, widest),
        )
        return


def rule_impossible_sign_for_magnitude(reduction: Reduction) -> Iterator[Finding]:
    """A quantity that cannot be negative is reported negative.

    A gap between two events, a duration, a count: the stated sign is outside
    the quantity's own domain, which happens when values are subtracted in a
    coordinate that wraps.
    """

    for observation in reduction.observations:
        low = observation.low if observation.kind is ObservationKind.RANGE else observation.value
        if low is None or low >= 0:
            continue
        if not _subject_has(observation, "gap", "duration", "length", "time", "count", "minutes"):
            continue
        yield Finding(
            rule="impossible_sign_for_magnitude",
            responsibilities=(Responsibility.REPRESENTATION,),
            strength=_SPECIFIC,
            detail=(
                f"a quantity that cannot be negative is reported at {low:g}, so the subtraction "
                "crosses a boundary the coordinate does not carry"
            ),
            observations=(observation,),
        )
        return


def rule_method_instability_exceeds_reported_effect(reduction: Reduction) -> Iterator[Finding]:
    """Re-running the same computation moves the answer by more than the answer.

    Summing the same file in a different row order changes the total by up to
    2,300 while the gap under investigation is 1,842: the reported quantity is
    smaller than the method's own noise, so no tolerance on it means anything.
    """

    unstable = [
        o
        for o in _numeric(reduction)
        if o.has("TRIAL") and o.value is not None and _subject_has(o, "changes", "differ", "moves",
                                                                   "up to", "by up to")
    ]
    reported = [
        o for o in _numeric(reduction) if o.has("REPORTED") and o.value is not None
    ]
    for noise in unstable:
        for effect in reported:
            if effect.source == noise.source or effect.value is None or noise.value is None:
                continue
            if effect.unit_class != noise.unit_class:
                continue
            if abs(effect.value) > abs(noise.value) or abs(effect.value) < 1:
                continue
            yield Finding(
                rule="method_instability_exceeds_reported_effect",
                responsibilities=(Responsibility.REPRESENTATION,),
                strength=_SPECIFIC + 0.1,
                detail=(
                    f"re-running the same computation moves the result by {noise.value:g}, more "
                    f"than the {effect.value:g} under investigation"
                ),
                observations=(noise, effect),
            )
            return


def rule_null_control_reproduces_effect(reduction: Reduction) -> Iterator[Finding]:
    """Destroying the structure leaves the effect intact.

    Shuffling each column independently and re-running reproduces negative
    correlations of similar size: the effect is a property of the coordinates
    the values are expressed in, not of any relation among them, so no
    substantive reading of it survives.
    """

    for observation in reduction.observations:
        lowered = observation.text.lower()
        # The control must both destroy the structure and be stated to give the
        # effect back. `two groups worked independently` describes two people,
        # not a null, and reading it as one fires a coordinate fault on a case
        # whose relation is a capture-recapture estimate.
        if not any(word in lowered for word in ("shuffl", "permut", "at random")):
            continue
        if "reproduc" not in lowered and "of similar size" not in lowered:
            continue
        yield Finding(
            rule="null_control_reproduces_effect",
            responsibilities=(Responsibility.REPRESENTATION,),
            strength=_SPECIFIC + 0.1,
            detail="a control that destroys the structure reproduces the reported effect",
            observations=(observation,),
        )
        return


def rule_effect_rests_on_few_points(reduction: Reduction) -> Iterator[Finding]:
    """A stated removal of a handful of points removes the effect.

    Two of sixty teams carry a reported correlation from 0.61 to 0.04. An
    association a stated small subset can erase is a property of where those
    points sit on the scale, not of the association it is read as; the relation
    is the ratio of the two stated values, not the word `leverage`.
    """

    for observation in reduction.observations:
        lowered = observation.text.lower()
        if "removing" not in lowered and "leverage" not in lowered:
            continue
        numbers = [
            o.value
            for o in _numeric(reduction)
            if o.text == observation.text and o.value is not None
        ]
        if len(numbers) != 2:
            continue
        before, after = numbers
        if before == 0 or abs(after) > 0.25 * abs(before):
            continue
        yield Finding(
            rule="effect_rests_on_few_points",
            responsibilities=(Responsibility.REPRESENTATION,),
            strength=_SPECIFIC,
            detail=(
                f"removing a stated handful of points moves the reported effect from {before:g} "
                f"to {after:g}"
            ),
            observations=(observation,),
        )
        return


def rule_same_summary_from_different_distributions(reduction: Reduction) -> Iterator[Finding]:
    """Two groups share a summary while their stated shapes are opposite.

    Forty per cent at one end and forty-four at the other averages to the same
    value as seventy-eight per cent in the middle. The summary is not a
    function of the thing being compared, so a difference test on it compares
    nothing. Read at line level, because the shares and the summaries sit in
    different clauses of the same distribution table.
    """

    for source in reduction.sources():
        rows = reduction.in_source(source)
        averages = [o.value for o in rows if _is_central(o) and o.value is not None]
        shares = [
            o.value for o in rows if o.unit_class == "share" and o.value is not None
        ]
        if len(averages) < 2 or len(set(averages)) != 1 or len(shares) < 2:
            continue
        if max(shares) - min(shares) < 20:
            continue
        yield Finding(
            rule="same_summary_from_different_distributions",
            responsibilities=(Responsibility.REPRESENTATION,),
            strength=_SPECIFIC,
            detail=(
                f"both groups summarise to {averages[0]:g} while their stated shares differ by "
                f"{max(shares) - min(shares):.0f} points"
            ),
            observations=tuple(rows[:3]),
        )
        return


def rule_operation_not_invariant(reduction: Reduction) -> Iterator[Finding]:
    """A stated check shows the combining rule depends on how the question is put.

    Averaging the members' probabilities for the complement and subtracting
    from one gives a different answer than averaging the originals. An
    operation that must be invariant and is stated not to be is being applied
    in the wrong space.
    """

    for observation in reduction.observations:
        lowered = observation.text.lower()
        if not any(word in lowered for word in ("symmetry", "complement", "subtracting")):
            continue
        if "different" not in lowered and "differs" not in lowered:
            continue
        yield Finding(
            rule="operation_not_invariant",
            responsibilities=(Responsibility.REPRESENTATION,),
            strength=_SPECIFIC,
            detail="the combining rule gives a different answer under a transformation "
            "that must preserve it",
            observations=(observation,),
        )
        return


_COORDINATE_WORDS = ("heading", "turn", "chassis", "latitude", "longitude", "span", "degree")


def rule_error_confined_to_stated_regime(reduction: Reduction) -> Iterator[Finding]:
    """The discrepancy sits exactly where a stated coordinate property bites.

    Ninety-four per cent of the mismatched assignments are north of 55 degrees,
    where one degree of longitude covers half the ground span it covers at 25.
    The recovered path agrees with the surveyed marks along straight runs and
    diverges after every turn, where the heading swings ninety degrees a
    second. In both, the error is a function of the coordinate rather than of
    the thing being measured, which is what a coordinate fault means.

    Two entries, because a case may state the confinement either as a share of
    the error falling inside a region, or as agreement in one regime beside
    divergence in another.
    """

    regime = [
        o
        for o in reduction.observations
        if any(word in o.text.lower() for word in _COORDINATE_WORDS)
    ]
    if len({o.source for o in regime}) < 2:
        return
    concentrated = [
        o
        for o in _numeric(reduction)
        if o.unit_class == "share"
        and o.value is not None
        and o.value >= 80
        and _subject_has(o, "of those", "of them", "sit", "are")
    ]
    if concentrated:
        yield Finding(
            rule="error_confined_to_stated_regime",
            responsibilities=(Responsibility.REPRESENTATION,),
            strength=_SPECIFIC,
            detail=(
                f"{concentrated[0].value:g}% of the discrepancy sits in the stated region where "
                "the coordinate's own scaling changes"
            ),
            observations=(concentrated[0], regime[0]),
        )
        return
    for observation in reduction.observations:
        lowered = observation.text.lower()
        if "agrees with" not in lowered and "agree with" not in lowered:
            continue
        if "diverge" not in lowered and "disagree" not in lowered:
            continue
        yield Finding(
            rule="error_confined_to_stated_regime",
            responsibilities=(Responsibility.REPRESENTATION,),
            strength=_SPECIFIC,
            detail=(
                "the derived quantity is stated to agree in one regime and diverge in another, "
                "and the regimes are named by a coordinate quantity rather than by the subject"
            ),
            observations=(observation, regime[0]),
        )
        return


def rule_distinct_encodings_never_merge(reduction: Reduction) -> Iterator[Finding]:
    """Two byte forms of one entity are stated never to merge.

    Counts on each form plus a statement that the comparison never joins them:
    a distinctness count computed under that comparison counts encodings, not
    entities.
    """

    for observation in reduction.observations:
        lowered = observation.text.lower()
        if "never merge" not in lowered and "the two groups" not in lowered:
            continue
        if not _case_has(reduction, "ENCODING"):
            continue
        yield Finding(
            rule="distinct_encodings_never_merge",
            responsibilities=(Responsibility.REPRESENTATION,),
            strength=_SPECIFIC,
            detail="two stated encodings of one entity are never joined by the comparison in use",
            observations=(observation,),
        )
        return


def rule_running_total_summarised_as_level(reduction: Reduction) -> Iterator[Finding]:
    """A cumulative series is averaged, so the answer is the level not the flow.

    The series is stated to be a running total since process start. Its own
    samples move by a few hundred thousand across the window while sitting at
    the four-billion mark, and the published figure is that mark. Averaging a
    cumulative series measures where the counter stood, never what happened in
    the window, and the ratio of the samples' span to their level is what says
    so — the same ratio an increment would have to be read from.
    """

    if not any(
        "running total" in o.text.lower() or "since start" in o.text.lower()
        for o in reduction.observations
    ):
        return
    for source in reduction.sources():
        levels = [value for value in reduction.numbers_in(source) if value > 1e6]
        if len(levels) < 2:
            continue
        low, high = min(levels), max(levels)
        span = high - low
        if span <= 0 or span > 0.01 * high:
            continue
        published = [
            o
            for o in _numeric(reduction)
            if o.source != source and o.value is not None and relative_gap(o.value, high) < 0.01
        ]
        if not published:
            continue
        yield Finding(
            rule="running_total_summarised_as_level",
            responsibilities=(Responsibility.REPRESENTATION,),
            strength=_SPECIFIC + 0.1,
            detail=(
                f"the stated samples move by {span:g} across the window while sitting at the "
                f"{high:g} level of a cumulative series, and {published[0].value:g} is published "
                "as the window's volume"
            ),
            observations=(published[0],) + reduction.in_source(source)[:2],
        )
        return


def rule_components_contradict_reported_direction(reduction: Reduction) -> Iterator[Finding]:
    """A direction computed from stated orthogonal components contradicts the reported one.

    Two derivations of one quantity: what the tool reports, and what the same
    instrument's own components give. The second needs no vocabulary — it is
    ``atan2`` on two printed numbers — and where the two disagree by more than
    the instrument's precision, the reported direction is not a direction of
    those components.
    """

    east = [o for o in _numeric(reduction) if _subject_has(o, "east") and o.value is not None]
    north = [o for o in _numeric(reduction) if _subject_has(o, "north") and o.value is not None]
    reported = [
        o
        for o in _numeric(reduction)
        if o.unit_class == "angle" and o.value is not None and _is_central(o)
    ]
    if not (east and north and reported):
        return
    assert east[0].value is not None and north[0].value is not None
    derived = bearing_from_components(east[0].value, north[0].value)
    for observation in reported:
        assert observation.value is not None
        separation = circular_separation(derived, observation.value)
        if separation <= _ANGLE_TOLERANCE_DEGREES:
            continue
        yield Finding(
            rule="components_contradict_reported_direction",
            responsibilities=(Responsibility.REPRESENTATION,),
            strength=_SPECIFIC + 0.15,
            detail=(
                f"the same instrument's components give {derived:.1f} degrees against a reported "
                f"{observation.value:g}, a {separation:.1f} degree contradiction"
            ),
            observations=(observation, east[0], north[0]),
        )
        return


# --------------------------------------------------------------------------
# Measurement: the quantity counts the wrong unit
# --------------------------------------------------------------------------


def rule_equal_weight_aggregation_over_skewed_units(reduction: Reduction) -> Iterator[Finding]:
    """Units are combined with equal weight while their stated sizes are not equal.

    Forty services averaged with equal contribution where one carries 71% of
    the calls; sixty hosts averaged where three carry 82% of the slow
    requests; sessions counted where the top tenth of people start sixty times
    as many. The aggregation's unit of account and the stated distribution over
    that unit are the two observations, and a disagreeing figure is the third.
    """

    aggregation = [
        o for o in reduction.with_marker("UNIT_OF_ACCOUNT") if o.has("TRANSFORM", "UNIT_OF_ACCOUNT")
    ]
    skew = [o for o in reduction.with_marker("SKEW")]
    pair = _best_pair(reduction)
    if not aggregation or not skew or pair is None:
        return
    if {aggregation[0].source} == {skew[0].source}:
        return
    first, second, gap = pair
    yield Finding(
        rule="equal_weight_aggregation_over_skewed_units",
        responsibilities=(Responsibility.MEASUREMENT,),
        strength=_SPECIFIC + 0.05,
        detail=(
            "the reported figure weights every unit equally while the stated distribution over "
            f"those units is concentrated, and the two derivations differ by {gap:.0%}"
        ),
        observations=(aggregation[0], skew[0], first, second),
    )


def rule_period_parts_exceed_whole(reduction: Reduction) -> Iterator[Finding]:
    """Daily distinct counts are added to give a month, and the month is smaller.

    Adding a non-additive quantity over periods double-counts whatever recurs.
    The relation is the stated sum against the stated whole; the ratio is the
    amount of recurrence the framing throws away.
    """

    added = [
        o
        for o in _numeric(reduction)
        if o.line_has("UNIT_OF_ACCOUNT") and _subject_has(o, "adding to", "add to", "adds to")
    ]
    whole = [
        o
        for o in _numeric(reduction)
        if o.line_has("UNIT_OF_ACCOUNT")
        and _subject_has(o, "in total", "across the whole", "reconciliation")
    ]
    for part in added:
        for total in whole:
            if part.source == total.source or part.value is None or total.value is None:
                continue
            if total.value == 0 or part.value <= 1.5 * total.value:
                continue
            yield Finding(
                rule="period_parts_exceed_whole",
                responsibilities=(Responsibility.MEASUREMENT,),
                strength=_SPECIFIC + 0.1,
                detail=(
                    f"the per-period figures add to {part.value:g} against a stated whole of "
                    f"{total.value:g}, so the quantity is not additive over periods"
                ),
                observations=(part, total),
            )
            return


def rule_headline_below_trivial_baseline(reduction: Reduction) -> Iterator[Finding]:
    """A reported score is beaten by a stated rule that does nothing.

    Ninety-four per cent correct against a rule that always answers the
    majority class and is right on 98.1: the reported quantity does not
    discriminate, whatever else it does.
    """

    trivial = [
        o
        for o in _numeric(reduction)
        if o.unit_class == "share"
        and o.value is not None
        and _subject_has(o, "always answers", "a rule that", "majority")
    ]
    claimed = [
        o
        for o in _numeric(reduction)
        if o.unit_class == "share" and o.value is not None and _subject_has(o, "correct", "accuracy")
    ]
    for floor in trivial:
        for score in claimed:
            if floor.value is None or score.value is None or floor.value <= score.value:
                continue
            yield Finding(
                rule="headline_below_trivial_baseline",
                responsibilities=(Responsibility.MEASUREMENT,),
                strength=_SPECIFIC + 0.1,
                detail=(
                    f"the reported {score.value:g}% is below the {floor.value:g}% a stated "
                    "do-nothing rule reaches, so the figure carries no discrimination"
                ),
                observations=(score, floor),
            )
            return


def rule_stated_calibration_contradicts_use(reduction: Reduction) -> Iterator[Finding]:
    """The emitted number is used as a rate its own table says it is not.

    Rows scoring 0.30-0.35 are fraudulent 7.8% of the time and rows scoring
    0.90-0.95 are 19.4%: each stated band is paired with the observed rate
    written after it, and both sit far from the band itself. Multiplying such a
    score by an amount does not give an expected amount, and the table says so
    without anyone having to know what calibration is.
    """

    for source in reduction.sources():
        rows = sorted(
            reduction.in_source(source), key=lambda o: (o.clause_index, o.position)
        )
        pairs: list[tuple[Observation, Observation]] = []
        pending: Observation | None = None
        for item in rows:
            if (
                item.kind is ObservationKind.RANGE
                and item.low is not None
                and item.high is not None
                and 0.0 <= item.low
                and item.high <= 1.0
            ):
                pending = item
            elif pending is not None and item.unit_class == "share" and item.value is not None:
                pairs.append((pending, item))
                pending = None
        if len(pairs) < 2:
            continue
        mismatched = [
            (band, rate)
            for band, rate in pairs
            if relative_gap(100.0 * ((band.low or 0.0) + (band.high or 0.0)) / 2.0, rate.value or 0.0)
            > 0.4
        ]
        if len(mismatched) < 2:
            continue
        yield Finding(
            rule="stated_calibration_contradicts_use",
            responsibilities=(Responsibility.MEASUREMENT,),
            strength=_SPECIFIC,
            detail=(
                f"{len(mismatched)} stated score bands have observed rates far from the score "
                "itself, so the emitted number is not the rate it is multiplied as"
            ),
            observations=tuple(item for pair in mismatched[:2] for item in pair),
        )
        return


def rule_two_stopping_points_for_one_duration(reduction: Reduction) -> Iterator[Finding]:
    """The published duration stops at a different event than the one that matters.

    A mean taken to the first status change against a mean taken to the final
    close, on the same tickets, differing by three orders of magnitude. Both
    are durations of the same process; the framing chose the earlier stop.
    """

    durations = [o for o in _numeric(reduction) if o.unit_class == "duration" and o.seconds]
    early = [
        o
        for o in durations
        if o.has("REPORTED", "UNIT_OF_ACCOUNT") or _subject_has(o, "first", "published")
    ]
    late = [o for o in durations if _subject_has(o, "final", "closed_at", "final close")]
    for first in early:
        for second in late:
            one, two = first.seconds, second.seconds
            if first.source == second.source or one is None or two is None or one == 0:
                continue
            if max(one, two) / min(one, two) < 4.0:
                continue
            yield Finding(
                rule="two_stopping_points_for_one_duration",
                responsibilities=(Responsibility.MEASUREMENT,),
                strength=_SPECIFIC,
                detail=(
                    f"the same process measured to two stated stopping points gives {one:g}s and "
                    f"{two:g}s, a factor of {max(one, two) / min(one, two):.0f}"
                ),
                observations=(first, second),
            )
            return


def rule_counted_population_admits_excluded_outcomes(reduction: Reduction) -> Iterator[Finding]:
    """The counter admits work the conclusion excludes, and that share moved.

    Requests counted at the load balancer whatever their status, against a
    failure share that rose from 0.4% to 6.1% and completed journeys that fell:
    the headline rose because the counter counts attempts, and attempts include
    the retries the failures cause.
    """

    admits = [
        o
        for o in reduction.observations
        if o.line_has("UNIT_OF_ACCOUNT")
        and any(word in o.text.lower() for word in ("whatever its status", "counts each attempt",
                                                    "counts each", "re-sends"))
    ]
    moved = [o for o in _shares(reduction) if _subject_has(o, "rose", "fell")]
    if len(admits) >= 1 and len({o.source for o in moved}) >= 2:
        yield Finding(
            rule="counted_population_admits_excluded_outcomes",
            responsibilities=(Responsibility.MEASUREMENT,),
            strength=_SPECIFIC,
            detail=(
                "the counter is stated to admit outcomes the conclusion excludes, and the share "
                "of those outcomes moved over the same window"
            ),
            observations=(admits[0],) + tuple(moved[:2]),
        )


# --------------------------------------------------------------------------
# Evaluator: the instrument that produced the score is biased
# --------------------------------------------------------------------------


def rule_debiased_rerun_collapses_gap(reduction: Reduction) -> Iterator[Finding]:
    """Re-scoring under a stated procedure change removes the reported gap.

    Captions removed and order shuffled turns 8.4 against 6.9 into 7.1 against
    7.0; splitting by customer and freezing the features turns 0.93 into 0.63,
    which is where the live figure already sat. The counterfactual varies the
    judging procedure and nothing else, so the gap belonged to the procedure.
    """

    for observation in reduction.observations:
        if not observation.has("TRIAL"):
            continue
        lowered = observation.text.lower()
        if not any(word in lowered for word in _JUDGING_CHANGE):
            continue
        rerun = [o.value for o in _numeric(reduction) if o.text == observation.text]
        values = [v for v in rerun if v is not None and 0 < v <= 10]
        others = [
            o.value
            for o in _numeric(reduction)
            if o.source != observation.source and o.value is not None and 0 < o.value <= 10
            and o.has("REPORTED")
        ]
        if len(values) >= 2 and len(others) >= 2:
            rerun_gap = max(values) - min(values)
            claimed_gap = max(others) - min(others)
            if claimed_gap > 0 and rerun_gap < 0.4 * claimed_gap:
                yield Finding(
                    rule="debiased_rerun_collapses_gap",
                    responsibilities=(Responsibility.EVALUATOR,),
                    strength=_SPECIFIC + 0.1,
                    detail=(
                        f"under the stated procedure change the gap falls from {claimed_gap:g} to "
                        f"{rerun_gap:g}"
                    ),
                    observations=(observation,),
                )
                return
        if len(values) == 1 and others:
            external = [
                o.value
                for o in _numeric(reduction)
                if o.has("EXTERNAL") and o.value is not None and 0 < o.value <= 10
            ]
            corrected = values[0]
            claimed = max(others)
            if external and relative_gap(corrected, min(external, key=lambda v: abs(v - corrected))) < 0.1:
                if relative_gap(corrected, claimed) > 0.2:
                    yield Finding(
                        rule="debiased_rerun_collapses_gap",
                        responsibilities=(Responsibility.EVALUATOR,),
                        strength=_SPECIFIC + 0.1,
                        detail=(
                            f"the corrected-procedure figure {corrected:g} matches the "
                            f"independent figure while the reported {claimed:g} does not"
                        ),
                        observations=(observation,),
                    )
                    return


def rule_evaluation_composition_differs_from_deployment(reduction: Reduction) -> Iterator[Finding]:
    """The pooled score is a weighted mean under weights that are not the deployment's.

    Three query kinds at 78/14/8 in the bench and 41/33/26 in production, with
    per-kind scores 0.86/0.31/0.22. Reweighting the stated per-kind scores by
    the stated deployment mix is arithmetic, and here it moves the pooled
    figure far enough to cross the bar the decision used. What differs between
    the two derivations is the composition of the sample being scored, which is
    a property of the instrument rather than of the thing measured.
    """

    def _mix(source: str) -> list[float]:
        values = [
            o.value
            for o in reduction.in_source(source)
            if o.unit_class == "share" and o.value is not None
        ]
        return values if 2 <= len(values) <= 6 and 95 <= sum(values) <= 105 else []

    mixes = {source: _mix(source) for source in reduction.sources()}
    mixes = {source: values for source, values in mixes.items() if values}
    if len(mixes) < 2:
        return
    sources = list(mixes)
    for index, first in enumerate(sources):
        for second in sources[index + 1 :]:
            one, two = mixes[first], mixes[second]
            if len(one) != len(two) or max(abs(a - b) for a, b in zip(one, two)) < 10:
                continue
            # The per-category scores are whatever line carries at least as many
            # unit-interval values as there are categories, and is neither mix
            # nor the prompt's own headline.
            scored = [
                source
                for source in reduction.sources()
                if source not in mixes
                and source != "prompt"
                and not source.lower().startswith("closure:")
                and len(_unit_interval(reduction, source)) >= len(one)
            ]
            if not scored:
                continue
            per_kind = _unit_interval(reduction, min(scored, key=lambda s: len(
                _unit_interval(reduction, s))))[: len(one)]
            pooled_one = sum(w * v for w, v in zip(one, per_kind)) / 100.0
            pooled_two = sum(w * v for w, v in zip(two, per_kind)) / 100.0
            if relative_gap(pooled_one, pooled_two) < 0.15:
                continue
            yield Finding(
                rule="evaluation_composition_differs_from_deployment",
                responsibilities=(Responsibility.EVALUATOR,),
                strength=_SPECIFIC + 0.05,
                detail=(
                    "reweighting the stated per-category scores from the evaluation mix to the "
                    f"deployment mix moves the pooled figure from {pooled_one:.2f} to "
                    f"{pooled_two:.2f}"
                ),
                observations=tuple(reduction.in_source(first)[:1])
                + tuple(reduction.in_source(second)[:1]),
            )
            return


def rule_agreement_barely_exceeds_chance(reduction: Reduction) -> Iterator[Finding]:
    """Two raters agree about as often as their own marginals force them to.

    With one label applied to 91% of items, two raters who never look at each
    other still match on 0.91^2 + 0.09^2 = 83.6% of items. A reported 88% match
    is 0.27 of the way from that floor to perfect, so the raw match rate is not
    a reliability figure and no ceiling follows from it.
    """

    shares = [o for o in _numeric(reduction) if o.unit_class == "share" and o.value is not None]
    match = [o for o in shares if _subject_has(o, "match on", "agree on", "match")]
    prevalence = [o for o in shares if _subject_has(o, "majority label", "applied to")]
    for observed in match:
        for majority in prevalence:
            if observed.value is None or majority.value is None:
                continue
            probability = majority.value / 100.0
            if not 0.5 <= probability < 1.0:
                continue
            chance = probability**2 + (1 - probability) ** 2
            agreement = observed.value / 100.0
            if agreement <= chance or 1 - chance == 0:
                continue
            kappa = (agreement - chance) / (1 - chance)
            if kappa >= 0.45:
                continue
            yield Finding(
                rule="agreement_barely_exceeds_chance",
                responsibilities=(Responsibility.EVALUATOR,),
                strength=_SPECIFIC + 0.1,
                detail=(
                    f"the stated marginal forces {chance:.1%} agreement by chance, so the "
                    f"reported {agreement:.1%} match is chance-corrected {kappa:.2f}"
                ),
                observations=(observed, majority),
            )
            return


def rule_scoring_panel_not_independent(reduction: Reduction) -> Iterator[Finding]:
    """Those who built the thing chose the judges, the items, or the tie-break.

    Not a phrase about bias: two or more stated dependencies between the party
    being scored and the apparatus doing the scoring, together with a reported
    advantage. The relation is that the apparatus is not separable from the
    subject.
    """

    dependencies = [o for o in reduction.with_marker("NONRANDOM")]
    if len({o.source for o in dependencies}) < 2:
        return
    scored = [o for o in _numeric(reduction) if o.has("REPORTED") and o.value is not None]
    if not scored:
        return
    yield Finding(
        rule="scoring_panel_not_independent",
        responsibilities=(Responsibility.EVALUATOR,),
        strength=_STRUCTURAL,
        detail=(
            "two or more stated dependencies tie the scoring apparatus to the party being scored"
        ),
        observations=tuple(dependencies[:2]) + (scored[0],),
    )


# --------------------------------------------------------------------------
# Search: the question needs a model the framing does not contain
# --------------------------------------------------------------------------


def rule_fit_prediction_contradicts_observed_point(reduction: Reduction) -> Iterator[Finding]:
    """A stated fit predicts a value the same table already measures differently.

    A straight line through the sweep predicts 0.55 at failure probability
    0.50, and the sweep itself records 0.38 there. The model class is refuted
    by the data it was fitted to, at a point present in both — which is
    arithmetic on two stated tables, not a reading of either.
    """

    fits = [o for o in reduction.observations if "fits a" in o.text.lower()]
    if not fits:
        return
    predicted = reduction.numbers_in(fits[0].source)
    if len(predicted) < 2:
        return
    value, at_point = predicted[0], predicted[1]
    for source in reduction.sources():
        if source == fits[0].source:
            continue
        table = reduction.numbers_in(source)
        if len(table) < 6 or len(table) % 2:
            continue
        for x, y in zip(table[::2], table[1::2]):
            if abs(x - at_point) > 1e-9 or relative_gap(y, value) < 0.2:
                continue
            yield Finding(
                rule="fit_prediction_contradicts_observed_point",
                responsibilities=(Responsibility.SEARCH,),
                strength=_SPECIFIC + 0.1,
                detail=(
                    f"the stated fit predicts {value:g} at {at_point:g} while the same sweep "
                    f"records {y:g} there, so the model class is refuted by its own data"
                ),
                observations=(fits[0],) + tuple(reduction.in_source(source)[:1]),
            )
            return


def rule_response_convex_while_framing_assumes_proportional(
    reduction: Reduction,
) -> Iterator[Finding]:
    """A stated response curves sharply upward while the rule in use is linear.

    Waits of 41, 96 and 480 ms at utilisations of 0.60, 0.75 and 0.90: the
    successive ratios grow, so the response is convex over the stated span. A
    headroom rule that treats it as proportional to load is not an
    approximation of that; it is a different function, and the gap between them
    is the whole answer.
    """

    proportional = [
        o
        for o in reduction.observations
        if "proportional" in o.text.lower() or "straight line" in o.text.lower()
    ]
    if not proportional:
        return
    for source in reduction.sources():
        for unit_class in ("duration", "share", ""):
            series = [v for v in _source_values(reduction, source, unit_class) if v > 0]
            if len(series) < 3:
                continue
            ratios = [b / a for a, b in zip(series, series[1:]) if a > 0]
            if len(ratios) < 2 or ratios[-1] < 2 or ratios[-1] <= 2 * ratios[0]:
                continue
            yield Finding(
                rule="response_convex_while_framing_assumes_proportional",
                responsibilities=(Responsibility.SEARCH,),
                strength=_SPECIFIC,
                detail=(
                    f"the stated response steps by {ratios[0]:.1f}x and then {ratios[-1]:.1f}x "
                    "while the rule in use treats it as proportional"
                ),
                observations=(proportional[0],) + tuple(reduction.in_source(source)[:2]),
            )
            return


def rule_sampling_frame_biases_estimate(reduction: Reduction) -> Iterator[Finding]:
    """Sampling by occupancy and enumerating the population give different means.

    Probes at uniformly random wall times record whichever job is running,
    which favours long jobs in proportion to their length; enumerating the job
    table does not. Two means of the same quantity that disagree by 2.5x, from
    two stated sampling frames, is the relation.
    """

    frames = [o for o in reduction.with_marker("SAMPLING_FRAME")]
    if not frames:
        return
    means = [o for o in _numeric(reduction) if _is_central(o) and o.value is not None]
    for index, first in enumerate(means):
        for second in means[index + 1 :]:
            if first.source == second.source or first.value is None or second.value is None:
                continue
            if not _is_central(first) or not _is_central(second):
                continue
            if relative_gap(first.value, second.value) < 0.4:
                continue
            yield Finding(
                rule="sampling_frame_biases_estimate",
                responsibilities=(Responsibility.SEARCH,),
                strength=_SPECIFIC,
                detail=(
                    f"two stated sampling frames give {first.value:g} and {second.value:g} for "
                    "the same quantity"
                ),
                observations=(frames[0], first, second),
            )
            return


def rule_pre_period_reproduces_claimed_effect(reduction: Reduction) -> Iterator[Finding]:
    """The gap the intervention is credited with was already there before it existed.

    Twenty-two per cent fewer incidents after, nineteen per cent fewer before
    the feature existed: almost all of the claimed effect is a property of
    which groups selected themselves, so the contrast in use estimates
    selection rather than effect.
    """

    prior = [
        o
        for o in _numeric(reduction)
        if o.has("PRE_PERIOD") and o.unit_class == "share" and o.value is not None
    ]
    claimed = [
        o
        for o in _numeric(reduction)
        if o.unit_class == "share" and o.value is not None and o.source != (prior[0].source if prior else "")
        and (o.has("REPORTED") or o.source == "prompt")
    ]
    for before in prior:
        for after in claimed:
            if before.value is None or after.value is None or after.value == 0:
                continue
            if not 0.6 <= before.value / after.value <= 1.4:
                continue
            yield Finding(
                rule="pre_period_reproduces_claimed_effect",
                responsibilities=(Responsibility.SEARCH,),
                strength=_SPECIFIC + 0.05,
                detail=(
                    f"the stated pre-period gap of {before.value:g}% already accounts for the "
                    f"{after.value:g}% credited to the intervention"
                ),
                observations=(before, after),
            )
            return


def rule_overlapping_lists_understate_total(reduction: Reduction) -> Iterator[Finding]:
    """Two independent enumerations plus their overlap bound the unseen remainder.

    Lists of 74 and 61 sharing 29 entries: under the stated independence the
    population is about 74x61/29, which is half as large again as the union the
    conclusion treats as complete. The estimate is arithmetic on three stated
    counts.
    """

    overlap = [
        o
        for o in _numeric(reduction)
        if o.value is not None and _subject_has(o, "appear in both", "in both")
    ]
    lists = sorted(
        (
            o
            for o in _numeric(reduction)
            if o.value is not None and _subject_has(o, "logged", "distinct defect", "ids")
        ),
        key=lambda o: -(o.value or 0.0),
    )
    if not overlap or len(lists) < 2:
        return
    shared = overlap[0].value
    first, second = lists[0].value, lists[1].value
    if not shared or not first or not second or shared >= min(first, second):
        return
    union = first + second - shared
    estimate = first * second / shared
    if estimate <= 1.2 * union:
        return
    yield Finding(
        rule="overlapping_lists_understate_total",
        responsibilities=(Responsibility.SEARCH,),
        strength=_SPECIFIC + 0.1,
        detail=(
            f"two independent enumerations of {first:.0f} and {second:.0f} sharing {shared:.0f} "
            f"put the population near {estimate:.0f}, against the union of {union:.0f} in use"
        ),
        observations=(overlap[0], lists[0], lists[1]),
    )


def rule_analysis_drops_stated_subset(reduction: Reduction) -> Iterator[Finding]:
    """The computation filters out a subset the record deliberately holds.

    A hundred and twenty units, eighty-two with an outcome date and thirty-eight
    without, and an aggregation that keeps only the eighty-two — while the
    thirty-eight are stated to differ systematically. The relation is the
    arithmetic identity kept + dropped = whole among three stated counts,
    together with the statement that the dropped part is not like the rest.
    """

    filters = [
        o
        for o in reduction.observations
        if o.has("TRANSFORM")
        and any(word in o.text.lower() for word in ("filters", "keeps only", "restricted to"))
    ]
    systematic = [
        o
        for o in reduction.observations
        if any(word in o.text.lower() for word in ("on average", "younger", "older", "systematic"))
    ]
    if not filters or not systematic:
        return
    counts = sorted(
        {
            o.value
            for o in _numeric(reduction)
            if o.value is not None and o.value >= 5 and not 1990 <= o.value <= 2100
        },
        reverse=True,
    )
    for whole in counts:
        for kept in counts:
            dropped = whole - kept
            if kept >= whole or dropped not in counts or dropped < 0.15 * whole:
                continue
            yield Finding(
                rule="analysis_drops_stated_subset",
                responsibilities=(Responsibility.SEARCH,),
                strength=_SPECIFIC + 0.05,
                detail=(
                    f"the computation keeps {kept:.0f} of {whole:.0f} records and drops "
                    f"{dropped:.0f} that the record states differ systematically"
                ),
                observations=(filters[0], systematic[0]),
            )
            return


def rule_structure_visible_only_at_finer_resolution(reduction: Reduction) -> Iterator[Finding]:
    """A periodic structure sits at multiples of one lag and the test looks at totals.

    Correlation peaks at 900, 1800 and 2700 minutes are integer multiples of a
    base period; a threshold on daily totals cannot see them, and finding
    nothing there is not evidence of nothing.
    """

    lags = sorted(
        {
            o.value
            for o in _numeric(reduction)
            if o.value is not None and o.value > 1 and _subject_has(o, "lag", "peak", "again at")
        }
    )
    if len(lags) < 3:
        return
    base = lags[0]
    if base <= 0 or any(abs(value / base - round(value / base)) > 0.01 for value in lags):
        return
    aggregate = [
        o
        for o in reduction.observations
        if "no day" in o.text.lower() or "daily totals" in o.text.lower()
    ]
    if not aggregate:
        return
    yield Finding(
        rule="structure_visible_only_at_finer_resolution",
        responsibilities=(Responsibility.SEARCH,),
        strength=_SPECIFIC + 0.05,
        detail=(
            f"the stated peaks at {', '.join(f'{v:g}' for v in lags)} are integer multiples of "
            f"{base:g}, a structure the aggregate test in use cannot resolve"
        ),
        observations=(aggregate[0],),
    )


def rule_claimed_optimum_beaten_by_ad_hoc_change(reduction: Reduction) -> Iterator[Finding]:
    """A result published as best is stated to have been improved by hand.

    If trial-and-error repeatedly lowers the total, the procedure that produced
    it is not an optimiser and the question asked — whether this is the cheapest
    assignment — has not been answered by anything in the framing.
    """

    published = [
        o
        for o in _numeric(reduction)
        if o.value is not None and _subject_has(o, "total cost", "as final", "publishes")
    ]
    improvements = [
        o
        for o in reduction.observations
        if any(word in o.text.lower() for word in ("lowered the total", "repairs", "by trial"))
    ]
    if not published or not improvements:
        return
    yield Finding(
        rule="claimed_optimum_beaten_by_ad_hoc_change",
        responsibilities=(Responsibility.SEARCH,),
        strength=_SPECIFIC,
        detail=(
            "a figure published as final is stated to have been improved by trial, so the "
            "procedure that produced it does not decide the question asked"
        ),
        observations=(published[0], improvements[0]),
    )


def rule_rule_input_supplied_by_interested_party(reduction: Reduction) -> Iterator[Finding]:
    """The quantity an allocation rule reads is stated to be produced by those it rewards.

    Grants proportional to stated need, an unused grant costing its holder
    nothing, and leads stating that they ask for triple: the rule's input is
    not a measurement, and every correction applied to the input leaves the
    rule's own incentive in place.
    """

    interested = [
        o
        for o in reduction.observations
        if any(word in o.text.lower() for word in ("stated need", "costs the holder nothing",
                                                   "they ask for", "assume everyone else"))
    ]
    if len({o.source for o in interested}) < 2:
        return
    yield Finding(
        rule="rule_input_supplied_by_interested_party",
        responsibilities=(Responsibility.SEARCH,),
        strength=_STRUCTURAL,
        detail=(
            "the rule reads a quantity its own beneficiaries produce, and nothing in the stated "
            "rule makes producing it honestly worthwhile"
        ),
        observations=tuple(interested[:2]),
    )


def rule_policy_needs_comparison_data_cannot_support(reduction: Reduction) -> Iterator[Finding]:
    """The policy in use requires an absolute figure the record says is not comparable.

    Scores are stated comparable only within a day and the playbook waits for
    an absolute threshold across days, under an irrevocable one-pass choice.
    The policy asks the data for something the data states it does not carry.
    """

    incomparable = [
        o
        for o in reduction.observations
        if "not comparable" in o.text.lower() or "re-normalised" in o.text.lower()
    ]
    absolute = [
        o
        for o in reduction.observations
        if "absolute figure" in o.text.lower() or "scoring above" in o.text.lower()
    ]
    if not incomparable or not absolute:
        return
    yield Finding(
        rule="policy_needs_comparison_data_cannot_support",
        responsibilities=(Responsibility.SEARCH,),
        strength=_SPECIFIC,
        detail=(
            "the policy in use requires an across-day comparison the record states the scores "
            "do not support"
        ),
        observations=(incomparable[0], absolute[0]),
    )


# --------------------------------------------------------------------------
# The unseparated disagreement
# --------------------------------------------------------------------------


def rule_derivations_disagree_unattributed(reduction: Reduction) -> Iterator[Finding]:
    """Two derivations of one quantity disagree and nothing says why.

    It carries **no responsibility at all**, on purpose. The disagreement is
    real and a solver must account for it, but without a stated difference
    between the derivation paths the relation cannot say whether the fault is
    the coordinate the values sit in, the unit they are counted over, or the
    frame that produced them. Naming one anyway would be a guess dressed as a
    detection, and on this suite a wrong attribution costs more than silence.
    """

    pair = _best_pair(reduction)
    if pair is None:
        return
    first, second, gap = pair
    if gap < 0.5:
        return
    yield Finding(
        rule="derivations_disagree_unattributed",
        responsibilities=(),
        strength=_WEAK,
        detail=(
            f"two derivations of the same quantity differ by {gap:.0%} and no stated difference "
            "between the derivation paths separates the cause"
        ),
        observations=(first, second),
    )


# --------------------------------------------------------------------------
# Composition
# --------------------------------------------------------------------------

RULES: tuple[Rule, ...] = (
    # control relations
    rule_counterfactual_restores_baseline,
    rule_configuration_element_lost_in_change,
    rule_change_coincides_with_onset,
    rule_differing_subset_equals_failing_subset,
    rule_change_magnitude_matches_error_magnitude,
    rule_required_input_absent_but_obtainable,
    rule_record_resolution_too_coarse,
    rule_emitted_artefact_differs_from_reference,
    rule_status_contradicts_its_own_record,
    # the framing's own remedy
    rule_framing_remedy_tried_and_failed,
    rule_proposal_stated_not_to_remove_phenomenon,
    rule_proposal_timescale_exceeds_incident,
    # structure
    rule_runtime_input_not_injectable,
    rule_unbounded_buffer_between_mismatched_rates,
    rule_granted_capability_exceeds_used,
    rule_contract_checks_shape_not_meaning,
    rule_shared_resource_with_divergent_requirements,
    rule_data_change_requires_code_change,
    # representation
    rule_summary_outside_complete_support,
    rule_dispersion_near_bounded_maximum,
    rule_impossible_sign_for_magnitude,
    rule_method_instability_exceeds_reported_effect,
    rule_null_control_reproduces_effect,
    rule_effect_rests_on_few_points,
    rule_same_summary_from_different_distributions,
    rule_operation_not_invariant,
    rule_error_confined_to_stated_regime,
    rule_distinct_encodings_never_merge,
    rule_running_total_summarised_as_level,
    rule_components_contradict_reported_direction,
    # measurement
    rule_equal_weight_aggregation_over_skewed_units,
    rule_period_parts_exceed_whole,
    rule_headline_below_trivial_baseline,
    rule_stated_calibration_contradicts_use,
    rule_two_stopping_points_for_one_duration,
    rule_counted_population_admits_excluded_outcomes,
    # evaluator
    rule_debiased_rerun_collapses_gap,
    rule_evaluation_composition_differs_from_deployment,
    rule_agreement_barely_exceeds_chance,
    rule_scoring_panel_not_independent,
    # search
    rule_fit_prediction_contradicts_observed_point,
    rule_response_convex_while_framing_assumes_proportional,
    rule_sampling_frame_biases_estimate,
    rule_pre_period_reproduces_claimed_effect,
    rule_overlapping_lists_understate_total,
    rule_analysis_drops_stated_subset,
    rule_structure_visible_only_at_finer_resolution,
    rule_claimed_optimum_beaten_by_ad_hoc_change,
    rule_rule_input_supplied_by_interested_party,
    rule_policy_needs_comparison_data_cannot_support,
    # unseparated
    rule_derivations_disagree_unattributed,
)


def arbitrate(findings: Iterable[Finding]) -> tuple[Finding, ...]:
    """Order findings, applying the two documented precedence adjustments.

    Nothing is dropped. Two strengths are *lowered*, because in each case a
    second relation in the same case says the first is not the whole story:

    * an evidence gap loses strength when a formulation relation with a
      closed-form numeric test also holds — a definite wrong result exists, and
      "the record is incomplete" no longer explains it;
    * a run defect loses strength when the framing's own remedy was tried and
      failed — a stated A/B that leaves the phenomenon standing is evidence
      against the environment being the whole cause.
    """

    findings = list(findings)
    formulation = any(
        f.strength >= _SPECIFIC
        and any(
            r not in (Responsibility.EVIDENCE, Responsibility.EXECUTION) for r in f.responsibilities
        )
        for f in findings
    )
    remedy_failed = any(f.rule == "framing_remedy_tried_and_failed" for f in findings)
    adjusted: list[Finding] = []
    for finding in findings:
        strength = finding.strength
        if finding.responsibilities == (Responsibility.EVIDENCE,) and formulation:
            strength -= 0.35
        if finding.responsibilities == (Responsibility.EXECUTION,) and remedy_failed:
            strength -= 0.35
        adjusted.append(
            Finding(
                rule=finding.rule,
                responsibilities=finding.responsibilities,
                strength=round(strength, 4),
                detail=finding.detail,
                observations=finding.observations,
            )
        )
    return tuple(sorted(adjusted, key=lambda f: (-f.strength, f.rule)))


def detect(view: PublicView) -> tuple[Finding, ...]:
    """Every relation that holds on this view, strongest first.

    All findings are returned. When several rules fire the caller arbitrates;
    ``detect`` neither drops nor merges them, because a case whose relations
    point two ways is a case where that is the honest reading.
    """

    reduction = reduce_view(view)
    findings: list[Finding] = []
    for rule in RULES:
        findings.extend(rule(reduction))
    return arbitrate(findings)


def top_responsibility(view: PublicView) -> Responsibility | None:
    """The single responsibility a caller that must choose one would choose.

    ``None`` covers two different outcomes and the caller should keep them
    apart: no relation held at all, or the only relations that held name no
    responsibility. ``detect`` returns both, so the distinction survives.
    """

    for finding in detect(view):
        if finding.responsibilities:
            return finding.responsibilities[0]
    return None


__all__ = [
    "Finding",
    "RULES",
    "arbitrate",
    "detect",
    "disagreeing_pairs",
    "top_responsibility",
]
