from __future__ import annotations
import json
from responsibility_carried_state_v1 import *

def h(x): return digest({"x":x})

def main():
    pred=build_witness(responsibility_id="PREDICT",witness_id="w-predict",status=WitnessStatus.SUPPORTED,
        resource_bound={"decoder":1},authority_owner_id="external")
    inter=build_witness(responsibility_id="INTERVENE",witness_id="w-intervene",status=WitnessStatus.APPROXIMATE,
        resource_bound={"decoder":1},authority_owner_id="external")
    state=build_state(source_digest=h("source"),compiler_digest=h("compiler"),compiled_state_digest=h("compiled"),
        responsibility_witnesses=[pred,inter],omitted_coordinate_classes=["repair_owner"],
        raw_source_available=True,reconstruction_witness_id="raw-reconstruct",
        frozen_context={"schema":"v1","objective":"predict","data_revision":"r1"},
        required_same_coordinates=["schema"],reopen_on_change_coordinates=["data_revision"],
        evaluator_id="evaluator",authority_owner_id="external")
    cases={
      "supported_use": assess(state,responsibility_id="PREDICT",current_context={"schema":"v1","objective":"predict","data_revision":"r1"},requested_resource_bound={"decoder":1}).value,
      "approx_cannot_check": assess(state,responsibility_id="INTERVENE",current_context={"schema":"v1","objective":"predict","data_revision":"r1"},requested_resource_bound={"decoder":1}).value,
      "missing_resp_cannot_check": assess(state,responsibility_id="REPAIR",current_context={"schema":"v1","objective":"predict","data_revision":"r1"},requested_resource_bound={"decoder":1}).value,
      "reopen_on_revision": assess(state,responsibility_id="PREDICT",current_context={"schema":"v1","objective":"predict","data_revision":"r2"},requested_resource_bound={"decoder":1}).value,
      "required_same_change": assess(state,responsibility_id="PREDICT",current_context={"schema":"v2","objective":"predict","data_revision":"r1"},requested_resource_bound={"decoder":1}).value,
      "resource_mismatch": assess(state,responsibility_id="PREDICT",current_context={"schema":"v1","objective":"predict","data_revision":"r1"},requested_resource_bound={"decoder":2}).value,
    }
    expected={"supported_use":"USE_COMPILED","approx_cannot_check":"CANNOT_CHECK","missing_resp_cannot_check":"CANNOT_CHECK",
              "reopen_on_revision":"REOPEN_REQUIRED","required_same_change":"CANNOT_CHECK","resource_mismatch":"CANNOT_CHECK"}
    evaluator_authority_guard=False
    try:
        build_state(source_digest=h("s"),compiler_digest=h("c"),compiled_state_digest=h("z"),responsibility_witnesses=[pred],
          raw_source_available=False,frozen_context={"schema":"v1"},evaluator_id="same",authority_owner_id="same")
    except ValueError:
        evaluator_authority_guard=True
    result={"schema":"ORION.P17.ResponsibilityCarryingStateCheck.v1","cases":cases,"expected":expected,
            "evaluator_authority_guard":evaluator_authority_guard,
            "grants_scientific_authority":False,"grants_novelty_authority":False}
    result["terminal"]="P17_RESPONSIBILITY_CARRYING_STATE_SUBSTRATE_GREEN" if cases==expected and evaluator_authority_guard else "P17_RESPONSIBILITY_CARRYING_STATE_SUBSTRATE_RED"
    print(json.dumps(result,indent=2,sort_keys=True))
    if result["terminal"].endswith("_RED"): raise SystemExit(1)
if __name__=="__main__":main()
