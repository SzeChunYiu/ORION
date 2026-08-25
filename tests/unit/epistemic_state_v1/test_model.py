from dataclasses import replace
from fractions import Fraction
import pytest
from orion.epistemic_state_v1.model import *

def c(value,status=Status.KNOWN,epoch=0): return Coordinate(value,status,"unit",epoch,("r",),"v1")
def state(subject="s"):
    return State(subject,"PROMOTE",0,c(Fraction(9,10)),c(True),c(Fraction(4,5)),frozenset({"o1","o2"}),frozenset({"o1","o2"}),c(True),c(True),frozenset({"PROMOTE"}),(SupportFamily("f",frozenset({"p"}),frozenset({"o1","o2"})),),frozenset(),True,frozenset({"m"}),frozenset({"n"}),frozenset({"e"}))

def test_noncompensatory_projection():
    p=promotion_policy("PROMOTE"); s=state(); assert p.project(s) is Terminal.ADMISSIBLE
    assert p.project(replace(s,evidence=c(1),identifiability=c(False))) is Terminal.BLOCKED
    assert p.project(replace(s,custody_external=False)) is Terminal.CANNOT_CHECK

def test_event_idempotence_and_replay():
    s=state(); e=Event("e1","s","replication","abc",1,{"evidence":c(Fraction(19,20),epoch=1)})
    once=apply_event(s,e); assert apply_event(once,e)==once; assert replay(s,[e,e])==once

def test_event_guards():
    with pytest.raises(ValueError): apply_event(state(),Event("e","other","x","d",1,{}))
    with pytest.raises(ValueError): apply_event(state(),Event("e","s","x","d",1,{"magic_score":1}))

def test_revocation_preserves_alternative_support():
    fs=(SupportFamily("a",frozenset({"p1"}),frozenset({"o"})),SupportFamily("b",frozenset({"p2"}),frozenset({"o"})))
    assert [x.family_id for x in revocation_survivors(fs,{"p1"})]==["b"]

def test_legacy_inverse_is_set_valued():
    p=promotion_policy("PROMOTE"); a=replace(state("a"),custody_external=False); b=replace(state("b"),custody_external=False)
    assert len(compatible_states((a,b),p,Terminal.CANNOT_CHECK))==2

def test_pareto_keeps_tradeoffs_and_removes_dominated():
    a=ResearchAction("a",Action.SEARCH_LOCAL,GainVector(coverage=Fraction(1,3),cost=ResourceVector(acquisition=1)),"near",True)
    b=ResearchAction("b",Action.DISCRIMINATE,GainVector(identifiability=1,cost=ResourceVector(acquisition=3)),"near",True)
    d=ResearchAction("d",Action.SEARCH_LOCAL,GainVector(coverage=Fraction(1,4),cost=ResourceVector(acquisition=2)),"near",True)
    assert {x.action_id for x in pareto((a,b,d))}=={"a","b"}

def test_remote_jump_requires_saturation_and_open_obligation():
    s=replace(state(),obligations_satisfied=frozenset({"o1"}))
    local=ResearchAction("l",Action.SEARCH_LOCAL,GainVector(cost=ResourceVector(acquisition=1)),"near",True)
    remote=ResearchAction("r",Action.SEARCH_REMOTE_STRUCTURE,GainVector(obligation=1,cost=ResourceVector(acquisition=2)),"music",False)
    assert local_saturated((local,remote)); assert should_jump(s,(local,remote)); assert not should_jump(state(),(local,remote))
