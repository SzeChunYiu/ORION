#!/usr/bin/env python3
"""Run exact upstream Mathlib files through the exact native Lean toolchain."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / "NATIVE_VERIFICATION_PROTOCOL_V1.json"
SAMPLE = ROOT / "NATIVE_VERIFICATION_SAMPLE_V1.json"
CORPUS_MANIFEST = ROOT / "MATHLIB_CORPUS_V2_MANIFEST.json"
DEFAULT_OUTPUT = ROOT.parent / "results" / "MATHLIB_NATIVE_RECEIPTS_V1.json"
NEGATIVE_PATH = Path("/tmp/ORIONP10NegativeControl.lean")


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def canonical_digest(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return digest_bytes(raw)


def run(
    command: list[str],
    cwd: Path,
    env: dict[str, str],
    *,
    include_stdout_utf8: bool = False,
) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=cwd, env=env, capture_output=True, check=False)
    receipt = {
        "command": command,
        "exit_status": completed.returncode,
        "verdict": "SUCCESS" if completed.returncode == 0 else "FAIL",
        "stdout_sha256": digest_bytes(completed.stdout),
        "stderr_sha256": digest_bytes(completed.stderr),
        "stdout_bytes": len(completed.stdout),
        "stderr_bytes": len(completed.stderr),
    }
    if include_stdout_utf8:
        receipt["stdout_utf8"] = completed.stdout.decode("utf-8", errors="strict").strip()
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mathlib-checkout", type=Path, required=True)
    parser.add_argument("--lake", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--runtime-adapter", type=Path)
    args = parser.parse_args()

    protocol = json.loads(PROTOCOL.read_text())
    sample = json.loads(SAMPLE.read_text())
    if sample["protocol_sha256"] != digest_file(PROTOCOL):
        raise AssertionError("sample/protocol binding mismatch")
    if sample["corpus_manifest_sha256"] != digest_file(CORPUS_MANIFEST):
        raise AssertionError("sample/corpus-manifest binding mismatch")

    checkout = args.mathlib_checkout.resolve()
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=checkout, capture_output=True, text=True, check=True
    ).stdout.strip()
    if head != protocol["source"]["commit"]:
        raise AssertionError(f"Mathlib revision mismatch: {head}")
    if (checkout / "lean-toolchain").read_text().strip() != protocol["source"]["lean_toolchain"]:
        raise AssertionError("Lean toolchain mismatch")
    if digest_file(checkout / "lake-manifest.json") != protocol["source"]["dependency_manifest_sha256"]:
        raise AssertionError("dependency manifest mismatch")

    environment = os.environ.copy()
    adapter = None
    if args.runtime_adapter is not None:
        adapter = {
            "path": args.runtime_adapter.as_posix(),
            "sha256": digest_file(args.runtime_adapter),
        }
        environment["LD_PRELOAD"] = str(args.runtime_adapter.resolve())

    version = run(
        [str(args.lake), "env", "lean", "--version"],
        checkout,
        environment,
        include_stdout_utf8=True,
    )
    if version["exit_status"] != 0:
        raise AssertionError("native Lean version preflight failed")

    receipts = []
    for item in sample["files"]:
        upstream_path = checkout / item["path"]
        if digest_file(upstream_path) != item["source_sha256"]:
            raise AssertionError(f"upstream source digest mismatch: {item['path']}")
        environment_subject = {
            "repository": protocol["source"]["repository"],
            "source_revision": protocol["source"]["commit"],
            "lean_toolchain": protocol["source"]["lean_toolchain"],
            "dependency_manifest_sha256": protocol["source"]["dependency_manifest_sha256"],
            "source_path": item["path"],
            "source_sha256": item["source_sha256"],
            "branch": protocol["source"]["branch"],
        }
        receipt = run([str(args.lake), "env", "lean", item["path"]], checkout, environment)
        receipt.update(
            {
                "top_module": item["top_module"],
                "source_path": item["path"],
                "source_sha256": item["source_sha256"],
                "environment_sha256": canonical_digest(environment_subject),
            }
        )
        receipts.append(receipt)

    negative_source = protocol["negative_control"]["source"]
    NEGATIVE_PATH.write_text(negative_source)
    try:
        negative = run([str(args.lake), "env", "lean", str(NEGATIVE_PATH)], checkout, environment)
    finally:
        NEGATIVE_PATH.unlink(missing_ok=True)
    negative["source_sha256"] = digest_bytes(negative_source.encode())
    negative["expected_verdict"] = "FAIL"

    passed = all(receipt["verdict"] == "SUCCESS" for receipt in receipts)
    passed = passed and negative["verdict"] == "FAIL"
    output = {
        "schema": "P10MathlibNativeReceipts.v1",
        "protocol_sha256": digest_file(PROTOCOL),
        "sample_sha256": digest_file(SAMPLE),
        "corpus_manifest_sha256": digest_file(CORPUS_MANIFEST),
        "mathlib_commit": head,
        "lean_toolchain": protocol["source"]["lean_toolchain"],
        "lean_release_sha256": protocol["source"]["lean_release_sha256"],
        "runtime_adapter": adapter,
        "version_preflight": version,
        "receipts": receipts,
        "negative_control": negative,
        "passes": passed,
        "claim_boundary": "Native acceptance is established only for these eight exact files; identity, statement faithfulness and authority remain separate.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    if not passed:
        raise SystemExit("P10 native verification: FAIL")
    print(f"P10 native verification: PASS ({len(receipts)} exact files; negative control rejected)")


if __name__ == "__main__":
    main()
