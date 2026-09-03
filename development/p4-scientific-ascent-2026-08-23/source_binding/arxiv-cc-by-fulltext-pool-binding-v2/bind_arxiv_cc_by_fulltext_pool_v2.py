#!/usr/bin/env python3
"""Exact-version full-text binding for ALL rows of the frozen A5 arXiv CC-BY pool.

Extends the 8-row live preflight (bind_arxiv_cc_by_fulltext_live_preflight_v1.py,
frozen network policy preserved verbatim) to every one of the 1536 pool rows.

Frozen etiquette (unchanged from preflight v1): serial fetch, one arXiv request in
flight, >= 3.1 s minimum interval between request starts, HTTPS-only arXiv hosts,
PDF signature + <= 64 MiB checks, per-item sha256. PDF bytes are stored OUTSIDE the
repository (--bytes-dir); only receipts, hashes and the append-only access log are
committed. Resumable: rows already bound with byte-verified receipts are skipped.

Authority boundary: this script binds exact source bytes and rights only. It
performs no pair adjudication, no case-eligibility decision, and accesses no
protected outcomes. It grants no scientific authority.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

EXPECTED_POOL_SHA256 = "47dd24657752731cdf45bab95852f3e18b50946af8a29b5acee95956ec81d895"
EXPECTED_ROWS = 1536
EXPECTED_PER_DOMAIN = {"EARTH_ENVIRONMENT": 384, "LIFE_BIOMEDICAL": 384, "PHYSICAL_ENGINEERING": 384, "SCIENTIFIC_SOFTWARE": 384}
# Durable live receipts already pinned by workflow run 33542940707 (RESULT_V1.json).
EXPECTED_PREFLIGHT_BINDINGS = {
    "1801.09096v1": "71bfd9838971530820eec7f8c433647686a5c6a988fbb4bf2888b787d802f5da",
    "2007.07828v1": "8ad451cb16b12295446c4495e2a212f9edaea7483efc6788429e28ee463adcb3",
    "1801.00636v1": "adff320e9e73d575037d2e41b850f11a0d8f1c585b292a03e6f64bba008b32f9",
    "1808.02195v2": "31bf4b3025199d9bd1320abff4d6b122c31db5b7bbee8ed7bf9a1ebdcd3c7d20",
    "1801.04644v1": "8b5b9cf2e38c53abbaa1237f56174b5bda3a755407333e004a4f04409ca3bc52",
    "2103.11013v1": "68ad94ee7f37f8d370d04e8a027f7a3cc0552676e30ed8b463d5b8064022def4",
    "1801.02128v1": "6b534137f95df42ff20d60cde7de3fb8348ad38b61eb3f7c79dab1aa00cdce75",
    "1909.05128v1": "9190ebe40c51a28505644213a8ebbf3f3ab5aef72f9ba7283a801cbdb0cfae13",
}
REQUEST_INTERVAL_SECONDS = 3.1
MAX_PDF_BYTES = 64 * 1024 * 1024
USER_AGENT = "ORION-P4-A5-fulltext-pool-binding-v2/1.0 (research source binding; https://github.com/SzeChunYiu/ORION)"
PDF_HOSTS = {"arxiv.org", "export.arxiv.org"}
VERSION_RE = re.compile(r"v[1-9][0-9]*\Z")
RETRIES_PER_PDF = 3
TIMEOUT_SECONDS = 120.0

SCHEMA = "ORION.A5.ArxivCCByFulltextPoolBinding.v2"
TERMINAL_COMPLETE = "ARXIV_CC_BY_EXACT_VERSION_FULLTEXT_POOL_BINDING_COMPLETE"
TERMINAL_INCOMPLETE = "ARXIV_CC_BY_EXACT_VERSION_FULLTEXT_POOL_BINDING_INCOMPLETE__RESUME_REQUIRED"


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_sha(value: Any) -> str:
    return sha256_bytes(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))


def validate_row(row: dict[str, Any]) -> None:
    required = {"schema_version", "domain_id", "arxiv_id", "exact_version", "exact_arxiv_id", "abstract", "abstract_sha256", "content_license", "content_license_url", "immutable_abs_url", "immutable_pdf_url", "immutable_source_url", "attribution", "binding_state"}
    missing = sorted(required - set(row))
    if missing:
        raise ValueError(f"source row missing required keys: {missing}")
    if row["schema_version"] != "orion.p4.arxiv-ccby-source-frame.v1":
        raise ValueError("source row schema mismatch")
    if row["content_license"] != "CC BY 4.0" or row["content_license_url"] != "https://creativecommons.org/licenses/by/4.0/":
        raise ValueError("source row is not exact CC BY 4.0")
    if row["binding_state"] != "CONTENT_LICENSE_CONFIRMED__CASE_ELIGIBILITY_UNADJUDICATED":
        raise ValueError("source row binding state mismatch")
    if row["domain_id"] not in EXPECTED_PER_DOMAIN:
        raise ValueError(f"unexpected source domain: {row['domain_id']}")
    version = str(row["exact_version"])
    if not VERSION_RE.fullmatch(version):
        raise ValueError(f"invalid exact version: {version!r}")
    exact = f"{row['arxiv_id']}{version}"
    if row["exact_arxiv_id"] != exact:
        raise ValueError("exact_arxiv_id is not arxiv_id + exact_version")
    if row["immutable_abs_url"] != f"https://arxiv.org/abs/{exact}" or row["immutable_pdf_url"] != f"https://arxiv.org/pdf/{exact}" or row["immutable_source_url"] != f"https://export.arxiv.org/e-print/{exact}":
        raise ValueError("immutable source URL mismatch")
    if sha256_bytes(str(row["abstract"]).encode("utf-8")) != row["abstract_sha256"]:
        raise ValueError("abstract_sha256 mismatch")


def load_frozen_pool(pool_path: Path, binding_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    binding = json.loads(binding_path.read_text(encoding="utf-8"))
    if binding.get("binding_id") != "P4.NAT.AXIS.768.ARXIV_CC_BY_POOL_1536.V1":
        raise ValueError("source binding id mismatch")
    frame = binding.get("frame", {})
    if frame.get("path") != pool_path.name or frame.get("sha256") != EXPECTED_POOL_SHA256 or frame.get("rows") != EXPECTED_ROWS:
        raise ValueError("source binding frame mismatch")
    if binding.get("outcomes_accessed") is not False or binding.get("grants_scientific_authority") is not False:
        raise ValueError("source binding authority boundary mismatch")
    raw = pool_path.read_bytes()
    if sha256_bytes(raw) != EXPECTED_POOL_SHA256:
        raise ValueError("frozen source pool SHA-256 mismatch")
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    per_domain = {k: 0 for k in EXPECTED_PER_DOMAIN}
    for line_no, line in enumerate(raw.decode("utf-8").splitlines(), 1):
        if not line.strip():
            raise ValueError(f"blank source-pool line {line_no}")
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"non-object source-pool line {line_no}")
        validate_row(row)
        exact = row["exact_arxiv_id"]
        if exact in seen:
            raise ValueError(f"duplicate exact arXiv id: {exact}")
        seen.add(exact)
        per_domain[row["domain_id"]] += 1
        rows.append(row)
    if len(rows) != EXPECTED_ROWS or per_domain != EXPECTED_PER_DOMAIN:
        raise ValueError(f"source pool shape mismatch: rows={len(rows)} per_domain={per_domain}")
    return binding, rows


def read_limited(response: Any) -> bytes:
    declared = response.headers.get("Content-Length")
    if declared:
        try:
            if int(declared) > MAX_PDF_BYTES:
                raise ValueError(f"PDF Content-Length exceeds {MAX_PDF_BYTES} bytes")
        except ValueError as exc:
            if "exceeds" in str(exc):
                raise
    data = response.read(MAX_PDF_BYTES + 1)
    if len(data) > MAX_PDF_BYTES:
        raise ValueError(f"PDF exceeds {MAX_PDF_BYTES} bytes")
    return data


def validate_final_url(url: str, exact_arxiv_id: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or (parsed.hostname or "").lower() not in PDF_HOSTS:
        raise ValueError(f"PDF redirect escaped allowed arXiv hosts: {url}")
    if not parsed.path.startswith("/pdf/"):
        raise ValueError(f"PDF final path is not /pdf/: {url}")
    tail = parsed.path.removeprefix("/pdf/").removesuffix(".pdf")
    if tail != exact_arxiv_id:
        raise ValueError(f"PDF final URL id {tail!r} != exact source id {exact_arxiv_id!r}")


class AccessLog:
    """Append-only JSONL log: one line per HTTP attempt + run markers."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.attempts = 0

    def _append(self, record: dict[str, Any]) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
            fh.flush()
            import os

            os.fsync(fh.fileno())

    def run_marker(self, event: str, extra: dict[str, Any] | None = None) -> None:
        rec: dict[str, Any] = {"ts_utc": utc_now(), "event": event}
        if extra:
            rec.update(extra)
        self._append(rec)

    def attempt(self, row: dict[str, Any], pool_index: int, attempt: int, url: str, started_utc: str, outcome: str, http_status: Any = None, final_url: str | None = None, pdf_bytes: int | None = None, pdf_sha256: str | None = None, error: str | None = None) -> None:
        self.attempts += 1
        rec: dict[str, Any] = {"ts_utc": utc_now(), "event": "http_attempt", "request_started_utc": started_utc, "pool_index": pool_index, "exact_arxiv_id": row["exact_arxiv_id"], "request_url": url, "attempt": attempt, "outcome": outcome}
        if http_status is not None:
            rec["http_status"] = http_status
        if final_url is not None:
            rec["final_url"] = final_url
        if pdf_bytes is not None:
            rec["pdf_bytes"] = pdf_bytes
        if pdf_sha256 is not None:
            rec["pdf_sha256"] = pdf_sha256
        if error is not None:
            rec["error"] = error[:500]
        self._append(rec)


class Receipts:
    """Append-only JSONL receipts; resume keeps the last byte-verified row per id."""

    def __init__(self, path: Path, bytes_dir: Path) -> None:
        self.path = path
        self.bytes_dir = bytes_dir
        self.by_index: dict[int, dict[str, Any]] = {}
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    rec = json.loads(line)
                    self.by_index[rec["pool_index"]] = rec

    def bound_indices(self) -> set[int]:
        ok: set[int] = set()
        for idx, rec in self.by_index.items():
            if rec.get("status") != "EXACT_VERSION_CC_BY_FULLTEXT_BOUND":
                continue
            f = self.bytes_dir / rec["bytes_relpath"]
            if not f.exists():
                continue
            if sha256_bytes(f.read_bytes()) != rec["pdf_sha256"]:
                continue
            ok.add(idx)
        return ok

    def append(self, rec: dict[str, Any]) -> None:
        self.by_index[rec["pool_index"]] = rec
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, sort_keys=True, ensure_ascii=False) + "\n")
            fh.flush()
            import os

            os.fsync(fh.fileno())


def fetch_pdf_attempt(row: dict[str, Any]) -> dict[str, Any]:
    url, exact = row["immutable_pdf_url"], row["exact_arxiv_id"]
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/pdf,*/*;q=0.1"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as response:
        status = getattr(response, "status", 200)
        if status != 200:
            raise RuntimeError(f"HTTP {status}")
        final_url = response.geturl()
        validate_final_url(final_url, exact)
        data = read_limited(response)
        if not data.startswith(b"%PDF-"):
            raise ValueError("response is not PDF bytes")
        return {"request_url": url, "final_url": final_url, "http_status": status, "content_type": response.headers.get("Content-Type"), "etag": response.headers.get("ETag"), "last_modified": response.headers.get("Last-Modified"), "pdf_bytes": len(data), "pdf_sha256": sha256_bytes(data), "pdf_signature_valid": True, "pdf_data": data}


def run_live(pool_path: Path, binding_path: Path, out_dir: Path, bytes_dir: Path, run_host: str, max_rows: int | None) -> dict[str, Any]:
    binding, rows = load_frozen_pool(pool_path, binding_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    bytes_dir.mkdir(parents=True, exist_ok=True)
    log = AccessLog(out_dir / "ACCESS_LOG_V2.jsonl")
    receipts = Receipts(out_dir / "BINDING_V2_RECEIPTS.jsonl", bytes_dir)
    already = receipts.bound_indices()
    script_sha = sha256_bytes(Path(__file__).read_bytes())
    run_started_utc = utc_now()
    log.run_marker("run_start", {"run_host": run_host, "script_sha256": script_sha, "source_pool_sha256": EXPECTED_POOL_SHA256, "source_pool_rows": EXPECTED_ROWS, "already_bound_n": len(already), "max_rows": max_rows})

    targets = [i for i in range(EXPECTED_ROWS) if i not in already]
    if max_rows is not None:
        targets = targets[:max_rows]
    cannot_check: list[dict[str, Any]] = []
    newly_bound = 0
    last_request_at = 0.0

    for index in targets:
        row = rows[index]
        base = {"pool_index": index, "domain_id": row["domain_id"], "arxiv_id": row["arxiv_id"], "exact_version": row["exact_version"], "exact_arxiv_id": row["exact_arxiv_id"], "abstract_sha256": row["abstract_sha256"], "content_license": row["content_license"], "content_license_url": row["content_license_url"], "attribution": row["attribution"]}
        last_error: str | None = None
        bound = False
        for attempt in range(1, RETRIES_PER_PDF + 1):
            delay = REQUEST_INTERVAL_SECONDS - (time.monotonic() - last_request_at)
            if delay > 0:
                time.sleep(delay)
            started_utc = utc_now()
            last_request_at = time.monotonic()
            try:
                got = fetch_pdf_attempt(row)
            except urllib.error.HTTPError as exc:
                last_error = f"HTTPError {exc.code}: {exc.reason}"
                log.attempt(row, index, attempt, row["immutable_pdf_url"], started_utc, "RETRYABLE_FAILURE" if attempt < RETRIES_PER_PDF else "FAILED", http_status=exc.code, error=last_error)
            except (urllib.error.URLError, TimeoutError, RuntimeError, ValueError, OSError) as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                log.attempt(row, index, attempt, row["immutable_pdf_url"], started_utc, "RETRYABLE_FAILURE" if attempt < RETRIES_PER_PDF else "FAILED", error=last_error)
            else:
                data = got.pop("pdf_data")
                relpath = f"pdf/{row['exact_arxiv_id']}.pdf"
                dest = bytes_dir / relpath
                dest.parent.mkdir(parents=True, exist_ok=True)
                tmp = dest.with_suffix(dest.suffix + ".part")
                tmp.write_bytes(data)
                tmp.replace(dest)
                rec = {**base, "status": "EXACT_VERSION_CC_BY_FULLTEXT_BOUND", "fetched_at_utc": utc_now(), "bound_run_host": run_host, "bytes_relpath": relpath, **got}
                receipts.append(rec)
                log.attempt(row, index, attempt, got["request_url"], started_utc, "BOUND", http_status=got["http_status"], final_url=got["final_url"], pdf_bytes=got["pdf_bytes"], pdf_sha256=got["pdf_sha256"])
                newly_bound += 1
                bound = True
                break
        if not bound:
            cannot_check.append({**base, "status": "CANNOT_CHECK_EXACT_VERSION_FULLTEXT_BINDING", "reason": last_error})

    run_finished_utc = utc_now()
    final_bound = receipts.bound_indices()
    bound_n = len(final_bound)
    # Cross-check against the durable preflight receipts (workflow run 33542940707).
    preflight_check = {"checked_n": len(EXPECTED_PREFLIGHT_BINDINGS), "matched_n": 0, "mismatches": []}
    for exact, expected_sha in EXPECTED_PREFLIGHT_BINDINGS.items():
        got = next((r for r in receipts.by_index.values() if r.get("exact_arxiv_id") == exact), None)
        if got is None:
            preflight_check["mismatches"].append({"exact_arxiv_id": exact, "issue": "not yet bound in this receipts file"})
        elif got.get("pdf_sha256") != expected_sha:
            preflight_check["mismatches"].append({"exact_arxiv_id": exact, "issue": "pdf_sha256 differs from durable preflight receipt", "preflight_pdf_sha256": expected_sha, "this_run_pdf_sha256": got.get("pdf_sha256")})
        else:
            preflight_check["matched_n"] += 1

    receipts_relpath = "BINDING_V2_RECEIPTS.jsonl"
    access_log_relpath = "ACCESS_LOG_V2.jsonl"
    receipts_sha = sha256_bytes((out_dir / receipts_relpath).read_bytes())
    access_log_sha = sha256_bytes((out_dir / access_log_relpath).read_bytes())
    # Per-domain tallies over ALL bound rows.
    per_domain: dict[str, int] = {k: 0 for k in EXPECTED_PER_DOMAIN}
    for idx in final_bound:
        per_domain[rows[idx]["domain_id"]] += 1

    result = {
        "schema": SCHEMA,
        "terminal": TERMINAL_COMPLETE if bound_n == EXPECTED_ROWS else TERMINAL_INCOMPLETE,
        "source_binding_id": binding["binding_id"],
        "source_pool_sha256": EXPECTED_POOL_SHA256,
        "source_pool_rows": EXPECTED_ROWS,
        "selection_rule": {"frozen_before_network_access": True, "description": "ALL rows of the frozen pool (extension of the 8-row live preflight to the full 1536-row candidate frame)", "indices_zero_based": "0..1535 inclusive", "sample_n": EXPECTED_ROWS, "data_dependent_selection": False},
        "network_policy": {"maximum_concurrency": 1, "minimum_request_interval_seconds": REQUEST_INTERVAL_SECONDS, "interval_enforced": "between every pair of request starts, including retries and across rows", "retries_per_pdf": RETRIES_PER_PDF, "timeout_seconds": TIMEOUT_SECONDS, "maximum_pdf_bytes": MAX_PDF_BYTES, "allowed_final_hosts": sorted(PDF_HOSTS), "allowed_schemes": ["https"]},
        "provenance": {"run_host": run_host, "run_started_utc": run_started_utc, "run_finished_utc": run_finished_utc, "script_sha256": script_sha, "pdf_bytes_stored": "outside repository at --bytes-dir; NOT committed", "receipts_relpath": receipts_relpath, "receipts_sha256": receipts_sha, "access_log_relpath": access_log_relpath, "access_log_sha256": access_log_sha, "access_log_attempts": log.attempts, "resumed_already_bound_n": len(already), "newly_bound_this_run": newly_bound, "durable_preflight_reference": {"workflow_run_id": 33542940707, "workflow_job_id": 99973407799, "artifact_id": 9814382058}},
        "bound_n": bound_n,
        "cannot_check_n": EXPECTED_ROWS - bound_n,
        "bound_per_domain": per_domain,
        "preflight_consistency_cross_check": preflight_check,
        "cannot_check_rows": cannot_check,
        "result_rows_sha256": canonical_json_sha([r for i, r in sorted(receipts.by_index.items())]),
        "full_pool_per_item_binding_complete": bound_n == EXPECTED_ROWS,
        "route_specific_pair_adjudication_performed": False,
        "case_eligibility_adjudicated": False,
        "protected_orion_predictions_accessed": False,
        "baseline_predictions_accessed": False,
        "external_gold_accessed": False,
        "grants_scientific_authority": False,
        "scientific_authority_delta": "NONE__EXACT_SOURCE_AND_RIGHTS_BINDING_ONLY",
    }
    log.run_marker("run_end", {"terminal": result["terminal"], "bound_n": bound_n, "newly_bound_this_run": newly_bound, "cannot_check_n": result["cannot_check_n"], "http_attempts": log.attempts})
    return result


def self_test(pool_path: Path, binding_path: Path) -> dict[str, Any]:
    binding, rows = load_frozen_pool(pool_path, binding_path)
    validate_final_url("https://arxiv.org/pdf/2501.01234v2.pdf", "2501.01234v2")
    try:
        validate_final_url("https://example.org/pdf/2501.01234v2", "2501.01234v2")
    except ValueError:
        pass
    else:
        raise AssertionError("off-provider redirect accepted")
    try:
        validate_final_url("https://arxiv.org/pdf/9999.9999v1", "2501.01234v2")
    except ValueError:
        pass
    else:
        raise AssertionError("id-mismatched final URL accepted")
    return {"decision": "GREEN", "network_accessed": False, "frozen_pool_sha256_verified": True, "source_binding_id": binding["binding_id"], "source_pool_rows": len(rows), "all_indices_in_scope": True, "off_provider_redirect_rejected": True, "id_mismatch_rejected": True}


def main() -> int:
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", type=Path, default=here.parent / "ARXIV_CC_BY_SOURCE_POOL_V1.jsonl")
    ap.add_argument("--binding", type=Path, default=here.parent / "ARXIV_CC_BY_SOURCE_POOL_BINDING_V1.json")
    ap.add_argument("--out-dir", type=Path, default=here)
    ap.add_argument("--bytes-dir", type=Path, required=False)
    ap.add_argument("--run-host", default="unknown")
    ap.add_argument("--max-rows", type=int, default=None, help="bind at most N additional rows this run (smoke tests)")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        result: dict[str, Any] = self_test(args.pool, args.binding)
        rc = 0
    else:
        if args.bytes_dir is None:
            ap.error("--bytes-dir is required for a live run")
        result = run_live(args.pool, args.binding, args.out_dir, args.bytes_dir, args.run_host, args.max_rows)
        rc = 0 if result["terminal"] == TERMINAL_COMPLETE else 2
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    out = args.out_dir / "BINDING_V2_RESULT.json"
    out.write_text(text, encoding="utf-8")
    print(text, end="")
    print(f"\nwrote {out}", file=__import__("sys").stderr)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
