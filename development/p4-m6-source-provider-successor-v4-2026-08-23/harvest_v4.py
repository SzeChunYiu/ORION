#!/usr/bin/env python3
"""Bounded public-metadata harvest for the frozen P4 M6 V4 protocol."""

from __future__ import annotations

import concurrent.futures
import datetime as dt
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parent
PROTOCOL = json.loads((ROOT / "PROTOCOL_V4.json").read_text())
USER_AGENT = "OrionP4SourceAudit/4.0 (public-metadata-feasibility)"
ACCEPTED = set(PROTOCOL["strict_candidate_unit"]["accepted_spdx"])
LEXICON = PROTOCOL["domain_lexicon"]


def canonical_json_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_bytes(json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False).encode() + b"\n")


def http_get_json(url: str, timeout: int = 90) -> tuple[object, dict]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        body = response.read()
        meta = {
            "url": url,
            "http_status": response.status,
            "content_type": response.headers.get("Content-Type"),
            "body_sha256": sha256(body),
            "body_bytes": len(body),
        }
    return json.loads(body), meta


class AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.anchors: list[dict] = []
        self.current: dict | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        fields = {k.lower(): v for k, v in attrs}
        self.current = {"href": fields.get("href") or "", "title": fields.get("title") or "", "text": ""}

    def handle_data(self, data: str) -> None:
        if self.current is not None:
            self.current["text"] += data

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self.current is not None:
            self.current["text"] = " ".join(self.current["text"].split())
            self.anchors.append(self.current)
            self.current = None


def fetch_joss_relation(doi: str) -> dict:
    url = f"https://joss.theoj.org/papers/{doi.lower()}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=45) as response:
        body = response.read()
        status = response.status
        content_type = response.headers.get("Content-Type")
    parser = AnchorParser()
    parser.feed(body.decode("utf-8", "replace"))
    candidates = []
    for a in parser.anchors:
        href = html.unescape(a["href"]).rstrip("/")
        m = re.fullmatch(r"https://github\.com/([^/]+)/([^/#?]+)", href, re.I)
        if not m:
            continue
        owner, repo = m.group(1), re.sub(r"\.git$", "", m.group(2), flags=re.I)
        if owner.casefold() == "openjournals":
            continue
        candidates.append({**a, "href": href, "owner": owner, "repo": repo})
    labelled = [a for a in candidates if "software" in (a["title"] + " " + a["text"]).casefold() or "repository" in (a["title"] + " " + a["text"]).casefold()]
    selected = labelled[0] if len(labelled) == 1 else (candidates[0] if len(candidates) == 1 else None)
    return {
        "url": url,
        "http_status": status,
        "content_type": content_type,
        "body_sha256": sha256(body),
        "body_bytes": len(body),
        "github_repository_candidates": candidates,
        "labelled_candidate_count": len(labelled),
        "selected_relation": selected,
        "relation_status": "PASS" if selected else ("CANNOT_CHECK_MULTIPLE" if candidates else "CANNOT_CHECK_MISSING"),
    }


def gh_api(endpoint: str) -> tuple[dict | list | None, dict]:
    command = ["gh", "api", "-H", "Accept: application/vnd.github+json", "-H", "X-GitHub-Api-Version: 2022-11-28", endpoint]
    proc = subprocess.run(command, capture_output=True, timeout=45)
    stdout, stderr = proc.stdout, proc.stderr
    status_match = re.search(rb"HTTP (\d{3})", stderr)
    status = 200 if proc.returncode == 0 else (int(status_match.group(1)) if status_match else None)
    meta = {
        "endpoint": "https://api.github.com/" + endpoint,
        "returncode": proc.returncode,
        "http_status": status,
        "body_sha256": sha256(stdout),
        "body_bytes": len(stdout),
        "error": stderr.decode("utf-8", "replace").strip()[:400] or None,
    }
    if proc.returncode != 0:
        return None, meta
    return json.loads(stdout), meta


def resolve_tag(full_name: str, tag: str) -> dict:
    encoded = urllib.parse.quote(tag, safe="")
    data, meta = gh_api(f"repos/{full_name}/git/ref/tags/{encoded}")
    if not isinstance(data, dict):
        return {"status": "CANNOT_CHECK_TAG_REF", "requests": [meta]}
    obj = data.get("object") or {}
    requests = [meta]
    seen = set()
    while obj.get("type") == "tag" and obj.get("sha") not in seen:
        seen.add(obj.get("sha"))
        tag_data, tag_meta = gh_api(f"repos/{full_name}/git/tags/{obj.get('sha')}")
        requests.append(tag_meta)
        if not isinstance(tag_data, dict):
            return {"status": "CANNOT_CHECK_ANNOTATED_TAG", "requests": requests}
        obj = tag_data.get("object") or {}
    return {
        "status": "PASS" if obj.get("type") == "commit" and re.fullmatch(r"[0-9a-f]{40}", str(obj.get("sha") or "")) else "CANNOT_CHECK_NONCOMMIT_TAG",
        "commit_sha": obj.get("sha") if obj.get("type") == "commit" else None,
        "terminal_object_type": obj.get("type"),
        "requests": requests,
    }


def plain_text(value: object) -> str:
    text = " " if value is None else str(value)
    text = re.sub(r"<[^>]+>", " ", html.unescape(text))
    return " ".join(text.split())


def classify_domain(text: str) -> dict:
    folded = text.casefold()
    scores = {}
    matches = {}
    for domain in PROTOCOL["scope"]["domains"]:
        hits = sorted({token for token in LEXICON[domain] if token.casefold() in folded})
        scores[domain] = len(hits)
        matches[domain] = hits
    maximum = max(scores.values())
    winners = [d for d, score in scores.items() if score == maximum]
    if maximum == 0:
        status, assigned = "CANNOT_CHECK_DOMAIN_UNCLASSIFIED", None
    elif len(winners) != 1:
        status, assigned = "CANNOT_CHECK_DOMAIN_AMBIGUOUS", None
    else:
        status, assigned = "PASS", winners[0]
    return {"status": status, "assigned_domain": assigned, "scores": scores, "matched_tokens": matches}


def author_signature(item: dict) -> list[str]:
    values = []
    for author in item.get("author") or []:
        orcid = str(author.get("ORCID") or "").removeprefix("https://orcid.org/").casefold()
        name = " ".join([str(author.get("given") or ""), str(author.get("family") or "")]).strip().casefold()
        values.append("orcid:" + orcid if orcid else "name:" + re.sub(r"[^a-z0-9]+", "", name))
    return sorted(set(v for v in values if v not in {"name:", "orcid:"}))


def audit_item(index_item: tuple[int, dict]) -> dict:
    index, item = index_item
    doi = str(item.get("DOI") or "").lower()
    result = {
        "frozen_index": index,
        "publication_doi": doi,
        "publication_title": plain_text((item.get("title") or [""])[0]),
        "publication_abstract": plain_text(item.get("abstract")),
        "publication_authors": author_signature(item),
        "provider_family": "JOSS_GITHUB_RELEASE",
        "mechanism": "M6_ARTICLE_TO_CODE_RELEASE",
        "strict_eligible": False,
        "failure_causes": [],
    }
    try:
        relation = fetch_joss_relation(doi)
    except Exception as exc:
        result["joss_relation"] = {"status": "CANNOT_CHECK_TRANSPORT", "error": f"{type(exc).__name__}: {exc}"}
        result["failure_causes"].append("JOSS_RELATION_TRANSPORT_CANNOT_CHECK")
        return result
    result["joss_relation"] = relation
    selected = relation.get("selected_relation")
    if not selected:
        result["failure_causes"].append("JOSS_STRUCTURED_REPOSITORY_RELATION_CANNOT_CHECK")
        return result
    full_name = f"{selected['owner']}/{selected['repo']}"
    repo, repo_meta = gh_api(f"repos/{full_name}")
    result["github_repository_request"] = repo_meta
    if not isinstance(repo, dict):
        result["failure_causes"].append("GITHUB_REPOSITORY_TRANSPORT_CANNOT_CHECK")
        return result
    result["repository"] = {
        "id": repo.get("id"), "full_name": repo.get("full_name"), "html_url": repo.get("html_url"),
        "private": repo.get("private"), "visibility": repo.get("visibility"), "archived": repo.get("archived"),
        "disabled": repo.get("disabled"), "fork": repo.get("fork"), "owner_login": (repo.get("owner") or {}).get("login"),
        "owner_id": (repo.get("owner") or {}).get("id"), "owner_type": (repo.get("owner") or {}).get("type"),
        "description": repo.get("description"), "topics": repo.get("topics") or [], "default_branch": repo.get("default_branch"),
    }
    if repo.get("private") is not False or repo.get("visibility") != "public" or repo.get("archived") or repo.get("disabled"):
        result["failure_causes"].append("GITHUB_PUBLIC_ACTIVE_REPOSITORY_GATE_FAIL")
    release, release_meta = gh_api(f"repos/{full_name}/releases/latest")
    result["github_release_request"] = release_meta
    if not isinstance(release, dict):
        result["failure_causes"].append("GITHUB_LATEST_RELEASE_CANNOT_CHECK")
        return result
    tag = str(release.get("tag_name") or "")
    result["release"] = {
        "id": release.get("id"), "tag_name": tag, "name": release.get("name"), "draft": release.get("draft"),
        "prerelease": release.get("prerelease"), "published_at": release.get("published_at"),
        "tarball_url": release.get("tarball_url"), "zipball_url": release.get("zipball_url"),
        "html_url": release.get("html_url"), "asset_count": len(release.get("assets") or []),
    }
    if release.get("draft") or not tag or not str(release.get("tarball_url") or "").startswith("https://api.github.com/"):
        result["failure_causes"].append("GITHUB_RELEASE_IDENTITY_OR_TRANSPORT_FAIL")
    tag_resolution = resolve_tag(full_name, tag)
    result["tag_resolution"] = tag_resolution
    if tag_resolution.get("status") != "PASS":
        result["failure_causes"].append(tag_resolution.get("status") or "GITHUB_TAG_RESOLUTION_CANNOT_CHECK")
    encoded_tag = urllib.parse.quote(tag, safe="")
    license_data, license_meta = gh_api(f"repos/{full_name}/license?ref={encoded_tag}")
    result["github_license_request"] = license_meta
    if isinstance(license_data, dict):
        lic = license_data.get("license") or {}
        result["license_at_release"] = {
            "spdx_id": lic.get("spdx_id"), "name": lic.get("name"), "key": lic.get("key"),
            "license_blob_sha": license_data.get("sha"), "path": license_data.get("path"),
            "html_url": license_data.get("html_url"),
        }
    else:
        result["license_at_release"] = None
    spdx = ((result.get("license_at_release") or {}).get("spdx_id"))
    blob = ((result.get("license_at_release") or {}).get("license_blob_sha"))
    if spdx not in ACCEPTED or not re.fullmatch(r"[0-9a-f]{40}", str(blob or "")):
        result["failure_causes"].append("EXACT_RELEASE_LICENSE_GATE_FAIL")
    domain_text = " ".join([
        result["publication_title"], result["publication_abstract"], plain_text(repo.get("description")),
        " ".join(repo.get("topics") or []),
    ])
    result["domain_classification"] = classify_domain(domain_text)
    if result["domain_classification"]["status"] != "PASS":
        result["failure_causes"].append(result["domain_classification"]["status"])
    result["concept_identity"] = {
        "publication_doi": doi,
        "repository_full_name_casefolded": str(repo.get("full_name") or full_name).casefold(),
        "repository_id": repo.get("id"),
        "release_is_evidence_not_unit": True,
    }
    result["publication_release_version_alignment"] = "CANNOT_CHECK_UNLESS_JOSS_PAGE_EXPLICITLY_BINDS_RELEASE_TAG"
    result["author_lineage_independence"] = "CANNOT_CHECK_EXTERNAL_ADJUDICATION_REQUIRED"
    result["natural_pair_eligibility"] = "CANNOT_CHECK_EXTERNAL_ADJUDICATION_REQUIRED"
    result["strict_eligible"] = not result["failure_causes"]
    return result


def main() -> int:
    freeze = json.loads((ROOT / "PROTOCOL_FREEZE_RECEIPT_V4.json").read_text())
    if freeze.get("status") != "FROZEN_BEFORE_V4_METADATA_HARVEST":
        raise RuntimeError("missing valid pre-harvest freeze")
    query = PROTOCOL["provider_freeze"]["crossref_query"]
    params = {
        "filter": query["filter"], "sort": query["sort"], "order": query["order"],
        "rows": query["rows"], "cursor": query["cursor"],
    }
    url = query["endpoint"] + "?" + urllib.parse.urlencode(params)
    crossref, crossref_meta = http_get_json(url)
    write_json(ROOT / "CROSSREF_PAGE_V4.json", crossref)
    message = crossref.get("message") if isinstance(crossref, dict) else None
    items = (message or {}).get("items") or []
    unique = []
    seen_dois = set()
    for item in items:
        doi = str(item.get("DOI") or "").lower()
        if doi and doi not in seen_dois:
            seen_dois.add(doi)
            unique.append(item)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        rows = list(pool.map(audit_item, enumerate(unique, start=1)))
    seen_publications: set[str] = set()
    seen_repositories: set[str] = set()
    for row in rows:
        identity = row.get("concept_identity") or {}
        doi = identity.get("publication_doi")
        repo = identity.get("repository_full_name_casefolded")
        collisions = []
        if doi and doi in seen_publications:
            collisions.append("DUPLICATE_PUBLICATION_DOI")
        if repo and repo in seen_repositories:
            collisions.append("DUPLICATE_REPOSITORY_CONCEPT")
        if doi:
            seen_publications.add(doi)
        if repo:
            seen_repositories.add(repo)
        if collisions:
            row["failure_causes"].extend(collisions)
            row["strict_eligible"] = False
        row["deduplication_failures"] = collisions
    with (ROOT / "CANDIDATES_V4.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
    strict = [row for row in rows if row.get("strict_eligible")]
    write_json(ROOT / "STRICT_CANDIDATES_V4.json", strict)
    log = {
        "schema_version": "orion.p4.m6.source-provider-successor.transport-log.v4",
        "protocol_id": PROTOCOL["protocol_id"],
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "crossref": crossref_meta,
        "crossref_message_total_results": (message or {}).get("total-results"),
        "frozen_rows_requested": query["rows"],
        "crossref_rows_returned": len(items),
        "unique_publication_dois_audited": len(unique),
        "candidate_rows": len(rows),
        "provider_qualified_candidate_rows": len(strict),
        "joss_transport_failures": sum(1 for r in rows if "JOSS_RELATION_TRANSPORT_CANNOT_CHECK" in r.get("failure_causes", [])),
        "github_repository_transport_failures": sum(1 for r in rows if "GITHUB_REPOSITORY_TRANSPORT_CANNOT_CHECK" in r.get("failure_causes", [])),
        "github_release_transport_or_absence_failures": sum(1 for r in rows if "GITHUB_LATEST_RELEASE_CANNOT_CHECK" in r.get("failure_causes", [])),
        "raw_crossref_path": "CROSSREF_PAGE_V4.json",
        "candidate_path": "CANDIDATES_V4.jsonl",
        "candidate_sha256": sha256((ROOT / "CANDIDATES_V4.jsonl").read_bytes()),
        "outcomes_accessed": False,
        "protected_data_accessed": False,
    }
    write_json(ROOT / "TRANSPORT_LOG_V4.json", log)
    print(json.dumps(log, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
