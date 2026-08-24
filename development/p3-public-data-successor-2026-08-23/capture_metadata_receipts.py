#!/usr/bin/env python3
"""Capture official metadata/HEAD receipts without opening dataset bodies."""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


USER_AGENT = "ORION-P3-public-metadata/1.0"


def request(url: str, method: str = "GET") -> tuple[bytes, dict[str, Any]]:
    req = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as response:
        body = response.read() if method == "GET" else b""
        receipt = {
            "url": url,
            "method": method,
            "http_status": response.status,
            "content_type": response.headers.get("Content-Type"),
            "content_length_header": response.headers.get("Content-Length"),
            "etag": response.headers.get("ETag"),
            "last_modified": response.headers.get("Last-Modified"),
            "body_bytes_accessed": len(body),
            "body_sha256": hashlib.sha256(body).hexdigest() if body else None,
        }
        return body, receipt


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: capture_metadata_receipts.py OUTPUT.json")
    receipts: list[dict[str, Any]] = []
    extracted: dict[str, Any] = {}

    for source_id, url in [
        ("CRAFT_SHARED_TASK_2019_ZENODO_3460908", "https://zenodo.org/api/records/3460908"),
        ("OAEI_2004_ZENODO_15827226", "https://zenodo.org/api/records/15827226"),
    ]:
        body, receipt = request(url)
        receipt["source_id"] = source_id
        receipts.append(receipt)
        payload = json.loads(body)
        extracted[source_id] = {
            "record_id": str(payload["id"]),
            "doi": payload["metadata"].get("doi"),
            "title": payload["metadata"].get("title"),
            "license": payload["metadata"].get("license"),
            "publication_date": payload["metadata"].get("publication_date"),
            "creators": payload["metadata"].get("creators"),
            "files": [{"key": f["key"], "size": f["size"], "checksum": f["checksum"]} for f in payload.get("files", [])],
        }

    commit_url = "https://api.github.com/repos/allenai/SciREX/commits/7daad660fe94f504433590b7a781cfabe1e179c6"
    body, receipt = request(commit_url)
    receipt["source_id"] = "SCIREX_GITHUB_7DAAD660"
    receipts.append(receipt)
    commit = json.loads(body)
    extracted["SCIREX_GITHUB_7DAAD660"] = {
        "commit_sha": commit.get("sha"),
        "commit_date_utc": commit.get("commit", {}).get("committer", {}).get("date"),
        "tree_sha": commit.get("commit", {}).get("tree", {}).get("sha"),
    }

    for role, url in [
        ("README", "https://raw.githubusercontent.com/allenai/SciREX/7daad660fe94f504433590b7a781cfabe1e179c6/README.md"),
        ("LICENSE", "https://raw.githubusercontent.com/allenai/SciREX/7daad660fe94f504433590b7a781cfabe1e179c6/LICENSE"),
    ]:
        body, receipt = request(url)
        receipt.update({"source_id": "SCIREX_GITHUB_7DAAD660", "role": role})
        receipts.append(receipt)
        extracted["SCIREX_GITHUB_7DAAD660"][f"{role.lower()}_sha256"] = hashlib.sha256(body).hexdigest()

    release_url = "https://raw.githubusercontent.com/allenai/SciREX/7daad660fe94f504433590b7a781cfabe1e179c6/scirex_dataset/release_data.tar.gz"
    _, receipt = request(release_url, method="HEAD")
    receipt.update({"source_id": "SCIREX_GITHUB_7DAAD660", "role": "DATA_RELEASE_HEAD", "dataset_body_accessed": False})
    receipts.append(receipt)
    extracted["SCIREX_GITHUB_7DAAD660"]["release_head"] = {
        "content_length_header": receipt["content_length_header"],
        "etag": receipt["etag"],
        "dataset_body_accessed": False,
    }

    output = {
        "schema_version": "orion.p3.public-metadata-receipts.v1",
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "authority": "OFFICIAL_PROVIDER_METADATA_AND_PINNED_TEXT_ONLY__NO_DATASET_BODY_OR_OUTCOME_ACCESS",
        "dataset_bodies_accessed": 0,
        "gold_objects_accessed": 0,
        "extracted": extracted,
        "http_receipts": receipts,
    }
    path = Path(sys.argv[1])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
