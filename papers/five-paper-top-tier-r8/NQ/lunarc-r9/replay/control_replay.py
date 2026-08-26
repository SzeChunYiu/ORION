#!/usr/bin/env python3
"""Deterministic CR-A/CR-B rank-two prefix replay for issue #1383.

This is a pre-census discriminator only.  It executes a declared-complete
multiset grammar over a five-element rank-two alphabet, compares Engine A's
multi-bin DP with Engine B's SAT automaton and a tiny labelled-bin reference,
and binds every case, representative, orbit and disagreement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from itertools import combinations_with_replacement
from pathlib import Path
from typing import Any, Mapping

REPLAY_ROOT = Path(__file__).resolve().parent
NQ_ROOT = REPLAY_ROOT.parents[1]
ENGINE_A_SRC = NQ_ROOT / "engine-a-bounded-pilot-v1" / "src"
ENGINE_B_ROOT = REPLAY_ROOT / "engine_b"
for source_root in (ENGINE_A_SRC, ENGINE_B_ROOT):
    if str(source_root) not in sys.path:
        sys.path.insert(0, str(source_root))

import engine_b as eb  # noqa: E402
import symmetry  # noqa: E402
from nq_engine_a.canonical import canonical_multiset  # noqa: E402
from nq_engine_a.factorization import FactorizationStatus, find_disjoint_zero_sums  # noqa: E402
from nq_engine_a.group import GroupSpec  # noqa: E402

SCIENTIFIC_SUBJECT = eb.SUBJECT_COMMIT
CUSTODY_PARENT = "6167aa27e9b7aebd4fcc766159cdc80bf3b3130a"
CONTROL_SCOPE = "C5^3_EMBEDDED_RANK2_FIVE_SYMBOL_MULTISET_LENGTH_2_TO_4_K2"
PASS_TERMINAL = "NQ_CR_A_CR_B_RANK2_PREFIX_CONTROL_PASS"
DISAGREEMENT_TERMINAL = "NQ_CR_A_CR_B_RANK2_PREFIX_CONTROL_DISAGREEMENT"
AUTHORITY_CEILING = "ENGINEERING_CONTROL_ONLY__FULL_REPLAY_NOT_RUN__CANNOT_CHECK"


def _sha256(value: Any) -> str:
    return hashlib.sha256(eb.canonical_json_bytes(value)).hexdigest()


def _alphabet() -> tuple[int, ...]:
    zero = eb.ZERO
    e1 = eb.encode_element((1, 0, 0))
    e2 = eb.encode_element((0, 1, 0))
    return tuple(sorted((zero, e1, eb.negate(e1), e2, eb.negate(e2))))


def frozen_rank_two_cases() -> tuple[tuple[int, ...], ...]:
    cases = []
    alphabet = _alphabet()
    for length in range(2, 5):
        for sequence in combinations_with_replacement(alphabet, length):
            if symmetry.span_rank(sequence) == 2:
                cases.append(sequence)
    return tuple(cases)


def _engine_a_sequence(sequence: tuple[int, ...]) -> tuple[tuple[int, int, int], ...]:
    return tuple(eb.decode_element(element) for element in sequence)


def _status_a(sequence: tuple[int, ...]) -> tuple[str, list[list[int]] | None]:
    spec = GroupSpec(5, 3)
    vectors = _engine_a_sequence(sequence)
    result = find_disjoint_zero_sums(spec, vectors, 2)
    if result.status is FactorizationStatus.CANNOT_CHECK_RESOURCE_BOUND:
        return result.status.value, None
    certificate = None
    if result.certificate is not None:
        certificate = [list(selected) for selected in result.certificate.bins]
    return result.status.value, certificate


def _status_b(sequence: tuple[int, ...]) -> tuple[str, list[list[int]] | None, str]:
    encoded = eb.build_factorization_cnf(sequence, 2)
    model = eb.solve_cnf_dpll(encoded.cnf)
    if model is None:
        return "NEGATIVE", None, encoded.cnf_sha256
    witness = encoded.extract_witness(model)
    eb.verify_witness(sequence, required_bins=2, bins=witness)
    return "POSITIVE", [list(selected) for selected in witness], encoded.cnf_sha256


def _engine_a_record(index: int, sequence: tuple[int, ...]) -> dict[str, Any]:
    vectors = _engine_a_sequence(sequence)
    representative_a = canonical_multiset(GroupSpec(5, 3), vectors)
    status_a, witness_a = _status_a(sequence)
    payload = {
        "record_id": f"rank2-prefix-{index:03d}",
        "sequence_sha256": _sha256(list(sequence)),
        "status": status_a,
        "witness": witness_a,
        "representative_sha256": _sha256([list(vector) for vector in representative_a]),
    }
    payload["record_sha256"] = _sha256(payload)
    return payload


def _engine_b_record(index: int, sequence: tuple[int, ...]) -> dict[str, Any]:
    representative_b = symmetry.canonical_matrix_action(sequence)
    status_b, witness_b, cnf_sha256 = _status_b(sequence)
    representative_b_payload = [list(vector) for vector in representative_b]
    payload = {
        "record_id": f"rank2-prefix-{index:03d}",
        "sequence_sha256": _sha256(list(sequence)),
        "status": status_b,
        "witness": witness_b,
        "cnf_sha256": cnf_sha256,
        "representative": representative_b_payload,
        "representative_sha256": _sha256(representative_b_payload),
        "orbit_sha256": symmetry.orbit_sha256(sequence),
    }
    payload["record_sha256"] = _sha256(payload)
    return payload


def _reference_record(index: int, sequence: tuple[int, ...]) -> dict[str, Any]:
    status = "POSITIVE" if eb.has_k_disjoint_zero_sums_bruteforce(sequence, 2) else "NEGATIVE"
    payload = {
        "record_id": f"rank2-prefix-{index:03d}",
        "sequence_sha256": _sha256(list(sequence)),
        "status": status,
    }
    payload["record_sha256"] = _sha256(payload)
    return payload


def _combine_case_record(
    index: int,
    sequence: tuple[int, ...],
    engine_a: Mapping[str, Any],
    engine_b: Mapping[str, Any],
    reference: Mapping[str, Any],
) -> dict[str, Any]:
    record_id = f"rank2-prefix-{index:03d}"
    sequence_sha256 = _sha256(list(sequence))
    if any(
        record.get("record_id") != record_id or record.get("sequence_sha256") != sequence_sha256
        for record in (engine_a, engine_b, reference)
    ):
        raise RuntimeError("independent control-pass identity mismatch")
    agreement = (
        engine_a["status"] == engine_b["status"] == reference["status"]
        and engine_a["representative_sha256"] == engine_b["representative_sha256"]
    )
    record: dict[str, Any] = {
        "record_id": record_id,
        "sequence": list(sequence),
        "sequence_sha256": sequence_sha256,
        "required_bins": 2,
        "reference_status": reference["status"],
        "engine_a_status": engine_a["status"],
        "engine_b_status": engine_b["status"],
        "engine_a_witness": engine_a["witness"],
        "engine_b_witness": engine_b["witness"],
        "engine_b_cnf_sha256": engine_b["cnf_sha256"],
        "canonical_representative": engine_b["representative"],
        "engine_a_representative_sha256": engine_a["representative_sha256"],
        "engine_b_representative_sha256": engine_b["representative_sha256"],
        "engine_b_orbit_sha256": engine_b["orbit_sha256"],
        "engine_a_record_sha256": engine_a["record_sha256"],
        "engine_b_record_sha256": engine_b["record_sha256"],
        "reference_record_sha256": reference["record_sha256"],
        "agreement": agreement,
    }
    record["case_sha256"] = _sha256(record)
    return record


def build_control_receipt() -> dict[str, Any]:
    sequences = frozen_rank_two_cases()
    # Each pass completes and is digest-bound before any cross-engine comparison.
    engine_a_pass = tuple(
        _engine_a_record(index, sequence) for index, sequence in enumerate(sequences)
    )
    engine_b_pass = tuple(
        _engine_b_record(index, sequence) for index, sequence in enumerate(sequences)
    )
    reference_pass = tuple(
        _reference_record(index, sequence) for index, sequence in enumerate(sequences)
    )
    engine_a_pass_sha256 = _sha256([record["record_sha256"] for record in engine_a_pass])
    engine_b_pass_sha256 = _sha256([record["record_sha256"] for record in engine_b_pass])
    reference_pass_sha256 = _sha256([record["record_sha256"] for record in reference_pass])
    cases = tuple(
        _combine_case_record(index, sequence, engine_a, engine_b, reference)
        for index, (sequence, engine_a, engine_b, reference) in enumerate(
            zip(sequences, engine_a_pass, engine_b_pass, reference_pass, strict=True)
        )
    )
    mismatches = [
        {
            "record_id": case["record_id"],
            "sequence": case["sequence"],
            "reference_status": case["reference_status"],
            "engine_a_status": case["engine_a_status"],
            "engine_b_status": case["engine_b_status"],
            "engine_a_representative_sha256": case["engine_a_representative_sha256"],
            "engine_b_representative_sha256": case["engine_b_representative_sha256"],
        }
        for case in cases
        if not case["agreement"]
    ]
    positive = sum(case["reference_status"] == "POSITIVE" for case in cases)
    terminal = PASS_TERMINAL if not mismatches else DISAGREEMENT_TERMINAL
    receipt: dict[str, Any] = {
        "schema": "ORION.NQ.R9.CRABRank2ControlReceipt.v1",
        "scientific_subject": SCIENTIFIC_SUBJECT,
        "custody_parent": CUSTODY_PARENT,
        "scope": CONTROL_SCOPE,
        "grammar": {
            "alphabet": list(_alphabet()),
            "sequence_kind": "nondecreasing_multiset",
            "lengths": [2, 3, 4],
            "rank": 2,
            "required_bins": 2,
            "declared_complete_for_this_control_grammar": True,
        },
        "engine_independence": {
            "engine_a": "canonical orderly generation plus multi-bin subset-sum DP",
            "engine_b": "CNF prefix-sum automaton plus literal GL(r,5) matrix action",
            "same_generated_clause_solver_is_independence": False,
            "blinded_independence": "NOT_CLAIMED_EXPECTED_OUTCOMES_EXPOSED",
            "engine_b_imports_engine_a": False,
            "comparison_occurs_only_after_both_passes_complete": True,
        },
        "engine_a_pass_sha256": engine_a_pass_sha256,
        "engine_b_pass_sha256": engine_b_pass_sha256,
        "reference_pass_sha256": reference_pass_sha256,
        "case_count": len(cases),
        "positive_count": positive,
        "negative_count": len(cases) - positive,
        "mismatch_count": len(mismatches),
        "cases_sha256": _sha256([case["case_sha256"] for case in cases]),
        "orbit_range_sha256": _sha256(
            [
                [
                    case["record_id"],
                    case["engine_b_representative_sha256"],
                    case["engine_b_orbit_sha256"],
                ]
                for case in cases
            ]
        ),
        "cases": list(cases),
        "disagreements": mismatches,
        "terminal": terminal,
        "full_census_executed": False,
        "d2_d3_replay_complete": False,
        "d4_c5_cubed": "OPEN",
        "science_terminal": "CANNOT_CHECK",
        "independence_terminal": "CANNOT_CHECK",
        "authority_ceiling": AUTHORITY_CEILING,
    }
    receipt["receipt_sha256"] = _sha256(receipt)
    return receipt


def write_json_atomic(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=REPLAY_ROOT / "controls" / "RANK2_PREFIX_CONTROL_RECEIPT.json",
    )
    args = parser.parse_args()
    receipt = build_control_receipt()
    write_json_atomic(args.output, receipt)
    print(receipt["terminal"])
    print(receipt["receipt_sha256"])
    return 0 if receipt["terminal"] == PASS_TERMINAL else 3


if __name__ == "__main__":
    raise SystemExit(main())
