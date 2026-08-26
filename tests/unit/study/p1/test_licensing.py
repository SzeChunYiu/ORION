"""The licensing relation is Paper I's only surviving claim, so it is tested as one.

``NEAREST_WORK_MATRIX_V2.md`` records that after 33 neighbouring mechanisms are
absorbed, what is left is: **only a formulation or search-universe
responsibility licenses a coordinate-specific rewrite of W or M.** Every
neighbour produces a descriptive label; none attaches a permission to it.

These tests are therefore not a smoke test of two new modules. They are the
falsifier for that sentence, and they are written so that they can fail:

* the invariant is quantified over the **whole matrix** and over a **generated
  input sweep**, not spot-checked on two entries;
* the sweep reads the grounding class **off the decision**, never off the input
  that produced it, so it cannot pass by restating the code;
* the alarm is proved to fire — a deliberately corrupted matrix must be refused
  at issue time and must fail the audit;
* the sweep asserts it actually issued mutation licences, so a mechanism that
  refused everything could not pass by being uselessly conservative.

Nothing here is calibrated against P1 gold. No test asserts an accuracy,
a success rate or any other score, and the one test that runs over the frozen
66-case suite asserts the invariant and nothing else.
"""

from __future__ import annotations

import json
from dataclasses import replace
from itertools import combinations
from pathlib import Path

import pytest

from orion.core.residuals import Responsibility
from orion.kernel.store import canonical_bytes
from orion.study.p1.cases import PublicView, Split, load_cases, suite_fingerprint
from orion.study.p1.diagnosability import (
    ALL_RESPONSIBILITIES,
    AUTHORITY_CLASS_BY_RESPONSIBILITY,
    MUTATION_BEARING_CLASSES,
    AuthorityClass,
    DiagnosabilityState,
    EvidenceItem,
    Probe,
    assess_diagnosability,
    authority_class_of,
    build_posterior,
    evidence_fingerprint,
    expected_information_gain,
    minimum_decisive_weight,
    rank_probes,
    shannon_entropy,
)
from orion.study.p1.licensing import (
    COORDINATE_BY_ACTION,
    DECISIVE_WEIGHT,
    FAIL_CLOSED_REMEDY,
    LICENSING_MATRIX,
    MUTATING_ACTIONS,
    NEGATIVE_CONTROLS,
    PROTECTED_COORDINATES,
    SUB_DECISIVE_WEIGHT,
    V2_PROBE_MENU,
    V2_SUITE_BINDINGS,
    AuditVerdict,
    EpistemicAction,
    LicenseDecision,
    RefusalReason,
    audit_licensing_matrix,
    bind_split,
    control_archive_payload,
    coordinate_of,
    invariant_violations,
    is_formulation_mutation,
    issue_license,
    matrix_fingerprint,
    protocol_version,
    run_control,
    run_controls,
    run_v2_split,
    run_v2_view,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
CASES_ROOT = (
    REPO_ROOT
    / "papers"
    / "orion-11-recursive-epistemic-reconstruction"
    / "protocol"
    / "cases"
)
PROTOCOL_JSON = (
    REPO_ROOT
    / "papers"
    / "orion-11-recursive-epistemic-reconstruction"
    / "protocol"
    / "PROTOCOL_V1.json"
)

# Pinned so that editing the permission table is a visible act. A reviewer who
# changes a row must change this line too, in the same diff, which is the whole
# point of a tamper-evident rule set.
EXPECTED_MATRIX_FINGERPRINT = (
    "5a6a5d7f53c1ae1b9764194edf267a3c597401e638e9afd26903ddb0f93c7c19"
)

SPACE_SIZE = len(ALL_RESPONSIBILITIES)
FLOOR = minimum_decisive_weight(SPACE_SIZE)


def item(
    evidence_id: str,
    *supports: Responsibility,
    weight: float = 1.0,
    source: str = "test",
) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=evidence_id, supports=supports, weight=weight, source=source
    )


@pytest.fixture(scope="module")
def suites() -> dict[Split, tuple]:
    return {split: load_cases(CASES_ROOT, split=split) for split in Split}


# --------------------------------------------------------------------------- #
# schemas and deterministic serialization
# --------------------------------------------------------------------------- #


def test_two_differently_ordered_constructions_serialize_byte_identically() -> None:
    """Determinism has to be tested across construction orders, not across calls.

    Calling ``to_payload`` twice on one object passes trivially. What actually
    breaks byte-identity is summation order over evidence and iteration order
    over a set, so the two inputs here are the same evidence set built backwards
    and with permuted support tuples.
    """

    forward = (
        item("a", Responsibility.EVIDENCE, weight=0.4),
        item("b", Responsibility.INTERFACE, Responsibility.DECOMPOSITION, weight=0.7),
        item("c", Responsibility.MEASUREMENT, weight=0.9),
    )
    backward = (
        item("c", Responsibility.MEASUREMENT, weight=0.9),
        item("b", Responsibility.DECOMPOSITION, Responsibility.INTERFACE, weight=0.7),
        item("a", Responsibility.EVIDENCE, weight=0.4),
    )
    left = assess_diagnosability(forward)
    right = assess_diagnosability(backward)
    assert canonical_bytes(left.to_payload()) == canonical_bytes(right.to_payload())
    assert evidence_fingerprint(forward) == evidence_fingerprint(backward)
    assert left.posterior is not None and right.posterior is not None
    assert left.posterior.masses == right.posterior.masses


def test_receipt_payloads_are_byte_identical_across_two_independent_runs(
    suites,
) -> None:
    first = run_v2_split(suites[Split.PILOT], split=Split.PILOT)
    second = run_v2_split(suites[Split.PILOT], split=Split.PILOT)
    assert first.to_jsonl() == second.to_jsonl()
    assert canonical_bytes(first.to_payload()) == canonical_bytes(second.to_payload())


def test_no_payload_carries_a_set_or_a_negative_zero(suites) -> None:
    """Set order is the nondeterminism that survives a same-process check.

    ``-0.0`` is the other one: two summation orders can reach it and it
    serializes differently from ``0.0``.
    """

    archive = run_v2_split(suites[Split.PILOT], split=Split.PILOT)
    payload = archive.to_payload()

    def walk(node) -> None:
        assert not isinstance(node, (set, frozenset)), node
        if isinstance(node, dict):
            for key, value in node.items():
                assert isinstance(key, str), key
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
        else:
            assert isinstance(node, (str, int, float, bool, type(None))), node

    walk(payload)
    assert "-0.0" not in json.dumps(payload)


def test_a_schema_survives_a_json_round_trip(suites) -> None:
    archive = run_v2_split(suites[Split.PILOT], split=Split.PILOT)
    for receipt in archive.receipts:
        assert json.loads(receipt.to_json()) == json.loads(
            canonical_bytes(receipt.to_payload()).decode()
        )


def test_malformed_evidence_cannot_be_constructed() -> None:
    with pytest.raises(ValueError):
        EvidenceItem(evidence_id=" ", supports=(Responsibility.EVIDENCE,), weight=1.0)
    with pytest.raises(ValueError):
        EvidenceItem(evidence_id="x", supports=(), weight=1.0)
    for weight in (-0.001, 1.001, 2.0, -1.0):
        with pytest.raises(ValueError):
            EvidenceItem(
                evidence_id="x", supports=(Responsibility.EVIDENCE,), weight=weight
            )
    with pytest.raises(ValueError):
        EvidenceItem(
            evidence_id="x",
            supports=(Responsibility.EVIDENCE,),
            weight=0.5,
            source="  ",
        )


def test_a_probe_cannot_report_outside_its_declared_reach() -> None:
    probe = Probe(probe_id="p", discriminates=(Responsibility.MEASUREMENT,))
    assert probe.observe(Responsibility.MEASUREMENT) is not None
    assert probe.observe(None) is None
    with pytest.raises(ValueError):
        probe.observe(Responsibility.REPRESENTATION)
    for reliability in (0.0, -0.1, 1.5):
        with pytest.raises(ValueError):
            Probe(probe_id="p", reliability=reliability)


# --------------------------------------------------------------------------- #
# the tables are total — no permissive default anywhere
# --------------------------------------------------------------------------- #


def test_every_table_is_total_over_its_key_type() -> None:
    """A member added later must not fall into a default.

    The authority table is the one that matters: an unclassified responsibility
    with a permissive default is exactly how an evidence diagnosis would acquire
    a rewrite licence.
    """

    assert set(AUTHORITY_CLASS_BY_RESPONSIBILITY) == set(Responsibility)
    assert set(LICENSING_MATRIX) == set(Responsibility)
    assert set(COORDINATE_BY_ACTION) == set(EpistemicAction)
    for responsibility in Responsibility:
        assert isinstance(authority_class_of(responsibility), AuthorityClass)


def test_every_authority_class_is_populated() -> None:
    """A class nobody maps to would make the invariant vacuous for that class."""

    seen = set(AUTHORITY_CLASS_BY_RESPONSIBILITY.values())
    assert seen == set(AuthorityClass)


def test_the_authority_classification_itself_is_pinned() -> None:
    """The one assumption the property test cannot check from the inside.

    Every other test here quantifies over *authority classes*. If EVIDENCE were
    reclassified as FORMULATION, all of them would keep passing while the claim
    they exist to defend became false — the invariant would be satisfied by a
    relabelling rather than by a rule. So the classification is written out in
    full, once, and a reclassification has to be argued for in a diff.
    """

    assert AUTHORITY_CLASS_BY_RESPONSIBILITY == {
        Responsibility.QUESTION: AuthorityClass.FORMULATION,
        Responsibility.REPRESENTATION: AuthorityClass.FORMULATION,
        Responsibility.DECOMPOSITION: AuthorityClass.FORMULATION,
        Responsibility.INTERFACE: AuthorityClass.FORMULATION,
        Responsibility.MEASUREMENT: AuthorityClass.FORMULATION,
        Responsibility.EVALUATOR: AuthorityClass.FORMULATION,
        Responsibility.SEARCH: AuthorityClass.SEARCH_UNIVERSE,
        Responsibility.ROUTING: AuthorityClass.SEARCH_UNIVERSE,
        Responsibility.METHOD: AuthorityClass.METHOD,
        Responsibility.EVIDENCE: AuthorityClass.EVIDENCE,
        Responsibility.EXECUTION: AuthorityClass.EXECUTION,
    }
    assert MUTATION_BEARING_CLASSES == frozenset(
        {AuthorityClass.FORMULATION, AuthorityClass.SEARCH_UNIVERSE}
    )
    assert AuthorityClass.EVIDENCE not in MUTATION_BEARING_CLASSES
    assert AuthorityClass.EXECUTION not in MUTATION_BEARING_CLASSES
    assert AuthorityClass.METHOD not in MUTATION_BEARING_CLASSES


# --------------------------------------------------------------------------- #
# THE INVARIANT — static, over every (class, action) pair in the matrix
# --------------------------------------------------------------------------- #


def test_no_evidence_or_execution_row_licenses_a_formulation_mutation() -> None:
    """Paper I's claim, quantified over the whole matrix.

    Not a spot check: every responsibility crossed with every epistemic action,
    with the mutating-ness of the action derived from its coordinate namespace
    rather than from a hand-kept list that could drift.
    """

    checked = 0
    for responsibility in Responsibility:
        authority = authority_class_of(responsibility)
        for action in EpistemicAction:
            checked += 1
            if action not in LICENSING_MATRIX[responsibility]:
                continue
            if not is_formulation_mutation(action):
                continue
            assert authority in MUTATION_BEARING_CLASSES, (
                f"{responsibility.value} ({authority.value}) licenses "
                f"{action.value} ({coordinate_of(action)}), which rewrites W or M"
            )
    assert checked == len(Responsibility) * len(EpistemicAction)
    # And the two classes the claim names explicitly, stated directly.
    for responsibility in (Responsibility.EVIDENCE, Responsibility.EXECUTION):
        assert not (set(LICENSING_MATRIX[responsibility]) & set(MUTATING_ACTIONS))


def test_a_mutation_licence_names_exactly_one_coordinate() -> None:
    """"Coordinate-specific" is half the claim and is testable on its own."""

    for responsibility in Responsibility:
        mutating = [
            action
            for action in LICENSING_MATRIX[responsibility]
            if is_formulation_mutation(action)
        ]
        assert len(mutating) <= 1, (responsibility, mutating)
        authority = authority_class_of(responsibility)
        if authority in MUTATION_BEARING_CLASSES:
            assert len(mutating) == 1, responsibility


def test_no_row_reaches_the_protected_method_coordinate() -> None:
    for responsibility in Responsibility:
        for action in LICENSING_MATRIX[responsibility]:
            assert coordinate_of(action) not in PROTECTED_COORDINATES


def test_the_mutating_action_set_is_derived_and_non_empty() -> None:
    assert MUTATING_ACTIONS
    for action in EpistemicAction:
        coordinate = coordinate_of(action)
        assert is_formulation_mutation(action) == coordinate.startswith(
            ("FRAME.", "W.", "M.")
        )
    assert not is_formulation_mutation(EpistemicAction.REVISE_CLAIM)
    assert coordinate_of(EpistemicAction.REVISE_CLAIM).startswith("K.")


def test_the_matrix_fingerprint_ignores_dict_and_set_ordering() -> None:
    """The digest must name the rules, not the order they were written in.

    Python preserves insertion order for dicts and gives no order at all for
    frozensets, so a fingerprint that iterated either one directly would be
    stable within a process and unstable across machines — the worst possible
    failure, because it passes every test you run locally.
    """

    reordered = {
        key: frozenset(reversed(sorted(value, key=lambda a: a.value)))
        for key, value in reversed(list(LICENSING_MATRIX.items()))
    }
    assert list(reordered) != list(LICENSING_MATRIX)
    assert matrix_fingerprint(reordered) == matrix_fingerprint()


def test_the_matrix_audit_passes_and_the_rules_are_fingerprinted() -> None:
    audit = audit_licensing_matrix()
    assert audit.verdict is AuditVerdict.PASS, audit.violations
    assert audit.violations == ()
    assert audit.checked_pairs == len(Responsibility) * len(EpistemicAction)
    assert audit.fingerprint == matrix_fingerprint()
    assert audit.fingerprint == EXPECTED_MATRIX_FINGERPRINT


# --------------------------------------------------------------------------- #
# THE INVARIANT — end to end, over a generated input sweep
# --------------------------------------------------------------------------- #


def _sweep_reports():
    """Adversarial inputs, including the ones designed to break the invariant.

    Weights straddle the derived decisive floor from both sides; single- and
    two-class items; disjoint decisive pairs; caller-narrowed hypothesis spaces;
    probe outcomes; and the empty set.
    """

    weights = (0.0, 0.1, SUB_DECISIVE_WEIGHT, FLOOR, FLOOR + 1e-9, DECISIVE_WEIGHT, 1.0)
    yield assess_diagnosability(())
    for responsibility in ALL_RESPONSIBILITIES:
        for weight in weights:
            yield assess_diagnosability((item("e0", responsibility, weight=weight),))
    for first, second in combinations(ALL_RESPONSIBILITIES, 2):
        yield assess_diagnosability((item("e0", first, second, weight=1.0),))
        for weight in (SUB_DECISIVE_WEIGHT, DECISIVE_WEIGHT, 1.0):
            yield assess_diagnosability(
                (
                    item("e0", first, weight=weight),
                    item("e1", second, weight=weight),
                )
            )
            yield assess_diagnosability(
                (
                    item("e0", first, weight=1.0),
                    item("e1", second, weight=weight),
                )
            )
        # A caller narrowing the space around exactly what the evidence names.
        yield assess_diagnosability(
            (item("e0", first, weight=DECISIVE_WEIGHT),), space=(first, second)
        )
        # Accumulated sub-decisive mass outvoting a decisive observation of
        # another class. `_decisive_ids` cannot see the accumulation, so this
        # region reaches DIAGNOSABLE without ever passing through the conflict
        # branch — a distinct code path from either the single-item or the
        # disjoint-decisive-pair cases above.
        for left, right in ((first, second), (second, first)):
            yield assess_diagnosability(
                (
                    item("decisive", left, weight=DECISIVE_WEIGHT),
                    *(
                        item(f"weak{n}", right, weight=SUB_DECISIVE_WEIGHT)
                        for n in range(5)
                    ),
                )
            )
    for probe in V2_PROBE_MENU:
        for observed in probe.discriminates:
            outcome = probe.observe(observed)
            assert outcome is not None
            yield assess_diagnosability(
                (item("standing", Responsibility.EVIDENCE, weight=1.0), outcome)
            )
            yield assess_diagnosability((outcome,))


def test_the_licensing_invariant_holds_for_every_generated_input() -> None:
    """The end-to-end falsifier.

    Every generated diagnosis is crossed with every epistemic action, and the
    grounding class is read **off the returned decision**. Reading it off the
    input would make the assertion a restatement of the code under test.

    The non-vacuity assertions at the end matter as much as the invariant: a
    mechanism that refused every request would satisfy the invariant while
    testing nothing, and so would a sweep that never generated a formulation
    diagnosis.
    """

    granted_mutations = 0
    granted_total = 0
    refused_mutations = 0
    reports = 0
    for report in _sweep_reports():
        reports += 1
        for action in EpistemicAction:
            decision = issue_license(report, action)
            assert decision.action is action
            # Fail-closed advice is never a licence, and never a mutation.
            for remedy in decision.remedy:
                assert not is_formulation_mutation(remedy)
            if not decision.granted:
                assert decision.refusal is not None
                if is_formulation_mutation(action):
                    refused_mutations += 1
                continue
            granted_total += 1
            assert decision.refusal is None
            assert decision.ground_class is not None
            assert decision.ground_authority is authority_class_of(decision.ground_class)
            if decision.mutates_formulation:
                granted_mutations += 1
                assert decision.ground_authority in MUTATION_BEARING_CLASSES, decision
                assert decision.coordinate not in PROTECTED_COORDINATES
        assert invariant_violations(
            [issue_license(report, action) for action in EpistemicAction]
        ) == ()

    assert reports > 200, reports
    assert granted_total > 0
    assert granted_mutations > 0, "the sweep never exercised a granted mutation"
    assert refused_mutations > 0


def test_a_caller_cannot_narrow_the_hypothesis_space_to_manufacture_certainty() -> None:
    """The sharpest attack on the mechanism, refused before any mass is computed.

    Ask a one-sided question — "is it REPRESENTATION?" — while holding evidence
    that points at EVIDENCE, and a naive posterior returns 1.0 on
    REPRESENTATION with zero entropy. Admissibility is settled first, exactly as
    ``evaluate_hard_gates`` settles contract chronology before reading numbers.
    """

    evidence = (item("e0", Responsibility.EVIDENCE, weight=1.0),)
    narrowed = assess_diagnosability(
        evidence, space=(Responsibility.REPRESENTATION, Responsibility.MEASUREMENT)
    )
    assert narrowed.state is DiagnosabilityState.INADMISSIBLE
    assert narrowed.posterior is None
    assert any("evidence_outside_hypothesis_space" in r for r in narrowed.reasons)
    decision = issue_license(narrowed, EpistemicAction.REWRITE_REPRESENTATION)
    assert not decision.granted
    assert decision.refusal is RefusalReason.EVIDENCE_INADMISSIBLE

    single = assess_diagnosability(evidence, space=(Responsibility.EVIDENCE,))
    assert single.state is DiagnosabilityState.INADMISSIBLE
    assert "hypothesis_space_degenerate" in single.reasons


def test_duplicate_evidence_ids_are_inadmissible() -> None:
    duplicated = (
        item("same", Responsibility.MEASUREMENT, weight=1.0),
        item("same", Responsibility.MEASUREMENT, weight=1.0),
    )
    report = assess_diagnosability(duplicated)
    assert report.state is DiagnosabilityState.INADMISSIBLE
    assert any("duplicate_evidence_id" in reason for reason in report.reasons)
    assert not issue_license(report, EpistemicAction.REWRITE_MEASUREMENT).granted


def test_an_evidence_fingerprint_mismatch_refuses_the_licence() -> None:
    """A licence must not be replayable against evidence edited afterwards."""

    report = assess_diagnosability((item("e0", Responsibility.SEARCH, weight=1.0),))
    assert report.state is DiagnosabilityState.DIAGNOSABLE
    good = issue_license(
        report,
        EpistemicAction.REWRITE_SEARCH_UNIVERSE,
        expected_evidence_fingerprint=report.evidence_fingerprint,
    )
    assert good.granted
    stale = issue_license(
        report,
        EpistemicAction.REWRITE_SEARCH_UNIVERSE,
        expected_evidence_fingerprint="0" * 64,
    )
    assert not stale.granted
    assert stale.refusal is RefusalReason.EVIDENCE_FINGERPRINT_MISMATCH


# --------------------------------------------------------------------------- #
# prove the alarm fires
# --------------------------------------------------------------------------- #


def test_a_corrupted_matrix_is_refused_at_issue_time() -> None:
    """The claim survives an edited rule table, or it is not a mechanism.

    A checker that has never alarmed is an untested checker. Here the table
    itself is corrupted into granting a representation rewrite from an evidence
    diagnosis — the exact failure the paper claims cannot happen — and both the
    audit and the issuing path must refuse it.
    """

    corrupted = dict(LICENSING_MATRIX)
    corrupted[Responsibility.EVIDENCE] = frozenset(
        {EpistemicAction.ACQUIRE_EVIDENCE, EpistemicAction.REWRITE_REPRESENTATION}
    )

    audit = audit_licensing_matrix(corrupted)
    assert audit.verdict is AuditVerdict.FAIL
    assert any(
        violation.startswith("mutation_licensed_by_non_mutation_class:EVIDENCE")
        for violation in audit.violations
    )
    assert audit.fingerprint != matrix_fingerprint()

    report = assess_diagnosability((item("e0", Responsibility.EVIDENCE, weight=1.0),))
    assert report.state is DiagnosabilityState.DIAGNOSABLE
    assert report.diagnosed is Responsibility.EVIDENCE
    decision = issue_license(
        report, EpistemicAction.REWRITE_REPRESENTATION, matrix=corrupted
    )
    assert not decision.granted
    assert decision.refusal is RefusalReason.LICENSING_INVARIANT_BREACH
    assert decision.ground_class is Responsibility.EVIDENCE
    # The legitimate row of the corrupted table still works, so the refusal is
    # aimed at the violation rather than at the table being unfamiliar.
    assert issue_license(
        report, EpistemicAction.ACQUIRE_EVIDENCE, matrix=corrupted
    ).granted


def test_a_corrupted_matrix_cannot_reach_the_protected_coordinate() -> None:
    corrupted = dict(LICENSING_MATRIX)
    corrupted[Responsibility.MEASUREMENT] = frozenset(
        {EpistemicAction.REWRITE_MEASUREMENT, EpistemicAction.REWRITE_METHOD}
    )
    audit = audit_licensing_matrix(corrupted)
    assert audit.verdict is AuditVerdict.FAIL
    assert any(
        violation.startswith("protected_coordinate_licensed:MEASUREMENT")
        for violation in audit.violations
    )
    report = assess_diagnosability(
        (item("e0", Responsibility.MEASUREMENT, weight=1.0),)
    )
    decision = issue_license(report, EpistemicAction.REWRITE_METHOD, matrix=corrupted)
    assert not decision.granted
    assert decision.refusal is RefusalReason.PROTECTED_COORDINATE


def test_a_matrix_missing_a_row_fails_closed() -> None:
    incomplete = {
        key: value
        for key, value in LICENSING_MATRIX.items()
        if key is not Responsibility.MEASUREMENT
    }
    assert audit_licensing_matrix(incomplete).verdict is AuditVerdict.FAIL
    report = assess_diagnosability(
        (item("e0", Responsibility.MEASUREMENT, weight=1.0),)
    )
    decision = issue_license(
        report, EpistemicAction.REWRITE_MEASUREMENT, matrix=incomplete
    )
    assert not decision.granted
    assert decision.refusal is RefusalReason.MATRIX_INCOMPLETE


def test_the_after_the_fact_auditor_alarms_on_a_forged_decision() -> None:
    """``invariant_violations`` reads receipts, so it must catch a bad receipt.

    Constructed by hand rather than produced by ``issue_license``: an auditor
    that can only ever see well-formed input has not been tested.
    """

    forged = LicenseDecision(
        action=EpistemicAction.REWRITE_REPRESENTATION,
        granted=True,
        ground_class=Responsibility.EVIDENCE,
        ground_authority=AuthorityClass.EVIDENCE,
        coordinate=coordinate_of(EpistemicAction.REWRITE_REPRESENTATION),
    )
    violations = invariant_violations([forged])
    assert violations
    assert violations[0].startswith("granted_mutation_from_non_mutation_class")
    assert invariant_violations([replace(forged, granted=False)]) == ()


# --------------------------------------------------------------------------- #
# fail closed: every non-diagnosable state refuses every action
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("evidence", "state", "reason"),
    [
        ((), DiagnosabilityState.NO_EVIDENCE, RefusalReason.NO_EVIDENCE),
        (
            (item("e0", Responsibility.MEASUREMENT, weight=SUB_DECISIVE_WEIGHT),),
            DiagnosabilityState.LOW_CONFIDENCE,
            RefusalReason.LOW_CONFIDENCE,
        ),
        (
            (
                item(
                    "e0",
                    Responsibility.INTERFACE,
                    Responsibility.DECOMPOSITION,
                    weight=1.0,
                ),
            ),
            DiagnosabilityState.INDISTINGUISHABLE,
            RefusalReason.NOT_DIAGNOSABLE,
        ),
        (
            (
                item("e0", Responsibility.EVIDENCE, weight=1.0),
                item("e1", Responsibility.REPRESENTATION, weight=1.0),
            ),
            DiagnosabilityState.CONFLICTING,
            RefusalReason.CONFLICTING_EVIDENCE,
        ),
        (
            (
                item("dup", Responsibility.SEARCH, weight=1.0),
                item("dup", Responsibility.SEARCH, weight=1.0),
            ),
            DiagnosabilityState.INADMISSIBLE,
            RefusalReason.EVIDENCE_INADMISSIBLE,
        ),
    ],
)
def test_every_non_diagnosable_state_issues_no_licence_at_all(
    evidence, state, reason
) -> None:
    """No licence, not a weaker licence — and a typed reason for every action."""

    report = assess_diagnosability(evidence)
    assert report.state is state, report.reasons
    assert report.diagnosed is None
    for action in EpistemicAction:
        decision = issue_license(report, action)
        assert not decision.granted, action
        assert decision.refusal is reason, (action, decision.refusal)
        assert decision.remedy == FAIL_CLOSED_REMEDY
        assert decision.detail


def test_indistinguishable_reports_which_classes_it_could_not_separate() -> None:
    """Not distinguishable is a state with contents, not a low confidence."""

    report = assess_diagnosability(
        (item("e0", Responsibility.INTERFACE, Responsibility.DECOMPOSITION, weight=1.0),)
    )
    assert report.state is DiagnosabilityState.INDISTINGUISHABLE
    assert set(report.indistinguishable_classes) == {
        Responsibility.INTERFACE,
        Responsibility.DECOMPOSITION,
    }
    assert report.posterior is not None
    assert report.posterior.entropy_bits > 0.0


def test_conflict_names_the_observations_that_disagree() -> None:
    report = assess_diagnosability(
        (
            item("e0", Responsibility.EVIDENCE, weight=1.0),
            item("e1", Responsibility.SEARCH, weight=1.0),
        )
    )
    assert report.state is DiagnosabilityState.CONFLICTING
    assert report.conflicting_evidence_ids == ("e0", "e1")


def test_a_two_class_observation_is_never_decisive_however_strong() -> None:
    for first, second in combinations(ALL_RESPONSIBILITIES, 2):
        report = assess_diagnosability((item("e0", first, second, weight=1.0),))
        assert report.state is not DiagnosabilityState.DIAGNOSABLE
        assert report.diagnosed is None


def test_the_confidence_rule_is_derived_rather_than_chosen() -> None:
    """One observation at the derived floor does not diagnose; just above it does.

    ``minimum_decisive_weight`` is algebra over the prior, not a tuned number,
    and this pins the algebra against the implementation.
    """

    assert FLOOR == pytest.approx(1.0 - 2.0 / SPACE_SIZE)
    at_floor = assess_diagnosability(
        (item("e0", Responsibility.MEASUREMENT, weight=FLOOR),)
    )
    assert at_floor.state is DiagnosabilityState.LOW_CONFIDENCE
    just_above = assess_diagnosability(
        (item("e0", Responsibility.MEASUREMENT, weight=FLOOR + 1e-6),)
    )
    assert just_above.state is DiagnosabilityState.DIAGNOSABLE
    assert just_above.posterior is not None
    assert just_above.posterior.mass(Responsibility.MEASUREMENT) > 0.5


# --------------------------------------------------------------------------- #
# probes: entropy and expected information gain
# --------------------------------------------------------------------------- #


def test_a_blind_probe_is_worth_exactly_zero_bits() -> None:
    """Zero by the arithmetic, not by a special case for the control."""

    blind = Probe(probe_id="blind", discriminates=())
    for evidence in ((), (item("e0", Responsibility.EVIDENCE, weight=1.0),)):
        posterior = build_posterior(evidence)
        assert expected_information_gain(posterior, blind) == 0.0


def test_information_gain_is_never_negative() -> None:
    """Mutual information is non-negative; an implementation bug shows up here."""

    for report in _sweep_reports():
        if report.posterior is None:
            continue
        space = set(report.posterior.hypothesis_space)
        reachable = [
            probe for probe in V2_PROBE_MENU if set(probe.discriminates) <= space
        ]
        assert reachable
        for value in rank_probes(report.posterior, reachable):
            assert value.expected_information_gain_bits >= -1e-12, value


def test_a_probe_with_wider_reach_is_worth_more_under_a_uniform_prior() -> None:
    posterior = build_posterior(())
    by_reach = {}
    for probe in V2_PROBE_MENU:
        by_reach[len(probe.discriminates)] = expected_information_gain(posterior, probe)
    ordered = [by_reach[size] for size in sorted(by_reach)]
    assert ordered == sorted(ordered)
    assert ordered[0] == 0.0
    assert ordered[-1] > ordered[0]


def test_probe_ranking_is_deterministic_and_reports_gain_per_cost() -> None:
    posterior = build_posterior((item("e0", Responsibility.EVIDENCE, weight=0.3),))
    first = rank_probes(posterior, V2_PROBE_MENU)
    second = rank_probes(posterior, tuple(reversed(V2_PROBE_MENU)))
    assert [v.probe_id for v in first] == [v.probe_id for v in second]
    assert canonical_bytes([v.to_payload() for v in first]) == canonical_bytes(
        [v.to_payload() for v in second]
    )
    assert first[-1].probe_id == "blind_control"


def test_a_probe_outside_the_hypothesis_space_is_refused_not_scored() -> None:
    posterior = build_posterior(
        (item("e0", Responsibility.SEARCH, weight=0.3),),
        space=(Responsibility.SEARCH, Responsibility.ROUTING),
    )
    with pytest.raises(ValueError):
        expected_information_gain(
            posterior, Probe(probe_id="p", discriminates=(Responsibility.EVIDENCE,))
        )


def test_entropy_is_maximal_under_the_prior_and_lower_after_evidence() -> None:
    prior = build_posterior(())
    assert prior.entropy_bits == pytest.approx(prior.max_entropy_bits)
    assert prior.normalized_entropy == pytest.approx(1.0)
    informed = build_posterior((item("e0", Responsibility.SEARCH, weight=1.0),))
    assert informed.entropy_bits < prior.entropy_bits
    assert shannon_entropy([1.0]) == 0.0
    assert shannon_entropy([0.5, 0.5]) == pytest.approx(1.0)


# --------------------------------------------------------------------------- #
# negative controls
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("scenario", NEGATIVE_CONTROLS, ids=lambda s: s.control_id)
def test_every_declared_negative_control_is_satisfied(scenario) -> None:
    receipt = run_control(scenario)
    assert receipt.satisfied, receipt.mismatches
    assert invariant_violations(receipt.decisions) == ()


def test_the_six_controls_the_issue_names_are_all_present() -> None:
    assert {scenario.control_id for scenario in NEGATIVE_CONTROLS} == {
        "blind_probe",
        "misleading_probe",
        "evidence_only_case",
        "execution_only_case",
        "formulation_case",
        "search_universe_case",
    }


def test_a_misleading_probe_issues_no_licence_of_any_kind() -> None:
    """The control that matters.

    A well-formed probe returns REPRESENTATION on a case whose standing
    observation is decisive for EVIDENCE. Two decisive observations pointing at
    different authority classes is a contradiction between instruments, and the
    mechanism fails closed: not a weaker licence, not a licence with a caveat —
    no licence at all, and a typed reason naming the conflict.
    """

    receipt = run_control(
        next(s for s in NEGATIVE_CONTROLS if s.control_id == "misleading_probe")
    )
    assert receipt.observed_state is DiagnosabilityState.CONFLICTING
    assert receipt.report.diagnosed is None
    assert all(not decision.granted for decision in receipt.decisions)
    assert {decision.refusal for decision in receipt.decisions} == {
        RefusalReason.CONFLICTING_EVIDENCE
    }
    # Grouped by the authority class each observation speaks for, so a reader
    # can see *which* two authorities collided rather than only that two ids did.
    assert receipt.report.conflicting_evidence_ids == (
        "standing_record_gap",
        "probe:coordinate_change",
    )


def test_a_sole_misleading_probe_is_a_diagnosis_failure_not_a_licensing_breach() -> None:
    """The boundary of what licensing can do, pinned so it cannot be forgotten.

    Strip the standing evidence away and the misleading probe is the only thing
    on the record. There is then nothing to contradict it: the mechanism
    diagnoses REPRESENTATION and licenses the representation coordinate. The
    licensing invariant is **not** violated — the licence names the class it was
    granted on, so the wrong diagnosis is visible on the receipt rather than
    laundered into an unexplained rewrite.

    No confidence bar is lowered to make this case refuse. Calibrating a
    threshold until a chosen input flips is tuning, and the licensing relation
    is a mechanism, not a score. What the case shows is a real limit: a
    permission attached to a label cannot repair a corrupted label.
    """

    probe = Probe(
        probe_id="coordinate_change",
        discriminates=(Responsibility.QUESTION, Responsibility.REPRESENTATION),
    )
    outcome = probe.observe(Responsibility.REPRESENTATION)
    assert outcome is not None
    report = assess_diagnosability((outcome,))

    assert report.state is DiagnosabilityState.DIAGNOSABLE
    assert report.diagnosed is Responsibility.REPRESENTATION
    decision = issue_license(report, EpistemicAction.REWRITE_REPRESENTATION)
    assert decision.granted
    # The grant is auditable: it names the class it rests on, and the invariant
    # holds because that class really is a formulation class.
    assert decision.ground_class is Responsibility.REPRESENTATION
    assert decision.ground_authority is AuthorityClass.FORMULATION
    assert invariant_violations([decision]) == ()
    # And it still cannot reach any other coordinate.
    for action in MUTATING_ACTIONS:
        if action is EpistemicAction.REWRITE_REPRESENTATION:
            continue
        assert not issue_license(report, action).granted


def test_accumulated_weak_evidence_can_outvote_a_decisive_observation() -> None:
    """Characterization, not an endorsement — a region of the model, pinned.

    ``_decisive_ids`` asks whether *one* observation would settle the question
    on its own, so accumulated sub-decisive mass is invisible to the conflict
    branch however much of it there is. Five half-strength REPRESENTATION
    observations outweigh one decisive EVIDENCE observation, the argmax is
    unique and clears the majority bar, and a representation rewrite is
    licensed while a decisive evidence observation sits on the record.

    The licensing invariant is **not** breached: the licence grounds on
    REPRESENTATION, which really is a formulation class, and the receipt says
    so. Whether accumulation *should* count as a conflict is a question about
    the evidence model, and widening the decisive test until this case flips
    would be tuning a rule against a chosen input. It is recorded here instead,
    so nobody has to rediscover it from the sweep.
    """

    evidence = (
        item("decisive_evidence", Responsibility.EVIDENCE, weight=DECISIVE_WEIGHT),
        *(
            item(f"weak{n}", Responsibility.REPRESENTATION, weight=0.5)
            for n in range(5)
        ),
    )
    report = assess_diagnosability(evidence)
    assert report.state is DiagnosabilityState.DIAGNOSABLE
    assert report.diagnosed is Responsibility.REPRESENTATION
    assert report.conflicting_evidence_ids == ()
    assert report.posterior is not None
    assert report.posterior.mass(Responsibility.REPRESENTATION) > 0.5

    decision = issue_license(report, EpistemicAction.REWRITE_REPRESENTATION)
    assert decision.granted
    assert decision.ground_class is Responsibility.REPRESENTATION
    assert decision.ground_authority is AuthorityClass.FORMULATION
    assert invariant_violations([decision]) == ()
    # The evidence class it outvoted gets nothing, which is the licensing
    # relation behaving exactly as specified for the class that was *not*
    # diagnosed.
    assert not issue_license(report, EpistemicAction.ACQUIRE_EVIDENCE).granted


def test_the_control_block_is_machine_readable() -> None:
    payload = control_archive_payload()
    assert payload["all_satisfied"] is True
    assert payload["matrix_audit"]["verdict"] == "PASS"
    assert payload["protocol_version"] == "P1.hidden-formulation.v1.1"
    assert "UNCHANGED" in payload["p1_v1_status"]
    assert len(payload["controls"]) == len(NEGATIVE_CONTROLS)
    assert json.loads(canonical_bytes(payload).decode()) == payload
    assert all(
        not record["invariant_violations"] for record in payload["controls"]
    )
    assert canonical_bytes(control_archive_payload(run_controls())) == canonical_bytes(
        payload
    )


# --------------------------------------------------------------------------- #
# the V2 harness — additive, and bound to the frozen suites by content
# --------------------------------------------------------------------------- #


def test_the_v2_bindings_are_the_frozen_p1_fingerprints(suites) -> None:
    """Recomputed from the cases on disk, not quoted.

    A declared binding that is never checked is a claim. This is what makes it a
    binding: the digests are recomputed from the frozen suites and cross-checked
    against ``PROTOCOL_V1.json``, which this lane does not modify.
    """

    declared = json.loads(PROTOCOL_JSON.read_text())["execution_bindings"][
        "dataset_revisions"
    ]
    assert V2_SUITE_BINDINGS[Split.PILOT.value] == declared["hidden_shift_suite_pilot"]
    assert V2_SUITE_BINDINGS[Split.TEST.value] == declared["hidden_shift_suite_test"]
    for split in Split:
        computed = suite_fingerprint(suites[split])
        assert computed == V2_SUITE_BINDINGS[split.value]
        assert bind_split(suites[split], split=split) == computed
    assert protocol_version() == "P1.hidden-formulation.v1.1"


def test_the_harness_refuses_a_suite_that_moved(suites) -> None:
    """Prove the binding alarms rather than merely existing."""

    cases = list(suites[Split.PILOT])
    cases[0] = replace(cases[0], public_prompt=cases[0].public_prompt + " ")
    with pytest.raises(ValueError, match="does not match the frozen"):
        bind_split(tuple(cases), split=Split.PILOT)


def test_the_mechanism_reads_public_views_only(suites) -> None:
    """The access boundary, enforced rather than documented.

    ``HiddenShiftCase`` also carries ``case_id``, ``public_prompt``,
    ``observable_resources`` and ``budget_class``, so a case handed to the
    mechanism would run and would put ``protected_gold`` one attribute access
    away. The refusal is the boundary.
    """

    case = suites[Split.PILOT][0]
    with pytest.raises(TypeError, match="PublicView only"):
        run_v2_view(case, split="PILOT", suite_fingerprint_value="x")
    receipt = run_v2_view(
        case.public_view, split="PILOT", suite_fingerprint_value="x"
    )
    assert receipt.case_id == case.case_id
    assert isinstance(case.public_view, PublicView)


def test_the_invariant_holds_on_every_case_of_the_frozen_suite(suites) -> None:
    """The checker, validated against real data rather than fixtures only.

    Sixty-six real cases through the real detector. This test asserts the
    invariant and the accounting, and deliberately asserts **no** accuracy: the
    licensing relation is a mechanism, and scoring it against gold here would be
    exactly the tuning pressure the study is built to avoid.
    """

    total = 0
    for split, expected in ((Split.PILOT, 18), (Split.TEST, 48)):
        archive = run_v2_split(suites[split], split=split)
        assert len(archive.receipts) == expected
        assert archive.matrix_audit.verdict is AuditVerdict.PASS
        assert archive.violations == (), archive.violations
        assert archive.suite_fingerprint == V2_SUITE_BINDINGS[split.value]
        counts = archive.state_counts()
        assert sum(counts.values()) == expected
        for receipt in archive.receipts:
            assert receipt.violations == ()
            for decision in receipt.decisions:
                assert decision.matrix_fingerprint == matrix_fingerprint()
                assert decision.evidence_fingerprint == receipt.report.evidence_fingerprint
                if decision.granted and decision.mutates_formulation:
                    assert decision.ground_authority in MUTATION_BEARING_CLASSES
        total += len(archive.receipts)
    assert total == 66


def test_the_frozen_suite_exercises_the_fail_closed_path_and_the_grant_path(
    suites,
) -> None:
    """Non-vacuity on real data, stated as a shape and not as a score.

    If every real case refused, the invariant would hold trivially; if every
    case granted, the fail-closed branch would be untested. Both branches must
    be reachable from the frozen suite. The exact counts are deliberately not
    asserted — they are a property of the detector, which this lane does not
    touch, and pinning them here would turn a mechanism test into a benchmark.
    """

    states: set[DiagnosabilityState] = set()
    granted_mutation = 0
    refused = 0
    for split in Split:
        archive = run_v2_split(suites[split], split=split)
        for receipt in archive.receipts:
            states.add(receipt.report.state)
            for decision in receipt.decisions:
                if decision.granted and decision.mutates_formulation:
                    granted_mutation += 1
                elif not decision.granted:
                    refused += 1
    assert DiagnosabilityState.DIAGNOSABLE in states
    assert states & {
        DiagnosabilityState.LOW_CONFIDENCE,
        DiagnosabilityState.INDISTINGUISHABLE,
        DiagnosabilityState.NO_EVIDENCE,
    }
    assert granted_mutation > 0
    assert refused > 0


def test_the_archive_payload_declares_v1_untouched_and_names_its_bindings(
    suites,
) -> None:
    archive = run_v2_split(suites[Split.PILOT], split=Split.PILOT)
    payload = archive.to_payload()
    assert payload["study_id"] == "P1.V2.responsibility-licensing.v1"
    assert payload["protocol_id"] == "P1.hidden-formulation.v1"
    assert payload["protocol_version"] == "P1.hidden-formulation.v1.1"
    assert payload["p1_v1_status"].startswith("UNCHANGED")
    assert payload["suite_fingerprint"] == V2_SUITE_BINDINGS[Split.PILOT.value]
    assert payload["matrix_audit"]["fingerprint"] == EXPECTED_MATRIX_FINGERPRINT
    assert payload["invariant_violations"] == []
    first = payload["receipts"][0]
    assert set(first) >= {
        "case_id",
        "decisions",
        "diagnosability",
        "evidence",
        "granted_actions",
        "invariant_violations",
        "matrix_fingerprint",
        "probe_values",
        "suite_fingerprint",
    }
    assert first["diagnosability"]["posterior"]["hypothesis_space"] == [
        r.value for r in ALL_RESPONSIBILITIES
    ]
