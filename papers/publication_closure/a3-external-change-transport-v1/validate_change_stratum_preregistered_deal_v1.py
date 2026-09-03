#!/usr/bin/env python3
"""Validate A3_CHANGE_STRATUM_PREREGISTERED_DEAL_V1 and its committed evidence.

Fail-closed checker for the preregistered outcome-blind blocking-stratum deal
and the allocation it feeds:

- Freeze-document mode: the governance record must carry the exact deal
  identity (rule, ordering, assignment step, zero free parameters, no
  run-time resolution), executable digests must match the live bytes, the
  execution record must bind the actual billy-laptop-old run with rc 0 for
  every command, every committed output digest must match, every
  scientific-lineage binding must match the live file digest (proving this
  governance package modified no frozen artifact), the authority chain must
  record external non-self sign-off with self-promotion and self-sign-off
  false, and all custody flags must be false.
- Evidence mode: the committed ASSIGNMENTS_V1.json must equal, row for row,
  what the frozen rule re-derives from the committed frame and census; the
  committed pool must be byte-identical to a fresh build; the committed
  allocation must equal what the frozen allocator re-derives over the
  committed pool (terminal, 24/8 per stratum, selection manifest digest,
  membership lists); strata must be 32/32/32/32.
- Quota consequence: a bare census-organization lineage pool must fail the
  frozen allocator closed, proving the recorded cluster-granularity forcing
  arithmetic (33 distinct organizations < 128 required distinct lineages).
- The deal module and the pool builder must pass their own networkless
  self-tests inside this check.
Self-test only; mutation controls over tempdir tree copies give the checks
teeth (green inputs pass, deliberate tampers raise).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

RECORD_SCHEMA = "ORION.A3.ChangeStratumPreregisteredDeal.v1"
EVIDENCE_SCHEMA = "ORION.A3.ChangeStratumPreregisteredDealAssignments.v1"
POOL_SCHEMA = "ORION.A3.EligibleChangeClusterPool.v1"
ALLOCATION_SCHEMA = "ORION.A3.ChangeClusterPreOutcomeAllocation.v1"
DEAL_ID = "A3_CHANGE_STRATUM_PREREGISTERED_DEAL_V1"
FRAME_SHA256 = "a47d9255aa37de056cb5cdd7c140bcccb487aa3285790655a48abb5e538c2993"
CENSUS_MANIFEST_SHA256 = "1eef635eafb387fe7d5a60fb32476a3597ac019392b7e5de23478db3977fcd52"
STRATA = (
    "representation_schema",
    "responsibility_output_contract",
    "objective_acceptance_criterion",
    "evidence_dependency",
)
ALLOCATION_TERMINAL = "A3_PREOUTCOME_PRIMARY_REPLICATION_ALLOCATION_FROZEN"
SHORTFALL_TERMINAL = "CANNOT_CHECK_A3_PREOUTCOME_QUOTA_OR_DISJOINTNESS_SHORTFALL"
REQUIRED_FALSE_FLAGS = (
    "external_gold_accessed",
    "candidate_predictions_computed",
    "protected_outcomes_accessed",
    "eligible_pool_modified",
    "frozen_executables_modified",
    "external_semantic_adjudication_performed",
    "scientific_judgment_made",
)
A3_DIR_REL = "papers/publication_closure/a3-external-change-transport-v1"
A6_CENSUS_REL = "papers/publication_closure/a6-external-authority-study-v1/workflowhub-census-v1"


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_record(root: Path) -> dict[str, Any]:
    a3 = root / A3_DIR_REL
    record = json.loads((a3 / "A3_CHANGE_STRATUM_PREREGISTERED_DEAL_V1.json").read_text(encoding="utf-8"))
    if record.get("schema") != RECORD_SCHEMA:
        raise ValueError("record schema mismatch")
    if record.get("artifact_class") != "FROZEN_GOVERNANCE_PREREGISTERED_OUTCOME_BLIND_STRATUM_DEAL":
        raise ValueError("record artifact_class mismatch")
    if not (root / str(record.get("decision_document", ""))).is_file():
        raise ValueError("decision document not present")
    if not str(record.get("purpose", "")).strip():
        raise ValueError("purpose must be recorded")

    ident = record.get("deal_identity")
    if not isinstance(ident, dict):
        raise ValueError("deal_identity must be an object")
    if ident.get("deal_id") != DEAL_ID:
        raise ValueError("deal id mismatch")
    for key in ("rule_score", "rule_ordering", "rule_assignment", "inputs", "scope"):
        if not str(ident.get(key, "")).strip():
            raise ValueError(f"deal identity must record {key}")
    if ident.get("free_parameters") != [] or ident.get("run_time_resolution") != "NONE":
        raise ValueError("the deal must have zero free parameters")
    if ident.get("outcome_blind_by_construction") is not True:
        raise ValueError("deal must be recorded as outcome-blind by construction")
    if ident.get("successor_frame_sha256") != FRAME_SHA256:
        raise ValueError("deal does not bind the frozen successor frame")
    exe = root / str(ident.get("executable", ""))
    if not exe.is_file() or _digest(exe) != ident.get("executable_sha256"):
        raise ValueError("deal executable digest does not match the frozen identity")
    builder_rel = ident.get("pool_builder_executable")
    builder = root / str(builder_rel)
    if not builder.is_file() or _digest(builder) != ident.get("pool_builder_executable_sha256"):
        raise ValueError("pool builder digest does not match the frozen identity")

    execr = record.get("execution_record")
    if not isinstance(execr, dict):
        raise ValueError("execution_record must be an object")
    if "billy-laptop-old" not in str(execr.get("run_environment", "")):
        raise ValueError("execution record must bind the actual billy-laptop-old run")
    commands = execr.get("commands")
    if not isinstance(commands, list) or len(commands) != 3:
        raise ValueError("execution record must bind the three run commands")
    for cmd in commands:
        if not str(cmd.get("cmd", "")).strip() or cmd.get("rc") != 0:
            raise ValueError(f"run command not green: {cmd}")
    for key, rel in (
        ("assignments", "blocking-stratum-deal-v1/ASSIGNMENTS_V1.json"),
        ("pool", "eligible-pool-v1/A3_ELIGIBLE_POOL_BLOCKING_DEAL_V1.json"),
        ("allocation", "allocation-v1/A3_PREOUTCOME_ALLOCATION_RESULT_V1.json"),
    ):
        entry = execr.get(key, {})
        path = root / str(entry.get("path", ""))
        if not path.is_file() or _digest(path) != entry.get("sha256"):
            raise ValueError(f"committed {key} digest does not match the frozen execution record")

    # Evidence mode: the committed assignments are exactly what the rule yields.
    evidence = json.loads((a3 / "blocking-stratum-deal-v1" / "ASSIGNMENTS_V1.json").read_text(encoding="utf-8"))
    if evidence.get("schema") != EVIDENCE_SCHEMA:
        raise ValueError("evidence schema mismatch")
    if evidence.get("deal_id") != DEAL_ID or evidence.get("successor_frame_sha256") != FRAME_SHA256:
        raise ValueError("evidence does not bind the deal and the frozen frame")
    if evidence.get("census_manifest_sha256") != CENSUS_MANIFEST_SHA256:
        raise ValueError("evidence does not bind the frozen A6 census manifest")
    if evidence.get("family_n") != 128:
        raise ValueError("evidence family count mismatch")
    counts = Counter(a["stratum"] for a in evidence["assignments"])
    if dict(sorted(counts.items())) != {s: 32 for s in sorted(STRATA)}:
        raise ValueError(f"evidence stratum deal is not 32/32/32/32: {dict(counts)}")
    deal_mod = _load("a3_deal_check", a3 / "assign_change_stratum_preregistered_deal_v1.py")
    rederived = deal_mod.deal()
    if evidence["assignments"] != rederived:
        raise ValueError("committed assignments differ from the frozen-rule re-derivation")
    if evidence.get("assignments_sha256") != deal_mod.assignments_digest(rederived):
        raise ValueError("evidence assignments digest mismatch")

    # Pool: committed bytes must be exactly a fresh build.
    pool_path = a3 / "eligible-pool-v1" / "A3_ELIGIBLE_POOL_BLOCKING_DEAL_V1.json"
    pool_mod = _load("a3_pool_deal_check", a3 / "build_eligible_change_cluster_pool_blocking_deal_v1.py")
    pool = json.loads(pool_path.read_text(encoding="utf-8"))
    if pool.get("schema") != POOL_SCHEMA:
        raise ValueError("pool schema mismatch")
    if pool.get("stratum_adjudication_completed_before_candidate_predictions") is not True:
        raise ValueError("pool does not freeze stratum adjudication before predictions")
    if pool.get("blocking_stratum_assignment", {}).get("deal_id") != DEAL_ID:
        raise ValueError("pool does not bind the preregistered deal")
    if pool.get("eligible_cluster_n") != 128 or pool.get("pending_external_curator_n") != 0:
        raise ValueError("pool does not materialize the full frame")
    rebuilt = pool_mod.build()
    if json.dumps(rebuilt, sort_keys=True) != json.dumps(pool, sort_keys=True):
        raise ValueError("committed pool differs from a fresh deterministic build")
    if json.dumps(rebuilt, indent=2, sort_keys=True) + "\n" != pool_path.read_text(encoding="utf-8"):
        raise ValueError("committed pool bytes are not the canonical serialization")

    # Allocation: the frozen allocator re-derives the committed result exactly.
    alloc_path = a3 / "allocation-v1" / "A3_PREOUTCOME_ALLOCATION_RESULT_V1.json"
    allocator = _load("a3_allocator_check", a3 / "allocate_change_clusters_v1.py")
    alloc = json.loads(alloc_path.read_text(encoding="utf-8"))
    if alloc.get("schema") != ALLOCATION_SCHEMA:
        raise ValueError("allocation schema mismatch")
    reallocated = allocator.allocate(pool)
    for key in ("terminal", "selected_n", "counts", "shortfalls", "selection_manifest_sha256"):
        if alloc.get(key) != reallocated.get(key):
            raise ValueError(f"committed allocation {key} differs from the frozen-allocator re-derivation")
    if alloc["terminal"] != ALLOCATION_TERMINAL or alloc["selected_n"] != 128:
        raise ValueError("committed allocation is not the frozen 128-selection terminal")
    if alloc["counts"] != {s: {"primary": 24, "replication": 8} for s in STRATA}:
        raise ValueError("committed allocation quotas are not 24/8 per stratum")
    if alloc.get("clusters") != reallocated.get("clusters"):
        raise ValueError("committed allocation membership differs from the re-derivation")
    if alloc.get("gold_present") is not False or alloc.get("protected_outcomes_accessed") is not False:
        raise ValueError("allocation must record gold/outcome absence")

    # Lineage bindings: this package must not have modified anything frozen.
    lineage = record.get("scientific_lineage_bound_verbatim")
    if not isinstance(lineage, dict) or len(lineage) < 8:
        raise ValueError("scientific lineage must bind the adjudicated frozen artifacts")
    for name, binding in lineage.items():
        path = root / str(binding.get("path", ""))
        if not path.is_file():
            raise ValueError(f"lineage artifact absent: {name}")
        if _digest(path) != binding.get("sha256"):
            raise ValueError(f"lineage digest mismatch for {name}: this record must not modify what it binds")

    chain = record.get("authority_chain")
    if not isinstance(chain, dict):
        raise ValueError("authority_chain must be an object")
    if chain.get("self_promotion_performed") is not False or chain.get("self_sign_off_performed") is not False:
        raise ValueError("self-promotion and self-sign-off must be explicitly false")
    sign_off = chain.get("sign_off", {})
    if sign_off.get("required") is not True or "external" not in str(sign_off.get("nature", "")):
        raise ValueError("sign-off must be recorded as external and non-self")
    if "never promotion" not in str(sign_off.get("semantics", "")):
        raise ValueError("sign-off semantics must state continuation-never-promotion")

    flags = record.get("flags", {})
    for flag in REQUIRED_FALSE_FLAGS:
        if flags.get(flag) is not False:
            raise ValueError(f"custody flag must be false: {flag}")
    if record.get("grants_scientific_authority") is not False:
        raise ValueError("the record must grant no scientific authority")
    if record.get("scientific_authority_delta") != "NONE__GOVERNANCE_ADJUDICATION_RECORD_ONLY":
        raise ValueError("scientific authority delta mismatch")

    return {
        "decision": "GREEN",
        "record_schema": RECORD_SCHEMA,
        "deal_id": DEAL_ID,
        "stratum_counts": dict(sorted(counts.items())),
        "allocation_terminal": alloc["terminal"],
        "allocation_selected_n": alloc["selected_n"],
        "allocation_selection_manifest_sha256": alloc["selection_manifest_sha256"],
        "assignments_sha256": evidence["assignments_sha256"],
        "lineage_bindings_n": len(lineage),
        "self_promotion_performed": False,
    }


def quota_consequence() -> dict[str, Any]:
    """Mechanical proof of the recorded cluster-granularity forcing arithmetic."""
    a3 = ROOT / A3_DIR_REL
    pool_mod = _load("a3_pool_deal_qc", a3 / "build_eligible_change_cluster_pool_blocking_deal_v1.py")
    allocator = _load("a3_allocator_qc", a3 / "allocate_change_clusters_v1.py")
    pool = pool_mod.build()
    for row in pool["clusters"]:
        row["normalized_organization_lineage"] = row["normalized_organization_lineage"].rsplit(":family:", 1)[0]
    distinct = {r["normalized_organization_lineage"] for r in pool["clusters"]}
    if len(distinct) != 33:
        raise ValueError("bare-org control no longer exhibits the 33-organization premise")
    bare = allocator.allocate(pool)
    if bare["terminal"] != SHORTFALL_TERMINAL:
        raise ValueError("bare census-organization lineage must fail the frozen allocator closed")
    full = pool_mod.build()
    if allocator.allocate(full)["terminal"] != ALLOCATION_TERMINAL:
        raise ValueError("cluster-granular control must still allocate (teeth for the bare-org check)")
    return {
        "distinct_bare_organizations": len(distinct),
        "required_distinct_lineages": 128,
        "bare_org_terminal": bare["terminal"],
        "cluster_granular_control_terminal": ALLOCATION_TERMINAL,
    }


def self_test() -> dict[str, Any]:
    result = check_record(ROOT)

    a3 = ROOT / A3_DIR_REL
    deal_mod = _load("a3_deal_st", a3 / "assign_change_stratum_preregistered_deal_v1.py")
    if deal_mod._self_test().get("decision") != "GREEN":
        raise ValueError("deal module self-test not green")
    pool_mod = _load("a3_pool_st", a3 / "build_eligible_change_cluster_pool_blocking_deal_v1.py")
    if pool_mod._self_test().get("decision") != "GREEN":
        raise ValueError("pool builder self-test not green")

    quota = quota_consequence()

    def mutate(fn) -> str:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "papers" / "publication_closure").mkdir(parents=True)
            shutil.copytree(ROOT / A3_DIR_REL, root / A3_DIR_REL)
            shutil.copytree(ROOT / A6_CENSUS_REL, root / A6_CENSUS_REL)
            fn(root)
            try:
                check_record(root)
            except ValueError:
                return "rejected"
        raise AssertionError(f"mutation accepted: {fn.__name__}")

    def record_path(root: Path) -> Path:
        return root / A3_DIR_REL / "A3_CHANGE_STRATUM_PREREGISTERED_DEAL_V1.json"

    def flip_assignment_stratum(root: Path) -> None:
        p = root / A3_DIR_REL / "blocking-stratum-deal-v1" / "ASSIGNMENTS_V1.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        d["assignments"][0]["stratum"] = STRATA[1] if d["assignments"][0]["stratum"] != STRATA[1] else STRATA[0]
        p.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def tamper_pool_bytes(root: Path) -> None:
        p = root / A3_DIR_REL / "eligible-pool-v1" / "A3_ELIGIBLE_POOL_BLOCKING_DEAL_V1.json"
        p.write_bytes(p.read_bytes() + b"\n")

    def tamper_allocation_membership(root: Path) -> None:
        p = root / A3_DIR_REL / "allocation-v1" / "A3_PREOUTCOME_ALLOCATION_RESULT_V1.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        d["clusters"][0]["split"] = "replication" if d["clusters"][0]["split"] == "primary" else "primary"
        p.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def tamper_census_bytes(root: Path) -> None:
        p = root / A6_CENSUS_REL / "ROWS_301_313.json"
        p.write_bytes(p.read_bytes() + b"\n")

    def tamper_lineage_digest(root: Path) -> None:
        p = record_path(root)
        d = json.loads(p.read_text(encoding="utf-8"))
        first = sorted(d["scientific_lineage_bound_verbatim"])[0]
        d["scientific_lineage_bound_verbatim"][first]["sha256"] = "0" * 64
        p.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def flip_flag(root: Path) -> None:
        p = record_path(root)
        d = json.loads(p.read_text(encoding="utf-8"))
        d["flags"]["protected_outcomes_accessed"] = True
        p.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def self_sign(root: Path) -> None:
        p = record_path(root)
        d = json.loads(p.read_text(encoding="utf-8"))
        d["authority_chain"]["self_sign_off_performed"] = True
        p.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def flip_run_rc(root: Path) -> None:
        p = record_path(root)
        d = json.loads(p.read_text(encoding="utf-8"))
        d["execution_record"]["commands"][0]["rc"] = 1
        p.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rejected = [mutate(fn) for fn in (
        flip_assignment_stratum, tamper_pool_bytes, tamper_allocation_membership,
        tamper_census_bytes, tamper_lineage_digest, flip_flag, self_sign, flip_run_rc,
    )]
    if set(rejected) != {"rejected"}:
        raise AssertionError("a mutation control did not run")

    return {
        **result,
        "quota_consequence": quota,
        "mutation_controls_all_rejected": True,
        "mutation_controls_n": len(rejected),
        "module_self_tests_green": True,
        "network_accessed": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
        return 0
    print(json.dumps(check_record(ROOT), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
