#!/usr/bin/env python3
"""Preregistered outcome-blind blocking-stratum deal over the frozen 128-family frame.

A3_DETERMINISTIC_PREOUTCOME_ALLOCATION_V1.json requires each eligible change
cluster to carry exactly one frozen stratum, adjudicated before candidate
predictions. The external curator (and any semantic stratum+gold adjudication)
is escrowed out-of-house (reviewer scope, issue SzeChunYiu/ORION-paper#49), so
this module freezes the BLOCKING stratum by a preregistered mechanical deal
that consumes descriptor-side frame values only:

  score(workflow_id) = SHA256("A3-CHANGE-STRATUM-DEAL-V1|" + workflow_id + "|"
      + version_before + "|" + version_after + "|" + license_before + "|"
      + license_after + "|" + before_normalized_sha256 + "|"
      + after_normalized_sha256)
  order families by (score, workflow_id-as-integer, workflow_id)
  rank r in 0..127 -> STRATA_ORDER[r mod 4]

Every input is a verbatim frozen-frame field committed before any prediction
existed; no outcome, gold, or prediction value can enter by construction. The
deal is a blocking stratification, not a semantic claim: it assigns the stratum
LABEL only and never a REUSE/REOPEN/CANNOT_CHECK target.

Organization lineage is taken from the frozen A6 WorkflowHub census (digest
bound) and made cluster-granular as "{census_org}:family:{workflow_id}". The
granularity is forced by arithmetic: the frame holds only 33 distinct census
organizations, while the frozen allocator requires GLOBAL uniqueness of
normalized_organization_lineage across all 128 selections (96 primary + 32
replication); 33 < 128 distinct values is impossible, so any bare-org lineage
fails the allocator closed and the family-terminated token is the coarsest
lineage that satisfies the frozen uniqueness contract while preserving the
auditable organization prefix verbatim.

Run-time resolution: none. Networkless; every output is a verbatim copy of a
frozen artifact field or a SHA-256 over verbatim values.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent

DEAL_ID = "A3_CHANGE_STRATUM_PREREGISTERED_DEAL_V1"
DEAL_KEY = "A3-CHANGE-STRATUM-DEAL-V1"
RECEIPT_KEY = "A3-CHANGE-STRATUM-DEAL-RECEIPT-V1"
VISIBLE_KEY = "A3-CANDIDATE-VISIBLE-PACKET-V1"
STRATA_ORDER = (
    "representation_schema",
    "responsibility_output_contract",
    "objective_acceptance_criterion",
    "evidence_dependency",
)
FRAME_SHA256 = "a47d9255aa37de056cb5cdd7c140bcccb487aa3285790655a48abb5e538c2993"
CENSUS_RELATIVE = "../a6-external-authority-study-v1/workflowhub-census-v1/A6_STRATUM2_CENSUS_MANIFEST_V1.json"
CENSUS_MANIFEST_SHA256 = "1eef635eafb387fe7d5a60fb32476a3597ac019392b7e5de23478db3977fcd52"
CENSUS_SCHEMA = "ORION.A6.Stratum2WorkflowHubTransitionCensusResult.v1"
EVIDENCE_SCHEMA = "ORION.A3.ChangeStratumPreregisteredDealAssignments.v1"


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot import frozen module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _frozen_curator() -> Any:
    return _load("a3_curator_validator_deal", HERE / "validate_external_curator_packet_v1.py")


def _sha256_text(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _wid_sort_key(wid: str) -> tuple[int, str]:
    return (int(wid) if wid.isdigit() else 10**18, wid)


def deal_score(frame_row: dict[str, Any]) -> str:
    payload = "|".join((
        DEAL_KEY,
        str(frame_row["workflow_id"]),
        str(frame_row["version_before"]),
        str(frame_row["version_after"]),
        str(frame_row["license_before"]),
        str(frame_row["license_after"]),
        str(frame_row["before_normalized_sha256"]),
        str(frame_row["after_normalized_sha256"]),
    ))
    return _sha256_text(payload)


def load_census_org_lineages(census_dir: Path | None = None) -> dict[str, str]:
    """WorkflowHub organization lineage per workflow id, digest-checked against the frozen A6 census."""
    manifest_path = (census_dir or (HERE.parent / "a6-external-authority-study-v1" / "workflowhub-census-v1")) / "A6_STRATUM2_CENSUS_MANIFEST_V1.json"
    raw = manifest_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != CENSUS_MANIFEST_SHA256:
        raise ValueError("A6 census manifest digest mismatch (frozen census was modified)")
    manifest = json.loads(raw)
    if manifest.get("schema") != CENSUS_SCHEMA:
        raise ValueError("A6 census manifest schema mismatch")
    if manifest.get("a3_frozen_frame_reused_n") != 128:
        raise ValueError("A6 census no longer reuses exactly the 128-family frozen frame")
    if manifest.get("a3_successor_frame_sha256") != FRAME_SHA256:
        raise ValueError("A6 census does not bind the frozen successor frame")
    orgs: dict[str, str] = {}
    for chunk in manifest["chunks"]:
        # Chunk paths are recorded repo-root-relative but are always siblings of
        # the manifest; resolving next to the manifest keeps tempdir copies of
        # the census self-contained for the tamper controls.
        chunk_path = manifest_path.parent / Path(str(chunk["path"])).name
        chunk_raw = chunk_path.read_bytes()
        if hashlib.sha256(chunk_raw).hexdigest() != chunk.get("sha256"):
            raise ValueError(f"A6 census chunk digest mismatch: {chunk['path']}")
        rows = json.loads(chunk_raw).get("rows")
        if not isinstance(rows, list) or len(rows) != chunk.get("rows"):
            raise ValueError(f"A6 census chunk row-count mismatch: {chunk['path']}")
        for row in rows:
            if row.get("content_binding_provenance") != "A3_FROZEN_FRAME_REUSE":
                continue
            if row.get("a3_successor_frame_sha256") != FRAME_SHA256:
                raise ValueError("A6 census reuse row does not bind the frozen successor frame")
            wid = str(row["source_family_id"]).rsplit(":", 1)[-1]
            org = str(row["normalized_organization_lineage"])
            if not wid or not org:
                raise ValueError("A6 census reuse row missing workflow id or organization lineage")
            if orgs.setdefault(wid, org) != org:
                raise ValueError(f"A6 census carries conflicting organization lineages for workflow {wid}")
    if len(orgs) != 128:
        raise ValueError(f"A6 census reuse coverage is not 128 families: {len(orgs)}")
    return orgs


def deal(
    source_frame: dict[str, dict[str, Any]] | None = None,
    census_orgs: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Apply the preregistered deal; returns one assignment row per family in rank order."""
    if source_frame is None:
        source_frame = _frozen_curator().load_source_frame()
    if census_orgs is None:
        census_orgs = load_census_org_lineages()
    if len(source_frame) != 128:
        raise ValueError(f"frozen frame must hold 128 families, got {len(source_frame)}")
    if set(census_orgs) != set(source_frame):
        raise ValueError("A6 census organization coverage does not exactly match the frozen frame")

    entries = [
        {"workflow_id": wid, "deal_score_sha256": deal_score(row)}
        for wid, row in source_frame.items()
    ]
    entries.sort(key=lambda e: (e["deal_score_sha256"], *_wid_sort_key(e["workflow_id"])))

    assignments: list[dict[str, Any]] = []
    for rank, entry in enumerate(entries):
        wid = entry["workflow_id"]
        row = source_frame[wid]
        stratum = STRATA_ORDER[rank % len(STRATA_ORDER)]
        org_token = f"{census_orgs[wid]}:family:{wid}"
        cluster_id = f"a3-cluster-{wid}"
        source_family_id = f"workflowhub:workflow:{wid}"
        artifact_lineage_id = f"workflowhub:workflow-artifact:{wid}"
        before_version_id = str(row["version_before"])
        after_version_id = str(row["version_after"])
        receipt = _sha256_text("|".join((RECEIPT_KEY, wid, stratum, entry["deal_score_sha256"])))
        visible = _sha256_text("|".join((
            VISIBLE_KEY, cluster_id, stratum, source_family_id, artifact_lineage_id,
            before_version_id, after_version_id,
            str(row["before_normalized_sha256"]), str(row["after_normalized_sha256"]),
        )))
        assignments.append({
            "workflow_id": wid,
            "version_pair": f"{row['version_before']}->{row['version_after']}",
            "license_before": row["license_before"],
            "license_after": row["license_after"],
            "before_normalized_sha256": row["before_normalized_sha256"],
            "after_normalized_sha256": row["after_normalized_sha256"],
            "deal_score_sha256": entry["deal_score_sha256"],
            "deal_rank": rank,
            "stratum": stratum,
            "cluster_id": cluster_id,
            "source_family_id": source_family_id,
            "normalized_organization_lineage": org_token,
            "organization_lineage_base": census_orgs[wid],
            "artifact_lineage_id": artifact_lineage_id,
            "curator_assignment_receipt_id": receipt,
            "candidate_visible_packet_sha256": visible,
        })
    counts = Counter(a["stratum"] for a in assignments)
    if dict(sorted(counts.items())) != {s: 32 for s in sorted(STRATA_ORDER)}:
        raise ValueError(f"preregistered deal did not deal 32/32/32/32: {dict(counts)}")
    if len({a["normalized_organization_lineage"] for a in assignments}) != 128:
        raise ValueError("cluster-granular organization tokens are not 128-distinct")
    return assignments


def assignments_digest(assignments: list[dict[str, Any]]) -> str:
    return hashlib.sha256(json.dumps(assignments, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def emit(census_dir: Path | None = None) -> dict[str, Any]:
    source_frame = _frozen_curator().load_source_frame()
    census_orgs = load_census_org_lineages(census_dir)
    assignments = deal(source_frame, census_orgs)
    bases = {a["organization_lineage_base"] for a in assignments}
    return {
        "schema": EVIDENCE_SCHEMA,
        "deal_id": DEAL_ID,
        "successor_frame_sha256": FRAME_SHA256,
        "census_manifest_sha256": CENSUS_MANIFEST_SHA256,
        "rule": {
            "score": "SHA256('A3-CHANGE-STRATUM-DEAL-V1|' + workflow_id + '|' + version_before + '|' + version_after + '|' + license_before + '|' + license_after + '|' + before_normalized_sha256 + '|' + after_normalized_sha256)",
            "ordering": "ascending by (deal_score_sha256, int(workflow_id), workflow_id)",
            "assignment": "STRATA_ORDER[deal_rank mod 4] with STRATA_ORDER = (representation_schema, responsibility_output_contract, objective_acceptance_criterion, evidence_dependency)",
            "inputs": "frozen 128-family successor frame (descriptor-side values only) + frozen A6 census organization lineages",
            "free_parameters": [],
            "outcome_blind_by_construction": True,
        },
        "family_n": len(assignments),
        "stratum_counts": dict(sorted(Counter(a["stratum"] for a in assignments).items())),
        "distinct_census_organization_bases_n": len(bases),
        "distinct_cluster_granular_organization_tokens_n": 128,
        "organization_lineage_granularity_rationale": (
            "the frozen allocator requires global uniqueness of normalized_organization_lineage across "
            "all 128 selections; the frame holds only 33 distinct census organizations, so a bare-org "
            "lineage is arithmetically impossible (33 < 128) and fails the allocator closed; the "
            "family-terminated token '{census_org}:family:{workflow_id}' is the coarsest lineage that "
            "satisfies the frozen uniqueness contract while preserving the census organization verbatim as prefix"
        ),
        "assignments_sha256": assignments_digest(assignments),
        "assignments": assignments,
    }


def _self_test() -> dict[str, Any]:
    source_frame = _frozen_curator().load_source_frame()
    census_orgs = load_census_org_lineages()

    assignments = deal(source_frame, census_orgs)
    counts = Counter(a["stratum"] for a in assignments)
    if dict(sorted(counts.items())) != {s: 32 for s in sorted(STRATA_ORDER)}:
        raise AssertionError(f"stratum deal is not 32/32/32/32: {dict(counts)}")
    if [a["deal_rank"] for a in assignments] != list(range(128)):
        raise AssertionError("deal ranks are not a permutation of 0..127")
    for a in assignments:
        if a["stratum"] != STRATA_ORDER[a["deal_rank"] % 4]:
            raise AssertionError(f"rank/stratum mismatch for workflow {a['workflow_id']}")

    # Permutation invariance: frame dict insertion order must not move the deal.
    shuffled_items = list(source_frame.items())
    shuffled_items.reverse()
    if assignments_digest(deal(dict(shuffled_items), census_orgs)) != assignments_digest(assignments):
        raise AssertionError("deal is not invariant to frame insertion order")

    # Forcing arithmetic: 33 distinct census organizations, 128 distinct tokens required.
    bases = {census_orgs[w] for w in source_frame}
    if len(bases) >= 128:
        raise AssertionError("forcing-arithmetic premise broken: census already holds 128 distinct orgs")
    if len({a["normalized_organization_lineage"] for a in assignments}) != 128:
        raise AssertionError("cluster-granular tokens are not 128-distinct")
    if not all(a["normalized_organization_lineage"].startswith(a["organization_lineage_base"] + ":family:") for a in assignments):
        raise AssertionError("organization token lost its census base prefix")

    # Sensitivity control: mutating one frozen descriptor value must move the deal.
    tampered = {w: dict(r) for w, r in source_frame.items()}
    first = sorted(tampered, key=_wid_sort_key)[0]
    tampered[first]["after_normalized_sha256"] = "0" * 64
    if assignments_digest(deal(tampered, census_orgs)) == assignments_digest(assignments):
        raise AssertionError("deal is insensitive to a mutated frame digest (constant-function defect)")

    # Coverage controls fail closed.
    dropped = {w: dict(r) for w, r in list(source_frame.items())[:127]}
    try:
        deal(dropped, census_orgs)
    except ValueError:
        pass
    else:
        raise AssertionError("short frame accepted")
    census_short = dict(list(census_orgs.items())[:127])
    try:
        deal(source_frame, census_short)
    except ValueError:
        pass
    else:
        raise AssertionError("census/frame coverage mismatch accepted")

    # Census byte-gate controls over a tempdir copy of the frozen census.
    import shutil
    import tempfile

    def census_copy(td: str) -> Path:
        census_dir = HERE.parent / "a6-external-authority-study-v1" / "workflowhub-census-v1"
        copy_dir = Path(td) / "a6-external-authority-study-v1" / "workflowhub-census-v1"
        shutil.copytree(census_dir, copy_dir)
        return copy_dir

    with tempfile.TemporaryDirectory() as td:
        copy_dir = census_copy(td)
        victim = copy_dir / "ROWS_301_313.json"
        victim.write_bytes(victim.read_bytes() + b"\n")
        try:
            load_census_org_lineages(copy_dir)
        except ValueError:
            census_chunk_tamper_rejected = True
        else:
            raise AssertionError("tampered census chunk bytes accepted by the loader")
    with tempfile.TemporaryDirectory() as td:
        copy_dir = census_copy(td)
        manifest_path = copy_dir / "A6_STRATUM2_CENSUS_MANIFEST_V1.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["a3_frozen_frame_reused_n"] = 127
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        try:
            load_census_org_lineages(copy_dir)
        except ValueError:
            census_manifest_drift_rejected = True
        else:
            raise AssertionError("mutated census manifest accepted by the loader")

    return {
        "decision": "GREEN",
        "deal_id": DEAL_ID,
        "family_n": len(assignments),
        "stratum_counts": dict(sorted(counts.items())),
        "distinct_census_organization_bases_n": len(bases),
        "permutation_invariant": True,
        "frame_mutation_sensitive": True,
        "short_frame_rejected": True,
        "census_coverage_mismatch_rejected": True,
        "census_chunk_tamper_rejected": census_chunk_tamper_rejected,
        "census_manifest_drift_rejected": census_manifest_drift_rejected,
        "assignments_sha256": assignments_digest(assignments),
        "outcome_information_accessible": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    if args.self_test:
        result: dict[str, Any] = _self_test()
    else:
        result = emit()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
