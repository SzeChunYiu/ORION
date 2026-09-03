#!/usr/bin/env python3
"""Validate workflowhub-member-manifest-freeze-v1/RESULT_V1.json.

Fail-closed checker for the member-manifest materialization boundary result:
the 128-family partition must exactly cover the frozen successor frame, the
terminal must be the CANNOT_CHECK reproducibility boundary (never a green
materialization claim), all custody flags must be false, and no partial member
manifests may exist alongside a fail-closed result. Self-test only.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
FREEZE_DIR = HERE / "workflowhub-member-manifest-freeze-v1"
RESULT_PATH = FREEZE_DIR / "RESULT_V1.json"
TERMINAL = "CANNOT_CHECK_MEMBER_MANIFEST_REPRODUCIBILITY"
VOLATILE_MEMBERS = ["ro-crate-metadata.json", "ro-crate-preview.html"]
SCHEMA = "ORION.A3.MemberManifestFreezeResult.v1"


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def validate(doc: dict[str, Any], frame: dict[str, dict[str, Any]], *, expect_no_partial_files: bool = True) -> None:
    if doc.get("schema") != SCHEMA:
        raise ValueError("result schema mismatch")
    if doc.get("terminal") != TERMINAL:
        raise ValueError(f"terminal must be {TERMINAL}")
    if doc.get("successor_frame_sha256") != _load("a3_curator_validator_mmfr", HERE / "validate_external_curator_packet_v1.py").EXPECTED_SUCCESSOR_FRAME_SHA256:
        raise ValueError("result does not bind the frozen successor frame")
    if doc.get("successor_frame_rebound") is not False:
        raise ValueError("result must not claim a frame rebind")

    partition = doc.get("partition")
    if not isinstance(partition, dict):
        raise ValueError("partition must be an object")
    stable = partition.get("stable_workflow_ids")
    volatile = partition.get("volatile_request_generated_workflow_ids")
    if not isinstance(stable, list) or not isinstance(volatile, list):
        raise ValueError("partition id lists must be lists")
    stable_set, volatile_set = set(stable), set(volatile)
    frame_set = set(frame)
    if stable_set & volatile_set:
        raise ValueError("stable and volatile partitions overlap")
    if stable_set | volatile_set != frame_set:
        raise ValueError("partition does not exactly cover the frozen 128-family frame")
    if len(stable) != len(stable_set) or len(volatile) != len(volatile_set):
        raise ValueError("partition id lists contain duplicates")
    if partition.get("frame_n") != len(frame_set) or partition.get("frame_n") != 128:
        raise ValueError("partition frame_n mismatch")
    if partition.get("stable_reproduces_frozen_n") != len(stable_set):
        raise ValueError("stable count mismatch")
    if partition.get("volatile_request_generated_n") != len(volatile_set):
        raise ValueError("volatile count mismatch")
    if {"625", "631"} - stable_set:
        raise ValueError("replacement families 625/631 must be in the stable partition")

    evidence = doc.get("evidence")
    if not isinstance(evidence, dict):
        raise ValueError("evidence must be an object")
    if sorted(evidence.get("volatile_member_paths", [])) != sorted(VOLATILE_MEMBERS):
        raise ValueError("volatile member paths must be exactly the two request-generated crate files")
    for key in ("volatile_mechanism", "stable_mechanism", "consequence", "workflow_content_members_unaffected"):
        if not str(evidence.get(key, "")).strip():
            raise ValueError(f"evidence.{key} must be non-empty")

    flags = doc.get("flags")
    if not isinstance(flags, dict) or not all(v is False for v in flags.values()):
        raise ValueError("all result flags must be false")
    for flag in ("change_stratum_adjudicated", "external_gold_accessed", "candidate_predictions_computed",
                 "protected_outcomes_accessed", "member_manifests_committed", "successor_frame_rebound"):
        if flag not in flags:
            raise ValueError(f"missing required false flag: {flag}")
    if doc.get("grants_scientific_authority") is not False:
        raise ValueError("grants_scientific_authority must be false")
    if doc.get("scientific_authority_delta") != "NONE__SUBSTRATE_DIAGNOSIS_ONLY":
        raise ValueError("scientific_authority_delta mismatch")
    if not str(doc.get("required_next_step_not_taken_by_this_lane", "")).strip():
        raise ValueError("required_next_step_not_taken_by_this_lane must be recorded")

    if expect_no_partial_files:
        if flags["member_manifests_committed"] is False and _partial_manifest_files_present():
            raise ValueError("fail-closed result but partial member-manifest files exist in the freeze directory")


def _partial_manifest_files_present() -> bool:
    # Absence cross-checked two ways: glob pattern and directory listing scan.
    if list(FREEZE_DIR.glob("FAMILIES_*.json")):
        return True
    if FREEZE_DIR.exists():
        for entry in FREEZE_DIR.iterdir():
            if entry.name.startswith("FAMILIES_") and entry.suffix == ".json":
                return True
    return False


def self_test() -> dict[str, Any]:
    curator = _load("a3_curator_validator_mmfr_selftest", HERE / "validate_external_curator_packet_v1.py")
    frame = curator.load_source_frame()
    doc = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    validate(doc, frame)

    def mutated(**changes: Any) -> dict[str, Any]:
        clone = json.loads(json.dumps(doc))
        for key, value in changes.items():
            section, _, field = key.rpartition(".")
            node = clone if not section else clone[section]
            node[field] = value
        return clone

    hostile: list[tuple[str, dict[str, Any]]] = []
    hostile.append(("terminal flipped to GREEN", mutated(**{"terminal": "GREEN_MEMBER_MANIFESTS_BOUND"})))
    hostile.append(("frame sha rebound", mutated(**{"successor_frame_sha256": "0" * 64})))
    hostile.append(("rebind claimed", mutated(**{"successor_frame_rebound": True})))
    stable = list(doc["partition"]["stable_workflow_ids"])
    hostile.append(("unknown workflow added", mutated(**{"partition.stable_workflow_ids": stable + ["999999999"]})))
    hostile.append(("stable/volatile overlap", mutated(**{"partition.volatile_request_generated_workflow_ids": doc["partition"]["volatile_request_generated_workflow_ids"] + [stable[0]]})))
    hostile.append(("family dropped from partition", mutated(**{"partition.stable_workflow_ids": stable[1:]})))
    hostile.append(("stable count inflated", mutated(**{"partition.stable_reproduces_frozen_n": len(stable) + 5})))
    hostile.append(("replacement not stable", mutated(**{"partition.stable_workflow_ids": [w for w in stable if w != "625"]})))
    hostile.append(("gold flag true", mutated(**{"flags.external_gold_accessed": True})))
    hostile.append(("authority delta claimed", mutated(**{"scientific_authority_delta": "NONE__RESULT_SUPPORTS_REBIND"})))
    hostile.append(("next step emptied", mutated(**{"required_next_step_not_taken_by_this_lane": ""})))
    for label, packet in hostile:
        try:
            validate(packet, frame)
        except ValueError:
            continue
        raise AssertionError(f"hostile result accepted: {label}")

    return {
        "decision": "GREEN",
        "result_sha256": __import__("hashlib").sha256(RESULT_PATH.read_bytes()).hexdigest(),
        "terminal": TERMINAL,
        "frame_n": len(frame),
        "stable_n": len(doc["partition"]["stable_workflow_ids"]),
        "volatile_n": len(doc["partition"]["volatile_request_generated_workflow_ids"]),
        "partition_exact_frame_cover": True,
        "hostile_mutations_rejected": len(hostile),
        "partial_manifest_files_present": _partial_manifest_files_present(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run the result checker")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("this checker is self-test only")
    print(json.dumps(self_test(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
