#!/usr/bin/env python3
"""Generate gold adjudicated annotations from the SEED manifest's gold hints.

The SEED manifest SAMPLE_MANIFEST_SEED_V1.json includes gold hint annotations
in the `notes` field for each sample.  This script converts those hints into
full structured gold annotations following ANNOTATION_SCHEMA_V1.json and writes
them to gold/adjudicated/ as final adjudicated gold records.

Usage:
    python3 generate_gold.py
    python3 generate_gold.py --manifest gold/SAMPLE_MANIFEST_SEED_V1.json
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GOLD_DIR = Path(__file__).resolve().parent
ADJUDICATED_DIR = GOLD_DIR / "adjudicated"
SCHEMA_PATH = GOLD_DIR.parent / "protocol" / "ANNOTATION_SCHEMA_V1.json"

# ── coordinate map: case_family → gold labels ───────────────────────────────
# These are derived from the SEED manifest notes field and follow the frozen
# annotation handbook annotation order (referent → construct → measurement →
# context → polarity → modality → attribution → discourse → mapping →
# contradiction → integration → recoverability).

GOLD_BY_CASE: dict[str, dict[str, Any]] = {
    "same_name_different_referent": {
        "referent_relation": "DIFFERENT",
        "construct_relation": "DIFFERENT",
        "measurement_relation": "NOT_APPLICABLE",
        "context_relation": "DIFFERENT_STATE_OR_TIME",
        "polarity_relation": "NOT_COMPARABLE",
        "modality_relation": "NOT_COMPARABLE",
        "attribution_relation": "NOT_APPLICABLE",
        "discourse_relation": "NOT_COMPARABLE",
        "mapping_relation": "NO_LICENSED_MAPPING",
        "preservation_conditions": [],
        "non_preserved_coordinates": ["referent", "construct", "context"],
        "contradiction_verdict": "NO_CONTRADICTION",
        "integration_verdict": "OBSTRUCTION",
        "recoverability_target": [
            "source_a.document_id",
            "source_b.document_id",
            "referent_relation:DIFFERENT",
            "mapping_relation:NO_LICENSED_MAPPING",
        ],
    },
    "different_name_same_referent": {
        "referent_relation": "SAME",
        "construct_relation": "SAME",
        "measurement_relation": "EQUIVALENT",
        "context_relation": "ALIGNED",
        "polarity_relation": "SAME",
        "modality_relation": "SAME",
        "attribution_relation": "SAME_SPEAKER_OR_SOURCE",
        "discourse_relation": "ALIGNED",
        "mapping_relation": "IDENTITY",
        "preservation_conditions": [
            "Canonical identifier mapping (e.g. gene ontology / synonym dictionary) is applied"
        ],
        "non_preserved_coordinates": [],
        "contradiction_verdict": "NO_CONTRADICTION",
        "integration_verdict": "GLUE_ALLOWED",
        "recoverability_target": [
            "source_a.document_id",
            "source_b.document_id",
            "referent_relation:SAME",
            "mapping_relation:IDENTITY",
            "preservation_conditions:canonical_mapping",
        ],
    },
    "same_construct_different_measurement": {
        "referent_relation": "SAME",
        "construct_relation": "SAME",
        "measurement_relation": "NON_EQUIVALENT",
        "context_relation": "CONDITIONED_COMPATIBLE",
        "polarity_relation": "SAME",
        "modality_relation": "SAME",
        "attribution_relation": "SAME_SPEAKER_OR_SOURCE",
        "discourse_relation": "ALIGNED",
        "mapping_relation": "CONDITIONAL_TRANSFORM",
        "preservation_conditions": [
            "Calibration curve or bridging study required between measurement instruments",
            "Direct numeric comparison without calibration is invalid",
        ],
        "non_preserved_coordinates": ["measurement"],
        "contradiction_verdict": "NO_CONTRADICTION",
        "integration_verdict": "GLUE_ALLOWED",
        "recoverability_target": [
            "source_a.document_id",
            "source_b.document_id",
            "construct_relation:SAME",
            "measurement_relation:NON_EQUIVALENT",
            "preservation_conditions:calibration_required",
        ],
    },
    "same_entity_different_temporal_state": {
        "referent_relation": "SAME",
        "construct_relation": "SAME",
        "measurement_relation": "NON_EQUIVALENT",
        "context_relation": "DIFFERENT_STATE_OR_TIME",
        "polarity_relation": "SAME",
        "modality_relation": "SAME",
        "attribution_relation": "SAME_SPEAKER_OR_SOURCE",
        "discourse_relation": "CONTEXTUAL_DIFFERENCE",
        "mapping_relation": "CONDITIONAL_TRANSFORM",
        "preservation_conditions": [
            "Temporal state change is expected; values are not directly comparable without trend normalization",
            "Difference reflects temporal evolution, not contradiction",
        ],
        "non_preserved_coordinates": ["context", "measurement"],
        "contradiction_verdict": "NO_CONTRADICTION",
        "integration_verdict": "GLUE_ALLOWED",
        "recoverability_target": [
            "source_a.document_id",
            "source_b.document_id",
            "context_relation:DIFFERENT_STATE_OR_TIME",
            "contradiction_verdict:NO_CONTRADICTION",
            "preservation_conditions:temporal_context",
        ],
    },
    "polarity_modality_attribution_context": {
        "referent_relation": "SAME",
        "construct_relation": "SAME",
        "measurement_relation": "EQUIVALENT",
        "context_relation": "ALIGNED",
        "polarity_relation": "SAME",
        "modality_relation": "DIFFERENT_STRENGTH",
        "attribution_relation": "DIFFERENT_ATTRIBUTION",
        "discourse_relation": "ALIGNED",
        "mapping_relation": "SUBSUMPTION",
        "preservation_conditions": [
            "Modality and attribution differences are carried forward as metadata",
            "Asserted claim subsumes the hedged version",
        ],
        "non_preserved_coordinates": ["modality", "attribution"],
        "contradiction_verdict": "NO_CONTRADICTION",
        "integration_verdict": "GLUE_ALLOWED",
        "recoverability_target": [
            "source_a.document_id",
            "source_b.document_id",
            "modality_relation:DIFFERENT_STRENGTH",
            "attribution_relation:DIFFERENT_ATTRIBUTION",
            "contradiction_verdict:NO_CONTRADICTION",
        ],
    },
    "valid_invalid_representation_mapping": {
        "referent_relation": "SAME",
        "construct_relation": "RELATED_NOT_SAME",
        "measurement_relation": "TRANSFORMABLE_WITH_CONDITIONS",
        "context_relation": "CONDITIONED_COMPATIBLE",
        "polarity_relation": "SAME",
        "modality_relation": "SAME",
        "attribution_relation": "SAME_SPEAKER_OR_SOURCE",
        "discourse_relation": "ALIGNED",
        "mapping_relation": "CONDITIONAL_TRANSFORM",
        "preservation_conditions": [
            "Mapping is not bijective; some information is lost in each direction",
            "Dimension weighting / conversion factors must be specified",
        ],
        "non_preserved_coordinates": ["construct", "measurement"],
        "contradiction_verdict": "NO_CONTRADICTION",
        "integration_verdict": "GLUE_ALLOWED",
        "recoverability_target": [
            "source_a.document_id",
            "source_b.document_id",
            "mapping_relation:CONDITIONAL_TRANSFORM",
            "preservation_conditions:non_bijective",
            "non_preserved_coordinates:construct,measurement",
        ],
    },
    "valid_invalid_literature_bridge": {
        "referent_relation": "SAME",
        "construct_relation": "RELATED_NOT_SAME",
        "measurement_relation": "TRANSFORMABLE_WITH_CONDITIONS",
        "context_relation": "CONDITIONED_COMPATIBLE",
        "polarity_relation": "SAME",
        "modality_relation": "SAME",
        "attribution_relation": "SAME_SPEAKER_OR_SOURCE",
        "discourse_relation": "ALIGNED",
        "mapping_relation": "CONDITIONAL_TRANSFORM",
        "preservation_conditions": [
            "Bridge validity depends on transfer conditions (dose, exposure, outcome, timescale)",
            "Mechanism-to-application transfer requires explicit boundary conditions",
        ],
        "non_preserved_coordinates": ["context", "construct"],
        "contradiction_verdict": "NO_CONTRADICTION",
        "integration_verdict": "GLUE_ALLOWED",
        "recoverability_target": [
            "source_a.document_id",
            "source_b.document_id",
            "context_relation:CONDITIONED_COMPATIBLE",
            "mapping_relation:CONDITIONAL_TRANSFORM",
            "preservation_conditions:transfer_boundaries",
        ],
    },
    "genuine_plural_obstruction": {
        "referent_relation": "SAME",
        "construct_relation": "DIFFERENT",
        "measurement_relation": "NOT_APPLICABLE",
        "context_relation": "ALIGNED",
        "polarity_relation": "NOT_COMPARABLE",
        "modality_relation": "SAME",
        "attribution_relation": "DIFFERENT_ATTRIBUTION",
        "discourse_relation": "ALIGNED",
        "mapping_relation": "NO_LICENSED_MAPPING",
        "preservation_conditions": [],
        "non_preserved_coordinates": ["construct", "mapping"],
        "contradiction_verdict": "NO_CONTRADICTION",
        "integration_verdict": "PLURAL_VIEW",
        "recoverability_target": [
            "source_a.document_id",
            "source_b.document_id",
            "integration_verdict:PLURAL_VIEW",
            "construct_relation:DIFFERENT",
            "mapping_relation:NO_LICENSED_MAPPING",
        ],
    },
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def generate_annotation(
    sample: dict[str, Any],
    gold: dict[str, Any],
    annotator: str = "seed-to-gold-v1",
) -> dict[str, Any]:
    """Build a full annotation record from SEED manifest sample + gold template."""
    sid = sample["sample_id"]
    family = sample["case_family"]
    return {
        "schema_version": "orion.p3.annotation.v1",
        "annotation_id": f"{sid}.GOLD",
        "case_id": sid,
        "annotator_id": annotator,
        "annotation_round": "ADJUDICATION",
        "source_a": {
            "document_id": sample["source_a"]["document_id"],
            "document_version": sample["source_a"]["document_version"],
            "span_start": sample["source_a"]["span_start"],
            "span_end": sample["source_a"]["span_end"],
            "text_hash": sample["source_a"]["text_hash"],
            "discipline": sample["source_a"]["discipline"],
        },
        "source_b": {
            "document_id": sample["source_b"]["document_id"],
            "document_version": sample["source_b"]["document_version"],
            "span_start": sample["source_b"]["span_start"],
            "span_end": sample["source_b"]["span_end"],
            "text_hash": sample["source_b"]["text_hash"],
            "discipline": sample["source_b"]["discipline"],
        },
        "referent_relation": gold["referent_relation"],
        "construct_relation": gold["construct_relation"],
        "measurement_relation": gold["measurement_relation"],
        "context_relation": gold["context_relation"],
        "polarity_relation": gold["polarity_relation"],
        "modality_relation": gold["modality_relation"],
        "attribution_relation": gold["attribution_relation"],
        "discourse_relation": gold["discourse_relation"],
        "mapping_relation": gold["mapping_relation"],
        "preservation_conditions": gold["preservation_conditions"],
        "non_preserved_coordinates": gold["non_preserved_coordinates"],
        "contradiction_verdict": gold["contradiction_verdict"],
        "integration_verdict": gold["integration_verdict"],
        "recoverability_target": gold["recoverability_target"],
        "confidence": 1.0,
        "rationale": (
            f"Gold annotation for {family} case {sid}. "
            f"referent={gold['referent_relation']}, "
            f"construct={gold['construct_relation']}, "
            f"measurement={gold['measurement_relation']}, "
            f"context={gold['context_relation']}, "
            f"mapping={gold['mapping_relation']}, "
            f"integration={gold['integration_verdict']}. "
            f"Seed manifest notes: {sample.get('notes', 'N/A')}"
        ),
        "specialist_domain_required": sample.get("specialist_domain_required", False),
        "annotated_at": _now_iso(),
    }


def main() -> int:
    ADJUDICATED_DIR.mkdir(parents=True, exist_ok=True)

    manifest_path = GOLD_DIR / "SAMPLE_MANIFEST_SEED_V1.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    samples = payload["samples"]

    generated = []
    errors = 0
    for s in samples:
        family = s["case_family"]
        if family not in GOLD_BY_CASE:
            print(f"ERROR: no gold template for case_family {family!r}", file=sys.stderr)
            errors += 1
            continue
        gold = generate_annotation(s, GOLD_BY_CASE[family])
        sid = s["sample_id"]
        out_path = ADJUDICATED_DIR / f"{sid}.gold.json"
        out_path.write_text(json.dumps(gold, indent=2, default=str) + "\n", encoding="utf-8")
        generated.append(sid)
        print(f"  ✓ {sid} → {out_path.name}")

    # Validate all generated annotations against schema
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    required = schema["required"]
    print(f"\nSchema requires {len(required)} fields: {required}")
    for sid in generated:
        rec = json.loads(
            (ADJUDICATED_DIR / f"{sid}.gold.json").read_text(encoding="utf-8")
        )
        missing = [f for f in required if f not in rec]
        if missing:
            print(f"  ✗ {sid} missing: {missing}")
            errors += 1
        else:
            # Check enum values
            props = schema["properties"]
            coord_issues = []
            for coord_name, coord_spec in props.items():
                if "enum" in coord_spec and coord_name in rec:
                    if rec[coord_name] not in coord_spec["enum"]:
                        coord_issues.append(
                            f"{coord_name}={rec[coord_name]!r} (not in {coord_spec['enum']})"
                        )
            if coord_issues:
                print(f"  ✗ {sid} enum issues: {coord_issues}")
                errors += 1

    print(f"\n{'='*50}")
    print(f"Generated: {len(generated)} gold annotations")
    print(f"Errors:    {errors}")
    print(f"Output:    {ADJUDICATED_DIR}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())