"""Hostile checks over the P1-P10 superiority ledger.

Every check here names a failure that has actually happened in this repository's
history, not a hypothetical one. The list was assembled by reading what went
wrong across the ``P<n>-X`` claim-expansion series, the P1-U R2/R3/R4/R5
acquisition campaigns and the status correction on #649, then asking of each:
*what would a ledger look like if this happened again and nobody noticed?*

The battery is deliberately **not** registered into
``orion.programme.catalogue.ALL_CHECKS``. That catalogue is the Phase-4
anti-collapse battery for issue #210 and its membership is asserted by existing
tests; extending it is a shared-registry edit under ``AGENTS.md``. This is a
second, separately-run battery over a different state object, and it carries its
own catalogue.

Framework contract, inherited from ``orion.programme.hostile``: three outcomes,
``CANNOT_CHECK`` blocks, an empty report blocks, and every check names the test
that shows it rejecting something.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from orion.programme.hostile import (
    CheckResult,
    HostileCheckReport,
    cannot_check,
    failed,
    passed,
)
from orion.programme.programme_state import CANDIDATE_CUSTODY
from orion.programme.records import Outcome
from orion.programme.superiority import (
    MAX_SCOPE_FOR_GRADE,
    MIN_REPLICATION_DOMAINS,
    EvidenceGrade,
    TerminalKind,
    on_bounded_disjunct,
)
from orion.programme.superiority_ledger import SuperiorityLedger
from orion.programme.superiority_terminals import (
    FUTURE_PAPER_DIRECTORIES,
    FUTURE_RETIRED_PAPER_DIRECTORIES,
    PAPER_DIRECTORIES,
    PAPER_GATES,
    REGISTERED_PAPER_DIRECTORIES,
)


@dataclass(frozen=True)
class SuperiorityCheck:
    """One check over the superiority ledger.

    A local mirror of :class:`orion.programme.hostile.HostileCheck` rather than a
    reuse of it: that class is typed over ``ProgrammeState``, and passing a
    ledger through it would work at runtime while lying in the annotation. The
    contract is identical --- ``failure_class`` names the collapse mode,
    ``negative_fixture_id`` names the test that shows this check rejecting
    something, and an exception is an inability to check rather than a pass.
    """

    check_id: str
    title: str
    failure_class: str
    negative_fixture_id: str
    evaluate: Callable[[SuperiorityLedger], CheckResult]

    def __post_init__(self) -> None:
        for name in ("check_id", "title", "failure_class", "negative_fixture_id"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"superiority check {name} is required")

    def run(self, ledger: SuperiorityLedger) -> CheckResult:
        try:
            result = self.evaluate(ledger)
        except Exception as error:  # noqa: BLE001 - an unevaluable check must block
            return CheckResult(
                check_id=self.check_id,
                outcome=Outcome.CANNOT_CHECK,
                reason=f"check raised {type(error).__name__}: {error}",
            )
        if result.check_id != self.check_id:
            return CheckResult(
                check_id=self.check_id,
                outcome=Outcome.CANNOT_CHECK,
                reason="check returned a result for a different check id",
            )
        return result


TERMINAL_COVERAGE = "HC-SUP-TERMINAL-COVERAGE"
MANUSCRIPT_SUBSTITUTION = "HC-SUP-MANUSCRIPT-SUBSTITUTION"
MECHANISM_SUBSTITUTION = "HC-SUP-MECHANISM-SUBSTITUTION"
CANNOT_CHECK_LAUNDERING = "HC-SUP-CANNOT-CHECK-LAUNDERING"
DONOR_INCOMPLETE_COMPARATOR = "HC-SUP-DONOR-INCOMPLETE-COMPARATOR"
COMPENSATORY_SCORING = "HC-SUP-COMPENSATORY-SCORING"
THIN_REPLICATION = "HC-SUP-THIN-REPLICATION"
POST_HOC_FREEZE = "HC-SUP-POST-HOC-FREEZE"
SELF_CERTIFICATION = "HC-SUP-SELF-CERTIFICATION"
CLAIM_WIDER_THAN_EVIDENCE = "HC-SUP-CLAIM-WIDER-THAN-EVIDENCE"
PREDECESSOR_REUSE = "HC-SUP-PREDECESSOR-REUSE"
UNCLASSIFIED_BLOCKER = "HC-SUP-UNCLASSIFIED-BLOCKER"
STALE_PAPER_IDENTITY = "HC-SUP-STALE-PAPER-IDENTITY"
SPLIT_PAPER_IDENTITY = "HC-SUP-SPLIT-PAPER-IDENTITY"

# Kinds that ask for an empirical outcome. The two scope kinds are excluded
# throughout: a scope gate's artifact legitimately *is* a manuscript, because
# what it adjudicates is how that manuscript words its claim.
_OUTCOME_KINDS = frozenset(
    {
        TerminalKind.PROTECTED_SUPERIORITY,
        TerminalKind.HARM_GUARD,
        TerminalKind.REPLICATION,
        TerminalKind.SUCCESSOR_MECHANIC,
        TerminalKind.INDEPENDENT_REVIEW,
    }
)


def _gate_kinds(paper_id: str) -> dict[str, TerminalKind]:
    return {gate.gate_id: gate.kind for gate in PAPER_GATES[paper_id]}


def _check_terminal_coverage(ledger: SuperiorityLedger) -> CheckResult:
    """A ledger that omits a paper cannot be read as a clean bill for that paper."""

    if not ledger.papers:
        return cannot_check(TERMINAL_COVERAGE, "the ledger records no papers at all")

    drift: list[str] = []
    for paper in ledger.papers:
        registered = PAPER_GATES[paper.paper_id]
        if tuple(gate.gate_id for gate in paper.gates) != tuple(
            gate.gate_id for gate in registered
        ):
            drift.append(
                f"{paper.paper_id} gate list disagrees with the frozen registry"
            )
    if drift:
        return failed(
            TERMINAL_COVERAGE,
            "a paper's gate list has drifted from the frozen terminal registry",
            tuple(drift),
        )

    missing = ledger.missing_paper_ids
    if missing:
        return cannot_check(
            TERMINAL_COVERAGE,
            "the ledger says nothing about " + ", ".join(missing),
        )
    return passed(
        TERMINAL_COVERAGE,
        f"all {len(PAPER_GATES)} registered papers are present with their frozen gate lists",
    )


def _substitution_check(
    ledger: SuperiorityLedger,
    check_id: str,
    grade: EvidenceGrade,
    description: str,
) -> CheckResult:
    findings = [
        f"{paper.paper_id}/{item.gate_id} ({kinds[item.gate_id].value}) is fed by "
        f"{grade.value}: {', '.join(item.artifact_refs) or 'no artifact'}"
        for paper in ledger.papers
        for kinds in (_gate_kinds(paper.paper_id),)
        for item in paper.evidence
        if item.grade is grade and kinds.get(item.gate_id) in _OUTCOME_KINDS
    ]
    if findings:
        return failed(check_id, description, tuple(findings))
    return passed(check_id, f"no outcome terminal is fed by {grade.value}")


def _check_manuscript_substitution(ledger: SuperiorityLedger) -> CheckResult:
    return _substitution_check(
        ledger,
        MANUSCRIPT_SUBSTITUTION,
        EvidenceGrade.MANUSCRIPT_COMPLETION,
        "a written or merged manuscript is recorded against a terminal that asks "
        "for an outcome; #649 records this exact substitution being made and corrected",
    )


def _check_mechanism_substitution(ledger: SuperiorityLedger) -> CheckResult:
    return _substitution_check(
        ledger,
        MECHANISM_SUBSTITUTION,
        EvidenceGrade.MECHANISM_NON_VACUITY,
        "an exact result on an authored finite arena is recorded against a terminal "
        "that asks for a naturalistic protected outcome; a bounded mechanism result "
        "shows non-vacuity and says nothing about transfer",
    )


def _check_cannot_check_laundering(ledger: SuperiorityLedger) -> CheckResult:
    return _substitution_check(
        ledger,
        CANNOT_CHECK_LAUNDERING,
        EvidenceGrade.CANNOT_CHECK,
        "a campaign that terminated before producing an outcome is recorded as "
        "evidence for a terminal; preserving a CANNOT_CHECK campaign is right, "
        "counting it is not",
    )


def _check_donor_incomplete_comparator(ledger: SuperiorityLedger) -> CheckResult:
    violated: list[str] = []
    unrecorded: list[str] = []
    for paper in ledger.papers:
        kinds = _gate_kinds(paper.paper_id)
        for item in paper.evidence:
            if kinds.get(item.gate_id) is not TerminalKind.PROTECTED_SUPERIORITY:
                continue
            if item.grade is EvidenceGrade.ABSENT:
                continue
            if item.comparator_donor_complete is False:
                violated.append(
                    f"{paper.paper_id}/{item.gate_id} claims superiority over a "
                    "comparator that is not donor-complete"
                )
            elif item.comparator_donor_complete is None:
                unrecorded.append(
                    f"{paper.paper_id}/{item.gate_id} does not record whether its "
                    "comparator is donor-complete"
                )
    if violated:
        return failed(
            DONOR_INCOMPLETE_COMPARATOR,
            "a superiority claim rests on a comparator that is not donor-complete",
            tuple(violated),
        )
    if unrecorded:
        return cannot_check(
            DONOR_INCOMPLETE_COMPARATOR,
            "comparator donor-completeness is unrecorded for at least one superiority claim",
        )
    return passed(
        DONOR_INCOMPLETE_COMPARATOR,
        "every recorded superiority claim names a donor-complete comparator",
    )


def _check_compensatory_scoring(ledger: SuperiorityLedger) -> CheckResult:
    """A win must not stand while a guard the same paper declared does not.

    Also catches a dangling ``harm_guard_gate_ids`` reference, which is the same
    failure one step earlier: a claim conditioned on a guard that is not there.
    """

    findings: list[str] = []
    standing_wins = 0

    for paper in ledger.papers:
        kinds = _gate_kinds(paper.paper_id)
        known = set(kinds)
        by_gate = {status.gate_id: status for status in paper.statuses()}

        for item in paper.evidence:
            dangling = [ref for ref in item.harm_guard_gate_ids if ref not in known]
            if dangling:
                findings.append(
                    f"{paper.paper_id}/{item.gate_id} is conditioned on guard(s) "
                    f"{', '.join(dangling)}, which this paper does not declare"
                )

        blocked_guards = [
            gate_id
            for gate_id, kind in kinds.items()
            if kind is TerminalKind.HARM_GUARD and by_gate[gate_id].blocks
        ]
        passing_wins = [
            gate_id
            for gate_id, kind in kinds.items()
            if kind is TerminalKind.PROTECTED_SUPERIORITY
            and by_gate[gate_id].outcome is Outcome.PASS
        ]
        standing_wins += len(passing_wins)
        if passing_wins and blocked_guards:
            findings.append(
                f"{paper.paper_id} counts {', '.join(passing_wins)} as won while "
                f"{', '.join(blocked_guards)} does not pass"
            )

    if findings:
        return failed(
            COMPENSATORY_SCORING,
            "a superiority win is standing on top of a guard that has not passed",
            tuple(findings),
        )
    if standing_wins == 0:
        return passed(
            COMPENSATORY_SCORING,
            "no superiority win currently stands anywhere in the ledger, so no guard "
            "is being compensated for",
        )
    return passed(
        COMPENSATORY_SCORING,
        f"{standing_wins} standing superiority win(s), each with every declared guard passing",
    )


def _check_thin_replication(ledger: SuperiorityLedger) -> CheckResult:
    findings: list[str] = []
    for paper in ledger.papers:
        kinds = _gate_kinds(paper.paper_id)
        gates = {gate.gate_id: gate for gate in PAPER_GATES[paper.paper_id]}
        for item in paper.evidence:
            if kinds.get(item.gate_id) is not TerminalKind.REPLICATION:
                continue
            if item.grade is EvidenceGrade.ABSENT:
                continue
            if on_bounded_disjunct(gates[item.gate_id], item):
                # The narrower disjunct the issue itself offers is bounded to one
                # family by definition. Holding it to the domain floor would fail
                # the exact shape #662 and #663 explicitly admit.
                continue
            distinct = len(set(item.domains))
            if distinct < MIN_REPLICATION_DOMAINS:
                findings.append(
                    f"{paper.paper_id}/{item.gate_id} claims replication across "
                    f"{distinct} distinct domain(s); {MIN_REPLICATION_DOMAINS} are required"
                )
            elif distinct < len(item.domains):
                findings.append(
                    f"{paper.paper_id}/{item.gate_id} lists {len(item.domains)} domains "
                    f"of which only {distinct} are distinct"
                )
    if findings:
        return failed(
            THIN_REPLICATION,
            "a replication terminal is credited from insufficient or repeated domains",
            tuple(findings),
        )
    return passed(
        THIN_REPLICATION,
        "no replication terminal is credited from fewer than "
        f"{MIN_REPLICATION_DOMAINS} distinct domains",
    )


def _check_post_hoc_freeze(ledger: SuperiorityLedger) -> CheckResult:
    violated: list[str] = []
    unrecorded: list[str] = []
    for paper in ledger.papers:
        kinds = _gate_kinds(paper.paper_id)
        for item in paper.evidence:
            if kinds.get(item.gate_id) not in _OUTCOME_KINDS:
                continue
            if item.grade is EvidenceGrade.ABSENT:
                continue
            if item.grade is EvidenceGrade.MECHANIZED_THEOREM:
                # A theorem has no outcome access, so there is no "before" for a
                # protocol to have been frozen relative to.
                continue
            if item.protocol_frozen_before_outcome is False:
                violated.append(
                    f"{paper.paper_id}/{item.gate_id} was scored under a protocol "
                    "frozen after outcome access"
                )
            elif item.protocol_frozen_before_outcome is None:
                unrecorded.append(
                    f"{paper.paper_id}/{item.gate_id} does not record when its protocol "
                    "was frozen relative to outcome access"
                )
    if violated:
        return failed(
            POST_HOC_FREEZE,
            "an outcome was scored under a protocol that was not frozen beforehand",
            tuple(violated),
        )
    if unrecorded:
        return cannot_check(
            POST_HOC_FREEZE,
            "protocol freeze order is unrecorded for at least one outcome terminal",
        )
    return passed(POST_HOC_FREEZE, "every recorded outcome was scored under a pre-frozen protocol")


def _check_self_certification(ledger: SuperiorityLedger) -> CheckResult:
    findings = [
        f"{paper.paper_id}/{item.gate_id} was evaluated under {CANDIDATE_CUSTODY} custody"
        for paper in ledger.papers
        for item in paper.evidence
        if item.evaluator_custody == CANDIDATE_CUSTODY
    ]
    if findings:
        return failed(
            SELF_CERTIFICATION,
            "a terminal was discharged by an evaluator inside candidate custody; "
            "proposal is not adoption and generation cannot certify itself",
            tuple(findings),
        )
    return passed(SELF_CERTIFICATION, "no terminal is discharged under candidate custody")


def _check_claim_wider_than_evidence(ledger: SuperiorityLedger) -> CheckResult:
    violated: list[str] = []
    unrecorded: list[str] = []
    for paper in ledger.papers:
        if paper.declared_claim_scope is None:
            unrecorded.append(f"{paper.paper_id} does not declare a claim scope")
            continue
        permitted = MAX_SCOPE_FOR_GRADE[paper.strongest_grade]
        if paper.declared_claim_scope.rank > permitted.rank:
            violated.append(
                f"{paper.paper_id} advertises {paper.declared_claim_scope.value} on "
                f"{paper.strongest_grade.value} evidence, which licenses at most "
                f"{permitted.value}"
            )
    if violated:
        return failed(
            CLAIM_WIDER_THAN_EVIDENCE,
            "a paper advertises a claim wider than its strongest evidence licenses",
            tuple(violated),
        )
    if unrecorded:
        return cannot_check(
            CLAIM_WIDER_THAN_EVIDENCE,
            "claim scope is unrecorded for " + ", ".join(unrecorded),
        )
    return passed(
        CLAIM_WIDER_THAN_EVIDENCE,
        "every paper's advertised claim is within what its strongest grade licenses",
    )


def _check_predecessor_reuse(ledger: SuperiorityLedger) -> CheckResult:
    """The same file cannot be both the predecessor and the discharge.

    This is the substitution caught one level below
    ``HC-SUP-MECHANISM-SUBSTITUTION``: that check reads the declared grade, and a
    grade is a claim. This one reads the artifact path, which is a fact. A ledger
    entry asserting ``PROSPECTIVE_PROTECTED`` while pointing at the bounded exact
    terminal it was supposed to supersede fails here regardless of what it says
    about itself.
    """

    findings: list[str] = []
    for paper in ledger.papers:
        predecessors = {item.artifact_ref for item in paper.predecessor_artifacts}
        if not predecessors:
            continue
        for item in paper.evidence:
            reused = sorted(set(item.artifact_refs) & predecessors)
            if reused:
                findings.append(
                    f"{paper.paper_id}/{item.gate_id} discharges at grade "
                    f"{item.grade.value} using predecessor artifact(s) {', '.join(reused)}"
                )
    if findings:
        return failed(
            PREDECESSOR_REUSE,
            "a terminal is discharged by an artifact the same paper lists as a "
            "predecessor that discharges nothing",
            tuple(findings),
        )
    return passed(
        PREDECESSOR_REUSE,
        "no terminal is discharged by an artifact listed as a non-discharging predecessor",
    )


def _check_unclassified_blocker(ledger: SuperiorityLedger) -> CheckResult:
    """Every blocked terminal states why it is blocked and what would move it.

    Without this, ``CANNOT_CHECK`` is one word covering a one-file defect, an
    evaluation arena nobody has built, and a theorem nobody has proved. Those are
    not the same status and cannot be worked from the same queue. A blocked gate
    with no recorded blocker is an unanswered question wearing the costume of a
    status, so this fails rather than merely declining to check: the answer to
    "is every blocked terminal accounted for?" is a definite no.

    Note this is a *ledger hygiene* failure, not a scientific one, and
    ``build_report`` keeps the two apart when it sets ``overall_terminal``.
    """

    findings: list[str] = []
    classified = 0
    for paper in ledger.papers:
        unclassified = paper.unclassified_blocked_gate_ids()
        classified += len(paper.work_queue())
        if unclassified:
            findings.append(
                f"{paper.paper_id} leaves {', '.join(unclassified)} blocked with no "
                "recorded responsibility class or unblock action"
            )
    if findings:
        return failed(
            UNCLASSIFIED_BLOCKER,
            "a terminal is blocked with no stated cause, so it cannot be worked",
            tuple(findings),
        )
    if not classified:
        return passed(
            UNCLASSIFIED_BLOCKER,
            "no terminal is blocked, so there is nothing to classify",
        )
    return passed(
        UNCLASSIFIED_BLOCKER,
        f"all {classified} blocked terminal(s) carry a responsibility class and an "
        "unblock action",
    )


_PAPER_DIR_PATTERN = re.compile(r"^paper-(\d{2})-")

#: ``Q-paper-NN-*`` is the ORION-Q programme's own numbering namespace and is
#: deliberately out of scope here: this module adjudicates the ``P<n>-U`` terminals
#: of #649-#663, and ORION-Q has separate issues. The pattern above already
#: excludes it by requiring ``paper-`` at position zero; this note exists so the
#: exclusion reads as a decision rather than an accident of the regex.
_OUT_OF_SCOPE_PREFIXES = ("Q-",)

#: ``paper-xx-*`` is a former candidate whose number has been vacated. The
#: pattern above already excludes it by requiring two digits; this names the
#: exclusion so it reads as a decision. See ``VACATED_PAPER_NUMBERS``.


def _holds_content(directory: Path) -> bool:
    """True if a directory holds anything but Python build artifacts.

    Without this, stale ``__pycache__/`` left behind by a directory move reads as
    a live paper identity: after P6-P10 moved out of ``papers/candidates/`` the
    old paths still existed on disk holding nothing but ``.pyc`` files, and a
    filesystem walk reported three unregistered papers that git had never heard
    of. The check is about repository content, so residue must not speak for it.
    """

    for path in directory.rglob("*"):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix in (".pyc", ".pyo"):
            continue
        return True
    return False


def paper_identity_findings(repo_root: Path) -> tuple[str, ...] | None:
    """Unregistered paper-numbered directories, or ``None`` if the tree is absent.

    Split out from the check so a caller can run it against any checkout.
    """

    papers = repo_root / "papers"
    if not papers.is_dir():
        return None
    found: list[str] = []
    for parent in (papers, papers / "candidates"):
        if not parent.is_dir():
            continue
        for child in sorted(parent.iterdir()):
            if not child.is_dir() or not _PAPER_DIR_PATTERN.match(child.name):
                continue
            if child.name.startswith(_OUT_OF_SCOPE_PREFIXES):
                continue
            relative = child.relative_to(repo_root).as_posix()
            if relative in REGISTERED_PAPER_DIRECTORIES:
                continue
            if not _holds_content(child):
                continue
            found.append(relative)
    return tuple(found)


def split_identity_findings(repo_root: Path) -> tuple[str, ...] | None:
    """Unresolved directory *names* that hold content in more than one location.

    Distinct from an unregistered directory, and distinct from P9/P10's two
    directories: those are two different slugs, one active and one a recorded
    predecessor. This is the *same* slug living under two parents at once ---
    ``papers/paper-11-state-as-computation`` beside
    ``papers/candidates/paper-11-state-as-computation`` --- which is one identity
    split across layouts rather than two identities.

    It is a live risk rather than a hypothetical: PR #715 was authored against the
    pre-refactor tree and still targets ``papers/candidates/``. Registering both
    spellings is what stops that landing from reading as identity *rot*; this is
    what stops it from being silent if both ever hold content at once.
    """

    papers = repo_root / "papers"
    if not papers.is_dir():
        return None
    locations: dict[str, list[str]] = {}
    for parent in (papers, papers / "candidates"):
        if not parent.is_dir():
            continue
        for child in sorted(parent.iterdir()):
            if not child.is_dir() or not _PAPER_DIR_PATTERN.match(child.name):
                continue
            if child.name.startswith(_OUT_OF_SCOPE_PREFIXES):
                continue
            if not _holds_content(child):
                continue
            locations.setdefault(child.name, []).append(
                child.relative_to(repo_root).as_posix()
            )
    recorded_successions = [
        frozenset((entry.active, *(directory for directory, _ in entry.retired)))
        for entry in PAPER_DIRECTORIES
    ]
    recorded_successions.extend(
        frozenset(
            (
                active,
                *(
                    directory
                    for directory, _ in FUTURE_RETIRED_PAPER_DIRECTORIES.get(
                        paper_id, ()
                    )
                ),
            )
        )
        for paper_id, active in FUTURE_PAPER_DIRECTORIES.items()
    )
    return tuple(
        f"{name} holds content in {' and '.join(paths)}"
        for name, paths in sorted(locations.items())
        if len(paths) > 1
        and not any(set(paths) <= succession for succession in recorded_successions)
    )


def _check_split_paper_identity(ledger: SuperiorityLedger) -> CheckResult:
    """One paper identity must live in one place."""

    findings = split_identity_findings(Path(__file__).resolve().parents[3])
    if findings is None:
        return cannot_check(
            SPLIT_PAPER_IDENTITY,
            "no papers/ tree is visible from this checkout, so paper identity "
            "cannot be resolved",
        )
    if findings:
        return failed(
            SPLIT_PAPER_IDENTITY,
            "a paper identity holds content in two locations at once, so nothing "
            "says which one carries it",
            findings,
        )
    return passed(
        SPLIT_PAPER_IDENTITY, "every paper identity holds content in exactly one location"
    )


def _check_stale_paper_identity(ledger: SuperiorityLedger) -> CheckResult:
    """A paper number carried by an unregistered directory is an identity ambiguity.

    Two directories under one paper number is not, by itself, a defect --- P9 and
    P10 each legitimately keep a merged predecessor beside the active identity,
    because live tests and other papers cite them. What is a defect is a directory
    the registry has never heard of, since then nothing says which one carries the
    identity and a reader has to open each README to guess. That is exactly how
    ``papers/candidates/README.md`` came to list two retired titles as the current
    P9 and P10 candidates.
    """

    repo_root = Path(__file__).resolve().parents[3]
    findings = paper_identity_findings(repo_root)
    if findings is None:
        return cannot_check(
            STALE_PAPER_IDENTITY,
            "no papers/ tree is visible from this checkout, so paper identity "
            "cannot be resolved",
        )
    if findings:
        return failed(
            STALE_PAPER_IDENTITY,
            "a paper-numbered directory is not registered as either the active "
            "identity or a recorded predecessor",
            tuple(f"{item} is unregistered" for item in findings),
        )
    retired = sum(len(entry.retired) for entry in PAPER_DIRECTORIES)
    return passed(
        STALE_PAPER_IDENTITY,
        f"every paper-numbered directory is registered: {len(PAPER_DIRECTORIES)} active "
        f"identities and {retired} recorded predecessor(s)",
    )


SUPERIORITY_CHECKS: tuple[SuperiorityCheck, ...] = (
    SuperiorityCheck(
        check_id=TERMINAL_COVERAGE,
        title="Every registered paper is adjudicated against its frozen gate list",
        failure_class="SILENT_TERMINAL_OMISSION",
        negative_fixture_id="tests/unit/programme/test_superiority_gates.py::test_coverage_blocks_on_missing_paper",
        evaluate=_check_terminal_coverage,
    ),
    SuperiorityCheck(
        check_id=MANUSCRIPT_SUBSTITUTION,
        title="A manuscript is not an outcome",
        failure_class="MANUSCRIPT_SUBSTITUTED_FOR_OUTCOME",
        negative_fixture_id="tests/unit/programme/test_superiority_gates.py::test_manuscript_substitution_fails",
        evaluate=_check_manuscript_substitution,
    ),
    SuperiorityCheck(
        check_id=MECHANISM_SUBSTITUTION,
        title="A bounded exact result is not a naturalistic result",
        failure_class="MECHANISM_SUBSTITUTED_FOR_TRANSFER",
        negative_fixture_id="tests/unit/programme/test_superiority_gates.py::test_mechanism_substitution_fails",
        evaluate=_check_mechanism_substitution,
    ),
    SuperiorityCheck(
        check_id=CANNOT_CHECK_LAUNDERING,
        title="A campaign that could not conclude has not concluded",
        failure_class="CANNOT_CHECK_COUNTED_AS_EVIDENCE",
        negative_fixture_id="tests/unit/programme/test_superiority_gates.py::test_cannot_check_laundering_fails",
        evaluate=_check_cannot_check_laundering,
    ),
    SuperiorityCheck(
        check_id=DONOR_INCOMPLETE_COMPARATOR,
        title="Superiority is measured against the strongest available comparator",
        failure_class="STRAW_COMPARATOR",
        negative_fixture_id="tests/unit/programme/test_superiority_gates.py::test_donor_incomplete_comparator_fails",
        evaluate=_check_donor_incomplete_comparator,
    ),
    SuperiorityCheck(
        check_id=COMPENSATORY_SCORING,
        title="A win never buys off a guard",
        failure_class="COMPENSATORY_SCORING",
        negative_fixture_id="tests/unit/programme/test_superiority_gates.py::test_compensatory_scoring_fails",
        evaluate=_check_compensatory_scoring,
    ),
    SuperiorityCheck(
        check_id=THIN_REPLICATION,
        title="Replication needs disjoint domains, not repeated ones",
        failure_class="THIN_REPLICATION",
        negative_fixture_id="tests/unit/programme/test_superiority_gates.py::test_thin_replication_fails",
        evaluate=_check_thin_replication,
    ),
    SuperiorityCheck(
        check_id=POST_HOC_FREEZE,
        title="The protocol is frozen before the outcome is seen",
        failure_class="POST_HOC_PROTOCOL",
        negative_fixture_id="tests/unit/programme/test_superiority_gates.py::test_post_hoc_freeze_fails",
        evaluate=_check_post_hoc_freeze,
    ),
    SuperiorityCheck(
        check_id=SELF_CERTIFICATION,
        title="Candidate custody cannot discharge its own terminal",
        failure_class="SELF_CERTIFICATION",
        negative_fixture_id="tests/unit/programme/test_superiority_gates.py::test_self_certification_fails",
        evaluate=_check_self_certification,
    ),
    SuperiorityCheck(
        check_id=STALE_PAPER_IDENTITY,
        title="Every paper number resolves to one registered identity",
        failure_class="STALE_PAPER_IDENTITY",
        negative_fixture_id="tests/unit/programme/test_superiority_gates.py::test_stale_paper_identity_fails",
        evaluate=_check_stale_paper_identity,
    ),
    SuperiorityCheck(
        check_id=SPLIT_PAPER_IDENTITY,
        title="One paper identity lives in one place",
        failure_class="SPLIT_PAPER_IDENTITY",
        negative_fixture_id="tests/unit/programme/test_superiority_gates.py::test_split_paper_identity_fails",
        evaluate=_check_split_paper_identity,
    ),
    SuperiorityCheck(
        check_id=UNCLASSIFIED_BLOCKER,
        title="A blocked terminal says why, and what would move it",
        failure_class="UNCLASSIFIED_BLOCKER",
        negative_fixture_id="tests/unit/programme/test_superiority_gates.py::test_unclassified_blocker_fails",
        evaluate=_check_unclassified_blocker,
    ),
    SuperiorityCheck(
        check_id=PREDECESSOR_REUSE,
        title="A predecessor result cannot discharge the terminal that supersedes it",
        failure_class="PREDECESSOR_REUSED_AS_DISCHARGE",
        negative_fixture_id="tests/unit/programme/test_superiority_gates.py::test_predecessor_reuse_fails",
        evaluate=_check_predecessor_reuse,
    ),
    SuperiorityCheck(
        check_id=CLAIM_WIDER_THAN_EVIDENCE,
        title="The advertised claim stays inside the earned grade",
        failure_class="CLAIM_WIDER_THAN_EVIDENCE",
        negative_fixture_id="tests/unit/programme/test_superiority_gates.py::test_claim_wider_than_evidence_fails",
        evaluate=_check_claim_wider_than_evidence,
    ),
)

SUPERIORITY_CHECK_IDS: tuple[str, ...] = tuple(check.check_id for check in SUPERIORITY_CHECKS)


def run_superiority_checks(
    ledger: SuperiorityLedger,
    checks: Sequence[SuperiorityCheck] | None = None,
) -> HostileCheckReport:
    """Run the battery. The report blocks unless every check passes."""

    selected = tuple(SUPERIORITY_CHECKS if checks is None else checks)
    return HostileCheckReport(
        results=tuple(check.run(ledger) for check in selected),
        expected_check_ids=tuple(check.check_id for check in selected),
    )


def validate_superiority_catalogue() -> tuple[str, ...]:
    """Structural errors in the battery. Empty means intact."""

    errors: list[str] = []
    seen: set[str] = set()
    for check in SUPERIORITY_CHECKS:
        if check.check_id in seen:
            errors.append(f"duplicate check id {check.check_id}")
        seen.add(check.check_id)
        if "::" not in check.negative_fixture_id:
            errors.append(
                f"{check.check_id} must name a negative fixture as path::test, "
                f"got {check.negative_fixture_id}"
            )
    return tuple(dict.fromkeys(errors))


__all__ = [
    "CANNOT_CHECK_LAUNDERING",
    "CLAIM_WIDER_THAN_EVIDENCE",
    "COMPENSATORY_SCORING",
    "DONOR_INCOMPLETE_COMPARATOR",
    "MANUSCRIPT_SUBSTITUTION",
    "MECHANISM_SUBSTITUTION",
    "POST_HOC_FREEZE",
    "PREDECESSOR_REUSE",
    "SELF_CERTIFICATION",
    "SPLIT_PAPER_IDENTITY",
    "STALE_PAPER_IDENTITY",
    "paper_identity_findings",
    "split_identity_findings",
    "SUPERIORITY_CHECKS",
    "SuperiorityCheck",
    "run_superiority_checks",
    "SUPERIORITY_CHECK_IDS",
    "TERMINAL_COVERAGE",
    "UNCLASSIFIED_BLOCKER",
    "THIN_REPLICATION",
    "validate_superiority_catalogue",
]
