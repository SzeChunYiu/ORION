from __future__ import annotations

import json
import pathlib

from orion.conformance import (
    ConformanceVerdict,
    check_annotator_independence,
    check_papers,
    check_stochastic_repeats,
    violations,
)

#: Resolved from this file rather than the working directory. The first version
#: used a bare relative path and passed locally only because pytest happened to
#: run from the repository root; CI runs elsewhere and every real-tree assertion
#: silently found no papers at all — which read as "the requirement is no longer
#: checked", the exact failure the checker exists to detect.
PAPERS = pathlib.Path(__file__).resolve().parents[2] / "papers"



def test_the_real_tree_reproduces_the_p3_annotator_finding() -> None:
    """Found by hand first, then reproduced by an independent implementation.

    P3's protocol asks for two independent annotators; the corpus carries one.
    A protocol asking for independent labels is asking for disagreement to be
    observable, and the agreement statistic cannot be recovered afterwards from
    adjudicated output because adjudication has already collapsed the
    disagreement it would measure.
    """

    findings = check_papers(PAPERS)
    annotator = [item for item in findings if item.requirement == "independent_annotators"]
    assert annotator, "the annotator requirement is no longer being checked at all"
    assert annotator[0].verdict is ConformanceVerdict.VIOLATED
    assert annotator[0].observed == 1


def test_a_missing_archive_is_cannot_check_not_a_violation() -> None:
    """A declared quantity with nothing to check it against is unknown, not
    wrong. Reporting it as a violation would make every unstarted paper look
    defective and get the checker switched off on its first run."""

    findings = check_papers(PAPERS)
    unrun = [
        item
        for item in findings
        if item.requirement == "stochastic_repeats" and item.observed is None
    ]
    assert unrun
    assert all(item.verdict is ConformanceVerdict.CANNOT_CHECK for item in unrun)


def test_a_satisfied_quantity_is_reported_satisfied() -> None:
    """The no-alarm case. A checker that only ever reports problems has not
    been shown to distinguish them from their absence."""

    findings = check_papers(PAPERS)
    satisfied = [item for item in findings if item.verdict is ConformanceVerdict.SATISFIED]
    assert satisfied, "nothing passes, which means the checker is not discriminating"


def test_the_annotator_alarm_fires_and_clears(tmp_path) -> None:
    """Prove both directions on constructed corpora."""

    annotations = tmp_path / "gold" / "annotations"
    annotations.mkdir(parents=True)
    (annotations / "case1.annotator-a.json").write_text("{}")
    single = check_annotator_independence(tmp_path, "PX")
    assert single is not None and single.verdict is ConformanceVerdict.VIOLATED

    (annotations / "case1.annotator-b.json").write_text("{}")
    pair = check_annotator_independence(tmp_path, "PX")
    assert pair is not None and pair.verdict is ConformanceVerdict.SATISFIED


def test_the_repeat_alarm_fires_on_a_short_archive(tmp_path) -> None:
    """A run with fewer seeds than declared is a violation, and the minimum
    across cells is what counts — one thin cell is enough, because an average
    would let a well-covered cell pay for a starved one."""

    raw = tmp_path / "results" / "raw"
    raw.mkdir(parents=True)
    lines = []
    for seed in range(5):
        lines.append(json.dumps({"case_id": "c1", "system_id": "s1", "seed": seed}))
    for seed in range(2):
        lines.append(json.dumps({"case_id": "c2", "system_id": "s1", "seed": seed}))
    (raw / "test_runs.jsonl").write_text("\n".join(lines))

    short = check_stochastic_repeats(tmp_path, "PX", 5)
    assert short is not None and short.verdict is ConformanceVerdict.VIOLATED
    assert short.observed == 2


def test_violations_filters_to_only_real_faults() -> None:
    findings = check_papers(PAPERS)
    assert all(item.verdict is ConformanceVerdict.VIOLATED for item in violations(findings))


def test_a_waived_violation_does_not_fail_the_run() -> None:
    """A permanently red check gets ignored, so a known external blocker is
    waived with its reason rather than left to redden the build forever."""

    from orion.conformance import KNOWN_VIOLATIONS

    findings = check_papers(PAPERS)
    assert ("P3", "independent_annotators") in KNOWN_VIOLATIONS
    assert violations(findings) == ()


def test_a_waiver_whose_violation_cleared_fails_the_run() -> None:
    """The half that makes waiving honest. A waiver for something now satisfied
    misdescribes the repository, so it fails — which forces the waiver to be
    deleted rather than left to rot into a lie about the current state.

    Same mechanism as the strict xfail that carried the template leak earlier
    today: it broke the build the moment the leak was fixed, which is what got
    the marker removed.
    """

    from orion.conformance import ConformanceFinding, stale_waivers

    satisfied_now = (
        ConformanceFinding(
            "P3", "independent_annotators", 2, 2, ConformanceVerdict.SATISFIED, "two present"
        ),
    )
    assert stale_waivers(satisfied_now) == (("P3", "independent_annotators"),)


def test_an_unchecked_requirement_is_not_a_stale_waiver() -> None:
    """A waiver for something this run never examined is not stale — it is
    simply unexercised. Failing on it would punish narrowing a run's scope."""

    from orion.conformance import stale_waivers

    assert stale_waivers(()) == ()
