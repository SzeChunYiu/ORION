#!/usr/bin/env python3
"""Fail-closed V3 validator for the clean NQ Engine-A LUNARC authorization."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

AUTH_NAME = "LUNARC_AUTHORIZATION_CORRECTION_CLEAN_R9_V3.json"
EXPECTED_SCHEMA = "ORION.NQ.EngineA.LunarcAuthorizationCorrectionCleanR9.v3"
EXPECTED_ENGINE_TREE = "b64f2188238e5fc869680ca117d241a0a3615349"
EXPECTED_WRAPPER_TREE = "69f45633c7c632d74fff23771461d7cd0be38933"
EXPECTED_WRAPPER_PATH = "papers/five-paper-top-tier-r8/NQ/lunarc-bounded-pilot-v1"
EXPECTED_AUTH_DIR = "papers/five-paper-top-tier-r8/NQ/lunarc-authorization-clean-r9-v3"
EXPECTED_SUBMIT = f"{EXPECTED_WRAPPER_PATH}/submit_nq_engine_a_bounded_pilot.sh"
EXPECTED_MANIFEST = "papers/five-paper-top-tier-r8/NQ/ENGINE_A_CLEAN_INTEGRATION_R9.json"
EXPECTED_ACCOUNT = "lu2026-2-51"
EXPECTED_KEY = (
    "NQ-ENGINE-A-R9-CLEAN-V3:"
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


def recursive_tree_rows(repo: Path) -> list[tuple[str, str]]:
    raw = run(
        repo,
        "git",
        "ls-tree",
        "-r",
        "-t",
        "HEAD",
        "papers/five-paper-top-tier-r8/NQ",
    )
    rows: list[tuple[str, str]] = []
    for line in raw.splitlines():
        if not line:
            continue
        metadata, path = line.split("\t", 1)
        _mode, object_type, sha = metadata.split()
        if object_type == "tree":
            rows.append((sha, path))
    return rows


def main() -> None:
    here = Path(__file__).resolve()
    repo = Path(run(here.parent, "git", "rev-parse", "--show-toplevel"))
    auth_path = here.with_name(AUTH_NAME)
    relative_auth = auth_path.relative_to(repo).as_posix()
    assert auth_path.parent.relative_to(repo).as_posix() == EXPECTED_AUTH_DIR
    assert not relative_auth.startswith(EXPECTED_WRAPPER_PATH + "/")

    auth_bytes = auth_path.read_bytes()
    auth = json.loads(auth_bytes)
    assert auth["schema"] == EXPECTED_SCHEMA
    assert {row["branch"] for row in auth["supersedes"]} == {
        "chatgpt/r9-nq-clean-lunarc-authorization-20260826",
        "chatgpt/r9-nq-clean-lunarc-authorization-v2-20260826",
    }
    assert all(row["submission_authority"] is False for row in auth["supersedes"])

    payload = auth["immutable_payload"]
    assert payload["engine_tree_sha"] == EXPECTED_ENGINE_TREE
    assert payload["lunarc_wrapper_tree_sha"] == EXPECTED_WRAPPER_TREE
    assert payload["lunarc_wrapper_path"] == EXPECTED_WRAPPER_PATH
    assert payload["submit_script_path"] == EXPECTED_SUBMIT
    assert payload["clean_integration_manifest_path"] == EXPECTED_MANIFEST
    assert payload["authorization_material_is_outside_payload_tree"] is True
    assert payload["recursive_tree_enumeration"].startswith("git ls-tree -r -t")
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

    tracked_status = run(repo, "git", "status", "--porcelain", "--untracked-files=no")
    assert tracked_status == "", f"tracked working tree is not clean: {tracked_status}"

    tree_rows = recursive_tree_rows(repo)
    engine_paths = sorted(path for sha, path in tree_rows if sha == EXPECTED_ENGINE_TREE)
    wrapper_paths = sorted(path for sha, path in tree_rows if sha == EXPECTED_WRAPPER_TREE)
    assert engine_paths, "authorized Engine-A tree is absent under the NQ subtree"
    assert wrapper_paths == [EXPECTED_WRAPPER_PATH], wrapper_paths
    assert all(not path.startswith(EXPECTED_WRAPPER_PATH + "/") for _sha, path in tree_rows if path == EXPECTED_AUTH_DIR)

    wrapper_tree_at_path = run(repo, "git", "rev-parse", f"HEAD:{EXPECTED_WRAPPER_PATH}")
    assert wrapper_tree_at_path == EXPECTED_WRAPPER_TREE
    submit_path = repo / EXPECTED_SUBMIT
    manifest_path = repo / EXPECTED_MANIFEST
    assert submit_path.is_file()
    assert manifest_path.is_file()
    submit_blob = run(repo, "git", "rev-parse", f"HEAD:{EXPECTED_SUBMIT}")

    wrapper_listing = run(repo, "git", "ls-tree", "-r", "--name-only", "HEAD", EXPECTED_WRAPPER_PATH)
    wrapper_files = [line for line in wrapper_listing.splitlines() if line]
    assert EXPECTED_SUBMIT in wrapper_files
    forbidden_names = {
        AUTH_NAME,
        "LUNARC_AUTHORIZATION_CORRECTION_CLEAN_R9.json",
        "validate_clean_lunarc_authorization_r9.py",
        "validate_clean_lunarc_authorization_r9_v3.py",
    }
    assert not any(Path(path).name in forbidden_names for path in wrapper_files)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_scalars = set(all_scalar_values(manifest))
    assert EXPECTED_ENGINE_TREE in manifest_scalars
    assert EXPECTED_WRAPPER_TREE in manifest_scalars

    head = run(repo, "git", "rev-parse", "HEAD")
    validator_bytes = here.read_bytes()
    result = {
        "schema": "ORION.NQ.EngineA.CleanLunarcAuthorizationValidationR9.v3",
        "status": "PASS_STATIC_AUTHORIZATION_V3",
        "head_commit": head,
        "superseded_authorizations_have_submission_authority": False,
        "authorization": {
            "path": relative_auth,
            "outside_wrapper_tree": True,
            "sha256": hashlib.sha256(auth_bytes).hexdigest(),
            "authorization_id": auth["authorization_id"],
            "nonduplication_key": EXPECTED_KEY,
        },
        "validator": {
            "path": here.relative_to(repo).as_posix(),
            "sha256": hashlib.sha256(validator_bytes).hexdigest(),
            "recursive_tree_enumeration": "git ls-tree -r -t",
        },
        "payload": {
            "engine_tree_sha": EXPECTED_ENGINE_TREE,
            "engine_tree_paths": engine_paths,
            "wrapper_tree_sha": EXPECTED_WRAPPER_TREE,
            "wrapper_tree_path": EXPECTED_WRAPPER_PATH,
            "wrapper_tree_unchanged": True,
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
            "V3 nonduplication receipt before the single authorized submission"
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
