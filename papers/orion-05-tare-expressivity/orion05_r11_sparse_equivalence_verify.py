#!/usr/bin/env python3
"""Hostile verification for the ORION-05 R11 sparse direct solver.

The solver under test is standard-library-only and separate from the frozen
production DP. This verifier uses that DP as a separate exact optimum oracle,
but reuses some sparse-solver algebra for witness checks; it is not claimed to
be a structurally independent implementation of every witness identity.
"""

from __future__ import annotations

import ast
import hashlib
import importlib
import itertools
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
Q_SOURCE = ROOT / "research" / "extensions" / "orion-q"
SOLVER_PATH = HERE / "orion05_r11_sparse_direct_solver.py"
RESULT_PATH = HERE / "ORION05_R11_SPARSE_EQUIVALENCE_RESULTS.json"
THEOREM_PATH = HERE / "ORION05_R11_EXACT_O_N9_DIRECT_SOLVER_THEOREM.md"
STATUS_PATH = HERE / "ORION05_R11_ROUND1_STATUS.json"
DEVELOPMENT_PATH = (
    ROOT
    / "development"
    / "orion-05-r11-sparse-direct-solver-2026-08-27"
    / "DEVELOPMENT_PACKET.md"
)
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "orion05-r11-sparse-theorem.yml"
BASE_COMMIT = "63c36a20c8120fcd45469bbe5708b9e9aadfe923"
BASE_TREE = "25980098d01d69faf02feb8f03f1e6be27e6c32e"
TERMINAL = "ORION05_R11_EXACT_O_N9_DIRECT_SOLVER_THEOREM__FROZEN_R6M_ONLY"
SCIENCE_V1_PATH = "research/orion-01-05-convergence-v1/SCIENCE_STATUS_V1.json"
SUPERSESSION_V1_PATH = (
    "research/orion-01-05-convergence-v1/SUPERSESSION_PLAN_V1.json"
)
Q1_XOVER_COMMIT = "272f2a1aa7b63d409fc460b35bb89e4aa8b5dcbb"

EXPECTED_V1_BINDINGS = {
    SCIENCE_V1_PATH: {
        "git_blob": "b8e65dfd421e2188ed41f1f3595f05c05b57c1cf",
        "sha256": "ba51c854a5a0b2dd37da513aada1173399cc0b53139fce039ae8f805b2bcb8fb",
    },
    SUPERSESSION_V1_PATH: {
        "git_blob": "7512cea3d6f1f069bc03f4a13f0073f62c4e2cd3",
        "sha256": "8f6c6d1d42a2ff55470b876a4bd33755f6a014f3522851f1714abd48c683a26b",
    },
}

EXPECTED_Q1_XOVER_BINDINGS = {
    "research/extensions/orion-q/Q1_XOVER_RESULTS_V1.json": {
        "git_blob": "40a92fe215c0585310d87fcd027bd12069f42f45",
        "sha256": "05eb59f6635ebccd8ebcebc79f3b9646aab6fce1d9852735c67d01f9cd3821f1",
    },
    "research/extensions/orion-q/Q1_XOVER_TIMING_V1.json": {
        "git_blob": "ed2d51bb7ea78efbead015ce6eaa2aacfff65f43",
        "sha256": "1949a1174c318a643cbe47740438f22f25ff4db96e69dac0e44ffbb4e66bd4b7",
    },
    "research/extensions/orion-q/Q1_XOVER_PROTOCOL_V1.md": {
        "git_blob": "a9b723fa8e4ff485390412fe85f16d778a1d45ad",
        "sha256": "6eded50cce8f546afbd59ace8bd3f054270779518df222b1fa3747eb91a197a1",
    },
    "research/extensions/orion-q/q1_crossover_evaluation.py": {
        "git_blob": "819c4b19c204fc01b826a79eb6446e0fac9de4f5",
        "sha256": "56ec39f8e95074a3ab44d012c1e33112881b75edbcb4a1563be70e0706021d88",
    },
}

EXPECTED_FROZEN_BINDINGS = {
    "sparse_solver": "642cc67a280abb2ca06089ae01510040f1f598ec638d525ddcc29fae8c6b25d3",
    "frozen_r6m_dp": "7c6579db5f4afbc1738e8b3d96aa3730023bc3831d1fc4950ab34e071c0e3d90",
    "frozen_r6m_protocol": "33465bd585f09a8d936aaa38d90beb4916943f826eb970bfeced102eeac93986",
    "r6s_human_proof": "ad4f3704cfac4569b74725cb8608ed5f5ba88b847d2d8a2820b3e184d9d1dae6",
    "r6s_receipt": "b6d72913c3bd42d9c822eace19563378c046e620d7b9641ec7d818fbcc6b9875",
    "r6o_adverse_receipt": "e40e7a948061b9e4b647ba091c04a73b39cffa619ca829bbf4cef4beacdad352",
    "r6p_support_two_receipt": "3eef07d16353b606a133d7fb977d5039ad1c639c7a531a47ae82be4be9051190",
    "qg21_current_resource_adverse_receipt": "fb1dfea5ef16c91f17045f173d5f8522be7df35db2c15714ff0a56eecad97ea3",
}

EXPECTED_CHANGED_PATHS = {
    ".github/workflows/orion05-r11-sparse-theorem.yml",
    "development/orion-05-r11-sparse-direct-solver-2026-08-27/DEVELOPMENT_PACKET.md",
    "papers/orion-05-tare-expressivity/ORION05_R11_EXACT_O_N9_DIRECT_SOLVER_THEOREM.md",
    "papers/orion-05-tare-expressivity/ORION05_R11_ROUND1_STATUS.json",
    "papers/orion-05-tare-expressivity/ORION05_R11_SPARSE_EQUIVALENCE_RESULTS.json",
    "papers/orion-05-tare-expressivity/orion05_r11_sparse_direct_solver.py",
    "papers/orion-05-tare-expressivity/orion05_r11_sparse_equivalence_verify.py",
}
PROTECTED_PREFIXES = (
    "research/orion-v1-freeze/",
    "research/extensions/p9-structured-neural/",
    "papers/orion-19-structured-epistemic-learning/",
    "papers/candidates/paper-09-structured-epistemic-learning/",
    "development/p1-scienceagentbench-protected-",
    "development/p9-",
)
PROTECTED_BLOB_GUARDS = {
    "research/extensions/p9-structured-neural/D1_PROTOCOL_V1.json": "a92de3d2a568805aa5f442bb3126731af4175c0a",
    "research/extensions/p9-structured-neural/P9_FINAL_SCOPE_PROTOCOL_V1.json": "39a4368dc1978f1294c24ea12cdcce392b7463c7",
    "research/extensions/p9-structured-neural/successors/S3_RESULT_PROTOCOL_V1.json": "a2c82973a44858aff5ae2f3909af24d1616deb0f",
    "papers/orion-19-structured-epistemic-learning/evidence/P9_D1V1_2_PINNED_REPLAY_R1_2026-08-24.json": "9791e3597fb59041b9cbe8d127a3c98e685e9279",
    "development/p1-scienceagentbench-protected-rr1-direct-route-freeze-v1-2026-08-24/TUPLE_FREEZE_V1.json": "2140d22f315ce5a2b2c732dabffe640a031139db",
}

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(Q_SOURCE))

import orion05_r11_sparse_direct_solver as sparse  # noqa: E402


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True, stderr=subprocess.STDOUT
    ).strip()


def git_file_bytes(commit: str, path: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{commit}:{path}"], cwd=ROOT, stderr=subprocess.STDOUT
    )


def json_pointer_get(value: Any, pointer: str) -> Any:
    if pointer == "":
        return value
    if not pointer.startswith("/"):
        raise AssertionError({"invalid_json_pointer": pointer})
    current = value
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def _working_tree_records() -> list[tuple[str, str]]:
    raw = git("status", "--porcelain=v1", "--untracked-files=all")
    records = []
    for line in raw.splitlines():
        code, path = line[:2], line[3:]
        if " -> " in path or "R" in code or "C" in code or "D" in code:
            raise AssertionError({"rename_copy_or_delete_not_allowed": line})
        status = "A" if code == "??" or "A" in code else "M"
        records.append((status, path))
    return records


def _committed_records() -> list[tuple[str, str]]:
    raw = git("diff", "--name-status", "-M", "-C", f"{BASE_COMMIT}..HEAD")
    records = []
    for line in raw.splitlines():
        fields = line.split("\t")
        if len(fields) != 2:
            raise AssertionError({"rename_copy_or_delete_not_allowed": line})
        records.append((fields[0], fields[1]))
    return records


def verify_change_scope() -> dict[str, Any]:
    observed_base_tree = git("rev-parse", f"{BASE_COMMIT}^{{tree}}")
    if observed_base_tree != BASE_TREE:
        raise AssertionError(
            {"base_tree_drift": {"expected": BASE_TREE, "actual": observed_base_tree}}
        )
    head = git("rev-parse", "HEAD")
    merge_base = git("merge-base", BASE_COMMIT, head)
    if merge_base != BASE_COMMIT:
        raise AssertionError(
            {"not_a_clean_current_main_descendant": {"base": BASE_COMMIT, "head": head}}
        )
    records = _working_tree_records() if head == BASE_COMMIT else _committed_records()
    actual = {path for _, path in records}
    if len(records) != len(actual):
        raise AssertionError({"duplicate_changed_path_record": records})
    if actual != EXPECTED_CHANGED_PATHS:
        raise AssertionError(
            {
                "changed_path_mismatch": {
                    "missing": sorted(EXPECTED_CHANGED_PATHS - actual),
                    "extra": sorted(actual - EXPECTED_CHANGED_PATHS),
                }
            }
        )
    if any(status != "A" for status, _ in records):
        raise AssertionError({"theorem_successor_must_be_additive_only": records})
    protected_hits = sorted(
        path for path in actual if path.startswith(PROTECTED_PREFIXES)
    )
    if protected_hits:
        raise AssertionError({"protected_path_changed": protected_hits})
    for path, expected_blob in PROTECTED_BLOB_GUARDS.items():
        base_blob = git("rev-parse", f"{BASE_COMMIT}:{path}")
        head_blob = git("rev-parse", f"HEAD:{path}")
        if base_blob != expected_blob or head_blob != expected_blob:
            raise AssertionError(
                {
                    "protected_blob_drift": {
                        "path": path,
                        "expected": expected_blob,
                        "base": base_blob,
                        "head": head_blob,
                    }
                }
            )
    return {
        "base_commit": BASE_COMMIT,
        "base_tree": BASE_TREE,
        "lineage": "EXACT_BASE_DESCENDANT",
        "changed_paths": sorted(actual),
        "additive_only": True,
        "protected_unchanged": True,
    }


def global_key_to_dense(key: Sequence[int], n: int) -> sparse.DensePauli:
    x, z = int(key[0]), int(key[1])
    return tuple(sparse.BITS_CODE[((x >> q) & 1, (z >> q) & 1)] for q in range(n))


def dense_to_global_key(pauli: Sequence[int]) -> tuple[int, int]:
    x = z = 0
    for q, letter in enumerate(pauli):
        bx, bz = sparse.CODE_BITS[int(letter)]
        x |= bx << q
        z |= bz << q
    return x, z


def target_pairs_from_dense(targets: Sequence[Sequence[int]]):
    return tuple((tuple(targets[2 * j]), tuple(targets[2 * j + 1])) for j in range(3))


def naive_pair_set(n: int):
    paulis = [
        tuple(row)
        for row in itertools.product(range(4), repeat=n)
        if 1 <= sum(letter != 0 for letter in row) <= 2
    ]
    pairs = {
        (a, b)
        for a in paulis
        for b in paulis
        if sum(sparse.local_symp(x, y) for x, y in zip(a, b)) & 1
    }
    return paulis, pairs


def constructive_pair_checks() -> dict[str, Any]:
    rows = []
    for n in range(1, 7):
        paulis, naive = naive_pair_set(n)
        generated = tuple(sparse.ordered_anticommuting_pairs(n))
        generated_dense = {
            (
                sparse.sparse_to_dense(pair.r0, n),
                sparse.sparse_to_dense(pair.r1, n),
            )
            for pair in generated
        }
        if len(generated) != len(generated_dense):
            raise AssertionError({"constructive_generator_duplicate": n})
        if generated_dense != naive:
            raise AssertionError(
                {
                    "constructive_generator_set_mismatch": n,
                    "missing": len(naive - generated_dense),
                    "extra": len(generated_dense - naive),
                }
            )
        formula = sparse.pair_count_formula(n)
        if len(generated) != formula:
            raise AssertionError({"pair_formula_mismatch": [n, len(generated), formula]})
        per_first = {}
        for first in paulis:
            degree = sum((first, second) in naive for second in paulis)
            weight = sum(letter != 0 for letter in first)
            expected = 6 * n - 4 if weight == 1 else 12 * n - 16
            if degree != expected:
                raise AssertionError({"per_first_degree_mismatch": [n, first, degree, expected]})
            per_first.setdefault(weight, set()).add(degree)
        if any(len(pair.active) > 3 for pair in generated):
            raise AssertionError({"single_pair_active_union_exceeds_three": n})
        rows.append(
            {
                "n": n,
                "paulis_support_one_or_two": len(paulis),
                "ordered_anticommuting_pairs": len(generated),
                "formula": formula,
                "per_first_degrees": {
                    str(weight): sorted(values) for weight, values in per_first.items()
                },
                "duplicate_free": True,
                "naive_set_equal": True,
                "pair_union_at_most_three": True,
            }
        )

    # Attainability of the 3-per-pair and 9-for-three-pairs bounds.
    sharp_pairs = tuple(
        sparse.FramePair(
            ((base, 1), (base + 1, 1)),
            ((base, 3), (base + 2, 1)),
        )
        for base in (0, 3, 6)
    )
    if not all(sparse.sparse_symp(pair.r0, pair.r1) == 1 for pair in sharp_pairs):
        raise AssertionError("constructed union-nine pairs are not anticommuting")
    if tuple(len(pair.active) for pair in sharp_pairs) != (3, 3, 3):
        raise AssertionError("single-pair union-three boundary not attained")
    if len(sparse.active_union(sharp_pairs)) != 9:
        raise AssertionError("three-pair union-nine boundary not attained")
    return {
        "n1_through_n6": rows,
        "pair_union_three_attained": True,
        "three_pair_union_nine_attained": True,
    }


def brute_tag_minimum(n: int, pairs, orientation):
    frames = tuple(frame for pair in pairs for frame in (pair.r0, pair.r1))
    best = None
    for dense in itertools.product(range(4), repeat=n):
        tag = sparse.dense_to_sparse(dense)
        got = tuple(sparse.sparse_symp(tag, frame) for frame in frames)
        rhs = tuple(orientation[k % 2] for k in range(6))
        if got == rhs:
            key = (len(tag), dense)
            if best is None or key < best[0]:
                best = (key, tag)
    return None if best is None else (best[0][0], best[1])


def deterministic_targets(n: int, salt: int):
    return tuple(
        tuple((q + 2 * slot + salt * (slot + 1)) % 4 for q in range(n)) for slot in range(6)
    )


def sample_indices(size: int) -> tuple[int, ...]:
    return tuple(sorted({0, size - 1, size // 3, (2 * size) // 3}))


def tag_and_preprocessing_checks() -> dict[str, Any]:
    tag_cases = 0
    feasible = 0
    infeasible = 0
    baseline_cases = 0
    max_tag_weight = 0
    max_rank = 0
    for n in range(1, 6):
        grammar = sparse.SparseGrammar(n)
        idx = sample_indices(len(grammar.pairs))
        for ia, ib, ic in itertools.product(idx, repeat=3):
            pairs = (grammar.pairs[ia], grammar.pairs[ib], grammar.pairs[ic])
            if len(sparse.active_union(pairs)) > min(n, 9):
                raise AssertionError({"active_union_bound_failed": [n, ia, ib, ic]})
            for orientation in sparse.ORIENTATIONS:
                direct = sparse.minimum_tag(pairs, orientation)
                brute = brute_tag_minimum(n, pairs, orientation)
                accelerated = grammar.minimum_tag_indices((ia, ib, ic), orientation)
                if (None if direct is None else direct[0]) != (None if brute is None else brute[0]):
                    raise AssertionError(
                        {
                            "full_vs_active_tag_minimum_mismatch": [
                                n,
                                ia,
                                ib,
                                ic,
                                orientation,
                                direct,
                                brute,
                            ]
                        }
                    )
                if (None if accelerated is None else accelerated[0]) != (
                    None if direct is None else direct[0]
                ):
                    raise AssertionError(
                        {"small_n_tag_accelerator_mismatch": [n, ia, ib, ic, orientation]}
                    )
                tag_cases += 1
                if direct is None:
                    infeasible += 1
                else:
                    rank = sparse.tag_constraint_rank(pairs)
                    if not (direct[0] <= rank <= 6):
                        raise AssertionError(
                            {"tag_rank_support_bound_failed": [n, direct[0], rank]}
                        )
                    if not set(q for q, _ in direct[1]).issubset(sparse.active_union(pairs)):
                        raise AssertionError("minimum Tag escaped the active union")
                    feasible += 1
                    max_tag_weight = max(max_tag_weight, direct[0])
                    max_rank = max(max_rank, rank)

            for salt in (0, 1, 3):
                targets = deterministic_targets(n, salt)
                prep = sparse.preprocess_targets(targets)
                active_cost = sparse.restore_cost_sparse(prep, pairs)
                full_cost = sparse.restore_cost_full_scan(targets, pairs)
                if active_cost != full_cost:
                    raise AssertionError(
                        {"baseline_active_correction_mismatch": [n, ia, ib, ic, salt]}
                    )
                baseline_cases += 1

    # A long target exercises far-apart sparse indices.  Preprocessing scans the
    # input once; candidate scoring changes only nine active coordinates.
    long_n = 257
    long_pairs = tuple(
        sparse.FramePair(
            ((base, 1), (base + 1, 1)),
            ((base, 3), (base + 2, 1)),
        )
        for base in (0, 100, 254)
    )
    long_targets = deterministic_targets(long_n, 5)
    long_prep = sparse.preprocess_targets(long_targets)
    if sparse.restore_cost_sparse(long_prep, long_pairs) != sparse.restore_cost_full_scan(
        long_targets, long_pairs
    ):
        raise AssertionError("long-target baseline correction mismatch")
    if len(sparse.active_union(long_pairs)) != 9:
        raise AssertionError("long-target hostile did not exercise nine active coordinates")
    baseline_cases += 1
    return {
        "full_vs_active_tag_cases": tag_cases,
        "feasible_tag_cases": feasible,
        "infeasible_tag_cases": infeasible,
        "maximum_observed_minimum_tag_weight": max_tag_weight,
        "maximum_observed_constraint_rank": max_rank,
        "tag_support_le_rank_le_six_all_feasible": True,
        "tag_confined_to_active_union_all_feasible": True,
        "baseline_plus_active_correction_cases": baseline_cases,
        "long_target_n": long_n,
        "long_target_active_coordinates": 9,
    }


def source_independence_check() -> dict[str, Any]:
    source = SOLVER_PATH.read_text()
    tree = ast.parse(source)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add((node.module or "").split(".")[0])
    allowed = {"__future__", "dataclasses", "itertools", "typing"}
    if not imports.issubset(allowed):
        raise AssertionError({"non_stdlib_or_unapproved_import": sorted(imports - allowed)})
    forbidden_calls = {
        "_solve_config",
        "_local_table",
        "exact_r6m_matching",
        "XOR512",
        "PARITY_STATES",
    }
    referenced_names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)} | {
        node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
    }
    if forbidden_calls & referenced_names:
        raise AssertionError(
            {"production_dp_symbol_referenced": sorted(forbidden_calls & referenced_names)}
        )
    return {
        "imports": sorted(imports),
        "standard_library_only": True,
        "production_dp_symbols_absent": True,
        "solver_source_sha256": hashlib.sha256(source.encode()).hexdigest(),
    }


def _production_module():
    return importlib.import_module("max_r6m_exact_three_tare2_shared_factor_dp")


def decode_n1_option(option: int):
    return tuple((option >> (2 * (6 - slot))) & 3 for slot in range(7))


def separate_ordered_witness_cost(targets, frames_and_tag, centrals, orientation):
    frames = tuple(sparse.dense_to_sparse((letter,)) for letter in frames_and_tag[:6])
    pairs = tuple(sparse.FramePair(frames[2 * block], frames[2 * block + 1]) for block in range(3))
    tag = sparse.dense_to_sparse((frames_and_tag[6],))
    labels = tuple(
        (sparse.sparse_symp(tag, pair.r0), sparse.sparse_symp(tag, pair.r1)) for pair in pairs
    )
    if any(label != orientation for label in labels):
        raise AssertionError({"production_n1_witness_label_failure": labels})
    if any(sparse.sparse_symp(pair.r0, pair.r1) != 1 for pair in pairs):
        raise AssertionError("production n1 witness frame anticommutation failure")
    c_frame = sparse.frame_cost(pairs, centrals)
    c_tag = 2 * len(tag)
    c_restore = sparse.restore_cost_full_scan(targets, pairs)
    witness = sparse.SparseWitness(
        c_frame + c_tag + c_restore,
        pairs,
        tag,
        orientation,
        centrals,
        (0, 0),
        c_frame,
        c_tag,
        c_restore,
    )
    target_pairs = target_pairs_from_dense(targets)
    phase_certificate = sparse.build_phase_certificate(target_pairs, witness)
    return (
        sparse.frame_cost(pairs, centrals)
        + 2 * len(tag)
        + sparse.restore_cost_full_scan(targets, pairs)
    ), all(phase_certificate["checks"].values())


def complete_n1_equivalence(dp) -> dict[str, Any]:
    grammar = sparse.SparseGrammar(1)
    instances = 0
    configuration_orientations = 0
    cost_matches = 0
    sparse_witnesses_valid = 0
    production_witnesses_valid = 0
    sparse_phase_certificates_valid = 0
    production_phase_certificates_valid = 0
    for p6 in itertools.product(range(4), repeat=6):
        targets = tuple((letter,) for letter in p6)
        target_pairs = target_pairs_from_dense(targets)
        for centrals in sparse.CENTRALS:
            local_cost, local_option = dp._local_table(tuple(p6), centrals)
            for orientation in sparse.ORIENTATIONS:
                state = 0b111 | (orientation[0] << 7) | (orientation[1] << 8)
                production_cost = int(local_cost[state]) - 18
                if production_cost >= sparse.INF // 2:
                    raise AssertionError(
                        {"production_n1_accepting_state_unreachable": [p6, centrals, orientation]}
                    )
                witness = sparse.solve_ordered_targets(
                    targets,
                    grammar=grammar,
                    centrals=centrals,
                    orientation=orientation,
                )
                if witness.cost != production_cost:
                    raise AssertionError(
                        {
                            "complete_n1_cost_mismatch": [
                                p6,
                                centrals,
                                orientation,
                                witness.cost,
                                production_cost,
                            ]
                        }
                    )
                checks = sparse.verify_witness(target_pairs, witness)
                if not all(checks.values()):
                    raise AssertionError({"complete_n1_sparse_witness_invalid": checks})
                sparse_phase = sparse.build_phase_certificate(target_pairs, witness)
                if not all(sparse_phase["checks"].values()):
                    raise AssertionError(
                        {"complete_n1_sparse_phase_certificate_invalid": sparse_phase["checks"]}
                    )
                option = int(local_option[state])
                if option < 0:
                    raise AssertionError("production n1 local optimum has no option")
                option_cost, option_phase_valid = separate_ordered_witness_cost(
                    targets, decode_n1_option(option), centrals, orientation
                )
                if option_cost != production_cost:
                    raise AssertionError(
                        {
                            "complete_n1_production_witness_cost_mismatch": [
                                option_cost,
                                production_cost,
                            ]
                        }
                    )
                if not option_phase_valid:
                    raise AssertionError("complete n1 production phase certificate invalid")
                configuration_orientations += 1
                cost_matches += 1
                sparse_witnesses_valid += 1
                production_witnesses_valid += 1
                sparse_phase_certificates_valid += 1
                production_phase_certificates_valid += 1
        dp._local_table.cache_clear()
        instances += 1
    return {
        "target_six_tuples": instances,
        "central_orientation_slices": configuration_orientations,
        "exact_cost_matches": cost_matches,
        "sparse_optimum_witnesses_separately_valid": sparse_witnesses_valid,
        "production_optimum_witnesses_separately_valid": production_witnesses_valid,
        "sparse_phase_certificates_separately_valid": sparse_phase_certificates_valid,
        "production_phase_certificates_separately_valid": production_phase_certificates_valid,
        "witness_equivalence_definition": "both feasible witnesses separately recompute the same exact optimum; serialized tie identity is not required",
        "all_pass": (
            instances == 4096
            and configuration_orientations == 4096 * 8 * 2
            and cost_matches == configuration_orientations
            and sparse_witnesses_valid == configuration_orientations
            and production_witnesses_valid == configuration_orientations
            and sparse_phase_certificates_valid == configuration_orientations
            and production_phase_certificates_valid == configuration_orientations
        ),
    }


def separately_check_production_witness(target_pairs_global, witness, n: int):
    target_pairs = tuple(
        tuple(global_key_to_dense(target, n) for target in pair) for pair in target_pairs_global
    )
    permutations = (
        int(witness["relative_permutation_B"]),
        int(witness["relative_permutation_C"]),
    )
    variants = dict(sparse._ordered_variants(target_pairs))
    prep = variants[permutations]
    frames_global = tuple(tuple(item) for block in ("A", "B", "C") for item in witness["R"][block])
    frames = tuple(sparse.dense_to_sparse(global_key_to_dense(key, n)) for key in frames_global)
    pairs = tuple(sparse.FramePair(frames[2 * block], frames[2 * block + 1]) for block in range(3))
    tag = sparse.dense_to_sparse(global_key_to_dense(witness["S"], n))
    orientation = tuple(int(x) for x in witness["common_labels"])
    centrals = tuple(int(x) for x in witness["centrals"])
    labels = tuple(
        (sparse.sparse_symp(tag, pair.r0), sparse.sparse_symp(tag, pair.r1)) for pair in pairs
    )
    recomputed = (
        sparse.frame_cost(pairs, centrals)
        + 2 * len(tag)
        + sparse.restore_cost_full_scan(prep.targets, pairs)
    )
    reconstructed = sparse.SparseWitness(
        recomputed,
        pairs,
        tag,
        orientation,
        centrals,
        permutations,
        sparse.frame_cost(pairs, centrals),
        2 * len(tag),
        sparse.restore_cost_full_scan(prep.targets, pairs),
    )
    phase_certificate = sparse.build_phase_certificate(target_pairs, reconstructed)
    checks = {
        "production_internal_checks": all(witness["checks"].values()),
        "anticommuting_pairs": all(sparse.sparse_symp(pair.r0, pair.r1) == 1 for pair in pairs),
        "common_distinct_labels": orientation in sparse.ORIENTATIONS
        and all(label == orientation for label in labels),
        "cost_separately_recomputed": recomputed == int(witness["C_R6M"]),
        "phase_certificate_separately_reconstructed": all(phase_certificate["checks"].values()),
    }
    return checks


def n2_hostile_equivalence(dp) -> dict[str, Any]:
    sharpness = (
        ((1, 0), (1, 0)),
        ((1, 0), (1, 0)),
        ((2, 0), (2, 2)),
    )
    panels = {
        "registered_hostile_n2_a": dp._HOSTILE_N2_PANELS["n2_a"],
        "registered_hostile_n2_b": dp._HOSTILE_N2_PANELS["n2_b"],
        "registered_support_one_sharpness_5_lt_6": sharpness,
    }
    grammar2 = sparse.SparseGrammar(2, max_support=2)
    grammar1 = sparse.SparseGrammar(2, max_support=1)
    rows = []
    for name, pairs_global in panels.items():
        pairs_global = tuple((tuple(pair[0]), tuple(pair[1])) for pair in pairs_global)
        dense_pairs = tuple(
            tuple(global_key_to_dense(target, 2) for target in pair) for pair in pairs_global
        )
        terms = dp._synthetic_terms(pairs_global)
        production = dp.exact_r6m_matching(terms, dp._SYNTHETIC_MATCHING, 2, list(range(6)))
        sparse2 = sparse.solve_matching(dense_pairs, grammar=grammar2, max_support=2)
        sparse1 = sparse.solve_matching(dense_pairs, grammar=grammar1, max_support=1)
        sparse_checks = sparse.verify_witness(dense_pairs, sparse2)
        sparse_phase_certificate = sparse.build_phase_certificate(dense_pairs, sparse2)
        production_checks = separately_check_production_witness(pairs_global, production, 2)
        if not all(sparse_checks.values()):
            raise AssertionError({"n2_sparse_witness_invalid": [name, sparse_checks]})
        if not all(sparse_phase_certificate["checks"].values()):
            raise AssertionError(
                {
                    "n2_sparse_phase_certificate_invalid": [
                        name,
                        sparse_phase_certificate["checks"],
                    ]
                }
            )
        if not all(production_checks.values()):
            raise AssertionError({"n2_production_witness_invalid": [name, production_checks]})
        if sparse2.cost != int(production["C_R6M"]):
            raise AssertionError(
                {
                    "n2_exact_cost_mismatch": [
                        name,
                        sparse2.cost,
                        int(production["C_R6M"]),
                    ]
                }
            )
        row = {
            "panel": name,
            "production_512_state_dp_cost": int(production["C_R6M"]),
            "sparse_support_two_cost": sparse2.cost,
            "sparse_support_one_cost": sparse1.cost,
            "exact_cost_equal": True,
            "sparse_witness_checks": sparse_checks,
            "sparse_phase_certificate": sparse_phase_certificate,
            "production_witness_separate_checks": production_checks,
            "sparse_support_two_witness": sparse2.as_dict(),
            "sparse_support_one_witness": sparse1.as_dict(),
        }
        rows.append(row)

    sharp = next(row for row in rows if "sharpness" in row["panel"])
    if not (
        sharp["production_512_state_dp_cost"] == 5
        and sharp["sparse_support_two_cost"] == 5
        and sharp["sparse_support_one_cost"] == 6
        and any(
            len(frame) == 2
            for pair in sparse.solve_matching(
                tuple(
                    tuple(global_key_to_dense(target, 2) for target in pair) for pair in sharpness
                ),
                grammar=grammar2,
                max_support=2,
            ).pairs
            for frame in (pair.r0, pair.r1)
        )
    ):
        raise AssertionError({"support_one_sharpness_not_reproduced": sharp})
    return {
        "panels": rows,
        "support_one_sharpness_preserved": True,
        "terminal": "SUPPORT_ONE_REFUTED__SUPPORT_TWO_NEEDED_ON_REGISTERED_INSTANCE",
        "all_pass": all(row["exact_cost_equal"] for row in rows),
    }


def verify_canonical_status_delta() -> dict[str, Any]:
    status = json.loads(STATUS_PATH.read_text())
    if status["schema"] != "ORION.ORION05.R11.Round1CanonicalDelta.v1":
        raise AssertionError({"wrong_status_delta_schema": status.get("schema")})
    if status["record_kind"] != "ADDITIVE_CANONICAL_STATUS_AND_SUPERSESSION_DELTA":
        raise AssertionError({"wrong_status_record_kind": status.get("record_kind")})
    delta = status["canonical_delta"]
    if delta["base_commit"] != BASE_COMMIT:
        raise AssertionError({"status_delta_base_drift": delta["base_commit"]})

    source_rows = {row["path"]: row for row in delta["immutable_sources"]}
    if set(source_rows) != set(EXPECTED_V1_BINDINGS):
        raise AssertionError({"immutable_source_set_drift": sorted(source_rows)})
    source_json: dict[str, Any] = {}
    for path, expected in EXPECTED_V1_BINDINGS.items():
        row = source_rows[path]
        if {"git_blob": row["git_blob"], "sha256": row["sha256"]} != expected:
            raise AssertionError({"declared_v1_binding_drift": {path: row}})
        observed_blob = git("rev-parse", f"{BASE_COMMIT}:{path}")
        payload = git_file_bytes(BASE_COMMIT, path)
        observed = {"git_blob": observed_blob, "sha256": sha256_bytes(payload)}
        if observed != expected:
            raise AssertionError({"observed_v1_binding_drift": {path: observed}})
        source_json[path] = json.loads(payload)

    authority_conditions = [
        "this exact packet commit is reachable from main",
        "the merged-main ORION-05 R11 sparse direct-solver theorem workflow passes",
    ]
    precedence = delta["precedence"]
    if precedence["authority_effective_only_if"] != authority_conditions:
        raise AssertionError({"delta_authority_conditions_drift": precedence})
    if status["authority_effective_only_if"] != authority_conditions:
        raise AssertionError({"status_authority_conditions_drift": status})
    if precedence["all_non_orion05_v1_fields"] != "UNCHANGED":
        raise AssertionError({"non_orion05_mutation_not_forbidden": precedence})
    if not precedence["science_status_remains_open"]:
        raise AssertionError({"science_status_closed_without_round2": precedence})
    if precedence["portfolio_submission_authorized"]:
        raise AssertionError({"submission_improperly_authorized": precedence})

    expected_science_new = {
        "/papers/ORION-05/rounds/consumed": 1,
        "/papers/ORION-05/rounds/current": (
            "ROUND_1_POSITIVE_THEOREM_ESTABLISHED__ROUND_2_PRODUCTION_VALUE_OPEN"
        ),
        "/papers/ORION-05/next_gate": (
            "Execute the prospectively frozen production-faithful support-two "
            "versus unrestricted-referee Round 2; do not infer production value "
            "from the Round-1 theorem."
        ),
        "/papers/ORION-05/authority/runtime_theorem_established": True,
        "/papers/ORION-05/evidence_status/pending_candidates/0/emitted_terminal": TERMINAL,
        "/papers/ORION-05/evidence_status/pending_candidates/0/disposition": (
            "ESTABLISHED_AT_FROZEN_R6M_GRAMMAR_CEILING"
        ),
        "/papers/ORION-05/evidence_status/pending_candidates/0/current_main_authority": True,
        "/papers/ORION-05/evidence_status/pending_candidates/0/merged_main_verification": True,
        "/papers/ORION-05/evidence_status/pending_candidates/0/claim_boundary": (
            "EXACT_O_N9_RUNTIME_ESTABLISHED_FOR_FROZEN_R6M_ONLY__NO_PRODUCTION_RESOURCE_VALUE"
        ),
        "/papers/ORION-05/evidence_status/convergence_summary/label": (
            "ORION-05_ROUND_1_EXACT_O_N9_THEOREM_PASS__ROUND_2_PRODUCTION_VALUE_OPEN"
        ),
        "/papers/ORION-05/coordinator_issues": [1511],
        "/papers/ORION-05/active_science_pull_requests": [],
        "/papers/ORION-05/candidate_scope": [],
        "/papers/ORION-05/established_scope": [
            "sharp frozen-R6M frame-support theorem kappa_R6M = 2 at its existing current-main ceiling",
            "support-one adverse witness with exact cost 5 < 6 preserved",
            "exact constructive ordered support-at-most-two anticommuting-pair count B(n)=54n^3-108n^2+60n",
            "exact O(n^9) word-RAM direct optimizer for the frozen R6M six-slot grammar and support-count objective",
            "active-union bound at most nine and minimum compatible Tag support at most rank at most six",
        ],
        "/papers/ORION-05/open_science_gates": [
            "production-faithful measured resource value",
            "external quantum review and novelty adjudication",
        ],
        "/papers/ORION-05/evidence_status/pending_candidates": [],
        "/papers/ORION-05/evidence_status/convergence_summary/derived_from": [
            "ORION05_SOURCE_BINDING",
            "ORION05_RESOURCE_MAP",
            "ORION05_NOVELTY",
            "ORION05_R20_RESOURCE_AUDIT",
            "ORION05_R11_DIRECT_SOLVER_ESTABLISHED",
        ],
    }
    science_rows = {
        row["json_pointer"]: row for row in delta["science_status_transitions"]
    }
    if set(science_rows) != set(expected_science_new):
        raise AssertionError({"science_transition_set_drift": sorted(science_rows)})
    science_v1 = source_json[SCIENCE_V1_PATH]
    for pointer, expected_new in expected_science_new.items():
        row = science_rows[pointer]
        observed_old = json_pointer_get(science_v1, pointer)
        if row["old"] != observed_old or row["new"] != expected_new:
            raise AssertionError(
                {
                    "science_transition_drift": {
                        "pointer": pointer,
                        "declared": row,
                        "observed_old": observed_old,
                        "expected_new": expected_new,
                    }
                }
            )

    expected_established_record = {
        "id": "ORION05_R11_DIRECT_SOLVER_ESTABLISHED",
        "value": TERMINAL,
        "record_kind": "RAW_SCIENCE_TERMINAL",
        "source": {
            "kind": "CURRENT_MAIN_ADDITIVE_PACKET_AFTER_MERGED_MAIN_PASS",
            "theorem": "papers/orion-05-tare-expressivity/ORION05_R11_EXACT_O_N9_DIRECT_SOLVER_THEOREM.md",
            "receipt": "papers/orion-05-tare-expressivity/ORION05_R11_SPARSE_EQUIVALENCE_RESULTS.json",
            "status_delta": "papers/orion-05-tare-expressivity/ORION05_R11_ROUND1_STATUS.json",
            "candidate_donors": [1430, 1524],
        },
        "authority_scope": "exact O(n^9) word-RAM optimizer for the frozen R6M six-slot grammar and support-count objective only",
        "controls_current_science_status": True,
        "disposition": "ACTIVE",
        "authority": {
            "production_runtime_value": False,
            "external_independence": False,
            "novelty": False,
            "journal_authority": False,
            "submission_authorized": False,
        },
    }
    additions = delta["science_status_additions"]
    if additions != [
        {
            "json_pointer": "/papers/ORION-05/evidence_status/established_records",
            "old_state": "ABSENT",
            "new": [expected_established_record],
        }
    ]:
        raise AssertionError({"science_status_addition_drift": additions})
    try:
        json_pointer_get(
            science_v1, "/papers/ORION-05/evidence_status/established_records"
        )
    except KeyError:
        pass
    else:
        raise AssertionError("established_records was not absent in immutable V1")

    expected_supersession_new = {
        "/after_orion05_theorem_successor_merge/close_pull_requests": [1430, 1524],
        "/after_orion05_theorem_successor_merge/close_issues": [1518, 1523],
        "/after_orion05_theorem_successor_merge/keep_open_for_round_2": [1511],
        "/keep_open_after_convergence/active_science_pull_requests": [
            1449,
            1466,
            1469,
            1472,
        ],
    }
    supersession_rows = {
        row["json_pointer"]: row
        for row in delta["supersession_plan_transitions"]
    }
    if set(supersession_rows) != set(expected_supersession_new):
        raise AssertionError(
            {"supersession_transition_set_drift": sorted(supersession_rows)}
        )
    supersession_v1 = source_json[SUPERSESSION_V1_PATH]
    for pointer, expected_new in expected_supersession_new.items():
        row = supersession_rows[pointer]
        observed_old = json_pointer_get(supersession_v1, pointer)
        if row["old"] != observed_old or row["new"] != expected_new:
            raise AssertionError(
                {
                    "supersession_transition_drift": {
                        "pointer": pointer,
                        "declared": row,
                        "observed_old": observed_old,
                        "expected_new": expected_new,
                    }
                }
            )

    if status["science_status"] != "OPEN" or status["rounds"] != {
        "consumed": 1,
        "maximum": 3,
        "current": expected_science_new["/papers/ORION-05/rounds/current"],
    }:
        raise AssertionError({"effective_round_status_drift": status["rounds"]})
    if status["supersedes_after_authority_effective"] != {
        "candidate_pull_requests": [1430, 1524],
        "candidate_issues": [1518, 1523],
        "scope": "pair-count and frozen-R6M O(n^9) theorem-candidate status only",
        "close_only_after_both_authority_conditions": True,
        "retain_open": {
            "round_2_programme_issue": [1511],
            "resource_report_layer_pull_request": [1449],
            "adverse_timeout_custody_pull_request": [1498],
        },
    }:
        raise AssertionError(
            {"effective_supersession_delta_drift": status["supersedes_after_authority_effective"]}
        )

    review = status["same_owner_hostile_review"]
    expected_review_hashes = {
        "theorem": sha256_file(THEOREM_PATH),
        "sparse_solver": sha256_file(SOLVER_PATH),
        "verifier": sha256_file(Path(__file__)),
        "r6s_human_proof": sha256_file(HERE / "HUMAN_PROOF_R6S_2026-08-22.md"),
        "frozen_r6m_dp": sha256_file(
            Q_SOURCE / "max_r6m_exact_three_tare2_shared_factor_dp.py"
        ),
    }
    if review["reviewed_input_sha256"] != expected_review_hashes:
        raise AssertionError(
            {
                "hostile_review_input_binding_drift": {
                    "declared": review["reviewed_input_sha256"],
                    "expected": expected_review_hashes,
                }
            }
        )
    if review["authority"] != "SAME_OWNER_SAME_SESSION_HOSTILE_PROOF_AND_CODE_REVIEW_ONLY":
        raise AssertionError({"hostile_review_authority_overstated": review})
    if review["external_independence_established"]:
        raise AssertionError({"external_independence_improperly_promoted": review})

    adverse = status["pr1498_adverse_runtime_context"]
    source = adverse["source"]
    if source["head_commit"] != Q1_XOVER_COMMIT or source["pull_request"] != 1498:
        raise AssertionError({"q1_xover_source_drift": source})
    declared_q1_bindings = {row["path"]: row for row in source["bindings"]}
    if set(declared_q1_bindings) != set(EXPECTED_Q1_XOVER_BINDINGS):
        raise AssertionError({"q1_xover_binding_set_drift": declared_q1_bindings})
    q1_payloads: dict[str, bytes] = {}
    for path, expected in EXPECTED_Q1_XOVER_BINDINGS.items():
        row = declared_q1_bindings[path]
        if {"git_blob": row["git_blob"], "sha256": row["sha256"]} != expected:
            raise AssertionError({"declared_q1_xover_binding_drift": {path: row}})
        payload = git_file_bytes(Q1_XOVER_COMMIT, path)
        observed = {
            "git_blob": git("rev-parse", f"{Q1_XOVER_COMMIT}:{path}"),
            "sha256": sha256_bytes(payload),
        }
        if observed != expected:
            raise AssertionError({"observed_q1_xover_binding_drift": {path: observed}})
        q1_payloads[path] = payload

    q1_result = json.loads(
        q1_payloads["research/extensions/orion-q/Q1_XOVER_RESULTS_V1.json"]
    )
    instances_by_n = [
        (cell["n"], instance)
        for family in q1_result["panel"].values()
        for cell in family
        for instance in cell["instances"]
    ]
    observed_by_n = {
        n: {
            "sampled": sum(row_n == n for row_n, _ in instances_by_n),
            "exact": sum(
                row_n == n and row["dxx"]["status"] == "EXACT"
                for row_n, row in instances_by_n
            ),
            "timeouts": sum(
                row_n == n and row["dxx"]["status"] == "TIMEOUT"
                for row_n, row in instances_by_n
            ),
        }
        for n in range(1, 7)
    }
    expected_by_n = {
        1: {"sampled": 72, "exact": 72, "timeouts": 0},
        2: {"sampled": 96, "exact": 96, "timeouts": 0},
        3: {"sampled": 96, "exact": 96, "timeouts": 0},
        4: {"sampled": 72, "exact": 72, "timeouts": 0},
        5: {"sampled": 36, "exact": 36, "timeouts": 0},
        6: {"sampled": 12, "exact": 0, "timeouts": 12},
    }
    if observed_by_n != expected_by_n:
        raise AssertionError({"q1_xover_by_n_coverage_drift": observed_by_n})
    sampled = sum(row["sampled"] for row in observed_by_n.values())
    exact = sum(row["exact"] for row in observed_by_n.values())
    timeouts = sum(row["timeouts"] for row in observed_by_n.values())
    predictions = q1_result["prediction_outcomes"]
    if q1_result["verdict"] != "RUN_INCOMPLETE":
        raise AssertionError({"q1_xover_raw_verdict_drift": q1_result["verdict"]})
    expected_predictions = {
        "P1_all_size_theorem": True,
        "P2_sandwich": True,
        "P3_family_size_identity": True,
        "P4_witness_support": True,
        "P5_r6q_identity_fresh_subject": True,
        "P6_feasibility_rule": False,
    }
    if predictions != expected_predictions:
        raise AssertionError({"q1_xover_prediction_bytes_drift": predictions})
    if (sampled, exact, timeouts) != (384, 372, 12):
        raise AssertionError(
            {"q1_xover_raw_coverage_drift": [sampled, exact, timeouts]}
        )
    raw = adverse["raw_observations"]
    if (
        raw["receipt_verdict_preserved_verbatim"] != "RUN_INCOMPLETE"
        or raw["sampled_cells_total"] != 384
        or raw["n_le_5_exact"] != 372
        or raw["n_le_5_nonexact"] != 0
        or raw["n_6_timeout"] != 12
        or raw["n_6_sampled"] != 12
        or raw["per_cell_budget_seconds"] != 600
        or raw["new_sparse_o_n9_solver_executed_by_pr1498"]
    ):
        raise AssertionError({"q1_xover_status_summary_drift": raw})
    correction = adverse["authority_correction"]
    required_corrections = (
        "registered_p6_did_not_predict_zero_timeouts",
        "evaluator_added_unregistered_timeouts_equal_zero_clause",
        "evaluator_structural_clause_did_not_test_the_named_n_gt_6_collections",
        "p6_false_is_not_authority_for_general_prediction_refutation",
    )
    if not all(correction[key] for key in required_corrections):
        raise AssertionError({"q1_xover_authority_correction_missing": correction})
    if adverse["round_accounting"] != (
        "ADVERSE_CONTEXT_ONLY__DOES_NOT_CONSUME_PROSPECTIVE_ROUND_2"
    ):
        raise AssertionError({"q1_xover_round_accounting_drift": adverse})

    return {
        "terminal": "ORION05_R11_CANONICAL_DELTA_AND_PR1498_ADVERSE_CUSTODY_PASS",
        "v1_sources_bound": sorted(EXPECTED_V1_BINDINGS),
        "science_transitions": len(science_rows),
        "supersession_transitions": len(supersession_rows),
        "q1_xover_source_commit": Q1_XOVER_COMMIT,
        "q1_xover_raw_coverage": {
            "sampled": sampled,
            "exact_n_le_5": exact,
            "timeouts_n_6": timeouts,
            "by_n": observed_by_n,
        },
        "same_owner_hostile_review_bound": True,
        "external_independence": False,
        "round_2_open": True,
    }


def main() -> dict[str, Any]:
    change_scope = verify_change_scope()
    canonical_status_delta = verify_canonical_status_delta()
    independence = source_independence_check()
    pair_checks = constructive_pair_checks()
    tag_preprocessing = tag_and_preprocessing_checks()
    dp = _production_module()
    n1 = complete_n1_equivalence(dp)
    n2 = n2_hostile_equivalence(dp)

    bindings = {
        "base_commit": BASE_COMMIT,
        "base_tree": BASE_TREE,
        "sparse_solver": sha256_file(SOLVER_PATH),
        "verifier": sha256_file(Path(__file__)),
        "theorem_statement": sha256_file(THEOREM_PATH),
        "round1_status": sha256_file(STATUS_PATH),
        "development_packet": sha256_file(DEVELOPMENT_PATH),
        "workflow": sha256_file(WORKFLOW_PATH),
        "frozen_r6m_dp": sha256_file(Q_SOURCE / "max_r6m_exact_three_tare2_shared_factor_dp.py"),
        "frozen_r6m_protocol": sha256_file(
            ROOT
            / "development"
            / "orion-q-max-r0"
            / "MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_PROTOCOL.md"
        ),
        "r6s_human_proof": sha256_file(HERE / "HUMAN_PROOF_R6S_2026-08-22.md"),
        "r6s_receipt": sha256_file(Q_SOURCE / "MAX_R6S_ALL_N_COMPOSITION_RESULTS.json"),
        "r6o_adverse_receipt": sha256_file(Q_SOURCE / "MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json"),
        "r6p_support_two_receipt": sha256_file(
            Q_SOURCE / "MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json"
        ),
        "qg21_current_resource_adverse_receipt": sha256_file(
            ROOT / "research" / "extensions" / "orion-qg" / "QG21_FT_CHEMISTRY_RESULTS.json"
        ),
    }
    frozen_mismatches = {
        name: {"expected": expected, "actual": bindings.get(name)}
        for name, expected in EXPECTED_FROZEN_BINDINGS.items()
        if bindings.get(name) != expected
    }
    if frozen_mismatches:
        raise AssertionError({"frozen_source_or_solver_binding_drift": frozen_mismatches})
    gates = {
        "constructive_pair_generator_exact_n1_n6": all(
            row["naive_set_equal"] for row in pair_checks["n1_through_n6"]
        ),
        "pair_count_formula_exact_n1_n6": all(
            row["ordered_anticommuting_pairs"] == row["formula"]
            for row in pair_checks["n1_through_n6"]
        ),
        "single_pair_union_le_three_and_three_pairs_union_le_nine": pair_checks[
            "pair_union_three_attained"
        ]
        and pair_checks["three_pair_union_nine_attained"],
        "minimum_tag_confined_and_support_le_rank_le_six": tag_preprocessing[
            "tag_support_le_rank_le_six_all_feasible"
        ]
        and tag_preprocessing["tag_confined_to_active_union_all_feasible"],
        "baseline_plus_active_correction_exact": tag_preprocessing[
            "baseline_plus_active_correction_cases"
        ]
        > 0,
        "solver_standard_library_only_no_production_dp_symbols": independence[
            "standard_library_only"
        ]
        and independence["production_dp_symbols_absent"],
        "complete_n1_cost_and_witness_equivalence": n1["all_pass"],
        "hostile_n2_cost_and_witness_equivalence": n2["all_pass"],
        "support_one_adverse_boundary_preserved": n2["support_one_sharpness_preserved"],
        "no_protected_task3_path": change_scope["protected_unchanged"],
        "canonical_status_delta_and_pr1498_adverse_custody_bound": (
            canonical_status_delta["round_2_open"]
            and canonical_status_delta["same_owner_hostile_review_bound"]
        ),
    }
    if not all(gates.values()):
        raise AssertionError({"orion05_r11_gate_failure": gates})
    result = {
        "schema": "ORION.ORION05.R11.SparseDirectSolverEquivalence.v1",
        "terminal": TERMINAL,
        "scope": "FROZEN_R6M_SIX_SLOT_GRAMMAR_AND_SUPPORT_COUNT_OBJECTIVE_ONLY",
        "authority": "THEOREM_GRADE_ON_FROZEN_GRAMMAR__NOT_PRODUCTION_RUNTIME_NOVELTY_RESOURCE_VENUE_OR_SUBMISSION_AUTHORITY",
        "bindings": bindings,
        "change_scope": change_scope,
        "canonical_status_delta": canonical_status_delta,
        "source_independence": independence,
        "constructive_pair_checks": pair_checks,
        "tag_and_preprocessing_checks": tag_preprocessing,
        "complete_n1_equivalence": n1,
        "hostile_n2_equivalence": n2,
        "gates": gates,
        "claim_boundaries": {
            "generic_tare": False,
            "existing_production_dp_acceleration": False,
            "hardware_or_physical_resource_advantage": False,
            "novelty": False,
            "journal_or_submission_authority": False,
            "protected_task3_access": False,
        },
        "adverse_results_preserved": [
            "SUPPORT_ONE_REFUTED__SUPPORT_TWO_NEEDED_ON_REGISTERED_INSTANCE",
            "ORIGINAL_TWO_TRADE_ALL_N_CHARACTERIZATION_REFUTED",
            "PAIR_COUNT_RECEIVES_NO_GENERIC_NOVELTY_CREDIT",
            "QG21_PRIMARY_THETA_FT_DONOR_EXACT_90_OF_90",
            "QG21_S1_ONLY_18_OF_90_IMPROVED_BY_TWO_LOGICAL_TWO_QUBIT_CLIFFORDS",
            "PARTIAL_RESOURCE_MAP__MEASURED_PRODUCTION_BENCHMARK_OPEN",
            "PR1498_RAW_BUDGET_FRONTIER_PRESERVED__WRAPPER_DEFECTIVE__NO_SPARSE_SOLVER_REFUTATION",
        ],
    }
    RESULT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(TERMINAL)
    print(canonical_json({"gates": gates, "result": str(RESULT_PATH.relative_to(ROOT))}))
    return result


if __name__ == "__main__":
    main()
