"""Baseline, reference and successor candidate-generation mechanics.

Five arms over one index, defined by
`papers/paper-02-open-world-scientific-discovery/protocol/P2_LEXICAL_ECHO_SUCCESSOR_FREEZE_2026-08-21.md`:

* **B0** `CURRENT_D1_UNWEIGHTED` — the mechanic that produced the negative.
  `arb_runtime.derive_current_vocabulary_query` (rule `D1_CURRENT_VOCABULARY`)
  followed by an unweighted surface-frequency ranking. This is the "treat every
  query term as a content term" behaviour the stage attribution names.
* **B1** `CURRENT_D1_BM25` — the same `D1` query ranked by
  `baselines.Bm25Scorer`, reused verbatim. Present because BM25's document-side
  IDF is the obvious objection to the successor: if BM25 alone repairs the
  world, the successor's marginal contribution is small and the freeze commits
  to saying so.
* **S1** `D4_DISCRIMINATIVE_TERM_GATING` — the successor. Gate the question's
  tokens by corpus document frequency, select by discriminativeness rather than
  by within-question repetition, score with IDF weights and term saturation, and
  admit only documents that agree with the query on two discriminative terms.
* **A1** `D4_GATED_QUERY_UNWEIGHTED` — successor query, baseline ranking.
  Isolates the query-*selection* half of the repair.
* **A2** `D1_QUERY_WEIGHTED` — baseline query, successor ranking, no admission
  rule. Isolates the *scoring* half.

Everything is deterministic. No arm sees the gold set, the target document, or
the family label; the only corpus knowledge any arm uses is document frequency,
which is an index statistic rather than an answer.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from .arb_runtime import _content_tokens, derive_current_vocabulary_query
from .baselines import Bm25Scorer
from .corpus import Document

# --------------------------------------------------------------------------
# Frozen mechanic constants (hashed with the world parameters).
# --------------------------------------------------------------------------

CANDIDATE_BUDGET_K = 11
PRIMARY_K = 10
QUERY_WIDTH = 6
INCIDENTAL_DF_FRACTION = 0.05
TF_SATURATION = 1.2
MIN_CONTENT_MATCH = 2
MRR_DEPTH = 50

ARM_B0 = "B0_CURRENT_D1_UNWEIGHTED"
ARM_B1 = "B1_CURRENT_D1_BM25"
ARM_S1 = "S1_D4_DISCRIMINATIVE_TERM_GATING"
ARM_A1 = "A1_D4_GATED_QUERY_UNWEIGHTED"
ARM_A2 = "A2_D1_QUERY_WEIGHTED"

ARM_ORDER: tuple[str, ...] = (ARM_B0, ARM_B1, ARM_S1, ARM_A1, ARM_A2)

MECHANIC_PARAMETERS: dict[str, Any] = {
    "candidate_budget_k": CANDIDATE_BUDGET_K,
    "primary_k": PRIMARY_K,
    "query_width": QUERY_WIDTH,
    "incidental_df_fraction": INCIDENTAL_DF_FRACTION,
    "tf_saturation": TF_SATURATION,
    "min_content_match": MIN_CONTENT_MATCH,
    "mrr_depth": MRR_DEPTH,
    "arms": list(ARM_ORDER),
}


# --------------------------------------------------------------------------
# Index
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class EchoIndex:
    """Term statistics over the corpus, shared by every arm.

    `term_frequency` uses the *same* tokenizer the baseline's query derivation
    uses (`arb_runtime._content_tokens`), so no arm can gain from a different
    analyzer. `document_frequency` and `idf` come from `baselines.Bm25Scorer`,
    so B1 and S1 share one definition of discriminativeness and cannot differ
    because of it.
    """

    doc_ids: tuple[str, ...]
    term_frequency: dict[str, dict[str, int]]
    scorer: Bm25Scorer
    size: int
    #: Memo for BM25 per-term contributions. BM25's score over a term set is the
    #: sum of its per-term contributions, so caching them is exact, not an
    #: approximation, and it keeps the reference arm from re-tokenising the
    #: corpus once per task.
    _bm25_cache: dict[str, dict[str, float]] = field(default_factory=dict)

    def document_frequency(self, term: str) -> int:
        return len(self.term_frequency.get(term, ()))

    def idf(self, term: str) -> float:
        return self.scorer.inverse_document_frequency(term)

    def bm25_contribution(self, term: str, doc_id: str) -> float:
        cached = self._bm25_cache.get(term)
        if cached is None:
            cached = {
                key: self.scorer.score(key, (term,))
                for key in self.term_frequency.get(term, {})
            }
            self._bm25_cache[term] = cached
        return cached.get(doc_id, 0.0)


def build_index(documents: Sequence[Document]) -> EchoIndex:
    texts = [(item.doc_id, f"{item.title} {item.abstract}") for item in documents]
    term_frequency: dict[str, dict[str, int]] = {}
    for doc_id, text in texts:
        for token in _content_tokens(text):
            term_frequency.setdefault(token, {})
            counts = term_frequency[token]
            counts[doc_id] = counts.get(doc_id, 0) + 1
    return EchoIndex(
        doc_ids=tuple(doc_id for doc_id, _ in texts),
        term_frequency=term_frequency,
        scorer=Bm25Scorer(texts),
        size=len(texts),
    )


# --------------------------------------------------------------------------
# Query derivations
# --------------------------------------------------------------------------


def baseline_query(question: str) -> tuple[str, ...]:
    """D1, exactly as the probe ran it: within-question frequency, top 6."""

    return derive_current_vocabulary_query(question, limit=QUERY_WIDTH).source_terms


def successor_query(question: str, index: EchoIndex) -> tuple[str, ...]:
    """D4: gate by corpus document frequency, then select by discriminativeness.

    Two departures from D1, both aimed at the named mechanism:

    * a token in more than `INCIDENTAL_DF_FRACTION` of the corpus cannot by
      itself identify a needle, so it is not a content term and is dropped —
      this is what removes 'supplementary' from the query rather than letting it
      compete with the topic;
    * the survivors are ranked by ``idf`` alone rather than by within-question
      repetition, which is what lets a content term mentioned once outrank an
      apparatus term mentioned twice.

    Selection by ``idf * count`` was considered and rejected in the freeze: a
    doubled count can still lift a low-idf term above a high-idf one, so it does
    not separate the strata. Query width is the same 6 as D1, so the comparison
    is not a budget gift.
    """

    counts: dict[str, int] = {}
    order: dict[str, int] = {}
    for position, token in enumerate(_content_tokens(question)):
        counts[token] = counts.get(token, 0) + 1
        order.setdefault(token, position)

    retained: list[str] = []
    for token in counts:
        frequency = index.document_frequency(token)
        if frequency == 0:
            continue
        if frequency / max(1, index.size) > INCIDENTAL_DF_FRACTION:
            continue
        retained.append(token)

    retained.sort(key=lambda token: (-index.idf(token), order[token]))
    return tuple(retained[:QUERY_WIDTH])


# --------------------------------------------------------------------------
# Rankings
# --------------------------------------------------------------------------


def _unweighted_scores(terms: Sequence[str], index: EchoIndex) -> dict[str, float]:
    """B0's ranking: every query term contributes its raw frequency, equally."""

    scores: dict[str, float] = {}
    for term in dict.fromkeys(terms):
        for doc_id, count in index.term_frequency.get(term, {}).items():
            scores[doc_id] = scores.get(doc_id, 0.0) + float(count)
    return scores


def _bm25_scores(terms: Sequence[str], index: EchoIndex) -> dict[str, float]:
    scores: dict[str, float] = {}
    for term in dict.fromkeys(terms):
        for doc_id in index.term_frequency.get(term, {}):
            scores[doc_id] = scores.get(doc_id, 0.0) + index.bm25_contribution(term, doc_id)
    return scores


def _weighted_scores(terms: Sequence[str], index: EchoIndex) -> dict[str, float]:
    """S1's ranking: idf-weighted, saturating in term frequency.

    The weight makes a match on a rare content term worth more than a match on a
    common one. The saturation stops an abstract that says 'supplementary' four
    times from outranking a document that matches several distinct content terms.
    """

    scores: dict[str, float] = {}
    for term in dict.fromkeys(terms):
        weight = index.idf(term)
        for doc_id, count in index.term_frequency.get(term, {}).items():
            saturated = count / (count + TF_SATURATION)
            scores[doc_id] = scores.get(doc_id, 0.0) + weight * saturated
    return scores


def _match_counts(terms: Sequence[str], index: EchoIndex) -> dict[str, int]:
    matches: dict[str, int] = {}
    for term in dict.fromkeys(terms):
        for doc_id in index.term_frequency.get(term, {}):
            matches[doc_id] = matches.get(doc_id, 0) + 1
    return matches


def _rank(
    index: EchoIndex,
    scores: dict[str, float],
    admitted: dict[str, int] | None = None,
) -> tuple[str, ...]:
    """Full deterministic ranking over the whole corpus.

    Ties break on `doc_id` ascending. When `admitted` is supplied, documents
    failing the topical-agreement rule are ordered strictly below every admitted
    document — demoted, not deleted, so the rule cannot inflate recall at large
    `k`.
    """

    def key(doc_id: str) -> tuple[int, float, str]:
        gate = 0
        if admitted is not None and admitted.get(doc_id, 0) < MIN_CONTENT_MATCH:
            gate = 1
        return (gate, -scores.get(doc_id, 0.0), doc_id)

    return tuple(sorted(index.doc_ids, key=key))


# --------------------------------------------------------------------------
# Arms
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ArmResult:
    """One arm's outcome on one task."""

    arm: str
    task_id: str
    family: str
    query_terms: tuple[str, ...]
    ranking: tuple[str, ...]
    target_rank: int

    @property
    def candidates(self) -> tuple[str, ...]:
        return self.ranking[:CANDIDATE_BUDGET_K]

    def hit_at(self, k: int) -> bool:
        return self.target_rank <= k


def generate_candidates(
    arm: str, question: str, index: EchoIndex
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Run one arm's candidate generation. Returns `(query_terms, ranking)`.

    This function is the whole of every arm, and its only inputs are the
    question text and index statistics. It is deliberately not given the task,
    the target or the family label — the package boundary rule in
    `orion.study.p2.__init__` is that a system under test never receives the
    gold, and an arm that could read `target_doc_id` would breach it even if it
    chose not to.
    """

    if arm in (ARM_B0, ARM_B1, ARM_A2):
        terms = baseline_query(question)
    elif arm in (ARM_S1, ARM_A1):
        terms = successor_query(question, index)
    else:
        raise ValueError(f"unknown arm {arm}")

    if arm in (ARM_B0, ARM_A1):
        scores = _unweighted_scores(terms, index)
        admitted = None
    elif arm == ARM_B1:
        scores = _bm25_scores(terms, index)
        admitted = None
    elif arm == ARM_A2:
        scores = _weighted_scores(terms, index)
        admitted = None
    else:
        scores = _weighted_scores(terms, index)
        admitted = _match_counts(terms, index)

    return terms, _rank(index, scores, admitted)


def run_arm(arm: str, task: Any, index: EchoIndex) -> ArmResult:
    """Host-side scoring of one arm on one task.

    The arm produces its ranking from the question alone; the target is applied
    here, outside the arm, purely to locate it in that ranking.
    """

    terms, ranking = generate_candidates(arm, task.question, index)
    target_rank = ranking.index(task.target_doc_id) + 1
    return ArmResult(
        arm=arm,
        task_id=task.task_id,
        family=task.family,
        query_terms=terms,
        ranking=ranking[:MRR_DEPTH],
        target_rank=target_rank,
    )


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------


def _median(values: Sequence[float]) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[middle])
    return (ordered[middle - 1] + ordered[middle]) / 2.0


def summarize(results: Sequence[ArmResult]) -> dict[str, Any]:
    """hit@1, hit@10, MRR@50 and rank distribution for one arm on one family."""

    total = len(results)
    if total == 0:
        return {"tasks": 0}
    ranks = [item.target_rank for item in results]
    return {
        "tasks": total,
        "hit_at_1": sum(1 for r in ranks if r <= 1) / total,
        "hit_at_10": sum(1 for r in ranks if r <= PRIMARY_K) / total,
        "hit_at_k_budget": sum(1 for r in ranks if r <= CANDIDATE_BUDGET_K) / total,
        "mrr_at_50": sum((1.0 / r) if r <= MRR_DEPTH else 0.0 for r in ranks) / total,
        "median_target_rank": _median(ranks),
        "best_target_rank": min(ranks),
        "worst_target_rank": max(ranks),
    }


def mcnemar_exact(
    left: Sequence[bool], right: Sequence[bool]
) -> dict[str, Any]:
    """Exact two-sided McNemar (binomial) on paired binary outcomes.

    `b` counts tasks the left arm wins and the right loses, `c` the reverse. The
    p-value is the two-sided exact binomial tail at p=0.5 over the discordant
    pairs, which needs no large-sample approximation and stays valid when `b` is
    zero — which is the case this study most expects.
    """

    if len(left) != len(right):
        raise ValueError("paired outcomes must be the same length")
    b = sum(1 for x, y in zip(left, right) if x and not y)
    c = sum(1 for x, y in zip(left, right) if y and not x)
    discordant = b + c
    if discordant == 0:
        return {"b": b, "c": c, "discordant": 0, "p_value": 1.0}
    smaller = min(b, c)
    tail = sum(math.comb(discordant, i) for i in range(smaller + 1)) / (2.0**discordant)
    return {
        "b": b,
        "c": c,
        "discordant": discordant,
        "p_value": min(1.0, 2.0 * tail),
    }
