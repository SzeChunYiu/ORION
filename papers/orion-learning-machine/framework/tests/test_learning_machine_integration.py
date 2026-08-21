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
    spec=MechanicSpec('m','stable','absorbed capability')
    lm.library.register(spec)
    rows=[Experience('m',{'x':0.},Verdict.FAIL,'s','D','t',0)]
    lm.fit_competence(rows)
    assert lm.library.resolve('m')==spec
    assert len(lm.ledger.entries)==0
    lm.record_experiences(rows)
    assert len(lm.ledger.entries)==1 and lm.ledger.verify()


def test_capability_routing_selects_supported_mechanic_without_authority():
    lm=LearningMachine.empty()
    lm.library.register(MechanicSpec('strong','route','supported'))
    lm.library.register(MechanicSpec('weak','route','unsupported'))
    rows=[]
    for i in range(6):
        rows.append(Experience('strong',{'x':float(i)},Verdict.SUCCESS,'s','D',f's{i}',0))
        rows.append(Experience('weak',{'x':float(i)},Verdict.FAIL,'s','D',f'w{i}',0))
    lm.fit_competence(rows)

    route=lm.route_capability(
        ('weak','strong'),
        {'weak':{'x':2.0},'strong':{'x':2.0}},
    )
    assert route.status==Verdict.SUCCESS
    assert route.selected_mechanic_id=='strong'
    assert route.authorizes_execution is False
    assert [a.mechanic_id for a in route.assessments]==['weak','strong']


def test_capability_routing_abstains_on_unknown_or_failure_only_evidence():
    lm=LearningMachine.empty()
    lm.library.register(MechanicSpec('m','route','bounded'))
    rows=[Experience('m',{'x':float(i)},Verdict.FAIL,'s','D',f't{i}',0) for i in range(6)]
    lm.fit_competence(rows)

    failed=lm.route_capability(('m',),{'m':{'x':2.0}})
    unknown=lm.route_capability(('m',),{'m':{'x':1000.0}})
    assert failed.selected_mechanic_id is None and failed.status==Verdict.FAIL
    assert unknown.selected_mechanic_id is None and unknown.status==Verdict.UNKNOWN
    assert failed.authorizes_execution is False and unknown.authorizes_execution is False
