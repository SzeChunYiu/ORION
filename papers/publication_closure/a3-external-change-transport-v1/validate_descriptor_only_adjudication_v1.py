#!/usr/bin/env python3
"""Validate A3_DESCRIPTOR_ONLY_ADJUDICATION_V1 and its committed evidence.

Fail-closed checker for the descriptor-only adjudication record:

- Freeze-document mode: the record JSON must carry the exact adjudication
  identity (three families bound to the frozen v3 failure partition, 3 fetches
  per family per version, the three-verdict vocabulary, zero free parameters),
  the executable and evidence digests must match the live bytes, every
  scientific-lineage binding must match the live file digest (proving this
  governance record modified no frozen artifact it adjudicated), the rebind
  decision must be the recorded NO with its rationale and mechanical
  evidence, the authority chain must record external non-self sign-off with
  self-promotion and self-sign-off false, and all custody flags must be false.
- Evidence mode: the committed EVIDENCE_V1.json must bind the frozen v3
  failure result and successor frame, cover exactly the three families, carry
  a re-verified collapse, and every per-family verdict must be the verdict the
  pre-registered rule mechanically yields from that family's own evidence;
  the record's verdicts must equal the evidence verdicts. The v3 freeze
  directory must contain no snapshot (there is no substrate to rebind to),
  cross-checked two ways.
- The frozen adjudicator and the frozen v3 normalization must pass their own
  networkless self-tests inside this check.
- Mechanical quota consequence: a synthetic pool over the frozen frame minus
  the three families fails the frozen allocator closed with the shortfall
  terminal, proving the 125-family consequence recorded in the rebind
  rationale.
Self-test only; mutation controls give the checks teeth.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

RECORD_SCHEMA = "ORION.A3.DescriptorOnlyAdjudication.v1"
EVIDENCE_SCHEMA = "ORION.A3.DescriptorOnlyAdjudicationEvidence.v1"
FAMILIES = ["106", "360", "384"]
VERDICTS = {
    "DESCRIPTOR_SHOWS_VERSION_PINNED_TRANSITION",
    "REQUEST_GENERATION_ARTIFACT",
    "CANNOT_DISTINGUISH",
}
REQUIRED_FALSE_FLAGS = (
    "successor_frame_rebound",
    "change_stratum_adjudicated",
    "external_gold_accessed",
    "candidate_predictions_computed",
    "protected_outcomes_accessed",
    "eligible_pool_modified",
    "frozen_executables_modified",
)
SHORTFALL_TERMINAL = "CANNOT_CHECK_A3_PREOUTCOME_QUOTA_OR_DISJOINTNESS_SHORTFALL"
ALLOCATION_TERMINAL = "A3_PREOUTCOME_PRIMARY_REPLICATION_ALLOCATION_FROZEN"
V3_FREEZE_DIRNAME = "workflowhub-member-manifest-freeze-v3"


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot import frozen module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rule_verdict(fam: dict[str, Any]) -> str:
    """The pre-registered verdict rule applied to one evidence family row."""
    pinned = bool(fam["version_pinned_differing_paths"]) or bool(fam["version_pinned_graph_nodes"])
    cross = bool(fam["cross_version_differing_paths_in_every_pair"])
    if fam["collapse_reverified_in_run"] is not True:
        return "CANNOT_DISTINGUISH"
    if pinned:
        return "DESCRIPTOR_SHOWS_VERSION_PINNED_TRANSITION"
    if not cross:
        return "REQUEST_GENERATION_ARTIFACT"
    return "CANNOT_DISTINGUISH"


def check_no_v3_substrate(v3_dir: Path) -> None:
    """No snapshot exists to rebind to; absence cross-checked two ways."""
    if (v3_dir / "SNAPSHOT_V3.json").is_file():
        raise ValueError("a v3 snapshot exists: the no-substrate premise of the no-rebind decision is false")
    json_files = sorted(p.name for p in v3_dir.glob("*.json")) if v3_dir.is_dir() else []
    if json_files != ["RESULT_V3.json"]:
        raise ValueError(f"unexpected v3 freeze directory contents: {json_files}")


def check_record(root: Path) -> dict[str, Any]:
    """Freeze-document + evidence mode over the live tree rooted at `root`."""
    a3 = root / "papers" / "publication_closure" / "a3-external-change-transport-v1"
    record = json.loads((a3 / "A3_DESCRIPTOR_ONLY_ADJUDICATION_V1.json").read_text(encoding="utf-8"))
    if record.get("schema") != RECORD_SCHEMA:
        raise ValueError("record schema mismatch")
    if record.get("artifact_class") != "FROZEN_GOVERNANCE_ADJUDICATION_OF_V3_DESCRIPTOR_ONLY_COLLAPSE":
        raise ValueError("record artifact_class mismatch")
    if not (root / str(record.get("decision_document", ""))).is_file():
        raise ValueError("decision document not present")
    if not str(record.get("purpose", "")).strip():
        raise ValueError("purpose must be recorded")

    ident = record.get("adjudication_identity")
    if not isinstance(ident, dict):
        raise ValueError("adjudication_identity must be an object")
    if ident.get("adjudication_id") != "A3_DESCRIPTOR_ONLY_ADJUDICATION_V1":
        raise ValueError("adjudication id mismatch")
    if ident.get("families") != FAMILIES:
        raise ValueError("families must be exactly the frozen v3 failure partition")
    if ident.get("fetches_per_family_version") != 3:
        raise ValueError("fetch count must mirror the frozen minimum of 3")
    if sorted(ident.get("verdict_vocabulary", [])) != sorted(VERDICTS):
        raise ValueError("verdict vocabulary mismatch")
    if ident.get("free_parameters") != [] or ident.get("run_time_resolution") != "NONE":
        raise ValueError("the adjudication must have zero free parameters")
    for key in ("comparison_method", "verdict_rule", "families_bound_to"):
        if not str(ident.get(key, "")).strip():
            raise ValueError(f"adjudication identity must record {key}")
    exe = root / str(ident.get("executable", ""))
    if not exe.is_file() or _digest(exe) != ident.get("executable_sha256"):
        raise ValueError("adjudicator digest does not match the frozen identity")

    execr = record.get("execution_record")
    if not isinstance(execr, dict):
        raise ValueError("execution_record must be an object")
    if "sbatch 3571474" not in str(execr.get("run_environment", "")):
        raise ValueError("execution record must bind the actual LUNARC sbatch run 3571474")
    if "/projects/hep/fs9/users/scyiu/orion-a3-v3/adjudication-20260903" not in str(execr.get("staging", "")):
        raise ValueError("staging must be the fs9 adjudication directory (never /home/scyiu)")
    evidence_path = root / str(execr.get("evidence_file", {}).get("path", ""))
    if not evidence_path.is_file() or _digest(evidence_path) != execr.get("evidence_file", {}).get("sha256"):
        raise ValueError("evidence file digest does not match the frozen execution record")
    if "never committed" not in str(execr.get("raw_descriptor_bytes", "")):
        raise ValueError("raw per-request descriptor bytes must be recorded as staged-only")

    verdicts = record.get("per_family_verdicts")
    if not isinstance(verdicts, dict) or sorted(verdicts) != sorted(FAMILIES):
        raise ValueError("per-family verdicts must cover exactly the three families")
    frame = _load("a3_curator_validator_adjv", a3 / "validate_external_curator_packet_v1.py").load_source_frame()
    for wid, entry in verdicts.items():
        if entry.get("verdict") not in VERDICTS:
            raise ValueError(f"family {wid}: verdict outside the frozen vocabulary")
        row = frame[wid]
        expected_pair = f"{row['version_before']}->{row['version_after']}"
        if entry.get("version_pair") != expected_pair:
            raise ValueError(f"family {wid}: version pair {entry.get('version_pair')} != frozen frame {expected_pair}")
        if not str(entry.get("evidence", "")).strip():
            raise ValueError(f"family {wid}: evidence must be recorded")

    rebind = record.get("successor_frame_rebind_decision")
    if not isinstance(rebind, dict):
        raise ValueError("successor_frame_rebind_decision must be an object")
    if rebind.get("rebind_v3_aggregates") is not False:
        raise ValueError("this record's frozen decision is NO_REBIND; a rebind requires a new governed record")
    if rebind.get("decision") != "NO_REBIND__V2_BOUND_FRAME_REMAINS_THE_ADMISSION_AUTHORITY":
        raise ValueError("rebind decision id mismatch")
    if len(rebind.get("rationale", [])) < 4:
        raise ValueError("the four recorded no-rebind rationales must be present")
    mech = rebind.get("mechanical_evidence", {})
    for key in ("no_v3_snapshot_exists", "quota_shortfall_under_125_family_frame", "pool_machinery_rerun"):
        if not str(mech.get(key, "")).strip():
            raise ValueError(f"mechanical evidence must record {key}")
    if len(rebind.get("what_would_license_a_future_rebind", [])) < 4:
        raise ValueError("the future-rebind preconditions must be recorded")

    limits = record.get("licenses_and_limits", {})
    if len(limits.get("licenses", [])) < 3 or len(limits.get("does_not_license", [])) < 4:
        raise ValueError("licenses and limits must both be recorded")

    lineage = record.get("scientific_lineage_bound_verbatim")
    if not isinstance(lineage, dict) or len(lineage) < 9:
        raise ValueError("scientific lineage must bind the adjudicated frozen artifacts")
    for name, binding in lineage.items():
        path = root / str(binding.get("path", ""))
        if not path.is_file():
            raise ValueError(f"lineage artifact absent: {name}")
        if _digest(path) != binding.get("sha256"):
            raise ValueError(f"lineage digest mismatch for {name}: this record must not modify what it adjudicates")

    chain = record.get("authority_chain")
    if not isinstance(chain, dict):
        raise ValueError("authority_chain must be an object")
    if chain.get("self_promotion_performed") is not False or chain.get("self_sign_off_performed") is not False:
        raise ValueError("self-promotion and self-sign-off must be explicitly false")
    sign_off = chain.get("sign_off", {})
    if sign_off.get("required") is not True or "external" not in str(sign_off.get("nature", "")):
        raise ValueError("sign-off must be recorded as external and non-self")
    if len(sign_off.get("acts", [])) < 2:
        raise ValueError("the external sign-off acts must be recorded")
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

    # Evidence mode: the committed evidence must satisfy the frozen rule internally.
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if evidence.get("schema") != EVIDENCE_SCHEMA:
        raise ValueError("evidence schema mismatch")
    if evidence.get("adjudication_id") != "A3_DESCRIPTOR_ONLY_ADJUDICATION_V1":
        raise ValueError("evidence adjudication id mismatch")
    if evidence.get("successor_frame_sha256") != "a47d9255aa37de056cb5cdd7c140bcccb487aa3285790655a48abb5e538c2993":
        raise ValueError("evidence does not bind the frozen successor frame")
    if "sbatch 3571474" not in str(evidence.get("run_environment", "")):
        raise ValueError("evidence run environment does not bind the same governed sbatch run 3571474")
    bound = evidence.get("bound_v3_failure_result", {})
    v3_result = json.loads((a3 / V3_FREEZE_DIRNAME / "RESULT_V3.json").read_text(encoding="utf-8"))
    if bound.get("terminal") != v3_result.get("terminal") != "CANNOT_CHECK_MEMBER_MANIFEST_V3_REPRODUCIBILITY":
        raise ValueError("evidence does not bind the frozen v3 failure terminal")
    if bound.get("v3_content_only_before_after_equal_workflow_ids") != v3_result["partition"]["v3_content_only_before_after_equal_workflow_ids"]:
        raise ValueError("evidence does not bind the frozen v3 collapse partition")
    rows = evidence.get("families", [])
    if [r["workflow_id"] for r in rows] != FAMILIES:
        raise ValueError("evidence families mismatch")
    for row in rows:
        wid = row["workflow_id"]
        expected = _rule_verdict(row)
        if row.get("verdict") != expected:
            raise ValueError(f"family {wid}: evidence verdict {row.get('verdict')!r} is not what the frozen rule yields ({expected!r})")
        if verdicts[wid]["verdict"] != row["verdict"]:
            raise ValueError(f"family {wid}: record verdict does not equal evidence verdict")
        for side in ("before", "after"):
            if row[side]["v3_aggregate_stable_across_fetches"] is not True:
                raise ValueError(f"family {wid}: {side} v3 aggregate unstable across fetches")
            if row[side]["fetches"][0].get("excluded_paths") != ["ro-crate-metadata.json", "ro-crate-preview.html"]:
                raise ValueError(f"family {wid}: {side} excluded member set mismatch")
        if row["before"]["fetches"][0]["v3_aggregate"] != row["after"]["fetches"][0]["v3_aggregate"]:
            raise ValueError(f"family {wid}: evidence does not show the collapse being adjudicated")

    check_no_v3_substrate(a3 / V3_FREEZE_DIRNAME)
    return {
        "decision": "GREEN",
        "record_schema": RECORD_SCHEMA,
        "families": FAMILIES,
        "verdicts": {wid: verdicts[wid]["verdict"] for wid in FAMILIES},
        "rebind_decision": rebind["decision"],
        "lineage_bindings_n": len(lineage),
        "evidence_sha256": execr["evidence_file"]["sha256"],
        "no_v3_substrate": True,
        "self_promotion_performed": False,
    }


def quota_consequence() -> dict[str, Any]:
    """Mechanical proof of the recorded 125-family consequence."""
    pool_mod = _load("a3_pool_adjv", HERE / "build_eligible_change_cluster_pool_v1.py")
    packets, source_frame = pool_mod._synthetic_batch()
    keep = [p for p in packets if str(p["source"]["workflow_id"]) not in FAMILIES]
    dropped_pool = pool_mod.build(keep)
    if dropped_pool["pending_external_curator_n"] != 3:
        raise ValueError("expected exactly the three descriptor-only families to be pending")
    alloc = pool_mod._frozen_allocator().allocate(dropped_pool)
    if alloc["terminal"] != SHORTFALL_TERMINAL:
        raise ValueError(f"125-family pool must fail the frozen allocator closed, got {alloc['terminal']}")
    full = pool_mod.build(packets)
    if pool_mod._frozen_allocator().allocate(full)["terminal"] != ALLOCATION_TERMINAL:
        raise ValueError("full-frame control must still allocate (teeth for the shortfall check)")
    return {
        "dropped_families": FAMILIES,
        "dropped_terminal": alloc["terminal"],
        "full_frame_control_terminal": ALLOCATION_TERMINAL,
    }


def self_test() -> dict[str, Any]:
    result = check_record(ROOT)

    # The frozen adjudicator and the frozen v3 normalization pass their own checks.
    adj = _load("a3_adjudicator_adjv", HERE / "adjudicate_descriptor_only_families_v1.py")
    if adj._self_test().get("decision") != "GREEN":
        raise ValueError("frozen adjudicator self-test not green")
    v3norm = _load("a3_v3norm_adjv", HERE / "normalize_member_manifests_v3.py")
    if v3norm.self_test().get("decision") != "GREEN":
        raise ValueError("frozen v3 normalization self-test not green")

    quota = quota_consequence()

    # Mutation controls over a temp copy of the live tree (each must fail closed).
    def mutate(fn) -> str:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "papers" / "publication_closure").mkdir(parents=True)
            shutil.copytree(HERE, root / "papers" / "publication_closure" / "a3-external-change-transport-v1")
            fn(root)
            try:
                check_record(root)
            except ValueError:
                return "rejected"
            raise AssertionError(f"mutation accepted: {fn.__name__}")

    def flip_rebind(root: Path) -> None:
        p = root / "papers/publication_closure/a3-external-change-transport-v1/A3_DESCRIPTOR_ONLY_ADJUDICATION_V1.json"
        d = json.loads(p.read_text())
        d["successor_frame_rebind_decision"]["rebind_v3_aggregates"] = True
        p.write_text(json.dumps(d))

    def flip_verdict(root: Path) -> None:
        p = root / "papers/publication_closure/a3-external-change-transport-v1/A3_DESCRIPTOR_ONLY_ADJUDICATION_V1.json"
        d = json.loads(p.read_text())
        d["per_family_verdicts"]["384"]["verdict"] = "REQUEST_GENERATION_ARTIFACT"
        p.write_text(json.dumps(d))

    def tamper_lineage(root: Path) -> None:
        p = root / "papers/publication_closure/a3-external-change-transport-v1/A3_DESCRIPTOR_ONLY_ADJUDICATION_V1.json"
        d = json.loads(p.read_text())
        d["scientific_lineage_bound_verbatim"]["candidate_policy_executable"]["sha256"] = "0" * 64
        p.write_text(json.dumps(d))

    def tamper_evidence_bytes(root: Path) -> None:
        p = root / "papers/publication_closure/a3-external-change-transport-v1/workflowhub-descriptor-only-adjudication-v1/EVIDENCE_V1.json"
        p.write_bytes(p.read_bytes() + b"\n")

    def tamper_evidence_verdict(root: Path) -> None:
        p = root / "papers/publication_closure/a3-external-change-transport-v1/workflowhub-descriptor-only-adjudication-v1/EVIDENCE_V1.json"
        d = json.loads(p.read_text())
        d["families"][2]["verdict"] = "CANNOT_DISTINGUISH"
        p.write_text(json.dumps(d))

    def flip_flag(root: Path) -> None:
        p = root / "papers/publication_closure/a3-external-change-transport-v1/A3_DESCRIPTOR_ONLY_ADJUDICATION_V1.json"
        d = json.loads(p.read_text())
        d["flags"]["successor_frame_rebound"] = True
        p.write_text(json.dumps(d))

    def plant_snapshot(root: Path) -> None:
        d = root / "papers/publication_closure/a3-external-change-transport-v1/workflowhub-member-manifest-freeze-v3"
        (d / "SNAPSHOT_V3.json").write_text("{}")

    def self_sign(root: Path) -> None:
        p = root / "papers/publication_closure/a3-external-change-transport-v1/A3_DESCRIPTOR_ONLY_ADJUDICATION_V1.json"
        d = json.loads(p.read_text())
        d["authority_chain"]["self_sign_off_performed"] = True
        p.write_text(json.dumps(d))

    rejected = [mutate(fn) for fn in (flip_rebind, flip_verdict, tamper_lineage, tamper_evidence_bytes, tamper_evidence_verdict, flip_flag, plant_snapshot, self_sign)]
    if set(rejected) != {"rejected"}:
        raise AssertionError("a mutation control did not run")

    return {
        **result,
        "quota_consequence": quota,
        "mutation_controls_all_rejected": True,
        "mutation_controls_n": len(rejected),
        "frozen_self_tests_green": True,
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
