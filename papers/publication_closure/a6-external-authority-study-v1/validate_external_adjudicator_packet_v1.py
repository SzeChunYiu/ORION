#!/usr/bin/env python3
"""Validate externally authored A6 adjudicator gold packets without creating labels.

Each packet must bind field-exactly to one frozen intake packet
(ORION.A6.ExternalAuthorityPacketIntakeManifest.v1) and carry BOTH gold labels
(local_action_release_authority, scientific_discharge_admission_authority) over
the terminal alphabet ADMIT/DENY/CANNOT_CHECK. The validator never infers a
label, never fills an unadjudicated packet, and never reads ORION predictions
or protected outcomes.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import validate_external_authority_packet_manifest_v1 as intake_mod  # noqa: E402

GOLD_SCHEMA = "ORION.A6.ExternalAdjudicatorGoldPacket.v1"
INTAKE_SCHEMA = "ORION.A6.ExternalAuthorityPacketIntakeManifest.v1"
LABELS = ("local_action_release_authority", "scientific_discharge_admission_authority")
TARGETS = {"ADMIT", "DENY", "CANNOT_CHECK"}
EXACT_FIELDS = (
    "stratum",
    "split",
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
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def require_nonempty(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def require_hex64(value: Any, label: str) -> str:
    value = require_nonempty(value, label)
    if not HEX64.fullmatch(value):
        raise ValueError(f"{label} must be lowercase SHA-256 hex")
    return value


def load_intake(path: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    intake_mod.validate(manifest)
    index: dict[str, dict[str, Any]] = {}
    for row in manifest["packets"]:
        if row["packet_id"] in index:
            raise ValueError(f"duplicate intake packet: {row['packet_id']}")
        index[row["packet_id"]] = row
    return manifest, index


def validate_label(label_name: str, label: Any) -> str:
    if not isinstance(label, dict):
        raise ValueError(f"labels.{label_name} must be an object")
    target = label.get("target")
    if target not in TARGETS:
        raise ValueError(f"labels.{label_name}.target invalid: {target!r}")
    require_nonempty(label.get("rationale"), f"labels.{label_name}.rationale")
    evidence_refs = label.get("evidence_refs")
    if not isinstance(evidence_refs, list) or not evidence_refs:
        raise ValueError(f"labels.{label_name}.evidence_refs must be a non-empty list")
    for i, ref in enumerate(evidence_refs):
        require_nonempty(ref, f"labels.{label_name}.evidence_refs[{i}]")
    disagreement = label.get("disagreement_record")
    if not isinstance(disagreement, dict) or not isinstance(disagreement.get("disagreement_observed"), bool):
        raise ValueError(f"labels.{label_name}.disagreement_record must explicitly record disagreement_observed")
    require_nonempty(disagreement.get("notes"), f"labels.{label_name}.disagreement_record.notes")
    resolution = disagreement.get("resolution")
    if disagreement["disagreement_observed"]:
        if resolution in (None, ""):
            if target != "CANNOT_CHECK":
                raise ValueError(
                    f"labels.{label_name}: unresolved disagreement must yield CANNOT_CHECK, got {target!r}"
                )
        else:
            require_nonempty(resolution, f"labels.{label_name}.disagreement_record.resolution")
    elif resolution not in (None, ""):
        raise ValueError(f"labels.{label_name}.resolution must be null/empty when no disagreement was observed")
    return target


def validate_packet(packet: dict[str, Any], intake_index: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if packet.get("schema") != GOLD_SCHEMA:
        raise ValueError("gold packet schema mismatch")
    packet_id = require_nonempty(packet.get("packet_id"), "packet_id")
    intake_row = intake_index.get(packet_id)
    if intake_row is None:
        raise ValueError(f"packet_id {packet_id} is not a frozen intake packet")
    for field in EXACT_FIELDS:
        if packet.get(field) != intake_row[field]:
            raise ValueError(f"{field} does not exactly match the frozen intake packet {packet_id}")
    if packet["before_sha256"] == packet["after_sha256"]:
        raise ValueError("transition digests must differ")
    require_hex64(packet.get("candidate_visible_packet_sha256"), "candidate_visible_packet_sha256")

    labels = packet.get("labels")
    if not isinstance(labels, dict) or set(labels) != set(LABELS):
        raise ValueError(f"labels must carry exactly both gold labels: {sorted(LABELS)}")
    targets = {name: validate_label(name, labels[name]) for name in LABELS}

    receipt = packet.get("adjudicator_receipt")
    if not isinstance(receipt, dict):
        raise ValueError("adjudicator_receipt must be an object")
    require_nonempty(receipt.get("adjudicator_id"), "adjudicator_receipt.adjudicator_id")
    require_nonempty(receipt.get("adjudicated_at_utc"), "adjudicator_receipt.adjudicated_at_utc")
    require_hex64(receipt.get("receipt_sha256"), "adjudicator_receipt.receipt_sha256")
    for key in ("independence_attested", "adjudication_started_before_prediction_reveal"):
        if receipt.get(key) is not True:
            raise ValueError(f"adjudicator_receipt.{key} must be true")
    for key in ("orion_predictions_visible", "baseline_predictions_visible", "protected_outcomes_visible"):
        if receipt.get(key) is not False:
            raise ValueError(f"adjudicator_receipt.{key} must be false")
    for key in ("candidate_predictions_in_packet", "baseline_predictions_in_packet", "protected_outcomes_in_packet"):
        if packet.get(key) is not False:
            raise ValueError(f"{key} must be false")
    return {
        "packet_id": packet_id,
        "stratum": intake_row["stratum"],
        "split": intake_row["split"],
        "targets": targets,
    }


def validate_packets(packets: list[dict[str, Any]], manifest: dict[str, Any], intake_index: dict[str, dict[str, Any]]) -> dict[str, Any]:
    summaries = [validate_packet(packet, intake_index) for packet in packets]
    seen: set[str] = set()
    for row in summaries:
        if row["packet_id"] in seen:
            raise ValueError(f"duplicate gold packet_id: {row['packet_id']}")
        seen.add(row["packet_id"])
    unadjudicated = sorted(set(intake_index) - seen)
    return {
        "schema": "ORION.A6.ExternalAdjudicatorPacketValidationResult.v1",
        "gold_packet_n": len(summaries),
        "intake_packet_n": len(intake_index),
        "unadjudicated_intake_packet_ids": unadjudicated,
        "unadjudicated_packets_filled": False,
        "packets": summaries,
        "scientific_authority_delta": "NONE__CUSTODY_VALIDATION_ONLY",
    }


def hexdigest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def fixture_intake() -> dict[str, Any]:
    rows = []
    n = 0
    for split, per in (("primary", 20), ("replication", 2)):
        for s in intake_mod.STRATA:
            for _ in range(per):
                pid = f"{split}-{n}"
                rows.append({
                    "packet_id": pid,
                    "split": split,
                    "stratum": s,
                    "source_family_id": f"sf-{pid}",
                    "normalized_organization_lineage": f"org-{pid}",
                    "artifact_lineage_id": f"art-{pid}",
                    "before_version_id": f"b-{pid}",
                    "after_version_id": f"a-{pid}",
                    "before_sha256": hexdigest(f"before-{pid}"),
                    "after_sha256": hexdigest(f"after-{pid}"),
                    "license_or_rights_receipt_id": f"rights-{pid}",
                    "external_custody_receipt_id": f"custody-{pid}",
                    "adjudicator_assignment_receipt_id": f"adj-{pid}",
                    "candidate_visible_packet_sha256": hexdigest(f"visible-{pid}"),
                    "eligible_preterminal": True,
                    "candidate_blind_gold_process_frozen": True,
                })
                n += 1
    return {
        "schema": INTAKE_SCHEMA,
        "protected_outcomes_accessed": False,
        "replication_target_n": 6,
        "replication_n_frozen_before_predictions": True,
        "packets": rows,
    }


def synthetic_gold(intake_row: dict[str, Any]) -> dict[str, Any]:
    def label(target: str) -> dict[str, Any]:
        return {
            "target": target,
            "rationale": "Synthetic validator self-test only; not a scientific judgment.",
            "evidence_refs": ["synthetic:evidence:1"],
            "disagreement_record": {"disagreement_observed": False, "resolution": None, "notes": "Synthetic no-disagreement control."},
        }

    return {
        "schema": GOLD_SCHEMA,
        "packet_id": intake_row["packet_id"],
        "stratum": intake_row["stratum"],
        "split": intake_row["split"],
        "source_family_id": intake_row["source_family_id"],
        "normalized_organization_lineage": intake_row["normalized_organization_lineage"],
        "artifact_lineage_id": intake_row["artifact_lineage_id"],
        "before_version_id": intake_row["before_version_id"],
        "after_version_id": intake_row["after_version_id"],
        "before_sha256": intake_row["before_sha256"],
        "after_sha256": intake_row["after_sha256"],
        "license_or_rights_receipt_id": intake_row["license_or_rights_receipt_id"],
        "external_custody_receipt_id": intake_row["external_custody_receipt_id"],
        "adjudicator_assignment_receipt_id": intake_row["adjudicator_assignment_receipt_id"],
        "candidate_visible_packet_sha256": intake_row["candidate_visible_packet_sha256"],
        "labels": {
            "local_action_release_authority": label("CANNOT_CHECK"),
            "scientific_discharge_admission_authority": label("CANNOT_CHECK"),
        },
        "adjudicator_receipt": {
            "adjudicator_id": "synthetic-self-test-adjudicator",
            "adjudicated_at_utc": "2099-01-01T00:00:00Z",
            "receipt_sha256": "2" * 64,
            "independence_attested": True,
            "adjudication_started_before_prediction_reveal": True,
            "orion_predictions_visible": False,
            "baseline_predictions_visible": False,
            "protected_outcomes_visible": False,
        },
        "candidate_predictions_in_packet": False,
        "baseline_predictions_in_packet": False,
        "protected_outcomes_in_packet": False,
    }


def expect_reject(packet: dict[str, Any], intake_index: dict[str, dict[str, Any]]) -> None:
    try:
        validate_packet(packet, intake_index)
    except ValueError:
        return
    raise AssertionError("hostile adjudicator packet was accepted")


def self_test() -> dict[str, Any]:
    manifest = fixture_intake()
    intake_mod.validate(manifest)
    intake_index = {row["packet_id"]: row for row in manifest["packets"]}
    first = manifest["packets"][0]
    good = synthetic_gold(first)
    validate_packet(good, intake_index)

    forged = copy.deepcopy(good)
    forged["before_sha256"] = "0" * 64
    expect_reject(forged, intake_index)
    bad_target = copy.deepcopy(good)
    bad_target["labels"]["local_action_release_authority"]["target"] = "MAYBE"
    expect_reject(bad_target, intake_index)
    one_label = copy.deepcopy(good)
    del one_label["labels"]["scientific_discharge_admission_authority"]
    expect_reject(one_label, intake_index)
    exposed = copy.deepcopy(good)
    exposed["adjudicator_receipt"]["orion_predictions_visible"] = True
    expect_reject(exposed, intake_index)
    unknown = copy.deepcopy(good)
    unknown["packet_id"] = "not-in-intake"
    expect_reject(unknown, intake_index)
    wrong_split = copy.deepcopy(good)
    wrong_split["split"] = "replication"
    expect_reject(wrong_split, intake_index)
    unresolved = copy.deepcopy(good)
    unresolved["labels"]["scientific_discharge_admission_authority"] = {
        "target": "ADMIT",
        "rationale": "Synthetic unresolved disagreement control.",
        "evidence_refs": ["synthetic:evidence:2"],
        "disagreement_record": {"disagreement_observed": True, "resolution": None, "notes": "Synthetic disagreement left unresolved."},
    }
    expect_reject(unresolved, intake_index)
    unresolved_ok = copy.deepcopy(unresolved)
    unresolved_ok["labels"]["scientific_discharge_admission_authority"]["target"] = "CANNOT_CHECK"
    validate_packet(unresolved_ok, intake_index)
    try:
        validate_packets([good, copy.deepcopy(good)], manifest, intake_index)
    except ValueError:
        duplicate_rejected = True
    else:
        raise AssertionError("duplicate gold packet ids accepted")
    result = validate_packets([good], manifest, intake_index)
    assert result["gold_packet_n"] == 1 and result["unadjudicated_intake_packet_ids"]
    return {
        "decision": "GREEN",
        "intake_packet_n": len(intake_index),
        "valid_packet_accepted": True,
        "forged_transition_digest_rejected": True,
        "invalid_target_rejected": True,
        "missing_second_label_rejected": True,
        "prediction_exposure_rejected": True,
        "unknown_packet_rejected": True,
        "split_mismatch_rejected": True,
        "unresolved_disagreement_non_cannot_check_rejected": True,
        "unresolved_disagreement_cannot_check_accepted": True,
        "duplicate_packet_rejected": duplicate_rejected,
        "unadjudicated_packets_left_unfilled": True,
        "gold_labels_created": False,
    }


def read_packets(paths: list[Path]) -> list[dict[str, Any]]:
    packets: list[dict[str, Any]] = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            packets.extend(payload)
        elif isinstance(payload, dict):
            packets.append(payload)
        else:
            raise ValueError(f"{path} must contain a JSON object or list")
    return packets


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--intake", type=Path)
    ap.add_argument("paths", nargs="*", type=Path)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    if args.self_test:
        result = self_test()
    else:
        if not args.paths:
            ap.error("provide adjudicator gold packet JSON path(s) or --self-test")
        if args.intake is None:
            ap.error("--intake intake manifest path is required when validating packets")
        manifest, intake_index = load_intake(args.intake)
        result = validate_packets(read_packets(args.paths), manifest, intake_index)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
