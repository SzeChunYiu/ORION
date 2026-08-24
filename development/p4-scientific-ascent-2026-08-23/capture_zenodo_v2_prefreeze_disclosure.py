#!/usr/bin/env python3
"""Capture the outcome-free Zenodo probes that precede the V2 census freeze."""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v1-protocol", required=True, type=Path)
    parser.add_argument("--cache", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()

    if args.receipt.exists():
        raise RuntimeError(
            f"refusing to overwrite disclosure bound by V2: {args.receipt}; "
            "open a new successor identity instead"
        )

    protocol = json.loads(args.v1_protocol.read_text(encoding="utf-8"))
    args.cache.mkdir(parents=True, exist_ok=True)
    queries = []
    all_ids: set[str] = set(protocol["preflight_exclusions"]["record_ids"])
    for number, query in enumerate(protocol["queries"], start=1):
        params = urllib.parse.urlencode(
            {"q": query["q"], "size": 25, "sort": protocol["provider"]["sort"]}
        )
        url = f"{protocol['provider']['endpoint']}?{params}"
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "ORION-P4-public-metadata-census/2.0-prefreeze (metadata only)"},
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read()
            status = response.status
        raw_path = args.cache / f"{number:02d}_{query['query_id']}.json"
        raw_path.write_bytes(raw)
        payload = json.loads(raw)
        hits = payload.get("hits", {}).get("hits", [])
        ids = sorted({str(hit.get("id", "")) for hit in hits if hit.get("id")})
        all_ids.update(ids)
        queries.append(
            {
                "query_id": query["query_id"],
                "http_status": status,
                "request_url_sha256": sha256_bytes(url.encode("utf-8")),
                "reported_total_hits": payload.get("hits", {}).get("total"),
                "returned_record_count": len(hits),
                "returned_record_ids": ids,
                "raw_response_file_outside_git": str(raw_path),
                "raw_response_bytes": len(raw),
                "raw_response_sha256": sha256_bytes(raw),
            }
        )
    receipt = {
        "schema_version": "orion.p4.zenodo-v2-prefreeze-probe-disclosure.v1",
        "date": "2026-08-23",
        "authority": "OUTCOME_FREE_TRANSPORT_AND_SCHEMA_PROBES_ONLY",
        "v1_protocol_sha256": sha256_file(args.v1_protocol),
        "probe_page_size": 25,
        "query_count": len(queries),
        "queries": queries,
        "all_disclosed_record_ids": sorted(all_ids),
        "all_disclosed_record_count": len(all_ids),
        "files_downloaded": False,
        "case_outcomes_accessed": False,
        "model_outcomes_executed": False,
        "use_in_v2": "EXCLUDE_ALL_DISCLOSED_RECORD_IDS_FROM_V2_CANDIDATE_COUNTS",
        "terminal": "P4_ZENODO_V2_PREFREEZE_PROBES_DISCLOSED__V2_NOT_YET_FROZEN",
    }
    args.receipt.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
