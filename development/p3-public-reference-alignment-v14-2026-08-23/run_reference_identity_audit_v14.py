#!/usr/bin/env python3
"""Fail-closed identity audit for a public reference for the frozen V12/V13 pair."""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
TERMINAL = (
    "P3_V14_PROVIDER_NATIVE_REFERENCE_IDENTITY_CANNOT_CHECK__FROZEN_PAIR_IS_"
    "SYNTHETIC_AND_MATCHES_NO_OAEI_BIOML_CASE__NO_PUBLIC_GOLD_ADMITTED__NO_"
    "METRICS_OR_COMPARATOR_COMPUTED"
)

FILES = {
    "v6_input_amendment": ROOT / "p3-comparator-native-preflight-v6-2026-08-23" / "PROTOCOL_K3_INPUT_AMENDMENT_V6.json",
    "v13_result": ROOT / "p3-optional-wrapper-typed-decoder-v13-2026-08-23" / "RESULT_V13.json",
    "v13_receipt": ROOT / "p3-optional-wrapper-typed-decoder-v13-2026-08-23" / "RECEIPT_V13.json",
    "v13_decoded_mapping": ROOT / "p3-optional-wrapper-typed-decoder-v13-2026-08-23" / "runtime" / "decoded-match" / "repaired_mappings.tsv",
    "oaei_rights": ROOT / "p3-oaei-public-development-execution-2026-08-23" / "OAEI_RIGHTS_AND_ATTRIBUTION_RECEIPT_V1.json",
    "oaei_case_universe": ROOT / "p3-oaei-public-development-execution-2026-08-23" / "CASE_UNIVERSE_RECEIPT_V2.json",
    "oaei_public_gold_join_receipt": ROOT / "p3-oaei-public-development-execution-2026-08-23" / "PUBLIC_GOLD_JOIN_RECEIPT_V2.json",
    "source_rights_registry": ROOT / "p3-public-data-successor-2026-08-23" / "SOURCE_RIGHTS_REGISTRY_V1.json",
    "oaei_input_inventory": ROOT / "p3-public-data-successor-2026-08-23" / "OAEI_INPUT_INVENTORY_V1.jsonl",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def dump_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    started_wall = datetime.now(timezone.utc)
    started_ns = time.monotonic_ns()

    v6 = read_json(FILES["v6_input_amendment"])
    v13_result = read_json(FILES["v13_result"])
    v13_receipt = read_json(FILES["v13_receipt"])
    rights = read_json(FILES["oaei_rights"])
    cases = read_json(FILES["oaei_case_universe"])
    gold_join = read_json(FILES["oaei_public_gold_join_receipt"])
    registry = read_json(FILES["source_rights_registry"])
    inventory = [json.loads(line) for line in FILES["oaei_input_inventory"].read_text(encoding="utf-8").splitlines() if line]

    source = v6["amended_inputs"]["source"]
    target = v6["amended_inputs"]["target"]
    frozen_hashes = {source["sha256"], target["sha256"]}
    source_iri = "urn:orion:p3:v6:bertmap-smoke:source"
    target_iri = "urn:orion:p3:v6:bertmap-smoke:target"

    assert v6["amended_inputs"]["construction"] == (
        "Synthetic parallel labels/hierarchies only; no mappings, disjointness, truth, gold, reference, protected row, or task outcome."
    )
    assert source == {"named_classes": 16, "path": "BERTMAP_SMOKE_SOURCE_V6.owl", "sha256": "c347f32626f6c5b3b782b2f6344bca5ac2282a701161d11f1e02a7422fef4d9e"}
    assert target == {"named_classes": 16, "path": "BERTMAP_SMOKE_TARGET_V6.owl", "sha256": "16bd34ec22c3d130b94257404fd60a112a3383d16255a67472e0c5e1518c5521"}
    assert v13_receipt["real_decode"]["decoded_artifact"]["sha256"] == sha256(FILES["v13_decoded_mapping"])
    assert v13_receipt["real_decode"]["decoded_rows"] == 16
    assert v13_result["raw_v12_unchanged"]["unchanged"] is True
    assert rights["source_id"] == "OAEI_2004_ZENODO_15827226"
    assert rights["provider_checksum"] == "md5:31676c68912a22622f6ca6d031519df9"
    assert rights["license"] == "CC-BY-4.0"
    assert cases["public_reference_content_opened"] is False
    assert gold_join["authority"] == "PUBLIC_REFERENCE_ONLY__NOT_PROTECTED"

    ontology_hashes = sorted({m["member_sha256"] for m in cases["member_receipts"]})
    reference_members = gold_join.get("reference_members", [])
    reference_hashes = sorted({m["sha256"] for m in reference_members})
    registered_oaei = [s for s in registry["sources"] if s["donor_family"] == "OAEI"]
    registered_bioml = [s for s in registry["sources"] if "BIOML" in s["donor_family"].upper() or "BIO-ML" in s["donor_family"].upper()]

    assert frozen_hashes.isdisjoint(ontology_hashes)
    assert frozen_hashes.isdisjoint(reference_hashes)
    assert len(registered_oaei) == 1
    assert len(registered_bioml) == 0
    assert len(inventory) == 21
    assert {r["source_id"] for r in inventory} == {"OAEI_2004_ZENODO_15827226"}

    provider_receipt_text = "\n".join(
        FILES[k].read_text(encoding="utf-8")
        for k in ("oaei_rights", "oaei_case_universe", "oaei_public_gold_join_receipt", "source_rights_registry", "oaei_input_inventory")
    )
    provider_literal_hits = {
        source["sha256"]: provider_receipt_text.count(source["sha256"]),
        target["sha256"]: provider_receipt_text.count(target["sha256"]),
        source_iri: provider_receipt_text.count(source_iri),
        target_iri: provider_receipt_text.count(target_iri),
    }
    assert set(provider_literal_hits.values()) == {0}

    decoded_before = sha256(FILES["v13_decoded_mapping"])
    result = {
        "schema_version": "orion.p3.public-reference-identity-audit.v14",
        "protocol_id": "P3_V14_FROZEN_V12_V13_PROVIDER_NATIVE_REFERENCE_IDENTITY_AUDIT",
        "terminal": TERMINAL,
        "authority": "LOCAL_RECEIPT_BOUND_PROVIDER_IDENTITY_AUDIT_ONLY__PUBLIC_DEVELOPMENT_EVIDENCE__NOT_PROTECTED_CONFIRMATION",
        "frozen_pair": {
            "construction": v6["amended_inputs"]["construction"],
            "provider_native": False,
            "source": {**source, "ontology_iri": source_iri},
            "target": {**target, "ontology_iri": target_iri},
        },
        "v13_decoded_mapping": {
            "rows": 16,
            "sha256_before_v14": decoded_before,
            "sha256_after_v14": sha256(FILES["v13_decoded_mapping"]),
            "unchanged": decoded_before == sha256(FILES["v13_decoded_mapping"]),
            "raw_v12_unchanged_in_v13": True,
        },
        "provider_evidence": {
            "oaei_2004": {
                "source_id": rights["source_id"],
                "record": rights["record"],
                "doi": rights["doi"],
                "archive": rights["archive"],
                "provider_checksum": rights["provider_checksum"],
                "license": rights["license"],
                "conditions": rights["conditions"],
                "protected_authority": rights["protected_authority"],
                "inventory_units": len(inventory),
                "ontology_member_hashes_checked": len(ontology_hashes),
                "reference_member_hashes_checked": len(reference_hashes),
                "frozen_hash_match_count": sum(h in frozen_hashes for h in ontology_hashes + reference_hashes),
                "provider_literal_hits_for_frozen_hashes_and_iris": provider_literal_hits,
                "public_gold_join_gate_status": gold_join["gate_status"],
            },
            "bioml": {
                "status": "NOT_ADMITTED__NO_EXACT_BIOML_VERSION_RIGHTS_ONTOLOGY_HASH_AND_REFERENCE_HASH_RECORD_IN_FROZEN_PROVIDER_REGISTRY",
                "registered_records": len(registered_bioml),
            },
        },
        "admission": {
            "exact_provider_native_case_found": False,
            "reference_alignment_admitted": False,
            "gold_or_reference_file_opened_by_v14": False,
            "identity_by_equal_class_label_invented": False,
            "reason": "The frozen pair is locally constructed synthetic input, its hashes and IRIs match no admitted provider record, and no exact Bio-ML identity packet is present.",
        },
        "metrics": {"precision": "CANNOT_CHECK", "recall": "CANNOT_CHECK", "f1": "CANNOT_CHECK"},
        "same_universe_frozen_comparator": "CANNOT_CHECK",
        "claim_boundary": {
            "mapping_truth": "CANNOT_CHECK",
            "performance": "CANNOT_CHECK",
            "superiority": "CANNOT_CHECK",
            "protected_confirmation": "CANNOT_CHECK",
            "public_data_role": "DEVELOPMENT_EVIDENCE_ONLY",
        },
        "next_discriminator": "Run the already frozen matcher/decoder on a separately frozen provider-native ontology pair only after exact version, rights, ontology hashes, reference hash, and same-universe comparator identity are all admitted prospectively.",
    }

    dump_json(OUT / "RESULT_V14.json", result)
    (OUT / "TERMINAL_V14.txt").write_text(TERMINAL + "\n", encoding="utf-8")
    report = f"""# P3 V14 provider-native public-reference identity audit

**Terminal:** `{TERMINAL}`

## Result

The V12/V13 pair is not provider-native OAEI or Bio-ML data. It is a frozen local synthetic pair with ontology IRIs `{source_iri}` and `{target_iri}` and SHA-256 digests `{source['sha256']}` and `{target['sha256']}`. Its construction receipt explicitly says it contains no truth, gold, or reference.

The admitted OAEI 2004 provider packet is Zenodo record 15827226, DOI `{rights['doi']}`, archive `{rights['archive']}`, provider checksum `{rights['provider_checksum']}`, under `{rights['license']}` with attribution, DOI citation, and adaptation-notice conditions. The audit checked {len(ontology_hashes)} ontology-member hashes, {len(reference_hashes)} reference-member hashes, and {len(inventory)} input inventory units. None matches either frozen ontology hash, and none of the provider receipts contains either frozen ontology IRI. The registry contains no exact Bio-ML version/rights/ontology-hash/reference-hash identity packet.

Therefore V14 admitted no public gold or reference file and did not invent an identity-by-equal-label alignment. Precision, recall, and F1 are `CANNOT_CHECK`; a same-universe frozen comparator is also `CANNOT_CHECK`. The pre-existing OAEI public data remains development evidence, not protected confirmation.

## Preservation

The V13 decoded mapping remains unchanged: 16 rows, SHA-256 `{decoded_before}`. Raw V12 was recorded unchanged by V13. V14 performed no training, matcher execution, Java execution, downloads, retry, tuning, scientific scoring, or comparator run.

## Efficient successor

Do not spend more compute on this synthetic pair for truth/performance metrics. The shortest valid next gate is a provider-native identity packet binding exact version, rights, both ontology hashes, reference hash, and comparator universe before one prospective matcher run.
"""
    (OUT / "SCIENTIFIC_REPORT_V14.md").write_text(report, encoding="utf-8")

    finished_ns = time.monotonic_ns()
    finished_wall = datetime.now(timezone.utc)
    receipt = {
        "schema_version": "orion.p3.public-reference-identity-receipt.v14",
        "protocol_id": result["protocol_id"],
        "terminal": TERMINAL,
        "success": True,
        "started_at": started_wall.isoformat(),
        "finished_at": finished_wall.isoformat(),
        "runtime_nanoseconds": finished_ns - started_ns,
        "runtime_seconds": (finished_ns - started_ns) / 1_000_000_000,
        "attempts": 1,
        "downloads": 0,
        "training_attempts": 0,
        "matcher_attempts": 0,
        "java_attempts": 0,
        "scientific_scoring_performed": False,
        "comparator_computed": False,
        "gold_or_reference_file_opened": False,
        "input_receipts": {k: {"path": str(p), "sha256": sha256(p)} for k, p in FILES.items() if k != "v13_decoded_mapping"},
        "preserved_mapping": {"path": str(FILES["v13_decoded_mapping"]), "sha256": decoded_before, "unchanged": True},
        "outputs": {
            name: {"path": str(OUT / name), "sha256": sha256(OUT / name)}
            for name in ("RESULT_V14.json", "SCIENTIFIC_REPORT_V14.md", "TERMINAL_V14.txt")
        },
    }
    dump_json(OUT / "RECEIPT_V14.json", receipt)

    names = ["RECEIPT_V14.json", "RESULT_V14.json", "SCIENTIFIC_REPORT_V14.md", "TERMINAL_V14.txt", "run_reference_identity_audit_v14.py"]
    (OUT / "SHA256SUMS").write_text("".join(f"{sha256(OUT / name)}  {name}\n" for name in names), encoding="utf-8")
    print(json.dumps({"terminal": TERMINAL, "runtime_seconds": receipt["runtime_seconds"], "receipt_sha256": sha256(OUT / "RECEIPT_V14.json"), "result_sha256": sha256(OUT / "RESULT_V14.json")}, sort_keys=True))


if __name__ == "__main__":
    main()
