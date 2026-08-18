from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence
from .canonical import content_digest

class ProvenanceClass(str,Enum):
    DONOR_METHOD_REALIZATION='DONOR_METHOD_REALIZATION'; TRANSFERRED_METHOD='TRANSFERRED_METHOD'; COMPOSED_METHOD='COMPOSED_METHOD'; GENERALIZED_METHOD='GENERALIZED_METHOD'; SPECIALIZED_METHOD='SPECIALIZED_METHOD'; LEARNED_METHOD_PREDICTION='LEARNED_METHOD_PREDICTION'; INVENTED_METHOD_CANDIDATE='INVENTED_METHOD_CANDIDATE'; VERIFIED_METHOD_CANDIDATE='VERIFIED_METHOD_CANDIDATE'; ADOPTED_METHOD='ADOPTED_METHOD'
class AuthorityCoordinate(str,Enum):
    VALIDITY='VALIDITY'; APPLICABILITY='APPLICABILITY'; TRANSFER='TRANSFER'; NOVELTY='NOVELTY'; UTILITY='UTILITY'; ADOPTION='ADOPTION'; SEARCH_STOP='SEARCH_STOP'
class AuthorityState(str,Enum):
    SUPPORTED='SUPPORTED'; BLOCKED='BLOCKED'; CANNOT_CHECK='CANNOT_CHECK'
class CapabilityKind(str,Enum):
    P6_FIBRE='P6_FIBRE'; P7_NAVIGATION='P7_NAVIGATION'; P9_PREDICTION='P9_PREDICTION'; P10_GENERATION='P10_GENERATION'; P4_VERIFICATION='P4_VERIFICATION'; NOVELTY_REVIEW='NOVELTY_REVIEW'; P5_HOST_ADOPTION='P5_HOST_ADOPTION'; TASK_CLOSURE='TASK_CLOSURE'
class DefeaterKind(str,Enum):
    HIDDEN_ASSUMPTION='HIDDEN_ASSUMPTION'; FRESH_COUNTEREXAMPLE='FRESH_COUNTEREXAMPLE'; PRIOR_ART='PRIOR_ART'; PROTECTED_HARM='PROTECTED_HARM'; REPRESENTATION_CHANGED='REPRESENTATION_CHANGED'; SUBJECT_IDENTITY_CHANGED='SUBJECT_IDENTITY_CHANGED'; COMPOSITION_FOOTPRINT_CHANGED='COMPOSITION_FOOTPRINT_CHANGED'; EVALUATOR_CHANGED='EVALUATOR_CHANGED'

LEGAL:dict[CapabilityKind,frozenset[AuthorityCoordinate]]={
    CapabilityKind.P6_FIBRE:frozenset(),CapabilityKind.P7_NAVIGATION:frozenset(),CapabilityKind.P9_PREDICTION:frozenset(),CapabilityKind.P10_GENERATION:frozenset(),
    CapabilityKind.P4_VERIFICATION:frozenset({AuthorityCoordinate.VALIDITY,AuthorityCoordinate.APPLICABILITY,AuthorityCoordinate.TRANSFER,AuthorityCoordinate.UTILITY}),
    CapabilityKind.NOVELTY_REVIEW:frozenset({AuthorityCoordinate.NOVELTY}),CapabilityKind.P5_HOST_ADOPTION:frozenset({AuthorityCoordinate.ADOPTION}),CapabilityKind.TASK_CLOSURE:frozenset({AuthorityCoordinate.SEARCH_STOP})}

@dataclass(frozen=True)
class MethodProvenanceRecord:
    method_id:str; provenance_class:ProvenanceClass; subject_digest:str; source_ids:tuple[str,...]; generator_id:str; generator_version:str; predecessor_digest:str; evidence_digest:str; digest:str
    def unsigned(self):return {'version':'P8.MethodProvenanceRecord.v1','method_id':self.method_id,'provenance_class':self.provenance_class.value,'subject_digest':self.subject_digest,'source_ids':list(self.source_ids),'generator_id':self.generator_id,'generator_version':self.generator_version,'predecessor_digest':self.predecessor_digest,'evidence_digest':self.evidence_digest}
    def verify(self):
        if not self.subject_digest.startswith('sha256:') or not self.evidence_digest.startswith('sha256:'):raise ValueError('content identity required')
        if content_digest(self.unsigned())!=self.digest:raise ValueError('provenance digest mismatch')

def provenance(*,method_id:str,provenance_class:ProvenanceClass,subject_digest:str,source_ids:Sequence[str]=(),generator_id:str='',generator_version:str='',predecessor_digest:str='',evidence_digest:str):
    base={'version':'P8.MethodProvenanceRecord.v1','method_id':method_id,'provenance_class':provenance_class.value,'subject_digest':subject_digest,'source_ids':sorted(set(source_ids)),'generator_id':generator_id,'generator_version':generator_version,'predecessor_digest':predecessor_digest,'evidence_digest':evidence_digest};r=MethodProvenanceRecord(method_id,provenance_class,subject_digest,tuple(base['source_ids']),generator_id,generator_version,predecessor_digest,evidence_digest,content_digest(base));r.verify();return r

@dataclass(frozen=True)
class CapabilityOutput:
    kind:CapabilityKind; subject_digest:str; evidence_digest:str; score:float|None=None; label:str=''
@dataclass(frozen=True)
class CoercionDecision:
    source:CapabilityKind; coordinate:AuthorityCoordinate; state:AuthorityState; reason:str; evidence_digest:str; digest:str
    def unsigned(self):return {'version':'P8.CoercionDecision.v1','source':self.source.value,'coordinate':self.coordinate.value,'state':self.state.value,'reason':self.reason,'evidence_digest':self.evidence_digest}
    def verify(self):
        if content_digest(self.unsigned())!=self.digest:raise ValueError('coercion digest mismatch')

def coerce(output:CapabilityOutput, coordinate:AuthorityCoordinate):
    if coordinate not in LEGAL[output.kind]: state=AuthorityState.BLOCKED;reason='ILLICIT_CAPABILITY_TO_AUTHORITY_COERCION'
    elif not output.evidence_digest or not output.evidence_digest.startswith('sha256:'): state=AuthorityState.CANNOT_CHECK;reason='BOUND_EVIDENCE_MISSING'
    else: state=AuthorityState.SUPPORTED;reason='DECLARED_LEGAL_COERCION_WITH_BOUND_EVIDENCE'
    base={'version':'P8.CoercionDecision.v1','source':output.kind.value,'coordinate':coordinate.value,'state':state.value,'reason':reason,'evidence_digest':output.evidence_digest};x=CoercionDecision(output.kind,coordinate,state,reason,output.evidence_digest,content_digest(base));x.verify();return x

@dataclass(frozen=True)
class MethodAuthorityRecord:
    method_id:str; subject_digest:str; provenance_digest:str; states:tuple[tuple[AuthorityCoordinate,AuthorityState],...]; epoch:int; predecessor_digest:str; reasons:tuple[str,...]; digest:str
    def state(self,c):return dict(self.states)[c]
    def unsigned(self):return {'version':'P8.MethodAuthorityRecord.v1','method_id':self.method_id,'subject_digest':self.subject_digest,'provenance_digest':self.provenance_digest,'states':[[c.value,s.value] for c,s in self.states],'epoch':self.epoch,'predecessor_digest':self.predecessor_digest,'reasons':list(self.reasons)}
    def verify(self):
        if content_digest(self.unsigned())!=self.digest:raise ValueError('authority digest mismatch')

def authority_record(p:MethodProvenanceRecord):
    p.verify(); states=tuple((c,AuthorityState.CANNOT_CHECK) for c in AuthorityCoordinate);base={'version':'P8.MethodAuthorityRecord.v1','method_id':p.method_id,'subject_digest':p.subject_digest,'provenance_digest':p.digest,'states':[[c.value,s.value] for c,s in states],'epoch':1,'predecessor_digest':'','reasons':['NO_COORDINATE_AUTHORITY_YET']};return MethodAuthorityRecord(p.method_id,p.subject_digest,p.digest,states,1,'',('NO_COORDINATE_AUTHORITY_YET',),content_digest(base))

def apply_decision(record:MethodAuthorityRecord, decision:CoercionDecision):
    record.verify();decision.verify(); states=dict(record.states);states[decision.coordinate]=decision.state;ordered=tuple((c,states[c]) for c in AuthorityCoordinate);reasons=tuple((*record.reasons,f'{decision.coordinate.value}:{decision.reason}'));base={'version':'P8.MethodAuthorityRecord.v1','method_id':record.method_id,'subject_digest':record.subject_digest,'provenance_digest':record.provenance_digest,'states':[[c.value,s.value] for c,s in ordered],'epoch':record.epoch+1,'predecessor_digest':record.digest,'reasons':list(reasons)};return MethodAuthorityRecord(record.method_id,record.subject_digest,record.provenance_digest,ordered,record.epoch+1,record.digest,reasons,content_digest(base))

def p9_prediction(*,subject_digest:str,evidence_digest:str,score:float):return CapabilityOutput(CapabilityKind.P9_PREDICTION,subject_digest,evidence_digest,score,'prediction')
def p10_candidate(*,subject_digest:str,evidence_digest:str):return CapabilityOutput(CapabilityKind.P10_GENERATION,subject_digest,evidence_digest,None,'generated_candidate')

def apply_p4(record:MethodAuthorityRecord, states:Mapping[str,str], evidence_digest:str):
    out=record
    for c in (AuthorityCoordinate.VALIDITY,AuthorityCoordinate.APPLICABILITY,AuthorityCoordinate.TRANSFER,AuthorityCoordinate.UTILITY):
        if states.get(c.value)=='SUPPORTED':out=apply_decision(out,coerce(CapabilityOutput(CapabilityKind.P4_VERIFICATION,record.subject_digest,evidence_digest),c))
        elif states.get(c.value)=='BLOCKED':
            dec=coerce(CapabilityOutput(CapabilityKind.P4_VERIFICATION,record.subject_digest,evidence_digest),c); payload={'version':'P8.CoercionDecision.v1','source':dec.source.value,'coordinate':dec.coordinate.value,'state':'BLOCKED','reason':'P4_COORDINATE_BLOCKED','evidence_digest':evidence_digest};dec=CoercionDecision(dec.source,dec.coordinate,AuthorityState.BLOCKED,'P4_COORDINATE_BLOCKED',evidence_digest,content_digest(payload));out=apply_decision(out,dec)
    return out

DEFEATER_COORDS={
 DefeaterKind.HIDDEN_ASSUMPTION:(AuthorityCoordinate.APPLICABILITY,AuthorityCoordinate.TRANSFER),DefeaterKind.FRESH_COUNTEREXAMPLE:(AuthorityCoordinate.VALIDITY,AuthorityCoordinate.APPLICABILITY,AuthorityCoordinate.UTILITY),DefeaterKind.PRIOR_ART:(AuthorityCoordinate.NOVELTY,),DefeaterKind.PROTECTED_HARM:(AuthorityCoordinate.UTILITY,AuthorityCoordinate.ADOPTION),DefeaterKind.REPRESENTATION_CHANGED:(AuthorityCoordinate.APPLICABILITY,AuthorityCoordinate.TRANSFER,AuthorityCoordinate.SEARCH_STOP),DefeaterKind.SUBJECT_IDENTITY_CHANGED:tuple(AuthorityCoordinate),DefeaterKind.COMPOSITION_FOOTPRINT_CHANGED:(AuthorityCoordinate.TRANSFER,AuthorityCoordinate.UTILITY,AuthorityCoordinate.ADOPTION),DefeaterKind.EVALUATOR_CHANGED:(AuthorityCoordinate.VALIDITY,AuthorityCoordinate.UTILITY)}

def revoke(record:MethodAuthorityRecord, *, defeater:DefeaterKind,evidence_digest:str):
    record.verify();states=dict(record.states)
    for c in DEFEATER_COORDS[defeater]:states[c]=AuthorityState.BLOCKED if defeater not in {DefeaterKind.SUBJECT_IDENTITY_CHANGED,DefeaterKind.EVALUATOR_CHANGED,DefeaterKind.REPRESENTATION_CHANGED} else AuthorityState.CANNOT_CHECK
    ordered=tuple((c,states[c]) for c in AuthorityCoordinate);reasons=tuple((*record.reasons,f'DEFEATER:{defeater.value}:{evidence_digest}'));base={'version':'P8.MethodAuthorityRecord.v1','method_id':record.method_id,'subject_digest':record.subject_digest,'provenance_digest':record.provenance_digest,'states':[[c.value,s.value] for c,s in ordered],'epoch':record.epoch+1,'predecessor_digest':record.digest,'reasons':list(reasons)};return MethodAuthorityRecord(record.method_id,record.subject_digest,record.provenance_digest,ordered,record.epoch+1,record.digest,reasons,content_digest(base))
