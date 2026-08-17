"""One-stage failure attribution for P2 external revival (issue #279).

The taxonomy is the issue's frozen list. Classification is a pure function of a
retained trace: it does not read campaign prose and it does not average stages.
The earliest pipeline stage that explains a miss wins.

Censoring is not a later residual that can be skipped. A rate-limited or
unavailable route that never observed the index is ``CENSORED_ROUTE`` (an open
obligation), never a silent candidate-generation zero. Semantic Scholar HTTP 429
is the named case of that rule.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Mapping, Sequence

__all__ = [
    "CENSOR_STATUSES",
    "FailureStage",
    "ItemTrace",
    "STAGE_ORDER",
    "aggregate_stages",
    "classify_item",
    "deep_archive_stage",
    "ledger_from_artifacts",
    "normalize_tokens",
    "query_is_plausible",
    "wide_campaign_attribution",
]

TOKEN = re.compile(r"[A-Za-z0-9]{4,}")

#: Provider statuses that mean "we did not observe the index".
CENSOR_STATUSES = frozenset(
    {
        "RATE_LIMITED",
        "RATE_LIMIT_DEFERRED",
        "UNAVAILABLE",
        "KEY_REQUIRED",
        "CREDENTIAL_REQUIRED",
        "TIMEOUT",
        "SERVICE_ERROR",
        "PROVIDER_ERROR",
        "TRANSPORT_ERROR",
        "ERROR",
    }
)
OK_STATUSES = frozenset({"OK", "RESULTS", "EMPTY"})


class FailureStage(str, Enum):
    """Earliest causal stage for a missed gold item or premature closure."""

    NONE = "NONE"
    QUERY_DERIVATION_MISS = "QUERY_DERIVATION_MISS"
    CANDIDATE_GENERATION_MISS = "CANDIDATE_GENERATION_MISS"
    RANKING_MISS = "RANKING_MISS"
    SCREENING_MISS = "SCREENING_MISS"
    IDENTITY_DEDUP_ERROR = "IDENTITY_DEDUP_ERROR"
    ROUTE_STOP_ERROR = "ROUTE_STOP_ERROR"
    TASK_STOP_ERROR = "TASK_STOP_ERROR"
    CENSORED_ROUTE = "CENSORED_ROUTE"
    BUDGET_EXHAUSTION = "BUDGET_EXHAUSTION"
    OTHER_UNRESOLVED = "OTHER_UNRESOLVED"
    CANNOT_CHECK = "CANNOT_CHECK"


#: Pipeline order used as earliest-stage precedence. ``CENSORED_ROUTE`` is
#: consulted at retrieval time (before candidate-generation is allowed to
#: explain a miss that was never observed).
STAGE_ORDER: tuple[FailureStage, ...] = (
    FailureStage.QUERY_DERIVATION_MISS,
    FailureStage.CANDIDATE_GENERATION_MISS,
    FailureStage.RANKING_MISS,
    FailureStage.SCREENING_MISS,
    FailureStage.IDENTITY_DEDUP_ERROR,
    FailureStage.ROUTE_STOP_ERROR,
    FailureStage.TASK_STOP_ERROR,
    FailureStage.CENSORED_ROUTE,
    FailureStage.BUDGET_EXHAUSTION,
    FailureStage.OTHER_UNRESOLVED,
)


@dataclass(frozen=True)
class ItemTrace:
    """Everything classification is allowed to see. Gold enters as labels, not
    as a licence to rewrite queries: this object is scored after candidate
    custody, from retained traces."""

    task_id: str
    gold_ids: tuple[str, ...] = ()
    gold_titles: tuple[str, ...] = ()
    queries: tuple[str, ...] = ()
    candidates: tuple[str, ...] = ()
    candidate_pool_ranked: tuple[str, ...] | None = None
    ranking_cutoff: int | None = None
    screened_out: tuple[str, ...] = ()
    identity_conflated: bool = False
    route_stop_while_gain_possible: bool = False
    task_closed_with_open_routes: bool = False
    provider_statuses: tuple[str, ...] = ()
    budget_exhausted: bool = False
    gold_recovered: bool | None = None


def normalize_tokens(text: str) -> frozenset[str]:
    """Lowercased tokens of length >= 4. Shared with the Deep string diagnostic."""

    return frozenset(TOKEN.findall(text.lower()))


def query_is_plausible(
    queries: Sequence[str],
    *,
    gold_ids: Sequence[str],
    gold_titles: Sequence[str],
) -> bool:
    """True iff at least one query could plausibly surface a gold item.

    A query is plausible when it contains a gold identifier, or shares two or
    more content tokens with a gold title. This is a retained-trace test, not a
    learned ranker.
    """

    gold_id_set = {item.strip().lower() for item in gold_ids if item.strip()}
    title_token_sets = [normalize_tokens(title) for title in gold_titles if title.strip()]
    for query in queries:
        lowered = query.lower()
        if any(gold_id and gold_id in lowered for gold_id in gold_id_set):
            return True
        query_tokens = normalize_tokens(query)
        for title_tokens in title_token_sets:
            if len(query_tokens & title_tokens) >= 2:
                return True
    return False


def _norm_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _gold_in(haystack: Iterable[str], trace: ItemTrace) -> bool:
    needles = [_norm_key(item) for item in (*trace.gold_ids, *trace.gold_titles) if item.strip()]
    if not needles:
        return False
    hay = [_norm_key(item) for item in haystack if item.strip()]
    for needle in needles:
        if not needle:
            continue
        for item in hay:
            if needle == item or needle in item or item in needle:
                return True
    return False


def _statuses(trace: ItemTrace) -> tuple[frozenset[str], bool, bool]:
    statuses = frozenset(item.upper() for item in trace.provider_statuses)
    censored = bool(statuses & CENSOR_STATUSES)
    observed = bool(statuses & OK_STATUSES) or bool(trace.candidates) or bool(
        trace.candidate_pool_ranked
    )
    return statuses, censored, observed


def classify_item(trace: ItemTrace) -> FailureStage:
    """Return the earliest causal stage for one missed item.

    Hits return ``NONE``. A trace with no gold labels returns ``CANNOT_CHECK``.
    """

    if not trace.gold_ids and not trace.gold_titles:
        return FailureStage.CANNOT_CHECK

    recovered = (
        trace.gold_recovered
        if trace.gold_recovered is not None
        else _gold_in(trace.candidates, trace)
    )
    if recovered:
        return FailureStage.NONE

    _, censored, observed = _statuses(trace)
    pool = trace.candidate_pool_ranked if trace.candidate_pool_ranked is not None else trace.candidates
    gold_in_pool = _gold_in(pool, trace)
    plausible = query_is_plausible(
        trace.queries, gold_ids=trace.gold_ids, gold_titles=trace.gold_titles
    )

    # Never treat an unobserved index as evidence that the item is absent.
    if censored and not observed:
        return FailureStage.CENSORED_ROUTE

    if not trace.queries or not plausible:
        return FailureStage.QUERY_DERIVATION_MISS

    if not gold_in_pool:
        return FailureStage.CANDIDATE_GENERATION_MISS

    if (
        trace.ranking_cutoff is not None
        and trace.candidate_pool_ranked is not None
        and not _gold_in(trace.candidates, trace)
    ):
        return FailureStage.RANKING_MISS

    if trace.screened_out and _gold_in(trace.screened_out, trace):
        return FailureStage.SCREENING_MISS

    if trace.identity_conflated:
        return FailureStage.IDENTITY_DEDUP_ERROR

    if trace.route_stop_while_gain_possible:
        return FailureStage.ROUTE_STOP_ERROR

    if trace.task_closed_with_open_routes:
        return FailureStage.TASK_STOP_ERROR

    if censored:
        return FailureStage.CENSORED_ROUTE

    if trace.budget_exhausted:
        return FailureStage.BUDGET_EXHAUSTION

    return FailureStage.OTHER_UNRESOLVED


def aggregate_stages(stages: Sequence[FailureStage]) -> dict[str, Any]:
    """Count stages. Dominance ignores NONE and CANNOT_CHECK."""

    counts: dict[str, int] = {}
    for stage in stages:
        counts[stage.value] = counts.get(stage.value, 0) + 1
    actionable = [
        stage
        for stage in stages
        if stage not in {FailureStage.NONE, FailureStage.CANNOT_CHECK}
    ]
    dominant = None
    if actionable:
        ranked = sorted(
            (
                (actionable.count(stage), STAGE_ORDER.index(stage), stage.value)
                for stage in set(actionable)
            ),
            key=lambda row: (-row[0], row[1]),
        )
        dominant = ranked[0][2]
    return {
        "n": len(stages),
        "counts": dict(sorted(counts.items())),
        "dominant_earliest_stage": dominant,
    }


def deep_archive_stage(attribution: Mapping[str, Any], archive: Mapping[str, Any]) -> dict[str, Any]:
    """Map the committed Deep zero-hit diagnostic onto the taxonomy.

    Exact and substring recoveries of 0 with a passing judge control is
    candidate generation, not a judge or stopping failure.
    """

    counts = attribution.get("counts") or {}
    exact = int(counts.get("exact_title_recoveries", -1))
    substring = int(counts.get("substring_recoveries", -1))
    total = int(counts.get("total_items", 0))
    hits = int((archive.get("official_metrics") or {}).get("hits", -1))
    hit_rate = (archive.get("official_metrics") or {}).get("hit_rate")
    control = archive.get("judge_control") or {}
    control_passed = bool(control.get("verdict") == "CONTROL_PASSED")

    if exact == 0 and substring == 0 and hits == 0 and control_passed:
        stage = FailureStage.CANDIDATE_GENERATION_MISS.value
        reason = (
            "Judge control passed; official hits 0; judge-free exact and substring "
            "recovery of reference titles from frozen candidates is 0. The failing "
            "stage is candidate generation, not judging, screening, or stopping."
        )
    else:
        stage = FailureStage.OTHER_UNRESOLVED.value
        reason = "Deep diagnostic did not match the exact-zero candidate-generation signature."

    return {
        "benchmark": "AutoResearchBench Deep",
        "n_items": total,
        "official_hits": hits,
        "official_hit_rate": hit_rate,
        "exact_title_recoveries": exact,
        "substring_recoveries": substring,
        "token_overlap_ge_0.5_recoveries": counts.get("token_overlap_ge_0.5_recoveries"),
        "items_empty_candidates": counts.get("items_empty_candidates"),
        "judge_control_passed": control_passed,
        "earliest_stage": stage,
        "item_level_computable": True,
        "reason": reason,
        "source_records": [
            "evidence/external_results/DEEP_ZERO_HIT_STAGE_ATTRIBUTION_2026-08-17.json",
            "evidence/external_results/DEEP_OFFICIAL_ARCHIVE_V1.json",
        ],
    }


def wide_campaign_attribution(probe: Mapping[str, Any]) -> dict[str, Any]:
    """Campaign-level Wide attribution from the archived keyless probe.

    Per-task traces are not in the repository, so item-level stages are
    ``CANNOT_CHECK``. Provider 429/service failures are censored-route census,
    not scientific zeros. The remaining OK traffic is consistent with
    candidate-generation failure but cannot be item-classified here.
    """

    status_counts = probe.get("provider_status_counts") or {}
    ok = int(status_counts.get("OK", 0))
    rate_limited = int(status_counts.get("RATE_LIMITED", 0))
    service_error = int(status_counts.get("SERVICE_ERROR", 0))
    metrics = probe.get("official_metrics") or {}
    attempted = int((probe.get("coverage") or {}).get("tasks_attempted", 0))
    censored = rate_limited + service_error
    return {
        "benchmark": "AutoResearchBench Wide",
        "archive": "AUTORESEARCHBENCH_WIDE_KEYLESS_PROBE_V1.json",
        "claim_scope": probe.get("claim_scope"),
        "n_tasks_attempted": attempted,
        "avg_iou": metrics.get("avg_iou"),
        "avg_recall": metrics.get("avg_recall"),
        "provider_status_counts": dict(status_counts),
        "censored_route_census": {
            "RATE_LIMITED": rate_limited,
            "SERVICE_ERROR": service_error,
            "total": censored,
            "rule": (
                "HTTP 429 / service error is CENSORED_ROUTE (open obligation), "
                "never a silent drop and never evidence of absence."
            ),
        },
        "item_level_computable": False,
        "item_level_stage": FailureStage.CANNOT_CHECK.value,
        "item_level_blocker": (
            "Per-task candidate/query traces for the keyless Wide probe are not "
            "committed in the repository; only the official summary is."
        ),
        "ok_traffic_consistent_with": FailureStage.CANDIDATE_GENERATION_MISS.value,
        "ok_traffic_n": ok,
        "reason": (
            f"{ok} provider-OK tasks scored avg_recall "
            f"{metrics.get('avg_recall')} / avg_iou {metrics.get('avg_iou')}; "
            f"{censored} tasks are censored-route obligations. Item-level "
            "confirmation requires retained traces."
        ),
    }


def ledger_from_artifacts(
    *,
    deep_attribution: Mapping[str, Any],
    deep_archive: Mapping[str, Any],
    wide_probe: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the issue #279 one-stage ledger from committed artifacts only."""

    deep = deep_archive_stage(deep_attribution, deep_archive)
    wide = wide_campaign_attribution(wide_probe)
    dominant = deep["earliest_stage"]
    return {
        "schema_version": "orion.p2.one-stage-failure-attribution.v1",
        "issue": 279,
        "rule": (
            "Classify the earliest causal stage from retained traces. Do not "
            "average stages. Do not treat provider unavailability as a scientific zero."
        ),
        "taxonomy": [stage.value for stage in STAGE_ORDER],
        "deep": deep,
        "wide": wide,
        "dominant_earliest_stage": dominant,
        "revival_family": (
            "query_and_candidate_generation"
            if dominant == FailureStage.CANDIDATE_GENERATION_MISS.value
            else "unresolved"
        ),
        "allocator_architecture": "not_licensed_before_external_test",
        "p2_v1_mutation": "forbidden",
        "close_issue": False,
        "close_reason": (
            "Offline 390-task positivity cannot close #279. External Wide matched "
            "campaign is not yet executed; Deep bounded probe hit rate is 0.000."
        ),
    }
