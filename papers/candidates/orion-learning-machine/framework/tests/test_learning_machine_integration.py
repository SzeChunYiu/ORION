from orion_learning_machine import *


def test_transition_absorption_preserves_donors_and_empirical_effects():
    lm=LearningMachine.empty()
    rows=[
        TransitionObservation('simp',{'goals_before':'1'},'closed','A','a','ta'),
        TransitionObservation('simp',{'goals_before':'1'},'closed','B','b','tb'),
    ]
    contracts=lm.absorb_transition_observations(rows,min_support=2)
    assert len(contracts)==1 and contracts[0].modal_effect=='closed'
    spec=lm.library.resolve('simp')
    assert {p.donor for p in spec.provenance}=={'A','B'}
    assert set(spec.protected_traits)=={'A:observed_effect=closed','B:observed_effect=closed'}


def test_absorbed_transition_does_not_self_authorize():
    lm=LearningMachine.empty()
    lm.absorb_transition_observations([
        TransitionObservation('simp',{},'closed','A','a','ta'),
        TransitionObservation('simp',{},'closed','B','b','tb'),
    ])
    plan=SolverPlan((PlanStep('simp',1,1,'empirical'),),1,1,Verdict.SUCCESS)
    run=lm.execute_plan(plan,{'goals':1},lambda s,m: Verdict.UNAUTHORIZED)
    assert run.verdict==Verdict.UNAUTHORIZED


def test_recording_experience_is_append_only_and_separate_from_fitting():
    lm=LearningMachine.empty()
    rows=[Experience('m',{'x':0.},Verdict.FAIL,'s','D','t',0)]
    lm.fit_competence(rows)
    assert len(lm.ledger.entries)==0
    lm.record_experiences(rows)
    assert len(lm.ledger.entries)==1 and lm.ledger.verify()
