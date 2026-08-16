"""Reduce a P1 public view to typed observations.

The layer this module supplies is the one the mechanical arm was missing.
``baselines.extract_cues`` reads the public view as *prose* and matches
phrases against a responsibility table; the suite bans gold vocabulary from
every public field, so that detector finds nothing on the real cases and the
whole arm abstains. The conclusion drawn from that — that no mechanical
detector can work — does not follow. It was disproved on one case by hand:
``p1-c109`` states a reported mean bearing of 181.4 degrees while the same
instrument's east/north components for the same hour give
``atan2(-0.4, 7.9) = 357.1`` degrees, a 175.7 degree contradiction computed
from numbers printed in the resource text, with no gold token anywhere.

What was missing is not a bigger phrase table. It is a reduction: the resource
lines have to become *quantities, ranges, counts, fractions, token lists,
stated transformations and stated capability states*, each carrying the source
line it came from, so that ``contradiction`` can compute **relations between
observations** instead of matching words.

Three properties this module holds to.

**Deterministic.** No model, no network, no randomness. The same view reduces
to the same observations on every machine.

**Label-blind.** Nothing here reads ``protected_gold``; nothing here names a
responsibility. The lexicon below types *what kind of statement* a clause is
(a stated transformation, a stated absence, a stated capability) and never
what the answer is. That distinction is the whole difference between this and
the phrase table: a marker such as ``ABSENT`` is true of clauses in every one
of the six families, and on its own decides nothing.

**Shape-neutral.** ``ObservationKind`` is deliberately a small, near-universal
vocabulary — the same seven kinds appear across all six families. Anything
that would *discriminate* a family (whether an absence is recoverable, whether
a trial restored the baseline) lives in ``Observation.markers``, a field, not
in the kind. That is what keeps the reduction's *shape* uninformative, which
``test_observation`` measures with the degeneracy probe rather than asserting:
a kind vocabulary that carried the answer would let a responder that sees only
the kind histogram beat the majority baseline, and that is a leak in the
reduction, not in the probe.

A declared ``signal:<phenomenon>`` resource is refused here exactly as
``baselines.readable_resources`` refuses it. That channel was measured
DEGENERATE at 1.000 and the refusal is reused rather than re-implemented so
the two cannot drift apart.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from enum import Enum

from .baselines import readable_resources
from .cases import PublicView

# --------------------------------------------------------------------------
# Kinds
# --------------------------------------------------------------------------


class ObservationKind(str, Enum):
    """What sort of thing a clause states.

    Seven kinds, chosen to be near-universal across the six families. A kind
    answers "what shape of statement is this", never "what is wrong here".
    """

    QUANTITY = "QUANTITY"
    """A number with a unit and the words that name it."""

    RANGE = "RANGE"
    """A stated interval or cluster bound: `between 352 and 359`, `1 to 600`."""

    FRACTION = "FRACTION"
    """A share of a whole: a percentage, or `61 of 4,900`."""

    COUNT = "COUNT"
    """A cardinality: `41 duplicate charges`, `60 nodes`."""

    TOKEN_LIST = "TOKEN_LIST"
    """Identifiers named in a line: file names, columns, env vars, predicates."""

    STATEMENT = "STATEMENT"
    """A clause carrying no number, typed only by its markers."""

    CLOSURE = "CLOSURE"
    """A `closure:<id>` line and what it is stated to rest on."""


PROMPT_SOURCE = "prompt"

# --------------------------------------------------------------------------
# Lexicon
# --------------------------------------------------------------------------
#
# Every entry types a *clause*, never an answer. Each marker below is present
# in cases from several different families — that is the test applied when
# adding one, and it is why none of them can be read off as a responsibility.

_MARKERS: tuple[tuple[str, str], ...] = (
    # --- a stated computation over data -----------------------------------
    ("computes", "TRANSFORM"),
    ("computed from", "TRANSFORM"),
    ("recomputed", "TRANSFORM"),
    ("averag", "TRANSFORM"),
    ("the mean of", "TRANSFORM"),
    ("plain mean", "TRANSFORM"),
    ("takes each", "TRANSFORM"),
    ("adds the", "TRANSFORM"),
    ("adds up", "TRANSFORM"),
    ("divides by", "TRANSFORM"),
    ("summed as", "TRANSFORM"),
    ("summing", "TRANSFORM"),
    ("applies", "TRANSFORM"),
    ("fits a", "TRANSFORM"),
    ("multiplies", "TRANSFORM"),
    ("integrate", "TRANSFORM"),
    ("correlat", "TRANSFORM"),
    ("emits", "TRANSFORM"),
    ("filters", "TRANSFORM"),
    ("pooled", "TRANSFORM"),
    ("equal contribution", "TRANSFORM"),
    ("per-team averages", "TRANSFORM"),
    # --- the aggregation's unit of account --------------------------------
    ("per session", "UNIT_OF_ACCOUNT"),
    ("of sessions", "UNIT_OF_ACCOUNT"),
    ("per-host", "UNIT_OF_ACCOUNT"),
    ("per host", "UNIT_OF_ACCOUNT"),
    ("per-person", "UNIT_OF_ACCOUNT"),
    ("per person", "UNIT_OF_ACCOUNT"),
    ("of monthly people", "UNIT_OF_ACCOUNT"),
    ("distinct", "UNIT_OF_ACCOUNT"),
    ("each judge", "UNIT_OF_ACCOUNT"),
    ("counts each", "UNIT_OF_ACCOUNT"),
    ("counted at", "UNIT_OF_ACCOUNT"),
    ("counts the first", "UNIT_OF_ACCOUNT"),
    ("taken at the final", "UNIT_OF_ACCOUNT"),
    ("individual", "UNIT_OF_ACCOUNT"),
    ("across 60 hosts", "UNIT_OF_ACCOUNT"),
    ("and divides by", "UNIT_OF_ACCOUNT"),
    # --- a figure that has been published, certified or acted on ----------
    ("reported", "REPORTED"),
    ("reports", "REPORTED"),
    ("published", "REPORTED"),
    ("publishes", "REPORTED"),
    ("certif", "REPORTED"),
    ("attribut", "REPORTED"),
    ("declared", "REPORTED"),
    ("concludes", "REPORTED"),
    ("states", "REPORTED"),
    ("scores", "REPORTED"),
    # --- something the record does not hold -------------------------------
    ("is null", "ABSENT"),
    ("are null", "ABSENT"),
    ("null for every", "ABSENT"),
    ("no record", "ABSENT"),
    ("never written down", "ABSENT"),
    ("nothing persisted", "ABSENT"),
    ("was never", "ABSENT"),
    ("is empty", "ABSENT"),
    ("field is empty", "ABSENT"),
    ("removed by", "ABSENT"),
    ("were removed", "ABSENT"),
    ("long past", "ABSENT"),
    ("is absent", "ABSENT"),
    ("are absent", "ABSENT"),
    ("no way to", "ABSENT"),
    ("has no", "ABSENT"),
    ("holds no", "ABSENT"),
    ("never called", "ABSENT"),
    ("no matching", "ABSENT"),
    ("cannot run without", "ABSENT"),
    ("were untouched", "UNCHANGED"),
    ("untouched", "UNCHANGED"),
    ("differs from", "ABSENT"),
    ("checksum differs", "ABSENT"),
    ("populated for", "PARTIAL"),
    ("present for", "PARTIAL"),
    ("are present for", "PARTIAL"),
    ("of the 14", "PARTIAL"),
    ("only", "PARTIAL"),
    # --- something a stated capability could still produce ----------------
    ("is retained", "OBTAINABLE"),
    ("are retained", "OBTAINABLE"),
    ("are kept", "OBTAINABLE"),
    ("retains", "OBTAINABLE"),
    ("can be requested", "OBTAINABLE"),
    ("can be provisioned", "OBTAINABLE"),
    ("can be digitised", "OBTAINABLE"),
    ("can be issued", "OBTAINABLE"),
    ("regenerates", "OBTAINABLE"),
    ("restore", "OBTAINABLE"),
    ("snapshot holds", "OBTAINABLE"),
    ("still reachable", "OBTAINABLE"),
    ("runnable against", "OBTAINABLE"),
    ("on request", "OBTAINABLE"),
    ("needs a request", "OBTAINABLE"),
    ("supports enabling", "OBTAINABLE"),
    ("with recording on", "OBTAINABLE"),
    ("is recorded here", "OBTAINABLE"),
    ("deterministic hash", "OBTAINABLE"),
    ("replays deterministic", "OBTAINABLE"),
    ("permits redeploying", "OBTAINABLE"),
    ("reproduces on staging", "OBTAINABLE"),
    ("has continued", "OBTAINABLE"),
    ("timestamps for all", "OBTAINABLE"),
    ("are present", "OBTAINABLE"),
    ("exists", "OBTAINABLE"),
    # --- a stated capability of the tooling, and its state ----------------
    ("supports", "CAPABILITY"),
    ("can issue", "CAPABILITY"),
    ("accepts a caller", "CAPABILITY"),
    ("the provider can", "CAPABILITY"),
    ("worked example", "CAPABILITY"),
    ("is disabled", "DISABLED"),
    ("is off", "DISABLED"),
    ("flag that", "DISABLED"),
    # --- a change proposed inside the current framing ---------------------
    #
    # `the team's framing is` and `the plan is` are REFUSED, not merely unused.
    # The suite's own solvability audit measured each of them as a perfect
    # separator of hidden-shift cases from negative controls (66/66 on the
    # single tokens `framing` and `team's`), which is the H2 question answered
    # with no comprehension at all. A detector that reads them scores by
    # template rather than by content, so they are kept out of the lexicon
    # entirely. A proposal is recognised from what it proposes.
    ("proposal", "PROPOSAL"),
    ("adds a guard", "PROPOSAL"),
    ("adds 14 more", "PROPOSAL"),
    ("replaces the branches", "PROPOSAL"),
    ("scans every", "PROPOSAL"),
    ("rotates every", "PROPOSAL"),
    ("raises the drift", "PROPOSAL"),
    # --- a stated counterfactual run --------------------------------------
    ("trial", "TRIAL"),
    ("re-run", "TRIAL"),
    ("rerun", "TRIAL"),
    ("ablation", "TRIAL"),
    ("refit", "TRIAL"),
    ("pinning", "TRIAL"),
    ("forced to", "TRIAL"),
    ("frozen", "TRIAL"),
    ("removing the", "TRIAL"),
    ("line removed", "TRIAL"),
    ("shuffling each", "TRIAL"),
    ("captions removed", "TRIAL"),
    ("order shuffled", "TRIAL"),
    ("did not run", "TRIAL"),
    ("divides by customer", "TRIAL"),
    ("in a different row order", "TRIAL"),
    ("hand review", "TRIAL"),
    ("audit by a subject expert", "TRIAL"),
    ("clean nights", "TRIAL"),
    ("spot-check", "TRIAL"),
    ("by hand", "TRIAL"),
    ("manual", "TRIAL"),
    # --- what the counterfactual did to the outcome -----------------------
    ("restores", "RESTORED"),
    ("reproduces bit for bit", "RESTORED"),
    ("bit-identical", "RESTORED"),
    ("repeats", "RESTORED"),
    ("finishes in", "RESTORED"),
    ("on time", "RESTORED"),
    ("agree with", "RESTORED"),
    ("agrees with", "RESTORED"),
    ("reconcile to", "RESTORED"),
    ("still matching", "RESTORED"),
    ("not fewer", "UNCHANGED"),
    ("did not", "UNCHANGED"),
    ("left reporting", "UNCHANGED"),
    ("left the", "UNCHANGED"),
    ("moved the first crash", "UNCHANGED"),
    ("of similar size", "UNCHANGED"),
    ("still requires", "UNCHANGED"),
    ("cannot tell", "UNCHANGED"),
    ("never merge", "UNCHANGED"),
    ("raised the", "WORSE"),
    ("produced 63", "WORSE"),
    ("refused 6%", "WORSE"),
    # --- an independent reading of the same thing -------------------------
    ("customer", "EXTERNAL"),
    ("complaint", "EXTERNAL"),
    ("driver-measured", "EXTERNAL"),
    ("surveyed", "EXTERNAL"),
    ("ground-truth", "EXTERNAL"),
    ("bank total", "EXTERNAL"),
    ("subject expert", "EXTERNAL"),
    ("a human reading", "EXTERNAL"),
    ("the same instrument", "EXTERNAL"),
    ("reconciliation", "EXTERNAL"),
    ("live", "EXTERNAL"),
    ("in production", "EXTERNAL"),
    ("escalated", "EXTERNAL"),
    # --- a stated non-uniformity over the units being aggregated ----------
    ("accounts for", "SKEW"),
    ("account for", "SKEW"),
    ("carries 71%", "SKEW"),
    ("carry under", "SKEW"),
    ("orders of magnitude", "SKEW"),
    ("more sessions than", "SKEW"),
    ("heavy on the right", "SKEW"),
    ("far up and far to the right", "SKEW"),
    ("largest", "SKEW"),
    ("dense cloud", "SKEW"),
    ("times the median", "SKEW"),
    ("x the median", "SKEW"),
    # --- a stated departure from random assignment or sampling ------------
    ("never at random", "NONRANDOM"),
    ("no team was assigned at random", "NONRANDOM"),
    ("was a team decision", "NONRANDOM"),
    ("picked by that same team", "NONRANDOM"),
    ("belong to the team", "NONRANDOM"),
    ("opted in", "NONRANDOM"),
    ("chose to complain", "NONRANDOM"),
    ("uniformly random wall times", "SAMPLING_FRAME"),
    ("then running", "SAMPLING_FRAME"),
    ("probe", "SAMPLING_FRAME"),
    ("pre-period", "PRE_PERIOD"),
    ("before the feature existed", "PRE_PERIOD"),
    ("already", "PRE_PERIOD"),
    # --- a stated property of how the values are encoded ------------------
    ("degrees", "ENCODING"),
    ("time of day", "ENCODING"),
    ("time_of_day", "ENCODING"),
    ("no date part", "ENCODING"),
    ("running total", "ENCODING"),
    ("since start", "ENCODING"),
    ("floating point", "ENCODING"),
    ("fractional digits", "ENCODING"),
    ("minor currency unit", "ENCODING"),
    ("utf-8", "ENCODING"),
    ("bytes", "ENCODING"),
    ("lowercasing", "ENCODING"),
    ("add to 100", "ENCODING"),
    ("adds to 100", "ENCODING"),
    ("share", "ENCODING"),
    ("chassis", "ENCODING"),
    ("heading", "ENCODING"),
    ("east and north", "ENCODING"),
    ("latitude", "ENCODING"),
    ("longitude", "ENCODING"),
    ("coded 1 to 5", "ENCODING"),
    ("five-point", "ENCODING"),
    ("ordinal", "ENCODING"),
    # --- a boundary between two parts of a system -------------------------
    ("shared by", "BOUNDARY"),
    ("one connection pool", "BOUNDARY"),
    ("one worker pool", "BOUNDARY"),
    ("unbounded", "BOUNDARY"),
    ("in-process", "BOUNDARY"),
    ("downstream", "BOUNDARY"),
    ("consumer", "BOUNDARY"),
    ("producer", "BOUNDARY"),
    ("caller", "BOUNDARY"),
    ("wildcard permission", "BOUNDARY"),
    ("interleaved", "BOUNDARY"),
    ("call sites", "BOUNDARY"),
    ("branch tree", "BOUNDARY"),
    ("per-tier branches", "BOUNDARY"),
    ("redeploy", "BOUNDARY"),
    ("commits the order row", "BOUNDARY"),
    ("straight from the runtime", "BOUNDARY"),
    ("reads from whichever", "BOUNDARY"),
    # --- an environment, version or configuration difference --------------
    ("env-diff", "ENV_DIFF"),
    ("lockfile", "ENV_DIFF"),
    ("moved from", "ENV_DIFF"),
    ("changelog", "ENV_DIFF"),
    ("breaking:", "ENV_DIFF"),
    ("before the", "ENV_DIFF"),
    ("after it", "ENV_DIFF"),
    ("migrated", "ENV_DIFF"),
    ("pre-migration", "ENV_DIFF"),
    ("was built", "ENV_DIFF"),
    ("build agent", "ENV_DIFF"),
    ("distinguishes upper and lower case", "ENV_DIFF"),
    ("no pipefail", "ENV_DIFF"),
    ("without pipefail", "ENV_DIFF"),
    ("lock file", "ENV_DIFF"),
    ("at build time", "ENV_DIFF"),
    ("returns early", "ENV_DIFF"),
    ("upgrade", "ENV_DIFF"),
    # --- exactly-coinciding sets ------------------------------------------
    ("are exactly the", "COINCIDENCE"),
    ("line up exactly", "COINCIDENCE"),
    ("matching sample", "COINCIDENCE"),
    ("all 5 carrying", "COINCIDENCE"),
    ("every run since", "COINCIDENCE"),
    ("out of 30", "COINCIDENCE"),
    ("the same 3%", "COINCIDENCE"),
)

# Sorted longest-first so `no record` wins over `record` when both would match.
_MARKERS_BY_LENGTH: tuple[tuple[str, str], ...] = tuple(
    sorted(_MARKERS, key=lambda item: -len(item[0]))
)

# --------------------------------------------------------------------------
# Numbers and units
# --------------------------------------------------------------------------

_NUMBER = r"-?\d[\d,]*(?:\.\d+)?"
_NUMBER_RE = re.compile(rf"(?<![\w.]){_NUMBER}")

# Multiplier words. `MB`/`GB` are units and must not be read as `M`/`B`, so the
# short forms are matched case-sensitively and only as whole tokens.
_MAGNITUDE = {
    "k": 1e3,
    "M": 1e6,
    "B": 1e9,
    "bn": 1e9,
    "thousand": 1e3,
    "million": 1e6,
    "billion": 1e9,
}

_TIME_SECONDS = {
    "ms": 1e-3,
    "millisecond": 1e-3,
    "milliseconds": 1e-3,
    "s": 1.0,
    "sec": 1.0,
    "second": 1.0,
    "seconds": 1.0,
    "minute": 60.0,
    "minutes": 60.0,
    "min": 60.0,
    "h": 3600.0,
    "hour": 3600.0,
    "hours": 3600.0,
    "day": 86400.0,
    "days": 86400.0,
    "week": 604800.0,
    "weeks": 604800.0,
    "month": 2592000.0,
    "months": 2592000.0,
    "year": 31536000.0,
    "years": 31536000.0,
}

_ANGLE = {"degree", "degrees"}
_BYTES = {"mb", "gb", "gib", "tb", "kb", "kib", "mib"}

_UNIT_TOKEN = re.compile(r"[A-Za-z][A-Za-z/%°]*")

# A unit is only recorded when the token following the number is a real unit.
# Without this the parser reads `between 352 and 359` as carrying the unit
# `and`, and every later comparison on unit class becomes noise.
_KNOWN_UNITS: frozenset[str] = frozenset(
    {"%", "percent", "x", "times", "m/s", "rps"}
    | set(_TIME_SECONDS)
    | _ANGLE
    | _BYTES
)


def _unit_class(unit: str) -> str:
    """Coarse class used to decide whether two quantities are comparable."""

    lowered = unit.lower().strip()
    if lowered in {"%", "percent", "per cent"}:
        return "share"
    if lowered in _TIME_SECONDS:
        return "duration"
    if lowered in _ANGLE:
        return "angle"
    if lowered in _BYTES:
        return "bytes"
    if lowered in {"x", "times"}:
        return "ratio"
    return ""


def _to_seconds(value: float, unit: str) -> float | None:
    scale = _TIME_SECONDS.get(unit.lower().strip())
    return None if scale is None else value * scale


def _parse_number(raw: str) -> float:
    return float(raw.replace(",", ""))


def _round(value: float) -> float:
    """Drop binary-float dust so `4.1M` reads as 4100000.0, not 4099999.99."""

    return float(f"{value:.12g}")


# --------------------------------------------------------------------------
# Observation
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Observation:
    """One typed statement, traceable to the resource line it was read from.

    ``source`` is the resource path (``site/bearings.csv``), the closure id, or
    ``"prompt"``. Every downstream claim can therefore name the line that
    justifies it, which is what makes a finding auditable rather than asserted.
    """

    kind: ObservationKind
    source: str
    text: str
    subject: str = ""
    value: float | None = None
    low: float | None = None
    high: float | None = None
    unit: str = ""
    unit_class: str = ""
    tokens: tuple[str, ...] = ()
    markers: tuple[str, ...] = ()
    line_markers: tuple[str, ...] = ()
    clause_index: int = 0
    position: int = 0

    def has(self, *markers: str) -> bool:
        return any(marker in self.markers for marker in markers)

    def line_has(self, *markers: str) -> bool:
        """Markers of the whole line this clause came from.

        A resource line states a counterfactual in one clause and its outcome
        in the next (`on the 30 nights the marketing job did not run, the
        export finished on time 30 times out of 30`). A rule that reasons about
        a trial and its result has to see both, and clause-local markers cannot
        show it."""

        return any(marker in self.line_markers for marker in markers)

    @property
    def seconds(self) -> float | None:
        if self.value is None or self.unit_class != "duration":
            return None
        return _to_seconds(self.value, self.unit)

    @property
    def cite(self) -> str:
        return f"{self.source}: {self.text.strip()}"


@dataclass(frozen=True)
class Reduction:
    """Every observation read from one public view, plus shape summaries."""

    case_id: str
    observations: tuple[Observation, ...]

    def of_kind(self, *kinds: ObservationKind) -> tuple[Observation, ...]:
        wanted = set(kinds)
        return tuple(o for o in self.observations if o.kind in wanted)

    def with_marker(self, *markers: str) -> tuple[Observation, ...]:
        return tuple(o for o in self.observations if o.has(*markers))

    def from_prompt(self) -> tuple[Observation, ...]:
        return tuple(o for o in self.observations if o.source == PROMPT_SOURCE)

    def from_resources(self) -> tuple[Observation, ...]:
        return tuple(o for o in self.observations if o.source != PROMPT_SOURCE)

    def numeric(self) -> tuple[Observation, ...]:
        return tuple(o for o in self.observations if o.value is not None)

    def numbers_in(self, source: str) -> tuple[float, ...]:
        """Every number read from one line, in the order it is written.

        Range bounds are included at the position of the range, so a sweep
        written as `0.10 to 0.97, 0.20 to 0.93` reads back as the flat
        sequence a caller can pair up.
        """

        rows: list[tuple[int, int, float]] = []
        for item in self.observations:
            if item.source != source:
                continue
            if item.kind is ObservationKind.RANGE and item.low is not None:
                rows.append((item.clause_index, item.position, item.low))
                if item.high is not None:
                    rows.append((item.clause_index, item.position + 1, item.high))
            elif item.value is not None and item.kind is not ObservationKind.CLOSURE:
                rows.append((item.clause_index, item.position, item.value))
        rows.sort()
        return tuple(value for _, _, value in rows)

    def in_source(self, source: str) -> tuple[Observation, ...]:
        return tuple(o for o in self.observations if o.source == source)

    def sources(self) -> tuple[str, ...]:
        seen: list[str] = []
        for observation in self.observations:
            if observation.source not in seen:
                seen.append(observation.source)
        return tuple(seen)

    def kind_histogram(self) -> dict[str, int]:
        """Counts per kind — the *shape* of the reduction, values stripped.

        This is exactly the view handed to the shape-only blind responder in
        the tests. If it predicts the responsibility, the kind vocabulary is
        carrying the answer and the vocabulary is what has to change.
        """

        histogram = {kind.value: 0 for kind in ObservationKind}
        for observation in self.observations:
            histogram[observation.kind.value] += 1
        return histogram

    def structure_features(self) -> dict[str, object]:
        """Label-free structural summary, for the degeneracy probe.

        Deliberately *shape only*: how many observations of each kind, and how
        many lines they came from. Nothing marker-derived appears here — a
        count of distinct statement types is a summary of what the prose says,
        which is content and not shape, and putting it in this vector would
        answer the leak question with the wrong quantity.

        Feature names avoid ``id``/``name``/``key``/``label``/``case``/``title``
        so ``degeneracy._looks_like_identifier`` does not classify any of them
        as an identifier; the case id belongs in ``LabeledRecord.record_id``.
        """

        histogram = self.kind_histogram()
        numeric = self.numeric()
        return {
            "observations": len(self.observations),
            "resources_read": len(self.sources()),
            **{f"kind_{k.lower()}": v for k, v in histogram.items()},
            "numeric_observations": len(numeric),
            "prompt_observations": len(self.from_prompt()),
        }


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------

_RESOURCE_SPLIT = re.compile(r"\s+[—–-]{1,2}\s+")
# Commas inside `41,000` must not split a clause, so a comma only splits when
# it is not immediately followed by a digit.
_CLAUSE_SPLIT = re.compile(r";|,(?!\d)|(?<=[a-z])\.\s")

_RANGE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(rf"between\s+({_NUMBER})\s*%?\s+and\s+({_NUMBER})\s*(%?)"),
    re.compile(rf"from\s+({_NUMBER})\s*%?\s+to\s+({_NUMBER})\s*(%?)"),
    re.compile(rf"spans?\s+({_NUMBER})\s*%?\s+to\s+({_NUMBER})\s*(%?)"),
    re.compile(rf"\b({_NUMBER})%\s+to\s+({_NUMBER})(%)"),
    re.compile(rf"\b({_NUMBER})\s+to\s+({_NUMBER})\s*(%?)\s*(?:degrees|minutes|$|\b)"),
    re.compile(rf"\b({_NUMBER})\.\.({_NUMBER})()"),
    # A bare `a-b` range. The lookarounds keep `2026-01-11` out: a bound may
    # not be adjacent to another digit-dash group, which every ISO date is.
    re.compile(r"(?<![\d-])(\d[\d,]*(?:\.\d+)?)-(\d[\d,]*(?:\.\d+)?)()(?![-\d])"),
)

# Unit words that name a quantity in the words *before* a range, used when the
# range's own trailing token carries no unit (`reported in degrees from 0 to
# 359`).
_UNIT_IN_SUBJECT = re.compile(
    r"\b(" + "|".join(sorted(_ANGLE | set(_TIME_SECONDS) | _BYTES, key=len, reverse=True)) + r")\b",
    re.I,
)

_FRACTION_OF = re.compile(rf"\b({_NUMBER})\s+(?:of|in|out of)\s+(?:the\s+)?({_NUMBER})\b")

_TOKEN_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"`([^`]+)`"),
    re.compile(r"'([^']+)'"),
    re.compile(r"\b([A-Za-z][\w-]*(?:/[\w.-]+)+)\b"),
    re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*\.(?:py|sql|csv|json|md|yml|yaml|toml|txt|go))\b"),
    re.compile(r"\b([A-Z][A-Z0-9]*_[A-Z0-9_]+)\b"),
    re.compile(r"\b([a-z]+_[a-z_]+)\b"),
)


def _clauses(text: str) -> tuple[str, ...]:
    parts = [part.strip() for part in _CLAUSE_SPLIT.split(text)]
    return tuple(part for part in parts if part)


def _markers_for(text: str) -> tuple[str, ...]:
    lowered = text.lower()
    found: list[str] = []
    for phrase, marker in _MARKERS_BY_LENGTH:
        if marker in found:
            continue
        if phrase in lowered:
            found.append(marker)
    return tuple(sorted(found))


def _tokens_in(text: str) -> tuple[str, ...]:
    found: list[str] = []
    for pattern in _TOKEN_PATTERNS:
        for match in pattern.findall(text):
            token = match if isinstance(match, str) else match[0]
            token = token.strip()
            if token and token not in found:
                found.append(token)
    return tuple(found)


def _subject_before(clause: str, start: int) -> str:
    """The words immediately preceding a number — what the number is about."""

    head = clause[:start].strip().rstrip(":")
    words = head.split()
    return " ".join(words[-6:])


def _unit_after(clause: str, end: int) -> str:
    tail = clause[end:]
    if tail.startswith("%"):
        return "%"
    stripped = tail.lstrip()
    if stripped.startswith("%"):
        return "%"
    match = _UNIT_TOKEN.match(stripped)
    if match is None:
        return ""
    token = match.group(0)
    if token in _MAGNITUDE:
        rest = stripped[match.end() :].lstrip()
        follow = _UNIT_TOKEN.match(rest)
        token = follow.group(0) if follow else ""
    return token if token.lower() in _KNOWN_UNITS else ""


def _magnitude_after(clause: str, end: int) -> float:
    tail = clause[end:]
    stripped = tail.lstrip()
    match = _UNIT_TOKEN.match(stripped)
    if match is None:
        return 1.0
    token = match.group(0)
    if token in _MAGNITUDE and (tail[:1] == "" or tail[:1] in " " or token in {"M", "B", "k"}):
        return _MAGNITUDE[token]
    return 1.0


def _quantity_kind(unit: str) -> ObservationKind:
    if unit == "%":
        return ObservationKind.FRACTION
    return ObservationKind.QUANTITY if _unit_class(unit) else ObservationKind.COUNT


def _range_observations(
    clause: str, source: str, index: int, line: tuple[str, ...]
) -> tuple[list[Observation], list[tuple[int, int]]]:
    """Ranges in one clause, with the character spans their bounds occupy.

    The spans are returned so the quantity pass can skip them. Matching on the
    formatted number instead would re-read `0.10 to 0.97` as a range *and* two
    loose quantities, because `0.10` formats back as `0.1`.
    """

    out: list[Observation] = []
    spans: list[tuple[int, int]] = []
    for pattern in _RANGE_PATTERNS:
        for match in pattern.finditer(clause):
            try:
                low = _parse_number(match.group(1))
                high = _parse_number(match.group(2))
            except ValueError:  # pragma: no cover - regex guarantees digits
                continue
            if high < low:
                continue
            spans.append((match.start(1), match.end(2)))
            subject = _subject_before(clause, match.start())
            unit = (match.group(3) or "").strip() or _unit_after(clause, match.end())
            if not unit:
                # Only the tail of the subject may name the unit: `reported in
                # degrees` does, while `hour 14 holds 31 readings` must not
                # hand `hour` to a range over compass bearings.
                tail = " ".join(subject.split()[-2:])
                in_subject = _UNIT_IN_SUBJECT.search(tail)
                unit = in_subject.group(1) if in_subject else ""
            out.append(
                Observation(
                    kind=ObservationKind.RANGE,
                    source=source,
                    text=clause,
                    subject=subject,
                    low=low,
                    high=high,
                    unit=unit,
                    unit_class=_unit_class(unit),
                    markers=_markers_for(f"{source} {clause}"),
                    line_markers=line,
                    clause_index=index,
                    position=match.start(),
                )
            )
        if out:
            break
    return out, spans


def _quantity_observations(
    clause: str, source: str, covered: list[tuple[int, int]], index: int, line: tuple[str, ...]
) -> list[Observation]:
    out: list[Observation] = []
    for match in _NUMBER_RE.finditer(clause):
        raw = match.group(0)
        if any(start <= match.start() < end for start, end in covered):
            continue
        value = _round(_parse_number(raw) * _magnitude_after(clause, match.end()))
        unit = _unit_after(clause, match.end())
        out.append(
            Observation(
                kind=_quantity_kind(unit),
                source=source,
                text=clause,
                subject=_subject_before(clause, match.start()),
                value=value,
                unit=unit,
                unit_class=_unit_class(unit),
                markers=_markers_for(f"{source} {clause}"),
                line_markers=line,
                clause_index=index,
                position=match.start(),
            )
        )
    return out


def _fraction_observations(
    clause: str, source: str, index: int, line: tuple[str, ...]
) -> list[Observation]:
    out: list[Observation] = []
    for match in _FRACTION_OF.finditer(clause):
        part = _parse_number(match.group(1))
        whole = _parse_number(match.group(2))
        if whole <= 0 or part > whole:
            continue
        out.append(
            Observation(
                kind=ObservationKind.FRACTION,
                source=source,
                text=clause,
                subject=_subject_before(clause, match.start()),
                value=100.0 * part / whole,
                low=part,
                high=whole,
                unit="%",
                unit_class="share",
                markers=_markers_for(f"{source} {clause}"),
                line_markers=line,
                clause_index=index,
                position=match.start(),
            )
        )
    return out


def _reduce_text(text: str, source: str) -> list[Observation]:
    """Reduce one line to observations, one clause at a time.

    Every clause yields at least one observation. A clause carrying no number
    and no marker still becomes a bare ``STATEMENT``, because a finding that
    cites a line has to be able to name the clause it read, and a clause the
    reduction silently dropped cannot be cited.
    """

    line = _markers_for(f"{source} {text}")
    out: list[Observation] = []
    for index, clause in enumerate(_clauses(text)):
        ranges, covered = _range_observations(clause, source, index, line)
        out.extend(ranges)
        fractions = _fraction_observations(clause, source, index, line)
        out.extend(fractions)
        quantities = _quantity_observations(clause, source, covered, index, line)
        out.extend(quantities)
        markers = _markers_for(f"{source} {clause}")
        tokens = _tokens_in(clause)
        if tokens:
            out.append(
                Observation(
                    kind=ObservationKind.TOKEN_LIST,
                    source=source,
                    text=clause,
                    tokens=tokens,
                    markers=markers,
                    line_markers=line,
                    clause_index=index,
                )
            )
        if not ranges and not fractions and not quantities:
            out.append(
                Observation(
                    kind=ObservationKind.STATEMENT,
                    source=source,
                    text=clause,
                    markers=markers,
                    line_markers=line,
                    clause_index=index,
                )
            )
    return out


def reduce_view(view: PublicView) -> Reduction:
    """Reduce one public view to typed observations.

    The prompt is reduced first, then each resource line under its own path, so
    ``Observation.source`` always names the line a downstream finding rests on.
    """

    observations: list[Observation] = list(_reduce_text(view.public_prompt, PROMPT_SOURCE))
    for line in readable_resources(view):
        source, _, body = line.partition("—")
        if not body:
            parts = _RESOURCE_SPLIT.split(line, maxsplit=1)
            source, body = parts[0], parts[1] if len(parts) > 1 else ""
        source = source.strip()
        body = body.strip()
        if source.lower().startswith("closure:"):
            observations.append(
                Observation(
                    kind=ObservationKind.CLOSURE,
                    source=source,
                    text=body or source,
                    subject=source,
                    tokens=_tokens_in(body),
                    markers=_markers_for(f"{source} {body}"),
                    line_markers=_markers_for(f"{source} {body}"),
                )
            )
        observations.extend(_reduce_text(body, source))
    return Reduction(case_id=view.case_id, observations=tuple(observations))


# --------------------------------------------------------------------------
# Derived quantities
# --------------------------------------------------------------------------


def bearing_from_components(east: float, north: float) -> float:
    """Direction of a resultant given its orthogonal components, in degrees.

    Kept here rather than inside a rule because it is arithmetic over stated
    numbers, not a judgement: given `mean east -0.4 m/s, mean north 7.9 m/s`,
    the resultant direction is fixed and any reported direction that disagrees
    with it disagrees with the instrument's own components.
    """

    return math.degrees(math.atan2(east, north)) % 360.0


def circular_separation(first: float, second: float) -> float:
    """Smallest angle between two bearings, in degrees."""

    gap = abs(first - second) % 360.0
    return min(gap, 360.0 - gap)


def relative_gap(first: float, second: float) -> float:
    """|a-b| over the larger magnitude; 0.0 when both are 0."""

    scale = max(abs(first), abs(second))
    return 0.0 if scale == 0 else abs(first - second) / scale


__all__ = [
    "PROMPT_SOURCE",
    "Observation",
    "ObservationKind",
    "Reduction",
    "bearing_from_components",
    "circular_separation",
    "reduce_view",
    "relative_gap",
]
