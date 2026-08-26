"""Tests for the observation reducer and the relation detector.

Three groups, in the order that matters.

**Unit tests on synthetic views** fix the parser's and the rules' behaviour
without touching the suite, so they keep meaning while the case files are being
edited.

**Discipline tests** check the two things a reviewer would otherwise have to
take on trust: that no rule branches on a case identifier, and that the
template phrases the suite's own solvability audit measured as a perfect
hidden-shift/control separator are refused rather than merely unused.

**Suite tests** are the leak verification the task turns on. They read
``protected_gold`` — only to score, never inside a detector — and they assert
that the reduction is CLEAN under ``orion.benchmarks.degeneracy``, that the
strongest shape-only blind responder cannot beat the majority baseline, and
that detection survives replacing every resource path stem with an opaque id.

Suite-level assertions carry deliberate slack, documented at each one: the case
files are edited by another lane, so an assertion pinned to an exact count
would fail on churn rather than on a defect.
"""

from __future__ import annotations

import inspect
from collections import Counter
from pathlib import Path

import pytest

from orion.benchmarks.degeneracy import DegeneracyStatus, LabeledRecord, probe_records
from orion.core.residuals import Responsibility
from orion.study.p1 import contradiction as contradiction_module
from orion.study.p1 import observation as observation_module
from orion.study.p1.cases import HiddenShiftCase, PublicView, Split, load_cases
from orion.study.p1.contradiction import RULES, arbitrate, detect, disagreeing_pairs
from orion.study.p1.observation import (
    ObservationKind,
    bearing_from_components,
    reduce_view,
)

CASE_ROOT = Path(__file__).resolve().parents[4] / (
    "papers/orion-11-recursive-epistemic-reconstruction/protocol/cases"
)


def view(prompt: str, *resources: str, case_id: str = "synthetic-1") -> PublicView:
    return PublicView(
        case_id=case_id,
        public_prompt=prompt,
        observable_resources=tuple(resources),
        budget_class="p1_standard_v1",
    )


def fired(result, rule: str) -> bool:
    return any(finding.rule == rule for finding in result)


# --------------------------------------------------------------------------
# The reducer
# --------------------------------------------------------------------------


def test_a_quantity_carries_its_value_unit_and_source_line() -> None:
    reduction = reduce_view(view("Report it.", "obs/panel.json — the panel reads 180 ms"))
    quantities = [o for o in reduction.observations if o.value == 180.0]
    assert quantities, "the number in the resource line was not read"
    assert quantities[0].unit == "ms"
    assert quantities[0].unit_class == "duration"
    assert quantities[0].seconds == pytest.approx(0.18)
    assert quantities[0].source == "obs/panel.json"
    assert "obs/panel.json" in quantities[0].cite


def test_magnitude_words_scale_the_value_and_byte_units_do_not() -> None:
    reduction = reduce_view(
        view("Report it.", "a/b.csv — 13.6M sessions, 4.1 billion requests and 240 MB of heap")
    )
    values = {o.value for o in reduction.observations if o.value is not None}
    assert 13_600_000.0 in values
    assert 4_100_000_000.0 in values
    # `240 MB` must stay 240 with unit MB; reading `M` as a multiplier here
    # would turn a heap size into 240 million.
    assert 240.0 in values
    assert 240_000_000.0 not in values


def test_a_unit_is_only_recorded_when_the_following_token_is_one() -> None:
    reduction = reduce_view(view("Report it.", "a/b.csv — 31 readings between 352 and 359"))
    ranges = [o for o in reduction.observations if o.kind is ObservationKind.RANGE]
    assert len(ranges) == 1
    assert (ranges[0].low, ranges[0].high) == (352.0, 359.0)
    assert ranges[0].unit == "", "the word `and` was read as a unit"


def test_an_iso_date_is_not_read_as_a_numeric_range() -> None:
    reduction = reduce_view(view("Report it.", "a/b.csv — rows written on 2026-01-11"))
    assert not [o for o in reduction.observations if o.kind is ObservationKind.RANGE]


def test_a_range_takes_its_unit_from_the_tail_of_its_own_subject() -> None:
    reduction = reduce_view(view("Bearings are reported in degrees from 0 to 359."))
    ranges = [o for o in reduction.observations if o.kind is ObservationKind.RANGE]
    assert (ranges[0].low, ranges[0].high, ranges[0].unit) == (0.0, 359.0, "degrees")
    # ...and not from an unrelated noun earlier in the clause.
    other = reduce_view(view("Report it.", "a/b.csv — hour 14 holds 31 readings between 1 and 9"))
    assert [o.unit for o in other.observations if o.kind is ObservationKind.RANGE] == [""]


def test_every_clause_becomes_at_least_one_traceable_observation() -> None:
    line = "a/b.csv — scores are not comparable across days; the weights are re-normalised"
    reduction = reduce_view(view("Report it.", line))
    texts = [o.text for o in reduction.in_source("a/b.csv")]
    assert any("not comparable" in text for text in texts)
    assert any("re-normalised" in text for text in texts)


def test_a_closure_line_is_typed_as_a_closure_and_keeps_its_identifier() -> None:
    reduction = reduce_view(view("Report it.", "closure:gate-v1 — closed; gates on 99.5%"))
    closures = reduction.of_kind(ObservationKind.CLOSURE)
    assert [o.source for o in closures] == ["closure:gate-v1"]


def test_a_declared_signal_channel_is_refused_by_the_reducer() -> None:
    """The `signal:` channel was measured DEGENERATE at 1.000 and stays refused.

    The refusal is inherited from `baselines.readable_resources` rather than
    re-implemented, so the two cannot drift apart.
    """

    reduction = reduce_view(
        view("Report it.", "signal:scale_mismatch — a declared phenomenon", "a/b.csv — 41 rows")
    )
    assert all(o.source != "signal:scale_mismatch" for o in reduction.observations)
    assert any(o.source == "a/b.csv" for o in reduction.observations)


def test_the_reduction_is_deterministic() -> None:
    subject = view("Report it.", "a/b.csv — 41 of 300 runs hold an error line and are green")
    first, second = reduce_view(subject), reduce_view(subject)
    assert first.observations == second.observations


def test_line_markers_see_a_clause_the_clause_itself_cannot() -> None:
    """A counterfactual and its outcome are often split by a comma."""

    reduction = reduce_view(
        view("Report it.", "etl/nights.csv — on nights the other job did not run, it finished "
             "on time 30 times out of 30")
    )
    outcome = [o for o in reduction.in_source("etl/nights.csv") if o.has("UNCHANGED")]
    assert outcome, "the clause-local marker was not found"
    assert outcome[0].line_has("RESTORED"), "the sibling clause's outcome was invisible"


def test_bearing_from_components_is_the_arithmetic_it_claims() -> None:
    assert bearing_from_components(0.0, 1.0) == pytest.approx(0.0)
    assert bearing_from_components(1.0, 0.0) == pytest.approx(90.0)
    assert bearing_from_components(-0.4, 7.9) == pytest.approx(357.1, abs=0.1)


def test_numbers_in_returns_a_line_in_written_order_with_range_bounds() -> None:
    reduction = reduce_view(view("Report it.", "m/s.csv — 0.10 to 0.97, 0.20 to 0.93"))
    assert reduction.numbers_in("m/s.csv") == (0.1, 0.97, 0.2, 0.93)


# --------------------------------------------------------------------------
# The rules, on synthetic views
# --------------------------------------------------------------------------


def test_a_summary_outside_a_completely_counted_support_is_a_coordinate_fault() -> None:
    result = detect(
        view(
            "A tool averages 60 bearings reported in degrees from 0 to 359 and reports a mean "
            "of 181.4 degrees.",
            "site/bearings.csv — the hour holds 31 readings between 352 and 359 and 29 readings "
            "between 1 and 9",
        )
    )
    assert fired(result, "summary_outside_complete_support")
    top = next(f for f in result if f.rule == "summary_outside_complete_support")
    assert top.responsibilities == (Responsibility.REPRESENTATION,)
    assert top.citations, "a finding must name the lines it rests on"


def test_components_contradicting_a_reported_direction_is_computed_not_matched() -> None:
    result = detect(
        view(
            "For the hour it reports a mean bearing of 181.4 degrees.",
            "site/components.csv — the same instrument's mean east -0.4 m/s, mean north 7.9 m/s",
        )
    )
    assert fired(result, "components_contradict_reported_direction")
    detail = next(
        f.detail for f in result if f.rule == "components_contradict_reported_direction"
    )
    assert "357.1" in detail


def test_a_counterfactual_that_restores_and_one_that_does_not_are_opposite_relations() -> None:
    """Same parsed shape, opposite sign, opposite responsibility.

    A revert that brings the good outcome back is a run defect. A remedy that
    is applied and leaves the phenomenon standing is evidence *against* the
    environment being the cause, and points at the arrangement instead.
    """

    restored = detect(
        view(
            "Accuracy fell after a dependency bump.",
            "train/lockfile.diff — the library moves from 3.4.1 to 4.0.0",
            "train/rerun.log — pinning the library back to 3.4.1 restores 0.91",
        )
    )
    assert fired(restored, "counterfactual_restores_baseline")
    assert not fired(restored, "framing_remedy_tried_and_failed")

    persisted = detect(
        view(
            "Customers are charged twice; shorten the timeout from 30 s to 10 s.",
            "payments/timeout-trial.md — a trial at a 10 s timeout produced 63 duplicate "
            "charges, not fewer",
        )
    )
    assert fired(persisted, "framing_remedy_tried_and_failed")
    assert not fired(persisted, "counterfactual_restores_baseline")
    boundary = next(f for f in persisted if f.rule == "framing_remedy_tried_and_failed")
    assert set(boundary.responsibilities) == {
        Responsibility.INTERFACE,
        Responsibility.DECOMPOSITION,
    }


def test_a_hand_recomputation_is_not_read_as_an_environment_counterfactual() -> None:
    """Recomputing forty lines on paper is an independent measurement.

    Reading it as a restoring counterfactual would fire EXECUTION on cases
    whose defect is arithmetic, which is the expensive error class here.
    """

    result = detect(
        view(
            "The reconciler reports a gap of 1,842 currency units.",
            "ledger/spot-check.md — 40 sampled lines reconcile to the last minor unit when "
            "added by hand",
        )
    )
    assert not fired(result, "counterfactual_restores_baseline")


def test_an_absent_record_plus_a_stated_capability_is_an_evidence_gap() -> None:
    result = detect(
        view(
            "Correlate each failure with what ran before it.",
            "ci/history.parquet — 900 runs with pass or fail per test, but no record of the "
            "order used",
            "ci/runner-config.yml — order-shuffle seed recording is disabled; the runner "
            "supports enabling it",
        )
    )
    assert fired(result, "required_input_absent_but_obtainable")
    finding = next(f for f in result if f.rule == "required_input_absent_but_obtainable")
    assert finding.responsibilities == (Responsibility.EVIDENCE,)
    assert len(finding.observations) >= 2, "the pairing must cite both sides"


def test_a_capability_statement_alone_is_not_an_evidence_gap() -> None:
    """`the gateway accepts a caller-supplied reference` is a design fact."""

    result = detect(
        view(
            "Diagnose the defect.",
            "payments/gateway-docs.md — the downstream gateway accepts a caller-supplied "
            "reference and refuses a repeat within 24 hours",
        )
    )
    assert not fired(result, "required_input_absent_but_obtainable")


def test_agreement_is_measured_against_the_chance_its_own_marginal_forces() -> None:
    result = detect(
        view(
            "Report whether the label set supports the ceiling claim.",
            "labels/match.csv — 3,000 double-labelled items; the two annotators match on 88.0%",
            "labels/marginals.csv — the majority label is applied to 91% of items",
        )
    )
    assert fired(result, "agreement_barely_exceeds_chance")
    detail = next(f.detail for f in result if f.rule == "agreement_barely_exceeds_chance")
    assert "83.6%" in detail, detail


def test_a_null_control_that_reproduces_the_effect_is_a_coordinate_fault() -> None:
    result = detect(
        view(
            "Report whether displacement is supported.",
            "traffic/correlations.csv — all three pairwise correlations are negative; shuffling "
            "each column independently and re-running reproduces negative correlations of "
            "similar size",
        )
    )
    assert fired(result, "null_control_reproduces_effect")


def test_two_people_working_independently_is_not_a_null_control() -> None:
    result = detect(
        view(
            "Report how many defects the specification still holds.",
            "review/protocol.md — the two groups worked the same revision independently on the "
            "same day",
        )
    )
    assert not fired(result, "null_control_reproduces_effect")


def test_an_emitted_artefact_is_compared_against_its_stated_reference() -> None:
    """Two quoted predicates for one purpose, compared as word sets."""

    result = detect(
        view(
            "Find the defect in the checker and repair it.",
            "dq/generated.sql — the emitted predicate for the guard is `WHERE col != NULL`",
            "dq/framework-docs.md — the framework's worked example emits `IS NOT NULL` for "
            "this guard",
        )
    )
    assert fired(result, "emitted_artefact_differs_from_reference")
    finding = next(f for f in result if f.rule == "emitted_artefact_differs_from_reference")
    assert finding.responsibilities == (Responsibility.EXECUTION,)


def test_a_stated_score_band_is_paired_with_the_rate_written_after_it() -> None:
    result = detect(
        view(
            "Report whether the emitted number can be used that way.",
            "risk/buckets.csv — of rows scoring 0.30-0.35, 7.8% were fraud; of rows scoring "
            "0.90-0.95, 19.4% were fraud",
        )
    )
    assert fired(result, "stated_calibration_contradicts_use")


def test_overlapping_enumerations_bound_the_unseen_remainder() -> None:
    result = detect(
        view(
            "Report how many defects neither group logged.",
            "review/pass-a.json — group A logged 74 distinct defect ids",
            "review/pass-b.json — group B logged 61 distinct defect ids",
            "review/overlap.json — 29 defect ids appear in both lists",
        )
    )
    assert fired(result, "overlapping_lists_understate_total")
    detail = next(f.detail for f in result if f.rule == "overlapping_lists_understate_total")
    assert "156" in detail, detail


def test_an_unseparated_disagreement_names_no_responsibility() -> None:
    """The relation is real; the attribution is withheld rather than guessed."""

    result = detect(
        view(
            "Report the figure.",
            "a/one.csv — the panel reads 180 ms",
            "b/two.csv — the raw sample gives 2,310 ms",
        )
    )
    unattributed = [f for f in result if f.rule == "derivations_disagree_unattributed"]
    assert unattributed, "the disagreement was not detected at all"
    assert unattributed[0].responsibilities == ()


def test_disagreeing_pairs_ignores_quantities_with_no_shared_unit() -> None:
    """`41 charges` and `41 modules` share no unit; comparing them invents facts."""

    reduction = reduce_view(
        view("Report it.", "a/one.csv — 41 charges", "b/two.csv — 300 modules")
    )
    assert disagreeing_pairs(reduction) == ()


def test_detect_returns_every_finding_and_orders_them_by_strength() -> None:
    result = detect(
        view(
            "Diagnose the defect and specify the fix.",
            "payments/timeout-trial.md — a trial at a 10 s timeout produced 63 duplicate "
            "charges, not fewer",
            "payments/audit.csv — the reference column is NULL for every row",
            "payments/backups.md — nightly snapshots are kept 90 days and can be restored",
        )
    )
    assert len(result) >= 2, "several relations hold and all of them must be returned"
    assert list(result) == sorted(result, key=lambda f: (-f.strength, f.rule))


def test_arbitrate_lowers_strengths_and_drops_nothing() -> None:
    findings = [
        rule(reduce_view(view("Report it.", "a/b.csv — 41 rows"))) for rule in RULES
    ]
    flat = [f for group in findings for f in group]
    assert len(arbitrate(flat)) == len(flat)


# --------------------------------------------------------------------------
# Discipline
# --------------------------------------------------------------------------


def executable_sources() -> list[tuple[str, str]]:
    """Every function body in both modules, module docstrings excluded.

    The exclusion is deliberate and narrow: a module docstring that cites
    `p1-c109` as the case the whole approach was disproved on is provenance,
    not a branch. Anything that can influence a decision lives inside a
    function, and that is what is checked.
    """

    out = []
    for module in (observation_module, contradiction_module):
        for name, member in vars(module).items():
            if callable(member) and getattr(member, "__module__", "") == module.__name__:
                out.append((f"{module.__name__}.{name}", inspect.getsource(member)))
    return out


def test_no_rule_branches_on_a_case_identifier() -> None:
    """A rule that can only fire on one named case is a lookup table."""

    named = [name for name, source in executable_sources() if "p1-c" in source]
    assert not named, f"these functions name a case id: {named}"


def test_neither_module_can_reach_the_protected_gold() -> None:
    """The detector cannot see the answer even by accident."""

    for module in (observation_module, contradiction_module):
        assert "ProtectedGold" not in vars(module)
        assert "load_cases" not in vars(module)
    for banned in ("protected_gold", "ProtectedGold", "task_family", "responsibility_family"):
        offenders = [name for name, source in executable_sources() if banned in source]
        assert not offenders, f"{banned} reachable from {offenders}"


def test_the_suite_template_separator_phrases_are_refused() -> None:
    """`the team's framing is` separates hidden-shift from control 66/66.

    The suite's own solvability audit measured that, and measured `the plan is`
    and `carry out the plan` as perfect separators in the control direction.
    Reading any of them answers H2 with no comprehension, so they are kept out
    of the lexicon rather than merely unused: two prompts that differ only by
    the template sentence must reduce to the same markers.
    """

    lexicon = {phrase for phrase, _ in observation_module._MARKERS}
    for banned in ("framing is", "the plan is", "team's", "carry out the plan"):
        assert not any(banned in phrase for phrase in lexicon), banned

    framed = reduce_view(
        view("The team's framing is that this is settled. Report whether A and B differ.")
    )
    plain = reduce_view(view("Report whether A and B differ."))
    assert {m for o in framed.observations for m in o.markers} == {
        m for o in plain.observations for m in o.markers
    }


def test_every_rule_is_reachable_on_the_frozen_suite() -> None:
    """A rule that never fires anywhere is dead weight and is reported as such.

    Slack: the case files are being edited by another lane, so a small number
    of rules may be temporarily unreachable without anything being wrong.
    """

    cases = load_cases(CASE_ROOT, split=Split.PILOT) + load_cases(CASE_ROOT, split=Split.TEST)
    reductions = [reduce_view(case.public_view) for case in cases]
    dead = [
        rule.__name__
        for rule in RULES
        if not any(list(rule(reduction)) for reduction in reductions)
    ]
    assert len(dead) <= 2, f"rules that never fire: {dead}"


# --------------------------------------------------------------------------
# Leak verification on the frozen suite
# --------------------------------------------------------------------------


def suite() -> tuple[tuple[HiddenShiftCase, ...], tuple[HiddenShiftCase, ...]]:
    return (
        load_cases(CASE_ROOT, split=Split.PILOT),
        load_cases(CASE_ROOT, split=Split.TEST),
    )


def records(cases: tuple[HiddenShiftCase, ...]) -> list[LabeledRecord]:
    """Reducer output as features, gold family as the value being graded.

    Gold is read here to *score* the surface. Nothing in `observation` or
    `contradiction` can reach it.
    """

    return [
        LabeledRecord(
            record_id=case.case_id,
            features=reduce_view(case.public_view).structure_features(),
            label=case.protected_gold.responsibility_family,
        )
        for case in cases
    ]


def kind_shape(record: LabeledRecord) -> tuple[int, ...]:
    return tuple(
        int(value) for name, value in sorted(record.features.items()) if name.startswith("kind_")
    )


def nearest_neighbour(pool: list[LabeledRecord]):
    """The strongest shape-only responder: leave-one-out 1-NN on kind counts.

    It sees how many observations of each kind a case reduced to and nothing
    else — no values, no units, no subjects, no markers, no text. If the shape
    of the reduction carried the answer, this would find it.
    """

    def responder(record: LabeledRecord) -> object:
        target = kind_shape(record)
        others = [other for other in pool if other.record_id != record.record_id]
        nearest = min(
            others,
            key=lambda other: (
                sum(abs(a - b) for a, b in zip(kind_shape(other), target)),
                str(other.record_id),
            ),
        )
        return nearest.label

    return responder


def blind_responders(pool: list[LabeledRecord]):
    majority = Counter(record.label for record in pool).most_common(1)[0][0]
    return {
        "kind_histogram_1nn": nearest_neighbour(pool),
        "observation_count": lambda r: "EVIDENCE" if int(r.features["observations"]) > 30
        else "EXECUTION",
        "resource_count": lambda r: "EVIDENCE" if int(r.features["resources_read"]) > 7
        else "EXECUTION",
        "constant_majority": lambda r: majority,
    }


@pytest.mark.parametrize("split", ["POOLED", "PILOT", "TEST"])
def test_the_reduction_does_not_leak_the_responsibility(split: str) -> None:
    """The reduction's structure must not reproduce the label.

    Run pooled and on each split separately: pilot alone is a small panel where
    single-feature purity is easy to hit by chance, and reporting only the
    pooled result would hide it.
    """

    pilot, test = suite()
    cases = {"POOLED": pilot + test, "PILOT": pilot, "TEST": test}[split]
    if not cases:
        pytest.skip(f"{split} split is empty")
    pool = records(cases)
    report = probe_records(pool, surface=split, blind_responders=blind_responders(pool))
    assert report.status is DegeneracyStatus.CLEAN, [f.detail for f in report.findings]
    assert report.permits_score_as_evidence


@pytest.mark.parametrize("split", ["POOLED", "PILOT", "TEST"])
def test_a_shape_only_responder_cannot_beat_the_majority_baseline(split: str) -> None:
    """Stated as a number rather than left to the probe's margin.

    Measured on the suite as authored: 0.106 pooled, 0.056 pilot, 0.188 test,
    against a 0.167 majority baseline. The bound below allows the probe's own
    0.05 margin and nothing more.
    """

    pilot, test = suite()
    cases = {"POOLED": pilot + test, "PILOT": pilot, "TEST": test}[split]
    if not cases:
        pytest.skip(f"{split} split is empty")
    pool = records(cases)
    labels = [record.label for record in pool]
    baseline = Counter(labels).most_common(1)[0][1] / len(labels)
    responder = nearest_neighbour(pool)
    accuracy = sum(responder(record) == record.label for record in pool) / len(pool)
    assert accuracy <= baseline + 0.05, (
        f"the kind histogram alone reaches {accuracy:.3f} against a baseline of "
        f"{baseline:.3f}; the kind vocabulary is carrying the answer and must be coarsened"
    )


def anonymised(subject: PublicView) -> PublicView:
    """Every resource path stem and closure slug replaced by an opaque id."""

    lines = []
    for index, line in enumerate(subject.observable_resources):
        stem, separator, body = line.partition("—")
        opaque = (
            f"closure:k{index}" if stem.strip().lower().startswith("closure:") else f"res{index}"
        )
        lines.append(f"{opaque} {separator} {body}" if separator else opaque)
    return PublicView(
        case_id=subject.case_id,
        public_prompt=subject.public_prompt,
        observable_resources=tuple(lines),
        budget_class=subject.budget_class,
    )


def top_family(subject: PublicView) -> str | None:
    for finding in detect(subject):
        if finding.responsibilities:
            return finding.responsibilities[0].value
    return None


def test_detection_does_not_ride_the_resource_path_stems() -> None:
    """The audit's probe 2 reads stems alone and recovers a family at 1.00 precision.

    A detector that scored by reading `-trial.md` and `-proposal.diff` in the
    file names would reproduce that shortcut and look like comprehension. The
    check replaces every stem with an opaque id and requires almost all of the
    score to survive; measured, the loss is one case out of sixty-six.
    """

    pilot, test = suite()
    cases = pilot + test
    plain = sum(
        top_family(case.public_view) == case.protected_gold.responsibility_family
        for case in cases
    )
    stripped = sum(
        top_family(anonymised(case.public_view)) == case.protected_gold.responsibility_family
        for case in cases
    )
    assert plain > 0
    assert stripped >= 0.9 * plain, (
        f"{plain} correct with path stems and {stripped} without: the rules are reading file "
        "names rather than content"
    )


def test_no_negative_control_is_topped_by_a_formulation_responsibility() -> None:
    """The honesty claim the whole exercise turns on.

    On the two negative-control families the right answer is that the
    formulation is fine. A formulation responsibility ranked first there is
    worse than silence, so the count is asserted rather than reported.

    Slack: two, out of twenty-two, because the case files are in flux.
    """

    pilot, test = suite()
    surface = frozenset({"EVIDENCE", "EXECUTION"})
    controls = [
        case
        for case in pilot + test
        if case.protected_gold.responsibility_family in surface
    ]
    wrong = [
        (case.case_id, case.protected_gold.responsibility_family, top_family(case.public_view))
        for case in controls
        if top_family(case.public_view) not in surface
        and top_family(case.public_view) is not None
    ]
    assert len(wrong) <= 2, wrong


def test_the_detector_reaches_most_of_the_suite_without_wrong_answers() -> None:
    """Coverage and error rate together: silence is honest, a wrong fire is not.

    Measured on the suite as authored: 62 top-ranked correct, 3 returned inside
    a multi-responsibility finding, 1 detected but deliberately unattributed, 0
    wrong. The coverage bound absorbs case churn; the error bound does not.
    """

    pilot, test = suite()
    cases = pilot + test
    correct = in_set = wrong = 0
    for case in cases:
        gold = case.protected_gold.responsibility_family
        findings = detect(case.public_view)
        returned = {r.value for f in findings for r in f.responsibilities}
        top = top_family(case.public_view)
        if top == gold:
            correct += 1
        elif top is None:
            continue
        elif gold in returned:
            in_set += 1
        else:
            wrong += 1
    assert correct >= 0.75 * len(cases), f"{correct}/{len(cases)} top-ranked correct"
    # The headline is zero wrong. Allowing three would let the detector drift
    # into guessing while the test still passed, and the stated principle is
    # that a wrong fire costs more than silence — so the bound guards the claim
    # rather than the score.
    assert wrong <= 1, f"{wrong}/{len(cases)} wrong attributions"
    assert in_set >= 0
