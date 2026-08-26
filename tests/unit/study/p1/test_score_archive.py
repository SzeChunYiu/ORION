from __future__ import annotations

import json
from glob import glob

import pytest

from orion.study.p1.cases import Split, case_from_dict
from orion.study.p1.score_archive import score_archive

CASES = "papers/orion-11-recursive-epistemic-reconstruction/protocol/cases"


def _case(index: int = 0):
    path = sorted(glob(f"{CASES}/test/*.json"))[index]
    return case_from_dict(json.loads(open(path).read()), split=Split.TEST)


def _run(case, *, status="OK", trace=True, error="", system="orion_full"):
    payload = {
        "case_id": case.case_id,
        "system_id": system,
        "seed": 0,
        "status": status,
        "trace": None,
        "elapsed_seconds": 0.25,
        "suite_fingerprint": "f" * 64,
        "subject_revision": "abc1234",
        "protocol_id": "P1.hidden-formulation.v1.1",
        "budget_class": case.budget_class,
        "error": error,
    }
    if trace:
        payload["trace"] = {
            "case_id": case.case_id,
            "system_id": system,
            "seed": 0,
            "reframed": True,
            "responsibility_family": case.protected_gold.responsibility_family,
            "target_coordinates": list(case.protected_gold.target_coordinates),
            "reopened": list(case.protected_gold.dependencies_to_reopen),
            "root_solved": True,
            "abstained": False,
            "invariant_violations": [],
            "authority_violations": [],
            "max_recursion_depth": max(case.protected_gold.dependency_depth, 1),
            "resources": {
                "wallclock_seconds": 0.0,
                "model_tokens": 10,
                "tool_calls": 1,
                "search_queries": 1,
            },
            "notes": "",
        }
    return payload


def test_a_perfect_run_scores_through_the_seam() -> None:
    """The seam itself. The harness archives run records and the tables read
    scored case records; nothing converted one to the other until this module,
    so a real archive was rejected as malformed. Each side had been tested
    against its own fixtures, which is exactly why neither caught it."""

    case = _case()
    records = score_archive([_run(case)], [case])
    assert len(records) == 1
    assert records[0]["case_id"] == case.case_id
    assert records[0]["root_success"] is True


def test_an_incomplete_run_is_cannot_check_and_never_a_zero() -> None:
    """A system that could not be measured has not failed. Scoring a missing
    trace as 0 would let an outage read as a result."""

    case = _case()
    records = score_archive([_run(case, status="ERROR", trace=False, error="boom")], [case])
    assert records[0]["status"] == "CANNOT_CHECK"
    assert records[0]["root_success"] is not False


def test_the_harness_measured_time_reaches_the_score() -> None:
    """Mechanical systems report 0.0 wallclock by construction — they do no
    timed external work — so a cost frontier built on the trace alone plots
    every system at the origin. The harness measures the real figure."""

    case = _case()
    records = score_archive([_run(case)], [case])
    assert records[0]["resources"]["wallclock_seconds"] == pytest.approx(0.25)


def test_an_archived_case_absent_from_the_suite_is_refused_loudly() -> None:
    """Dropping it silently would let a mismatched suite look like a complete
    run — the archive and the suite would disagree and nothing would say so."""

    case = _case()
    stray = _run(case)
    stray["case_id"] = "p1-c999-not-in-suite"
    with pytest.raises(ValueError, match="absent from the supplied suite"):
        score_archive([stray], [case])


def test_a_record_missing_a_harness_key_is_refused() -> None:
    """The archive carries no schema tag, so shape is the only identity
    available. Requiring the full key set means a truncated or foreign file is
    refused rather than half-read into confident numbers."""

    from orion.study.p1.score_archive import _RUN_KEYS

    assert "suite_fingerprint" in _RUN_KEYS
    case = _case()
    partial = _run(case)
    del partial["suite_fingerprint"]
    with pytest.raises(KeyError):
        score_archive([partial], [case])


def test_system_role_is_derived_not_declared() -> None:
    """Roles come from the frozen system registry, so an archive cannot promote
    a baseline to subject by relabelling it."""

    from orion.study.p1.orion_system import FULL_ORION_ID

    case = _case()
    subject = score_archive([_run(case, system=FULL_ORION_ID)], [case])[0]
    baseline = score_archive([_run(case, system="static_react_tool_workflow")], [case])[0]
    assert subject["system_role"] != baseline["system_role"]


def test_the_one_command_runner_uses_the_validated_reader() -> None:
    """run_trial grew its own reader while score_archive already had one that
    checks the full harness key set. The one-command path — the one anyone
    actually uses — therefore skipped validation and would half-read a
    truncated archive into confident numbers.

    Two readers with one validated is worse than one unvalidated reader,
    because the validation exists and creates the impression it runs.
    """

    import inspect

    from orion.study.p1 import run_trial

    source = inspect.getsource(run_trial)
    assert "read_runs(archive_path)" in source
    assert "def _reload" not in source, "the second, unvalidated reader is back"
