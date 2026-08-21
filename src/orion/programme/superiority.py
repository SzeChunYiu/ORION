"""Adjudication vocabulary for the P1-P10 superiority terminals (issues #649-#663).

Why this module exists
----------------------
Every one of the ten ``P<n>-U`` issues ends in a ``Done when`` list, and each of
those lists is a *terminal*: the condition under which that paper's programme is
finished. The recurring failure is not that the terminals are unclear. It is that
a different, cheaper artifact keeps arriving in their place and the substitution
is only caught by a human reading prose. Issue #649 records the correction in as
many words --- "No manuscript-completion status is allowed to substitute for this
issue's superiority terminal" --- after a merged manuscript refinement had been
read as progress against a protected-superiority gate.

So the adjudication is made typed here rather than left to prose. A gate names
the *kind* of terminal it demands; evidence names the *grade* of artifact that
was actually produced; and :func:`adjudicate` decides whether that grade is
admissible for that kind. A bounded exact result cannot discharge a naturalistic
protected gate no matter how strong it is, because the grades do not overlap.

Three properties are load-bearing, and they match
``orion.programme.hostile``:

1. **Three outcomes.** ``PASS`` / ``FAIL`` / ``CANNOT_CHECK``.
2. **CANNOT_CHECK blocks.** An unrecorded precondition is never a pass. This is
   the state most of these gates are actually in, and it is deliberately not
   spelled ``FAIL``: nothing has been refuted, nothing has been shown either.
3. **Non-compensatory.** A paper terminal is earned only when *every* gate
   passes. A superiority win does not buy off a failed harm guard, which is the
   exact shape of the pre-registered guards in #649, #650, #651 and #653.

Nothing here grants closure. :meth:`PaperSuperiorityRecord.terminal` returns a
status; the authority to close an issue sits with the repository owner.

These modules are deliberately not re-exported from ``orion.programme.__init__``.
That file's export list is a shared registry under ``AGENTS.md``, owned by the
lane running the Phase-4 wave; importing by full module path costs a caller
nothing and keeps this addition to files no other lane is editing.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from orion.programme.identity import PROGRAMME_SCHEMA_NAMESPACE
from orion.programme.programme_state import CANDIDATE_CUSTODY, EXTERNAL_CUSTODY
from orion.programme.records import Outcome, dedup

SUPERIORITY_GATE_SCHEMA = f"{PROGRAMME_SCHEMA_NAMESPACE}.superiority-gate.v1"
SUPERIORITY_LEDGER_SCHEMA = f"{PROGRAMME_SCHEMA_NAMESPACE}.superiority-ledger.v1"
SUPERIORITY_REPORT_SCHEMA = f"{PROGRAMME_SCHEMA_NAMESPACE}.superiority-report.v1"


class TerminalKind(str, Enum):
    """What kind of thing a ``Done when`` bullet is actually asking for.

    The kinds are distinguished by *what evidence could discharge them*, not by
    subject matter. Two bullets about false-merge rates land in different kinds
    if one asks for a win and the other asks for a ceiling not to be crossed.
    """

    PROTECTED_SUPERIORITY = "PROTECTED_SUPERIORITY"
    """A win over a donor-complete comparator on protected, prospective outcomes."""

    HARM_GUARD = "HARM_GUARD"
    """A ceiling that must hold. Never tradeable against a superiority win."""

    REPLICATION = "REPLICATION"
    """The effect survives a disjoint domain and an independent implementation."""

    FORMAL_GENERALIZATION = "FORMAL_GENERALIZATION"
    """A theorem from primitive semantics, with the finite result as a corollary."""

    SUCCESSOR_MECHANIC = "SUCCESSOR_MECHANIC"
    """A negative or tied family converted into a prospectively validated mechanic."""

    INDEPENDENT_REVIEW = "INDEPENDENT_REVIEW"
    """Someone outside the producing lane checked the artifact.

    Distinct from ``REPLICATION``, which asks whether an *effect* survives a
    disjoint domain and a second implementation. An independent proof or checker
    review asks whether a *formal artifact* holds up under outside scrutiny: it
    has no domains to be disjoint across, and its natural evidence is a
    mechanized theorem plus a reviewer's report.

    Typing these as ``REPLICATION`` made three terminals unpassable via their own
    documented unblock path --- #654's "Independent proof/checker review", #655's
    "Independent formal/empirical reproduction" and #656's "Independent formal and
    systems reproduction" all sat behind an admissible set of
    ``{PROSPECTIVE_PROTECTED}`` while their blockers said to mechanize a proof and
    have it reviewed. Caught by review on PR #739.

    Note the conjunction in #655 and #656: both name a formal *and* an empirical
    review. One grade cannot represent both, so this kind admits either and the
    requirement that both be produced lives in those gates' blocker text, which
    states it explicitly. A single evidence entry claiming only one half will pass
    this kind and should not be recorded until both exist.
    """

    SCOPE_DISCIPLINE = "SCOPE_DISCIPLINE"
    """The advertised claim does not exceed the strongest grade actually earned."""

    SCOPE_EXPANSION = "SCOPE_EXPANSION"
    """The advertised claim *reaches past* the registered families, and is backed there.

    Only #649's fourth bullet asks for this, and it asks for the opposite of
    discipline: "Claim is wider than the current registered families because new
    heterogeneous naturalistic tasks support it." Typing it as
    ``SCOPE_DISCIPLINE`` would let a correctly-narrow claim pass a terminal that
    demands a wider one, which is the inversion this kind exists to prevent.
    """


class EvidenceGrade(str, Enum):
    """What class of artifact was actually produced for a gate.

    Ordered by :attr:`rank` for the scope comparison only. The ordering is *not*
    a licence to substitute: admissibility is decided by
    :data:`ADMISSIBLE_GRADES`, which is a relation and not a threshold. A
    mechanized theorem outranks nothing empirical and is outranked by nothing
    empirical; it discharges a different kind of gate entirely.
    """

    ABSENT = "ABSENT"
    """No artifact. Distinct from an artifact that ran and could not conclude."""

    CANNOT_CHECK = "CANNOT_CHECK"
    """A campaign executed and terminated before an outcome.

    This is the grade of the P1-U R2/R3/R4/R5 acquisition campaigns: real work,
    honestly preserved, and worth exactly zero against a superiority gate.
    """

    MANUSCRIPT_COMPLETION = "MANUSCRIPT_COMPLETION"
    """A written, refined or merged manuscript. Never evidence of an outcome."""

    MECHANISM_NON_VACUITY = "MECHANISM_NON_VACUITY"
    """An exact result on an authored finite arena.

    The whole ``P<n>-X`` series sits here: bounded exact contract families with an
    information-equivalent ideal product tying exactly. Strong evidence that a
    mechanism is not vacuous; no evidence at all about naturalistic transfer.
    """

    MECHANIZED_THEOREM = "MECHANIZED_THEOREM"
    """A machine-checked general theorem from primitive semantics."""

    BOUNDED_PROTECTED = "BOUNDED_PROTECTED"
    """A protected outcome, bounded to the registered families it was run on."""

    PROSPECTIVE_PROTECTED = "PROSPECTIVE_PROTECTED"
    """A protected outcome on fresh naturalistic tasks under external custody."""

    @property
    def rank(self) -> int:
        return _GRADE_RANK[self]


_GRADE_RANK: dict[EvidenceGrade, int] = {
    EvidenceGrade.ABSENT: 0,
    EvidenceGrade.CANNOT_CHECK: 1,
    EvidenceGrade.MANUSCRIPT_COMPLETION: 2,
    EvidenceGrade.MECHANISM_NON_VACUITY: 3,
    EvidenceGrade.MECHANIZED_THEOREM: 4,
    EvidenceGrade.BOUNDED_PROTECTED: 5,
    EvidenceGrade.PROSPECTIVE_PROTECTED: 6,
}


ADMISSIBLE_GRADES: dict[TerminalKind, frozenset[EvidenceGrade]] = {
    TerminalKind.PROTECTED_SUPERIORITY: frozenset({EvidenceGrade.PROSPECTIVE_PROTECTED}),
    # A guard is a ceiling, and a ceiling can be established on the registered
    # families it was declared over. It still has to be protected: a guard read
    # off an authored arena is a guard against the author.
    TerminalKind.HARM_GUARD: frozenset(
        {EvidenceGrade.BOUNDED_PROTECTED, EvidenceGrade.PROSPECTIVE_PROTECTED}
    ),
    TerminalKind.REPLICATION: frozenset({EvidenceGrade.PROSPECTIVE_PROTECTED}),
    # Either an independently checked formal artifact or an independent
    # empirical reproduction. Which one depends on what the paper's terminal
    # is about, and both are genuinely 'someone outside checked this'.
    TerminalKind.INDEPENDENT_REVIEW: frozenset(
        {EvidenceGrade.MECHANIZED_THEOREM, EvidenceGrade.PROSPECTIVE_PROTECTED}
    ),
    TerminalKind.FORMAL_GENERALIZATION: frozenset({EvidenceGrade.MECHANIZED_THEOREM}),
    TerminalKind.SUCCESSOR_MECHANIC: frozenset({EvidenceGrade.PROSPECTIVE_PROTECTED}),
    # Scope discipline is the one kind decided by comparing a declaration to the
    # rest of the ledger rather than by the grade attached to it, so every grade
    # is admissible here and the work is done in _adjudicate_scope.
    TerminalKind.SCOPE_DISCIPLINE: frozenset(EvidenceGrade),
    TerminalKind.SCOPE_EXPANSION: frozenset(EvidenceGrade),
}

_SCOPE_KINDS = frozenset({TerminalKind.SCOPE_DISCIPLINE, TerminalKind.SCOPE_EXPANSION})


class ClaimScope(str, Enum):
    """How wide a paper currently advertises its claim."""

    NONE = "NONE"
    BOUNDED_EXACT = "BOUNDED_EXACT"
    BOUNDED_PROTECTED = "BOUNDED_PROTECTED"
    GENERAL_PROSPECTIVE = "GENERAL_PROSPECTIVE"

    @property
    def rank(self) -> int:
        return _SCOPE_RANK[self]


_SCOPE_RANK: dict[ClaimScope, int] = {
    ClaimScope.NONE: 0,
    ClaimScope.BOUNDED_EXACT: 1,
    ClaimScope.BOUNDED_PROTECTED: 2,
    ClaimScope.GENERAL_PROSPECTIVE: 3,
}

MAX_SCOPE_FOR_GRADE: dict[EvidenceGrade, ClaimScope] = {
    EvidenceGrade.ABSENT: ClaimScope.NONE,
    EvidenceGrade.CANNOT_CHECK: ClaimScope.NONE,
    EvidenceGrade.MANUSCRIPT_COMPLETION: ClaimScope.NONE,
    EvidenceGrade.MECHANISM_NON_VACUITY: ClaimScope.BOUNDED_EXACT,
    # A theorem licenses a claim about its own semantics, not about systems.
    EvidenceGrade.MECHANIZED_THEOREM: ClaimScope.BOUNDED_EXACT,
    EvidenceGrade.BOUNDED_PROTECTED: ClaimScope.BOUNDED_PROTECTED,
    EvidenceGrade.PROSPECTIVE_PROTECTED: ClaimScope.GENERAL_PROSPECTIVE,
}

MIN_REPLICATION_DOMAINS = 2


class ResponsibilityClass(str, Enum):
    """Why a terminal is blocked, in P1's own frozen vocabulary.

    Transcribed from ``development/p1-u-gpt-r2-naturalistic/DEVELOPMENT_PACKET.md``
    rather than invented here. Reusing it is deliberate: P1's scientific claim is
    that a system should identify which of these classes is load-bearing *before*
    escalating, and a ledger that records blockers in some other vocabulary could
    not be read against that claim.

    ``NO_HIGH_LEVEL_REFORMULATION`` and ``UNRESOLVED`` are in the packet's list
    and are omitted here: the first is a control label for an episode, not a
    reason a programme is stuck, and the second is what this field exists to stop
    a blocked gate from silently being.
    """

    SEARCH_OR_EVIDENCE = "SEARCH_OR_EVIDENCE"
    REPRESENTATION_OR_INTERFACE = "REPRESENTATION_OR_INTERFACE"
    IMPLEMENTATION_OR_ENVIRONMENT = "IMPLEMENTATION_OR_ENVIRONMENT"
    MEASUREMENT_OR_EVALUATOR = "MEASUREMENT_OR_EVALUATOR"
    OBJECTIVE_OR_MODEL_CLASS = "OBJECTIVE_OR_MODEL_CLASS"
    PROBLEM_BOUNDARY = "PROBLEM_BOUNDARY"


class Actionability(str, Enum):
    """What it would take to move a blocked terminal, ordered by nearness.

    This is the field that makes the report a work queue rather than a status
    board. ``CANNOT_CHECK`` was covering three unrelated situations --- a
    one-file defect, an evaluation arena that does not exist, and a theorem
    nobody has proved --- under one word, which is precisely the collapse the
    three-valued outcome exists to prevent one level up.
    """

    ACTIONABLE_NOW = "ACTIONABLE_NOW"
    """A defined change to code or artifacts already in this repository."""

    BLOCKED_ON_UPSTREAM = "BLOCKED_ON_UPSTREAM"
    """Another lane's in-flight work. Nameable by issue or PR."""

    BLOCKED_ON_CAMPAIGN = "BLOCKED_ON_CAMPAIGN"
    """The arena and comparator exist; a protected run has not been scored."""

    BLOCKED_ON_NEW_ARENA = "BLOCKED_ON_NEW_ARENA"
    """The evaluation object itself does not exist yet and must be built."""

    BLOCKED_ON_PROOF = "BLOCKED_ON_PROOF"
    """Needs a mechanized theorem from primitive semantics."""

    @property
    def queue_rank(self) -> int:
        return _ACTIONABILITY_RANK[self]


_ACTIONABILITY_RANK: dict[Actionability, int] = {
    Actionability.ACTIONABLE_NOW: 0,
    Actionability.BLOCKED_ON_UPSTREAM: 1,
    Actionability.BLOCKED_ON_CAMPAIGN: 2,
    Actionability.BLOCKED_ON_NEW_ARENA: 3,
    Actionability.BLOCKED_ON_PROOF: 4,
}


@dataclass(frozen=True)
class GateBlocker:
    """Why one terminal is blocked, and what would unblock it.

    A blocked gate without one of these is an unanswered question wearing the
    costume of a status. ``HC-SUP-UNCLASSIFIED-BLOCKER`` refuses that.
    """

    gate_id: str
    responsibility: ResponsibilityClass
    actionability: Actionability
    statement: str
    """What is actually blocking, in one sentence."""

    unblock: str
    """What would move it. Concrete enough to be picked up."""

    refs: tuple[str, ...] = ()
    """Issues, PRs, files or failure records that evidence the diagnosis."""

    def __post_init__(self) -> None:
        for name in ("gate_id", "statement", "unblock"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"gate blocker {name} is required")


@dataclass(frozen=True)
class TerminalGate:
    """One ``Done when`` bullet, transcribed and typed.

    ``statement`` is the bullet verbatim. Keeping the source text next to the
    typing is what makes a mis-typing reviewable: a reader can check the kind
    against the words without leaving the file.
    """

    gate_id: str
    paper_id: str
    issue_number: int
    kind: TerminalKind
    statement: str
    bounded_terminal_admissible: bool = False
    """True where the issue itself offers a narrower disjunct.

    Two bullets do: #662's "second-family replication **or** explicit
    family-bounded terminal" and #663's "independently reproduced **or** retained
    as a negative". Both are discharged by a protected bounded result that says
    so explicitly, and the flag exists so that fidelity to the issue text does
    not require weakening :data:`ADMISSIBLE_GRADES` for every other gate.

    It does two things, and the second was missing at first --- caught by review
    on PR #739. Widening the admissible grades is not enough: a ``REPLICATION``
    gate also demands :data:`MIN_REPLICATION_DOMAINS` distinct domains and an
    independent implementation, and the bounded disjunct exists *precisely
    because those cannot be met*. A family-bounded terminal is bounded to one
    family; a negative retained as a negative was never reproduced. Demanding two
    domains of either is self-contradictory, so on this path those two
    requirements are lifted. Everything else still holds: the outcome must be
    protected, pre-frozen and under external custody.
    """

    def __post_init__(self) -> None:
        for name in ("gate_id", "paper_id", "statement"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"terminal gate {name} is required")
        if self.issue_number <= 0:
            raise ValueError("terminal gate issue_number must be a positive issue id")

    @property
    def admissible_grades(self) -> frozenset[EvidenceGrade]:
        grades = ADMISSIBLE_GRADES[self.kind]
        if self.bounded_terminal_admissible:
            return grades | {EvidenceGrade.BOUNDED_PROTECTED}
        return grades


@dataclass(frozen=True)
class GateEvidence:
    """What has actually been produced against one gate.

    Every precondition is a ``bool | None`` rather than a ``bool``. ``None`` means
    *not recorded*, and it yields ``CANNOT_CHECK`` rather than ``FAIL``: a
    campaign that never stated whether its comparator was donor-complete has not
    been shown to have a weak comparator, it has been shown to be unevaluable.
    Defaulting these to ``False`` would report refutations that nobody earned.
    """

    gate_id: str
    grade: EvidenceGrade
    artifact_refs: tuple[str, ...] = ()
    protocol_frozen_before_outcome: bool | None = None
    comparator_donor_complete: bool | None = None
    evaluator_custody: str | None = None
    domains: tuple[str, ...] = ()
    independent_implementation: bool | None = None
    harm_guard_gate_ids: tuple[str, ...] = ()
    """Guards this claim declares itself non-compensatorily conditioned on.

    Read by ``HC-SUP-COMPENSATORY-SCORING``, which fails on a *dangling*
    reference: a claim conditioned on a guard the paper does not declare. The
    stronger rule --- no win stands while any of the paper's guards blocks ---
    does not need this field and is enforced over the paper's whole gate list, so
    leaving it empty weakens nothing.
    """

    declared_scope: ClaimScope | None = None
    """Only meaningful on a ``SCOPE_DISCIPLINE`` or ``SCOPE_EXPANSION`` gate."""

    notes: str = ""

    def __post_init__(self) -> None:
        if not str(self.gate_id).strip():
            raise ValueError("gate evidence gate_id is required")
        if self.grade is not EvidenceGrade.ABSENT and not self.artifact_refs:
            raise ValueError(
                f"gate evidence {self.gate_id} claims grade {self.grade.value} "
                "without naming an artifact"
            )
        if self.evaluator_custody is not None and self.evaluator_custody not in (
            EXTERNAL_CUSTODY,
            CANDIDATE_CUSTODY,
        ):
            raise ValueError(
                f"gate evidence {self.gate_id} custody must be "
                f"{EXTERNAL_CUSTODY!r} or {CANDIDATE_CUSTODY!r}"
            )


@dataclass(frozen=True)
class GateStatus:
    """Adjudication of one gate. ``CANNOT_CHECK`` blocks exactly as ``FAIL`` does."""

    gate_id: str
    kind: TerminalKind
    outcome: Outcome
    reason: str
    findings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.reason.strip():
            raise ValueError("a gate status must state its reason")

    @property
    def blocks(self) -> bool:
        return self.outcome.blocks


def _status(
    gate: TerminalGate, outcome: Outcome, reason: str, findings: tuple[str, ...] = ()
) -> GateStatus:
    return GateStatus(
        gate_id=gate.gate_id, kind=gate.kind, outcome=outcome, reason=reason, findings=findings
    )


def _grade_admissibility_errors(gate: TerminalGate, evidence: GateEvidence) -> tuple[str, ...]:
    if evidence.grade in gate.admissible_grades:
        return ()
    admissible = ", ".join(sorted(grade.value for grade in gate.admissible_grades))
    return (
        f"grade {evidence.grade.value} cannot discharge a {gate.kind.value} terminal; "
        f"admissible: {admissible}",
    )


def _protected_preconditions(
    gate: TerminalGate, evidence: GateEvidence
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return ``(unrecorded, violated)`` preconditions for a protected outcome.

    Donor-completeness is required of ``PROTECTED_SUPERIORITY`` only. Beating the
    strongest available comparator is what a superiority claim *means*; a guard
    such as #649's "no-regression/no-unnecessary-reformulation" is a ceiling on
    the system's own behaviour and often has no comparator at all. Demanding one
    everywhere would park those gates at ``CANNOT_CHECK`` permanently, or invite
    a ``true`` that means nothing --- and a precondition that gets filled in to
    make a report move is worse than no precondition.
    """

    unrecorded: list[str] = []
    violated: list[str] = []

    if evidence.protocol_frozen_before_outcome is None:
        unrecorded.append("protocol freeze relative to outcome access is not recorded")
    elif not evidence.protocol_frozen_before_outcome:
        violated.append("protocol was not frozen before outcome access")

    if gate.kind is TerminalKind.PROTECTED_SUPERIORITY:
        if evidence.comparator_donor_complete is None:
            unrecorded.append("comparator donor-completeness is not recorded")
        elif not evidence.comparator_donor_complete:
            violated.append("comparator is not donor-complete")

    if evidence.evaluator_custody is None:
        unrecorded.append("evaluator custody is not recorded")
    elif evidence.evaluator_custody != EXTERNAL_CUSTODY:
        violated.append(
            f"evaluator custody is {evidence.evaluator_custody}, not {EXTERNAL_CUSTODY}"
        )

    return tuple(dedup(unrecorded)), tuple(dedup(violated))


def on_bounded_disjunct(gate: TerminalGate, evidence: GateEvidence) -> bool:
    """True when this evidence takes the narrower path the issue itself offers.

    See :attr:`TerminalGate.bounded_terminal_admissible`. Kept as one predicate so
    that :mod:`orion.programme.checks_superiority` decides identically --- the
    first version of this had ``adjudicate`` and ``HC-SUP-THIN-REPLICATION``
    disagreeing about the same row.
    """

    return (
        gate.bounded_terminal_admissible
        and evidence.grade is EvidenceGrade.BOUNDED_PROTECTED
    )


def _adjudicate_scope(
    gate: TerminalGate,
    declared_scope: ClaimScope | None,
    strongest_grade: EvidenceGrade,
) -> GateStatus:
    if declared_scope is None:
        return _status(
            gate,
            Outcome.CANNOT_CHECK,
            "the paper's declared claim scope is not recorded, so it cannot be "
            "compared against the strongest grade in the ledger",
        )
    permitted = MAX_SCOPE_FOR_GRADE[strongest_grade]
    if declared_scope.rank > permitted.rank:
        return _status(
            gate,
            Outcome.FAIL,
            f"declared claim scope {declared_scope.value} exceeds "
            f"{permitted.value}, the widest scope licensed by the strongest grade "
            f"in this paper's ledger ({strongest_grade.value})",
        )
    return _status(
        gate,
        Outcome.PASS,
        f"declared claim scope {declared_scope.value} is within "
        f"{permitted.value}, licensed by grade {strongest_grade.value}",
    )


def _adjudicate_scope_expansion(
    gate: TerminalGate,
    declared_scope: ClaimScope | None,
    strongest_grade: EvidenceGrade,
) -> GateStatus:
    """Discipline first, then width.

    An over-wide claim is a ``FAIL`` here for the same reason it is under
    discipline, so that half is delegated rather than restated. What this kind
    adds is the second requirement: a correctly-bounded claim satisfies
    discipline and does *not* satisfy expansion.
    """

    disciplined = _adjudicate_scope(gate, declared_scope, strongest_grade)
    if disciplined.outcome is not Outcome.PASS:
        return disciplined
    if declared_scope is not ClaimScope.GENERAL_PROSPECTIVE:
        return _status(
            gate,
            Outcome.CANNOT_CHECK,
            "this terminal asks for a claim wider than the registered families; the "
            f"paper currently declares {declared_scope.value}, which is correctly "
            "bounded but has not yet reached the demanded width",
        )
    return _status(
        gate,
        Outcome.PASS,
        f"claim reaches {declared_scope.value}, licensed by grade {strongest_grade.value}",
    )


def adjudicate(
    gate: TerminalGate,
    evidence: GateEvidence | None,
    *,
    strongest_grade: EvidenceGrade = EvidenceGrade.ABSENT,
    declared_claim_scope: ClaimScope | None = None,
) -> GateStatus:
    """Decide one gate. Absence blocks; a wrong-kind artifact fails.

    ``strongest_grade`` and ``declared_claim_scope`` are properties of the whole
    paper and are consulted only by the two scope kinds, which ask a question
    about the paper rather than about their own evidence. A scope recorded on the
    gate's own evidence wins over the paper-level default, so a per-gate
    declaration can be narrower than the paper's headline claim.
    """

    if gate.kind in _SCOPE_KINDS:
        declared = declared_claim_scope
        if evidence is not None and evidence.declared_scope is not None:
            declared = evidence.declared_scope
        if gate.kind is TerminalKind.SCOPE_EXPANSION:
            return _adjudicate_scope_expansion(gate, declared, strongest_grade)
        return _adjudicate_scope(gate, declared, strongest_grade)

    if evidence is None:
        return _status(
            gate, Outcome.CANNOT_CHECK, "no evidence is recorded against this terminal"
        )
    if evidence.gate_id != gate.gate_id:
        return _status(
            gate, Outcome.CANNOT_CHECK, "evidence is recorded against a different gate id"
        )

    if evidence.grade is EvidenceGrade.ABSENT:
        return _status(gate, Outcome.CANNOT_CHECK, "no artifact is recorded against this terminal")

    substitution = _grade_admissibility_errors(gate, evidence)
    if substitution:
        return _status(gate, Outcome.FAIL, substitution[0], substitution)

    if gate.kind is TerminalKind.FORMAL_GENERALIZATION:
        # A theorem is discharged by the artifact itself. Custody and comparators
        # are empirical-campaign preconditions and asking for them here would
        # block every provable gate on a category error.
        return _status(
            gate,
            Outcome.PASS,
            f"mechanized theorem recorded: {', '.join(evidence.artifact_refs)}",
        )

    if gate.kind is TerminalKind.INDEPENDENT_REVIEW:
        if evidence.independent_implementation is None:
            return _status(
                gate,
                Outcome.CANNOT_CHECK,
                "independence of the reviewer is not recorded",
            )
        if not evidence.independent_implementation:
            return _status(
                gate, Outcome.FAIL, "the review was not carried out independently"
            )
        if evidence.grade is EvidenceGrade.MECHANIZED_THEOREM:
            # Same category point as above: a proof review has no evaluator
            # custody and no outcome to have been frozen before.
            return _status(
                gate,
                Outcome.PASS,
                f"independent formal review recorded: {', '.join(evidence.artifact_refs)}",
            )

    unrecorded, violated = _protected_preconditions(gate, evidence)
    if violated:
        return _status(gate, Outcome.FAIL, violated[0], tuple(violated))
    if unrecorded:
        return _status(gate, Outcome.CANNOT_CHECK, unrecorded[0], tuple(unrecorded))

    if gate.kind is TerminalKind.REPLICATION and on_bounded_disjunct(gate, evidence):
        return _status(
            gate,
            Outcome.PASS,
            "discharged on the narrower disjunct this terminal offers, at grade "
            f"{evidence.grade.value}: {', '.join(evidence.artifact_refs)}",
        )

    if gate.kind is TerminalKind.REPLICATION:
        replication_findings: list[str] = []
        if len(set(evidence.domains)) < MIN_REPLICATION_DOMAINS:
            replication_findings.append(
                f"replication needs at least {MIN_REPLICATION_DOMAINS} distinct domains; "
                f"recorded: {len(set(evidence.domains))}"
            )
        if evidence.independent_implementation is False:
            replication_findings.append("no independent implementation is recorded")
        if replication_findings:
            return _status(
                gate, Outcome.FAIL, replication_findings[0], tuple(replication_findings)
            )
        if evidence.independent_implementation is None:
            return _status(
                gate,
                Outcome.CANNOT_CHECK,
                "independent implementation is not recorded",
            )

    return _status(
        gate,
        Outcome.PASS,
        f"{gate.kind.value} discharged at grade {evidence.grade.value} by "
        f"{', '.join(evidence.artifact_refs)}",
    )


@dataclass(frozen=True)
class PredecessorArtifact:
    """A prior result that is *not* offered as discharging any terminal.

    Every one of these ten programmes stands on a predecessor: the ``P<n>-X``
    bounded exact terminals, P5's ``21/24`` attribution record, P9's bounded
    structural-learning receipt. Naming them is how the ledger stays informative
    without counting them --- the whole point of #649's status correction is that
    a predecessor is real work *and* discharges nothing.

    ``terminal`` is the artifact's own terminal string where it declares one, so
    the boundary it drew around itself travels with the reference.
    """

    artifact_ref: str
    grade: "EvidenceGrade"
    terminal: str = ""
    note: str = ""

    def __post_init__(self) -> None:
        if not str(self.artifact_ref).strip():
            raise ValueError("predecessor artifact_ref is required")


class PaperTerminalStatus(str, Enum):
    """Aggregate state of one paper's ``Done when`` list."""

    EARNED = "EARNED"
    NOT_EARNED = "NOT_EARNED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class PaperSuperiorityRecord:
    """One paper's gates and whatever evidence exists against them."""

    paper_id: str
    issue_number: int
    gates: tuple[TerminalGate, ...]
    evidence: tuple[GateEvidence, ...] = ()
    predecessor_artifacts: tuple[PredecessorArtifact, ...] = ()
    blockers: tuple[GateBlocker, ...] = ()
    declared_claim_scope: ClaimScope | None = None
    """How wide this paper currently advertises its claim, ``None`` if unrecorded.

    Held on the paper rather than on a gate because seven of the ten issues have
    no ``SCOPE_DISCIPLINE`` bullet, and ``HC-SUP-CLAIM-WIDER-THAN-EVIDENCE`` has
    to be able to ask the question of all ten.
    """

    def __post_init__(self) -> None:
        if not self.gates:
            raise ValueError(f"paper {self.paper_id} must declare at least one terminal gate")
        foreign = [gate.gate_id for gate in self.gates if gate.paper_id != self.paper_id]
        if foreign:
            raise ValueError(f"paper {self.paper_id} declares gates owned by another paper")

    @property
    def evidence_by_gate(self) -> dict[str, GateEvidence]:
        return {item.gate_id: item for item in self.evidence}

    @property
    def blockers_by_gate(self) -> dict[str, GateBlocker]:
        return {item.gate_id: item for item in self.blockers}

    def unclassified_blocked_gate_ids(self) -> tuple[str, ...]:
        """Blocked gates with no recorded reason, in registry order."""

        recorded = self.blockers_by_gate
        return tuple(
            status.gate_id
            for status in self.statuses()
            if status.blocks and status.gate_id not in recorded
        )

    def work_queue(self) -> tuple[GateBlocker, ...]:
        """This paper's blockers, nearest-to-actionable first.

        Ties break on gate id so the queue is stable across runs; a queue that
        reorders itself on every regeneration cannot be diffed.
        """

        recorded = self.blockers_by_gate
        blocked = [status.gate_id for status in self.statuses() if status.blocks]
        return tuple(
            sorted(
                (recorded[gate_id] for gate_id in blocked if gate_id in recorded),
                key=lambda item: (item.actionability.queue_rank, item.gate_id),
            )
        )

    @property
    def strongest_grade(self) -> EvidenceGrade:
        """Highest grade anywhere in this paper's ledger, predecessors included.

        Predecessors count here and only here. A bounded exact predecessor does
        license a bounded exact *claim* --- that is what the ``P<n>-X`` terminals
        already say about themselves --- while discharging no ``P<n>-U`` gate,
        because discharge is decided by :data:`ADMISSIBLE_GRADES` rather than by
        this number. Keeping the two apart is what lets the scope kinds ask
        "is the advertised claim honest?" without reopening "is the terminal
        earned?".

        Scope-gate evidence is excluded: its grade describes the declaration, not
        an outcome, so counting it would let a paper license its own claim width
        by asserting one.
        """

        scope_gate_ids = {
            gate.gate_id for gate in self.gates if gate.kind in _SCOPE_KINDS
        }
        grades = [item.grade for item in self.evidence if item.gate_id not in scope_gate_ids]
        grades.extend(item.grade for item in self.predecessor_artifacts)
        if not grades:
            return EvidenceGrade.ABSENT
        return max(grades, key=lambda grade: grade.rank)

    def statuses(self) -> tuple[GateStatus, ...]:
        by_gate = self.evidence_by_gate
        strongest = self.strongest_grade
        return tuple(
            adjudicate(
                gate,
                by_gate.get(gate.gate_id),
                strongest_grade=strongest,
                declared_claim_scope=self.declared_claim_scope,
            )
            for gate in self.gates
        )

    def terminal(self) -> PaperTerminalStatus:
        """Non-compensatory: every gate must pass, or the terminal is not earned."""

        statuses = self.statuses()
        if any(status.outcome is Outcome.FAIL for status in statuses):
            return PaperTerminalStatus.NOT_EARNED
        if any(status.outcome is Outcome.CANNOT_CHECK for status in statuses):
            return PaperTerminalStatus.CANNOT_CHECK
        return PaperTerminalStatus.EARNED


__all__ = [
    "ADMISSIBLE_GRADES",
    "MAX_SCOPE_FOR_GRADE",
    "MIN_REPLICATION_DOMAINS",
    "SUPERIORITY_GATE_SCHEMA",
    "SUPERIORITY_LEDGER_SCHEMA",
    "SUPERIORITY_REPORT_SCHEMA",
    "ClaimScope",
    "EvidenceGrade",
    "GateEvidence",
    "GateStatus",
    "PaperSuperiorityRecord",
    "Actionability",
    "GateBlocker",
    "PaperTerminalStatus",
    "PredecessorArtifact",
    "ResponsibilityClass",
    "TerminalGate",
    "TerminalKind",
    "adjudicate",
    "on_bounded_disjunct",
]
