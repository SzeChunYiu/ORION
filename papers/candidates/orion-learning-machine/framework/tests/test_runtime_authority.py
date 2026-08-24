from orion_learning_machine import *

def test_authority_blocks_capability_without_execution():
    called=[]
    def exe(state):
        called.append(True); return ExecutionResult(Verdict.SUCCESS,state+1,'m')
    lm=LearningMachine.empty(); lm.library.register(MechanicSpec('m','f','d',executor=exe))
    plan=SolverPlan((PlanStep('m',1,1,'test'),),1,1,Verdict.SUCCESS)
    run=lm.execute_plan(plan,0,lambda s,m: Verdict.UNAUTHORIZED)
    assert run.verdict==Verdict.UNAUTHORIZED and not called

def test_authorized_execution_attaches_provenance():
    p=Provenance('D','s')
    def exe(state): return ExecutionResult(Verdict.SUCCESS,state+1,'m')
    lm=LearningMachine.empty(); lm.library.register(MechanicSpec('m','f','d',provenance=(p,),executor=exe))
    plan=SolverPlan((PlanStep('m',1,1,'test'),),1,1,Verdict.SUCCESS)
    run=lm.execute_plan(plan,0,lambda s,m: Verdict.SUCCESS)
    assert run.verdict==Verdict.SUCCESS and run.final_state==1 and run.results[0].provenance==(p,)
