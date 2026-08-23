import pytest
from orion_learning_machine import MechanicLibrary, MechanicSpec, Provenance, mine_macros


def test_same_id_cannot_launder_different_preconditions_or_cost():
    lib=MechanicLibrary()
    lib.register(MechanicSpec('m','rewrite','donor A',cost=1,prerequisites=('eq',),compatibility_key='rw-v1'))
    with pytest.raises(ValueError):
        lib.register(MechanicSpec('m','rewrite','donor B',cost=2,prerequisites=('eq',),compatibility_key='rw-v1'))
    with pytest.raises(ValueError):
        lib.register(MechanicSpec('m','rewrite','donor C',cost=1,prerequisites=('ring',),compatibility_key='rw-v1'))
    with pytest.raises(ValueError):
        lib.register(MechanicSpec('m','rewrite','donor D',cost=1,prerequisites=('eq',),compatibility_key='rw-v2'))


def test_protected_traits_survive_generalization():
    lib=MechanicLibrary()
    lib.register(MechanicSpec('m','rewrite','canonical',protected_traits=('A:cheap-on-equalities',),provenance=(Provenance('A','a'),)))
    lib.register(MechanicSpec('m','rewrite','canonical',protected_traits=('B:handles-directed-rules',),provenance=(Provenance('B','b'),)))
    m=lib.resolve('m')
    assert set(m.protected_traits)=={'A:cheap-on-equalities','B:handles-directed-rules'}
    assert {p.donor for p in m.provenance}=={'A','B'}


def test_cross_donor_macro_gate():
    rows=[
      {'trajectory_id':'a','donor':'A','source_id':'a','mechanics':['x','y','z']},
      {'trajectory_id':'b','donor':'A','source_id':'b','mechanics':['x','y']},
      {'trajectory_id':'c','donor':'B','source_id':'c','mechanics':['x','y']},
    ]
    m=mine_macros(rows,min_support=3,require_multi_donor=True)
    xy=next(x for x in m if x.sequence==('x','y'))
    assert xy.donors==('A','B')
    assert xy.source_ids==('a','b','c')
