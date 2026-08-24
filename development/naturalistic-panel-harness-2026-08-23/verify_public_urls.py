#!/usr/bin/env python3
"""Verify public identity/revision URLs and pinned licence bytes only."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import urllib.request


ROOT = pathlib.Path(__file__).resolve().parent
SNAPSHOT = ROOT / "SOURCE_METADATA_SNAPSHOT_V1.json"
OUT = ROOT / "URL_VERIFICATION_V1.json"


def request(url: str, *, method: str = "HEAD") -> tuple[int, str, bytes, dict]:
    req = urllib.request.Request(
        url,
        method=method,
        headers={"User-Agent": "orion-outcome-blind-url-audit"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        body = response.read()
        return response.status, response.geturl(), body, {
            "etag": response.headers.get("ETag"),
            "last_modified": response.headers.get("Last-Modified"),
            "content_type": response.headers.get("Content-Type"),
        }


def main() -> int:
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    checks: list[dict] = []
    failures: list[str] = []
    for record in snapshot["records"]:
        repository = record["official_repository_identity"]
        primary_status, primary_final, _, primary_headers = request(
            record["primary_source_url"]
        )
        revision_status, revision_final, _, revision_headers = request(
            record["selected_revision_url"]
        )
        licence_status, licence_final, licence_bytes, licence_headers = request(
            record["licence"]["download_url_at_selected_revision"], method="GET"
        )
        licence_sha = hashlib.sha256(licence_bytes).hexdigest()
        expected_sha = record["licence"]["text_sha256"]
        passed = (
            primary_status == 200
            and revision_status == 200
            and licence_status == 200
            and licence_sha == expected_sha
        )
        if not passed:
            failures.append(repository)
        checks.append(
            {
                "official_repository_identity": repository,
                "primary_source": {
                    "requested_url": record["primary_source_url"],
                    "final_url": primary_final,
                    "http_status": primary_status,
                    **primary_headers,
                },
                "selected_revision": {
                    "sha": record["selected_revision_sha"],
                    "requested_url": record["selected_revision_url"],
                    "final_url": revision_final,
                    "http_status": revision_status,
                    **revision_headers,
                },
                "licence_at_selected_revision": {
                    "requested_url": record["licence"]["download_url_at_selected_revision"],
                    "final_url": licence_final,
                    "http_status": licence_status,
                    "download_sha256": licence_sha,
                    "matches_archived_sha256": licence_sha == expected_sha,
                    **licence_headers,
                },
                "passed": passed,
            }
        )
    result = {
        "schema_version": "orion.shared-naturalistic-source-url-verification.v1",
        "verified_at_utc": dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat(),
        "authority": "PUBLIC_URL_AND_LICENCE_FIXITY_ONLY__NO_CASE_OR_OUTCOME_AUTHORITY",
        "snapshot_payload_sha256": snapshot["snapshot_payload_sha256"],
        "records_checked": len(checks),
        "records_passed": sum(check["passed"] for check in checks),
        "failures": failures,
        "checks": checks,
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(OUT),
                "records_checked": result["records_checked"],
                "records_passed": result["records_passed"],
                "failures": failures,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
