"""Finite typed dynamic epistemic state for ORION.

Human-readable terminals are decision projections, not stored scientific state.
This reference implementation grants no scientific or publication authority.
"""
from __future__ import annotations
from dataclasses import dataclass, field, replace
from enum import Enum
from fractions import Fraction
from typing import Any, Callable, FrozenSet, Iterable, Mapping, Sequence

class Status(str, Enum):
    KNOWN="KNOWN"; PARTIAL="PARTIAL"; CANNOT_CHECK="CANNOT_CHECK"; REVOKED="REVOKED"
class Terminal(str, Enum):
    ADMISSIBLE="ADMISSIBLE"; PROVISIONAL="PROVISIONAL"; BLOCKED="BLOCKED"; CANNOT_CHECK="CANNOT_CHECK"
class Action(str, Enum):
    ACQUIRE_EVIDENCE="ACQUIRE_EVIDENCE"; EXPAND_COVERAGE="EXPAND_COVERAGE"; DISCRIMINATE="DISCRIMINATE"; OBTAIN_EXTERNAL_CUSTODY="OBTAIN_EXTERNAL_CUSTODY"; REVALIDATE="REVALIDATE"; SEARCH_LOCAL="SEARCH_LOCAL"; SEARCH_REMOTE_STRUCTURE="SEARCH_REMOTE_STRUCTURE"; EXPAND_METHOD_LANGUAGE="EXPAND_METHOD_LANGUAGE"; STOP="STOP"

@dataclass(frozen=True)
class Coordinate:
    value: Any; status: Status; scope: str; epoch: int; provenance_ids: tuple[str,...]=(); estimator_version: str="unspecified"
    def __post_init__(self):
        if not self.scope or self.epoch < 0: raise ValueError("invalid coordinate")
        if len(self.provenance_ids)!=len(set(self.provenance_ids)): raise ValueError("duplicate provenance")

@dataclass(frozen=True)
class SupportFamily:
    family_id: str; premise_ids: FrozenSet[str]; obligation_ids: FrozenSet[str]
    def __post_init__(self):
        if not self.family_id or not self.obligation_ids: raise ValueError("invalid support family")
    def survives(self, revoked: FrozenSet[str])->bool: return self.premise_ids.isdisjoint(revoked)

@dataclass(frozen=True)
class ResourceVector:
    acquisition: Fraction=Fraction(0); state: Fraction=Fraction(0); reasoning: Fraction=Fraction(0); verification: Fraction=Fraction(0); recovery: Fraction=Fraction(0); latency: Fraction=Fraction(0)
    def tuple(self): return (self.acquisition,self.state,self.reasoning,self.verification,self.recovery,self.latency)
    def no_more_than(self, other): return all(a<=b for a,b in zip(self.tuple(),other.tuple(),strict=True))

@dataclass(frozen=True)
class GainVector:
    identifiability: Fraction=Fraction(0); coverage: Fraction=Fraction(0); obligation: Fraction=Fraction(0); support: Fraction=Fraction(0); residual: Fraction=Fraction(0); method: Fraction=Fraction(0); frontier: Fraction=Fraction(0); cost: ResourceVector=field(default_factory=ResourceVector)
    def benefits(self): return (self.identifiability,self.coverage,self.obligation,self.support,self.residual,self.method,self.frontier)
    def dominates(self, other): return all(a>=b for a,b in zip(self.benefits(),other.benefits(),strict=True)) and self.cost.no_more_than(other.cost) and self!=other

@dataclass(frozen=True)
class State:
    subject_id: str; responsibility_id: str; epoch: int
    evidence: Coordinate; identifiability: Coordinate; coverage: Coordinate
    obligations_required: FrozenSet[str]; obligations_satisfied: FrozenSet[str]
    provenance: Coordinate; verification: Coordinate; authority_scopes: FrozenSet[str]
    support_families: tuple[SupportFamily,...]; active_defeaters: FrozenSet[str]
    custody_external: bool|None; method_reach_ids: FrozenSet[str]
    knowledge_node_ids: FrozenSet[str]; knowledge_edge_ids: FrozenSet[str]
    resources: ResourceVector=field(default_factory=ResourceVector)
    revoked_premise_ids: FrozenSet[str]=frozenset(); applied_event_ids: FrozenSet[str]=frozenset()
    def __post_init__(self):
        if not self.subject_id or not self.responsibility_id or self.epoch<0: raise ValueError("invalid state identity")
        if not self.obligations_satisfied.issubset(self.obligations_required): raise ValueError("invalid obligations")
    @property
    def unresolved(self): return self.obligations_required-self.obligations_satisfied
    @property
    def surviving_families(self): return tuple(f for f in self.support_families if f.survives(self.revoked_premise_ids))
    def complete_support(self): return any(self.obligations_required.issubset(f.obligation_ids) for f in self.surviving_families)

@dataclass(frozen=True)
class Event:
    event_id: str; subject_id: str; kind: str; digest: str; epoch: int; writes: Mapping[str,Any]
    def __post_init__(self):
        if not self.event_id or not self.subject_id or not self.kind or not self.digest or self.epoch<0: raise ValueError("invalid event")

_WRITABLE=frozenset({"evidence","identifiability","coverage","obligations_required","obligations_satisfied","provenance","verification","authority_scopes","support_families","active_defeaters","custody_external","method_reach_ids","knowledge_node_ids","knowledge_edge_ids","resources","revoked_premise_ids"})
def apply_event(state:State,event:Event)->State:
    if event.subject_id!=state.subject_id: raise ValueError("wrong subject")
    if event.event_id in state.applied_event_ids: return state
    if event.epoch<state.epoch: raise ValueError("backward epoch")
    unknown=set(event.writes)-_WRITABLE
    if unknown: raise ValueError(f"unregistered writes {sorted(unknown)}")
    return replace(state,epoch=event.epoch,applied_event_ids=state.applied_event_ids|{event.event_id},**dict(event.writes))
def replay(initial:State,events:Sequence[Event])->State:
    state=initial
    for event in events: state=apply_event(state,event)
    return state

@dataclass(frozen=True)
class HardObligation:
    obligation_id: str; predicate: Callable[[State],bool|None]; failure: Terminal=Terminal.BLOCKED
@dataclass(frozen=True)
class Policy:
    policy_id: str; responsibility_id: str; obligations: tuple[HardObligation,...]
    def project(self,state:State)->Terminal:
        if state.responsibility_id!=self.responsibility_id: return Terminal.CANNOT_CHECK
        unknown=False
        for h in self.obligations:
            result=h.predicate(state)
            if result is None: unknown=True
            elif result is False: return h.failure
        return Terminal.CANNOT_CHECK if unknown else Terminal.ADMISSIBLE

def promotion_policy(rid:str)->Policy:
    return Policy("promotion:v1",rid,(
        HardObligation("identified",lambda s: None if s.identifiability.status is Status.CANNOT_CHECK else bool(s.identifiability.value)),
        HardObligation("obligations",lambda s:not s.unresolved),
        HardObligation("support",lambda s:s.complete_support()),
        HardObligation("defeaters",lambda s:not s.active_defeaters),
        HardObligation("custody",lambda s:s.custody_external,Terminal.CANNOT_CHECK),
        HardObligation("authority",lambda s:rid in s.authority_scopes),
    ))

def compatible_states(states:Iterable[State],policy:Policy,terminal:Terminal): return tuple(s for s in states if policy.project(s) is terminal)

@dataclass(frozen=True)
class ResearchAction:
    action_id: str; action: Action; gain: GainVector; region_id: str; local: bool

def pareto(actions:Sequence[ResearchAction]):
    if len({a.action_id for a in actions})!=len(actions): raise ValueError("duplicate action")
    return tuple(a for a in actions if not any(b.action_id!=a.action_id and b.gain.dominates(a.gain) for b in actions))
def local_saturated(actions:Sequence[ResearchAction],minimum:Fraction=Fraction(0)):
    local=[a for a in actions if a.local]
    return bool(local) and all(not any(v>minimum for v in a.gain.benefits()) for a in pareto(local))
def should_jump(state:State,actions:Sequence[ResearchAction],minimum:Fraction=Fraction(0)):
    if not state.unresolved and not state.active_defeaters: return False
    if not local_saturated(actions,minimum): return False
    return any(any(v>minimum for v in a.gain.benefits()) for a in pareto([x for x in actions if not x.local]))

def revocation_survivors(families:Sequence[SupportFamily],revoked:Iterable[str]):
    r=frozenset(revoked); return tuple(f for f in families if f.survives(r))
