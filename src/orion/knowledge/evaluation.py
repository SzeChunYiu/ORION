from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum

_TOKEN = re.compile(r"[a-z0-9]+")


class GoldTier(str, Enum):
    """How much a gold set can support, from the recall-benchmark survey.

    The tiers are not decoration. Most published "recall" numbers are T1 — a
    single target document — and reporting those as recall is the central
    measurement error in this literature.
    """

    T3_PROTOCOL_COMPLETE = "T3_PROTOCOL_COMPLETE"
    T2_POOLED = "T2_POOLED"
    T1_SINGLE_TARGET = "T1_SINGLE_TARGET"
    T0_NO_DOCUMENT_GOLD = "T0_NO_DOCUMENT_GOLD"

    @property
    def supports_recall(self) -> bool:
        """Only a complete or pooled relevant set has a real denominator."""

        return self in {GoldTier.T3_PROTOCOL_COMPLETE, GoldTier.T2_POOLED}


@dataclass(frozen=True)
class RecallTask:
    """One retrieval task with a declared gold set and its provenance."""

    task_id: str
    query: str
    gold_ids: frozenset[str]
    corpus_ids: tuple[str, ...]
    tier: GoldTier
    provenance: str

    def __post_init__(self) -> None:
        if not self.task_id.strip() or not self.query.strip():
            raise ValueError("a recall task needs an identity and a query")
        if not self.provenance.strip():
            raise ValueError("a gold set must state where it came from")
        missing = self.gold_ids - set(self.corpus_ids)
        if missing:
            raise ValueError(
                f"gold ids absent from the corpus make recall unmeasurable: {sorted(missing)[:3]}"
            )

    @property
    def prevalence(self) -> float:
        """Base rate. Every recall number must be read against it."""

        return len(self.gold_ids) / len(self.corpus_ids) if self.corpus_ids else 0.0


@dataclass(frozen=True)
class RankingScore:
    """What one ranking achieved on one task."""

    system: str
    task_id: str
    recall_at_k: tuple[tuple[int, float], ...]
    screened_to_target_recall: int | None
    work_saved: float | None
    target_recall: float

    def recall(self, k: int) -> float | None:
        for cutoff, value in self.recall_at_k:
            if cutoff == k:
                return value
        return None


def recall_at(ranking: Sequence[str], gold: frozenset[str], k: int) -> float:
    if k < 1:
        raise ValueError("k must be positive")
    if not gold:
        return 0.0
    return len(set(ranking[:k]) & gold) / len(gold)


def screened_to_recall(
    ranking: Sequence[str], gold: frozenset[str], target: float
) -> int | None:
    """How far down the ranking you must screen to reach a recall target.

    None means the target is unreachable in this ranking, which is a real
    outcome and must not be rendered as a large number.
    """

    if not 0.0 < target <= 1.0:
        raise ValueError("target recall must be in (0, 1]")
    if not gold:
        return None
    needed = math.ceil(target * len(gold))
    found = 0
    for position, item in enumerate(ranking, start=1):
        if item in gold:
            found += 1
            if found >= needed:
                return position
    return None


def work_saved_over_sampling(
    screened: int | None, corpus_size: int, target: float
) -> float | None:
    """WSS@target: fraction of screening avoided versus random sampling.

    `WSS@r = (N - n_r)/N - (1 - r)`. Subtracting `(1 - r)` is what makes this a
    comparison against chance rather than a raw saving, so a ranking no better
    than random scores about zero instead of looking impressive.
    """

    if screened is None or corpus_size <= 0:
        return None
    return (corpus_size - screened) / corpus_size - (1.0 - target)


def _tokens(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


def naive_keyword_ranking(
    task: RecallTask, documents: Mapping[str, str]
) -> tuple[str, ...]:
    """The baseline every claim about ORION's retrieval must beat.

    Deliberately plain BM25-style lexical scoring over the query terms. This is
    not a straw man: on ResearchArena a naive title query outscored every LLM
    agent, and on MetaSyn one-pass retrieval beat the agentic systems by roughly
    twenty points of inclusion recall. The prior from the evidence is that
    scaffolding loses, so the baseline is the hypothesis to falsify.
    """

    query_terms = set(_tokens(task.query))
    if not query_terms:
        return tuple(task.corpus_ids)
    corpus = [(item, _tokens(documents.get(item, ""))) for item in task.corpus_ids]
    total = len(corpus) or 1
    lengths = [len(tokens) for _, tokens in corpus]
    average_length = (sum(lengths) / total) or 1.0
    frequency = Counter(
        term
        for _, tokens in corpus
        for term in set(tokens)
        if term in query_terms
    )
    k1, b = 1.5, 0.75

    scored: list[tuple[float, int, str]] = []
    for index, (item, tokens) in enumerate(corpus):
        counts = Counter(tokens)
        length = len(tokens) or 1
        score = 0.0
        for term in query_terms:
            occurrences = counts.get(term, 0)
            if not occurrences:
                continue
            containing = frequency.get(term, 0)
            idf = math.log(1 + (total - containing + 0.5) / (containing + 0.5))
            norm = occurrences * (k1 + 1) / (
                occurrences + k1 * (1 - b + b * length / average_length)
            )
            score += idf * norm
        scored.append((-score, index, item))
    scored.sort()
    return tuple(item for _, _, item in scored)


def score_ranking(
    system: str,
    task: RecallTask,
    ranking: Sequence[str],
    *,
    cutoffs: Sequence[int] = (10, 100, 1000),
    target_recall: float = 0.95,
) -> RankingScore:
    screened = screened_to_recall(ranking, task.gold_ids, target_recall)
    return RankingScore(
        system=system,
        task_id=task.task_id,
        recall_at_k=tuple((k, recall_at(ranking, task.gold_ids, k)) for k in cutoffs),
        screened_to_target_recall=screened,
        work_saved=work_saved_over_sampling(
            screened, len(task.corpus_ids), target_recall
        ),
        target_recall=target_recall,
    )


class UnsupportedClaim(ValueError):
    """Raised when a report would assert more than its gold set can support."""


@dataclass(frozen=True)
class Comparison:
    """A system score reported only alongside the baseline it must beat."""

    task: RecallTask
    system: RankingScore
    baseline: RankingScore

    def margin_at(self, k: int) -> float | None:
        system = self.system.recall(k)
        baseline = self.baseline.recall(k)
        if system is None or baseline is None:
            return None
        return system - baseline

    @property
    def beats_baseline(self) -> bool:
        margins = [self.margin_at(k) for k, _ in self.system.recall_at_k]
        present = [item for item in margins if item is not None]
        return bool(present) and all(item >= 0 for item in present) and any(
            item > 0 for item in present
        )


def compare_against_baseline(
    task: RecallTask,
    system_ranking: Sequence[str],
    documents: Mapping[str, str],
    *,
    system: str = "orion",
    cutoffs: Sequence[int] = (10, 100, 1000),
    target_recall: float = 0.95,
) -> Comparison:
    """Score a system against the naive baseline on one task, or refuse.

    Two refusals rather than one caveat. A gold set that cannot support recall
    is rejected outright, because a single-target set measures whether one known
    paper was found and reporting that as recall is the central measurement
    error in this literature. And a system score is never produced alone: the
    baseline is computed in the same call, on the same task, so a report that
    omits it cannot be assembled by accident.
    """

    if not task.tier.supports_recall:
        raise UnsupportedClaim(
            f"tier {task.tier.value} has no complete relevant set; recall is undefined "
            "for it, and reporting a top-k hit rate as recall is the error this "
            "harness exists to prevent"
        )
    return Comparison(
        task=task,
        system=score_ranking(
            system, task, system_ranking, cutoffs=cutoffs, target_recall=target_recall
        ),
        baseline=score_ranking(
            "naive_keyword",
            task,
            naive_keyword_ranking(task, documents),
            cutoffs=cutoffs,
            target_recall=target_recall,
        ),
    )
