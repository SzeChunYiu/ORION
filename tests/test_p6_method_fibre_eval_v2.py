import importlib.util
import json
from dataclasses import replace
from pathlib import Path

import pytest

from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.p6_fibre_evaluation_v2 import assess_membership_bound, build_fibre_bound
from orion.transfer.v2.p6_method_fibres import build_reduction, build_signature, membership_evidence, MethodRealizationView


def load_runner():
    p=Path("research/extensions/p6-method-fibres/run_method_fibre_eval_v2.py")
    spec=importlib.util.spec_from_file_location("p6_eval_v2",p);mod=importlib.util.module_from_spec(spec);assert spec.loader is not None;spec.loader.exec_module(mod);return mod


def test_frozen_p6_eval_v2_replays_exactly():
    mod=load_runner(); protocol=json.loads(Path("research/extensions/p6-method-fibres/METHOD_FIBRE_EVAL_V2_PROTOCOL.json").read_text()); expected=json.loads(Path("research/extensions/p6-method-fibres/METHOD_FIBRE_EVAL_V2_RESULTS.json").read_text())
    actual=mod.run(protocol)
    assert actual == expected
    assert actual["all_typed_cases_pass"] is True
    assert actual["mutation_detection_rate"] == 1.0
    assert actual["comparator_accuracy"]["p6_typed_bound"] == 1.0
    assert actual["comparator_accuracy"]["behavioral_bisimulation_style"] < 1.0


def v(name):
    return MethodRealizationView(name,content_digest({"n":name}),("p",),("a",),(),("i",),("e",),"t","r",("f",),(name,))


def test_bound_receipt_cannot_be_replayed_against_another_realization():
    base=v("base"); red=build_reduction(base,reduction_id="r",claim_id="c",preserved=("preconditions","invariants","effects","termination","reconstruction")); s=build_signature(base,red)
    first=v("first"); second=v("second")
    e=membership_evidence(s,first,assumptions=True,invariants=True,effects=True,reconstruction=True,provenance=True,beyond_single_panel=True)
    with pytest.raises(ValueError,match="different realization"):
        assess_membership_bound(s,second,e)


def test_bound_fibre_rejects_cross_signature_or_tampered_receipt():
    base=v("base"); red=build_reduction(base,reduction_id="r",claim_id="c",preserved=("preconditions","invariants","effects","termination","reconstruction")); s=build_signature(base,red)
    candidate=v("candidate"); e=membership_evidence(s,candidate,assumptions=True,invariants=True,effects=True,reconstruction=True,provenance=True,beyond_single_panel=True); receipt=assess_membership_bound(s,candidate,e)
    with pytest.raises(ValueError): build_fibre_bound(s,[replace(receipt,evidence_digest="sha256:"+"0"*64)])
    other_base=v("other"); other_red=build_reduction(other_base,reduction_id="o",claim_id="o",preserved=("preconditions",)); other_s=build_signature(other_base,other_red)
    with pytest.raises(ValueError,match="cross-signature"):
        build_fibre_bound(other_s,[receipt])
