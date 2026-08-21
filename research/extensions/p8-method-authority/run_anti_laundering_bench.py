#!/usr/bin/env python3
"""P8's anti-laundering bench: fifteen frozen coercion/revocation cases, and a terminal derived from them.

The terminal used to be the string literal ``'P8_P9_P10_ANTI_LAUNDERING_CLEAR'``
written into the emitted dict beside four computed rates, and ``claim_ceiling``
was ``panel['claim_ceiling']`` echoed back. Neither read a row, a rate or a
digest: replacing the graded authority table with one that launders every
capability into every coordinate dropped ``illicit_coercion_block_rate`` from
1.0 to 0.0 and the receipt still published ``CLEAR``
(``research/failures/2026-08-unconditional-terminal-self-issued-authority/``).

Now each of the four rates is an :class:`~orion.programme.guard_exercise.GuardExercise`
- a stated denominator and the violations against it - and the terminal is
``worst_outcome`` over the four assessments. It is three-valued, because a slice
with no cases in it has no rate: its rate is emitted as ``null`` rather than as a
division error or a 1.0, and its assessment is ``CANNOT_CHECK``, which blocks
exactly as ``FAIL`` does.

``declared_claim_ceiling_from_input`` is the old ``claim_ceiling`` under a name
that says where it came from. The run still cannot set it, so the receipt no
longer presents it as though it could.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from orion.programme.guard_exercise import GuardExercise, assess_guard, worst_outcome
from orion.programme.records import Outcome
from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.p8_method_authority import (
    AuthorityCoordinate, AuthorityState, CapabilityKind, CapabilityOutput,
    DefeaterKind, ProvenanceClass, apply_decision, authority_record,
    coerce, provenance, revoke,
)
ROOT=Path(__file__).resolve().parent
PANEL=ROOT/'P9_P10_ANTI_LAUNDERING_CASES_V1.json'
SUMMARY=ROOT/'P9_P10_ANTI_LAUNDERING_SUMMARY_V1.json'
#: One terminal per outcome. ``CANNOT_CHECK`` is not a softer ``CLEAR``: by
#: ``Outcome.blocks`` it stops a promotion exactly as ``VIOLATED`` does.
TERMINALS={Outcome.PASS:'P8_P9_P10_ANTI_LAUNDERING_CLEAR',Outcome.FAIL:'P8_P9_P10_ANTI_LAUNDERING_VIOLATED',Outcome.CANNOT_CHECK:'P8_P9_P10_ANTI_LAUNDERING_CANNOT_CHECK'}
#: The four graded slices: emitted rate field, guard id, and the denominator stated in a sentence.
SLICES=(('contract_accuracy','p8_anti_laundering_contract','every frozen case in the panel, coercion and revocation alike'),
        ('illicit_coercion_block_rate','p8_illicit_coercion_block','frozen coercion cases whose declared outcome is BLOCKED: the laundering attacks'),
        ('clean_legal_coverage','p8_clean_legal_coverage','frozen coercion cases whose declared outcome is SUPPORTED: the legal lanes that must not be broken shut'),
        ('revocation_accuracy','p8_revocation','frozen revocation cases: defeater propagation and reopening'))
#: Emitted beside the echoed ceiling so no reader can mistake it for a measured bound.
CEILING_NOTE='Echoed verbatim from the input panel\'s claim_ceiling. It is a bound this suite was handed, not one it earned; no state of the run can widen, narrow or contradict it.'
def d(x):return content_digest({'x':x})
def base_record():return authority_record(provenance(method_id='bench-method',provenance_class=ProvenanceClass.INVENTED_METHOD_CANDIDATE,subject_digest=d('subject'),source_ids=('donor',),generator_id='p10',generator_version='v1',evidence_digest=d('provenance')))
def grant_for(record,coordinate):
    source={AuthorityCoordinate.NOVELTY:CapabilityKind.NOVELTY_REVIEW,AuthorityCoordinate.ADOPTION:CapabilityKind.P5_HOST_ADOPTION,AuthorityCoordinate.SEARCH_STOP:CapabilityKind.TASK_CLOSURE}.get(coordinate,CapabilityKind.P4_VERIFICATION)
    return apply_decision(record,coerce(CapabilityOutput(source,record.subject_digest,d('grant:'+coordinate.value)),coordinate))
def evaluate(case):
    coordinate=AuthorityCoordinate(case['coordinate'])
    if case['kind']=='coercion':
        return coerce(CapabilityOutput(CapabilityKind(case['source']),d('subject'),d('case:'+case['id'])),coordinate).state.value
    record=grant_for(base_record(),coordinate)
    return revoke(record,defeater=DefeaterKind(case['defeater']),evidence_digest=d('defeater:'+case['id'])).state(coordinate).value
def exercise_for(guard_id,rows,definition,protocol_id):
    """One slice as a stated denominator and the cases that failed against it."""
    return GuardExercise(guard_id=guard_id,arm_id=protocol_id,opportunities=len(rows),violations=sum(1 for r in rows if not r['pass']),opportunity_definition=definition)
def rate_of(rows):
    """The pass rate over a slice, or ``None`` when the slice is empty.

    ``None`` and not 1.0: a slice with no cases in it did not score perfectly, it
    did not score. The terminal reads the assessments below, never this value, so
    an absent rate cannot be mistaken for a clean one on the way to a verdict.
    """
    return sum(r['pass'] for r in rows)/len(rows) if rows else None
def run(panel):
    rows=[]
    for case in panel['cases']:
        actual=evaluate(case);rows.append({'id':case['id'],'kind':case['kind'],'expected':case['expected'],'actual':actual,'pass':actual==case['expected']})
    attacks=[r for r in rows if r['kind']=='coercion' and r['expected']=='BLOCKED'];clean=[r for r in rows if r['kind']=='coercion' and r['expected']=='SUPPORTED'];rev=[r for r in rows if r['kind']=='revocation']
    slices=dict(zip((name for name,_guard,_definition in SLICES),(rows,attacks,clean,rev)))
    exercises=[(name,exercise_for(guard,slices[name],definition,panel['protocol_id'])) for name,guard,definition in SLICES]
    assessments=[(name,assess_guard(exercise)) for name,exercise in exercises]
    terminal=TERMINALS[worst_outcome(tuple(assessment for _name,assessment in assessments))]
    basis=[{'rate_field':name,'guard_id':assessment.guard_id,'opportunity_definition':exercise.opportunity_definition,'opportunities':exercise.opportunities,'violations':exercise.violations,'rate':rate_of(slices[name]),'outcome':assessment.outcome.value,'reason':assessment.reason.value}
           for (name,exercise),(_name,assessment) in zip(exercises,assessments)]
    out={'result_version':'P8_P9_P10_ANTI_LAUNDERING_SUMMARY_V1','protocol_id':panel['protocol_id'],'panel_digest':content_digest(panel),'n_cases':len(rows),'contract_accuracy':rate_of(rows),'illicit_coercion_block_rate':rate_of(attacks),'clean_legal_coverage':rate_of(clean),'revocation_accuracy':rate_of(rev),'rows':rows,'terminal':terminal,'terminal_basis':basis,'declared_claim_ceiling_from_input':panel['claim_ceiling'],'declared_claim_ceiling_note':CEILING_NOTE}
    out['result_digest']=content_digest(out);return out
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--check',action='store_true');a=ap.parse_args();out=run(json.loads(PANEL.read_text()));text=json.dumps(out,indent=2,sort_keys=True)+'\n'
    if a.write:SUMMARY.write_text(text)
    if a.check and (not SUMMARY.exists() or SUMMARY.read_text()!=text):raise SystemExit('P8 anti-laundering summary drift')
    if not a.write and not a.check:print(text,end='')
if __name__=='__main__':main()
