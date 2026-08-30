"""Tests for the P1-P10 superiority terminal battery.

Two disciplines, both inherited from ``test_anti_collapse_battery.py``:

1. **Every check has a negative fixture.** ``SuperiorityCheck`` names the test
   that shows it rejecting something, and ``test_every_check_names_a_live_fixture``
   proves each named test actually exists in this module. A check that has never
   exhibited a failing case of its own is not demonstrably failable.
2. **The no-alarm case is asserted too.** ``clean_ledger`` is a fully discharged
   programme on which every check must pass. A battery that fires on a healthy
   ledger gets switched off, and a switched-off battery detects nothing.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from orion.programme.checks_superiority import (
    CANNOT_CHECK_LAUNDERING,
    CLAIM_WIDER_THAN_EVIDENCE,
    COMPENSATORY_SCORING,
    DONOR_INCOMPLETE_COMPARATOR,
    MANUSCRIPT_SUBSTITUTION,
    MECHANISM_SUBSTITUTION,
    POST_HOC_FREEZE,
    PREDECESSOR_REUSE,
    SELF_CERTIFICATION,
    SPLIT_PAPER_IDENTITY,
    STALE_PAPER_IDENTITY,
    SUPERIORITY_CHECKS,
    TERMINAL_COVERAGE,
    THIN_REPLICATION,
    UNCLASSIFIED_BLOCKER,
    paper_identity_findings,
    split_identity_findings,
    run_superiority_checks,
    validate_superiority_catalogue,
)
from orion.programme.identity import verify_seal
from orion.programme.programme_state import CANDIDATE_CUSTODY, EXTERNAL_CUSTODY
from orion.programme.records import Outcome
from orion.programme.superiority import (
    ADMISSIBLE_GRADES,
    SUPERIORITY_LEDGER_SCHEMA,
    Actionability,
    ClaimScope,
    EvidenceGrade,
    GateBlocker,
    GateEvidence,
    PaperSuperiorityRecord,
    PaperTerminalStatus,
    PredecessorArtifact,
    ResponsibilityClass,
    TerminalKind,
    adjudicate,
)
from orion.programme.superiority_ledger import (
    LedgerBindingError,
    SuperiorityLedger,
    ledger_from_payload,
    ledger_to_payload,
)
from orion.programme.superiority_report import (
    EXIT_CANNOT_CHECK,
    EXIT_MALFORMED,
    EXIT_NOT_EARNED,
    build_report,
    main,
)
from orion.programme.superiority_terminals import (
    ALL_GATES,
    FUTURE_PAPER_DIRECTORIES,
    FUTURE_RETIRED_PAPER_DIRECTORIES,
    PAPER_DIRECTORIES,
    PAPER_DIRECTORIES_BY_ID,
    PAPER_GATES,
    PAPER_ISSUES,
    REGISTERED_PAPER_DIRECTORIES,
    RETIRED_PAPER_NUMBERING,
    SHARED_LANES,
    VACATED_PAPER_NUMBERS,
    validate_registry,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
LEDGER_PATH = REPO_ROOT / "research/paper-programme-v1/P1_P10_SUPERIORITY_TERMINAL_LEDGER_V1.json"
REPORT_PATH = (
    REPO_ROOT / "research/paper-programme-v1/P1_P10_SUPERIORITY_TERMINAL_REPORT_2026-08-21.json"
)


def _discharging_evidence(gate) -> GateEvidence:
    """The weakest evidence that legitimately discharges ``gate``."""

    if gate.kind is TerminalKind.FORMAL_GENERALIZATION:
        return GateEvidence(
            gate_id=gate.gate_id,
            grade=EvidenceGrade.MECHANIZED_THEOREM,
            artifact_refs=(f"proofs/{gate.gate_id}.v",),
        )
    if gate.kind is TerminalKind.INDEPENDENT_REVIEW:
        return GateEvidence(
            gate_id=gate.gate_id,
            grade=EvidenceGrade.MECHANIZED_THEOREM,
            artifact_refs=(f"proofs/{gate.gate_id}.v", f"reviews/{gate.gate_id}.md"),
            independent_implementation=True,
        )
    if gate.kind in (TerminalKind.SCOPE_DISCIPLINE, TerminalKind.SCOPE_EXPANSION):
        return GateEvidence(
            gate_id=gate.gate_id,
            grade=EvidenceGrade.PROSPECTIVE_PROTECTED,
            artifact_refs=(f"claims/{gate.gate_id}.md",),
            declared_scope=ClaimScope.GENERAL_PROSPECTIVE,
        )

    guards = tuple(
        other.gate_id
        for other in PAPER_GATES[gate.paper_id]
        if other.kind is TerminalKind.HARM_GUARD
    )
    return GateEvidence(
        gate_id=gate.gate_id,
        grade=EvidenceGrade.PROSPECTIVE_PROTECTED,
        artifact_refs=(f"results/{gate.gate_id}.json",),
        protocol_frozen_before_outcome=True,
        comparator_donor_complete=True,
        evaluator_custody=EXTERNAL_CUSTODY,
        domains=("chemistry", "epidemiology"),
        independent_implementation=True,
        harm_guard_gate_ids=guards,
    )


@pytest.fixture
def clean_ledger() -> SuperiorityLedger:
    """A hypothetical fully-discharged programme. Not repository content."""

    return SuperiorityLedger(
        ledger_id="clean-fixture",
        frozen_at="2026-08-21",
        papers=tuple(
            PaperSuperiorityRecord(
                paper_id=paper_id,
                issue_number=PAPER_ISSUES[paper_id],
                gates=gates,
                evidence=tuple(_discharging_evidence(gate) for gate in gates),
                declared_claim_scope=ClaimScope.GENERAL_PROSPECTIVE,
            )
            for paper_id, gates in PAPER_GATES.items()
        ),
    )


def _mutate(ledger: SuperiorityLedger, paper_id: str, **changes) -> SuperiorityLedger:
    papers = tuple(
        replace(paper, **changes) if paper.paper_id == paper_id else paper
        for paper in ledger.papers
    )
    return replace(ledger, papers=papers)


def _replace_evidence(
    ledger: SuperiorityLedger, paper_id: str, gate_id: str, **changes
) -> SuperiorityLedger:
    paper = ledger.paper(paper_id)
    assert paper is not None
    evidence = tuple(
        replace(item, **changes) if item.gate_id == gate_id else item for item in paper.evidence
    )
    return _mutate(ledger, paper_id, evidence=evidence)


def _result(ledger: SuperiorityLedger, check_id: str):
    report = run_superiority_checks(ledger)
    matches = [result for result in report.results if result.check_id == check_id]
    assert matches, f"{check_id} did not run"
    return matches[0]


def _gate_of_kind(paper_id: str, kind: TerminalKind):
    for gate in PAPER_GATES[paper_id]:
        if gate.kind is kind:
            return gate
    raise AssertionError(f"{paper_id} declares no {kind.value} gate")


# --- registry and framework ---------------------------------------------------


def test_registry_is_structurally_intact() -> None:
    assert validate_registry() == ()
    assert validate_superiority_catalogue() == ()


def test_registry_covers_all_ten_papers_and_gate_ids_are_unique() -> None:
    assert set(PAPER_GATES) == set(PAPER_ISSUES)
    assert len(PAPER_GATES) == 10
    gate_ids = [gate.gate_id for gate in ALL_GATES]
    assert len(gate_ids) == len(set(gate_ids))
    assert len(gate_ids) == 51


def test_every_check_names_a_live_fixture() -> None:
    """A named negative fixture that does not exist is not a negative fixture."""

    module_source = Path(__file__).read_text(encoding="utf-8")
    for check in SUPERIORITY_CHECKS:
        path, _, test_name = check.negative_fixture_id.partition("::")
        assert path.endswith("test_superiority_gates.py"), check.check_id
        assert f"def {test_name}(" in module_source, (
            f"{check.check_id} names missing fixture {check.negative_fixture_id}"
        )


def test_a_raising_check_cannot_check_rather_than_passes() -> None:
    from orion.programme.checks_superiority import SuperiorityCheck

    def explode(_ledger):  # pragma: no cover - body never returns
        raise RuntimeError("boom")

    check = SuperiorityCheck(
        check_id="HC-SUP-EXPLODES",
        title="t",
        failure_class="f",
        negative_fixture_id="tests/unit/programme/test_superiority_gates.py::test_a_raising_check_cannot_check_rather_than_passes",
        evaluate=explode,
    )
    result = check.run(
        SuperiorityLedger(ledger_id="x", frozen_at="2026-08-21", papers=())
    )
    assert result.outcome is Outcome.CANNOT_CHECK
    assert "RuntimeError" in result.reason


def test_empty_report_blocks() -> None:
    ledger = SuperiorityLedger(ledger_id="x", frozen_at="2026-08-21", papers=())
    assert run_superiority_checks(ledger, checks=()).blocked is True


# --- the no-alarm case --------------------------------------------------------


def test_clean_ledger_passes_every_check(clean_ledger: SuperiorityLedger) -> None:
    report = run_superiority_checks(clean_ledger)
    offenders = [
        (result.check_id, result.outcome.value, result.reason)
        for result in report.results
        if result.blocks
    ]
    assert offenders == []
    assert report.blocked is False


def test_clean_ledger_earns_every_terminal(clean_ledger: SuperiorityLedger) -> None:
    assert set(clean_ledger.terminals().values()) == {PaperTerminalStatus.EARNED}
    report = build_report(clean_ledger)
    assert report["overall_terminal"] == PaperTerminalStatus.EARNED.value
    assert report["grants_issue_closure"] is False


# --- adjudication semantics ---------------------------------------------------


def test_absent_evidence_blocks_without_failing() -> None:
    gate = _gate_of_kind("P1", TerminalKind.PROTECTED_SUPERIORITY)
    assert adjudicate(gate, None).outcome is Outcome.CANNOT_CHECK


def test_unrecorded_precondition_cannot_check_rather_than_fails() -> None:
    gate = _gate_of_kind("P2", TerminalKind.PROTECTED_SUPERIORITY)
    evidence = GateEvidence(
        gate_id=gate.gate_id,
        grade=EvidenceGrade.PROSPECTIVE_PROTECTED,
        artifact_refs=("r.json",),
        protocol_frozen_before_outcome=True,
        evaluator_custody=EXTERNAL_CUSTODY,
    )
    status = adjudicate(gate, evidence)
    assert status.outcome is Outcome.CANNOT_CHECK
    assert "donor-complete" in status.reason


def test_violated_precondition_fails_rather_than_cannot_check() -> None:
    gate = _gate_of_kind("P2", TerminalKind.PROTECTED_SUPERIORITY)
    evidence = GateEvidence(
        gate_id=gate.gate_id,
        grade=EvidenceGrade.PROSPECTIVE_PROTECTED,
        artifact_refs=("r.json",),
        protocol_frozen_before_outcome=True,
        comparator_donor_complete=False,
        evaluator_custody=EXTERNAL_CUSTODY,
    )
    assert adjudicate(gate, evidence).outcome is Outcome.FAIL


def test_a_guard_without_a_comparator_still_discharges() -> None:
    """Donor-completeness is a superiority precondition, not a universal one.

    #649's no-regression guard is a ceiling on the system's own behaviour and has
    no comparator to be complete about. Demanding one would park it at
    CANNOT_CHECK forever, or invite a `true` that means nothing.
    """

    guard = _gate_of_kind("P1", TerminalKind.HARM_GUARD)
    evidence = GateEvidence(
        gate_id=guard.gate_id,
        grade=EvidenceGrade.BOUNDED_PROTECTED,
        artifact_refs=("guards/regression.json",),
        protocol_frozen_before_outcome=True,
        evaluator_custody=EXTERNAL_CUSTODY,
    )
    assert adjudicate(guard, evidence).outcome is Outcome.PASS

    superiority = _gate_of_kind("P1", TerminalKind.PROTECTED_SUPERIORITY)
    same_gaps = replace(
        evidence, gate_id=superiority.gate_id, grade=EvidenceGrade.PROSPECTIVE_PROTECTED
    )
    assert adjudicate(superiority, same_gaps).outcome is Outcome.CANNOT_CHECK


def test_bounded_protected_cannot_discharge_a_superiority_gate() -> None:
    gate = _gate_of_kind("P3", TerminalKind.PROTECTED_SUPERIORITY)
    evidence = GateEvidence(
        gate_id=gate.gate_id,
        grade=EvidenceGrade.BOUNDED_PROTECTED,
        artifact_refs=("r.json",),
        protocol_frozen_before_outcome=True,
        comparator_donor_complete=True,
        evaluator_custody=EXTERNAL_CUSTODY,
    )
    status = adjudicate(gate, evidence)
    assert status.outcome is Outcome.FAIL
    assert "cannot discharge" in status.reason


def test_bounded_terminal_disjunct_is_honoured_where_the_issue_offers_one() -> None:
    """#662 and #663 each offer a narrower disjunct; no other gate does."""

    bounded = GateEvidence(
        gate_id="P9-U-T2",
        grade=EvidenceGrade.BOUNDED_PROTECTED,
        artifact_refs=("r.json",),
        protocol_frozen_before_outcome=True,
        comparator_donor_complete=True,
        evaluator_custody=EXTERNAL_CUSTODY,
        domains=("lean", "procedural"),
        independent_implementation=True,
    )
    p9_t2 = next(gate for gate in PAPER_GATES["P9"] if gate.gate_id == "P9-U-T2")
    assert adjudicate(p9_t2, bounded).outcome is Outcome.PASS

    p1_t2 = next(gate for gate in PAPER_GATES["P1"] if gate.gate_id == "P1-U-T2")
    assert adjudicate(p1_t2, replace(bounded, gate_id="P1-U-T2")).outcome is Outcome.FAIL


def test_scope_expansion_is_not_satisfied_by_a_correctly_narrow_claim() -> None:
    """#649's fourth bullet asks for a *wider* claim, not a disciplined one."""

    record = PaperSuperiorityRecord(
        paper_id="P1",
        issue_number=PAPER_ISSUES["P1"],
        gates=PAPER_GATES["P1"],
        predecessor_artifacts=(
            PredecessorArtifact(
                artifact_ref="p1x.md", grade=EvidenceGrade.MECHANISM_NON_VACUITY
            ),
        ),
        declared_claim_scope=ClaimScope.BOUNDED_EXACT,
    )
    status = next(item for item in record.statuses() if item.gate_id == "P1-U-T4")
    assert status.outcome is Outcome.CANNOT_CHECK
    assert "wider" in status.reason


def test_terminal_is_non_compensatory() -> None:
    """One failed guard sinks the terminal however many wins stand beside it."""

    gates = PAPER_GATES["P5"]
    guard = _gate_of_kind("P5", TerminalKind.HARM_GUARD)
    evidence = []
    for gate in gates:
        item = _discharging_evidence(gate)
        if gate.gate_id == guard.gate_id:
            item = replace(item, protocol_frozen_before_outcome=False)
        evidence.append(item)
    record = PaperSuperiorityRecord(
        paper_id="P5",
        issue_number=PAPER_ISSUES["P5"],
        gates=gates,
        evidence=tuple(evidence),
        declared_claim_scope=ClaimScope.GENERAL_PROSPECTIVE,
    )
    assert record.terminal() is PaperTerminalStatus.NOT_EARNED


def test_predecessor_licenses_scope_without_discharging_a_gate() -> None:
    record = PaperSuperiorityRecord(
        paper_id="P6",
        issue_number=PAPER_ISSUES["P6"],
        gates=PAPER_GATES["P6"],
        predecessor_artifacts=(
            PredecessorArtifact(
                artifact_ref="p6x.md", grade=EvidenceGrade.MECHANISM_NON_VACUITY
            ),
        ),
        declared_claim_scope=ClaimScope.BOUNDED_EXACT,
    )
    assert record.strongest_grade is EvidenceGrade.MECHANISM_NON_VACUITY
    assert record.terminal() is PaperTerminalStatus.CANNOT_CHECK
    assert all(status.outcome is not Outcome.PASS for status in record.statuses())


# --- one negative fixture per check ------------------------------------------


def test_coverage_blocks_on_missing_paper(clean_ledger: SuperiorityLedger) -> None:
    partial = replace(clean_ledger, papers=clean_ledger.papers[:-1])
    result = _result(partial, TERMINAL_COVERAGE)
    assert result.outcome is Outcome.CANNOT_CHECK
    assert "P10" in result.reason


def test_coverage_fails_on_gate_list_drift(clean_ledger: SuperiorityLedger) -> None:
    drifted = _mutate(clean_ledger, "P4", gates=PAPER_GATES["P4"][:-1])
    result = _result(drifted, TERMINAL_COVERAGE)
    assert result.outcome is Outcome.FAIL


def test_manuscript_substitution_fails(clean_ledger: SuperiorityLedger) -> None:
    gate = _gate_of_kind("P1", TerminalKind.PROTECTED_SUPERIORITY)
    ledger = _replace_evidence(
        clean_ledger,
        "P1",
        gate.gate_id,
        grade=EvidenceGrade.MANUSCRIPT_COMPLETION,
        artifact_refs=("papers/p1/manuscript/FINAL.tex",),
    )
    result = _result(ledger, MANUSCRIPT_SUBSTITUTION)
    assert result.outcome is Outcome.FAIL
    assert any(gate.gate_id in finding for finding in result.findings)


def test_mechanism_substitution_fails(clean_ledger: SuperiorityLedger) -> None:
    gate = _gate_of_kind("P2", TerminalKind.PROTECTED_SUPERIORITY)
    ledger = _replace_evidence(
        clean_ledger,
        "P2",
        gate.gate_id,
        grade=EvidenceGrade.MECHANISM_NON_VACUITY,
        artifact_refs=("research/claim_expansion/p2/P2_X_FINAL_SCIENTIFIC_TERMINAL_V1.md",),
    )
    result = _result(ledger, MECHANISM_SUBSTITUTION)
    assert result.outcome is Outcome.FAIL


def test_cannot_check_laundering_fails(clean_ledger: SuperiorityLedger) -> None:
    gate = _gate_of_kind("P1", TerminalKind.SUCCESSOR_MECHANIC)
    ledger = _replace_evidence(
        clean_ledger,
        "P1",
        gate.gate_id,
        grade=EvidenceGrade.CANNOT_CHECK,
        artifact_refs=("development/p1-u-gpt-r3-source-universe/DEVELOPMENT_PACKET.md",),
    )
    result = _result(ledger, CANNOT_CHECK_LAUNDERING)
    assert result.outcome is Outcome.FAIL


def test_donor_incomplete_comparator_fails(clean_ledger: SuperiorityLedger) -> None:
    gate = _gate_of_kind("P4", TerminalKind.PROTECTED_SUPERIORITY)
    ledger = _replace_evidence(
        clean_ledger, "P4", gate.gate_id, comparator_donor_complete=False
    )
    result = _result(ledger, DONOR_INCOMPLETE_COMPARATOR)
    assert result.outcome is Outcome.FAIL


def test_donor_incomplete_comparator_cannot_check_when_unrecorded(
    clean_ledger: SuperiorityLedger,
) -> None:
    gate = _gate_of_kind("P4", TerminalKind.PROTECTED_SUPERIORITY)
    ledger = _replace_evidence(
        clean_ledger, "P4", gate.gate_id, comparator_donor_complete=None
    )
    assert _result(ledger, DONOR_INCOMPLETE_COMPARATOR).outcome is Outcome.CANNOT_CHECK


def test_compensatory_scoring_fails(clean_ledger: SuperiorityLedger) -> None:
    """A standing win beside a guard that no longer passes."""

    guard = _gate_of_kind("P3", TerminalKind.HARM_GUARD)
    ledger = _replace_evidence(
        clean_ledger,
        "P3",
        guard.gate_id,
        grade=EvidenceGrade.MECHANISM_NON_VACUITY,
    )
    result = _result(ledger, COMPENSATORY_SCORING)
    assert result.outcome is Outcome.FAIL
    assert any(guard.gate_id in finding for finding in result.findings)


def test_compensatory_scoring_fails_on_dangling_guard_reference(
    clean_ledger: SuperiorityLedger,
) -> None:
    gate = _gate_of_kind("P1", TerminalKind.PROTECTED_SUPERIORITY)
    ledger = _replace_evidence(
        clean_ledger, "P1", gate.gate_id, harm_guard_gate_ids=("P1-U-T99",)
    )
    result = _result(ledger, COMPENSATORY_SCORING)
    assert result.outcome is Outcome.FAIL
    assert any("P1-U-T99" in finding for finding in result.findings)


def test_thin_replication_fails(clean_ledger: SuperiorityLedger) -> None:
    gate = _gate_of_kind("P2", TerminalKind.REPLICATION)
    ledger = _replace_evidence(clean_ledger, "P2", gate.gate_id, domains=("chemistry",))
    result = _result(ledger, THIN_REPLICATION)
    assert result.outcome is Outcome.FAIL


def test_thin_replication_fails_on_repeated_domains(clean_ledger: SuperiorityLedger) -> None:
    gate = _gate_of_kind("P2", TerminalKind.REPLICATION)
    ledger = _replace_evidence(
        clean_ledger, "P2", gate.gate_id, domains=("chemistry", "chemistry", "biology")
    )
    result = _result(ledger, THIN_REPLICATION)
    assert result.outcome is Outcome.FAIL
    assert "only 2 are distinct" in result.findings[0]


def test_post_hoc_freeze_fails(clean_ledger: SuperiorityLedger) -> None:
    gate = _gate_of_kind("P5", TerminalKind.PROTECTED_SUPERIORITY)
    ledger = _replace_evidence(
        clean_ledger, "P5", gate.gate_id, protocol_frozen_before_outcome=False
    )
    result = _result(ledger, POST_HOC_FREEZE)
    assert result.outcome is Outcome.FAIL


def test_self_certification_fails(clean_ledger: SuperiorityLedger) -> None:
    gate = _gate_of_kind("P5", TerminalKind.PROTECTED_SUPERIORITY)
    ledger = _replace_evidence(
        clean_ledger, "P5", gate.gate_id, evaluator_custody=CANDIDATE_CUSTODY
    )
    result = _result(ledger, SELF_CERTIFICATION)
    assert result.outcome is Outcome.FAIL


def test_predecessor_reuse_fails(clean_ledger: SuperiorityLedger) -> None:
    """A grade is an assertion; the artifact path is a fact."""

    gate = _gate_of_kind("P8", TerminalKind.PROTECTED_SUPERIORITY)
    ledger = _mutate(
        clean_ledger,
        "P8",
        predecessor_artifacts=(
            PredecessorArtifact(
                artifact_ref="research/claim_expansion/p8/P8_X4_SCIENCE_TERMINAL_V1.md",
                grade=EvidenceGrade.MECHANISM_NON_VACUITY,
            ),
        ),
    )
    ledger = _replace_evidence(
        ledger,
        "P8",
        gate.gate_id,
        artifact_refs=("research/claim_expansion/p8/P8_X4_SCIENCE_TERMINAL_V1.md",),
    )
    result = _result(ledger, PREDECESSOR_REUSE)
    assert result.outcome is Outcome.FAIL
    # The declared grade is still PROSPECTIVE_PROTECTED, so the grade-reading
    # checks stay quiet. Only the path-reading check catches this.
    assert _result(ledger, MECHANISM_SUBSTITUTION).outcome is Outcome.PASS


def test_claim_wider_than_evidence_fails(clean_ledger: SuperiorityLedger) -> None:
    stripped = _mutate(
        clean_ledger,
        "P7",
        evidence=(),
        predecessor_artifacts=(
            PredecessorArtifact(
                artifact_ref="p7x.md", grade=EvidenceGrade.MECHANISM_NON_VACUITY
            ),
        ),
    )
    result = _result(stripped, CLAIM_WIDER_THAN_EVIDENCE)
    assert result.outcome is Outcome.FAIL
    assert "GENERAL_PROSPECTIVE" in result.findings[0]


def test_claim_wider_than_evidence_cannot_check_when_scope_unrecorded(
    clean_ledger: SuperiorityLedger,
) -> None:
    ledger = _mutate(clean_ledger, "P7", declared_claim_scope=None)
    assert _result(ledger, CLAIM_WIDER_THAN_EVIDENCE).outcome is Outcome.CANNOT_CHECK


# --- ledger binding -----------------------------------------------------------


def test_ledger_refuses_an_unknown_gate_id() -> None:
    payload = {
        "schema_version": SUPERIORITY_LEDGER_SCHEMA,
        "ledger_id": "x",
        "frozen_at": "2026-08-21",
        "papers": [
            {"paper_id": "P1", "evidence": [{"gate_id": "P1-U-T99", "grade": "ABSENT"}]}
        ],
    }
    with pytest.raises(LedgerBindingError, match="unknown gate id"):
        ledger_from_payload(payload)


def test_ledger_refuses_a_wrong_schema_version() -> None:
    with pytest.raises(LedgerBindingError, match="schema_version"):
        ledger_from_payload({"schema_version": "nope", "ledger_id": "x", "frozen_at": "y"})


def test_ledger_refuses_duplicate_evidence_for_one_gate() -> None:
    entry = {"gate_id": "P1-U-T1", "grade": "ABSENT"}
    payload = {
        "schema_version": SUPERIORITY_LEDGER_SCHEMA,
        "ledger_id": "x",
        "frozen_at": "2026-08-21",
        "papers": [{"paper_id": "P1", "evidence": [entry, dict(entry)]}],
    }
    with pytest.raises(LedgerBindingError, match="two pieces of evidence"):
        ledger_from_payload(payload)


def test_ledger_refuses_a_grade_claimed_without_an_artifact() -> None:
    payload = {
        "schema_version": SUPERIORITY_LEDGER_SCHEMA,
        "ledger_id": "x",
        "frozen_at": "2026-08-21",
        "papers": [
            {
                "paper_id": "P1",
                "evidence": [{"gate_id": "P1-U-T1", "grade": "PROSPECTIVE_PROTECTED"}],
            }
        ],
    }
    with pytest.raises(LedgerBindingError, match="without naming an artifact"):
        ledger_from_payload(payload)


def test_ledger_round_trips(clean_ledger: SuperiorityLedger) -> None:
    assert ledger_from_payload(ledger_to_payload(clean_ledger)) == clean_ledger


# --- the committed repository ledger -----------------------------------------


def test_committed_ledger_binds_and_blocks() -> None:
    """The real ledger is CANNOT_CHECK: nothing established, nothing refuted."""

    ledger = ledger_from_payload(json.loads(LEDGER_PATH.read_text(encoding="utf-8")))
    assert set(ledger.paper_ids) == set(PAPER_GATES)
    assert ledger.missing_paper_ids == ()

    report = build_report(ledger)
    assert report["overall_terminal"] == PaperTerminalStatus.CANNOT_CHECK.value
    assert report["grants_issue_closure"] is False
    # No substitution is currently being made anywhere in the ledger, and the
    # report still blocks. Those are different facts and both must hold.
    assert report["battery"]["blocked"] is False


def test_committed_ledger_cites_artifacts_that_exist() -> None:
    ledger = ledger_from_payload(json.loads(LEDGER_PATH.read_text(encoding="utf-8")))
    missing = [
        item.artifact_ref
        for paper in ledger.papers
        for item in paper.predecessor_artifacts
        if not (REPO_ROOT / item.artifact_ref).exists()
    ] + [
        ref
        for paper in ledger.papers
        for item in paper.evidence
        for ref in item.artifact_refs
        if not (REPO_ROOT / ref).exists()
    ]
    assert missing == []


def test_committed_report_matches_a_fresh_run() -> None:
    """The committed report is derived; drift from the ledger is a defect."""

    ledger = ledger_from_payload(json.loads(LEDGER_PATH.read_text(encoding="utf-8")))
    committed = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    assert verify_seal(committed) == ()
    assert build_report(ledger) == committed


def test_cli_reports_cannot_check_on_the_committed_ledger(tmp_path: Path) -> None:
    out = tmp_path / "report.json"
    code = main(["--ledger", str(LEDGER_PATH), "--out", str(out), "--quiet"])
    assert code == EXIT_CANNOT_CHECK
    assert verify_seal(json.loads(out.read_text(encoding="utf-8"))) == ()


def test_cli_reports_malformed_ledger_distinctly(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text('{"schema_version": "nope"}', encoding="utf-8")
    assert main(["--ledger", str(bad), "--quiet"]) == EXIT_MALFORMED
    assert main(["--ledger", str(tmp_path / "absent.json"), "--quiet"]) == EXIT_MALFORMED


def test_cli_reports_a_real_negative_distinctly(
    tmp_path: Path, clean_ledger: SuperiorityLedger
) -> None:
    gate = _gate_of_kind("P1", TerminalKind.PROTECTED_SUPERIORITY)
    broken = _replace_evidence(
        clean_ledger, "P1", gate.gate_id, comparator_donor_complete=False
    )
    path = tmp_path / "ledger.json"
    path.write_text(json.dumps(ledger_to_payload(broken)), encoding="utf-8")
    assert main(["--ledger", str(path), "--quiet"]) == EXIT_NOT_EARNED


# --- blockers: every CANNOT_CHECK is a classified task ------------------------


def _blocker(gate_id: str, actionability: Actionability) -> GateBlocker:
    return GateBlocker(
        gate_id=gate_id,
        responsibility=ResponsibilityClass.IMPLEMENTATION_OR_ENVIRONMENT,
        actionability=actionability,
        statement="something is blocking",
        unblock="do the thing",
    )


def test_unclassified_blocker_fails() -> None:
    """A blocked terminal with no stated cause cannot be worked."""

    record = PaperSuperiorityRecord(
        paper_id="P1",
        issue_number=PAPER_ISSUES["P1"],
        gates=PAPER_GATES["P1"],
        declared_claim_scope=ClaimScope.BOUNDED_EXACT,
    )
    ledger = SuperiorityLedger(
        ledger_id="x", frozen_at="2026-08-21", papers=(record,)
    )
    result = _result(ledger, UNCLASSIFIED_BLOCKER)
    assert result.outcome is Outcome.FAIL
    assert "P1-U-T1" in result.findings[0]


def test_a_fully_classified_ledger_passes_the_blocker_check() -> None:
    record = PaperSuperiorityRecord(
        paper_id="P1",
        issue_number=PAPER_ISSUES["P1"],
        gates=PAPER_GATES["P1"],
        declared_claim_scope=ClaimScope.BOUNDED_EXACT,
        blockers=tuple(
            _blocker(gate.gate_id, Actionability.BLOCKED_ON_CAMPAIGN)
            for gate in PAPER_GATES["P1"]
        ),
    )
    ledger = SuperiorityLedger(ledger_id="x", frozen_at="2026-08-21", papers=(record,))
    assert _result(ledger, UNCLASSIFIED_BLOCKER).outcome is Outcome.PASS


def test_an_unblocked_ledger_has_nothing_to_classify(
    clean_ledger: SuperiorityLedger,
) -> None:
    result = _result(clean_ledger, UNCLASSIFIED_BLOCKER)
    assert result.outcome is Outcome.PASS
    assert "nothing to classify" in result.reason


def test_work_queue_is_ordered_by_actionability_then_stable() -> None:
    gates = PAPER_GATES["P1"]
    record = PaperSuperiorityRecord(
        paper_id="P1",
        issue_number=PAPER_ISSUES["P1"],
        gates=gates,
        declared_claim_scope=ClaimScope.BOUNDED_EXACT,
        blockers=(
            _blocker(gates[0].gate_id, Actionability.BLOCKED_ON_PROOF),
            _blocker(gates[1].gate_id, Actionability.ACTIONABLE_NOW),
            _blocker(gates[2].gate_id, Actionability.BLOCKED_ON_CAMPAIGN),
            _blocker(gates[3].gate_id, Actionability.ACTIONABLE_NOW),
            _blocker(gates[4].gate_id, Actionability.BLOCKED_ON_UPSTREAM),
        ),
    )
    queue = record.work_queue()
    assert [item.actionability for item in queue] == [
        Actionability.ACTIONABLE_NOW,
        Actionability.ACTIONABLE_NOW,
        Actionability.BLOCKED_ON_UPSTREAM,
        Actionability.BLOCKED_ON_CAMPAIGN,
        Actionability.BLOCKED_ON_PROOF,
    ]
    # Ties break on gate id, so a regenerated queue is diffable.
    assert queue[0].gate_id < queue[1].gate_id
    assert record.work_queue() == queue


def test_a_blocker_on_a_passing_gate_is_not_queued(
    clean_ledger: SuperiorityLedger,
) -> None:
    """The queue is what is blocked, not what someone wrote a note about."""

    paper = clean_ledger.paper("P1")
    assert paper is not None
    with_note = replace(
        paper, blockers=(_blocker("P1-U-T1", Actionability.ACTIONABLE_NOW),)
    )
    assert with_note.work_queue() == ()


def test_ledger_refuses_an_unknown_responsibility_class() -> None:
    payload = {
        "schema_version": SUPERIORITY_LEDGER_SCHEMA,
        "ledger_id": "x",
        "frozen_at": "2026-08-21",
        "papers": [
            {
                "paper_id": "P1",
                "blockers": [
                    {
                        "gate_id": "P1-U-T1",
                        "responsibility": "VIBES",
                        "actionability": "ACTIONABLE_NOW",
                        "statement": "s",
                        "unblock": "u",
                    }
                ],
            }
        ],
    }
    with pytest.raises(LedgerBindingError, match="responsibility"):
        ledger_from_payload(payload)


def test_ledger_refuses_two_blockers_for_one_gate() -> None:
    entry = {
        "gate_id": "P1-U-T1",
        "responsibility": "IMPLEMENTATION_OR_ENVIRONMENT",
        "actionability": "ACTIONABLE_NOW",
        "statement": "s",
        "unblock": "u",
    }
    payload = {
        "schema_version": SUPERIORITY_LEDGER_SCHEMA,
        "ledger_id": "x",
        "frozen_at": "2026-08-21",
        "papers": [{"paper_id": "P1", "blockers": [entry, dict(entry)]}],
    }
    with pytest.raises(LedgerBindingError, match="two blockers"):
        ledger_from_payload(payload)


def test_committed_ledger_classifies_every_blocked_terminal() -> None:
    """Every blocked terminal says why, and the blocked count is pinned.

    The count was 49 of 51 until the three formal-generalization papers were
    adjudicated on their own terms. P6-U-T1, P6-U-T2, P7-U-T1, P7-U-T2, P8-U-T1
    and P8-U-T2 are discharged by mechanized theorems, which is what those gates
    admit; the blockers written against them had been asking for evaluator
    custody, and custody is a precondition of an empirical campaign, not of a
    proof. Two of them cost more than the rest. P7-U-T2 was blocked a second
    time after the derivation existed, because the finite result it derived
    turned out to evaluate its composition rule at two of eight argument
    triples, and it moved only once the donor families were interpreted as
    transformations with their own hand-off contracts. P8-U-T2 moved only when
    the 169 heterogeneous chain compositions -- an object separate from the
    3,072-state model, and the one its blocker named -- were derived from the
    chain theorem instantiated at the donor level; instrumenting them showed the
    shipped chain loop ignoring both of its donor variables, so the 169 is one
    composition counted thirteen times thirteen. The number is pinned rather
    than computed so that a terminal moving in either direction has to be
    noticed here.
    """

    ledger = ledger_from_payload(json.loads(LEDGER_PATH.read_text(encoding="utf-8")))
    for paper in ledger.papers:
        assert paper.unclassified_blocked_gate_ids() == (), paper.paper_id
    total = sum(len(paper.work_queue()) for paper in ledger.papers)
    assert total == 43, "43 of the 51 registered terminals are blocked"


def test_committed_ledger_pins_the_p1_diagnosis() -> None:
    """P1's terminal is blocked on a role leak into the candidate payload.

    This pin has now earned itself twice, and the history is the point. It was
    first written asserting ``IMPLEMENTATION_OR_ENVIRONMENT`` — the digest defect
    that rejected 100% of R6's native rows — and failed when cross-agent
    verification showed that defect solved and the real blocker one layer up:
    ``ORION_NATIVE_BASE`` returned UNRESOLVED on 48/48 episodes, so the ablation
    arm could not attribute the gain. It was then ``MEASUREMENT_OR_EVALUATOR`` /
    ``BLOCKED_ON_UPSTREAM`` and failed again when that cause was repaired,
    DIAGNOSE became reachable on 48/48, and repairing the three guards P1-U-T3
    named moved the terminal to NOT_SUPPORTED — because ``problem_id`` is built as
    ``p1-r6-root:{episode_id}`` and episode ids end in ``-A``/``-C``/``-U``, so the
    pair role reaches the candidate-visible payload on 96 of 96 episode-arms.

    It has since earned itself a third time. The role leak was closed under its
    own freeze, the primary survived it with every scored statistic bit-identical,
    and the blocker moved back to ``MEASUREMENT_OR_EVALUATOR`` — because what now
    holds the terminal is not an implementation defect at all but evaluator
    custody: the evaluator is authored in the same lane as the candidate, and
    ``PROTECTED_SUPERIORITY`` admits only ``PROSPECTIVE_PROTECTED`` evidence.

    Each reclassification cost a deliberate edit here, which is what this pin is
    for. Reclassifying P1's headline blocker should never be free.
    """

    ledger = ledger_from_payload(json.loads(LEDGER_PATH.read_text(encoding="utf-8")))
    p1 = ledger.paper("P1")
    assert p1 is not None

    t1 = p1.blockers_by_gate["P1-U-T1"]
    assert t1.responsibility is ResponsibilityClass.MEASUREMENT_OR_EVALUATOR
    assert t1.actionability is Actionability.BLOCKED_ON_CAMPAIGN
    # The leak is closed; what remains is custody and the semantic host.
    assert "custody" in t1.statement
    assert "bit-identical" in t1.statement

    # The replication gate is the one still held by an implementation literal:
    # the evaluator hard-wires source_year == 2020.
    t2 = p1.blockers_by_gate["P1-U-T2"]
    assert t2.responsibility is ResponsibilityClass.IMPLEMENTATION_OR_ENVIRONMENT

    # No verification finding may be recorded as evidence for a P1 gate.
    assert p1.evidence == ()
    assert p1.terminal() is PaperTerminalStatus.CANNOT_CHECK


def test_report_emits_a_cross_paper_work_queue() -> None:
    ledger = ledger_from_payload(json.loads(LEDGER_PATH.read_text(encoding="utf-8")))
    report = build_report(ledger)
    queue = report["work_queue"]
    assert len(queue) == 43
    ranks = [Actionability(item["actionability"]).queue_rank for item in queue]
    assert ranks == sorted(ranks), "the queue must be ordered by actionability"
    assert all({"paper_id", "gate_id", "responsibility", "unblock"} <= set(item) for item in queue)
    assert sum(report["work_queue_by_actionability"].values()) == 43
    assert sum(report["work_queue_by_responsibility"].values()) == 43


def test_ledger_document_counts_match_the_report() -> None:
    """The prose table and the generated report must not drift apart."""

    document = (
        REPO_ROOT
        / "research/paper-programme-v1/P1_P10_SUPERIORITY_TERMINAL_LEDGER_2026-08-21.md"
    ).read_text(encoding="utf-8")
    ledger = ledger_from_payload(json.loads(LEDGER_PATH.read_text(encoding="utf-8")))
    report = build_report(ledger)

    for name, count in report["work_queue_by_actionability"].items():
        assert f"| `{name}` | {count} |" in document, f"{name} count drifted"
    for name, count in report["work_queue_by_responsibility"].items():
        assert f"`{name}` {count}" in document, f"{name} count drifted"


# --- paper identity ----------------------------------------------------------


def test_every_registered_paper_directory_exists() -> None:
    """The registry names real directories, active and retired alike.

    Only the ten adjudicated papers. ``FUTURE_PAPER_DIRECTORIES`` deliberately
    names directories that do not exist yet.
    """

    for entry in PAPER_DIRECTORIES:
        assert (REPO_ROOT / entry.active).is_dir(), entry.active
        for directory, reason in entry.retired:
            assert (REPO_ROOT / directory).is_dir(), directory
            assert reason.strip(), f"{directory} must say why it is retained"


def test_the_repository_has_no_unregistered_paper_directory() -> None:
    assert paper_identity_findings(REPO_ROOT) == ()
    result = _result(
        SuperiorityLedger(ledger_id="x", frozen_at="2026-08-21", papers=()),
        STALE_PAPER_IDENTITY,
    )
    assert result.outcome is Outcome.PASS


def test_stale_paper_identity_fails(tmp_path: Path) -> None:
    """A paper number carried by a directory nobody registered."""

    (tmp_path / "papers" / "candidates").mkdir(parents=True)
    for entry in PAPER_DIRECTORIES:
        (tmp_path / entry.active).mkdir(parents=True, exist_ok=True)
        for directory, _ in entry.retired:
            (tmp_path / directory).mkdir(parents=True, exist_ok=True)
    assert paper_identity_findings(tmp_path) == ()

    third = tmp_path / "papers" / "candidates" / "paper-09-some-third-thing"
    third.mkdir()
    (third / "README.md").write_text("a third P9", encoding="utf-8")
    findings = paper_identity_findings(tmp_path)
    assert findings == ("papers/candidates/paper-09-some-third-thing",)


def test_paper_identity_cannot_check_without_a_papers_tree(tmp_path: Path) -> None:
    assert paper_identity_findings(tmp_path) is None


def test_every_paper_carries_one_active_directory_and_documented_history() -> None:
    """Historical snapshots never compete with the one active directory."""

    for entry in PAPER_DIRECTORIES:
        retired = {directory for directory, _ in entry.retired}
        assert entry.active not in retired, entry.paper_id
        assert len(retired) == len(entry.retired), entry.paper_id


def test_vacated_numbers_are_recorded_and_are_not_identities() -> None:
    """The two former candidates keep their content and lose their number.

    Neither could be renumbered into P11-P14: both are already absorbed, into P8
    and P4/P8, and re-absorbing them would contradict a recorded terminal while
    moving them away from the papers that own their subjects.
    """

    assert len(VACATED_PAPER_NUMBERS) == 2
    actives = {entry.active for entry in PAPER_DIRECTORIES}
    for directory, was, reason in VACATED_PAPER_NUMBERS:
        assert (REPO_ROOT / directory).is_dir(), directory
        # R0 moved one of these under papers/archive/2026-08-pre-unification/.
        # What matters is the identity, not where it is filed: the basename must
        # still be paper-xx-, which is what keeps it invisible to the
        # paper-number scan.
        assert directory.startswith("papers/")
        assert directory.rsplit("/", 1)[-1].startswith("paper-xx-")
        assert was in ("was P9", "was P10")
        assert reason.strip()
        # Vacated means vacated: not a registered identity, and invisible to the
        # paper-number scan because `paper-xx-` carries no digits.
        assert directory not in REGISTERED_PAPER_DIRECTORIES
        assert directory not in actives


def test_every_retired_directory_states_why_it_is_not_active() -> None:
    for entry in PAPER_DIRECTORIES:
        for directory, reason in entry.retired:
            assert (REPO_ROOT / directory).is_dir(), directory
            assert any(word in reason for word in ("historical", "preserved")), reason


def test_the_ledger_cites_only_known_paper_directories() -> None:
    """Predecessor evidence must point somewhere the registry accounts for.

    Three places are legitimate: a registered paper identity, a vacated former
    candidate, or a shared lane. P10's predecessor evidence now sits in a vacated
    directory --- it is still the evidence, it just no longer carries a number.
    """

    known = (
        set(REGISTERED_PAPER_DIRECTORIES)
        | {directory for directory, _, _ in VACATED_PAPER_NUMBERS}
        | set(SHARED_LANES)
    )
    ledger = ledger_from_payload(json.loads(LEDGER_PATH.read_text(encoding="utf-8")))
    for paper in ledger.papers:
        for item in paper.predecessor_artifacts:
            if not item.artifact_ref.startswith("papers/"):
                continue
            assert any(
                item.artifact_ref.startswith(f"{directory}/") for directory in known
            ), item.artifact_ref


def test_future_identities_are_registered_before_their_directories_arrive() -> None:
    """P11-P14 must not red the identity check the day PR #715 lands.

    A check that fires on identity rot must not fire on a legitimate new identity.
    Registering the four names ahead of the directories is what keeps those two
    apart, so this asserts both halves: the names are known, and they are not
    expected on disk yet.
    """

    assert set(FUTURE_PAPER_DIRECTORIES) == {"P11", "P12", "P13", "P14", "P15"}
    for paper_id, directory in FUTURE_PAPER_DIRECTORIES.items():
        assert directory in REGISTERED_PAPER_DIRECTORIES
        assert paper_id not in PAPER_DIRECTORIES_BY_ID, "not adjudicated by this module"
        assert paper_id not in PAPER_GATES, "no Done-when gates exist for P11-P14"


def test_a_future_directory_appearing_does_not_fail_the_identity_check(
    tmp_path: Path,
) -> None:
    (tmp_path / "papers" / "candidates").mkdir(parents=True)
    for entry in PAPER_DIRECTORIES:
        (tmp_path / entry.active).mkdir(parents=True, exist_ok=True)
        for directory, _ in entry.retired:
            (tmp_path / directory).mkdir(parents=True, exist_ok=True)
    for directory in FUTURE_PAPER_DIRECTORIES.values():
        (tmp_path / directory).mkdir(parents=True, exist_ok=True)
    assert paper_identity_findings(tmp_path) == ()


def test_retired_numbering_records_what_absorbed_each_track() -> None:
    """#670 retires a number rather than renumbering a paper.

    Three research tracks lost their standalone paper numbering and became child
    tracks. The issues stay open; only the publication identity was withdrawn.
    """

    assert {issue for issue, _, _ in RETIRED_PAPER_NUMBERING} == {664, 667, 668}
    for issue, description, absorbed_into in RETIRED_PAPER_NUMBERING:
        assert description.strip(), issue
        assert absorbed_into in FUTURE_PAPER_DIRECTORIES or absorbed_into in PAPER_GATES

    # Nothing in P1-P10 was absorbed: #670 states "P1-U-P8-U remain #649-#656",
    # and P9/P10 keep their own successor issues.
    assert not any(target in PAPER_GATES for _, _, target in RETIRED_PAPER_NUMBERING)


# --- every terminal must be reachable ----------------------------------------


def _natural_grades_for(kind: TerminalKind) -> tuple[EvidenceGrade, ...]:
    """The grades a reader of the issue would expect to satisfy this kind."""

    return tuple(sorted(ADMISSIBLE_GRADES[kind], key=lambda grade: grade.rank))


def test_every_gate_is_reachable_by_its_own_admissible_grades() -> None:
    """No terminal may be unpassable however good the evidence gets.

    The general form of a defect found by review on PR #739: three gates asking
    for an independent proof review were typed ``REPLICATION``, whose only
    admissible grade is ``PROSPECTIVE_PROTECTED``, so mechanizing the proof and
    having it reviewed --- their own documented unblock path --- still could not
    discharge them. Pinning those three would not have caught the class.
    """

    unreachable: list[str] = []
    for paper_id, gates in PAPER_GATES.items():
        record = PaperSuperiorityRecord(
            paper_id=paper_id,
            issue_number=PAPER_ISSUES[paper_id],
            gates=gates,
            evidence=tuple(_discharging_evidence(gate) for gate in gates),
            declared_claim_scope=ClaimScope.GENERAL_PROSPECTIVE,
        )
        for status in record.statuses():
            if status.outcome is not Outcome.PASS:
                unreachable.append(f"{status.gate_id} ({status.kind.value}): {status.reason}")
    assert unreachable == []


def test_every_disjunct_a_terminal_offers_is_reachable() -> None:
    """Reachable by *some* path is not enough; each documented path must work.

    The test above passed while ``P9-U-T2`` and ``P10-U-T1`` were still broken,
    because its fixture always supplied two domains and so only ever walked the
    full replication path. The bounded disjunct --- #662's "explicit
    family-bounded terminal", #663's "retained as a negative" --- was never
    exercised, and both were unpassable: bounded to one family by definition, yet
    held to a two-domain floor. Second finding of the same class on PR #739, which
    is what a gap in a class-level test looks like from outside.
    """

    for paper_id, gates in PAPER_GATES.items():
        for gate in gates:
            if not gate.bounded_terminal_admissible:
                continue
            bounded = GateEvidence(
                gate_id=gate.gate_id,
                grade=EvidenceGrade.BOUNDED_PROTECTED,
                artifact_refs=(f"results/{gate.gate_id}-bounded.json",),
                protocol_frozen_before_outcome=True,
                comparator_donor_complete=True,
                evaluator_custody=EXTERNAL_CUSTODY,
                domains=("the one family it is bounded to",),
            )
            status = adjudicate(gate, bounded)
            assert status.outcome is Outcome.PASS, (
                f"{paper_id}/{gate.gate_id} declares a narrower disjunct that "
                f"cannot pass: {status.reason}"
            )

    # Exactly the two the issues offer, so a third cannot appear unnoticed.
    offered = [g.gate_id for gates in PAPER_GATES.values() for g in gates
               if g.bounded_terminal_admissible]
    assert offered == ["P9-U-T2", "P10-U-T1"]


def test_the_bounded_disjunct_still_requires_a_protected_outcome() -> None:
    """The narrower path drops the domain floor, not the protection."""

    gate = next(g for g in PAPER_GATES["P9"] if g.gate_id == "P9-U-T2")
    base = GateEvidence(
        gate_id="P9-U-T2",
        grade=EvidenceGrade.BOUNDED_PROTECTED,
        artifact_refs=("results/family_bounded.json",),
        protocol_frozen_before_outcome=True,
        comparator_donor_complete=True,
        evaluator_custody=EXTERNAL_CUSTODY,
        domains=("qwen2.5",),
    )
    assert adjudicate(gate, base).outcome is Outcome.PASS
    assert (
        adjudicate(gate, replace(base, protocol_frozen_before_outcome=False)).outcome
        is Outcome.FAIL
    )
    assert (
        adjudicate(gate, replace(base, evaluator_custody=CANDIDATE_CUSTODY)).outcome
        is Outcome.FAIL
    )
    # A mechanism result still cannot take the narrower path.
    assert (
        adjudicate(gate, replace(base, grade=EvidenceGrade.MECHANISM_NON_VACUITY)).outcome
        is Outcome.FAIL
    )


def test_thin_replication_does_not_fire_on_a_bounded_disjunct(
    clean_ledger: SuperiorityLedger,
) -> None:
    """adjudicate and the battery must agree about the same row."""

    bounded = GateEvidence(
        gate_id="P9-U-T2",
        grade=EvidenceGrade.BOUNDED_PROTECTED,
        artifact_refs=("results/family_bounded.json",),
        protocol_frozen_before_outcome=True,
        comparator_donor_complete=True,
        evaluator_custody=EXTERNAL_CUSTODY,
        domains=("qwen2.5",),
    )
    paper = clean_ledger.paper("P9")
    assert paper is not None
    evidence = tuple(
        bounded if item.gate_id == "P9-U-T2" else item for item in paper.evidence
    )
    ledger = _mutate(clean_ledger, "P9", evidence=evidence)
    assert _result(ledger, THIN_REPLICATION).outcome is Outcome.PASS
    # ...and a genuinely thin *full* replication still fails.
    thin = replace(bounded, grade=EvidenceGrade.PROSPECTIVE_PROTECTED)
    ledger2 = _mutate(
        clean_ledger,
        "P9",
        evidence=tuple(thin if i.gate_id == "P9-U-T2" else i for i in paper.evidence),
    )
    assert _result(ledger2, THIN_REPLICATION).outcome is Outcome.FAIL


def test_an_independent_review_gate_accepts_a_mechanized_proof() -> None:
    """The exact defect PR #739 review caught, pinned at the instance too."""

    for gate_id, paper_id in (("P6-U-T4", "P6"), ("P7-U-T5", "P7"), ("P8-U-T5", "P8")):
        gate = next(g for g in PAPER_GATES[paper_id] if g.gate_id == gate_id)
        assert gate.kind is TerminalKind.INDEPENDENT_REVIEW, gate_id
        assert EvidenceGrade.MECHANIZED_THEOREM in gate.admissible_grades


def test_an_independent_review_must_actually_be_independent() -> None:
    gate = next(g for g in PAPER_GATES["P6"] if g.gate_id == "P6-U-T4")
    proof = GateEvidence(
        gate_id="P6-U-T4",
        grade=EvidenceGrade.MECHANIZED_THEOREM,
        artifact_refs=("proofs/p6.v",),
    )
    assert adjudicate(gate, proof).outcome is Outcome.CANNOT_CHECK
    assert (
        adjudicate(gate, replace(proof, independent_implementation=False)).outcome
        is Outcome.FAIL
    )
    assert (
        adjudicate(gate, replace(proof, independent_implementation=True)).outcome
        is Outcome.PASS
    )


def test_a_manuscript_still_cannot_discharge_an_independent_review() -> None:
    gate = next(g for g in PAPER_GATES["P6"] if g.gate_id == "P6-U-T4")
    manuscript = GateEvidence(
        gate_id="P6-U-T4",
        grade=EvidenceGrade.MANUSCRIPT_COMPLETION,
        artifact_refs=("papers/p6/manuscript.tex",),
        independent_implementation=True,
    )
    assert adjudicate(gate, manuscript).outcome is Outcome.FAIL
    assert _natural_grades_for(TerminalKind.INDEPENDENT_REVIEW) == (
        EvidenceGrade.MECHANIZED_THEOREM,
        EvidenceGrade.PROSPECTIVE_PROTECTED,
    )


def test_build_residue_is_not_a_paper_identity(tmp_path: Path) -> None:
    """Stale __pycache__ from a directory move must not read as a live paper.

    This is what actually happened when P6-P10 moved out of ``papers/candidates/``
    into ``papers/``: the old paths survived on disk holding nothing but ``.pyc``
    files, and a filesystem walk reported three unregistered papers that git had
    never heard of.
    """

    (tmp_path / "papers" / "candidates").mkdir(parents=True)
    for entry in PAPER_DIRECTORIES:
        (tmp_path / entry.active).mkdir(parents=True, exist_ok=True)
        for directory, _ in entry.retired:
            (tmp_path / directory).mkdir(parents=True, exist_ok=True)

    residue = tmp_path / "papers" / "candidates" / "paper-99-build-residue"
    (residue / "formal" / "__pycache__").mkdir(parents=True)
    (residue / "formal" / "__pycache__" / "check.cpython-311.pyc").write_bytes(b"\x00")
    assert paper_identity_findings(tmp_path) == ()

    # Real content in the same place is still a finding.
    (residue / "README.md").write_text("a real paper", encoding="utf-8")
    assert paper_identity_findings(tmp_path) == (
        "papers/candidates/paper-99-build-residue",
    )


def test_the_q_paper_namespace_is_out_of_scope(tmp_path: Path) -> None:
    """ORION-Q has its own numbering and its own issues."""

    (tmp_path / "papers").mkdir(parents=True)
    for entry in PAPER_DIRECTORIES:
        (tmp_path / entry.active).mkdir(parents=True, exist_ok=True)
        for directory, _ in entry.retired:
            (tmp_path / directory).mkdir(parents=True, exist_ok=True)
    q = tmp_path / "papers" / "orion-05-tare-expressivity"
    q.mkdir()
    (q / "CLAIM_LEDGER.md").write_text("q", encoding="utf-8")
    assert paper_identity_findings(tmp_path) == ()


def test_future_identities_are_registered_under_both_layouts() -> None:
    """PR #715 was authored pre-refactor; either landing order must be clean."""

    for paper_id, directory in FUTURE_PAPER_DIRECTORIES.items():
        assert directory.startswith("papers/orion-2")
        assert directory in REGISTERED_PAPER_DIRECTORIES
        legacy = directory.replace("papers/", "papers/candidates/", 1)
        assert legacy in REGISTERED_PAPER_DIRECTORIES
        # The retired entry used to be asserted as the candidates/ spelling of
        # the active name. Wave R0 renamed the active packages to the orion-NN
        # series while the snapshots kept their original paper-NN names, so that
        # derivation now names a directory that does not exist. Assert the
        # stronger, rename-proof property instead: each recorded snapshot is a
        # real directory under papers/candidates/.
        if paper_id in FUTURE_RETIRED_PAPER_DIRECTORIES:
            for path, _ in FUTURE_RETIRED_PAPER_DIRECTORIES[paper_id]:
                assert path.startswith("papers/candidates/")
                assert (REPO_ROOT / path).is_dir(), f"{paper_id} snapshot missing: {path}"


# --- P11-P14 folders, shared lanes, split identity ----------------------------


def test_p11_to_p14_directories_exist_with_a_readme() -> None:
    """The four identities #670 assigns now have a home under papers/."""

    for paper_id, directory in FUTURE_PAPER_DIRECTORIES.items():
        path = REPO_ROOT / directory
        assert path.is_dir(), f"{paper_id} has no directory at {directory}"
        readme = path / "README.md"
        assert readme.is_file(), f"{paper_id} has no README"
        text = readme.read_text(encoding="utf-8")
        assert f"ORION-{paper_id}" in text
        assert "NO_PROTECTED_RESULT" in text, f"{paper_id} must not imply a result"


def test_p11_to_p14_add_no_manuscript_that_would_collide_with_pr_715() -> None:
    """PR #715 owns MANUSCRIPT.md; opening the folder must not pre-empt it."""

    for directory in FUTURE_PAPER_DIRECTORIES.values():
        assert not (REPO_ROOT / directory / "MANUSCRIPT.md").exists()


def test_shared_lanes_are_not_paper_identities() -> None:
    """`orion-learning-machine` is code and results, not a paper."""

    assert list(SHARED_LANES) == ["papers/orion-learning-machine"]
    for lane, reason in SHARED_LANES.items():
        assert (REPO_ROOT / lane).is_dir(), lane
        assert reason.strip()
        assert lane not in REGISTERED_PAPER_DIRECTORIES
        # The README that was missing is what made it read as a paper.
        assert (REPO_ROOT / lane / "README.md").is_file(), f"{lane} needs a README"


def test_split_paper_identity_fails(tmp_path: Path) -> None:
    """One identity, two live locations, nothing saying which carries it.

    The live risk: PR #715 was authored pre-refactor and still targets
    `papers/candidates/`. Registering both spellings stops that reading as
    identity *rot*; this stops it being silent if both ever hold content.
    """

    (tmp_path / "papers" / "candidates").mkdir(parents=True)
    for entry in PAPER_DIRECTORIES:
        (tmp_path / entry.active).mkdir(parents=True, exist_ok=True)
        for directory, _ in entry.retired:
            (tmp_path / directory).mkdir(parents=True, exist_ok=True)

    slug = "paper-99-unregistered-split"
    new = tmp_path / "papers" / slug
    new.mkdir()
    (new / "README.md").write_text("here", encoding="utf-8")
    assert split_identity_findings(tmp_path) == ()

    old = tmp_path / "papers" / "candidates" / slug
    old.mkdir()
    (old / "MANUSCRIPT.md").write_text("also here", encoding="utf-8")
    findings = split_identity_findings(tmp_path)
    assert len(findings) == 1
    assert slug in findings[0]
    assert "papers/candidates/" in findings[0] and "and" in findings[0]


def test_split_identity_ignores_empty_and_residue_directories(tmp_path: Path) -> None:
    (tmp_path / "papers" / "candidates").mkdir(parents=True)
    slug = "orion-21-state-as-computation"
    live = tmp_path / "papers" / slug
    live.mkdir()
    (live / "README.md").write_text("here", encoding="utf-8")
    residue = tmp_path / "papers" / "candidates" / slug / "__pycache__"
    residue.mkdir(parents=True)
    (residue / "x.cpython-311.pyc").write_bytes(b"\x00")
    assert split_identity_findings(tmp_path) == ()


def test_the_repository_has_no_split_paper_identity() -> None:
    assert split_identity_findings(REPO_ROOT) == ()
    result = _result(
        SuperiorityLedger(ledger_id="x", frozen_at="2026-08-21", papers=()),
        SPLIT_PAPER_IDENTITY,
    )
    assert result.outcome is Outcome.PASS
