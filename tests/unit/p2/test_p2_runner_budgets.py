"""Budget enforcement, failure retention, and record-schema conformance.

Two properties are load-bearing here. Budgets must bind a system that does not
cooperate — enforcement that a candidate can opt out of is not enforcement. And
failures must survive: `ANALYSIS_STANDARD_V1` keeps candidate-caused failures,
timeouts and abstentions in the denominator, so a harness that drops them makes
every rate it later reports optimistic.

Numbers asserted in this file are fixture numbers proving code behaviour. They
are not results about any system.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

from orion.study.p2.corpus import DiscoveryRoute
from orion.study.p2.freeze import load_suite
from orion.study.p2.runner import (
    BudgetExhausted,
    BudgetedSession,
    SessionConfig,
    build_public_index,
    execute,
    run_suite,
    write_artifacts,
    write_records,
)
from orion.study.p2.systems import SystemReport

REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = (
    REPO_ROOT / "research" / "paper-programme-v1" / "protocols" / "RESULT_RECORD_SCHEMA_V1.json"
)
FIXTURE_RUN_MANIFEST_HASH = "b" * 64


# --------------------------------------------------------------------------
# A minimal JSON Schema check, run against the committed schema file itself
# rather than a hand-copied summary of it — a validator that drifts from the
# schema it claims to enforce is worse than none.
# --------------------------------------------------------------------------


def schema_violations(payload: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    problems: list[str] = []
    expected = schema.get("type")
    if expected is not None:
        kinds = expected if isinstance(expected, list) else [expected]
        if not any(_is_type(payload, kind) for kind in kinds):
            return [f"{path}: expected {kinds}, got {type(payload).__name__}"]
    if "const" in schema and payload != schema["const"]:
        problems.append(f"{path}: expected const {schema['const']!r}")
    if "enum" in schema and payload not in schema["enum"]:
        problems.append(f"{path}: {payload!r} not in {schema['enum']}")
    if "pattern" in schema and isinstance(payload, str):
        if not re.search(schema["pattern"], payload):
            problems.append(f"{path}: {payload!r} does not match {schema['pattern']}")
    if isinstance(payload, dict):
        for key in schema.get("required", ()):
            if key not in payload:
                problems.append(f"{path}: missing required field {key!r}")
        properties = schema.get("properties", {})
        for key, value in sorted(payload.items()):
            if key in properties:
                problems.extend(schema_violations(value, properties[key], f"{path}.{key}"))
            elif isinstance(schema.get("additionalProperties"), dict):
                problems.extend(
                    schema_violations(value, schema["additionalProperties"], f"{path}.{key}")
                )
    if isinstance(payload, list) and isinstance(schema.get("items"), dict):
        for index, item in enumerate(payload):
            problems.extend(schema_violations(item, schema["items"], f"{path}[{index}]"))
    return problems


def _is_type(value: Any, kind: str) -> bool:
    if kind == "object":
        return isinstance(value, dict)
    if kind == "array":
        return isinstance(value, list)
    if kind == "string":
        return isinstance(value, str)
    if kind == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if kind == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if kind == "boolean":
        return isinstance(value, bool)
    if kind == "null":
        return value is None
    return True


@pytest.fixture(scope="module")
def schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def suite():
    return load_suite()


def _task(suite, name: str):
    return next(item for item in suite.tasks if item.task_id == name)


# --------------------------------------------------------------------------
# Fixture systems
# --------------------------------------------------------------------------


class Runaway:
    """Queries forever and ignores refusals. Enforcement has to survive this."""

    system_id = "fixture-runaway"

    def __init__(self) -> None:
        self.attempts = 0
        self.refusals = 0

    def run(self, view, session, *, seed):
        probes = view.probes_for(DiscoveryRoute.LEXICAL)
        for _ in range(500):
            for probe in probes:
                self.attempts += 1
                try:
                    session.query(DiscoveryRoute.LEXICAL.value, probe)
                except BudgetExhausted:
                    self.refusals += 1  # swallow it and keep going
        return SystemReport(notes="never stopped voluntarily")


class Frugal:
    """Spends two calls and stops. The no-alarm case for every budget assertion."""

    system_id = "fixture-frugal"

    def run(self, view, session, *, seed):
        found: set[str] = set()
        for probe in view.probes_for(DiscoveryRoute.LEXICAL)[:2]:
            outcome = session.query(DiscoveryRoute.LEXICAL.value, probe)
            found.update(item.content_identity for item in outcome.records)
        session.declare_route_stop(DiscoveryRoute.LEXICAL.value, "enough_for_a_fixture")
        return SystemReport(tuple(sorted(found)), False, notes="frugal")


class Crasher:
    system_id = "fixture-crasher"

    def run(self, view, session, *, seed):
        session.query(DiscoveryRoute.LEXICAL.value, view.probes_for(DiscoveryRoute.LEXICAL)[0])
        raise ZeroDivisionError("candidate exploded")


class Abstainer:
    system_id = "fixture-abstainer"

    def run(self, view, session, *, seed):
        return SystemReport(abstained=True, notes="declined")


# --------------------------------------------------------------------------
# Enforcement
# --------------------------------------------------------------------------


def test_budget_stops_a_runaway_system(suite) -> None:
    system = Runaway()
    task = _task(suite, "p2-measurement-invariance-complete-gold-multiroute")
    outcome = execute(
        system, suite.world, task, seed=1, run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH
    )

    assert system.attempts > task.budget.max_route_calls, "the system really did keep asking"
    assert system.refusals > 0, "and it really was refused"
    assert outcome.record["cost"]["search_queries"] == float(task.budget.max_route_calls)
    assert outcome.trace.truncated_at_cap == "route_calls"


def test_the_session_stays_closed_once_exhausted(suite) -> None:
    """Swallowing the exception must not buy a single extra call."""

    task = _task(suite, "p2-measurement-invariance-complete-gold-multiroute")
    session = BudgetedSession(build_public_index(suite.world), SessionConfig.from_task(task))
    probe = task.public_view.probes_for(DiscoveryRoute.LEXICAL)[0]

    for _ in range(task.budget.max_route_calls):
        session.query(DiscoveryRoute.LEXICAL.value, probe)
    for _ in range(5):
        with pytest.raises(BudgetExhausted):
            session.query(DiscoveryRoute.LEXICAL.value, probe)
    # A different budget dimension is refused too: exhaustion closes the session,
    # it does not merely close one counter.
    with pytest.raises(BudgetExhausted):
        session.read(session.route_trials[0].retrieved_doc_ids[0])
    assert len(session.route_trials) == task.budget.max_route_calls


def test_a_frugal_system_is_not_flagged_as_exhausted(suite) -> None:
    """No-alarm: the enforcement above must be discriminating, not universal."""

    task = _task(suite, "p2-measurement-invariance-complete-gold-multiroute")
    outcome = execute(
        Frugal(), suite.world, task, seed=1, run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH
    )
    assert outcome.trace.truncated_at_cap == ""
    assert outcome.record["failure_class"] != "budget_exhausted"
    assert outcome.record["cost"]["search_queries"] == 2.0


def test_reads_require_prior_retrieval(suite) -> None:
    task = _task(suite, "p2-measurement-invariance-complete-gold-multiroute")
    session = BudgetedSession(build_public_index(suite.world), SessionConfig.from_task(task))
    with pytest.raises(ValueError):
        session.read("measurement-invariance:lex-a")


def test_a_citation_probe_must_be_a_retrieved_document(suite) -> None:
    """Snowballing from a seed you never held is not snowballing."""

    task = _task(suite, "p2-measurement-invariance-complete-gold-multiroute")
    session = BudgetedSession(build_public_index(suite.world), SessionConfig.from_task(task))
    outcome = session.query(DiscoveryRoute.CITATION.value, "measurement-invariance:lex-a")
    assert outcome.status.value == "ERROR"
    assert outcome.note == "citation_seed_not_retrieved"
    assert outcome.records == ()


def test_wallclock_budget_is_enforced(suite) -> None:
    task = _task(suite, "p2-measurement-invariance-complete-gold-multiroute")
    # Session start, then the first call's check, then a clock far past the ceiling.
    ticks = iter([0.0, 0.0])

    def clock() -> float:
        return next(ticks, 10_000.0)

    session = BudgetedSession(
        build_public_index(suite.world), SessionConfig.from_task(task), clock=clock
    )
    probe = task.public_view.probes_for(DiscoveryRoute.LEXICAL)[0]
    session.query(DiscoveryRoute.LEXICAL.value, probe)
    with pytest.raises(BudgetExhausted):
        session.query(DiscoveryRoute.LEXICAL.value, probe)
    assert session.exhausted_dimension == "wallclock_seconds"


# --------------------------------------------------------------------------
# Failures are outcomes
# --------------------------------------------------------------------------


def test_a_budget_exhausted_run_is_retained_as_an_outcome(suite, schema) -> None:
    task = _task(suite, "p2-measurement-invariance-complete-gold-multiroute")
    outcome = execute(
        Runaway(), suite.world, task, seed=7, run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH
    )
    assert outcome.record["status"] == "FAIL"
    assert outcome.record["failure_class"] == "budget_exhausted"
    assert schema_violations(outcome.record, schema) == []


def test_a_crashing_system_is_retained_as_an_outcome(suite, schema) -> None:
    task = _task(suite, "p2-measurement-invariance-complete-gold-multiroute")
    outcome = execute(
        Crasher(), suite.world, task, seed=3, run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH
    )
    assert outcome.record["status"] == "FAIL"
    assert outcome.record["failure_class"] == "candidate_error"
    assert outcome.trace.error_class == "ZeroDivisionError"
    # The work it managed before crashing is kept, not discarded with it.
    assert outcome.record["cost"]["search_queries"] == 1.0
    assert schema_violations(outcome.record, schema) == []


def test_an_abstention_is_an_outcome_not_missing_data(suite) -> None:
    task = _task(suite, "p2-measurement-invariance-complete-gold-multiroute")
    outcome = execute(
        Abstainer(), suite.world, task, seed=1, run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH
    )
    assert outcome.record["status"] == "CANNOT_CHECK"
    assert outcome.trace.report.abstained is True


# --------------------------------------------------------------------------
# Record shape
# --------------------------------------------------------------------------


def test_every_emitted_record_validates_against_the_committed_schema(suite, schema) -> None:
    outcomes = list(
        run_suite(
            Frugal(),
            suite.world,
            suite.tasks[:4],
            seeds=(1, 2),
            run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH,
        )
    )
    assert len(outcomes) == 8
    for outcome in outcomes:
        assert schema_violations(outcome.record, schema) == [], outcome.record["result_id"]


def test_the_schema_checker_rejects_a_malformed_record(suite, schema) -> None:
    """No-alarm validation for the validator itself."""

    task = _task(suite, "p2-measurement-invariance-complete-gold-multiroute")
    record = execute(
        Frugal(), suite.world, task, seed=1, run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH
    ).record

    assert schema_violations({**record, "status": "MAYBE"}, schema)
    assert schema_violations({**record, "paper_id": "P9"}, schema)
    assert schema_violations({**record, "raw_artifact_hash": "not-a-digest"}, schema)
    assert schema_violations({**record, "metrics": {"recall": True}}, schema), (
        "a boolean is not a number, and the schema says metrics are numbers"
    )
    assert schema_violations({key: value for key, value in record.items() if key != "seed"}, schema)


def test_metrics_are_numbers_and_structure_lives_in_the_hashed_artifact(suite) -> None:
    """The record's `metrics` object cannot carry lists, so the artifact does."""

    task = _task(suite, "p2-measurement-invariance-complete-gold-multiroute")
    outcome = execute(
        Frugal(), suite.world, task, seed=1, run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH
    )
    assert all(
        isinstance(value, (int, float)) and not isinstance(value, bool)
        for value in outcome.record["metrics"].values()
    )
    assert outcome.record["raw_artifact_hash"] == outcome.artifact_hash
    evaluation = outcome.artifact["evaluation"]
    assert isinstance(evaluation["discovered_gold_ids"], list)
    assert isinstance(evaluation["route_contributions"], list)


def test_the_task_family_stays_inside_the_frozen_protocol(suite) -> None:
    """PROTOCOL_V1 froze five families. Case structure is not a sixth."""

    protocol = json.loads(
        (
            REPO_ROOT
            / "papers"
            / "orion-12-open-world-scientific-discovery"
            / "protocol"
            / "PROTOCOL_V1.json"
        ).read_text(encoding="utf-8")
    )
    for outcome in run_suite(
        Frugal(),
        suite.world,
        suite.tasks[:3],
        seeds=(1,),
        run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH,
    ):
        assert outcome.record["task_family"] in protocol["task_families"]
        assert outcome.record["task_family"] == "offline_complete_gold"
        assert outcome.record["protocol_id"] == protocol["protocol_id"]


def test_run_manifest_hash_is_supplied_not_manufactured(suite) -> None:
    """The harness cannot mint a binding that has not been made."""

    task = _task(suite, "p2-measurement-invariance-complete-gold-multiroute")
    with pytest.raises(ValueError):
        execute(Frugal(), suite.world, task, seed=1, run_manifest_hash="UNBOUND")


def test_records_and_artifacts_write_to_disk(suite, tmp_path: Path, schema) -> None:
    outcomes = list(
        run_suite(
            Frugal(),
            suite.world,
            suite.tasks[:2],
            seeds=(1,),
            run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH,
        )
    )
    target = tmp_path / "records.jsonl"
    assert write_records(outcomes, target) == 2
    lines = target.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    for line in lines:
        assert schema_violations(json.loads(line), schema) == []

    written = write_artifacts(outcomes, tmp_path / "artifacts")
    assert len(written) == 2
    for path, outcome in zip(written, outcomes, strict=True):
        assert json.loads(path.read_text(encoding="utf-8")) == outcome.artifact


def test_repeats_are_nested_within_task_and_seeds_are_recorded(suite) -> None:
    outcomes = list(
        run_suite(
            Frugal(),
            suite.world,
            suite.tasks[:2],
            seeds=(11, 22, 33),
            run_manifest_hash=FIXTURE_RUN_MANIFEST_HASH,
        )
    )
    assert [item.record["seed"] for item in outcomes] == [11, 22, 33, 11, 22, 33]
    assert len({item.record["result_id"] for item in outcomes}) == 6
