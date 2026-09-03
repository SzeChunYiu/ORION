#!/usr/bin/env python3
"""Build the A3 EligibleChangeClusterPool from the preregistered blocking stratum deal.

This builder materializes the pool WITHOUT external curator packets: the
blocking stratum label comes from the preregistered, outcome-blind
A3_CHANGE_STRATUM_PREREGISTERED_DEAL_V1 (assign_change_stratum_preregistered_deal_v1.py,
imported verbatim), and every other field is a verbatim copy of the frozen
128-family successor frame, the frozen A6 census organization lineage, or the
frozen licence-receipt / v3-boundary machinery of
build_eligible_change_cluster_pool_v1.py (imported verbatim). The resulting
pool is a valid input for the frozen allocate_change_clusters_v1.py.

Scope honesty: the external curator's semantic adjudication (stratum review
and the escrowed REUSE/REOPEN/CANNOT_CHECK gold) remains out of house; the
curator_assignment_receipt_id on each row is the deal's mechanical receipt,
explicitly labeled as standing in for the external curator for the BLOCKING
stratum only. No gold, prediction, or outcome value exists anywhere in this
pipeline by construction.

Run-time resolution: none. Networkless; deterministic byte-for-byte.
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
POOL_SCHEMA = "ORION.A3.EligibleChangeClusterPool.v1"
DEAL_ID = "A3_CHANGE_STRATUM_PREREGISTERED_DEAL_V1"
STRATA = (
    "representation_schema",
    "responsibility_output_contract",
    "objective_acceptance_criterion",
    "evidence_dependency",
)
GOLD_KEYS = (
    "gold", "reuse_gold", "adjudicated_target", "reuse_reopen_target", "target",
    "candidate_prediction", "baseline_prediction", "outcome", "protected_outcome",
)
ALLOCATION_TERMINAL = "A3_PREOUTCOME_PRIMARY_REPLICATION_ALLOCATION_FROZEN"
SHORTFALL_TERMINAL = "CANNOT_CHECK_A3_PREOUTCOME_QUOTA_OR_DISJOINTNESS_SHORTFALL"
V3_FAILURE_TERMINAL = "CANNOT_CHECK_MEMBER_MANIFEST_V3_REPRODUCIBILITY"


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot import frozen module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _deal_module() -> Any:
    return _load("a3_stratum_deal_v1", HERE / "assign_change_stratum_preregistered_deal_v1.py")


def _pool_builder() -> Any:
    return _load("a3_pool_builder_v1", HERE / "build_eligible_change_cluster_pool_v1.py")


def _allocator() -> Any:
    return _load("a3_allocator_deal_v1", HERE / "allocate_change_clusters_v1.py")


def build(census_dir: Path | None = None, v3_base_dir: Path | None = None) -> dict[str, Any]:
    deal_mod = _deal_module()
    builder = _pool_builder()
    source_frame = builder._frozen_validator().load_source_frame()
    census_orgs = deal_mod.load_census_org_lineages(census_dir)
    assignments = deal_mod.deal(source_frame, census_orgs)
    by_wid = {a["workflow_id"]: a for a in assignments}

    substrate = builder._member_manifests_v3(source_frame, base_dir=v3_base_dir if v3_base_dir is not None else HERE)
    if substrate is None or substrate.get("bound") is True:
        raise ValueError(
            "blocking-deal pool requires the recorded-not-bound v3 failure boundary; "
            "a materialized or successful v3 substrate belongs to freeze governance, not this builder"
        )

    clusters: list[dict[str, Any]] = []
    for wid in builder._sorted_frame(source_frame):
        frame_row = source_frame[wid]
        assignment = by_wid[wid]
        clusters.append({
            "cluster_id": assignment["cluster_id"],
            "eligible": True,
            "stratum": assignment["stratum"],
            "workflow_id": wid,
            "source_family_id": assignment["source_family_id"],
            "normalized_organization_lineage": assignment["normalized_organization_lineage"],
            "artifact_lineage_id": assignment["artifact_lineage_id"],
            "before_version_id": str(frame_row["version_before"]),
            "after_version_id": str(frame_row["version_after"]),
            "before_sha256": frame_row["before_normalized_sha256"],
            "after_sha256": frame_row["after_normalized_sha256"],
            "license_before": frame_row["license_before"],
            "license_after": frame_row["license_after"],
            "license_or_rights_receipt_id": builder.licence_receipt_id(frame_row),
            "curator_assignment_receipt_id": assignment["curator_assignment_receipt_id"],
            "curator_assignment_receipt_basis": (
                "preregistered mechanical deal receipt (A3_CHANGE_STRATUM_PREREGISTERED_DEAL_V1) standing in "
                "for the external curator for the blocking stratum label only; not an external custody receipt"
            ),
            "candidate_visible_packet_frozen": True,
            "candidate_visible_packet_sha256": assignment["candidate_visible_packet_sha256"],
            "blocking_stratum_source": DEAL_ID,
            "deal_score_sha256": assignment["deal_score_sha256"],
            "deal_rank": assignment["deal_rank"],
        })

    pool = {
        "schema": POOL_SCHEMA,
        "successor_frame_sha256": builder._frozen_validator().EXPECTED_SUCCESSOR_FRAME_SHA256,
        "source_family_n": len(source_frame),
        "eligible_cluster_n": len(clusters),
        "pending_external_curator_n": 0,
        "stratum_adjudicated_cluster_n": len(clusters),
        "blocking_stratum_assignment": {
            "deal_id": DEAL_ID,
            "rule_sha256_input": "descriptor-side frozen frame values only (workflow_id, versions, licences, before/after normalized digests)",
            "assignments_sha256": deal_mod.assignments_digest(assignments),
            "stratum_counts": dict(sorted(Counter(a["stratum"] for a in assignments).items())),
            "outcome_blind_by_construction": True,
        },
        "external_semantic_adjudication": (
            "external curator semantic adjudication (stratum review and the escrowed "
            "REUSE/REOPEN/CANNOT_CHECK gold) remains out of house and pending; this pool carries "
            "the preregistered blocking stratum label only"
        ),
        "member_manifest_freeze_v3": {
            "normalization_id": builder.V3_NORMALIZATION_ID,
            "present": True,
            "bound": False,
            "result_terminal": substrate["result_terminal"],
            "result_sha256": substrate["result_sha256"],
            "v3_reproducible_n": substrate["v3_reproducible_n"],
            "v3_nonreproducible_workflow_ids": substrate["v3_nonreproducible_workflow_ids"],
            "v3_content_only_before_after_equal_workflow_ids": substrate["v3_content_only_before_after_equal_workflow_ids"],
            "v2_aggregate_reproduces_frozen_frame_n": substrate["v2_aggregate_reproduces_frozen_frame_n"],
            "state": substrate["state"],
        },
        "gold_escrow": "adjudication targets remain escrowed with the external curator; no gold value is present in this pool",
        "protected_outcomes_accessed": False,
        "candidate_predictions_accessed": False,
        "stratum_adjudication_completed_before_candidate_predictions": True,
        "clusters": clusters,
    }
    _assert_gold_free(pool)
    return pool


def _assert_gold_free(pool: dict[str, Any]) -> None:
    for row in pool["clusters"]:
        bad = set(GOLD_KEYS) & set(row)
        if bad:
            raise ValueError(f"gold-bearing field entered the eligible pool: {sorted(bad)}")


def _self_test() -> dict[str, Any]:
    allocator = _allocator()
    pool = build()

    if pool["eligible_cluster_n"] != 128 or pool["pending_external_curator_n"] != 0:
        raise AssertionError("blocking-deal pool did not cover the full frozen frame")
    counts = Counter(c["stratum"] for c in pool["clusters"])
    if dict(sorted(counts.items())) != {s: 32 for s in sorted(STRATA)}:
        raise AssertionError(f"pool stratum coverage is not 32/32/32/32: {dict(counts)}")
    v3_block = pool["member_manifest_freeze_v3"]
    if v3_block.get("bound") is not False or v3_block.get("result_terminal") != V3_FAILURE_TERMINAL:
        raise AssertionError("v3 boundary block is not the recorded-not-bound failure terminal")
    if any(("before_manifest_v3_sha256" in c) or ("after_manifest_v3_sha256" in c) for c in pool["clusters"]):
        raise AssertionError("unbound v3 aggregates leaked onto pool rows")

    # Frozen allocator over the built pool: the full 96+32 selection.
    allocation = allocator.allocate(pool)
    if allocation["terminal"] != ALLOCATION_TERMINAL:
        raise AssertionError(f"allocation terminal: {allocation['terminal']}")
    if allocation["selected_n"] != 128 or allocation["counts"] != {s: {"primary": 24, "replication": 8} for s in STRATA}:
        raise AssertionError("blocking-deal allocation did not reach 96 primary + 32 replication")
    # Determinism under pool row permutation and across rebuilds.
    shuffled = json.loads(json.dumps(pool))
    shuffled["clusters"].reverse()
    if allocator.allocate(shuffled)["selection_manifest_sha256"] != allocation["selection_manifest_sha256"]:
        raise AssertionError("allocation is not invariant to pool row order")
    if json.dumps(build(), sort_keys=True) != json.dumps(pool, sort_keys=True):
        raise AssertionError("pool build is not deterministic")

    # Gold must be rejected by the frozen allocator even if injected here.
    poisoned = json.loads(json.dumps(pool))
    poisoned["clusters"][0]["gold"] = "REOPEN"
    try:
        allocator.validate_pool(poisoned)
    except ValueError as exc:
        assert "forbidden" in str(exc)
    else:
        raise AssertionError("gold-bearing pool accepted by the frozen allocator")

    # Quota consequence (forcing arithmetic): bare census organizations cannot
    # satisfy global lineage uniqueness, so a bare-org pool must fail the frozen
    # allocator closed rather than rebalance.
    bare = json.loads(json.dumps(pool))
    for row in bare["clusters"]:
        row["normalized_organization_lineage"] = row["normalized_organization_lineage"].rsplit(":family:", 1)[0]
    if len({r["normalized_organization_lineage"] for r in bare["clusters"]}) != 33:
        raise AssertionError("bare-org control no longer exhibits the 33-org premise")
    bare_alloc = allocator.allocate(bare)
    if bare_alloc["terminal"] != SHORTFALL_TERMINAL:
        raise AssertionError("bare-org pool must fail the frozen allocator closed")
    if bare_alloc["selected_n"] >= 128:
        raise AssertionError("bare-org pool must lose selections to lineage collisions")

    # Stratum tamper control: moving one cluster across strata must break the quota.
    moved = json.loads(json.dumps(pool))
    moved["clusters"][0]["stratum"] = STRATA[1] if moved["clusters"][0]["stratum"] != STRATA[1] else STRATA[0]
    moved_counts = Counter(c["stratum"] for c in moved["clusters"])
    if allocator.allocate(moved)["terminal"] != SHORTFALL_TERMINAL:
        raise AssertionError("stratum-tampered pool must fail the frozen allocator closed")

    # v3 substrate tamper control: a hostile successful-substrate swap is not consumable here.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        builder = _pool_builder()
        source_frame = builder._frozen_validator().load_source_frame()
        synthetic = builder._synthetic_v3_freeze_dir(source_frame, base)
        del synthetic
        try:
            build(v3_base_dir=base)
        except ValueError:
            v3_success_substrate_rejected = True
        else:
            raise AssertionError("a materialized v3 success substrate was consumed by the blocking-deal builder")

    return {
        "decision": "GREEN",
        "pool_schema": POOL_SCHEMA,
        "eligible_cluster_n": pool["eligible_cluster_n"],
        "stratum_counts": dict(sorted(counts.items())),
        "allocation_terminal": allocation["terminal"],
        "allocation_selected_n": allocation["selected_n"],
        "allocation_selection_manifest_sha256": allocation["selection_manifest_sha256"],
        "member_manifest_v3_boundary": "recorded_not_bound",
        "bare_org_lineage_fails_closed": True,
        "stratum_tamper_fails_closed": True,
        "v3_success_substrate_rejected": v3_success_substrate_rejected,
        "gold_never_enters_pool": True,
        "deterministic_rebuild": True,
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
        result = build()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
