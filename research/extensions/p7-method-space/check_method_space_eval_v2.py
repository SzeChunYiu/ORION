#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
RUNNER=ROOT/'run_method_space_eval_v2.py'
PROTOCOL=ROOT/'METHOD_SPACE_EVAL_V2_PROTOCOL.json'
SUMMARY=ROOT/'METHOD_SPACE_EVAL_V2_SUMMARY.json'


def _runner():
    spec=importlib.util.spec_from_file_location('p7_eval_v2',RUNNER)
    module=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(module); return module


def summarize(result):
    keys=(
        'protocol_id','protocol_digest','n_worlds','policy_accuracy','target_discovery_rate',
        'false_analogy_control','harmful_reframe_control','premature_stop_rate','reopen_correctness',
        'invention_escalation_correctness','loop_control','mutation_detection_rate','terminal',
        'claim_ceiling','result_digest',
    )
    return {key:result[key] for key in keys}


def derive():
    protocol=json.loads(PROTOCOL.read_text()); return summarize(_runner().run(protocol))


def main():
    expected=json.loads(SUMMARY.read_text()); actual=derive()
    if actual != expected: raise SystemExit('P7 MethodSpaceEval.v2 summary drift')
    print(json.dumps(actual,indent=2,sort_keys=True))

if __name__=='__main__': main()
