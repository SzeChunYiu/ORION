#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "SUBMISSION_MANIFEST_V3.json"
CHECKSUMS = ROOT / "SHA256SUMS"

REQUIRED_FILES = [
    "README.md",
    "PR1602_ADOPTION_RECEIPT.json",
    "theory-A-MANUSCRIPT_V3.md",
    "theory-A-MANUSCRIPT_V3.pdf",
    "theory-B-MANUSCRIPT_V3.md",
    "theory-B-MANUSCRIPT_V3.pdf",
    "PROOF_REPAIR_DISPOSITION_V3.md",
    "NOVELTY_AUDIT_V2.md",
    "proof_checker_v3.py",
    "test_proof_checker_v3.py",
    "PROOF_CHECK_RESULT_V3.json",
    "DATA_CODE_AVAILABILITY.md",
    "LICENSE.md",
    "COVER_LETTER_A.md",
    "COVER_LETTER_B.md",
    "COMPILE.md",
    "build_manifest_v3.py",
]


def file_record(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    payload = path.read_bytes()
    return {
        "path": relative,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def build_manifest() -> dict[str, Any]:
    missing = [relative for relative in REQUIRED_FILES if not (ROOT / relative).is_file()]
    if missing:
        raise FileNotFoundError("missing required package files: " + ", ".join(missing))

    proof = load_json(ROOT / "PROOF_CHECK_RESULT_V3.json")
    receipt = load_json(ROOT / "PR1602_ADOPTION_RECEIPT.json")
    if proof.get("all_passed") is not True:
        raise AssertionError("independent proof checker is not PASS")
    if receipt.get("round3", {}).get("terminal") != "CANNOT_CHECK_MOVE_COMPLETENESS":
        raise AssertionError("PR #1602 adverse terminal was not preserved")
    if receipt.get("round3", {}).get("all_tasks_hit_frozen_cap") is not True:
        raise AssertionError("PR #1602 cap-eight custody was not preserved")

    records = [file_record(relative) for relative in REQUIRED_FILES]
    return {
        "schema": "ORION.ORION01.SubmissionManifest.v3",
        "package_identity": "orion-01-bounded-closeout-v3-2026-08-29",
        "paper_id": "ORION-01",
        "issue": 1701,
        "generated_at": "2026-08-29T00:00:00Z",
        "bounded_terminal": "BOUNDED_PAPER_RETAINED",
        "portfolio_routing": "TOP_TIER_PROMOTION_ACTIVE__THEORY_OR_EXACT_COMPUTE",
        "old_experiment_terminal": "CANNOT_CHECK_MOVE_COMPLETENESS",
        "old_cap_increase_authorized": False,
        "implementation_independent_check": proof["terminal"],
        "files": records,
        "parent_evidence": {
            "pr1602_commit": "9e9b870b795b6ae0b3726031ced0b9ebef004897",
            "pr1602_aggregate_sha256": "7e26974b9afab27abb88a27b7c2c5ba058e6d351f0d2f8428c4fa8e50acada31",
            "round2_result_sha256": "db1253e52a44741613abb9217eb4a865d190c3948abdab9f8fbd344ada035efd",
            "r6m_upper": "research/extensions/orion-qg/PAPER_A_A1_MULTITAG_TARE_RESULTS_2026-08-24.json",
            "r6m_lower": "research/extensions/orion-qg/QG18_TARE_KAPPA_RESULTS.json",
            "all_size_upper": "research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json"
        },
        "novelty_disposition": "NOVELTY_NARROWED__RESIDUAL_CANDIDATE_ONLY",
        "external_peer_review": False,
        "external_novelty_authority": False,
        "visual_inspection": "REQUIRED_BEFORE_SUBMISSION",
        "submission_authority": False,
        "release_state": "BUILD_COMPLETE__AUTHOR_VISUAL_REVIEW_REQUIRED"
    }


def parse_checksums() -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in CHECKSUMS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, relative = line.split(maxsplit=1)
        relative = relative.lstrip("*").strip()
        parsed[relative] = digest
    return parsed


def verify() -> None:
    manifest = load_json(MANIFEST)
    expected = build_manifest()
    if manifest != expected:
        raise AssertionError("committed manifest differs from deterministic rebuild")

    checksums = parse_checksums()
    required_checksum_paths = REQUIRED_FILES + [MANIFEST.name]
    for relative in required_checksum_paths:
        path = ROOT / relative
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if checksums.get(relative) != digest:
            raise AssertionError(f"checksum mismatch or omission: {relative}")

    extras = sorted(set(checksums) - set(required_checksum_paths))
    if extras:
        raise AssertionError("unexpected checksum entries: " + ", ".join(extras))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        verify()
        print("ORION-01 V3 manifest verification: PASS")
        return 0

    rendered = json.dumps(build_manifest(), indent=2, sort_keys=True) + "\n"
    MANIFEST.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
