#!/usr/bin/env python3
"""One targeted provider-native pass over the ten frozen P4 V7 identities."""

from __future__ import annotations

import base64
import datetime as dt
import hashlib
import io
import json
import os
import re
import subprocess
import tarfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
V7 = HERE.parent / "p4-unresolved-identity-v7-2026-08-23"
OUT = HERE / "PROVIDER_PROBE_RECEIPT_V8.json"
EVIDENCE = HERE / "evidence"
UA = "orion-p4-v8-frozen-ten-provider-pass/1.0"
MAX_ARCHIVE_BYTES = 120_000_000
MAX_MEMBER_BYTES = 2_000_000
MAX_SCAN_BYTES = 50_000_000

ACCEPTED = {
    "MIT", "BSD-2-Clause", "BSD-3-Clause", "Apache-2.0", "GPL-2.0-only",
    "GPL-2.0-or-later", "GPL-3.0-only", "GPL-3.0-or-later",
    "LGPL-2.1-only", "LGPL-2.1-or-later", "LGPL-3.0-only",
    "LGPL-3.0-or-later", "MPL-2.0", "ISC", "EPL-2.0",
    "AGPL-3.0-only", "AGPL-3.0-or-later", "Unlicense", "CC0-1.0",
}


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def md5(body: bytes) -> str:
    return hashlib.md5(body, usedforsecurity=False).hexdigest()


def token() -> str:
    for key in ("GITHUB_TOKEN", "GH_TOKEN"):
        if os.environ.get(key):
            return os.environ[key]
    try:
        return subprocess.check_output(
            ["gh", "auth", "token"], text=True, stderr=subprocess.DEVNULL, timeout=10
        ).strip()
    except Exception:
        return ""


TOKEN = token()


def fetch(url: str, *, github: bool = False, accept: str | None = None) -> tuple[bytes | None, dict[str, Any]]:
    started = now()
    headers = {"User-Agent": UA, "Accept": accept or ("application/vnd.github+json" if github else "application/json")}
    if github and TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=240) as response:
            body = response.read(MAX_ARCHIVE_BYTES + 1)
            too_large = len(body) > MAX_ARCHIVE_BYTES
            if too_large:
                body = None
            receipt = {
                "url": url,
                "started_at": started,
                "finished_at": now(),
                "http_status": response.status,
                "final_url": response.geturl(),
                "content_type": response.headers.get("Content-Type"),
                "content_length_header": response.headers.get("Content-Length"),
                "body_bytes": None if body is None else len(body),
                "body_sha256": None if body is None else sha256(body),
                "body_md5": None if body is None else md5(body),
                "error": "ABOVE_120MB_BOUND" if too_large else None,
            }
            return body, receipt
    except urllib.error.HTTPError as exc:
        error_body = exc.read()
        return None, {
            "url": url,
            "started_at": started,
            "finished_at": now(),
            "http_status": exc.code,
            "final_url": exc.geturl(),
            "content_type": exc.headers.get("Content-Type"),
            "content_length_header": exc.headers.get("Content-Length"),
            "body_bytes": len(error_body),
            "body_sha256": sha256(error_body),
            "body_md5": md5(error_body),
            "error": f"HTTPError:{exc.code}",
        }
    except Exception as exc:
        return None, {
            "url": url,
            "started_at": started,
            "finished_at": now(),
            "http_status": None,
            "final_url": None,
            "content_type": None,
            "content_length_header": None,
            "body_bytes": 0,
            "body_sha256": None,
            "body_md5": None,
            "error": f"{type(exc).__name__}:{exc}",
        }


def json_fetch(url: str, *, github: bool = False) -> tuple[Any, dict[str, Any]]:
    body, receipt = fetch(url, github=github)
    if body is None:
        return None, receipt
    try:
        return json.loads(body), receipt
    except Exception:
        receipt["error"] = "JSONDecodeError"
        return None, receipt


def load_rows() -> list[dict[str, Any]]:
    values = []
    for line in (V7 / "IDENTITY_RESOLUTION_ROWS_V7.jsonl").read_text().splitlines():
        row = json.loads(line)
        if not row["v7_same_identity_resolution"]:
            row["v7_row_line_sha256"] = sha256((line + "\n").encode())
            values.append(row)
    if len(values) != 10:
        raise RuntimeError(f"expected ten unresolved rows, found {len(values)}")
    return values


def norm_version(value: Any) -> str:
    text = str(value or "").strip().casefold()
    return text[1:] if text.startswith("v") else text


def datacite_attributes(obj: Any) -> dict[str, Any] | None:
    if not isinstance(obj, dict):
        return None
    data = obj.get("data") or {}
    attrs = data.get("attributes") or {}
    return {
        "doi": attrs.get("doi"),
        "url": attrs.get("url"),
        "version": attrs.get("version"),
        "publisher": attrs.get("publisher"),
        "rightsList": attrs.get("rightsList"),
        "relatedIdentifiers": attrs.get("relatedIdentifiers"),
        "state": attrs.get("state"),
    }


def github_release(repository: str, tag: str) -> dict[str, Any]:
    encoded = urllib.parse.quote(tag, safe="")
    url = f"https://api.github.com/repos/{repository}/releases/tags/{encoded}"
    obj, receipt = json_fetch(url, github=True)
    selected = None
    if isinstance(obj, dict):
        selected = {
            "id": obj.get("id"),
            "tag_name": obj.get("tag_name"),
            "target_commitish": obj.get("target_commitish"),
            "draft": obj.get("draft"),
            "prerelease": obj.get("prerelease"),
            "html_url": obj.get("html_url"),
            "assets": [
                {
                    "id": asset.get("id"),
                    "name": asset.get("name"),
                    "size": asset.get("size"),
                    "browser_download_url": asset.get("browser_download_url"),
                    "digest": asset.get("digest"),
                }
                for asset in obj.get("assets") or []
            ],
        }
    return {"request": receipt, "metadata": selected}


def github_license(repository: str, commit: str) -> dict[str, Any]:
    url = f"https://api.github.com/repos/{repository}/license?ref={commit}"
    obj, receipt = json_fetch(url, github=True)
    selected = None
    content = None
    if isinstance(obj, dict):
        raw = obj.get("content")
        if isinstance(raw, str) and obj.get("encoding") == "base64":
            try:
                content = base64.b64decode(raw)
            except Exception:
                content = None
        license_obj = obj.get("license") or {}
        selected = {
            "path": obj.get("path"),
            "git_blob_sha": obj.get("sha"),
            "spdx_id": license_obj.get("spdx_id"),
            "content_sha256": sha256(content) if content is not None else None,
            "content_bytes": len(content) if content is not None else None,
        }
    return {"request": receipt, "metadata": selected, "content": content}


def spdx_from_text(body: bytes) -> str | None:
    text = body.decode("utf-8", errors="ignore").casefold()
    if "apache license" in text and "version 2.0" in text:
        return "Apache-2.0"
    if "permission is hereby granted, free of charge" in text:
        return "MIT"
    if "redistribution and use in source and binary forms" in text and "neither the name" in text:
        return "BSD-3-Clause"
    if "redistribution and use in source and binary forms" in text:
        return "BSD-2-Clause"
    if "gnu general public license" in text and "version 3" in text:
        return "GPL-3.0-only"
    if "gnu general public license" in text and "version 2" in text:
        return "GPL-2.0-only"
    if "mozilla public license" in text and "2.0" in text:
        return "MPL-2.0"
    return None


def safe_evidence_name(index: int, member: str) -> Path:
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", member).strip("_")
    return EVIDENCE / f"{index}_{name[-140:]}"


def archive_members(body: bytes) -> tuple[str, list[tuple[str, int, bytes]]]:
    rows: list[tuple[str, int, bytes]] = []
    bio = io.BytesIO(body)
    if zipfile.is_zipfile(bio):
        bio.seek(0)
        with zipfile.ZipFile(bio) as archive:
            for info in archive.infolist():
                if info.is_dir() or info.file_size > MAX_MEMBER_BYTES:
                    continue
                try:
                    data = archive.read(info)
                except Exception:
                    continue
                rows.append((info.filename, info.file_size, data))
        return "zip", rows
    bio.seek(0)
    try:
        with tarfile.open(fileobj=bio, mode="r:*") as archive:
            for info in archive:
                if not info.isfile() or info.size > MAX_MEMBER_BYTES:
                    continue
                handle = archive.extractfile(info)
                if handle is None:
                    continue
                try:
                    data = handle.read(MAX_MEMBER_BYTES + 1)
                except Exception:
                    continue
                if len(data) <= MAX_MEMBER_BYTES:
                    rows.append((info.name, info.size, data))
        return "tar", rows
    except Exception:
        return "unknown", []


def interesting_path(path: str) -> bool:
    low = path.casefold()
    base = PurePosixPath(path).name.casefold()
    if any(token in base for token in ("license", "licence", "copying", "notice")):
        return True
    if "/.git/" in f"/{low}" or base in {".git_archival.txt", "fetch_head", "packed-refs", "head"}:
        return True
    if any(token in low for token in ("citation", "codemeta", "zenodo", "pkg-info", "direct_url", "metadata")):
        return True
    if base in {"pyproject.toml", "setup.cfg", "setup.py", "description", "description.md", "version.py", "_version.py"}:
        return True
    return False


def analyze_archive(
    index: int,
    body: bytes,
    *,
    expected_commit: str | None,
    expected_tag: str | None,
    commit_license: bytes | None,
) -> dict[str, Any]:
    kind, members = archive_members(body)
    scanned = 0
    commit_hits = []
    provenance_sha_candidates: dict[str, list[str]] = {}
    tag_hits = []
    licenses = []
    roots = sorted({PurePosixPath(path).parts[0] for path, _, _ in members if PurePosixPath(path).parts})
    for path, size, data in members:
        if scanned >= MAX_SCAN_BYTES:
            break
        textual = interesting_path(path) or (size <= 100_000 and PurePosixPath(path).suffix.casefold() in {
            ".txt", ".md", ".toml", ".cfg", ".ini", ".json", ".yaml", ".yml", ".py", ".r", ".jl"
        })
        if not textual:
            continue
        scanned += len(data)
        text = data.decode("utf-8", errors="ignore")
        low_path = path.casefold()
        is_provenance = "/.git/" in f"/{low_path}" or any(
            token in low_path for token in ("archival", "citation", "codemeta", "zenodo", "pkg-info", "direct_url", "metadata")
        )
        if expected_commit and expected_commit.casefold() in text.casefold():
            evidence_path = safe_evidence_name(index, path)
            evidence_path.parent.mkdir(parents=True, exist_ok=True)
            evidence_path.write_bytes(data)
            commit_hits.append({
                "member_path": path,
                "member_sha256": sha256(data),
                "member_bytes": len(data),
                "evidence_path": str(evidence_path.relative_to(HERE)),
                "provenance_shaped_path": is_provenance,
            })
        if is_provenance:
            candidates = sorted(set(re.findall(r"(?<![0-9a-fA-F])([0-9a-fA-F]{40})(?![0-9a-fA-F])", text)))
            if candidates:
                provenance_sha_candidates[path] = [value.casefold() for value in candidates]
        if expected_tag and expected_tag.casefold() in text.casefold() and is_provenance:
            tag_hits.append({"member_path": path, "member_sha256": sha256(data), "member_bytes": len(data)})
        base = PurePosixPath(path).name.casefold()
        if any(token in base for token in ("license", "licence", "copying")):
            detected = spdx_from_text(data)
            match = commit_license is not None and data == commit_license
            evidence_path = safe_evidence_name(index, path)
            evidence_path.parent.mkdir(parents=True, exist_ok=True)
            evidence_path.write_bytes(data)
            licenses.append({
                "member_path": path,
                "member_sha256": sha256(data),
                "member_bytes": len(data),
                "detected_spdx": detected,
                "accepted_spdx": detected in ACCEPTED,
                "byte_equal_to_exact_commit_license": match,
                "evidence_path": str(evidence_path.relative_to(HERE)),
            })
    return {
        "archive_kind": kind,
        "eligible_small_member_count": len(members),
        "root_names_from_eligible_members": roots,
        "scanned_bytes": scanned,
        "exact_full_commit_hits": commit_hits,
        "provenance_full_sha_candidates": provenance_sha_candidates,
        "exact_tag_provenance_hits": tag_hits,
        "license_candidates": licenses,
    }


def version_field(row: dict[str, Any]) -> str | None:
    return (row.get("joss_review_evidence") or {}).get("version_field")


def selected_archive_metadata(row: dict[str, Any]) -> dict[str, Any] | None:
    evidence = row.get("archive_provider_evidence") or {}
    metadata = evidence.get("metadata") or evidence.get("frozen_record_metadata")
    return metadata if isinstance(metadata, dict) and metadata.get("files") else None


def discover_concept_child(row: dict[str, Any], probe: dict[str, Any]) -> dict[str, Any] | None:
    doi = row["archive_doi"]
    recid = doi.rsplit(".", 1)[-1]
    dc, dc_receipt = json_fetch(f"https://api.datacite.org/dois/{urllib.parse.quote(doi, safe='')}")
    probe["datacite_frozen_doi"] = {"request": dc_receipt, "attributes": datacite_attributes(dc)}
    direct, direct_receipt = json_fetch(f"https://zenodo.org/api/records/{recid}")
    probe["zenodo_direct_record"] = {"request": direct_receipt, "metadata": direct if isinstance(direct, dict) else None}
    versions, versions_receipt = json_fetch(f"https://zenodo.org/api/records/{recid}/versions")
    probe["zenodo_versions"] = {"request": versions_receipt, "metadata": versions if isinstance(versions, dict) else None}
    query = urllib.parse.quote(f"conceptrecid:{recid}")
    search, search_receipt = json_fetch(f"https://zenodo.org/api/records?q={query}&all_versions=true&size=50")
    probe["zenodo_exact_concept_search"] = {"request": search_receipt, "metadata": search if isinstance(search, dict) else None}
    candidates = []
    for obj in (direct,):
        if isinstance(obj, dict) and obj.get("files"):
            candidates.append(obj)
    for obj in (versions, search):
        hits = ((obj or {}).get("hits") or {}).get("hits") if isinstance(obj, dict) else []
        for hit in hits or []:
            if isinstance(hit, dict) and hit.get("files"):
                candidates.append(hit)
    wanted = norm_version(version_field(row))
    compatible = [item for item in candidates if norm_version((item.get("metadata") or {}).get("version")) == wanted]
    unique = {str(item.get("id")): item for item in compatible if item.get("id")}
    probe["unique_provider_version_matches"] = [
        {
            "id": item.get("id"),
            "doi": ((item.get("pids") or {}).get("doi") or {}).get("identifier") or (item.get("metadata") or {}).get("doi"),
            "version": (item.get("metadata") or {}).get("version"),
            "files": item.get("files"),
            "license": (item.get("metadata") or {}).get("license"),
        }
        for item in unique.values()
    ]
    return next(iter(unique.values())) if len(unique) == 1 else None


def main() -> None:
    started_wall = now()
    started_mono = time.monotonic()
    EVIDENCE.mkdir(exist_ok=True)
    probes = []
    for row in load_rows():
        index = row["frozen_index"]
        tag = version_field(row)
        accepted = row.get("accepted_exact_tag_commit") or {}
        commit = accepted.get("commit_sha")
        probe: dict[str, Any] = {
            "frozen_index": index,
            "publication_doi": row["publication_doi"],
            "archive_doi": row["archive_doi"],
            "repository": row["repository"],
            "v7_row_line_sha256": row["v7_row_line_sha256"],
            "v7_failure_causes": row["v7_failure_causes"],
            "publication_version_field": tag,
            "v7_exact_commit": commit,
        }

        if index in {36, 196}:
            discovered = discover_concept_child(row, probe)
            archive_metadata = discovered
        else:
            archive_metadata = selected_archive_metadata(row)

        release = github_release(row["repository"], tag) if tag else None
        probe["source_native_release"] = release

        license_result = github_license(row["repository"], commit) if commit else None
        commit_license = license_result.pop("content") if license_result else None
        probe["exact_commit_license"] = license_result

        files = (archive_metadata or {}).get("files") or []
        archive_file = files[0] if len(files) == 1 else None
        content_url = None
        if isinstance(archive_file, dict):
            links = archive_file.get("links") or {}
            content_url = archive_file.get("content_url") or links.get("content") or archive_file.get("download")
        if content_url:
            body, archive_request = fetch(content_url, accept="application/octet-stream")
            probe["provider_archive_request"] = archive_request
            provider_checksum = archive_file.get("checksum") if isinstance(archive_file, dict) else None
            checksum_ok = None
            if body is not None and isinstance(provider_checksum, str) and provider_checksum.startswith("md5:"):
                checksum_ok = md5(body) == provider_checksum.split(":", 1)[1].casefold()
            probe["provider_checksum"] = provider_checksum
            probe["provider_checksum_verified"] = checksum_ok
            if body is not None:
                probe["archive_analysis"] = analyze_archive(
                    index,
                    body,
                    expected_commit=commit,
                    expected_tag=tag,
                    commit_license=commit_license,
                )
                assets = ((release or {}).get("metadata") or {}).get("assets") or []
                exact_asset_matches = []
                for asset in assets:
                    if asset.get("size") != len(body) or not asset.get("browser_download_url"):
                        continue
                    asset_body, asset_receipt = fetch(asset["browser_download_url"], accept="application/octet-stream")
                    exact_asset_matches.append({
                        "asset": asset,
                        "request": asset_receipt,
                        "byte_equal_to_provider_archive": asset_body == body if asset_body is not None else False,
                    })
                probe["exact_size_release_asset_attempts"] = exact_asset_matches
        else:
            probe["provider_archive_request"] = None
            probe["archive_analysis"] = None

        # The exact SWH archive path for TARGENE embeds a seven-hex Git commit
        # prefix. Resolve that one provider-authenticated candidate only.
        if index == 199:
            swhid = (((row.get("archive_provider_evidence") or {}).get("metadata") or {}).get("swh") or {}).get("swhid")
            match = re.search(r"-([0-9a-f]{7,40})(?:$|[;/?])", str(swhid or ""), re.I)
            prefix = match.group(1).casefold() if match else None
            candidate = None
            candidate_receipt = None
            if prefix:
                candidate, candidate_receipt = json_fetch(
                    f"https://api.github.com/repos/{row['repository']}/commits/{prefix}", github=True
                )
            probe["provider_swh_path_commit_prefix"] = {
                "swhid": swhid,
                "prefix": prefix,
                "request": candidate_receipt,
                "full_commit_sha": candidate.get("sha") if isinstance(candidate, dict) else None,
            }
        probes.append(probe)

    runtime = time.monotonic() - started_mono
    output = {
        "schema_version": "orion.p4.provider-native-targeted-probe-receipt.v8",
        "authority": "PROVIDER_NATIVE_AUTHORITATIVE_METADATA_ARCHIVES_AND_APIS_ONLY",
        "started_at": started_wall,
        "finished_at": now(),
        "runtime_seconds": round(runtime, 6),
        "target_count": len(probes),
        "one_targeted_pass": True,
        "broad_harvest": False,
        "probes": probes,
    }
    OUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(f"P4_V8_PROVIDER_PASS_COMPLETE__10_TARGETS__RUNTIME_SECONDS={runtime:.6f}")


if __name__ == "__main__":
    main()
