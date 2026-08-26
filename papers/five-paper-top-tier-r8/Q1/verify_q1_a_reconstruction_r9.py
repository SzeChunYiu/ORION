#!/usr/bin/env python3
"""Clean-room verifier for the Q1-A support-two reconstruction.

This file is derived only from the frozen neutral definitions and claim ledger.
It intentionally does not import any registered ORION-Q solver, canonicalizer,
witness generator, support checker, or result receipt.
"""

from __future__ import annotations

import hashlib
import itertools
from functools import lru_cache
import json
from pathlib import Path
from typing import Iterable, Optional, Sequence

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
PAULI_LETTERS = ("I", "X", "Y", "Z")
FROZEN_TARGETS = (("ZI", "XZ"), ("IX", "IZ"), ("IZ", "IZ"))
SOURCE_COMMIT = "1e18787841d99d76a3c7661505838d2eca8780db"


def pauli_weight(pauli: str) -> int:
    return sum(letter != "I" for letter in pauli)


def pauli_multiply(left: str, right: str) -> str:
    """Multiply phase-free Pauli words."""
    if len(left) != len(right):
        raise ValueError("Pauli lengths differ")
    product = []
    for a, b in zip(left, right):
        if a == "I":
            product.append(b)
        elif b == "I":
            product.append(a)
        elif a == b:
            product.append("I")
        else:
            product.append(({"X", "Y", "Z"} - {a, b}).pop())
    return "".join(product)


def symplectic(left: str, right: str) -> int:
    """Return phase-free symplectic parity."""
    if len(left) != len(right):
        raise ValueError("Pauli lengths differ")
    return sum(a != "I" and b != "I" and a != b for a, b in zip(left, right)) % 2


def f3_local(a: str, b: str, c: str) -> int:
    if a == b == c and a != "I":
        return 1
    return sum(letter != "I" for letter in (a, b, c))


def restore_cost(restore_triples: Sequence[Sequence[str]]) -> int:
    """Evaluate both branch triples with the frozen coordinate-local F3 rule."""
    if len(restore_triples) != 3 or any(len(pair) != 2 for pair in restore_triples):
        raise ValueError("Expected three blocks with two Restore words each")
    n = len(restore_triples[0][0])
    return sum(
        f3_local(
            restore_triples[0][branch][coordinate],
            restore_triples[1][branch][coordinate],
            restore_triples[2][branch][coordinate],
        )
        for branch in range(2)
        for coordinate in range(n)
    )


def maximum_single_donor_f3_increase() -> tuple[int, dict]:
    best = None
    for before in itertools.product(PAULI_LETTERS, repeat=3):
        before_cost = f3_local(*before)
        for donor in range(3):
            for replacement in PAULI_LETTERS:
                after = list(before)
                after[donor] = replacement
                after_cost = f3_local(*after)
                candidate = (
                    after_cost - before_cost,
                    {
                        "before": list(before),
                        "after": after,
                        "changed_donor": donor,
                        "before_cost": before_cost,
                        "after_cost": after_cost,
                    },
                )
                if best is None or candidate[0] > best[0]:
                    best = candidate
    assert best is not None
    return best


def xor_signature(signatures: Iterable[tuple[int, int]]) -> tuple[int, int]:
    first = second = 0
    for a, b in signatures:
        first ^= a
        second ^= b
    return first, second


def find_proper_zero_sum_subset(
    signatures: Sequence[tuple[int, int]],
) -> Optional[tuple[int, ...]]:
    """Find the size-at-most-three deletion used by the exchange lemma."""
    n = len(signatures)
    for size in range(1, min(3, n - 1) + 1):
        for indices in itertools.combinations(range(n), size):
            if xor_signature(signatures[i] for i in indices) == (0, 0):
                return indices
    return None


def objective_multiplier_control() -> dict:
    before = ("X", "X", "X")
    after = ("Y", "X", "X")
    penalty = f3_local(*after) - f3_local(*before)
    return {
        "before": list(before),
        "after": list(after),
        "restore_penalty": penalty,
        "net_change_m1": penalty - 1,
        "net_change_m2": penalty - 2,
        "net_change_m4": penalty - 4,
    }


def _all_paulis(n: int) -> tuple[str, ...]:
    return tuple("".join(word) for word in itertools.product(PAULI_LETTERS, repeat=n))


def _block_states(
    targets: tuple[str, str],
    tag: str,
    orientation: tuple[int, int],
    max_frame_support: int,
) -> tuple[dict, int]:
    """Exactly eliminate local choices, retaining the minimum by Restore pair."""
    paulis = tuple(
        pauli
        for pauli in _all_paulis(len(tag))
        if 0 < pauli_weight(pauli) <= max_frame_support
    )
    best_by_restore = {}
    raw_count = 0
    for frame_0 in paulis:
        if symplectic(frame_0, tag) != orientation[0]:
            continue
        for frame_1 in paulis:
            if symplectic(frame_1, tag) != orientation[1]:
                continue
            if symplectic(frame_0, frame_1) != 1:
                continue
            for permutation in ((0, 1), (1, 0)):
                assigned = (targets[permutation[0]], targets[permutation[1]])
                restores = (
                    pauli_multiply(assigned[0], frame_0),
                    pauli_multiply(assigned[1], frame_1),
                )
                for central_branch in (0, 1):
                    raw_count += 1
                    multipliers = (2, 4) if central_branch == 0 else (4, 2)
                    frame_cost = (
                        multipliers[0] * (pauli_weight(frame_0) - 1)
                        + multipliers[1] * (pauli_weight(frame_1) - 1)
                    )
                    witness = {
                        "frames": [frame_0, frame_1],
                        "target_permutation": list(permutation),
                        "central_branch": central_branch,
                        "frame_cost": frame_cost,
                        "restores": list(restores),
                    }
                    incumbent = best_by_restore.get(restores)
                    ordering = (frame_cost, json.dumps(witness, sort_keys=True))
                    if incumbent is None or ordering < incumbent[0]:
                        best_by_restore[restores] = (ordering, witness)
    return ({key: value[1] for key, value in best_by_restore.items()}, raw_count)


@lru_cache(maxsize=None)
def solve_frozen_two_qubit_instance(max_frame_support: Optional[int]) -> dict:
    """Exact clean-room enumeration for the independently chosen lower witness."""
    n = 2
    effective_limit = n if max_frame_support is None else max_frame_support
    if effective_limit < 1:
        return {
            "terminal": "INFEASIBLE",
            "max_frame_support": max_frame_support,
            "optimum": None,
            "optimum_witness_count": 0,
            "raw_block_configurations": 0,
            "compressed_global_states": 0,
            "witness": None,
        }

    all_nonidentity = tuple(pauli for pauli in _all_paulis(n) if pauli != "II")
    optimum = None
    winner = None
    optimum_witness_count = 0
    raw_block_configurations = 0
    compressed_global_states = 0

    for tag in all_nonidentity:
        for orientation in ((0, 1), (1, 0)):
            state_maps = []
            raw_counts = []
            for targets in FROZEN_TARGETS:
                state_map, raw_count = _block_states(
                    targets, tag, orientation, effective_limit
                )
                state_maps.append(state_map)
                raw_counts.append(raw_count)
            raw_block_configurations += sum(raw_counts)
            if any(not state_map for state_map in state_maps):
                continue
            compressed_global_states += (
                len(state_maps[0]) * len(state_maps[1]) * len(state_maps[2])
            )
            for restores_0, block_0 in state_maps[0].items():
                for restores_1, block_1 in state_maps[1].items():
                    for restores_2, block_2 in state_maps[2].items():
                        blocks = (block_0, block_1, block_2)
                        restores = (restores_0, restores_1, restores_2)
                        tag_cost = 2 * pauli_weight(tag)
                        donor_cost = restore_cost(restores)
                        value = (
                            tag_cost
                            + sum(block["frame_cost"] for block in blocks)
                            + donor_cost
                        )
                        if optimum is not None and value > optimum:
                            continue
                        candidate = {
                            "tag": tag,
                            "orientation": list(orientation),
                            "blocks": list(blocks),
                            "tag_cost": tag_cost,
                            "restore_cost": donor_cost,
                            "total_cost": value,
                            "maximum_frame_support": max(
                                pauli_weight(frame)
                                for block in blocks
                                for frame in block["frames"]
                            ),
                        }
                        candidate_key = json.dumps(candidate, sort_keys=True)
                        if optimum is None or value < optimum:
                            optimum = value
                            winner = (candidate_key, candidate)
                            optimum_witness_count = 1
                        elif value == optimum:
                            optimum_witness_count += 1
                            if winner is None or candidate_key < winner[0]:
                                winner = (candidate_key, candidate)

    return {
        "terminal": "EXACT_OPTIMUM" if optimum is not None else "INFEASIBLE",
        "max_frame_support": max_frame_support,
        "optimum": optimum,
        "optimum_witness_count": optimum_witness_count,
        "raw_block_configurations": raw_block_configurations,
        "compressed_global_states": compressed_global_states,
        "witness": winner[1] if winner else None,
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_blob_sha1(path: Path) -> str:
    content = path.read_bytes()
    return hashlib.sha1(f"blob {len(content)}\0".encode() + content).hexdigest()


def build_phase1_receipt() -> dict:
    manuscript = REPO_ROOT / "papers/Q-paper-01-tare-expressivity/MANUSCRIPT_V3_REFINED.md"
    ledger = REPO_ROOT / "papers/Q-paper-01-tare-expressivity/CLAIM_LEDGER_V3.md"
    support_zero = solve_frozen_two_qubit_instance(0)
    support_one = solve_frozen_two_qubit_instance(1)
    unrestricted = solve_frozen_two_qubit_instance(None)
    maximum_restore_increase, restore_witness = maximum_single_donor_f3_increase()
    return {
        "schema_version": "q1-a-phase1-reconstruction-r9-v1",
        "source_binding": {
            "repository": "https://github.com/SzeChunYiu/ORION.git",
            "commit": SOURCE_COMMIT,
            "manuscript": {
                "path": "papers/Q-paper-01-tare-expressivity/MANUSCRIPT_V3_REFINED.md",
                "git_blob_sha1": _git_blob_sha1(manuscript),
                "sha256": _sha256(manuscript),
                "phase1_read_scope": "neutral definitions and feasibility lines 66-107 only",
            },
            "claim_ledger": {
                "path": "papers/Q-paper-01-tare-expressivity/CLAIM_LEDGER_V3.md",
                "git_blob_sha1": _git_blob_sha1(ledger),
                "sha256": _sha256(ledger),
            },
            "registered_proof": {
                "path": "papers/Q-paper-01-tare-expressivity/HUMAN_PROOF_R6S_2026-08-22.md",
                "git_blob_sha1": "a22754e8afef0e9914b75b37f0aee673ccd2ca95",
                "sha256": "ad4f3704cfac4569b74725cb8608ed5f5ba88b847d2d8a2820b3e184d9d1dae6",
                "phase1_content_access": "FORBIDDEN_NOT_READ",
            },
            "q1_paper_tree_sha1": "d805ae36e6ad0f8844bd12aba32b3efae001dfce",
            "registered_implementation_tree_sha1": "81c0d03d5f3da35c6f35dfdd6d523ac8f180847c",
        },
        "frozen_claim": {
            "instance_family": "six n-qubit phase-free Pauli targets in three ordered two-term blocks",
            "feasibility": "nonidentity anticommuting frame pair per block; one shared Tag; common opposite branch-Tag symplectic orientation; fixed assignment, central branch, partner, other blocks during exchange",
            "invariant": "exact Pauli target semantics through Restore=P*R and unchanged frame-partner and frame-Tag symplectic parities",
            "objective": "sum m_jk(w(R_jk)-1), m_jk in {2,4}; plus 2w(S); plus coordinate-local donor F3 over the three Restores of each branch",
            "support_functional": "maximum Pauli support of the six frame Paulis",
            "upper_statement": "for every admitted finite-n instance, an exact optimum exists with all frame supports at most two",
            "sharpness_statement": "the least uniform cap is two; the frozen n=2 witness has unrestricted optimum 5 and support-at-most-one optimum 6",
            "theorem_kind": "existential normal-form theorem with a constructive descent; not a runtime or production-resource theorem",
        },
        "dependency_dag": {
            "nodes": [
                "D0_PHASE_FREE_PAULI_ALGEBRA",
                "D1_FROZEN_FEASIBILITY_AND_OBJECTIVE",
                "L1_TWO_BIT_SIGNATURE_ENCODING",
                "L2_PROPER_ZERO_SUM_SUBSET",
                "L3_FEASIBILITY_PRESERVATION",
                "L4_SINGLE_DONOR_F3_LIPSCHITZ_TWO",
                "L5_NONINCREASING_EXCHANGE",
                "L6_TERMINATING_OPTIMUM_DESCENT",
                "U1_SUPPORT_TWO_UPPER_BOUND",
                "W1_TWO_QUBIT_SHARPNESS_WITNESS",
                "L7_EXACT_FINITE_MIN_PLUS_ENUMERATION",
                "W2_SUPPORT_ONE_LOWER_BOUND",
                "T1_KAPPA_R6M_EQUALS_TWO",
            ],
            "edges": [
                ["D0_PHASE_FREE_PAULI_ALGEBRA", "L1_TWO_BIT_SIGNATURE_ENCODING"],
                ["D1_FROZEN_FEASIBILITY_AND_OBJECTIVE", "L1_TWO_BIT_SIGNATURE_ENCODING"],
                ["L1_TWO_BIT_SIGNATURE_ENCODING", "L2_PROPER_ZERO_SUM_SUBSET"],
                ["L2_PROPER_ZERO_SUM_SUBSET", "L3_FEASIBILITY_PRESERVATION"],
                ["D1_FROZEN_FEASIBILITY_AND_OBJECTIVE", "L3_FEASIBILITY_PRESERVATION"],
                ["D1_FROZEN_FEASIBILITY_AND_OBJECTIVE", "L4_SINGLE_DONOR_F3_LIPSCHITZ_TWO"],
                ["L3_FEASIBILITY_PRESERVATION", "L5_NONINCREASING_EXCHANGE"],
                ["L4_SINGLE_DONOR_F3_LIPSCHITZ_TWO", "L5_NONINCREASING_EXCHANGE"],
                ["L5_NONINCREASING_EXCHANGE", "L6_TERMINATING_OPTIMUM_DESCENT"],
                ["L6_TERMINATING_OPTIMUM_DESCENT", "U1_SUPPORT_TWO_UPPER_BOUND"],
                ["W1_TWO_QUBIT_SHARPNESS_WITNESS", "L7_EXACT_FINITE_MIN_PLUS_ENUMERATION"],
                ["L7_EXACT_FINITE_MIN_PLUS_ENUMERATION", "W2_SUPPORT_ONE_LOWER_BOUND"],
                ["U1_SUPPORT_TWO_UPPER_BOUND", "T1_KAPPA_R6M_EQUALS_TWO"],
                ["W2_SUPPORT_ONE_LOWER_BOUND", "T1_KAPPA_R6M_EQUALS_TWO"],
            ],
        },
        "attacks": {
            "support_0": support_zero,
            "support_1": support_one,
            "support_2_unrestricted_at_n2": unrestricted,
            "support_3_and_above": "proper zero-sum exchange strictly reduces frame support while preserving feasibility and nonincreasing objective",
            "degeneracies": "00 signatures delete singly; duplicate signatures delete in pairs; full deletion is forbidden",
            "aliases": "Tag/frame/partner aliases are covered because only symplectic signature bits enter the exchange",
            "ties": "m=2 and maximum F3 penalty produce an objective tie, retained as an optimum-preserving exchange",
            "vanishing_coefficients": "numeric target amplitudes are absent from the frozen grammar and objective; any amplitude-dependent admission rule is outside this theorem",
        },
        "hostile_controls": {
            "maximum_single_donor_f3_increase": maximum_restore_increase,
            "maximum_single_donor_f3_witness": restore_witness,
            "odd_partner_parity_removed": {
                "signatures": [[0, 1], [1, 0], [1, 1]],
                "total": [0, 0],
                "proper_zero_sum_subset": None,
                "terminal": "EXPECTED_PREMISE_FAILURE",
            },
            "objective_multiplier_below_two": objective_multiplier_control(),
            "broken_shared_tag_or_multi_frame_edit": "REJECTED_OUTSIDE_ONE-FRAME_UNCHANGED-TAG_EXCHANGE",
        },
        "phase_1_access_log": {
            "allowed": [
                "CLAIM_LEDGER_V3.md",
                "MANUSCRIPT_V3_REFINED.md lines 66-107 neutral definitions and feasibility",
                "INDEPENDENT_SUPPORT_TWO_AUDIT_PACKET_R9.md",
            ],
            "forbidden_not_read": [
                "HUMAN_PROOF_R6S_2026-08-22.md content",
                "MANUSCRIPT_V3_REFINED.md proof sections 3-4",
                "registered ORION-Q solver/canonicalizer/checker source",
                "registered ORION-Q result receipts",
            ],
        },
        "phase_1_terminal": "PHASE1_LOCKED_BEFORE_REGISTERED_PROOF",
        "independence": {
            "procedure": "clean-room same-program reconstruction from neutral definitions and claim ledger; transparent independent n=2 enumeration",
            "same_program_internal": True,
            "external_independence": "CANNOT_CHECK",
        },
        "authority": {
            "theorem_scope_only": True,
            "production_resource_interpretation": "CANNOT_CHECK",
            "novelty": "CANNOT_CHECK",
            "journal_authority": "CANNOT_CHECK",
        },
    }


def main() -> int:
    receipt_path = HERE / "Q1_A_PHASE1_RECONSTRUCTION_RECEIPT_R9.json"
    expected = build_phase1_receipt()
    if not receipt_path.exists():
        print(json.dumps(expected, indent=2, sort_keys=True))
        return 2
    committed = json.loads(receipt_path.read_text())
    if committed != expected:
        print("Q1_A_PHASE1_RECEIPT_MISMATCH")
        return 1
    print("Q1_A_PHASE1_RECEIPT_VALID")
    print(json.dumps({
        "phase_1_terminal": committed["phase_1_terminal"],
        "unrestricted_optimum": committed["attacks"]["support_2_unrestricted_at_n2"]["optimum"],
        "support_one_optimum": committed["attacks"]["support_1"]["optimum"],
        "external_independence": committed["independence"]["external_independence"],
        "journal_authority": committed["authority"]["journal_authority"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
