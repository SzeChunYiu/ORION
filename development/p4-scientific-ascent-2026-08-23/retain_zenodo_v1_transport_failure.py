#!/usr/bin/env python3
"""Reproduce and retain the frozen V1 Zenodo transport failure."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", required=True, type=Path)
    parser.add_argument("--cache", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()

    if args.receipt.exists():
        raise RuntimeError(
            f"refusing to overwrite retained V1 identity: {args.receipt}; "
            "use a new successor identity for any new observation"
        )

    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    query = protocol["queries"][0]
    params = urllib.parse.urlencode(
        {
            "q": query["q"],
            "size": protocol["provider"]["page_size"],
            "sort": protocol["provider"]["sort"],
        }
    )
    url = f"{protocol['provider']['endpoint']}?{params}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "ORION-P4-public-metadata-census/1.0 (research; no file downloads)"},
    )
    args.cache.mkdir(parents=True, exist_ok=True)
    raw_path = args.cache / "V1_HTTP_RESPONSE.json"
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read()
            status = response.status
    except urllib.error.HTTPError as error:
        body = error.read()
        status = error.code
    raw_path.write_bytes(body)

    try:
        provider_payload = json.loads(body)
    except json.JSONDecodeError:
        provider_payload = None
    retained = {
        "schema_version": "orion.p4.zenodo-related-object-census-retained-transport-failure.v1",
        "date": "2026-08-23",
        "reproduction_observed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "identity": "P4_ZENODO_RELATED_OBJECT_CENSUS_V1",
        "protocol_sha256": sha256_file(args.protocol),
        "query_id": query["query_id"],
        "requested_page_size": protocol["provider"]["page_size"],
        "request_url_sha256": sha256_bytes(url.encode("utf-8")),
        "http_status": status,
        "raw_response_file_outside_git": str(raw_path),
        "raw_response_bytes": len(body),
        "raw_response_sha256": sha256_bytes(body),
        "provider_payload": provider_payload,
        "model_outcome_executed": False,
        "repair_policy": "V1_RETAINED_UNCHANGED__ANY_PAGE_SIZE_OR_PAGINATION_REPAIR_REQUIRES_DISTINCT_V2_IDENTITY",
        "terminal": "P4_ZENODO_RELATED_OBJECT_CENSUS_V1_TRANSPORT_CANNOT_CHECK_HTTP_400",
    }
    args.receipt.write_text(json.dumps(retained, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0 if status == 400 else 1


if __name__ == "__main__":
    raise SystemExit(main())
