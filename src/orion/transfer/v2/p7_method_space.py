from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Sequence
from .canonical import content_digest

class EdgeKind(str,Enum):
    METHOD_NEIGHBOR='METHOD_NEIGHBOR'; FIBRE_REALIZATION='FIBRE_REALIZATION'; STRUCTURAL_ANALOGY_ROUTE='STRUCTURAL_ANALOGY_ROUTE'; METHOD_GENERALIZE='METHOD_GENERALIZE'; METHOD_SPECIALIZE='METHOD_SPECIALIZE'; METHOD_COMPOSE_ROUTE='METHOD_COMPOSE_ROUTE'; REPRESENTATION_CHANGE='REPRESENTATION_CHANGE'; INVENTION_ESCALATION='INVENTION_ESCALATION'
class StopScope(str,Enum):
    ROUTE='ROUTE'; CHART='CHART'; KNOWN_LIBRARY='KNOWN_LIBRARY'; TASK='TASK'
class NavState(str,Enum):
    AVAILABLE='AVAILABLE'; BLOCKED='BLOCKED'; UNRESOLVED='UNRESOLVED'

@dataclass(frozen=True)
class MethodChartEdge:
    source_digest:str; target_digest:str; kind:EdgeKind; provenance_digest:str; rationale:str; reconstruction_required:bool=False; reconstruction_valid:bool|None=None
    def __post_init__(self):
        for x in (self.source_digest,self.target_digest,self.provenance_digest):
            if not x.startswith('sha256:'): raise ValueError('edge digests must be sha256-prefixed')
    def payload(self): return {'source_digest':self.source_digest,'target_digest':self.target_digest,'kind':self.kind.value,'provenance_digest':self.provenance_digest,'rationale':self.rationale,'reconstruction_required':self.reconstruction_required,'reconstruction_valid':self.reconstruction_valid}

@dataclass(frozen=True)
class MethodChart:
    chart_id:str; subject_digest:str; construction_rule:str; signature_digests:tuple[str,...]; fibre_digests:tuple[str,...]; edges:tuple[MethodChartEdge,...]; route_ids:tuple[str,...]; source_families:tuple[str,...]; unknown_boundary:tuple[str,...]; noncoverage:tuple[str,...]; reopen_triggers:tuple[str,...]; epoch:int; digest:str
    def unsigned(self): return {'version':'MethodChart.v1','chart_id':self.chart_id,'subject_digest':self.subject_digest,'construction_rule':self.construction_rule,'signature_digests':list(self.signature_digests),'fibre_digests':list(self.fibre_digests),'edges':[e.payload() for e in self.edges],'route_ids':list(self.route_ids),'source_families':list(self.source_families),'unknown_boundary':list(self.unknown_boundary),'noncoverage':list(self.noncoverage),'reopen_triggers':list(self.reopen_triggers),'epoch':self.epoch,'authority_scope':'NAVIGATION_ONLY','can_claim_global_exhaustion':False,'can_authorize_invention':False}
    def verify(self):
        if not self.chart_id or not self.subject_digest.startswith('sha256:'): raise ValueError('invalid chart identity')
        if content_digest(self.unsigned())!=self.digest: raise ValueError('chart digest mismatch')

def build_chart(*,chart_id:str,subject_digest:str,construction_rule:str,signature_digests:Sequence[str],fibre_digests:Sequence[str]=(),edges:Sequence[MethodChartEdge]=(),route_ids:Sequence[str]=(),source_families:Sequence[str]=(),unknown_boundary:Sequence[str]=(),noncoverage:Sequence[str]=(),reopen_triggers:Sequence[str]=(),epoch:int=1):
    ordered=tuple(sorted(edges,key=lambda e:(e.source_digest,e.target_digest,e.kind.value)))
    base={'version':'MethodChart.v1','chart_id':chart_id,'subject_digest':subject_digest,'construction_rule':construction_rule,'signature_digests':sorted(set(signature_digests)),'fibre_digests':sorted(set(fibre_digests)),'edges':[e.payload() for e in ordered],'route_ids':sorted(set(route_ids)),'source_families':sorted(set(source_families)),'unknown_boundary':sorted(set(unknown_boundary)),'noncoverage':sorted(set(noncoverage)),'reopen_triggers':sorted(set(reopen_triggers)),'epoch':epoch,'authority_scope':'NAVIGATION_ONLY','can_claim_global_exhaustion':False,'can_authorize_invention':False}
    c=MethodChart(chart_id,subject_digest,construction_rule,tuple(base['signature_digests']),tuple(base['fibre_digests']),ordered,tuple(base['route_ids']),tuple(base['source_families']),tuple(base['unknown_boundary']),tuple(base['noncoverage']),tuple(base['reopen_triggers']),epoch,content_digest(base));c.verify();return c

def edge_state(edge:MethodChartEdge):
    if edge.kind is EdgeKind.REPRESENTATION_CHANGE and edge.reconstruction_required:
        if edge.reconstruction_valid is False:return NavState.BLOCKED
        if edge.reconstruction_valid is None:return NavState.UNRESOLVED
    return NavState.AVAILABLE

@dataclass(frozen=True)
class NavigationEvent:
    event_id:str; chart_digest:str; kind:EdgeKind; source_digest:str; target_digest:str; evidence_digest:str; provenance_digest:str; rationale:str; state:NavState; digest:str
    def unsigned(self): return {'version':'P7.NavigationEvent.v1','event_id':self.event_id,'chart_digest':self.chart_digest,'kind':self.kind.value,'source_digest':self.source_digest,'target_digest':self.target_digest,'evidence_digest':self.evidence_digest,'provenance_digest':self.provenance_digest,'rationale':self.rationale,'state':self.state.value,'authority_scope':'NAVIGATION_ONLY','can_authorize_transfer':False,'can_claim_novelty':False}
    def verify(self):
        if content_digest(self.unsigned())!=self.digest: raise ValueError('event digest mismatch')

def record_event(chart:MethodChart, edge:MethodChartEdge, *, event_id:str,evidence_digest:str):
    chart.verify(); st=edge_state(edge); base={'version':'P7.NavigationEvent.v1','event_id':event_id,'chart_digest':chart.digest,'kind':edge.kind.value,'source_digest':edge.source_digest,'target_digest':edge.target_digest,'evidence_digest':evidence_digest,'provenance_digest':edge.provenance_digest,'rationale':edge.rationale,'state':st.value,'authority_scope':'NAVIGATION_ONLY','can_authorize_transfer':False,'can_claim_novelty':False};e=NavigationEvent(event_id,chart.digest,edge.kind,edge.source_digest,edge.target_digest,evidence_digest,edge.provenance_digest,edge.rationale,st,content_digest(base));e.verify();return e

@dataclass(frozen=True)
class StopReceipt:
    scope:StopScope; chart_digest:str; reason:str; task_terminal:str; global_method_space_open:bool; external_authority_digest:str; digest:str
    def unsigned(self): return {'version':'P7.MethodStopReceipt.v1','scope':self.scope.value,'chart_digest':self.chart_digest,'reason':self.reason,'task_terminal':self.task_terminal,'global_method_space_open':self.global_method_space_open,'external_authority_digest':self.external_authority_digest,'can_claim_global_nonexistence':False}
    def verify(self):
        if self.scope is not StopScope.TASK and (self.task_terminal!='OPEN' or not self.global_method_space_open): raise ValueError('local stop cannot close global task')
        if self.scope is StopScope.TASK and (self.task_terminal!='CLOSED' or not self.external_authority_digest.startswith('sha256:')): raise ValueError('task stop requires external authority')
        if content_digest(self.unsigned())!=self.digest: raise ValueError('stop digest mismatch')

def stop(chart:MethodChart, *, scope:StopScope,reason:str,task_closable:bool=False,external_authority_digest:str=''):
    chart.verify(); terminal='CLOSED' if scope is StopScope.TASK and task_closable else 'OPEN'; open_space=scope is not StopScope.TASK
    if scope is StopScope.TASK and not task_closable: raise ValueError('task stop not externally authorized')
    base={'version':'P7.MethodStopReceipt.v1','scope':scope.value,'chart_digest':chart.digest,'reason':reason,'task_terminal':terminal,'global_method_space_open':open_space,'external_authority_digest':external_authority_digest,'can_claim_global_nonexistence':False};r=StopReceipt(scope,chart.digest,reason,terminal,open_space,external_authority_digest,content_digest(base));r.verify();return r

@dataclass(frozen=True)
class InventionEscalation:
    chart_digest:str; attempted_route_ids:tuple[str,...]; required_route_ids:tuple[str,...]; eligible:bool; reason:str; can_authorize_invention:bool=False

def propose_invention(chart:MethodChart, *, attempted_route_ids:Sequence[str],required_route_ids:Sequence[str]):
    chart.verify(); missing=sorted(set(required_route_ids)-set(attempted_route_ids)); return InventionEscalation(chart.digest,tuple(sorted(set(attempted_route_ids))),tuple(sorted(set(required_route_ids))),not missing,'BOUNDED_KNOWN_ROUTE_POLICY_EXHAUSTED' if not missing else 'REQUIRED_KNOWN_ROUTES_UNTRIED',False)

def reopen_chart(chart:MethodChart, *, new_signature_digest:str|None=None,new_route_id:str|None=None):
    chart.verify(); sig=list(chart.signature_digests); routes=list(chart.route_ids)
    if new_signature_digest and new_signature_digest not in sig:sig.append(new_signature_digest)
    if new_route_id and new_route_id not in routes:routes.append(new_route_id)
    if not new_signature_digest and not new_route_id:return chart
    return build_chart(chart_id=chart.chart_id,subject_digest=chart.subject_digest,construction_rule=chart.construction_rule,signature_digests=sig,fibre_digests=chart.fibre_digests,edges=chart.edges,route_ids=routes,source_families=chart.source_families,unknown_boundary=chart.unknown_boundary,noncoverage=chart.noncoverage,reopen_triggers=chart.reopen_triggers,epoch=chart.epoch+1)

class RevisitLedger:
    def __init__(self): self._seen:set[tuple[str,str]]=set()
    def allow(self, event:NavigationEvent):
        key=(event.target_digest,event.evidence_digest)
        if key in self._seen:return False
        self._seen.add(key);return True
