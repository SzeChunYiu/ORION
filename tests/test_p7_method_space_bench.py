import json
from pathlib import Path
from orion.transfer.v2.canonical import content_digest
ROOT=Path(__file__).resolve().parents[1]
PANEL=ROOT/'papers/candidates/paper-07-epistemic-navigation-open-worlds/method_space_extension/METHOD_SPACE_BENCH_V1.json'
SUMMARY=ROOT/'papers/candidates/paper-07-epistemic-navigation-open-worlds/method_space_extension/METHOD_SPACE_BENCH_SUMMARY_V1.json'
def test_method_space_bench_receipt_is_bound_and_narrowed():
    panel=json.loads(PANEL.read_text()); summary=json.loads(SUMMARY.read_text())
    assert summary['panel_digest']==content_digest(panel)
    assert summary['contract_accuracy']==1.0
    assert all(row['pass'] for row in summary['rows'])
    assert summary['terminal']=='P7_METHOD_SPACE_NAVIGATION_NARROWED'
