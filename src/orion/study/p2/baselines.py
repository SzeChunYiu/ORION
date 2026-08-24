"""The six matched-budget baselines PROTOCOL_V1 froze for the P2 discovery study.

What a baseline can and cannot be in this world
----------------------------------------------
Retrieval here is exact posting-list membership: `DiscoverySession.query(route,
probe)` returns every document whose authored access key for that route equals
that probe, unranked (`corpus.DiscoveryWorld.lookup`). There is no scoring
retrieval function to replace, so a baseline's competence lives in two places
and only two:

1. **probe selection** — which of the published probes to spend a metered route
   call on, and in what order, under a budget set below the cost of enumerating
   them all; and
2. **screening** — which of the returned records to spend a read on, and which
   to claim as relevant.

Everything below is therefore a *ranking policy over probes and records*. Saying
so plainly matters: a reader who assumed these baselines were competing retrieval
engines would be reading a different experiment than the one that ran.

Honest naming of `dense_retrieval`
----------------------------------
`dense_retrieval` is **not neural**. It is a deterministic lexical-distributional
retriever built in this repository from the standard hashing trick over whole
tokens and character trigrams, scored by cosine. It carries no learned
parameters, no pretrained embedding table and no model of any kind. It therefore
bridges *morphological* variation (``estimation``/``estimator``) and nothing
more. It cannot bridge a true paraphrase, and this world contains paraphrase gaps
by construction — `corpus._TopicPlan.semantic_key` shares no token with
`lexical_key`, so no lexical-distributional method reaches paraphrase-only gold.
No claim about neural dense retrieval may be drawn from this baseline, and the
manuscript must not imply one was tested.

Declared constants
------------------
Every numeric constant in this module is declared once, at module level, with the
external convention it comes from. **None was fitted to the frozen suite**: no
baseline in this module has been run over the frozen task suite, and no
comparative score exists to have fitted them against.

One structural fact about the corpus did inform a *rule class* choice, and is
disclosed here rather than hidden: every record in a topic's neighbourhood — gold
and distractor alike — embeds the topic label sentence, so BM25 scores within a
neighbourhood are compressed into a narrow band. Screening by absolute or
relative *score magnitude* is uninformative in such a band; screening by *rank*
is not. These baselines therefore screen by rank and declared depth, which is
also what conventional IR practice does. The distractors carry one of the two
required concepts each, so a lexical system ranks them below gold but inside a
recall-oriented depth, and pays precision for them. That cost is designed into
the world (`corpus._topic_documents`) and is not engineered around here.

Transport status is three-valued, not two
-----------------------------------------
`OK` with records, `OK` with no records, and a transport failure are three
different things and every baseline here treats them as three:

- `OK` with records — the route is productive;
- `OK` with zero records — the route answered and had nothing; evidence the
  route is dry, and the only one of the three that licenses abandoning it;
- `UNAVAILABLE` / `TIMEOUT` / `ERROR` — the provider did not answer. What it
  holds is *censored*, not absent. This opens an obligation that no baseline
  discharges by inference, and while one is open no baseline closes the task.

Budget exhaustion
-----------------
`runner.execute` replaces the report with an empty one if `BudgetExhausted`
escapes `run`, so a baseline that lets it propagate scores zero regardless of
what it found. Every baseline here funnels session access through `_Run`, which
catches exhaustion, latches it, and returns what was accumulated. Per
`STATISTICAL_PLAN_V1.matched_budget_policy.cap_hit_rule`, a run truncated at a
cap "did not declare closure": exhaustion forces `task_closed_as_complete=False`.

Required bindings
-----------------
`STATISTICAL_PLAN_V1.required_bindings` names sixteen fields. Most are host-owned
and the harness emits them. Two are not derivable from anything the host records:
B14 (`read_encounter.decision_before_execution`) and B15
(`read_encounter.executed`) are specified per *presented* record "whether or not
a read followed", and the session only ever records reads that executed — an
encounter a system declined is invisible to it by construction. The frozen
`SystemReport` has no field for them. Each baseline therefore accumulates them,
together with the route-trial bindings B2/B3/B11, on itself as a `BindingTrace`
reachable via `bindings_for(task_id, seed)`. Stuffing JSON into `SystemReport.
notes` was rejected as a fake structured channel. Widening the result record is
harness work and is not done here.
"""

from __future__ import annotations

import hashlib
import math
import random
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Any

from orion.core.search import SearchRouteKind
from orion.knowledge.route_control import (
    FrozenRouteControlPolicy,
    RouteAttempt,
    RouteControlAction,
    RouteControlState,
    decide_route,
)

from .cases import PublicView
from .corpus import ROUTE_SPEC_BY_ROUTE, DiscoveryRoute
from .runner import BudgetExhausted
from .systems import (
    DiscoverySession,
    ReadOutcome,
    RetrievedRecord,
    RouteOutcome,
    SystemReport,
    TransportStatus,
)

# ---------------------------------------------------------------------------
# Declared constants. Provenance is an external convention in every case; none
# is fitted to the frozen suite, which no baseline in this module has been run
# against.
# ---------------------------------------------------------------------------

#: Okapi BM25 term-frequency saturation and length normalisation. The values
#: Robertson & Zaragoza (2009) give as the standard operating point, and the
#: defaults shipped by Lucene and Anserini.
BM25_K1 = 1.2
BM25_B = 0.75

#: Screening depth for `bm25_keyword`: the records it is willing to claim, taken
#: in BM25 rank order. Twenty is a conventional recall-oriented pool depth in
#: TREC-style evaluation, chosen over depth-10 because the task question asks for
#: *every* qualifying study.
BM25_SCREEN_DEPTH = 20

#: Reciprocal-rank-fusion constant, from Cormack, Clarke & Buettcher (2009),
#: which introduces RRF and uses k=60 throughout. Equal weight per system: an
#: unequal weight would be a free parameter with no external justification.
RRF_K = 60

#: Hashing-trick width and character n-gram order for the distributional
#: retriever. 2**8 dimensions and trigrams are conventional settings for
#: hashed character-n-gram text vectors.
HASH_DIMENSIONS = 256
CHAR_NGRAM_ORDER = 3

#: Weight on character-trigram evidence relative to whole-token evidence.
#: Trigrams are a secondary, morphological signal and are weighted below whole
#: tokens; one half is the conventional subordinate weighting.
CHAR_NGRAM_WEIGHT = 0.5

#: `one_pass_rag`: one retrieval pass, then screening of exactly that set. Ten is
#: the conventional top-k context depth in retrieval-augmented generation.
ONE_PASS_RETRIEVAL_DEPTH = 10

#: `one_pass_rag`: how many route calls constitute its single pass. A single call
#: could not touch more than one route, which would silently make it a
#: single-route system and duplicate `agentic_single_route`; one call per
#: available route is the smallest pass that keeps the two baselines distinct.
ONE_PASS_CALLS_PER_ROUTE = 1

#: `agentic_single_route`: the frozen route-control policy it reformulates under.
#: Both thresholds are the smallest values `FrozenRouteControlPolicy` admits,
#: so the policy is fully determined by its own validation rules rather than by
#: a choice made here.
AGENTIC_ROUTE_POLICY = FrozenRouteControlPolicy(
    policy_id="p2.baseline.agentic_single_route.v1",
    reformulate_after_zero_novelty=1,
    switch_after_zero_novelty=2,
)

#: `protocol_driven_systematic_review`: stop after this many consecutive screened
#: records fail the eligibility criteria. Consecutive-irrelevant stopping rules
#: are standard in the systematic-review screening literature; twenty-five and
#: fifty are common values at review scale, and five is the same rule scaled to a
#: world whose per-task read budget is twenty-four.
SR_STOP_AFTER_CONSECUTIVE_NON_ELIGIBLE = 5

#: Every session call is one tool call. Declared through `session.spend` so
#: budgets stay matched across systems.
TOOL_CALLS_PER_SESSION_CALL = 1

#: These baselines are deterministic and call no language model, so they declare
#: zero model tokens. Declaring a nonzero figure would be fabricating a cost that
#: was never paid.
MODEL_TOKENS_PER_CALL = 0


_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")

#: A small closed stoplist: English function words, plus the boilerplate the task
#: questions and the corpus's generated abstracts share verbatim
#: (`cases.build_tasks`, `corpus._topic_documents`). Leaving the boilerplate in
#: would let every record in the world match the query on words that carry no
#: topical information at all.
_STOPWORDS = frozenset(
    """
    a an and are as at be by for from has have in into is it its of on or that the
    this to was were which with
    identify every study studies addressing record records reports findings tagged
    concerns
    """.split()
)


def tokenize(text: str) -> tuple[str, ...]:
    """Lowercase, split on any non-alphanumeric run, drop stopwords and unigrams.

    Splitting on non-alphanumerics means an underscored concept tag such as
    ``measurement_invariance`` becomes ``measurement`` and ``invariance``. That is
    the single decision the lexical baselines rest on, and it is a property of the
    tokenizer rather than of this corpus: underscore-joined compounds are split by
    every standard analyzer.
    """

    return tuple(
        token
        for token in _TOKEN_PATTERN.findall(text.lower())
        if token not in _STOPWORDS and len(token) > 1
    )


def derive_query_terms(question: str) -> tuple[str, ...]:
    """The fixed rule turning a task question into query terms.

    Tokenize the question, drop stopwords, keep first occurrence order. No
    expansion, no synonym list and no reference to the corpus: a derivation that
    consulted the world would be deriving the query from the answer.
    """

    seen: dict[str, None] = {}
    for token in tokenize(question):
        seen.setdefault(token, None)
    return tuple(seen)


def _stable_hash(text: str) -> int:
    """Process-stable hash. `hash()` is salted per interpreter and would make
    every dense score irreproducible across runs."""

    return int.from_bytes(hashlib.blake2b(text.encode("utf-8"), digest_size=8).digest(), "big")


# ---------------------------------------------------------------------------
# Scorers
# ---------------------------------------------------------------------------


class Bm25Scorer:
    """Okapi BM25 over a fixed set of texts.

    Standard formulation: the Robertson/Sparck Jones IDF in its
    ``log(1 + (N - df + 0.5) / (df + 0.5))`` form, which is non-negative for every
    df and so cannot award a negative contribution to a term that appears in most
    of the collection.
    """

    def __init__(
        self,
        documents: Sequence[tuple[str, str]],
        *,
        k1: float = BM25_K1,
        b: float = BM25_B,
    ) -> None:
        self.k1 = k1
        self.b = b
        self._tokens: dict[str, tuple[str, ...]] = {key: tokenize(text) for key, text in documents}
        self._count = max(1, len(self._tokens))
        lengths = [len(item) for item in self._tokens.values()]
        self._average_length = (sum(lengths) / len(lengths)) if lengths else 1.0
        self._document_frequency: dict[str, int] = {}
        for tokens in self._tokens.values():
            for token in set(tokens):
                self._document_frequency[token] = self._document_frequency.get(token, 0) + 1

    def inverse_document_frequency(self, term: str) -> float:
        frequency = self._document_frequency.get(term, 0)
        return math.log(1.0 + (self._count - frequency + 0.5) / (frequency + 0.5))

    def score(self, key: str, terms: Sequence[str]) -> float:
        tokens = self._tokens.get(key)
        if not tokens:
            return 0.0
        length = len(tokens)
        counts: dict[str, int] = {}
        for token in tokens:
            counts[token] = counts.get(token, 0) + 1
        norm = self.k1 * (1.0 - self.b + self.b * length / (self._average_length or 1.0))
        total = 0.0
        for term in dict.fromkeys(terms):
            frequency = counts.get(term, 0)
            if not frequency:
                continue
            total += self.inverse_document_frequency(term) * (
                frequency * (self.k1 + 1.0) / (frequency + norm)
            )
        return total


class HashedDistributionalScorer:
    """Deterministic lexical-distributional vectors, scored by cosine.

    Not a neural retriever and not an embedding model. Each text becomes a sparse
    vector over `HASH_DIMENSIONS` buckets: one unit of mass per whole token, and
    `CHAR_NGRAM_WEIGHT` per character trigram of that token. Trigrams are what
    make this different from an exact-match scorer — they let ``estimation`` and
    ``estimator`` share mass — and they are also the ceiling on what it can do.
    A paraphrase that reuses no character sequence is invisible to it.
    """

    def __init__(
        self,
        documents: Sequence[tuple[str, str]],
        *,
        dimensions: int = HASH_DIMENSIONS,
        ngram_order: int = CHAR_NGRAM_ORDER,
        ngram_weight: float = CHAR_NGRAM_WEIGHT,
    ) -> None:
        self.dimensions = dimensions
        self.ngram_order = ngram_order
        self.ngram_weight = ngram_weight
        self._vectors: dict[str, dict[int, float]] = {
            key: self.vectorize(text) for key, text in documents
        }

    def vectorize(self, text: str) -> dict[int, float]:
        vector: dict[int, float] = {}
        for token in tokenize(text):
            index = _stable_hash(token) % self.dimensions
            vector[index] = vector.get(index, 0.0) + 1.0
            padded = f"^{token}$"
            for start in range(len(padded) - self.ngram_order + 1):
                gram = padded[start : start + self.ngram_order]
                gram_index = _stable_hash(gram) % self.dimensions
                vector[gram_index] = vector.get(gram_index, 0.0) + self.ngram_weight
        norm = math.sqrt(sum(value * value for value in vector.values()))
        if norm == 0.0:
            return {}
        return {index: value / norm for index, value in vector.items()}

    def score(self, key: str, query_vector: dict[int, float]) -> float:
        vector = self._vectors.get(key)
        if not vector or not query_vector:
            return 0.0
        if len(query_vector) < len(vector):
            small, large = query_vector, vector
        else:
            small, large = vector, query_vector
        return sum(value * large.get(index, 0.0) for index, value in small.items())


def reciprocal_rank_fusion(
    rankings: Sequence[Sequence[str]], *, k: int = RRF_K
) -> dict[str, float]:
    """Fuse ranked key lists into one score map. Cormack, Clarke & Buettcher (2009).

    Each list contributes ``1 / (k + rank)`` with rank one-based, equally weighted.
    Rank fusion rather than score fusion because the two scorers here are on
    incomparable scales, and normalising them would introduce a free choice.
    """

    fused: dict[str, float] = {}
    for ranking in rankings:
        for position, key in enumerate(ranking, start=1):
            fused[key] = fused.get(key, 0.0) + 1.0 / (k + position)
    return fused


# ---------------------------------------------------------------------------
# Required-binding telemetry the frozen SystemReport has no field for
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RouteTrialBinding:
    """B2, B3 and B11 for one route call, as the system saw them.

    B2 and B3 are also derivable host-side from `RouteEvent`, and B11 from the
    session's `UNAVAILABLE` events; they are recorded here so a system-side and a
    host-side derivation can be cross-checked rather than assumed equal.
    """

    route: str
    probe: str
    attempt_index: int
    consecutive_zero_novelty_before: int
    open_obligation_ids: tuple[str, ...]
    status: str
    retrieved_content_identities: tuple[str, ...]
    novel_content_identities: tuple[str, ...]

    def as_json(self) -> dict[str, Any]:
        return {
            "route": self.route,
            "probe": self.probe,
            "attempt_index": self.attempt_index,
            "consecutive_zero_novelty_before": self.consecutive_zero_novelty_before,
            "open_obligation_ids": list(self.open_obligation_ids),
            "status": self.status,
            "retrieved_content_identities": list(self.retrieved_content_identities),
            "novel_content_identities": list(self.novel_content_identities),
        }


@dataclass(frozen=True)
class ReadEncounterBinding:
    """B14 and B15: one *presented* record, whether or not a read followed.

    `NEW_SCHEMA` never occurs in this world — the offline corpus has one record
    schema — so the enum is used at four of its five values. Recording the
    encounter that did not execute is the whole point: encounter minus execution
    is what makes read suppression visible, and the host cannot see it.
    """

    merged_source_id: str
    content_digest: str
    frame_id: str
    decision_before_execution: str
    executed: bool

    def as_json(self) -> dict[str, Any]:
        return {
            "merged_source_id": self.merged_source_id,
            "content_digest": self.content_digest,
            "frame_id": self.frame_id,
            "decision_before_execution": self.decision_before_execution,
            "executed": self.executed,
        }


@dataclass
class BindingTrace:
    """The system-side half of the required bindings for one (task, seed) run."""

    system_id: str
    task_id: str
    seed: int
    route_trials: list[RouteTrialBinding] = field(default_factory=list)
    read_encounters: list[ReadEncounterBinding] = field(default_factory=list)
    open_obligation_ids_at_closure: tuple[str, ...] = ()
    truncated_at_cap: bool = False

    def as_json(self) -> dict[str, Any]:
        return {
            "system_id": self.system_id,
            "task_id": self.task_id,
            "seed": self.seed,
            "route_trials": [item.as_json() for item in self.route_trials],
            "read_encounters": [item.as_json() for item in self.read_encounters],
            "open_obligation_ids_at_closure": list(self.open_obligation_ids_at_closure),
            "truncated_at_cap": self.truncated_at_cap,
        }


# ---------------------------------------------------------------------------
# Budget-safe session wrapper shared by every baseline
# ---------------------------------------------------------------------------


class _Run:
    """One baseline's pass over one task: metered access, plus its own ledger.

    Every session call goes through here so that budget exhaustion is caught in
    exactly one place. `runner.execute` discards the report of a baseline that
    lets `BudgetExhausted` escape, which would score a system at zero recall for
    material it actually found; latching the flag and returning `None` keeps the
    partial result, which is what the cap-hit rule requires.
    """

    def __init__(self, view: PublicView, session: DiscoverySession, *, seed: int) -> None:
        self.view = view
        self.session = session
        self.rng = random.Random(seed)
        self.exhausted = False
        self.query_terms = derive_query_terms(view.question)
        self.records: dict[str, RetrievedRecord] = {}
        self.identity_order: list[str] = []
        self.seen_identities: set[str] = set()
        self.read_doc_ids: set[str] = set()
        #: (content_identity, content_digest, frame) triples this baseline has read.
        self.read_keys: set[tuple[str, str, str]] = set()
        self.read_identity_digests: set[tuple[str, str]] = set()
        self.route_attempts: dict[str, int] = {}
        self.route_zero_novelty: dict[str, int] = {}
        self.open_obligations: dict[str, str] = {}
        self.dry_routes: set[str] = set()
        self.trace = BindingTrace(system_id="", task_id=view.task_id, seed=seed)

    # -- metered access ---------------------------------------------------

    def _spend(self) -> None:
        try:
            self.session.spend(
                model_tokens=MODEL_TOKENS_PER_CALL, tool_calls=TOOL_CALLS_PER_SESSION_CALL
            )
        except BudgetExhausted:
            self.exhausted = True

    def query(self, route: str, probe: str) -> RouteOutcome | None:
        """Spend one route call. `None` means the budget is gone, not that the
        route was empty — the two must never collapse into one another."""

        if self.exhausted:
            return None
        attempt_index = self.route_attempts.get(route, 0)
        zero_novelty_before = self.route_zero_novelty.get(route, 0)
        try:
            outcome = self.session.query(route, probe)
        except BudgetExhausted:
            self.exhausted = True
            return None
        self.route_attempts[route] = attempt_index + 1

        novel: tuple[str, ...] = ()
        identities: tuple[str, ...] = ()
        if outcome.status is TransportStatus.OK:
            identities = tuple(sorted({item.content_identity for item in outcome.records}))
            novel = tuple(sorted(set(identities) - self.seen_identities))
            for record in outcome.records:
                self.records.setdefault(record.doc_id, record)
                if record.content_identity not in self.seen_identities:
                    self.seen_identities.add(record.content_identity)
                    self.identity_order.append(record.content_identity)
            if not outcome.records:
                # The route answered and had nothing. Evidence it is dry.
                self.dry_routes.add(route)
            self.route_zero_novelty[route] = 0 if novel else zero_novelty_before + 1
        else:
            # A provider that did not answer censors what it holds. Recording an
            # obligation here is what stops the run treating silence as absence.
            self.open_obligations[f"{route}:{attempt_index}"] = outcome.status.value
            self.route_zero_novelty[route] = zero_novelty_before

        self.trace.route_trials.append(
            RouteTrialBinding(
                route=route,
                probe=probe,
                attempt_index=attempt_index,
                consecutive_zero_novelty_before=zero_novelty_before,
                open_obligation_ids=tuple(sorted(self.open_obligations)),
                status=outcome.status.value,
                retrieved_content_identities=identities,
                novel_content_identities=novel,
            )
        )
        self._spend()
        return outcome

    def encounter(self, record: RetrievedRecord, *, execute: bool) -> ReadOutcome | None:
        """Present one record to the read policy, then read it or decline it.

        The decision is computed against this baseline's own ledger *before* the
        encounter, which is what B14 specifies, and is recorded whether or not the
        read follows, which is what B15 exists for.
        """

        frame = self.session.current_extraction_question
        key = (record.content_identity, record.content_digest, frame)
        if key in self.read_keys:
            decision = "ALREADY_READ"
        elif not any(
            identity == record.content_identity for identity, _ in self.read_identity_digests
        ):
            decision = "UNSEEN"
        elif (record.content_identity, record.content_digest) not in self.read_identity_digests:
            decision = "CONTENT_CHANGED"
        else:
            decision = "NEW_FRAME"

        if not execute or self.exhausted:
            self.trace.read_encounters.append(
                ReadEncounterBinding(
                    merged_source_id=record.content_identity,
                    content_digest=record.content_digest,
                    frame_id=frame,
                    decision_before_execution=decision,
                    executed=False,
                )
            )
            return None

        try:
            outcome = self.session.read(record.doc_id)
        except BudgetExhausted:
            self.exhausted = True
            self.trace.read_encounters.append(
                ReadEncounterBinding(
                    merged_source_id=record.content_identity,
                    content_digest=record.content_digest,
                    frame_id=frame,
                    decision_before_execution=decision,
                    executed=False,
                )
            )
            return None

        self.read_doc_ids.add(record.doc_id)
        self.read_keys.add(key)
        self.read_identity_digests.add((record.content_identity, record.content_digest))
        self.trace.read_encounters.append(
            ReadEncounterBinding(
                merged_source_id=record.content_identity,
                content_digest=record.content_digest,
                frame_id=frame,
                decision_before_execution=decision,
                executed=True,
            )
        )
        self._spend()
        return outcome

    def declare_route_stop(self, route: str, reason: str) -> None:
        if self.exhausted:
            return
        try:
            self.session.declare_route_stop(route, reason)
        except BudgetExhausted:  # pragma: no cover - declare_route_stop is unmetered
            self.exhausted = True

    # -- shared policy ----------------------------------------------------

    def probe_plan(self, routes: Iterable[str]) -> tuple[tuple[str, str], ...]:
        """Order (route, probe) pairs by lexical affinity to the question.

        Zero-affinity probes are kept and issued after the rest rather than
        dropped. A baseline that refused to look down a route whose published
        vocabulary shares no term with the question would be declining to spend a
        budget it has, and its coverage would be a property of that refusal rather
        than of the method. Ties are broken by a seeded shuffle, so the three
        stochastic repeats differ where the method genuinely does not care.
        """

        allowed = set(routes)
        pairs = [
            (route, probe)
            for route, probes in self.view.route_probes
            for probe in probes
            if route in allowed
        ]
        if not pairs:
            return ()
        scorer = Bm25Scorer([(f"{route}{probe}", probe) for route, probe in pairs])
        scored = [
            (scorer.score(f"{route}{probe}", self.query_terms), route, probe)
            for route, probe in pairs
        ]
        buckets: dict[float, list[tuple[str, str]]] = {}
        for score, route, probe in scored:
            buckets.setdefault(score, []).append((route, probe))
        plan: list[tuple[str, str]] = []
        for score in sorted(buckets, reverse=True):
            group = sorted(buckets[score])
            self.rng.shuffle(group)
            plan.extend(group)
        return tuple(plan)

    def unread_records(self) -> tuple[RetrievedRecord, ...]:
        """Retrieved records this baseline has not read, in a stable order.

        Deduplication is by locator only. Work-level content identity is the
        mechanism P2 is testing, and a baseline that deduplicated by it would be
        borrowing the system under test's machinery; a conventional retrieval
        pipeline deduplicates by document id and no further.
        """

        return tuple(
            self.records[doc_id]
            for doc_id in sorted(self.records)
            if doc_id not in self.read_doc_ids
        )

    def record_text(self, record: RetrievedRecord) -> str:
        return f"{record.title}\n\n{record.abstract}"

    def may_close(self) -> bool:
        """Closure is refused while an obligation is open or a cap was hit.

        Both halves are required by the frozen plan: an unresolved unavailability
        obligation is what B11 drives `unjustified_closure_rate` from, and a run
        truncated at a cap "did not declare closure" under the cap-hit rule.
        """

        return not self.open_obligations and not self.exhausted

    def finish(self, claims: Iterable[str], *, closed: bool, notes: str) -> SystemReport:
        """Assemble the report. Claims are always retained, closure never assumed.

        A claim about material the baseline never retrieved is discarded here
        rather than left for the evaluator to reject: `gold.evaluate` treats
        unsupported claims as a scoring error, and emitting one would be claiming
        a discovery that did not happen.
        """

        supported = {item for item in claims if item in self.seen_identities}
        self.trace.open_obligation_ids_at_closure = tuple(sorted(self.open_obligations))
        self.trace.truncated_at_cap = self.exhausted
        return SystemReport(
            claimed_relevant_merged_source_ids=tuple(sorted(supported)),
            task_closed_as_complete=bool(closed and self.may_close()),
            abstained=not supported,
            notes=notes,
        )


class _Baseline:
    """Shared plumbing: identity, and per-(task, seed) binding custody."""

    system_id = "unset"

    def __init__(self) -> None:
        self._bindings: dict[tuple[str, int], BindingTrace] = {}

    def bindings_for(self, task_id: str, seed: int) -> BindingTrace | None:
        """The system-side required bindings for one run, or `None` if never run."""

        return self._bindings.get((task_id, seed))

    def _begin(self, view: PublicView, session: DiscoverySession, *, seed: int) -> _Run:
        run = _Run(view, session, seed=seed)
        run.trace.system_id = self.system_id
        self._bindings[(view.task_id, seed)] = run.trace
        return run

    def _rank_by_bm25(self, run: _Run, records: Sequence[RetrievedRecord]) -> list[RetrievedRecord]:
        if not records:
            return []
        scorer = Bm25Scorer([(item.doc_id, run.record_text(item)) for item in records])
        scored = [(scorer.score(item.doc_id, run.query_terms), item.doc_id, item) for item in records]
        scored.sort(key=lambda entry: (-entry[0], entry[1]))
        return [item for _, _, item in scored]


# ---------------------------------------------------------------------------
# 1. bm25_keyword — the promotion gate
# ---------------------------------------------------------------------------


class Bm25KeywordBaseline(_Baseline):
    """Okapi BM25 over probes and over retrieved records.

    `STATISTICAL_PLAN_V1.baselines` gives this baseline the role
    `promotion_gate` (`sage_lexical_gate`): a discovery claim that does not beat
    it is withdrawn. It is therefore built to be a competent lexical system, not
    a foil. Concretely it (a) ranks every published probe on every available route
    by BM25 against the derived query and spends its route budget in that order,
    keeping zero-affinity probes rather than refusing them; (b) ranks every
    retrieved record by BM25 and spends its read budget in that order, so the
    best candidates are screened first and a truncated run is truncated at the
    tail; and (c) claims the top `BM25_SCREEN_DEPTH` records it screened.

    It has no route-independence notion, no work-level identity notion and no
    separation between abandoning a route and closing a task. Those are the
    mechanisms under test, and a baseline holding them would not be a baseline.
    """

    system_id = "bm25_keyword"

    def run(self, view: PublicView, session: DiscoverySession, *, seed: int) -> SystemReport:
        run = self._begin(view, session, seed=seed)

        for route, probe in run.probe_plan(view.available_routes):
            if run.exhausted:
                break
            run.query(route, probe)

        claims: list[str] = []
        for record in self._rank_by_bm25(run, run.unread_records()):
            if run.exhausted or len(claims) >= BM25_SCREEN_DEPTH:
                run.encounter(record, execute=False)
                continue
            if run.encounter(record, execute=True) is None:
                continue
            claims.append(record.content_identity)

        return run.finish(
            claims,
            # A lexical system that has spent its probe list has no further move,
            # and reports so. Whether that is premature is exactly what the
            # premature-closure metric is for; refusing to close would be this
            # baseline borrowing the fail-closed behaviour under test.
            closed=True,
            notes="bm25 probe ranking, bm25 screening, no route governance",
        )


# ---------------------------------------------------------------------------
# 2. dense_retrieval — lexical-distributional, NOT neural
# ---------------------------------------------------------------------------


class DenseRetrievalBaseline(_Baseline):
    """Hashed distributional vectors with cosine scoring. **Not a neural system.**

    Identical control flow to `bm25_keyword`; only the scorer differs. It
    substitutes hashed whole-token-plus-character-trigram cosine for BM25, which
    buys tolerance to morphological variation and nothing else. In particular it
    does not bridge the paraphrase gap this world is built around, and no
    conclusion about neural dense retrieval follows from its results. See the
    module docstring.
    """

    system_id = "dense_retrieval"

    def _rank(self, run: _Run, records: Sequence[RetrievedRecord]) -> list[RetrievedRecord]:
        if not records:
            return []
        scorer = HashedDistributionalScorer(
            [(item.doc_id, run.record_text(item)) for item in records]
        )
        query_vector = scorer.vectorize(" ".join(run.query_terms))
        scored = [(scorer.score(item.doc_id, query_vector), item.doc_id, item) for item in records]
        scored.sort(key=lambda entry: (-entry[0], entry[1]))
        return [item for _, _, item in scored]

    def _probe_plan(self, run: _Run, routes: Sequence[str]) -> tuple[tuple[str, str], ...]:
        allowed = set(routes)
        pairs = [
            (route, probe)
            for route, probes in run.view.route_probes
            for probe in probes
            if route in allowed
        ]
        if not pairs:
            return ()
        scorer = HashedDistributionalScorer(
            [(f"{route}{probe}", probe) for route, probe in pairs]
        )
        query_vector = scorer.vectorize(" ".join(run.query_terms))
        buckets: dict[float, list[tuple[str, str]]] = {}
        for route, probe in pairs:
            score = scorer.score(f"{route}{probe}", query_vector)
            buckets.setdefault(score, []).append((route, probe))
        plan: list[tuple[str, str]] = []
        for score in sorted(buckets, reverse=True):
            group = sorted(buckets[score])
            run.rng.shuffle(group)
            plan.extend(group)
        return tuple(plan)

    def run(self, view: PublicView, session: DiscoverySession, *, seed: int) -> SystemReport:
        run = self._begin(view, session, seed=seed)

        for route, probe in self._probe_plan(run, view.available_routes):
            if run.exhausted:
                break
            run.query(route, probe)

        claims: list[str] = []
        for record in self._rank(run, run.unread_records()):
            if run.exhausted or len(claims) >= BM25_SCREEN_DEPTH:
                run.encounter(record, execute=False)
                continue
            if run.encounter(record, execute=True) is None:
                continue
            claims.append(record.content_identity)

        return run.finish(
            claims,
            closed=True,
            notes="hashed lexical-distributional cosine; not a neural retriever",
        )


# ---------------------------------------------------------------------------
# 3. sparse_dense_hybrid — reciprocal rank fusion of 1 and 2
# ---------------------------------------------------------------------------


class SparseDenseHybridBaseline(_Baseline):
    """Reciprocal-rank fusion of the BM25 and distributional rankings.

    Rank fusion rather than score fusion, and equal weight per constituent. The
    two scorers are on incomparable scales, so normalising them to combine scores
    would require a normalisation choice and a weight; RRF requires neither. `k`
    is `RRF_K`, the value the paper that introduced RRF uses. Nothing here is
    fitted: an unequal weight is precisely the free parameter that could only have
    been set by looking at results.
    """

    system_id = "sparse_dense_hybrid"

    def _fuse(
        self, run: _Run, keyed: Sequence[tuple[str, str]]
    ) -> list[tuple[float, str]]:
        """Fuse BM25 and distributional rankings over `(key, text)` pairs."""

        if not keyed:
            return []
        lexical = Bm25Scorer(keyed)
        distributional = HashedDistributionalScorer(keyed)
        query_vector = distributional.vectorize(" ".join(run.query_terms))

        lexical_rank = sorted(
            keyed, key=lambda entry: (-lexical.score(entry[0], run.query_terms), entry[0])
        )
        dense_rank = sorted(
            keyed, key=lambda entry: (-distributional.score(entry[0], query_vector), entry[0])
        )
        fused = reciprocal_rank_fusion(
            [[key for key, _ in lexical_rank], [key for key, _ in dense_rank]]
        )
        return sorted(((fused.get(key, 0.0), key) for key, _ in keyed), key=lambda e: (-e[0], e[1]))

    def run(self, view: PublicView, session: DiscoverySession, *, seed: int) -> SystemReport:
        run = self._begin(view, session, seed=seed)

        allowed = set(view.available_routes)
        pairs = [
            (route, probe)
            for route, probes in view.route_probes
            for probe in probes
            if route in allowed
        ]
        keyed = [(f"{route}{probe}", probe) for route, probe in pairs]
        for _, key in self._fuse(run, keyed):
            if run.exhausted:
                break
            route, probe = key.split("", 1)
            run.query(route, probe)

        records = {item.doc_id: item for item in run.unread_records()}
        ranked = self._fuse(run, [(doc_id, run.record_text(item)) for doc_id, item in records.items()])
        claims: list[str] = []
        for _, doc_id in ranked:
            record = records[doc_id]
            if run.exhausted or len(claims) >= BM25_SCREEN_DEPTH:
                run.encounter(record, execute=False)
                continue
            if run.encounter(record, execute=True) is None:
                continue
            claims.append(record.content_identity)

        return run.finish(
            claims,
            closed=True,
            notes=f"reciprocal rank fusion, k={RRF_K}, equal weight",
        )


# ---------------------------------------------------------------------------
# 4. one_pass_rag — retrieve once, screen exactly that set
# ---------------------------------------------------------------------------


class OnePassRagBaseline(_Baseline):
    """One retrieval pass, fixed k, then screening of exactly that set.

    The absence of iteration is the baseline, not a shortcoming of it: whatever
    the single pass missed stays missed, and no observation made during screening
    feeds back into retrieval. It issues `ONE_PASS_CALLS_PER_ROUTE` call on each
    available route — its best probe for that route — takes the top
    `ONE_PASS_RETRIEVAL_DEPTH` records by BM25, and screens those and no others.
    """

    system_id = "one_pass_rag"

    def run(self, view: PublicView, session: DiscoverySession, *, seed: int) -> SystemReport:
        run = self._begin(view, session, seed=seed)

        issued: dict[str, int] = {}
        for route, probe in run.probe_plan(view.available_routes):
            if run.exhausted:
                break
            if issued.get(route, 0) >= ONE_PASS_CALLS_PER_ROUTE:
                continue
            issued[route] = issued.get(route, 0) + 1
            run.query(route, probe)

        ranked = self._rank_by_bm25(run, run.unread_records())
        context = ranked[:ONE_PASS_RETRIEVAL_DEPTH]
        # Everything outside the fixed context window is an encounter this
        # baseline declines by construction. Recording those declines is what
        # makes the one-pass ceiling visible rather than merely asserted.
        for record in ranked[ONE_PASS_RETRIEVAL_DEPTH:]:
            run.encounter(record, execute=False)

        claims: list[str] = []
        for record in context:
            if run.exhausted:
                run.encounter(record, execute=False)
                continue
            if run.encounter(record, execute=True) is None:
                continue
            claims.append(record.content_identity)

        return run.finish(
            claims,
            closed=True,
            notes=f"single pass, k={ONE_PASS_RETRIEVAL_DEPTH}, no iteration",
        )


# ---------------------------------------------------------------------------
# 5. agentic_single_route — iterative reformulation on one route
# ---------------------------------------------------------------------------


class AgenticSingleRouteBaseline(_Baseline):
    """Iterative query reformulation on one route, under a frozen policy.

    Route choice is the highest-affinity available route by BM25, and never
    changes: no cross-route logic, no dedup across routes, no switching. Each
    attempt is folded into a `RouteControlState` and `decide_route` is consulted
    under `AGENTIC_ROUTE_POLICY`; the loop continues while the decision is
    CONTINUE or REFORMULATE and stops on STOP or SUSPEND. `alternative_route_kinds`
    is empty because there is, for this baseline, no alternative — which is what
    makes SWITCH unreachable and the single-route ceiling real.

    This baseline has no route-stop/task-stop separation: when its one route is
    done it reports the task done. That conflation is the baseline's defining
    property and the thing P2.H3 contrasts against; it is stated here so it is not
    mistaken for a defect in this implementation. It is still not permitted to
    close over an open transport obligation — silence from a dead provider is not
    evidence of absence for any system, baseline or otherwise.
    """

    system_id = "agentic_single_route"

    def _select_route(self, run: _Run, view: PublicView) -> str | None:
        plan = run.probe_plan(view.available_routes)
        return plan[0][0] if plan else None

    def run(self, view: PublicView, session: DiscoverySession, *, seed: int) -> SystemReport:
        run = self._begin(view, session, seed=seed)

        route = self._select_route(run, view)
        if route is None:
            return run.finish((), closed=False, notes="no available route carried a probe")

        spec = ROUTE_SPEC_BY_ROUTE.get(DiscoveryRoute(route))
        route_kind = SearchRouteKind(spec.orion_route_kind) if spec else SearchRouteKind.CURRENT_VOCABULARY
        probes = [probe for candidate, probe in run.probe_plan((route,)) if candidate == route]

        attempts: list[RouteAttempt] = []
        budget_units = float(view.budget.max_route_calls)
        stop_reason = "probe_vocabulary_exhausted"

        for index, probe in enumerate(probes):
            state = RouteControlState(
                route_id=route,
                route_kind=route_kind,
                attempts=tuple(attempts),
                budget_units=budget_units,
                alternative_route_kinds=(),
            )
            decision = decide_route(state, AGENTIC_ROUTE_POLICY)
            if decision.action in (RouteControlAction.STOP, RouteControlAction.SUSPEND):
                stop_reason = ",".join(decision.reasons)
                break
            outcome = run.query(route, probe)
            if outcome is None:
                stop_reason = "budget_exhausted"
                break
            identities = tuple(sorted({item.content_identity for item in outcome.records}))
            previously = set(identities) & {
                key for attempt in attempts for key in attempt.retrieved_digests
            }
            attempts.append(
                RouteAttempt(
                    attempt_id=f"{route}:{index}",
                    query_id=f"probe:{index}",
                    retrieved_digests=identities,
                    novel_digests=tuple(sorted(set(identities) - previously)),
                    cost_units=1.0,
                    execution_failure_signatures=(
                        () if outcome.status is TransportStatus.OK else (outcome.status.value,)
                    ),
                )
            )
        else:
            # The probe vocabulary ran out before the policy said stop. Consult the
            # policy once more so the recorded reason is the policy's, not a guess.
            final = decide_route(
                RouteControlState(
                    route_id=route,
                    route_kind=route_kind,
                    attempts=tuple(attempts),
                    budget_units=budget_units,
                    alternative_route_kinds=(),
                ),
                AGENTIC_ROUTE_POLICY,
            )
            stop_reason = ",".join(final.reasons) or stop_reason

        run.declare_route_stop(route, stop_reason)

        claims: list[str] = []
        for record in self._rank_by_bm25(run, run.unread_records()):
            if run.exhausted or len(claims) >= BM25_SCREEN_DEPTH:
                run.encounter(record, execute=False)
                continue
            if run.encounter(record, execute=True) is None:
                continue
            claims.append(record.content_identity)

        return run.finish(
            claims,
            closed=True,
            notes=f"single route {route}; route stop reason {stop_reason}",
        )


# ---------------------------------------------------------------------------
# 6. protocol_driven_systematic_review
# ---------------------------------------------------------------------------


class ProtocolDrivenSystematicReviewBaseline(_Baseline):
    """A predeclared search protocol, fixed eligibility criteria, an SR stopping rule.

    This imitates the *shape* of protocol-driven systematic review practice as
    codified in PRISMA-S (search reporting) and in the consecutive-irrelevant
    stopping heuristics used in screening prioritisation. It does **not**
    reproduce AgentSLR: `EXTERNAL_ACCESS_AUDIT_V1.json` records that AgentSLR's
    code carries no licence, so it was neither read nor ported, and no claim of
    equivalence to it is made here or in the manuscript.

    Three properties make it the SR baseline rather than another retrieval one:

    - the search is **predeclared**: the probe list is fixed from the question
      before the first call and never revised in light of what comes back, which
      is what makes a systematic search reproducible;
    - eligibility is a **fixed criterion** applied uniformly — a record is
      eligible iff its text carries every derived query term — rather than a rank
      cut, because SR eligibility is a stated rule, not a ranking; and
    - stopping is by the **consecutive non-eligible** rule, not by exhaustion of a
      ranked list.

    Its precision on this world is expected to be poor: the eligibility criterion
    is conjunctive over query terms, and this corpus writes the topic label into
    every neighbourhood record, so distractors satisfy it. That is a faithful
    consequence of a broad, recall-oriented criterion, and it is not compensated
    for.
    """

    system_id = "protocol_driven_systematic_review"

    def _eligible(self, run: _Run, text: str) -> bool:
        tokens = set(tokenize(text))
        return bool(run.query_terms) and all(term in tokens for term in run.query_terms)

    def run(self, view: PublicView, session: DiscoverySession, *, seed: int) -> SystemReport:
        run = self._begin(view, session, seed=seed)

        # Predeclared search: fixed before the first call, executed in order,
        # never revised in light of results.
        protocol = run.probe_plan(view.available_routes)
        for route, probe in protocol:
            if run.exhausted:
                break
            run.query(route, probe)

        claims: list[str] = []
        consecutive_non_eligible = 0
        stopped = False
        for record in self._rank_by_bm25(run, run.unread_records()):
            if stopped or run.exhausted:
                run.encounter(record, execute=False)
                continue
            outcome = run.encounter(record, execute=True)
            if outcome is None:
                continue
            if self._eligible(run, outcome.text):
                claims.append(record.content_identity)
                consecutive_non_eligible = 0
                continue
            consecutive_non_eligible += 1
            if consecutive_non_eligible >= SR_STOP_AFTER_CONSECUTIVE_NON_ELIGIBLE:
                stopped = True

        return run.finish(
            claims,
            closed=True,
            notes=(
                "predeclared protocol; conjunctive eligibility; stopped after "
                f"{SR_STOP_AFTER_CONSECUTIVE_NON_ELIGIBLE} consecutive non-eligible screens"
            ),
        )


#: Construction order matches `PROTOCOL_V1.json:baselines`. `protocol_driven_
#: systematic_review` is spelled as the protocol spells it; the shorter
#: `protocol_driven_review` appears nowhere frozen and would not join to the
#: statistical plan's baseline roles.
def build_baselines() -> tuple[Any, ...]:
    """One fresh instance of each protocol baseline, in protocol order."""

    return (
        Bm25KeywordBaseline(),
        DenseRetrievalBaseline(),
        SparseDenseHybridBaseline(),
        OnePassRagBaseline(),
        AgenticSingleRouteBaseline(),
        ProtocolDrivenSystematicReviewBaseline(),
    )


BASELINE_SYSTEM_IDS: tuple[str, ...] = (
    "bm25_keyword",
    "dense_retrieval",
    "sparse_dense_hybrid",
    "one_pass_rag",
    "agentic_single_route",
    "protocol_driven_systematic_review",
)


__all__ = [
    "AGENTIC_ROUTE_POLICY",
    "BASELINE_SYSTEM_IDS",
    "BM25_B",
    "BM25_K1",
    "BM25_SCREEN_DEPTH",
    "AgenticSingleRouteBaseline",
    "BindingTrace",
    "Bm25KeywordBaseline",
    "Bm25Scorer",
    "CHAR_NGRAM_ORDER",
    "CHAR_NGRAM_WEIGHT",
    "DenseRetrievalBaseline",
    "HASH_DIMENSIONS",
    "HashedDistributionalScorer",
    "MODEL_TOKENS_PER_CALL",
    "ONE_PASS_CALLS_PER_ROUTE",
    "ONE_PASS_RETRIEVAL_DEPTH",
    "OnePassRagBaseline",
    "ProtocolDrivenSystematicReviewBaseline",
    "RRF_K",
    "ReadEncounterBinding",
    "RouteTrialBinding",
    "SR_STOP_AFTER_CONSECUTIVE_NON_ELIGIBLE",
    "SparseDenseHybridBaseline",
    "TOOL_CALLS_PER_SESSION_CALL",
    "build_baselines",
    "derive_query_terms",
    "reciprocal_rank_fusion",
    "tokenize",
]
