#!/usr/bin/env python3
"""P13+P14 corpus git-license-binding acquisition V1.

Successor to the adverse live-Git acquisition V1
(P13_P14_LIVE_GIT_ACQUISITION_MINIMUM_NOT_MET__CAMPAIGN_BLOCKED): every
eligible corpus row failed its digest gate because the frozen
`evidence_fetch_sha256` hashes an unretained GitHub REST representation, not
git blob bytes. That adverse terminal stands untouched.

This increment REPAIRS the instrumentation, not the outcome: it observes,
from live Git objects at each pinned sha, the license blob's path (parsed
from the frozen evidence_url), git blob SHA-1, blob-byte SHA-256 and byte
length, and records them as NEW receipted bindings under a NEW identity.
The old field is never relabelled; where the observed blob-byte hash differs
from `evidence_fetch_sha256` the row records OBSERVED_DIFFERS_FROM_REST_HASH
as context, evidencing nothing beyond the V1 diagnosis.

Receipts only; no gold, no policy, scientific_authority_delta NONE.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import platform
import re
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any

GIT_TIMEOUT_S = 900
BLOB_URL = re.compile(r"https://github\.com/([^/]+/[^/]+)/blob/([^/]+)/(.+)$")


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


class Receipts:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def run(self, argv: list[str], cwd: Path | None = None) -> tuple[int, bytes, bytes]:
        started = utc_now()
        try:
            proc = subprocess.run(argv, cwd=cwd, capture_output=True, timeout=GIT_TIMEOUT_S)
            code, out, err = proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired:
            code, out, err = -1, b"", b"TIMEOUT"
        except OSError as exc:
            code, out, err = -2, b"", str(exc).encode()
        self.rows.append(
            {
                "utc": started,
                "argv": argv,
                "cwd": str(cwd) if cwd else None,
                "exit": code,
                "stdout_sha256": sha256_bytes(out),
                "stderr_sha256": sha256_bytes(err),
            }
        )
        return code, out, err

    def chain_digest(self) -> str:
        h = hashlib.sha256()
        for row in self.rows:
            h.update(json.dumps(row, sort_keys=True).encode())
        return h.hexdigest()


def ensure_clone(rc: Receipts, workdir: Path, repo_id: str, url: str) -> Path | None:
    dest = workdir / repo_id.replace("/", "__")
    if (dest / "HEAD").is_file() or (dest / ".git").is_dir():
        rc.run(["git", "-C", str(dest), "fetch", "origin", "--prune"])
        return dest
    code, _, _ = rc.run(
        ["git", "clone", "--filter=blob:none", "--no-checkout", "--bare", url, str(dest)]
    )
    return dest if code == 0 else None


def object_exists(rc: Receipts, clone: Path, sha: str) -> bool:
    code, _, _ = rc.run(["git", "-C", str(clone), "cat-file", "-e", f"{sha}^{{commit}}"])
    if code == 0:
        return True
    rc.run(["git", "-C", str(clone), "fetch", "origin", sha])
    code, _, _ = rc.run(["git", "-C", str(clone), "cat-file", "-e", f"{sha}^{{commit}}"])
    return code == 0


def observe_entry(rc: Receipts, clone: Path, entry: dict[str, Any]) -> dict[str, Any]:
    obs: dict[str, Any] = {}
    sha = entry["pinned_sha"]
    if not object_exists(rc, clone, sha):
        obs["status"] = "CANNOT_CHECK__PINNED_OBJECT_UNRETRIEVABLE"
        return obs
    m = BLOB_URL.match(entry["license"].get("evidence_url") or "")
    if not m:
        obs["status"] = "CANNOT_CHECK__NO_PARSEABLE_LICENSE_PATH"
        return obs
    path = m.group(3)
    obs["license_path"] = path
    code, out, _ = rc.run(["git", "-C", str(clone), "rev-parse", f"{sha}:{path}"])
    if code != 0:
        obs["status"] = "CANNOT_CHECK__LICENSE_PATH_UNRESOLVED_AT_PIN"
        return obs
    obs["git_blob_sha1"] = out.decode().strip()
    code, out, _ = rc.run(["git", "-C", str(clone), "cat-file", "blob", f"{sha}:{path}"])
    if code != 0:
        obs["status"] = "CANNOT_CHECK__BLOB_UNREADABLE"
        return obs
    obs["blob_byte_sha256"] = sha256_bytes(out)
    obs["blob_bytes"] = len(out)
    rest = entry["license"].get("evidence_fetch_sha256")
    obs["rest_hash_context"] = (
        "OBSERVED_EQUALS_REST_HASH"
        if rest == obs["blob_byte_sha256"]
        else "OBSERVED_DIFFERS_FROM_REST_HASH"
    )
    obs["status"] = "BINDING_RECORDED"
    return obs


def flip_last_hex(s: str) -> str:
    return s[:-1] + ("0" if s[-1] != "0" else "1")


def planted_controls(rc: Receipts, workdir: Path, entry: dict[str, Any]) -> dict[str, Any]:
    """Planted violations through the SAME observe path: forged pin must fail
    retrieval; forged license path must fail resolution."""
    out: dict[str, Any] = {"subject": entry["repo_id"]}
    forged_pin = dict(entry)
    forged_pin["pinned_sha"] = flip_last_hex(entry["pinned_sha"])
    clone = ensure_clone(rc, workdir, entry["repo_id"], entry["url"])
    if clone is None:
        out["status"] = "CANNOT_CHECK__CONTROL_SUBJECT_UNAVAILABLE"
        return out
    a = observe_entry(rc, clone, forged_pin)
    out["control_a_forged_pin_status"] = a.get("status")
    out["control_a_fired"] = a.get("status") != "BINDING_RECORDED"
    forged_path = json.loads(json.dumps(entry))
    forged_path["license"]["evidence_url"] = entry["license"]["evidence_url"] + ".does-not-exist"
    b = observe_entry(rc, clone, forged_path)
    out["control_b_forged_path_status"] = b.get("status")
    out["control_b_fired"] = b.get("status") != "BINDING_RECORDED"
    out["status"] = (
        "CONTROLS_FIRED"
        if out["control_a_fired"] and out["control_b_fired"]
        else "CANNOT_CHECK__CONTROL_FAILURE"
    )
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--protocol", type=Path, required=True)
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--workdir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--source-commit", required=True)
    args = ap.parse_args()

    protocol_bytes = args.protocol.read_bytes()
    protocol = json.loads(protocol_bytes)
    corpus_bytes = args.corpus.read_bytes()
    if protocol["bindings"]["corpus_sha256"] != sha256_bytes(corpus_bytes):
        print("BINDING_DRIFT corpus", file=sys.stderr)
        return 3
    corpus = json.loads(corpus_bytes)

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
        "clone_filter": "--filter=blob:none",
    }

    records = []
    for entry in corpus["entries"]:
        rc = Receipts()
        clone = ensure_clone(rc, args.workdir, entry["repo_id"], entry["url"])
        if clone is None:
            obs: dict[str, Any] = {"status": "CANNOT_CHECK__CLONE_FAILED"}
        else:
            obs = observe_entry(rc, clone, entry)
        records.append(
            {
                "repo_id": entry["repo_id"],
                "org_login": entry["org_login"],
                "pinned_sha": entry["pinned_sha"],
                "gold_eligible": entry.get("gold_eligible", False),
                "observation": obs,
                "raw_command_receipt_digest": rc.chain_digest(),
                "receipts": rc.rows,
            }
        )
        print(f"[{utc_now()}] {entry['repo_id']}: {obs['status']}", flush=True)

    rc_ctl = Receipts()
    controls = planted_controls(rc_ctl, args.workdir, corpus["entries"][0])
    controls["raw_command_receipt_digest"] = rc_ctl.chain_digest()

    statuses = [r["observation"]["status"] for r in records]
    recorded = statuses.count("BINDING_RECORDED")
    if controls.get("status") != "CONTROLS_FIRED":
        run_terminal = "CANNOT_CHECK__CONTROL_FAILURE"
    elif recorded == len(records):
        run_terminal = "T1_ALL_BINDINGS_RECORDED"
    elif recorded > 0:
        run_terminal = "T2_PARTIAL_BINDINGS_RECORDED"
    else:
        run_terminal = "T3_NO_BINDING_RECORDED"

    result = {
        "schema": "ORION.P13P14.CorpusGitLicenseBinding.v1",
        "environment": env,
        "environment_receipts": rc_env.rows,
        "planted_controls": controls,
        "counts": {
            "entries": len(records),
            "bindings_recorded": recorded,
            "differs_from_rest_hash": sum(
                1
                for r in records
                if r["observation"].get("rest_hash_context") == "OBSERVED_DIFFERS_FROM_REST_HASH"
            ),
            "equals_rest_hash": sum(
                1
                for r in records
                if r["observation"].get("rest_hash_context") == "OBSERVED_EQUALS_REST_HASH"
            ),
        },
        "run_terminal": run_terminal,
        "boundaries": {
            "v1_adverse_terminal_untouched": True,
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
