#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

STRATA = (
    "representation_schema",
    "responsibility_output_contract",
    "objective_acceptance_criterion",
    "evidence_dependency",
)
FORBIDDEN_KEYS = {"gold", "reuse_gold", "candidate_prediction", "baseline_prediction", "outcome"}


def _nonempty(row: dict[str, Any], key: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be a nonempty string")
    return value


def validate(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("schema") != "ORION.A3.ChangeClusterIntakeManifest.v1":
        raise ValueError("wrong schema")
    if payload.get("protected_outcomes_accessed") is not False:
        raise ValueError("intake manifest must precede protected outcomes")
    rows = payload.get("clusters")
    if not isinstance(rows, list):
        raise ValueError("clusters must be list")
    seen: set[str] = set()
    primary: list[dict[str, Any]] = []
    repl: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("cluster must be object")
        if FORBIDDEN_KEYS & set(row):
            raise ValueError(f"outcome/gold field present in pre-gold manifest: {sorted(FORBIDDEN_KEYS & set(row))}")
        cid = _nonempty(row, "cluster_id")
        if cid in seen:
            raise ValueError(f"duplicate cluster_id: {cid}")
        seen.add(cid)
        if row.get("split") not in ("primary", "replication"):
            raise ValueError("split must be primary/replication")
        if row.get("stratum") not in STRATA:
            raise ValueError("bad stratum")
        for key in (
            "source_family_id", "normalized_organization_lineage", "artifact_lineage_id",
            "before_version_id", "after_version_id", "before_sha256", "after_sha256",
            "license_or_rights_receipt_id", "curator_assignment_receipt_id",
        ):
            _nonempty(row, key)
        if row["before_sha256"] == row["after_sha256"]:
            raise ValueError("before/after bytes must differ for a change cluster")
        if row.get("candidate_visible_packet_frozen") is not True:
            raise ValueError("candidate-visible packet must be frozen at intake")
        (primary if row["split"] == "primary" else repl).append(row)
    pc = Counter(r["stratum"] for r in primary)
    rc = Counter(r["stratum"] for r in repl)
    quota_ok = len(primary) == 96 and len(repl) == 32 and all(pc[s] == 24 and rc[s] == 8 for s in STRATA)
    if not quota_ok:
        raise ValueError(f"quota mismatch primary={dict(pc)} replication={dict(rc)}")
    for key in ("source_family_id", "normalized_organization_lineage", "artifact_lineage_id"):
        overlap = sorted({r[key] for r in primary} & {r[key] for r in repl})
        if overlap:
            raise ValueError(f"primary/replication {key} overlap: {overlap[:5]}")
    return {
        "schema": "ORION.A3.ChangeClusterIntakeValidation.v1",
        "decision": "GREEN",
        "primary_n": 96,
        "replication_n": 32,
        "primary_counts": {s: pc[s] for s in STRATA},
        "replication_counts": {s: rc[s] for s in STRATA},
        "outcome_fields_present": False,
        "source_disjoint": True,
    }


def fixture() -> dict[str, Any]:
    rows = []
    n = 0
    for split, per in (("primary", 24), ("replication", 8)):
        for s in STRATA:
            for _ in range(per):
                cid = f"{split}-{n}"
                rows.append({
                    "cluster_id": cid, "split": split, "stratum": s,
                    "source_family_id": f"sf-{cid}", "normalized_organization_lineage": f"org-{cid}",
                    "artifact_lineage_id": f"art-{cid}", "before_version_id": f"b-{cid}", "after_version_id": f"a-{cid}",
                    "before_sha256": f"before-{cid}", "after_sha256": f"after-{cid}",
                    "license_or_rights_receipt_id": f"rights-{cid}", "curator_assignment_receipt_id": f"curator-{cid}",
                    "candidate_visible_packet_frozen": True,
                })
                n += 1
    return {"schema": "ORION.A3.ChangeClusterIntakeManifest.v1", "protected_outcomes_accessed": False, "clusters": rows}


def self_test() -> dict[str, Any]:
    good = fixture()
    result = validate(good)
    bad = fixture(); bad["clusters"][0]["gold"] = "REOPEN"
    try: validate(bad)
    except ValueError as exc: assert "outcome/gold" in str(exc)
    else: raise AssertionError("gold-field mutant accepted")
    bad2 = fixture(); bad2["clusters"][-1]["source_family_id"] = bad2["clusters"][0]["source_family_id"]
    try: validate(bad2)
    except ValueError as exc: assert "overlap" in str(exc)
    else: raise AssertionError("source-overlap mutant accepted")
    return {"decision": "GREEN", "validated": result}


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("input", nargs="?", type=Path); ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), indent=2, sort_keys=True)); return 0
    if args.input is None: ap.error("input required unless --self-test")
    print(json.dumps(validate(json.loads(args.input.read_text())), indent=2, sort_keys=True)); return 0

if __name__ == "__main__": raise SystemExit(main())
