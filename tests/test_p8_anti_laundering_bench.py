import importlib.util, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXT=ROOT/'research/extensions/p8-method-authority'
PANEL=EXT/'P9_P10_ANTI_LAUNDERING_CASES_V1.json'
SUMMARY=EXT/'P9_P10_ANTI_LAUNDERING_SUMMARY_V1.json'
SCRIPT=EXT/'run_anti_laundering_bench.py'
def test_p9_p10_anti_laundering_suite_rederives_exactly():
    spec=importlib.util.spec_from_file_location('p8_bench',SCRIPT);assert spec and spec.loader
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    actual=mod.run(json.loads(PANEL.read_text()));summary=json.loads(SUMMARY.read_text())
    assert actual==summary
    assert summary['contract_accuracy']==1.0
    assert summary['illicit_coercion_block_rate']==1.0
    assert summary['clean_legal_coverage']==1.0
    assert summary['revocation_accuracy']==1.0
    assert summary['terminal']=='P8_P9_P10_ANTI_LAUNDERING_CLEAR'
