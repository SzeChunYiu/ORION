"""Responsibility-scoped epistemic licensing — the P1 V2 mechanism.

**ADDITIVE ONLY — P1 V1 is untouched, and this module states it as a rule.**
``PROTOCOL_V1.json`` is frozen at ``P1.hidden-formulation.v1.1`` and is read
here, never written. The frozen case suites, their two content fingerprints
(pilot ``7a50a2d5…``, test ``21b461d8…``), ``cases.py``, ``observation.py``,
``contradiction.py`` and every V1 result under
``papers/orion-11-recursive-epistemic-reconstruction/results/`` are inputs to
this module and are not modified, re-scored or superseded by it. No number
reported by P1 V1 changes because this file exists. The V2 manifest below lives
in code, next to the mechanism it binds, precisely so that adding it required
no edit to the frozen protocol.

The claim this implements
-------------------------

``NEAREST_WORK_MATRIX_V2.md`` records the smallest surviving Paper-I claim
after absorbing 33 neighbouring mechanisms:

    only a formulation or search-universe responsibility licenses a
    coordinate-specific rewrite of ``W`` or ``M``, while evidence and execution
    responsibilities are routed to acquisition and repair and are denied the
    rewrite licence.

ARTS diagnoses implementation-fault versus bad-hypothesis. Iris attributes a
failure to the specific claim that is wrong. MAST sorts failures into fourteen
modes. Who&When localises an agent and a step. All four produce a **descriptive
label**. None attaches a **permission** to it. The licensing matrix below is
that permission, written down.

Three properties make it a mechanism rather than a table
--------------------------------------------------------

1. **Total.** Every ``Responsibility`` has a row. There is no default and no
   ``.get`` fallback: a responsibility the table does not classify is refused,
   because a permissive default is exactly how an evidence diagnosis would
   acquire a rewrite licence.
2. **Coordinate-specific.** A row permits at most one mutating action, and that
   action's coordinate is the one ``baselines.COORDINATE_BY_RESPONSIBILITY``
   already assigns to the responsibility. A MEASUREMENT diagnosis licenses
   ``M.MEASUREMENT`` and not ``W.REPRESENTATIONS``.
3. **Non-compensatory, and re-checked at issue time.** ``issue_license`` does
   not trust the table. It re-derives the invariant from the requested action's
   coordinate namespace and the diagnosed class's authority class, and refuses
   with ``LICENSING_INVARIANT_BREACH`` if the two disagree. This is the same
   pattern as ``kernel.hard_gates``: the gate is the thing that cannot be
   outweighed, so it is evaluated last and independently. A test corrupts the
   matrix and asserts the alarm fires.

Two divergences recorded rather than smoothed over
---------------------------------------------------

*EVALUATOR.* ``engine.cycle.local_reframe_allowed`` refuses
``Responsibility.EVALUATOR`` because ORION's own evaluator binding
(``MethodState.evaluator_id``) is protected by Self-ORION.
``orion_system._license`` permits it because the P1 suite's EVALUATOR label
denotes the *task's* scoring model, which is part of the task formulation. This
module follows ``orion_system``: ``M.EVALUATOR`` here is the task's evaluator.
ORION's own evaluator binding is reached only through ``Responsibility.METHOD``,
which licenses nothing.

*METHOD.* No row permits ``REWRITE_METHOD``, matching
``OrionPolicy.reachable_coordinates``, which never contains ``M.METHOD``.
Method revision is a governed Self-ORION transition; the only thing a METHOD
diagnosis licenses is escalation.

What this module cannot do, stated plainly
-------------------------------------------

Licensing binds a permission to a *diagnosed class*. It cannot repair a
diagnosis that is wrong. A probe that reports the wrong class, with no standing
evidence to contradict it, yields a confident wrong diagnosis and a licence
grounded on that wrong class. The invariant still holds — the licence names the
class it was granted on, so the error is visible on the receipt — but no
licensing rule can recover a corrupted instrument. That case is pinned in
``test_licensing`` as a diagnosis failure, deliberately not defended against by
lowering a confidence bar, which would be tuning.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from pathlib import Path

from orion.core.residuals import Responsibility
from orion.kernel.store import canonical_bytes

from .baselines import CLAIM_COORDINATE, COORDINATE_BY_RESPONSIBILITY
from .cases import HiddenShiftCase, PublicView, Split, suite_fingerprint
from .contradiction import Finding, detect
from .diagnosability import (
    ALL_RESPONSIBILITIES,
    MUTATION_BEARING_CLASSES,
    AuthorityClass,
    DiagnosabilityReport,
    DiagnosabilityState,
    EvidenceItem,
    Probe,
    ProbeValue,
    assess_diagnosability,
    authority_class_of,
    minimum_decisive_weight,
    rank_probes,
)
from .harness import PROTOCOL_PATH, UNBOUND, protocol_id

#: Additive V2 surface (issue #136): unconsumed by design until separately
#: execution-frozen. Being imported by a V1-frozen module is the defect here,
#: not being unconsumed — `orion.adoption` checks that direction.
ADOPTION_BOUNDARY = "V2_ADDITIVE"

SCHEMA_VERSION = "orion.p1.v2.license-receipt.v1"

# --------------------------------------------------------------------------
# V2 manifest — additive, and bound to the V1 suites by content
# --------------------------------------------------------------------------

V2_STUDY_ID = "P1.V2.responsibility-licensing.v1"

# The two frozen P1 case-family fingerprints, copied from
# `PROTOCOL_V1.json.execution_bindings.dataset_revisions`. `bind_split`
# recomputes them from the cases on disk and refuses on mismatch, so these are
# a binding rather than a claim: if the suite moves, the V2 harness stops.
V2_SUITE_BINDINGS: dict[str, str] = {
    Split.PILOT.value: (
        "7a50a2d5025beb7dea4835911fa7dbf4a191431447397c73939c276b71dc49b5"
    ),
    Split.TEST.value: (
        "21b461d89280631b93b766d6fb000c7f9f5fbeccee7cb6664f238c2c5c8e6420"
    ),
}

# Coordinate namespaces. A rewrite inside `FRAME.`, `W.` or `M.` is a
# formulation or search-universe mutation; `K.` is knowledge revision, which
# Iris already does and which no responsibility class is denied.
MUTATION_NAMESPACES: tuple[str, ...] = ("FRAME.", "W.", "M.")
PROTECTED_COORDINATES: frozenset[str] = frozenset({"M.METHOD"})


# --------------------------------------------------------------------------
# Epistemic actions
# --------------------------------------------------------------------------


class EpistemicAction(str, Enum):
    """Everything a diagnosis could be taken to permit.

    The enum is deliberately wider than any single row of the matrix, so that
    "not licensed" is a statement about a real alternative rather than about an
    action nobody modelled.
    """

    ACQUIRE_EVIDENCE = "ACQUIRE_EVIDENCE"
    REPAIR_EXECUTION = "REPAIR_EXECUTION"
    RUN_PROBE = "RUN_PROBE"
    REVISE_CLAIM = "REVISE_CLAIM"
    ESCALATE_TO_GOVERNANCE = "ESCALATE_TO_GOVERNANCE"
    REWRITE_QUESTION = "REWRITE_QUESTION"
    REWRITE_SEARCH_UNIVERSE = "REWRITE_SEARCH_UNIVERSE"
    REWRITE_REPRESENTATION = "REWRITE_REPRESENTATION"
    REWRITE_DECOMPOSITION = "REWRITE_DECOMPOSITION"
    REWRITE_INTERFACE = "REWRITE_INTERFACE"
    REWRITE_MEASUREMENT = "REWRITE_MEASUREMENT"
    REWRITE_EVALUATOR = "REWRITE_EVALUATOR"
    REWRITE_METHOD = "REWRITE_METHOD"


# Total map. The coordinate is what decides whether an action mutates the
# formulation, so `is_formulation_mutation` is derived from this namespace
# rather than from a hand-maintained list of mutating actions: an action added
# later with a `W.` coordinate is classified correctly without anyone
# remembering to update a second table.
COORDINATE_BY_ACTION: dict[EpistemicAction, str] = {
    EpistemicAction.ACQUIRE_EVIDENCE: "",
    EpistemicAction.REPAIR_EXECUTION: "",
    EpistemicAction.RUN_PROBE: "",
    EpistemicAction.REVISE_CLAIM: CLAIM_COORDINATE,
    EpistemicAction.ESCALATE_TO_GOVERNANCE: "",
    EpistemicAction.REWRITE_QUESTION: "FRAME.QUESTION",
    EpistemicAction.REWRITE_SEARCH_UNIVERSE: "W.ACTIVE_DOMAINS",
    EpistemicAction.REWRITE_REPRESENTATION: "W.REPRESENTATIONS",
    EpistemicAction.REWRITE_DECOMPOSITION: "W.DECOMPOSITION",
    EpistemicAction.REWRITE_INTERFACE: "W.INTERFACE",
    EpistemicAction.REWRITE_MEASUREMENT: "M.MEASUREMENT",
    EpistemicAction.REWRITE_EVALUATOR: "M.EVALUATOR",
    EpistemicAction.REWRITE_METHOD: "M.METHOD",
}


def coordinate_of(action: EpistemicAction) -> str:
    try:
        return COORDINATE_BY_ACTION[action]
    except KeyError as error:  # pragma: no cover - guarded by a totality test
        raise ValueError(f"{action!r} has no coordinate; the table is incomplete") from error


def is_formulation_mutation(action: EpistemicAction) -> bool:
    """Does this action rewrite ``W`` or ``M`` (or the question they serve)?

    Derived from the coordinate namespace, so the property test quantifies over
    something that stays true as the action vocabulary grows.
    """

    coordinate = coordinate_of(action)
    return any(coordinate.startswith(prefix) for prefix in MUTATION_NAMESPACES)


MUTATING_ACTIONS: tuple[EpistemicAction, ...] = tuple(
    action for action in EpistemicAction if is_formulation_mutation(action)
)

# Available whatever the diagnosis says, because none of them changes the
# formulation: probing and claim revision are Iris's epistemic actions, which
# produce discriminative evidence without modifying the retained solution, and
# escalation is a request rather than an act.
UNIVERSAL_ACTIONS: frozenset[EpistemicAction] = frozenset(
    {
        EpistemicAction.RUN_PROBE,
        EpistemicAction.REVISE_CLAIM,
        EpistemicAction.ESCALATE_TO_GOVERNANCE,
    }
)


def _row(*actions: EpistemicAction) -> frozenset[EpistemicAction]:
    return UNIVERSAL_ACTIONS | frozenset(actions)


# --------------------------------------------------------------------------
# The licensing matrix
# --------------------------------------------------------------------------

LICENSING_MATRIX: dict[Responsibility, frozenset[EpistemicAction]] = {
    # --- formulation: one coordinate each --------------------------------
    Responsibility.QUESTION: _row(EpistemicAction.REWRITE_QUESTION),
    Responsibility.REPRESENTATION: _row(EpistemicAction.REWRITE_REPRESENTATION),
    Responsibility.DECOMPOSITION: _row(EpistemicAction.REWRITE_DECOMPOSITION),
    Responsibility.INTERFACE: _row(EpistemicAction.REWRITE_INTERFACE),
    Responsibility.MEASUREMENT: _row(EpistemicAction.REWRITE_MEASUREMENT),
    Responsibility.EVALUATOR: _row(EpistemicAction.REWRITE_EVALUATOR),
    # --- search universe --------------------------------------------------
    Responsibility.SEARCH: _row(EpistemicAction.REWRITE_SEARCH_UNIVERSE),
    Responsibility.ROUTING: _row(EpistemicAction.REWRITE_SEARCH_UNIVERSE),
    # --- routed to acquisition and repair; no rewrite licence -------------
    Responsibility.EVIDENCE: _row(EpistemicAction.ACQUIRE_EVIDENCE),
    Responsibility.EXECUTION: _row(EpistemicAction.REPAIR_EXECUTION),
    # --- protected: escalation only ---------------------------------------
    Responsibility.METHOD: _row(),
}


def matrix_fingerprint(
    matrix: dict[Responsibility, frozenset[EpistemicAction]] | None = None,
) -> str:
    """Content hash of a licensing matrix, so a receipt names the rules it used.

    Sets are sorted before hashing; nothing here iterates a ``frozenset`` into a
    payload, because set order is the one nondeterminism that survives a
    same-process check and breaks across processes.
    """

    table = LICENSING_MATRIX if matrix is None else matrix
    payload = [
        [
            responsibility.value,
            sorted(action.value for action in table[responsibility]),
        ]
        for responsibility in ALL_RESPONSIBILITIES
        if responsibility in table
    ]
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


# --------------------------------------------------------------------------
# Matrix audit — the invariant, executed and recorded rather than only asserted
# --------------------------------------------------------------------------


class AuditVerdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


@dataclass(frozen=True)
class MatrixAudit:
    """The licensing invariant run over a whole matrix, as a receipt."""

    verdict: AuditVerdict
    fingerprint: str
    checked_pairs: int
    violations: tuple[str, ...] = ()

    def to_payload(self) -> dict:
        return {
            "verdict": self.verdict.value,
            "fingerprint": self.fingerprint,
            "checked_pairs": self.checked_pairs,
            "violations": list(self.violations),
        }


def audit_licensing_matrix(
    matrix: dict[Responsibility, frozenset[EpistemicAction]] | None = None,
) -> MatrixAudit:
    """Check every (responsibility, action) pair against the invariant.

    Five conditions, all of them structural:

    1. the matrix is total over ``Responsibility``;
    2. no mutating action appears in a row whose authority class is not
       FORMULATION or SEARCH_UNIVERSE — **the paper's claim**;
    3. no row permits more than one mutating action, so a licence names one
       coordinate;
    4. the mutating action a row permits carries the coordinate
       ``COORDINATE_BY_RESPONSIBILITY`` already assigns to that responsibility;
    5. no row reaches a protected coordinate.
    """

    table = LICENSING_MATRIX if matrix is None else matrix
    violations: list[str] = []
    known = set(ALL_RESPONSIBILITIES)
    missing = [item.value for item in ALL_RESPONSIBILITIES if item not in table]
    violations.extend(f"row_missing:{name}" for name in sorted(missing))
    extra = sorted(str(item) for item in table if item not in known)
    violations.extend(f"row_unknown:{name}" for name in extra)

    checked = 0
    for responsibility in ALL_RESPONSIBILITIES:
        if responsibility not in table:
            continue
        authority = authority_class_of(responsibility)
        mutating: list[EpistemicAction] = []
        for action in EpistemicAction:
            checked += 1
            if action not in table[responsibility]:
                continue
            if coordinate_of(action) in PROTECTED_COORDINATES:
                violations.append(
                    f"protected_coordinate_licensed:{responsibility.value}:{action.value}"
                )
            if not is_formulation_mutation(action):
                continue
            mutating.append(action)
            if authority not in MUTATION_BEARING_CLASSES:
                violations.append(
                    "mutation_licensed_by_non_mutation_class:"
                    f"{responsibility.value}({authority.value}):{action.value}"
                )
        if len(mutating) > 1:
            violations.append(
                f"row_licenses_several_coordinates:{responsibility.value}:"
                + ",".join(action.value for action in sorted(mutating, key=lambda a: a.value))
            )
        expected = COORDINATE_BY_RESPONSIBILITY.get(responsibility, "")
        for action in mutating:
            if coordinate_of(action) != expected:
                violations.append(
                    f"coordinate_disagrees_with_engine_namespace:{responsibility.value}:"
                    f"{coordinate_of(action)}!={expected or '<none>'}"
                )
        if authority in MUTATION_BEARING_CLASSES and not mutating:
            violations.append(f"mutation_class_licenses_no_coordinate:{responsibility.value}")
    return MatrixAudit(
        verdict=AuditVerdict.FAIL if violations else AuditVerdict.PASS,
        fingerprint=matrix_fingerprint(table),
        checked_pairs=checked,
        violations=tuple(violations),
    )


# --------------------------------------------------------------------------
# Licences
# --------------------------------------------------------------------------


class RefusalReason(str, Enum):
    """Why no licence was issued. Every refusal is typed; none is a score."""

    EVIDENCE_INADMISSIBLE = "EVIDENCE_INADMISSIBLE"
    NO_EVIDENCE = "NO_EVIDENCE"
    CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"
    NOT_DIAGNOSABLE = "NOT_DIAGNOSABLE"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    EVIDENCE_FINGERPRINT_MISMATCH = "EVIDENCE_FINGERPRINT_MISMATCH"
    MATRIX_INCOMPLETE = "MATRIX_INCOMPLETE"
    PROTECTED_COORDINATE = "PROTECTED_COORDINATE"
    ACTION_NOT_LICENSED_FOR_CLASS = "ACTION_NOT_LICENSED_FOR_CLASS"
    LICENSING_INVARIANT_BREACH = "LICENSING_INVARIANT_BREACH"


_REFUSAL_BY_STATE: dict[DiagnosabilityState, RefusalReason] = {
    DiagnosabilityState.INADMISSIBLE: RefusalReason.EVIDENCE_INADMISSIBLE,
    DiagnosabilityState.NO_EVIDENCE: RefusalReason.NO_EVIDENCE,
    DiagnosabilityState.CONFLICTING: RefusalReason.CONFLICTING_EVIDENCE,
    DiagnosabilityState.INDISTINGUISHABLE: RefusalReason.NOT_DIAGNOSABLE,
    DiagnosabilityState.LOW_CONFIDENCE: RefusalReason.LOW_CONFIDENCE,
}

# What a caller may do when no licence exists. These are *not* a licence: they
# are the actions that make the question answerable, and none of them touches
# the formulation. The property test asserts that.
FAIL_CLOSED_REMEDY: tuple[EpistemicAction, ...] = (
    EpistemicAction.RUN_PROBE,
    EpistemicAction.ACQUIRE_EVIDENCE,
    EpistemicAction.ESCALATE_TO_GOVERNANCE,
)


@dataclass(frozen=True)
class LicenseDecision:
    """One request, answered. Granted or refused, always with its ground.

    ``ground_class`` is read off the diagnosis, not off the request, so a
    receipt records what the licence was actually granted on. That is what
    makes an audit of the invariant possible after the fact — and what makes a
    wrong diagnosis visible instead of silent.
    """

    action: EpistemicAction
    granted: bool
    ground_class: Responsibility | None
    ground_authority: AuthorityClass | None
    coordinate: str
    refusal: RefusalReason | None = None
    detail: str = ""
    remedy: tuple[EpistemicAction, ...] = ()
    evidence_fingerprint: str = ""
    matrix_fingerprint: str = ""

    @property
    def mutates_formulation(self) -> bool:
        return is_formulation_mutation(self.action)

    def to_payload(self) -> dict:
        return {
            "action": self.action.value,
            "granted": self.granted,
            "ground_class": self.ground_class.value if self.ground_class else "",
            "ground_authority": (
                self.ground_authority.value if self.ground_authority else ""
            ),
            "coordinate": self.coordinate,
            "mutates_formulation": self.mutates_formulation,
            "refusal": self.refusal.value if self.refusal else "",
            "detail": self.detail,
            "remedy": [item.value for item in self.remedy],
            "evidence_fingerprint": self.evidence_fingerprint,
            "matrix_fingerprint": self.matrix_fingerprint,
        }


def issue_license(
    report: DiagnosabilityReport,
    action: EpistemicAction,
    *,
    matrix: dict[Responsibility, frozenset[EpistemicAction]] | None = None,
    expected_evidence_fingerprint: str | None = None,
) -> LicenseDecision:
    """Grant or refuse one epistemic action, failing closed at every step.

    The order is the point, and it mirrors ``evaluate_hard_gates``:
    admissibility of the *question* is settled before the table is consulted,
    and the invariant is re-derived after the table has answered. A matrix that
    has been edited into permitting a mutation from an evidence diagnosis does
    not get its way; it trips ``LICENSING_INVARIANT_BREACH``.
    """

    table = LICENSING_MATRIX if matrix is None else matrix
    fingerprint = matrix_fingerprint(table)
    coordinate = coordinate_of(action)

    def refuse(
        reason: RefusalReason,
        detail: str,
        *,
        ground: Responsibility | None = None,
    ) -> LicenseDecision:
        return LicenseDecision(
            action=action,
            granted=False,
            ground_class=ground,
            ground_authority=authority_class_of(ground) if ground else None,
            coordinate=coordinate,
            refusal=reason,
            detail=detail,
            remedy=FAIL_CLOSED_REMEDY,
            evidence_fingerprint=report.evidence_fingerprint,
            matrix_fingerprint=fingerprint,
        )

    if report.state is not DiagnosabilityState.DIAGNOSABLE or report.diagnosed is None:
        return refuse(
            _REFUSAL_BY_STATE.get(report.state, RefusalReason.NOT_DIAGNOSABLE),
            "; ".join(report.reasons) or report.state.value,
        )

    if (
        expected_evidence_fingerprint is not None
        and expected_evidence_fingerprint != report.evidence_fingerprint
    ):
        return refuse(
            RefusalReason.EVIDENCE_FINGERPRINT_MISMATCH,
            f"diagnosis was made over {report.evidence_fingerprint[:12]}, not "
            f"{expected_evidence_fingerprint[:12]}",
            ground=report.diagnosed,
        )

    ground = report.diagnosed
    authority = authority_class_of(ground)

    if coordinate in PROTECTED_COORDINATES:
        return refuse(
            RefusalReason.PROTECTED_COORDINATE,
            f"{coordinate} is a governed Self-ORION transition, not a P1 operation",
            ground=ground,
        )

    permitted = table.get(ground)
    if permitted is None:
        return refuse(
            RefusalReason.MATRIX_INCOMPLETE,
            f"the matrix has no row for {ground.value}",
            ground=ground,
        )

    if action not in permitted:
        return refuse(
            RefusalReason.ACTION_NOT_LICENSED_FOR_CLASS,
            f"{ground.value} ({authority.value}) does not license {action.value}",
            ground=ground,
        )

    # Re-derived, not read back from the table that just said yes.
    if is_formulation_mutation(action) and authority not in MUTATION_BEARING_CLASSES:
        return refuse(
            RefusalReason.LICENSING_INVARIANT_BREACH,
            f"the matrix licenses {action.value} ({coordinate}) from "
            f"{ground.value} ({authority.value}), which cannot mutate W or M",
            ground=ground,
        )

    return LicenseDecision(
        action=action,
        granted=True,
        ground_class=ground,
        ground_authority=authority,
        coordinate=coordinate,
        detail=f"licensed by {ground.value} ({authority.value})",
        evidence_fingerprint=report.evidence_fingerprint,
        matrix_fingerprint=fingerprint,
    )


def invariant_violations(decisions: Sequence[LicenseDecision]) -> tuple[str, ...]:
    """Audit issued decisions after the fact — the paper's claim, over data.

    Reads the ground class **off the decision**, never off whatever produced it,
    so the audit is not a restatement of the code that made the decision.
    """

    violations: list[str] = []
    for decision in decisions:
        if not decision.granted:
            continue
        if not decision.mutates_formulation:
            continue
        if decision.ground_authority not in MUTATION_BEARING_CLASSES:
            violations.append(
                "granted_mutation_from_non_mutation_class:"
                f"{decision.action.value}:"
                f"{decision.ground_class.value if decision.ground_class else '<none>'}"
            )
        if decision.coordinate in PROTECTED_COORDINATES:
            violations.append(f"granted_protected_coordinate:{decision.action.value}")
    return tuple(violations)


# --------------------------------------------------------------------------
# The V2 probe menu
# --------------------------------------------------------------------------
#
# `reliability` here is an instrument *specification*, not a fitted parameter.
# No calibration data exists for these probes on this suite, and inventing a
# number would be worse than an explicit idealisation, so the menu declares
# perfect reliability and the resulting expected information gain measures
# reach alone. A deployment with measured instruments supplies its own.

V2_PROBE_MENU: tuple[Probe, ...] = (
    Probe(
        probe_id="blind_control",
        discriminates=(),
        description="reaches nothing; the blind-probe negative control",
    ),
    Probe(
        probe_id="record_completeness",
        discriminates=(Responsibility.EVIDENCE,),
        description="is the required record obtainable, or absent",
    ),
    Probe(
        probe_id="rerun_under_fixed_configuration",
        discriminates=(Responsibility.EXECUTION,),
        description="does the phenomenon survive a corrected run",
    ),
    Probe(
        probe_id="population_frame",
        discriminates=(Responsibility.SEARCH, Responsibility.ROUTING),
        description="does the sampling frame contain what the question is about",
    ),
    Probe(
        probe_id="coordinate_change",
        discriminates=(Responsibility.QUESTION, Responsibility.REPRESENTATION),
        description="does re-expressing the values remove the residual",
    ),
    Probe(
        probe_id="boundary_trace",
        discriminates=(Responsibility.DECOMPOSITION, Responsibility.INTERFACE),
        description="does the residual sit at a seam or inside a component",
    ),
    Probe(
        probe_id="unit_and_weighting_recount",
        discriminates=(Responsibility.MEASUREMENT, Responsibility.EVALUATOR),
        description="does the quantity count the unit the question asks about",
    ),
)


# --------------------------------------------------------------------------
# Receipts
# --------------------------------------------------------------------------


@lru_cache(maxsize=4)
def protocol_version(path: Path = PROTOCOL_PATH) -> str:
    """Read the frozen protocol's version. Read-only, always.

    Cached because a receipt names it and a study writes thousands of receipts;
    the protocol is frozen, so re-reading it per record buys nothing.
    """

    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return UNBOUND
    return str(payload.get("protocol_version", UNBOUND))


@lru_cache(maxsize=1)
def _protocol_id() -> str:
    return protocol_id()


@dataclass(frozen=True)
class LicenseReceipt:
    """One case, fully accounted for, in a form an external evaluator can read.

    Everything needed to re-derive the decision is on the record: the evidence
    with its citations, the posterior, the diagnosability state, the probe
    ranking, every decision with the class it was grounded on, and the digests
    binding the whole thing to a matrix and an evidence set.
    """

    case_id: str
    split: str
    suite_fingerprint: str
    evidence: tuple[EvidenceItem, ...]
    report: DiagnosabilityReport
    probe_values: tuple[ProbeValue, ...]
    decisions: tuple[LicenseDecision, ...]
    notes: tuple[str, ...] = ()

    @property
    def granted_actions(self) -> tuple[EpistemicAction, ...]:
        return tuple(item.action for item in self.decisions if item.granted)

    @property
    def violations(self) -> tuple[str, ...]:
        return invariant_violations(self.decisions)

    def to_payload(self) -> dict:
        return {
            "schema_version": SCHEMA_VERSION,
            "study_id": V2_STUDY_ID,
            "protocol_id": _protocol_id(),
            "protocol_version": protocol_version(),
            "case_id": self.case_id,
            "split": self.split,
            "suite_fingerprint": self.suite_fingerprint,
            "matrix_fingerprint": matrix_fingerprint(),
            "evidence": [item.to_payload() for item in self.evidence],
            "diagnosability": self.report.to_payload(),
            "probe_values": [item.to_payload() for item in self.probe_values],
            "decisions": [item.to_payload() for item in self.decisions],
            "granted_actions": [item.value for item in self.granted_actions],
            "invariant_violations": list(self.violations),
            "notes": list(self.notes),
        }

    def to_json(self) -> str:
        return canonical_bytes(self.to_payload()).decode("utf-8")


@dataclass(frozen=True)
class V2Archive:
    """Every receipt from one V2 run, plus the audit of the rules it used."""

    receipts: tuple[LicenseReceipt, ...]
    split: str
    suite_fingerprint: str
    matrix_audit: MatrixAudit

    @property
    def violations(self) -> tuple[str, ...]:
        return tuple(
            f"{receipt.case_id}:{item}"
            for receipt in self.receipts
            for item in receipt.violations
        )

    def state_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {state.value: 0 for state in DiagnosabilityState}
        for receipt in self.receipts:
            counts[receipt.report.state.value] += 1
        return counts

    def to_payload(self) -> dict:
        return {
            "schema_version": SCHEMA_VERSION,
            "study_id": V2_STUDY_ID,
            "protocol_id": _protocol_id(),
            "protocol_version": protocol_version(),
            "p1_v1_status": "UNCHANGED: this run reads V1 artifacts and writes none",
            "split": self.split,
            "suite_fingerprint": self.suite_fingerprint,
            "matrix_audit": self.matrix_audit.to_payload(),
            "state_counts": self.state_counts(),
            "invariant_violations": list(self.violations),
            "receipts": [receipt.to_payload() for receipt in self.receipts],
        }

    def to_jsonl(self) -> str:
        return "".join(f"{receipt.to_json()}\n" for receipt in self.receipts)


# --------------------------------------------------------------------------
# The V2 harness
# --------------------------------------------------------------------------


def bind_split(cases: Sequence[HiddenShiftCase], *, split: Split) -> str:
    """Recompute the suite fingerprint and refuse if it is not the frozen one.

    This is the only function in the module that touches a ``HiddenShiftCase``.
    It returns a digest and nothing else; everything downstream receives
    ``PublicView`` only, so ``protected_gold`` never reaches the mechanism. That
    is the same access boundary ``harness.run_one`` enforces, restated here
    because this is the other place it could be broken.
    """

    computed = suite_fingerprint(tuple(cases))
    declared = V2_SUITE_BINDINGS[split.value]
    if computed != declared:
        raise ValueError(
            f"{split.value} suite fingerprint {computed} does not match the frozen "
            f"P1 binding {declared}; the V2 harness is bound to the V1 case families "
            "and refuses to run against a suite that moved"
        )
    return computed


def evidence_from_findings(findings: Sequence[Finding]) -> tuple[EvidenceItem, ...]:
    """Turn detector findings into evidence, with no re-tuning of the detector.

    Every finding becomes one evidence item whose supported classes are the
    finding's own and whose weight is the finding's own strength, clamped to
    ``[0, 1]`` because ``contradiction.arbitrate`` subtracts from a strength and
    can land on zero. A finding naming no responsibility is skipped rather than
    coerced into one; the caller reports how many were skipped.
    """

    items: list[EvidenceItem] = []
    for index, finding in enumerate(findings):
        if not finding.responsibilities:
            continue
        items.append(
            EvidenceItem(
                evidence_id=f"{index:03d}:{finding.rule}",
                supports=finding.responsibilities,
                weight=min(max(finding.strength, 0.0), 1.0),
                source="contradiction.detect",
                citation=" | ".join(finding.citations),
            )
        )
    return tuple(items)


def evidence_from_view(view: PublicView) -> tuple[EvidenceItem, ...]:
    """Reduce a public view to evidence with the existing P1 detector."""

    return evidence_from_findings(detect(view))


def run_v2_view(
    view: PublicView,
    *,
    split: str,
    suite_fingerprint_value: str,
    probes: Sequence[Probe] = V2_PROBE_MENU,
    extra_evidence: Sequence[EvidenceItem] = (),
) -> LicenseReceipt:
    """Diagnose one public view and answer every possible request against it.

    Every member of ``EpistemicAction`` is requested, not just the plausible
    ones. A licensing claim that only ever answers the requests the mechanism
    expects is untested against the request that matters.

    The type check is not ceremony. ``HiddenShiftCase`` carries ``case_id``,
    ``public_prompt``, ``observable_resources`` and ``budget_class`` too, so a
    case object handed here would run happily and would put ``protected_gold``
    one attribute access away from the mechanism. The access boundary the study
    depends on is enforced, not documented.
    """

    if not isinstance(view, PublicView):
        raise TypeError(
            "the licensing mechanism reads PublicView only; a HiddenShiftCase "
            "carries protected gold and must not cross this boundary"
        )
    detected = detect(view)
    evidence = (*evidence_from_findings(detected), *extra_evidence)
    report = assess_diagnosability(evidence)
    values = rank_probes(report.posterior, probes) if report.posterior else ()
    decisions = tuple(
        issue_license(
            report,
            action,
            expected_evidence_fingerprint=report.evidence_fingerprint,
        )
        for action in EpistemicAction
    )
    unattributed = sum(1 for finding in detected if not finding.responsibilities)
    notes = (f"findings={len(detected)}", f"findings_without_responsibility={unattributed}")
    return LicenseReceipt(
        case_id=view.case_id,
        split=split,
        suite_fingerprint=suite_fingerprint_value,
        evidence=evidence,
        report=report,
        probe_values=values,
        decisions=decisions,
        notes=notes,
    )


def run_v2(
    views: Sequence[PublicView],
    *,
    split: str,
    suite_fingerprint_value: str,
    probes: Sequence[Probe] = V2_PROBE_MENU,
) -> V2Archive:
    """Run the licensing mechanism over public views only."""

    receipts = tuple(
        run_v2_view(
            view,
            split=split,
            suite_fingerprint_value=suite_fingerprint_value,
            probes=probes,
        )
        for view in views
    )
    return V2Archive(
        receipts=receipts,
        split=split,
        suite_fingerprint=suite_fingerprint_value,
        matrix_audit=audit_licensing_matrix(),
    )


def run_v2_split(
    cases: Sequence[HiddenShiftCase],
    *,
    split: Split,
    probes: Sequence[Probe] = V2_PROBE_MENU,
) -> V2Archive:
    """Bind the suite by content, then run over public views only."""

    fingerprint = bind_split(cases, split=split)
    views = tuple(case.public_view for case in cases)
    return run_v2(
        views,
        split=split.value,
        suite_fingerprint_value=fingerprint,
        probes=probes,
    )


# --------------------------------------------------------------------------
# Negative controls
# --------------------------------------------------------------------------
#
# Constructed rather than drawn from the frozen suite, deliberately. A control
# has to be *by construction* an evidence-only or a formulation case; selecting
# real cases by their gold label would make the control a measurement of the
# detector instead of a test of the mechanism, and would put gold on the wrong
# side of the access boundary. The real suite is exercised separately, by
# running the invariant over every case and asserting only the invariant.

_SPACE_SIZE = len(ALL_RESPONSIBILITIES)

# Strictly inside the decisive band, and derived from it: the midpoint between
# the weight at which one observation alone diagnoses a class and certainty.
# Nothing here was chosen by looking at an outcome.
DECISIVE_WEIGHT: float = (minimum_decisive_weight(_SPACE_SIZE) + 1.0) / 2.0
SUB_DECISIVE_WEIGHT: float = minimum_decisive_weight(_SPACE_SIZE) / 2.0


@dataclass(frozen=True)
class ControlExpectation:
    action: EpistemicAction
    granted: bool
    refusal: RefusalReason | None = None

    def to_payload(self) -> dict:
        return {
            "action": self.action.value,
            "granted": self.granted,
            "refusal": self.refusal.value if self.refusal else "",
        }


@dataclass(frozen=True)
class ControlScenario:
    """A constructed case with a declared expected outcome."""

    control_id: str
    rationale: str
    evidence: tuple[EvidenceItem, ...]
    expected_state: DiagnosabilityState
    expectations: tuple[ControlExpectation, ...]
    probes: tuple[Probe, ...] = ()

    def to_payload(self) -> dict:
        return {
            "control_id": self.control_id,
            "rationale": self.rationale,
            "evidence": [item.to_payload() for item in self.evidence],
            "expected_state": self.expected_state.value,
            "expectations": [item.to_payload() for item in self.expectations],
            "probes": [item.to_payload() for item in self.probes],
        }


@dataclass(frozen=True)
class ControlReceipt:
    """What the mechanism actually did on a control, and whether it matched."""

    control_id: str
    satisfied: bool
    observed_state: DiagnosabilityState
    expected_state: DiagnosabilityState
    mismatches: tuple[str, ...]
    report: DiagnosabilityReport
    decisions: tuple[LicenseDecision, ...]
    probe_values: tuple[ProbeValue, ...]

    def to_payload(self) -> dict:
        return {
            "schema_version": SCHEMA_VERSION,
            "study_id": V2_STUDY_ID,
            "control_id": self.control_id,
            "satisfied": self.satisfied,
            "observed_state": self.observed_state.value,
            "expected_state": self.expected_state.value,
            "mismatches": list(self.mismatches),
            "matrix_fingerprint": matrix_fingerprint(),
            "diagnosability": self.report.to_payload(),
            "decisions": [item.to_payload() for item in self.decisions],
            "probe_values": [item.to_payload() for item in self.probe_values],
            "invariant_violations": list(invariant_violations(self.decisions)),
        }


def _item(
    evidence_id: str,
    responsibility: Responsibility,
    weight: float,
    source: str = "constructed",
) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=evidence_id,
        supports=(responsibility,),
        weight=weight,
        source=source,
        citation=f"constructed control observation for {responsibility.value}",
    )


_BLIND_PROBE = Probe(
    probe_id="blind_control",
    discriminates=(),
    description="reaches nothing",
)

_MISLEADING_PROBE = Probe(
    probe_id="coordinate_change",
    discriminates=(Responsibility.QUESTION, Responsibility.REPRESENTATION),
    description="a well-formed probe returning the wrong class",
)


def _all_mutations_refused(
    reason: RefusalReason, *, protected_reason: RefusalReason | None = None
) -> tuple[ControlExpectation, ...]:
    """Declare that *every* mutating action is refused, and with which reason.

    ``protected_reason`` exists because the refusal ladder is ordered: when a
    class *was* diagnosed, ``M.METHOD`` is refused as a protected coordinate
    before the matrix is consulted, whereas when nothing was diagnosed the
    fail-closed reason preempts everything. Declaring the ladder rather than
    accepting whichever reason comes back is what makes the control able to
    fail.
    """

    return tuple(
        ControlExpectation(
            action=action,
            granted=False,
            refusal=(
                protected_reason
                if protected_reason is not None
                and coordinate_of(action) in PROTECTED_COORDINATES
                else reason
            ),
        )
        for action in MUTATING_ACTIONS
    )


NEGATIVE_CONTROLS: tuple[ControlScenario, ...] = (
    ControlScenario(
        control_id="blind_probe",
        rationale=(
            "A probe that reaches nothing must be worth exactly zero bits and must "
            "not shift any licence. The standing diagnosis is EVIDENCE, so no "
            "mutation is licensed with or without it."
        ),
        evidence=(_item("standing_record_gap", Responsibility.EVIDENCE, DECISIVE_WEIGHT),),
        expected_state=DiagnosabilityState.DIAGNOSABLE,
        expectations=(
            *_all_mutations_refused(
                RefusalReason.ACTION_NOT_LICENSED_FOR_CLASS,
                protected_reason=RefusalReason.PROTECTED_COORDINATE,
            ),
            ControlExpectation(EpistemicAction.ACQUIRE_EVIDENCE, True),
        ),
        probes=(_BLIND_PROBE,),
    ),
    ControlScenario(
        control_id="misleading_probe",
        rationale=(
            "The control that matters. A well-formed probe reports REPRESENTATION "
            "on a case whose standing observation is decisive for EVIDENCE. Two "
            "decisive observations pointing at different authority classes is a "
            "conflict, and a conflict issues no licence at all — least of all a "
            "mutation licence bought from the probe."
        ),
        evidence=(
            _item("standing_record_gap", Responsibility.EVIDENCE, DECISIVE_WEIGHT),
            EvidenceItem(
                evidence_id="probe:coordinate_change",
                supports=(Responsibility.REPRESENTATION,),
                weight=_MISLEADING_PROBE.reliability,
                source="probe:coordinate_change",
                citation="probe reported REPRESENTATION",
            ),
        ),
        expected_state=DiagnosabilityState.CONFLICTING,
        expectations=(
            *_all_mutations_refused(RefusalReason.CONFLICTING_EVIDENCE),
            ControlExpectation(
                EpistemicAction.ACQUIRE_EVIDENCE,
                False,
                RefusalReason.CONFLICTING_EVIDENCE,
            ),
            ControlExpectation(
                EpistemicAction.RUN_PROBE, False, RefusalReason.CONFLICTING_EVIDENCE
            ),
        ),
        probes=(_MISLEADING_PROBE,),
    ),
    ControlScenario(
        control_id="evidence_only_case",
        rationale=(
            "Evidence responsibility routes to acquisition. No coordinate of W or "
            "M may be rewritten on it, however strong the observation."
        ),
        evidence=(_item("record_absent_but_obtainable", Responsibility.EVIDENCE, 1.0),),
        expected_state=DiagnosabilityState.DIAGNOSABLE,
        expectations=(
            *_all_mutations_refused(
                RefusalReason.ACTION_NOT_LICENSED_FOR_CLASS,
                protected_reason=RefusalReason.PROTECTED_COORDINATE,
            ),
            ControlExpectation(EpistemicAction.ACQUIRE_EVIDENCE, True),
            ControlExpectation(
                EpistemicAction.REPAIR_EXECUTION,
                False,
                RefusalReason.ACTION_NOT_LICENSED_FOR_CLASS,
            ),
        ),
    ),
    ControlScenario(
        control_id="execution_only_case",
        rationale=(
            "Execution responsibility routes to repair in place. The run is "
            "broken; the formulation is not."
        ),
        evidence=(_item("stale_configuration_element", Responsibility.EXECUTION, 1.0),),
        expected_state=DiagnosabilityState.DIAGNOSABLE,
        expectations=(
            *_all_mutations_refused(
                RefusalReason.ACTION_NOT_LICENSED_FOR_CLASS,
                protected_reason=RefusalReason.PROTECTED_COORDINATE,
            ),
            ControlExpectation(EpistemicAction.REPAIR_EXECUTION, True),
            ControlExpectation(
                EpistemicAction.ACQUIRE_EVIDENCE,
                False,
                RefusalReason.ACTION_NOT_LICENSED_FOR_CLASS,
            ),
        ),
    ),
    ControlScenario(
        control_id="formulation_case",
        rationale=(
            "A measurement responsibility licenses the measurement coordinate and "
            "only that one. Coordinate-specificity is half the claim: a licence "
            "that granted any formulation rewrite would be a permission to "
            "reformulate at will."
        ),
        evidence=(_item("quantity_counts_wrong_unit", Responsibility.MEASUREMENT, 1.0),),
        expected_state=DiagnosabilityState.DIAGNOSABLE,
        expectations=(
            ControlExpectation(EpistemicAction.REWRITE_MEASUREMENT, True),
            ControlExpectation(
                EpistemicAction.REWRITE_REPRESENTATION,
                False,
                RefusalReason.ACTION_NOT_LICENSED_FOR_CLASS,
            ),
            ControlExpectation(
                EpistemicAction.REWRITE_SEARCH_UNIVERSE,
                False,
                RefusalReason.ACTION_NOT_LICENSED_FOR_CLASS,
            ),
            ControlExpectation(
                EpistemicAction.REWRITE_METHOD,
                False,
                RefusalReason.PROTECTED_COORDINATE,
            ),
        ),
    ),
    ControlScenario(
        control_id="search_universe_case",
        rationale=(
            "A search responsibility licenses the active-domain set — the one "
            "coordinate that changes what the search is over."
        ),
        evidence=(_item("population_frame_excludes_subject", Responsibility.SEARCH, 1.0),),
        expected_state=DiagnosabilityState.DIAGNOSABLE,
        expectations=(
            ControlExpectation(EpistemicAction.REWRITE_SEARCH_UNIVERSE, True),
            ControlExpectation(
                EpistemicAction.REWRITE_MEASUREMENT,
                False,
                RefusalReason.ACTION_NOT_LICENSED_FOR_CLASS,
            ),
            ControlExpectation(
                EpistemicAction.REWRITE_METHOD,
                False,
                RefusalReason.PROTECTED_COORDINATE,
            ),
        ),
    ),
)


def run_control(scenario: ControlScenario) -> ControlReceipt:
    """Execute one control and record every mismatch against its declaration."""

    report = assess_diagnosability(scenario.evidence)
    decisions = tuple(
        issue_license(
            report, action, expected_evidence_fingerprint=report.evidence_fingerprint
        )
        for action in EpistemicAction
    )
    by_action = {decision.action: decision for decision in decisions}
    mismatches: list[str] = []
    if report.state is not scenario.expected_state:
        mismatches.append(
            f"state:{report.state.value}!={scenario.expected_state.value}"
        )
    for expectation in scenario.expectations:
        decision = by_action[expectation.action]
        if decision.granted != expectation.granted:
            mismatches.append(
                f"granted:{expectation.action.value}:"
                f"{decision.granted}!={expectation.granted}"
            )
        if expectation.refusal is not None and decision.refusal is not expectation.refusal:
            observed = decision.refusal.value if decision.refusal else "<granted>"
            mismatches.append(
                f"refusal:{expectation.action.value}:"
                f"{observed}!={expectation.refusal.value}"
            )
    mismatches.extend(invariant_violations(decisions))
    values = rank_probes(report.posterior, scenario.probes) if report.posterior else ()
    return ControlReceipt(
        control_id=scenario.control_id,
        satisfied=not mismatches,
        observed_state=report.state,
        expected_state=scenario.expected_state,
        mismatches=tuple(mismatches),
        report=report,
        decisions=decisions,
        probe_values=values,
    )


def run_controls(
    scenarios: Iterable[ControlScenario] = NEGATIVE_CONTROLS,
) -> tuple[ControlReceipt, ...]:
    return tuple(run_control(scenario) for scenario in scenarios)


def control_archive_payload(
    receipts: Sequence[ControlReceipt] | None = None,
) -> dict:
    """Machine-readable control block, suitable for external evaluation."""

    records = tuple(receipts) if receipts is not None else run_controls()
    return {
        "schema_version": SCHEMA_VERSION,
        "study_id": V2_STUDY_ID,
        "protocol_id": _protocol_id(),
        "protocol_version": protocol_version(),
        "p1_v1_status": "UNCHANGED: controls are constructed, not drawn from the suite",
        "matrix_audit": audit_licensing_matrix().to_payload(),
        "controls": [receipt.to_payload() for receipt in records],
        "all_satisfied": all(receipt.satisfied for receipt in records),
    }


__all__ = [
    "COORDINATE_BY_ACTION",
    "DECISIVE_WEIGHT",
    "FAIL_CLOSED_REMEDY",
    "LICENSING_MATRIX",
    "MUTATING_ACTIONS",
    "MUTATION_NAMESPACES",
    "NEGATIVE_CONTROLS",
    "PROTECTED_COORDINATES",
    "SCHEMA_VERSION",
    "SUB_DECISIVE_WEIGHT",
    "UNIVERSAL_ACTIONS",
    "V2_PROBE_MENU",
    "V2_STUDY_ID",
    "V2_SUITE_BINDINGS",
    "AuditVerdict",
    "ControlExpectation",
    "ControlReceipt",
    "ControlScenario",
    "EpistemicAction",
    "LicenseDecision",
    "LicenseReceipt",
    "MatrixAudit",
    "RefusalReason",
    "V2Archive",
    "audit_licensing_matrix",
    "bind_split",
    "control_archive_payload",
    "coordinate_of",
    "evidence_from_findings",
    "evidence_from_view",
    "invariant_violations",
    "is_formulation_mutation",
    "issue_license",
    "matrix_fingerprint",
    "protocol_version",
    "run_control",
    "run_controls",
    "run_v2",
    "run_v2_split",
    "run_v2_view",
]
