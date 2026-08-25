"""Execution tests for the P2 frozen offline baselines, ORION and ablations."""

from __future__ import annotations

import functools
import json
from pathlib import Path

import pytest

from orion.study.p2.cases import CaseFamily, build_tasks
from orion.study.p2.corpus import build_world
from orion.study.p2.offline_systems import (
    ABLATIONS,
    ALL_SYSTEMS,
    BASELINES,
    EXPLORATORY_BASELINES,
    ORION_FULL,
    system_by_id,
)
from orion.study.p2.runner import execute

SEED = 20260816
MANIFEST_HASH = "0" * 64
PROTOCOL = Path("papers/paper-02-open-world-scientific-discovery/protocol/PROTOCOL_V1.json")


@functools.cache
def _suite():
    """Build the frozen world once per session.

    `build_world` + `build_tasks` costs ~4s and is called by every helper below,
    18 times across this module, for about 70s of pure repetition. It is
    deterministic on SEED, `world` and every task are frozen dataclasses, and
    `build_tasks` returns a tuple, so there is nothing a test could mutate to leak
    state into the next one. Caching changes timing only.
    """

    world = build_world(SEED)
    return world, build_tasks(world)


def _outcome(system_id: str, family: CaseFamily, *, topic_fragment: str | None = None):
    world, tasks = _suite()
    matches = [task for task in tasks if task.case_family is family]
    if topic_fragment is not None:
        matches = [task for task in matches if topic_fragment in task.task_id]
    assert matches
    return execute(
        system_by_id(system_id),
        world,
        matches[0],
        seed=1,
        run_manifest_hash=MANIFEST_HASH,
    )


def test_confirmatory_system_ids_match_the_frozen_protocol_exactly() -> None:
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert [system.system_id for system in BASELINES] == protocol["baselines"]
    assert [system.system_id for system in ABLATIONS] == protocol["ablations"]
    assert ORION_FULL.system_id == "orion_full"
    assert [system.system_id for system in EXPLORATORY_BASELINES] == [
        "adaptive_multiroute_exploratory"
    ]
    assert "adaptive_multiroute_exploratory" not in protocol["baselines"]


@pytest.mark.parametrize("system", ALL_SYSTEMS, ids=lambda s: s.system_id)
def test_every_frozen_system_respects_host_budgets_and_never_emits_invalid_claims(
    system,
) -> None:
    """Every system, every task: valid claims and budgets respected.

    Parametrised over systems rather than looping over them inside one test. The
    coverage is identical -- 14 systems x 390 tasks either way -- but this was a
    single 675s test, and one test is one item to pytest-split no matter how many
    groups exist, so it set the floor on total CI time by itself. As 14 items it
    distributes across shards, and a failure now names the offending system in the
    test id rather than only inside an assertion message.
    """

    world, tasks = _suite()
    for task in tasks:
        outcome = execute(
            system,
            world,
            task,
            seed=1,
            run_manifest_hash=MANIFEST_HASH,
        )
        assert outcome.record["status"] != "INVALID", (
            system.system_id,
            task.task_id,
            outcome.record,
        )
        assert len(outcome.trace.route_trials) <= task.budget.max_route_calls
        assert len(outcome.trace.read_encounters) <= task.budget.max_reads
        assert outcome.trace.resources.query_count <= task.budget.max_route_calls
        assert outcome.trace.resources.reads <= task.budget.max_reads


def test_full_orion_beats_lexical_only_on_complete_gold_multiroute() -> None:
    orion = _outcome("orion_full", CaseFamily.COMPLETE_GOLD_MULTIROUTE)
    bm25 = _outcome("bm25_keyword", CaseFamily.COMPLETE_GOLD_MULTIROUTE)
    assert orion.record["metrics"]["complete_gold_recall"] > bm25.record["metrics"][
        "complete_gold_recall"
    ]
    assert orion.record["metrics"]["routes_used"] > bm25.record["metrics"]["routes_used"]
    assert bm25.record["failure_class"] == "premature_closure"


def test_nominal_shared_backend_independence_ablation_loses_recall() -> None:
    full = _outcome("orion_full", CaseFamily.COMPLETE_GOLD_MULTIROUTE)
    ablated = _outcome("no_route_independence_check", CaseFamily.COMPLETE_GOLD_MULTIROUTE)
    assert full.record["metrics"]["complete_gold_recall"] > ablated.record["metrics"][
        "complete_gold_recall"
    ]
    assert ablated.record["failure_class"] == "premature_closure"


def test_route_stop_must_not_be_promoted_to_task_stop() -> None:
    full = _outcome("orion_full", CaseFamily.ROUTE_EXHAUSTION)
    ablated = _outcome("route_stop_can_close_task", CaseFamily.ROUTE_EXHAUSTION)
    assert full.record["metrics"]["complete_gold_recall"] > ablated.record["metrics"][
        "complete_gold_recall"
    ]
    assert ablated.record["metrics"]["premature_task_closure"] == 1.0
    assert ablated.record["failure_class"] == "premature_closure"


def test_unavailable_route_is_censored_not_silently_empty() -> None:
    # Query diversification's correct restricted probe is not the first public
    # probe attempted, so the provider dies before that gold can be retrieved.
    full = _outcome(
        "orion_full",
        CaseFamily.UNAVAILABLE_ROUTE,
        topic_fragment="query-diversification",
    )
    ablated = _outcome(
        "no_unavailable_route_open_state",
        CaseFamily.UNAVAILABLE_ROUTE,
        topic_fragment="query-diversification",
    )
    assert full.record["status"] == "CANNOT_CHECK"
    assert full.record["metrics"]["censored_identity_count"] >= 1.0
    assert full.record["authority_flags"]["closed_task_as_complete"] is False
    assert ablated.record["status"] == "FAIL"
    assert ablated.record["failure_class"] == "premature_closure"
    assert ablated.record["authority_flags"]["closed_task_as_complete"] is True


def test_question_conditioned_ledger_preserves_legitimate_rereads() -> None:
    full = _outcome("orion_full", CaseFamily.EXTRACTION_QUESTION_SHIFT)
    ablated = _outcome(
        "no_question_conditioned_read_ledger",
        CaseFamily.EXTRACTION_QUESTION_SHIFT,
    )
    assert full.record["metrics"]["legitimate_reread_count"] > ablated.record["metrics"][
        "legitimate_reread_count"
    ]
    assert ablated.record["metrics"]["legitimate_reread_count"] >= 1.0  # revisions still count


def test_content_identity_dedup_avoids_duplicate_processing() -> None:
    full = _outcome("orion_full", CaseFamily.DUPLICATE_IDENTITY)
    ablated = _outcome("no_content_identity_dedup", CaseFamily.DUPLICATE_IDENTITY)
    assert full.record["metrics"]["duplicate_processing_count"] == 0.0
    assert ablated.record["metrics"]["duplicate_processing_count"] > 0.0
    assert ablated.record["metrics"]["duplicate_processing_rate"] > full.record["metrics"][
        "duplicate_processing_rate"
    ]


def test_coverage_diagnostic_has_no_closure_authority_in_full_system() -> None:
    full = _outcome("orion_full", CaseFamily.COMPLETE_GOLD_MULTIROUTE)
    ablated = _outcome(
        "coverage_diagnostic_controls_stopping",
        CaseFamily.COMPLETE_GOLD_MULTIROUTE,
    )
    assert full.record["metrics"]["complete_gold_recall"] > ablated.record["metrics"][
        "complete_gold_recall"
    ]
    assert ablated.record["failure_class"] == "premature_closure"
