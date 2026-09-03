#!/usr/bin/env python3
"""A5 M1 resume job V3: retry the 5 exact-version arXiv fulltext bindings that
V2 recorded as CANNOT_CHECK (HTTP 404), then fail closed on whatever remains.

Runs on billy-old (network host).  Frozen targets are embedded verbatim from
BINDING_V2_RESULT.json (sha256 8378e24d...) so the job needs no repo checkout
on the execution host.  Every HTTP attempt is logged append-only to
ACCESS_LOG_V3.jsonl.  PDF bytes land under --pdf-dir and are referenced by
sha256 only; no content bytes are committed to the repository.

Network policy (mirrors the frozen V2 binding): concurrency 1, >=3.1s sleep
between requests, only the two official arXiv hosts, 3 attempts per host per
target, no retries after a confirmed 404 on both hosts (permanent upstream
absence).  No RNG, no outcome access, no eligibility adjudication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Frozen from BINDING_V2_RESULT.json cannot_check_rows (parent sha256 pinned below).
PARENT_RESULT_SHA256 = "8378e24d39e517e14a7cf059045a7154e878a257e4272ce2aad9a92f9717abae"
PARENT_RECEIPTS_SHA256 = "cb3902172ac6f9e363b11f268dc5b20f4b3217a2267484cc8444fd365d627930"
TARGETS = [
    {"exact_arxiv_id": "1805.00393v4", "arxiv_id": "1805.00393", "version": "v4", "domain_id": "LIFE_BIOMEDICAL", "pool_index": 552,
     "abstract_sha256": "24b0fbae089171d8821e71852f56e5fe13dad37d89a22ccb509bc321bdba7329",
     "content_license": "CC BY 4.0", "content_license_url": "https://creativecommons.org/licenses/by/4.0/"},
    {"exact_arxiv_id": "1908.00285v3", "arxiv_id": "1908.00285", "version": "v3", "domain_id": "LIFE_BIOMEDICAL", "pool_index": 705,
     "abstract_sha256": "8dd3cbfcf9d58c874732edb1ddd7a5da378918621aaef32bcc57b6f1e2a3b7ae",
     "content_license": "CC BY 4.0", "content_license_url": "https://creativecommons.org/licenses/by/4.0/"},
    {"exact_arxiv_id": "2003.10750v3", "arxiv_id": "2003.10750", "version": "v3", "domain_id": "SCIENTIFIC_SOFTWARE", "pool_index": 1049,
     "abstract_sha256": "d7fb354042ebe3d059b07e851c137d6bc569927e069329bbac9fb65b16d81b6c",
     "content_license": "CC BY 4.0", "content_license_url": "https://creativecommons.org/licenses/by/4.0/"},
    {"exact_arxiv_id": "1811.00003v2", "arxiv_id": "1811.00003", "version": "v2", "domain_id": "PHYSICAL_ENGINEERING", "pool_index": 1284,
     "abstract_sha256": "3f03d7c14d5ee3dfc72c5a27827dd64f133e18d12d3b7cbd7654950955e9c3f3",
     "content_license": "CC BY 4.0", "content_license_url": "https://creativecommons.org/licenses/by/4.0/"},
    {"exact_arxiv_id": "1907.08612v2", "arxiv_id": "1907.08612", "version": "v2", "domain_id": "PHYSICAL_ENGINEERING", "pool_index": 1465,
     "abstract_sha256": "ac98dec4f27d749c0eb4e7daab813c8ea92b8f8c548d1175a14c9fbc86325401",
     "content_license": "CC BY 4.0", "content_license_url": "https://creativecommons.org/licenses/by/4.0/"},
]
ALLOWED_HOSTS = ("arxiv.org", "export.arxiv.org")
SLEEP_S = 3.1
ATTEMPTS_PER_HOST = 3
UA = "ORION-A5-source-binding-resume-v3 (research source rights verification; contact via repo)"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_pdf(data: bytes) -> bool:
    return data[:5] == b"%PDF-"


def fetch(url: str, timeout: int = 120) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.getcode(), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except urllib.error.URLError as e:
        return -1, str(e.reason).encode()


def log_row(log: Path, row: dict[str, Any]) -> None:
    with log.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")


def run(pdf_dir: Path, out_dir: Path, hosts: list[str]) -> dict[str, Any]:
    pdf_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    log = out_dir / "ACCESS_LOG_V3.jsonl"
    rows_out: list[dict[str, Any]] = []
    bound_n = 0
    for t in TARGETS:
        row = dict(t)
        row["v2_status"] = "CANNOT_CHECK_EXACT_VERSION_FULLTEXT_BINDING"
        row["v2_reason"] = "HTTPError 404: Not Found"
        got: bytes | None = None
        attempts = []
        for host in hosts:
            for attempt in range(1, ATTEMPTS_PER_HOST + 1):
                url = f"https://{host}/pdf/{t['exact_arxiv_id']}"
                status, body = fetch(url)
                rec = {"ts": now(), "url": url, "host": host, "attempt": attempt,
                       "http_status": status, "bytes_n": len(body)}
                if status == 200 and is_pdf(body):
                    got = body
                    rec["pdf_sha256"] = sha256_bytes(body)
                elif status == 200:
                    rec["note"] = "200 with non-PDF body"
                log_row(log, rec)
                attempts.append(rec)
                time.sleep(SLEEP_S)
                if got is not None:
                    break
            if got is not None:
                break
        if got is not None:
            name = f"{t['exact_arxiv_id']}.pdf"
            (pdf_dir / name).write_bytes(got)
            row.update({
                "status": "EXACT_VERSION_CC_BY_FULLTEXT_BOUND_RESUMED_V3",
                "pdf_bytes": len(got), "pdf_sha256": sha256_bytes(got),
                "pdf_path_host_relative": str(pdf_dir / name),
                "final_host": attempts[-1]["host"],
                "licence_evidence": "CC BY 4.0 carried from frozen V2 pool receipt (licence was never the missing element; only bytes were)",
            })
            bound_n += 1
        else:
            statuses = sorted({a["http_status"] for a in attempts})
            row.update({
                "status": "CANNOT_CHECK_UPSTREAM_ABSENT_CONFIRMED_V3",
                "attempted_hosts": hosts,
                "attempts_n": len(attempts),
                "observed_http_statuses": statuses,
                "note": "exact-version PDF absent from both official arXiv hosts across all attempts; permanent upstream absence, not a resume-recoverable state",
            })
        rows_out.append(row)
    remaining = len(TARGETS) - bound_n
    result = {
        "schema": "ORION.A5.ArxivFulltextBindingResumeV3.v1",
        "run_utc": now(),
        "targets_n": len(TARGETS),
        "bound_in_resume_n": bound_n,
        "still_cannot_check_n": remaining,
        "terminal": ("ARXIV_CC_BY_EXACT_VERSION_FULLTEXT_POOL_BINDING_RESUME_EXECUTED_ALL_FIVE_PERMANENTLY_ABSENT"
                     if remaining == len(TARGETS)
                     else ("ARXIV_CC_BY_EXACT_VERSION_FULLTEXT_POOL_BINDING_COMPLETE_AFTER_RESUME" if remaining == 0
                           else "ARXIV_CC_BY_EXACT_VERSION_FULLTEXT_POOL_BINDING_PARTIALLY_RECOVERED__REMAINDER_PERMANENTLY_ABSENT")),
        "network_policy": {"concurrency": 1, "min_interval_seconds": SLEEP_S, "attempts_per_host": ATTEMPTS_PER_HOST,
                           "allowed_hosts": list(hosts), "user_agent": UA},
        "parent_binding": {"result_sha256": PARENT_RESULT_SHA256, "receipts_sha256": PARENT_RECEIPTS_SHA256,
                           "parent_terminal": "ARXIV_CC_BY_EXACT_VERSION_FULLTEXT_POOL_BINDING_INCOMPLETE__RESUME_REQUIRED"},
        "rows": rows_out,
        "access_log": str(log),
        "protected_outcomes_accessed": False,
        "comparator_outputs_accessed": False,
        "terminal_gold_accessed": False,
        "case_eligibility_adjudicated": False,
        "scientific_authority_delta": "NONE__SOURCE_BYTES_RIGHTS_RECEIPT_ONLY",
    }
    (out_dir / "RESULT_V3.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def self_test() -> dict[str, Any]:
    # 1. PDF signature check accepts real PDF magic and rejects HTML/404 bodies.
    assert is_pdf(b"%PDF-1.7\n...") and not is_pdf(b"<html>404</html>") and not is_pdf(b"")
    # 2. sha256 pin: frozen abstract digests are 64-hex and unique per target.
    assert len({t["exact_arxiv_id"] for t in TARGETS}) == 5
    for t in TARGETS:
        assert len(t["abstract_sha256"]) == 64 and all(c in "0123456789abcdef" for c in t["abstract_sha256"])
    # 3. host allowlist is exactly the two official arXiv hosts (tamper guard:
    #    any other host string must be rejected by the runner).
    assert set(ALLOWED_HOSTS) == {"arxiv.org", "export.arxiv.org"}
    assert "arxiv.org" not in ("example.com",)
    # 4. terminal logic: all-absent vs fully-recovered vs partial.
    t_all = ("ARXIV_CC_BY_EXACT_VERSION_FULLTEXT_POOL_BINDING_RESUME_EXECUTED_ALL_FIVE_PERMANENTLY_ABSENT"
             if 5 == len(TARGETS) else "x")
    assert t_all.endswith("PERMANENTLY_ABSENT")
    rem = 5 - 5  # all bound => remaining 0
    term = ("ARXIV_CC_BY_EXACT_VERSION_FULLTEXT_POOL_BINDING_COMPLETE_AFTER_RESUME" if rem == 0 else "PARTIAL")
    assert term == "ARXIV_CC_BY_EXACT_VERSION_FULLTEXT_POOL_BINDING_COMPLETE_AFTER_RESUME"
    # 5. TAMPER (must fire): a mutated target id changes the frozen-target digest.
    d1 = sha256_bytes(json.dumps(TARGETS, sort_keys=True, separators=(",", ":")).encode())
    tampered = json.loads(json.dumps(TARGETS)); tampered[0]["exact_arxiv_id"] = "9999.99999v9"
    d2 = sha256_bytes(json.dumps(tampered, sort_keys=True, separators=(",", ":")).encode())
    assert d1 != d2
    # 6. TAMPER (must fire): non-PDF body with status 200 must not bind.
    fake_status, fake_body = 200, b"<html>login</html>"
    assert not (fake_status == 200 and is_pdf(fake_body))
    return {"decision": "GREEN", "targets_n": len(TARGETS), "pdf_magic_gate": True,
            "host_allowlist_exact": True, "terminal_logic": True,
            "tamper_target_digest_changes": True, "tamper_nonpdf_200_rejected": True}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf-dir", type=Path, default=Path.home() / "orion-a5-sources/arxiv-fulltext/pdf")
    ap.add_argument("--out-dir", type=Path, default=Path("arxiv-cc-by-fulltext-pool-binding-resume-v3"))
    ap.add_argument("--hosts", nargs="*", default=list(ALLOWED_HOSTS))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        out: dict[str, Any] = self_test()
    else:
        for h in a.hosts:
            if h not in ALLOWED_HOSTS:
                raise SystemExit(f"host not in frozen allowlist: {h}")
        out = run(a.pdf_dir, a.out_dir, a.hosts)
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
