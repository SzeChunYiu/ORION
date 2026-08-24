#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"
EVIDENCE.mkdir(exist_ok=True)
PROTOCOL = json.loads((ROOT / "PROTOCOL_V10.json").read_text())
UA = "ORION-P4-exact-edge-authority-v10/1.0 (public research evidence audit)"


def capture(url: str, slug: str, accept: str = "application/json") -> dict:
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    request = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept": accept},
    )
    body = b""
    status = None
    final_url = url
    headers: dict[str, str] = {}
    error = None
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            status = response.status
            final_url = response.geturl()
            headers = dict(response.headers)
            body = response.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        final_url = exc.geturl()
        headers = dict(exc.headers)
        body = exc.read()
        error = f"HTTPError:{exc.code}"
    except Exception as exc:
        error = f"{type(exc).__name__}:{exc}"

    body_path = EVIDENCE / f"{slug}.body"
    body_path.write_bytes(body)
    receipt = {
        "url": url,
        "started_at": started,
        "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": status,
        "final_url": final_url,
        "headers": {
            key: value
            for key, value in headers.items()
            if key.lower()
            in {
                "content-type",
                "content-length",
                "etag",
                "last-modified",
                "link",
                "x-ratelimit-limit",
                "x-ratelimit-remaining",
                "x-ratelimit-reset",
            }
        },
        "body_path": str(body_path.relative_to(ROOT)),
        "body_bytes": len(body),
        "body_sha256": hashlib.sha256(body).hexdigest(),
        "error": error,
    }
    (EVIDENCE / f"{slug}.receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    time.sleep(0.20)
    return receipt


rows = []
for target in PROTOCOL["targets"]:
    index = target["frozen_index"]
    repository = target["repository"]
    record = target["archive_doi"].rsplit(".", 1)[-1]
    requests = []

    requests.append(capture(f"https://zenodo.org/api/records/{record}", f"{index}_zenodo_record"))
    requests.append(capture(f"https://zenodo.org/api/records/{record}/versions", f"{index}_zenodo_versions"))
    requests.append(capture(f"https://api.github.com/repos/{repository}", f"{index}_github_repository", "application/vnd.github+json"))
    requests.append(capture(f"https://api.github.com/repos/{repository}/commits/{target.get('accepted_commit', target.get('discovered_commit'))}", f"{index}_github_exact_commit", "application/vnd.github+json"))

    tags = [target["publication_version"]]
    if target.get("accepted_source_tag"):
        tags.append(target["accepted_source_tag"])
    for tag in list(tags):
        if tag.startswith("v"):
            tags.append(tag[1:])
        else:
            tags.append("v" + tag)
    tags = list(dict.fromkeys(tags))
    for tag_number, tag in enumerate(tags):
        encoded = urllib.parse.quote(tag, safe="")
        requests.append(capture(f"https://api.github.com/repos/{repository}/git/ref/tags/{encoded}", f"{index}_github_ref_{tag_number}", "application/vnd.github+json"))
        requests.append(capture(f"https://api.github.com/repos/{repository}/releases/tags/{encoded}", f"{index}_github_release_{tag_number}", "application/vnd.github+json"))

    if index in {133, 185}:
        filename = urllib.parse.quote(target["artifact_filename"], safe="")
        package = "woodtapper" if index == 133 else "disruption-py"
        version = "0.0.13" if index == 133 else "0.14.0"
        digest = "sha256:" + target["artifact_sha256"]
        requests.append(capture(f"https://pypi.org/integrity/{package}/{version}/{filename}/provenance", f"{index}_pypi_integrity"))
        requests.append(capture(f"https://api.github.com/repos/{repository}/attestations/{digest}", f"{index}_github_artifact_attestation", "application/vnd.github+json"))
        requests.append(capture(f"https://pypi.org/pypi/{package}/{version}/json", f"{index}_pypi_json"))

    if index == 199:
        snapshot = target["source_origin_snapshot"]
        revision = target["discovered_commit"]
        directory = target["archive_inner_directory_swhid"].rsplit(":", 1)[-1]
        origin = urllib.parse.quote(f"https://github.com/{repository}", safe="")
        requests.append(capture(f"https://archive.softwareheritage.org/api/1/origin/{origin}/visits/", "199_swh_origin_visits"))
        requests.append(capture(f"https://archive.softwareheritage.org/api/1/snapshot/{snapshot}/", "199_swh_origin_snapshot"))
        requests.append(capture(f"https://archive.softwareheritage.org/api/1/revision/{revision}/", "199_swh_exact_revision"))
        requests.append(capture(f"https://archive.softwareheritage.org/api/1/directory/{directory}/", "199_swh_exact_directory"))
        requests.append(capture("https://archive.softwareheritage.org/api/1/content/sha1_git:a2bc6f7644e165ad7c9b0c6215ba20bdbe634728/raw/", "199_swh_exact_license", "text/plain"))

    issue_number = str(int(target["publication_doi"].rsplit(".", 1)[-1]))
    requests.append(capture(f"https://api.github.com/repos/openjournals/joss-reviews/issues/{issue_number}", f"{index}_joss_issue", "application/vnd.github+json"))
    requests.append(capture(f"https://api.github.com/repos/openjournals/joss-reviews/issues/{issue_number}/comments?per_page=100&page=1", f"{index}_joss_comments", "application/vnd.github+json"))

    rows.append({"frozen_index": index, "repository": repository, "requests": requests})

receipt = {
    "schema_version": "orion.p4.exact-edge-lineage-authority.v10.provider-probe-receipt",
    "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "protocol_sha256": hashlib.sha256((ROOT / "PROTOCOL_V10.json").read_bytes()).hexdigest(),
    "rows": rows,
}
(ROOT / "PROVIDER_AUTHORITY_PROBE_RECEIPT_V10.json").write_text(
    json.dumps(receipt, indent=2, sort_keys=True) + "\n"
)

statuses: dict[str, int] = {}
for row in rows:
    for request in row["requests"]:
        key = str(request["status"])
        statuses[key] = statuses.get(key, 0) + 1
print(json.dumps({"targets": len(rows), "requests": sum(len(row["requests"]) for row in rows), "statuses": statuses}, sort_keys=True))
