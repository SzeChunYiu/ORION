#!/usr/bin/env python3
"""Resolve only the 24 frozen P4 V6 identities with publication-native evidence.

The V7 discriminator is deliberately different from the V6 manifest search.  It
uses the exact Crossref/JOSS review record, the exact archive provider record,
and the final JOSS editorial archive/version/tag checks to bind a source-native
tag to an immutable commit.  Nothing except the frozen publications counts as a
unit.  A missing edge remains CANNOT_CHECK.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import os
import re
import stat
import subprocess
import tarfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any


HERE = Path(__file__).resolve().parent
V6 = HERE.parent / "p4-m6-joss-bridge-repair-v6-2026-08-23"
INPUT = HERE / "UNRESOLVED_IDENTITIES_INPUT_V7.jsonl"
ROWS = HERE / "IDENTITY_RESOLUTION_ROWS_V7.jsonl"
UA = "orion-p4-v7-targeted-identity-resolution/1.0"

ACCEPTED = {
    "MIT", "BSD-2-Clause", "BSD-3-Clause", "Apache-2.0", "GPL-2.0-only",
    "GPL-2.0-or-later", "GPL-3.0-only", "GPL-3.0-or-later",
    "LGPL-2.1-only", "LGPL-2.1-or-later", "LGPL-3.0-only",
    "LGPL-3.0-or-later", "MPL-2.0", "ISC", "EPL-2.0",
    "AGPL-3.0-only", "AGPL-3.0-or-later", "Unlicense", "CC0-1.0",
}
ALIASES = {
    "mit": "MIT", "mit-license": "MIT", "bsd-2-clause": "BSD-2-Clause",
    "bsd-2-clause-netbsd": "BSD-2-Clause", "bsd-3-clause": "BSD-3-Clause",
    "apache-2.0": "Apache-2.0", "apache2.0": "Apache-2.0",
    "gpl-2.0": "GPL-2.0-only", "gpl-3.0": "GPL-3.0-only",
    "gpl-3.0-or-later": "GPL-3.0-or-later", "lgpl-2.1": "LGPL-2.1-only",
    "lgpl-3.0": "LGPL-3.0-only", "mpl-2.0": "MPL-2.0", "isc": "ISC",
    "unlicense": "Unlicense", "cc0-1.0": "CC0-1.0",
}


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def canon_sha(value: Any) -> str:
    return sha_bytes(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def dump_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def spdx(value: Any) -> str | None:
    if isinstance(value, dict):
        value = value.get("id") or value.get("name")
    if not value:
        return None
    text = str(value).strip()
    if text in ACCEPTED:
        return text
    return ALIASES.get(text.casefold())


def github_token() -> str:
    for key in ("GITHUB_TOKEN", "GH_TOKEN"):
        if os.environ.get(key):
            return os.environ[key]
    try:
        return subprocess.check_output(
            ["gh", "auth", "token"], text=True, stderr=subprocess.DEVNULL, timeout=10
        ).strip()
    except Exception:
        return ""


TOKEN = github_token()


def fetch(url: str, *, github: bool = False, attempts: int = 3) -> tuple[bytes | None, dict[str, Any]]:
    trail: list[dict[str, Any]] = []
    for attempt in range(1, attempts + 1):
        started = now()
        headers = {"User-Agent": UA, "Accept": "application/vnd.github+json" if github else "application/json"}
        if github and TOKEN:
            headers["Authorization"] = f"Bearer {TOKEN}"
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                body = response.read()
                trail.append({
                    "attempt": attempt,
                    "started_at": started,
                    "http_status": response.status,
                    "final_url": response.geturl(),
                    "content_type": response.headers.get("Content-Type"),
                    "body_bytes": len(body),
                    "body_sha256": sha_bytes(body),
                    "error": None,
                })
                return body, {"url": url, "attempts": trail}
        except urllib.error.HTTPError as exc:
            body = exc.read()
            trail.append({
                "attempt": attempt,
                "started_at": started,
                "http_status": exc.code,
                "final_url": exc.geturl(),
                "content_type": exc.headers.get("Content-Type"),
                "body_bytes": len(body),
                "body_sha256": sha_bytes(body),
                "error": f"HTTPError:{exc.code}",
            })
            if exc.code not in (429, 500, 502, 503, 504):
                break
        except Exception as exc:
            trail.append({
                "attempt": attempt,
                "started_at": started,
                "http_status": None,
                "final_url": None,
                "content_type": None,
                "body_bytes": 0,
                "body_sha256": None,
                "error": type(exc).__name__,
            })
        time.sleep(min(8, 2 ** (attempt - 1)))
    return None, {"url": url, "attempts": trail}


def json_fetch(url: str, *, github: bool = False) -> tuple[Any, dict[str, Any]]:
    body, receipt = fetch(url, github=github)
    if body is None:
        return None, receipt
    try:
        return json.loads(body), receipt
    except Exception:
        receipt["parse_error"] = "JSONDecodeError"
        return None, receipt


def request_pass(receipt: dict[str, Any]) -> bool:
    attempts = receipt.get("attempts") or []
    return bool(attempts and attempts[-1].get("http_status") == 200 and not receipt.get("parse_error"))


def marker(body: str, name: str) -> str | None:
    match = re.search(rf"<!--{re.escape(name)}-->(.*?)<!--end-{re.escape(name)}-->", body or "", re.I | re.S)
    if not match:
        return None
    value = re.sub(r"<[^>]+>", "", match.group(1)).strip()
    return value or None


def norm_doi(value: Any) -> str:
    text = str(value or "").strip().casefold()
    text = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", text)
    return text.rstrip("/.,;)")


def norm_repo(value: Any) -> str | None:
    text = str(value or "").strip()
    match = re.search(r"github\.com/([^/\s]+)/([^/\s#?]+)", text, re.I)
    if match:
        return f"{match.group(1)}/{match.group(2).removesuffix('.git')}".casefold()
    if re.fullmatch(r"[^/\s]+/[^/\s]+", text):
        return text.removesuffix(".git").casefold()
    return None


def norm_version(value: Any) -> str:
    text = str(value or "").strip().casefold()
    return text[1:] if text.startswith("v") else text


def version_candidates(value: Any) -> list[str]:
    text = str(value or "").strip()
    if not text:
        return []
    values = [text]
    variant = text[1:] if text[:1] in "vV" else f"v{text}"
    if variant and variant not in values:
        values.append(variant)
    return values


def resolve_tag(repository: str, tag: str) -> tuple[str | None, list[dict[str, Any]]]:
    owner, name = repository.split("/", 1)
    encoded = urllib.parse.quote(tag, safe="")
    obj, receipt = json_fetch(
        f"https://api.github.com/repos/{owner}/{name}/git/ref/tags/{encoded}", github=True
    )
    receipts = [{"purpose": "resolve_exact_tag_ref", **receipt}]
    if not isinstance(obj, dict):
        return None, receipts
    target = obj.get("object") or {}
    target_type, target_sha = target.get("type"), target.get("sha")
    if target_type == "tag" and re.fullmatch(r"[0-9a-fA-F]{40}", str(target_sha or "")):
        annotated, annotated_receipt = json_fetch(
            f"https://api.github.com/repos/{owner}/{name}/git/tags/{target_sha}", github=True
        )
        receipts.append({"purpose": "dereference_annotated_tag", **annotated_receipt})
        if isinstance(annotated, dict):
            target = annotated.get("object") or {}
            target_type, target_sha = target.get("type"), target.get("sha")
    if target_type == "commit" and re.fullmatch(r"[0-9a-fA-F]{40}", str(target_sha or "")):
        return str(target_sha).lower(), receipts
    return None, receipts


def license_at(repository: str, commit: str) -> tuple[str | None, dict[str, Any]]:
    owner, name = repository.split("/", 1)
    obj, receipt = json_fetch(
        f"https://api.github.com/repos/{owner}/{name}/license?ref={commit}", github=True
    )
    license_obj = (obj or {}).get("license") or {} if isinstance(obj, dict) else {}
    selected = {
        "spdx_id": license_obj.get("spdx_id"),
        "name": license_obj.get("name"),
        "key": license_obj.get("key"),
        "license_blob_sha": (obj or {}).get("sha") if isinstance(obj, dict) else None,
        "path": (obj or {}).get("path") if isinstance(obj, dict) else None,
    }
    return spdx(selected.get("spdx_id")), {"purpose": "bind_license_at_exact_commit", "metadata": selected, **receipt}


def crossref_relation(message: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    relation = message.get("relation") or {}
    archive = norm_doi(row["archive_doi"])
    references = [norm_doi(item.get("id")) for item in relation.get("references") or []]
    reviews = [str(item.get("id") or "") for item in relation.get("has-review") or []]
    issue_number = int(row["publication_doi"].rsplit(".", 1)[-1])
    expected_review = f"https://github.com/openjournals/joss-reviews/issues/{issue_number}"
    return {
        "publication_doi": norm_doi(message.get("DOI")),
        "exact_publication_doi_match": norm_doi(message.get("DOI")) == norm_doi(row["publication_doi"]),
        "referenced_archive_dois": references,
        "exact_archive_doi_referenced": archive in references,
        "review_urls": reviews,
        "exact_review_issue_referenced": expected_review.casefold() in {url.casefold().rstrip("/") for url in reviews},
        "expected_review_issue_url": expected_review,
    }


def selected_zenodo(record: dict[str, Any]) -> dict[str, Any]:
    metadata = record.get("metadata") or {}
    custom = metadata.get("custom") or {}
    return {
        "id": record.get("id"),
        "doi": record.get("doi"),
        "conceptdoi": record.get("conceptdoi"),
        "conceptrecid": record.get("conceptrecid"),
        "version": metadata.get("version"),
        "license": metadata.get("license"),
        "resource_type": metadata.get("resource_type"),
        "code_repository": custom.get("code:codeRepository"),
        "related_identifiers": metadata.get("related_identifiers") or [],
        "relations": metadata.get("relations") or {},
        "swh": record.get("swh") or {},
        "files": [
            {
                "key": item.get("key"),
                "size": item.get("size"),
                "checksum": item.get("checksum"),
                "content_url": (item.get("links") or {}).get("self"),
            }
            for item in record.get("files") or []
        ],
    }


def archive_version_compatible(publication_version: Any, archive_version: Any) -> bool:
    """Match exact case-sensitive versions after removing only a lowercase v prefix.

    The pre-live V7 freeze did not authorize case folding.  A provider ``V`` and
    a JOSS ``v`` therefore remain different even when every other edge passes.
    The sole suffix rule is the provider's explicit ``-JOSS`` archival tag.
    """
    publication = str(publication_version or "").strip()
    archive = str(archive_version or "").strip()
    if publication.startswith("v"):
        publication = publication[1:]
    if archive.startswith("v"):
        archive = archive[1:]
    return bool(publication and archive and (archive == publication or archive == f"{publication}-JOSS"))


def fetch_archive(row: dict[str, Any], publication_version: Any) -> dict[str, Any]:
    doi = norm_doi(row["archive_doi"])
    zenodo = re.fullmatch(r"10\.5281/zenodo\.(\d+)", doi)
    if zenodo:
        record_id = zenodo.group(1)
        frozen_record, frozen_record_receipt = json_fetch(f"https://zenodo.org/api/records/{record_id}")
        versions_url = (frozen_record.get("links") or {}).get("versions") if isinstance(frozen_record, dict) else None
        versions, versions_receipt = json_fetch(versions_url) if versions_url else (None, {"url": None, "attempts": []})
        version_members: list[dict[str, Any]] = []
        if isinstance(versions, dict):
            for hit in ((versions.get("hits") or {}).get("hits") or []):
                metadata = hit.get("metadata") or {}
                version_members.append({
                    "id": hit.get("id"),
                    "doi": norm_doi(hit.get("doi") or metadata.get("doi")),
                    "version": metadata.get("version"),
                    "version_compatible_with_publication": archive_version_compatible(
                        publication_version, metadata.get("version")
                    ),
                })
        frozen_selected = selected_zenodo(frozen_record) if isinstance(frozen_record, dict) else {}
        direct_exact = norm_doi(frozen_selected.get("doi")) == doi
        compatible = [item for item in version_members if item["version_compatible_with_publication"]]
        selected_record = frozen_record if direct_exact else None
        selection_method = "EXACT_FROZEN_VERSION_DOI" if selected_record is not None else None
        selected_record_request = frozen_record_receipt if selected_record is not None else None
        if selected_record is None and len(compatible) == 1:
            selected_record, selected_record_request = json_fetch(
                f"https://zenodo.org/api/records/{compatible[0]['id']}"
            )
            if isinstance(selected_record, dict):
                selection_method = "FROZEN_CONCEPT_VERSION_HISTORY_UNIQUE_JOSS_VERSION_CHILD"
        selected = selected_zenodo(selected_record) if isinstance(selected_record, dict) else {}
        exact_relation = bool(direct_exact or (
            selected and archive_version_compatible(publication_version, selected.get("version"))
        ))
        concept = norm_doi((frozen_record or {}).get("conceptdoi")) if isinstance(frozen_record, dict) else ""
        frozen_is_concept = bool(not direct_exact and concept == doi)
        return {
            "provider": "ZENODO",
            "frozen_record_request": frozen_record_receipt,
            "versions_request": versions_receipt,
            "selected_record_request": selected_record_request,
            "frozen_record_metadata": frozen_selected,
            "metadata": selected,
            "version_members": version_members,
            "version_selection_method": selection_method,
            "selected_archive_doi": norm_doi(selected.get("doi")) or None,
            "selected_archive_is_frozen_doi": norm_doi(selected.get("doi")) == doi,
            "exact_frozen_archive_doi_match": direct_exact,
            "exact_archive_version_relation": exact_relation,
            "distinct_concept_doi": concept if concept and concept != doi else None,
            "frozen_doi_is_concept_or_latest_redirect": frozen_is_concept,
            "accepted_archive_spdx": spdx(selected.get("license")),
            "provider_file_checksums_bound": bool(selected.get("files")) and all(
                item.get("checksum") for item in selected.get("files") or []
            ),
            "transport_pass": request_pass(frozen_record_receipt) and request_pass(versions_receipt)
            and bool(selected_record_request and request_pass(selected_record_request)),
        }
    figshare = re.fullmatch(r"10\.6084/m9\.figshare\.(\d+)(?:\.v(\d+))?", doi)
    if figshare:
        article_id, explicit_version = figshare.group(1), figshare.group(2)
        suffix = f"/versions/{explicit_version}" if explicit_version else ""
        record, record_receipt = json_fetch(f"https://api.figshare.com/v2/articles/{article_id}{suffix}")
        versions, versions_receipt = json_fetch(f"https://api.figshare.com/v2/articles/{article_id}/versions")
        selected = {}
        if isinstance(record, dict):
            selected = {
                "id": record.get("id"), "doi": record.get("doi"), "version": record.get("version"),
                "license": record.get("license"), "references": record.get("references") or [],
                "related_materials": record.get("related_materials") or [],
                "files": [
                    {
                        "id": item.get("id"), "key": item.get("name"), "size": item.get("size"),
                        "checksum": item.get("supplied_md5") or item.get("computed_md5"),
                        "content_url": item.get("download_url"),
                    }
                    for item in record.get("files") or []
                ],
            }
        version_dois = []
        for item in versions if isinstance(versions, list) else []:
            version_dois.append(f"10.6084/m9.figshare.{article_id}.v{item.get('version')}")
        exact = norm_doi(selected.get("doi")) == doi
        base_to_v1 = bool(not explicit_version and selected.get("version") == 1 and norm_doi(selected.get("doi")) == f"{doi}.v1")
        return {
            "provider": "FIGSHARE", "record_request": record_receipt,
            "versions_request": versions_receipt, "metadata": selected,
            "version_history_dois": version_dois,
            "version_selection_method": "FIGSHARE_FROZEN_BASE_DOI_UNIQUE_V1" if base_to_v1 else ("EXACT_FROZEN_VERSION_DOI" if exact else None),
            "selected_archive_doi": norm_doi(selected.get("doi")) or None,
            "selected_archive_is_frozen_doi": exact,
            "exact_frozen_archive_doi_match": exact,
            "exact_archive_version_relation": exact or base_to_v1,
            "distinct_concept_doi": None,
            "frozen_doi_is_concept_or_latest_redirect": not exact and explicit_version is None,
            "accepted_archive_spdx": spdx(selected.get("license")),
            "provider_file_checksums_bound": bool(selected.get("files")) and all(
                item.get("checksum") for item in selected.get("files") or []
            ),
            "transport_pass": request_pass(record_receipt) and request_pass(versions_receipt),
        }
    return {
        "provider": "UNSUPPORTED", "metadata": {}, "exact_frozen_archive_doi_match": False,
        "exact_archive_version_relation": False,
        "accepted_archive_spdx": None, "provider_file_checksums_bound": False,
        "transport_pass": False,
    }


def safe_parts(name: str) -> list[str] | None:
    path = PurePosixPath(name.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts:
        return None
    return [part for part in path.parts if part not in ("", ".")]


def normalized_archive_manifest(body: bytes, *, commit: str | None = None) -> tuple[dict[str, Any], list[str]]:
    """Return V6-compatible normalized manifest metadata without retaining files."""
    items: list[dict[str, Any]] = []
    commit_paths: list[str] = []
    kind = None
    try:
        stream = io.BytesIO(body)
        if zipfile.is_zipfile(stream):
            kind = "zip"
            stream.seek(0)
            with zipfile.ZipFile(stream) as archive:
                seen: set[str] = set()
                for info in archive.infolist():
                    if info.is_dir():
                        continue
                    parts = safe_parts(info.filename)
                    if not parts:
                        return {"status": "REJECT_UNSAFE_PATH", "archive_kind": kind}, []
                    name = "/".join(parts)
                    if name in seen:
                        return {"status": "REJECT_DUPLICATE_PATH", "archive_kind": kind}, []
                    seen.add(name)
                    mode = (info.external_attr >> 16) & 0o177777
                    data = archive.read(info)
                    entry_type = "symlink" if stat.S_ISLNK(mode) else "file"
                    executable = bool(mode & 0o111) if entry_type == "file" else False
                    if commit and commit.encode() in data:
                        commit_paths.append(name)
                    items.append({
                        "path": name, "type": entry_type, "executable": executable,
                        "size": len(data), "sha256": sha_bytes(data),
                    })
        else:
            stream.seek(0)
            with tarfile.open(fileobj=stream, mode="r:*") as archive:
                kind = "tar"
                seen = set()
                for info in archive.getmembers():
                    if info.isdir():
                        continue
                    parts = safe_parts(info.name)
                    if not parts:
                        return {"status": "REJECT_UNSAFE_PATH", "archive_kind": kind}, []
                    name = "/".join(parts)
                    if name in seen:
                        return {"status": "REJECT_DUPLICATE_PATH", "archive_kind": kind}, []
                    seen.add(name)
                    if info.issym():
                        data, entry_type, executable = info.linkname.encode(), "symlink", False
                    elif info.isfile():
                        extracted = archive.extractfile(info)
                        data = extracted.read() if extracted else b""
                        entry_type, executable = "file", bool(info.mode & 0o111)
                    else:
                        continue
                    if commit and commit.encode() in data:
                        commit_paths.append(name)
                    items.append({
                        "path": name, "type": entry_type, "executable": executable,
                        "size": len(data), "sha256": sha_bytes(data),
                    })
    except (tarfile.TarError, zipfile.BadZipFile):
        return {"status": "CANNOT_CHECK_UNSUPPORTED_ARCHIVE", "archive_kind": kind}, []
    except Exception as exc:
        return {"status": f"CANNOT_CHECK_EXTRACTION_{type(exc).__name__}", "archive_kind": kind}, []
    first = {item["path"].split("/", 1)[0] for item in items if item.get("path")}
    if len(first) == 1 and items and all("/" in item["path"] for item in items):
        for item in items:
            item["path"] = item["path"].split("/", 1)[1]
    items.sort(key=lambda item: (item["path"], item["type"]))
    return {
        "status": "PASS", "archive_kind": kind, "file_count": len(items),
        "manifest_sha256": canon_sha(items),
        "total_uncompressed_bytes": sum(item["size"] for item in items),
    }, commit_paths


def parse_swh(metadata: dict[str, Any]) -> dict[str, Any]:
    swhid = (metadata.get("swh") or {}).get("swhid") if isinstance(metadata.get("swh"), dict) else None
    if not swhid:
        return {"swhid": None, "directory_id": None, "path": None}
    directory = re.search(r"^swh:1:dir:([0-9a-f]{40})", swhid)
    path_match = re.search(r"(?:^|;)path=([^;]*)", swhid)
    return {
        "swhid": swhid,
        "directory_id": directory.group(1) if directory else None,
        "path": urllib.parse.unquote(path_match.group(1)) if path_match else None,
    }


def resolve_swh_path(directory_id: str, path: str | None) -> tuple[str | None, list[dict[str, Any]]]:
    current = directory_id
    receipts: list[dict[str, Any]] = []
    for component in [part for part in (path or "").strip("/").split("/") if part]:
        entries, receipt = json_fetch(f"https://archive.softwareheritage.org/api/1/directory/{current}/")
        receipts.append({"purpose": "resolve_qualified_swhid_path_component", "component": component, **receipt})
        match = None
        for entry in entries if isinstance(entries, list) else []:
            name = entry.get("name")
            if isinstance(name, bytes):
                name = name.decode(errors="replace")
            if name == component and entry.get("type") == "dir":
                match = entry.get("target")
                break
        if not re.fullmatch(r"[0-9a-f]{40}", str(match or "")):
            return None, receipts
        current = str(match)
    return current, receipts


def related_identifier_targets(metadata: dict[str, Any], repository: str) -> list[dict[str, Any]]:
    values: list[Any] = list(metadata.get("related_identifiers") or [])
    values.extend(metadata.get("related_materials") or [])
    values.extend(metadata.get("references") or [])
    output: list[dict[str, Any]] = []
    expected = repository.casefold()
    for item in values:
        url = item.get("identifier") or item.get("url") if isinstance(item, dict) else str(item)
        url = str(url or "")
        if norm_repo(url) != expected:
            continue
        tag_match = re.search(r"/(?:tree|releases/tag)/([^/?#]+)", url, re.I)
        commit_match = re.search(r"/commit/([0-9a-fA-F]{40})(?:$|[/?#])", url, re.I)
        output.append({
            "url": url,
            "relation": item.get("relation") if isinstance(item, dict) else None,
            "tag": urllib.parse.unquote(tag_match.group(1)) if tag_match else None,
            "commit_sha": commit_match.group(1).lower() if commit_match else None,
        })
    return output


def evaluate_archive_commit_identity(
    row: dict[str, Any], archive: dict[str, Any], selected_tag: dict[str, Any] | None,
    v6_row: dict[str, Any],
) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        "status": "CANNOT_CHECK", "accepted_method": None,
        "related_identifier_attempts": [], "swh_attempt": None,
        "content_attempts": [],
    }
    if not selected_tag or not archive.get("exact_archive_version_relation"):
        return evidence
    commit = selected_tag["commit_sha"]
    selected_doi = norm_doi(archive.get("selected_archive_doi"))

    prior = v6_row.get("accepted_content_identity")
    prior_doi = norm_doi((v6_row.get("source_native_metadata") or {}).get("doi"))
    if prior and prior.get("commit_sha") == commit and prior_doi == selected_doi:
        evidence.update({
            "status": "PASS", "accepted_method": f"V6_{prior.get('content_identity_method')}",
            "prior_v6_content_identity": prior,
        })
        return evidence

    targets = related_identifier_targets(archive.get("metadata") or {}, row["repository"])
    for target in targets:
        target_commit = target.get("commit_sha")
        requests: list[dict[str, Any]] = []
        if target.get("tag"):
            target_commit, requests = resolve_tag(row["repository"], target["tag"])
        attempt = {**target, "resolved_commit_sha": target_commit, "requests": requests}
        evidence["related_identifier_attempts"].append(attempt)
        if target_commit == commit:
            evidence.update({
                "status": "PASS",
                "accepted_method": "ARCHIVE_PROVIDER_RELATED_IDENTIFIER_EXACT_TAG_TO_SAME_IMMUTABLE_COMMIT",
            })
            return evidence

    swh = parse_swh(archive.get("metadata") or {})
    if swh.get("directory_id"):
        revision, revision_request = json_fetch(
            f"https://archive.softwareheritage.org/api/1/revision/{commit}/"
        )
        commit_directory = revision.get("directory") if isinstance(revision, dict) else None
        resolved_directory, path_requests = resolve_swh_path(swh["directory_id"], swh.get("path"))
        contains_exact_tree = False
        root_request = None
        root_entries_selected: list[dict[str, Any]] = []
        if commit_directory and resolved_directory == swh["directory_id"] and resolved_directory != commit_directory:
            entries, root_request = json_fetch(
                f"https://archive.softwareheritage.org/api/1/directory/{resolved_directory}/"
            )
            if isinstance(entries, list):
                for entry in entries:
                    name = entry.get("name")
                    if isinstance(name, bytes):
                        name = name.decode(errors="replace")
                    root_entries_selected.append({"name": name, "type": entry.get("type"), "target": entry.get("target")})
                exact_children = [entry for entry in root_entries_selected if entry["type"] == "dir" and entry["target"] == commit_directory]
                other_dirs = [entry for entry in root_entries_selected if entry["type"] == "dir" and entry["target"] != commit_directory]
                contains_exact_tree = len(exact_children) == 1 and all(
                    str(entry["name"]).casefold() == "__macosx" for entry in other_dirs
                )
        evidence["swh_attempt"] = {
            **swh, "commit_revision_directory": commit_directory,
            "resolved_archive_directory": resolved_directory,
            "qualified_path_or_root_equals_commit_directory": resolved_directory == commit_directory,
            "wrapper_root_contains_exact_commit_directory_plus_only_macos_metadata": contains_exact_tree,
            "revision_request": revision_request, "path_requests": path_requests,
            "root_request": root_request, "root_entries": root_entries_selected,
        }
        if commit_directory and (resolved_directory == commit_directory or contains_exact_tree):
            evidence.update({
                "status": "PASS",
                "accepted_method": "ARCHIVE_SWH_DIRECTORY_IDENTITY_EQUALS_IMMUTABLE_COMMIT_ROOT_TREE",
            })
            return evidence

    max_bytes = int(os.environ.get("P4_V7_CONTENT_IDENTITY_MAX_BYTES", "60000000"))
    for file_meta in (archive.get("metadata") or {}).get("files") or []:
        size = int(file_meta.get("size") or 0)
        url = file_meta.get("content_url")
        if not url or not size or size > max_bytes:
            evidence["content_attempts"].append({
                "file": file_meta.get("key"), "size": size,
                "status": "CANNOT_CHECK_ABOVE_DISCLOSED_BYTE_BOUND_OR_NO_URL",
                "byte_bound": max_bytes,
            })
            continue
        archive_body, archive_request = fetch(url)
        attempt: dict[str, Any] = {
            "file": file_meta.get("key"), "size": size,
            "archive_download_request": archive_request,
            "provider_checksum": file_meta.get("checksum"),
            "byte_bound": max_bytes,
        }
        if archive_body is None:
            attempt["status"] = "CANNOT_CHECK_ARCHIVE_DOWNLOAD"
            evidence["content_attempts"].append(attempt)
            continue
        archive_manifest, commit_paths = normalized_archive_manifest(archive_body, commit=commit)
        attempt["archive_manifest"] = archive_manifest
        attempt["archive_full_commit_sha_paths"] = commit_paths
        provenance_names = {
            "revision.py", "_version.py", "version.py", "git_revision", "git_revision.txt",
            "commit.txt", "commit_sha.txt", "revision.txt",
        }
        provenance_paths = [
            path for path in commit_paths
            if PurePosixPath(path).name.casefold() in provenance_names and "/.git/" not in f"/{path.casefold()}/"
        ]
        attempt["archive_provenance_files_embedding_full_commit_sha"] = provenance_paths
        if provenance_paths:
            attempt["status"] = "PASS_ARCHIVE_EMBEDS_EXACT_FULL_COMMIT_SHA"
            evidence["content_attempts"].append(attempt)
            evidence.update({
                "status": "PASS",
                "accepted_method": "ARCHIVE_BYTES_EMBED_EXACT_FULL_COMMIT_SHA_RESOLVED_FROM_JOSS_TAG",
            })
            return evidence

        owner, name = row["repository"].split("/", 1)
        github_body, github_request = fetch(
            f"https://api.github.com/repos/{owner}/{name}/tarball/{commit}", github=True
        )
        attempt["immutable_commit_archive_request"] = github_request
        if github_body is not None:
            github_manifest, _ = normalized_archive_manifest(github_body)
            attempt["immutable_commit_manifest"] = github_manifest
            manifest_equal = all([
                archive_manifest.get("status") == "PASS",
                github_manifest.get("status") == "PASS",
                archive_manifest.get("manifest_sha256") == github_manifest.get("manifest_sha256"),
            ])
            attempt["normalized_manifest_equal"] = manifest_equal
            if manifest_equal:
                attempt["status"] = "PASS_NORMALIZED_MANIFEST_EQUALITY"
                evidence["content_attempts"].append(attempt)
                evidence.update({
                    "status": "PASS",
                    "accepted_method": "ARCHIVE_NORMALIZED_MANIFEST_EQUALS_IMMUTABLE_COMMIT_ARCHIVE_MANIFEST",
                })
                return evidence

        release, release_request = json_fetch(
            f"https://api.github.com/repos/{owner}/{name}/releases/tags/{urllib.parse.quote(selected_tag['tag'], safe='')}",
            github=True,
        )
        attempt["exact_release_request"] = release_request
        exact_assets = []
        if isinstance(release, dict):
            exact_assets = [asset for asset in release.get("assets") or [] if asset.get("name") == file_meta.get("key") and int(asset.get("size") or 0) == size]
        if len(exact_assets) == 1:
            asset = exact_assets[0]
            asset_body, asset_request = fetch(asset.get("browser_download_url"), github=True)
            attempt["exact_release_asset"] = {
                "id": asset.get("id"), "name": asset.get("name"), "size": asset.get("size"),
                "url": asset.get("browser_download_url"), "digest": asset.get("digest"),
                "download_request": asset_request,
            }
            if asset_body is not None and sha_bytes(asset_body) == sha_bytes(archive_body):
                attempt["exact_release_asset"]["sha256"] = sha_bytes(asset_body)
                attempt["status"] = "PASS_EXACT_RELEASE_ASSET_BYTE_EQUALITY"
                evidence["content_attempts"].append(attempt)
                evidence.update({
                    "status": "PASS",
                    "accepted_method": "ARCHIVE_BYTES_EQUAL_EXACT_GITHUB_TAG_RELEASE_ASSET_BYTES",
                })
                return evidence
        attempt.setdefault("status", "CANNOT_CHECK_NO_CONTENT_IDENTITY")
        evidence["content_attempts"].append(attempt)
    return evidence


def extract_review_evidence(issue: dict[str, Any], comments: list[dict[str, Any]], row: dict[str, Any]) -> dict[str, Any]:
    body = str(issue.get("body") or "")
    repository_field = marker(body, "target-repository")
    version_field = marker(body, "version")
    archive_field = marker(body, "archive")
    editor_field = marker(body, "editor")
    archive = norm_doi(row["archive_doi"])
    repository = row["repository"].casefold()
    version_normalized = norm_version(version_field)
    archive_set_events: list[dict[str, Any]] = []
    version_set_events: list[dict[str, Any]] = []
    release_events: list[dict[str, Any]] = []
    checked_identity_statements: list[dict[str, Any]] = []
    archive_and_release_paired_events: list[dict[str, Any]] = []
    release_pattern = re.compile(
        r"https?://github\.com/([^/\s]+)/([^/\s)<>]+)/releases/tag/([^\s)<>]+)", re.I
    )
    for comment in comments:
        comment_body = str(comment.get("body") or "")
        common = {
            "comment_id": comment.get("id"),
            "user": (comment.get("user") or {}).get("login"),
            "created_at": comment.get("created_at"),
            "html_url": comment.get("html_url"),
            "body_sha256": sha_bytes(comment_body.encode()),
        }
        lower = comment_body.casefold()
        if "@editorialbot set" in lower and " as archive" in lower and archive in norm_doi(comment_body):
            archive_set_events.append(common)
        if "@editorialbot set" in lower and " as version" in lower and version_normalized:
            set_matches = re.findall(r"@editorialbot\s+set\s+([^\s]+)\s+as\s+version", comment_body, re.I)
            if any(norm_version(value) == version_normalized for value in set_matches):
                version_set_events.append({**common, "set_values": set_matches})
        current_releases = []
        for match in release_pattern.finditer(comment_body):
            release_repo = f"{match.group(1)}/{match.group(2).removesuffix('.git')}".casefold()
            tag = urllib.parse.unquote(match.group(3)).rstrip(".,;]")
            if release_repo != repository:
                continue
            event = {**common, "repository": release_repo, "tag": tag, "url": match.group(0).rstrip(".,;")}
            release_events.append(event)
            current_releases.append(event)
        if archive in norm_doi(comment_body):
            archive_and_release_paired_events.extend(current_releases)
        for line in comment_body.splitlines():
            compact = re.sub(r"\s+", " ", line).strip()
            low_line = compact.casefold()
            if not re.search(r"-\s*\[x\]", low_line):
                continue
            exact_archive_version_check = "archive" in low_line and (
                "version tag" in low_line or ("github release" in low_line and "release" in low_line)
            )
            tag_to_release_check = "software version tag" in low_line and "tagged release" in low_line
            if exact_archive_version_check or tag_to_release_check:
                checked_identity_statements.append({**common, "statement": compact})
    paired_tags = {event["tag"] for event in archive_and_release_paired_events}
    matching_release_tags = {
        event["tag"] for event in release_events if norm_version(event["tag"]) == version_normalized
    }
    return {
        "issue_number": issue.get("number"),
        "issue_html_url": issue.get("html_url"),
        "issue_state": issue.get("state"),
        "issue_body_sha256": sha_bytes(body.encode()),
        "repository_field": repository_field,
        "version_field": version_field,
        "archive_field": archive_field,
        "editor_field": editor_field,
        "exact_repository_match": norm_repo(repository_field) == repository,
        "exact_archive_field_match": norm_doi(archive_field) == archive,
        "archive_set_events": archive_set_events,
        "version_set_events": version_set_events,
        "release_events": release_events,
        "archive_and_release_paired_events": archive_and_release_paired_events,
        "checked_identity_statements": checked_identity_statements,
        "paired_exact_version_release_tags": sorted(
            tag for tag in paired_tags if norm_version(tag) == version_normalized
        ),
        "matching_release_tags": sorted(matching_release_tags),
    }


def primary_failure(causes: list[str]) -> str:
    order = [
        "EXACT_PUBLICATION_DOI_RELATION_CANNOT_CHECK",
        "EXACT_ARCHIVE_VERSION_DOI_RELATION_CANNOT_CHECK",
        "SAME_FROZEN_REPOSITORY_CANNOT_CHECK",
        "EXACT_JOSS_ARCHIVE_VERSION_TAG_EDITORIAL_RELATION_CANNOT_CHECK",
        "EXACT_TAG_TO_IMMUTABLE_COMMIT_CANNOT_CHECK",
        "EXACT_ARCHIVE_SOFTWARE_RIGHTS_CANNOT_CHECK_OR_NOT_ACCEPTED",
        "ARCHIVE_TO_COMMIT_AUTHENTICATED_IDENTITY_CANNOT_CHECK",
        "EXACT_COMMIT_SOFTWARE_RIGHTS_CANNOT_CHECK_OR_NOT_ACCEPTED",
        "PUBLIC_TRANSPORT_CANNOT_CHECK",
    ]
    return next((cause for cause in order if cause in causes), "UNRESOLVED_IDENTITY_CANNOT_CHECK")


def main() -> None:
    started_at = now()
    protocol = json.loads((HERE / "PROTOCOL_V7.json").read_text())
    freeze = json.loads((HERE / "PROTOCOL_FREEZE_RECEIPT_V7.json").read_text())
    inputs = load_jsonl(INPUT)
    v6_rows = {row["frozen_index"]: row for row in load_jsonl(V6 / "BRIDGE_REPAIR_ROWS_V6.jsonl")}
    if freeze.get("protocol_sha256") != sha_file(HERE / "PROTOCOL_V7.json"):
        raise SystemExit("frozen protocol hash mismatch")
    if freeze.get("input_sha256") != sha_file(INPUT):
        raise SystemExit("frozen input hash mismatch")
    if len(inputs) != 24:
        raise SystemExit("V7 input is not exactly 24 identities")

    output: list[dict[str, Any]] = []
    for position, row in enumerate(inputs, 1):
        index = row["frozen_index"]
        publication_doi = norm_doi(row["publication_doi"])
        issue_number = int(publication_doi.rsplit(".", 1)[-1])

        crossref_obj, crossref_request = json_fetch(
            f"https://api.crossref.org/works/{urllib.parse.quote(publication_doi, safe='/')}"
        )
        crossref_message = (crossref_obj or {}).get("message") if isinstance(crossref_obj, dict) else {}
        crossref_selected = crossref_relation(crossref_message or {}, row)

        issue, issue_request = json_fetch(
            f"https://api.github.com/repos/openjournals/joss-reviews/issues/{issue_number}", github=True
        )
        comments: list[dict[str, Any]] = []
        comments_requests: list[dict[str, Any]] = []
        for page in range(1, 6):
            page_obj, page_request = json_fetch(
                f"https://api.github.com/repos/openjournals/joss-reviews/issues/{issue_number}/comments?per_page=100&page={page}",
                github=True,
            )
            comments_requests.append({"page": page, **page_request})
            if not isinstance(page_obj, list):
                break
            comments.extend(page_obj)
            if len(page_obj) < 100:
                break
        review = extract_review_evidence(issue or {}, comments, row) if isinstance(issue, dict) else {}
        archive = fetch_archive(row, review.get("version_field"))

        candidate_values = version_candidates(review.get("version_field"))
        for tag in review.get("matching_release_tags") or []:
            if tag not in candidate_values:
                candidate_values.append(tag)
        tag_attempts: list[dict[str, Any]] = []
        for tag in candidate_values:
            if norm_version(tag) != norm_version(review.get("version_field")):
                continue
            commit, receipts = resolve_tag(row["repository"], tag)
            tag_attempts.append({
                "candidate_kind": "JOSS_FINAL_VERSION_OR_EXACT_RELEASE_TAG",
                "tag": tag,
                "commit_sha": commit,
                "paired_with_exact_archive_in_review_comment": tag in set(review.get("paired_exact_version_release_tags") or []),
                "appears_in_exact_review_release_url": tag in set(review.get("matching_release_tags") or []),
                "requests": receipts,
            })

        resolved = [attempt for attempt in tag_attempts if attempt.get("commit_sha")]
        paired = [attempt for attempt in resolved if attempt.get("paired_with_exact_archive_in_review_comment")]
        exact_named = [attempt for attempt in resolved if attempt.get("tag") == review.get("version_field")]
        selected_tag = None
        selection_ambiguous = False
        preferred = paired or exact_named or resolved
        if preferred:
            commits = {attempt["commit_sha"] for attempt in preferred}
            if len(commits) == 1:
                selected_tag = preferred[0]
            else:
                selection_ambiguous = True

        commit_spdx = None
        commit_license_request: dict[str, Any] | None = None
        if selected_tag:
            commit_spdx, commit_license_request = license_at(row["repository"], selected_tag["commit_sha"])

        v6_row = v6_rows[index]
        identity_evidence = evaluate_archive_commit_identity(
            row, archive, selected_tag, v6_row
        )

        exact_publication_relation = all([
            crossref_selected.get("exact_publication_doi_match"),
            crossref_selected.get("exact_archive_doi_referenced"),
            crossref_selected.get("exact_review_issue_referenced"),
            review.get("issue_number") == issue_number,
        ])
        exact_archive_version = bool(archive.get("exact_archive_version_relation"))
        same_repository = bool(review.get("exact_repository_match"))
        exact_editorial_relation = all([
            exact_publication_relation,
            review.get("exact_archive_field_match"),
            review.get("exact_repository_match"),
            review.get("version_field"),
        ])
        exact_tag_commit = bool(selected_tag and not selection_ambiguous)
        archive_commit_identity = identity_evidence.get("status") == "PASS"
        archive_rights = bool(archive.get("accepted_archive_spdx"))
        commit_rights = bool(commit_spdx)
        transport_pass = all([
            request_pass(crossref_request), request_pass(issue_request),
            bool(comments_requests) and all(request_pass(value) for value in comments_requests),
            archive.get("transport_pass"),
            not exact_tag_commit or all(request_pass(value) for value in (selected_tag.get("requests") or [])),
            not exact_tag_commit or (commit_license_request and request_pass(commit_license_request)),
        ])
        gates = {
            "exact_frozen_publication_doi": exact_publication_relation,
            "exact_frozen_archive_version_doi_relation": exact_archive_version,
            "same_frozen_repository": same_repository,
            "exact_joss_archive_version_tag_editorial_relation": exact_editorial_relation,
            "exact_source_native_tag_or_release_to_full_commit": exact_tag_commit,
            "archive_to_commit_content_or_authenticated_origin_identity": archive_commit_identity,
            "accepted_archive_software_rights": archive_rights,
            "accepted_commit_software_rights": commit_rights,
            "public_transport_receipted": transport_pass,
        }
        resolved_v7 = all(gates.values())
        causes = []
        mapping = {
            "exact_frozen_publication_doi": "EXACT_PUBLICATION_DOI_RELATION_CANNOT_CHECK",
            "exact_frozen_archive_version_doi_relation": "EXACT_ARCHIVE_VERSION_DOI_RELATION_CANNOT_CHECK",
            "same_frozen_repository": "SAME_FROZEN_REPOSITORY_CANNOT_CHECK",
            "exact_joss_archive_version_tag_editorial_relation": "EXACT_JOSS_ARCHIVE_VERSION_TAG_EDITORIAL_RELATION_CANNOT_CHECK",
            "exact_source_native_tag_or_release_to_full_commit": "EXACT_TAG_TO_IMMUTABLE_COMMIT_CANNOT_CHECK",
            "archive_to_commit_content_or_authenticated_origin_identity": "ARCHIVE_TO_COMMIT_AUTHENTICATED_IDENTITY_CANNOT_CHECK",
            "accepted_archive_software_rights": "EXACT_ARCHIVE_SOFTWARE_RIGHTS_CANNOT_CHECK_OR_NOT_ACCEPTED",
            "accepted_commit_software_rights": "EXACT_COMMIT_SOFTWARE_RIGHTS_CANNOT_CHECK_OR_NOT_ACCEPTED",
            "public_transport_receipted": "PUBLIC_TRANSPORT_CANNOT_CHECK",
        }
        for gate, passed in gates.items():
            if not passed:
                causes.append(mapping[gate])

        output.append({
            "schema_version": "orion.p4.targeted-identity.row.v7",
            "frozen_index": index,
            "publication_doi": row["publication_doi"],
            "archive_doi": row["archive_doi"],
            "repository": row["repository"],
            "domain": row["domain"],
            "v6_failure_causes": row["v6_failure_causes"],
            "v6_prior_content_identity": v6_row.get("accepted_content_identity"),
            "crossref_request": crossref_request,
            "crossref_relation": crossref_selected,
            "joss_review_issue_request": issue_request,
            "joss_review_comment_requests": comments_requests,
            "joss_review_evidence": review,
            "archive_provider_evidence": archive,
            "tag_resolution_attempts": tag_attempts,
            "tag_selection_ambiguous": selection_ambiguous,
            "accepted_exact_tag_commit": {
                "tag": selected_tag["tag"], "commit_sha": selected_tag["commit_sha"],
                "selection_basis": (
                    "EXACT_ARCHIVE_AND_RELEASE_PAIRED_IN_JOSS_REVIEW_COMMENT"
                    if selected_tag.get("paired_with_exact_archive_in_review_comment")
                    else "JOSS_FINAL_VERSION_FIELD_EXACT_TAG"
                ),
            } if selected_tag else None,
            "commit_spdx": commit_spdx,
            "commit_license_request": commit_license_request,
            "archive_commit_identity_evidence": identity_evidence,
            "accepted_identity_method": identity_evidence.get("accepted_method"),
            "gates": gates,
            "v7_same_identity_resolution": resolved_v7,
            "v7_failure_causes": causes,
            "v7_primary_failure": None if resolved_v7 else primary_failure(causes),
            "author_lineage_independence": "CANNOT_CHECK_EXTERNAL_OUTCOME_BLIND_ADJUDICATION_REQUIRED",
            "natural_pair_eligibility": "CANNOT_CHECK_EXTERNAL_OUTCOME_BLIND_ADJUDICATION_REQUIRED",
            "counts_as_unit": 1,
        })
        print(
            f"[{position:02d}/24] index={index} resolved={resolved_v7} "
            f"archive_version={exact_archive_version} editorial={exact_editorial_relation} "
            f"tag={selected_tag['tag'] if selected_tag else '-'} identity={identity_evidence.get('accepted_method') or '-'} "
            f"rights={archive.get('accepted_archive_spdx')}/{commit_spdx}",
            flush=True,
        )

    ROWS.write_text("".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in output))
    repaired = [row for row in output if row["v7_same_identity_resolution"]]
    unresolved = [row for row in output if not row["v7_same_identity_resolution"]]
    by_domain = defaultdict(lambda: {"entering_v7": 0, "v7_repairs": 0, "remaining_unresolved": 0})
    for row in output:
        by_domain[row["domain"]]["entering_v7"] += 1
        by_domain[row["domain"]]["v7_repairs" if row["v7_same_identity_resolution"] else "remaining_unresolved"] += 1
    primary_counts = Counter(row["v7_primary_failure"] for row in unresolved)
    overlapping_counts = Counter(cause for row in unresolved for cause in row["v7_failure_causes"])

    receipt = {
        "schema_version": "orion.p4.targeted-identity.harvest-receipt.v7",
        "created_at": now(), "started_at": started_at, "status": "PASS",
        "artifact": str(ROWS), "artifact_sha256": sha_file(ROWS),
        "protocol_sha256": sha_file(HERE / "PROTOCOL_V7.json"),
        "input_sha256": sha_file(INPUT),
        "runner_sha256": sha_file(Path(__file__)),
        "counts": {
            "frozen_input_identities": len(output), "same_identity_repairs": len(repaired),
            "remaining_unresolved": len(unresolved),
            "exact_archive_version_doi_relations": sum(row["gates"]["exact_frozen_archive_version_doi_relation"] for row in output),
            "exact_editorial_archive_version_tag_relations": sum(row["gates"]["exact_joss_archive_version_tag_editorial_relation"] for row in output),
            "exact_tag_commits": sum(row["gates"]["exact_source_native_tag_or_release_to_full_commit"] for row in output),
            "accepted_archive_rights": sum(row["gates"]["accepted_archive_software_rights"] for row in output),
            "accepted_commit_rights": sum(row["gates"]["accepted_commit_software_rights"] for row in output),
            "new_or_replacement_publication_dois": 0,
            "files_versions_tags_commits_requests_counted_as_units": 0,
            "author_lineage_adjudications": 0, "natural_pair_adjudications": 0,
            "eligible_natural_pairs": 0,
        },
        "github_authentication_available": bool(TOKEN), "token_retained": False,
        "download_payloads_retained": False, "protected_or_system_outcomes_accessed": False,
    }
    dump_json(HERE / "HARVEST_RECEIPT_V7.json", receipt)

    result = {
        "schema_version": "orion.p4.targeted-identity.result.v7",
        "created_at": now(),
        "authority": protocol["authority"],
        "status": "V7_TARGETED_IDENTITY_RESOLUTION_COMPLETE",
        "programme_terminal": "P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK",
        "counts": {
            "v6_exact_joss_bridges": 56,
            "v6_unresolved_entering_v7": 24,
            "v7_same_identity_repairs": len(repaired),
            "v7_remaining_unresolved": len(unresolved),
            "final_exact_joss_bridges": 56 + len(repaired),
            "same_frozen_publication_dois": 200,
            "v4_provider_qualified_frozen": 80,
            "new_or_replacement_publication_dois": 0,
            "files_versions_tags_commits_requests_counted_as_units": 0,
            "author_lineage_adjudications": 0,
            "natural_pair_adjudications": 0,
            "eligible_natural_pairs": 0,
        },
        "by_domain": dict(sorted(by_domain.items())),
        "repaired_identities": [
            {
                "frozen_index": row["frozen_index"], "publication_doi": row["publication_doi"],
                "archive_doi": row["archive_doi"], "repository": row["repository"],
                "selected_archive_version_doi": row["archive_provider_evidence"].get("selected_archive_doi"),
                "tag": row["accepted_exact_tag_commit"]["tag"],
                "commit_sha": row["accepted_exact_tag_commit"]["commit_sha"],
                "archive_spdx": row["archive_provider_evidence"]["accepted_archive_spdx"],
                "commit_spdx": row["commit_spdx"], "identity_method": row["accepted_identity_method"],
            }
            for row in repaired
        ],
        "unresolved_identities": [
            {
                "frozen_index": row["frozen_index"], "publication_doi": row["publication_doi"],
                "archive_doi": row["archive_doi"], "repository": row["repository"],
                "domain": row["domain"], "primary_failure": row["v7_primary_failure"],
                "overlapping_failures": row["v7_failure_causes"],
            }
            for row in unresolved
        ],
        "primary_mutually_exclusive_counts": dict(sorted(primary_counts.items())),
        "overlapping_gate_counts": dict(sorted(overlapping_counts.items())),
        "preserved_boundaries": protocol["preserved_boundaries"],
        "artifact_hashes": {
            "protocol": sha_file(HERE / "PROTOCOL_V7.json"),
            "protocol_freeze": sha_file(HERE / "PROTOCOL_FREEZE_RECEIPT_V7.json"),
            "input": sha_file(INPUT), "runner": sha_file(Path(__file__)),
            "rows": sha_file(ROWS), "harvest_receipt": sha_file(HERE / "HARVEST_RECEIPT_V7.json"),
            "v6_rows": sha_file(V6 / "BRIDGE_REPAIR_ROWS_V6.jsonl"),
            "v6_result": sha_file(V6 / "RESULT_V6.json"),
        },
    }
    dump_json(HERE / "RESULT_V7.json", result)

    ledger_entries = []
    for cause, count in sorted(primary_counts.items()):
        if cause == "EXACT_ARCHIVE_VERSION_DOI_RELATION_CANNOT_CHECK":
            identity = "EXACT_ARCHIVE_VERSION_IDENTITY"
            observed = f"{count}/{len(unresolved)} remaining identities use a concept or mutable latest DOI rather than the exact immutable version DOI."
            residual = "JOSS metadata can bind a publication to the cited DOI, but cannot convert that concept DOI into a version DOI."
            discriminator = "Obtain an immutable provider version relation for the same frozen DOI identity; do not substitute a later version DOI."
        elif cause == "EXACT_ARCHIVE_SOFTWARE_RIGHTS_CANNOT_CHECK_OR_NOT_ACCEPTED":
            identity = "EXACT_ARCHIVE_SOFTWARE_RIGHTS"
            observed = f"{count}/{len(unresolved)} remaining identities have no accepted software license bound at the exact archive record."
            residual = "A publication/editorial tag relation does not transfer repository license rights onto an archive carrying a non-software or unaccepted license."
            discriminator = "Obtain source-native accepted software rights on the same archive DOI, or retain CANNOT_CHECK."
        else:
            identity = cause.removesuffix("_CANNOT_CHECK")
            observed = f"{count}/{len(unresolved)} remaining identities fail this primary gate."
            residual = "The V7 exact publication/archive/tag/commit chain is incomplete at this gate."
            discriminator = "Seek a source-native authenticated edge for the same frozen identity; retain CANNOT_CHECK otherwise."
        ledger_entries.append({
            "identity": identity, "cause": cause, "observed": observed,
            "residual": residual, "next_discriminator": discriminator,
        })
    ledger = {
        "schema_version": "orion.p4.targeted-identity.negative-result-ledger.v7",
        "created_at": now(), "terminal": "OPEN_NO_SOLUTION_CERTIFICATE",
        "preserved_programme_terminal": "P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK",
        "unresolved_identity_count": len(unresolved),
        "primary_mutually_exclusive_counts": dict(sorted(primary_counts.items())),
        "overlapping_gate_counts": dict(sorted(overlapping_counts.items())),
        "by_domain": dict(sorted(by_domain.items())),
        "entries": ledger_entries,
        "row_level_unresolved": result["unresolved_identities"],
        "research_boundary": "Each negative is a same-identity research topic; none is relabelled positive and no replacement publication is introduced.",
    }
    dump_json(HERE / "NEGATIVE_RESULT_LEDGER_V7.json", ledger)

    results_md = [
        "# P4 V7 Targeted Unresolved-Identity Result", "",
        "## Outcome", "",
        f"- Frozen unresolved identities revisited: **24/24**",
        f"- New same-identity repairs: **{len(repaired)}**",
        f"- Exact JOSS bridges after V7: **{56 + len(repaired)}/80**",
        f"- Remaining unresolved: **{len(unresolved)}**",
        "- Replacement publications: **0**",
        "- Files, versions, tags, commits, or requests counted as units: **0**",
        "- Author-lineage adjudications: **0**",
        "- Natural-pair adjudications / eligible pairs: **0 / 0**", "",
        "## Scientific discriminator", "",
        "V7 adds the exact Crossref-to-JOSS-review relation and uses the frozen JOSS version to select a unique publication-time child from provider version history. A positive row also requires an exact source-native tag resolved to a 40-hex commit, archive-authenticated content/origin identity (provider related identifier, SWH tree identity, normalized manifest equality, exact embedded revision, or exact release-asset byte equality), provider-bound checksums, and accepted rights at both archive and commit. Editorial assertion alone never closes the identity gate.", "",
        "## Primary unresolved causes", "",
    ]
    for cause, count in sorted(primary_counts.items()):
        results_md.append(f"- `{cause}`: **{count}**")
    results_md += ["", "## Boundary", "", "The packet is development transport evidence, not natural-pair or author-lineage adjudication. The programme terminal remains `P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK`.", ""]
    (HERE / "RESULTS_V7.md").write_text("\n".join(results_md))

    handoff = [
        "# P4 V7 Handoff", "", "## Frozen scope", "",
        "This packet revisits exactly the 24 unresolved V6 identities. It adds no publication, archive, repository, file, version, tag, commit, request, lineage decision, or natural pair as a counting unit.", "",
        "## Result", "",
        f"V7 repairs **{len(repaired)}** identities and leaves **{len(unresolved)}** unresolved. The cumulative exact JOSS bridge count is **{56 + len(repaired)}/80**.", "",
        "## What changed scientifically", "",
        "The new discriminator uses the final publication-native JOSS review workflow to identify the exact archive family and publication version, then enumerates provider version history rather than following current-latest redirects. Positives require an independent archive-authenticated edge to the immutable tag commit: provider related identifier, SWH tree equality, normalized content-manifest equality, an exact embedded revision marker, or exact release-asset bytes. Editorial assertion alone is not an identity bridge.", "",
        "## What remains closed", "",
        "- Concept or mutable-latest DOIs are not promoted to immutable version DOIs.",
        "- Editorial evidence does not override missing or unaccepted archive software rights.",
        "- Author-lineage independence and natural-pair eligibility remain externally unadjudicated.",
        "- No result here is a protected-outcome, performance, or top-tier-publication claim.", "",
        "## Next discriminator", "",
        "For every remaining row, follow the row-level negative ledger. Work only on the same frozen identity. A later provider version, replacement publication, repository proxy, filename resemblance, or current-latest tag cannot repair a frozen row.", "",
    ]
    (HERE / "HANDOFF_V7.md").write_text("\n".join(handoff))

    print(f"wrote {ROWS.name}: repaired={len(repaired)} unresolved={len(unresolved)}", flush=True)


if __name__ == "__main__":
    main()
