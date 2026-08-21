from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Any, Callable, Mapping
from .library import MechanicLibrary
from .competence import CompetenceMap
from .abstraction import mine_macros
from .induction import TransitionContractInducer
from .ledger import ExperienceLedger
from .types import (
    Experience, MechanicSpec, Provenance, Verdict, SolverPlan,
    ExecutionResult, PlanExecution, TransitionObservation,
    CapabilityRoute, EmpiricalMechanicContract,
)

Authorizer = Callable[[Any, MechanicSpec], Verdict]
ExternalExecutor = Callable[[Any, MechanicSpec], ExecutionResult]

@dataclass
class LearningMachine:
    """Executable P9 research core.

    The object deliberately separates four responsibilities:
    * `library`: what named mechanics have been absorbed, with donor lineage;
    * `competence`: where admitted success/failure evidence supports use;
    * `contracts`: empirical state-effect regularities learned from transitions;
    * `ledger`: append-only retained experience, including failures/UNKNOWN.

    None of those components can authorize an external effect.  Execution always
    passes through an authority callback owned outside P9.
    """
    library: MechanicLibrary
    competence: CompetenceMap
    contracts: TransitionContractInducer
    ledger: ExperienceLedger

    @classmethod
    def empty(cls) -> "LearningMachine":
        return cls(MechanicLibrary(), CompetenceMap(), TransitionContractInducer(), ExperienceLedger())

    def absorb_action_families(self, trajectories: list[dict]) -> None:
        """Absorb conservative source-level action families.

        This is intentionally a low-authority adapter: recurring source syntax
        becomes a provenance-bearing candidate mechanic, not a semantic theorem
        about what that action always does.
        """
        for t in trajectories:
            donor=t["donor"]; source=t["source_id"]
            for fam in t["mechanics"]:
                mid=f"lean:{fam}"
                self.library.register(MechanicSpec(
                    mid,fam,f"Conservative Lean source family: {fam}",1.0,
                    (Provenance(donor,source),), compatibility_key=f"lean-source-family:{fam}"
                ))
        for macro in mine_macros(trajectories):
            self.library.register_macro(macro)

    def absorb_transition_observations(
        self,
        rows: list[TransitionObservation],
        *,
        min_support: int = 2,
    ) -> tuple[EmpiricalMechanicContract, ...]:
        """Induce empirical mechanic contracts from observed state transitions.

        Donor-specific observed effects are retained as protected traits, while
        the modal contract remains explicitly empirical.  This method never
        upgrades an observation into a universal precondition/effect rule.
        """
        for r in rows:
            self.library.register(MechanicSpec(
                mechanic_id=r.mechanic_id,
                family="empirical_transition",
                description=f"Empirical transition mechanic: {r.mechanic_id}",
                provenance=(Provenance(r.donor,r.source_id,step=None,metadata={"trace_id":r.trace_id}),),
                protected_traits=(f"{r.donor}:observed_effect={r.effect}",),
                compatibility_key=f"empirical-transition:{r.mechanic_id}",
            ))
        self.contracts=TransitionContractInducer(min_support=min_support).fit(rows)
        return self.contracts.contracts

    def record_experience(self, experience: Experience) -> None:
        self.ledger.append(experience)

    def record_experiences(self, experiences: list[Experience]) -> None:
        for e in experiences:
            self.record_experience(e)

    def fit_competence(self, experiences: list[Experience]) -> None:
        """Fit competence without silently rewriting the evidence ledger."""
        self.competence.fit(experiences)

    def route_capability(
        self,
        candidate_mechanic_ids: tuple[str, ...] | list[str],
        features_by_mechanic: Mapping[str, Mapping[str, float]],
        *,
        min_success_probability: float = 0.5,
    ) -> CapabilityRoute:
        """Select supported capability or abstain, without authorizing execution.

        This is the framework-level selective-prediction boundary. Every
        candidate receives an inspectable competence estimate. Unknown or
        failure-only evidence fails closed; ties are deterministic by mechanic
        ID. A successful route must still pass through ``execute_plan`` and its
        external authorizer before any effect occurs.
        """
        if not 0.0 <= min_success_probability <= 1.0:
            raise ValueError("min_success_probability must be in [0, 1]")
        candidate_ids = tuple(dict.fromkeys(candidate_mechanic_ids))
        if not candidate_ids:
            raise ValueError("at least one candidate mechanic is required")

        assessments = []
        for mechanic_id in candidate_ids:
            self.library.resolve(mechanic_id)
            assessments.append(
                self.competence.estimate(
                    mechanic_id,
                    dict(features_by_mechanic.get(mechanic_id, {})),
                )
            )
        eligible = [
            estimate
            for estimate in assessments
            if estimate.status == Verdict.SUCCESS
            and estimate.p_success >= min_success_probability
        ]
        if eligible:
            selected = sorted(
                eligible,
                key=lambda estimate: (-estimate.p_success, estimate.mechanic_id),
            )[0]
            return CapabilityRoute(
                selected_mechanic_id=selected.mechanic_id,
                status=Verdict.SUCCESS,
                assessments=tuple(assessments),
                min_success_probability=min_success_probability,
                reason="highest supported competence estimate; external authorization still required",
            )

        status = (
            Verdict.UNKNOWN
            if any(estimate.status == Verdict.UNKNOWN for estimate in assessments)
            else Verdict.FAIL
        )
        return CapabilityRoute(
            selected_mechanic_id=None,
            status=status,
            assessments=tuple(assessments),
            min_success_probability=min_success_probability,
            reason="abstained: no candidate has supported success above threshold",
        )

    def execute_plan(
        self,
        plan: SolverPlan,
        state: Any,
        authorizer: Authorizer,
        external_executor: ExternalExecutor | None = None,
    ) -> PlanExecution:
        """Execute only after an external authority decision for every step.

        P9 supplies capability; it never upgrades capability into authority. A
        future P8 adapter can implement `authorizer`. Missing execution
        capability or non-success authority fails closed.
        """
        results=[]; cur=state
        for i,step in enumerate(plan.steps):
            spec=self.library.resolve(step.mechanic_id)
            auth=authorizer(cur,spec)
            if auth != Verdict.SUCCESS:
                verdict=auth if auth in {Verdict.UNAUTHORIZED,Verdict.CANNOT_CHECK,Verdict.FAIL,Verdict.UNKNOWN} else Verdict.UNAUTHORIZED
                r=ExecutionResult(verdict,cur,spec.mechanic_id,provenance=spec.provenance,reason='authority did not permit commit')
                results.append(r)
                return PlanExecution(verdict,cur,tuple(results),i,r.reason)
            if external_executor is not None:
                r=external_executor(cur,spec)
            elif spec.executor is not None:
                r=spec.executor(cur)
            else:
                r=ExecutionResult(Verdict.CANNOT_CHECK,cur,spec.mechanic_id,provenance=spec.provenance,reason='no executor bound')
            if r.mechanic_id != spec.mechanic_id:
                raise ValueError(f'executor identity mismatch: {r.mechanic_id} != {spec.mechanic_id}')
            if not r.provenance:
                r=replace(r,provenance=spec.provenance)
            results.append(r); cur=r.state
            if r.verdict != Verdict.SUCCESS:
                return PlanExecution(r.verdict,cur,tuple(results),i,r.reason)
        return PlanExecution(Verdict.SUCCESS,cur,tuple(results),None,None)
