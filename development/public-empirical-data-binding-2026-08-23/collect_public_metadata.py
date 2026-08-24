#!/usr/bin/env python3
"""Collect public metadata only; never fetch dataset rows or outcome files."""

from __future__ import annotations

import hashlib
import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


OUT = Path(__file__).resolve().parent
USER_AGENT = "orion-public-empirical-data-binding-audit/1.0"


GITHUB_REPOS = [
    {
        "source_id": "SWE_BENCH_REPO",
        "repo": "SWE-bench/SWE-bench",
        "commit_sha": "7a21e05772954cc81471ae19d56f436cecf43c54",
        "tree_sha": "e667352e125abfd369a6129673d5289aa168e78b",
        "readme": "README.md",
        "license": "LICENSE",
    },
    {
        "source_id": "DEFECTS4J",
        "repo": "rjust/defects4j",
        "commit_sha": "8c16da8230843cdc918eaf4ddb449637f02b83c6",
        "tree_sha": "e2912f772b85037f8c3c1bdc2a27db6bfc70e661",
        "readme": "README.md",
        "license": "license.txt",
    },
    {
        "source_id": "BUGSINPY",
        "repo": "soarsmu/BugsInPy",
        "commit_sha": "11c5f1eea954a42132cfd06bf257766a7963e0fd",
        "tree_sha": "d00ce0495ba73abe50317599f48bced3c9afe4b3",
        "readme": "README.md",
        "license": "LICENSE",
    },
    {
        "source_id": "SYNERGY_REPO",
        "repo": "asreview/synergy-dataset",
        "commit_sha": "dc2dadfdbb98eb1b4259604789abd640aa3b693e",
        "tree_sha": "2173535d1bb1c918e127acd9145fd42d37ee82a2",
        "readme": "README.md",
        "license": "LICENSE",
    },
    {
        "source_id": "SCIFACT_REPO",
        "repo": "allenai/scifact",
        "commit_sha": "68b98a56d93e0f9da0d2aab4e6c3294699a0f72e",
        "tree_sha": "4bb595deb94c29d0964ee93cdcfeb062b4e09634",
        "readme": "README.md",
        "license": "LICENSE.md",
    },
    {
        "source_id": "SCIREX",
        "repo": "allenai/SciREX",
        "commit_sha": "7daad660fe94f504433590b7a781cfabe1e179c6",
        "tree_sha": "c9931b14f2a085fecb6fb5cd36980fdc89b56c6c",
        "readme": "README.md",
        "license": "LICENSE",
        "metadata_only_head_paths": ["scirex_dataset/release_data.tar.gz"],
    },
    {
        "source_id": "PEERREAD_REPO",
        "repo": "allenai/PeerRead",
        "commit_sha": "9bb37751781a900cee9e74ec3105997732c8e8e5",
        "tree_sha": None,
        "readme": "README.md",
        "license": "LICENSE",
    },
    {
        "source_id": "BUGSWARM",
        "repo": "BugSwarm/bugswarm",
        "commit_sha": "2b276ac5c475bcc71c9d62384943206c7768408f",
        "tree_sha": None,
        "readme": "README.md",
        "license": "LICENSE",
    },
    {
        "source_id": "ASREVIEW_COMPARATOR",
        "repo": "asreview/asreview",
        "commit_sha": "1788bc97ff5b5652dbe1e5b5ad5253bef1b03aef",
        "tree_sha": None,
        "readme": "README.md",
        "license": "LICENSE",
    },
    {
        "source_id": "SWE_AGENT_COMPARATOR",
        "repo": "SWE-agent/SWE-agent",
        "commit_sha": "3ea751c087f32b16e039a2233dd6eefecef325d5",
        "tree_sha": None,
        "readme": "README.md",
        "license": "LICENSE",
    },
    {
        "source_id": "OPENEA",
        "repo": "nju-websoft/OpenEA",
        "commit_sha": "b59e014153c27c7166d78475e3474c7e86a10be9",
        "tree_sha": None,
        "readme": "README.md",
        "license": "LICENSE",
    },
]


HF_DATASETS = [
    "SWE-bench/SWE-bench_Multilingual",
    "SWE-bench/SWE-bench_Verified",
    "allenai/scifact",
    "allenai/peer_read",
]


ZENODO_RECORDS = ["10423427", "3460908", "15827226"]


def request(url: str, method: str = "GET") -> tuple[dict[str, Any], bytes]:
    req = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            body = b"" if method == "HEAD" else response.read()
            receipt = {
                "url": url,
                "method": method,
                "http_status": response.status,
                "content_type": response.headers.get("Content-Type"),
                "content_length_header": response.headers.get("Content-Length"),
                "etag": response.headers.get("ETag"),
                "last_modified": response.headers.get("Last-Modified"),
                "response_byte_count": len(body),
                "response_sha256": hashlib.sha256(body).hexdigest() if body else None,
            }
            return receipt, body
    except urllib.error.HTTPError as error:
        body = error.read()
        return (
            {
                "url": url,
                "method": method,
                "http_status": error.code,
                "content_type": error.headers.get("Content-Type"),
                "content_length_header": error.headers.get("Content-Length"),
                "etag": error.headers.get("ETag"),
                "last_modified": error.headers.get("Last-Modified"),
                "response_byte_count": len(body),
                "response_sha256": hashlib.sha256(body).hexdigest() if body else None,
            },
            body,
        )


def json_body(body: bytes) -> Any:
    return json.loads(body.decode("utf-8"))


def collect_github(receipts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for spec in GITHUB_REPOS:
        base = f"https://raw.githubusercontent.com/{spec['repo']}/{spec['commit_sha']}"
        readme_url = f"{base}/{spec['readme']}"
        license_url = f"{base}/{spec['license']}"
        readme_receipt, readme = request(readme_url)
        license_receipt, license_bytes = request(license_url)
        receipts.extend([readme_receipt, license_receipt])
        record: dict[str, Any] = {
            "source_id": spec["source_id"],
            "provider": "GITHUB_RAW",
            "repository": spec["repo"],
            "canonical_url": f"https://github.com/{spec['repo']}",
            "commit_sha": spec["commit_sha"],
            "tree_sha": spec["tree_sha"],
            "archive_url": f"https://github.com/{spec['repo']}/archive/{spec['commit_sha']}.tar.gz",
            "readme": {
                "path": spec["readme"],
                "http_status": readme_receipt["http_status"],
                "byte_count": len(readme),
                "sha256": hashlib.sha256(readme).hexdigest() if readme else None,
            },
            "license_file": {
                "path": spec["license"],
                "http_status": license_receipt["http_status"],
                "byte_count": len(license_bytes),
                "sha256": hashlib.sha256(license_bytes).hexdigest() if license_bytes else None,
                "first_line": license_bytes.decode("utf-8", "replace").splitlines()[0]
                if license_bytes
                else None,
                "assertion_extracts": [
                    line.strip()
                    for line in license_bytes.decode("utf-8", "replace").splitlines()
                    if re.search(
                        r"(licensed under|released under|permission is hereby granted|creative commons|apache license|bsd|gnu general public license)",
                        line,
                        re.I,
                    )
                ][:12]
                if license_bytes
                else [],
            },
        }
        if readme:
            text = readme.decode("utf-8", "replace")
            record["readme_assertion_extracts"] = [
                line.strip()
                for line in text.splitlines()
                if re.search(
                    r"(dataset|benchmark|label|included|excluded|bug|coreference|relation|alignment|private|license)",
                    line,
                    re.I,
                )
            ][:12]
        heads = []
        for path in spec.get("metadata_only_head_paths", []):
            url = f"{base}/{path}"
            head_receipt, _ = request(url, method="HEAD")
            receipts.append(head_receipt)
            heads.append(
                {
                    "path": path,
                    "url": url,
                    "http_status": head_receipt["http_status"],
                    "content_length_header": head_receipt["content_length_header"],
                    "etag": head_receipt["etag"],
                    "body_accessed": False,
                }
            )
        if heads:
            record["metadata_only_file_heads"] = heads
        records.append(record)
    return records


def collect_huggingface(receipts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for dataset_id in HF_DATASETS:
        api_url = f"https://huggingface.co/api/datasets/{dataset_id}?blobs=true"
        api_receipt, body = request(api_url)
        receipts.append(api_receipt)
        payload = json_body(body)
        revision = payload["sha"]
        card_url = f"https://huggingface.co/datasets/{dataset_id}/raw/{revision}/README.md"
        card_receipt, card = request(card_url)
        receipts.append(card_receipt)
        siblings = []
        for sibling in payload.get("siblings", []):
            siblings.append(
                {
                    "path": sibling.get("rfilename"),
                    "size": sibling.get("size"),
                    "git_blob_id": sibling.get("blobId"),
                    "lfs": sibling.get("lfs"),
                }
            )
        records.append(
            {
                "source_id": dataset_id.replace("/", "__").upper(),
                "provider": "HUGGING_FACE_HUB",
                "dataset_id": dataset_id,
                "canonical_url": f"https://huggingface.co/datasets/{dataset_id}",
                "revision_sha": revision,
                "last_modified": payload.get("lastModified"),
                "private": payload.get("private"),
                "gated": payload.get("gated"),
                "license_card_field": (payload.get("cardData") or {}).get("license"),
                "license_tags": [tag for tag in payload.get("tags", []) if tag.startswith("license:")],
                "dataset_info": (payload.get("cardData") or {}).get("dataset_info"),
                "siblings": siblings,
                "card": {
                    "url": card_url,
                    "byte_count": len(card),
                    "sha256": hashlib.sha256(card).hexdigest(),
                },
                "rows_accessed": 0,
                "protected_outcome_bytes_accessed": False,
            }
        )
    return records


def collect_zenodo(receipts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for record_id in ZENODO_RECORDS:
        url = f"https://zenodo.org/api/records/{record_id}"
        receipt, body = request(url)
        receipts.append(receipt)
        payload = json_body(body)
        metadata = payload.get("metadata", {})
        files = [
            {
                "key": file.get("key"),
                "size": file.get("size"),
                "checksum": file.get("checksum"),
                "download_url": (file.get("links") or {}).get("self"),
            }
            for file in payload.get("files", [])
        ]
        records.append(
            {
                "source_id": f"ZENODO_{record_id}",
                "provider": "ZENODO",
                "record_id": record_id,
                "canonical_url": f"https://zenodo.org/records/{record_id}",
                "doi": metadata.get("doi"),
                "title": metadata.get("title"),
                "publication_date": metadata.get("publication_date"),
                "license": (metadata.get("license") or {}).get("id"),
                "keywords": metadata.get("keywords"),
                "files": files,
                "file_bodies_accessed": 0,
                "protected_outcome_bytes_accessed": False,
            }
        )
    return records


def collect_dataverse(receipts: list[dict[str, Any]]) -> dict[str, Any]:
    url = (
        "https://dataverse.nl/api/datasets/:persistentId/versions/1.0"
        "?persistentId=doi:10.34894/HE6NAQ"
    )
    receipt, body = request(url)
    receipts.append(receipt)
    payload = json_body(body)["data"]
    files = []
    for file in payload.get("files", []):
        data_file = file.get("dataFile", {})
        files.append(
            {
                "directory_label": file.get("directoryLabel"),
                "label": file.get("label"),
                "file_id": data_file.get("id"),
                "size": data_file.get("filesize"),
                "checksum": data_file.get("checksum"),
                "download_url": f"https://dataverse.nl/api/access/datafile/{data_file.get('id')}",
            }
        )
    return {
        "source_id": "SYNERGY_DATAVERSE_V1_0",
        "provider": "DATAVERSE_NL",
        "persistent_id": payload.get("datasetPersistentId"),
        "canonical_url": "https://doi.org/10.34894/HE6NAQ",
        "version": f"{payload.get('versionNumber')}.{payload.get('versionMinorNumber')}",
        "version_state": payload.get("versionState"),
        "release_time": payload.get("releaseTime"),
        "license": payload.get("license"),
        "file_count": len(files),
        "files": files,
        "file_bodies_accessed": 0,
        "protected_outcome_bytes_accessed": False,
    }


def main() -> None:
    receipts: list[dict[str, Any]] = []
    evidence = {
        "schema_version": "orion.public-empirical-data-binding.online-evidence.v1",
        "captured_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "authority": "PUBLIC_METADATA_AND_LICENCE_PREFLIGHT_ONLY__NOT_EMPIRICAL_EVIDENCE",
        "dataset_rows_accessed": 0,
        "protected_outcome_bytes_accessed": False,
        "github": collect_github(receipts),
        "hugging_face": collect_huggingface(receipts),
        "zenodo": collect_zenodo(receipts),
        "dataverse": collect_dataverse(receipts),
        "http_receipts": receipts,
    }
    (OUT / "ONLINE_EVIDENCE_RECEIPTS.json").write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    )


if __name__ == "__main__":
    main()
