#!/usr/bin/env python3
"""Independent replay and structural verifier for the ORION-01 Round-2 study.

Two evidence layers, two outcome paths:

* success path: the committed SUBSET receipt must carry the frozen schema, a
  legal terminal, all gates passed, sorted rows, and no floating-point
  numbers anywhere (receipts are ints/bools/strings/lists only); every
  subset row is then re-executed and must reproduce byte-for-byte;
* fail-closed path (no SUBSET receipt exists): the committed RESULTS receipt
  must carry the fail terminal, passing audits and freeze binding, and every
  one of its rows — cap rows included — is re-executed and must reproduce
  byte-for-byte, so a fail-closed outcome is enforced as strongly as a
  positive one.

Usage:
    python verify_orion01_round2_atomic.py           # verify + replay
    python verify_orion01_round2_atomic.py --check   # same, CI gate form

Exit codes: 0 verified, 4 mismatch/failure.  The final stdout line is the
receipt terminal.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
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


def assert_package_integrity(results: dict[str, Any]) -> None:
    manifest_path = HERE / "PACKAGE_MANIFEST_R2.json"
    manifest = load_receipt_no_floats(manifest_path)
    if manifest.get("schema") != "ORION.ORION01.Round2.PackageManifest.v1":
        raise VerificationFailure("unexpected package manifest schema")
    if manifest.get("paper_id") != "ORION-01":
        raise VerificationFailure("package manifest paper identity mismatch")
    entries = manifest.get("entries", [])
    paths = [entry.get("path") for entry in entries]
    if len(paths) != len(set(paths)) or manifest_path.relative_to(REPO_ROOT).as_posix() in paths:
        raise VerificationFailure("manifest duplicate or self-hash entry")
    for entry in entries:
        path = REPO_ROOT / entry["path"]
        if not path.is_file():
            raise VerificationFailure(f"manifest file missing: {entry['path']}")
        payload = path.read_bytes()
        if len(payload) != entry["bytes"]:
            raise VerificationFailure(f"manifest byte mismatch: {entry['path']}")
        if hashlib.sha256(payload).hexdigest() != entry["sha256"]:
            raise VerificationFailure(f"manifest digest mismatch: {entry['path']}")
    ledger = load_receipt_no_floats(HERE / "ATTEMPT_LEDGER_R2.json")
    if ledger.get("scientific_authority_delta") != "NONE":
        raise VerificationFailure("attempt ledger authority delta is not NONE")
    if ledger.get("overall_terminal") != "CANNOT_CHECK_MOVE_COMPLETENESS":
        raise VerificationFailure("attempt ledger lost the fail-closed terminal")
    if ledger.get("stop_condition") is not None:
        raise VerificationFailure("active material negative carries a premature stop condition")
    if ledger.get("material_negative_status") != "ACTIVE":
        raise VerificationFailure("material fail-closed negative is not ACTIVE")
    if ledger.get("final_freeze_claimed_by_this_successor") is not False:
        raise VerificationFailure("successor improperly claims a final freeze")
    if ledger.get("current_paper_freeze", {}).get("mutated_by_successor") is not False:
        raise VerificationFailure("successor claims mutation of the frozen paper")
    if ledger.get("raw_result", {}).get("sha256") != hashlib.sha256(
        (HERE / "ORION01_ROUND2_ATOMIC_RESULTS.json").read_bytes()
    ).hexdigest():
        raise VerificationFailure("attempt ledger raw-result digest mismatch")
    rows = results["rows"]
    if sum(bool(row.get("cap_hit")) for row in rows) != 8:
        raise VerificationFailure("attempt ledger package expected eight cap rows")
    if sum(bool(row.get("strict_gap")) for row in rows) != 4:
        raise VerificationFailure("attempt ledger package expected four strict gaps")
    if sum(bool(row.get("strict_gap")) and not row.get("generic_match", True) for row in rows) != 2:
        raise VerificationFailure("attempt ledger package expected two generic misses")


def assert_failure_structure(results: dict[str, Any], study: Any) -> None:
    """Structure gate for the fail-closed outcome path (no subset receipt).

    A fail-closed run writes only the RESULTS receipt.  The terminal, audits,
    freeze binding, and row shapes are enforced here; every row (including the
    cap rows) is replayed by ``replay_results_rows`` below, so the committed
    failure receipt is as strongly bound as the success-subset path.
    """

    registry = study.load_registry()
    if results["schema"] != "ORION.ORION01.Round2.PyZXAtomicCheckerRegistryResults.v1":
        raise VerificationFailure("unexpected results schema")
    if results["paper_id"] != "ORION-01" or results["round"] != 2:
        raise VerificationFailure("results receipt is not ORION-01 Round 2")
    outcome = results["outcome"]
    if outcome["terminal"] != study.FAIL_TERMINAL:
        raise VerificationFailure(
            f"failure receipt carries an unexpected terminal: {outcome['terminal']}"
        )
    if not outcome.get("failure_kind") or not outcome.get("failure_message"):
        raise VerificationFailure("failure receipt lacks failure kind/message")
    if outcome["records_completed_before_failure"] != len(results["rows"]):
        raise VerificationFailure("records_completed_before_failure does not match rows")
    audits = results["audits"]
    if audits["primitive_closure_exact"] is not True:
        raise VerificationFailure("primitive closure audit failed on the failure receipt")
    if audits["hostile_omissions_rejected"] != 12:
        raise VerificationFailure("hostile omission audit failed on the failure receipt")
    if audits["mutator_method_surface_covered"] is not True:
        raise VerificationFailure("mutator surface audit failed on the failure receipt")
    if audits["guard_purity_all_pure"] is not True:
        raise VerificationFailure("guard purity audit failed on the failure receipt")
    if results["freeze_binding"]["introduced_in_one_commit"] is not True:
        raise VerificationFailure("frozen inputs were not introduced in one commit")
    if results["source_verification"]["commit"] != study.EXPECTED_COMMIT:
        raise VerificationFailure("failure receipt bound to an unexpected commit")
    rows = results["rows"]
    indexes = [row["word_index"] for row in rows]
    if indexes != sorted(indexes):
        raise VerificationFailure("results rows are not sorted by word index")
    primary = [row for row in rows if row["domain"] == "primary"]
    probe = [row for row in rows if row["domain"] == "probe"]
    if len(primary) != registry["input_domain"]["primary_word_count"]:
        raise VerificationFailure(f"primary domain count mismatch: {len(primary)}")
    if len(probe) != registry["input_domain"]["boundary_probe_length6_word_count"]:
        raise VerificationFailure(f"probe domain count mismatch: {len(probe)}")
    cap_rows = [row for row in rows if row.get("cap_hit")]
    if not cap_rows:
        raise VerificationFailure("fail-closed receipt without any cap row")
    for row in cap_rows:
        if row["domain"] != "primary":
            raise VerificationFailure("cap row outside the primary domain")
        if "native_resource" in row or "witness" in row:
            raise VerificationFailure("cap row carries arm fields")
    for row in rows:
        if row.get("cap_hit"):
            continue
        if row["domain"] == "primary" and not row.get("interaction_census"):
            raise VerificationFailure("completed primary row without census")
        if not row["witness_replay_ok"]:
            raise VerificationFailure("witness replay flagged false in committed receipt")
        if row["domain"] == "primary" and not row["native_state_represented"]:
            raise VerificationFailure("native output unrepresented for a primary word")


def replay_results_rows(results: dict[str, Any], study: Any) -> int:
    """Replay every committed failure-receipt row, cap rows included."""

    registry = study.load_registry()
    cap = int(registry["max_states_per_input_fail_closed"])
    replayed = 0
    for committed in results["rows"]:
        task = study.WordTask(
            word=tuple(committed["word"]),
            word_index=committed["word_index"],
            mode="execute",
            domain=committed["domain"],
            cap=cap,
        )
        fresh = study.analyze_word(task)
        if committed.get("cap_hit"):
            if not fresh.get("cap_hit"):
                raise VerificationFailure(
                    f"cap row did not reproduce its cap hit: {committed['word']}"
                )
            fresh = {
                key: fresh[key]
                for key in (
                    "word",
                    "word_index",
                    "domain",
                    "start_sha256",
                    "cap_hit",
                    "reachable_states",
                    "reachable_transitions",
                    "move_attempts",
                    "semantic_edges_checked",
                )
            }
        if study.canonical_json(fresh) != study.canonical_json(committed):
            raise VerificationFailure(
                f"results replay mismatch: word_index={committed['word_index']}"
            )
        replayed += 1
    return replayed


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
        if study.SUBSET_RESULTS_PATH.is_file():
            subset = load_receipt_no_floats(study.SUBSET_RESULTS_PATH)
            assert_subset_structure(subset, study)
            replayed = replay_subset_rows(subset, study)
            terminal = subset["outcome"]["terminal"]
        else:
            results = load_receipt_no_floats(study.RESULTS_PATH)
            assert_package_integrity(results)
            assert_failure_structure(results, study)
            replayed = replay_results_rows(results, study)
            terminal = results["outcome"]["terminal"]
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
