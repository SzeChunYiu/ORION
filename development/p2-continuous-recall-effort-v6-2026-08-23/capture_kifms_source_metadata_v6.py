#!/usr/bin/env python3
"""Capture public, label-free source metadata for the P2 V6 KIFMS freeze.

This script deliberately does not download any CSV source body.  It records the
OSF node, its licence, the osfstorage file inventory and immutable version-one
metadata, plus the exact public code/documentation identities that describe the
14-review family and its schema.
"""

from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path


OSF_NODE = "vt3n4"
GITHUB_REPO = "asreview/paper-guidelines-KIFMS"
GITHUB_COMMIT = "e056573791bfbdd339fa5ffd628a6443fdf220fb"


def get_json(url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "orion-p2-v6-metadata/1"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def get_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "orion-p2-v6-metadata/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=True)

    node = get_json(f"https://api.osf.io/v2/nodes/{OSF_NODE}/")
    write_json(out / "osf-node-vt3n4.json", node)
    licence_url = node["data"]["relationships"]["license"]["links"]["related"]["href"]
    write_json(out / "osf-license-vt3n4.json", get_json(licence_url))

    inventory = get_json(
        f"https://api.osf.io/v2/nodes/{OSF_NODE}/files/osfstorage/?page%5Bsize%5D=100"
    )
    write_json(out / "osf-file-inventory-vt3n4.json", inventory)
    csv_files = [
        item
        for item in inventory["data"]
        if item["attributes"]["kind"] == "file"
        and item["attributes"]["name"].endswith(".csv")
    ]
    versions = {}
    for item in sorted(csv_files, key=lambda value: value["attributes"]["name"]):
        file_id = item["id"]
        metadata = get_json(f"https://api.osf.io/v2/files/{file_id}/")
        current_version = metadata["data"]["attributes"]["current_version"]
        version = get_json(
            f"https://api.osf.io/v2/files/{file_id}/versions/{current_version}/"
        )
        versions[item["attributes"]["name"]] = {
            "file_metadata": metadata,
            "version_metadata": version,
        }
    write_json(out / "osf-csv-version-metadata-vt3n4.json", versions)

    repo = get_json(f"https://api.github.com/repos/{GITHUB_REPO}")
    commit = get_json(f"https://api.github.com/repos/{GITHUB_REPO}/commits/{GITHUB_COMMIT}")
    write_json(out / "github-kifms-repository.json", repo)
    write_json(out / "github-kifms-commit-e056573.json", commit)
    raw_base = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_COMMIT}"
    (out / "github-kifms-LICENSE").write_bytes(get_bytes(f"{raw_base}/LICENSE"))
    (out / "github-kifms-README.md").write_bytes(get_bytes(f"{raw_base}/README.md"))
    (out / "osf-source-README.md").write_bytes(get_bytes("https://osf.io/download/68sjv/?revision=1"))

    print(f"captured {len(csv_files)} CSV identities without downloading CSV bodies")


if __name__ == "__main__":
    main()
