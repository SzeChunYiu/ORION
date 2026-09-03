#!/usr/bin/env python3
"""Prepare per-packet external adjudicator prep packets with EMPTY sign-off slots.

For every frozen intake packet this emits one prep file under
adjudication-prep-v1/ carrying (a) the intake-bound fields verbatim and
(b) the candidate-visible packet (target-relevant scientific coordinates +
terminal alphabet), rebuilt from the frozen census bytes and asserted to hash
to the intake's candidate_visible_packet_sha256. The adjudication block is
explicitly UNADJUDICATED: both gold labels are null, the adjudicator receipt
is null, and sign_off_slots_empty is true. Nothing here adjudicates, signs,
promotes, or infers a label; governance sign-off is external continuation.

--verify re-reads a committed prep directory against a committed intake
manifest and the frozen census and fails closed on any drift, any filled
sign-off slot, or any coverage digest mismatch.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PREP_SCHEMA = "ORION.A6.ExternalAdjudicatorPrepPacket.v1"
COVERAGE_SCHEMA = "ORION.A6.AdjudicationPrepCoverageManifest.v1"
INTAKE_SCHEMA = "ORION.A6.ExternalAuthorityPacketIntakeManifest.v1"
STRATA = (
    "scientific_software_release_provenance_attestation",
    "workflowhub_rocrate_versioned_workflow",
    "scientific_record_transition",
)
BOUND_FIELDS = (
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
)
SIGNOFF_KEYS = ("adjudicator_id", "adjudicated_at_utc", "receipt_sha256", "adjudication")
_SAFE = re.compile(r"[^A-Za-z0-9._-]+")


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot import frozen module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _pool_builder() -> Any:
    return _load("a6_pool_builder_v1", HERE / "build_eligible_external_authority_pool_v1.py")


def _intake_validator() -> Any:
    return _load("a6_intake_validator_v1", HERE / "validate_external_authority_packet_manifest_v1.py")


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def safe_name(packet_id: str) -> str:
    return _SAFE.sub("_", packet_id)


def load_census_rows(census_root: Path) -> dict[str, dict[str, Any]]:
    builder = _pool_builder()
    rows: dict[str, dict[str, Any]] = {}
    for stratum in STRATA:
        loaded = builder.load_census_stratum(stratum, census_root)
        for row in loaded["rows"]:
            rows[row["packet_id"]] = row
    return rows


def visible_sha_for(census_row: dict[str, Any]) -> str:
    builder = _pool_builder()
    payload = builder.candidate_visible_payload(census_row)
    return hashlib.sha256(canonical(payload)).hexdigest(), payload


def build_prep(intake: dict[str, Any], census_root: Path, prep_dir: Path) -> dict[str, Any]:
    if intake.get("schema") != INTAKE_SCHEMA:
        raise ValueError("wrong intake schema")
    _intake_validator().validate(intake)
    census_rows = load_census_rows(census_root)
    prep_dir.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, Any]] = []
    names: dict[str, str] = {}
    for row in intake["packets"]:
        pid = row["packet_id"]
        census_row = census_rows.get(pid)
        if census_row is None:
            raise ValueError(f"intake packet not present in the frozen census: {pid}")
        visible_sha, payload = visible_sha_for(census_row)
        if visible_sha != row["candidate_visible_packet_sha256"]:
            raise ValueError(f"candidate-visible payload does not re-derive from the frozen census: {pid}")
        name = f"PACKET_{safe_name(pid)}.json"
        if name in names:
            raise ValueError(f"sanitized filename collision: {name} ({names[name]} vs {pid})")
        names[name] = pid
        prep = {
            "schema": PREP_SCHEMA,
            **{field: row[field] for field in BOUND_FIELDS},
            "candidate_blind_gold_process_frozen": True,
            "candidate_visible_packet": payload,
            "adjudication": {
                "status": "UNADJUDICATED",
                "sign_off_slots_empty": True,
                "labels": {
                    "local_action_release_authority": None,
                    "scientific_discharge_admission_authority": None,
                },
                "adjudicator_receipt": None,
            },
            "template": "papers/publication_closure/a6-external-authority-study-v1/A6_EXTERNAL_ADJUDICATOR_PACKET_TEMPLATE_V1.json",
            "candidate_predictions_in_packet": False,
            "baseline_predictions_in_packet": False,
            "protected_outcomes_in_packet": False,
        }
        path = prep_dir / name
        path.write_text(json.dumps(prep, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        entries.append({
            "packet_id": pid,
            "split": row["split"],
            "stratum": row["stratum"],
            "file": name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "candidate_visible_packet_sha256": row["candidate_visible_packet_sha256"],
        })
    entries.sort(key=lambda e: e["packet_id"])
    counts = {s: {"primary": 0, "replication": 0} for s in STRATA}
    for entry in entries:
        counts[entry["stratum"]][entry["split"]] += 1
    coverage = {
        "schema": COVERAGE_SCHEMA,
        "prep_packet_n": len(entries),
        "counts": counts,
        "sign_off_slots_empty_for_every_packet": True,
        "adjudications_performed": 0,
        "gold_labels_created": False,
        "gold_labels_inferred": False,
        "external_sign_off_present": False,
        "packets": entries,
        "scientific_authority_delta": "NONE__PREP_ONLY_SIGN_OFF_SLOTS_EMPTY",
    }
    (prep_dir / "A6_PREP_COVERAGE_MANIFEST_V1.json").write_text(json.dumps(coverage, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return coverage


def verify_prep(intake: dict[str, Any], census_root: Path, prep_dir: Path) -> dict[str, Any]:
    if intake.get("schema") != INTAKE_SCHEMA:
        raise ValueError("wrong intake schema")
    _intake_validator().validate(intake)
    coverage = json.loads((prep_dir / "A6_PREP_COVERAGE_MANIFEST_V1.json").read_text(encoding="utf-8"))
    if coverage.get("schema") != COVERAGE_SCHEMA:
        raise ValueError("wrong coverage schema")
    if coverage.get("sign_off_slots_empty_for_every_packet") is not True or coverage.get("external_sign_off_present") is not False:
        raise ValueError("coverage manifest does not assert empty sign-off slots")
    by_id = {e["packet_id"]: e for e in coverage["packets"]}
    if len(by_id) != len(coverage["packets"]) or set(by_id) != {r["packet_id"] for r in intake["packets"]}:
        raise ValueError("coverage does not exactly cover the frozen intake packets")
    census_rows = load_census_rows(census_root)
    for row in intake["packets"]:
        pid = row["packet_id"]
        entry = by_id[pid]
        path = prep_dir / entry["file"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"prep file digest mismatch: {pid}")
        prep = json.loads(path.read_text(encoding="utf-8"))
        if prep.get("schema") != PREP_SCHEMA:
            raise ValueError(f"prep schema mismatch: {pid}")
        for field in BOUND_FIELDS:
            if prep.get(field) != row[field]:
                raise ValueError(f"prep bound field does not match the frozen intake packet ({field}): {pid}")
        adjudication = prep.get("adjudication")
        if not isinstance(adjudication, dict) or adjudication.get("status") != "UNADJUDICATED" or adjudication.get("sign_off_slots_empty") is not True:
            raise ValueError(f"prep adjudication block is not explicitly unadjudicated: {pid}")
        if adjudication.get("adjudicator_receipt") is not None:
            raise ValueError(f"sign-off slot is filled: {pid}")
        labels = adjudication.get("labels")
        if not isinstance(labels, dict) or any(labels.get(k) is not None for k in ("local_action_release_authority", "scientific_discharge_admission_authority")):
            raise ValueError(f"label slot is filled: {pid}")
        visible_sha, _payload = visible_sha_for(census_rows[pid])
        if visible_sha != row["candidate_visible_packet_sha256"] or prep["candidate_visible_packet_sha256"] != visible_sha:
            raise ValueError(f"candidate-visible payload does not re-derive: {pid}")
    for path in sorted(prep_dir.glob("PACKET_*.json")):
        prep = json.loads(path.read_text(encoding="utf-8"))
        for key in ("candidate_predictions_in_packet", "baseline_predictions_in_packet", "protected_outcomes_in_packet"):
            if prep.get(key) is not False:
                raise ValueError(f"{key} is not false in {path.name}")
    return {
        "schema": "ORION.A6.AdjudicationPrepVerification.v1",
        "decision": "GREEN",
        "prep_packet_n": len(by_id),
        "bound_fields_exact": True,
        "sign_off_slots_empty": True,
        "candidate_visible_payloads_rederive": True,
        "coverage_digests_match": True,
        "adjudications_performed": 0,
        "scientific_authority_delta": "NONE__PREP_VERIFICATION_ONLY",
    }


def self_test() -> dict[str, Any]:
    allocator = _load("a6_allocator_v1", HERE / "allocate_external_authority_packets_v1.py")
    builder = _pool_builder()
    intake_builder = _load("a6_intake_builder_v1", HERE / "build_external_authority_intake_manifest_v1.py")

    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        census_root = builder._synthetic_census(base)
        freeze_path = builder._synthetic_freeze(base)
        pool = builder.build(census_root, freeze_path)
        allocation = allocator.allocate(pool)
        intake = intake_builder.build_intake(pool, allocation)
        prep_dir = base / "prep"
        coverage = build_prep(intake, census_root, prep_dir)
        if coverage["prep_packet_n"] != len(intake["packets"]):
            raise ValueError("coverage does not cover every intake packet")
        result = verify_prep(intake, census_root, prep_dir)
        if result["decision"] != "GREEN":
            raise ValueError("clean prep directory did not verify")

        # A filled label slot is rejected.
        victim = sorted(prep_dir.glob("PACKET_*.json"))[0]
        prep = json.loads(victim.read_text())
        prep["adjudication"]["labels"]["local_action_release_authority"] = "ADMIT"
        victim.write_text(json.dumps(prep, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        try:
            verify_prep(intake, census_root, prep_dir)
        except ValueError:
            pass
        else:
            raise AssertionError("filled label slot accepted")

        # A filled receipt slot is rejected.
        prep = json.loads(victim.read_text())
        prep["adjudication"]["labels"]["local_action_release_authority"] = None
        prep["adjudication"]["adjudicator_receipt"] = {"adjudicator_id": "x"}
        victim.write_text(json.dumps(prep, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        try:
            verify_prep(intake, census_root, prep_dir)
        except ValueError:
            pass
        else:
            raise AssertionError("filled receipt slot accepted")

        # A drifted bound field is rejected.
        prep = json.loads(victim.read_text())
        prep["adjudication"]["adjudicator_receipt"] = None
        prep["before_sha256"] = "0" * 64
        victim.write_text(json.dumps(prep, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        try:
            verify_prep(intake, census_root, prep_dir)
        except ValueError:
            pass
        else:
            raise AssertionError("drifted bound field accepted")

        # Restore the true bound field, then tamper the coverage digest itself.
        prep = json.loads(victim.read_text())
        row = next(r for r in intake["packets"] if r["packet_id"] == prep["packet_id"])
        prep["before_sha256"] = row["before_sha256"]
        victim.write_text(json.dumps(prep, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        coverage_manifest = json.loads((prep_dir / "A6_PREP_COVERAGE_MANIFEST_V1.json").read_text())
        coverage_manifest["packets"][0]["sha256"] = "0" * 64
        (prep_dir / "A6_PREP_COVERAGE_MANIFEST_V1.json").write_text(json.dumps(coverage_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        try:
            verify_prep(intake, census_root, prep_dir)
        except ValueError:
            pass
        else:
            raise AssertionError("tampered coverage digest accepted")

    return {
        "decision": "GREEN",
        "prep_schema": PREP_SCHEMA,
        "coverage_schema": COVERAGE_SCHEMA,
        "clean_prep_verifies": True,
        "filled_label_rejected": True,
        "filled_receipt_rejected": True,
        "bound_field_drift_rejected": True,
        "coverage_tamper_rejected": True,
        "sign_off_slots_empty": True,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--intake", type=Path)
    ap.add_argument("--census-root", type=Path, default=HERE)
    ap.add_argument("--prep-dir", type=Path, default=HERE / "adjudication-prep-v1")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        result = self_test()
    else:
        if args.intake is None:
            ap.error("--intake is required unless --self-test")
        intake = json.loads(args.intake.read_text(encoding="utf-8"))
        result = verify_prep(intake, args.census_root, args.prep_dir) if args.verify else build_prep(intake, args.census_root, args.prep_dir)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
