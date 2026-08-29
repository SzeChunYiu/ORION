#!/usr/bin/env python3
"""Fail-closed aggregation of two byte-identical runs for all eight R3 tasks."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import run_orion01_round3_cap8 as r3

TERMINAL_MAP = {
    "AB_R2_ATOMIC_CHECKER_REGISTRY_REALIZED_GAP": "AB_R3_CAP8_EXTENSION_REALIZED_GAP",
    "AB_R2_ATOMIC_CHECKER_REGISTRY_NO_STRICT_GAP": "AB_R3_CAP8_EXTENSION_NO_STRICT_GAP",
    "AB_R2_GAP_MATCHED_BY_GENERIC_SEARCH": "AB_R3_CAP8_EXTENSION_GAP_MATCHED_BY_GENERIC_SEARCH",
    "AB_R2_CROSS_MOVE_COLLAPSES_GAP": "AB_R3_CAP8_EXTENSION_CROSS_MOVE_COLLAPSES_GAP",
}


def sha_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_pairs(results_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    payloads: list[dict[str, Any]] = []
    receipts: list[dict[str, Any]] = []
    for task_index in range(len(r3.TASKS)):
        p1 = results_dir / f"task{task_index}.run1.json"
        p2 = results_dir / f"task{task_index}.run2.json"
        b1, b2 = p1.read_bytes(), p2.read_bytes()
        if b1 != b2:
            raise RuntimeError(f"task {task_index} runs are not byte-identical")
        payload = json.loads(b1)
        if payload.get("schema") != "ORION.ORION01.Round3.Cap8TaskResult.v1":
            raise RuntimeError(f"task {task_index} schema mismatch")
        if payload.get("task_index") != task_index:
            raise RuntimeError(f"task {task_index} identity mismatch")
        payloads.append(payload)
        receipts.append(
            {
                "task_index": task_index,
                "sha256": sha_bytes(b1),
                "bytes": len(b1),
                "byte_identical_two_runs": True,
            }
        )
    return payloads, receipts


def aggregate(results_dir: Path) -> dict[str, Any]:
    binding = r3.verify_bindings()
    freeze = r3.freeze_binding(binding)
    payloads, receipts = load_pairs(results_dir)
    task_terminal = r3.task_set_terminal(payloads)
    base: dict[str, Any] = {
        "schema": "ORION.ORION01.Round3.Cap8AggregateResult.v1",
        "paper_id": "ORION-01",
        "round": 3,
        "date": "2026-08-28",
        "parent_round2_result_sha256": r3.sha256(
            r3.R2 / "ORION01_ROUND2_ATOMIC_RESULTS.json"
        ),
        "source_binding_sha256": r3.sha256(r3.SOURCE_BINDING),
        "freeze_binding": freeze,
        "task_receipts": receipts,
        "task_set_terminal": task_terminal,
        "scientific_authority_delta": "NONE",
        "current_paper_freeze_mutated": False,
        "final_freeze_claimed": False,
    }
    if task_terminal == "CANNOT_CHECK_MOVE_COMPLETENESS":
        base.update(
            {
                "terminal": "CANNOT_CHECK_MOVE_COMPLETENESS",
                "full_domain_reconstruction": None,
                "approximate_result_promoted": False,
            }
        )
        return base
    parent = json.loads(
        (r3.R2 / "ORION01_ROUND2_ATOMIC_RESULTS.json").read_text()
    )
    replacements = {payload["word_index"]: payload["row"] for payload in payloads}
    if set(replacements) != {index for index, _word in r3.TASKS}:
        raise RuntimeError("replacement task set mismatch")
    records = [replacements.get(row["word_index"], row) for row in parent["rows"]]
    if any(row.get("cap_hit") for row in records if row["domain"] == "primary"):
        raise RuntimeError("full-domain reconstruction retained a cap row")
    full = r3.r2.success_receipt(
        "r3-cap8-exact-extension",
        r3.r2.load_registry(),
        parent["source_verification"],
        parent["audits"],
        freeze,
        records,
    )
    parent_terminal = full["outcome"]["terminal"]
    if parent_terminal not in TERMINAL_MAP:
        raise RuntimeError(f"unmapped full-domain terminal: {parent_terminal}")
    base.update(
        {
            "terminal": TERMINAL_MAP[parent_terminal],
            "full_domain_reconstruction": full,
            "approximate_result_promoted": False,
        }
    )
    return base


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = aggregate(args.results_dir)
    args.output.write_text(r3.canonical_json(payload) + "\n")
    print(payload["terminal"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
