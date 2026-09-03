#!/usr/bin/env python3
"""R3 PROSPECTIVE byte binding for Zenodo census-V2 candidates (M5/M6).

Route R3_ZENODO_RELATED_DATA (P4_NATURAL_PAIR_SOURCE_EXPANSION_FREEZE_V1.json):
content gate = "exact CC BY 4.0 or CC0 record, typed IsSupplementTo/IsDocumentedBy/
IsReferencedBy relation, separately hashed files and attribution".

Input: the frozen census P4_ZENODO_RELATED_OBJECT_CANDIDATES_V2.jsonl (metadata +
record licence already recorded there; census result V2 sha256-pinned). This stage
binds actual FILE BYTES for a bounded subset of CC BY 4.0 / CC0 records via the
official Zenodo Records API: per-record file enumeration, per-file sha256 of
downloaded bytes, provider md5 cross-check, append-only access log. PDF/data bytes
stay OUTSIDE the repository; only receipts/hashes/logs are committed.

PROSPECTIVE harvesting only: no eligibility adjudication, no pair adjudication,
no protected outcomes, no scientific authority.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

MIN_INTERVAL_SECONDS = 2.5
RETRIES = 3
TIMEOUT_SECONDS = 180.0
MAX_FILE_BYTES = 256 * 1024 * 1024
USER_AGENT = "ORION-P4-A5-zenodo-bytes-binding-v1/1.0 (research source binding; https://github.com/SzeChunYiu/ORION)"
ALLOWED_LICENSES = {"cc-by-4.0", "cc-zero"}
EXPECTED_CENSUS_CANDIDATES_SHA256 = "d6f767e88cdc401dd1f7643ed76e4460645fcc3dff9744dc504fed01351c1247"


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def md5_bytes(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


class Fetcher:
    def __init__(self, log_path: Path, interval: float = MIN_INTERVAL_SECONDS) -> None:
        self.log_path = log_path
        self.interval = interval
        self.last_request_at = 0.0
        self.requests = 0
        self._fh = log_path.open("a", encoding="utf-8")

    def _log(self, record: dict[str, Any]) -> None:
        self._fh.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
        self._fh.flush()

    def get(self, url: str, context: dict[str, Any] | None = None) -> tuple[bytes, int, str]:
        last: Exception | None = None
        for attempt in range(1, RETRIES + 1):
            delay = self.interval - (time.monotonic() - self.last_request_at)
            if delay > 0:
                time.sleep(delay)
            started = utc_now()
            self.last_request_at = time.monotonic()
            self.requests += 1
            try:
                req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json,*/*;q=0.1"})
                with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as response:
                    status = getattr(response, "status", 200)
                    if status != 200:
                        raise RuntimeError(f"HTTP {status}")
                    declared = response.headers.get("Content-Length")
                    if declared and int(declared) > MAX_FILE_BYTES:
                        raise ValueError(f"file Content-Length exceeds cap: {declared}")
                    data = response.read(MAX_FILE_BYTES + 1)
                    if len(data) > MAX_FILE_BYTES:
                        raise ValueError("file exceeds byte cap")
                    self._log({"ts_utc": utc_now(), "event": "http_attempt", "request_started_utc": started, "url": url, "http_status": status, "final_url": response.geturl(), "bytes": len(data), "sha256": sha256_bytes(data), "outcome": "OK", **(context or {})})
                    return data, status, response.geturl()
            except urllib.error.HTTPError as exc:
                last = exc
                self._log({"ts_utc": utc_now(), "event": "http_attempt", "request_started_utc": started, "url": url, "http_status": exc.code, "outcome": "FAILED" if attempt == RETRIES else "RETRY", "error": f"HTTPError {exc.code}", **(context or {})})
                if exc.code in (400, 401, 403, 404, 410):
                    raise
            except (urllib.error.URLError, TimeoutError, RuntimeError, ValueError, OSError) as exc:
                last = exc
                self._log({"ts_utc": utc_now(), "event": "http_attempt", "request_started_utc": started, "url": url, "outcome": "FAILED" if attempt == RETRIES else "RETRY", "error": f"{type(exc).__name__}: {str(exc)[:300]}", **(context or {})})
            if attempt < RETRIES:
                time.sleep(self.interval * 2 * attempt)
        raise RuntimeError(f"failed after {RETRIES} attempts: {url}: {last}")

    def close(self) -> None:
        self._fh.close()


def load_candidates(path: Path) -> list[dict[str, Any]]:
    raw = path.read_bytes()
    if sha256_bytes(raw) != EXPECTED_CENSUS_CANDIDATES_SHA256:
        raise ValueError("census candidates JSONL sha256 mismatch (frozen input)")
    rows = [json.loads(l) for l in raw.decode("utf-8").splitlines() if l.strip()]
    return rows


def select_records(rows: list[dict[str, Any]], per_cell_cap: int, max_files_per_record: int) -> list[tuple[dict[str, Any], int]]:
    """Round-robin across (domain, mechanism) cells; CC BY 4.0 first, then CC0."""
    cells: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for r in rows:
        if r.get("license_id") not in ALLOWED_LICENSES:
            continue
        cells.setdefault((r["domain_id"], r["mechanism_id"]), []).append(r)
    for key in cells:
        cells[key].sort(key=lambda r: (r.get("license_id") != "cc-by-4.0", r.get("publication_date") or "",))
    selected: list[tuple[dict[str, Any], int]] = []
    round_idx = 0
    while len(selected) < sum(min(len(v), per_cell_cap) for v in cells.values()):
        progressed = False
        for key in sorted(cells):
            bucket = cells[key]
            if round_idx < min(len(bucket), per_cell_cap):
                r = bucket[round_idx]
                n_files = min(int(r.get("public_file_count") or 1), max_files_per_record)
                selected.append((r, max(n_files, 1)))
                progressed = True
                if len(selected) >= 200:
                    return selected
        if not progressed:
            break
        round_idx += 1
    return selected


def snapshot_policies(fetcher: Fetcher, dirp: Path) -> list[dict[str, Any]]:
    dirp.mkdir(parents=True, exist_ok=True)
    targets = [
        ("zenodo_developers_api_2026-09-03.html", "https://developers.zenodo.org/"),
        ("zenodo_principles_2026-09-03.html", "https://about.zenodo.org/principles/"),
        ("zenodo_terms_2026-09-03.html", "https://about.zenodo.org/terms/"),
    ]
    manifest = []
    for name, url in targets:
        try:
            data, status, final = fetcher.get(url, context={"phase": "policy_snapshot", "target": name})
            (dirp / name).write_bytes(data)
            manifest.append({"file": name, "url": url, "final_url": final, "http_status": status, "bytes": len(data), "sha256": sha256_bytes(data)})
        except Exception as exc:
            manifest.append({"file": name, "url": url, "error": f"{type(exc).__name__}: {str(exc)[:200]}"})
    (dirp / "SNAPSHOT_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", type=Path, default=here.parent.parent / "P4_ZENODO_RELATED_OBJECT_CANDIDATES_V2.jsonl")
    ap.add_argument("--out-dir", type=Path, default=here)
    ap.add_argument("--bytes-dir", type=Path, required=True)
    ap.add_argument("--run-host", default="unknown")
    ap.add_argument("--per-cell-cap", type=int, default=8)
    ap.add_argument("--max-files-per-record", type=int, default=2)
    ap.add_argument("--max-records", type=int, default=48)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    fetcher = Fetcher(args.out_dir / "ACCESS_LOG_V1.jsonl")
    started = utc_now()
    policies: list[dict[str, Any]] = []
    receipts: list[dict[str, Any]] = []
    try:
        policies = snapshot_policies(fetcher, args.out_dir / "policy_snapshots")
        rows = load_candidates(args.candidates)
        selected = select_records(rows, args.per_cell_cap, args.max_files_per_record)[: args.max_records]
        for cand, n_files in selected:
            api_url = cand["record_api_url"]
            try:
                data, status, final = fetcher.get(api_url, context={"phase": "record_api", "record_id": cand["record_id"]})
                rec = json.loads(data.decode("utf-8"))
            except Exception as exc:
                receipts.append({"mechanism_id": cand["mechanism_id"], "domain_id": cand["domain_id"], "record_id": cand["record_id"], "doi": cand["doi"], "status": "RECORD_API_CANNOT_CHECK", "reason": f"{type(exc).__name__}: {str(exc)[:300]}"})
                continue
            md = rec.get("metadata", {})
            files = rec.get("files", []) or []
            out_files = []
            for f in files[:n_files]:
                links = f.get("links", {})
                furl = links.get("self") or links.get("download")
                entry: dict[str, Any] = {"file_key": f.get("key"), "file_size": f.get("size"), "provider_checksum": f.get("checksum"), "url": furl}
                if not furl:
                    entry["status"] = "FILE_URL_MISSING"
                    out_files.append(entry)
                    continue
                if (f.get("size") or 0) > MAX_FILE_BYTES:
                    entry["status"] = "FILE_EXCEEDS_BYTE_CAP_NOT_DOWNLOADED"
                    out_files.append(entry)
                    continue
                try:
                    fdata, fstatus, _ = fetcher.get(furl, context={"phase": "file_bytes", "record_id": cand["record_id"], "file": f.get("key")})
                    safe = (f.get("key") or "file").replace("/", "_").replace("\\", "_").replace("..", "_")
                    dest = args.bytes_dir / "zenodo" / f"{cand['record_id']}__{safe}"
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(fdata)
                    entry.update({"status": "FILE_BYTES_BOUND", "http_status": fstatus, "bytes": len(fdata), "sha256": sha256_bytes(fdata), "md5": md5_bytes(fdata), "bytes_relpath": str(dest.relative_to(args.bytes_dir)), "provider_md5_match": (f.get("checksum") or "").endswith(md5_bytes(fdata))})
                except Exception as exc:
                    entry["status"] = "FILE_FETCH_FAILED"
                    entry["error"] = f"{type(exc).__name__}: {str(exc)[:200]}"
                out_files.append(entry)
            receipts.append({
                "mechanism_id": cand["mechanism_id"],
                "domain_id": cand["domain_id"],
                "status": "PROSPECTIVE_ZENODO_BYTES_BOUND",
                "record_id": cand["record_id"],
                "conceptrecid": cand.get("conceptrecid"),
                "doi": cand.get("doi"),
                "title": md.get("title") or cand.get("title"),
                "creators": [c.get("name") for c in (md.get("creators") or [])][:12],
                "license_id": (md.get("license") or {}).get("id") or cand.get("license_id"),
                "record_metadata_sha256": sha256_bytes(data),
                "publication_related_identifiers": cand.get("publication_related_identifiers"),
                "rights_note": "record-level licence from Zenodo metadata; per-file hashes bound below; linked-object rights not inferred",
                "files": out_files,
                "fetched_at_utc": utc_now(),
            })
    finally:
        fetcher.close()
    with (args.out_dir / "BINDING_V1_RECEIPTS.jsonl").open("w", encoding="utf-8") as fh:
        for r in receipts:
            fh.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")
    bound_files = sum(1 for r in receipts for f in r.get("files", []) if f.get("status") == "FILE_BYTES_BOUND")
    md5_ok = sum(1 for r in receipts for f in r.get("files", []) if f.get("provider_md5_match") is True)
    result = {
        "schema": "ORION.A5.ZenodoCandidateBytesBinding.v1",
        "route_id": "R3_ZENODO_RELATED_DATA",
        "status": "PROSPECTIVE_BYTE_BINDING_EXECUTED",
        "input_census": {"candidates_jsonl": str(args.candidates.name), "candidates_sha256": EXPECTED_CENSUS_CANDIDATES_SHA256, "rows": 173},
        "run_provenance": {"run_host": args.run_host, "started_utc": started, "finished_utc": utc_now(), "http_requests": fetcher.requests},
        "network_policy": {"maximum_concurrency": 1, "minimum_request_interval_seconds": MIN_INTERVAL_SECONDS, "retries": RETRIES, "timeout_seconds": TIMEOUT_SECONDS, "per_file_byte_cap": MAX_FILE_BYTES, "provider_hosts": ["zenodo.org", "www.zenodo.org"], "bytes_note": "file bytes stored outside repository at --bytes-dir; NOT committed"},
        "records_receipted_n": len(receipts),
        "files_byte_bound_n": bound_files,
        "provider_md5_crosscheck_match_n": md5_ok,
        "policy_snapshots": policies,
        "interpretation_boundary": {"prospective_only": True, "case_eligibility_adjudicated": False, "route_specific_pair_adjudication_performed": False, "grants_scientific_authority": False, "protected_orion_predictions_accessed": False, "external_gold_accessed": False},
    }
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    (args.out_dir / "RESULT_V1.json").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
