#!/usr/bin/env python3
"""P3 OAEI cross-construct public-development successor.

This is a distinct, explicitly post-public-gold-informed development identity.
It preserves V1/V2 adverse results, removes the same-construct universe block,
and makes benchmark expressibility explicit through CANNOT_CHECK rows.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import unicodedata
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urldefrag, urljoin
from xml.etree import ElementTree


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREDECESSOR = ROOT / "work/orion-takeover/development/p3-oaei-public-development-execution-2026-08-23"
ADAPTER_PATH = ROOT / "work/orion-takeover/development/p3-public-data-successor-2026-08-23/p3_public_data_adapter.py"
LOSS_PROTOCOL_PATH = ROOT / "work/orion-takeover/development/p3-public-data-successor-2026-08-23/P3_PUBLIC_DATA_SUCCESSOR_PROTOCOL_V1_1.json"
PROTOCOL_ID = "P3.PUBLIC.OAEI.CROSS_CONSTRUCT.IDENTIFICATION_ENVELOPE.DEV.V3"
TARGETS = ["102", "103", "104", "105", "201", "202", "204", "205", "206", "221", "222", "223", "224", "225", "228", "230", "301", "302", "303", "304"]
SYSTEMS = [
    "AML_V3_2_AUTO_SOURCE_NATIVE",
    "FLAT_LABEL_EQUALITY_V1",
    "TOKEN_JACCARD_FORCED_V1",
    "P3_CONFLICT_PRESERVING_WRAPPER_V2_CROSS_CONSTRUCT",
    "P3_MAXIMAL_BINARY_IDENTIFICATION_ENVELOPE_V3",
    "P3_INFORMATION_EQUIVALENT_IDEAL_V3",
]

spec = importlib.util.spec_from_file_location("p3_v11_adapter", ADAPTER_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load repaired V1.1 adapter")
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON") from exc


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def normalize_label(value: Any) -> str:
    text = unicodedata.normalize("NFKC", "" if value is None else str(value)).casefold()
    return " ".join(piece for piece in re.split(r"[^\w]+", text) if piece)


def jaccard(left: str, right: str) -> float:
    a, b = set(left.split()), set(right.split())
    return len(a & b) / len(a | b) if a or b else 0.0


def canonical_referent(test_id: str, uri: str) -> str:
    """Reconcile only aliases of the ontology document IRI."""
    base, fragment = urldefrag(uri)
    if uri.startswith("#"):
        return f"DOCUMENT::{test_id}#{fragment}"
    if fragment and re.search(rf"(?:^|/){re.escape(test_id)}/onto\.rdf$", base):
        return f"DOCUMENT::{test_id}#{fragment}"
    return f"ABSOLUTE::{uri}"


def target_of_case(case: dict[str, Any]) -> str:
    return Path(case["provenance"]["right_member"]).parent.name


def case_key(case: dict[str, Any]) -> tuple[str, str, str]:
    target = target_of_case(case)
    return (
        target,
        canonical_referent("101", case["left"]["coordinates"]["REFERENT"]),
        canonical_referent(target, case["right"]["coordinates"]["REFERENT"]),
    )


def alignment_cells(raw: bytes) -> list[dict[str, Any]]:
    root = ElementTree.fromstring(raw)
    rdf_resource = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"
    cells: list[dict[str, Any]] = []
    for cell in root.iter():
        if adapter.xml_local_name(cell.tag) != "Cell":
            continue
        row: dict[str, Any] = {"entity1": None, "entity2": None, "relation": None, "measure": None}
        for child in cell:
            name = adapter.xml_local_name(child.tag)
            if name in {"entity1", "entity2"}:
                row[name] = child.attrib.get(rdf_resource)
            elif name == "relation":
                row[name] = (child.text or "").strip()
            elif name == "measure":
                try:
                    row[name] = float((child.text or "").strip())
                except ValueError:
                    row[name] = None
        if row["entity1"] and row["entity2"]:
            cells.append(row)
    return cells


def signature_entities(raw: bytes, member_name: str, test_id: str) -> tuple[list[dict[str, str]], dict[str, Any]]:
    """Build a referent registry without using reference-alignment content."""
    root = ElementTree.fromstring(raw)
    xml_base = root.attrib.get("{http://www.w3.org/XML/1998/namespace}base", "")
    rdf_resource = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"
    explicit = adapter.oaei_entities(raw, member_name)
    class_positions = {"subClassOf", "domain", "range", "equivalentClass", "disjointWith", "allValuesFrom", "someValuesFrom", "onClass"}
    property_positions = {"onProperty", "subPropertyOf", "equivalentProperty", "inverseOf"}
    builtins = (
        "http://www.w3.org/2001/XMLSchema#",
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "http://www.w3.org/2000/01/rdf-schema#",
        "http://www.w3.org/2002/07/owl#",
    )
    registry: dict[str, dict[str, Any]] = {}

    def add(uri: str, construct: str, label: str | None, explicit_declaration: bool) -> None:
        if not uri:
            return
        key = canonical_referent(test_id, uri)
        row = registry.setdefault(key, {"uris": set(), "explicit_constructs": set(), "inferred_constructs": set(), "labels": set(), "explicit": False})
        row["uris"].add(uri)
        if explicit_declaration:
            row["explicit_constructs"].add(construct)
        else:
            row["inferred_constructs"].add(construct)
        if label:
            row["labels"].add(label)
        row["explicit"] = row["explicit"] or explicit_declaration

    for row in explicit:
        add(row["uri"], row["entity_type"], row["label"], True)
    for element in root.iter():
        name = adapter.xml_local_name(element.tag)
        if name not in class_positions | property_positions:
            continue
        value = element.attrib.get(rdf_resource)
        if not value:
            continue
        uri = urljoin(xml_base, value)
        if uri.startswith(builtins):
            continue
        construct = "ClassReference" if name in class_positions else "PropertyReference"
        add(uri, construct, adapter.uri_local_name(uri), False)

    rows: list[dict[str, str]] = []
    for key, value in sorted(registry.items()):
        uris = sorted(value["uris"], key=lambda item: (not item.startswith("#"), len(item), item))
        labels = sorted(value["labels"], key=lambda item: (len(item), item.casefold(), item))
        constructs = value["explicit_constructs"] or value["inferred_constructs"]
        rows.append({
            "identity_key": key,
            "uri": uris[0],
            "label": labels[0] if labels else adapter.uri_local_name(uris[0]),
            "construct": "+".join(sorted(constructs)),
            "explicit": str(bool(value["explicit"])).lower(),
        })
    return rows, {
        "n_explicit_declarations": len(explicit),
        "n_signature_referents": len(rows),
        "n_added_referents": sum(row["explicit"] == "false" for row in rows),
        "construct_counts": dict(sorted(Counter(row["construct"] for row in rows).items())),
    }


def cmd_build_cases(args: argparse.Namespace) -> None:
    archive_path = Path(args.archive)
    output = Path(args.out)
    receipt = Path(args.receipt)
    expected_archive = "f22aac206773e4eacdd54cf9519ffe997332a430326bdae29f4210a24efab0b4"
    if sha(archive_path) != expected_archive:
        raise ValueError("OAEI archive digest mismatch")
    output.parent.mkdir(parents=True, exist_ok=True)
    member_receipts: list[dict[str, Any]] = []
    n_cases = 0
    same_construct = 0
    cross_construct = 0
    case_ids: set[str] = set()
    with zipfile.ZipFile(archive_path) as archive, output.open("w", encoding="utf-8") as handle:
        members = adapter.oaei_onto_members(archive)
        source_raw = archive.read(members["101"])
        source_entities, source_stats = signature_entities(source_raw, members["101"], "101")
        member_receipts.append({"test_id": "101", "member": members["101"], "member_sha256": hashlib.sha256(source_raw).hexdigest(), **source_stats})
        for target in TARGETS:
            target_raw = archive.read(members[target])
            target_entities, target_stats = signature_entities(target_raw, members[target], target)
            member_receipts.append({"test_id": target, "member": members[target], "member_sha256": hashlib.sha256(target_raw).hexdigest(), **target_stats})
            for left in source_entities:
                for right in target_entities:
                    identity = f"{PROTOCOL_ID}\0{target}\0{left['identity_key']}\0{right['identity_key']}"
                    cid = "P3.OAEI.CROSS.V3." + hashlib.sha256(identity.encode()).hexdigest()[:24]
                    case = {
                        "case_id": cid,
                        "cluster_id": "OAEI2004::BIBLIOGRAPHIC_SEED_FAMILY",
                        "source_id": "OAEI_2004_ZENODO_15827226",
                        "panel_id": "OAEI_2004_CROSS_CONSTRUCT_FULL_SIGNATURE_CENSUS",
                        "left": {
                            "label": left["label"],
                            "entity_type": left["construct"],
                            "coordinates": {"REFERENT": left["uri"], "CONSTRUCT": left["construct"]},
                            "observedness": {"REFERENT": "OBSERVED", "CONSTRUCT": "OBSERVED"},
                        },
                        "right": {
                            "label": right["label"],
                            "entity_type": right["construct"],
                            "coordinates": {"REFERENT": right["uri"], "CONSTRUCT": right["construct"]},
                            "observedness": {"REFERENT": "OBSERVED", "CONSTRUCT": "OBSERVED"},
                        },
                        "required_coordinates": ["REFERENT"],
                        "provenance": {
                            "source_archive_sha256": expected_archive,
                            "source_revision": "ZENODO_15827226__MD5_VERIFIED",
                            "left_member": members["101"],
                            "right_member": members[target],
                            "left_locator": f"{members['101']}::{left['identity_key']}",
                            "right_locator": f"{members[target]}::{right['identity_key']}",
                            "builder_id": "P3_OAEI_CROSS_CONSTRUCT_INPUT_SIGNATURE_V3",
                            "builder_revision": "3.0.0",
                        },
                    }
                    case["input_digest"] = adapter.canonical_case_digest(case)
                    adapter.validate_case(case, f"built[{n_cases + 1}]", True)
                    if cid in case_ids:
                        raise ValueError("duplicate case ID")
                    case_ids.add(cid)
                    handle.write(json.dumps(case, sort_keys=True, ensure_ascii=False) + "\n")
                    n_cases += 1
                    if left["construct"] == right["construct"]:
                        same_construct += 1
                    else:
                        cross_construct += 1
    write_json(receipt, {
        "schema_version": "orion.p3.oaei-cross-construct-case-universe.v3",
        "protocol_id": PROTOCOL_ID,
        "authority": "INPUT_ONLY_FULL_CROSS_CONSTRUCT_SIGNATURE_UNIVERSE",
        "public_gold_influenced_protocol_design": True,
        "reference_alignment_content_used_by_case_builder": False,
        "archive_sha256": expected_archive,
        "construction": "FULL_SOURCE_BY_TARGET_CROSS_PRODUCT_OVER_EXPLICIT_PLUS_CLASS_AND_PROPERTY_POSITION_SIGNATURE",
        "identity_policy": "FULL_IRI_EXCEPT_DOCUMENT_RELATIVE_ALIASES__NO_LOCAL_FRAGMENT_COLLAPSE",
        "n_cases": n_cases,
        "n_same_construct_cases": same_construct,
        "n_cross_construct_cases": cross_construct,
        "n_clusters": 1,
        "member_receipts": member_receipts,
        "case_file": str(output),
        "case_file_size": output.stat().st_size,
        "case_file_sha256": sha(output),
        "current_terminal": "V3_CROSS_CONSTRUCT_INPUT_UNIVERSE_BUILT__PUBLIC_DEVELOPMENT_ONLY",
    })


def frozen_aml_pairs(output_dir: Path, manifest: dict[str, Any]) -> tuple[set[tuple[str, str, str]], dict[str, str], dict[str, Any]]:
    selected: set[tuple[str, str, str]] = set()
    statuses = {row["target_test"]: row["status"] for row in manifest["targets"]}
    rows = {row["target_test"]: row for row in manifest["targets"]}
    raw_equivalence_cells = 0
    duplicate_counts: Counter[str] = Counter()
    for target, status in statuses.items():
        if status != "EXECUTED":
            continue
        path = output_dir / f"{target}.rdf"
        if sha(path) != rows[target]["output_sha256"] or path.stat().st_size != rows[target]["output_size"]:
            raise ValueError(f"AML output digest mismatch for {target}")
        target_pairs = []
        for cell in alignment_cells(path.read_bytes()):
            if cell["relation"] not in {"=", "%3D"}:
                continue
            raw_equivalence_cells += 1
            pair = (
                target,
                canonical_referent("101", cell["entity1"]),
                canonical_referent(target, cell["entity2"]),
            )
            target_pairs.append(pair)
            selected.add(pair)
        duplicate_counts[target] = len(target_pairs) - len(set(target_pairs))
    return selected, statuses, {
        "raw_equivalence_cells": raw_equivalence_cells,
        "unique_canonical_pairs": len(selected),
        "duplicate_cells_by_target": dict(sorted(duplicate_counts.items())),
        "n_targets_executed": sum(status == "EXECUTED" for status in statuses.values()),
        "n_targets_failed": sum(status != "EXECUTED" for status in statuses.values()),
    }


def prediction(case: dict[str, Any], system_id: str, aml_selected: bool, aml_available: bool) -> dict[str, Any]:
    left = normalize_label(case["left"]["label"])
    right = normalize_label(case["right"]["label"])
    lexical = bool(left and left == right)
    token_score = jaccard(left, right)
    token = token_score >= 0.5
    if system_id == "AML_V3_2_AUTO_SOURCE_NATIVE":
        if not aml_available:
            relation, admissible = "UNRESOLVED", ["GLUE", "OBSTRUCTION"]
        else:
            relation = "GLUE" if aml_selected else "OBSTRUCTION"
            admissible = [relation]
    elif system_id == "FLAT_LABEL_EQUALITY_V1":
        relation = "GLUE" if lexical else "OBSTRUCTION"
        admissible = [relation]
    elif system_id == "TOKEN_JACCARD_FORCED_V1":
        relation = "GLUE" if token else "OBSTRUCTION"
        admissible = [relation]
    elif system_id == "P3_CONFLICT_PRESERVING_WRAPPER_V2_CROSS_CONSTRUCT":
        if not aml_available or aml_selected != lexical:
            relation, admissible = "UNRESOLVED", ["GLUE", "OBSTRUCTION"]
        else:
            relation = "GLUE" if aml_selected else "OBSTRUCTION"
            admissible = [relation]
    elif system_id in {"P3_MAXIMAL_BINARY_IDENTIFICATION_ENVELOPE_V3", "P3_INFORMATION_EQUIVALENT_IDEAL_V3"}:
        relation, admissible = "UNRESOLVED", ["GLUE", "OBSTRUCTION"]
    else:
        raise ValueError(system_id)
    row = {
        "schema_version": "orion.p3.public-prediction.v1.1",
        "case_id": case["case_id"],
        "system_id": system_id,
        "relation": relation,
        "admissible_relations": admissible,
        "input_digest": case["input_digest"],
        "details": {
            "aml_available": aml_available,
            "aml_selected": aml_selected,
            "normalized_label_equal": lexical,
            "token_jaccard": token_score,
            "construct_transition": f"{case['left']['entity_type']}->{case['right']['entity_type']}",
        },
        "gold_accessed": False,
    }
    adapter.validate_prediction(row, f"prediction[{case['case_id']}/{system_id}]")
    return row


def cmd_run_systems(args: argparse.Namespace) -> None:
    cases_path = Path(args.cases)
    output = Path(args.out)
    receipt = Path(args.receipt)
    manifest = json.loads(Path(args.aml_manifest).read_text())
    selected, statuses, aml_stats = frozen_aml_pairs(Path(args.aml_output_dir), manifest)
    keys: set[tuple[str, str, str]] = set()
    n_cases = 0
    for case in read_jsonl(cases_path):
        adapter.validate_case(case, f"case-map[{n_cases + 1}]", True)
        if case["input_digest"] != adapter.canonical_case_digest(case):
            raise ValueError("case digest mismatch")
        key = case_key(case)
        if key in keys:
            raise ValueError(f"ambiguous cross-construct case key: {key}")
        keys.add(key)
        n_cases += 1
    unmatched = sorted(selected - keys)
    if unmatched:
        raise ValueError(f"{len(unmatched)} AML pairs outside V3 case universe")
    output.parent.mkdir(parents=True, exist_ok=True)
    action_counts = {system: Counter() for system in SYSTEMS}
    construct_counts: Counter[str] = Counter()
    with output.open("w", encoding="utf-8") as handle:
        for case in read_jsonl(cases_path):
            target, _, _ = case_key(case)
            is_selected = case_key(case) in selected
            available = statuses[target] == "EXECUTED"
            construct_counts[f"{case['left']['entity_type']}->{case['right']['entity_type']}"] += 1
            for system in SYSTEMS:
                row = prediction(case, system, is_selected, available)
                handle.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
                action_counts[system][row["relation"]] += 1
    write_json(receipt, {
        "schema_version": "orion.p3.oaei-cross-construct-prediction-freeze.v3",
        "protocol_id": PROTOCOL_ID,
        "authority": "POST_PUBLIC_GOLD_INFORMED_DEVELOPMENT_PREDICTION_FREEZE",
        "public_gold_influenced_system_design": True,
        "reference_alignment_read_during_this_execution": False,
        "case_file_sha256": sha(cases_path),
        "prediction_file": str(output),
        "prediction_file_size": output.stat().st_size,
        "prediction_file_sha256": sha(output),
        "n_cases": n_cases,
        "n_prediction_rows": n_cases * len(SYSTEMS),
        "systems": SYSTEMS,
        "system_action_counts": {system: dict(sorted(counts.items())) for system, counts in action_counts.items()},
        "construct_transition_counts": dict(sorted(construct_counts.items())),
        "aml_stats": aml_stats,
        "aml_pairs_outside_case_universe": len(unmatched),
        "current_terminal": "V3_CROSS_CONSTRUCT_PREDICTIONS_FROZEN__POST_GOLD_INFORMED_PUBLIC_DEVELOPMENT",
    })


def cmd_freeze(args: argparse.Namespace) -> None:
    protocol = Path(args.protocol)
    script = Path(args.script)
    case_receipt_path = Path(args.case_receipt)
    prediction_receipt_path = Path(args.prediction_receipt)
    cases = Path(args.cases)
    predictions = Path(args.predictions)
    case_receipt = json.loads(case_receipt_path.read_text())
    prediction_receipt = json.loads(prediction_receipt_path.read_text())
    if json.loads(protocol.read_text()).get("protocol_id") != PROTOCOL_ID:
        raise ValueError("protocol identity mismatch")
    if case_receipt.get("case_file_sha256") != sha(cases):
        raise ValueError("case receipt mismatch")
    if prediction_receipt.get("case_file_sha256") != sha(cases) or prediction_receipt.get("prediction_file_sha256") != sha(predictions):
        raise ValueError("prediction receipt mismatch")
    files = [protocol, script, case_receipt_path, prediction_receipt_path, cases, predictions, Path(args.rights), Path(args.aml_binding), Path(args.aml_manifest)]
    write_json(Path(args.out), {
        "schema_version": "orion.p3.oaei-cross-construct-development-freeze.v3",
        "protocol_id": PROTOCOL_ID,
        "authority": "POST_PUBLIC_GOLD_INFORMED_DEVELOPMENT_EXECUTION_FREEZE",
        "public_gold_influenced_design": True,
        "no_blind_or_confirmatory_custody_claim": True,
        "frozen_files": [{"path": str(path), "size": path.stat().st_size, "sha256": sha(path)} for path in files],
        "current_terminal": "V3_DEVELOPMENT_IDENTITY_FROZEN__PUBLIC_REFERENCE_REPLAY_MAY_RUN",
    })


def cmd_join_gold(args: argparse.Namespace) -> None:
    cases_path = Path(args.cases)
    archive_path = Path(args.archive)
    output = Path(args.out)
    receipt_path = Path(args.receipt)
    cases: dict[str, dict[str, Any]] = {}
    keys: dict[tuple[str, str, str], str] = {}
    cases_by_target: Counter[str] = Counter()
    for index, case in enumerate(read_jsonl(cases_path), 1):
        adapter.validate_case(case, f"case[{index}]", True)
        key = case_key(case)
        if key in keys:
            raise ValueError(f"ambiguous case key {key}")
        keys[key] = case["case_id"]
        cases[case["case_id"]] = case
        cases_by_target[key[0]] += 1

    refs: dict[str, str] = {}
    reference: dict[str, dict[str, Any]] = {}
    member_receipts = []
    with zipfile.ZipFile(archive_path) as archive:
        refs = {Path(name).parent.name: name for name in archive.namelist() if Path(name).name.lower() == "refalign.rdf"}
        for target in TARGETS:
            if target not in refs:
                reference[target] = {"status": "NO_REFERENCE_MEMBER", "source_domain": set(), "target_domain": set(), "equivalence": set(), "nonexpressible": set(), "cells": []}
                continue
            raw = archive.read(refs[target])
            cells = alignment_cells(raw)
            source_domain: set[str] = set()
            target_domain: set[str] = set()
            equivalence: set[tuple[str, str]] = set()
            nonexpressible: set[tuple[str, str]] = set()
            for cell in cells:
                left = canonical_referent("101", cell["entity1"])
                right = canonical_referent(target, cell["entity2"])
                source_domain.add(left)
                target_domain.add(right)
                if cell["relation"] in {"=", "%3D"}:
                    equivalence.add((left, right))
                else:
                    nonexpressible.add((left, right))
            reference[target] = {"status": "REFERENCE_AVAILABLE", "source_domain": source_domain, "target_domain": target_domain, "equivalence": equivalence, "nonexpressible": nonexpressible, "cells": cells}
            member_receipts.append({
                "target_test": target,
                "member": refs[target],
                "sha256": hashlib.sha256(raw).hexdigest(),
                "n_cells": len(cells),
                "n_equivalence_pairs": len(equivalence),
                "n_nonexpressible_pairs": len(nonexpressible),
                "n_source_domain_referents": len(source_domain),
                "n_target_domain_referents": len(target_domain),
            })

    missing_equivalence = []
    missing_nonexpressible = []
    equivalence_total = 0
    equivalence_mapped = 0
    nonexpressible_total = 0
    nonexpressible_mapped = 0
    for target, row in reference.items():
        for left, right in row["equivalence"]:
            equivalence_total += 1
            if (target, left, right) in keys:
                equivalence_mapped += 1
            else:
                missing_equivalence.append({"target": target, "left": left, "right": right})
        for left, right in row["nonexpressible"]:
            nonexpressible_total += 1
            if (target, left, right) in keys:
                nonexpressible_mapped += 1
            else:
                missing_nonexpressible.append({"target": target, "left": left, "right": right})

    status_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    truth_counts: Counter[str] = Counter()
    by_target: dict[str, Counter[str]] = {target: Counter() for target in TARGETS}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for cid, case in cases.items():
            target, left, right = case_key(case)
            ref = reference[target]
            if ref["status"] == "NO_REFERENCE_MEMBER":
                status, reason, truth, identified = "CANNOT_CHECK", "NO_REFERENCE_MEMBER", None, []
            elif left not in ref["source_domain"] or right not in ref["target_domain"]:
                status, reason, truth, identified = "CANNOT_CHECK", "OUTSIDE_REFERENCE_DOMAIN", None, []
            elif (left, right) in ref["nonexpressible"]:
                status, reason, truth, identified = "CANNOT_CHECK", "NON_BINARY_REFERENCE_RELATION", None, []
            elif (left, right) in ref["equivalence"]:
                status, reason, truth, identified = "SCORABLE", None, "GLUE", ["GLUE"]
            else:
                status, reason, truth, identified = "SCORABLE", None, "OBSTRUCTION", ["OBSTRUCTION"]
            row = {
                "schema_version": "orion.p3.oaei-cross-construct-public-gold.v3",
                "case_id": cid,
                "input_digest": case["input_digest"],
                "evaluation_status": status,
                "cannot_check_reason": reason,
                "true_relation": truth,
                "identified_relations": identified,
                "gold_authority": "OAEI_PUBLIC_REFERENCE__POST_GOLD_INFORMED_DEVELOPMENT",
                "protected_evidence": False,
            }
            handle.write(json.dumps(row, sort_keys=True) + "\n")
            status_counts[status] += 1
            by_target[target][status] += 1
            if reason:
                reason_counts[reason] += 1
                by_target[target][reason] += 1
            if truth:
                truth_counts[truth] += 1
                by_target[target][truth] += 1

    recall = equivalence_mapped / equivalence_total if equivalence_total else 0.0
    write_json(receipt_path, {
        "schema_version": "orion.p3.oaei-cross-construct-public-gold-join.v3",
        "protocol_id": PROTOCOL_ID,
        "authority": "PUBLIC_GOLD_INFORMED_DEVELOPMENT__NOT_PROTECTED",
        "archive_sha256": sha(archive_path),
        "case_file_sha256": sha(cases_path),
        "gold_file": str(output),
        "gold_file_size": output.stat().st_size,
        "gold_file_sha256": sha(output),
        "n_cases": len(cases),
        "status_counts": dict(sorted(status_counts.items())),
        "cannot_check_reason_counts": dict(sorted(reason_counts.items())),
        "scorable_truth_counts": dict(sorted(truth_counts.items())),
        "by_target": {target: dict(sorted(counts.items())) for target, counts in by_target.items()},
        "reference_members": member_receipts,
        "missing_reference_members": sorted(set(TARGETS) - set(refs)),
        "binary_equivalence_pairs_total": equivalence_total,
        "binary_equivalence_pairs_mapped": equivalence_mapped,
        "candidate_universe_recall": recall,
        "nonexpressible_pairs_total": nonexpressible_total,
        "nonexpressible_pairs_mapped_to_cannot_check": nonexpressible_mapped,
        "missing_equivalence_pairs": missing_equivalence,
        "missing_nonexpressible_pairs": missing_nonexpressible,
        "gate_status": "PASS" if recall == 1.0 and not missing_equivalence else "FAIL_INVALID_CANDIDATE_UNIVERSE",
        "current_terminal": "V3_PUBLIC_GOLD_EXPRESSIBILITY_JOIN_COMPLETE__PUBLIC_DEVELOPMENT_ONLY",
    })


def empty_counter() -> dict[str, Any]:
    return {"n": 0, "tp": 0, "fp": 0, "fn": 0, "tn": 0, "exact": 0, "unresolved": 0, "covered": 0, "loss_sums": [0.0, 0.0, 0.0]}


def update_counter(counter: dict[str, Any], truth: str, pred: str, covered: bool, losses: list[float]) -> None:
    counter["n"] += 1
    counter["exact"] += pred == truth
    counter["unresolved"] += pred == "UNRESOLVED"
    counter["covered"] += covered
    counter["tp"] += truth == "GLUE" and pred == "GLUE"
    counter["fp"] += truth == "OBSTRUCTION" and pred == "GLUE"
    counter["fn"] += truth == "GLUE" and pred != "GLUE"
    counter["tn"] += truth == "OBSTRUCTION" and pred == "OBSTRUCTION"
    for index, value in enumerate(losses):
        counter["loss_sums"][index] += value


def finalize(counter: dict[str, Any]) -> dict[str, Any]:
    precision = counter["tp"] / (counter["tp"] + counter["fp"]) if counter["tp"] + counter["fp"] else None
    recall = counter["tp"] / (counter["tp"] + counter["fn"]) if counter["tp"] + counter["fn"] else None
    f1 = 2 * precision * recall / (precision + recall) if precision is not None and recall is not None and precision + recall else None
    return {
        **{key: counter[key] for key in ["n", "tp", "fp", "fn", "tn"]},
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "exact_rate": counter["exact"] / counter["n"] if counter["n"] else None,
        "unresolved_rate": counter["unresolved"] / counter["n"] if counter["n"] else None,
        "gold_in_envelope_coverage": counter["covered"] / counter["n"] if counter["n"] else None,
        "mean_floor_adjusted_harm": [value / counter["n"] for value in counter["loss_sums"]] if counter["n"] else None,
    }


def cmd_score(args: argparse.Namespace) -> None:
    cases_path = Path(args.cases)
    predictions_path = Path(args.predictions)
    gold_path = Path(args.gold)
    cases: dict[str, dict[str, Any]] = {}
    case_targets: dict[str, str] = {}
    for index, case in enumerate(read_jsonl(cases_path), 1):
        adapter.validate_case(case, f"case[{index}]", True)
        if case["input_digest"] != adapter.canonical_case_digest(case):
            raise ValueError("case digest mismatch")
        if case["case_id"] in cases:
            raise ValueError("duplicate case")
        cases[case["case_id"]] = case
        case_targets[case["case_id"]] = target_of_case(case)
    gold: dict[str, dict[str, Any]] = {}
    for row in read_jsonl(gold_path):
        cid = row["case_id"]
        if cid not in cases or cid in gold:
            raise ValueError("gold identity failure")
        if row["input_digest"] != cases[cid]["input_digest"]:
            raise ValueError("gold digest mismatch")
        if row["evaluation_status"] == "SCORABLE":
            if row["true_relation"] not in {"GLUE", "OBSTRUCTION"} or row["identified_relations"] != [row["true_relation"]]:
                raise ValueError("invalid scorable gold")
        elif row["evaluation_status"] == "CANNOT_CHECK":
            if row["true_relation"] is not None or row["identified_relations"] != [] or not row["cannot_check_reason"]:
                raise ValueError("invalid CANNOT_CHECK gold")
        else:
            raise ValueError("unknown evaluation status")
        gold[cid] = row
    if set(gold) != set(cases):
        raise ValueError("gold coverage failure")

    loss_grid = json.loads(LOSS_PROTOCOL_PATH.read_text())["endpoints"]["loss_grid"]
    counters = {system: empty_counter() for system in SYSTEMS}
    per_target = {system: {target: empty_counter() for target in TARGETS} for system in SYSTEMS}
    seen = {system: set() for system in SYSTEMS}
    paired: dict[str, dict[str, Any]] = {}
    for index, pred in enumerate(read_jsonl(predictions_path), 1):
        adapter.validate_prediction(pred, f"prediction[{index}]")
        cid, system = pred["case_id"], pred["system_id"]
        if cid not in cases or system not in counters or cid in seen[system]:
            raise ValueError("prediction identity failure")
        if pred["input_digest"] != cases[cid]["input_digest"]:
            raise ValueError("prediction digest mismatch")
        seen[system].add(cid)
        if gold[cid]["evaluation_status"] != "SCORABLE":
            continue
        truth = gold[cid]["true_relation"]
        covered = truth in pred["admissible_relations"]
        losses = [adapter.point_loss(pred["relation"], truth, costs) for costs in loss_grid]
        update_counter(counters[system], truth, pred["relation"], covered, losses)
        update_counter(per_target[system][case_targets[cid]], truth, pred["relation"], covered, losses)
        if system in {"P3_MAXIMAL_BINARY_IDENTIFICATION_ENVELOPE_V3", "P3_INFORMATION_EQUIVALENT_IDEAL_V3"}:
            paired.setdefault(cid, {})[system] = {"relation": pred["relation"], "admissible": pred["admissible_relations"], "losses": losses}
    for system in SYSTEMS:
        if seen[system] != set(cases):
            raise ValueError(f"prediction full-universe coverage failure: {system}")

    systems = {system: {"scorable_census": finalize(counters[system]), "per_target": {target: finalize(per_target[system][target]) for target in TARGETS}} for system in SYSTEMS}
    candidate = "P3_MAXIMAL_BINARY_IDENTIFICATION_ENVELOPE_V3"
    ideal = "P3_INFORMATION_EQUIVALENT_IDEAL_V3"
    aml = "AML_V3_2_AUTO_SOURCE_NATIVE"
    ideal_tie = all(row[candidate] == row[ideal] for row in paired.values())
    harm_delta = [systems[candidate]["scorable_census"]["mean_floor_adjusted_harm"][i] - systems[aml]["scorable_census"]["mean_floor_adjusted_harm"][i] for i in range(3)]
    gold_receipt = json.loads(Path(args.gold_receipt).read_text())

    joint_contrasts: Counter[str] = Counter()
    truth_by_construct_contrast: Counter[str] = Counter()
    construct_transitions: Counter[str] = Counter()
    for cid, row in gold.items():
        if row["evaluation_status"] != "SCORABLE":
            continue
        case = cases[cid]
        target = target_of_case(case)
        left_ref = canonical_referent("101", case["left"]["coordinates"]["REFERENT"])
        right_ref = canonical_referent(target, case["right"]["coordinates"]["REFERENT"])
        referent_contrast = left_ref != right_ref
        construct_contrast = case["left"]["entity_type"] != case["right"]["entity_type"]
        pattern = f"REFERENT_{int(referent_contrast)}__CONSTRUCT_{int(construct_contrast)}"
        joint_contrasts[pattern] += 1
        truth_by_construct_contrast[f"CONSTRUCT_{int(construct_contrast)}__{row['true_relation']}"] += 1
        construct_transitions[f"{case['left']['entity_type']}->{case['right']['entity_type']}"] += 1

    candidate_metrics = systems[candidate]["scorable_census"]
    gates = {
        "binary_candidate_universe_recall_1_0": gold_receipt["candidate_universe_recall"] == 1.0,
        "nonexpressible_pairs_all_mapped_to_cannot_check": gold_receipt["nonexpressible_pairs_mapped_to_cannot_check"] == gold_receipt["nonexpressible_pairs_total"],
        "successor_gold_in_envelope_coverage_1_0": candidate_metrics["gold_in_envelope_coverage"] == 1.0,
        "successor_information_equivalent_ideal_exact_tie": ideal_tie,
        "one_independent_cluster_only": True,
        "public_gold_informed_design": True,
        "protected_authority": False,
    }
    if not gates["binary_candidate_universe_recall_1_0"]:
        mechanics_terminal = "PUBLIC_V3_INVALID_CANDIDATE_UNIVERSE"
    elif not gates["nonexpressible_pairs_all_mapped_to_cannot_check"]:
        mechanics_terminal = "PUBLIC_V3_INVALID_EXPRESSIBILITY_MAP"
    elif not gates["successor_gold_in_envelope_coverage_1_0"]:
        mechanics_terminal = "PUBLIC_V3_INVALID_ENVELOPE_COVERAGE"
    elif not gates["successor_information_equivalent_ideal_exact_tie"]:
        mechanics_terminal = "PUBLIC_V3_INFORMATION_EQUIVALENT_BOUNDARY_FAILED"
    else:
        mechanics_terminal = "PUBLIC_V3_MAXIMAL_BINARY_ENVELOPE_COVERAGE_PASS"
    comparative_terminal = "PUBLIC_V3_DESCRIPTIVE_HARM_SIGNAL" if all(value < 0 for value in harm_delta) else "PUBLIC_V3_NO_HARM_SUPERIORITY"
    coordinate_audit = {
        "claimed_coordinate": "REFERENT",
        "joint_binary_contrast_counts": dict(sorted(joint_contrasts.items())),
        "truth_by_construct_contrast": dict(sorted(truth_by_construct_contrast.items())),
        "construct_transition_counts": dict(sorted(construct_transitions.items())),
        "measurement_opportunity": "CANNOT_CHECK",
        "temporal_context_opportunity": "CANNOT_CHECK",
        "plural_opportunity": "NON_BINARY_OAEI_RELATIONS_EXCLUDED_AS_CANNOT_CHECK__NO_P3_PLURAL_MAPPING_LICENSE",
        "identification_terminal": "DESCRIPTIVE_REFERENT_OPPORTUNITY_ONLY__NO_CAUSAL_COORDINATE_SEPARABILITY_OR_INDEPENDENT_EVALUATOR",
    }
    result = {
        "schema_version": "orion.p3.oaei-cross-construct-development-result.v3",
        "protocol_id": PROTOCOL_ID,
        "authority": "POST_PUBLIC_GOLD_INFORMED_ONE_SEED_FAMILY_DEVELOPMENT_ONLY",
        "protected_evidence": False,
        "n_universe_cases": len(cases),
        "n_scorable_cases": candidate_metrics["n"],
        "n_cannot_check_cases": len(cases) - candidate_metrics["n"],
        "n_clusters": 1,
        "systems": systems,
        "candidate_vs_source_native": {
            "candidate": candidate,
            "comparator": aml,
            "candidate_minus_aml_exact_rate": candidate_metrics["exact_rate"] - systems[aml]["scorable_census"]["exact_rate"],
            "candidate_minus_aml_unresolved_rate": candidate_metrics["unresolved_rate"] - systems[aml]["scorable_census"]["unresolved_rate"],
            "candidate_minus_aml_mean_floor_adjusted_harm": harm_delta,
        },
        "gates": gates,
        "coordinate_audit": coordinate_audit,
        "mechanics_terminal": mechanics_terminal,
        "comparative_terminal": comparative_terminal,
        "adverse_terminals": [
            "POST_PUBLIC_GOLD_INFORMED_DESIGN__NO_CONFIRMATORY_AUTHORITY",
            "AML_TEST_206_UNPARSABLE_SOURCE_NATIVE_RUNTIME_FAILURE",
            "ONE_SEED_FAMILY__NO_INFERENTIAL_AUTHORITY",
            "CURRENT_STRONGEST_COMPARATOR_SET_CANNOT_CHECK",
            "NO_CAUSAL_COORDINATE_SEPARABILITY",
        ],
        "protected_source_disjoint_multi_family_terminal": "CANNOT_CHECK",
        "current_terminal": mechanics_terminal + "__" + comparative_terminal + "__PUBLIC_NONPROTECTED_ONE_SEED_FAMILY_ONLY",
    }
    write_json(Path(args.out), result)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="command", required=True)
    command = sub.add_parser("build-cases")
    command.add_argument("--archive", required=True)
    command.add_argument("--out", required=True)
    command.add_argument("--receipt", required=True)
    command.set_defaults(func=cmd_build_cases)
    command = sub.add_parser("run-systems")
    command.add_argument("--cases", required=True)
    command.add_argument("--aml-manifest", required=True)
    command.add_argument("--aml-output-dir", required=True)
    command.add_argument("--out", required=True)
    command.add_argument("--receipt", required=True)
    command.set_defaults(func=cmd_run_systems)
    command = sub.add_parser("freeze")
    for name in ["protocol", "script", "case-receipt", "prediction-receipt", "cases", "predictions", "rights", "aml-binding", "aml-manifest", "out"]:
        command.add_argument("--" + name, required=True)
    command.set_defaults(func=cmd_freeze)
    command = sub.add_parser("join-gold")
    command.add_argument("--cases", required=True)
    command.add_argument("--archive", required=True)
    command.add_argument("--out", required=True)
    command.add_argument("--receipt", required=True)
    command.set_defaults(func=cmd_join_gold)
    command = sub.add_parser("score")
    command.add_argument("--cases", required=True)
    command.add_argument("--predictions", required=True)
    command.add_argument("--gold", required=True)
    command.add_argument("--gold-receipt", required=True)
    command.add_argument("--out", required=True)
    command.set_defaults(func=cmd_score)
    return root


def main() -> None:
    args = parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
