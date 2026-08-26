#!/usr/bin/env python3
"""Export a neutral JSONL corpus for independent generalized-Davenport solvers.

The export contains only group parameters, complete sequence multisets, boundary
metadata, and the registered expected packing number. It deliberately omits
zero-sum position masks, dynamic-programming states, and solver traces.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import engine_b_small_group_oracle_r9 as oracle

SCHEMA = "ORION.NQ.EngineBSmallGroupNeutralCaseR9.v1"
MANIFEST_SCHEMA = "ORION.NQ.EngineBSmallGroupNeutralCorpusManifestR9.v1"


def encode_sequence(sequence: tuple[oracle.Element, ...]) -> list[list[int]]:
    return [list(element) for element in sequence]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="JSONL output path")
    parser.add_argument("--manifest", required=True, help="manifest JSON output path")
    args = parser.parse_args()
    output = Path(args.output)
    manifest_path = Path(args.manifest)
    output.parent.mkdir(parents=True, exist_ok=True)
    case_count = 0
    boundary_rows: list[dict[str, object]] = []
    with output.open("w", encoding="utf-8") as handle:
        for boundary_index, case in enumerate(oracle.CASES):
            boundary_count = 0
            for relation, length, expected_minimum in (
                ("LOWER", case.expected_dk - 1, case.k - 1),
                ("UPPER", case.expected_dk, case.k),
            ):
                relation_count = 0
                for sequence_index, sequence in enumerate(oracle.sequence_multisets(case.group, length)):
                    record = {
                        "schema": SCHEMA,
                        "case_id": f"{boundary_index:02d}-{relation}-{sequence_index:06d}",
                        "group": {
                            "name": case.group.name,
                            "moduli": list(case.group.moduli),
                            "zero": list(case.group.zero),
                        },
                        "boundary": {
                            "k": case.k,
                            "expected_D_k": case.expected_dk,
                            "relation": relation,
                            "sequence_length": length,
                            "registered_minimum_packing_at_length": expected_minimum,
                        },
                        "sequence_multiset": encode_sequence(sequence),
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
                    boundary_count += 1
                    case_count += 1
                boundary_rows.append({
                    "group": case.group.name,
                    "moduli": list(case.group.moduli),
                    "k": case.k,
                    "expected_D_k": case.expected_dk,
                    "relation": relation,
                    "sequence_length": length,
                    "expected_minimum_packing_at_length": expected_minimum,
                    "case_count": relation_count,
                })
            assert boundary_count > 0
    corpus_bytes = output.read_bytes()
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "corpus_path": output.name,
        "corpus_sha256": hashlib.sha256(corpus_bytes).hexdigest(),
        "corpus_bytes": len(corpus_bytes),
        "case_count": case_count,
        "boundaries": boundary_rows,
        "neutrality": {
            "contains_group_and_sequence_inputs": True,
            "contains_registered_expected_packing": True,
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
            "neutral_differential_corpus": True,
            "independent_solver_result": False,
            "independent_C5_3_replay": False,
            "grants_journal_authority": False
        }
    }
    assert case_count == 21604
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
