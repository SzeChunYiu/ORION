from orion_learning_machine import *
from orion_learning_machine.adapters.lean_source import parse_lean_source, tactic_family

def test_provenance_merge_preserves_donors():
    lib=MechanicLibrary()
    lib.register(MechanicSpec('m','rewrite','x',provenance=(Provenance('A','a'),)))
    lib.register(MechanicSpec('m','rewrite','x',provenance=(Provenance('B','b'),)))
    assert {p.donor for p in lib.resolve('m').provenance} == {'A','B'}

def test_unknown_is_not_negative():
    ex=[]
    for i in range(12):
        ex.append(Experience('m',{'x':float(i)/10},Verdict.SUCCESS if i<6 else Verdict.FAIL,'s','d',f't{i}',0))
    c=CompetenceMap(min_evidence=2).fit(ex)
    near=c.estimate('m',{'x':.2})
    far=c.estimate('m',{'x':100.})
    assert near.status in {Verdict.SUCCESS,Verdict.FAIL}
    assert far.status == Verdict.UNKNOWN

def test_macro_requires_cross_source():
    ts=[
        {'trajectory_id':'a','donor':'d1','source_id':'s1','mechanics':['rewrite','simplify','apply']},
        {'trajectory_id':'b','donor':'d2','source_id':'s2','mechanics':['rewrite','simplify','cases']},
        {'trajectory_id':'c','donor':'d3','source_id':'s3','mechanics':['rewrite','simplify','apply']},
    ]
    ms=mine_macros(ts,min_support=3)
    assert any(m.sequence==('rewrite','simplify') for m in ms)

def test_residual_invention_gate():
    rows=[{'verdict':'fail','residual_signature':['needs_transport'],'source_id':f's{i%3}'} for i in range(6)]
    r=residual_clusters(rows,min_count=5,min_sources=3)[0]
    assert r.eligible_for_invention

def test_lean_parser_conservative():
    src='''lemma foo (a b : ℝ) (h : a=b) : b=a := by\n  rw [h]\n  simp\n\nlemma bar (P : Prop) (h:P) : P := by\n  exact h\n'''
    th=parse_lean_source(src,'toy.lean')
    assert [x.tactics for x in th] == [('rewrite','simplify'),('apply',)]
    assert tactic_family('custom_tactic') == 'unknown'
