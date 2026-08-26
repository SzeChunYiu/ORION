from __future__ import annotations

import hashlib
import json
import math
import resource
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

from . import EXPECTED_OUTCOME_MARKER, EXPOSURE_MARKER, INDEPENDENCE_TERMINAL
from .augmentation import extension_orbit_representatives, generate_canonical_classes
from .canonical import canonical_multiset
from .checkpoint import (
    CheckpointConfig,
    CheckpointTerminal,
    advance_child_level,
    build_donor_range_manifest,
    canonical_records_sha256,
    merge_donor_range_manifests,
)
from .factorization import find_disjoint_zero_sums
from .group import GroupSpec, InputError, Matrix, Vector
from .manifest import sha256_file
from .normalization import declared_donor_images
from .receipt import canonical_json_sha256, factorization_result_payload

T = TypeVar("T")
EXPOSURE_MARKERS = [EXPECTED_OUTCOME_MARKER, EXPOSURE_MARKER]


def deterministic_gl_matrices(
    spec: GroupSpec, seed_label: object, count: object
) -> tuple[Matrix, ...]:
    if not isinstance(seed_label, str) or not seed_label:
        raise InputError("seed_label must be a nonempty string")
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise InputError("count must be a positive integer")
    matrices: list[Matrix] = []
    counter = 0
    while len(matrices) < count:
        digest = hashlib.sha256(f"{seed_label}:{counter}".encode()).digest()
        matrix = tuple(
            tuple(digest[spec.d * row + column] % spec.p for column in range(spec.d))
            for row in range(spec.d)
        )
        if spec.rank(matrix) == spec.d and matrix not in matrices:
            matrices.append(matrix)
        counter += 1
    return tuple(matrices)


def _timed(function: Callable[[], T]) -> tuple[T, int]:
    started = time.perf_counter_ns()
    result = function()
    return result, time.perf_counter_ns() - started


def _records_payload(records: tuple[tuple[Vector, ...], ...]) -> list[list[list[int]]]:
    return [[list(vector) for vector in record] for record in records]


def measure_target_case(
    spec: GroupSpec,
    witness: object,
    matrix: object,
    *,
    case_index: object,
    factorization_k: object,
    factorization_max_states: object,
) -> dict[str, Any]:
    vectors = spec.validate_sequence(witness)
    if isinstance(case_index, bool) or not isinstance(case_index, int) or case_index < 0:
        raise InputError("case_index must be a nonnegative integer")
    if not isinstance(matrix, tuple) or spec.rank(matrix) != spec.d:
        raise InputError("matrix must be an invertible tuple matrix")
    transformed = tuple(spec.matvec(matrix, vector) for vector in vectors)
    canonical, canonical_ns = _timed(lambda: canonical_multiset(spec, transformed))
    donor_images, donor_ns = _timed(lambda: declared_donor_images(spec, transformed))
    representatives, stabilizer_ns = _timed(
        lambda: extension_orbit_representatives(spec, canonical)
    )
    factorization, factor_ns = _timed(
        lambda: find_disjoint_zero_sums(
            spec,
            transformed,
            factorization_k,
            max_states=factorization_max_states,
        )
    )
    return {
        "case_index": case_index,
        "matrix": [list(row) for row in matrix],
        "witness_length": len(vectors),
        "transformed_witness_sha256": canonical_json_sha256(
            [list(vector) for vector in transformed]
        ),
        "scientific_terminal": "CANNOT_CHECK",
        "kernels": {
            "canonicalization": {
                "elapsed_ns": canonical_ns,
                "record_sha256": canonical_records_sha256((canonical,)),
            },
            "donor_slice_expansion": {
                "elapsed_ns": donor_ns,
                "image_count": len(donor_images),
                "image_sha256": canonical_json_sha256(_records_payload(donor_images)),
            },
            "extension_orbit_stabilizer_construction": {
                "elapsed_ns": stabilizer_ns,
                "representative_count": len(representatives),
                "representative_sha256": canonical_json_sha256(
                    [list(vector) for vector in representatives]
                ),
            },
            "exact_two_bin_factorization_dp": {
                "elapsed_ns": factor_ns,
                "max_states": factorization_max_states,
                **factorization_result_payload(factorization),
            },
        },
    }


def derive_slurm_pilot_envelope(
    *, total_elapsed_ns: object, max_rss_bytes: object
) -> dict[str, int | str]:
    if (
        isinstance(total_elapsed_ns, bool)
        or not isinstance(total_elapsed_ns, int)
        or total_elapsed_ns < 0
    ):
        raise InputError("total_elapsed_ns must be a nonnegative integer")
    if isinstance(max_rss_bytes, bool) or not isinstance(max_rss_bytes, int) or max_rss_bytes < 0:
        raise InputError("max_rss_bytes must be a nonnegative integer")
    elapsed_minutes = total_elapsed_ns / (60 * 1_000_000_000)
    observed_gib = max_rss_bytes / 1024**3
    return {
        "cpu_count": 1,
        "memory_gib": max(4, math.ceil(4 * observed_gib)),
        "wall_minutes": max(30, math.ceil(10 * elapsed_minutes)),
        "scope": "future_same_pilot_only_not_full_census",
    }


def process_max_rss() -> tuple[int, int, str]:
    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return raw, raw, "bytes"
    return raw, raw * 1024, "kibibytes"


def _load_protocol(root: Path) -> tuple[dict[str, Any], str]:
    protocol_path = root / "TARGET_RESOURCE_PILOT_PROTOCOL.json"
    digest = sha256_file(protocol_path)
    declared = (root / "TARGET_RESOURCE_PILOT_PROTOCOL.sha256").read_text().split()[0]
    if digest != declared:
        raise ValueError("target resource protocol digest mismatch")
    return json.loads(protocol_path.read_text()), digest


def build_target_resource_pilot_receipt(
    root: Path | str, *, source_manifest_sha256: str
) -> dict[str, Any]:
    base = Path(root).resolve()
    protocol, protocol_sha256 = _load_protocol(base)
    if protocol["execution"]["lunarc_submission_authorized"] is not False:
        raise ValueError("local pilot protocol unexpectedly authorizes LUNARC")
    source_digest = source_manifest_sha256
    if not isinstance(source_digest, str) or len(source_digest) != 64:
        raise ValueError("source manifest SHA-256 is invalid")
    checkpoint_protocol = protocol["checkpoint_child_level"]
    group = checkpoint_protocol["group"]
    spec = GroupSpec(group["p"], group["d"])
    pilot_started = time.perf_counter_ns()

    parents = generate_canonical_classes(spec, checkpoint_protocol["parent_level"]).records
    parent_sha256 = canonical_records_sha256(parents)
    expected_parent = checkpoint_protocol["parent_manifest"]
    if len(parents) != expected_parent["record_count"]:
        raise ValueError("frozen checkpoint parent count mismatch")
    if parent_sha256 != expected_parent["record_sha256"]:
        raise ValueError("frozen checkpoint parent record digest mismatch")
    profile_payload = checkpoint_protocol["constraints"]
    from .augmentation import ConstraintProfile

    checkpoint_config = CheckpointConfig(
        p=spec.p,
        d=spec.d,
        parent_level=checkpoint_protocol["parent_level"],
        target_level=checkpoint_protocol["target_level"],
        range_start=checkpoint_protocol["parent_range"][0],
        range_stop=checkpoint_protocol["parent_range"][1],
        parent_records_sha256=parent_sha256,
        protocol_sha256=protocol_sha256,
        source_manifest_sha256=source_digest,
        candidate_edge_budget=checkpoint_protocol["candidate_edge_budget_per_invocation"],
        profile=ConstraintProfile(**profile_payload),
    )
    restarted = advance_child_level(
        spec,
        parents,
        checkpoint_config,
        edge_budget=checkpoint_config.candidate_edge_budget,
    )
    invocations: list[dict[str, Any]] = []
    while True:
        invocations.append(
            {
                "invocation_index": len(invocations),
                "terminal": restarted.terminal.value,
                "checkpoint_sha256": None
                if restarted.checkpoint is None
                else restarted.checkpoint.to_dict()["checkpoint_sha256"],
                "candidate_edges": None
                if restarted.checkpoint is None
                else restarted.checkpoint.candidate_edges,
                "cursor": None
                if restarted.checkpoint is None
                else {
                    "parent_index": restarted.checkpoint.cursor_parent_index,
                    "representative_index": restarted.checkpoint.cursor_representative_index,
                },
            }
        )
        if restarted.terminal is not CheckpointTerminal.CHECKPOINT_SAVED:
            break
        assert restarted.checkpoint is not None
        restarted = advance_child_level(
            spec,
            parents,
            checkpoint_config,
            checkpoint=restarted.checkpoint.to_dict(),
            edge_budget=checkpoint_config.candidate_edge_budget,
        )
    if restarted.terminal is not CheckpointTerminal.CHECKPOINT_LEVEL_COMPLETE:
        raise ValueError(f"checkpoint pilot did not complete: {restarted.terminal.value}")
    uninterrupted = advance_child_level(
        spec,
        parents,
        checkpoint_config,
        edge_budget=100_000,
        reference_uninterrupted=True,
    )
    if uninterrupted.terminal is not CheckpointTerminal.CHECKPOINT_LEVEL_COMPLETE:
        raise ValueError("uninterrupted checkpoint reference did not complete")
    if restarted.to_dict() != uninterrupted.to_dict():
        raise ValueError("checkpoint restart differs from uninterrupted reference")
    assert restarted.checkpoint is not None
    checkpoint_records = restarted.records

    donor_protocol = protocol["donor_slice_ranges"]
    ranges = tuple(tuple(item) for item in donor_protocol["ranges"])
    donor_manifests = tuple(
        build_donor_range_manifest(
            spec,
            parents,
            start,
            stop,
            parent_records_sha256=parent_sha256,
            protocol_sha256=protocol_sha256,
        )
        for start, stop in ranges
    )
    donor_merge = merge_donor_range_manifests(
        spec,
        parents,
        donor_manifests,
        expected_ranges=ranges,
        parent_records_sha256=parent_sha256,
        protocol_sha256=protocol_sha256,
    )

    target_protocol = protocol["target_kernel_panel"]
    fixture_path = base / target_protocol["donor_fixture_path"]
    if sha256_file(fixture_path) != target_protocol["donor_fixture_sha256"]:
        raise ValueError("target kernel witness fixture digest mismatch")
    witness = json.loads(fixture_path.read_text())["witness"]
    matrices = deterministic_gl_matrices(
        spec,
        target_protocol["matrix_generation"]["seed_label"],
        target_protocol["case_count"],
    )
    cases = [
        measure_target_case(
            spec,
            witness,
            matrix,
            case_index=index,
            factorization_k=target_protocol["factorization_k"],
            factorization_max_states=target_protocol["factorization_max_states"],
        )
        for index, matrix in enumerate(matrices)
    ]
    total_elapsed_ns = time.perf_counter_ns() - pilot_started
    raw_rss, max_rss_bytes, rss_unit = process_max_rss()
    non_duplication_payload = {
        "pilot_id": protocol["pilot_id"],
        "protocol_sha256": protocol_sha256,
        "source_manifest_sha256": source_digest,
        "parent_records_sha256": parent_sha256,
        "donor_fixture_sha256": target_protocol["donor_fixture_sha256"],
        "ranges": [list(item) for item in ranges],
        "matrix_sha256": canonical_json_sha256(
            [[list(row) for row in matrix] for matrix in matrices]
        ),
    }
    return {
        "schema_version": "nq-engine-a-target-resource-pilot-receipt-v1",
        "pilot_id": protocol["pilot_id"],
        "authority": "engineering_resource_pilot_only",
        "terminal": "PILOT_EXECUTED_ENGINEERING_ONLY__CANNOT_CHECK",
        "independence_terminal": INDEPENDENCE_TERMINAL,
        "exposure_markers": EXPOSURE_MARKERS,
        "scientific_terminal": "CANNOT_CHECK",
        "protocol_sha256": protocol_sha256,
        "source_manifest_sha256": source_digest,
        "non_duplication_key": canonical_json_sha256(non_duplication_payload),
        "full_census_executed": False,
        "lunarc_submission": None,
        "two_engine_pass_increment": 0,
        "checkpoint_restart": {
            "terminal": restarted.terminal.value,
            "parent_records_sha256": parent_sha256,
            "parent_range": [checkpoint_config.range_start, checkpoint_config.range_stop],
            "candidate_edge_budget_per_invocation": checkpoint_config.candidate_edge_budget,
            "invocation_count": len(invocations),
            "invocations": invocations,
            "uninterrupted_restart_byte_identical": True,
            "final_checkpoint_sha256": restarted.checkpoint.to_dict()["checkpoint_sha256"],
            "candidate_edges": restarted.checkpoint.candidate_edges,
            "output_record_count": len(checkpoint_records),
            "output_sha256": canonical_records_sha256(checkpoint_records),
            "global_coverage": False,
        },
        "donor_slice_ranges": {
            "terminal": donor_merge["terminal"],
            "ranges": [list(item) for item in ranges],
            "range_manifest_sha256": [
                manifest["range_manifest_sha256"] for manifest in donor_manifests
            ],
            "output_record_count": donor_merge["output_record_count"],
            "output_sha256": donor_merge["output_sha256"],
            "union_dedup_equal_to_uninterrupted": True,
            "global_coverage": False,
        },
        "target_kernel_panel": {
            "case_count": len(cases),
            "cases": cases,
        },
        "observed_resources": {
            "total_elapsed_ns": total_elapsed_ns,
            "process_max_rss_raw": raw_rss,
            "process_max_rss_raw_unit": rss_unit,
            "process_max_rss_bytes": max_rss_bytes,
        },
        "future_slurm_pilot_envelope": derive_slurm_pilot_envelope(
            total_elapsed_ns=total_elapsed_ns, max_rss_bytes=max_rss_bytes
        ),
    }
