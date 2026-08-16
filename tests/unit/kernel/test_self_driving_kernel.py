from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from orion.kernel import (
    AnswerAuthority,
    CheckOutcome,
    DirectoryAnswerSource,
    DiscriminatingCheck,
    EntryKind,
    EvidenceStatus,
    LedgerIntegrityError,
    LedgerStore,
    SelfDrivingDriver,
    StaticAnswerSource,
    apply_selection_guards,
    battery_order,
    discrimination_order,
    grade_and_apply,
    host_battery,
    resolve_evidence_ref,
    run_discriminating_check,
    run_round,
)
from orion.kernel.battery import JUNK_TOKEN, writable_fields
from orion.kernel.guards import GuardEffect, GuardRule
from orion.kernel.saturation import (
    GrowthVector,
    SaturationBasis,
    SaturationVerdict,
    assess_saturation,
)
from orion.experience.model import LessonAuthority
from orion.mechanics.answers import AnswerRecord
from orion.mechanics.model import MechanicCell, MechanicDimension
from orion.mechanics.program import observe_mechanics_program
from orion.mechanics.questioning import generate_mechanic_questions
from orion.kernel.evidence import expected_binding
from orion.mechanics.workflow import ORION_WORKFLOW_ROOT_ID

_UNRESOLVABLE_BINDING = "0" * 64


def _binding(ref: str, root: Path) -> tuple[tuple[str, str], ...]:
    """The content binding an honest lane would declare for this reference."""

    resolution = resolve_evidence_ref(ref, {"orion": root})
    digest = (
        expected_binding(resolution) if resolution.resolved else _UNRESOLVABLE_BINDING
    )
    return ((ref, digest),)

TARGET = "T.STORAGE.v1"


def _evidence(tmp_path: Path, name: str = "source.md", body: str = "real content") -> str:
    path = tmp_path / name
    path.write_text(body, encoding="utf-8")
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    return f"orion:{name}@{digest[:12]}"


def _program() -> tuple[MechanicCell, ...]:
    root = MechanicCell(
        mechanic_id=ORION_WORKFLOW_ROOT_ID,
        purpose="root",
        scope="one root problem",
        child_mechanic_ids=(TARGET,),
    )
    child = MechanicCell(mechanic_id=TARGET, purpose="store step output", scope="one step")
    return (root, child)


def _storage_check(*, lane: str = "verifier", frozen_at_round: int | None = 0) -> DiscriminatingCheck:
    return DiscriminatingCheck(
        check_id="check:storage-names-a-durable-medium",
        dimension=MechanicDimension.STORAGE,
        lane=lane,
        predicate=lambda cell: any(
            "ledger" in item for item in cell.storage_contracts
        ),
        positive_fixture=MechanicCell(
            mechanic_id="fixture.pos",
            purpose="p",
            scope="s",
            storage_contracts=("append-only ledger entry per answer",),
        ),
        negative_fixtures=(MechanicCell(mechanic_id="fixture.neg", purpose="p", scope="s"),),
        frozen_at_round=frozen_at_round,
    )


def _answer(ref: str, *, root: Path, record_id: str = "a1", lane: str = "machine", value: str = "append-only ledger entry per answer") -> AnswerRecord:
    return AnswerRecord(
        record_id=record_id,
        mechanic_id=TARGET,
        dimension=MechanicDimension.STORAGE,
        lane=lane,
        evidence_refs=(ref,),
        evidence_bindings=_binding(ref, root),
        payload=(("storage_contracts", (value,)),),
    )


# --- evidence resolution -------------------------------------------------


def test_fabricated_evidence_reference_does_not_resolve(tmp_path: Path) -> None:
    resolution = resolve_evidence_ref("orion:nowhere.md@abcdef123456", {"orion": tmp_path})
    assert resolution.status is EvidenceStatus.MISSING_ARTIFACT
    assert not resolution.resolved


def test_digest_must_match_actual_content(tmp_path: Path) -> None:
    (tmp_path / "source.md").write_text("real content", encoding="utf-8")
    resolution = resolve_evidence_ref("orion:source.md@000000000000", {"orion": tmp_path})
    assert resolution.status is EvidenceStatus.DIGEST_MISMATCH


def test_evidence_path_cannot_escape_its_root(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    (tmp_path / "outside.md").write_text("x", encoding="utf-8")
    resolution = resolve_evidence_ref("orion:../outside.md@abcdef123456", {"orion": root})
    assert resolution.status is EvidenceStatus.ESCAPES_ROOT


# --- the anti-gaming ladder ----------------------------------------------


def test_string_filling_without_evidence_cannot_close_a_question(tmp_path: Path) -> None:
    """The defect this kernel exists to prevent: closure by writing any string."""

    cells = _program()
    before = observe_mechanics_program(cells)
    junk = AnswerRecord(
        record_id="junk",
        mechanic_id=TARGET,
        dimension=MechanicDimension.STORAGE,
        lane="machine",
        evidence_refs=("orion:invented.md@deadbeefcafe",),
        evidence_bindings=(("orion:invented.md@deadbeefcafe", _UNRESOLVABLE_BINDING),),
        payload=(("storage_contracts", ("xxxxx",)),),
    )
    result = grade_and_apply(cells, (junk,), evidence_roots={"orion": tmp_path})
    after = observe_mechanics_program(result.cells)

    assert result.gradings[0].authority is AnswerAuthority.PROPOSED
    assert result.refused_record_ids == ("junk",)
    assert after.open_question_count == before.open_question_count


def test_evidence_bound_answer_applies_content_but_keeps_the_question_open(
    tmp_path: Path,
) -> None:
    cells = _program()
    before = observe_mechanics_program(cells)
    result = grade_and_apply(
        cells, (_answer(_evidence(tmp_path), root=tmp_path),), evidence_roots={"orion": tmp_path}
    )
    after = observe_mechanics_program(result.cells)
    target = next(item for item in result.cells if item.mechanic_id == TARGET)

    assert result.gradings[0].authority is AnswerAuthority.EVIDENCE_BOUND
    assert target.storage_contracts  # content landed
    assert MechanicDimension.STORAGE in target.provisional_dimensions
    assert after.open_question_count == before.open_question_count


def test_independent_frozen_discriminating_check_closes_exactly_one_question(
    tmp_path: Path,
) -> None:
    cells = _program()
    before = observe_mechanics_program(cells)
    result = grade_and_apply(
        cells,
        (_answer(_evidence(tmp_path), root=tmp_path),),
        evidence_roots={"orion": tmp_path},
        checks={"c": _storage_check()},
        round_index=1,
    )
    after = observe_mechanics_program(result.cells)

    assert result.gradings[0].authority is AnswerAuthority.VERIFIED
    assert before.open_question_count - after.open_question_count == 1


def test_check_that_accepts_its_negative_fixture_cannot_verify(tmp_path: Path) -> None:
    """A check that separates nothing is the signature of closure-by-string."""

    permissive = DiscriminatingCheck(
        check_id="c",
        dimension=MechanicDimension.STORAGE,
        lane="verifier",
        predicate=lambda cell: True,
        positive_fixture=MechanicCell(mechanic_id="p", purpose="p", scope="s"),
        negative_fixtures=(MechanicCell(mechanic_id="n", purpose="p", scope="s"),),
        frozen_at_round=0,
    )
    result = grade_and_apply(
        _program(),
        (_answer(_evidence(tmp_path), root=tmp_path),),
        evidence_roots={"orion": tmp_path},
        checks={"c": permissive},
        round_index=1,
    )
    grading = result.gradings[0]
    assert grading.check_outcome is CheckOutcome.NOT_DISCRIMINATING
    assert grading.authority is AnswerAuthority.EVIDENCE_BOUND


def _check_with(predicate, *, negatives: tuple[MechanicCell, ...] = ()) -> DiscriminatingCheck:
    return DiscriminatingCheck(
        check_id="c",
        dimension=MechanicDimension.STORAGE,
        lane="verifier",
        predicate=predicate,
        positive_fixture=MechanicCell(
            mechanic_id="fixture.pos",
            purpose="p",
            scope="s",
            storage_contracts=("append-only ledger entry per answer",),
        ),
        negative_fixtures=negatives,
        frozen_at_round=0,
    )


def test_the_satisfaction_predicate_itself_cannot_be_admitted() -> None:
    """The theorem the host battery buys.

    `questioning._satisfied` is `bool(cell.some_tuple)`. If that predicate could
    be registered as a check, the loop would verify any string and the entire
    authority ladder would be decorative. The battery's junk member has every
    writable field non-empty, so admissibility entails the predicate is not
    mere non-emptiness — for any dimension, without enumerating attacks.
    """

    defect = _check_with(lambda cell: bool(cell.storage_contracts))
    outcome, reasons = run_discriminating_check(
        defect,
        MechanicCell(
            mechanic_id="t", purpose="p", scope="s", storage_contracts=("anything",)
        ),
    )
    assert outcome is CheckOutcome.NOT_DISCRIMINATING
    # The theorem, asserted directly rather than through a reason string: the
    # junk member has every writable field non-empty, so a non-emptiness
    # predicate must accept it.
    junk = host_battery(MechanicDimension.STORAGE)[1]
    assert defect.predicate(junk)
    assert reasons


def test_a_check_satisfied_by_restating_the_question_cannot_be_admitted() -> None:
    """Envelope laundering: closure by echoing the audit question back."""

    # "It is substantive because it is long" — accepts the real answer and the
    # dimension's own question text alike.
    echo = _check_with(
        lambda cell: any(len(item) > 20 for item in cell.storage_contracts)
    )
    outcome, reasons = run_discriminating_check(
        echo,
        MechanicCell(
            mechanic_id="t",
            purpose="p",
            scope="s",
            storage_contracts=("a reasonably long sounding phrase",),
        ),
    )
    assert outcome is CheckOutcome.NOT_DISCRIMINATING
    envelope = host_battery(MechanicDimension.STORAGE)[2]
    assert echo.predicate(envelope)
    assert reasons


def test_a_weak_author_declared_negative_does_not_lower_the_bar() -> None:
    """The author picks negatives; the host picks more. Only the host's bind."""

    weak = _check_with(
        lambda cell: bool(cell.storage_contracts),
        negatives=(MechanicCell(mechanic_id="trivial", purpose="p", scope="s"),),
    )
    outcome, _ = run_discriminating_check(
        weak,
        MechanicCell(mechanic_id="t", purpose="p", scope="s", storage_contracts=("x",)),
    )
    assert outcome is CheckOutcome.NOT_DISCRIMINATING
    assert discrimination_order(weak) == 1 + battery_order(MechanicDimension.STORAGE)


def test_no_dimension_falls_below_the_host_floor() -> None:
    """Every dimension, including the two that carry structured payloads.

    Found by running against the real decomposition rather than fixtures:
    HANDOFF and METRICS write typed objects, not strings, so a string-only
    battery left exactly those two at order 1 — readmitting the defect
    predicate for them alone.
    """

    assert {battery_order(dimension) for dimension in MechanicDimension} == {3}


def test_non_emptiness_is_inadmissible_for_every_dimension() -> None:
    """The theorem, universally quantified over the audit grammar."""

    for dimension in MechanicDimension:
        junk = host_battery(dimension)[1]
        fields = writable_fields(dimension) or (
            "handoff_fields" if dimension is MechanicDimension.HANDOFF else "metrics",
        )
        for field in fields:
            check = DiscriminatingCheck(
                check_id=f"c:{dimension.value}:{field}",
                dimension=dimension,
                lane="verifier",
                predicate=lambda cell, name=field: bool(getattr(cell, name)),
                positive_fixture=junk,
                frozen_at_round=0,
            )
            outcome, _ = run_discriminating_check(check, junk)
            assert outcome is CheckOutcome.NOT_DISCRIMINATING, (
                f"{dimension.value}.{field} still admits mere non-emptiness"
            )


def test_the_battery_exercises_every_field_the_dimension_may_write() -> None:
    """A battery that left a writable field empty would leave an unguarded path."""

    for dimension in MechanicDimension:
        fields = writable_fields(dimension)
        if not fields:
            continue
        junk = host_battery(dimension)[1]
        assert all(getattr(junk, name) == (JUNK_TOKEN,) for name in fields)


def test_check_written_after_the_answer_cannot_verify(tmp_path: Path) -> None:
    result = grade_and_apply(
        _program(),
        (_answer(_evidence(tmp_path), root=tmp_path),),
        evidence_roots={"orion": tmp_path},
        checks={"c": _storage_check(frozen_at_round=None)},
        round_index=1,
    )
    grading = result.gradings[0]
    assert grading.check_outcome is CheckOutcome.CHRONOLOGY_UNVERIFIED
    assert grading.authority is AnswerAuthority.EVIDENCE_BOUND


def test_a_lane_cannot_verify_its_own_answer(tmp_path: Path) -> None:
    result = grade_and_apply(
        _program(),
        (_answer(_evidence(tmp_path), root=tmp_path, lane="machine"),),
        evidence_roots={"orion": tmp_path},
        checks={"c": _storage_check(lane="machine")},
        round_index=1,
    )
    grading = result.gradings[0]
    assert grading.check_outcome is CheckOutcome.LANE_NOT_INDEPENDENT
    assert grading.authority is AnswerAuthority.EVIDENCE_BOUND


def test_unverified_waiver_is_refused(tmp_path: Path) -> None:
    """Waiver laundering: closing questions by declaring them inapplicable."""

    waiver = AnswerRecord(
        record_id="w1",
        mechanic_id=TARGET,
        dimension=MechanicDimension.STORAGE,
        lane="machine",
        evidence_refs=(waiver_ref := _evidence(tmp_path),),
        evidence_bindings=_binding(waiver_ref, tmp_path),
        waiver_reason="this step stores nothing",
    )
    cells = _program()
    before = observe_mechanics_program(cells)
    result = grade_and_apply(cells, (waiver,), evidence_roots={"orion": tmp_path})
    after = observe_mechanics_program(result.cells)

    assert result.gradings[0].authority is AnswerAuthority.REJECTED
    assert after.open_question_count == before.open_question_count


# --- durable state -------------------------------------------------------


def test_ledger_detects_a_silently_edited_history(tmp_path: Path) -> None:
    store = LedgerStore(tmp_path / "state")
    store.append(EntryKind.ROUND, {"round_index": 0})
    store.append(EntryKind.ROUND, {"round_index": 1})
    lines = store.path.read_text(encoding="utf-8").splitlines()
    lines[0] = lines[0].replace('"round_index":0', '"round_index":9')
    store.path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    assert store.verify()
    with pytest.raises(LedgerIntegrityError):
        store.entries()


def test_run_resumes_from_disk_in_a_fresh_process_state(tmp_path: Path) -> None:
    state = tmp_path / "state"
    ref = _evidence(tmp_path)
    checks = {"c": _storage_check()}

    first = SelfDrivingDriver(
        store=LedgerStore(state),
        source=StaticAnswerSource(records=(_answer(ref, root=tmp_path),)),
        evidence_roots={"orion": tmp_path},
        checks=checks,
        seed_cells=_program(),
        selection_limit=64,
    )
    first_report = first.run(max_rounds=1)
    assert first_report.rounds[0].application.verified_record_ids == ("a1",)

    # A completely new driver object, holding nothing but the ledger directory.
    resumed = SelfDrivingDriver(
        store=LedgerStore(state),
        source=StaticAnswerSource(records=()),
        evidence_roots={"orion": tmp_path},
        checks=checks,
        seed_cells=_program(),
        selection_limit=64,
    )
    cells = resumed.cells()
    target = next(item for item in cells if item.mechanic_id == TARGET)

    assert target.storage_contracts == ("append-only ledger entry per answer",)
    assert MechanicDimension.STORAGE not in target.provisional_dimensions
    assert resumed.store.completed_round_count() == 1


def test_resume_revalidates_evidence_that_changed_since_it_was_cited(
    tmp_path: Path,
) -> None:
    state = tmp_path / "state"
    ref = _evidence(tmp_path)
    checks = {"c": _storage_check()}
    SelfDrivingDriver(
        store=LedgerStore(state),
        source=StaticAnswerSource(records=(_answer(ref, root=tmp_path),)),
        evidence_roots={"orion": tmp_path},
        checks=checks,
        seed_cells=_program(),
        selection_limit=64,
    ).run(max_rounds=1)

    (tmp_path / "source.md").write_text("content was rewritten", encoding="utf-8")
    resumed = SelfDrivingDriver(
        store=LedgerStore(state),
        source=StaticAnswerSource(records=()),
        evidence_roots={"orion": tmp_path},
        checks=checks,
        seed_cells=_program(),
        selection_limit=64,
    )
    target = next(item for item in resumed.cells() if item.mechanic_id == TARGET)
    assert target.storage_contracts == ()


# --- failure learning that changes behavior ------------------------------


def test_repeated_unresolvable_evidence_produces_an_executable_guard(
    tmp_path: Path,
) -> None:
    store = LedgerStore(tmp_path / "state")
    cells = _program()
    for round_index in range(2):
        broken = tuple(
            AnswerRecord(
                record_id=f"bad-{round_index}-{index}",
                mechanic_id=TARGET,
                dimension=MechanicDimension.STORAGE,
                lane="machine",
                evidence_refs=(f"orion:ghost-{round_index}-{index}.md@abcdef123456",),
                evidence_bindings=(
                    (f"orion:ghost-{round_index}-{index}.md@abcdef123456", _UNRESOLVABLE_BINDING),
                ),
                payload=(("storage_contracts", (f"claim {index}",)),),
            )
            for index in range(2)
        )
        cells = run_round(
            cells,
            store=store,
            source=StaticAnswerSource(records=broken),
            evidence_roots={"orion": tmp_path},
            round_index=round_index,
            selection_limit=64,
        ).cells

    from orion.kernel.driver import learn_guards

    guards = learn_guards(store)
    assert guards, "repeated identical failures produced no guard"
    guard = guards[0]
    assert guard.effect is GuardEffect.REJECT_EVIDENCE_STATUS
    assert guard.argument == EvidenceStatus.MISSING_ARTIFACT.value
    assert guard.active, "a guard reproduced across distinct rounds must be active"


def test_an_active_guard_changes_what_the_next_round_selects() -> None:
    cell = MechanicCell(mechanic_id=TARGET, purpose="p", scope="s")
    questions = generate_mechanic_questions(cell)
    guard = GuardRule(
        guard_id="guard:pattern:x",
        pattern_id="pattern:x",
        effect=GuardEffect.DEPRIORITIZE_DIMENSION,
        argument=MechanicDimension.VERIFICATION.value,
        authority=LessonAuthority.VERIFIED_LOCAL,
        rationale="repeatedly unproductive",
    )
    baseline = tuple(item.question_id for item in questions)
    guarded = tuple(item.question_id for item in apply_selection_guards(questions, (guard,)))

    assert guarded != baseline, "an active guard did not change selection"
    assert set(guarded) == set(baseline), "a guard must reorder work, never delete it"
    assert guarded[-1].endswith(MechanicDimension.VERIFICATION.value)


def test_a_candidate_guard_does_not_change_behavior() -> None:
    cell = MechanicCell(mechanic_id=TARGET, purpose="p", scope="s")
    questions = generate_mechanic_questions(cell)
    candidate = GuardRule(
        guard_id="guard:pattern:x",
        pattern_id="pattern:x",
        effect=GuardEffect.DEPRIORITIZE_DIMENSION,
        argument=MechanicDimension.VERIFICATION.value,
        authority=LessonAuthority.CANDIDATE,
        rationale="seen once",
    )
    assert apply_selection_guards(questions, (candidate,)) == questions


def test_guard_withholds_a_matching_answer_in_the_next_round(tmp_path: Path) -> None:
    store = LedgerStore(tmp_path / "state")
    guard = GuardRule(
        guard_id="guard:pattern:t",
        pattern_id="pattern:t",
        effect=GuardEffect.REJECT_EVIDENCE_STATUS,
        argument=EvidenceStatus.MISSING_ARTIFACT.value,
        authority=LessonAuthority.VERIFIED_LOCAL,
        rationale="learned",
    )
    outcome = run_round(
        _program(),
        store=store,
        source=StaticAnswerSource(
            records=(
                AnswerRecord(
                    record_id="bad",
                    mechanic_id=TARGET,
                    dimension=MechanicDimension.STORAGE,
                    lane="machine",
                    evidence_refs=("orion:ghost.md@abcdef123456",),
                    evidence_bindings=(("orion:ghost.md@abcdef123456", _UNRESOLVABLE_BINDING),),
                    payload=(("storage_contracts", ("claim",)),),
                ),
            )
        ),
        evidence_roots={"orion": tmp_path},
        guards=(guard,),
        selection_limit=64,
    )
    assert outcome.guard_refusal_reasons
    assert outcome.after.open_question_count == outcome.before.open_question_count


# --- driver behavior -----------------------------------------------------


def test_driver_stops_on_bounded_flatness_rather_than_spinning(tmp_path: Path) -> None:
    report = SelfDrivingDriver(
        store=LedgerStore(tmp_path / "state"),
        source=StaticAnswerSource(records=()),
        evidence_roots={"orion": tmp_path},
        seed_cells=_program(),
        selection_limit=64,
    ).run(max_rounds=8)

    assert report.stop_reason == "flat_lineage_unidentified"
    assert len(report.rounds) == 2
    assert report.verified_closures == 0
    assert report.saturation is not None
    assert report.saturation.verdict is SaturationVerdict.PARTIALLY_IDENTIFIED_LINEAGE
    assert all(vector.flat for vector in report.growth)
    assert not report.saturation.may_stop
    # Bounded, never absolute: stopping is a statement about a declared basis.
    assert report.saturation.absolute_complete is False


def test_growth_in_any_coordinate_prevents_stopping(tmp_path: Path) -> None:
    report = SelfDrivingDriver(
        store=LedgerStore(tmp_path / "state"),
        source=StaticAnswerSource(records=(_answer(_evidence(tmp_path), root=tmp_path),)),
        evidence_roots={"orion": tmp_path},
        seed_cells=_program(),
        selection_limit=64,
    ).run(max_rounds=1)

    first = report.growth[0]
    assert not first.flat
    assert first.evidence_bound_additions == 1
    assert first.new_evidence_roots == 1
    assert report.saturation is not None
    assert report.saturation.verdict is not SaturationVerdict.A_PRIORI_FRAME_FLAT


def test_a_resumed_run_does_not_recount_its_own_history_as_growth(
    tmp_path: Path,
) -> None:
    """Growth is change. A resumed run re-reads the ledger, and must not treat
    the decomposition and evidence it already recorded as fresh discovery."""

    state = tmp_path / "state"
    ref = _evidence(tmp_path)
    first = SelfDrivingDriver(
        store=LedgerStore(state),
        source=StaticAnswerSource(records=(_answer(ref, root=tmp_path),)),
        evidence_roots={"orion": tmp_path},
        seed_cells=_program(),
        selection_limit=64,
    ).run(max_rounds=1)
    assert not first.growth[0].flat  # the original round really did discover things

    resumed = SelfDrivingDriver(
        store=LedgerStore(state),
        source=StaticAnswerSource(records=()),
        evidence_roots={"orion": tmp_path},
        seed_cells=_program(),
        selection_limit=64,
    ).run(max_rounds=2)

    assert all(vector.flat for vector in resumed.growth)
    # Flat, but nothing bound this run, so the rounds cannot testify to
    # each other. Stopping is right; calling it saturation would not be.
    assert resumed.stop_reason == "flat_lineage_unidentified"


def test_changing_the_basis_voids_earlier_flat_rounds() -> None:
    basis = SaturationBasis(
        root_mechanic_id=ORION_WORKFLOW_ROOT_ID,
        dimension_vocabulary=("STORAGE",),
        priority_order=("STORAGE",),
        evidence_schemes=("orion",),
        registered_check_ids=(),
        selection_limit=8,
    )
    flat = tuple(
        GrowthVector(
            round_index=index,
            basis_fingerprint=basis.fingerprint,
            evidence_lineage=(f"orion:round{index}.md@{index:012d}",),
        )
        for index in range(2)
    )
    assert assess_saturation(flat, basis).verdict is SaturationVerdict.A_PRIORI_FRAME_FLAT

    wider = SaturationBasis(
        root_mechanic_id=basis.root_mechanic_id,
        dimension_vocabulary=basis.dimension_vocabulary,
        priority_order=basis.priority_order,
        evidence_schemes=basis.evidence_schemes,
        registered_check_ids=("check:new",),
        selection_limit=basis.selection_limit,
    )
    assert assess_saturation(flat, wider).verdict is SaturationVerdict.INVALID_BASIS


def test_flat_rounds_resting_on_the_same_evidence_are_not_independent() -> None:
    basis = SaturationBasis(
        root_mechanic_id=ORION_WORKFLOW_ROOT_ID,
        dimension_vocabulary=("STORAGE",),
        priority_order=("STORAGE",),
        evidence_schemes=("orion",),
        registered_check_ids=(),
        selection_limit=8,
    )
    shared = tuple(
        GrowthVector(
            round_index=index,
            basis_fingerprint=basis.fingerprint,
            evidence_lineage=("orion:same.md@aaaaaaaaaaaa",),
        )
        for index in range(3)
    )
    report = assess_saturation(shared, basis)
    assert report.verdict is SaturationVerdict.DEPENDENT_FLAT_ROUNDS
    assert report.independent_flat_rounds == 1


def test_directory_source_serves_each_record_once(tmp_path: Path) -> None:
    inbox = tmp_path / "answers" / "machine"
    inbox.mkdir(parents=True)
    ref = _evidence(tmp_path)
    record = {
        "record_id": "a1",
        "mechanic_id": TARGET,
        "dimension": "STORAGE",
        "evidence_refs": [ref],
        "evidence_bindings": dict(_binding(ref, tmp_path)),
        "payload": {"storage_contracts": ["append-only ledger entry per answer"]},
    }
    inbox.joinpath(f"{TARGET}.jsonl").write_text(
        json.dumps(record) + "\n", encoding="utf-8"
    )
    source = DirectoryAnswerSource(root=tmp_path / "answers")
    driver = SelfDrivingDriver(
        store=LedgerStore(tmp_path / "state"),
        source=source,
        evidence_roots={"orion": tmp_path},
        checks={"c": _storage_check()},
        seed_cells=_program(),
        selection_limit=64,
    )
    report = driver.run(max_rounds=3)

    assert report.verified_closures == 1
    assert report.rounds[1].fetched_record_ids == ()


def test_the_stopping_verdict_never_certifies_recall(tmp_path: Path) -> None:
    """The rule implemented here is a heuristic with three prior names.

    Francis et al.'s "10+3", Guest/Namey/Chen's 0% new-information threshold,
    and TAR's IH50 are the same rule. Guest et al. bootstrap the 0% threshold at
    87-89% of themes captured; Callaghan et al. (2024) measured 5th-percentile
    recall of 53% for this family. A run may stop on it — it may not claim
    coverage from it.
    """

    report = SelfDrivingDriver(
        store=LedgerStore(tmp_path / "state"),
        source=StaticAnswerSource(records=()),
        evidence_roots={"orion": tmp_path},
        seed_cells=_program(),
        selection_limit=64,
    ).run(max_rounds=8)

    assert report.stop_reason == "flat_lineage_unidentified"
    assert report.saturation is not None
    assert not report.saturation.certifies_recall
    assert not report.saturation.absolute_complete
    # The reason now names the deeper problem: the flat rounds bound nothing,
    # so they cannot corroborate each other at all — a weaker claim than
    # "flat within a declared frame", and the honest one here.
    assert any("no evidence lineage" in item for item in report.saturation.reasons)


def test_one_paper_reached_by_two_references_counts_as_one_discovery(
    tmp_path: Path,
) -> None:
    """The noisy-TV defect, in ORION's own growth vector.

    Counting reference strings lets any source that re-mints identifiers — a
    mirror, a re-crawl, a live search API — manufacture growth forever, so the
    novelty signal can never fall to zero and saturation is unreachable for the
    wrong reason. Growth is counted over content digests instead.
    """

    body = "the same underlying paper"
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    (tmp_path / "primary.md").write_text(body, encoding="utf-8")
    (tmp_path / "mirror.md").write_text(body, encoding="utf-8")

    records = tuple(
        AnswerRecord(
            record_id=f"a{index}",
            mechanic_id=TARGET,
            dimension=MechanicDimension.STORAGE,
            lane="machine",
            evidence_refs=(ref,),
            evidence_bindings=_binding(ref, tmp_path),
            payload=(("storage_contracts", (f"claim {index}",)),),
        )
        for index, ref in enumerate(
            (f"orion:primary.md@{digest[:12]}", f"orion:mirror.md@{digest[:12]}")
        )
    )
    # Two distinct references, identical bytes behind them.
    assert records[0].evidence_refs != records[1].evidence_refs

    report = SelfDrivingDriver(
        store=LedgerStore(tmp_path / "state"),
        source=StaticAnswerSource(records=records),
        evidence_roots={"orion": tmp_path},
        seed_cells=_program(),
        selection_limit=64,
    ).run(max_rounds=1)

    assert report.growth[0].new_evidence_roots == 1


def test_a_starved_selection_window_is_not_reported_as_flatness(tmp_path: Path) -> None:
    """FALSE_FLATNESS_BY_STARVATION, measured by another lane and confirmed here.

    The fixed breadth-first priority feeds the selection window from the top
    dimensions, so a narrow window never reaches the lower ones and never asks
    the source for them. Nothing about the knowledge is flat — the window is.
    A run that called that saturation would be reporting its own scheduling as
    a property of the world.
    """

    ref = _evidence(tmp_path)
    # An answer the window will not reach: STORAGE sits far down the priority order.
    withheld = _answer(ref, root=tmp_path, record_id="unreached")
    report = SelfDrivingDriver(
        store=LedgerStore(tmp_path / "state"),
        source=StaticAnswerSource(records=(withheld,)),
        evidence_roots={"orion": tmp_path},
        seed_cells=_program(),
        selection_limit=1,
    ).run(max_rounds=4)

    assert report.stop_reason == "selection_window_exhausted"


def test_a_source_that_cannot_be_probed_does_not_license_a_flat_claim(
    tmp_path: Path,
) -> None:
    """Unknown source coverage is not verified source coverage."""

    class _Opaque:
        def fetch(self, tasks, cells, round_index):
            return ()

    report = SelfDrivingDriver(
        store=LedgerStore(tmp_path / "state"),
        source=_Opaque(),
        evidence_roots={"orion": tmp_path},
        seed_cells=_program(),
        selection_limit=64,
    ).run(max_rounds=4)

    assert report.stop_reason == "flat_source_coverage_unverified"
