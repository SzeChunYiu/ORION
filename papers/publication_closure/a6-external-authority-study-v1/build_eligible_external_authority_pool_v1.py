#!/usr/bin/env python3
"""Deterministically build the A6 EligibleExternalAuthorityPacketPool from the frozen census.

Consumes the three outcome-blind A6 census snapshots (chunk digests and
packet_candidate_rows_sha256 re-verified against each frozen census manifest)
plus the externally derived replication quota freeze, and emits an
ORION.A6.EligibleExternalAuthorityPacketPool.v1 payload for the frozen
allocator (allocate_external_authority_packets_v1.py, imported verbatim).

Eligibility is adjudicated from registry/metadata properties only: structural
completeness, the census-bound content route, open licensing and open access.
No ORION prediction, baseline or protected outcome exists at this stage and
none is read. The three derived receipts are custody/bindings, never sign-offs:

- external_custody_receipt_id binds the transition bytes to the external
  source coordinates that hold them (registry + family + versions + digests).
- adjudicator_assignment_receipt_id binds the packet to the frozen external
  adjudicator handoff contract queue. It stages the packet for external
  adjudication; it confers no authority and records no adjudication.
- candidate_visible_packet_sha256 hashes the canonical candidate-visible
  payload (target-relevant scientific coordinates + the terminal alphabet
  only), which is the exact substrate the external adjudicator receives.

Run-time resolution: none. Every emitted value is a verbatim copy of a
verified census field or a deterministic SHA-256 over verbatim values.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
POOL_SCHEMA = "ORION.A6.EligibleExternalAuthorityPacketPool.v1"
FREEZE_SCHEMA = "ORION.A6.ReplicationQuotaFreeze.v1"
HANDOFF_PATH = "A6_EXTERNAL_ADJUDICATOR_HANDOFF_V1.json"
VISIBLE_SCHEMA = "ORION.A6.CandidateVisiblePacket.v1"
GOLD_LABELS = ("local_action_release_authority", "scientific_discharge_admission_authority")
TERMINAL_ALPHABET = ["ADMIT", "DENY", "CANNOT_CHECK"]
STRATA = (
    "scientific_software_release_provenance_attestation",
    "workflowhub_rocrate_versioned_workflow",
    "scientific_record_transition",
)
CENSUS = {
    "scientific_software_release_provenance_attestation": ("zenodo-census-v1", "A6_STRATUM1_CENSUS_MANIFEST_V1.json"),
    "workflowhub_rocrate_versioned_workflow": ("workflowhub-census-v1", "A6_STRATUM2_CENSUS_MANIFEST_V1.json"),
    "scientific_record_transition": ("scientific-record-census-v1", "A6_STRATUM3_CENSUS_MANIFEST_V1.json"),
}
EXPECTED_PROVENANCE = {
    "scientific_software_release_provenance_attestation": ("A6_ZENODO_REST_PUBLIC_METADATA",),
    "workflowhub_rocrate_versioned_workflow": ("A3_FROZEN_FRAME_REUSE", "A6_FRESH_ROCRATE_BINDING"),
    "scientific_record_transition": ("A6_CROSSREF_ARTICLE_TO_DATACITE_SUPPLEMENT_PUBLIC_METADATA",),
}
ELIGIBILITY_RULES = {
    "E_COMMON_STRATUM_MATCH": "row stratum equals the frozen census manifest stratum",
    "E_COMMON_LINEAGE_TRIO_PRESENT": "source_family_id, normalized_organization_lineage, artifact_lineage_id all nonempty",
    "E_COMMON_VERSION_IDS_PRESENT": "before_version_id and after_version_id nonempty",
    "E_COMMON_TRANSITION_DIGESTS_HEX64": "before_sha256 and after_sha256 are lowercase 64-hex digests",
    "E_COMMON_TRANSITION_BYTES_DIFFER": "before_sha256 != after_sha256 (a real transition)",
    "E_COMMON_LICENSE_RECEIPT_PRESENT": "license_or_rights_receipt_id nonempty",
    "E_COMMON_PROVENANCE_BOUND": "content_binding_provenance matches the census-bound route for the stratum",
    "E_S1_ACCESS_RIGHT_OPEN": "stratum 1: Zenodo access_right == open",
    "E_S1_LICENSES_PRESENT": "stratum 1: license_before and license_after both nonempty (open-licensed transition)",
    "E_S2_LICENSES_PRESENT": "stratum 2: license_before and license_after both nonempty",
    "E_S2_REUSE_FRAME_BOUND": "stratum 2: A3-reuse rows carry the frozen successor frame sha256 recorded by the census manifest",
    "E_S3_SUPPLEMENT_TYPE_DATASET": "stratum 3: supplement_resource_type_general == Dataset (the mechanically bound sub-route; software-side supplements are a recorded CANNOT_CHECK class and are not eligible)",
    "E_S3_ENUMERATION_SIDE_BOUND": "stratum 3: enumeration_side == DATACITE_SUPPLEMENT_SIDE",
    "E_S3_TRANSITION_KIND_BOUND": "stratum 3: transition_kind == article_to_data_or_code_release",
}
FORBIDDEN_ROW_KEYS = {"gold", "scientific_gold", "local_authority_gold", "candidate_prediction", "baseline_prediction", "adjudication_outcome", "outcome"}
_HEX64 = set("0123456789abcdef")


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot import frozen module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _allocator() -> Any:
    return _load("a6_allocator_v1", HERE / "allocate_external_authority_packets_v1.py")


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def is_hex64(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value) <= _HEX64


def nonempty(row: dict[str, Any], key: str) -> bool:
    value = row.get(key)
    return isinstance(value, str) and bool(value.strip())


def load_census_stratum(stratum: str, census_root: Path) -> dict[str, Any]:
    dirname, manifest_name = CENSUS[stratum]
    stratum_dir = census_root / dirname
    manifest_path = stratum_dir / manifest_name
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for chunk in manifest.get("chunks", []):
        chunk_path = stratum_dir / Path(str(chunk["path"])).name
        chunk_bytes = chunk_path.read_bytes()
        if hashlib.sha256(chunk_bytes).hexdigest() != chunk.get("sha256"):
            raise ValueError(f"census chunk digest mismatch: {chunk_path.name}")
        payload = json.loads(chunk_bytes.decode("utf-8"))
        rows.extend(payload["rows"])
    if digest(rows) != manifest.get("packet_candidate_rows_sha256"):
        raise ValueError(f"census packet_candidate_rows_sha256 mismatch: {stratum}")
    if len(rows) != manifest.get("packet_candidate_n"):
        raise ValueError(f"census packet_candidate_n mismatch: {stratum}")
    for field in ("distinct_source_family_n", "distinct_normalized_organization_lineage_n", "distinct_artifact_lineage_n"):
        key = {"distinct_source_family_n": "source_family_id", "distinct_normalized_organization_lineage_n": "normalized_organization_lineage", "distinct_artifact_lineage_n": "artifact_lineage_id"}[field]
        if len({r.get(key) for r in rows}) != manifest.get(field):
            raise ValueError(f"census {field} mismatch: {stratum}")
    if manifest.get("protected_orion_predictions_accessed") is not False or manifest.get("gold_adjudicated") is not False:
        raise ValueError(f"census manifest is not outcome-blind: {stratum}")
    if manifest.get("stratum") != stratum:
        raise ValueError(f"census manifest stratum mismatch: {stratum}")
    seen: set[str] = set()
    for row in rows:
        pid = row.get("packet_id")
        if pid in seen:
            raise ValueError(f"duplicate census packet_id: {pid}")
        seen.add(pid)
    return {"manifest": manifest, "rows": rows, "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(), "dir": dirname}


def eligibility_failures(stratum: str, row: dict[str, Any], manifest: dict[str, Any]) -> list[str]:
    failed: list[str] = []
    if row.get("stratum") != stratum:
        failed.append("E_COMMON_STRATUM_MATCH")
    if not all(nonempty(row, k) for k in ("source_family_id", "normalized_organization_lineage", "artifact_lineage_id")):
        failed.append("E_COMMON_LINEAGE_TRIO_PRESENT")
    if not (nonempty(row, "before_version_id") and nonempty(row, "after_version_id")):
        failed.append("E_COMMON_VERSION_IDS_PRESENT")
    if not (is_hex64(row.get("before_sha256")) and is_hex64(row.get("after_sha256"))):
        failed.append("E_COMMON_TRANSITION_DIGESTS_HEX64")
    if row.get("before_sha256") == row.get("after_sha256"):
        failed.append("E_COMMON_TRANSITION_BYTES_DIFFER")
    if not nonempty(row, "license_or_rights_receipt_id"):
        failed.append("E_COMMON_LICENSE_RECEIPT_PRESENT")
    if row.get("content_binding_provenance") not in EXPECTED_PROVENANCE[stratum]:
        failed.append("E_COMMON_PROVENANCE_BOUND")
    if stratum == "scientific_software_release_provenance_attestation":
        if row.get("access_right") != "open":
            failed.append("E_S1_ACCESS_RIGHT_OPEN")
        if not (nonempty(row, "license_before") and nonempty(row, "license_after")):
            failed.append("E_S1_LICENSES_PRESENT")
    elif stratum == "workflowhub_rocrate_versioned_workflow":
        if not (nonempty(row, "license_before") and nonempty(row, "license_after")):
            failed.append("E_S2_LICENSES_PRESENT")
        if row.get("content_binding_provenance") == "A3_FROZEN_FRAME_REUSE" and row.get("a3_successor_frame_sha256") != manifest.get("a3_successor_frame_sha256"):
            failed.append("E_S2_REUSE_FRAME_BOUND")
    else:
        if row.get("supplement_resource_type_general") != "Dataset":
            failed.append("E_S3_SUPPLEMENT_TYPE_DATASET")
        if row.get("enumeration_side") != "DATACITE_SUPPLEMENT_SIDE":
            failed.append("E_S3_ENUMERATION_SIDE_BOUND")
        if row.get("transition_kind") != "article_to_data_or_code_release":
            failed.append("E_S3_TRANSITION_KIND_BOUND")
    return failed


def candidate_visible_payload(row: dict[str, Any]) -> dict[str, Any]:
    """Target-relevant scientific coordinates + terminal alphabet, nothing else.

    No ORION predictions, no split/allocation information, no lineage-trio
    identifiers (the adjudicator re-derives custody from the source; lineage
    ids stay in the bound-fields block of the prep packet, not the science
    payload). Stratum-specific descriptors are included only when nonempty,
    under a fixed documented presence rule.
    """
    payload: dict[str, Any] = {
        "schema": VISIBLE_SCHEMA,
        "packet_id": row["packet_id"],
        "stratum": row["stratum"],
        "source_family_id": row["source_family_id"],
        "before_version_id": row["before_version_id"],
        "after_version_id": row["after_version_id"],
        "before_sha256": row["before_sha256"],
        "after_sha256": row["after_sha256"],
        "license_or_rights_receipt_id": row["license_or_rights_receipt_id"],
        "gold_labels": list(GOLD_LABELS),
        "terminal_alphabet": list(TERMINAL_ALPHABET),
    }
    if row["stratum"] == "scientific_software_release_provenance_attestation":
        for key in ("license_before", "license_after", "access_right", "transition_title"):
            if nonempty(row, key):
                payload[key] = row[key]
    elif row["stratum"] == "workflowhub_rocrate_versioned_workflow":
        for key in ("license_before", "license_after", "workflow_name", "organization_name"):
            if nonempty(row, key):
                payload[key] = row[key]
    else:
        for key in ("supplement_resource_type_general", "transition_kind"):
            if nonempty(row, key):
                payload[key] = row[key]
        urls = row.get("article_crossref_license_urls")
        if isinstance(urls, list) and urls:
            payload["article_crossref_license_urls"] = urls
    return payload


def external_custody_receipt(row: dict[str, Any]) -> str:
    payload = "|".join((
        "A6-EXTERNAL-CUSTODY-RECEIPT-V1",
        row["stratum"],
        row["source_family_id"],
        row["before_version_id"],
        row["after_version_id"],
        row["before_sha256"],
        row["after_sha256"],
        row["content_binding_provenance"],
    ))
    return "a6-external-custody:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def adjudicator_assignment_receipt(row: dict[str, Any], visible_sha: str, handoff_sha: str) -> str:
    payload = "|".join((
        "A6-ADJUDICATOR-ASSIGNMENT-RECEIPT-V1",
        row["packet_id"],
        visible_sha,
        handoff_sha,
    ))
    return "a6-adjudicator-assignment:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_quota_freeze(path: Path, census: dict[str, dict[str, Any]]) -> dict[str, Any]:
    freeze = json.loads(path.read_text(encoding="utf-8"))
    if freeze.get("schema") != FREEZE_SCHEMA:
        raise ValueError("wrong quota freeze schema")
    if freeze.get("frozen_before_candidate_predictions") is not True or freeze.get("protected_outcomes_accessed") is not False:
        raise ValueError("quota freeze is not pre-prediction/outcome-blind")
    quotas = freeze.get("replication_quota_by_stratum")
    target = freeze.get("replication_target_n")
    if not isinstance(quotas, dict) or set(quotas) != set(STRATA) or any(not isinstance(quotas[s], int) or isinstance(quotas[s], bool) or quotas[s] < 1 for s in STRATA):
        raise ValueError("invalid replication_quota_by_stratum in freeze")
    if not isinstance(target, int) or isinstance(target, bool) or target < 3 or sum(quotas.values()) != target:
        raise ValueError("replication_target_n does not sum the frozen stratum quotas")
    # Zero-free-parameter derivation is re-proved against the live census facts:
    # the freeze cannot drift from the census manifests it cites.
    rule = freeze.get("derivation_rule", {})
    inputs = rule.get("inputs", {})
    capacities = inputs.get("external_disjoint_lineage_capacity_by_stratum")
    if not isinstance(capacities, dict) or set(capacities) != set(STRATA):
        raise ValueError("freeze capacity inputs malformed")
    for s in STRATA:
        live = census[s]["manifest"]["distinct_normalized_organization_lineage_n"]
        if capacities[s] != live:
            raise ValueError(f"freeze capacity drifted from frozen census manifest for {s}: {capacities[s]} != {live}")
    primary = inputs.get("primary_quota_per_stratum")
    if primary != 20:
        raise ValueError("freeze primary quota is not the frozen 20 per stratum")
    expected_r = max(1, min(capacities[s] - primary for s in STRATA))
    if any(quotas[s] != expected_r for s in STRATA):
        raise ValueError(f"freeze quotas are not the derived uniform quota: expected {expected_r} per stratum, got {quotas}")
    return freeze


def build(census_root: Path, quota_freeze_path: Path, handoff_path: Path | None = None) -> dict[str, Any]:
    allocator = _allocator()
    handoff_path = handoff_path or (HERE / HANDOFF_PATH)
    handoff_sha = hashlib.sha256(handoff_path.read_bytes()).hexdigest()
    census = {s: load_census_stratum(s, census_root) for s in STRATA}
    freeze = load_quota_freeze(quota_freeze_path, census)
    quotas: dict[str, int] = freeze["replication_quota_by_stratum"]
    # Record the freeze location canonically (relative to this script's
    # directory when co-located) so the emitted pool bytes are independent of
    # the invocation working directory or staging root.
    try:
        freeze_recorded_path = quota_freeze_path.resolve().relative_to(HERE.resolve()).as_posix()
    except ValueError:
        freeze_recorded_path = quota_freeze_path.resolve().as_posix()

    packets: list[dict[str, Any]] = []
    stats: dict[str, Any] = {}
    for s in STRATA:
        manifest = census[s]["manifest"]
        eligible = 0
        failures: dict[str, int] = {}
        for row in census[s]["rows"]:
            failed = eligibility_failures(s, row, manifest)
            if FORBIDDEN_ROW_KEYS & set(row):
                raise ValueError(f"census row carries a forbidden key: {row.get('packet_id')}")
            if failed:
                for rule_id in failed:
                    failures[rule_id] = failures.get(rule_id, 0) + 1
                packets.append({
                    "packet_id": row.get("packet_id") or f"unnamed:{len(packets)}",
                    "stratum": s,
                    "eligible_preterminal": False,
                    "eligibility_rule_failures": failed,
                })
                continue
            payload = candidate_visible_payload(row)
            visible_sha = hashlib.sha256(canonical(payload)).hexdigest()
            packet = {
                "packet_id": row["packet_id"],
                "eligible_preterminal": True,
                "stratum": s,
                "source_family_id": row["source_family_id"],
                "normalized_organization_lineage": row["normalized_organization_lineage"],
                "artifact_lineage_id": row["artifact_lineage_id"],
                "before_version_id": row["before_version_id"],
                "after_version_id": row["after_version_id"],
                "before_sha256": row["before_sha256"],
                "after_sha256": row["after_sha256"],
                "license_or_rights_receipt_id": row["license_or_rights_receipt_id"],
                "external_custody_receipt_id": external_custody_receipt(row),
                "adjudicator_assignment_receipt_id": adjudicator_assignment_receipt(row, visible_sha, handoff_sha),
                "candidate_visible_packet_sha256": visible_sha,
                "candidate_blind_gold_process_frozen": True,
            }
            packets.append(packet)
            eligible += 1
        stats[s] = {
            "census_packet_candidates": census[s]["manifest"]["packet_candidate_n"],
            "eligible_preterminal_n": eligible,
            "ineligible_n": census[s]["manifest"]["packet_candidate_n"] - eligible,
            "ineligible_rule_counts": failures,
        }
    packets.sort(key=lambda p: p["packet_id"])

    pool = {
        "schema": POOL_SCHEMA,
        "protected_outcomes_accessed": False,
        "candidate_predictions_accessed": False,
        "replication_n_frozen_before_predictions": True,
        "replication_quota_by_stratum_frozen_before_predictions": True,
        "replication_target_n": freeze["replication_target_n"],
        "replication_quota_by_stratum": quotas,
        "quota_freeze_binding": {
            "path": freeze_recorded_path,
            "sha256": hashlib.sha256(quota_freeze_path.read_bytes()).hexdigest(),
            "schema": FREEZE_SCHEMA,
        },
        "handoff_contract_sha256": handoff_sha,
        "census_bindings": {
            s: {
                "manifest": f"papers/publication_closure/a6-external-authority-study-v1/{census[s]['dir']}/{CENSUS[s][1]}",
                "manifest_sha256": census[s]["manifest_sha256"],
                "packet_candidate_rows_sha256": census[s]["manifest"]["packet_candidate_rows_sha256"],
            }
            for s in STRATA
        },
        "eligibility_rules": dict(ELIGIBILITY_RULES),
        "eligibility_outcome_blind": "eligibility adjudicated from registry/metadata properties only; no ORION predictions, baselines or protected outcomes exist at this stage",
        "stratum_stats": stats,
        "packets_manifest_sha256": digest(packets),
        "packets": packets,
        "receipt_semantics": {
            "external_custody_receipt_id": "binds the transition bytes to the external source coordinates holding them; a custody statement, not a sign-off",
            "adjudicator_assignment_receipt_id": "stages the packet into the frozen external adjudicator handoff queue; confers no authority and records no adjudication",
            "candidate_visible_packet_sha256": "SHA-256 over the canonical candidate-visible payload (target-relevant scientific coordinates + terminal alphabet only)",
        },
        "gold_adjudicated": False,
        "scientific_authority_delta": "NONE__POOL_FREEZE_ONLY",
    }
    allocator.validate_pool(pool)
    return pool


# ---------------------------------------------------------------- self-test --

def _synthetic_census(base: Path) -> Path:
    root = base / "census"
    for i, s in enumerate(STRATA):
        dirname, manifest_name = CENSUS[s]
        sdir = root / dirname
        sdir.mkdir(parents=True, exist_ok=True)
        rows = []
        # Stratum 3 mirrors reality: its external org lineages are the scarce
        # dimension (21 for 30 rows), so it caps the derived replication quota.
        org_n = 21 if s == STRATA[2] else 30
        for j in range(30):
            pid = f"syn-{i}-{j:03d}"
            row = {
                "packet_id": pid,
                "stratum": s,
                "source_family_id": f"sf-{pid}",
                "normalized_organization_lineage": f"org-{i}-{j % org_n:03d}",
                "artifact_lineage_id": f"art-{pid}",
                "before_version_id": f"1.{j}",
                "after_version_id": f"1.{j + 1}",
                "before_sha256": hashlib.sha256(f"before-{pid}".encode()).hexdigest(),
                "after_sha256": hashlib.sha256(f"after-{pid}".encode()).hexdigest(),
                "license_or_rights_receipt_id": f"rights-{pid}",
                "content_binding_provenance": EXPECTED_PROVENANCE[s][0],
            }
            if s == "scientific_software_release_provenance_attestation":
                row.update({"access_right": "open", "license_before": "mit", "license_after": "mit", "transition_title": f"synthetic {pid}"})
            elif s == "workflowhub_rocrate_versioned_workflow":
                row.update({"license_before": "Apache-2.0", "license_after": "Apache-2.0", "workflow_name": f"workflow {pid}", "organization_name": f"org {j}", "a3_successor_frame_sha256": "f" * 64})
            else:
                row.update({"supplement_resource_type_general": "Dataset", "enumeration_side": "DATACITE_SUPPLEMENT_SIDE", "transition_kind": "article_to_data_or_code_release", "article_crossref_license_urls": ["https://example.org/license"]})
            rows.append(row)
        chunks = []
        for c in range(0, len(rows), 20):
            part = rows[c:c + 20]
            name = f"ROWS_{c + 1:03d}_{c + len(part):03d}.json"
            (sdir / name).write_text(json.dumps({"schema": "synthetic", "rows": part}, sort_keys=True) + "\n", encoding="utf-8")
            chunks.append({"path": f"papers/publication_closure/a6-external-authority-study-v1/{dirname}/{name}", "rows": len(part), "sha256": hashlib.sha256((sdir / name).read_bytes()).hexdigest()})
        manifest = {
            "schema": "synthetic",
            "stratum": s,
            "packet_candidate_n": len(rows),
            "packet_candidate_rows_sha256": digest(rows),
            "distinct_source_family_n": len({r["source_family_id"] for r in rows}),
            "distinct_normalized_organization_lineage_n": len({r["normalized_organization_lineage"] for r in rows}),
            "distinct_artifact_lineage_n": len({r["artifact_lineage_id"] for r in rows}),
            "a3_successor_frame_sha256": "f" * 64,
            "protected_orion_predictions_accessed": False,
            "gold_adjudicated": False,
            "chunks": chunks,
        }
        (sdir / manifest_name).write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return root


def _synthetic_freeze(base: Path, capacities: dict[str, int] | None = None) -> Path:
    capacities = capacities or {s: (21 if s == STRATA[2] else 30) for s in STRATA}
    r = max(1, min(capacities[s] - 20 for s in STRATA))
    freeze = {
        "schema": FREEZE_SCHEMA,
        "frozen_before_candidate_predictions": True,
        "protected_outcomes_accessed": False,
        "replication_quota_by_stratum": {s: r for s in STRATA},
        "replication_target_n": 3 * r,
        "derivation_rule": {"inputs": {"primary_quota_per_stratum": 20, "external_disjoint_lineage_capacity_by_stratum": capacities}},
    }
    path = base / "freeze.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(freeze, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return path


def self_test() -> dict[str, Any]:
    allocator = _allocator()
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        census_root = _synthetic_census(base)
        freeze_path = _synthetic_freeze(base)
        pool = build(census_root, freeze_path)
        if sum(1 for p in pool["packets"] if p["eligible_preterminal"]) != 90:
            raise ValueError("synthetic census did not yield 90 eligible packets")
        allocation = allocator.allocate(pool)
        if allocation["terminal"] != "A6_EXTERNAL_PRIMARY_REPLICATION_ALLOCATION_FROZEN":
            raise ValueError(f"synthetic pool failed the frozen allocation: {allocation['terminal']}")
        if allocation["primary_n"] != 60 or allocation["replication_n"] != 3:
            raise ValueError("synthetic allocation counts wrong")

        # Row-order invariance of the pool digest.
        shuffled = json.loads(json.dumps(pool))
        shuffled["packets"].reverse()
        if allocator.allocate(shuffled)["selection_manifest_sha256"] != allocation["selection_manifest_sha256"]:
            raise ValueError("allocation is not invariant to pool row order")

        # Tampered census chunk bytes are rejected.
        chunk = census_root / CENSUS[STRATA[0]][0] / "ROWS_001_020.json"
        chunk.write_bytes(chunk.read_bytes() + b" ")
        try:
            build(census_root, freeze_path)
        except ValueError:
            pass
        else:
            raise AssertionError("tampered census chunk accepted")
        census_root = _synthetic_census(base)

        # Quota freeze drifting from the derivation rule is rejected.
        drifted = json.loads(freeze_path.read_text())
        drifted["replication_quota_by_stratum"][STRATA[0]] += 1
        drifted_path = base / "drifted.json"
        drifted_path.write_text(json.dumps(drifted), encoding="utf-8")
        try:
            build(census_root, drifted_path)
        except ValueError:
            pass
        else:
            raise AssertionError("non-derived quota accepted")

        # Quota freeze citing stale capacities is rejected.
        stale = _synthetic_freeze(base / "stale.d", capacities={s: 99 for s in STRATA})
        try:
            build(census_root, stale)
        except ValueError:
            pass
        else:
            raise AssertionError("stale freeze capacities accepted")

        # A non-open-access row becomes ineligible and is never padded in.
        sdir = census_root / CENSUS[STRATA[0]][0]
        payload = json.loads((sdir / "ROWS_001_020.json").read_text())
        payload["rows"][0]["access_right"] = "restricted"
        (sdir / "ROWS_001_020.json").write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
        snapshot = json.loads((sdir / "A6_STRATUM1_CENSUS_MANIFEST_V1.json").read_text())
        rows = []
        for chunk_info in snapshot["chunks"]:
            chunk_file = sdir / Path(chunk_info["path"]).name
            rows.extend(json.loads(chunk_file.read_text())["rows"])
            chunk_info["sha256"] = hashlib.sha256(chunk_file.read_bytes()).hexdigest()
        snapshot["packet_candidate_rows_sha256"] = digest(rows)
        (sdir / "A6_STRATUM1_CENSUS_MANIFEST_V1.json").write_text(json.dumps(snapshot, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        strict = build(census_root, freeze_path)
        bad_row = next(p for p in strict["packets"] if p["packet_id"] == payload["rows"][0]["packet_id"])
        if bad_row["eligible_preterminal"] is not False or "E_S1_ACCESS_RIGHT_OPEN" not in bad_row["eligibility_rule_failures"]:
            raise ValueError("closed-access row was not marked ineligible")
        strict_alloc = allocator.allocate(strict)
        if strict_alloc["primary_n"] != 60:
            raise ValueError("ineligible row leaked into the primary quota")

        # Gold never enters the pool (frozen allocator is authoritative).
        poisoned = json.loads(json.dumps(pool))
        poisoned["packets"][0]["gold"] = "ADMIT"
        try:
            allocator.allocate(poisoned)
        except ValueError:
            pass
        else:
            raise AssertionError("gold-bearing pool accepted")

    return {
        "decision": "GREEN",
        "pool_schema": POOL_SCHEMA,
        "census_digests_verified": True,
        "quota_derivation_enforced_zero_free_parameters": True,
        "quota_drift_rejected": True,
        "stale_capacity_rejected": True,
        "tampered_chunk_rejected": True,
        "row_order_invariant": True,
        "eligibility_rules_fail_closed": True,
        "gold_never_enters_pool": True,
        "allocation_terminal_on_synthetic_pool": "A6_EXTERNAL_PRIMARY_REPLICATION_ALLOCATION_FROZEN",
        "scientific_judgment_made": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--census-root", type=Path, default=HERE)
    ap.add_argument("--quota-freeze", type=Path, default=HERE / "A6_REPLICATION_QUOTA_FREEZE_V1.json")
    ap.add_argument("--output", type=Path)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        result = self_test()
    else:
        result = build(args.census_root, args.quota_freeze)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
