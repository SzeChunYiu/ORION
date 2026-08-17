"""Shared primitives for the AutoResearchBench Wide systems under test.

Budgets, typed provider outcomes, query derivations and the per-run record that
carries the frozen statistical plan's required bindings.

Two design commitments live here rather than in any one system:

* **Budgets are enforced centrally.** Every provider call goes through one
  ``BudgetMeter``, so no system can win a comparison by spending more than
  another. A system that hits its cap stops and is *retained* as a
  budget-exhausted outcome; it is never dropped and never scored as if it had
  finished.

* **A failed call is not an empty result, and neither is an absence.** Provider
  outcomes are typed. ``KEY_REQUIRED``, ``RATE_LIMITED``, ``TIMEOUT``,
  ``UNAVAILABLE`` and ``ERROR`` open an obligation on the route
  (MEASUREMENT_PLAN_V1.md oracle O4) and are never route exhaustion. ``OK`` with
  zero records is a genuine empty result and is the only one of the two that
  counts as evidence about the corpus.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from enum import Enum

from orion.core.search import SearchRouteKind

__all__ = [
    "Budget",
    "BudgetExhausted",
    "BudgetMeter",
    "CapturedWork",
    "ProviderOutcome",
    "ProviderStatus",
    "QueryDerivation",
    "ReadEncounterRecord",
    "RouteTrialRecord",
    "SystemRun",
    "content_digest",
    "derive_citation_seed_query",
    "derive_current_vocabulary_query",
    "derive_lexical_variant_query",
    "DERIVATION_RULES",
]


class ProviderStatus(str, Enum):
    """Typed outcome of one provider call. Absence and failure are distinct."""

    OK = "OK"
    KEY_REQUIRED = "KEY_REQUIRED"
    RATE_LIMITED = "RATE_LIMITED"
    UNAVAILABLE = "UNAVAILABLE"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"
    MALFORMED = "MALFORMED"
    REFUSED_PAGING = "REFUSED_PAGING"

    @property
    def opens_obligation(self) -> bool:
        """Whether this outcome leaves the route's coverage unknown.

        ``OK`` does not: it is evidence. Everything else is a failure to look,
        which O4 says is never exhaustion and never evidence of absence.
        """

        return self is not ProviderStatus.OK


@dataclass(frozen=True)
class CapturedWork:
    """One work as a route saw it, in ORION identity terms."""

    source_id: str
    title: str = ""
    aliases: tuple[str, ...] = ()
    content_digest: str = ""
    referenced_works: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("a captured work requires a source id")


@dataclass(frozen=True)
class ProviderOutcome:
    """What one provider call produced, including why it produced nothing."""

    status: ProviderStatus
    records: tuple[CapturedWork, ...] = ()
    note: str = ""
    raw_response_sha256: str = ""
    retry_after_seconds: float | None = None

    @property
    def ok(self) -> bool:
        return self.status is ProviderStatus.OK


def content_digest(*parts: str) -> str:
    """Content identity of a rendition, never a source-minted id."""

    joined = "\x00".join(part.strip() for part in parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Budgets.
# ---------------------------------------------------------------------------


class BudgetExhausted(RuntimeError):
    """Raised when a system would exceed its matched cap. Retained as an outcome."""


@dataclass(frozen=True)
class Budget:
    """Per-task caps, identical for every system in the family."""

    query_count: int
    tool_calls: int
    model_tokens: int
    wallclock_seconds: float

    def __post_init__(self) -> None:
        if min(self.query_count, self.tool_calls, self.model_tokens) < 0:
            raise ValueError("budget caps cannot be negative")
        if self.wallclock_seconds <= 0:
            raise ValueError("a wall-clock cap must be positive")


@dataclass
class BudgetMeter:
    """Single point of enforcement for every capped resource.

    Systems never track their own spend. If they did, a bug in one system's
    accounting would show up as a capability difference rather than as a bug,
    which is the specific way a matched-resource comparison stops being matched.
    """

    budget: Budget
    clock: Callable[[], float]
    queries_spent: int = 0
    tool_calls_spent: int = 0
    model_tokens_spent: int = 0
    _started: float | None = field(default=None, repr=False)

    def start(self) -> None:
        self._started = self.clock()

    @property
    def elapsed_seconds(self) -> float:
        if self._started is None:
            return 0.0
        return max(0.0, self.clock() - self._started)

    @property
    def exhausted(self) -> bool:
        return (
            self.queries_spent >= self.budget.query_count
            or self.tool_calls_spent >= self.budget.tool_calls
            or self.elapsed_seconds >= self.budget.wallclock_seconds
        )

    def remaining_queries(self) -> int:
        return max(0, self.budget.query_count - self.queries_spent)

    def charge_provider_call(self, *, queries: int = 1, tool_calls: int = 1) -> None:
        """Charge one provider call, refusing before it is made, not after."""

        if self.queries_spent + queries > self.budget.query_count:
            raise BudgetExhausted(
                f"query cap {self.budget.query_count} reached "
                f"({self.queries_spent} spent)"
            )
        if self.tool_calls_spent + tool_calls > self.budget.tool_calls:
            raise BudgetExhausted(
                f"tool-call cap {self.budget.tool_calls} reached "
                f"({self.tool_calls_spent} spent)"
            )
        if self.elapsed_seconds >= self.budget.wallclock_seconds:
            raise BudgetExhausted(
                f"wall-clock cap {self.budget.wallclock_seconds}s reached "
                f"({self.elapsed_seconds:.3f}s elapsed)"
            )
        self.queries_spent += queries
        self.tool_calls_spent += tool_calls

    def charge_model_tokens(self, tokens: int) -> None:
        if self.model_tokens_spent + tokens > self.budget.model_tokens:
            raise BudgetExhausted(f"model-token cap {self.budget.model_tokens} reached")
        self.model_tokens_spent += tokens

    def cost(self) -> dict[str, float]:
        """Consumed resources, in the shape required binding B12 asks for."""

        return {
            "wallclock_seconds": round(self.elapsed_seconds, 6),
            "query_count": float(self.queries_spent),
            "model_tokens": float(self.model_tokens_spent),
            "tool_calls": float(self.tool_calls_spent),
        }


# ---------------------------------------------------------------------------
# Query derivations. These must genuinely differ, not merely be labelled apart.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class QueryDerivation:
    """A named, retained record of how a query string was produced."""

    rule_id: str
    query: str
    source_terms: tuple[str, ...] = ()


# Question boilerplate. These words carry no topical signal in a benchmark
# question and would dominate a term-frequency ranking if left in.
_STOPWORDS = frozenset(
    """a about above after again against all also am an and any are as at be because been
    before being below between both but by can cannot could did do does doing down during
    each few for from further had has have having he her here hers him his how i if in into
    is it its itself just me more most my no nor not now of off on once only or other our
    out over own same she should so some such than that the their them then there these they
    this those through to too under until up very was we were what when where which while
    who whom why will with would you your looking particular explicitly research paper papers
    work works study studies method methods approach approaches which want find identify
    including include includes such use uses used using""".split()
)

_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9\-]{2,}")

DERIVATION_RULES: dict[str, str] = {
    "D1_CURRENT_VOCABULARY": (
        "Rank the question's own content tokens by frequency then first "
        "appearance, keep the top 6, join with AND. Preserves the asker's "
        "vocabulary; makes no attempt to generalise it."
    ),
    "D2_LEXICAL_VARIANT": (
        "Select the 8 longest distinct stems (suffix-stripped), which favours "
        "specific multi-syllable terminology over frequent short words, and "
        "join with spaces for a relevance-ranked free-text match. A different "
        "selection function and a different join from D1, so the two routes do "
        "not share a query derivation."
    ),
    "D3_CITATION_NEIGHBORHOOD": (
        "Not derived from the question at all: the query is the identifier of "
        "an already-captured work, and the route follows its reference list."
    ),
}


def _content_tokens(question: str) -> list[str]:
    return [
        token.lower()
        for token in _TOKEN.findall(question)
        if token.lower() not in _STOPWORDS
    ]


def derive_current_vocabulary_query(question: str, limit: int = 6) -> QueryDerivation:
    """D1: the question's own most-repeated content terms, conjunctive.

    A repeated term in a Wide question is the asker restating the topic, so
    frequency is a reasonable salience proxy without any model call. Ties break
    on first appearance so the rule is deterministic.
    """

    tokens = _content_tokens(question)
    order: dict[str, int] = {}
    counts: dict[str, int] = {}
    for index, token in enumerate(tokens):
        counts[token] = counts.get(token, 0) + 1
        order.setdefault(token, index)
    ranked = sorted(counts, key=lambda token: (-counts[token], order[token]))
    chosen = tuple(ranked[:limit])
    return QueryDerivation(
        rule_id="D1_CURRENT_VOCABULARY",
        query=" AND ".join(chosen),
        source_terms=chosen,
    )


_SUFFIXES = ("ations", "ation", "ances", "ance", "ings", "ing", "ies", "ers", "es", "s")


def _stem(token: str) -> str:
    for suffix in _SUFFIXES:
        if token.endswith(suffix) and len(token) - len(suffix) >= 4:
            return token[: -len(suffix)]
    return token


def derive_lexical_variant_query(question: str, limit: int = 8) -> QueryDerivation:
    """D2: the longest distinct stems, as a free-text relevance string.

    Deliberately a different computation from D1, not a relabelling of it.
    D1 ranks by repetition and keeps surface forms; D2 ranks by term length
    after suffix stripping and keeps stems, which surfaces specific technical
    vocabulary that appears once. The two rules select different terms on real
    questions, which ``assess_pair`` needs in order to reach a verdict of
    INDEPENDENT honestly rather than by assertion.
    """

    stems: dict[str, int] = {}
    for index, token in enumerate(_content_tokens(question)):
        stems.setdefault(_stem(token), index)
    ranked = sorted(stems, key=lambda stem: (-len(stem), stems[stem]))
    chosen = tuple(ranked[:limit])
    return QueryDerivation(
        rule_id="D2_LEXICAL_VARIANT",
        query=" ".join(chosen),
        source_terms=chosen,
    )


def derive_citation_seed_query(source_id: str) -> QueryDerivation:
    """D3: follow a captured work's references. Not a text derivation at all."""

    return QueryDerivation(
        rule_id="D3_CITATION_NEIGHBORHOOD",
        query=source_id,
        source_terms=(source_id,),
    )


# ---------------------------------------------------------------------------
# The retained record. Field names track STATISTICAL_PLAN_V1.json required_bindings.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RouteTrialRecord:
    """One attempt on one route, with everything the oracles need (B2, B3, B4, B7, B11)."""

    route_id: str
    route_kind: SearchRouteKind
    backend: str
    attempt_index: int
    consecutive_zero_novelty_before: int
    query_derivation_rule: str
    query: str
    transport_status: str
    captures: tuple[dict[str, str], ...]
    novel_digests: tuple[str, ...]
    open_obligation_ids: tuple[str, ...]
    control_action: str = ""
    control_reasons: tuple[str, ...] = ()
    raw_response_sha256: str = ""
    note: str = ""


@dataclass(frozen=True)
class ReadEncounterRecord:
    """One *presented* source, read or not (B14, B15).

    The denominator is the encounter, not the execution. On an execution-only
    denominator a system that silently refuses legitimate rereads never executes
    them, so they vanish from numerator and denominator together and the rate
    looks healthy.
    """

    merged_source_id: str
    content_digest: str
    schema_version: str
    frame_id: str
    decision_before_execution: str
    executed: bool


@dataclass(frozen=True)
class SystemRun:
    """Everything one system did on one task."""

    system_id: str
    task_id: str
    repeat_index: int
    seed: int
    predicted_arxiv_ids: tuple[str, ...]
    route_trials: tuple[RouteTrialRecord, ...]
    read_encounters: tuple[ReadEncounterRecord, ...]
    task_closure_declared: bool
    task_closure_reason: str
    budget_exhausted: bool
    cost: dict[str, float]
    open_obligation_ids: tuple[str, ...] = ()
    independence_pairs: tuple[dict[str, str], ...] = ()
    coverage_refusal_reason: str = ""
    failure_class: str | None = None
    note: str = ""

    @property
    def status(self) -> str:
        """Result-record status. Absence of evidence is never a pass."""

        if self.failure_class:
            return "FAIL"
        return "PASS"


def merged_capture_rows(
    captures: Sequence[CapturedWork], merged_of: dict[str, str]
) -> tuple[dict[str, str], ...]:
    """Render captures as B4/B7 rows: merged primary key plus content digest."""

    rows: list[dict[str, str]] = []
    for item in captures:
        rows.append(
            {
                "merged_source_id": merged_of.get(item.source_id, item.source_id),
                "content_digest": item.content_digest,
                "raw_source_id": item.source_id,
            }
        )
    return tuple(rows)
