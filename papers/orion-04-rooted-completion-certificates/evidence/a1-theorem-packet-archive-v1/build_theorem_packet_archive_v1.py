#!/usr/bin/env python3
"""Build a hash-bound ORION-04 theorem archive readiness manifest.

The builder is intentionally fail-closed: current local evidence is archived as
available evidence, but THEOREM_PACKET_READY is impossible until the external
review, 78 independent branch certificate/output records, and final one-shot
custody receipt all satisfy the frozen contract.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def file_record(relative: str) -> dict[str, Any]:
    p = ROOT / relative
    if not p.is_file() or p.is_symlink():
        raise FileNotFoundError(relative)
    return {"path": relative, "bytes": p.stat().st_size, "sha256": sha256(p)}


def load_json(relative: str) -> dict[str, Any]:
    p = ROOT / relative
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{relative} must contain a JSON object")
    return data


def validate_reviewer(slot: dict[str, Any], blockers: list[str], records: list[dict[str, Any]]) -> None:
    path = slot["path"]
    p = ROOT / path
    if not p.is_file():
        blockers.append("MISSING_SIGNED_INDEPENDENT_MATHEMATICAL_REVIEW")
        return
    d = load_json(path)
    missing = [x for x in slot["required_fields"] if x not in d]
    if missing:
        blockers.append("INVALID_INDEPENDENT_REVIEW_FIELDS")
        return
    if d.get("verdict") != slot["required_verdict"]:
        blockers.append("INDEPENDENT_MATHEMATICAL_REVIEW_NOT_PASS")
        return
    if not all(d.get(k) is True for k in ("cover_60_patterns", "cover_78_branches", "dependency_chain_verified")):
        blockers.append("INDEPENDENT_MATHEMATICAL_REVIEW_INCOMPLETE")
        return
    records.append(file_record(path))


def validate_branch_manifest(slot: dict[str, Any], kind: str, blockers: list[str], records: list[dict[str, Any]]) -> None:
    path = slot["path"]
    p = ROOT / path
    tag = "CERTIFICATE" if kind == "certificate" else "OUTPUT"
    if not p.is_file():
        blockers.append(f"MISSING_INDEPENDENT_BRANCH_{tag}_MANIFEST")
        return
    d = load_json(path)
    branches = d.get("branches")
    if not isinstance(branches, list) or len(branches) != slot["required_branch_count"]:
        blockers.append(f"INVALID_INDEPENDENT_BRANCH_{tag}_COUNT")
        return
    fields = set(slot["required_fields_per_branch"])
    identities: set[str] = set()
    artifact_paths: set[str] = set()
    for row in branches:
        if not isinstance(row, dict) or not fields <= set(row):
            blockers.append(f"INVALID_INDEPENDENT_BRANCH_{tag}_FIELDS")
            return
        ident = row.get("branch_identity")
        artifact_field = "certificate_path" if kind == "certificate" else "output_path"
        artifact = row.get(artifact_field)
        if not isinstance(ident, str) or not ident or ident in identities:
            blockers.append(f"DUPLICATE_OR_INVALID_INDEPENDENT_BRANCH_{tag}_IDENTITY")
            return
        if not isinstance(artifact, str) or not artifact or artifact in artifact_paths:
            blockers.append(f"DUPLICATE_OR_INVALID_INDEPENDENT_BRANCH_{tag}_PATH")
            return
        identities.add(ident)
        artifact_paths.add(artifact)
        if row.get("survivor_count") != slot["required_survivor_count_per_branch"]:
            blockers.append(f"NONZERO_SURVIVOR_IN_INDEPENDENT_BRANCH_{tag}")
            return
        artifact_path = ROOT / artifact
        digest_field = "certificate_sha256" if kind == "certificate" else "output_sha256"
        if not artifact_path.is_file() or sha256(artifact_path) != row.get(digest_field):
            blockers.append(f"INDEPENDENT_BRANCH_{tag}_ARTIFACT_BINDING_MISMATCH")
            return
        if kind == "certificate":
            checker_receipt = row.get("checker_receipt_sha256")
            checker_identity = row.get("checker_identity")
            if not isinstance(checker_identity, str) or not checker_identity or not isinstance(checker_receipt, str) or len(checker_receipt) != 64:
                blockers.append("INDEPENDENT_BRANCH_CERTIFICATE_CHECKER_RECEIPT_INVALID")
                return
    records.append(file_record(path))
    for artifact in sorted(artifact_paths):
        records.append(file_record(artifact))


def validate_custody(slot: dict[str, Any], blockers: list[str], records: list[dict[str, Any]]) -> None:
    path = slot["path"]
    p = ROOT / path
    if not p.is_file():
        blockers.append("MISSING_FINAL_AUTHORIZATION_AND_CUSTODY_RECEIPT")
        return
    d = load_json(path)
    if any(field not in d for field in slot["required_fields"]):
        blockers.append("INVALID_FINAL_AUTHORIZATION_AND_CUSTODY_FIELDS")
        return
    if d.get("d4_rounds_consumed") != slot["required_d4_rounds_consumed"]:
        blockers.append("FINAL_AUTHORIZATION_D4_ROUND_COUNT_MISMATCH")
        return
    records.append(file_record(path))


def build(contract_path: Path) -> dict[str, Any]:
    relative_contract = contract_path.resolve().relative_to(ROOT.resolve()).as_posix()
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    if contract["schema"] != "ORION.A1.TheoremPacketArchiveContract.v1":
        raise ValueError("contract schema mismatch")
    if contract["protected_target_execution_authorized_by_this_contract"] is not False:
        raise ValueError("archive contract illegally authorizes target execution")

    records = [file_record(relative_contract)]
    blockers: list[str] = []
    for rel in contract["present_required_artifacts"]:
        try:
            records.append(file_record(rel))
        except FileNotFoundError:
            blockers.append(f"MISSING_LOCAL_REQUIRED_ARTIFACT:{rel}")

    slots = contract["future_external_slots"]
    validate_reviewer(slots["signed_independent_mathematical_review"], blockers, records)
    validate_branch_manifest(slots["independent_branch_certificate_manifest"], "certificate", blockers, records)
    validate_branch_manifest(slots["independent_branch_outputs_manifest"], "output", blockers, records)
    validate_custody(slots["final_authorization_and_custody_receipt"], blockers, records)

    records.sort(key=lambda x: x["path"])
    unique_paths = {r["path"] for r in records}
    if len(unique_paths) != len(records):
        blockers.append("ARCHIVE_DUPLICATE_PATH_BINDING")
    payload_digest = hashlib.sha256(json.dumps(records, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    ready = not blockers
    terminal = "THEOREM_PACKET_READY" if ready else "CANNOT_CHECK_THEOREM_PACKET_ARCHIVE_INCOMPLETE"
    return {
        "schema": "ORION.A1.TheoremPacketArchiveReadiness.v1",
        "terminal": terminal,
        "archive_ready": ready,
        "artifact_count": len(records),
        "artifact_manifest_sha256": payload_digest,
        "artifacts": records,
        "blockers": blockers,
        "target_d4_execution_performed_by_builder": False,
        "scientific_authority_delta": "NONE__ARCHIVE_READINESS_ONLY",
    }


def self_test() -> dict[str, Any]:
    # The live repository is expected to remain incomplete until external slots land.
    contract = Path(__file__).resolve().parent / "THEOREM_PACKET_ARCHIVE_CONTRACT_V1.json"
    result = build(contract)
    expected = {
        "MISSING_SIGNED_INDEPENDENT_MATHEMATICAL_REVIEW",
        "MISSING_INDEPENDENT_BRANCH_CERTIFICATE_MANIFEST",
        "MISSING_INDEPENDENT_BRANCH_OUTPUT_MANIFEST",
        "MISSING_FINAL_AUTHORIZATION_AND_CUSTODY_RECEIPT",
    }
    assert result["archive_ready"] is False
    assert result["terminal"] == "CANNOT_CHECK_THEOREM_PACKET_ARCHIVE_INCOMPLETE"
    assert expected <= set(result["blockers"])
    assert not any(x.startswith("MISSING_LOCAL_REQUIRED_ARTIFACT") for x in result["blockers"])
    return {"decision": "GREEN", "current_blockers": result["blockers"], "local_artifacts_hash_bound": result["artifact_count"]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", type=Path, default=Path(__file__).resolve().parent / "THEOREM_PACKET_ARCHIVE_CONTRACT_V1.json")
    ap.add_argument("--output", type=Path)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    result = self_test() if args.self_test else build(args.contract)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
