from orion_learning_machine import *


def _trained_machine():
    lm=LearningMachine.empty()
    lm.library.register(MechanicSpec('inc','step','increment',cost=1))
    ex=[Experience('inc',{'x':float(i)},Verdict.SUCCESS,'s','D',f't{i}',0) for i in range(6)]
    lm.fit_competence(ex)
    return lm


def test_planner_respects_max_depth_exactly():
    lm=_trained_machine(); p=ExplicitPlanner(lm.library,lm.competence)
    plan=p.plan(0,lambda s,m:{'x':float(s)},lambda s,m:s+1,lambda s:s==2,max_depth=1)
    assert plan.status != Verdict.SUCCESS
    plan2=p.plan(0,lambda s,m:{'x':float(s)},lambda s,m:s+1,lambda s:s==2,max_depth=2)
    assert plan2.status == Verdict.SUCCESS and len(plan2.steps)==2


def test_planner_cycle_pruning_requires_explicit_state_identity():
    lm=_trained_machine(); p=ExplicitPlanner(lm.library,lm.competence)
    # Transition loops forever. With an explicit state key and one visit, it is pruned.
    plan=p.plan(0,lambda s,m:{'x':0.},lambda s,m:0,lambda s:False,max_depth=5,state_key=lambda s:s)
    assert plan.status in {Verdict.UNKNOWN,Verdict.FAIL}
    assert plan.steps==()
