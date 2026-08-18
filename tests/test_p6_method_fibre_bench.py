from __future__ import annotations
import importlib.util, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'papers/candidates/paper-06-formal-epistemic-structures-and-mechanics/scripts/run_method_fibre_bench.py'
SUMMARY=ROOT/'papers/candidates/paper-06-formal-epistemic-structures-and-mechanics/method_fibre_extension/METHOD_FIBRE_BENCH_SUMMARY_V1.json'
PANEL=ROOT/'papers/candidates/paper-06-formal-epistemic-structures-and-mechanics/method_fibre_extension/METHOD_FIBRE_BENCH_V1.json'

def test_frozen_summary_rederives_exactly():
    spec=importlib.util.spec_from_file_location('p6_bench',SCRIPT); assert spec and spec.loader
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    actual=mod.run(json.loads(PANEL.read_text()))
    assert actual==json.loads(SUMMARY.read_text())
    assert actual['terminal']=='P6_METHOD_FIBRE_FORMALISM_NARROWED'
    assert actual['typed_calculus_accuracy']==1.0
    assert actual['false_fibre_control']==1.0
    assert actual['clean_acceptance']==1.0
