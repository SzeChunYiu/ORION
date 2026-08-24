#!/usr/bin/env python3
"""Outcome-blind base-IRI binding for the frozen OAEI 2004 test-103 pair.

The provider RDF/XML uses ``rdf:ID`` without an explicit ``xml:base``.  A
local-file loader would therefore mint file-scheme IRIs that cannot denote the
same pair universe as the public reference or AML output.  This adapter makes
the provider document IRIs explicit before matcher execution.  It never opens
the reference alignment.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path

from rdflib import Graph, OWL, RDF, URIRef
from rdflib.compare import isomorphic


ROOT = Path(__file__).resolve().parent
SPECS = {
    "source": {
        "input": ROOT / "inputs/SOURCE_PROVIDER_V17.rdf",
        "output": ROOT / "inputs/SOURCE_BASE_BOUND_V17.rdf",
        "base": "http://co4.inrialpes.fr/align/Contest/101/onto.rdf",
        "sha256": "d6143780103217a4a562e4982f0d4c724c09d3a3e7dc146a6b42cecc3e9f1064",
    },
    "target": {
        "input": ROOT / "inputs/TARGET_PROVIDER_V17.rdf",
        "output": ROOT / "inputs/TARGET_BASE_BOUND_V17.rdf",
        "base": "http://co4.inrialpes.fr/align/Contest/103/onto.rdf",
        "sha256": "e3643a6fcd237a162d120e58227df2e24e0398668c6f2428e4fea850180405cf",
    },
}
RECEIPT = ROOT / "BASE_IRI_ADAPTER_RECEIPT_V17.json"
UNIVERSE = ROOT / "UNIVERSE_MANIFEST_V17.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def graph(path: Path, public_id: str | None = None) -> Graph:
    value = Graph()
    value.parse(path, format="xml", publicID=public_id)
    return value


def bind(spec: dict[str, object]) -> dict[str, object]:
    input_path = Path(spec["input"])
    output_path = Path(spec["output"])
    base = str(spec["base"])
    if sha256(input_path) != spec["sha256"]:
        raise RuntimeError(f"provider input drift: {input_path}")
    if output_path.exists():
        raise RuntimeError(f"refuse overwrite: {output_path}")

    raw = input_path.read_bytes()
    anchor = b"<rdf:RDF\n"
    if raw.count(anchor) != 1 or b"xml:base=" in raw:
        raise RuntimeError(f"unexpected RDF/XML root shape: {input_path}")
    adapted = raw.replace(anchor, anchor + f' xml:base="{base}"\n'.encode("ascii"), 1)
    output_path.write_bytes(adapted)

    provider_semantics = graph(input_path, public_id=base)
    adapted_semantics = graph(output_path)
    if not isomorphic(provider_semantics, adapted_semantics):
        raise RuntimeError(f"base adapter changes provider-publicID semantics: {input_path}")

    classes = sorted(
        str(node)
        for node in adapted_semantics.subjects(RDF.type, OWL.Class)
        if isinstance(node, URIRef)
    )
    if len(classes) != 36 or len(classes) != len(set(classes)):
        raise RuntimeError(f"unexpected named-class universe: {len(classes)}")
    return {
        "provider_path": str(input_path),
        "provider_bytes": input_path.stat().st_size,
        "provider_sha256": sha256(input_path),
        "provider_public_id": base,
        "adapted_path": str(output_path),
        "adapted_bytes": output_path.stat().st_size,
        "adapted_sha256": sha256(output_path),
        "semantic_isomorphism_under_provider_public_id": True,
        "named_class_count": len(classes),
        "named_classes": classes,
    }


def main() -> int:
    if RECEIPT.exists() or UNIVERSE.exists():
        raise SystemExit("REFUSE_RERUN_OR_STALE_BASE_BINDING_ARTIFACT")
    rows = {role: bind(spec) for role, spec in SPECS.items()}
    universe = {
        "schema_version": "orion.p3.bertmap-universe-manifest.v7",
        "expected_source_iris": rows["source"]["named_classes"],
        "expected_target_iris": rows["target"]["named_classes"],
        "mapping_extension_threshold": "0.9",
        "mapping_filtered_threshold": "0.9995",
        "for_oaei": False,
        "excluded_source_iris": [],
    }
    UNIVERSE.write_text(json.dumps(universe, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema_version": "orion.p3.oaei-base-iri-adapter.receipt.v17",
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "authority": "OUTCOME_BLIND_PROVIDER_DOCUMENT_IRI_BINDING_ONLY__NO_REFERENCE_OR_MAPPING_OUTCOME_OPENED",
        "method": "insert one explicit xml:base equal to the provider document IRI; no other byte change",
        "inputs": rows,
        "universe_manifest": {
            "path": str(UNIVERSE),
            "sha256": sha256(UNIVERSE),
            "source_named_classes": len(universe["expected_source_iris"]),
            "target_named_classes": len(universe["expected_target_iris"]),
        },
        "reference_alignment_opened": False,
        "matcher_or_comparator_output_opened": False,
        "terminal": "P3_V17_PROVIDER_BASE_IRI_BINDING_PASS__SEMANTIC_ISOMORPHISM_UNDER_PUBLIC_DOCUMENT_IRI__THIRTY_SIX_BY_THIRTY_SIX_NAMED_CLASS_UNIVERSE_FROZEN",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["terminal"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
