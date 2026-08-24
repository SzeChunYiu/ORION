#!/usr/bin/env python3
"""Execute the frozen P13+P14 live-Git acquisition, never the policy campaign."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


PROTOCOL_SCHEMA = "ORION.P13P14.LiveGitAcquisitionProtocol.v1"
CORPUS_SCHEMA = "ORION.P13P14.PinnedRepositoryCorpus.v1"
RESULT_SCHEMA = "ORION.P13P14.LiveGitAcquisitionResult.v1"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA64 = re.compile(r"[0-9a-f]{64}\Z")
LICENSE_URL = re.compile(r"https://github\.com/([^/]+/[^/]+)/blob/([^/]+)/(.+)\Z")
REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
CORPUS_PATH = "papers/paper-13-responsibility-carrying-state/P13_P14_PINNED_REPOSITORY_CORPUS_V1.json"
CONTRACT_PATH = "papers/paper-13-responsibility-carrying-state/P13_P14_OBJECTIVE_GOLD_DERIVATION_CONTRACT_V1.json"
RUNNER_PATH = "development/p13-p14-live-git-acquisition-v1/run_live_git_acquisition_v1.py"
PROTOCOL_PATH = "development/p13-p14-live-git-acquisition-v1/LIVE_GIT_ACQUISITION_PROTOCOL_V1.json"
OBSERVATIONS = (
    "pinned_commit_object_exists",
    "all_direct_parent_objects_exist",
    "committer_epoch_recorded",
    "license_blob_path_resolved",
    "license_blob_sha256_matches_frozen_hash",
    "command_receipt_digest",
)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def exact_file(path: Path, expected: str) -> None:
    if type(expected) is not str or SHA64.fullmatch(expected) is None:
        raise ValueError("bound SHA-256 must be an exact lowercase string")
    if digest(path.read_bytes()) != expected:
        raise ValueError(f"bound file drift: {path}")


def validate_protocol(protocol: Mapping[str, Any], root: Path) -> None:
    if protocol.get("schema") != PROTOCOL_SCHEMA:
        raise ValueError("protocol schema drift")
    if protocol.get("status") != "FROZEN_AWAITING_POST_MERGE_EXECUTION":
        raise ValueError("protocol execution chronology drift")
    if type(protocol.get("issue")) is not int or protocol["issue"] != 1086:
        raise ValueError("issue identity drift")
    frozen_at = datetime.fromisoformat(protocol.get("frozen_at"))
    if frozen_at.tzinfo is None:
        raise ValueError("protocol freeze must be timezone-aware")
    corpus = protocol.get("corpus")
    contract = protocol.get("objective_gold_contract")
    runner = protocol.get("runner")
    if not all(isinstance(row, Mapping) for row in (corpus, contract, runner)):
        raise TypeError("bound artifact records are required")
    if corpus.get("path") != CORPUS_PATH or contract.get("path") != CONTRACT_PATH:
        raise ValueError("corpus/contract path binding drift")
    if runner.get("path") != RUNNER_PATH:
        raise ValueError("runner path binding drift")
    exact_file(root / corpus["path"], corpus["sha256"])
    exact_file(root / contract["path"], contract["sha256"])
    exact_file(root / runner["path"], runner["sha256"])
    counts = (
        corpus.get("repository_count"),
        corpus.get("eligible_repository_count"),
        corpus.get("eligible_organization_count"),
    )
    if any(type(value) is not int for value in counts) or counts != (45, 31, 14):
        raise ValueError("frozen corpus counts drift")
    if tuple(protocol.get("required_observations", ())) != OBSERVATIONS:
        raise ValueError("required observation set/order drift")
    if protocol.get("allowed_repository_redirects") != {
        "jquery/qunit": "qunitjs/qunit",
        "vuejs/vite": "vitejs/vite",
    }:
        raise ValueError("repository redirect allowlist drift")
    if protocol.get("execution_source_contract") != {
        "required_branch": "main",
        "clean_worktree_required": True,
        "committed_blob_equality_required": True,
        "protocol_raw_file_sha256_required": True,
    }:
        raise ValueError("execution source contract drift")
    fetch = protocol.get("fetch_contract")
    if not isinstance(fetch, Mapping) or fetch != {
        "transport": "https_git",
        "depth": 2,
        "tags": False,
        "partial_clone_filter": "blob:none",
        "timeout_seconds_per_command": 300,
    }:
        raise ValueError("fetch contract drift")
    retention = protocol.get("retention")
    if not isinstance(retention, Mapping) or retention != {
        "all_45_rows_required": True,
        "license_ineligible_rows": "EXCLUDED_LICENSE_CANNOT_CHECK",
        "failed_eligible_rows": "CANNOT_CHECK",
        "observed_digest_mismatch_rows": "OBJECTIVE_MISMATCH",
        "upstream_repository_or_license_bytes_redistributed": False,
    }:
        raise ValueError("retention contract drift")
    authority = protocol.get("authority", {})
    for flag in (
        "creates_campaign_result",
        "closes_issue_external_campaign_gate",
        "grants_objective_gold_before_live_execution",
        "grants_independent_adjudication",
        "grants_protected_custody",
        "grants_population_inference",
    ):
        if authority.get(flag) is not False:
            raise ValueError(f"authority flag must remain false: {flag}")
    if authority.get("scientific_authority_delta") != "NONE":
        raise ValueError("scientific authority delta drift")


def validate_corpus(corpus: Mapping[str, Any], protocol: Mapping[str, Any]) -> None:
    if corpus.get("schema") != CORPUS_SCHEMA:
        raise ValueError("corpus schema drift")
    entries = corpus.get("entries")
    if not isinstance(entries, list) or len(entries) != 45:
        raise ValueError("corpus must contain exactly 45 entries")
    if any(type(row.get("gold_eligible")) is not bool for row in entries):
        raise ValueError("gold eligibility must be exact Boolean")
    eligible = [row for row in entries if row["gold_eligible"]]
    if len(eligible) != 31:
        raise ValueError("eligible corpus must contain exactly 31 entries")
    if len({row["org_login"] for row in eligible}) != 14:
        raise ValueError("eligible organization count drift")
    seen: set[str] = set()
    freeze = datetime.fromisoformat(protocol["frozen_at"])
    aliases = protocol["allowed_repository_redirects"]
    for row in entries:
        if type(row.get("repo_id")) is not str or REPO.fullmatch(row["repo_id"]) is None:
            raise ValueError("repository identity drift")
        if row["repo_id"].split("/", 1)[0].lower() == "szechunyiu":
            raise ValueError("every SzeChunYiu-owned repository is an inadmissible subject")
        if row["repo_id"] in seen:
            raise ValueError("duplicate repository identity")
        seen.add(row["repo_id"])
        if row.get("org_login") != row["repo_id"].split("/", 1)[0]:
            raise ValueError("organization/repository binding drift")
        if type(row.get("pinned_sha")) is not str or SHA40.fullmatch(row["pinned_sha"]) is None:
            raise ValueError("pinned commit identity drift")
        if row["pinned_sha"] == "0" * 40:
            raise ValueError("zero pinned commit identity is inadmissible")
        if row.get("url") != f"https://github.com/{row['repo_id']}":
            raise ValueError("repository URL does not bind repository identity")
        retrieved = datetime.fromisoformat(row.get("retrieval_utc"))
        if retrieved.tzinfo is None or retrieved > freeze:
            raise ValueError("repository retrieval chronology drift")
        license_row = row.get("license")
        if not isinstance(license_row, Mapping):
            raise TypeError("license record is required")
        if row["gold_eligible"]:
            if license_row.get("verification") != "VERIFIED_WITH_URL_AND_DATE":
                raise ValueError("eligible license verification drift")
            if type(license_row.get("evidence_fetch_sha256")) is not str or SHA64.fullmatch(license_row["evidence_fetch_sha256"]) is None:
                raise ValueError("eligible license digest drift")
            match = LICENSE_URL.fullmatch(license_row.get("evidence_url"))
            if match is None:
                raise ValueError("eligible license URL drift")
            expected_repo = aliases.get(row["repo_id"], row["repo_id"])
            if match.group(1) != expected_repo or match.group(2) != row.get("pinned_ref"):
                raise ValueError("license URL repository/ref binding drift")
            license_path(license_row["evidence_url"])
        elif license_row.get("verification") != "CANNOT_CHECK__LICENSE_UNCLEAR":
            raise ValueError("ineligible license status drift")


def validate_execution_source(root: Path) -> dict[str, Any]:
    status = subprocess.check_output(["git", "status", "--porcelain"], cwd=root)
    if status:
        raise ValueError("execution requires a clean worktree before result creation")
    branch = subprocess.check_output(
        ["git", "branch", "--show-current"], cwd=root, text=True
    ).strip()
    if branch != "main":
        raise ValueError("post-merge acquisition must execute from branch main")
    source_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip()
    if SHA40.fullmatch(source_commit) is None or source_commit == "0" * 40:
        raise ValueError("source commit identity is invalid")
    paths = (PROTOCOL_PATH, RUNNER_PATH, CORPUS_PATH, CONTRACT_PATH)
    equality: dict[str, str] = {}
    for rel in paths:
        committed = subprocess.check_output(["git", "show", f"{source_commit}:{rel}"], cwd=root)
        observed = (root / rel).read_bytes()
        if committed != observed:
            raise ValueError(f"worktree bytes do not equal committed source: {rel}")
        equality[rel] = digest(observed)
    return {
        "source_commit": source_commit,
        "source_branch": branch,
        "committed_blob_equality": equality,
    }


def command(
    argv: Sequence[str], *, cwd: Path, timeout: int, retain_stdout: bool = False
) -> tuple[subprocess.CompletedProcess[bytes] | None, dict[str, Any]]:
    receipt: dict[str, Any] = {"argv": list(argv), "attempted": True}
    try:
        completed = subprocess.run(argv, cwd=cwd, capture_output=True, timeout=timeout, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        stdout = getattr(exc, "stdout", b"") or b""
        stderr = getattr(exc, "stderr", b"") or b""
        if isinstance(stdout, str):
            stdout = stdout.encode()
        if isinstance(stderr, str):
            stderr = stderr.encode()
        receipt.update({
            "exit_code": None,
            "error_type": type(exc).__name__,
            "stdout_sha256": digest(stdout),
            "stdout_bytes": len(stdout),
            "stderr_sha256": digest(stderr),
            "stderr_bytes": len(stderr),
        })
        return None, receipt
    receipt = {
        "argv": list(argv),
        "attempted": True,
        "exit_code": completed.returncode,
        "stdout_sha256": digest(completed.stdout),
        "stdout_bytes": len(completed.stdout),
        "stderr_sha256": digest(completed.stderr),
        "stderr_bytes": len(completed.stderr),
    }
    if retain_stdout:
        receipt["stdout_utf8"] = completed.stdout.decode("utf-8")
    return completed, receipt


def license_path(url: str) -> str:
    match = LICENSE_URL.fullmatch(url)
    if match is None or not match.group(3) or ".." in Path(match.group(3)).parts:
        raise ValueError("license evidence URL has no safe repository-relative path")
    return match.group(3)


def acquire(entry: Mapping[str, Any], root: Path, timeout: int) -> dict[str, Any]:
    base = {
        "repository": entry["repo_id"],
        "organization": entry["org_login"],
        "repository_remote": f"{entry['url']}.git",
        "pinned_sha": entry["pinned_sha"],
        "gold_eligible": entry["gold_eligible"],
        "command_receipts": [],
    }
    if entry["gold_eligible"] is not True:
        return {**base, "status": "EXCLUDED_LICENSE_CANNOT_CHECK", "reason": entry["license"]["verification"]}
    try:
        repo = root / entry["repo_id"].replace("/", "__")
        base["setup_receipts"] = [{"operation": "mkdir", "target": repo.name, "attempted": True}]
        repo.mkdir()
        calls = (
            (["git", "init", "--bare", "."], False),
            (["git", "remote", "add", "origin", f"{entry['url']}.git"], False),
            (["git", "fetch", "--depth=2", "--no-tags", "--filter=blob:none", "origin", entry["pinned_sha"]], False),
            (["git", "update-ref", "HEAD", entry["pinned_sha"]], False),
            (["git", "rev-parse", "--verify", "HEAD"], True),
            (["git", "cat-file", "-e", f"{entry['pinned_sha']}^{{commit}}"], False),
            (["git", "rev-list", "--parents", "-n", "1", entry["pinned_sha"]], True),
            (["git", "show", "-s", "--format=%ct", entry["pinned_sha"]], True),
        )
        outputs: list[bytes] = []
        for argv, retain in calls:
            completed, receipt = command(argv, cwd=repo, timeout=timeout, retain_stdout=retain)
            base["command_receipts"].append(receipt)
            if completed is None or completed.returncode != 0:
                return {**base, "status": "CANNOT_CHECK", "reason": f"command failed: {argv[1]}"}
            outputs.append(completed.stdout)
        if outputs[4].decode().strip() != entry["pinned_sha"]:
            return {**base, "status": "CANNOT_CHECK", "reason": "pre-derivation HEAD mismatch"}
        ancestry = outputs[6].decode().strip().split()
        if not ancestry or ancestry[0] != entry["pinned_sha"]:
            return {**base, "status": "CANNOT_CHECK", "reason": "rev-list head mismatch"}
        parents = ancestry[1:]
        for parent in parents:
            completed, receipt = command(["git", "cat-file", "-e", f"{parent}^{{commit}}"], cwd=repo, timeout=timeout)
            base["command_receipts"].append(receipt)
            if completed is None or completed.returncode != 0:
                return {**base, "status": "CANNOT_CHECK", "reason": "direct parent object unavailable"}
        path = license_path(entry["license"]["evidence_url"])
        completed, receipt = command(["git", "show", f"{entry['pinned_sha']}:{path}"], cwd=repo, timeout=timeout)
        base["command_receipts"].append(receipt)
        if completed is None or completed.returncode != 0:
            return {**base, "status": "CANNOT_CHECK", "reason": "license blob unavailable", "license_path": path}
        observed_license = digest(completed.stdout)
        final_head, receipt = command(["git", "rev-parse", "--verify", "HEAD"], cwd=repo, timeout=timeout, retain_stdout=True)
        base["command_receipts"].append(receipt)
        if final_head is None or final_head.returncode != 0 or final_head.stdout.decode().strip() != entry["pinned_sha"]:
            return {**base, "status": "CANNOT_CHECK", "reason": "post-derivation HEAD mismatch"}
        if observed_license != entry["license"]["evidence_fetch_sha256"]:
            return {
                **base,
                "status": "OBJECTIVE_MISMATCH",
                "reason": "license digest mismatch",
                "license_label": "DIGEST_MISMATCH",
                "license_path": path,
                "observed_license_sha256": observed_license,
            }
        receipts_digest = digest(canonical(base["command_receipts"]))
        return {
            **base,
            "status": "VERIFIED_OBJECT_FACTS",
            "direct_parent_shas": parents,
            "committer_epoch": int(outputs[7].decode().strip()),
            "license_path": path,
            "license_sha256": observed_license,
            "command_receipts_sha256": receipts_digest,
        }
    except (OSError, UnicodeError, ValueError, subprocess.SubprocessError) as exc:
        return {**base, "status": "CANNOT_CHECK", "reason": f"{type(exc).__name__}: {exc}"}


def execute(protocol: Mapping[str, Any], corpus: Mapping[str, Any], root: Path, scratch: Path, jobs: int) -> dict[str, Any]:
    validate_protocol(protocol, root)
    validate_corpus(corpus, protocol)
    source = validate_execution_source(root)
    started_at = datetime.now(timezone.utc).isoformat()
    timeout = protocol["fetch_contract"]["timeout_seconds_per_command"]
    def safe_acquire(row: Mapping[str, Any]) -> dict[str, Any]:
        try:
            return acquire(row, scratch, timeout)
        except Exception as exc:  # fail closed per-row; never abort the corpus map
            return {
                "repository": row.get("repo_id"),
                "organization": row.get("org_login"),
                "pinned_sha": row.get("pinned_sha"),
                "gold_eligible": row.get("gold_eligible"),
                "repository_remote": f"{row.get('url')}.git",
                "command_receipts": [],
                "status": "CANNOT_CHECK",
                "reason": f"unhandled {type(exc).__name__}: {exc}",
                "setup_attempted": True,
            }

    with ThreadPoolExecutor(max_workers=jobs) as pool:
        rows = list(pool.map(safe_acquire, corpus["entries"]))
    for row in rows:
        row["command_receipts_sha256"] = digest(canonical(row["command_receipts"]))
    verified = [row for row in rows if row["status"] == "VERIFIED_OBJECT_FACTS"]
    verified_orgs = {row["organization"] for row in verified}
    terminal = (
        "P13_P14_LIVE_GIT_ACQUISITION_MINIMUM_MET__CAMPAIGN_RESULT_NOT_CREATED"
        if len(verified) >= 30 and len(verified_orgs) >= 5
        else "P13_P14_LIVE_GIT_ACQUISITION_MINIMUM_NOT_MET__CAMPAIGN_BLOCKED"
    )
    result = {
        "schema": RESULT_SCHEMA,
        "protocol_sha256": digest(canonical(protocol)),
        "protocol_file_sha256": digest((root / PROTOCOL_PATH).read_bytes()),
        "runner_sha256": digest(Path(__file__).read_bytes()),
        "corpus_file_sha256": digest((root / protocol["corpus"]["path"]).read_bytes()),
        "objective_gold_contract_file_sha256": digest((root / protocol["objective_gold_contract"]["path"]).read_bytes()),
        "source_commit": source["source_commit"],
        "source_branch": source["source_branch"],
        "committed_blob_equality": source["committed_blob_equality"],
        "execution_started_at": started_at,
        "execution_finished_at": datetime.now(timezone.utc).isoformat(),
        "observed_environment": {
            "git": subprocess.check_output(["git", "--version"], text=True).strip(),
            "python": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "platform": platform.platform(),
            "executable": sys.executable,
        },
        "repository_rows": rows,
        "retained_repository_count": len(rows),
        "verified_repository_count": len(verified),
        "verified_organization_count": len(verified_orgs),
        "terminal": terminal,
        "campaign_result_created": False,
        "issue_external_campaign_gate": "OPEN",
        "scientific_authority_delta": "NONE",
        "independent_adjudication": "CANNOT_CHECK",
        "protected_custody": "CANNOT_CHECK",
    }
    result["receipt_sha256"] = digest(canonical(result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--scratch", type=Path)
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    protocol = json.loads(args.protocol.read_text())
    corpus = json.loads((root / protocol["corpus"]["path"]).read_text())
    if type(args.jobs) is not int or not 1 <= args.jobs <= 8:
        raise ValueError("jobs must be an integer from 1 to 8")
    if args.out.exists():
        raise FileExistsError("refusing to overwrite an existing acquisition receipt")
    if args.scratch is None:
        with tempfile.TemporaryDirectory(prefix="orion-p13-p14-live-git-") as temporary:
            result = execute(protocol, corpus, root, Path(temporary), args.jobs)
    else:
        args.scratch.mkdir(parents=True, exist_ok=False)
        result = execute(protocol, corpus, root, args.scratch, args.jobs)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["terminal"])
    return 0 if "MINIMUM_MET" in result["terminal"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
