from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Any, Callable
from .library import MechanicLibrary
from .competence import CompetenceMap
from .abstraction import mine_macros
from .induction import TransitionContractInducer
from .ledger import ExperienceLedger
from .types import (
    Experience, MechanicSpec, Provenance, Verdict, SolverPlan,
    ExecutionResult, PlanExecution, TransitionObservation,
    EmpiricalMechanicContract,
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
