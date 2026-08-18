from dataclasses import replace
import pytest
from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.p6_method_fibres import *

def d(x): return content_digest({'x':x})
def r(name='a',**kw):
    x=dict(realization_id=name,source_digest=d(name),preconditions=('finite',),actions=('a','b'),dependencies=(('a','b'),),invariants=('safe',),effects=('reduce',),termination='rank',reconstruction='lift',failures=('stuck',),lineage=(name,)); x.update(kw); return MethodRealizationView(**x)
def sig(rr=None):
    rr=rr or r(); red=build_reduction(rr,reduction_id='red',claim_id='claim',preserved=('preconditions','invariants','effects','reconstruction'),erased=('actions','dependencies','termination','failures','lineage'),load_bearing=('preconditions','invariants','effects','reconstruction'),justifications={'actions':'surface','dependencies':'schedule','termination':'local','failures':'out','lineage':'retained externally'}); return rr,red,build_signature(rr,red)
def m(s,rr,**kw):
    x=dict(assumptions=True,invariants=True,effects=True,reconstruction=True,provenance=True,beyond_single_panel=True);x.update(kw);return assess_membership(s,rr,membership_evidence(s,rr,**x))

def test_claim_relative_digest_and_no_authority():
    rr,red,s=sig(); red.verify();s.verify(); assert s.unsigned()['can_authorize_transfer'] is False
    with pytest.raises(ValueError): replace(red,claim_id='other').verify()
def test_surface_same_different_precondition_blocked():
    _,_,s=sig(); assert m(s,r('b',preconditions=('continuous',)),assumptions=False).status is FibreStatus.BLOCKED
def test_one_panel_is_unresolved():
    _,_,s=sig(); q=m(s,r('b'),beyond_single_panel=False); assert q.status is FibreStatus.UNRESOLVED and 'ONE_PANEL' in q.reasons[0]
def test_load_bearing_erasure_needs_evidence():
    rr=r(); red=build_reduction(rr,reduction_id='x',claim_id='x',preserved=('effects',),erased=('preconditions',),load_bearing=('preconditions',),justifications={'preconditions':'hypothesis'}); assert build_signature(rr,red).state is ReductionState.UNRESOLVED; assert build_signature(rr,red,erasure_evidence={'preconditions':False}).state is ReductionState.OBSTRUCTION
def test_unknown_preserved_stays_unresolved():
    rr=r(unknown_coordinates=('reconstruction',)); _,red,_=sig(rr); assert build_signature(rr,red).state is ReductionState.UNRESOLVED
def test_fibre_retains_members_and_unknowns():
    rr,_,s=sig(); b=r('b'); u=r('u'); f=build_fibre(s,[m(s,rr),m(s,b),m(s,u,provenance=None)]); assert set(f.members)=={rr.digest,b.digest} and f.unresolved==(u.digest,)
def test_composition_traps_and_clean_case():
    base=dict(right_preconditions=('ready',),left_guarantees=('ready',),required_dependencies=('m',),declared_dependencies=('m',),emitted_authorities=('local',),permitted_authorities=('local',))
    assert check_composition(CompositionContract(CompositionKind.SEQUENTIAL,**base))[0] is CompositionStatus.COMPATIBLE
    assert check_composition(CompositionContract(CompositionKind.PARALLEL,left_write=('x',),right_read=('x',),**base))[0] is CompositionStatus.BLOCKED
    assert check_composition(CompositionContract(CompositionKind.SEQUENTIAL,emitted_authorities=('adopt',),permitted_authorities=(),right_preconditions=('ready',),left_guarantees=('ready',)))[0] is CompositionStatus.BLOCKED
    assert check_composition(CompositionContract(CompositionKind.RECURSIVE,rank_decreases=False))[0] is CompositionStatus.BLOCKED
    assert check_composition(CompositionContract(CompositionKind.RECURSIVE,rank_decreases=None))[0] is CompositionStatus.UNRESOLVED
def test_direction_and_reconstruction():
    assert relation(base_preconditions=('finite',),candidate_preconditions=('finite','acyclic'),base_effects=('solve',),candidate_effects=('solve',),requested=StructuralRelation.SPECIALIZES,obligations_satisfied=True) is StructuralRelation.SPECIALIZES
    assert relation(base_preconditions=('finite',),candidate_preconditions=('finite','acyclic'),base_effects=('solve',),candidate_effects=('solve',),requested=StructuralRelation.EQUIVALENT,obligations_satisfied=True) is StructuralRelation.UNRESOLVED
    assert representation_lift(True) is ReductionState.SUPPORTED and representation_lift(False) is ReductionState.OBSTRUCTION and representation_lift(None) is ReductionState.UNRESOLVED
