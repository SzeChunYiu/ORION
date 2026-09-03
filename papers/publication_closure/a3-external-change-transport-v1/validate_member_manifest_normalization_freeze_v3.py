#!/usr/bin/env python3
"""Validate WORKFLOWHUB_MEMBER_MANIFEST_NORMALIZATION_FREEZE_V3 and its harvest result.

Fail-closed checker for the v3 member-manifest normalization freeze:

- Freeze-document mode (always): the freeze JSON must carry the exact
  normalization identity (zero free parameters, the two request-generated root
  members and only those, v2 imported verbatim), the executable digests must
  match the live bytes, every scientific-lineage binding must match the live
  file digest, all custody flags must be false, and no scientific authority is
  granted. The frozen normalization and the frozen harvester must both pass
  their own networkless self-tests inside this check.
- Result mode (once workflowhub-member-manifest-freeze-v3/RESULT_V3.json
  exists): the terminal must be one of the two frozen terminals, the result
  must bind the frozen successor frame exactly, the partition must be
  internally consistent and exactly cover the 128 families, the v2
  cross-check counts must match the rows, a success must have byte-verified
  chunks covering every frame family with before != after v3 aggregates that
  the frozen candidate policy consumes, and a failure must have emitted
  nothing. Self-test only.
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
FREEZE_PATH = HERE / "WORKFLOWHUB_MEMBER_MANIFEST_NORMALIZATION_FREEZE_V3.json"
RESULT_DIR = HERE / "workflowhub-member-manifest-freeze-v3"
RESULT_PATH = RESULT_DIR / "RESULT_V3.json"

FREEZE_SCHEMA = "ORION.A3.WorkflowHubMemberManifestNormalizationFreeze.v3"
RESULT_SCHEMA = "ORION.A3.MemberManifestFreezeResult.v3"
SNAPSHOT_SCHEMA = "ORION.A3.MemberManifestFreezeSnapshot.v3"
CHUNK_SCHEMA = "ORION.A3.MemberManifestFreezeChunk.v3"
SUCCESS_TERMINAL = "WORKFLOWHUB_MEMBER_MANIFEST_V3_REPRODUCIBLE_FROZEN"
FAILURE_TERMINAL = "CANNOT_CHECK_MEMBER_MANIFEST_V3_REPRODUCIBILITY"
EXCLUDED_MEMBERS = ["ro-crate-metadata.json", "ro-crate-preview.html"]
REQUIRED_FALSE_FLAGS = (
    "successor_frame_rebound",
    "change_stratum_adjudicated",
    "external_gold_accessed",
    "candidate_predictions_computed",
    "protected_outcomes_accessed",
    "v3_harvest_executed",
    "member_manifests_committed",
)


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


def validate_freeze(doc: dict[str, Any]) -> None:
    if doc.get("schema") != FREEZE_SCHEMA:
        raise ValueError("freeze schema mismatch")
    if doc.get("artifact_class") != "FROZEN_BEFORE_V3_HARVEST_AND_SUCCESSOR_FRAME_REBIND":
        raise ValueError("freeze artifact_class must state frozen-before-harvest")
    decision = Path(str(doc.get("decision_document", "")))
    if not (ROOT / decision).is_file():
        raise ValueError("decision document not present in the repository")

    identity = doc.get("normalization_identity")
    if not isinstance(identity, dict):
        raise ValueError("normalization_identity must be an object")
    if identity.get("normalization_id") != "WORKFLOWHUB_MEMBER_MANIFEST_NORMALIZATION_V3":
        raise ValueError("normalization id mismatch")
    if sorted(identity.get("request_generated_root_members_excluded", [])) != sorted(EXCLUDED_MEMBERS):
        raise ValueError("excluded member set must be exactly the two request-generated crate files")
    rule = str(identity.get("rule", ""))
    if not rule or not all(member in rule for member in EXCLUDED_MEMBERS):
        raise ValueError("rule must name both excluded members")
    if identity.get("free_parameters") != []:
        raise ValueError("the frozen normalization must have zero free parameters")
    if identity.get("run_time_resolution") != "NONE":
        raise ValueError("run_time_resolution must be NONE")
    if identity.get("v2_normalization_imported_verbatim") is not True:
        raise ValueError("the v2 normalization must be imported verbatim")
    if not str(identity.get("exclusion_scope", "")).strip():
        raise ValueError("exclusion_scope must be recorded")
    structural = identity.get("structural_requirements_retained_verbatim")
    if not isinstance(structural, list) or not structural:
        raise ValueError("structural requirements must be retained and listed")

    exe = Path(str(identity.get("executable", "")))
    if not (ROOT / exe).is_file():
        raise ValueError("normalization executable not present")
    if _digest(ROOT / exe) != identity.get("executable_sha256"):
        raise ValueError("normalization executable digest does not match the frozen identity")

    contract = doc.get("execution_contract")
    if not isinstance(contract, dict):
        raise ValueError("execution_contract must be an object")
    harv = Path(str(contract.get("harvester", "")))
    if not (ROOT / harv).is_file():
        raise ValueError("harvester not present")
    if _digest(ROOT / harv) != contract.get("harvester_sha256"):
        raise ValueError("harvester digest does not match the frozen execution contract")
    if contract.get("success_terminal") != SUCCESS_TERMINAL or contract.get("failure_terminal") != FAILURE_TERMINAL:
        raise ValueError("execution contract terminals must match the frozen v3 terminals")
    fetch_rule = str(contract.get("fetch_independence_requirement", ""))
    if "at least 3 independent fetches" not in fetch_rule:
        raise ValueError("fetch independence requirement must demand at least 3 independent fetches")
    if len(contract.get("fail_closed_rules", [])) != 3:
        raise ValueError("the three fail-closed rules must be recorded")
    if not str(contract.get("expected_outcome_recorded_before_execution", "")).strip():
        raise ValueError("expected outcome must be recorded before execution")

    gives_up = doc.get("gives_up_recorded")
    if not isinstance(gives_up, list) or len(gives_up) < 5:
        raise ValueError("at least five explicit gives-up items must be recorded")
    if any(not str(item).strip() for item in gives_up):
        raise ValueError("gives-up items must be non-empty")

    lineage = doc.get("scientific_lineage_bound_verbatim")
    if not isinstance(lineage, dict) or not lineage:
        raise ValueError("scientific lineage must be bound")
    for name, binding in lineage.items():
        path = ROOT / str(binding.get("path", ""))
        if not path.is_file():
            raise ValueError(f"lineage artifact absent: {name}")
        if _digest(path) != binding.get("sha256"):
            raise ValueError(f"lineage digest mismatch for {name}: frozen bytes drifted")

    if not str(doc.get("downstream_contract_delta", "")).strip():
        raise ValueError("downstream_contract_delta must be recorded")

    flags = doc.get("flags")
    if not isinstance(flags, dict):
        raise ValueError("flags must be an object")
    for flag in REQUIRED_FALSE_FLAGS:
        if flags.get(flag) is not False:
            raise ValueError(f"freeze flag must be false: {flag}")
    if set(flags) != set(REQUIRED_FALSE_FLAGS):
        raise ValueError("freeze flag set must be exactly the required custody flags")
    if doc.get("grants_scientific_authority") is not False:
        raise ValueError("the freeze must not grant scientific authority")
    if doc.get("scientific_authority_delta") != "NONE__NORMALIZATION_IDENTITY_FREEZE_ONLY":
        raise ValueError("scientific_authority_delta mismatch")


def _result_files_present(directory: Path) -> list[str]:
    # Absence cross-checked two ways: glob pattern and directory listing scan.
    names: set[str] = set()
    for hit in directory.glob("FAMILIES_*.json"):
        names.add(hit.name)
    if directory.exists():
        for entry in directory.iterdir():
            if entry.name.startswith("FAMILIES_") and entry.suffix == ".json":
                names.add(entry.name)
    return sorted(names)


def validate_result(doc: dict[str, Any], frame: dict[str, dict[str, Any]], directory: Path) -> None:
    curator = _load("a3_curator_validator_v3fz", HERE / "validate_external_curator_packet_v1.py")
    if doc.get("schema") != RESULT_SCHEMA:
        raise ValueError("result schema mismatch")
    terminal = doc.get("terminal")
    if terminal not in (SUCCESS_TERMINAL, FAILURE_TERMINAL):
        raise ValueError(f"terminal must be one of the two frozen v3 terminals, got: {terminal!r}")
    if doc.get("successor_frame_sha256") != curator.EXPECTED_SUCCESSOR_FRAME_SHA256:
        raise ValueError("result does not bind the frozen successor frame")
    if doc.get("successor_frame_rebound") is not False:
        raise ValueError("result must not claim a frame rebind")
    if doc.get("grants_scientific_authority") is not False:
        raise ValueError("result must not grant scientific authority")

    normalization = doc.get("normalization")
    if not isinstance(normalization, dict):
        raise ValueError("normalization block must be an object")
    if normalization.get("id") != "WORKFLOWHUB_MEMBER_MANIFEST_NORMALIZATION_V3":
        raise ValueError("result normalization id mismatch")
    if sorted(normalization.get("request_generated_root_members_excluded", [])) != sorted(EXCLUDED_MEMBERS):
        raise ValueError("result excluded member set mismatch")
    if normalization.get("v2_normalization_imported_verbatim") is not True:
        raise ValueError("result must record v2 imported verbatim")

    partition = doc.get("partition")
    if not isinstance(partition, dict):
        raise ValueError("partition must be an object")
    frame_set = set(frame)
    if partition.get("frame_n") != 128 or len(frame_set) != 128:
        raise ValueError("partition frame_n must be 128 and match the frozen frame")
    fetches = partition.get("fetches_per_family_version")
    if not isinstance(fetches, int) or fetches < 3:
        raise ValueError("partition must record at least 3 fetches per family per version")
    nonrepro = partition.get("v3_nonreproducible_workflow_ids")
    collapsed = partition.get("v3_content_only_before_after_equal_workflow_ids")
    if not isinstance(nonrepro, list) or not isinstance(collapsed, list):
        raise ValueError("v3 partition id lists must be lists")
    if len(nonrepro) != len(set(nonrepro)) or len(collapsed) != len(set(collapsed)):
        raise ValueError("v3 partition id lists contain duplicates")
    if set(nonrepro) - frame_set or set(collapsed) - frame_set:
        raise ValueError("v3 partition ids must be frame families")
    if partition.get("v3_reproducible_n") != 128 - len(nonrepro):
        raise ValueError("v3_reproducible_n inconsistent with the nonreproducible list")
    if partition.get("v2_aggregate_reproduces_frozen_frame_n") + partition.get("v2_aggregate_mismatch_workflow_ids_n", -1) != 128:
        raise ValueError("v2 cross-check counts must partition the 128 families")

    flags = doc.get("flags")
    if not isinstance(flags, dict):
        raise ValueError("result flags must be an object")
    for flag in ("change_stratum_adjudicated", "external_gold_accessed", "candidate_predictions_computed",
                 "protected_outcomes_accessed", "successor_frame_rebound"):
        if flags.get(flag) is not False:
            raise ValueError(f"result flag must be false: {flag}")
    if flags.get("member_manifests_committed") != (terminal == SUCCESS_TERMINAL):
        raise ValueError("member_manifests_committed must equal (terminal is success)")

    if terminal == FAILURE_TERMINAL:
        evidence = doc.get("evidence")
        if not isinstance(evidence, dict):
            raise ValueError("failure evidence must be an object")
        if evidence.get("fail_closed_before_emitting_any_chunk") is not True:
            raise ValueError("failure must record fail-closed-before-emitting")
        if not nonrepro and not collapsed:
            raise ValueError("a failure terminal without a failing partition is incoherent")
        if _result_files_present(directory):
            raise ValueError("fail-closed result but chunk files exist in the freeze directory")
        if (directory / "SNAPSHOT_V3.json").exists():
            raise ValueError("fail-closed result but SNAPSHOT_V3.json exists")
        return

    evidence = doc.get("evidence")
    if not isinstance(evidence, dict) or evidence.get("fail_closed_before_emitting_any_chunk") is not False:
        raise ValueError("success must record that the fail-closed gate passed open")
    snapshot = json.loads((directory / "SNAPSHOT_V3.json").read_text(encoding="utf-8"))
    if snapshot.get("schema") != SNAPSHOT_SCHEMA:
        raise ValueError("snapshot schema mismatch")
    if snapshot.get("successor_frame_sha256") != curator.EXPECTED_SUCCESSOR_FRAME_SHA256:
        raise ValueError("snapshot does not bind the frozen successor frame")
    if snapshot.get("normalization_id") != "WORKFLOWHUB_MEMBER_MANIFEST_NORMALIZATION_V3":
        raise ValueError("snapshot normalization id mismatch")
    if snapshot.get("source_family_n") != 128:
        raise ValueError("snapshot must cover 128 families")
    if snapshot.get("v3_aggregate_reproducible_for_every_family") is not True:
        raise ValueError("snapshot must record per-family reproducibility")
    if snapshot.get("candidate_predictions_computed") is not False or snapshot.get("external_gold_accessed") is not False:
        raise ValueError("snapshot custody flags must be false")

    chunks = snapshot.get("chunks")
    if not isinstance(chunks, list) or len(chunks) != 4:
        raise ValueError("snapshot must carry four 32-row chunks")
    seen_ids: set[str] = set()
    v2_stable_n = 0
    rows_for_digest: list[dict[str, Any]] = []
    candidate = _load("a3_candidate_policy_v3fz", HERE / "candidate_policy_v1.py")
    first_row: dict[str, Any] | None = None
    for chunk in chunks:
        if chunk.get("rows") != 32:
            raise ValueError("each chunk must carry 32 rows")
        chunk_path = directory / Path(str(chunk["path"])).name
        payload = json.loads(chunk_path.read_text(encoding="utf-8"))
        if _digest(chunk_path) != chunk.get("sha256"):
            raise ValueError(f"chunk digest mismatch: {chunk_path.name}")
        if payload.get("schema") != CHUNK_SCHEMA:
            raise ValueError("chunk schema mismatch")
        if payload.get("normalization_id") != "WORKFLOWHUB_MEMBER_MANIFEST_NORMALIZATION_V3":
            raise ValueError("chunk normalization id mismatch")
        for row in payload["rows"]:
            wid = str(row["workflow_id"])
            if wid in seen_ids:
                raise ValueError(f"duplicate family in snapshot: {wid}")
            seen_ids.add(wid)
            if row.get("fetches_per_version") != fetches:
                raise ValueError(f"row fetch count mismatch: {wid}")
            for path_key in ("before_excluded_request_generated_paths", "after_excluded_request_generated_paths"):
                if sorted(row.get(path_key, [])) != sorted(EXCLUDED_MEMBERS):
                    raise ValueError(f"row excluded-path set mismatch: {wid} {path_key}")
            if row["before_normalized_manifest_v3_sha256"] == row["after_normalized_manifest_v3_sha256"]:
                raise ValueError(f"family collapsed to equal v3 aggregates: {wid}")
            if not row["before_manifest"] or not row["after_manifest"]:
                raise ValueError(f"row missing member manifests: {wid}")
            if row["before_v2_aggregate_reproduces_frozen_frame"] and row["after_v2_aggregate_reproduces_frozen_frame"]:
                v2_stable_n += 1
            if first_row is None:
                first_row = row
            rows_for_digest.append(
                {k: v for k, v in row.items()
                 if k not in ("before_manifest", "after_manifest", "before_defect", "after_defect")}
            )
    if seen_ids != frame_set:
        raise ValueError("snapshot rows do not exactly cover the frozen 128-family frame")
    if v2_stable_n != partition["v2_aggregate_reproduces_frozen_frame_n"]:
        raise ValueError("row-level v2 cross-check count disagrees with the partition")
    frozen_rows_digest = hashlib.sha256(
        json.dumps(rows_for_digest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if frozen_rows_digest != snapshot.get("frozen_rows_digest_sha256"):
        raise ValueError("frozen_rows_digest does not match the snapshot rows")
    record = {
        "schema": candidate.VISIBLE_SCHEMA,
        "workflow_id": first_row["workflow_id"],
        "version_before": int(frame[first_row["workflow_id"]]["version_before"]),
        "version_after": int(frame[first_row["workflow_id"]]["version_after"]),
        "before_manifest": first_row["before_manifest"],
        "after_manifest": first_row["after_manifest"],
    }
    decision = candidate.evaluate(record)
    if decision.get("decision") not in ("REUSE", "REOPEN", "CANNOT_DECIDE"):
        raise ValueError("frozen candidate policy could not consume the first v3 snapshot row")


def self_test() -> dict[str, Any]:
    doc = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    validate_freeze(doc)

    v3norm = _load("a3_member_manifest_v3norm_val", HERE / "normalize_member_manifests_v3.py")
    harvester = _load("a3_harvest_v3_val", HERE / "harvest_member_manifests_v3.py")
    norm_st = v3norm.self_test()
    harv_st = harvester._self_test()
    if norm_st.get("decision") != "GREEN" or harv_st.get("decision") != "GREEN":
        raise ValueError("frozen v3 modules failed their networkless self-tests")

    def mutated(**changes: Any) -> dict[str, Any]:
        clone = json.loads(json.dumps(doc))
        for key, value in changes.items():
            node: dict[str, Any] = clone
            parts = key.split(".")
            for part in parts[:-1]:
                node = node[part]
            node[parts[-1]] = value
        return clone

    hostile: list[tuple[str, dict[str, Any]]] = []
    hostile.append(("free parameter added", mutated(**{"normalization_identity.free_parameters": ["tolerance"]})))
    hostile.append(("third member excluded", mutated(**{"normalization_identity.request_generated_root_members_excluded": EXCLUDED_MEMBERS + ["workflow.cwl"]})))
    hostile.append(("rule emptied", mutated(**{"normalization_identity.rule": ""})))
    hostile.append(("run-time resolution granted", mutated(**{"normalization_identity.run_time_resolution": "PER_FAMILY"})))
    hostile.append(("v2 reimplemented", mutated(**{"normalization_identity.v2_normalization_imported_verbatim": False})))
    hostile.append(("executable digest tampered", mutated(**{"normalization_identity.executable_sha256": "0" * 64})))
    hostile.append(("harvester digest tampered", mutated(**{"execution_contract.harvester_sha256": "0" * 64})))
    hostile.append(("lineage digest tampered", mutated(**{"scientific_lineage_bound_verbatim.v2_rocrate_normalization.sha256": "0" * 64})))
    hostile.append(("gives-up emptied", mutated(**{"gives_up_recorded": ["x"]})))
    hostile.append(("harvest flag flipped", mutated(**{"flags.v3_harvest_executed": True})))
    hostile.append(("authority granted", mutated(**{"grants_scientific_authority": True})))
    hostile.append(("authority delta inflated", mutated(**{"scientific_authority_delta": "NONE__RESULT_SUPPORTS_REBIND"})))
    hostile.append(("terminals swapped", mutated(**{"execution_contract.failure_terminal": "GREEN"})))
    hostile.append(("fetch requirement weakened", mutated(**{"execution_contract.fetch_independence_requirement": "1 fetch"})))
    for label, packet in hostile:
        try:
            validate_freeze(packet)
        except ValueError:
            continue
        raise AssertionError(f"hostile freeze accepted: {label}")

    curator = _load("a3_curator_validator_v3fz_st", HERE / "validate_external_curator_packet_v1.py")
    frame = curator.load_source_frame()
    result_present = RESULT_PATH.is_file()
    result_hostile_n = 0
    if result_present:
        result_doc = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        validate_result(result_doc, frame, RESULT_DIR)

        def rmutated(**changes: Any) -> dict[str, Any]:
            clone = json.loads(json.dumps(result_doc))
            for key, value in changes.items():
                node: dict[str, Any] = clone
                parts = key.split(".")
                for part in parts[:-1]:
                    node = node[part]
                node[parts[-1]] = value
            return clone

        rhostile: list[tuple[str, dict[str, Any]]] = []
        rhostile.append(("terminal invented", rmutated(**{"terminal": "GREEN_MEMBER_MANIFESTS_BOUND"})))
        rhostile.append(("frame sha rebound", rmutated(**{"successor_frame_sha256": "0" * 64})))
        rhostile.append(("rebind claimed", rmutated(**{"successor_frame_rebound": True})))
        rhostile.append(("nonreproducible list emptied", rmutated(**{"partition.v3_nonreproducible_workflow_ids": []})))
        rhostile.append(("fetches weakened", rmutated(**{"partition.fetches_per_family_version": 1})))
        rhostile.append(("authority granted", rmutated(**{"grants_scientific_authority": True})))
        rhostile.append(("committed flag flipped on failure", rmutated(**{"flags.member_manifests_committed": not result_doc["flags"]["member_manifests_committed"]})))
        rhostile.append(("v2 count inflated", rmutated(**{"partition.v2_aggregate_reproduces_frozen_frame_n": 128})))
        for label, packet in rhostile:
            try:
                validate_result(packet, frame, RESULT_DIR)
            except ValueError:
                continue
            raise AssertionError(f"hostile result accepted: {label}")
        result_hostile_n = len(rhostile)

        if result_doc["terminal"] == SUCCESS_TERMINAL:
            with tempfile.TemporaryDirectory() as td:
                scratch = Path(td) / "freeze-v3"
                shutil.copytree(RESULT_DIR, scratch)
                chunk_file = sorted(scratch.glob("FAMILIES_*.json"))[0]
                chunk_file.write_bytes(chunk_file.read_bytes() + b"\n")
                tampered = json.loads((scratch / "RESULT_V3.json").read_text(encoding="utf-8"))
                try:
                    validate_result(tampered, frame, scratch)
                except ValueError:
                    result_hostile_n += 1
                else:
                    raise AssertionError("hostile result accepted: tampered chunk bytes")
    else:
        # Absence cross-checked two ways before asserting it.
        if RESULT_PATH.exists() or (RESULT_DIR.exists() and (RESULT_DIR / "SNAPSHOT_V3.json").exists()):
            raise ValueError("result artifacts present but RESULT_V3.json absent")
        if _result_files_present(RESULT_DIR):
            raise ValueError("chunk files present but RESULT_V3.json absent")
        # Synthetic full-frame success must be structurally accepted (control:
        # the checker is not a blanket rejector), while a coverage hole and a
        # content collapse in the same construction must be rejected.
        synthetic_ok, synthetic_rejected = _synthetic_result_checks(frame)

    out: dict[str, Any] = {
        "decision": "GREEN",
        "freeze_sha256": _digest(FREEZE_PATH),
        "freeze_flags_all_false": True,
        "lineage_bindings_verified_against_live_bytes": len(doc["scientific_lineage_bound_verbatim"]),
        "frozen_module_self_tests": "GREEN",
        "hostile_freeze_mutations_rejected": len(hostile),
        "result_present": result_present,
        "result_hostile_mutations_rejected": result_hostile_n if result_present else None,
        "network_accessed": False,
    }
    if not result_present:
        out["synthetic_full_frame_success_accepted"] = synthetic_ok
        out["synthetic_defects_rejected"] = synthetic_rejected
    return out


def _synthetic_result_checks(frame: dict[str, dict[str, Any]]) -> tuple[bool, bool]:
    """Build a synthetic in-memory success result; controls for the checker.

    The positive control proves a structurally sound full-frame success passes
    validate_result; the same construction with one family dropped and one
    family collapsed (equal before/after v3 aggregates) must be rejected.
    """
    rows = []
    for wid in sorted(frame, key=lambda x: int(x)):
        rows.append({
            "workflow_id": wid,
            "fetches_per_version": 3,
            "before_manifest": [{"path": "workflow.cwl", "bytes": 2, "sha256": hashlib.sha256(b"a").hexdigest(), "kind": "regular", "executable": False}],
            "after_manifest": [{"path": "workflow.cwl", "bytes": 2, "sha256": hashlib.sha256(b"b").hexdigest(), "kind": "regular", "executable": False}],
            "before_excluded_request_generated_paths": list(EXCLUDED_MEMBERS),
            "after_excluded_request_generated_paths": list(EXCLUDED_MEMBERS),
            "before_normalized_manifest_v3_sha256": hashlib.sha256(b"before" + wid.encode()).hexdigest(),
            "after_normalized_manifest_v3_sha256": hashlib.sha256(b"after" + wid.encode()).hexdigest(),
            "before_v2_aggregate_reproduces_frozen_frame": False,
            "after_v2_aggregate_reproduces_frozen_frame": False,
        })
    with tempfile.TemporaryDirectory() as td:
        scratch = Path(td)
        result, snapshot = _write_synthetic_success(rows, scratch)
        validate_result(json.loads(json.dumps(result)), frame, scratch)
        dropped = json.loads(json.dumps(result))
        dropped_snapshot = json.loads(json.dumps(snapshot))
        dropped_snapshot["chunks"][0]["payload"]["rows"] = dropped_snapshot["chunks"][0]["payload"]["rows"][1:]
        _rewrite_synthetic(dropped, dropped_snapshot, scratch, "dropped")
        try:
            validate_result(dropped, frame, scratch)
        except ValueError:
            collapsed = json.loads(json.dumps(result))
            collapsed_snapshot = json.loads(json.dumps(snapshot))
            rows_c = collapsed_snapshot["chunks"][0]["payload"]["rows"]
            rows_c[0]["after_normalized_manifest_v3_sha256"] = rows_c[0]["before_normalized_manifest_v3_sha256"]
            _rewrite_synthetic(collapsed, collapsed_snapshot, scratch, "collapsed")
            try:
                validate_result(collapsed, frame, scratch)
            except ValueError:
                return True, True
            raise AssertionError("synthetic content collapse accepted")
        raise AssertionError("synthetic coverage hole accepted")


def _write_synthetic_success(rows: list[dict[str, Any]], scratch: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    chunks = []
    for i in range(0, len(rows), 32):
        block = rows[i:i + 32]
        name = f"FAMILIES_{i + 1:03d}_{i + len(block):03d}.json"
        payload = {"schema": CHUNK_SCHEMA, "normalization_id": "WORKFLOWHUB_MEMBER_MANIFEST_NORMALIZATION_V3", "rows": block}
        text = json.dumps(payload, indent=1, sort_keys=True) + "\n"
        (scratch / name).write_text(text, encoding="utf-8")
        chunks.append({
            "path": f"papers/publication_closure/a3-external-change-transport-v1/workflowhub-member-manifest-freeze-v3/{name}",
            "rows": len(block),
            "first_workflow_id": block[0]["workflow_id"],
            "last_workflow_id": block[-1]["workflow_id"],
            "sha256": hashlib.sha256((scratch / name).read_bytes()).hexdigest(),
            "payload": payload,
        })
    rows_for_digest = [
        {k: v for k, v in row.items() if k not in ("before_manifest", "after_manifest")}
        for row in rows
    ]
    snapshot = {
        "schema": SNAPSHOT_SCHEMA,
        "date": "2026-09-03",
        "successor_frame_sha256": _load("a3_cur_validator_syn", HERE / "validate_external_curator_packet_v1.py").EXPECTED_SUCCESSOR_FRAME_SHA256,
        "normalization_id": "WORKFLOWHUB_MEMBER_MANIFEST_NORMALIZATION_V3",
        "source_family_n": len(rows),
        "total_member_entries": sum(len(r["before_manifest"]) + len(r["after_manifest"]) for r in rows),
        "v3_aggregate_reproducible_for_every_family": True,
        "frozen_rows_digest_sha256": hashlib.sha256(json.dumps(rows_for_digest, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest(),
        "chunks": [{k: v for k, v in c.items() if k != "payload"} for c in chunks],
        "candidate_predictions_computed": False,
        "external_gold_accessed": False,
    }
    (scratch / "SNAPSHOT_V3.json").write_text(json.dumps(snapshot, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    snapshot["chunks"] = chunks
    result = {
        "schema": RESULT_SCHEMA,
        "date": "2026-09-03",
        "terminal": SUCCESS_TERMINAL,
        "successor_frame_sha256": snapshot["successor_frame_sha256"],
        "successor_frame_rebound": False,
        "normalization": {
            "id": "WORKFLOWHUB_MEMBER_MANIFEST_NORMALIZATION_V3",
            "request_generated_root_members_excluded": list(EXCLUDED_MEMBERS),
            "v2_normalization_imported_verbatim": True,
        },
        "partition": {
            "frame_n": len(rows),
            "fetches_per_family_version": 3,
            "v3_reproducible_n": len(rows),
            "v3_nonreproducible_workflow_ids": [],
            "v3_content_only_before_after_equal_workflow_ids": [],
            "v2_aggregate_reproduces_frozen_frame_n": sum(
                r["before_v2_aggregate_reproduces_frozen_frame"] and r["after_v2_aggregate_reproduces_frozen_frame"] for r in rows
            ),
            "v2_aggregate_mismatch_workflow_ids_n": len(rows),
        },
        "evidence": {"fail_closed_before_emitting_any_chunk": False},
        "flags": {
            "change_stratum_adjudicated": False,
            "external_gold_accessed": False,
            "candidate_predictions_computed": False,
            "protected_outcomes_accessed": False,
            "member_manifests_committed": True,
            "successor_frame_rebound": False,
        },
        "grants_scientific_authority": False,
    }
    (scratch / "RESULT_V3.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return result, snapshot


def _rewrite_synthetic(result: dict[str, Any], snapshot: dict[str, Any], scratch: Path, tag: str) -> None:
    for chunk in snapshot["chunks"]:
        name = Path(chunk["path"]).name
        text = json.dumps(chunk.pop("payload"), indent=1, sort_keys=True) + "\n"
        (scratch / name).write_text(text, encoding="utf-8")
        chunk["sha256"] = hashlib.sha256((scratch / name).read_bytes()).hexdigest()
    (scratch / "SNAPSHOT_V3.json").write_text(json.dumps(snapshot, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (scratch / f"RESULT_{tag}.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run the freeze checker")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("this checker is self-test only")
    print(json.dumps(self_test(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
