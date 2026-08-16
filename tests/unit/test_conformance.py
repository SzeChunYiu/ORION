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


def test_the_real_tree_reproduces_the_p3_annotator_finding() -> None:
    """Found by hand first, then reproduced by an independent implementation.

    P3's protocol asks for two independent annotators; the corpus carries one.
    A protocol asking for independent labels is asking for disagreement to be
    observable, and the agreement statistic cannot be recovered afterwards from
    adjudicated output because adjudication has already collapsed the
    disagreement it would measure.
    """

    findings = check_papers(pathlib.Path("papers"))
    annotator = [item for item in findings if item.requirement == "independent_annotators"]
    assert annotator, "the annotator requirement is no longer being checked at all"
    assert annotator[0].verdict is ConformanceVerdict.VIOLATED
    assert annotator[0].observed == 1


def test_a_missing_archive_is_cannot_check_not_a_violation() -> None:
    """A declared quantity with nothing to check it against is unknown, not
    wrong. Reporting it as a violation would make every unstarted paper look
    defective and get the checker switched off on its first run."""

    findings = check_papers(pathlib.Path("papers"))
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

    findings = check_papers(pathlib.Path("papers"))
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
    findings = check_papers(pathlib.Path("papers"))
    assert all(item.verdict is ConformanceVerdict.VIOLATED for item in violations(findings))
