#!/usr/bin/env python3
"""Structural and byte-fixity validation for the P4 arXiv source pool."""

from __future__ import annotations

import collections
import gzip
import hashlib
import json
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    here = Path(__file__).resolve().parent
    frame_path = here / "ARXIV_CC_BY_SOURCE_POOL_V1.jsonl"
    log_path = here / "ARXIV_CC_BY_POOL_HARVEST_LOG_V1.json"
    binding_path = here / "ARXIV_CC_BY_SOURCE_POOL_BINDING_V1.json"
    rows = [json.loads(line) for line in frame_path.read_text().splitlines()]
    log = json.loads(log_path.read_text())
    binding = json.loads(binding_path.read_text())
    domain_counts = dict(sorted(collections.Counter(r["domain_id"] for r in rows).items()))
    set_counts = dict(sorted(collections.Counter(r["acquisition_set"] for r in rows).items()))
    frame_sha = sha(frame_path)

    raw_checks = []
    for request in log["requests"]:
        path = here / request["retained_response_path"]
        compressed_sha = sha(path)
        uncompressed_sha = hashlib.sha256(gzip.decompress(path.read_bytes())).hexdigest()
        raw_checks.append(
            compressed_sha == request["retained_response_gzip_sha256"]
            and uncompressed_sha == request["response_sha256"]
        )

    checks = {
        "row_count_1536": len(rows) == 1536,
        "unique_arxiv_ids_1536": len({r["arxiv_id"] for r in rows}) == 1536,
        "domain_quota_384_each": set(domain_counts.values()) == {384} and len(domain_counts) == 4,
        "earth_subroute_quota_128_each": all(
            set_counts.get(name) == 128
            for name in [
                "physics:physics:ao-ph",
                "physics:physics:geo-ph",
                "physics:astro-ph:EP",
            ]
        ),
        "single_route_domain_quota_384_each": all(
            set_counts.get(name) == 384 for name in ["q-bio", "cs:cs:SE", "eess"]
        ),
        "all_content_license_cc_by_4": all(
            r["content_license_url"] == "https://creativecommons.org/licenses/by/4.0/"
            for r in rows
        ),
        "all_exact_version_urls": all(
            r["exact_version"].startswith("v")
            and r["immutable_abs_url"].endswith(r["exact_arxiv_id"])
            and r["immutable_pdf_url"].endswith(r["exact_arxiv_id"])
            for r in rows
        ),
        "all_abstract_hashes_match": all(
            hashlib.sha256(r["abstract"].encode("utf-8")).hexdigest() == r["abstract_sha256"]
            for r in rows
        ),
        "all_attribution_present": all(
            r["authors"] and r["title"] and r["exact_arxiv_id"] in r["attribution"]
            and "CC BY 4.0" in r["attribution"]
            for r in rows
        ),
        "frame_hash_matches_log": frame_sha == log["frame_sha256"],
        "frame_hash_matches_binding": frame_sha == binding["frame"]["sha256"],
        "log_hash_matches_binding": sha(log_path) == binding["harvest_log"]["sha256"],
        "all_retained_oai_page_hashes_match": all(raw_checks) and len(raw_checks) == len(log["requests"]),
        "outcomes_accessed_false": binding["outcomes_accessed"] is False,
        "scientific_authority_false": binding["grants_scientific_authority"] is False,
    }
    receipt = {
        "schema_version": "orion.p4.arxiv-source-pool-validation.v1",
        "frame_sha256": frame_sha,
        "rows": len(rows),
        "domain_counts": domain_counts,
        "acquisition_set_counts": set_counts,
        "retained_oai_pages": len(raw_checks),
        "checks": checks,
        "passed": all(checks.values()),
        "authority": "SOURCE_POOL_STRUCTURE_AND_BYTE_FIXITY_ONLY__NOT_CASE_ELIGIBILITY_OR_SCIENTIFIC_RESULT",
    }
    out = here / "ARXIV_CC_BY_SOURCE_POOL_VALIDATION_RECEIPT_V1.json"
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"path": str(out), "passed": receipt["passed"], "checks": len(checks)}))
    if not receipt["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
