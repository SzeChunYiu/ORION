from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.p8_method_authority import *
def d(x):return content_digest({'x':x})
def rec():return authority_record(provenance(method_id='m',provenance_class=ProvenanceClass.INVENTED_METHOD_CANDIDATE,subject_digest=d('s'),source_ids=('donor',),generator_id='p10',generator_version='v1',evidence_digest=d('p')))
def test_p9_and_p10_cannot_launder_authority():
    for cap in (p9_prediction(subject_digest=d('s'),evidence_digest=d('e'),score=.99),p10_candidate(subject_digest=d('s'),evidence_digest=d('e'))):
        for c in AuthorityCoordinate: assert coerce(cap,c).state is AuthorityState.BLOCKED
def test_p6_p7_do_not_authorize():
    for k in (CapabilityKind.P6_FIBRE,CapabilityKind.P7_NAVIGATION):assert coerce(CapabilityOutput(k,d('s'),d('e')),AuthorityCoordinate.TRANSFER).state is AuthorityState.BLOCKED
def test_legal_authority_is_coordinate_specific():
    assert coerce(CapabilityOutput(CapabilityKind.P4_VERIFICATION,d('s'),d('e')),AuthorityCoordinate.VALIDITY).state is AuthorityState.SUPPORTED
    assert coerce(CapabilityOutput(CapabilityKind.P4_VERIFICATION,d('s'),d('e')),AuthorityCoordinate.NOVELTY).state is AuthorityState.BLOCKED
    assert coerce(CapabilityOutput(CapabilityKind.NOVELTY_REVIEW,d('s'),d('e')),AuthorityCoordinate.NOVELTY).state is AuthorityState.SUPPORTED
    assert coerce(CapabilityOutput(CapabilityKind.NOVELTY_REVIEW,d('s'),d('e')),AuthorityCoordinate.VALIDITY).state is AuthorityState.BLOCKED
    assert coerce(CapabilityOutput(CapabilityKind.P5_HOST_ADOPTION,d('s'),d('e')),AuthorityCoordinate.ADOPTION).state is AuthorityState.SUPPORTED
def test_missing_bound_evidence_cannot_check():
    assert coerce(CapabilityOutput(CapabilityKind.P4_VERIFICATION,d('s'),''),AuthorityCoordinate.VALIDITY).state is AuthorityState.CANNOT_CHECK
def test_clean_path_requires_distinct_authorities():
    r=rec();r=apply_p4(r,{'VALIDITY':'SUPPORTED','APPLICABILITY':'SUPPORTED','TRANSFER':'SUPPORTED','UTILITY':'SUPPORTED'},d('p4'));r=apply_decision(r,coerce(CapabilityOutput(CapabilityKind.NOVELTY_REVIEW,d('s'),d('novel')),AuthorityCoordinate.NOVELTY));assert r.state(AuthorityCoordinate.ADOPTION) is AuthorityState.CANNOT_CHECK;r=apply_decision(r,coerce(CapabilityOutput(CapabilityKind.P5_HOST_ADOPTION,d('s'),d('host')),AuthorityCoordinate.ADOPTION));assert all(r.state(c) is AuthorityState.SUPPORTED for c in (AuthorityCoordinate.VALIDITY,AuthorityCoordinate.APPLICABILITY,AuthorityCoordinate.TRANSFER,AuthorityCoordinate.NOVELTY,AuthorityCoordinate.UTILITY,AuthorityCoordinate.ADOPTION))
def test_revocation_is_forward_only_and_historical_record_stays_valid():
    r=rec();r=apply_decision(r,coerce(CapabilityOutput(CapabilityKind.NOVELTY_REVIEW,d('s'),d('n')),AuthorityCoordinate.NOVELTY));old=r;new=revoke(r,defeater=DefeaterKind.PRIOR_ART,evidence_digest=d('prior'));old.verify();new.verify();assert old.state(AuthorityCoordinate.NOVELTY) is AuthorityState.SUPPORTED and new.state(AuthorityCoordinate.NOVELTY) is AuthorityState.BLOCKED and new.predecessor_digest==old.digest
def test_representation_or_identity_change_reopens_coordinates():
    r=rec();r=apply_p4(r,{'VALIDITY':'SUPPORTED','APPLICABILITY':'SUPPORTED','TRANSFER':'SUPPORTED','UTILITY':'SUPPORTED'},d('p4'));new=revoke(r,defeater=DefeaterKind.REPRESENTATION_CHANGED,evidence_digest=d('rep'));assert new.state(AuthorityCoordinate.APPLICABILITY) is AuthorityState.CANNOT_CHECK and new.state(AuthorityCoordinate.SEARCH_STOP) is AuthorityState.CANNOT_CHECK
def test_local_exhaustion_cannot_authorize_search_stop():
    assert coerce(CapabilityOutput(CapabilityKind.P7_NAVIGATION,d('s'),d('stop')),AuthorityCoordinate.SEARCH_STOP).state is AuthorityState.BLOCKED
    assert coerce(CapabilityOutput(CapabilityKind.TASK_CLOSURE,d('s'),d('external')),AuthorityCoordinate.SEARCH_STOP).state is AuthorityState.SUPPORTED
