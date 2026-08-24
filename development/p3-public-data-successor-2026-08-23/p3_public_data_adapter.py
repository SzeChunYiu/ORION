#!/usr/bin/env python3
"""Rights-gated acquisition, outcome-blind inventory, sampling and baselines.

This adapter deliberately separates input cases, system predictions and public
gold. Public labels remain development/transport evidence and are never marked
protected. The standard library is sufficient.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tarfile
import unicodedata
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urldefrag, urljoin
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parent
RIGHTS_PATH = ROOT / "SOURCE_RIGHTS_REGISTRY_V1.json"
PROTOCOL_PATH = ROOT / "P3_PUBLIC_DATA_SUCCESSOR_PROTOCOL_V1_1.json"
PROTOCOL_ID = "P3.PUBLIC.TRANSPORT.CRAFT_SCIREX_OAEI.V1.1"
RELATIONS = {"GLUE", "OBSTRUCTION", "PLURAL", "UNRESOLVED"}
COORDINATES = {"REFERENT", "CONSTRUCT", "MEASUREMENT", "TEMPORAL_CONTEXT"}
INVENTORY_FIELDS = {
    "source_id",
    "donor_family",
    "unit_id",
    "cluster_id",
    "provider_split",
    "container",
    "line_no_internal_not_selection",
    "selection_fields_only",
    "gold_accessed",
    "public_inline_label_bytes_parsed_but_not_retained_or_used",
    "protected_outcome_accessed",
    "reference_alignment_accessed",
    "independent_unit_warning",
}
CASE_FIELDS = {
    "case_id",
    "cluster_id",
    "source_id",
    "panel_id",
    "left",
    "right",
    "required_coordinates",
    "input_digest",
    "provenance",
}
PROJECTION_FIELDS = {"label", "entity_type", "coordinates", "observedness"}
PROVENANCE_FIELDS = {
    "source_archive_sha256",
    "source_revision",
    "source_member",
    "left_member",
    "right_member",
    "left_locator",
    "right_locator",
    "builder_id",
    "builder_revision",
}
PREDICTION_FIELDS = {
    "schema_version",
    "case_id",
    "system_id",
    "relation",
    "admissible_relations",
    "input_digest",
    "details",
    "gold_accessed",
}
GOLD_FIELDS = {
    "case_id",
    "cluster_id",
    "source_id",
    "panel_id",
    "input_digest",
    "true_relation",
    "identified_relations",
    "gold_authority",
    "protected_evidence",
    "coordinate_opportunities",
    "provenance",
}
FORBIDDEN_OUTCOME_KEYS = {
    "gold",
    "gold_relation",
    "gold_annotation_count",
    "annotation_count",
    "true_relation",
    "identified_relations",
    "candidate_output",
    "system_output",
    "error_type",
    "effect_size",
    "evaluator_gold",
}


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON") from exc


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")


def normalized_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value).casefold()).strip("_")


def find_forbidden_outcome_fields(value: Any, path: str = "$") -> list[str]:
    """Return forbidden outcome-bearing field paths at any nesting depth."""
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if normalized_key(key) in FORBIDDEN_OUTCOME_KEYS:
                found.append(child_path)
            found.extend(find_forbidden_outcome_fields(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(find_forbidden_outcome_fields(child, f"{path}[{index}]"))
    return found


def require_closed_fields(row: dict[str, Any], allowed: set[str], context: str) -> None:
    unknown = sorted(set(row) - allowed)
    if unknown:
        raise ValueError(f"{context}: unknown fields rejected by closed contract: {unknown}")


def validate_inventory_row(row: dict[str, Any], context: str) -> None:
    require_closed_fields(row, INVENTORY_FIELDS, context)
    forbidden = find_forbidden_outcome_fields(row)
    if forbidden:
        raise ValueError(f"{context}: forbidden outcome fields: {forbidden}")
    required = {"source_id", "donor_family", "unit_id", "cluster_id", "provider_split"}
    missing = sorted(required - set(row))
    if missing:
        raise ValueError(f"{context}: missing inventory fields: {missing}")
    for status_key in ("gold_accessed", "protected_outcome_accessed", "reference_alignment_accessed"):
        if row.get(status_key) is True:
            raise ValueError(f"{context}: {status_key}=true invalidates outcome-blind sampling")
    if row.get("selection_fields_only") is not True:
        raise ValueError(f"{context}: selection_fields_only must be true")


def validate_projection(projection: Any, context: str) -> None:
    if not isinstance(projection, dict):
        raise ValueError(f"{context}: projection must be an object")
    require_closed_fields(projection, PROJECTION_FIELDS, context)
    missing = sorted(PROJECTION_FIELDS - set(projection))
    if missing:
        raise ValueError(f"{context}: missing projection fields: {missing}")
    if projection["label"] is not None and not isinstance(projection["label"], str):
        raise ValueError(f"{context}: label must be string or null")
    if projection["entity_type"] is not None and not isinstance(projection["entity_type"], str):
        raise ValueError(f"{context}: entity_type must be string or null")
    if not isinstance(projection["coordinates"], dict) or not isinstance(projection["observedness"], dict):
        raise ValueError(f"{context}: coordinates and observedness must be objects")
    unknown_coordinates = sorted(set(projection["coordinates"]) - COORDINATES)
    unknown_observedness = sorted(set(projection["observedness"]) - COORDINATES)
    if unknown_coordinates or unknown_observedness:
        raise ValueError(
            f"{context}: unknown coordinate keys: coordinates={unknown_coordinates}, "
            f"observedness={unknown_observedness}"
        )
    invalid_statuses = {
        key: value
        for key, value in projection["observedness"].items()
        if value not in {"OBSERVED", "NOT_OBSERVED", "UNRESOLVED"}
    }
    if invalid_statuses:
        raise ValueError(f"{context}: invalid observedness values: {invalid_statuses}")


def validate_case(case: dict[str, Any], context: str, require_digest: bool) -> None:
    require_closed_fields(case, CASE_FIELDS, context)
    forbidden = find_forbidden_outcome_fields(case)
    if forbidden:
        raise ValueError(f"{context}: forbidden outcome fields: {forbidden}")
    required = {"case_id", "cluster_id", "source_id", "panel_id", "left", "right", "required_coordinates", "provenance"}
    if require_digest:
        required.add("input_digest")
    missing = sorted(required - set(case))
    if missing:
        raise ValueError(f"{context}: missing case fields: {missing}")
    for key in ("case_id", "cluster_id", "source_id", "panel_id"):
        if not isinstance(case[key], str) or not case[key]:
            raise ValueError(f"{context}: {key} must be a nonempty string")
    validate_projection(case["left"], f"{context}.left")
    validate_projection(case["right"], f"{context}.right")
    required_coordinates = case["required_coordinates"]
    if not isinstance(required_coordinates, list) or len(required_coordinates) != len(set(required_coordinates)):
        raise ValueError(f"{context}: required_coordinates must be a unique array")
    if not set(required_coordinates) <= COORDINATES:
        raise ValueError(f"{context}: invalid required_coordinates: {required_coordinates}")
    provenance = case["provenance"]
    if not isinstance(provenance, dict):
        raise ValueError(f"{context}: provenance must be an object")
    require_closed_fields(provenance, PROVENANCE_FIELDS, f"{context}.provenance")
    invalid_provenance = {key: value for key, value in provenance.items() if not isinstance(value, str) or not value}
    if invalid_provenance:
        raise ValueError(f"{context}: provenance values must be nonempty strings: {invalid_provenance}")
    if require_digest:
        declared = case["input_digest"]
        if not isinstance(declared, str) or not re.fullmatch(r"[0-9a-f]{64}", declared):
            raise ValueError(f"{context}: invalid input_digest")


def validate_prediction(prediction: dict[str, Any], context: str) -> None:
    require_closed_fields(prediction, PREDICTION_FIELDS, context)
    required = {"schema_version", "case_id", "system_id", "relation", "admissible_relations", "input_digest"}
    missing = sorted(required - set(prediction))
    if missing:
        raise ValueError(f"{context}: missing prediction fields: {missing}")
    if prediction["schema_version"] != "orion.p3.public-prediction.v1.1":
        raise ValueError(f"{context}: unsupported schema_version {prediction['schema_version']!r}")
    for key in ("case_id", "system_id"):
        if not isinstance(prediction[key], str) or not prediction[key]:
            raise ValueError(f"{context}: {key} must be a nonempty string")
    if prediction["relation"] not in RELATIONS:
        raise ValueError(f"{context}: invalid relation {prediction['relation']!r}")
    admissible = prediction["admissible_relations"]
    if (
        not isinstance(admissible, list)
        or not admissible
        or len(admissible) != len(set(admissible))
        or not set(admissible) <= RELATIONS
    ):
        raise ValueError(f"{context}: invalid admissible_relations")
    if not isinstance(prediction["input_digest"], str) or not re.fullmatch(r"[0-9a-f]{64}", prediction["input_digest"]):
        raise ValueError(f"{context}: invalid input_digest")
    if prediction.get("gold_accessed") is not False:
        raise ValueError(f"{context}: gold_accessed must be false")


class GateFailure(ValueError):
    """Raised when a noncompensatory scientific gate is not satisfied."""


def stream_digest(path: Path, algorithm: str) -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, target: Path, expected_size: int | None, checksum: str | None) -> dict[str, Any]:
    target.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "ORION-P3-public-adapter/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response, target.open("wb") as handle:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
    observed_size = target.stat().st_size
    if expected_size is not None and observed_size != expected_size:
        raise ValueError(f"size mismatch for {target}: {observed_size} != {expected_size}")
    observed_checksum = None
    if checksum:
        algorithm, expected = checksum.split(":", 1)
        observed_checksum = f"{algorithm}:{stream_digest(target, algorithm)}"
        if observed_checksum != checksum:
            raise ValueError(f"checksum mismatch for {target}: {observed_checksum} != {checksum}")
    return {"path": str(target), "size": observed_size, "checksum": observed_checksum}


def source_map() -> dict[str, dict[str, Any]]:
    return {entry["source_id"]: entry for entry in read_json(RIGHTS_PATH)["sources"]}


def load_rights_decisions(paths: list[str] | None) -> dict[str, dict[str, Any]]:
    decisions: dict[str, dict[str, Any]] = {}
    required = {
        "schema_version",
        "decision_id",
        "source_id",
        "decided_by",
        "decided_at_utc",
        "permitted_operations",
        "content_classes",
        "license_evidence",
        "required_conditions_acknowledged",
        "redistribution_plan",
        "terminal",
        "non_legal_advice_acknowledged",
    }
    for raw_path in paths or []:
        path = Path(raw_path)
        decision = read_json(path)
        if not isinstance(decision, dict):
            raise ValueError(f"rights decision {path} must be an object")
        require_closed_fields(decision, required, f"rights decision {path}")
        missing = sorted(required - set(decision))
        if missing:
            raise ValueError(f"rights decision {path} missing fields: {missing}")
        if decision["schema_version"] != "orion.p3.public-rights-decision.v1.1":
            raise ValueError(f"rights decision {path} has unsupported schema_version")
        if decision["source_id"] in decisions:
            raise ValueError(f"duplicate rights decision for {decision['source_id']}")
        if decision["terminal"] not in {"AUTHORIZED_FOR_DECLARED_RESEARCH_OPERATIONS", "DENIED", "CANNOT_CHECK"}:
            raise ValueError(f"rights decision {path} has invalid terminal")
        if decision["non_legal_advice_acknowledged"] is not True:
            raise ValueError(f"rights decision {path} must acknowledge the non-legal-advice boundary")
        for field in ("permitted_operations", "content_classes", "license_evidence", "required_conditions_acknowledged"):
            if not isinstance(decision[field], list) or not all(isinstance(item, str) and item for item in decision[field]):
                raise ValueError(f"rights decision {path} field {field} must be a string array")
        decision = dict(decision)
        decision["receipt_path"] = str(path)
        decision["receipt_sha256"] = stream_digest(path, "sha256")
        decisions[decision["source_id"]] = decision
    return decisions


def cmd_fetch(args: argparse.Namespace) -> None:
    sources = source_map()
    rights_decisions = load_rights_decisions(args.rights_decision)
    selected = args.source or list(sources)
    receipts: list[dict[str, Any]] = []
    for source_id in selected:
        if source_id not in sources:
            raise ValueError(f"unknown source: {source_id}")
        source = sources[source_id]
        family = source["donor_family"]
        decision = rights_decisions.get(source_id)
        if family in {"CRAFT", "SCIREX"} and (
            decision is None or decision["terminal"] != "AUTHORIZED_FOR_DECLARED_RESEARCH_OPERATIONS"
        ):
            receipts.append({
                "source_id": source_id,
                "status": "SKIPPED_DATA_BODY__HUMAN_RIGHTS_DECISION_ABSENT_OR_NOT_AUTHORIZED",
            })
            continue
        if family == "CRAFT":
            missing_conditions = sorted(set(source.get("required_conditions", [])) - set(decision["required_conditions_acknowledged"]))
            if missing_conditions:
                raise ValueError(f"CRAFT rights decision does not acknowledge required conditions: {missing_conditions}")
        if family == "SCIREX" and "UNDERLYING_ARTICLE_TEXT" not in decision["content_classes"]:
            raise ValueError("SciREX rights decision must explicitly name UNDERLYING_ARTICLE_TEXT")
        if family in {"CRAFT", "SCIREX"}:
            missing_operations = sorted({"DOWNLOAD", "PARSE_FOR_RESEARCH"} - set(decision["permitted_operations"]))
            if missing_operations:
                raise ValueError(f"{family} rights decision omits required operations: {missing_operations}")
        files = source.get("files", [])
        if family == "SCIREX":
            release = source["release"]
            files = [{
                "key": Path(release["path"]).name,
                "size": release["content_length_header"],
                "checksum": None,
                "download_url": release["url"],
                "role": "PUBLIC_INLINE_INPUT_AND_GOLD__RIGHTS_GATED",
            }]
        for record in files:
            if record.get("role", "").endswith("EVALUATOR_ONLY") and not args.include_public_gold:
                receipts.append({"source_id": source_id, "key": record["key"], "status": "SKIPPED_PUBLIC_GOLD"})
                continue
            target = Path(args.data_dir) / family.lower() / record["key"]
            result = download(record["download_url"], target, record.get("size"), record.get("checksum"))
            role = record.get("role", "")
            contains_public_gold_bytes = any(marker in role for marker in ("ANNOTATION", "GOLD", "REFERENCE_ALIGNMENTS"))
            result.update({
                "source_id": source_id,
                "key": record["key"],
                "role": role,
                "contains_public_gold_bytes": contains_public_gold_bytes,
                "public_gold_content_interpreted": False,
                "rights_decision_id": decision["decision_id"] if decision else None,
                "rights_decision_sha256": decision["receipt_sha256"] if decision else None,
                "status": "DOWNLOADED_AND_VERIFIED" if record.get("checksum") else "DOWNLOADED_SIZE_CHECKED__NO_EXPECTED_CHECKSUM",
            })
            receipts.append(result)
    write_json(Path(args.receipt), {
        "schema_version": "orion.p3.public-acquisition-receipt.v1.1",
        "authority": "ACQUISITION_ONLY__NO_EMPIRICAL_RESULT",
        "explicit_evaluator_only_gold_requested": bool(args.include_public_gold),
        "downloaded_containers_with_public_gold_bytes": sum(bool(row.get("contains_public_gold_bytes")) for row in receipts),
        "public_gold_content_interpreted": False,
        "rights_decision_receipts": [
            {
                "source_id": source_id,
                "decision_id": decision["decision_id"],
                "terminal": decision["terminal"],
                "receipt_sha256": decision["receipt_sha256"],
            }
            for source_id, decision in sorted(rights_decisions.items())
        ],
        "receipts": receipts,
    })


def craft_inventory(data_dir: Path) -> list[dict[str, Any]]:
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    base = data_dir / "craft"
    for archive in sorted(base.glob("*.tar.gz")):
        if archive.name == "evaluation-data.tar.gz":
            continue
        role = "PUBLIC_EVALUATION_INPUT" if "test_data" in archive.name else "PUBLIC_DEVELOPMENT_INPUT"
        with tarfile.open(archive, "r:gz") as handle:
            member_names = [member.name for member in handle.getmembers() if member.isfile()]
        for name in member_names:
            match = re.search(r"(PMC\d+)", name, flags=re.IGNORECASE)
            if not match:
                continue
            unit_id = match.group(1).upper()
            key = (archive.name, unit_id)
            rows[key] = {
                "source_id": "CRAFT_SHARED_TASK_2019_ZENODO_3460908",
                "donor_family": "CRAFT",
                "unit_id": unit_id,
                "cluster_id": f"CRAFT::{unit_id}",
                "provider_split": "evaluation" if role == "PUBLIC_EVALUATION_INPUT" else "development",
                "container": archive.name,
                "selection_fields_only": True,
                "gold_accessed": False,
            }
    return sorted(rows.values(), key=lambda row: (row["provider_split"], row["unit_id"]))


def scirex_inventory(data_dir: Path) -> list[dict[str, Any]]:
    archive = data_dir / "scirex" / "release_data.tar.gz"
    if not archive.exists():
        return []
    rows: list[dict[str, Any]] = []
    with tarfile.open(archive, "r:gz") as handle:
        for member in handle.getmembers():
            base = Path(member.name).name
            if base not in {"train.jsonl", "dev.jsonl", "test.jsonl"} or not member.isfile():
                continue
            stream = handle.extractfile(member)
            if stream is None:
                continue
            split = base.removesuffix(".jsonl")
            for line_no, raw in enumerate(stream, 1):
                # The public release stores labels inline. The sampler retains
                # only doc_id and official split; no label value or count is
                # emitted or used for selection.
                row = json.loads(raw)
                unit_id = str(row["doc_id"])
                rows.append({
                    "source_id": "SCIREX_GITHUB_7DAAD660",
                    "donor_family": "SCIREX",
                    "unit_id": unit_id,
                    "cluster_id": f"SCIREX::{unit_id}",
                    "provider_split": split,
                    "container": archive.name,
                    "line_no_internal_not_selection": line_no,
                    "selection_fields_only": True,
                    "public_inline_label_bytes_parsed_but_not_retained_or_used": True,
                    "protected_outcome_accessed": False,
                })
    return sorted(rows, key=lambda row: (row["provider_split"], row["unit_id"]))


def oaei_inventory(data_dir: Path) -> list[dict[str, Any]]:
    archive = data_dir / "oaei" / "oacontest17.zip"
    if not archive.exists():
        return []
    with zipfile.ZipFile(archive) as handle:
        names = set(handle.namelist())
    directories: set[str] = set()
    for name in names:
        path = Path(name)
        if path.name.lower() == "onto.rdf":
            directories.add(path.parent.as_posix())
    return [{
        "source_id": "OAEI_2004_ZENODO_15827226",
        "donor_family": "OAEI",
        "unit_id": directory,
        "cluster_id": "OAEI2004::BIBLIOGRAPHIC_SEED_FAMILY",
        "provider_split": "descriptive_stress",
        "container": archive.name,
        "selection_fields_only": True,
        "reference_alignment_accessed": False,
        "independent_unit_warning": "ALL_NUMBERED_TESTS_SHARE_ONE_SEED_FAMILY",
    } for directory in sorted(directories)]


def cmd_inventory(args: argparse.Namespace) -> None:
    data_dir = Path(args.data_dir)
    rows = craft_inventory(data_dir) + oaei_inventory(data_dir)
    if args.ack_scirex_content_rights:
        rows += scirex_inventory(data_dir)
    elif (data_dir / "scirex" / "release_data.tar.gz").exists():
        raise SystemExit("SciREX body exists but inventory requires --ack-scirex-content-rights.")
    write_jsonl(Path(args.out), sorted(rows, key=lambda row: (row["donor_family"], row["unit_id"])))


def selection_digest(source_id: str, unit_id: str) -> str:
    payload = f"{PROTOCOL_ID}\0{source_id}\0{unit_id}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def cmd_sample(args: argparse.Namespace) -> None:
    rows = list(read_jsonl(Path(args.inventory)))
    selected: list[dict[str, Any]] = []
    seen_units: set[tuple[str, str]] = set()
    for row_index, row in enumerate(rows, 1):
        validate_inventory_row(row, f"inventory[{row_index}]")
        unit_key = (row["source_id"], row["unit_id"])
        if unit_key in seen_units:
            raise ValueError(f"inventory[{row_index}]: duplicate source/unit identity {unit_key}")
        seen_units.add(unit_key)
        digest = selection_digest(row["source_id"], row["unit_id"])
        family = row["donor_family"]
        provider_split = row["provider_split"]
        if family == "CRAFT":
            role = "PUBLIC_AUDIT" if provider_split == "evaluation" else "PUBLIC_DEVELOPMENT"
        elif family == "SCIREX":
            role = "PUBLIC_AUDIT" if provider_split == "test" else "PUBLIC_DEVELOPMENT"
        else:
            role = "DESCRIPTIVE_STRESS_ONLY"
        selected.append({
            "source_id": row["source_id"],
            "donor_family": family,
            "unit_id": row["unit_id"],
            "cluster_id": row["cluster_id"],
            "provider_split": provider_split,
            "container": row.get("container"),
            "selection_digest": digest,
            "analysis_role": role,
            "selected_without_outcomes": True,
        })
    write_json(Path(args.out), {
        "schema_version": "orion.p3.public-outcome-blind-sample.v1",
        "protocol_id": PROTOCOL_ID,
        "selection_algorithm": "SHA256(PROTOCOL_ID || NUL || SOURCE_ID || NUL || UNIT_ID); census with provider split preserved",
        "gold_fields_used": [],
        "system_outputs_used": [],
        "public_not_protected": True,
        "units": sorted(selected, key=lambda row: (row["analysis_role"], row["selection_digest"])),
    })


def xml_local_name(value: str) -> str:
    return value.rsplit("}", 1)[-1].rsplit(":", 1)[-1]


def uri_local_name(value: str) -> str:
    base, fragment = urldefrag(value)
    tail = fragment or base.rstrip("/").rsplit("/", 1)[-1]
    return tail or value


def oaei_entities(raw: bytes, member_name: str) -> list[dict[str, str]]:
    """Parse source ontology entities only; never receives reference alignment bytes."""
    root = ElementTree.fromstring(raw)
    xml_base = root.attrib.get("{http://www.w3.org/XML/1998/namespace}base", "")
    rdf_about = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"
    rdf_id = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}ID"
    allowed_types = {"Class", "ObjectProperty", "DatatypeProperty", "AnnotationProperty", "NamedIndividual"}
    entities: dict[tuple[str, str], dict[str, str]] = {}
    for element in root.iter():
        entity_type = xml_local_name(element.tag)
        if entity_type not in allowed_types:
            continue
        uri = element.attrib.get(rdf_about)
        if not uri and element.attrib.get(rdf_id):
            uri = urljoin(xml_base, f"#{element.attrib[rdf_id]}")
        elif uri:
            uri = urljoin(xml_base, uri)
        if not uri:
            continue
        labels = [
            (child.text or "").strip()
            for child in element
            if xml_local_name(child.tag) == "label" and (child.text or "").strip()
        ]
        label = labels[0] if labels else uri_local_name(uri)
        entities[(entity_type, uri)] = {
            "entity_type": entity_type,
            "uri": uri,
            "label": label,
            "locator": f"{member_name}::{uri}",
        }
    return sorted(entities.values(), key=lambda row: (row["entity_type"], row["uri"]))


def oaei_onto_members(archive: zipfile.ZipFile) -> dict[str, str]:
    members: dict[str, str] = {}
    for name in archive.namelist():
        path = Path(name)
        if path.name.lower() != "onto.rdf":
            continue
        test_id = path.parent.name
        if test_id in members:
            raise ValueError(f"duplicate onto.rdf member for OAEI test {test_id}")
        members[test_id] = name
    return members


def cmd_build_oaei_cases(args: argparse.Namespace) -> None:
    """Build an exhaustive, outcome-blind, type-compatible OAEI case universe."""
    archive_path = Path(args.data_dir) / "oaei" / "oacontest17.zip"
    if not archive_path.exists():
        raise FileNotFoundError(archive_path)
    expected = source_map()["OAEI_2004_ZENODO_15827226"]["files"][0]["checksum"]
    algorithm, expected_digest = expected.split(":", 1)
    observed_digest = stream_digest(archive_path, algorithm)
    if observed_digest != expected_digest:
        raise ValueError(f"OAEI archive checksum mismatch: {algorithm}:{observed_digest} != {expected}")
    archive_sha256 = stream_digest(archive_path, "sha256")
    cases: list[dict[str, Any]] = []
    member_receipts: list[dict[str, Any]] = []
    with zipfile.ZipFile(archive_path) as archive:
        members = oaei_onto_members(archive)
        if args.source_test not in members:
            raise ValueError(f"source OAEI test {args.source_test} has no onto.rdf")
        source_member = members[args.source_test]
        source_raw = archive.read(source_member)
        source_entities = oaei_entities(source_raw, source_member)
        member_receipts.append({
            "test_id": args.source_test,
            "member": source_member,
            "member_sha256": hashlib.sha256(source_raw).hexdigest(),
            "n_entities": len(source_entities),
        })
        target_ids = sorted(test_id for test_id in members if test_id != args.source_test)
        for target_id in target_ids:
            target_member = members[target_id]
            target_raw = archive.read(target_member)
            target_entities = oaei_entities(target_raw, target_member)
            member_receipts.append({
                "test_id": target_id,
                "member": target_member,
                "member_sha256": hashlib.sha256(target_raw).hexdigest(),
                "n_entities": len(target_entities),
            })
            targets_by_type: dict[str, list[dict[str, str]]] = defaultdict(list)
            for entity in target_entities:
                targets_by_type[entity["entity_type"]].append(entity)
            for left in source_entities:
                for right in targets_by_type[left["entity_type"]]:
                    identity = f"{PROTOCOL_ID}\0OAEI\0{args.source_test}\0{target_id}\0{left['uri']}\0{right['uri']}"
                    case_id = "P3.OAEI." + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:24]
                    case = {
                        "case_id": case_id,
                        "cluster_id": "OAEI2004::BIBLIOGRAPHIC_SEED_FAMILY",
                        "source_id": "OAEI_2004_ZENODO_15827226",
                        "panel_id": "OAEI_2004_FULL_STRESS_CENSUS",
                        "left": {
                            "label": left["label"],
                            "entity_type": left["entity_type"],
                            "coordinates": {"REFERENT": left["uri"], "CONSTRUCT": left["entity_type"]},
                            "observedness": {"REFERENT": "OBSERVED", "CONSTRUCT": "OBSERVED"},
                        },
                        "right": {
                            "label": right["label"],
                            "entity_type": right["entity_type"],
                            "coordinates": {"REFERENT": right["uri"], "CONSTRUCT": right["entity_type"]},
                            "observedness": {"REFERENT": "OBSERVED", "CONSTRUCT": "OBSERVED"},
                        },
                        "required_coordinates": ["REFERENT", "CONSTRUCT"],
                        "provenance": {
                            "source_archive_sha256": archive_sha256,
                            "source_revision": "ZENODO_15827226__MD5_VERIFIED",
                            "left_member": source_member,
                            "right_member": target_member,
                            "left_locator": left["locator"],
                            "right_locator": right["locator"],
                            "builder_id": "OAEI_TYPE_COMPATIBLE_EXHAUSTIVE_V1",
                            "builder_revision": "1.0.0",
                        },
                    }
                    validate_case(case, f"built_case[{case_id}]", require_digest=False)
                    case["input_digest"] = canonical_case_digest(case)
                    cases.append(case)
    case_ids = [case["case_id"] for case in cases]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("OAEI case builder produced duplicate case IDs")
    output_path = Path(args.out)
    write_jsonl(output_path, sorted(cases, key=lambda row: row["case_id"]))
    write_json(Path(args.receipt), {
        "schema_version": "orion.p3.oaei-input-case-build-receipt.v1",
        "protocol_id": PROTOCOL_ID,
        "adapter_sha256": stream_digest(Path(__file__), "sha256"),
        "authority": "INPUT_ONLY_EXHAUSTIVE_CASE_UNIVERSE__NO_GOLD_OR_EMPIRICAL_RESULT",
        "source_archive": str(archive_path),
        "source_archive_provider_checksum": expected,
        "source_archive_sha256": archive_sha256,
        "source_test": args.source_test,
        "target_tests": len(member_receipts) - 1,
        "n_cases": len(cases),
        "case_file": str(output_path),
        "case_file_size": output_path.stat().st_size,
        "case_file_sha256": stream_digest(output_path, "sha256"),
        "cluster_count": 1,
        "candidate_universe": "EXHAUSTIVE_CROSS_PRODUCT_WITHIN_SOURCE_NATIVE_ENTITY_TYPE",
        "reference_alignment_members_read": 0,
        "member_receipts": member_receipts,
        "current_terminal": "OAEI_INPUT_CASE_UNIVERSE_BUILT__NO_GOLD__NO_CANDIDATE__NO_COMPARATIVE_RESULT",
    })


def normalize_label(value: Any) -> str:
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKC", text).casefold()
    return " ".join(token for token in re.split(r"[^\w]+", text) if token)


def jaccard(left: str, right: str) -> float:
    a, b = set(left.split()), set(right.split())
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def flat_label_equality(case: dict[str, Any]) -> tuple[str, list[str], dict[str, Any]]:
    left, right = normalize_label(case["left"].get("label")), normalize_label(case["right"].get("label"))
    relation = "GLUE" if left and left == right else "OBSTRUCTION"
    return relation, [relation], {"normalized_equal": bool(left and left == right)}


def token_jaccard_forced(case: dict[str, Any]) -> tuple[str, list[str], dict[str, Any]]:
    score = jaccard(normalize_label(case["left"].get("label")), normalize_label(case["right"].get("label")))
    relation = "GLUE" if score >= 0.5 else "OBSTRUCTION"
    return relation, [relation], {"token_jaccard": score, "threshold": 0.5}


def type_aware_pairwise(case: dict[str, Any]) -> tuple[str, list[str], dict[str, Any]]:
    left_label = normalize_label(case["left"].get("label"))
    right_label = normalize_label(case["right"].get("label"))
    left_type, right_type = case["left"].get("entity_type"), case["right"].get("entity_type")
    if not left_label or not right_label or not left_type or not right_type:
        return "UNRESOLVED", ["GLUE", "OBSTRUCTION"], {"reason": "MISSING_LABEL_OR_TYPE"}
    score = jaccard(left_label, right_label)
    relation = "GLUE" if left_type == right_type and score >= 0.5 else "OBSTRUCTION"
    return relation, [relation], {"types_equal": left_type == right_type, "token_jaccard": score}


def complete_case_conservative(case: dict[str, Any]) -> tuple[str, list[str], dict[str, Any]]:
    required = case.get("required_coordinates", [])
    left, right = case["left"], case["right"]
    missing: list[str] = []
    unequal: list[str] = []
    for coordinate in required:
        if left.get("observedness", {}).get(coordinate) != "OBSERVED" or right.get("observedness", {}).get(coordinate) != "OBSERVED":
            missing.append(coordinate)
            continue
        if left.get("coordinates", {}).get(coordinate) != right.get("coordinates", {}).get(coordinate):
            unequal.append(coordinate)
    if missing:
        return "UNRESOLVED", ["GLUE", "OBSTRUCTION"], {"missing_required_coordinates": missing}
    relation = "OBSTRUCTION" if unequal else "GLUE"
    return relation, [relation], {"unequal_required_coordinates": unequal}


COMPARATORS = {
    "FLAT_LABEL_EQUALITY_V1": flat_label_equality,
    "TOKEN_JACCARD_FORCED_V1": token_jaccard_forced,
    "TYPE_AWARE_PAIRWISE_V1": type_aware_pairwise,
    "COMPLETE_CASE_CONSERVATIVE_V1": complete_case_conservative,
}


def canonical_case_digest(case: dict[str, Any]) -> str:
    payload = {key: value for key, value in case.items() if key != "input_digest"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def cmd_seal_cases(args: argparse.Namespace) -> None:
    sealed: list[dict[str, Any]] = []
    seen_case_ids: set[str] = set()
    for row_index, case in enumerate(read_jsonl(Path(args.cases)), 1):
        validate_case(case, f"case[{row_index}]", require_digest=False)
        if case["case_id"] in seen_case_ids:
            raise ValueError(f"case[{row_index}]: duplicate case_id {case['case_id']}")
        seen_case_ids.add(case["case_id"])
        case = dict(case)
        case.pop("input_digest", None)
        case["input_digest"] = canonical_case_digest(case)
        sealed.append(case)
    write_jsonl(Path(args.out), sealed)


def cmd_run_comparators(args: argparse.Namespace) -> None:
    comparator_ids = args.comparator or list(COMPARATORS)
    unknown = sorted(set(comparator_ids) - set(COMPARATORS))
    if unknown:
        raise ValueError(f"unknown comparators: {unknown}")
    outputs: list[dict[str, Any]] = []
    seen_case_ids: set[str] = set()
    for row_index, case in enumerate(read_jsonl(Path(args.cases)), 1):
        validate_case(case, f"case[{row_index}]", require_digest=True)
        if case["case_id"] in seen_case_ids:
            raise ValueError(f"case[{row_index}]: duplicate case_id {case['case_id']}")
        seen_case_ids.add(case["case_id"])
        observed_digest = canonical_case_digest(case)
        declared_digest = case["input_digest"]
        if declared_digest != observed_digest:
            raise ValueError(f"case {case.get('case_id')} input_digest mismatch")
        for comparator_id in comparator_ids:
            relation, admissible, details = COMPARATORS[comparator_id](case)
            outputs.append({
                "schema_version": "orion.p3.public-prediction.v1.1",
                "case_id": case["case_id"],
                "system_id": comparator_id,
                "relation": relation,
                "admissible_relations": sorted(set(admissible)),
                "input_digest": observed_digest,
                "details": details,
                "gold_accessed": False,
            })
    write_jsonl(Path(args.out), outputs)


def point_loss(action: str, truth: str, costs: dict[str, float]) -> float:
    if action not in RELATIONS or truth not in RELATIONS:
        raise ValueError(f"point_loss requires declared relations, received action={action!r}, truth={truth!r}")
    if action == truth:
        return 0.0
    if action == "UNRESOLVED":
        return costs["unresolved"]
    if truth == "UNRESOLVED":
        return costs["unjustified_resolution"]
    if action == "GLUE":
        return costs["false_merge"]
    if action == "OBSTRUCTION":
        return costs["false_split"] if truth == "GLUE" else costs["plural_collapse"]
    if action == "PLURAL":
        return costs["false_plural"]
    raise AssertionError("unreachable four-terminal loss branch")


def robust_floor(identified: list[str], costs: dict[str, float]) -> float:
    actions = ["GLUE", "OBSTRUCTION", "PLURAL", "UNRESOLVED"]
    return min(max(point_loss(action, truth, costs) for truth in identified) for action in actions)


def validate_gold_row(row: dict[str, Any], case: dict[str, Any], context: str) -> None:
    require_closed_fields(row, GOLD_FIELDS, context)
    required = {
        "case_id",
        "cluster_id",
        "source_id",
        "panel_id",
        "input_digest",
        "true_relation",
        "identified_relations",
        "gold_authority",
        "protected_evidence",
        "coordinate_opportunities",
    }
    missing = sorted(required - set(row))
    if missing:
        raise ValueError(f"{context}: missing public-gold fields: {missing}")
    if row["protected_evidence"] is not False:
        raise ValueError(f"{context}: public gold must declare protected_evidence=false")
    if row["gold_authority"] not in {"CRAFT_PUBLIC_GOLD", "SCIREX_PUBLIC_GOLD", "OAEI_PUBLIC_REFERENCE"}:
        raise ValueError(f"{context}: invalid gold_authority {row['gold_authority']!r}")
    expected_authority = {
        "CRAFT_SHARED_TASK_2019_ZENODO_3460908": "CRAFT_PUBLIC_GOLD",
        "SCIREX_GITHUB_7DAAD660": "SCIREX_PUBLIC_GOLD",
        "OAEI_2004_ZENODO_15827226": "OAEI_PUBLIC_REFERENCE",
    }.get(case["source_id"])
    if expected_authority is not None and row["gold_authority"] != expected_authority:
        raise ValueError(f"{context}: source requires gold_authority={expected_authority}")
    if row["true_relation"] not in RELATIONS:
        raise ValueError(f"{context}: invalid true_relation {row['true_relation']!r}")
    identified = row["identified_relations"]
    if not isinstance(identified, list) or not identified or len(identified) != len(set(identified)) or not set(identified) <= RELATIONS:
        raise ValueError(f"{context}: invalid identified_relations")
    if row["true_relation"] not in identified:
        raise ValueError(f"{context}: true_relation must belong to identified_relations")
    for authority_key in ("cluster_id", "source_id", "panel_id", "input_digest"):
        if row[authority_key] != case[authority_key]:
            raise ValueError(
                f"{context}: {authority_key} mismatch, gold={row[authority_key]!r}, "
                f"case={case[authority_key]!r}"
            )
    opportunities = row["coordinate_opportunities"]
    if not isinstance(opportunities, dict) or not set(opportunities) <= COORDINATES:
        raise ValueError(f"{context}: invalid coordinate_opportunities object")
    for coordinate, entry in opportunities.items():
        if not isinstance(entry, dict) or set(entry) != {"status", "count"}:
            raise ValueError(f"{context}: {coordinate} opportunity must contain exactly status and count")
        if entry["status"] not in {"NONZERO", "ZERO", "CANNOT_CHECK"}:
            raise ValueError(f"{context}: invalid {coordinate} opportunity status")
        if not isinstance(entry["count"], int) or isinstance(entry["count"], bool) or entry["count"] < 0:
            raise ValueError(f"{context}: invalid {coordinate} opportunity count")
        if (entry["status"] == "NONZERO") != (entry["count"] > 0):
            raise ValueError(f"{context}: {coordinate} status/count contradiction")


def enforce_coordinate_opportunity_gates(cases: dict[str, dict[str, Any]], gold: dict[str, dict[str, Any]]) -> dict[str, Any]:
    claimed_by_source: dict[str, set[str]] = defaultdict(set)
    for case in cases.values():
        claimed_by_source[case["source_id"]].update(case["required_coordinates"])
    receipts: dict[str, Any] = {}
    for source_id, claimed in claimed_by_source.items():
        source_gold = [gold[case_id] for case_id, case in cases.items() if case["source_id"] == source_id]
        source_receipt: dict[str, Any] = {}
        for coordinate in sorted(claimed):
            entries: list[dict[str, Any]] = []
            for row in source_gold:
                entry = row["coordinate_opportunities"].get(coordinate)
                if entry is None:
                    raise GateFailure(f"ZERO_OR_UNKNOWN_OPPORTUNITY: {source_id}/{coordinate} missing on case {row['case_id']}")
                if entry["status"] == "CANNOT_CHECK":
                    raise GateFailure(f"ZERO_OR_UNKNOWN_OPPORTUNITY: {source_id}/{coordinate} cannot check on case {row['case_id']}")
                entries.append(entry)
            total = sum(entry["count"] for entry in entries)
            if total <= 0:
                raise GateFailure(f"ZERO_OR_UNKNOWN_OPPORTUNITY: {source_id}/{coordinate} total={total}")
            source_receipt[coordinate] = {"status": "PASS_NONZERO", "count": total, "n_cases_audited": len(entries)}
        receipts[source_id] = source_receipt
    return receipts


def summarize_rows(rows: list[dict[str, Any]], loss_grid: list[dict[str, float]]) -> dict[str, Any]:
    n = len(rows)
    merge_opportunities = sum(row["truth"] == "GLUE" for row in rows)
    obstruction_opportunities = sum(row["truth"] == "OBSTRUCTION" for row in rows)
    plural_opportunities = sum(row["truth"] == "PLURAL" for row in rows)
    unresolved_truth_opportunities = sum(row["truth"] == "UNRESOLVED" for row in rows)
    non_singleton_rows = [row for row in rows if row["identified_set_non_singleton"] is True]
    covered_rows = [row for row in rows if row["gold_in_envelope"]]
    floor_summary: list[dict[str, Any]] = []
    for grid_index, costs in enumerate(loss_grid):
        values = [row["floor_adjusted"][grid_index] for row in rows]
        by_cluster: dict[str, list[float]] = defaultdict(list)
        for row, value in zip(rows, values):
            by_cluster[row["cluster_id"]].append(value["excess_harm"])
        cluster_means = [sum(items) / len(items) for items in by_cluster.values()]
        floor_summary.append({
            "costs": costs,
            "status": "CLUSTER_WEIGHTED_DESCRIPTIVE_NO_INTERVAL",
            "case_weighted_mean_excess_harm": sum(value["excess_harm"] for value in values) / n if n else None,
            "cluster_weighted_mean_excess_harm": sum(cluster_means) / len(cluster_means) if cluster_means else None,
            "n_clusters": len(cluster_means),
        })
    return {
        "n_cases": n,
        "n_clusters": len({row["cluster_id"] for row in rows}),
        "exact_rate": sum(row["exact"] for row in rows) / n if n else None,
        "merge_opportunities": merge_opportunities,
        "false_split_rate_on_merge_opportunities": sum(row["false_split"] for row in rows) / merge_opportunities if merge_opportunities else None,
        "obstruction_opportunities": obstruction_opportunities,
        "false_merge_rate_on_obstruction_opportunities": sum(row["false_merge"] and row["truth"] == "OBSTRUCTION" for row in rows) / obstruction_opportunities if obstruction_opportunities else None,
        "plural_opportunities": plural_opportunities,
        "plural_collapse_rate": sum(row["plural_collapse"] for row in rows) / plural_opportunities if plural_opportunities else None,
        "false_merge_rate_on_plural_opportunities": sum(row["false_merge"] and row["truth"] == "PLURAL" for row in rows) / plural_opportunities if plural_opportunities else None,
        "false_plural_rate": sum(row["false_plural"] for row in rows) / (n - plural_opportunities - unresolved_truth_opportunities) if n - plural_opportunities - unresolved_truth_opportunities else None,
        "unresolved_truth_opportunities": unresolved_truth_opportunities,
        "unjustified_resolution_rate": sum(row["unjustified_resolution"] for row in rows) / unresolved_truth_opportunities if unresolved_truth_opportunities else None,
        "unresolved_rate": sum(row["unresolved"] for row in rows) / n if n else None,
        "gold_in_envelope_coverage": sum(row["gold_in_envelope"] for row in rows) / n if n else None,
        "mean_envelope_size_conditional_on_coverage": sum(row["envelope_size"] for row in covered_rows) / len(covered_rows) if covered_rows else None,
        "non_singleton_identified_set_opportunities": len(non_singleton_rows),
        "over_resolution_rate_on_non_singleton_identified_sets": sum(bool(row["over_resolution"]) for row in non_singleton_rows) / len(non_singleton_rows) if non_singleton_rows else None,
        "floor_adjusted_identified_case_count": n,
        "floor_adjusted_status": "DECIDED_DESCRIPTIVELY",
        "floor_adjusted_case_weighted_summary": floor_summary,
        "case_results": rows,
    }


def cmd_score_public(args: argparse.Namespace) -> None:
    if not args.ack_public_gold_not_protected:
        raise SystemExit("Scoring requires --ack-public-gold-not-protected.")
    case_rows = list(read_jsonl(Path(args.cases)))
    cases: dict[str, dict[str, Any]] = {}
    for row_index, case in enumerate(case_rows, 1):
        validate_case(case, f"case[{row_index}]", require_digest=True)
        if case["case_id"] in cases:
            raise ValueError(f"case[{row_index}]: duplicate case_id {case['case_id']}")
        if case["input_digest"] != canonical_case_digest(case):
            raise ValueError(f"case[{row_index}]: input_digest mismatch")
        cases[case["case_id"]] = case
    if not cases:
        raise ValueError("scoring requires at least one sealed case")

    gold_rows = list(read_jsonl(Path(args.gold)))
    gold: dict[str, dict[str, Any]] = {}
    for row_index, row in enumerate(gold_rows, 1):
        case_id = row.get("case_id")
        if case_id not in cases:
            raise ValueError(f"public_gold[{row_index}]: unknown case_id {case_id!r}")
        if case_id in gold:
            raise ValueError(f"public_gold[{row_index}]: duplicate case_id {case_id}")
        validate_gold_row(row, cases[case_id], f"public_gold[{row_index}]")
        gold[case_id] = row
    if set(gold) != set(cases):
        raise ValueError(f"public gold exact-coverage failure: missing={sorted(set(cases)-set(gold))}, extra={sorted(set(gold)-set(cases))}")
    opportunity_receipt = enforce_coordinate_opportunity_gates(cases, gold)

    predictions = list(read_jsonl(Path(args.predictions)))
    by_system_predictions: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row_index, prediction in enumerate(predictions, 1):
        validate_prediction(prediction, f"prediction[{row_index}]")
        case_id = prediction["case_id"]
        if case_id not in cases:
            raise ValueError(f"prediction[{row_index}]: unknown case_id {case_id}")
        system_id = prediction["system_id"]
        if case_id in by_system_predictions[system_id]:
            raise ValueError(f"prediction[{row_index}]: duplicate (system_id, case_id)=({system_id}, {case_id})")
        if prediction["input_digest"] != cases[case_id]["input_digest"]:
            raise ValueError(f"prediction[{row_index}]: input_digest mismatch for {case_id}")
        by_system_predictions[system_id][case_id] = prediction
    if not by_system_predictions:
        raise ValueError("scoring requires at least one prediction system")
    for system_id, system_predictions in by_system_predictions.items():
        if set(system_predictions) != set(cases):
            raise ValueError(
                f"prediction exact-coverage failure for {system_id}: "
                f"missing={sorted(set(cases)-set(system_predictions))}, extra={sorted(set(system_predictions)-set(cases))}"
            )

    loss_grid = read_json(PROTOCOL_PATH)["endpoints"]["loss_grid"]
    systems: dict[str, Any] = {}
    for system_id, system_predictions in sorted(by_system_predictions.items()):
        rows: list[dict[str, Any]] = []
        for case_id, case in cases.items():
            prediction = system_predictions[case_id]
            truth = gold[case_id]["true_relation"]
            relation = prediction["relation"]
            identified = gold[case_id]["identified_relations"]
            row = {
                "case_id": case_id,
                "cluster_id": case["cluster_id"],
                "source_id": case["source_id"],
                "panel_id": case["panel_id"],
                "truth": truth,
                "prediction": relation,
                "exact": relation == truth,
                "false_merge": relation == "GLUE" and truth in {"OBSTRUCTION", "PLURAL"},
                "false_split": relation == "OBSTRUCTION" and truth == "GLUE",
                "plural_collapse": relation == "OBSTRUCTION" and truth == "PLURAL",
                "false_plural": relation == "PLURAL" and truth in {"GLUE", "OBSTRUCTION"},
                "unjustified_resolution": truth == "UNRESOLVED" and relation != "UNRESOLVED",
                "unresolved": relation == "UNRESOLVED",
                "gold_in_envelope": truth in prediction["admissible_relations"],
                "envelope_size": len(prediction["admissible_relations"]),
                "identified_set_non_singleton": len(set(identified)) > 1,
                "over_resolution": len(set(identified)) > 1 and relation in {"GLUE", "OBSTRUCTION"},
                "floor_adjusted": [],
            }
            for costs in loss_grid:
                loss = max(point_loss(relation, possible, costs) for possible in identified)
                floor = robust_floor(identified, costs)
                row["floor_adjusted"].append({
                    "costs": costs,
                    "status": "DECIDED",
                    "loss": loss,
                    "floor": floor,
                    "excess_harm": loss - floor,
                })
            rows.append(row)
        by_source = {
            source_id: summarize_rows([row for row in rows if row["source_id"] == source_id], loss_grid)
            for source_id in sorted({row["source_id"] for row in rows})
        }
        systems[system_id] = {
            "cross_source_summary_authority": "DESCRIPTIVE_ONLY__NO_POOLED_PASS",
            "all_cases_descriptive": summarize_rows(rows, loss_grid),
            "source_results": by_source,
        }
    write_json(Path(args.out), {
        "schema_version": "orion.p3.public-score.v1.1",
        "protocol_id": PROTOCOL_ID,
        "authority": "PUBLIC_VISIBLE_GOLD_DEVELOPMENT_TRANSPORT_ONLY",
        "protected_evidence": False,
        "coordinate_opportunity_gates": opportunity_receipt,
        "comparative_terminal": "PUBLIC_TRANSPORT_CANNOT_CHECK_STRONGEST_SOURCE_NATIVE_COMPARATOR",
        "cross_source_terminal": "NO_POOLED_PASS",
        "warning": "Case-level rates are descriptive. Inference must use source-artifact-family clusters; OAEI numbered tests share one seed family.",
        "systems": systems,
    })


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    fetch = sub.add_parser("fetch", help="Download and verify rights-gated source packages")
    fetch.add_argument("--source", action="append", choices=list(source_map()))
    fetch.add_argument("--data-dir", required=True)
    fetch.add_argument("--receipt", required=True)
    fetch.add_argument(
        "--rights-decision",
        action="append",
        help="Human-owned V1.1 rights-decision JSON; required for CRAFT and SciREX bodies",
    )
    fetch.add_argument("--include-public-gold", action="store_true")
    fetch.add_argument("--ack-craft-terms", action="store_true", help="Legacy V1 flag; does not authorize V1.1 acquisition")
    fetch.add_argument("--ack-scirex-content-rights", action="store_true", help="Legacy V1 flag; does not authorize V1.1 acquisition")
    fetch.set_defaults(func=cmd_fetch)

    inventory = sub.add_parser("inventory", help="Enumerate independent units without label-conditioned selection")
    inventory.add_argument("--data-dir", required=True)
    inventory.add_argument("--out", required=True)
    inventory.add_argument("--ack-scirex-content-rights", action="store_true")
    inventory.set_defaults(func=cmd_inventory)

    sample = sub.add_parser("sample", help="Freeze a deterministic outcome-blind census/split manifest")
    sample.add_argument("--inventory", required=True)
    sample.add_argument("--out", required=True)
    sample.set_defaults(func=cmd_sample)

    build_oaei = sub.add_parser(
        "build-oaei-cases",
        help="Build exhaustive type-compatible OAEI input cases without opening reference alignments",
    )
    build_oaei.add_argument("--data-dir", required=True)
    build_oaei.add_argument("--source-test", default="101")
    build_oaei.add_argument("--out", required=True)
    build_oaei.add_argument("--receipt", required=True)
    build_oaei.set_defaults(func=cmd_build_oaei_cases)

    seal = sub.add_parser("seal-cases", help="Bind SHA-256 digests to gold-free common cases")
    seal.add_argument("--cases", required=True)
    seal.add_argument("--out", required=True)
    seal.set_defaults(func=cmd_seal_cases)

    compare = sub.add_parser("run-comparators", help="Run deterministic comparators on gold-free common cases")
    compare.add_argument("--cases", required=True)
    compare.add_argument("--out", required=True)
    compare.add_argument("--comparator", action="append", choices=list(COMPARATORS))
    compare.set_defaults(func=cmd_run_comparators)

    score = sub.add_parser("score-public", help="Score frozen predictions against visible public gold")
    score.add_argument("--cases", required=True)
    score.add_argument("--predictions", required=True)
    score.add_argument("--gold", required=True)
    score.add_argument("--out", required=True)
    score.add_argument("--ack-public-gold-not-protected", action="store_true")
    score.set_defaults(func=cmd_score_public)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
