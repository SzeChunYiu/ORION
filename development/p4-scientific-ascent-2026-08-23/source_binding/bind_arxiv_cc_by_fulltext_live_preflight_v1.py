#!/usr/bin/env python3
"""Outcome-blind live full-text binding preflight for the frozen A5 arXiv CC-BY pool."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
POOL = HERE / "ARXIV_CC_BY_SOURCE_POOL_V1.jsonl"
BINDING = HERE / "ARXIV_CC_BY_SOURCE_POOL_BINDING_V1.json"
EXPECTED_POOL_SHA256 = "47dd24657752731cdf45bab95852f3e18b50946af8a29b5acee95956ec81d895"
EXPECTED_ROWS = 1536
EXPECTED_PER_DOMAIN = {"EARTH_ENVIRONMENT": 384, "LIFE_BIOMEDICAL": 384, "PHYSICAL_ENGINEERING": 384, "SCIENTIFIC_SOFTWARE": 384}
FROZEN_SAMPLE_INDICES = [0, 383, 384, 767, 768, 1151, 1152, 1535]
REQUEST_INTERVAL_SECONDS = 3.1
MAX_PDF_BYTES = 64 * 1024 * 1024
USER_AGENT = "ORION-P4-A5-fulltext-preflight-v1/1.0 (research source binding; https://github.com/SzeChunYiu/ORION)"
PDF_HOSTS = {"arxiv.org", "export.arxiv.org"}
VERSION_RE = re.compile(r"v[1-9][0-9]*\Z")


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


def load_frozen_pool() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    binding = json.loads(BINDING.read_text(encoding="utf-8"))
    frame = binding.get("frame", {})
    if binding.get("binding_id") != "P4.NAT.AXIS.768.ARXIV_CC_BY_POOL_1536.V1":
        raise ValueError("source binding id mismatch")
    if frame.get("path") != POOL.name or frame.get("sha256") != EXPECTED_POOL_SHA256 or frame.get("rows") != EXPECTED_ROWS:
        raise ValueError("source binding frame mismatch")
    if binding.get("outcomes_accessed") is not False or binding.get("grants_scientific_authority") is not False:
        raise ValueError("source binding authority boundary mismatch")
    raw = POOL.read_bytes()
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
    sampled_domains = [rows[i]["domain_id"] for i in FROZEN_SAMPLE_INDICES]
    expected_domains = ["EARTH_ENVIRONMENT", "EARTH_ENVIRONMENT", "LIFE_BIOMEDICAL", "LIFE_BIOMEDICAL", "PHYSICAL_ENGINEERING", "PHYSICAL_ENGINEERING", "SCIENTIFIC_SOFTWARE", "SCIENTIFIC_SOFTWARE"]
    if sampled_domains != expected_domains:
        raise ValueError(f"frozen sample no longer maps two-per-domain: {sampled_domains}")
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


def fetch_pdf(row: dict[str, Any], retries: int = 3, timeout: float = 120.0) -> dict[str, Any]:
    url, exact = row["immutable_pdf_url"], row["exact_arxiv_id"]
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/pdf,*/*;q=0.1"})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                status = getattr(response, "status", 200)
                if status != 200:
                    raise RuntimeError(f"HTTP {status}")
                final_url = response.geturl()
                validate_final_url(final_url, exact)
                data = read_limited(response)
                if not data.startswith(b"%PDF-"):
                    raise ValueError("response is not PDF bytes")
                return {"request_url": url, "final_url": final_url, "http_status": status, "content_type": response.headers.get("Content-Type"), "etag": response.headers.get("ETag"), "last_modified": response.headers.get("Last-Modified"), "pdf_bytes": len(data), "pdf_sha256": sha256_bytes(data), "pdf_signature_valid": True}
        except (urllib.error.URLError, TimeoutError, RuntimeError, ValueError, OSError) as exc:
            last = exc
            if attempt + 1 < retries:
                time.sleep(REQUEST_INTERVAL_SECONDS)
    raise RuntimeError(f"failed exact-version PDF fetch after {retries} attempts: {last}")


def run_live() -> dict[str, Any]:
    binding, rows = load_frozen_pool()
    results: list[dict[str, Any]] = []
    last_request_at = 0.0
    for index in FROZEN_SAMPLE_INDICES:
        row = rows[index]
        delay = REQUEST_INTERVAL_SECONDS - (time.monotonic() - last_request_at)
        if delay > 0:
            time.sleep(delay)
        base = {"pool_index": index, "domain_id": row["domain_id"], "arxiv_id": row["arxiv_id"], "exact_version": row["exact_version"], "exact_arxiv_id": row["exact_arxiv_id"], "abstract_sha256": row["abstract_sha256"], "content_license": row["content_license"], "content_license_url": row["content_license_url"], "attribution": row["attribution"]}
        try:
            results.append({**base, "status": "EXACT_VERSION_CC_BY_FULLTEXT_BOUND", "fulltext": fetch_pdf(row)})
        except Exception as exc:
            results.append({**base, "status": "CANNOT_CHECK_EXACT_VERSION_FULLTEXT_BINDING", "reason": str(exc)[:500]})
        last_request_at = time.monotonic()
    bound_n = sum(r["status"] == "EXACT_VERSION_CC_BY_FULLTEXT_BOUND" for r in results)
    cannot_n = len(results) - bound_n
    return {"schema": "ORION.A5.ArxivCCByFulltextLivePreflight.v1", "terminal": "ARXIV_CC_BY_EXACT_VERSION_FULLTEXT_LIVE_PREFLIGHT_PASS" if cannot_n == 0 else "CANNOT_CHECK_ARXIV_CC_BY_EXACT_VERSION_FULLTEXT_LIVE_PREFLIGHT", "source_binding_id": binding["binding_id"], "source_pool_sha256": EXPECTED_POOL_SHA256, "source_pool_rows": EXPECTED_ROWS, "selection_rule": {"frozen_before_network_access": True, "description": "first and last candidate in each frozen 384-row domain block", "indices_zero_based": FROZEN_SAMPLE_INDICES, "sample_n": len(FROZEN_SAMPLE_INDICES), "data_dependent_selection": False}, "network_policy": {"maximum_concurrency": 1, "minimum_request_interval_seconds": REQUEST_INTERVAL_SECONDS, "retries_per_pdf": 3, "timeout_seconds": 120, "maximum_pdf_bytes": MAX_PDF_BYTES, "allowed_final_hosts": sorted(PDF_HOSTS)}, "bound_n": bound_n, "cannot_check_n": cannot_n, "result_rows_sha256": canonical_json_sha(results), "results": results, "full_pool_per_item_binding_complete": False, "route_specific_pair_adjudication_performed": False, "case_eligibility_adjudicated": False, "protected_orion_predictions_accessed": False, "baseline_predictions_accessed": False, "external_gold_accessed": False, "scientific_authority_delta": "NONE__LIVE_SOURCE_BINDING_PREFLIGHT_ONLY"}


def self_test() -> dict[str, Any]:
    binding, rows = load_frozen_pool()
    validate_final_url("https://arxiv.org/pdf/2501.01234v2.pdf", "2501.01234v2")
    try:
        validate_final_url("https://example.org/pdf/2501.01234v2", "2501.01234v2")
    except ValueError:
        pass
    else:
        raise AssertionError("off-provider redirect accepted")
    return {"decision": "GREEN", "network_accessed": False, "frozen_pool_sha256_verified": True, "source_binding_id": binding["binding_id"], "source_pool_rows": len(rows), "sample_indices": FROZEN_SAMPLE_INDICES, "sample_domains": [rows[i]["domain_id"] for i in FROZEN_SAMPLE_INDICES], "off_provider_redirect_rejected": True}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    result = self_test() if args.self_test else run_live()
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 2 if (not args.self_test and result["terminal"].startswith("CANNOT_CHECK")) else 0


if __name__ == "__main__":
    raise SystemExit(main())
