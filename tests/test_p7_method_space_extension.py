from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.p7_method_space import *
def d(x):return content_digest({'x':x})
def chart(edges=()):return build_chart(chart_id='c',subject_digest=d('s'),construction_rule='bounded',signature_digests=(d('a'),),edges=edges,route_ids=('r1','r2'),source_families=('f1',),unknown_boundary=('outside-chart',),noncoverage=('future-methods',),reopen_triggers=('new-route',))
def test_local_stops_remain_open():
    c=chart()
    for scope in (StopScope.ROUTE,StopScope.CHART,StopScope.KNOWN_LIBRARY):
        x=stop(c,scope=scope,reason='bounded');assert x.task_terminal=='OPEN' and x.global_method_space_open
def test_task_stop_requires_external_authority():
    c=chart()
    try: stop(c,scope=StopScope.TASK,reason='x')
    except ValueError: pass
    else: raise AssertionError
    x=stop(c,scope=StopScope.TASK,reason='verified',task_closable=True,external_authority_digest=d('authority'));assert x.task_terminal=='CLOSED'
def test_representation_change_requires_reconstruction():
    e=MethodChartEdge(d('a'),d('b'),EdgeKind.REPRESENTATION_CHANGE,d('p'),'reframe',True,False);c=chart((e,));assert record_event(c,e,event_id='e',evidence_digest=d('ev')).state is NavState.BLOCKED
    e2=MethodChartEdge(d('a'),d('c'),EdgeKind.REPRESENTATION_CHANGE,d('p2'),'reframe',True,True);assert record_event(build_chart(chart_id='c2',subject_digest=d('s'),construction_rule='x',signature_digests=(d('a'),),edges=(e2,)),e2,event_id='e2',evidence_digest=d('ev2')).state is NavState.AVAILABLE
def test_invention_only_after_required_routes_and_never_authorizes():
    c=chart();assert not propose_invention(c,attempted_route_ids=('r1',),required_route_ids=('r1','r2')).eligible
    x=propose_invention(c,attempted_route_ids=('r1','r2'),required_route_ids=('r1','r2'));assert x.eligible and not x.can_authorize_invention
def test_reopen_invalidates_stale_chart_identity():
    c=chart();n=reopen_chart(c,new_signature_digest=d('new'));assert n.epoch==2 and n.digest!=c.digest and d('new') in n.signature_digests
def test_revisit_requires_new_evidence():
    e=MethodChartEdge(d('a'),d('b'),EdgeKind.METHOD_NEIGHBOR,d('p'),'try');c=chart((e,));evt=record_event(c,e,event_id='1',evidence_digest=d('ev'));l=RevisitLedger();assert l.allow(evt) and not l.allow(evt)
def test_semantic_distance_has_no_status():
    e=MethodChartEdge(d('a'),d('far'),EdgeKind.STRUCTURAL_ANALOGY_ROUTE,d('p'),'candidate only');evt=record_event(chart((e,)),e,event_id='x',evidence_digest=d('ev'));assert evt.state is NavState.AVAILABLE and evt.unsigned()['can_authorize_transfer'] is False
