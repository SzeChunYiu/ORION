#!/usr/bin/env python3
"""Correct the Zenodo content Accept header for the same bounded V8 pass."""

from __future__ import annotations

import json
import time
from pathlib import Path

import run_targeted_provider_pass_v8 as v8


HERE = Path(__file__).resolve().parent
RECEIPT = HERE / "PROVIDER_PROBE_RECEIPT_V8.json"


def main() -> None:
    started = v8.now()
    clock = time.monotonic()
    receipt = json.loads(RECEIPT.read_text())
    rows = {row["frozen_index"]: row for row in v8.load_rows()}
    retried = 0
    for probe in receipt["probes"]:
        prior = probe.get("provider_archive_request") or {}
        if prior.get("http_status") not in {406, None}:
            continue
        index = probe["frozen_index"]
        row = rows[index]
        url = None
        matches = probe.get("unique_provider_version_matches") or []
        if len(matches) == 1:
            files = matches[0].get("files") or []
            if len(files) == 1:
                links = files[0].get("links") or {}
                url = links.get("self") or links.get("content")
        if not url:
            metadata = v8.selected_archive_metadata(row) or {}
            files = metadata.get("files") or []
            if len(files) == 1:
                links = files[0].get("links") or {}
                url = files[0].get("content_url") or links.get("self") or links.get("content")
        if not url:
            continue
        body, request = v8.fetch(url, accept="*/*")
        probe["archive_transport_retry"] = request
        retried += 1
        if body is None:
            continue
        expected_commit = (row.get("accepted_exact_tag_commit") or {}).get("commit_sha")
        probe["archive_transport_retry_analysis"] = v8.analyze_archive(
            index,
            body,
            expected_commit=expected_commit,
            expected_tag=v8.version_field(row),
            commit_license=None,
        )
        provider_checksum = None
        if len(matches) == 1 and len(matches[0].get("files") or []) == 1:
            provider_checksum = matches[0]["files"][0].get("checksum")
        if not provider_checksum:
            metadata = v8.selected_archive_metadata(row) or {}
            files = metadata.get("files") or []
            if len(files) == 1:
                provider_checksum = files[0].get("checksum")
        probe["archive_transport_retry_provider_checksum"] = provider_checksum
        probe["archive_transport_retry_checksum_verified"] = (
            v8.md5(body) == provider_checksum.split(":", 1)[1].casefold()
            if isinstance(provider_checksum, str) and provider_checksum.startswith("md5:")
            else None
        )
    receipt["archive_transport_retry"] = {
        "reason": "ZENODO_CONTENT_ENDPOINT_REJECTED_APPLICATION_OCTET_STREAM_ACCEPT_WITH_HTTP_406",
        "corrected_accept": "*/*",
        "started_at": started,
        "finished_at": v8.now(),
        "runtime_seconds": round(time.monotonic() - clock, 6),
        "retried_exact_archive_count": retried,
        "scope_expanded": False,
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(
        "P4_V8_ARCHIVE_TRANSPORT_RETRY_COMPLETE__"
        f"{retried}_EXACT_ARCHIVES__RUNTIME_SECONDS={time.monotonic() - clock:.6f}"
    )


if __name__ == "__main__":
    main()
