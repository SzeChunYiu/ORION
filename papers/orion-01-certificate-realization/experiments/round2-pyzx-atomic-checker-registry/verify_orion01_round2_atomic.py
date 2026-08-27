#!/usr/bin/env python3
"""Independent replay and structural verifier for the ORION-01 Round-2 study.

Two evidence layers:

* structural: the committed SUBSET receipt must carry the frozen schema, a
  legal terminal, all gates passed, sorted rows, and no floating-point
  numbers anywhere (receipts are ints/bools/strings/lists only);
* replay: every committed subset row is re-executed from the frozen task
  domain with the pinned production system and must reproduce the committed
  row byte-for-byte (canonical JSON equality).

Usage:
    python verify_orion01_round2_atomic.py           # verify + replay
    python verify_orion01_round2_atomic.py --check   # same, CI gate form

Exit codes: 0 verified, 4 mismatch/failure.  The final stdout line is the
receipt terminal.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "orion01_round2_atomic_registry.py"


def _load_module() -> Any:
    spec = importlib.util.spec_from_file_location("orion01_round2_atomic_registry", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class VerificationFailure(RuntimeError):
    pass


def _reject_float(value: str) -> float:
    raise VerificationFailure(f"receipt contains a floating-point literal: {value}")


def load_receipt_no_floats(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise VerificationFailure(f"missing receipt: {path.name}")
    return json.loads(path.read_text(encoding="utf-8"), parse_float=_reject_float)


def assert_subset_structure(subset: dict[str, Any], study: Any) -> None:
    registry = study.load_registry()
    if subset["schema"] != "ORION.ORION01.Round2.PyZXAtomicCheckerRegistryResultsSubset.v1":
        raise VerificationFailure("unexpected subset schema")
    if subset["paper_id"] != "ORION-01" or subset["round"] != 2:
        raise VerificationFailure("subset receipt is not ORION-01 Round 2")
    if not subset["gates_all_passed"]:
        raise VerificationFailure("subset receipt gates did not all pass")
    terminal = subset["outcome"]["terminal"]
    if terminal not in registry["allowed_terminals"]:
        raise VerificationFailure(f"terminal not allowed: {terminal}")
    rows = subset["rows"]
    indexes = [row["word_index"] for row in rows]
    if indexes != sorted(indexes):
        raise VerificationFailure("subset rows are not sorted by word index")
    if len(rows) != subset["subset_row_count"]:
        raise VerificationFailure("subset_row_count does not match row count")
    if subset["critical_interactions"]["pair_count"] != len(registry["registered_schemas"]) ** 2:
        raise VerificationFailure("critical-interaction matrix is not 12x12")
    primary = subset["domain_counts"]["primary"]
    probe = subset["domain_counts"]["probe"]
    if primary != registry["input_domain"]["primary_word_count"]:
        raise VerificationFailure(f"primary domain count mismatch: {primary}")
    if probe != registry["input_domain"]["boundary_probe_length6_word_count"]:
        raise VerificationFailure(f"probe domain count mismatch: {probe}")
    if subset["freeze_binding"]["introduced_in_one_commit"] is not True:
        raise VerificationFailure("frozen inputs were not introduced in one commit")
    if subset["source_verification"]["commit"] != study.EXPECTED_COMMIT:
        raise VerificationFailure("subset receipt bound to an unexpected commit")
    for row in rows:
        if "interaction_census" in row or "wall_seconds" in row:
            raise VerificationFailure("subset row carries non-replayable fields")
        if row.get("cap_hit"):
            raise VerificationFailure("subset row hit the fail-closed cap")
        if row["domain"] == "primary" and not row["native_state_represented"]:
            raise VerificationFailure("native output unrepresented for a primary word")
        if not row["witness_replay_ok"]:
            raise VerificationFailure("witness replay flagged false in committed receipt")


def replay_subset_rows(subset: dict[str, Any], study: Any) -> int:
    registry = study.load_registry()
    cap = int(registry["max_states_per_input_fail_closed"])
    for committed in subset["rows"]:
        task = study.WordTask(
            word=tuple(committed["word"]),
            word_index=committed["word_index"],
            mode="execute",
            domain=committed["domain"],
            cap=cap,
        )
        fresh = study.analyze_word(task)
        census = fresh.pop("interaction_census", None)
        if committed["domain"] == "primary" and census is None:
            raise VerificationFailure(f"missing census on replay: {committed['word']}")
        if committed.get("strict_gap"):
            start = study.start_state_from_word(committed["word"])
            native_state, _ = study.native_full_reduce(start)
            hostile = study.hostile_extension_outcomes(
                native_state, tuple(committed["optimum_resource"])
            )
            fresh["hostile_collapse"] = hostile["any_collapse"]
        if study.canonical_json(fresh) != study.canonical_json(committed):
            raise VerificationFailure(f"subset replay mismatch: word_index={committed['word_index']}")
    return len(subset["rows"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ORION-01 Round-2 subset verifier")
    parser.add_argument("--check", action="store_true", help="CI gate form (same evidence)")
    args = parser.parse_args(argv)

    study = _load_module()
    try:
        subset = load_receipt_no_floats(study.SUBSET_RESULTS_PATH)
        assert_subset_structure(subset, study)
        replayed = replay_subset_rows(subset, study)
        terminal = subset["outcome"]["terminal"]
    except VerificationFailure as failure:
        print(f"VERIFICATION_FAILURE: {failure}")
        return 4
    except Exception as exc:  # noqa: BLE001 - any replay error fails the gate
        print(f"VERIFICATION_FAILURE: {type(exc).__name__}: {exc}")
        return 4

    print(
        study.canonical_json(
            {
                "verified": True,
                "rows_replayed": replayed,
                "terminal": terminal,
                "mode": "check" if args.check else "verify",
            }
        )
    )
    print(terminal)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
