#!/usr/bin/env python3
"""Prove EXTERNAL_CURATOR_PACKET_TEMPLATE_V1.json is exactly packet-shaped.

Custody-preserving proof: the template is filled programmatically with
SYNTHETIC values (source bound to a real, public, frozen source-receipt row;
stratum/target/lineage/receipt all synthetic) and must validate GREEN through
the FROZEN validate_external_curator_packet_v1.validate_packet. Hostile
mutations of a filled packet must all be rejected. The raw template with nulls
must itself be rejected (a template is not a packet). Nothing here authors a
stratum or gold target: every synthetic value is marked synthetic and the
filled packet is never written anywhere.

No network, no randomness, no run-time free parameters. Fix the payload, never
the frozen validator.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent

TEMPLATE_PATH = HERE / "EXTERNAL_CURATOR_PACKET_TEMPLATE_V1.json"
FIXED_FALSE_FLAGS = (
    "curator_receipt.orion_predictions_visible",
    "curator_receipt.baseline_predictions_visible",
    "curator_receipt.protected_outcomes_visible",
    "candidate_predictions_in_packet",
    "baseline_predictions_in_packet",
    "protected_outcomes_in_packet",
)
GUIDED_LEAF_FIELDS = (
    "source_frame_sha256",
    "cluster_id",
    "source.workflow_id",
    "source.version_before",
    "source.version_after",
    "source.license_before",
    "source.license_after",
    "source.before_normalized_sha256",
    "source.after_normalized_sha256",
    "lineage.source_family_id",
    "lineage.normalized_organization_lineage",
    "lineage.artifact_lineage_id",
    "candidate_visible_packet_sha256",
    "adjudication.stratum",
    "adjudication.target",
    "adjudication.rationale",
    "adjudication.evidence_refs",
    "adjudication.disagreement_record.disagreement_observed",
    "adjudication.disagreement_record.resolution",
    "adjudication.disagreement_record.notes",
    "curator_receipt.curator_id",
    "curator_receipt.adjudicated_at_utc",
    "curator_receipt.receipt_sha256",
    "curator_receipt.independence_attested",
    "curator_receipt.adjudication_started_before_prediction_reveal",
)


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def leaf(doc: dict[str, Any], dotted: str) -> Any:
    node: Any = doc
    for part in dotted.split("."):
        node = node[part]
    return node


def set_leaf(doc: dict[str, Any], dotted: str, value: Any) -> None:
    parts = dotted.split(".")
    node: Any = doc
    for part in parts[:-1]:
        node = node[part]
    node[parts[-1]] = value


def check_template_structure(doc: dict[str, Any]) -> None:
    if doc.get("schema") != "ORION.A3.ExternalCuratorAdjudicationPacketTemplate.v1":
        raise AssertionError("template schema mismatch")
    if doc.get("packet_schema_to_emit") != "ORION.A3.ExternalCuratorAdjudicationPacket.v1":
        raise AssertionError("template packet schema mismatch")
    for flag in ("external_packet_committed_by_this_template", "stratum_judgments_created_by_this_template",
                 "gold_targets_created_by_this_template", "candidate_predictions_accessed",
                 "baseline_predictions_accessed", "protected_outcomes_accessed", "grants_scientific_authority"):
        if doc.get(flag) is not False:
            raise AssertionError(f"template custody flag must be false: {flag}")
    template = doc["template"]
    if template.get("schema") != "ORION.A3.ExternalCuratorAdjudicationPacket.v1":
        raise AssertionError("template.template schema mismatch")
    for dotted in FIXED_FALSE_FLAGS:
        if leaf(template, dotted) is not False:
            raise AssertionError(f"fixed false flag is not false in template: {dotted}")
    guidance = doc["field_guidance"]
    for dotted in GUIDED_LEAF_FIELDS:
        if not str(guidance.get(dotted, "")).strip():
            raise AssertionError(f"missing field guidance for {dotted}")
    for dotted in GUIDED_LEAF_FIELDS:
        if dotted in FIXED_FALSE_FLAGS:
            continue
        value = leaf(template, dotted)
        if dotted == "adjudication.evidence_refs":
            if value != []:
                raise AssertionError("evidence_refs placeholder must be an empty list")
            continue
        if dotted in ("curator_receipt.independence_attested",
                      "curator_receipt.adjudication_started_before_prediction_reveal",
                      "adjudication.disagreement_record.disagreement_observed"):
            if value is not None:
                raise AssertionError(f"boolean placeholder must be null: {dotted}")
            continue
        if value is not None:
            raise AssertionError(f"fill-in placeholder must be null: {dotted}")


def fill_template_synthetic(doc: dict[str, Any], source_row: dict[str, Any]) -> dict[str, Any]:
    packet = copy.deepcopy(doc["template"])
    packet["source_frame_sha256"] = doc["source_frame_sha256_required"]
    packet["cluster_id"] = "synthetic-template-proof-cluster"
    packet["source"] = {
        "workflow_id": str(source_row["workflow_id"]),
        "version_before": source_row["version_before"],
        "version_after": source_row["version_after"],
        "license_before": source_row["license_before"],
        "license_after": source_row["license_after"],
        "before_normalized_sha256": source_row["before_normalized_sha256"],
        "after_normalized_sha256": source_row["after_normalized_sha256"],
    }
    packet["lineage"] = {
        "source_family_id": f"workflowhub:{source_row['workflow_id']}",
        "normalized_organization_lineage": "synthetic-template-proof-org-lineage",
        "artifact_lineage_id": "synthetic-template-proof-artifact-lineage",
    }
    packet["candidate_visible_packet_sha256"] = hashlib.sha256(
        b"SYNTHETIC-TEMPLATE-PROOF-ONLY\x00" + str(source_row["workflow_id"]).encode("utf-8")
    ).hexdigest()
    packet["adjudication"] = {
        "stratum": "representation_schema",
        "target": "CANNOT_CHECK",
        "rationale": "SYNTHETIC TEMPLATE PROOF ONLY - not a scientific judgment.",
        "evidence_refs": ["synthetic-template-proof:evidence:1"],
        "disagreement_record": {
            "disagreement_observed": False,
            "resolution": None,
            "notes": "SYNTHETIC TEMPLATE PROOF ONLY - no adjudication occurred.",
        },
    }
    packet["curator_receipt"] = {
        "curator_id": "synthetic-template-proof-curator",
        "adjudicated_at_utc": "2099-01-01T00:00:00Z",
        "receipt_sha256": hashlib.sha256(b"SYNTHETIC-TEMPLATE-PROOF-RECEIPT").hexdigest(),
        "independence_attested": True,
        "adjudication_started_before_prediction_reveal": True,
        "orion_predictions_visible": False,
        "baseline_predictions_visible": False,
        "protected_outcomes_visible": False,
    }
    packet["candidate_predictions_in_packet"] = False
    packet["baseline_predictions_in_packet"] = False
    packet["protected_outcomes_in_packet"] = False
    return packet


def expect_reject(validator: Any, packet: dict[str, Any], source_frame: dict[str, Any], label: str) -> None:
    try:
        validator.validate_packet(packet, source_frame)
    except (ValueError, AssertionError):
        return
    raise AssertionError(f"hostile filled packet was accepted: {label}")


def self_test() -> dict[str, Any]:
    validator = _load("a3_packet_validator_v1", HERE / "validate_external_curator_packet_v1.py")
    doc = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    check_template_structure(doc)

    source_frame = validator.load_source_frame()
    first_id = sorted(source_frame, key=lambda x: (int(x) if x.isdigit() else 10**18, x))[0]
    row = source_frame[first_id]

    # Raw template with nulls must be rejected by the frozen validator.
    try:
        validator.validate_packet(copy.deepcopy(doc["template"]), source_frame)
    except (ValueError, AssertionError):
        raw_template_rejected = True
    else:
        raise AssertionError("raw template with null placeholders was accepted as a packet")
    # Filled synthetic packet must validate GREEN through the frozen validator.
    filled = fill_template_synthetic(doc, row)
    summary = validator.validate_packet(filled, source_frame)
    if summary["workflow_id"] != first_id or summary["stratum"] != "representation_schema":
        raise AssertionError("filled-packet validation summary mismatch")

    # Hostile mutations must all be rejected by the frozen validator.
    hostile: list[tuple[str, dict[str, Any]]] = []
    m = copy.deepcopy(filled); m["source_frame_sha256"] = "0" * 64
    hostile.append(("wrong source_frame_sha256", m))
    m = copy.deepcopy(filled); m["source"]["version_after"] = int(m["source"]["version_after"]) + 1
    hostile.append(("source version mismatch", m))
    m = copy.deepcopy(filled); m["source"]["after_normalized_sha256"] = m["source"]["before_normalized_sha256"]
    hostile.append(("normalized hashes do not differ", m))
    m = copy.deepcopy(filled); m["source"]["workflow_id"] = "999999999"
    hostile.append(("workflow outside frozen frame", m))
    m = copy.deepcopy(filled); m["adjudication"]["stratum"] = "performance_benchmark"
    hostile.append(("invalid stratum", m))
    m = copy.deepcopy(filled); m["adjudication"]["target"] = "REVOKE"
    hostile.append(("invalid target vocabulary", m))
    m = copy.deepcopy(filled); m["adjudication"]["rationale"] = ""
    hostile.append(("empty rationale", m))
    m = copy.deepcopy(filled); m["adjudication"]["evidence_refs"] = []
    hostile.append(("empty evidence_refs", m))
    m = copy.deepcopy(filled); m["adjudication"]["disagreement_record"]["disagreement_observed"] = True
    hostile.append(("disagreement without resolution", m))
    m = copy.deepcopy(filled); m["adjudication"]["disagreement_record"]["resolution"] = "resolved anyway"
    hostile.append(("resolution present without disagreement", m))
    m = copy.deepcopy(filled); m["candidate_predictions_in_packet"] = True
    hostile.append(("candidate predictions flag true", m))
    m = copy.deepcopy(filled); m["curator_receipt"]["orion_predictions_visible"] = True
    hostile.append(("orion predictions visible", m))
    m = copy.deepcopy(filled); m["curator_receipt"]["independence_attested"] = False
    hostile.append(("independence not attested", m))
    m = copy.deepcopy(filled); m["curator_receipt"]["receipt_sha256"] = "not-hex"
    hostile.append(("malformed receipt hash", m))
    for label, packet in hostile:
        expect_reject(validator, packet, source_frame, label)

    return {
        "decision": "GREEN",
        "template_sha256": hashlib.sha256(TEMPLATE_PATH.read_bytes()).hexdigest(),
        "guided_fields": len(GUIDED_LEAF_FIELDS),
        "fixed_false_flags": len(FIXED_FALSE_FLAGS),
        "filled_synthetic_packet_validates": True,
        "raw_template_rejected": raw_template_rejected,
        "hostile_mutations_rejected": len(hostile),
        "synthetic_values_marked": True,
        "stratum_judgments_created": False,
        "gold_targets_created": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run the custody-preserving template proof")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("this prover is self-test only; nothing to run by default")
    print(json.dumps(self_test(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
