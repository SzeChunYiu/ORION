#!/usr/bin/env python3
"""Build an outcome-blind metadata snapshot for candidate naturalistic sources.

This lane deliberately retrieves only repository identity, one pre-cutoff commit
identity, and the licence object at that exact commit.  It neither retrieves
issues/pull requests nor assigns scientific case labels, pair roles, protected
gold, revision classes, or outcomes.
"""

from __future__ import annotations

import base64
import datetime as dt
import hashlib
import json
import os
import pathlib
import urllib.error
import urllib.parse
import urllib.request


CUTOFF = "2025-12-31T23:59:59Z"
ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "SOURCE_METADATA_SNAPSHOT_V1.json"
LICENCE_DIR = ROOT / "raw" / "licences"

REPOSITORIES = (
    ("BIOMEDICAL_CLINICAL", "scverse/scanpy"),
    ("BIOMEDICAL_CLINICAL", "biopython/biopython"),
    ("BIOMEDICAL_CLINICAL", "nipy/nibabel"),
    ("EARTH_ENVIRONMENTAL", "pydata/xarray"),
    ("EARTH_ENVIRONMENTAL", "SciTools/cartopy"),
    ("EARTH_ENVIRONMENTAL", "Unidata/netcdf4-python"),
    ("COMPUTATIONAL_SCIENTIFIC_SOFTWARE", "numpy/numpy"),
    ("COMPUTATIONAL_SCIENTIFIC_SOFTWARE", "scipy/scipy"),
    ("COMPUTATIONAL_SCIENTIFIC_SOFTWARE", "scikit-learn/scikit-learn"),
    ("PHYSICAL_ENGINEERING", "astropy/astropy"),
    ("PHYSICAL_ENGINEERING", "qutip/qutip"),
    ("PHYSICAL_ENGINEERING", "scikit-rf/scikit-rf"),
)


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def fetch_json(url: str) -> tuple[dict | list, dict]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "orion-outcome-blind-metadata-audit",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read()
            receipt = {
                "request_url": url,
                "final_url": response.geturl(),
                "http_status": response.status,
                "etag": response.headers.get("ETag"),
                "last_modified": response.headers.get("Last-Modified"),
                "response_sha256": sha256(body),
                "response_bytes": len(body),
            }
    except urllib.error.HTTPError as exc:
        body = exc.read()
        raise RuntimeError(f"HTTP {exc.code} for {url}: {body[:500]!r}") from exc
    return json.loads(body), receipt


def fetch_bytes(url: str) -> tuple[bytes, dict]:
    request = urllib.request.Request(
        url, headers={"User-Agent": "orion-outcome-blind-metadata-audit"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read()
        receipt = {
            "request_url": url,
            "final_url": response.geturl(),
            "http_status": response.status,
            "etag": response.headers.get("ETag"),
            "last_modified": response.headers.get("Last-Modified"),
            "response_sha256": sha256(body),
            "response_bytes": len(body),
        }
    return body, receipt


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def main() -> int:
    captured_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    LICENCE_DIR.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    errors: list[dict] = []

    # A bounded retry can reuse already archived metadata records and fetch only
    # previously missing families.  This protects the unauthenticated provider
    # rate budget without changing any selected record.
    if os.environ.get("REUSE_EXISTING") == "1" and OUT.exists():
        prior = json.loads(OUT.read_text(encoding="utf-8"))
        records = list(prior.get("records", []))
    existing = {record["official_repository_identity"] for record in records}

    for domain, repository in REPOSITORIES:
        if repository in existing:
            continue
        owner, name = repository.split("/", 1)
        api_base = f"https://api.github.com/repos/{owner}/{name}"
        try:
            repo, repo_receipt = fetch_json(api_base)
            query = urllib.parse.urlencode({"until": CUTOFF, "per_page": 1})
            commits, commit_receipt = fetch_json(f"{api_base}/commits?{query}")
            if not isinstance(commits, list) or not commits:
                raise RuntimeError(f"no commit at or before {CUTOFF}")
            commit = commits[0]
            revision = str(commit["sha"])
            licence, licence_receipt = fetch_json(f"{api_base}/license?ref={revision}")
            licence_bytes = base64.b64decode(licence["content"], validate=False)
            api_download_url = licence["download_url"]
            downloaded_licence, download_receipt = fetch_bytes(api_download_url)
            resolved_download_url = api_download_url
            # GitHub's licence API dereferences repository symlinks in `content`
            # but may return a raw URL for the symlink blob.  Resolve only a
            # single relative filename pointer and require byte equality.
            if downloaded_licence != licence_bytes:
                pointer = downloaded_licence.decode("utf-8").strip()
                if not pointer or "/" in pointer or "\\" in pointer:
                    raise RuntimeError("licence download differs from API content and is not a safe filename pointer")
                resolved_download_url = api_download_url.rsplit("/", 1)[0] + "/" + pointer
                downloaded_licence, download_receipt = fetch_bytes(resolved_download_url)
                if downloaded_licence != licence_bytes:
                    raise RuntimeError("resolved licence download differs from API licence content")
            safe_name = repository.replace("/", "__")
            licence_path = LICENCE_DIR / f"{safe_name}__{revision[:12]}.txt"
            licence_path.write_bytes(licence_bytes)

            commit_date = commit["commit"]["committer"]["date"]
            record = {
                "candidate_source_family_id": f"github:{repository.casefold()}",
                "protected_domain_candidate": domain,
                "provider": "GitHub",
                "official_repository_identity": repository,
                "primary_source_url": repo["html_url"],
                "api_identity_url": api_base,
                "revision_cutoff_utc": CUTOFF,
                "selected_revision_sha": revision,
                "selected_revision_committer_date": commit_date,
                "selected_revision_url": f"{repo['html_url']}/commit/{revision}",
                "licence": {
                    "spdx_id_at_selected_revision": licence["license"]["spdx_id"],
                    "name_at_selected_revision": licence["license"]["name"],
                    "path_at_selected_revision": licence["path"],
                    "html_url_at_selected_revision": licence["html_url"],
                    "api_reported_download_url_at_selected_revision": api_download_url,
                    "download_url_at_selected_revision": resolved_download_url,
                    "text_sha256": sha256(licence_bytes),
                    "text_bytes": len(licence_bytes),
                    "archived_local_path": str(licence_path.relative_to(ROOT)),
                },
                "http_receipts": {
                    "repository_identity": repo_receipt,
                    "pre_cutoff_revision_query": commit_receipt,
                    "licence_at_selected_revision": licence_receipt,
                    "licence_download_at_selected_revision": download_receipt,
                },
                "study_fields_intentionally_not_accessed": [
                    "issues",
                    "pull_requests",
                    "discussions",
                    "scientific_case_text",
                    "adverse_or_control_pair_role",
                    "causal_family",
                    "revision_class",
                    "protected_gold",
                    "candidate_or_comparator_output",
                    "evaluator_disposition",
                    "fresh_transfer_outcome",
                ],
            }
            record["record_sha256"] = sha256(canonical_bytes(record))
            records.append(record)
        except Exception as exc:  # fail visibly and retain partial evidence
            errors.append({"repository": repository, "error": str(exc)})

    domain_counts: dict[str, int] = {}
    licence_counts: dict[str, int] = {}
    for record in records:
        domain = record["protected_domain_candidate"]
        spdx = record["licence"]["spdx_id_at_selected_revision"]
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        licence_counts[spdx] = licence_counts.get(spdx, 0) + 1

    snapshot = {
        "schema_version": "orion.shared-naturalistic-source-metadata.v1",
        "captured_at_utc": captured_at,
        "cutoff_utc": CUTOFF,
        "purpose": "outcome-blind candidate source-family identity, revision, URL, and licence preflight",
        "authority": "SOURCE_METADATA_ONLY__NOT_A_CASE_PANEL__NOT_SCIENTIFIC_EVIDENCE",
        "outcomes_accessed": False,
        "protected_case_fields_accessed": False,
        "repository_provider": "api.github.com",
        "provider_api_version": "2022-11-28",
        "records_requested": len(REPOSITORIES),
        "records_verified": len(records),
        "errors": errors,
        "domain_counts": dict(sorted(domain_counts.items())),
        "licence_spdx_counts": dict(sorted(licence_counts.items())),
        "records": records,
        "explicit_nonclaims": [
            "No issue or pull-request family was acquired or adjudicated.",
            "No record was shown to contain an adverse/control pair.",
            "No record was assigned a causal family, coordinate opportunity, unidentifiability mechanism, or revision class.",
            "No source-disjoint primary or replication frame was completed.",
            "No independent protected gold, evaluator, comparator, scorer, host, split, or verifier custody was bound.",
            "Repository code licensing does not by itself license third-party issue text, linked papers, datasets, or attachments.",
        ],
    }
    snapshot["snapshot_payload_sha256"] = sha256(canonical_bytes(snapshot))
    OUT.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(OUT),
                "records_verified": len(records),
                "errors": errors,
                "snapshot_payload_sha256": snapshot["snapshot_payload_sha256"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
