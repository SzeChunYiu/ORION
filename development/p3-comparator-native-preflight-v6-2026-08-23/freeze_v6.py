#!/usr/bin/env python3
"""Freeze outcome-blind smoke inputs and comparator-native success rules before execution."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parent
SHARED = ROOT.parents[0]


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(name: str, obj) -> None:
    (ROOT / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


SOURCE = """<?xml version="1.0"?>
<rdf:RDF xmlns="urn:orion:p3:v6:smoke:source#"
     xml:base="urn:orion:p3:v6:smoke:source"
     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
     xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
     xmlns:owl="http://www.w3.org/2002/07/owl#">
  <owl:Ontology rdf:about="urn:orion:p3:v6:smoke:source"/>
  <owl:Class rdf:about="urn:orion:p3:v6:smoke:source#Alpha"><rdfs:label xml:lang="en">alpha entity</rdfs:label></owl:Class>
  <owl:Class rdf:about="urn:orion:p3:v6:smoke:source#Beta"><rdfs:label xml:lang="en">beta entity</rdfs:label><rdfs:subClassOf rdf:resource="urn:orion:p3:v6:smoke:source#Alpha"/></owl:Class>
  <owl:Class rdf:about="urn:orion:p3:v6:smoke:source#Gamma"><rdfs:label xml:lang="en">gamma entity</rdfs:label><rdfs:subClassOf rdf:resource="urn:orion:p3:v6:smoke:source#Alpha"/></owl:Class>
</rdf:RDF>
"""

TARGET = """<?xml version="1.0"?>
<rdf:RDF xmlns="urn:orion:p3:v6:smoke:target#"
     xml:base="urn:orion:p3:v6:smoke:target"
     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
     xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
     xmlns:owl="http://www.w3.org/2002/07/owl#">
  <owl:Ontology rdf:about="urn:orion:p3:v6:smoke:target"/>
  <owl:Class rdf:about="urn:orion:p3:v6:smoke:target#Alpha"><rdfs:label xml:lang="en">alpha entity</rdfs:label></owl:Class>
  <owl:Class rdf:about="urn:orion:p3:v6:smoke:target#Beta"><rdfs:label xml:lang="en">beta entity</rdfs:label><rdfs:subClassOf rdf:resource="urn:orion:p3:v6:smoke:target#Alpha"/></owl:Class>
  <owl:Class rdf:about="urn:orion:p3:v6:smoke:target#Gamma"><rdfs:label xml:lang="en">gamma entity</rdfs:label><rdfs:subClassOf rdf:resource="urn:orion:p3:v6:smoke:target#Alpha"/></owl:Class>
</rdf:RDF>
"""


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    (ROOT / "SMOKE_SOURCE_V6.owl").write_text(SOURCE)
    (ROOT / "SMOKE_TARGET_V6.owl").write_text(TARGET)
    inherited = {
        "v3_comparator_identity": SHARED / "p3-cross-construct-successor" / "COMPARATOR_IDENTITY_AUDIT_V3.json",
        "v4_result": SHARED / "p3-selective-envelope-harm-successor-v4" / "RESULT_V4.json",
        "v5_result": SHARED / "p3-authoritative-negative-semantics-v5" / "RESULT_V5.json",
        "v5_adapters": SHARED / "p3-authoritative-negative-semantics-v5" / "COMPARATOR_ADAPTERS_V5.json",
    }
    protocol = {
        "schema_version": "orion.p3.comparator-native-preflight.protocol.v6",
        "protocol_id": "P3_V6_OUTCOME_BLIND_NATIVE_ARTIFACT_PREFLIGHT",
        "frozen_at": now(),
        "authority": "RUNTIME_AND_NATIVE_ARTIFACT_PREFLIGHT_ONLY__NO_PERFORMANCE_OR_SCIENTIFIC_OUTCOME_AUTHORITY",
        "inherited_bindings": {key: {"path": str(path), "sha256": sha(path)} for key, path in inherited.items()},
        "preserved_terminals": {
            "v3": "PUBLIC_V3_MAXIMAL_BINARY_ENVELOPE_COVERAGE_PASS__PUBLIC_V3_NO_HARM_SUPERIORITY__PUBLIC_NONPROTECTED_ONE_SEED_FAMILY_ONLY",
            "v4_source_admission": "0/7",
            "v4_comparator_readiness": "0/3",
            "v5_family_admission": "3/3_DIRECT_CERTIFICATE_CALIBRATION_ONLY",
            "v5_comparator_readiness": "0/3",
        },
        "inputs": {
            "source": {"path": "SMOKE_SOURCE_V6.owl", "sha256": sha(ROOT / "SMOKE_SOURCE_V6.owl"), "named_classes": 3},
            "target": {"path": "SMOKE_TARGET_V6.owl", "sha256": sha(ROOT / "SMOKE_TARGET_V6.owl"), "named_classes": 3},
            "construction": "Two synthetic, separately named ontology views with parallel three-class hierarchies and labels; no mapping reference, negative label, disjointness, evaluation row, or protected datum is supplied.",
            "gold_or_reference_alignment": None,
        },
        "global_rules": {
            "outcome_blind": True,
            "network": "Allowed only while staging exact source, dependency and model bytes. Matcher execution receives local ontology paths and no reference alignment; any matcher-time network requirement is a CANNOT_CHECK blocker.",
            "prediction_interpretation": "Native rows are validated structurally but not scored. Row presence is not treated as correctness; row absence is not obstruction.",
            "success": "The pinned native entrypoint completes within its budget and every prospectively required native artifact exists, is non-partial, parses under the frozen parser, and receives a SHA-256 digest.",
            "failure": "Build, dependency, model, runtime, timeout, nonzero process, missing/partial/invalid artifact, or matcher-time network dependency is CANNOT_CHECK for that slot; never an empty alignment or negative outcome.",
            "raw_or_large_retention": "Temporary sources, dependency caches, models, logs and raw native outputs are deleted after hashes, byte counts, parser counts and bounded failure excerpts are recorded.",
        },
        "slots": {
            "K1_AML": {
                "identity": "AML v3.2",
                "repository": "https://github.com/AgreementMakerLight/AML-Project",
                "commit": "d54a6650818d3474fe36090c2bc7dfe5bf4dfcb6",
                "release_asset": "https://github.com/AgreementMakerLight/AML-Project/releases/download/v3.2/AML_v3.2.zip",
                "expected_release_sha256": "7855c2d8efa131f012595313814a6466ad48f4e7ba26906c4f54801cd5a21f27",
                "expected_jar_sha256": "a5b831a6c000e49aa4702b16486dabdf38e40bb68203a16a8019414fecc2ecf3",
                "licence": "Apache-2.0",
                "entrypoint": "java -jar AgreementMakerLight.jar -s SOURCE -t TARGET -o OUTPUT -a",
                "budget": {"wall_seconds": 300, "cpu_threads_requested": 1, "max_heap": "2G", "retries": 0},
                "required_native_artifacts": ["declared AML alignment RDF/XML"],
                "parser": "XML parse plus Alignment/Cell count; declared output must exist even when cell count is zero",
            },
            "K2_LOGMAP": {
                "identity": "LogMap 4.0 source",
                "repository": "https://github.com/ernestojimenezruiz/logmap-matcher",
                "commit": "b3b57d0d8bfb5872bdffb49329d764acb4735713",
                "licence": "Apache-2.0",
                "mode": "MATCHER",
                "forbidden_modes": ["EVALUATION", "MATCHER-BIO"],
                "entrypoint": "java -Xms256M -Xmx2G -DentityExpansionLimit=10000000 --add-opens=java.base/java.lang=ALL-UNNAMED -jar logmap-matcher-4.0.jar MATCHER SOURCE_URI TARGET_URI OUTPUT_DIRECTORY false",
                "budget": {"wall_seconds": 600, "cpu_threads_requested": 1, "max_heap": "2G", "retries": 0},
                "required_native_artifacts": ["logmap_mappings.rdf"],
                "parser": "XML parse plus Alignment/Cell relation/type/confidence structural validation; expected artifact required because LogMap can catch exceptions without a failing exit code",
            },
            "K3_BERTMAP": {
                "identity": "BERTMap via DeepOnto 0.9.3",
                "repository": "https://github.com/KRR-Oxford/DeepOnto",
                "commit": "74ca8d47f01bad0b8739f19ee2c392bdf6d9c090",
                "package_version": "0.9.3",
                "licence": "Apache-2.0",
                "pretrained_model": "emilyalsentzer/Bio_ClinicalBERT",
                "pretrained_revision": "d5892b39a4adaed74b92212a44081509db72f87b",
                "pretrained_model_lfs_sha256": "a18c4c260fb5c0978b86658615106d5617050b5f14dac6ceb5e0d8beb2f9f719",
                "entrypoint": "python scripts/bertmap.py -s SOURCE -t TARGET -c FROZEN_CONFIG.yaml",
                "no_gold": {"known_mappings": None, "auxiliary_ontos": [], "reference_alignment": None},
                "thresholds": {"mapping_extension_threshold": 0.9, "mapping_filtered_threshold": 0.9995},
                "budget": {"wall_seconds": 1800, "cpu_threads_requested": 1, "device": "cpu", "retries": 0},
                "required_native_artifacts": [
                    "bertmap/match/raw_mappings.json",
                    "bertmap/match/raw_mappings.tsv",
                    "bertmap/match/extended_mappings.tsv",
                    "bertmap/match/filtered_mappings.tsv",
                    "bertmap/match/repaired_mappings.tsv",
                ],
                "parser": "JSON object and TSV row-shape validation with completion evidence; resumable or checkpoint-only partial files fail",
            },
        },
        "forbidden": [
            "opening any gold or reference alignment",
            "performance, harm, coverage, superiority or transport scoring",
            "tuning from native smoke rows",
            "interpreting nonselection as obstruction",
            "protected outcome access",
            "relaxing the three-family V5 gate",
        ],
    }
    dump("PROTOCOL_V6.json", protocol)
    receipt = {
        "schema_version": "orion.p3.comparator-native-preflight.freeze-receipt.v6",
        "created_at": now(),
        "protocol_sha256": sha(ROOT / "PROTOCOL_V6.json"),
        "source_input_sha256": protocol["inputs"]["source"]["sha256"],
        "target_input_sha256": protocol["inputs"]["target"]["sha256"],
        "comparator_outputs_opened": False,
        "gold_or_reference_opened": False,
        "protected_outcomes_opened": False,
        "status": "FROZEN_BEFORE_COMPARATOR_BUILD_OR_EXECUTION",
    }
    dump("PROTOCOL_FREEZE_RECEIPT_V6.json", receipt)
    print(receipt["protocol_sha256"])


if __name__ == "__main__":
    main()
