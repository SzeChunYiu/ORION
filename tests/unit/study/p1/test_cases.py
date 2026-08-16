"""The frozen ORION-P1 hidden-shift case suite must earn the right to be scored.

A benchmark that leaks its own answer produces a number, and the number means
nothing. These tests are the leak audit, not a smoke test: they load the frozen
suite from disk, assert the contract the protocol depends on, and run the
degeneracy probe over the panel as a whole. If the probe stops returning CLEAN,
the suite is at fault and the suite is what gets fixed.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import replace
from pathlib import Path

import pytest

from orion.benchmarks.degeneracy import DegeneracyStatus, LabeledRecord, probe_records
from orion.study.p1.cases import (
    AdjudicationStatus,
    HiddenShiftCase,
    Split,
    TaskFamily,
    load_cases,
    suite_fingerprint,
)

CASES_ROOT = (
    Path(__file__).resolve().parents[4]
    / "papers"
    / "paper-01-recursive-epistemic-reconstruction"
    / "protocol"
    / "cases"
)

CONTROLS = {TaskFamily.EVIDENCE_ONLY_CONTROL, TaskFamily.EXECUTION_ONLY_CONTROL}
PER_FAMILY = {Split.PILOT: 3, Split.TEST: 8}
FAMILY_ORDER = tuple(family.value for family in TaskFamily)

_TOKEN = re.compile(r"[a-z0-9]+")

# `only` is a structural adverb inside two frozen family names
# (`evidence_only_negative_control`, `execution_only_negative_control`). It
# carries no information about which family a case belongs to, so banning it from
# 22 prompts would police English rather than protect the label. Every other gold
# token, including every axis and target word, is banned outright.
DECLARED_STOPWORDS = frozenset({"only"})


def tokens(text: str) -> set[str]:
    return set(_TOKEN.findall(text.lower().replace("-", " ").replace("_", " ")))


def gold_vocabulary(case: HiddenShiftCase) -> set[str]:
    """Every word a solver would have to be told to answer this case for free."""

    raw: set[str] = set()
    for text in (
        case.task_family.value,
        case.protected_gold.responsibility_family,
        *case.protected_gold.target_coordinates,
    ):
        raw |= tokens(text)
    return {word for word in raw if len(word) >= 3 and word.isalpha()} - DECLARED_STOPWORDS


@pytest.fixture(scope="module")
def suites() -> dict[Split, tuple[HiddenShiftCase, ...]]:
    return {split: load_cases(CASES_ROOT, split=split) for split in Split}


# --------------------------------------------------------------------------- #
# the suite exists, loads, and is the size the protocol declares
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("split", list(Split))
def test_every_case_loads_and_validates(suites, split) -> None:
    """`load_cases` runs `__post_init__` on each file, so loading is validating.

    The count is asserted because `load_cases` returns an empty tuple for a
    missing directory: without it, a wrong path would read as a passing test.
    """

    cases = suites[split]
    assert len(cases) == PER_FAMILY[split] * len(TaskFamily)
    assert all(case.split is split for case in cases)
    assert len({case.case_id for case in cases}) == len(cases)


@pytest.mark.parametrize("split", list(Split))
def test_family_counts_are_exactly_as_specified(suites, split) -> None:
    counts = Counter(case.task_family for case in suites[split])
    assert counts == {family: PER_FAMILY[split] for family in TaskFamily}


@pytest.mark.parametrize("split", list(Split))
def test_the_whole_suite_is_mechanical_gold(suites, split) -> None:
    """The two human-adjudicated families are out of scope and stay open."""

    assert all(
        case.adjudication_status is AdjudicationStatus.MECHANICAL_GOLD
        for case in suites[split]
    )


@pytest.mark.parametrize("split", list(Split))
def test_budget_class_is_constant_across_the_suite(suites, split) -> None:
    """`budget_class` is public via `PublicView`.

    Any per-family variation would let a system read the family straight off the
    public view, which the protocol's `hidden_labels` policy forbids.
    """

    assert {case.budget_class for case in suites[split]} == {"p1_standard_v1"}


# --------------------------------------------------------------------------- #
# the gold contract each family carries
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("split", list(Split))
def test_hidden_shift_cases_carry_a_typed_reframe_and_a_reopen_set(suites, split) -> None:
    shifts = [c for c in suites[split] if c.task_family not in CONTROLS]
    assert len(shifts) == PER_FAMILY[split] * 4
    for case in shifts:
        gold = case.protected_gold
        assert gold.reframe_required
        assert len(gold.target_coordinates) == 2, case.case_id
        axis, target = gold.target_coordinates
        assert axis.split(".")[0] in {"W", "M"}, case.case_id
        assert ":" in target, case.case_id
        assert gold.dependencies_to_reopen, case.case_id
        assert 1 <= gold.dependency_depth <= 3, case.case_id
        assert gold.root_success_rubric.strip()


@pytest.mark.parametrize("split", list(Split))
def test_every_hidden_shift_family_spans_all_three_dependency_depths(suites, split) -> None:
    """H3 analyses reopening *by depth*; a family stuck at one depth measures nothing."""

    for family in set(TaskFamily) - CONTROLS:
        depths = {
            case.protected_gold.dependency_depth
            for case in suites[split]
            if case.task_family is family
        }
        assert depths == {1, 2, 3}, (family, depths)


@pytest.mark.parametrize("split", list(Split))
def test_negative_controls_require_no_reframe_and_no_reopen(suites, split) -> None:
    controls = [c for c in suites[split] if c.task_family in CONTROLS]
    assert len(controls) == PER_FAMILY[split] * 2
    for case in controls:
        gold = case.protected_gold
        assert not gold.reframe_required
        assert gold.target_coordinates == ()
        assert gold.dependencies_to_reopen == ()
        assert gold.dependency_depth == 0
        assert gold.responsibility_family in {"EVIDENCE", "EXECUTION"}


@pytest.mark.parametrize("split", list(Split))
def test_reopen_targets_are_visible_in_the_public_view(suites, split) -> None:
    """A reopen target no system can see makes reopen recall unmeasurable.

    Every dependency is named in the case's own `observable_resources`, so a
    system can answer in the same namespace the gold is scored in.
    """

    for case in suites[split]:
        blob = " ".join(case.observable_resources)
        for dependency in case.protected_gold.dependencies_to_reopen:
            assert dependency.startswith("closure:"), case.case_id
            assert dependency in blob, (case.case_id, dependency)


def named_closures(case: HiddenShiftCase) -> set[str]:
    return set(re.findall(r"(closure:[a-z0-9-]+)", " ".join(case.observable_resources)))


def reopen_f1(reopened: set[str], gold: tuple[str, ...]) -> float:
    if not gold or not reopened:
        return 0.0
    hits = len(reopened & set(gold))
    if not hits:
        return 0.0
    precision, recall = hits / len(reopened), hits / len(gold)
    return 2 * precision * recall / (precision + recall)


@pytest.mark.parametrize("split", list(Split))
def test_every_hidden_shift_case_carries_a_closure_that_must_survive(suites, split) -> None:
    """Reopen precision has to have something to lose, or H3 is unfalsifiable.

    If every closure a case names is also a gold dependency, then reopening
    everything is exactly right, and `full_reset_instead_of_dependency_reopen`
    cannot be distinguished from dependency-directed reopening. Each hidden-shift
    case therefore names at least one closed conclusion that does NOT rest on the
    formulation under revision and must be left alone.
    """

    for case in suites[split]:
        if case.task_family in CONTROLS:
            continue
        survivors = named_closures(case) - set(case.protected_gold.dependencies_to_reopen)
        assert survivors, case.case_id


@pytest.mark.parametrize("split", list(Split))
def test_reopening_everything_is_punished_on_every_hidden_shift_case(suites, split) -> None:
    """The discriminating cell H3 needs, asserted as the ablation would score it.

    A full-reset policy reopens every closure the case names. Scored against
    gold, it must lose precision on every single case — otherwise the ablation
    ties full ORION for free and the comparison measures nothing.
    """

    for case in suites[split]:
        if case.task_family in CONTROLS:
            continue
        gold = case.protected_gold.dependencies_to_reopen
        full_reset = reopen_f1(named_closures(case), gold)
        directed = reopen_f1(set(gold), gold)
        assert directed == 1.0, case.case_id
        assert full_reset < 1.0, case.case_id


@pytest.mark.parametrize("split", list(Split))
def test_a_control_punishes_reopening_anything_at_all(suites, split) -> None:
    """Controls carry closures too, and the correct reopen set is still empty.

    They are listed so that the presence of a `closure:` line, the resource count
    and the resource bulk carry no information about the family. A system that
    reopens on merely seeing one is wrong here, which is what H2 should punish.
    """

    carriers = 0
    for case in suites[split]:
        if case.task_family not in CONTROLS:
            continue
        assert case.protected_gold.dependencies_to_reopen == ()
        carriers += bool(named_closures(case))
    assert carriers == PER_FAMILY[split] * 2


@pytest.mark.parametrize("split", list(Split))
def test_closure_lines_are_unique_within_a_case(suites, split) -> None:
    for case in suites[split]:
        listed = [
            resource.split(" ", 1)[0]
            for resource in case.observable_resources
            if resource.startswith("closure:")
        ]
        assert len(listed) == len(set(listed)), case.case_id


@pytest.mark.parametrize("split", list(Split))
def test_every_case_carries_resources_and_a_rubric(suites, split) -> None:
    """`case_from_dict` reads `observable_resources` with `.get`.

    A file missing the key would load to an empty tuple and pass every other
    test here, since the reopen check iterates a control's empty dependency list
    and the rubric is otherwise only asserted on the hidden-shift half.
    """

    for case in suites[split]:
        assert case.observable_resources, case.case_id
        assert case.protected_gold.root_success_rubric.strip(), case.case_id
        assert case.protected_gold.responsibility_family.strip(), case.case_id


@pytest.mark.parametrize("split", list(Split))
def test_every_case_declares_constructed_provenance(suites, split) -> None:
    """These are authored benchmark cases, not empirical findings, and say so."""

    for case in suites[split]:
        assert "CONSTRUCTED_FOR_ORION_P1" in case.source_provenance, case.case_id


# --------------------------------------------------------------------------- #
# the gold vocabulary never reaches the public view
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("split", list(Split))
def test_no_case_states_its_own_gold_vocabulary(suites, split) -> None:
    """Checked over the loaded suite, every case, not a spot check.

    The public view is `case_id`, `public_prompt` and `observable_resources`. The
    gold cause must be inferable from the phenomena described there; naming it is
    handing over the answer. `__post_init__` already refuses an id that names its
    own family, which is the narrower half of this.
    """

    offenders: list[tuple[str, list[str]]] = []
    for case in suites[split]:
        banned = gold_vocabulary(case)
        public = " ".join((case.case_id, case.public_prompt, *case.observable_resources))
        leaked = sorted(banned & tokens(public))
        if leaked:
            offenders.append((case.case_id, leaked))
    assert offenders == []


def test_the_gold_vocabulary_check_detects_a_planted_leak(suites) -> None:
    """Assert the alarm fires, or the clean run above proves nothing.

    A checker only ever seen passing has not been shown to work. This plants the
    exact failure the suite is built to avoid and requires it to be caught.
    """

    case = next(c for c in suites[Split.TEST] if c.task_family not in CONTROLS)
    banned = gold_vocabulary(case)
    assert banned, case.case_id

    word = sorted(banned)[0]
    leaked = replace(case, public_prompt=f"{case.public_prompt} Consider {word}.")
    assert word in tokens(leaked.public_prompt) & gold_vocabulary(leaked)

    in_resource = replace(case, observable_resources=(*case.observable_resources, f"n.md {word}"))
    public = " ".join((in_resource.case_id, in_resource.public_prompt, *in_resource.observable_resources))
    assert word in tokens(public) & gold_vocabulary(in_resource)


# --------------------------------------------------------------------------- #
# fingerprint stability
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("split", list(Split))
def test_suite_fingerprint_is_stable_across_two_loads(suites, split) -> None:
    """`dataset_revisions` is unbound until a fingerprint is written into it.

    A fingerprint that moved between loads could not bind anything.
    """

    first = suite_fingerprint(load_cases(CASES_ROOT, split=split))
    second = suite_fingerprint(load_cases(CASES_ROOT, split=split))
    assert first == second == suite_fingerprint(suites[split])
    assert len(first) == 64


@pytest.mark.parametrize("split", list(Split))
def test_suite_fingerprint_changes_when_a_gold_label_changes(suites, split) -> None:
    """The fingerprint binds the gold, not merely the public text.

    `root_success_rubric` is deliberately not probed here: `suite_fingerprint`
    does not hash it, so mutating it would assert nothing about the binding.
    """

    cases = suites[split]
    baseline = suite_fingerprint(cases)
    case = next(c for c in cases if c.task_family not in CONTROLS)

    other_responsibility = replace(
        case,
        protected_gold=replace(case.protected_gold, responsibility_family="ROUTING"),
    )
    deeper = replace(
        case,
        protected_gold=replace(
            case.protected_gold, dependency_depth=case.protected_gold.dependency_depth + 1
        ),
    )
    retargeted = replace(
        case,
        protected_gold=replace(
            case.protected_gold,
            target_coordinates=(case.protected_gold.target_coordinates[0], "parent_domain:other"),
        ),
    )
    rest = tuple(c for c in cases if c.case_id != case.case_id)
    for mutated in (other_responsibility, deeper, retargeted):
        assert suite_fingerprint((*rest, mutated)) != baseline


# --------------------------------------------------------------------------- #
# the degeneracy probe over the whole panel
# --------------------------------------------------------------------------- #


def _records(cases: tuple[HiddenShiftCase, ...]) -> list[LabeledRecord]:
    return [
        LabeledRecord(
            record_id=case.case_id,
            features={
                "case_id": case.case_id,
                "prompt_len": len(case.public_prompt),
                "n_resources": len(case.observable_resources),
            },
            label=case.task_family.value,
        )
        for case in cases
    ]


def _id_only_responders(cases: tuple[HiddenShiftCase, ...]) -> dict:
    """Responders that read the case id and nothing else.

    These are the real leak vectors for an opaque sequential id: families
    assigned in blocks, in a repeating cycle, or keyed off the numeric suffix.
    A hash-based guesser is deliberately not used — on six balanced classes it
    clears the probe's margin by luck often enough to make the assertion a
    coin toss rather than a check.
    """

    position = {cid: i for i, cid in enumerate(sorted(c.case_id for c in cases))}
    block = max(len(cases) // len(FAMILY_ORDER), 1)

    def suffix(case_id: str) -> int:
        return int(re.search(r"(\d+)$", case_id).group(1))

    return {
        "constant_first_family": lambda r: FAMILY_ORDER[0],
        "id_sorted_position_block": lambda r: FAMILY_ORDER[
            min(position[r.features["case_id"]] // block, len(FAMILY_ORDER) - 1)
        ],
        "id_sorted_position_cycle": lambda r: FAMILY_ORDER[
            position[r.features["case_id"]] % len(FAMILY_ORDER)
        ],
        "id_numeric_suffix_mod": lambda r: FAMILY_ORDER[
            suffix(r.features["case_id"]) % len(FAMILY_ORDER)
        ],
        "id_numeric_suffix_parity": lambda r: FAMILY_ORDER[suffix(r.features["case_id"]) % 2],
    }


@pytest.mark.parametrize("split", list(Split))
def test_the_degeneracy_probe_returns_clean_over_the_suite(suites, split) -> None:
    """If this stops being CLEAN the suite leaks; fix the suite, never the probe."""

    cases = suites[split]
    report = probe_records(
        _records(cases),
        surface=f"orion-p1-hidden-shift-{split.value.lower()}",
        blind_responders=_id_only_responders(cases),
    )
    assert report.status is DegeneracyStatus.CLEAN, [f.detail for f in report.findings]
    assert report.permits_score_as_evidence
    assert report.records_probed == len(cases)


@pytest.mark.parametrize("split", list(Split))
def test_a_blind_responder_reading_the_id_cannot_beat_the_majority_baseline(
    suites, split
) -> None:
    """Stated directly rather than left implicit in the probe's margin."""

    cases = suites[split]
    labels = [case.task_family.value for case in cases]
    baseline = Counter(labels).most_common(1)[0][1] / len(labels)
    records = _records(cases)
    for name, responder in _id_only_responders(cases).items():
        hits = sum(responder(record) == label for record, label in zip(records, labels))
        assert hits / len(records) <= baseline, (split, name, hits, baseline)


def test_the_probe_catches_a_public_field_that_determines_the_family(suites) -> None:
    """The no-alarm result above is only meaningful if the alarm can fire.

    This is the concrete proposal the suite refuses: one extra public resource
    naming the phenomenon, one token per responsibility. It leaks whether or not
    the phenomenon-to-responsibility table is stored inside the case.
    """

    cases = suites[Split.TEST]
    signal = {
        "SEARCH": "signal:response-explodes-near-limit",
        "REPRESENTATION": "signal:two-forms-disagree",
        "DECOMPOSITION": "signal:parts-pass-whole-fails",
        "INTERFACE": "signal:accepted-then-lost",
        "MEASUREMENT": "signal:summary-hides-shape",
        "EVALUATOR": "signal:reviewers-disagree",
        "EVIDENCE": "signal:unsourced-figure",
        "EXECUTION": "signal:run-aborts",
    }
    leaky = [
        LabeledRecord(
            record_id=record.record_id,
            features={**record.features, "signal": signal[case.protected_gold.responsibility_family]},
            label=record.label,
        )
        for record, case in zip(_records(cases), cases)
    ]
    lookup = {rec.features["signal"]: rec.label for rec in leaky}
    report = probe_records(
        leaky, blind_responders={"signal_lookup": lambda r: lookup[r.features["signal"]]}
    )
    assert report.status is DegeneracyStatus.DEGENERATE
    assert not report.permits_score_as_evidence
    assert {finding.probe for finding in report.findings} == {
        "single_feature_determines_label",
        "blind_responder_ceiling",
    }
