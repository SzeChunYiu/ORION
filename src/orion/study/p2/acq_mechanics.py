"""Candidate-generation mechanics for the open-world acquisition successor study.

Six arms over one synthetic provider, defined by
`papers/orion-12-open-world-scientific-discovery/protocol/P2_OPEN_WORLD_ACQUISITION_FREEZE_2026-08-22.md`.

Why another mechanics module when `echo_mechanics` exists
--------------------------------------------------------

`echo_mechanics` measured *one needle* by `hit@10` over a whole-corpus ranking
with no provider, no call budget and no candidate cap. The V2 Wide campaign that
returned `DEV3R_FINAL_NON_ELIGIBLE` measured something structurally different:
mean recall over a **multi-document** gold set, produced by **three** provider
calls of **twenty** results each, merged into a **twenty**-candidate output. Its
archived numbers say the arms were not returning empty result sets —
``mean_candidates_returned = 20.0`` for both — they were returning twenty wrong
papers on 19 of 24 tasks. A mechanic validated on `hit@10` over an unbounded
ranking has not been shown to survive that, so this module re-poses the question
under the live budgets.

The arms
--------

* **B0** `ARCHIVED_WIDE_LEXICAL_V3` — the archived corrected lexical baseline
  reimplemented against a synthetic provider: `BASE_PRIMARY` (an OR over four
  adjacent-pair ANDs), `BASE_CORE` (a two-term AND) and `BASE_BROAD` (an OR over
  six tokens), merged round-robin and capped at twenty. This is the system that
  scored `mean recall 0.051422`, and reproducing *it* rather than a caricature is
  what makes gate G1 a reproduction.
* **B1** `SHIPPED_D1_D2_D3` — the three shipped derivations in
  `arb_runtime`, unedited: `D1_CURRENT_VOCABULARY` as a conjunction,
  `D2_LEXICAL_VARIANT` as free text, `D3_CITATION_NEIGHBORHOOD` from the
  best-ranked held record. Round-robin merge, cap twenty.
* **S2** `D5_GROUNDED_SPECIFICITY_LADDER` — the candidate. Ground every term in
  the index, gate out apparatus vocabulary, choose the conjunction width the
  arithmetic says is satisfiable, descend a three-rung specificity ladder within
  the same three-call budget, and merge coverage-first instead of round-robin.
* **A1** `D5_QUERIES_ROUND_ROBIN` — S2's queries, the archived merge. Isolates
  the *selection* half of the repair.
* **A2** `D1_TERMS_COVERAGE_MERGE` — D1's ungated terms, S2's merge. Isolates the
  *query* half.
* **A3** `D5_NO_EXPANSION` — S2 with the expansion rung replaced by a plain
  disjunction. Isolates the vocabulary-bridging half.

Everything is deterministic. No arm receives the task, the topic, the gold set or
the family label; the only corpus knowledge any arm uses is document frequency,
which is an index statistic and not an answer.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .arb_runtime import (
    _content_tokens,
    derive_citation_seed_query,
    derive_current_vocabulary_query,
    derive_lexical_variant_query,
)
from .baselines import Bm25Scorer
from .corpus import Document

# --------------------------------------------------------------------------
# Frozen mechanic constants. Hashed with the world parameters before any run.
# --------------------------------------------------------------------------

#: Matched budgets, taken from the archived Dev-3R execution so the offline
#: comparison is calibrated to the campaign it is trying to repair rather than to
#: a budget of this study's choosing.
PROVIDER_CALLS_PER_TASK = 3
RESULTS_PER_CALL = 20
CANDIDATE_CAP = 20

#: Query width, identical to `D1`'s. The candidate gets no term-budget gift.
QUERY_WIDTH = 6

#: Document-frequency ceiling above which a question token is apparatus rather
#: than content. Inherited verbatim from the validated `D4` mechanic in
#: `echo_mechanics.INCIDENTAL_DF_FRACTION`; it is not retuned here, because
#: retuning an inherited constant against a new world is the post-outcome
#: optimisation this programme's stop rules exist to forbid.
SCAFFOLD_DF_FRACTION = 0.05

#: Term-frequency saturation, also inherited from `echo_mechanics`.
TF_SATURATION = 1.2

#: The conjunction-width rule. A conjunction over terms ``T`` is expected, under a
#: term-independence assumption, to match ``N * prod(df(t)/N)`` documents. The
#: ladder's first rung uses the *widest* prefix whose expectation is at least this
#: many documents, so a query that arithmetic says will come back thin is never
#: issued in the first place. Five rather than one because the outcome here is
#: recall over a multi-document gold set: a conjunction expected to match a single
#: document cannot supply recall even when it is satisfiable.
MIN_EXPECTED_CONJUNCTION_HITS = 5.0
MIN_CONJUNCTION_WIDTH = 2
MAX_CONJUNCTION_WIDTH = 4

#: Grounded-expansion parameters. Feedback documents come from the ladder's first
#: two rungs; expansion terms are scored by a relevance-model weight and are
#: themselves subject to the apparatus gate.
FEEDBACK_DOCUMENTS = 8
EXPANSION_TERMS = 4
EXPANSION_WEIGHT = 0.4

#: Coverage admission for the merge. A candidate agreeing with the gated query on
#: fewer than this many distinct terms is ordered strictly below every candidate
#: that agrees on at least this many — demoted, never deleted, so the rule cannot
#: manufacture recall by hiding documents.
MIN_COVERAGE = 2

ARM_B0 = "B0_ARCHIVED_WIDE_LEXICAL_V3"
ARM_B1 = "B1_SHIPPED_D1_D2_D3"
ARM_S2 = "S2_D5_GROUNDED_SPECIFICITY_LADDER"
ARM_A1 = "A1_D5_QUERIES_ROUND_ROBIN"
ARM_A2 = "A2_D1_TERMS_COVERAGE_MERGE"
ARM_A3 = "A3_D5_NO_EXPANSION"

ARM_ORDER: tuple[str, ...] = (ARM_B0, ARM_B1, ARM_S2, ARM_A1, ARM_A2, ARM_A3)

MECHANIC_PARAMETERS: dict[str, Any] = {
    "provider_calls_per_task": PROVIDER_CALLS_PER_TASK,
    "results_per_call": RESULTS_PER_CALL,
    "candidate_cap": CANDIDATE_CAP,
    "query_width": QUERY_WIDTH,
    "scaffold_df_fraction": SCAFFOLD_DF_FRACTION,
    "tf_saturation": TF_SATURATION,
    "min_expected_conjunction_hits": MIN_EXPECTED_CONJUNCTION_HITS,
    "min_conjunction_width": MIN_CONJUNCTION_WIDTH,
    "max_conjunction_width": MAX_CONJUNCTION_WIDTH,
    "feedback_documents": FEEDBACK_DOCUMENTS,
    "expansion_terms": EXPANSION_TERMS,
    "expansion_weight": EXPANSION_WEIGHT,
    "min_coverage": MIN_COVERAGE,
    "arms": list(ARM_ORDER),
    "inherited_constants": {
        "scaffold_df_fraction": "echo_mechanics.INCIDENTAL_DF_FRACTION",
        "tf_saturation": "echo_mechanics.TF_SATURATION",
    },
}


# --------------------------------------------------------------------------
# Provider
# --------------------------------------------------------------------------


class QueryKind(str, Enum):
    """The three query shapes the archived arXiv scripts actually emitted."""

    #: ``all:a AND all:b AND ...`` — every term required.
    CONJUNCTION = "CONJUNCTION"
    #: ``all:a OR all:b OR ...`` — any term suffices.
    DISJUNCTION = "DISJUNCTION"
    #: ``(all:a AND all:b) OR (all:b AND all:c) OR ...`` — any listed pair.
    PAIR_DISJUNCTION = "PAIR_DISJUNCTION"
    #: Follow a held record's reference list. Not a text query at all.
    CITATION = "CITATION"


@dataclass(frozen=True)
class Query:
    """One provider call, with the derivation that produced it retained."""

    rule_id: str
    kind: QueryKind
    terms: tuple[str, ...] = ()
    pairs: tuple[tuple[str, str], ...] = ()
    seed_doc_id: str = ""

    def rendered(self) -> str:
        """The query as the provider grammar would carry it. For the record only."""

        if self.kind is QueryKind.CONJUNCTION:
            return " AND ".join(f"all:{term}" for term in self.terms)
        if self.kind is QueryKind.DISJUNCTION:
            return " OR ".join(f"all:{term}" for term in self.terms)
        if self.kind is QueryKind.PAIR_DISJUNCTION:
            return " OR ".join(f"(all:{a} AND all:{b})" for a, b in self.pairs)
        return f"references:{self.seed_doc_id}"


@dataclass(frozen=True)
class AcquisitionIndex:
    """Term statistics plus the retrieval the provider performs.

    Both halves live here rather than in any arm, so no arm can win by using a
    different analyzer, a different BM25 or a different result cap. Tokenisation
    is `arb_runtime._content_tokens`, which is the tokenizer the shipped
    derivations already use.
    """

    doc_ids: tuple[str, ...]
    postings: dict[str, dict[str, int]]
    references: dict[str, tuple[str, ...]]
    scorer: Bm25Scorer
    size: int
    _bm25_cache: dict[str, dict[str, float]] = field(default_factory=dict, repr=False)
    #: Memo for the forward view (a document's distinct terms), used only by
    #: relevance-model expansion. Reconstructed from the inverted index rather
    #: than read off the ``Document``, so an arm never touches a field the
    #: package boundary rule keeps away from systems under test.
    _forward_cache: dict[str, tuple[str, ...]] = field(default_factory=dict, repr=False)

    def document_frequency(self, term: str) -> int:
        return len(self.postings.get(term, ()))

    def df_fraction(self, term: str) -> float:
        return self.document_frequency(term) / max(1, self.size)

    def idf(self, term: str) -> float:
        return self.scorer.inverse_document_frequency(term)

    def bm25_contribution(self, term: str, doc_id: str) -> float:
        cached = self._bm25_cache.get(term)
        if cached is None:
            cached = {
                key: self.scorer.score(key, (term,))
                for key in self.postings.get(term, {})
            }
            self._bm25_cache[term] = cached
        return cached.get(doc_id, 0.0)

    # -- retrieval ---------------------------------------------------------

    def _bm25_rank(self, matches: Sequence[str], terms: Sequence[str]) -> tuple[str, ...]:
        scores = {
            doc_id: sum(self.bm25_contribution(term, doc_id) for term in dict.fromkeys(terms))
            for doc_id in matches
        }
        return tuple(sorted(matches, key=lambda d: (-scores[d], d)))

    def search(self, query: Query, *, max_results: int = RESULTS_PER_CALL) -> tuple[str, ...]:
        """Execute one provider call. Relevance-ranked, truncated at `max_results`.

        Truncation is the point: the live provider returned twenty of however many
        matched, and the archived diagnostic shows gold identifiers that were
        retrieved raw and then lost. A harness that returned every match would
        measure a retrieval problem nobody has.
        """

        if query.kind is QueryKind.CITATION:
            reachable = self.references.get(query.seed_doc_id, ())
            return tuple(sorted(reachable))[:max_results]

        if query.kind is QueryKind.CONJUNCTION:
            terms = [term for term in dict.fromkeys(query.terms)]
            if not terms:
                return ()
            matched: set[str] | None = None
            for term in terms:
                postings = set(self.postings.get(term, ()))
                matched = postings if matched is None else (matched & postings)
                if not matched:
                    return ()
            return self._bm25_rank(sorted(matched or ()), terms)[:max_results]

        if query.kind is QueryKind.PAIR_DISJUNCTION:
            matched = set()
            terms = []
            for left, right in query.pairs:
                matched |= set(self.postings.get(left, ())) & set(self.postings.get(right, ()))
                terms.extend((left, right))
            if not matched:
                return ()
            return self._bm25_rank(sorted(matched), list(dict.fromkeys(terms)))[:max_results]

        matched = set()
        for term in dict.fromkeys(query.terms):
            matched |= set(self.postings.get(term, ()))
        if not matched:
            return ()
        return self._bm25_rank(sorted(matched), query.terms)[:max_results]


def build_index(documents: Sequence[Document]) -> AcquisitionIndex:
    texts = [(item.doc_id, f"{item.title} {item.abstract}") for item in documents]
    postings: dict[str, dict[str, int]] = {}
    for doc_id, text in texts:
        for token in _content_tokens(text):
            postings.setdefault(token, {})
            counts = postings[token]
            counts[doc_id] = counts.get(doc_id, 0) + 1
    return AcquisitionIndex(
        doc_ids=tuple(doc_id for doc_id, _ in texts),
        postings=postings,
        references={item.doc_id: tuple(item.references) for item in documents},
        scorer=Bm25Scorer(texts),
        size=len(texts),
    )


# --------------------------------------------------------------------------
# Term selection
# --------------------------------------------------------------------------


def d1_terms(question: str, limit: int = QUERY_WIDTH) -> tuple[str, ...]:
    """The shipped `D1_CURRENT_VOCABULARY` selection, unedited."""

    return derive_current_vocabulary_query(question, limit=limit).source_terms


def d2_terms(question: str) -> tuple[str, ...]:
    """The shipped `D2_LEXICAL_VARIANT` selection, unedited."""

    return derive_lexical_variant_query(question).source_terms


def d5_terms(question: str, index: AcquisitionIndex) -> tuple[str, ...]:
    """`D5` term selection: ground first, then gate, then rank by discriminativeness.

    Three departures from `D1`, in the order they matter.

    *Grounding.* A token the index has never seen contributes nothing to a
    disjunction and empties any conjunction it enters. `D1` never asks, so a
    question word that happens to be absent from the collection can silently void
    a whole query. Dropping ``df == 0`` terms costs nothing and is the cheapest
    line in the mechanic.

    *Gating.* A token in more than `SCAFFOLD_DF_FRACTION` of the collection cannot
    by itself identify a topic; it is apparatus. This is `D4`'s finding, inherited
    at `D4`'s threshold rather than re-fitted here.

    *Ranking by idf rather than by within-question repetition.* `D1` ranks by how
    often the asker repeated a word, which in a natural research question rewards
    framing vocabulary. Ranking the survivors by idf lets a content term used once
    outrank an apparatus term used twice.
    """

    counts: dict[str, int] = {}
    order: dict[str, int] = {}
    for position, token in enumerate(_content_tokens(question)):
        counts[token] = counts.get(token, 0) + 1
        order.setdefault(token, position)

    grounded = [token for token in counts if index.document_frequency(token) > 0]
    retained = [
        token for token in grounded if index.df_fraction(token) <= SCAFFOLD_DF_FRACTION
    ]
    if not retained:
        # The gate emptied the query. `P2_LEXICAL_ECHO_SUCCESSOR_RESULT_2026-08-21`
        # §4 named this as `D4`'s untested exposure: a question whose entire content
        # vocabulary is common leaves the gate with nothing to keep. Falling back to
        # the grounded set ranked by idf is strictly better than issuing no query,
        # and it degrades to the baseline's own vocabulary rather than to silence.
        retained = list(grounded)
    if not retained:
        # Nothing in the question is in the collection at all. There is no
        # groundable query; emit the question's own terms so the arm still spends
        # its matched budget rather than silently returning an empty candidate set.
        retained = list(counts)
    retained.sort(key=lambda token: (-index.idf(token), order[token]))
    return tuple(retained[:QUERY_WIDTH])


def satisfiable_conjunction_width(terms: Sequence[str], index: AcquisitionIndex) -> int:
    """Widest prefix of `terms` whose expected conjunctive yield clears the floor.

    Under a term-independence assumption the conjunction over a prefix of length
    ``k`` matches ``N * prod(df(t)/N)`` documents in expectation. Independence is
    wrong — topical terms co-occur, so the true yield is higher — which makes the
    estimate *conservative* in the direction that matters: it under-predicts, so a
    width it accepts is one the collection can almost always satisfy.

    Returning a width rather than observing an empty result is deliberate. A
    system that discovers over-constraint by issuing the query and getting nothing
    has already spent one of three calls to learn a fact the index statistics
    could have told it for free.
    """

    usable = [term for term in terms if index.document_frequency(term) > 0]
    if len(usable) < MIN_CONJUNCTION_WIDTH:
        return 0
    best = MIN_CONJUNCTION_WIDTH
    expectation = float(index.size)
    for position, term in enumerate(usable[:MAX_CONJUNCTION_WIDTH], start=1):
        expectation *= index.df_fraction(term)
        if position < MIN_CONJUNCTION_WIDTH:
            continue
        if expectation >= MIN_EXPECTED_CONJUNCTION_HITS:
            best = position
        else:
            break
    return min(best, len(usable))


def expansion_terms(
    feedback: Sequence[str], base_terms: Sequence[str], index: AcquisitionIndex
) -> tuple[str, ...]:
    """Relevance-model expansion terms drawn from what the ladder already retrieved.

    ``w(t) = (fraction of feedback documents carrying t) * idf(t)``, restricted to
    terms that pass the same apparatus gate the query terms passed and that are not
    already in the query. This is the only part of `D5` that can reach a document
    sharing no token with the question, and it can only do so when the collection
    itself contains a record using both vocabularies. Where no such bridge exists
    the expansion is inert by construction, which is what gate G5 checks rather
    than assumes.
    """

    if not feedback:
        return ()
    held = set(base_terms)
    hits: dict[str, int] = {}
    for doc_id in feedback:
        for term in _document_terms(doc_id, index):
            hits[term] = hits.get(term, 0) + 1
    scored: list[tuple[float, str]] = []
    for term, count in hits.items():
        if term in held:
            continue
        if index.document_frequency(term) == 0:
            continue
        if index.df_fraction(term) > SCAFFOLD_DF_FRACTION:
            continue
        scored.append((-(count / len(feedback)) * index.idf(term), term))
    scored.sort()
    return tuple(term for _, term in scored[:EXPANSION_TERMS])


def _document_terms(doc_id: str, index: AcquisitionIndex) -> tuple[str, ...]:
    """Distinct terms of one document, read back from the inverted index.

    The index is the only corpus view any arm has; reading the document object
    directly would give the arm access to fields (concept tags, access keys) that
    the package boundary rule keeps away from systems under test.
    """

    hit = index._forward_cache.get(doc_id)
    if hit is None:
        hit = tuple(sorted(term for term, posting in index.postings.items() if doc_id in posting))
        index._forward_cache[doc_id] = hit
    return hit


# --------------------------------------------------------------------------
# Merges
# --------------------------------------------------------------------------


def select_round_robin(cap: int, groups: Sequence[Sequence[str]]) -> tuple[str, ...]:
    """The archived selection rule, reimplemented verbatim.

    Copied in behaviour from
    `papers/.../scripts/run_autoresearchbench_wide_comparison.py::select_round_robin`
    so that B0 and B1 are merged exactly the way the campaign merged them.
    """

    chosen: dict[str, None] = {}
    position = 0
    while len(chosen) < cap and any(position < len(group) for group in groups):
        for group in groups:
            if len(chosen) >= cap:
                break
            if position < len(group):
                chosen.setdefault(group[position], None)
        position += 1
    return tuple(list(chosen)[:cap])


def select_coverage_first(
    cap: int,
    groups: Sequence[Sequence[str]],
    terms: Sequence[str],
    expanded: Sequence[str],
    index: AcquisitionIndex,
) -> tuple[str, ...]:
    """`D5`'s merge: order the pooled candidates by evidence, not by their source.

    Round-robin gives every call an equal share of the twenty output slots. That is
    neutral between systems, which is why the campaign chose it, but it is not
    neutral between *documents*: a call that returned twenty adjacent-but-wrong
    records contributes a third of the final answer no matter how weak its records
    are, and the archived stage diagnostic records gold identifiers that were
    retrieved raw and then lost at exactly this step.

    The replacement orders the whole pool by, in priority: how many *distinct*
    gated query terms the candidate agrees with, then an idf-weighted saturating
    score with expansion terms discounted by `EXPANSION_WEIGHT`, then `doc_id` for
    determinism. Coordination level first, magnitude second: a record agreeing with
    three of the question's discriminative terms is better evidence than one that
    repeats a single term many times, and term-frequency scoring alone does not say
    so. Nothing is deleted — low-coverage records are ordered below, not removed —
    so the rule cannot inflate recall by hiding candidates.
    """

    pool: dict[str, None] = {}
    for group in groups:
        for doc_id in group:
            pool.setdefault(doc_id, None)

    weights: dict[str, float] = {term: index.idf(term) for term in dict.fromkeys(terms)}
    for term in dict.fromkeys(expanded):
        weights.setdefault(term, EXPANSION_WEIGHT * index.idf(term))
    core = set(dict.fromkeys(terms))

    def key(doc_id: str) -> tuple[int, int, float, str]:
        coverage = 0
        score = 0.0
        for term, weight in weights.items():
            count = index.postings.get(term, {}).get(doc_id, 0)
            if not count:
                continue
            if term in core:
                coverage += 1
            score += weight * (count / (count + TF_SATURATION))
        gate = 0 if coverage >= MIN_COVERAGE else 1
        return (gate, -coverage, -score, doc_id)

    return tuple(sorted(pool, key=key)[:cap])


# --------------------------------------------------------------------------
# Arms
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ArmRun:
    """Everything one arm did on one task."""

    arm: str
    task_id: str
    family: str
    queries: tuple[Query, ...]
    per_call_results: tuple[tuple[str, ...], ...]
    query_terms: tuple[str, ...]
    expanded_terms: tuple[str, ...]
    candidates: tuple[str, ...]

    @property
    def provider_calls(self) -> int:
        return len(self.queries)


def _adjacent_pairs(terms: Sequence[str]) -> tuple[tuple[str, str], ...]:
    return tuple(zip(terms[:4], terms[1:5]))


def _run_archived_baseline(question: str, index: AcquisitionIndex) -> tuple[
    tuple[Query, ...], tuple[tuple[str, ...], ...], tuple[str, ...], tuple[str, ...]
]:
    """B0: `BASE_PRIMARY` / `BASE_CORE` / `BASE_BROAD`, round-robin merged."""

    five = d1_terms(question, limit=5)
    three = d1_terms(question, limit=3)
    six = d1_terms(question, limit=6)
    queries = (
        Query("BASE_PRIMARY", QueryKind.PAIR_DISJUNCTION, pairs=_adjacent_pairs(five)),
        Query("BASE_CORE", QueryKind.CONJUNCTION, terms=three[:2]),
        Query("BASE_BROAD", QueryKind.DISJUNCTION, terms=six),
    )
    results = tuple(index.search(query) for query in queries)
    return queries, results, six, ()


def _run_shipped(question: str, index: AcquisitionIndex) -> tuple[
    tuple[Query, ...], tuple[tuple[str, ...], ...], tuple[str, ...], tuple[str, ...]
]:
    """B1: the three shipped `arb_runtime` derivations, round-robin merged."""

    first = derive_current_vocabulary_query(question, limit=QUERY_WIDTH)
    second = derive_lexical_variant_query(question)
    queries: list[Query] = [
        Query(first.rule_id, QueryKind.CONJUNCTION, terms=first.source_terms),
        Query(second.rule_id, QueryKind.DISJUNCTION, terms=second.source_terms),
    ]
    results: list[tuple[str, ...]] = [index.search(query) for query in queries]

    held = [doc_id for group in results for doc_id in group]
    seed = held[0] if held else ""
    third = derive_citation_seed_query(seed or "no-seed")
    citation = Query(third.rule_id, QueryKind.CITATION, seed_doc_id=seed)
    queries.append(citation)
    results.append(index.search(citation) if seed else ())
    return tuple(queries), tuple(results), second.source_terms, ()


def _run_ladder(
    question: str,
    index: AcquisitionIndex,
    *,
    terms: Sequence[str],
    expand: bool,
) -> tuple[tuple[Query, ...], tuple[tuple[str, ...], ...], tuple[str, ...], tuple[str, ...]]:
    """The `D5` specificity ladder: three rungs inside a three-call budget.

    Rung 1 is the most specific query the index statistics say is satisfiable.
    Rung 2 is the full gated disjunction, which is recall insurance and a
    genuinely different derivation from rung 1 rather than a relabelling — a
    different width and a different join. Rung 3 spends the last call on
    vocabulary the corpus itself supplied, which is the only rung that can reach a
    record sharing no token with the question.

    The rungs are issued unconditionally rather than only when the previous rung
    disappoints. Conditioning on an observed result would make the number of
    provider calls depend on the outcome, and a comparison in which one arm can
    spend more calls than another on hard tasks is no longer matched.
    """

    width = satisfiable_conjunction_width(terms, index)
    queries: list[Query] = []
    results: list[tuple[str, ...]] = []

    if width >= MIN_CONJUNCTION_WIDTH:
        rung_one = Query("D5_R1_SATISFIABLE_CONJUNCTION", QueryKind.CONJUNCTION, terms=tuple(terms[:width]))
    else:
        # Nothing groundable survived: fall back to the widest disjunction rather
        # than emitting a conjunction the arithmetic has already refused.
        rung_one = Query("D5_R1_UNGROUNDED_FALLBACK", QueryKind.DISJUNCTION, terms=tuple(terms))
    queries.append(rung_one)
    results.append(index.search(rung_one))

    rung_two = Query("D5_R2_GATED_DISJUNCTION", QueryKind.DISJUNCTION, terms=tuple(terms))
    queries.append(rung_two)
    results.append(index.search(rung_two))

    feedback = select_coverage_first(
        FEEDBACK_DOCUMENTS, results, terms, (), index
    )
    expanded = expansion_terms(feedback, terms, index) if expand else ()
    if expanded:
        rung_three = Query(
            "D5_R3_GROUNDED_EXPANSION",
            QueryKind.DISJUNCTION,
            terms=tuple(terms[:3]) + expanded,
        )
    else:
        rung_three = Query(
            "D5_R3_PAIR_DIVERSIFICATION",
            QueryKind.PAIR_DISJUNCTION,
            pairs=_adjacent_pairs(tuple(terms)),
        )
    queries.append(rung_three)
    results.append(index.search(rung_three))
    return tuple(queries), tuple(results), tuple(terms), expanded


def run_arm(arm: str, task: Any, index: AcquisitionIndex) -> ArmRun:
    """Run one arm on one task. The arm sees `task.question` and nothing else."""

    question = task.question
    if arm == ARM_B0:
        queries, results, terms, expanded = _run_archived_baseline(question, index)
        candidates = select_round_robin(CANDIDATE_CAP, results)
    elif arm == ARM_B1:
        queries, results, terms, expanded = _run_shipped(question, index)
        candidates = select_round_robin(CANDIDATE_CAP, results)
    elif arm == ARM_S2:
        terms_in = d5_terms(question, index)
        queries, results, terms, expanded = _run_ladder(question, index, terms=terms_in, expand=True)
        candidates = select_coverage_first(CANDIDATE_CAP, results, terms, expanded, index)
    elif arm == ARM_A1:
        terms_in = d5_terms(question, index)
        queries, results, terms, expanded = _run_ladder(question, index, terms=terms_in, expand=True)
        candidates = select_round_robin(CANDIDATE_CAP, results)
    elif arm == ARM_A2:
        terms_in = d1_terms(question, limit=QUERY_WIDTH)
        queries, results, terms, expanded = _run_ladder(question, index, terms=terms_in, expand=True)
        candidates = select_coverage_first(CANDIDATE_CAP, results, terms, expanded, index)
    elif arm == ARM_A3:
        terms_in = d5_terms(question, index)
        queries, results, terms, expanded = _run_ladder(question, index, terms=terms_in, expand=False)
        candidates = select_coverage_first(CANDIDATE_CAP, results, terms, expanded, index)
    else:
        raise ValueError(f"unknown arm {arm}")

    if len(queries) != PROVIDER_CALLS_PER_TASK:
        raise AssertionError(
            f"{arm} issued {len(queries)} provider calls; the matched budget is "
            f"{PROVIDER_CALLS_PER_TASK}"
        )
    return ArmRun(
        arm=arm,
        task_id=task.task_id,
        family=task.family,
        queries=queries,
        per_call_results=results,
        query_terms=tuple(terms),
        expanded_terms=tuple(expanded),
        candidates=tuple(candidates),
    )


# --------------------------------------------------------------------------
# Scoring. Applied host-side, outside every arm.
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class TaskScore:
    task_id: str
    family: str
    arm: str
    recall: float
    precision: float
    intersection_over_union: float
    hits: int
    gold: int
    returned: int


def score_run(run: ArmRun, gold_doc_ids: Sequence[str]) -> TaskScore:
    """Recall, precision and IoU of one arm's capped candidate set on one task."""

    gold = set(gold_doc_ids)
    predicted = set(run.candidates)
    hits = len(gold & predicted)
    union = len(gold | predicted)
    return TaskScore(
        task_id=run.task_id,
        family=run.family,
        arm=run.arm,
        recall=(hits / len(gold)) if gold else 0.0,
        precision=(hits / len(predicted)) if predicted else 0.0,
        intersection_over_union=(hits / union) if union else 0.0,
        hits=hits,
        gold=len(gold),
        returned=len(predicted),
    )


def summarize(scores: Sequence[TaskScore]) -> dict[str, Any]:
    """The metric block, shaped like the archived official Wide metrics."""

    total = len(scores)
    if total == 0:
        return {"tasks": 0}
    return {
        "tasks": total,
        "mean_recall": sum(item.recall for item in scores) / total,
        "mean_precision": sum(item.precision for item in scores) / total,
        "mean_iou": sum(item.intersection_over_union for item in scores) / total,
        "mean_candidates_returned": sum(item.returned for item in scores) / total,
        "zero_hit_tasks": sum(1 for item in scores if item.hits == 0),
        "zero_hit_fraction": sum(1 for item in scores if item.hits == 0) / total,
        "mean_gold_size": sum(item.gold for item in scores) / total,
    }


# --------------------------------------------------------------------------
# Paired statistics
# --------------------------------------------------------------------------


def sign_test_exact(left: Sequence[float], right: Sequence[float]) -> dict[str, Any]:
    """Two-sided exact sign test on paired differences.

    Distribution-free and exact, which matters because per-task recall on a
    24-to-120-task slice is neither normal nor continuous. Ties are dropped, which
    is the standard treatment and is conservative here: this study expects many
    tasks on which both arms score zero.
    """

    if len(left) != len(right):
        raise ValueError("paired samples must be the same length")
    wins = sum(1 for a, b in zip(left, right) if a > b)
    losses = sum(1 for a, b in zip(left, right) if b > a)
    trials = wins + losses
    if trials == 0:
        return {"wins": wins, "losses": losses, "trials": 0, "p_value": 1.0}
    smaller = min(wins, losses)
    tail = sum(math.comb(trials, i) for i in range(smaller + 1)) / (2.0**trials)
    return {
        "wins": wins,
        "losses": losses,
        "trials": trials,
        "p_value": min(1.0, 2.0 * tail),
    }


def paired_bootstrap(
    left: Sequence[float],
    right: Sequence[float],
    *,
    resamples: int,
    seed: int,
    confidence: float = 0.95,
) -> dict[str, Any]:
    """Percentile bootstrap CI for the paired mean difference `left - right`.

    Resampling is over *tasks*, keeping each task's pair together, because the two
    arms are run on the same tasks and treating them as independent samples would
    overstate the interval.
    """

    import random as _random

    if len(left) != len(right):
        raise ValueError("paired samples must be the same length")
    differences = [a - b for a, b in zip(left, right)]
    n = len(differences)
    if n == 0:
        return {"mean": 0.0, "ci_low": 0.0, "ci_high": 0.0, "resamples": 0}
    rng = _random.Random(seed)
    means: list[float] = []
    for _ in range(resamples):
        total = 0.0
        for _ in range(n):
            total += differences[rng.randrange(n)]
        means.append(total / n)
    means.sort()
    lower = (1.0 - confidence) / 2.0
    low_index = max(0, min(resamples - 1, int(lower * resamples)))
    high_index = max(0, min(resamples - 1, int((1.0 - lower) * resamples) - 1))
    return {
        "mean": sum(differences) / n,
        "ci_low": means[low_index],
        "ci_high": means[high_index],
        "resamples": resamples,
        "confidence": confidence,
        "seed": seed,
    }
