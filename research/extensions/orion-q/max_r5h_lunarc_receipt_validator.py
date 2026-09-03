#!/usr/bin/env python3
"""Structural validator for committed LUNARC execution receipts of the MAX-R5H
legs that cannot run inside CI (measured 2026-09-03: N2 subject and DEV
development both exceed 2h40m on a 2-core runner against a 30-minute job
timeout; CI rc=124 at 9600s while the 58.3s H4 subject passes).

Receipt envelope (one JSON file per leg, glob MAX_R5H_LUNARC_RECEIPT_*.json):
    schema             ORIONQ.MAXR5H.LunarcReceipt.V1
    leg                "SUBJECT:H4" | "SUBJECT:N2" | "DEV"
    exec_host          non-empty (e.g. "lunarc-cosmos slurm lu partition")
    slurm_job_id       non-empty digits
    wall_seconds       int > 0 (observed wall time of the leg)
    timeout_seconds    int > 0 (the `timeout` budget the leg ran under)
    completed_utc      ISO-8601 timestamp
    log_sha256         64 lowercase hex of the captured stdout log
    payload            the exact engine output object

Payload rules (by leg):
    SUBJECT:<S>  payload.schema == ORIONQ.MAXR5H.SubjectFast.v1,
                 payload.subject == <S>, and payload.result has the real frozen
                 fast-runner shape (the earlier arms->variants reading never
                 matched an actual SubjectFast.v1 result and would have
                 rejected the first real receipt): scalars subject/source_blob/
                 n_qubits/terms + stats leaves B0_Pauli_LCU and
                 B1_R5G_pair_reference + frontier sizes + non-empty
                 donor/mixed_window_meta lists + non-empty B2_donor_named /
                 B3_mixed_named variant dicts (each value None or a stats leaf)
                 + the three frozen booleans. A stats leaf is a dict with
                 integer CNOT > 0 and 64-hex partition_sha256. The chunked
                 instrument's extra top-level "chunked" provenance key is
                 allowed alongside schema/subject/result.
    DEV          payload.schema == ORIONQ.MAXR5H.MixedCardinalityDevelopment.v1,
                 payload.subjects a non-empty dict keyed by frozen subject
                 names, payload.r5h_development_pass a bool.

Exit codes: 0 with ORIONQ_MAX_R5H_RECEIPTS=VALIDATED n=<k> when all receipts
are structurally valid; 0 with ORIONQ_MAX_R5H_RECEIPTS=PENDING when no receipt
files are committed yet (receipts are produced by 8h-budget LUNARC jobs and
land as a follow-up commit); 2 with ORIONQ_MAX_R5H_RECEIPTS=INVALID when any
committed receipt fails validation. PENDING is never reported when a receipt
file exists — a present-but-broken receipt is a hard failure, and "cannot
check" is never conflated with "checked and fine".
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENVELOPE_SCHEMA = "ORIONQ.MAXR5H.LunarcReceipt.V1"
SUBJECT_PAYLOAD_SCHEMA = "ORIONQ.MAXR5H.SubjectFast.v1"
DEV_PAYLOAD_SCHEMA = "ORIONQ.MAXR5H.MixedCardinalityDevelopment.v1"
LEG_RE = re.compile(r"^(SUBJECT:(H4|N2)|DEV)$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
FROZEN_SUBJECTS = ("H4", "N2")


def _fail(path: Path, problems: list[str], msg: str) -> None:
    problems.append(f"{path.name}: {msg}")


def _stats_leaf_ok(stats: object, problems: list[str], where: str) -> bool:
    """A stats leaf (serialize() output) has integer CNOT > 0 and 64-hex
    partition_sha256; the remaining keys (Lambda, histogram, ...) are the
    engine's own and are not re-derived here."""
    if not isinstance(stats, dict):
        problems.append(f"{where}: stats leaf is not an object")
        return False
    cnot = stats.get("CNOT")
    if not isinstance(cnot, int) or isinstance(cnot, bool) or cnot <= 0:
        problems.append(f"{where}: CNOT {cnot!r} not a positive int")
        return False
    part = stats.get("partition_sha256")
    if not isinstance(part, str) or not HEX64_RE.match(part):
        problems.append(f"{where}: partition_sha256 {part!r} not 64-hex")
        return False
    return True


def validate_receipt(path: Path, problems: list[str]) -> None:
    try:
        doc = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        _fail(path, problems, f"unreadable/invalid JSON ({exc})")
        return
    if not isinstance(doc, dict):
        _fail(path, problems, "envelope is not an object")
        return
    if doc.get("schema") != ENVELOPE_SCHEMA:
        _fail(path, problems, f"envelope schema {doc.get('schema')!r} != {ENVELOPE_SCHEMA!r}")
        return
    for key in ("leg", "exec_host", "slurm_job_id", "completed_utc", "log_sha256"):
        if not isinstance(doc.get(key), str) or not doc[key]:
            _fail(path, problems, f"field {key!r} missing/empty")
            return
    if not LEG_RE.match(doc["leg"]):
        _fail(path, problems, f"leg {doc['leg']!r} not in SUBJECT:H4|SUBJECT:N2|DEV")
        return
    if not doc["slurm_job_id"].isdigit():
        _fail(path, problems, f"slurm_job_id {doc['slurm_job_id']!r} not numeric")
    if not HEX64_RE.match(doc["log_sha256"]):
        _fail(path, problems, "log_sha256 not 64 lowercase hex")
    for key in ("wall_seconds", "timeout_seconds"):
        val = doc.get(key)
        if not isinstance(val, int) or isinstance(val, bool) or val <= 0:
            _fail(path, problems, f"field {key!r} not a positive int")
            return
    if doc["wall_seconds"] >= doc["timeout_seconds"]:
        _fail(path, problems, "wall_seconds >= timeout_seconds: leg hit its budget, result is not a completion")

    payload = doc.get("payload")
    if not isinstance(payload, dict):
        _fail(path, problems, "payload missing/not an object")
        return
    if doc["leg"].startswith("SUBJECT:"):
        subject = doc["leg"].split(":", 1)[1]
        if payload.get("schema") != SUBJECT_PAYLOAD_SCHEMA:
            _fail(path, problems, f"payload schema {payload.get('schema')!r} != {SUBJECT_PAYLOAD_SCHEMA!r}")
            return
        if payload.get("subject") != subject:
            _fail(path, problems, f"payload.subject {payload.get('subject')!r} != leg subject {subject!r}")
            return
        result = payload.get("result")
        if not isinstance(result, dict) or not result:
            _fail(path, problems, "payload.result missing/empty")
            return
        name = path.name
        if not isinstance(result.get("subject"), str) or result["subject"] != subject:
            _fail(path, problems, f"result.subject {result.get('subject')!r} != {subject!r}")
            return
        for key in ("n_qubits", "terms", "donor_direct_frontier_size", "mixed_frontier_size"):
            val = result.get(key)
            if not isinstance(val, int) or isinstance(val, bool) or val <= 0:
                _fail(path, problems, f"result.{key} {val!r} not a positive int")
                return
        if not isinstance(result.get("source_blob"), str) or not result["source_blob"]:
            _fail(path, problems, "result.source_blob missing/empty")
            return
        for key in ("mixed_balanced_uses_TARE",
                    "mixed_balanced_distinct_from_all_donor_resources",
                    "r5h_subject_development_pass"):
            if not isinstance(result.get(key), bool):
                _fail(path, problems, f"result.{key} not a bool")
                return
        for key in ("B0_Pauli_LCU", "B1_R5G_pair_reference"):
            if not _stats_leaf_ok(result.get(key), problems, f"{name}: result.{key}"):
                return
        for key in ("donor_window_meta", "mixed_window_meta"):
            meta = result.get(key)
            if not isinstance(meta, list) or not meta:
                _fail(path, problems, f"result.{key} not a non-empty list")
                return
            for i, w in enumerate(meta):
                if not isinstance(w, dict) or not isinstance(w.get("start"), int) \
                        or not isinstance(w.get("global_frontier_after"), int):
                    _fail(path, problems, f"result.{key}[{i}] missing start/global_frontier_after ints")
                    return
        for key in ("B2_donor_named", "B3_mixed_named"):
            variants = result.get(key)
            if not isinstance(variants, dict) or not variants:
                _fail(path, problems, f"result.{key} missing/empty")
                return
            for variant, stats in variants.items():
                if stats is None:
                    continue  # a named variant the frontier does not contain is legal
                if not _stats_leaf_ok(stats, problems, f"{name}: result.{key}[{variant!r}]"):
                    return
    else:  # DEV
        if payload.get("schema") != DEV_PAYLOAD_SCHEMA:
            _fail(path, problems, f"payload schema {payload.get('schema')!r} != {DEV_PAYLOAD_SCHEMA!r}")
            return
        subjects = payload.get("subjects")
        if not isinstance(subjects, dict) or not subjects:
            _fail(path, problems, "payload.subjects missing/empty")
            return
        for name in subjects:
            if name not in FROZEN_SUBJECTS:
                _fail(path, problems, f"payload.subjects key {name!r} not a frozen subject")
                return
        if not isinstance(payload.get("r5h_development_pass"), bool):
            _fail(path, problems, "payload.r5h_development_pass not a bool")


def run(directory: Path = HERE) -> int:
    receipts = sorted(directory.glob("MAX_R5H_LUNARC_RECEIPT_*.json"))
    if not receipts:
        print("ORIONQ_MAX_R5H_RECEIPTS=PENDING reason=no-receipt-files-committed")
        return 0
    problems: list[str] = []
    legs: list[str] = []
    for path in receipts:
        validate_receipt(path, problems)
        try:
            legs.append(json.loads(path.read_text()).get("leg", "?"))
        except (OSError, json.JSONDecodeError):
            legs.append("?")
    dupes = {leg for leg in legs if legs.count(leg) > 1 and leg != "?"}
    if dupes:
        problems.append(f"duplicate leg receipts: {sorted(dupes)}")
    if problems:
        print("ORIONQ_MAX_R5H_RECEIPTS=INVALID")
        for line in problems:
            print(f"  {line}", file=sys.stderr)
        return 2
    print(f"ORIONQ_MAX_R5H_RECEIPTS=VALIDATED n={len(receipts)} legs={','.join(legs)}")
    return 0


def main() -> int:
    return run(HERE)


if __name__ == "__main__":
    raise SystemExit(main())
