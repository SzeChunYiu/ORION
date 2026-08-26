#!/usr/bin/env python3
"""Deterministic non-authorizing audit of the X1-B C15 candidate proof spine.

This script does not prove the theorem by itself. It checks that the exact
committed donor/finite-evidence packets used by the assembled proof have not
changed, reconstructs the greedy residual-tree arithmetic independently, and
emits a strict harness token with all authority flags false.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

PREFIX = "ORIONRG_X1B_C15_AUDIT="
ROOT = Path(__file__).resolve().parents[3]

EXPECTED_BLOBS = {
    "research/domains/orion-rg/X1B_C15_DAVENPORT_43_CANDIDATE_THEOREM_2026-08-22.md": "3ee8afdda1a4c6704abb08ab05d257e281658d1e",
    "research/domains/orion-rg/X1B_K3_10PT_RESIDUAL_CLOSURE_THEOREM_2026-08-22.md": "2ee618a789e506fbb8f23c9ef3b9697a01a055fd",
    "research/domains/orion-rg/X1B_K4_13PT_RESIDUAL_CLOSURE_THEOREM_2026-08-22.md": "2cc19e54f75b8a895d762a389e8c006c855264a3",
    "research/domains/orion-rg/X1B_C15_14PT_NO_SHORT_RAW_CONFIRM_RESULT_2026-08-22.md": "e40e4e3b1ab05c4ecb0eb88206428112b6e96f10",
    "research/domains/orion-rg/X1B_C15_16PT_RAW_QUOTIENT_RESULT_2026-08-22.md": "b7e92027f8d45afddf89f039fbc94c9eedc7d61d",
    "research/domains/orion-rg/X1B_GEROLDINGER_YANG_PGROUP_SCALARIZATION_DONOR_AUDIT_2026-08-22.md": "a537a7fef4e8beaa881cd13d87332170a8b44306",
    "research/domains/orion-rg/X1B_C15_DONOR_NUMERICAL_SPINE_AUDIT_2026-08-22.md": "2e29c171f783570f6b6d96a73ded34d2645a649a",
}

REQUIRED_TEXT = {
    "research/domains/orion-rg/X1B_C15_DAVENPORT_43_CANDIDATE_THEOREM_2026-08-22.md": [
        "D(C_15^3)=43",
        "m in {9,10,11,12}",
        "NOT YET EXTERNAL-PEER-REVIEWED OR NOVELTY-AUTHORIZED",
    ],
    "research/domains/orion-rg/X1B_K3_10PT_RESIDUAL_CLOSURE_THEOREM_2026-08-22.md": [
        "raw_candidates 1190124",
        "consistent 0",
    ],
    "research/domains/orion-rg/X1B_K4_13PT_RESIDUAL_CLOSURE_THEOREM_2026-08-22.md": [
        "No terminal leaf survives",
        "79,487,138",
        "54,683,021",
    ],
    "research/domains/orion-rg/X1B_C15_14PT_NO_SHORT_RAW_CONFIRM_RESULT_2026-08-22.md": [
        "38,376",
        "Failures:",
        "**0**.",
    ],
    "research/domains/orion-rg/X1B_C15_16PT_RAW_QUOTIENT_RESULT_2026-08-22.md": [
        "packed4 702",
        "failures 0",
    ],
    "research/domains/orion-rg/X1B_GEROLDINGER_YANG_PGROUP_SCALARIZATION_DONOR_AUDIT_2026-08-22.md": [
        "lambda_i(c)=lambda_i(h_i)=1",
        "Theorem 3.5",
    ],
    "research/domains/orion-rg/X1B_C15_DONOR_NUMERICAL_SPINE_AUDIT_2026-08-22.md": [
        "D(C_3^3)     = 7",
        "D_2(C_3^3)   = 11",
        "D_3(C_3^3)   = 15",
        "D^3(C_3^3)   = 17",
        "D(C_5^3)     = 13",
    ],
}


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def check_files() -> tuple[bool, dict[str, object]]:
    rows = {}
    all_ok = True
    for rel, expected in EXPECTED_BLOBS.items():
        path = ROOT / rel
        data = path.read_bytes()
        actual = git_blob_sha(data)
        text = data.decode("utf-8")
        tokens = REQUIRED_TEXT.get(rel, ())
        tokens_ok = all(token in text for token in tokens)
        ok = actual == expected and tokens_ok
        all_ok = all_ok and ok
        rows[rel] = {
            "expected_blob": expected,
            "actual_blob": actual,
            "tokens_ok": tokens_ok,
            "ok": ok,
        }
    return all_ok, rows


def check_arithmetic() -> dict[str, object]:
    n = 43
    short_cap = 3
    residual_upper = 16
    kernel_davenport = 13
    quotient_thresholds = {1: 7, 2: 11, 3: 15}

    min_removed_blocks = min(m for m in range(n + 1) if n - short_cap * m <= residual_upper)
    possible_counterexample_m = list(range(min_removed_blocks, kernel_davenport))

    hard = {}
    for m in possible_counterexample_m:
        residual_min = n - short_cap * m
        if m == 12:
            need = 1
            threshold = quotient_thresholds[1]
            hard_sizes = [] if residual_min >= threshold else list(range(residual_min, threshold))
        elif m == 11:
            need = 2
            threshold = quotient_thresholds[2]
            hard_sizes = list(range(residual_min, min(residual_upper, threshold - 1) + 1))
        elif m == 10:
            need = 3
            threshold = quotient_thresholds[3]
            hard_sizes = list(range(residual_min, min(residual_upper, threshold - 1) + 1))
        elif m == 9:
            need = 4
            threshold = None
            hard_sizes = [16]
        else:
            raise AssertionError(f"unexpected residual branch m={m}")
        hard[str(m)] = {
            "residual_min": residual_min,
            "blocks_needed": kernel_davenport - m,
            "generic_need": need,
            "threshold": threshold,
            "hard_sizes": hard_sizes,
        }

    expected_hard = {
        "12": [],
        "11": [10],
        "10": [13, 14],
        "9": [16],
    }
    tree_ok = (
        min_removed_blocks == 9
        and possible_counterexample_m == [9, 10, 11, 12]
        and all(hard[m]["hard_sizes"] == sizes for m, sizes in expected_hard.items())
    )

    return {
        "min_removed_blocks": min_removed_blocks,
        "possible_counterexample_m": possible_counterexample_m,
        "hard_branches": hard,
        "tree_ok": tree_ok,
    }


def main() -> None:
    files_ok, file_rows = check_files()
    arithmetic = check_arithmetic()
    all_ok = files_ok and bool(arithmetic["tree_ok"])
    payload = {
        "schema": "ORION.RG.X1B.C15CandidateProofAudit.v1",
        "candidate_claim": "D(C_15^3)=43",
        "artifact_integrity_ok": files_ok,
        "residual_tree_ok": arithmetic["tree_ok"],
        "all_internal_audit_gates": all_ok,
        "file_checks": file_rows,
        "arithmetic": arithmetic,
        "external_peer_review_complete": False,
        "novelty_authority": False,
        "scientific_authority": False,
        "publication_authority": False,
        "infinite_family_authority": False,
    }
    print(PREFIX + json.dumps(payload, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
