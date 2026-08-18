from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence
from .canonical import content_digest

class ReductionState(str, Enum):
    SUPPORTED='SUPPORTED'; OBSTRUCTION='OBSTRUCTION'; UNRESOLVED='UNRESOLVED'
class FibreStatus(str, Enum):
    MEMBER='MEMBER'; BLOCKED='BLOCKED'; UNRESOLVED='UNRESOLVED'
class CompositionKind(str, Enum):
    SEQUENTIAL='SEQUENTIAL'; CONDITIONAL='CONDITIONAL'; PARALLEL='PARALLEL'; RECURSIVE='RECURSIVE'
class CompositionStatus(str, Enum):
    COMPATIBLE='COMPATIBLE'; BLOCKED='BLOCKED'; UNRESOLVED='UNRESOLVED'
class StructuralRelation(str, Enum):
    EQUIVALENT='EQUIVALENT_FOR_CLAIM'; SPECIALIZES='SPECIALIZES'; GENERALIZES='GENERALIZES'; UNRESOLVED='UNRESOLVED'

COORDS=('preconditions','actions','dependencies','invariants','effects','termination','reconstruction','failures','lineage')

@dataclass(frozen=True)
class MethodRealizationView:
    realization_id:str; source_digest:str
    preconditions:tuple[str,...]=(); actions:tuple[str,...]=(); dependencies:tuple[tuple[str,str],...]=()
    invariants:tuple[str,...]=(); effects:tuple[str,...]=(); termination:str|None=None
    reconstruction:str|None=None; failures:tuple[str,...]=(); lineage:tuple[str,...]=(); unknown_coordinates:tuple[str,...]=()
    def __post_init__(self):
        if not self.realization_id or not self.source_digest.startswith('sha256:'): raise ValueError('invalid realization identity')
    def payload(self):
        return {'schema':'P6.MethodRealizationView.v1','realization_id':self.realization_id,'source_digest':self.source_digest,
                'preconditions':list(self.preconditions),'actions':list(self.actions),'dependencies':[list(x) for x in self.dependencies],
                'invariants':list(self.invariants),'effects':list(self.effects),'termination':self.termination,'reconstruction':self.reconstruction,
                'failures':list(self.failures),'lineage':list(self.lineage),'unknown_coordinates':list(self.unknown_coordinates),'authority_scope':'FORMAL_STRUCTURE_ONLY'}
    @property
    def digest(self): return content_digest(self.payload())
    @classmethod
    def from_mapping(cls, *, realization_id:str, source_digest:str, payload:Mapping[str,object]):
        def seq(*keys):
            for k in keys:
                if k in payload:
                    v=payload[k]
                    if v is None:return ()
                    if not isinstance(v,(list,tuple,set,frozenset)):raise ValueError(k)
                    return tuple(sorted(map(str,v)))
            return ()
        raw=payload.get('dependencies',payload.get('dependency_edges',())) or (); deps=[]
        for e in raw:
            if not isinstance(e,(list,tuple)) or len(e)!=2: raise ValueError('dependency edge')
            deps.append((str(e[0]),str(e[1])))
        t=payload.get('termination',payload.get('terminal_condition')); r=payload.get('reconstruction',payload.get('reconstruction_map'))
        return cls(realization_id,source_digest,seq('preconditions','assumptions'),seq('actions','mechanics'),tuple(sorted(deps)),seq('invariants','protected_properties'),seq('effects','effect_contract'),None if t is None else str(t),None if r is None else str(r),seq('failures','failure_modes'),seq('lineage','provenance'),seq('unknown_coordinates','unknowns'))

@dataclass(frozen=True)
class StructuralReduction:
    reduction_id:str; claim_id:str; realization_digest:str; preserved:tuple[str,...]; erased:tuple[str,...]; load_bearing:tuple[str,...]; unresolved:tuple[str,...]; obligations:tuple[str,...]; justifications:tuple[tuple[str,str],...]; digest:str
    def unsigned(self): return {'version':'StructuralReduction.v1','reduction_id':self.reduction_id,'claim_id':self.claim_id,'realization_digest':self.realization_digest,'preserved':list(self.preserved),'erased':list(self.erased),'load_bearing':list(self.load_bearing),'unresolved':list(self.unresolved),'obligations':list(self.obligations),'justifications':[list(x) for x in self.justifications],'authority_scope':'CLAIM_RELATIVE_FORMAL_REDUCTION_ONLY'}
    def verify(self):
        groups=[set(self.preserved),set(self.erased),set(self.unresolved)]
        if any(a&b for i,a in enumerate(groups) for b in groups[i+1:]): raise ValueError('overlapping coordinates')
        if not set().union(*groups,set(self.load_bearing))<=set(COORDS): raise ValueError('unknown coordinate')
        if set(dict(self.justifications))!=set(self.erased): raise ValueError('erasure justification missing')
        if content_digest(self.unsigned())!=self.digest: raise ValueError('reduction digest mismatch')

def build_reduction(r:MethodRealizationView, *, reduction_id:str, claim_id:str, preserved:Sequence[str], erased:Sequence[str]=(), load_bearing:Sequence[str]=(), unresolved:Sequence[str]=(), obligations:Sequence[str]=(), justifications:Mapping[str,str]|None=None):
    j=justifications or {}; base={'version':'StructuralReduction.v1','reduction_id':reduction_id,'claim_id':claim_id,'realization_digest':r.digest,'preserved':sorted(set(preserved)),'erased':sorted(set(erased)),'load_bearing':sorted(set(load_bearing)),'unresolved':sorted(set(unresolved)),'obligations':sorted(set(obligations)),'justifications':[[k,str(j[k])] for k in sorted(j)],'authority_scope':'CLAIM_RELATIVE_FORMAL_REDUCTION_ONLY'}
    out=StructuralReduction(reduction_id,claim_id,r.digest,tuple(base['preserved']),tuple(base['erased']),tuple(base['load_bearing']),tuple(base['unresolved']),tuple(base['obligations']),tuple((x[0],x[1]) for x in base['justifications']),content_digest(base)); out.verify(); return out

@dataclass(frozen=True)
class StructuralSignature:
    claim_id:str; reduction_digest:str; realization_digest:str; values:tuple[tuple[str,object],...]; state:ReductionState; reasons:tuple[str,...]; digest:str
    def unsigned(self): return {'version':'StructuralSignature.v1','claim_id':self.claim_id,'reduction_digest':self.reduction_digest,'realization_digest':self.realization_digest,'values':[[k,v] for k,v in self.values],'state':self.state.value,'reasons':list(self.reasons),'can_authorize_transfer':False,'can_claim_novelty':False}
    def verify(self):
        if content_digest(self.unsigned())!=self.digest: raise ValueError('signature digest mismatch')

def build_signature(r:MethodRealizationView, red:StructuralReduction, *, erasure_evidence:Mapping[str,bool|None]|None=None):
    red.verify(); ev=erasure_evidence or {}; reasons=[]; state=ReductionState.SUPPORTED
    for c in red.preserved:
        if c in r.unknown_coordinates: state=ReductionState.UNRESOLVED; reasons.append(f'PRESERVED_UNKNOWN:{c}')
    for c in set(red.erased)&set(red.load_bearing):
        if ev.get(c) is False: state=ReductionState.OBSTRUCTION; reasons.append(f'LOAD_BEARING_ERASURE_FAILED:{c}')
        elif ev.get(c) is not True and state is not ReductionState.OBSTRUCTION: state=ReductionState.UNRESOLVED; reasons.append(f'LOAD_BEARING_ERASURE_UNRESOLVED:{c}')
    vals=tuple((c,getattr(r,c)) for c in red.preserved); base={'version':'StructuralSignature.v1','claim_id':red.claim_id,'reduction_digest':red.digest,'realization_digest':r.digest,'values':[[k,v] for k,v in vals],'state':state.value,'reasons':sorted(reasons),'can_authorize_transfer':False,'can_claim_novelty':False}
    s=StructuralSignature(red.claim_id,red.digest,r.digest,vals,state,tuple(sorted(reasons)),content_digest(base)); s.verify(); return s

@dataclass(frozen=True)
class MembershipEvidence:
    signature_digest:str; realization_digest:str; assumptions:bool|None; invariants:bool|None; effects:bool|None; reconstruction:bool|None; provenance:bool|None; beyond_single_panel:bool|None; digest:str
    def unsigned(self): return {'version':'P6.FibreMembershipEvidence.v1','signature_digest':self.signature_digest,'realization_digest':self.realization_digest,'assumptions':self.assumptions,'invariants':self.invariants,'effects':self.effects,'reconstruction':self.reconstruction,'provenance':self.provenance,'beyond_single_panel':self.beyond_single_panel}
    def verify(self):
        if content_digest(self.unsigned())!=self.digest: raise ValueError('membership evidence digest mismatch')

def membership_evidence(s,r,**kw):
    base={'version':'P6.FibreMembershipEvidence.v1','signature_digest':s.digest,'realization_digest':r.digest,**kw}; return MembershipEvidence(s.digest,r.digest,kw['assumptions'],kw['invariants'],kw['effects'],kw['reconstruction'],kw['provenance'],kw['beyond_single_panel'],content_digest(base))

@dataclass(frozen=True)
class FibreMembership:
    signature_digest:str; realization_digest:str; evidence_digest:str; status:FibreStatus; reasons:tuple[str,...]

def assess_membership(s:StructuralSignature,r:MethodRealizationView,e:MembershipEvidence):
    s.verify();e.verify(); fields={'ASSUMPTIONS':e.assumptions,'INVARIANTS':e.invariants,'EFFECTS':e.effects,'RECONSTRUCTION':e.reconstruction,'PROVENANCE':e.provenance}
    false=[f'{k}_MISMATCH' for k,v in fields.items() if v is False]
    unknown=[f'{k}_UNRESOLVED' for k,v in fields.items() if v is None]
    if false: st=FibreStatus.BLOCKED; reasons=false
    elif unknown or e.beyond_single_panel is None: st=FibreStatus.UNRESOLVED; reasons=unknown+([] if e.beyond_single_panel is not None else ['PANEL_SCOPE_UNRESOLVED'])
    elif e.beyond_single_panel is False: st=FibreStatus.UNRESOLVED; reasons=['ONE_PANEL_EFFECT_COINCIDENCE_INSUFFICIENT']
    elif s.state is not ReductionState.SUPPORTED: st=FibreStatus.UNRESOLVED; reasons=['SIGNATURE_NOT_SUPPORTED']
    else: st=FibreStatus.MEMBER; reasons=[]
    return FibreMembership(s.digest,r.digest,e.digest,st,tuple(sorted(reasons)))

@dataclass(frozen=True)
class MethodFibre:
    signature_digest:str; members:tuple[str,...]; unresolved:tuple[str,...]; evidence_digests:tuple[str,...]; digest:str

def build_fibre(s:StructuralSignature, receipts:Sequence[FibreMembership]):
    members=tuple(sorted(x.realization_digest for x in receipts if x.status is FibreStatus.MEMBER)); unresolved=tuple(sorted(x.realization_digest for x in receipts if x.status is FibreStatus.UNRESOLVED)); evid=tuple(sorted(x.evidence_digest for x in receipts)); base={'version':'MethodFibre.v1','signature_digest':s.digest,'members':list(members),'unresolved':list(unresolved),'evidence_digests':list(evid),'authority_scope':'FORMAL_EQUIVALENCE_FOR_DECLARED_CLAIM_ONLY'}; return MethodFibre(s.digest,members,unresolved,evid,content_digest(base))

@dataclass(frozen=True)
class CompositionContract:
    kind:CompositionKind; left_read:tuple[str,...]=(); left_write:tuple[str,...]=(); right_read:tuple[str,...]=(); right_write:tuple[str,...]=(); allowed_collisions:tuple[str,...]=(); right_preconditions:tuple[str,...]=(); left_guarantees:tuple[str,...]=(); required_dependencies:tuple[str,...]=(); declared_dependencies:tuple[str,...]=(); emitted_authorities:tuple[str,...]=(); permitted_authorities:tuple[str,...]=(); rank_decreases:bool|None=True

def check_composition(c:CompositionContract):
    reasons=[]; unknown=[]
    if c.kind is CompositionKind.PARALLEL:
        collisions=(set(c.left_write)&(set(c.right_read)|set(c.right_write))) | (set(c.right_write)&set(c.left_read)); collisions-=set(c.allowed_collisions)
        reasons += [f'READ_WRITE_COLLISION:{x}' for x in sorted(collisions)]
    if c.kind in (CompositionKind.SEQUENTIAL,CompositionKind.CONDITIONAL): reasons += [f'RIGHT_PRECONDITION_NOT_GUARANTEED:{x}' for x in sorted(set(c.right_preconditions)-set(c.left_guarantees))]
    reasons += [f'HIDDEN_DEPENDENCY:{x}' for x in sorted(set(c.required_dependencies)-set(c.declared_dependencies))]
    reasons += [f'AUTHORITY_ESCALATION:{x}' for x in sorted(set(c.emitted_authorities)-set(c.permitted_authorities))]
    if c.kind is CompositionKind.RECURSIVE:
        if c.rank_decreases is False: reasons.append('RECURSIVE_RANK_NOT_DECREASING')
        elif c.rank_decreases is None: unknown.append('RECURSIVE_WELL_FOUNDEDNESS_UNRESOLVED')
    return CompositionStatus.BLOCKED if reasons else (CompositionStatus.UNRESOLVED if unknown else CompositionStatus.COMPATIBLE), tuple(reasons+unknown)

def relation(*, base_preconditions:Sequence[str], candidate_preconditions:Sequence[str], base_effects:Sequence[str], candidate_effects:Sequence[str], requested:StructuralRelation, obligations_satisfied:bool|None):
    bp,cp,be,ce=map(set,(base_preconditions,candidate_preconditions,base_effects,candidate_effects))
    if obligations_satisfied is not True:return StructuralRelation.UNRESOLVED
    if requested is StructuralRelation.SPECIALIZES and bp<=cp and be<=ce:return requested
    if requested is StructuralRelation.GENERALIZES and cp<=bp and be<=ce:return requested
    if requested is StructuralRelation.EQUIVALENT and bp==cp and be==ce:return requested
    return StructuralRelation.UNRESOLVED

def representation_lift(reconstruction_valid:bool|None):
    return ReductionState.SUPPORTED if reconstruction_valid is True else (ReductionState.OBSTRUCTION if reconstruction_valid is False else ReductionState.UNRESOLVED)
