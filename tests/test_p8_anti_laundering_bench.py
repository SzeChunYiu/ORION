"""The P8 anti-laundering suite, and the terminal it now has to earn.

Before 2026-08-21 the last assertion here compared the literal
``'P8_P9_P10_ANTI_LAUNDERING_CLEAR'`` in this file against the same literal in
the emitter's dict display, with no run in between: the four rates were
computed, the terminal was not, and every panel below would have produced it.
The terminal is now ``worst_outcome`` over four ``GuardExercise`` assessments,
so the same word is asserted against a panel that has to earn it, and the two
panels that must not earn it are asserted too.
"""
import importlib.util, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXT=ROOT/'research/extensions/p8-method-authority'
PANEL=EXT/'P9_P10_ANTI_LAUNDERING_CASES_V1.json'
SUMMARY=EXT/'P9_P10_ANTI_LAUNDERING_SUMMARY_V1.json'
SCRIPT=EXT/'run_anti_laundering_bench.py'
def _bench():
    spec=importlib.util.spec_from_file_location('p8_bench',SCRIPT);assert spec and spec.loader
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod
def test_p9_p10_anti_laundering_suite_rederives_exactly():
    mod=_bench()
    actual=mod.run(json.loads(PANEL.read_text()));summary=json.loads(SUMMARY.read_text())
    assert actual==summary
    assert summary['contract_accuracy']==1.0
    assert summary['illicit_coercion_block_rate']==1.0
    assert summary['clean_legal_coverage']==1.0
    assert summary['revocation_accuracy']==1.0
    assert summary['terminal']=='P8_P9_P10_ANTI_LAUNDERING_CLEAR'
def test_the_terminal_is_the_roll_up_of_the_four_rates_it_is_printed_beside():
    """Every emitted rate has a stated denominator, and the terminal is over all four."""
    summary=json.loads(SUMMARY.read_text())
    basis={item['rate_field']:item for item in summary['terminal_basis']}
    assert set(basis)=={'contract_accuracy','illicit_coercion_block_rate','clean_legal_coverage','revocation_accuracy'}
    for field,item in basis.items():
        assert item['rate']==summary[field]
        assert item['opportunities']>0 and item['violations']==0
        assert item['opportunity_definition'].strip()
        assert item['outcome']=='PASS'
    assert summary['terminal']=='P8_P9_P10_ANTI_LAUNDERING_CLEAR'
def test_a_panel_the_suite_fails_does_not_publish_clear():
    """The measurement that was impossible before: the verdict moves with the rates."""
    mod=_bench()
    panel=json.loads(PANEL.read_text())
    states=('BLOCKED','SUPPORTED','CANNOT_CHECK')
    for case in panel['cases']:
        case['expected']=next(state for state in states if state!=case['expected'])
    out=mod.run(panel)
    assert out['contract_accuracy']==0.0
    assert out['illicit_coercion_block_rate']==0.0
    assert out['terminal']=='P8_P9_P10_ANTI_LAUNDERING_VIOLATED'
def test_an_empty_slice_cannot_check_rather_than_scoring_one_point_zero():
    """A slice with no cases has no rate: ``None``, not 1.0, and never a pass.

    Each of the three constituent denominators is emptied on its own, because a
    two-valued terminal reading ``rate is not None`` would call every one of them
    clean --- ``not None`` is ``True``.
    """
    mod=_bench()
    panel=json.loads(PANEL.read_text())
    cases=panel['cases']
    empties={
        'illicit_coercion_block_rate':[c for c in cases if not (c['kind']=='coercion' and c['expected']=='BLOCKED')],
        'clean_legal_coverage':[c for c in cases if not (c['kind']=='coercion' and c['expected']=='SUPPORTED')],
        'revocation_accuracy':[c for c in cases if c['kind']!='revocation'],
    }
    for field,kept in empties.items():
        out=mod.run(dict(panel,cases=kept))
        assert out[field] is None
        basis=next(item for item in out['terminal_basis'] if item['rate_field']==field)
        assert basis['opportunities']==0 and basis['violations']==0
        assert basis['rate'] is None
        assert (basis['outcome'],basis['reason'])==('CANNOT_CHECK','NEVER_EXERCISED')
        assert out['terminal']=='P8_P9_P10_ANTI_LAUNDERING_CANNOT_CHECK'
    empty=mod.run(dict(panel,cases=[]))
    assert empty['n_cases']==0
    assert empty['contract_accuracy'] is None
    assert empty['terminal']=='P8_P9_P10_ANTI_LAUNDERING_CANNOT_CHECK'
def test_a_failing_case_outranks_a_missing_denominator():
    """Both block; ``VIOLATED`` is reported because a demonstrated failure is the more informative one."""
    mod=_bench()
    panel=json.loads(PANEL.read_text())
    cases=[c for c in panel['cases'] if c['kind']!='revocation']
    cases[0]=dict(cases[0],expected='SUPPORTED')
    out=mod.run(dict(panel,cases=cases))
    assert out['revocation_accuracy'] is None
    assert out['contract_accuracy']<1.0
    assert out['terminal']=='P8_P9_P10_ANTI_LAUNDERING_VIOLATED'
def test_the_declared_ceiling_is_derived_not_echoed():
    """Repaired 2026-08-21. This test used to assert the echo.

    Its old body checked that an injected sentence came back verbatim under
    ``declared_claim_ceiling_from_input``, and that the note admitted the bound
    was 'not one it earned'. Both were accurate, and pinning them made a
    laundering channel a fixture. The ceiling is now keyed off the terminal, and
    the input's own bound survives only as a digest.
    """
    mod=_bench()
    panel=json.loads(PANEL.read_text())
    injected='This suite establishes real method validity'
    out=mod.run(dict(panel,claim_ceiling=injected))
    assert out['claim_ceiling']!=injected
    assert injected not in json.dumps(out)
    assert '15 cases' in out['claim_ceiling']
    assert out['input_claim_ceiling_digest'].startswith('sha256:')
    assert 'derived from the graded assessments' in out['claim_ceiling_note'].lower()
    assert out['terminal']=='P8_P9_P10_ANTI_LAUNDERING_CLEAR'
