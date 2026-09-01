#!/usr/bin/env python3
"""Hash-bind frozen WorkflowHub before/after RO-Crate content without gold.

Raw ZIP hashes are transport receipts only. Scientific content identity is a
canonical digest over member paths, uncompressed bytes and minimal Unix file
semantics, so ZIP timestamps/order/compression cannot manufacture a change.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import io
import json
import stat
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SNAPSHOT_DIR = HERE / "workflowhub-source-census-v1"
MAX_BYTES = 256 * 1024 * 1024
UA = "ORION-A3-content-binding-v2/1.0 (+https://github.com/SzeChunYiu/ORION)"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_snapshot() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    m = json.loads((SNAPSHOT_DIR / "CENSUS_SNAPSHOT_V1.json").read_text())
    if m.get("schema") != "ORION.A3.WorkflowHubVersionedSourceCensusSnapshotManifest.v1":
        raise ValueError("snapshot manifest schema mismatch")
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for c in m["chunks"]:
        p = ROOT / c["path"]
        raw = p.read_bytes()
        if sha256_bytes(raw) != c["sha256"]:
            raise ValueError(f"snapshot chunk hash mismatch: {c['path']}")
        d = json.loads(raw)
        if d.get("schema") != "ORION.A3.WorkflowHubVersionedSourceCensusChunk.v1":
            raise ValueError("snapshot chunk schema mismatch")
        cols = d["columns"]
        for values in d["candidate_rows"]:
            row = dict(zip(cols, values, strict=True))
            if row["workflow_id"] in seen:
                raise ValueError("duplicate workflow id in snapshot")
            seen.add(row["workflow_id"])
            rows.append(row)
    digest = hashlib.sha256(
        json.dumps([[r[c] for c in m["columns"]] for r in rows], separators=(",", ":")).encode()
    ).hexdigest()
    if digest != m["snapshot_candidate_rows_sha256"]:
        raise ValueError("combined snapshot rows digest mismatch")
    if len(rows) != m["versioned_public_licensed_candidate_families"] != 128:
        raise ValueError("snapshot candidate count mismatch")
    return m, rows


def read_limited(response: Any, max_bytes: int = MAX_BYTES) -> bytes:
    declared = response.headers.get("Content-Length")
    if declared is not None:
        try:
            if int(declared) > max_bytes:
                raise ValueError(f"RO-Crate Content-Length exceeds {max_bytes} bytes")
        except ValueError as exc:
            if "exceeds" in str(exc):
                raise
    data = response.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError(f"RO-Crate exceeds {max_bytes} bytes")
    return data


def canonical_member_path(name: str) -> str:
    if not name or "\\" in name:
        raise ValueError(f"non-canonical ZIP member path: {name!r}")
    p = PurePosixPath(name)
    if p.is_absolute() or ".." in p.parts or "." in p.parts:
        raise ValueError(f"unsafe ZIP member path: {name!r}")
    rendered = p.as_posix()
    if rendered != name.rstrip("/"):
        raise ValueError(f"non-canonical ZIP member path: {name!r}")
    return rendered


def member_semantics(info: zipfile.ZipInfo) -> tuple[str, bool]:
    mode = (info.external_attr >> 16) & 0xFFFF
    kind_bits = stat.S_IFMT(mode)
    if kind_bits == stat.S_IFLNK:
        kind = "symlink"
    elif kind_bits in (0, stat.S_IFREG):
        kind = "regular"
    else:
        kind = f"other:{kind_bits:o}"
    executable = bool(mode & 0o111)
    return kind, executable


def normalized_content_manifest(zf: zipfile.ZipFile) -> tuple[list[dict[str, Any]], bytes]:
    infos = zf.infolist()
    seen: set[str] = set()
    entries: list[dict[str, Any]] = []
    metadata_bytes: bytes | None = None
    metadata_count = 0
    for info in infos:
        path = canonical_member_path(info.filename)
        if path in seen:
            raise ValueError(f"duplicate ZIP member path: {path}")
        seen.add(path)
        if info.is_dir():
            continue
        data = zf.read(info)
        kind, executable = member_semantics(info)
        entries.append({
            "path": path,
            "bytes": len(data),
            "sha256": sha256_bytes(data),
            "kind": kind,
            "executable": executable,
        })
        if path == "ro-crate-metadata.json":
            metadata_count += 1
            metadata_bytes = data
    if metadata_count != 1 or metadata_bytes is None:
        raise ValueError("RO-Crate zip must contain exactly one root ro-crate-metadata.json")
    entries.sort(key=lambda x: x["path"])
    return entries, metadata_bytes


def validate_rocrate_bytes(data: bytes) -> dict[str, Any]:
    if not data:
        raise ValueError("empty RO-Crate response")
    try:
        with zipfile.ZipFile(io.BytesIO(data), "r") as zf:
            bad = zf.testzip()
            if bad is not None:
                raise ValueError(f"RO-Crate zip CRC failure: {bad}")
            entries, metadata = normalized_content_manifest(zf)
    except zipfile.BadZipFile as exc:
        raise ValueError("response is not a valid ZIP") from exc
    return {
        "raw_archive_bytes": len(data),
        "raw_archive_sha256": sha256_bytes(data),
        "normalized_content_manifest_sha256": canonical_json_sha(entries),
        "ro_crate_metadata_sha256": sha256_bytes(metadata),
        "normalized_member_count": len(entries),
    }


def fetch_rocrate(workflow_id: str, version: int, retries: int = 3, timeout: float = 120.0) -> dict[str, Any]:
    url = f"https://workflowhub.eu/workflows/{urllib.parse.quote(workflow_id, safe='')}/ro_crate?version={version}"
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status = getattr(resp, "status", 200)
                if status != 200:
                    raise RuntimeError(f"HTTP {status}")
                data = read_limited(resp)
                result = validate_rocrate_bytes(data)
                result.update({
                    "url": url,
                    "content_type": resp.headers.get("Content-Type"),
                    "etag": resp.headers.get("ETag"),
                })
                return result
        except (urllib.error.URLError, TimeoutError, RuntimeError, ValueError, OSError) as exc:
            last = exc
            if attempt + 1 < retries:
                time.sleep(0.75 * (attempt + 1))
    raise RuntimeError(f"failed RO-Crate fetch after {retries} attempts: {last}")


def bind_pair(row: dict[str, Any]) -> dict[str, Any]:
    wid = row["workflow_id"]
    before = int(row["version_before"])
    after = int(row["version_after"])
    base = {
        "workflow_id": wid,
        "version_before": before,
        "version_after": after,
        "license_before": row["license_before"],
        "license_after": row["license_after"],
        "metadata_sha256_before": row["metadata_sha256_before"],
        "metadata_sha256_after": row["metadata_sha256_after"],
    }
    try:
        b = fetch_rocrate(wid, before)
        a = fetch_rocrate(wid, after)
        same = b["normalized_content_manifest_sha256"] == a["normalized_content_manifest_sha256"]
        return {
            **base,
            "status": "UNCHANGED_NORMALIZED_CONTENT" if same else "NORMALIZED_CONTENT_BOUND_DIFFERENT",
            "before": b,
            "after": a,
            "normalized_content_sha256_differ": not same,
        }
    except Exception as exc:
        return {**base, "status": "CANNOT_CHECK_NORMALIZED_CONTENT_BINDING", "reason": str(exc)[:500]}


def bind_all(max_workers: int = 2) -> dict[str, Any]:
    m, rows = load_snapshot()
    results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(bind_pair, row): row["workflow_id"] for row in rows}
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda r: (0, int(r["workflow_id"])) if str(r["workflow_id"]).isdigit() else (1, r["workflow_id"]))
    bound = [r for r in results if r["status"] == "NORMALIZED_CONTENT_BOUND_DIFFERENT"]
    unchanged = [r for r in results if r["status"] == "UNCHANGED_NORMALIZED_CONTENT"]
    failures = [r for r in results if r["status"] == "CANNOT_CHECK_NORMALIZED_CONTENT_BINDING"]
    result_digest = canonical_json_sha(results)
    success = len(bound) == 128 and not unchanged and not failures
    return {
        "schema": "ORION.A3.WorkflowHubNormalizedContentBindingResult.v2",
        "terminal": (
            "WORKFLOWHUB_128_FROZEN_FAMILIES_NORMALIZED_ROCRATE_CONTENT_BOUND"
            if success else "CANNOT_CHECK_WORKFLOWHUB_NORMALIZED_CONTENT_BINDING_FOR_128_FAMILIES"
        ),
        "source_snapshot_rows_sha256": m["snapshot_candidate_rows_sha256"],
        "source_candidate_manifest_sha256": m["candidate_manifest_sha256"],
        "candidate_n": len(results),
        "normalized_content_bound_different_n": len(bound),
        "unchanged_normalized_content_n": len(unchanged),
        "cannot_check_n": len(failures),
        "result_rows_sha256": result_digest,
        "results": results,
        "raw_zip_hash_is_transport_receipt_only": True,
        "change_stratum_adjudicated": False,
        "external_gold_accessed": False,
        "protected_orion_predictions_accessed": False,
        "scientific_authority_delta": "NONE__PUBLIC_NORMALIZED_CONTENT_HASH_PREFLIGHT_ONLY",
    }


def make_zip(entries: list[tuple[str, bytes]], *, compression: int, date: tuple[int, int, int, int, int, int]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=compression) as zf:
        for name, payload in entries:
            info = zipfile.ZipInfo(name, date_time=date)
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.compress_type = compression
            zf.writestr(info, payload)
    return buf.getvalue()


def self_test() -> dict[str, Any]:
    entries = [("ro-crate-metadata.json", b"{}"), ("workflow.cwl", b"cwlVersion: v1.2\n")]
    z1 = make_zip(entries, compression=zipfile.ZIP_STORED, date=(2020, 1, 1, 0, 0, 0))
    z2 = make_zip(list(reversed(entries)), compression=zipfile.ZIP_DEFLATED, date=(2026, 1, 1, 0, 0, 0))
    r1, r2 = validate_rocrate_bytes(z1), validate_rocrate_bytes(z2)
    assert r1["raw_archive_sha256"] != r2["raw_archive_sha256"]
    assert r1["normalized_content_manifest_sha256"] == r2["normalized_content_manifest_sha256"]
    changed = make_zip(
        [("ro-crate-metadata.json", b"{}"), ("workflow.cwl", b"cwlVersion: v1.2\n# changed\n")],
        compression=zipfile.ZIP_DEFLATED,
        date=(2026, 1, 1, 0, 0, 0),
    )
    assert validate_rocrate_bytes(changed)["normalized_content_manifest_sha256"] != r1["normalized_content_manifest_sha256"]
    bad = io.BytesIO()
    with zipfile.ZipFile(bad, "w") as zf:
        zf.writestr("workflow.cwl", "x")
    try:
        validate_rocrate_bytes(bad.getvalue())
    except ValueError as exc:
        assert "metadata" in str(exc)
    else:
        raise AssertionError("zip without RO-Crate metadata accepted")
    try:
        validate_rocrate_bytes(b"not-a-zip")
    except ValueError as exc:
        assert "ZIP" in str(exc)
    else:
        raise AssertionError("nonzip accepted")
    m, rows = load_snapshot()
    assert len(rows) == 128
    assert m["snapshot_candidate_rows_sha256"] == "a2d9f82fb78a0b73b9f6fa623cc9c115dddc25387208be17165140b6d2973f55"
    return {
        "decision": "GREEN",
        "snapshot_n": len(rows),
        "raw_zip_nuisance_normalized": True,
        "semantic_change_detected": True,
        "invalid_zip_rejected": True,
        "missing_metadata_rejected": True,
        "network_accessed": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--output", type=Path)
    ap.add_argument("--workers", type=int, default=2)
    args = ap.parse_args()
    if args.self_test:
        result = self_test()
        code = 0
    else:
        if not 1 <= args.workers <= 2:
            ap.error("--workers must be 1..2")
        result = bind_all(args.workers)
        code = 0 if result["terminal"].startswith("WORKFLOWHUB_128") else 2
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
