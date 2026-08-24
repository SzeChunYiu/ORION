#!/usr/bin/env python3
"""Live four-domain spot-check of the frozen arXiv CC BY source pool."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import time
import urllib.request
from pathlib import Path


USER_AGENT = "ORION-P4-public-source-audit/1.0 (rights spot check)"


def request(url: str, method: str = "GET"):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method=method)
    return urllib.request.urlopen(req, timeout=120)


def main() -> None:
    here = Path(__file__).resolve().parent
    rows = [json.loads(line) for line in (here / "ARXIV_CC_BY_SOURCE_POOL_V1.jsonl").read_text().splitlines()]
    samples = []
    seen = set()
    for row in rows:
        if row["domain_id"] in seen:
            continue
        seen.add(row["domain_id"])
        with request(row["immutable_abs_url"]) as response:
            html = response.read()
            abs_status = response.status
            abs_final_url = response.geturl()
        license_observed = (
            b"http://creativecommons.org/licenses/by/4.0/" in html
            or b"https://creativecommons.org/licenses/by/4.0/" in html
        )
        time.sleep(3.1)
        with request(row["immutable_pdf_url"], method="HEAD") as response:
            pdf_status = response.status
            pdf_final_url = response.geturl()
            pdf_headers = {key.lower(): value for key, value in response.headers.items()}
        samples.append(
            {
                "domain_id": row["domain_id"],
                "exact_arxiv_id": row["exact_arxiv_id"],
                "abs_url": row["immutable_abs_url"],
                "abs_final_url": abs_final_url,
                "abs_http_status": abs_status,
                "abs_html_sha256": hashlib.sha256(html).hexdigest(),
                "cc_by_4_link_observed_on_exact_abs_page": license_observed,
                "pdf_url": row["immutable_pdf_url"],
                "pdf_final_url": pdf_final_url,
                "pdf_http_status": pdf_status,
                "pdf_content_type": pdf_headers.get("content-type"),
                "pdf_etag": pdf_headers.get("etag"),
                "pdf_last_modified": pdf_headers.get("last-modified"),
            }
        )
        time.sleep(3.1)
        if len(samples) == 4:
            break
    receipt = {
        "schema_version": "orion.p4.arxiv-rights-live-sample.v1",
        "checked_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "frame_sha256": hashlib.sha256((here / "ARXIV_CC_BY_SOURCE_POOL_V1.jsonl").read_bytes()).hexdigest(),
        "selection": "first retained row in each frozen domain; diagnostic only",
        "sample_count": len(samples),
        "all_exact_abs_pages_show_cc_by_4": all(s["cc_by_4_link_observed_on_exact_abs_page"] for s in samples),
        "all_exact_pdf_urls_return_pdf": all(s["pdf_http_status"] == 200 and s["pdf_content_type"] == "application/pdf" for s in samples),
        "samples": samples,
        "authority": "LIVE_RIGHTS_AND_AVAILABILITY_SPOT_CHECK_ONLY__NOT_CASE_ELIGIBILITY",
    }
    out = here / "ARXIV_CC_BY_LIVE_SAMPLE_RECEIPT_V1.json"
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"path": str(out), "sample_count": len(samples), "license_ok": receipt["all_exact_abs_pages_show_cc_by_4"], "pdf_ok": receipt["all_exact_pdf_urls_return_pdf"]}))


if __name__ == "__main__":
    main()
