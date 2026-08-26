#!/usr/bin/env python3
"""Export V2 neutral cases with a registered per-sequence packing oracle value.

V1 exposed only the boundary minimum and could not support case-by-case
differential replay. V2 is authoritative for Engine-B handoff.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import engine_b_small_group_oracle_r9 as oracle

CASE_SCHEMA = "ORION.NQ.EngineBSmallGroupNeutralCaseR9.v2"
MANIFEST_SCHEMA = "ORION.NQ.EngineBSmallGroupNeutralCorpusManifestR9.v2"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    manifest_path = Path(args.manifest)
    output.parent.mkdir(parents=True, exist_ok=True)

    case_count = 0
    boundary_rows = []
    packing_histogram: dict[str, int] = {}
    with output.open("w", encoding="utf-8") as handle:
        for boundary_index, case in enumerate(oracle.CASES):
            for relation, length, registered_minimum in (
                ("LOWER", case.expected_dk - 1, case.k - 1),
                ("UPPER", case.expected_dk, case.k),
            ):
                relation_count = 0
                observed_minimum: int | None = None
                observed_maximum: int | None = None
                for sequence_index, sequence in enumerate(oracle.sequence_multisets(case.group, length)):
                    masks = oracle.zero_sum_masks(case.group, sequence)
                    packing_a = oracle.packing_solver_a(length, masks)
                    packing_b = oracle.packing_solver_b(length, masks)
                    assert packing_a == packing_b
                    packing = packing_a
                    observed_minimum = packing if observed_minimum is None else min(observed_minimum, packing)
                    observed_maximum = packing if observed_maximum is None else max(observed_maximum, packing)
                    histogram_key = f"{case.group.name};k={case.k};{relation};packing={packing}"
                    packing_histogram[histogram_key] = packing_histogram.get(histogram_key, 0) + 1
                    record = {
                        "schema": CASE_SCHEMA,
                        "case_id": f"{boundary_index:02d}-{relation}-{sequence_index:06d}",
                        "group": {
                            "name": case.group.name,
                            "moduli": list(case.group.moduli),
                        },
                        "boundary": {
                            "k": case.k,
                            "expected_D_k": case.expected_dk,
                            "relation": relation,
                            "sequence_length": length,
                            "registered_minimum_packing_at_length": registered_minimum,
                        },
                        "sequence_multiset": [list(element) for element in sequence],
                        "registered_expected_packing_number": packing,
                        "registered_oracle_agreement": {
                            "solver_a_equals_solver_b": True,
                            "zero_sum_masks_disclosed": False,
                            "solver_states_disclosed": False,
                            "solver_traces_disclosed": False,
                        },
                        "solver_input_contract": {
                            "positions_are_labeled_after_expansion": True,
                            "zero_elements_are_allowed": True,
                            "repeated_elements_are_distinct_positions": True,
                            "blocks_must_be_nonempty": True,
                            "unused_positions_are_allowed": True,
                            "blocks_must_be_pairwise_disjoint": True,
                            "group_addition_is_coordinatewise_moduli": True,
                        },
                    }
                    handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
                    relation_count += 1
                    case_count += 1
                assert observed_minimum == registered_minimum
                boundary_rows.append({
                    "group": case.group.name,
                    "moduli": list(case.group.moduli),
                    "k": case.k,
                    "expected_D_k": case.expected_dk,
                    "relation": relation,
                    "sequence_length": length,
                    "registered_minimum_packing_at_length": registered_minimum,
                    "observed_minimum_packing": observed_minimum,
                    "observed_maximum_packing": observed_maximum,
                    "case_count": relation_count,
                })

    corpus_bytes = output.read_bytes()
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "supersedes": {
            "schema": "ORION.NQ.EngineBSmallGroupNeutralCorpusManifestR9.v1",
            "reason": "V1 omitted per-sequence expected packing values and cannot support case-by-case differential replay.",
            "authority": False,
        },
        "corpus_path": output.name,
        "corpus_sha256": hashlib.sha256(corpus_bytes).hexdigest(),
        "corpus_bytes": len(corpus_bytes),
        "case_count": case_count,
        "boundaries": boundary_rows,
        "packing_histogram": dict(sorted(packing_histogram.items())),
        "neutrality": {
            "contains_group_and_sequence_inputs": True,
            "contains_per_sequence_registered_packing_number": True,
            "registered_value_requires_dual_oracle_agreement": True,
            "contains_zero_sum_position_masks": False,
            "contains_registered_solver_state": False,
            "contains_registered_solver_trace": False,
            "independent_solver_may_import_oracle_code": False,
        },
        "required_independent_output_schema": "ORION.NQ.EngineBSmallGroupIndependentOutputR9.v1",
        "required_terminals": [
            "AGREE_ALL_SMALL_GROUPS",
            "DISAGREE_SEQUENCE_ENCODING",
            "DISAGREE_ZERO_SUM_SUBSETS",
            "DISAGREE_PACKING_NUMBER",
            "DISAGREE_DK_BOUNDARY",
            "RESOURCE_EXHAUSTED",
            "CANNOT_CHECK"
        ],
        "authority": {
            "authoritative_neutral_differential_corpus": True,
            "independent_solver_result": False,
            "independent_C5_3_replay": False,
            "grants_journal_authority": False
        },
        "terminal": "NQ_ENGINE_B_NEUTRAL_CORPUS_V2__PER_SEQUENCE_DUAL_ORACLE_VALUES_BOUND"
    }
    assert case_count == 21604
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
