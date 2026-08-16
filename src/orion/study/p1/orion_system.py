"""Full ORION and the five frozen ablations as systems under test.

ORION is not re-implemented here. The decision path drives the runtime's own
machinery and inherits its rules rather than restating them:

* ``orion.core.state.OrionState`` / ``KnowledgeState`` / ``SearchUniverseState``
  carry K, W and M explicitly, and ``ClosureCertificate`` carries the
  dependency basis a reopen consults.
* ``orion.engine.operators.diagnose.DiagnoseOperator`` produces the typed
  ``Diagnosis``; ``orion.engine.cycle.revision_allowed`` and
  ``local_reframe_allowed`` decide whether it licenses a formulation change.
* ``orion.engine.operators.reframe.ReframeOperator`` performs the reframe and
  is what refuses a method-level rewrite — the ``PermissionError`` recorded as
  an authority violation is raised by the engine, not simulated here.
* ``orion.engine.operators.reopen.ReopenOperator`` performs dependency-directed
  reopening against the real certificates.
* ``orion.mechanics.audit.audit_mechanic`` audits the exact mechanic cells the
  run exercised (``DIAGNOSE.DISCRIMINATOR.v0``, ``REFRAME.v1``, ...), and
  ``orion.mechanics.diagnosis.DiagnosisState`` is the self-audit's verdict type.
* Every transition is a real ``orion.engine.cycle.Transition`` whose
  ``validate()`` is called; a raised violation is recorded, never swallowed.

**Two boundaries are recorded rather than smoothed over.**

1. *The engine can execute two of the six gold axes.* ``ReframeOperator`` emits
   ``W.ACTIVE_DOMAINS`` and ``W.REPRESENTATIONS``. The suite's gold also uses
   ``W.DECOMPOSITION``, ``W.INTERFACE``, ``M.MEASUREMENT`` and ``M.EVALUATOR``,
   for which no operator exists yet. On those axes the system records the
   decision and an ``engine_gap:<axis>`` note; it does not pretend a state
   transition happened. This is a real gap in the subject and belongs in the
   limitations, not in a silent shim.
2. *Two evaluators are not one evaluator.* ``local_reframe_allowed`` refuses
   ``Responsibility.EVALUATOR`` because ORION's *own* evaluator binding
   (``MethodState.evaluator_id``) is protected by Self-ORION. The suite's
   ``EVALUATOR`` label denotes the *task's* scoring model, which is part of the
   task formulation. Conflating them would either forbid a licensed reframe or
   launder a protected one, so the distinction is explicit in ``_license`` and
   ``Responsibility.METHOD`` remains protected without exception.

Ablations are resource-matched by construction: every member of the ORION
family runs the same number of resource probes and the same number of rounds,
computed from the shared perception layer *before* any policy branching. An
ablation that lost while spending less would be a confound, not a result.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache

from orion.core.closure import ClosureCertificate
from orion.core.method import MethodState
from orion.core.problem import Problem
from orion.core.residuals import Residual, Responsibility
from orion.core.search_universe import SearchUniverseState
from orion.core.state import KnowledgeState, OrionState
from orion.engine.cycle import (
    Transition,
    local_reframe_allowed,
    revision_allowed,
)
from orion.engine.operators.diagnose import DiagnoseOperator
from orion.engine.operators.reframe import ReframeOperator
from orion.engine.operators.reopen import ReopenOperator
from orion.mechanics.audit import MechanicAuditVerdict, audit_mechanic
from orion.mechanics.diagnosis import DiagnosisState
from orion.mechanics.program import current_program_cells
from orion.providers.reasoner.base import Diagnosis, ReframeProposal
from orion.registry import CORE_OPERATOR_IDS, FRAMEWORK_VERSION

from .baselines import (
    COORDINATE_BY_RESPONSIBILITY,
    Cue,
    ProbeLedger,
    PublicClosure,
    abstains,
    apply_repairs,
    axis_answer,
    budget_for,
    cue_to_residual,
    descendants_of,
    deterministic_rng,
    extract_cues,
    material_cues,
    planned_rounds,
    public_closures,
    readable_resources,
    solved,
    stale_closures_survive,
)
from .cases import PublicView
from .systems import SystemTrace

# Axes `orion.engine.operators.reframe` can actually execute today.
ENGINE_EXECUTABLE_AXES = frozenset({"W.ACTIVE_DOMAINS", "W.REPRESENTATIONS"})

W_AXES = frozenset(
    {"W.ACTIVE_DOMAINS", "W.REPRESENTATIONS", "W.DECOMPOSITION", "W.INTERFACE"}
)
M_AXES = frozenset({"M.MEASUREMENT", "M.EVALUATOR"})
FRAME_AXES = frozenset({"FRAME.QUESTION"})

# Mechanic cells the decision path exercises, audited by the self-audit step.
AUDITED_MECHANIC_IDS: tuple[str, ...] = (
    "DIAGNOSE.HYPOTHESES.v0",
    "DIAGNOSE.DISCRIMINATOR.v0",
    "DIAGNOSE.ATTRIBUTION.v0",
    "REFRAME.v1",
    "REOPEN.DEPENDENCY.v0",
)


class ReopenMode(str, Enum):
    DEPENDENCY_DIRECTED = "DEPENDENCY_DIRECTED"
    FULL_RESET = "FULL_RESET"
    NONE = "NONE"


@dataclass(frozen=True)
class OrionPolicy:
    """What full ORION does, and what each ablation removes from it."""

    explicit_w: bool = True
    explicit_m: bool = True
    typed_reframe: bool = True
    reopen_mode: ReopenMode = ReopenMode.DEPENDENCY_DIRECTED
    mechanic_self_audit: bool = True

    @property
    def reachable_coordinates(self) -> frozenset[str]:
        coordinates = set(FRAME_AXES)
        if self.explicit_w:
            coordinates |= W_AXES
        if self.explicit_m:
            coordinates |= M_AXES
        # M.METHOD is never reachable: method revision is a governed
        # Self-ORION transition, not a Paper-I operation.
        return frozenset(coordinates)


@lru_cache(maxsize=1)
def _audited_cells() -> tuple[tuple[str, MechanicAuditVerdict, int], ...]:
    """Audit the exercised mechanics once per process.

    The mechanic decomposition is static, so this is cached; the audit itself
    is the real `audit_mechanic`, not a stand-in.
    """

    by_id = {cell.mechanic_id: cell for cell in current_program_cells()}
    reports = []
    for mechanic_id in AUDITED_MECHANIC_IDS:
        cell = by_id.get(mechanic_id)
        if cell is None:
            reports.append((mechanic_id, MechanicAuditVerdict.CANNOT_CHECK, 0))
            continue
        report = audit_mechanic(cell)
        reports.append((mechanic_id, report.verdict, len(report.open_questions)))
    return tuple(reports)


class _StudyReasoner:
    """Deterministic reasoner for the study's DIAGNOSE/REFRAME path.

    It carries no knowledge the perception layer did not observe: the
    responsibility it reports is the one already typed on the cue. Only
    `diagnose` and `propose_reframe` are exercised — the search/absorb path is
    not part of a P1 case — and the unexercised members raise rather than
    return a plausible-looking placeholder that could be mistaken for work.
    """

    def __init__(self, cue_by_residual: dict[str, Cue], *, case_id: str) -> None:
        self._cues = cue_by_residual
        self._case_id = case_id

    def diagnose(self, residual: Residual, problem: Problem, state: OrionState) -> Diagnosis:
        cue = self._cues.get(residual.residual_id)
        if cue is None:
            return Diagnosis((), "no observation supports an attribution")
        return Diagnosis(
            (cue.responsibility,),
            f"attributed from {cue.strength.value} observation {cue.marker!r}",
        )

    def propose_reframe(
        self,
        residual: Residual,
        diagnosis: Diagnosis,
        problem: Problem,
        state: OrionState,
    ) -> ReframeProposal:
        responsibility = diagnosis.responsibilities[0]
        # The identity of the missing domain/representation is exactly what a
        # mechanical system cannot establish, so it is named as unresolved
        # rather than invented.
        if responsibility in {Responsibility.SEARCH, Responsibility.ROUTING}:
            return ReframeProposal(
                add_domain_ids=(f"unnamed-parent-domain:{self._case_id}",),
                note="a parent domain is required; its identity is not established",
            )
        if responsibility is Responsibility.REPRESENTATION:
            return ReframeProposal(
                add_representation_ids=(f"unnamed-representation:{self._case_id}",),
                note="a new representation is required; its identity is not established",
            )
        return ReframeProposal(note=f"{responsibility.value} coordinate change")

    def plan_search(self, problem: Problem, state: OrionState):  # pragma: no cover
        raise NotImplementedError("the study drives DIAGNOSE/REFRAME/REOPEN directly")

    def interpret(self, item, problem: Problem, state: OrionState):  # pragma: no cover
        raise NotImplementedError("the study drives DIAGNOSE/REFRAME/REOPEN directly")

    def reconstruct(self, problem: Problem, state: OrionState) -> str:  # pragma: no cover
        raise NotImplementedError("the study drives DIAGNOSE/REFRAME/REOPEN directly")

    def compose_answer(self, problem: Problem, state: OrionState) -> str:  # pragma: no cover
        raise NotImplementedError("the study drives DIAGNOSE/REFRAME/REOPEN directly")


def _license(responsibility: Responsibility) -> tuple[bool, str]:
    """Is a local formulation change licensed for this responsibility?

    `local_reframe_allowed` answers the question for ORION's own coordinates.
    The suite's EVALUATOR label denotes the *task's* scoring model rather than
    ORION's protected evaluator binding, so that one case is decided here, in
    the open, instead of by silently reusing an answer to a different question.
    METHOD stays protected with no exception.
    """

    if responsibility is Responsibility.METHOD:
        return False, "protected: method revision is a governed Self-ORION transition"
    if responsibility is Responsibility.EVALUATOR:
        return True, "task-level evaluator model is part of the task formulation"
    return local_reframe_allowed(responsibility), "engine licensing"


def _initial_state(closures: tuple[PublicClosure, ...], residuals: tuple[Residual, ...]) -> OrionState:
    return OrionState(
        knowledge=KnowledgeState(residuals=residuals),
        search_universe=SearchUniverseState(),
        method=MethodState(
            method_version=FRAMEWORK_VERSION,
            operator_ids=CORE_OPERATOR_IDS,
            evaluator_id="p1-study-host",
        ),
        closure_certificates=tuple(
            ClosureCertificate(
                certificate_id=item.closure_id,
                scope="p1-case",
                dependency_coordinates=item.dependency_coordinates,
            )
            for item in closures
        ),
    )


@dataclass(frozen=True)
class OrionSystem:
    """Full ORION, or one ablation of it, as a `SystemUnderTest`."""

    system_id: str
    policy: OrionPolicy = field(default_factory=OrionPolicy)
    # Optional hook: given the public view, name the closures a reframe
    # invalidates. Mechanical mode leaves it None and identifies nothing —
    # naming them is a reasoning act, not something the public view discloses.
    # The live arm supplies it; without it `D*(c)` cannot start on this suite.
    identify_closures: Callable[[PublicView], tuple[str, ...]] | None = None

    # -- decision ---------------------------------------------------------

    def _select(
        self, cues: tuple[Cue, ...], rng, tried: set[str]
    ) -> tuple[Cue | None, DiagnosisState, tuple[str, ...]]:
        """Choose the coordinate to change, or decline to change one.

        Returns the selected cue, the self-audit's diagnosis state, and the
        notes that state produced. `tried` carries the coordinates already
        varied, so untyped retry does not re-try the same branch.
        """

        material = material_cues(cues)
        strong_formulation = [cue for cue in material if cue.formulation]
        weak_formulation = [
            cue for cue in cues if cue.formulation and not cue.material
        ]

        if not self.policy.typed_reframe:
            # Generic retry: vary a coordinate without typing responsibility,
            # never re-trying a branch already varied.
            candidates = [
                cue
                for cue in cues
                if cue.formulation and cue.coordinate and cue.coordinate not in tried
            ]
            rng.shuffle(candidates)
            selected = candidates[0] if candidates else None
            if selected is not None:
                tried.add(selected.coordinate)
            return selected, DiagnosisState.UNCLASSIFIED, ("untyped_variation",)

        if not self.policy.mechanic_self_audit:
            # No discriminator obligation: commit to the highest-impact
            # hypothesis available, weak observations included. This is the
            # reframe-happy failure mode H2 measures.
            candidates = strong_formulation or weak_formulation
            selected = candidates[0] if candidates else None
            return selected, DiagnosisState.LOCALLY_ATTRIBUTED, ("no_self_audit",)

        if not strong_formulation:
            # Weak observations are hypotheses, not licenses. Nothing here
            # supports a formulation change.
            return None, DiagnosisState.LOCALLY_ATTRIBUTED, ("no_material_formulation_residual",)

        responsibilities = {cue.responsibility for cue in strong_formulation}
        if len(responsibilities) == 1:
            return strong_formulation[0], DiagnosisState.LOCALLY_ATTRIBUTED, ()

        # Ambiguous attribution. Try to discriminate on the only evidence
        # available without world knowledge: an observation of the failure
        # happening now (the prompt) outranks a statement of an assumption some
        # earlier closure was taken under (a resource line). The second is
        # evidence about the past, not about this failure.
        discriminated = [cue for cue in strong_formulation if cue.source == "prompt"]
        if len(discriminated) == 1:
            return (
                discriminated[0],
                DiagnosisState.LOCALLY_ATTRIBUTED,
                ("discriminator_applied",),
            )
        return (
            None,
            DiagnosisState.DISCRIMINATOR_REQUIRED,
            ("ambiguous_responsibility_blocks_high_impact_revision",),
        )

    # -- execution --------------------------------------------------------

    def run(self, view: PublicView, *, seed: int) -> SystemTrace:
        budget = budget_for(view)
        ledger = ProbeLedger(budget)
        rng = deterministic_rng(self.system_id, view, seed)

        cues = extract_cues(view)
        ledger.probe(len(readable_resources(view)))
        closures = public_closures(view)

        residual_by_cue = {
            cue.cue_id: cue_to_residual(cue, case_id=view.case_id) for cue in cues
        }
        cue_by_residual = {
            residual.residual_id: cue
            for cue in cues
            for residual in (residual_by_cue[cue.cue_id],)
        }
        state = _initial_state(closures, tuple(residual_by_cue.values()))
        problem = Problem(
            problem_id=view.case_id,
            question=view.public_prompt,
            scope="ORION-P1 hidden-formulation case",
        )
        reasoner = _StudyReasoner(cue_by_residual, case_id=view.case_id)
        diagnose_operator = DiagnoseOperator(reasoner)
        reframe_operator = ReframeOperator(reasoner)
        reopen_operator = ReopenOperator()

        notes: list[str] = []
        invariants: list[str] = []
        authority: list[str] = []
        changed: list[str] = []
        reopened: list[str] = []
        selected_responsibility: Responsibility | None = None
        audit_state = DiagnosisState.UNCLASSIFIED
        depth = 1

        # Self-audit of the mechanics this decision path exercises. A cell that
        # cannot be checked blocks the high-impact path; an OPEN cell is
        # recorded, because open coordinates are the normal state of a research
        # mechanic and are not a reason to refuse to act.
        #
        # The probe is charged whether or not the policy performs the audit, so
        # `orion_without_mechanic_self_audit` stays resource-matched: it holds
        # the same introspection slot and simply does nothing with it. An
        # ablation that spent less would confound the comparison.
        ledger.probe(1)
        if self.policy.mechanic_self_audit:
            blocked = [
                mechanic_id
                for mechanic_id, verdict, _ in _audited_cells()
                if verdict is MechanicAuditVerdict.CANNOT_CHECK
            ]
            open_total = sum(count for _, _, count in _audited_cells())
            notes.append(f"mechanic_self_audit open_questions={open_total}")
            if blocked:
                notes.append("mechanic_self_audit_blocked=" + ",".join(blocked))
                audit_state = DiagnosisState.CANNOT_CHECK

        # Rounds come from the shared planner, which every baseline also uses,
        # so all eleven systems get the same number of turns on the same case.
        rounds = planned_rounds(cues, budget)
        remaining = cues
        tried: set[str] = set()

        for _ in range(rounds):
            if not ledger.query(1):
                break
            if audit_state is DiagnosisState.CANNOT_CHECK:
                continue

            selected, audit_state, round_notes = self._select(remaining, rng, tried)
            notes.extend(round_notes)
            # Axes actually moved this round. A coordinate change counts as a
            # reframe whether or not it repaired anything — that is what makes
            # an unnecessary reframe on a negative control measurable.
            applied: list[str] = []

            if selected is not None:
                residual = residual_by_cue[selected.cue_id]
                diagnosis_result = diagnose_operator.run(residual, problem, state)
                self._validate(diagnosis_result.transition, invariants)
                diagnosis = diagnosis_result.output
                state = diagnosis_result.state

                licensed, reason = (
                    _license(diagnosis.responsibilities[0])
                    if revision_allowed(diagnosis.responsibilities)
                    else (False, "ambiguous responsibility")
                )
                if not licensed and diagnosis.responsibilities:
                    responsibility = diagnosis.responsibilities[0]
                    if responsibility is Responsibility.METHOD:
                        if self.policy.mechanic_self_audit:
                            notes.append("escalated_to_protected_gate:M.METHOD")
                        else:
                            # Attempt it and let the engine refuse: the refusal
                            # is the authority structure doing its job, and the
                            # attempt is what the study records.
                            try:
                                reframe_operator.run(residual, diagnosis, problem, state)
                            except PermissionError:
                                authority.append(
                                    "attempted_method_reframe_without_protected_gate"
                                )
                            except ValueError as error:
                                notes.append(f"reframe_refused:{error}")
                    else:
                        notes.append(f"reframe_not_licensed:{reason}")
                elif licensed:
                    axis = COORDINATE_BY_RESPONSIBILITY.get(selected.responsibility, "")
                    if axis in self.policy.reachable_coordinates:
                        if axis in ENGINE_EXECUTABLE_AXES:
                            result = reframe_operator.run(
                                residual, diagnosis, problem, state
                            )
                            self._validate(result.transition, invariants)
                            state = result.state
                            if axis not in result.transition.changed_coordinates:
                                invariants.append(
                                    f"reframe_did_not_move_claimed_axis:{axis}"
                                )
                        else:
                            notes.append(f"engine_gap:{axis}")
                        applied.append(axis)
                        if self.policy.typed_reframe and selected_responsibility is None:
                            # The primary attribution, not the last one. A deep
                            # case can require more than one coordinate change,
                            # and a later round must not overwrite the
                            # responsibility this run actually diagnosed first —
                            # which is also the one `target_coordinates` reports.
                            selected_responsibility = selected.responsibility
                    else:
                        notes.append(f"coordinate_out_of_policy:{axis}")

            outcome = apply_repairs(
                remaining,
                surface=frozenset({Responsibility.EVIDENCE, Responsibility.EXECUTION}),
                reachable_coordinates=frozenset(applied),
            )
            remaining = outcome.remaining
            if applied:
                changed.extend(applied)
                depth += 1
                reopened.extend(
                    self._reopen(
                        reopen_operator, state, tuple(applied), closures, view
                    )
                )

        changed_coordinates = tuple(dict.fromkeys(changed))
        reopened_ids = tuple(dict.fromkeys(reopened))
        if len(authority) > 1:
            # One kind of violation attempted N times is one violation with a
            # count, not N findings: `authority_violation_rate` counts systems
            # that broke the rule, and repeating the string would inflate it.
            notes.append(f"authority_attempts={len(authority)}")
        authority = list(dict.fromkeys(authority))
        notes = list(dict.fromkeys(notes))
        self._check_policy_scope(changed_coordinates, invariants)
        self._check_reopen_scope(reopened_ids, closures, invariants)

        stale = stale_closures_survive(
            closures, changed=changed_coordinates, reopened=reopened_ids
        )
        reframed = bool(changed_coordinates)
        return SystemTrace(
            case_id=view.case_id,
            system_id=self.system_id,
            seed=seed,
            reframed=reframed,
            responsibility_family=(
                selected_responsibility.value if selected_responsibility else ""
            ),
            target_coordinates=axis_answer(changed_coordinates) if reframed else (),
            reopened=reopened_ids,
            # Stale certainty is measured by its own protocol metric and is
            # reported in `notes`; folding it into root success would
            # double-charge one mistake and confound the primary metric.
            # Seeing no residual is not solving the task — see `abstains`.
            root_solved=solved(cues, remaining),
            abstained=abstains(cues, remaining, changed_coordinates),
            invariant_violations=tuple(invariants),
            authority_violations=tuple(authority),
            max_recursion_depth=depth,
            resources=ledger.usage,
            notes="; ".join(
                (*notes, f"diagnosis_state={audit_state.value}", f"stale={sorted(stale)}")
            ),
        )

    # -- reopening --------------------------------------------------------

    def _reopen(
        self,
        operator: ReopenOperator,
        state: OrionState,
        changed: tuple[str, ...],
        closures: tuple[PublicClosure, ...],
        view: PublicView,
    ) -> tuple[str, ...]:
        if self.policy.reopen_mode is ReopenMode.NONE:
            return ()
        if self.policy.reopen_mode is ReopenMode.FULL_RESET:
            # A full reset does not consult the dependency basis; that is
            # precisely what makes it a full reset.
            return tuple(item.closure_id for item in closures)
        result = operator.run(state, changed_coordinates=changed, reason="reframe")
        staled = tuple(result.output)
        # Coordinate-keyed staling is exact when a closure declares a basis, and
        # silent when it does not — which on the frozen suite is 37 of 44 cases.
        # A system that has *identified* the invalidated closure supplies it
        # here, and `D*(c)` is then completed over the closure graph. Mechanical
        # mode identifies nothing and this adds nothing; the live arm is where
        # it matters, and without it a correct live diagnosis would still reopen
        # nothing.
        identified = self.identify_closures(view) if self.identify_closures else ()
        if identified:
            staled = tuple(
                dict.fromkeys((*staled, *descendants_of(closures, tuple(identified))))
            )
        return staled

    # -- invariants -------------------------------------------------------

    @staticmethod
    def _validate(transition: Transition, invariants: list[str]) -> None:
        try:
            transition.validate()
        except ValueError as error:  # pragma: no cover - defense in depth
            invariants.append(f"transition_invalid:{transition.operator.value}:{error}")

    def _check_policy_scope(self, changed: tuple[str, ...], invariants: list[str]) -> None:
        """A system may not change a coordinate its policy cannot reach."""

        for axis in changed:
            if axis not in self.policy.reachable_coordinates:
                invariants.append(f"coordinate_outside_policy:{axis}")

    @staticmethod
    def _check_reopen_scope(
        reopened: tuple[str, ...],
        closures: tuple[PublicClosure, ...],
        invariants: list[str],
    ) -> None:
        """A system may only reopen closures the public view actually names."""

        known = {item.closure_id for item in closures}
        for closure_id in reopened:
            if closure_id not in known:
                invariants.append(f"reopened_unknown_closure:{closure_id}")


# --------------------------------------------------------------------------
# Full ORION and the five frozen ablations
# --------------------------------------------------------------------------


ABLATION_IDS: tuple[str, ...] = (
    "orion_without_explicit_W",
    "orion_without_explicit_M",
    "generic_retry_instead_of_typed_reframe",
    "full_reset_instead_of_dependency_reopen",
    "orion_without_mechanic_self_audit",
)

FULL_ORION_ID = "orion_full"


def full_orion() -> OrionSystem:
    return OrionSystem(system_id=FULL_ORION_ID, policy=OrionPolicy())


def ablation_systems() -> tuple[OrionSystem, ...]:
    """The five frozen ablations, resource-matched to full ORION.

    Each removes exactly one organ:

    * ``orion_without_explicit_W`` keeps typed diagnosis and dependency-directed
      reopening but has no world-model coordinates to move.
    * ``orion_without_explicit_M`` keeps W but cannot reach the measurement or
      evaluator coordinates.
    * ``generic_retry_instead_of_typed_reframe`` keeps K/W/M state *and* the
      dependency-directed reopen machinery, and replaces only the typed
      decision with an untyped variation. It is therefore not a re-labelled
      tree search: it still stales exactly what depended on what it changed.
    * ``full_reset_instead_of_dependency_reopen`` makes the identical typed
      decision as full ORION and differs only in reopen scope.
    * ``orion_without_mechanic_self_audit`` drops the discriminator obligation
      and commits to the highest-impact hypothesis, weak evidence included.
    """

    return (
        OrionSystem(
            system_id="orion_without_explicit_W",
            policy=OrionPolicy(explicit_w=False),
        ),
        OrionSystem(
            system_id="orion_without_explicit_M",
            policy=OrionPolicy(explicit_m=False),
        ),
        OrionSystem(
            system_id="generic_retry_instead_of_typed_reframe",
            policy=OrionPolicy(typed_reframe=False),
        ),
        OrionSystem(
            system_id="full_reset_instead_of_dependency_reopen",
            policy=OrionPolicy(reopen_mode=ReopenMode.FULL_RESET),
        ),
        OrionSystem(
            system_id="orion_without_mechanic_self_audit",
            policy=OrionPolicy(mechanic_self_audit=False),
        ),
    )


def orion_systems() -> tuple[OrionSystem, ...]:
    """Full ORION followed by the five ablations."""

    return (full_orion(), *ablation_systems())


__all__ = [
    "ABLATION_IDS",
    "AUDITED_MECHANIC_IDS",
    "ENGINE_EXECUTABLE_AXES",
    "FULL_ORION_ID",
    "OrionPolicy",
    "OrionSystem",
    "ReopenMode",
    "ablation_systems",
    "full_orion",
    "orion_systems",
]
