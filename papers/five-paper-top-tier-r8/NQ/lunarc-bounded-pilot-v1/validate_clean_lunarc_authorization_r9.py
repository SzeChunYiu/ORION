#!/usr/bin/env python3
"""Fail-closed validator for the one-shot clean NQ Engine-A LUNARC authorization."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

AUTH_NAME = "LUNARC_AUTHORIZATION_CORRECTION_CLEAN_R9.json"
EXPECTED_SCHEMA = "ORION.NQ.EngineA.LunarcAuthorizationCorrectionCleanR9.v1"
EXPECTED_ENGINE_TREE = "b64f2188238e5fc869680ca117d241a0a3615349"
EXPECTED_WRAPPER_TREE = "69f45633c7c632d74fff23771461d7cd0be38933"
EXPECTED_WRAPPER_PATH = "papers/five-paper-top-tier-r8/NQ/lunarc-bounded-pilot-v1"
EXPECTED_SUBMIT = f"{EXPECTED_WRAPPER_PATH}/submit_nq_engine_a_bounded_pilot.sh"
EXPECTED_MANIFEST = "papers/five-paper-top-tier-r8/NQ/ENGINE_A_CLEAN_INTEGRATION_R9.json"
EXPECTED_ACCOUNT = "lu2026-2-51"
EXPECTED_KEY = (
    "NQ-ENGINE-A-R9-CLEAN:"
    f"{EXPECTED_ENGINE_TREE}:{EXPECTED_WRAPPER_TREE}:"
    "lu2026-2-51:1node:1task:1cpu:4GiB:00-30-00:attempt-1"
)


def run(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        args,
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {' '.join(args)}\n{completed.stderr.strip()}"
        )
    return completed.stdout.strip()


def all_scalar_values(value: Any) -> list[Any]:
    if isinstance(value, dict):
        rows: list[Any] = []
        for child in value.values():
            rows.extend(all_scalar_values(child))
        return rows
    if isinstance(value, list):
        rows = []
        for child in value:
            rows.extend(all_scalar_values(child))
        return rows
    return [value]


def main() -> None:
    here = Path(__file__).resolve()
    repo = Path(run(here.parent, "git", "rev-parse", "--show-toplevel"))
    auth_path = here.with_name(AUTH_NAME)
    auth_bytes = auth_path.read_bytes()
    auth = json.loads(auth_bytes)

    assert auth["schema"] == EXPECTED_SCHEMA
    assert auth["immutable_payload"]["engine_tree_sha"] == EXPECTED_ENGINE_TREE
    assert auth["immutable_payload"]["lunarc_wrapper_tree_sha"] == EXPECTED_WRAPPER_TREE
    assert auth["immutable_payload"]["submit_script_path"] == EXPECTED_SUBMIT
    assert auth["immutable_payload"]["clean_integration_manifest_path"] == EXPECTED_MANIFEST
    assert auth["scheduler_envelope"] == {
        "system": "LUNARC",
        "scheduler": "Slurm",
        "account": EXPECTED_ACCOUNT,
        "partition": "scheduler_default",
        "nodes": 1,
        "ntasks": 1,
        "cpus_per_task": 1,
        "memory_gib": 4,
        "walltime": "00:30:00",
        "gpus": 0,
        "submission_limit": 1,
    }
    assert auth["nonduplication_key"] == EXPECTED_KEY

    status = run(repo, "git", "status", "--porcelain", "--untracked-files=no")
    assert status == "", f"tracked working tree is not clean: {status}"

    tree_rows: list[tuple[str, str]] = []
    raw_trees = run(
        repo,
        "git",
        "ls-tree",
        "-d",
        "-r",
        "HEAD",
        "papers/five-paper-top-tier-r8/NQ",
    )
    for line in raw_trees.splitlines():
        if not line:
            continue
        metadata, path = line.split("\t", 1)
        _mode, object_type, sha = metadata.split()
        assert object_type == "tree"
        tree_rows.append((sha, path))

    engine_paths = sorted(path for sha, path in tree_rows if sha == EXPECTED_ENGINE_TREE)
    wrapper_paths = sorted(path for sha, path in tree_rows if sha == EXPECTED_WRAPPER_TREE)
    assert engine_paths, "authorized Engine-A tree is absent under the NQ subtree"
    assert wrapper_paths == [EXPECTED_WRAPPER_PATH], wrapper_paths

    submit_path = repo / EXPECTED_SUBMIT
    manifest_path = repo / EXPECTED_MANIFEST
    assert submit_path.is_file()
    assert manifest_path.is_file()
    submit_blob = run(repo, "git", "rev-parse", f"HEAD:{EXPECTED_SUBMIT}")
    wrapper_tree_at_path = run(repo, "git", "rev-parse", f"HEAD:{EXPECTED_WRAPPER_PATH}")
    assert wrapper_tree_at_path == EXPECTED_WRAPPER_TREE

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_scalars = set(all_scalar_values(manifest))
    assert EXPECTED_ENGINE_TREE in manifest_scalars
    assert EXPECTED_WRAPPER_TREE in manifest_scalars

    head = run(repo, "git", "rev-parse", "HEAD")
    result = {
        "schema": "ORION.NQ.EngineA.CleanLunarcAuthorizationValidationR9.v1",
        "status": "PASS_STATIC_AUTHORIZATION",
        "head_commit": head,
        "authorization": {
            "path": str(auth_path.relative_to(repo)),
            "sha256": hashlib.sha256(auth_bytes).hexdigest(),
            "authorization_id": auth["authorization_id"],
            "nonduplication_key": EXPECTED_KEY,
        },
        "payload": {
            "engine_tree_sha": EXPECTED_ENGINE_TREE,
            "engine_tree_paths": engine_paths,
            "wrapper_tree_sha": EXPECTED_WRAPPER_TREE,
            "wrapper_tree_path": EXPECTED_WRAPPER_PATH,
            "submit_script_path": EXPECTED_SUBMIT,
            "submit_script_blob_sha": submit_blob,
            "integration_manifest_path": EXPECTED_MANIFEST,
        },
        "scheduler_envelope": auth["scheduler_envelope"],
        "submission_authority": {
            "one_shot": True,
            "scheduler_capability_checked_here": False,
            "account_capability_checked_here": False,
            "prior_nonduplication_receipt_checked_here": False,
            "scientific_promotion": False,
        },
        "next_required_terminal": (
            "operator must still check LUNARC account, sbatch availability, and absence of the "
            "nonduplication receipt before the single authorized submission"
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
