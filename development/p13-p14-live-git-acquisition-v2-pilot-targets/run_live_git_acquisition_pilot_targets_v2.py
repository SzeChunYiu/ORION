#!/usr/bin/env python3
"""P13+P14 live-Git acquisition runner V1.

Executes the acquisition increment named by the frozen pilot
(`development/p13-p14-public-lifecycle-v1/`, status
FROZEN_ACQUISITION_PILOT_AWAITING_EXECUTION): re-observe the pinned
public-repository facts from live Git objects, retaining a command receipt
digest for every observation. This increment creates acquisition receipts
ONLY. It derives no gold, evaluates no policy, and grants no scientific
authority (`scientific_authority_delta: NONE`).

Design contract: P13_P14_LIVE_GIT_ACQUISITION_PROTOCOL_V1.json (same dir).
Fail-closed: any predicate error, timeout, or partial evidence yields
CANNOT_CHECK for that observation; no label is inferred from absent evidence.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import platform
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any

CLONE_FILTER = "--filter=blob:none"
GIT_TIMEOUT_S = 900


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


class Receipts:
    """Append-only receipted command executor."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def run(self, argv: list[str], cwd: Path | None = None) -> tuple[int, bytes, bytes]:
        started = utc_now()
        try:
            proc = subprocess.run(
                argv, cwd=cwd, capture_output=True, timeout=GIT_TIMEOUT_S
            )
            code, out, err = proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired:
            code, out, err = -1, b"", b"TIMEOUT"
        except OSError as exc:  # git missing, path errors
            code, out, err = -2, b"", str(exc).encode()
        self.rows.append(
            {
                "utc": started,
                "argv": argv,
                "cwd": str(cwd) if cwd else None,
                "exit": code,
                "stdout_sha256": sha256_bytes(out),
                "stderr_sha256": sha256_bytes(err),
                "stdout_excerpt": out[:120].decode("utf-8", "replace"),
            }
        )
        return code, out, err

    def chain_digest(self) -> str:
        h = hashlib.sha256()
        for row in self.rows:
            h.update(json.dumps(row, sort_keys=True).encode())
        return h.hexdigest()


def ensure_clone(rc: Receipts, workdir: Path, repository: str, url: str) -> Path | None:
    dest = workdir / repository.replace("/", "__")
    if (dest / ".git").is_dir() or (dest / "HEAD").is_file():
        code, _, _ = rc.run(["git", "-C", str(dest), "fetch", "origin", "--prune"])
        return dest if code == 0 else dest  # stale fetch still allows object checks
    code, _, _ = rc.run(
        ["git", "clone", CLONE_FILTER, "--no-checkout", "--bare", url, str(dest)]
    )
    return dest if code == 0 else None


def object_exists(rc: Receipts, clone: Path, sha: str, url: str) -> str:
    """EXISTS | ABSENT | CANNOT_CHECK__OBJECT_UNRETRIEVABLE"""
    code, _, _ = rc.run(["git", "-C", str(clone), "cat-file", "-e", f"{sha}^{{commit}}"])
    if code == 0:
        return "EXISTS"
    # A force-pushed head may be unadvertised; one recorded retrieval attempt.
    rc.run(["git", "-C", str(clone), "fetch", "origin", sha])
    code, _, _ = rc.run(["git", "-C", str(clone), "cat-file", "-e", f"{sha}^{{commit}}"])
    if code == 0:
        return "EXISTS"
    return "CANNOT_CHECK__OBJECT_UNRETRIEVABLE"


def direct_parent(rc: Receipts, clone: Path, head: str, parent: str) -> str:
    code, out, _ = rc.run(["git", "-C", str(clone), "rev-list", "--parents", "-n", "1", head])
    if code != 0:
        return "CANNOT_CHECK"
    fields = out.decode().split()
    if len(fields) < 1 or fields[0] != head:
        return "CANNOT_CHECK"
    return "TRUE" if parent in fields[1:] else "FALSE"


def license_blob(rc: Receipts, clone: Path, head: str, path: str, blob_sha1: str) -> str:
    code, out, _ = rc.run(["git", "-C", str(clone), "rev-parse", f"{head}:{path}"])
    if code != 0:
        return "CANNOT_CHECK"
    return "MATCH" if out.decode().strip() == blob_sha1 else "MISMATCH"


def license_bytes(
    rc: Receipts, clone: Path, head: str, path: str, want_sha256: str, want_bytes: int
) -> str:
    code, out, _ = rc.run(["git", "-C", str(clone), "cat-file", "blob", f"{head}:{path}"])
    if code != 0:
        return "CANNOT_CHECK"
    if sha256_bytes(out) == want_sha256 and len(out) == want_bytes:
        return "MATCH"
    return "MISMATCH"


def observe_pilot(rc: Receipts, clone: Path, row: dict[str, Any]) -> dict[str, str]:
    head = row["head_sha"]
    lic = row["license"]
    obs = {
        "head_object_exists": object_exists(rc, clone, head, row["source_url"]),
        "parent_object_exists": object_exists(rc, clone, row["parent_sha"], row["source_url"]),
    }
    obs["parent_is_direct_parent"] = (
        direct_parent(rc, clone, head, row["parent_sha"])
        if obs["head_object_exists"] == "EXISTS"
        else "CANNOT_CHECK"
    )
    if obs["head_object_exists"] == "EXISTS":
        obs["license_blob_matches_git_object"] = license_blob(
            rc, clone, head, lic["path"], lic["git_blob_sha1"]
        )
        obs["license_sha256_matches_blob_bytes"] = license_bytes(
            rc, clone, head, lic["path"], lic["sha256"], lic["bytes"]
        )
    else:
        obs["license_blob_matches_git_object"] = "CANNOT_CHECK"
        obs["license_sha256_matches_blob_bytes"] = "CANNOT_CHECK"
    return obs


def observe_corpus(rc: Receipts, clone: Path, entry: dict[str, Any]) -> dict[str, str]:
    return {
        "pinned_object_exists": object_exists(
            rc, clone, entry["pinned_sha"], entry["url"]
        )
    }


def record_terminal(obs: dict[str, str]) -> str:
    labels = list(obs.values())
    if any(v in ("FALSE", "MISMATCH", "ABSENT") for v in labels):
        return "DIVERGENT"
    if any(v.startswith("CANNOT_CHECK") for v in labels):
        return "CANNOT_CHECK"
    return "VERIFIED_ALL"


def flip_last_hex(sha: str) -> str:
    last = sha[-1]
    repl = "0" if last != "0" else "1"
    return sha[:-1] + repl


def planted_controls(rc: Receipts, workdir: Path, pilot_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Two planted violations routed through the SAME predicates as real records.

    A: forged head sha (one hex flipped) must NOT verify as EXISTS.
    B: forged license sha256 must yield MISMATCH via the same byte comparison.
    A control that cannot fire is worse than none; failure of either control
    invalidates the whole run (CANNOT_CHECK__CONTROL_FAILURE).
    """
    base = pilot_rows[0]
    clone = ensure_clone(rc, workdir, base["repository"], base["source_url"])
    out: dict[str, Any] = {"subject": base["repository"]}
    if clone is None:
        out["status"] = "CANNOT_CHECK__CONTROL_SUBJECT_UNAVAILABLE"
        return out
    forged_head = flip_last_hex(base["head_sha"])
    a = object_exists(rc, clone, forged_head, base["source_url"])
    out["control_a_forged_head_label"] = a
    out["control_a_fired"] = a != "EXISTS"
    lic = base["license"]
    b = license_bytes(
        rc, clone, base["head_sha"], lic["path"], flip_last_hex(lic["sha256"]), lic["bytes"]
    )
    out["control_b_forged_license_label"] = b
    out["control_b_fired"] = b == "MISMATCH"
    out["status"] = (
        "CONTROLS_FIRED"
        if out["control_a_fired"] and out["control_b_fired"]
        else "CANNOT_CHECK__CONTROL_FAILURE"
    )
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--protocol", type=Path, required=True)
    ap.add_argument("--workdir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--source-commit", required=True)
    ap.add_argument("--only", default=None, help="single repository id to (re)acquire")
    args = ap.parse_args()

    protocol_bytes = args.protocol.read_bytes()
    protocol = json.loads(protocol_bytes)
    pilot = json.loads((args.protocol.parent.parent / "p13-p14-public-lifecycle-v1" / "P13_P14_PUBLIC_LIFECYCLE_PROTOCOL_V1.json").read_bytes())
    corpus_path = args.protocol.parent.parent.parent / "papers" / "orion-23-responsibility-carrying-state" / "P13_P14_PINNED_REPOSITORY_CORPUS_V1.json"
    corpus = json.loads(corpus_path.read_bytes())

    for name, want, got in (
        ("pilot_protocol", protocol["bindings"]["pilot_protocol_sha256"], sha256_bytes((args.protocol.parent.parent / "p13-p14-public-lifecycle-v1" / "P13_P14_PUBLIC_LIFECYCLE_PROTOCOL_V1.json").read_bytes())),
        ("corpus", protocol["bindings"]["corpus_sha256"], sha256_bytes(corpus_path.read_bytes())),
    ):
        if want != got:
            print(f"BINDING_DRIFT {name} want={want} got={got}", file=sys.stderr)
            return 3

    args.workdir.mkdir(parents=True, exist_ok=True)
    rc_env = Receipts()
    rc_env.run(["git", "--version"])
    env = {
        "utc": utc_now(),
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "protocol_sha256": sha256_bytes(protocol_bytes),
        "runner_sha256": sha256_bytes(Path(__file__).read_bytes()),
        "source_commit": args.source_commit,
        "clone_filter": CLONE_FILTER,
    }

    records: list[dict[str, Any]] = []
    subjects: list[tuple[str, dict[str, Any]]] = [
        ("ACQUISITION_TARGET", r) for r in pilot["records"]
    ] + [("CORPUS_PIN", e) for e in corpus["entries"]]

    for role, row in subjects:
        repo = row.get("repository") or row.get("repo_id")
        if args.only and repo != args.only:
            continue
        url = row.get("source_url") or row.get("url")
        rc = Receipts()
        clone = ensure_clone(rc, args.workdir, repo, url)
        if clone is None:
            obs: dict[str, str] = {"clone": "CANNOT_CHECK__CLONE_FAILED"}
        elif role == "ACQUISITION_TARGET":
            obs = observe_pilot(rc, clone, row)
        else:
            obs = observe_corpus(rc, clone, row)
        records.append(
            {
                "repository": repo,
                "role": role,
                "remote": url,
                "observations": obs,
                "record_terminal": record_terminal(obs),
                "raw_command_receipt_digest": rc.chain_digest(),
                "receipts": rc.rows,
            }
        )
        print(f"[{utc_now()}] {role} {repo}: {records[-1]['record_terminal']}", flush=True)

    rc_ctl = Receipts()
    controls = planted_controls(rc_ctl, args.workdir, pilot["records"])
    controls["raw_command_receipt_digest"] = rc_ctl.chain_digest()

    terminals = [r["record_terminal"] for r in records]
    if controls.get("status") != "CONTROLS_FIRED":
        run_terminal = "CANNOT_CHECK__CONTROL_FAILURE"
    elif any(t == "DIVERGENT" for t in terminals):
        run_terminal = "T2_DIVERGENCE_FOUND"
    elif any(t == "CANNOT_CHECK" for t in terminals):
        run_terminal = "T3_INCOMPLETE_CANNOT_CHECK"
    else:
        run_terminal = "T1_ALL_OBSERVATIONS_VERIFIED"

    result = {
        "schema": "ORION.P13P14.LiveGitAcquisitionReceipts.v1",
        "environment": env,
        "environment_receipts": rc_env.rows,
        "planted_controls": controls,
        "counts": {
            "subjects": len(records),
            "verified_all": terminals.count("VERIFIED_ALL"),
            "divergent": terminals.count("DIVERGENT"),
            "cannot_check": terminals.count("CANNOT_CHECK"),
        },
        "run_terminal": run_terminal,
        "boundaries": {
            "gold_derived": False,
            "policies_evaluated": False,
            "scientific_authority_delta": "NONE",
        },
        "records": records,
        "finished_utc": utc_now(),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print(f"run_terminal={run_terminal} -> {args.out}")
    return 0 if run_terminal.startswith("T1") else 2


if __name__ == "__main__":
    raise SystemExit(main())
