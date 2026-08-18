import importlib.util, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXT=ROOT/'research/extensions/p7-method-space'
PANEL=EXT/'METHOD_SPACE_BENCH_V1.json'
SUMMARY=EXT/'METHOD_SPACE_BENCH_SUMMARY_V1.json'
SCRIPT=EXT/'run_method_space_bench.py'
def test_method_space_bench_receipt_is_bound_and_narrowed():
    spec=importlib.util.spec_from_file_location('p7_bench',SCRIPT);assert spec and spec.loader
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    actual=mod.run(json.loads(PANEL.read_text()));summary=json.loads(SUMMARY.read_text())
    assert actual==summary
    assert summary['contract_accuracy']==1.0
    assert all(row['pass'] for row in summary['rows'])
    assert summary['terminal']=='P7_METHOD_SPACE_NAVIGATION_NARROWED'
