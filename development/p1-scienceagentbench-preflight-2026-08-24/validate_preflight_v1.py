#!/usr/bin/env python3
"""Static, network-free validator for the P1 ScienceAgentBench preflight."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXPECTED_EXCEPTIONS = {
    "3": "MATMINER_UPSTREAM_TERMS",
    "32": "RASTERIO_UPSTREAM_TERMS",
    "46": "RASTERIO_UPSTREAM_TERMS",
    "53": "RASTERIO_UPSTREAM_TERMS",
    "54": "RASTERIO_UPSTREAM_TERMS",
    "84": "RASTERIO_UPSTREAM_TERMS",
}
EXPECTED_DOMAINS = {
    "Bioinformatics": 27,
    "Computational Chemistry": 20,
    "Geographical Information Science": 27,
    "Psychology and Cognitive science": 28,
}


def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def digest(name: str) -> str:
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()


def main() -> None:
    mask = load("MASK_MANIFEST_V1.json")
    protocol = load("PROTOCOL_DESIGN_V0.json")
    receipt = load("PREFLIGHT_RECEIPT_V1.json")

    assert mask["schema_version"] == "orion.p1.scienceagentbench.mask-manifest.v1"
    assert mask["outcomes_opened"] is False
    assert mask["scientific_authority_delta"] == "NONE"
    assert mask["source"]["split"] == "verified"
    assert mask["source"]["revision"] == "9c6e96c9e74572e979b0930ee735041cef528cb7"
    records = mask["records"]
    assert len(records) == 102
    assert [record["instance_id"] for record in records] == [str(i) for i in range(1, 103)]
    assert Counter(record["domain"] for record in records) == Counter(EXPECTED_DOMAINS)

    observed_exceptions = {
        record["instance_id"]: record["license_partition"]
        for record in records
        if record["license_partition"] != "CC-BY-4.0_DEFAULT_TASK_PARTITION"
    }
    assert observed_exceptions == EXPECTED_EXCEPTIONS
    assert sum(
        record["license_partition"] == "CC-BY-4.0_DEFAULT_TASK_PARTITION"
        for record in records
    ) == 96

    expected_fields = {
        "task_inst",
        "output_fname",
        "domain_knowledge",
        "dataset_folder_tree",
        "dataset_preview",
    }
    for record in records:
        assert set(record["fields"]) == expected_fields
        # The committed mask manifest binds source text by digest only. It must
        # never vendor upstream task instructions, previews or knowledge text.
        for descriptor in record["fields"].values():
            assert set(descriptor) == {
                "state",
                "value_type",
                "canonical_json_bytes",
                "canonical_json_sha256",
            }
            assert len(descriptor["canonical_json_sha256"]) == 64
        binding = {
            "instance_id": record["instance_id"],
            "domain": record["domain"],
            "fields": record["fields"],
        }
        expected = hashlib.sha256(
            json.dumps(binding, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        assert record["binding_sha256"] == expected

    assert protocol["status"] == "MASK_FROZEN__MATCHED_ARM_AND_RUNTIME_BINDINGS_INCOMPLETE"
    assert protocol["outcomes_opened"] is False
    assert protocol["scientific_authority_delta"] == "NONE"
    assert protocol["source_population"]["split"] == "verified"
    assert protocol["source_population"]["task_count"] == 102
    assert [arm["arm_id"] for arm in protocol["candidate_arms"]] == ["RR", "OS", "NR"]
    assert protocol["source_population"]["mask_manifest"]["sha256"] == digest(
        "MASK_MANIFEST_V1.json"
    )

    assert receipt["inspection_boundary"]["official_or_historical_task_outcomes_opened"] is False
    assert receipt["inspection_boundary"]["tasks_executed"] == 0
    assert receipt["inspection_boundary"]["large_data_added_to_orion"] is False
    assert receipt["sources"]["verified_annotations"]["split"] == "verified"
    assert receipt["sources"]["verified_annotations"]["tasks"] == 102
    assert receipt["sources"]["full_verified_artifact"]["archive_payload_sha256"] is None
    assert receipt["official_evaluator_preflight"]["runtime_verified"] is False
    assert receipt["official_evaluator_preflight"]["required_evaluation_argument"] == "--split verified"
    assert receipt["protocol_feasibility"]["deterministic_mask_without_outcomes"]["verdict"] == "YES"
    assert receipt["protocol_feasibility"]["matched_arms_without_outcomes"]["verdict"] == "DESIGNABLE_BUT_NOT_YET_FROZEN"
    assert receipt["protocol_feasibility"]["deterministic_mask_without_outcomes"]["manifest_sha256"] == digest(
        "MASK_MANIFEST_V1.json"
    )
    assert receipt["protocol_feasibility"]["matched_arms_without_outcomes"]["protocol_sha256"] == digest(
        "PROTOCOL_DESIGN_V0.json"
    )
    assert [blocker["id"] for blocker in receipt["blockers"]] == [
        "PF-01",
        "PF-02",
        "PF-03",
        "PF-04",
        "PF-05",
        "PF-06",
    ]
    assert receipt["scientific_authority_delta"] == "NONE"
    assert receipt["terminal"].endswith("__ZERO_OUTCOMES_OPENED__ZERO_TASKS_RUN")

    print(
        "P1_SAB_PREFLIGHT_STATIC_VALIDATION_PASS "
        "tasks=102 exceptions=6 outcomes_opened=false tasks_run=0"
    )


if __name__ == "__main__":
    main()
