"""Evaluator custody, stopping semantics and read-identity accounting.

`PROTOCOL_V1.access_policy` requires that "candidate outputs cannot modify
evaluator state". Python has no hard private attribute, so that guarantee has to
be *arranged* rather than declared: the session is handed a label-free index and
a gold-free config, so there is no path from anything a system holds to the
relevance rule or the answer. The hostile fixture below goes looking for one.

Fixture numbers here prove code behaviour. They are not results about any system.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from orion.study.p2.cases import DiscoveryTask, ProtectedGold
from orion.study.p2.corpus import DiscoveryRoute, DiscoveryWorld, Document
from orion.study.p2.freeze import load_suite
from orion.study.p2.gold import EvaluationInputs, evaluate
from orion.study.p2.runner import (
    BudgetedSession,
    SessionConfig,
    build_public_index,
    execute,
)
from orion.study.p2.systems import ReadClassification, StopScope, SystemReport

FIXTURE_RUN_MANIFEST_HASH = "c" * 64


@pytest.fixture(scope="module")
def suite():
    return load_suite()


def _task(suite, name: str):
    return next(item for item in suite.tasks if item.task_id == name)


# --------------------------------------------------------------------------
# Custody
# --------------------------------------------------------------------------


class Hostile:
    """Tries every mutation and every reach for the gold that Python allows."""

    system_id = "fixture-hostile"

    def __init__(self) -> None:
        self.blocked: list[str] = []
        self.reached_gold = False

    def run(self, view, session, *, seed):
        try:
            view.route_probes[0][1].append("injected")  # type: ignore[attr-defined]
        except AttributeError:
            self.blocked.append("public_view_probes_immutable")
        try:
            view.budget.max_route_calls = 10_000  # type: ignore[misc]
        except FrozenInstanceError:
            self.blocked.append("budget_frozen")

        outcome = session.query(
            DiscoveryRoute.LEXICAL.value, view.probes_for(DiscoveryRoute.LEXICAL)[0]
        )
        try:
            outcome.records.append("forged")  # type: ignore[attr-defined]
        except AttributeError:
            self.blocked.append("route_records_immutable")
        try:
            session.route_events.append("forged")  # type: ignore[attr-defined]
        except AttributeError:
            self.blocked.append("event_log_immutable")

        # Reaching for the answer through whatever the session happens to hold.
        for value in vars(session).values():
            if isinstance(value, (DiscoveryWorld, DiscoveryTask, ProtectedGold, Document)):
                self.reached_gold = True
            if hasattr(value, "protected_gold") or hasattr(value, "concept_tags"):
                self.reached_gold = True

        return SystemReport(
            tuple(sorted({item.content_identity for item in outcome.records})), False
        )


def test_a_hostile_system_cannot_mutate_what_it_is_handed(suite) -> None:
    system = Hostile()
    task = _task(suite, "p2-measurement-invariance-complete-gold-multiroute")
    before = task.protected_gold

    outcome = execute(
        system, suite.world, task, seed=1, run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH
    )

    assert set(system.blocked) == {
        "public_view_probes_immutable",
        "budget_frozen",
        "route_records_immutable",
        "event_log_immutable",
    }
    assert task.protected_gold == before, "the frozen task survived the run unchanged"
    assert task.budget.max_route_calls == 12, "the budget it tried to raise is intact"
    assert outcome.record["status"] in {"PASS", "FAIL", "CANNOT_CHECK", "INVALID"}


def test_the_session_holds_no_path_to_the_gold_or_the_relevance_rule(suite) -> None:
    """Custody arranged, not asserted: what a system can reach carries no labels."""

    system = Hostile()
    task = _task(suite, "p2-measurement-invariance-complete-gold-multiroute")
    execute(system, suite.world, task, seed=1, run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH)
    assert system.reached_gold is False

    session = BudgetedSession(build_public_index(suite.world), SessionConfig.from_task(task))
    outcome = session.query(
        DiscoveryRoute.LEXICAL.value, task.public_view.probes_for(DiscoveryRoute.LEXICAL)[0]
    )
    assert outcome.records
    for record in outcome.records:
        assert not hasattr(record, "concept_tags")


def test_gold_and_evaluation_structures_are_frozen(suite) -> None:
    task = _task(suite, "p2-measurement-invariance-complete-gold-multiroute")
    with pytest.raises(FrozenInstanceError):
        task.protected_gold.gold_doc_ids = ()  # type: ignore[misc]
    with pytest.raises(AttributeError):
        task.protected_gold.gold_doc_ids.append("x")  # type: ignore[attr-defined]

    outcome = execute(
        Hostile(), suite.world, task, seed=1, run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH
    )
    evaluation = evaluate(EvaluationInputs(suite.world, task, outcome.trace))
    with pytest.raises(FrozenInstanceError):
        evaluation.status = "PASS"  # type: ignore[misc]
    with pytest.raises(AttributeError):
        evaluation.discovered_gold_identities.append("x")  # type: ignore[attr-defined]


class Fabricator:
    """Names plausible identifiers it never retrieved."""

    system_id = "fixture-fabricator"

    def run(self, view, session, *, seed):
        session.query(DiscoveryRoute.LEXICAL.value, view.probes_for(DiscoveryRoute.LEXICAL)[0])
        return SystemReport(
            ("work:measurement-invariance:sem-a", "work:measurement-invariance:restricted-a"),
            True,
        )


def test_claims_beyond_retrieval_are_invalid_not_credited(suite) -> None:
    """Otherwise a system could score by guessing identifiers it never found."""

    task = _task(suite, "p2-measurement-invariance-complete-gold-multiroute")
    outcome = execute(
        Fabricator(), suite.world, task, seed=1, run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH
    )
    assert outcome.record["status"] == "INVALID"
    assert outcome.record["failure_class"] == "unsupported_claim"
    assert outcome.record["metrics"]["complete_gold_recall"] == 0.0
    assert outcome.record["authority_flags"]["claims_exceed_retrieval"] is True


# --------------------------------------------------------------------------
# Stopping semantics
# --------------------------------------------------------------------------


class SingleRoute:
    """Uses one route, then declares the whole question answered."""

    system_id = "fixture-single-route"

    def __init__(self, *, close: bool) -> None:
        self.close = close
        self.system_id = f"fixture-single-route-close-{close}"

    def run(self, view, session, *, seed):
        found: set[str] = set()
        for probe in view.probes_for(DiscoveryRoute.LEXICAL):
            outcome = session.query(DiscoveryRoute.LEXICAL.value, probe)
            found.update(item.content_identity for item in outcome.records)
        session.declare_route_stop(DiscoveryRoute.LEXICAL.value, "no_more_probes")
        return SystemReport(tuple(sorted(found)), self.close)


def test_closing_a_task_with_material_still_reachable_is_premature(suite) -> None:
    task = _task(suite, "p2-measurement-invariance-complete-gold-multiroute")
    outcome = execute(
        SingleRoute(close=True), suite.world, task, seed=1, run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH
    )
    assert outcome.record["status"] == "FAIL"
    assert outcome.record["failure_class"] == "premature_closure"
    assert outcome.record["metrics"]["premature_task_closure"] == 1.0

    task_audit = next(
        item
        for item in outcome.artifact["evaluation"]["stop_audits"]
        if item["scope"] == StopScope.TASK.value
    )
    assert task_audit["still_reachable_count"] > 0
    assert task_audit["remaining_route_calls"] > 0
    assert task_audit["premature"] is True


def test_not_claiming_completeness_is_not_premature_closure(suite) -> None:
    """No-alarm: prematurity is a property of the claim, not of stopping."""

    task = _task(suite, "p2-measurement-invariance-complete-gold-multiroute")
    outcome = execute(
        SingleRoute(close=False), suite.world, task, seed=1, run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH
    )
    assert outcome.record["metrics"]["premature_task_closure"] == 0.0
    assert outcome.record["failure_class"] != "premature_closure"


def test_a_route_stop_is_audited_against_what_that_route_could_still_reach(suite) -> None:
    """Route-stop and task-stop are judged separately, as the paper requires."""

    task = _task(suite, "p2-measurement-invariance-complete-gold-multiroute")
    outcome = execute(
        SingleRoute(close=False), suite.world, task, seed=1, run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH
    )
    route_audits = [
        item
        for item in outcome.artifact["evaluation"]["stop_audits"]
        if item["scope"] == StopScope.ROUTE.value
    ]
    assert route_audits
    audit = route_audits[0]
    assert audit["route"] == DiscoveryRoute.LEXICAL.value
    # It exhausted the lexical probes, so nothing lexical remained: stopping that
    # route was correct even though the task was nowhere near answered.
    assert audit["still_reachable_count"] == 0
    assert audit["premature"] is False


class DeadProviderChaser:
    """Spends its restricted calls badly, so the provider dies before it pays off."""

    def __init__(self, *, close: bool) -> None:
        self.close = close
        self.system_id = f"fixture-dead-provider-close-{close}"

    def run(self, view, session, *, seed):
        found: set[str] = set()
        for probe in view.probes_for(DiscoveryRoute.RESTRICTED):
            outcome = session.query(DiscoveryRoute.RESTRICTED.value, probe)
            found.update(item.content_identity for item in outcome.records)
        for probe in view.probes_for(DiscoveryRoute.LEXICAL)[:2]:
            outcome = session.query(DiscoveryRoute.LEXICAL.value, probe)
            found.update(item.content_identity for item in outcome.records)
        return SystemReport(tuple(sorted(found)), self.close)


def test_refusing_closure_over_censored_evidence_is_cannot_check(suite) -> None:
    """The safe behaviour the paper claims must not be scored as a miss."""

    task = _task(suite, "p2-measurement-invariance-unavailable-route")
    outcome = execute(
        DeadProviderChaser(close=False),
        suite.world,
        task,
        seed=1,
        run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH,
    )
    evaluation = outcome.artifact["evaluation"]
    assert evaluation["unavailable_route_events"], "the provider really did go down"
    assert evaluation["censored_identities"], "and it really did hold unreached gold"
    assert outcome.record["status"] == "CANNOT_CHECK"
    assert outcome.record["failure_class"] is None
    assert outcome.record["authority_flags"]["closed_over_censored_evidence"] is False


def test_closing_over_censored_evidence_is_a_failure(suite) -> None:
    task = _task(suite, "p2-measurement-invariance-unavailable-route")
    outcome = execute(
        DeadProviderChaser(close=True),
        suite.world,
        task,
        seed=1,
        run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH,
    )
    assert outcome.record["status"] == "FAIL"
    assert outcome.record["failure_class"] == "premature_closure"
    assert outcome.record["authority_flags"]["closed_over_censored_evidence"] is True
    assert outcome.record["metrics"]["unavailable_route_event_count"] > 0


def test_an_untouched_dead_route_censors_nothing(suite) -> None:
    """No-alarm: censoring is a property of the run, not a label on the task."""

    task = _task(suite, "p2-measurement-invariance-unavailable-route")
    outcome = execute(
        SingleRoute(close=False), suite.world, task, seed=1, run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH
    )
    evaluation = outcome.artifact["evaluation"]
    assert evaluation["unavailable_route_events"] == []
    assert evaluation["censored_identities"] == []
    assert outcome.record["status"] != "CANNOT_CHECK"


# --------------------------------------------------------------------------
# Route contribution and read identity
# --------------------------------------------------------------------------


class MultiRoute:
    """Uses the right probe on each published route, then snowballs once."""

    system_id = "fixture-multiroute"

    def run(self, view, session, *, seed):
        found: dict[str, str] = {}
        for route in (DiscoveryRoute.LEXICAL, DiscoveryRoute.SEMANTIC, DiscoveryRoute.REFORMULATION):
            probe = next(
                item for item in view.probes_for(route) if "measurement invariance" in item
                or "scalar equivalence" in item
                or "differential item" in item
            )
            outcome = session.query(route.value, probe)
            for record in outcome.records:
                found[record.content_identity] = record.doc_id
        for doc_id in sorted(set(found.values())):
            outcome = session.query(DiscoveryRoute.CITATION.value, doc_id)
            for record in outcome.records:
                found[record.content_identity] = record.doc_id
        return SystemReport(tuple(sorted(found)), False)


def test_route_contribution_separates_unique_evidence_from_echo(suite) -> None:
    """P2.H2's quantity: a route that only re-finds is diversity in name only."""

    task = _task(suite, "p2-measurement-invariance-complete-gold-multiroute")
    outcome = execute(
        MultiRoute(), suite.world, task, seed=1, run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH
    )
    contributions = {
        item["route"]: item for item in outcome.artifact["evaluation"]["route_contributions"]
    }
    lexical = contributions[DiscoveryRoute.LEXICAL.value]
    semantic = contributions[DiscoveryRoute.SEMANTIC.value]

    # The cross-listed work is reachable both ways, so it is unique to neither.
    shared = "work:measurement-invariance:multi-a"
    assert shared in lexical["relevant_identities"]
    assert shared in semantic["relevant_identities"]
    assert shared not in lexical["unique_relevant_identities"]
    assert shared not in semantic["unique_relevant_identities"]
    assert lexical["unique_relevant_identities"], "lexical still contributed something of its own"

    overlap = {
        (item["left"], item["right"]): item
        for item in outcome.artifact["evaluation"]["route_pair_overlap"]
    }
    pair = overlap[(DiscoveryRoute.LEXICAL.value, DiscoveryRoute.SEMANTIC.value)]
    assert pair["shared"] >= 1 and 0.0 < pair["jaccard"] < 1.0


def test_routes_carry_the_backend_identity_independence_turns_on(suite) -> None:
    """`assess_pair` refuses independence for a shared backend, so it must be recorded."""

    task = _task(suite, "p2-measurement-invariance-complete-gold-multiroute")
    outcome = execute(
        MultiRoute(), suite.world, task, seed=1, run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH
    )
    contributions = {
        item["route"]: item for item in outcome.artifact["evaluation"]["route_contributions"]
    }
    lexical = contributions[DiscoveryRoute.LEXICAL.value]
    reformulation = contributions[DiscoveryRoute.REFORMULATION.value]
    semantic = contributions[DiscoveryRoute.SEMANTIC.value]

    assert lexical["backend_identity"] == reformulation["backend_identity"]
    assert lexical["query_derivation_identity"] != reformulation["query_derivation_identity"]
    assert semantic["backend_identity"] != lexical["backend_identity"]


class Rereader:
    """Reads a work, its republication and its revision, then re-reads one."""

    system_id = "fixture-rereader"

    def run(self, view, session, *, seed):
        probe = next(
            item for item in view.probes_for(DiscoveryRoute.LEXICAL) if "measurement invariance" in item
        )
        lexical = session.query(DiscoveryRoute.LEXICAL.value, probe)
        semantic = session.query(
            DiscoveryRoute.SEMANTIC.value,
            next(item for item in view.probes_for(DiscoveryRoute.SEMANTIC) if "scalar" in item),
        )
        order = [
            "measurement-invariance:lex-a",
            "measurement-invariance:lex-a-mirror",
            "measurement-invariance:sem-a",
            "measurement-invariance:sem-a-v2",
            "measurement-invariance:lex-a",
        ]
        for doc_id in order:
            session.read(doc_id)
        identities = {item.content_identity for item in (*lexical.records, *semantic.records)}
        return SystemReport(tuple(sorted(identities)), False)


def test_duplicate_processing_and_legitimate_reread_are_distinguishable(suite) -> None:
    """A republication is wasted work; a revision is not. Both are re-encounters."""

    task = _task(suite, "p2-measurement-invariance-duplicate-identity")
    outcome = execute(
        Rereader(), suite.world, task, seed=1, run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH
    )
    # Indexed by position, not by document: `lex-a` is read twice, and the second
    # read is the one that matters.
    events = outcome.artifact["trace"]["read_events"]
    assert [item["doc_id"] for item in events] == [
        "measurement-invariance:lex-a",
        "measurement-invariance:lex-a-mirror",
        "measurement-invariance:sem-a",
        "measurement-invariance:sem-a-v2",
        "measurement-invariance:lex-a",
    ]
    assert [item["classification"] for item in events] == [
        ReadClassification.FIRST_READ.value,
        # Same work, same bytes, different locator — nothing new was learned.
        ReadClassification.DUPLICATE.value,
        ReadClassification.FIRST_READ.value,
        # Same work, different bytes — a revision genuinely has to be read again.
        ReadClassification.REVISION_REREAD.value,
        # The same rendition under the same question, a second time.
        ReadClassification.DUPLICATE.value,
    ]

    evaluation = outcome.artifact["evaluation"]
    assert evaluation["duplicate_processing_count"] == 2  # the mirror, and lex-a re-read
    assert evaluation["legitimate_reread_count"] == 1
    assert evaluation["first_read_count"] == 2
    assert 0.0 < outcome.record["metrics"]["duplicate_processing_rate"] < 1.0


def test_processing_pairs_are_keyed_by_work_and_question(suite) -> None:
    """The read ledger's coordinates, emitted so the next phase can bind them."""

    task = _task(suite, "p2-measurement-invariance-duplicate-identity")
    outcome = execute(
        Rereader(), suite.world, task, seed=1, run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH
    )
    pairs = outcome.artifact["evaluation"]["processing_pairs"]
    assert pairs and all({"content_identity", "extraction_question"} == set(item) for item in pairs)
    # Five reads collapse to two (work, question) pairs: the republication shares
    # a work with `lex-a` and the revision shares one with `sem-a`. Counting
    # locators would have reported five, which is the inflation the study exists
    # to detect.
    assert len(outcome.artifact["trace"]["read_events"]) == 5
    assert len(pairs) == 2
    assert len({item["extraction_question"] for item in pairs}) == 1
    assert {item["content_identity"] for item in pairs} == {
        "work:measurement-invariance:lex-a",
        "work:measurement-invariance:sem-a",
    }


class ShiftAware:
    """Reads enough to cross the frame change, then re-reads under the new question."""

    system_id = "fixture-shift-aware"

    def run(self, view, session, *, seed):
        probe = next(
            item for item in view.probes_for(DiscoveryRoute.LEXICAL) if "measurement invariance" in item
        )
        outcome = session.query(DiscoveryRoute.LEXICAL.value, probe)
        doc_ids = sorted({item.doc_id for item in outcome.records})[:4]
        first_question = session.current_extraction_question
        for doc_id in doc_ids:
            session.read(doc_id)
        second_question = session.current_extraction_question
        assert first_question != second_question, "the host advanced the frame"
        session.read(doc_ids[0])
        return SystemReport(
            tuple(sorted({item.content_identity for item in outcome.records})), False
        )


def test_a_reread_under_a_changed_question_is_legitimate(suite) -> None:
    """The read ledger's whole point: 'seen this paper' is not 'answered this question'."""

    task = _task(suite, "p2-measurement-invariance-extraction-question-shift")
    outcome = execute(
        ShiftAware(), suite.world, task, seed=1, run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH
    )
    events = outcome.artifact["trace"]["read_events"]
    assert events[-1]["classification"] == ReadClassification.NEW_QUESTION_REREAD.value
    assert events[-1]["content_identity"] == events[0]["content_identity"]
    assert events[-1]["extraction_question"] != events[0]["extraction_question"]
    assert outcome.artifact["evaluation"]["duplicate_processing_count"] == 0
    assert outcome.artifact["evaluation"]["legitimate_reread_count"] == 1


def test_the_frame_is_host_controlled_not_system_declared(suite) -> None:
    """A system cannot mint itself a new question to license a reread."""

    task = _task(suite, "p2-measurement-invariance-extraction-question-shift")
    session = BudgetedSession(build_public_index(suite.world), SessionConfig.from_task(task))
    assert session.current_extraction_question == task.extraction_questions[0]
    with pytest.raises(AttributeError):
        session.current_extraction_question = "a question of my own"  # type: ignore[misc]
