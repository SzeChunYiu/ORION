#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.p1_method_realization import (
    PairDecision,
    assess_substitutability,
    build_method_realization,
    completeness_errors,
    material_differences,
)
from orion.transfer.v2.p3_method_projection import align_projections, build_projection

ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / "PROTOCOL_V1.json"
SUMMARY = ROOT / "RESULTS_V1.json"


def d(x: str) -> str:
    return content_digest({"fixture": x})


def make(name: str):
    common = dict(source_digest=d(name), source_version="authored-fixture-v1", authority_boundary="REPRESENTATION_ONLY")
    if name == "bisection":
        return build_method_realization(method_id=name, target_role="bounded_monotone_localization", preconditions=("ordered_domain","bracketed_target","monotone_response"), assumptions=("deterministic_response",), resources=("oracle",), representation_in="ordered_interval", representation_out="shrinking_interval", mechanics=("measure_midpoint","discard_inconsistent_half"), dependencies=(("measure_midpoint","discard_inconsistent_half"),), invariants=("target_remains_bracketed",), progress_measure="interval_width_decreases", effects=("shrink_candidate_interval",), terminal_condition="interval_width_below_tolerance", reconstruction_map="return_interval_representative", failure_modes=("non_monotone_response","target_not_bracketed"), lineage=("donor:bisection",), **common)
    if name == "threshold_calibration":
        return build_method_realization(method_id=name, target_role="bounded_monotone_localization", preconditions=("ordered_domain","bracketed_target","monotone_response"), assumptions=("deterministic_response",), resources=("oracle",), representation_in="ordered_interval", representation_out="shrinking_interval", mechanics=("sample_candidate","discard_inconsistent_region"), dependencies=(("sample_candidate","discard_inconsistent_region"),), invariants=("target_remains_bracketed",), progress_measure="interval_width_decreases", effects=("shrink_candidate_interval",), terminal_condition="interval_width_below_tolerance", reconstruction_map="return_interval_representative", failure_modes=("non_monotone_response","target_not_bracketed"), lineage=("donor:threshold",), **common)
    if name == "nonmonotone_midpoint":
        return build_method_realization(method_id=name, target_role="bounded_localization", preconditions=("ordered_domain","bracketed_target"), assumptions=("deterministic_response",), resources=("oracle",), representation_in="ordered_interval", representation_out="shrinking_interval", mechanics=("measure_midpoint","discard_half"), dependencies=(("measure_midpoint","discard_half"),), invariants=("finite_values",), progress_measure="interval_width_decreases", effects=("shrink_candidate_interval",), terminal_condition="interval_width_below_tolerance", reconstruction_map="return_interval_representative", failure_modes=("discarded_true_target",), lineage=("donor:nonmonotone",), **common)
    if name in {"queue_bfs", "layer_frontier_bfs"}:
        mechanics=("dequeue","enqueue_unseen") if name=="queue_bfs" else ("expand_frontier","form_next_frontier")
        return build_method_realization(method_id=name, target_role="unweighted_shortest_path_layers", preconditions=("unweighted_graph",), assumptions=("finite_graph",), resources=("adjacency_access",), representation_in="source_graph", representation_out="distance_layers", mechanics=mechanics, dependencies=((mechanics[0],mechanics[1]),), invariants=("first_visit_has_minimum_hop_distance",), progress_measure="visited_set_grows", effects=("discover_next_distance_layer",), terminal_condition="target_found_or_frontier_empty", reconstruction_map="parent_links_to_path", failure_modes=("target_unreachable",), lineage=(f"donor:{name}",), **common)
    if name == "stack_dfs":
        return build_method_realization(method_id=name, target_role="graph_reachability", preconditions=("finite_graph",), assumptions=(), resources=("adjacency_access",), representation_in="source_graph", representation_out="depth_first_tree", mechanics=("pop_stack","push_unseen"), dependencies=(("pop_stack","push_unseen"),), invariants=("visited_nodes_are_reachable",), progress_measure="visited_set_grows", effects=("discover_reachable_node",), terminal_condition="target_found_or_stack_empty", reconstruction_map="parent_links_to_some_path", failure_modes=("target_unreachable",), lineage=("donor:dfs",), **common)
    if name in {"transaction_rollback", "deployment_rollback"}:
        mechanics=("identify_changed_units","restore_prior_snapshot") if name=="transaction_rollback" else ("identify_changed_components","restore_prior_release")
        return build_method_realization(method_id=name, target_role="bounded_state_recovery", preconditions=("prior_good_state_available","changed_footprint_known"), assumptions=("restore_operation_idempotent",), resources=("snapshot_store",), representation_in="failed_state_plus_change_set", representation_out="restored_state", mechanics=mechanics, dependencies=((mechanics[0],mechanics[1]),), invariants=("unchanged_state_preserved",), progress_measure="unrecovered_footprint_decreases", effects=("restore_changed_footprint",), terminal_condition="all_changed_units_restored", reconstruction_map="identity_on_unaffected_state", failure_modes=("snapshot_missing","footprint_unknown"), lineage=(f"donor:{name}",), **common)
    if name == "opaque_recovery":
        return build_method_realization(method_id=name, target_role="bounded_state_recovery", preconditions=("prior_good_state_available",), assumptions=(), resources=("recovery_tool",), representation_in="failed_state", representation_out=None, mechanics=("invoke_recovery",), dependencies=(), invariants=("unchanged_state_preserved",), progress_measure=None, effects=("restore_changed_footprint",), terminal_condition="tool_reports_done", reconstruction_map=None, failure_modes=("unknown_failure",), lineage=("donor:opaque",), unknown_coordinates=("representation_out","progress_measure","reconstruction_map"), **common)
    raise KeyError(name)


def project(method):
    return build_projection(method, projection_id=f"proj:{method.method_id}", source_id=f"fixture:{method.method_id}", source_span_digests=(d("span:"+method.method_id),), initial_obstruction=("direct_method_not_assumed",), author_rationale=())


def transcript_baseline(left, right):
    # deliberately simple surface baseline: high action-set overlap implies same.
    l=set(left.mechanics); r=set(right.mechanics)
    j=len(l&r)/max(1,len(l|r))
    return "ALIGNED" if j >= 0.5 else "OBSTRUCTION"


def run(protocol: dict) -> dict:
    required=("preconditions","invariants","progress","termination","reconstruction")
    pair_rows=[]
    typed_correct=0; transcript_correct=0; unresolved_gold=0; unresolved_correct=0
    for row in protocol["pairs"]:
        left=make(row["left"]); right=make(row["right"])
        alignment=align_projections(project(left),project(right),alignment_id=row["id"],purpose="frozen fixture purpose",required_coordinates=required)
        actual=alignment.state.value
        if actual==row["gold"]: typed_correct += 1
        if transcript_baseline(left,right)==row["gold"]: transcript_correct += 1
        if row["gold"]=="UNRESOLVED":
            unresolved_gold += 1
            unresolved_correct += int(actual=="UNRESOLVED")
        pair_rows.append({"id":row["id"],"gold":row["gold"],"typed":actual,"transcript":transcript_baseline(left,right),"pass":actual==row["gold"]})

    base=make("bisection")
    corruptions=[]
    corruption_variants={
        "delete_invariant": make("bisection").__class__(**{**base.__dict__,"invariants":(),"digest":base.digest}),
    }
    # Material corruptions are evaluated by rebuilding valid but changed representations,
    # except digest tampering, which is separately guarded by unit tests.
    changed=[
        ("delete_invariant", build_method_realization(**{**base.unsigned(),"version":None,"invariants":(),"method_id":"c1"}) if False else None),
    ]
    # Use explicit checks rather than dynamic constructor tricks to keep the archive stable.
    variants={
        "delete_invariant": build_method_realization(method_id="c_inv",source_digest=d("c_inv"),source_version="v",target_role=base.target_role,preconditions=base.preconditions,assumptions=base.assumptions,resources=base.resources,representation_in=base.representation_in,representation_out=base.representation_out,mechanics=base.mechanics,dependencies=base.dependencies,invariants=(),progress_measure=base.progress_measure,effects=base.effects,terminal_condition=base.terminal_condition,reconstruction_map=base.reconstruction_map,failure_modes=base.failure_modes,lineage=base.lineage,authority_boundary=base.authority_boundary),
        "delete_reconstruction": build_method_realization(method_id="c_rec",source_digest=d("c_rec"),source_version="v",target_role=base.target_role,preconditions=base.preconditions,assumptions=base.assumptions,resources=base.resources,representation_in=base.representation_in,representation_out=base.representation_out,mechanics=base.mechanics,dependencies=base.dependencies,invariants=base.invariants,progress_measure=base.progress_measure,effects=base.effects,terminal_condition=base.terminal_condition,reconstruction_map=None,failure_modes=base.failure_modes,lineage=base.lineage,authority_boundary=base.authority_boundary,unknown_coordinates=("reconstruction_map",)),
        "reverse_dependency": build_method_realization(method_id="c_dep",source_digest=d("c_dep"),source_version="v",target_role=base.target_role,preconditions=base.preconditions,assumptions=base.assumptions,resources=base.resources,representation_in=base.representation_in,representation_out=base.representation_out,mechanics=base.mechanics,dependencies=((base.mechanics[1],base.mechanics[0]),),invariants=base.invariants,progress_measure=base.progress_measure,effects=base.effects,terminal_condition=base.terminal_condition,reconstruction_map=base.reconstruction_map,failure_modes=base.failure_modes,lineage=base.lineage,authority_boundary=base.authority_boundary),
        "swap_precondition": build_method_realization(method_id="c_pre",source_digest=d("c_pre"),source_version="v",target_role=base.target_role,preconditions=("unordered_domain",),assumptions=base.assumptions,resources=base.resources,representation_in=base.representation_in,representation_out=base.representation_out,mechanics=base.mechanics,dependencies=base.dependencies,invariants=base.invariants,progress_measure=base.progress_measure,effects=base.effects,terminal_condition=base.terminal_condition,reconstruction_map=base.reconstruction_map,failure_modes=base.failure_modes,lineage=base.lineage,authority_boundary=base.authority_boundary),
        "collapse_failure_semantics": build_method_realization(method_id="c_fail",source_digest=d("c_fail"),source_version="v",target_role=base.target_role,preconditions=base.preconditions,assumptions=base.assumptions,resources=base.resources,representation_in=base.representation_in,representation_out=base.representation_out,mechanics=base.mechanics,dependencies=base.dependencies,invariants=base.invariants,progress_measure=base.progress_measure,effects=base.effects,terminal_condition=base.terminal_condition,reconstruction_map=base.reconstruction_map,failure_modes=("FAIL",),lineage=base.lineage,authority_boundary=base.authority_boundary),
        "erase_lineage": build_method_realization(method_id="c_lin",source_digest=d("c_lin"),source_version="v",target_role=base.target_role,preconditions=base.preconditions,assumptions=base.assumptions,resources=base.resources,representation_in=base.representation_in,representation_out=base.representation_out,mechanics=base.mechanics,dependencies=base.dependencies,invariants=base.invariants,progress_measure=base.progress_measure,effects=base.effects,terminal_condition=base.terminal_condition,reconstruction_map=base.reconstruction_map,failure_modes=base.failure_modes,lineage=(),authority_boundary=base.authority_boundary),
        "widen_authority": build_method_realization(method_id="c_auth",source_digest=d("c_auth"),source_version="v",target_role=base.target_role,preconditions=base.preconditions,assumptions=base.assumptions,resources=base.resources,representation_in=base.representation_in,representation_out=base.representation_out,mechanics=base.mechanics,dependencies=base.dependencies,invariants=base.invariants,progress_measure=base.progress_measure,effects=base.effects,terminal_condition=base.terminal_condition,reconstruction_map=base.reconstruction_map,failure_modes=base.failure_modes,lineage=base.lineage,authority_boundary="ADOPTION_ALLOWED"),
        "fabricate_unknown": build_method_realization(method_id="c_unknown",source_digest=d("c_unknown"),source_version="v",target_role=base.target_role,preconditions=base.preconditions,assumptions=base.assumptions,resources=base.resources,representation_in=base.representation_in,representation_out=base.representation_out,mechanics=base.mechanics,dependencies=base.dependencies,invariants=base.invariants,progress_measure="fabricated_known_progress",effects=base.effects,terminal_condition=base.terminal_condition,reconstruction_map=base.reconstruction_map,failure_modes=base.failure_modes,lineage=base.lineage,authority_boundary=base.authority_boundary),
    }
    for name, variant in variants.items():
        detected=bool(material_differences(base,variant)) or bool(completeness_errors(variant))
        corruptions.append({"id":name,"detected":detected})

    required_sub=("preconditions","invariants","effects","terminal_condition","reconstruction_map")
    true_pair=assess_substitutability(make("bisection"),make("threshold_calibration"),required_coordinates=required_sub)
    false_pair=assess_substitutability(make("bisection"),make("nonmonotone_midpoint"),required_coordinates=required_sub)
    unresolved_pair=assess_substitutability(make("transaction_rollback"),make("opaque_recovery"),required_coordinates=required_sub)
    p1_ok=sum(1 for name in ("bisection","threshold_calibration","queue_bfs","layer_frontier_bfs","transaction_rollback") if not completeness_errors(make(name)))
    result={
        "protocol_id":protocol["protocol_id"],
        "protocol_digest":content_digest(protocol),
        "n_domains":len(protocol["domains"]),
        "n_pairs":len(protocol["pairs"]),
        "pair_rows":pair_rows,
        "coordinate_recoverability":p1_ok/5,
        "corruption_detection_recall":sum(x["detected"] for x in corruptions)/len(corruptions),
        "corruptions":corruptions,
        "substitution_true":true_pair.value,
        "substitution_false":false_pair.value,
        "substitution_unresolved":unresolved_pair.value,
        "false_substitutability_rate":0.0 if false_pair is PairDecision.NOT_SUBSTITUTABLE else 1.0,
        "correct_unresolved_rate":unresolved_correct/max(1,unresolved_gold),
        "projection_alignment_accuracy":typed_correct/len(protocol["pairs"]),
        "transcript_only_pair_accuracy":transcript_correct/len(protocol["pairs"]),
        "terminal":"P1_METHOD_RECONSTRUCTION_NARROWED__P3_METHOD_PROJECTION_NARROWED",
        "claim_ceiling":protocol["claim_ceiling"],
    }
    result["result_digest"]=content_digest(result)
    return result


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--write",action="store_true"); parser.add_argument("--check",action="store_true")
    args=parser.parse_args(); protocol=json.loads(PROTOCOL.read_text()); result=run(protocol)
    if args.write:
        SUMMARY.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    elif args.check:
        expected=json.loads(SUMMARY.read_text())
        if result != expected:
            raise SystemExit("structure pilot result drift")
    else:
        print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__": main()
