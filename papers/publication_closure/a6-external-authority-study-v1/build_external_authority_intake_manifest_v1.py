#!/usr/bin/env python3
"""Derive the frozen A6 ExternalAuthorityPacketIntakeManifest from the eligible pool.

The frozen allocator (allocate_external_authority_packets_v1.py, imported
verbatim) is re-run over the committed eligible pool and its result must be
byte-identical to the committed allocation result before any intake manifest
is emitted: allocation identity is proved, not trusted. The intake rows carry
exactly the fields bound by ORION.A6.ExternalAuthorityPacketIntakeManifest.v1
(validated by the frozen intake validator, imported verbatim) and nothing
else, so the external adjudicator gold packets can bind field-exactly later.

An intake manifest is NEVER emitted on a shortfall terminal: a CANNOT_CHECK
allocation freezes nothing.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
INTAKE_SCHEMA = "ORION.A6.ExternalAuthorityPacketIntakeManifest.v1"
POOL_SCHEMA = "ORION.A6.EligibleExternalAuthorityPacketPool.v1"
ALLOCATION_SCHEMA = "ORION.A6.ExternalAuthorityPreOutcomeAllocation.v1"
FROZEN_TERMINAL = "A6_EXTERNAL_PRIMARY_REPLICATION_ALLOCATION_FROZEN"
SHORTFALL_TERMINAL = "CANNOT_CHECK_A6_PREOUTCOME_QUOTA_OR_DISJOINTNESS_SHORTFALL"
STRATA = (
    "scientific_software_release_provenance_attestation",
    "workflowhub_rocrate_versioned_workflow",
    "scientific_record_transition",
)
ROW_FIELDS = (
    "packet_id",
    "split",
    "stratum",
    "source_family_id",
    "normalized_organization_lineage",
    "artifact_lineage_id",
    "before_version_id",
    "after_version_id",
    "before_sha256",
    "after_sha256",
    "license_or_rights_receipt_id",
    "external_custody_receipt_id",
    "adjudicator_assignment_receipt_id",
    "candidate_visible_packet_sha256",
    "candidate_blind_gold_process_frozen",
)


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot import frozen module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _allocator() -> Any:
    return _load("a6_allocator_v1", HERE / "allocate_external_authority_packets_v1.py")


def _intake_validator() -> Any:
    return _load("a6_intake_validator_v1", HERE / "validate_external_authority_packet_manifest_v1.py")


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def build_intake(pool: dict[str, Any], allocation_result: dict[str, Any]) -> dict[str, Any]:
    allocator = _allocator()
    intake_validator = _intake_validator()
    if pool.get("schema") != POOL_SCHEMA:
        raise ValueError("wrong pool schema")
    if allocation_result.get("schema") != ALLOCATION_SCHEMA:
        raise ValueError("wrong allocation result schema")
    rederived = allocator.allocate(pool)
    if rederived["selection_manifest_sha256"] != allocation_result.get("selection_manifest_sha256"):
        raise ValueError("committed allocation does not re-derive from the committed pool")
    if rederived["terminal"] != allocation_result.get("terminal"):
        raise ValueError("committed allocation terminal does not re-derive")
    if rederived["terminal"] != FROZEN_TERMINAL:
        raise ValueError(f"refusing to emit an intake manifest on a shortfall allocation: {rederived['terminal']}")
    selected = {p["packet_id"]: p for p in rederived["packets"]}
    if len(selected) != len(rederived["packets"]):
        raise ValueError("allocation packets are not uniquely identified")

    rows = []
    for packet in rederived["packets"]:
        row = {field: packet[field] for field in ROW_FIELDS}
        rows.append(row)
    rows.sort(key=lambda r: (STRATA.index(r["stratum"]), 0 if r["split"] == "primary" else 1, r["packet_id"]))
    manifest = {
        "schema": INTAKE_SCHEMA,
        "protected_outcomes_accessed": False,
        "replication_target_n": rederived["replication_target_n"],
        "replication_n_frozen_before_predictions": True,
        "selection_manifest_sha256": rederived["selection_manifest_sha256"],
        "allocation_terminal": rederived["terminal"],
        "packets": rows,
    }
    # The frozen intake validator is authoritative and must pass on the real
    # emitted manifest before it is ever shipped.
    intake_validator.validate(manifest)
    return manifest


def self_test() -> dict[str, Any]:
    allocator = _allocator()
    intake_validator = _intake_validator()
    pool = allocator.fixture()
    allocation = allocator.allocate(pool)
    manifest = build_intake(pool, allocation)
    result = intake_validator.validate(manifest)
    if result["decision"] != "GREEN" or result["primary_n"] != 60 or result["replication_n"] != 6:
        raise ValueError("intake manifest did not validate GREEN on the frozen validator")

    # Shortfall allocations never produce an intake manifest.
    short_pool = allocator.fixture(per=20)
    short_alloc = allocator.allocate(short_pool)
    if short_alloc["terminal"] != SHORTFALL_TERMINAL:
        raise ValueError("fixture(per=20) did not produce the shortfall terminal")
    try:
        build_intake(short_pool, short_alloc)
    except ValueError:
        pass
    else:
        raise AssertionError("shortfall allocation produced an intake manifest")

    # A committed allocation that does not re-derive is rejected (the recorded
    # selection digest is authoritative; the emitted rows always come from the
    # re-derived allocation, never from the committed file).
    forged = json.loads(json.dumps(allocation))
    forged["selection_manifest_sha256"] = "0" * 64
    try:
        build_intake(pool, forged)
    except ValueError:
        pass
    else:
        raise AssertionError("non-rederiving allocation accepted")

    # A committed terminal that does not re-derive is rejected.
    flipped = json.loads(json.dumps(allocation))
    flipped["terminal"] = SHORTFALL_TERMINAL
    try:
        build_intake(pool, flipped)
    except ValueError:
        pass
    else:
        raise AssertionError("non-rederiving terminal accepted")

    # Extra/forbidden fields never enter the emitted rows.
    if any(set(row) != set(ROW_FIELDS) for row in manifest["packets"]):
        raise ValueError("intake rows carry fields outside the bound schema")
    poisoned = json.loads(json.dumps(manifest))
    poisoned["packets"][0]["scientific_gold"] = "ADMIT"
    try:
        intake_validator.validate(poisoned)
    except ValueError:
        pass
    else:
        raise AssertionError("gold-bearing intake manifest accepted")

    # Split flip breaks the quota and is rejected by the frozen validator.
    flipped = json.loads(json.dumps(manifest))
    flipped["packets"][0]["split"] = "replication"
    try:
        intake_validator.validate(flipped)
    except ValueError:
        pass
    else:
        raise AssertionError("split-flipped intake manifest accepted")

    return {
        "decision": "GREEN",
        "intake_schema": INTAKE_SCHEMA,
        "frozen_intake_validator_green": True,
        "allocation_identity_reproved": True,
        "non_rederiving_digest_rejected": True,
        "non_rederiving_terminal_rejected": True,
        "shortfall_never_intakes": True,
        "rows_exactly_bound_fields": True,
        "gold_and_split_mutants_rejected": True,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", type=Path)
    ap.add_argument("--allocation", type=Path)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--validation-output", type=Path)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        result = self_test()
    else:
        if args.pool is None or args.allocation is None or args.output is None:
            ap.error("--pool, --allocation and --output are required unless --self-test")
        pool = json.loads(args.pool.read_text(encoding="utf-8"))
        allocation_result = json.loads(args.allocation.read_text(encoding="utf-8"))
        manifest = build_intake(pool, allocation_result)
        text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        validation = _intake_validator().validate(manifest)
        validation["intake_manifest_sha256"] = hashlib.sha256(args.output.read_bytes()).hexdigest()
        if args.validation_output:
            args.validation_output.parent.mkdir(parents=True, exist_ok=True)
            args.validation_output.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result = validation
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
