from orion_learning_machine import TransitionObservation, TransitionContractInducer, Verdict


def test_contract_induction_is_empirical_and_unknown_when_sparse():
    rows=[
      TransitionObservation('rw',{'target':'eq'},'one_goal','D','s1','t1'),
      TransitionObservation('rw',{'target':'eq'},'one_goal','D2','s2','t2'),
      TransitionObservation('rare',{'target':'eq'},'closed','D','s3','t3'),
    ]
    m=TransitionContractInducer(min_support=2).fit(rows)
    c=m.get('rw')
    assert c.modal_effect=='one_goal' and set(c.donors)=={'D','D2'}
    assert m.predict_effect('rare')==(Verdict.UNKNOWN,None)
    assert m.predict_effect('missing')==(Verdict.UNKNOWN,None)
