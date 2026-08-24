#!/usr/bin/env python3
"""Freeze a source-justified BERTMap smoke-size amendment before any K3 execution."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parent
RUNTIME = ROOT.parents[1] / ".p3v6-runtime"


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def owl(side: str) -> str:
    base = f"urn:orion:p3:v6:bertmap-smoke:{side}"
    rows = []
    for i in range(16):
        parent = "" if i == 0 else f'<rdfs:subClassOf rdf:resource="{base}#Class00"/>'
        rows.append(
            f'  <owl:Class rdf:about="{base}#Class{i:02d}"><rdfs:label xml:lang="en">semantic unit {i:02d}</rdfs:label>{parent}</owl:Class>'
        )
    return "\n".join(
        [
            '<?xml version="1.0"?>',
            f'<rdf:RDF xmlns="{base}#" xml:base="{base}"',
            ' xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"',
            ' xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"',
            ' xmlns:owl="http://www.w3.org/2002/07/owl#">',
            f'  <owl:Ontology rdf:about="{base}"/>',
            *rows,
            '</rdf:RDF>',
            '',
        ]
    )


def main() -> None:
    source = ROOT / "BERTMAP_SMOKE_SOURCE_V6.owl"
    target = ROOT / "BERTMAP_SMOKE_TARGET_V6.owl"
    source.write_text(owl("source"))
    target.write_text(owl("target"))
    model_path = RUNTIME / "Bio_ClinicalBERT-d5892b39"
    output_path = RUNTIME / "results" / "bertmap-out"
    config = ROOT / "BERTMAP_SMOKE_CONFIG_V6.yaml"
    config.write_text(
        f"""model: bertmap
output_path: {output_path}
annotation_property_iris:
  - http://www.w3.org/2000/01/rdf-schema#label
known_mappings: null
auxiliary_ontos: []
bert:
  pretrained_path: {model_path}
  max_length_for_input: 128
  num_epochs_for_training: 3.0
  batch_size_for_training: 1
  batch_size_for_prediction: 16
  resume_training: null
global_matching:
  enabled: true
  num_raw_candidates: 200
  num_best_predictions: 10
  mapping_extension_threshold: 0.9
  mapping_filtered_threshold: 0.9995
  for_oaei: false
"""
    )
    src = RUNTIME / "deeponto-src" / "src" / "deeponto" / "align" / "bertmap"
    amendment = {
        "schema_version": "orion.p3.comparator-native-preflight.k3-input-amendment.v6",
        "created_at": now(),
        "base_protocol_sha256": sha(ROOT / "PROTOCOL_V6.json"),
        "scope": "K3_BERTMAP_SMOKE_INPUT_SIZE_AND_BATCH_ONLY",
        "timing": "Frozen after source inspection and before any K3 environment execution, model load, training, prediction, or native output access.",
        "source_only_reason": (
            "Pinned DeepOnto computes logging_steps=int(floor(training_rows/batch_size)*0.02) and eval_steps=10*logging_steps. "
            "The original three-class smoke corpus cannot make these positive under batch 32, so the native Trainer contract is structurally invalid before model outcomes."
        ),
        "source_evidence": {
            "commit": "74ca8d47f01bad0b8739f19ee2c392bdf6d9c090",
            "bert_classifier_path": "src/deeponto/align/bertmap/bert_classifier.py",
            "bert_classifier_sha256": sha(src / "bert_classifier.py"),
            "line_anchor": "100-124",
            "text_semantics_path": "src/deeponto/align/bertmap/text_semantics.py",
            "text_semantics_sha256": sha(src / "text_semantics.py"),
            "line_anchor_corpus": "287-344 and 487-578",
        },
        "amended_inputs": {
            "source": {"path": source.name, "sha256": sha(source), "named_classes": 16},
            "target": {"path": target.name, "sha256": sha(target), "named_classes": 16},
            "construction": "Synthetic parallel labels/hierarchies only; no mappings, disjointness, truth, gold, reference, protected row, or task outcome.",
        },
        "config": {
            "path": config.name,
            "sha256": sha(config),
            "known_mappings": None,
            "auxiliary_ontos": [],
            "annotation_properties": ["http://www.w3.org/2000/01/rdf-schema#label"],
            "epochs": 3.0,
            "training_batch": 1,
            "prediction_batch": 16,
            "thresholds_unchanged": {"extension": 0.9, "filter": 0.9995},
        },
        "success_boundary": "Only complete native smoke pipeline readiness. The amended input/config cannot establish performance, transport, superiority, harm, reproducibility, or V5-frame execution readiness.",
    }
    (ROOT / "PROTOCOL_K3_INPUT_AMENDMENT_V6.json").write_text(json.dumps(amendment, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema_version": "orion.p3.comparator-native-preflight.k3-input-amendment-freeze.v6",
        "created_at": now(),
        "amendment_sha256": sha(ROOT / "PROTOCOL_K3_INPUT_AMENDMENT_V6.json"),
        "k3_outputs_opened": False,
        "gold_or_reference_opened": False,
        "protected_outcomes_opened": False,
        "status": "FROZEN_BEFORE_K3_EXECUTION",
    }
    (ROOT / "PROTOCOL_K3_INPUT_AMENDMENT_FREEZE_V6.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
