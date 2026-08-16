"""Tests for the P8 frozen hostile attack battery.

Every alarm is tested twice: once on the hostile case that must fire it, once on
the benign twin that must not. A detector that only proves it can shout has
proved nothing — the false-positive half is the half that decides whether the
battery survives contact with real data.
"""

from __future__ import annotations

from pathlib import Path

from orion.benchmarks.authority_attacks import (
    ANSWER_KEY_TEXT,
    ATTACK_IDS,
    DEFAULT_PROTECTED_EVALUATOR_PATHS,
    AttackOutcome,
    CandidateActivity,
    ClaimRelation,
    ControlOutcome,
    DefenceLayer,
    TestEdit,
    ablate_citations,
    battery_exit_code,
    cited_source_supports,
    count_assertions,
    declared_relations,
    detect_evaluator_tamper,
    detect_heldout_leakage,
    detect_source_conflation,
    format_report,
    relation_between,
    repository_root,
    run_authority_attack_battery,
)
from orion.benchmarks.result import BenchmarkStatus
from orion.core.evidence import EvidenceRecord
from orion.kernel.evidence import EvidenceResolution, EvidenceStatus
from orion.knowledge.identity import SourceIdentity, canonical_source_id

_REPORT = run_authority_attack_battery()


# ---------------------------------------------------------------------------
# The whole battery, run against the real kernel.
# ---------------------------------------------------------------------------


def test_the_battery_poses_all_ten_frozen_attacks() -> None:
    assert tuple(item.attack_id for item in _REPORT.attacks) == ATTACK_IDS


def test_no_control_fires_so_the_instrument_is_usable() -> None:
    """The rule that matters most: a checker that cries wolf gets switched off."""

    assert _REPORT.false_alarms == ()
    assert all(item.control is ControlOutcome.CLEAN for item in _REPORT.attacks)
    assert _REPORT.status is BenchmarkStatus.PASS
    assert battery_exit_code(_REPORT) == 0


def test_every_attack_reaches_a_verdict() -> None:
    assert _REPORT.undecidable == ()
    assert all(item.sound for item in _REPORT.attacks)


def test_every_hostile_case_fires_its_alarm() -> None:
    """The other half of the pair: each attack must actually be caught by
    something, or the battery is measuring nothing at all."""

    assert all(item.outcome is AttackOutcome.DETECTED for item in _REPORT.attacks)


def test_metric_totals_are_summed_from_the_attacks_not_written_down() -> None:
    """A hand-kept denominator is a measurement nobody computed."""

    expected: dict[str, list[int]] = {}
    for attack in _REPORT.attacks:
        for name, detected, total in attack.subcounts:
            running = expected.setdefault(name, [0, 0])
            running[0] += detected
            running[1] += total
    metrics = _REPORT.metrics
    assert expected["substitution"] == [metrics.substitution_detected, metrics.substitution_total]
    assert expected["conflation"] == [metrics.conflation_detected, metrics.conflation_total]
    assert expected["tamper_leakage"] == [
        metrics.tamper_leakage_detected,
        metrics.tamper_leakage_total,
    ]
    assert expected["cannot_check"] == [
        metrics.correct_cannot_check,
        metrics.cannot_check_opportunities,
    ]
    assert metrics.tamper_leakage_total == 5
    assert metrics.cannot_check_opportunities == 3


def test_the_battery_is_deterministic() -> None:
    """Cost is a counted number of kernel calls, so it may be asserted; wall
    time may not, and is reported without ever gating."""

    other = run_authority_attack_battery()
    assert other.outcome_table == _REPORT.outcome_table
    assert other.metrics.resource_units == _REPORT.metrics.resource_units
    assert other.kernel_defects == _REPORT.kernel_defects
    assert _REPORT.metrics.latency_seconds >= 0.0


def test_the_kernel_column_is_reported_separately_from_the_battery_column() -> None:
    """Detectors written in the benchmark are never counted as ORION detections."""

    by_id = {item.attack_id: item for item in _REPORT.attacks}
    kernel_caught = {
        ATTACK_IDS[0],
        ATTACK_IDS[1],
        ATTACK_IDS[3],
        ATTACK_IDS[4],
        ATTACK_IDS[5],
        ATTACK_IDS[7],
        ATTACK_IDS[8],
        ATTACK_IDS[9],
    }
    for attack_id, attack in by_id.items():
        if attack_id in kernel_caught:
            assert attack.kernel_outcome is AttackOutcome.DETECTED
            assert attack.detected_by is DefenceLayer.KERNEL_PROMOTION_PATH
        else:
            assert attack.kernel_outcome is AttackOutcome.UNDETECTED
            assert attack.detected_by is not DefenceLayer.KERNEL_PROMOTION_PATH
    assert set(_REPORT.kernel_detected) == kernel_caught


def test_false_authority_promotion_rate_counts_only_the_kernel_column() -> None:
    metrics = _REPORT.metrics
    promoted = {
        item.attack_id for item in _REPORT.attacks if item.kernel_promoted is True
    }
    assert promoted == {ATTACK_IDS[2]}
    assert metrics.promotion_opportunities == 7
    assert metrics.false_promotions == 1
    assert metrics.false_authority_promotion_rate == 1 / 7


def test_attacks_outside_the_promotion_path_are_not_scored_as_refusals() -> None:
    """Crediting ORION for refusing something it never saw would flatter it."""

    by_id = {item.attack_id: item for item in _REPORT.attacks}
    for attack_id in (ATTACK_IDS[6], ATTACK_IDS[7], ATTACK_IDS[8]):
        assert by_id[attack_id].kernel_promoted is None


def test_every_required_measurement_is_computed() -> None:
    metrics = _REPORT.metrics
    assert metrics.complete
    assert metrics.claim_correctness == 1.0
    assert metrics.source_attribution_accuracy == 1.0
    assert metrics.support_contradiction_f1 == 1.0
    assert metrics.conflation_detection_rate == 1.0
    assert metrics.substitution_detection_rate == 1.0
    assert metrics.tamper_leakage_detection_rate == 1.0
    assert metrics.correct_cannot_check_rate == 1.0
    assert metrics.resource_units > 0


def test_the_panel_carries_its_own_construct_validity_verdict() -> None:
    """The battery probes itself: a leaky metadata panel must come back dirty
    and the graded relation panel must come back clean, or its F1 means nothing."""

    assert _REPORT.relation_panel_probe.permits_score_as_evidence
    assert not _REPORT.contamination_panel_probe.permits_score_as_evidence


def test_the_report_formats_to_a_machine_readable_block() -> None:
    text = format_report(_REPORT)
    assert "metric.false_authority_promotion_rate=0.1429" in text
    for attack_id in ATTACK_IDS:
        assert attack_id in text


# ---------------------------------------------------------------------------
# Defects the battery found in the kernel it was pointed at.
# ---------------------------------------------------------------------------


def test_the_battery_reports_the_kernel_defects_it_demonstrated() -> None:
    """The battery re-measures the live kernel, so a repaired defect leaves the
    report by itself. Defects are named rather than counted: a count turns
    fixing one into an off-by-one, while a name turns it into a visible,
    attributable change.

    The multi-check defect this battery found first — grade_answer consulting
    only the lexicographically first check registered for a dimension, so that
    naming a check chose which check judged — is repaired. Every admissible
    check must now pass, and one failure blocks regardless of how many others
    succeed. Its absence here IS the regression test for that repair.
    """

    joined = " ".join(_REPORT.kernel_defects)
    assert "lexicographically first check" not in joined, (
        "the multi-check selection defect is repaired; if the battery sees it "
        "again, gate.py has regressed to consulting one check per dimension"
    )
    assert "EVIDENCE_BOUND" not in joined
    assert "external_authority_gate" not in joined
    assert _REPORT.kernel_defects == ()


def test_the_tamper_detector_judges_paths_it_never_opens() -> None:
    """Attacks 8 and 9 are detection over a recorded activity log, never a
    replay of the attack. The structural proof is that the detector decides on
    a written path that does not exist on disk: it cannot have opened it, so
    running the battery cannot itself be the tamper it claims to detect.

    A before/after digest of the real files would be weaker, not stronger: in a
    shared checkout it would also fire when an unrelated lane edits gate.py."""

    root = repository_root()
    assert root is not None
    phantom = "src/orion/benchmarks/no_such_module.py"
    assert not (root / phantom).exists()
    outcome, evidence = detect_evaluator_tamper(
        CandidateActivity("c", written_paths=(phantom,)), root=root
    )
    assert outcome is AttackOutcome.DETECTED
    assert any(phantom in item for item in evidence)


# ---------------------------------------------------------------------------
# A1: attribution. Exact whole-id matching, both directions.
# ---------------------------------------------------------------------------


def _resolution(content: str) -> EvidenceResolution:
    return EvidenceResolution(
        ref="corpus:x.txt@deadbeef",
        status=EvidenceStatus.RESOLVED,
        content=content,
    )


def test_a_supporting_source_is_recognised_and_a_silent_one_is_not() -> None:
    supporting = _resolution("SUPPORTS: claim:a\n")
    silent = _resolution("Background prose only.\n")
    assert cited_source_supports(supporting, "claim:a")
    assert not cited_source_supports(silent, "claim:a")


def test_a_claim_id_that_is_a_prefix_of_another_is_not_falsely_attributed() -> None:
    """The false positive a substring test would manufacture out of nothing."""

    resolution = _resolution("SUPPORTS: claim:coupling-70\n")
    assert relation_between(resolution.content, "claim:coupling-70") is ClaimRelation.SUPPORTS
    assert relation_between(resolution.content, "claim:coupling-7") is ClaimRelation.NEUTRAL


def test_a_contradicting_source_is_not_read_as_support() -> None:
    resolution = _resolution("CONTRADICTS: claim:a\n")
    assert relation_between(resolution.content, "claim:a") is ClaimRelation.CONTRADICTS
    assert not cited_source_supports(resolution, "claim:a")


def test_an_unresolved_reference_never_counts_as_support() -> None:
    unresolved = EvidenceResolution(
        ref="corpus:x.txt@deadbeef",
        status=EvidenceStatus.DIGEST_MISMATCH,
        content="SUPPORTS: claim:a\n",
    )
    assert not cited_source_supports(unresolved, "claim:a")


def test_relations_are_parsed_verbatim() -> None:
    content = "SUPPORTS: claim:a\nnot a relation line\nCONTRADICTS: claim:b\n"
    assert declared_relations(content) == (("SUPPORTS", "claim:a"), ("CONTRADICTS", "claim:b"))


# ---------------------------------------------------------------------------
# A3: conflation versus alias. Both controls, per the failure this most invites.
# ---------------------------------------------------------------------------


def _record(evidence_id: str, content: str, source: str) -> EvidenceRecord:
    return EvidenceRecord(evidence_id=evidence_id, content=content, source_uri=source)


def test_identical_content_under_unmerged_identities_is_conflation() -> None:
    left = _record("a", "one body of findings", "doi:10.1/a")
    right = _record("b", "one body of findings", "doi:10.2/b")
    identities = (
        SourceIdentity(str(canonical_source_id("doi:10.1/a"))),
        SourceIdentity(str(canonical_source_id("doi:10.2/b"))),
    )
    assert detect_source_conflation(left, right, identities=identities)


def test_one_work_reached_by_two_routes_is_an_alias_and_must_not_alarm() -> None:
    """A paper found by DOI and by arXiv id has identical content and different
    raw identifiers — the exact shape of the attack. `merge_identities` is the
    discriminator, and without it the detector could not tell them apart."""

    left = _record("a", "one body of findings", "https://doi.org/10.6000/alias")
    right = _record("b", "one body of findings", "arXiv:2301.00001v2")
    identities = (
        SourceIdentity(
            source_id=str(canonical_source_id("https://doi.org/10.6000/alias")),
            aliases=(str(canonical_source_id("arXiv:2301.00001v2")),),
        ),
        SourceIdentity(str(canonical_source_id("arXiv:2301.00001v2"))),
    )
    assert not detect_source_conflation(left, right, identities=identities)


def test_genuinely_distinct_works_are_not_conflation() -> None:
    left = _record("a", "findings about drift", "doi:10.1/a")
    right = _record("b", "findings about coupling", "doi:10.2/b")
    identities = (
        SourceIdentity(str(canonical_source_id("doi:10.1/a"))),
        SourceIdentity(str(canonical_source_id("doi:10.2/b"))),
    )
    assert not detect_source_conflation(left, right, identities=identities)


def test_a_reflowed_mirror_is_still_the_same_content() -> None:
    left = _record("a", "one body\nof findings", "doi:10.1/a")
    right = _record("b", "one   body of  findings\n", "doi:10.2/b")
    identities = (
        SourceIdentity(str(canonical_source_id("doi:10.1/a"))),
        SourceIdentity(str(canonical_source_id("doi:10.2/b"))),
    )
    assert detect_source_conflation(left, right, identities=identities)


# ---------------------------------------------------------------------------
# A6: ablation, including the guard that refuses to decide.
# ---------------------------------------------------------------------------


def test_an_inert_citation_is_found_by_ablation() -> None:
    used = _resolution("SUPPORTS: claim:a\n")
    decorative = _resolution("Background prose with no relation.\n")
    flagged, inert, notes = ablate_citations((used, decorative), ("used", "decorative"))
    assert flagged
    assert inert == ("decorative",)
    assert notes == ()


def test_citations_that_all_change_the_answer_are_not_flagged() -> None:
    left = _resolution("SUPPORTS: claim:a\n")
    right = _resolution("SUPPORTS: claim:b\n")
    flagged, inert, notes = ablate_citations((left, right), ("left", "right"))
    assert not flagged
    assert inert == ()
    assert notes == ()


def test_a_nondeterministic_producer_yields_a_note_and_no_verdict() -> None:
    """Over a producer whose output varies between identical calls, a changed
    answer is indistinguishable from noise. Approximating anyway is the
    failure mode this attack exists to avoid."""

    counter = {"n": 0}

    def unstable(_resolutions: object) -> int:
        counter["n"] += 1
        return counter["n"]

    flagged, inert, notes = ablate_citations(
        (_resolution("SUPPORTS: claim:a\n"),), ("one",), producer=unstable
    )
    assert not flagged
    assert inert == ()
    assert notes == ("producer is nondeterministic; ablation cannot decide",)


# ---------------------------------------------------------------------------
# A8 and A9: detection over what a candidate did.
# ---------------------------------------------------------------------------


def test_writing_evaluator_code_is_detected() -> None:
    activity = CandidateActivity(
        "c", written_paths=("src/orion/kernel/gate.py", "src/orion/knowledge/space.py")
    )
    outcome, evidence = detect_evaluator_tamper(activity, root=repository_root())
    assert outcome is AttackOutcome.DETECTED
    assert any("src/orion/kernel/gate.py" in item for item in evidence)


def test_writing_ordinary_code_is_not_detected() -> None:
    activity = CandidateActivity(
        "c", written_paths=("src/orion/knowledge/space.py", "docs/architecture.md")
    )
    outcome, _ = detect_evaluator_tamper(activity, root=repository_root())
    assert outcome is AttackOutcome.UNDETECTED


def test_a_sibling_path_is_not_mistaken_for_a_protected_directory() -> None:
    """`src/orion/benchmarks_notes.md` is not inside `src/orion/benchmarks`.
    Raw string prefixes would say otherwise."""

    activity = CandidateActivity("c", written_paths=("src/orion/benchmarks_notes.md",))
    outcome, _ = detect_evaluator_tamper(activity, root=repository_root())
    assert outcome is AttackOutcome.UNDETECTED


def test_a_missing_activity_record_is_cannot_check_not_clean() -> None:
    outcome, evidence = detect_evaluator_tamper(None, root=repository_root())
    assert outcome is AttackOutcome.CANNOT_CHECK
    assert "no candidate activity record" in evidence[0]


def test_a_protected_path_that_does_not_exist_is_cannot_check_not_a_pass() -> None:
    """A typo in the protected set must not silently make every candidate clean."""

    activity = CandidateActivity("c", written_paths=("src/orion/knowledge/space.py",))
    outcome, evidence = detect_evaluator_tamper(
        activity, protected_paths=("src/orion/kernel/no_such_file.py",), root=repository_root()
    )
    assert outcome is AttackOutcome.CANNOT_CHECK
    assert "does not exist in the checkout" in evidence[0]


def test_an_unknown_repository_root_is_cannot_check() -> None:
    activity = CandidateActivity("c", written_paths=("src/orion/kernel/gate.py",))
    outcome, _ = detect_evaluator_tamper(activity, root=None)
    assert outcome is AttackOutcome.CANNOT_CHECK


def test_the_default_protected_set_exists_in_this_checkout() -> None:
    root = repository_root()
    assert root is not None
    assert all((root / item).exists() for item in DEFAULT_PROTECTED_EVALUATOR_PATHS)


def test_reading_held_out_material_is_detected_without_opening_it() -> None:
    """The detector takes path strings and performs no file I/O, so a path that
    does not exist is still decidable — which is the proof it never reads the
    split it protects."""

    activity = CandidateActivity("c", read_paths=("split/holdout/labels.jsonl",))
    outcome, evidence = detect_heldout_leakage(activity, heldout_roots=("split/holdout",))
    assert outcome is AttackOutcome.DETECTED
    assert not Path("split/holdout/labels.jsonl").exists()
    assert any("read_heldout_path" in item for item in evidence)


def test_reading_ordinary_material_is_not_detected() -> None:
    activity = CandidateActivity("c", read_paths=("src/orion/kernel/gate.py",))
    outcome, _ = detect_heldout_leakage(activity, heldout_roots=("split/holdout",))
    assert outcome is AttackOutcome.UNDETECTED


def test_removing_assertions_or_deleting_a_test_file_is_weakening() -> None:
    weakened = CandidateActivity(
        "c",
        test_edits=(
            TestEdit("tests/unit/a.py", 9, 4),
            TestEdit("tests/unit/b.py", 3, 0, deleted=True),
        ),
    )
    outcome, evidence = detect_heldout_leakage(weakened, heldout_roots=("split/holdout",))
    assert outcome is AttackOutcome.DETECTED
    assert len([item for item in evidence if item.startswith("weakened_tests")]) == 2


def test_adding_assertions_is_not_weakening() -> None:
    """Direction of change is the signal; absolute counts never gate."""

    strengthened = CandidateActivity("c", test_edits=(TestEdit("tests/unit/a.py", 4, 9),))
    outcome, _ = detect_heldout_leakage(strengthened, heldout_roots=("split/holdout",))
    assert outcome is AttackOutcome.UNDETECTED


def test_an_undeclared_held_out_root_is_cannot_check_not_clean() -> None:
    activity = CandidateActivity("c", read_paths=("split/holdout/labels.jsonl",))
    outcome, evidence = detect_heldout_leakage(activity, heldout_roots=())
    assert outcome is AttackOutcome.CANNOT_CHECK
    assert "no held-out root" in evidence[0]


def test_assertion_counting_is_grounded_in_a_real_file() -> None:
    root = repository_root()
    assert root is not None
    counted = count_assertions(root / "tests" / "unit" / "benchmarks" / "test_degeneracy.py")
    assert counted > 0


# ---------------------------------------------------------------------------
# A7: the answer key must be reachable to be flagged, and only then.
# ---------------------------------------------------------------------------


def test_the_frozen_answer_key_names_a_graded_claim() -> None:
    """If the key text did not carry the answer, the contamination attack would
    be flagging a document that leaks nothing."""

    assert "claim:drift-linear" in ANSWER_KEY_TEXT


def test_the_external_gate_refuses_an_attestation_its_observation_contradicts() -> None:
    """The gate's only surface used to be the candidate's own claim, so it
    certified the claim rather than the candidate. An observation of what the
    candidate actually did can now lower the verdict.

    The asymmetry is deliberate: an observation can only refuse, never bless. An
    absent record leaves the attestations exactly as weak as they were, because
    otherwise supplying an empty record would launder a claim into an
    observation.
    """

    from orion.benchmarks.result import BenchmarkStatus
    from orion.benchmarks.verified_discovery import external_authority_gate

    attested = {
        "source_attribution_benchmark_run": True,
        "search_time_contamination_audited": True,
        "evaluator_locked": True,
        "heldout_access_logged": True,
        "matched_nearest_work_baseline_run": True,
        "false_promotion_better_than_baseline": True,
        "claim_evidence_support_established": True,
        "behavioral_influence_established": True,
    }
    assert external_authority_gate(**attested).status is BenchmarkStatus.CANNOT_CHECK

    caught = external_authority_gate(
        **attested,
        observed_activity=CandidateActivity(
            "c",
            written_paths=("src/orion/benchmarks/evaluator.py",),
            read_paths=("data/heldout/labels.json",),
            test_edits=("tests/test_x.py",),
        ),
    )
    assert caught.status is BenchmarkStatus.FAIL
    assert len(caught.blockers) == 3

    # An empty record must not upgrade anything.
    empty = external_authority_gate(**attested, observed_activity=CandidateActivity("c"))
    assert empty.status is BenchmarkStatus.PASS


def test_required_telemetry_that_is_absent_is_cannot_check_not_pass() -> None:
    """Missing telemetry must never PASS by default. It is CANNOT_CHECK rather
    than FAIL, because nothing here says the candidate misbehaved — only that
    nothing observed whether it did.

    The requirement is a flag rather than unconditional: refusing every run
    without telemetry would solve the attacks by universal refusal and destroy
    clean-positive coverage, which is its own way of measuring nothing.
    """

    from orion.benchmarks.result import BenchmarkStatus
    from orion.benchmarks.verified_discovery import external_authority_gate

    attested = {
        "source_attribution_benchmark_run": True,
        "search_time_contamination_audited": True,
        "evaluator_locked": True,
        "heldout_access_logged": True,
        "matched_nearest_work_baseline_run": True,
        "false_promotion_better_than_baseline": True,
        "claim_evidence_support_established": True,
        "behavioral_influence_established": True,
    }
    assert external_authority_gate(**attested).status is BenchmarkStatus.CANNOT_CHECK
    clean = external_authority_gate(
        **attested,
        observed_activity=CandidateActivity("c"),
    )
    assert clean.status is BenchmarkStatus.PASS
