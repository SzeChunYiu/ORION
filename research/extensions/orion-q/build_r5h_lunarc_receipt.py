#!/usr/bin/env python3
"""Build a committed LUNARC execution receipt for a completed r5h/r5f probe leg.

Usage (on LUNARC, after the probe job finishes):
    python3 build_r5h_lunarc_receipt.py --leg SUBJECT:N2 --job-id 3569287 \
        --timeout 28800 --logfile /home/scyiu/r5hprobe/probe_n2long_3569287.out \
        --outfile MAX_R5H_LUNARC_RECEIPT_N2_V1.json

Extracts the engine's JSON line from the captured stdout, wraps it in the
ORIONQ.MAXR5H.LunarcReceipt.V1 envelope (wall time from sacct, sha256 of the
log, completion UTC from the log's mtime), and refuses to emit a receipt when
the leg hit its timeout budget (that is a non-completion requiring redesign,
not a receipt). The emitted file is validated by max_r5h_lunarc_receipt_validator.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ENVELOPE_SCHEMA = "ORIONQ.MAXR5H.LunarcReceipt.V1"
PREFIXES = {
    "SUBJECT": "ORIONQ_MAX_R5H_SUBJECT=",
    "DEV": "ORIONQ_MAX_R5H_DEV=",
}


def sacct_elapsed_seconds(job_id: str) -> tuple[int, str, str]:
    out = subprocess.run(
        ["sacct", "-j", job_id, "-o", "Elapsed,NodeList,State", "--noheader", "-P"],
        capture_output=True, text=True, check=True,
    ).stdout
    elapsed_s = node = state = ""
    for line in out.splitlines():
        parts = line.split("|")
        if len(parts) < 3 or "." in parts[0] or "_" in parts[0]:
            continue  # skip .batch/.extern and array-element suffixes
        elapsed_s, node, state = parts[0].strip(), parts[1].strip(), parts[2].strip()
        break
    if not elapsed_s:
        raise SystemExit(f"no sacct Elapsed row for job {job_id}")
    m = re.match(r"^(?:(\d+)-)?(\d+):(\d+):(\d+)$", elapsed_s)
    if not m:
        raise SystemExit(f"unparseable Elapsed {elapsed_s!r}")
    days, hh, mm, ss = (int(g or 0) for g in m.groups())
    return days * 86400 + hh * 3600 + mm * 60 + ss, node, state


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--leg", required=True, choices=["SUBJECT:H4", "SUBJECT:N2", "DEV"])
    ap.add_argument("--job-id", required=True)
    ap.add_argument("--timeout", type=int, default=28800)
    ap.add_argument("--logfile", required=True)
    ap.add_argument("--outfile", required=True)
    args = ap.parse_args()

    log = Path(args.logfile)
    raw = log.read_bytes()
    prefix = PREFIXES[args.leg.split(":", 1)[0]]
    payload = None
    for line in raw.decode("utf-8", "replace").splitlines():
        if line.startswith(prefix):
            payload = json.loads(line[len(prefix):])
            break
    if payload is None:
        print(f"RECEIPT=FAILED reason=no-{prefix}line-in-log", file=sys.stderr)
        return 2

    wall, node, state = sacct_elapsed_seconds(args.job_id)
    if wall >= args.timeout:
        print(f"RECEIPT=FAILED reason=budget-hit wall={wall}s timeout={args.timeout}s "
              f"state={state}: redesign required (chunking or drop), not a receipt",
              file=sys.stderr)
        return 2
    if "COMPLETED" not in state and state not in ("TIMEOUT", "CANCELLED"):
        # completed-with-resource-exit is fine; anything else is not a completion
        print(f"RECEIPT=FAILED reason=bad-state state={state}", file=sys.stderr)
        return 2

    envelope = {
        "schema": ENVELOPE_SCHEMA,
        "leg": args.leg,
        "exec_host": f"lunarc-cosmos slurm ({node or 'unknown-node'})",
        "slurm_job_id": str(args.job_id),
        "wall_seconds": wall,
        "timeout_seconds": args.timeout,
        "completed_utc": datetime.fromtimestamp(log.stat().st_mtime, tz=timezone.utc)
            .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "log_sha256": hashlib.sha256(raw).hexdigest(),
        "payload": payload,
    }
    Path(args.outfile).write_text(json.dumps(envelope, indent=2, sort_keys=True) + "\n")
    print(f"RECEIPT=WRITTEN {args.outfile} wall={wall}s leg={args.leg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
