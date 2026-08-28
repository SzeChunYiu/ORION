#!/usr/bin/env python3
"""ORION-01 Round-3 exact cap-word extension.

This outcome-blind successor changes one lever only: the exact per-word state
budget for the eight Round-2 cap words.  All PyZX source, registered moves,
state serialization, semantic checks, resource order, native arm, generic
control, and hostile extensions are inherited byte-for-byte from Round 2.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
R2 = ROOT / "development/orion-01-round2-atomic-registry-2026-08-27"
R2_MODULE = R2 / "orion01_round2_atomic_registry.py"
SOURCE_BINDING = HERE / "SOURCE_BINDING_R3.json"
STATE_CAP = 500_000
TASKS = (
    (259, ("S0", "CX10", "S0")),
    (261, ("S0", "CX10", "T0")),
    (316, ("S1", "CX01", "S1")),
    (318, ("S1", "CX01", "T1")),
    (387, ("T0", "CX10", "S0")),
    (389, ("T0", "CX10", "T0")),
    (444, ("T1", "CX01", "S1")),
    (446, ("T1", "CX01", "T1")),
)


def _load_r2() -> Any:
    spec = importlib.util.spec_from_file_location("orion01_round2_parent", R2_MODULE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


r2 = _load_r2()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_bindings() -> dict[str, Any]:
    binding = json.loads(SOURCE_BINDING.read_text(encoding="utf-8"))
    if binding.get("schema") != "ORION.ORION01.Round3.SourceBinding.v1":
        raise RuntimeError("unexpected Round-3 source-binding schema")
    if binding.get("state_cap") != STATE_CAP or binding.get("tasks") != [
        {"word_index": index, "word": list(word)} for index, word in TASKS
    ]:
        raise RuntimeError("Round-3 task or cap binding drift")
    for entry in binding["entries"]:
        path = ROOT / entry["path"]
        payload = path.read_bytes()
        if len(payload) != entry["bytes"] or hashlib.sha256(payload).hexdigest() != entry["sha256"]:
            raise RuntimeError(f"source binding mismatch: {entry[path]}")
    return binding


def freeze_binding(binding: dict[str, Any]) -> dict[str, Any]:
    paths = binding.get("r3_frozen_paths", [])
    if not paths or SOURCE_BINDING.relative_to(ROOT).as_posix() not in paths:
        raise RuntimeError("Round-3 frozen path set is incomplete")
    commits = set()
    for path in paths:
        commit = subprocess.check_output(
            ["git", "-C", str(ROOT), "log", "--diff-filter=A", "-1", "--format=%H", "--", path],
            text=True,
        ).strip()
        if not commit:
            raise RuntimeError(f"no introduction commit for {path}")
        commits.add(commit)
    if len(commits) != 1:
        raise RuntimeError("Round-3 frozen inputs were not introduced in one commit")
    dirty = subprocess.run(
        ["git", "-C", str(ROOT), "diff", "--quiet", "HEAD", "--", *paths],
        check=False,
    ).returncode
    if dirty != 0:
        raise RuntimeError("Round-3 frozen inputs are dirty")
    return {
        "introduced_in_one_commit": True,
        "introduction_commit": next(iter(commits)),
        "frozen_paths": paths,
        "worktree_clean_for_frozen_inputs": True,
    }



def task_at(task_index: int) -> tuple[int, tuple[str, ...]]:
    if task_index < 0 or task_index >= len(TASKS):
        raise ValueError(f"task index out of range: {task_index}")
    return TASKS[task_index]



def task_set_terminal(payloads: list[dict[str, Any]]) -> str:
    indexes = sorted(payload.get("task_index") for payload in payloads)
    if indexes != list(range(len(TASKS))):
        raise ValueError("receipts do not cover the exact task set")
    terminals = [payload.get("terminal") for payload in payloads]
    if any(terminal == "CANNOT_CHECK_MOVE_COMPLETENESS" for terminal in terminals):
        return "CANNOT_CHECK_MOVE_COMPLETENESS"
    if terminals != ["R3_CAP8_TASK_EXACT_EXHAUSTION_COMPLETE"] * len(TASKS):
        raise ValueError("unexpected task terminal")
    return "R3_CAP8_TASK_SET_EXACT_EXHAUSTION_COMPLETE"


def build_receipt(
    task_index: int,
    row: dict[str, Any],
    hostile: dict[str, Any] | None = None,
    freeze: dict[str, Any] | None = None,
) -> dict[str, Any]:
    index, word = task_at(task_index)
    if row.get("word_index") != index or tuple(row.get("word", ())) != word:
        raise ValueError("result row does not match the frozen task")
    cap_hit = bool(row.get("cap_hit"))
    terminal = (
        "CANNOT_CHECK_MOVE_COMPLETENESS"
        if cap_hit
        else "R3_CAP8_TASK_EXACT_EXHAUSTION_COMPLETE"
    )
    return {
        "schema": "ORION.ORION01.Round3.Cap8TaskResult.v1",
        "paper_id": "ORION-01",
        "round": 3,
        "date": "2026-08-28",
        "task_index": task_index,
        "word_index": index,
        "word": list(word),
        "state_cap": STATE_CAP,
        "parent_round2_result_sha256": sha256(R2 / "ORION01_ROUND2_ATOMIC_RESULTS.json"),
        "terminal": terminal,
        "row": row,
        "hostile_extensions": hostile,
        "approximate_result_promoted": False,
        "full_domain_terminal_claimed": False,
        "independent_implementation": False,
        "freeze_binding": freeze,
        "source_binding_sha256": sha256(SOURCE_BINDING) if SOURCE_BINDING.is_file() else None,
        "scientific_authority_delta": "NONE",
    }


def execute(task_index: int) -> dict[str, Any]:
    binding = verify_bindings()
    freeze = freeze_binding(binding)
    index, word = task_at(task_index)
    task = r2.WordTask(
        word=word,
        word_index=index,
        mode="execute",
        domain="primary",
        cap=STATE_CAP,
    )
    row = r2.analyze_word(task)
    hostile = None
    if not row.get("cap_hit") and row.get("strict_gap"):
        start = r2.start_state_from_word(word)
        native_state, _ = r2.native_full_reduce(start)
        hostile = r2.hostile_extension_outcomes(
            native_state, tuple(row["optimum_resource"])
        )
    return build_receipt(task_index, row, hostile, freeze)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-index", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    payload = execute(args.task_index)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(canonical_json(payload) + "\n", encoding="utf-8")
    print(payload["terminal"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
