#!/usr/bin/env python3
"""Run the once-only P3 V19 DeepOnto class-surface compatibility microgate.

This gate is deliberately narrower than a matcher execution.  It may load the
two public ontologies, inspect their class/annotation surfaces, and exercise
the asserted taxonomy operations required by BERTMap.  It must not train,
match, read the reference alignment, or score any output.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import stat
import sys
import time
import traceback
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / "PROTOCOL_V19.json"
PREFLIGHT = ROOT / "RUNTIME_PREFLIGHT_V19.json"
LOCK = ROOT / "ATTEMPT_LOCK_V19.json"
RESULT = ROOT / "RESULT_V19.json"
TERMINAL = ROOT / "TERMINAL_V19.txt"
SOURCE = ROOT / "inputs/SOURCE_BASE_BOUND_V19.rdf"
TARGET = ROOT / "inputs/TARGET_BASE_BOUND_V19.rdf"
UNIVERSE = ROOT / "UNIVERSE_MANIFEST_V19.json"
RDFS_LABEL = "http://www.w3.org/2000/01/rdf-schema#label"
OWL_THING = "http://www.w3.org/2002/07/owl#Thing"


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def regular(path: Path) -> bool:
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return False
    return stat.S_ISREG(mode) and not path.is_symlink()


def canonical_hash(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def ontology_receipt(onto: object, expected: list[str], namespace: str) -> dict[str, object]:
    raw_observed = sorted(str(value) for value in onto.owl_classes.keys())
    expected_set = set(expected)
    raw_surface_pass = raw_observed == sorted(expected + [OWL_THING])
    removed = onto.owl_classes.pop(OWL_THING, None)
    observed = sorted(str(value) for value in onto.owl_classes.keys())
    class_identity_pass = removed is not None and observed == sorted(expected)

    annotation_index, annotation_properties = onto.build_annotation_index(
        annotation_property_iris=[RDFS_LABEL],
        apply_lowercasing=True,
    )
    annotations = {
        str(class_iri): sorted(str(value) for value in values)
        for class_iri, values in sorted(annotation_index.items())
    }
    expected_local = sorted(class_iri for class_iri in expected if class_iri.startswith(namespace + "#"))
    annotation_keys = sorted(annotations)
    nonempty_annotation_keys = sorted(class_iri for class_iri, values in annotations.items() if values)
    empty_annotation_keys = sorted(class_iri for class_iri, values in annotations.items() if not values)
    expected_empty = sorted(class_iri for class_iri in expected if not class_iri.startswith(namespace + "#"))
    annotation_pass = (
        annotation_properties == [RDFS_LABEL]
        and annotation_keys == sorted(expected)
        and nonempty_annotation_keys == expected_local
        and empty_annotation_keys == expected_empty
    )

    parents: dict[str, list[str]] = {}
    children: dict[str, list[str]] = {}
    for class_iri in expected:
        owl_class = onto.get_owl_object(class_iri)
        parents[class_iri] = sorted(
            str(value.getIRI()) for value in onto.get_asserted_parents(owl_class, named_only=True)
        )
        children[class_iri] = sorted(
            str(value.getIRI()) for value in onto.get_asserted_children(owl_class, named_only=True)
        )

    sibling_groups = sorted(
        (sorted(str(value) for value in group) for group in onto.sibling_class_groups),
        key=lambda values: (len(values), values),
    )
    taxonomy_members = {
        value
        for mapping in (parents, children)
        for values in mapping.values()
        for value in values
    }
    taxonomy_members.update(value for group in sibling_groups for value in group)
    taxonomy_pass = taxonomy_members.issubset(expected_set)

    consistency = bool(onto.check_consistency())
    return {
        "reasoner_type": str(onto.reasoner_type),
        "raw_class_count": len(raw_observed),
        "raw_expected_class_count": len(expected) + 1,
        "raw_surface_is_frozen_universe_plus_owl_thing": raw_surface_pass,
        "raw_observed_class_iris_sha256": canonical_hash(raw_observed),
        "removed_builtin": OWL_THING if removed is not None else None,
        "underlying_ontology_axioms_modified": False,
        "class_count": len(observed),
        "expected_class_count": len(expected),
        "class_identity_pass": class_identity_pass,
        "observed_class_iris_sha256": canonical_hash(observed),
        "annotation_property_iris": [str(value) for value in annotation_properties],
        "annotation_class_count": len(annotation_keys),
        "expected_annotation_class_count": len(expected),
        "nonempty_annotation_class_count": len(nonempty_annotation_keys),
        "expected_nonempty_annotation_class_count": len(expected_local),
        "empty_annotation_class_count": len(empty_annotation_keys),
        "expected_empty_annotation_class_count": len(expected_empty),
        "annotation_surface_pass": annotation_pass,
        "annotation_index_sha256": canonical_hash(annotations),
        "asserted_parent_map_sha256": canonical_hash(parents),
        "asserted_child_map_sha256": canonical_hash(children),
        "sibling_group_count": len(sibling_groups),
        "sibling_groups_sha256": canonical_hash(sibling_groups),
        "taxonomy_members_within_frozen_universe": taxonomy_pass,
        "structural_consistency_operation": consistency,
        "pass": (
            str(onto.reasoner_type) == "struct"
            and raw_surface_pass
            and class_identity_pass
            and annotation_pass
            and taxonomy_pass
            and consistency
        ),
    }


def main() -> int:
    if any(path.exists() for path in (PREFLIGHT, LOCK, RESULT, TERMINAL)):
        raise SystemExit("REFUSE_RERUN_OR_STALE_V19_ARTIFACT")

    protocol = json.loads(PROTOCOL.read_text())
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object = None) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})

    check("runner_identity", sha256(Path(__file__)) == protocol["frozen_code"]["runner_sha256"])
    for name, spec in protocol["frozen_inputs"].items():
        path = Path(spec["path"])
        check(f"input_{name}", regular(path) and path.stat().st_size == spec["bytes"] and sha256(path) == spec["sha256"])
    for name, spec in protocol["runtime"]["critical_files"].items():
        path = Path(spec["path"])
        check(f"runtime_{name}", regular(path) and path.stat().st_size == spec["bytes"] and sha256(path) == spec["sha256"])
    check("python_version", sys.version.split()[0] == protocol["runtime"]["python_version"], sys.version.split()[0])
    check("reasoner_type_frozen", protocol["reasoner_type"] == "struct")
    check("reference_path_absent", "reference" not in json.dumps(protocol).lower())
    check("training_matching_scoring_forbidden", not any(protocol["forbidden_operations"].values()))
    authorized = all(item["pass"] for item in checks)
    preflight = {
        "schema_version": "orion.p3.deeponto-class-surface.preflight.v19",
        "evaluated_at_utc": now(),
        "protocol_sha256": sha256(PROTOCOL),
        "checks_passed": sum(item["pass"] for item in checks),
        "checks_total": len(checks),
        "checks": checks,
        "microgate_authorized": authorized,
        "terminal": "P3_V19_CLASS_SURFACE_MICROGATE_PREFLIGHT_PASS" if authorized else "P3_V19_CLASS_SURFACE_MICROGATE_PREFLIGHT_FAIL",
    }
    PREFLIGHT.write_text(json.dumps(preflight, indent=2, sort_keys=True) + "\n")
    if not authorized:
        TERMINAL.write_text(preflight["terminal"] + "\n")
        return 1

    started = now()
    LOCK.write_text(
        json.dumps(
            {
                "schema_version": "orion.p3.deeponto-class-surface.attempt-lock.v19",
                "protocol_sha256": sha256(PROTOCOL),
                "preflight_sha256": sha256(PREFLIGHT),
                "started_at_utc": started,
                "attempts": 1,
                "retries": 0,
                "reasoner_type": "struct",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    universe = json.loads(UNIVERSE.read_text())
    source_expected = list(universe["expected_source_iris"])
    target_expected = list(universe["expected_target_iris"])
    start_ns = time.monotonic_ns()
    error: dict[str, object] | None = None
    source_receipt: dict[str, object] | None = None
    target_receipt: dict[str, object] | None = None
    try:
        # Imported only after the immutable attempt lock is written because this
        # import starts the JVM and therefore belongs to the single attempt.
        from deeponto.onto import Ontology

        source_onto = Ontology(str(SOURCE), reasoner_type="struct")
        target_onto = Ontology(str(TARGET), reasoner_type="struct")
        source_receipt = ontology_receipt(
            source_onto,
            source_expected,
            "http://co4.inrialpes.fr/align/Contest/101/onto.rdf",
        )
        target_receipt = ontology_receipt(
            target_onto,
            target_expected,
            "http://co4.inrialpes.fr/align/Contest/103/onto.rdf",
        )
    except BaseException as exc:
        error = {
            "type": f"{type(exc).__module__}.{type(exc).__qualname__}",
            "message": str(exc),
            "traceback": traceback.format_exc(),
        }

    wall_ns = time.monotonic_ns() - start_ns
    passed = (
        error is None
        and source_receipt is not None
        and target_receipt is not None
        and bool(source_receipt["pass"])
        and bool(target_receipt["pass"])
    )
    terminal = (
        "P3_V19_DEEPONTO_BUILTIN_CLASS_SURFACE_PASS__OWL_THING_EXACTLY_REMOVED_FROM_RUNTIME_INDEX__"
        "EXACT_36_BY_36_MATCHER_UNIVERSE_AND_33_BY_33_NONEMPTY_LABEL_SURFACE__V20_BERTMAP_FREEZE_AUTHORIZED"
        if passed
        else "P3_V19_DEEPONTO_BUILTIN_CLASS_SURFACE_FAIL__V20_BERTMAP_NOT_AUTHORIZED"
    )
    result = {
        "schema_version": "orion.p3.deeponto-class-surface.result.v19",
        "protocol_id": protocol["protocol_id"],
        "authority": "DEEPONTO_BUILTIN_CLASS_INDEX_FILTER_AND_STRUCTURAL_COMPATIBILITY_ONLY",
        "started_at_utc": started,
        "finished_at_utc": now(),
        "attempts": 1,
        "retries": 0,
        "reasoner_type": "struct",
        "wall_nanoseconds": wall_ns,
        "wall_seconds": wall_ns / 1_000_000_000,
        "source": source_receipt,
        "target": target_receipt,
        "error": error,
        "training_executed": False,
        "matching_executed": False,
        "reference_semantically_opened": False,
        "scoring_executed": False,
        "v20_full_bertmap_authorized": passed,
        "claim_boundary": protocol["claim_boundary"],
        "terminal": terminal,
    }
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    TERMINAL.write_text(terminal + "\n")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
