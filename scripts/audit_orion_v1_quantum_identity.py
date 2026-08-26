#!/usr/bin/env python3
"""Bind the 67 frozen ORION V1 quantum lexical candidates to GitHub identities.

This is an identity, route, and byte-custody audit.  It deliberately has no
scientific-disposition or publication-authority grant.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable, Mapping, Sequence

API_VERSION = "2022-11-28"
USER_AGENT = "ORION-V1-quantum-identity-audit/1"
PACKET_ID = "V1-Q-IDENTITY-BIND-01"
SOURCE_COMMIT = "bf9ee8fa34ffba7531de18e54b58eba4a641601c"
SOURCE_TREE = "88f8a6c2b24fcec02f2752b78946a7a14652c33c"
EXPECTED_CENSUS_SHA256 = "115b2ea69dba24bcf1a5959403dc6165ffc4b5b59ad4a5d81fd78ca293f408da"
EXPECTED_CANDIDATE_COUNT = 67
FINAL_DISPOSITIONS = {
    "PROVEN",
    "FORMALLY_CHECKED",
    "COMPUTATIONALLY_GREEN_BOUNDED",
    "SCIENTIFICALLY_CLOSED",
    "VALIDATED",
}
ALLOWED_LINK_EVIDENCE = {
    "EXACT_PULL_URL",
    "CONTEXTUAL_PR_REFERENCE",
    "TIMELINE_CROSS_REFERENCE",
    "TIMELINE_CONNECTED_PULL_REQUEST",
}
AUTHORITY_CEILING = {
    "scientific_disposition": "NONE",
    "paper_authority_delta": "NONE",
    "physical_quantum_validity": "CANNOT_CHECK",
    "quantum_advantage": "CANNOT_CHECK",
    "external_novelty": "CANNOT_CHECK",
    "issue_closure_authority": "NONE",
}
REQUIRED_FILES = (
    "FREEZE.json",
    "RAW_MANIFEST.json",
    "ISSUE_IDENTITY_LEDGER.json",
    "LINKED_PR_COMMIT_LEDGER.json",
    "CURRENT_MAIN_PRESENCE_LEDGER.json",
    "COMMON_CORE_ROUTE_LEDGER.json",
    "NEGATIVE_CONTROLS.json",
    "RESOURCE_LEDGER.json",
    "RESULT_BINDING_PACKET.json",
)
LEXICAL_EXCLUSION_REASONS = {
    632: "Historical programme prose contains quantum cross-references; this row is not a direct quantum-scientific issue.",
    1366: "The LUNARC renderer issue contains quantum-scope prose; its executable object is non-quantum infrastructure.",
}
PATH_PREFIXES = (
    ".github/",
    "artifacts/",
    "benchmarks/",
    "configs/",
    "data/",
    "development/",
    "docs/",
    "examples/",
    "paper/",
    "papers/",
    "research/",
    "results/",
    "scripts/",
    "src/",
    "tests/",
)


class AuditError(RuntimeError):
    """Fail-closed identity-audit error."""


class RateLimitCensored(AuditError):
    """GitHub rate-limit censorship terminal."""


@dataclass(frozen=True)
class Response:
    url: str
    status: int
    headers: Mapping[str, str]
    body: bytes

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.body).hexdigest()


class GitHubClient:
    def __init__(self, token: str, *, timeout: int = 60, retries: int = 4) -> None:
        if not token:
            raise AuditError("GitHub token is required")
        self.token = token
        self.timeout = timeout
        self.retries = retries
        self.request_count = 0
        self.response_bytes = 0
        self.rate_limit_remaining: list[int] = []
        self._cache: dict[str, Response] = {}

    def get(self, url: str) -> Response:
        if url in self._cache:
            return self._cache[url]
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "User-Agent": USER_AGENT,
            "X-GitHub-Api-Version": API_VERSION,
        }
        last_error: Exception | None = None
        for attempt in range(1, self.retries + 1):
            request = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    body = response.read()
                    result = Response(
                        url=response.geturl(),
                        status=int(response.status),
                        headers={k.lower(): v for k, v in response.headers.items()},
                        body=body,
                    )
                    self.request_count += 1
                    self.response_bytes += len(body)
                    remaining = result.headers.get("x-ratelimit-remaining")
                    if remaining is not None and remaining.isdigit():
                        self.rate_limit_remaining.append(int(remaining))
                    if result.status != 200:
                        raise AuditError(f"unexpected HTTP status {result.status}: {url}")
                    json.loads(result.body)
                    self._cache[url] = result
                    return result
            except urllib.error.HTTPError as exc:
                last_error = exc
                remaining = exc.headers.get("x-ratelimit-remaining") if exc.headers else None
                if exc.code in {403, 429} and remaining == "0":
                    raise RateLimitCensored(f"RATE_LIMIT_CENSORED: {url}") from exc
                retryable = exc.code == 429 or 500 <= exc.code < 600
                if not retryable or attempt == self.retries:
                    break
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt == self.retries:
                    break
            time.sleep(min(2 ** (attempt - 1), 8))
        raise AuditError(f"request failed after {self.retries} attempts: {url}: {last_error}")


class RawArchive:
    """Deterministic deflated storage retaining exact acquired bytes."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._zip = zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9)
        self._entries: dict[str, str] = {}

    def add(self, name: str, body: bytes) -> None:
        digest = sha256_bytes(body)
        previous = self._entries.get(name)
        if previous is not None:
            if previous != digest:
                raise AuditError(f"raw archive path collision with different bytes: {name}")
            return
        info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        self._zip.writestr(info, body)
        self._entries[name] = digest

    def close(self) -> None:
        self._zip.close()

    def __enter__(self) -> RawArchive:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_record(path: Path, relative: str | None = None) -> dict[str, Any]:
    data = path.read_bytes()
    return {"path": relative or path.name, "bytes": len(data), "sha256": sha256_bytes(data)}


def load_json_bytes(value: bytes, label: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise AuditError(f"{label}: invalid JSON") from exc


def load_object_bytes(value: bytes, label: str) -> dict[str, Any]:
    result = load_json_bytes(value, label)
    if not isinstance(result, dict):
        raise AuditError(f"{label}: object required")
    return result


def selected_headers(headers: Mapping[str, str]) -> dict[str, str]:
    keys = (
        "date",
        "etag",
        "last-modified",
        "link",
        "x-github-request-id",
        "x-ratelimit-limit",
        "x-ratelimit-remaining",
        "x-ratelimit-reset",
        "x-ratelimit-resource",
    )
    return {key: headers[key] for key in keys if key in headers}


def response_record(response: Response, path: str) -> dict[str, Any]:
    return {
        "archive_entry": path,
        "url": response.url,
        "status": response.status,
        "bytes": len(response.body),
        "sha256": response.sha256,
        "headers": selected_headers(response.headers),
        "pagination_complete": True,
    }


def parse_link_next(value: str | None) -> str | None:
    if not value:
        return None
    for part in value.split(","):
        match = re.match(r'\s*<([^>]+)>\s*;\s*rel="([^"]+)"', part)
        if match and "next" in match.group(2).split():
            return match.group(1)
    return None


def fetch_all_pages(
    client: Any,
    url: str,
    *,
    prefix: str,
    retain: Callable[[str, bytes], None],
) -> tuple[list[Any], list[dict[str, Any]]]:
    rows: list[Any] = []
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    page = 1
    current: str | None = url
    while current is not None:
        if current in seen:
            raise AuditError(f"pagination loop: {current}")
        seen.add(current)
        response = client.get(current)
        parsed = load_json_bytes(response.body, f"{prefix}-{page:04d}")
        if not isinstance(parsed, list):
            raise AuditError(f"{prefix}-{page:04d}: array required")
        path = f"{prefix}-{page:04d}.json"
        retain(path, response.body)
        records.append(response_record(response, path))
        rows.extend(parsed)
        current = parse_link_next(response.headers.get("link"))
        page += 1
    if not records:
        raise AuditError(f"no pagination page acquired: {url}")
    return rows, records


def validate_issue_payload(payload: Mapping[str, Any], expected_number: int) -> None:
    if "pull_request" in payload:
        raise AuditError(f"candidate #{expected_number} resolved to a pull request, not an issue")
    if payload.get("number") != expected_number:
        raise AuditError(f"issue identity mismatch: expected #{expected_number}, got {payload.get('number')!r}")
    if not isinstance(payload.get("title"), str):
        raise AuditError(f"issue #{expected_number}: title missing")
    if payload.get("body") is not None and not isinstance(payload.get("body"), str):
        raise AuditError(f"issue #{expected_number}: body must be text or null")


def body_bytes(payload: Mapping[str, Any]) -> bytes:
    value = payload.get("body")
    if value is None:
        value = ""
    if not isinstance(value, str):
        raise AuditError("body must be text or null")
    return value.encode("utf-8")


def validate_body_identity(census_row: Mapping[str, Any], payload: Mapping[str, Any]) -> None:
    actual = sha256_bytes(body_bytes(payload))
    if actual != census_row.get("body_sha256"):
        raise AuditError(
            f"issue #{census_row.get('number')}: body SHA does not match frozen census "
            f"({census_row.get('body_sha256')} != {actual})"
        )


def _invert_groups(groups: Mapping[str, Any], label: str) -> dict[int, str]:
    result: dict[int, str] = {}
    for group, values in groups.items():
        if not isinstance(group, str) or not isinstance(values, list):
            raise AuditError(f"{label}: malformed group")
        for value in values:
            if type(value) is not int:
                raise AuditError(f"{label}: non-integer issue number")
            if value in result:
                raise AuditError(f"{label}: duplicate issue #{value}")
            result[value] = group
    return result


def validate_denominator(
    census_rows: Sequence[Mapping[str, Any]], semantic: Mapping[str, Any]
) -> dict[int, tuple[str, str]]:
    numbers = [row.get("number") for row in census_rows]
    if any(type(number) is not int for number in numbers):
        raise AuditError("census denominator contains invalid issue number")
    if len(numbers) != len(set(numbers)):
        raise AuditError("census denominator contains duplicate issue number")
    intake = _invert_groups(semantic.get("intake_classes", {}), "intake classes")
    cores = _invert_groups(semantic.get("common_cores", {}), "common cores")
    census_set = set(numbers)
    if census_set != set(intake) or census_set != set(cores):
        raise AuditError(
            "quantum candidate denominator mismatch among census, intake classes, and common cores"
        )
    for row in census_rows:
        digest = row.get("body_sha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise AuditError(f"issue #{row.get('number')}: invalid frozen body SHA")
    return {number: (intake[number], cores[number]) for number in sorted(census_set)}


def _excerpt(text: str, start: int, end: int) -> str:
    left = max(0, start - 80)
    right = min(len(text), end + 80)
    return " ".join(text[left:right].split())[:240]


def extract_explicit_pr_references(
    text: str | None, repository: str, source: str
) -> list[dict[str, Any]]:
    if not text:
        return []
    owner, repo = map(re.escape, repository.split("/", 1))
    results: list[dict[str, Any]] = []
    occupied: list[tuple[int, int]] = []
    url_pattern = re.compile(
        rf"https://github\.com/{owner}/{repo}/pull/(\d+)(?:\b|/)", re.IGNORECASE
    )
    for match in url_pattern.finditer(text):
        results.append({
            "pr_number": int(match.group(1)),
            "evidence_kind": "EXACT_PULL_URL",
            "source": source,
            "excerpt": _excerpt(text, *match.span()),
        })
        occupied.append(match.span())
    contextual = re.compile(
        r"(?ix)(?:\bPR\b|\bpull\s+request\b|\bmerged?\s+via\b|\bimplemented\s+(?:by|in)\b|\bclosing\s+)"
        r"\s*(?:[:=-]\s*)?\#(\d+)"
    )
    for match in contextual.finditer(text):
        if any(match.start() < end and match.end() > start for start, end in occupied):
            continue
        results.append({
            "pr_number": int(match.group(1)),
            "evidence_kind": "CONTEXTUAL_PR_REFERENCE",
            "source": source,
            "excerpt": _excerpt(text, *match.span()),
        })
    unique: dict[tuple[int, str, str], dict[str, Any]] = {}
    for result in results:
        key = (result["pr_number"], result["evidence_kind"], result["source"])
        unique.setdefault(key, result)
    return sorted(unique.values(), key=lambda row: (row["pr_number"], row["evidence_kind"], row["source"]))


def timeline_pr_references(events: Sequence[Any], repository: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    prefix = f"https://github.com/{repository}/pull/"
    for event in events:
        if not isinstance(event, Mapping):
            continue
        event_name = event.get("event")
        source_issue = (event.get("source") or {}).get("issue") if isinstance(event.get("source"), Mapping) else None
        if not isinstance(source_issue, Mapping) or "pull_request" not in source_issue:
            continue
        number = source_issue.get("number")
        html_url = source_issue.get("html_url")
        if type(number) is not int or not isinstance(html_url, str) or not html_url.startswith(prefix):
            continue
        if event_name == "cross-referenced":
            kind = "TIMELINE_CROSS_REFERENCE"
        elif event_name in {"connected", "closed"}:
            kind = "TIMELINE_CONNECTED_PULL_REQUEST"
        else:
            continue
        results.append({"pr_number": number, "evidence_kind": kind, "source": "timeline"})
    unique = {(row["pr_number"], row["evidence_kind"]): row for row in results}
    return [unique[key] for key in sorted(unique)]


def _normalize_named_path(value: str) -> str | None:
    value = urllib.parse.unquote(value.strip().strip("`'\"()[]{}<>,.;:"))
    value = value.split("#", 1)[0].split("?", 1)[0]
    if value.startswith("./"):
        value = value[2:]
    if not value or "://" in value or value.startswith(("/", "../")) or "\\" in value:
        return None
    if any(part in {"", ".", ".."} for part in PurePosixPath(value).parts):
        return None
    if len(value) > 300 or any(char.isspace() for char in value):
        return None
    if not value.startswith(PATH_PREFIXES):
        return None
    return value.rstrip("/.,;:")


def extract_named_paths(text: str | None) -> list[str]:
    if not text:
        return []
    candidates: set[str] = set()
    for match in re.finditer(r"`([^`\n]+)`", text):
        normalized = _normalize_named_path(match.group(1))
        if normalized:
            candidates.add(normalized)
    for match in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", text):
        normalized = _normalize_named_path(match.group(1))
        if normalized:
            candidates.add(normalized)
    bare_prefix = "|".join(re.escape(prefix) for prefix in PATH_PREFIXES)
    for match in re.finditer(rf"(?<![\w/])((?:{bare_prefix})[^\s`'\"<>\]\[)]+)", text):
        normalized = _normalize_named_path(match.group(1))
        if normalized:
            candidates.add(normalized)
    return sorted(candidates)


def ancestry_from_compare(compare: Mapping[str, Any] | None, ancestor_sha: str) -> bool | str:
    if compare is None:
        return "CANNOT_CHECK"
    merge_base = compare.get("merge_base_commit")
    merge_base_sha = merge_base.get("sha") if isinstance(merge_base, Mapping) else None
    status = compare.get("status")
    if merge_base_sha == ancestor_sha and status in {"ahead", "identical"}:
        return True
    if isinstance(status, str):
        return False
    return "CANNOT_CHECK"


def classify_path_presence(
    paths: Iterable[str],
    current_tree: set[str],
    *,
    branch_changed: set[str],
    frozen_tree: set[str] | None = None,
) -> list[dict[str, Any]]:
    rows = []
    frozen_tree = frozen_tree or set()
    for path in sorted(set(paths)):
        present = path in current_tree
        rows.append({
            "path": path,
            "frozen_base_main_presence": "PRESENT_EXACT" if path in frozen_tree else "ABSENT_FROM_FROZEN_BASE_MAIN",
            "current_main_presence": "PRESENT_EXACT" if present else "ABSENT_FROM_CURRENT_MAIN",
            "branch_evidence": (
                "LINKED_PR_CHANGED_FILE_ONLY" if not present and path in branch_changed else
                "LINKED_PR_CHANGED_FILE_ALSO_CURRENT_MAIN" if present and path in branch_changed else
                "NONE"
            ),
            "classified_as_current_main_evidence": present,
        })
    return rows


def _comment_identity(row: Mapping[str, Any]) -> dict[str, Any]:
    body = row.get("body") or ""
    if not isinstance(body, str):
        raise AuditError("comment body must be text or null")
    user = row.get("user") or {}
    return {
        "comment_id": row.get("id"),
        "node_id": row.get("node_id"),
        "author": user.get("login") if isinstance(user, Mapping) else None,
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
        "body_bytes": len(body.encode("utf-8")),
        "body_sha256": sha256_bytes(body.encode("utf-8")),
        "url": row.get("html_url"),
    }


def _current_tree(client: GitHubClient, api: str, repository: str, ref: str, retain: Callable[[str, bytes], None], manifest: list[dict[str, Any]], label: str) -> tuple[str, str, set[str], bool]:
    encoded_ref = urllib.parse.quote(ref, safe="")
    commit_response = client.get(f"{api}/repos/{repository}/commits/{encoded_ref}")
    commit_path = f"raw/git/{label}-commit.json"
    retain(commit_path, commit_response.body)
    manifest.append(response_record(commit_response, commit_path))
    commit = load_object_bytes(commit_response.body, f"{label} commit")
    sha = commit.get("sha")
    tree = (commit.get("commit") or {}).get("tree") if isinstance(commit.get("commit"), Mapping) else None
    tree_sha = tree.get("sha") if isinstance(tree, Mapping) else None
    if not isinstance(sha, str) or not isinstance(tree_sha, str):
        raise AuditError(f"{label}: commit/tree identity missing")
    tree_response = client.get(f"{api}/repos/{repository}/git/trees/{tree_sha}?recursive=1")
    tree_path = f"raw/git/{label}-tree.json"
    retain(tree_path, tree_response.body)
    manifest.append(response_record(tree_response, tree_path))
    tree_object = load_object_bytes(tree_response.body, f"{label} tree")
    entries = tree_object.get("tree")
    if not isinstance(entries, list):
        raise AuditError(f"{label}: recursive tree entries missing")
    paths = {row.get("path") for row in entries if isinstance(row, Mapping) and isinstance(row.get("path"), str)}
    return sha, tree_sha, paths, bool(tree_object.get("truncated"))


def _compare_ancestry(client: GitHubClient, api: str, repository: str, ancestor: str, target: str, retain: Callable[[str, bytes], None], manifest: list[dict[str, Any]], label: str) -> bool | str:
    url = f"{api}/repos/{repository}/compare/{urllib.parse.quote(ancestor, safe='')}...{urllib.parse.quote(target, safe='')}"
    try:
        response = client.get(url)
    except AuditError:
        return "CANNOT_CHECK"
    path = f"raw/compare/{label}.json"
    retain(path, response.body)
    manifest.append(response_record(response, path))
    return ancestry_from_compare(load_object_bytes(response.body, label), ancestor)


def _load_census(census_zip: Path, semantic: Mapping[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], dict[int, dict[str, Any]], dict[str, Any]]:
    data = census_zip.read_bytes()
    digest = sha256_bytes(data)
    expected = ((semantic.get("census_binding") or {}).get("artifact_sha256"))
    if digest != EXPECTED_CENSUS_SHA256 or digest != expected:
        raise AuditError(f"census ZIP SHA mismatch: expected {expected}, got {digest}")
    with zipfile.ZipFile(census_zip) as archive:
        def member(name: str) -> Any:
            try:
                return load_json_bytes(archive.read(name), name)
            except KeyError as exc:
                raise AuditError(f"census member missing: {name}") from exc
        freeze = member("complete/FREEZE.json")
        candidates = member("complete/QUANTUM_CANDIDATES.json")
        open_issues = member("complete/OPEN_ISSUES.json")
        raw_manifest = member("complete/RAW_MANIFEST.json")
        if not isinstance(freeze, dict) or not isinstance(candidates, dict) or not isinstance(open_issues, dict) or not isinstance(raw_manifest, dict):
            raise AuditError("census control members must be objects")
        rows = candidates.get("issues")
        open_rows = open_issues.get("issues")
        if candidates.get("count") != EXPECTED_CANDIDATE_COUNT or not isinstance(rows, list):
            raise AuditError("quantum candidate denominator mismatch")
        if open_issues.get("count") != 129 or not isinstance(open_rows, list):
            raise AuditError("open issue census identity mismatch")
        open_by_number = {row.get("number"): row for row in open_rows if isinstance(row, dict)}
        candidate_rows = []
        for candidate in rows:
            if not isinstance(candidate, dict) or type(candidate.get("number")) is not int:
                raise AuditError("malformed quantum candidate")
            number = candidate["number"]
            if number not in open_by_number:
                raise AuditError(f"candidate #{number} absent from open issue census")
            candidate_rows.append(open_by_number[number])
        raw_issue_by_number: dict[int, dict[str, Any]] = {}
        for record in raw_manifest.get("responses", []):
            if not isinstance(record, Mapping):
                continue
            path = record.get("path")
            if isinstance(path, str) and path.startswith("raw/issues-page-"):
                page_rows = member(f"complete/{path}")
                if not isinstance(page_rows, list):
                    raise AuditError(f"{path}: array required")
                for row in page_rows:
                    if isinstance(row, dict) and "pull_request" not in row and type(row.get("number")) is int:
                        raw_issue_by_number[row["number"]] = row
        for row in candidate_rows:
            raw = raw_issue_by_number.get(row["number"])
            if raw is None:
                raise AuditError(f"issue #{row['number']}: raw census body missing")
            validate_body_identity(row, raw)
        return freeze, candidate_rows, raw_issue_by_number, raw_manifest


def _next_route(intake_class: str) -> str:
    if intake_class == "LEXICAL_FALSE_POSITIVE":
        return "LEXICAL_EXCLUSION_REVIEW_ONLY__ROW_RETAINED"
    if intake_class == "QUANTUM_STRUCTURAL_TRANSFER_CONSUMER":
        return "SOURCE_TARGET_TRANSFER_BINDING_REQUIRED__NO_AUTHORITY_TRANSFER"
    if intake_class == "PROGRAMME_COORDINATION_OR_PUBLICATION":
        return "CHILD_ATOM_ADJUDICATION_REQUIRED__NO_ADMINISTRATIVE_MASS_CLOSURE"
    return "ATOMIC_SCIENTIFIC_ADJUDICATION_REQUIRED__NO_DISPOSITION_ASSIGNED"


def validate_result_documents(documents: Mapping[str, Any], *, expected_numbers: set[int]) -> None:
    issues_doc = documents.get("ISSUE_IDENTITY_LEDGER.json")
    linked_doc = documents.get("LINKED_PR_COMMIT_LEDGER.json")
    presence_doc = documents.get("CURRENT_MAIN_PRESENCE_LEDGER.json")
    core_doc = documents.get("COMMON_CORE_ROUTE_LEDGER.json")
    if not all(isinstance(doc, Mapping) for doc in (issues_doc, linked_doc, presence_doc, core_doc)):
        raise AuditError("required result ledgers missing")
    issue_rows = issues_doc.get("rows")
    if not isinstance(issue_rows, list):
        raise AuditError("issue identity rows missing")
    numbers = [row.get("issue_number") for row in issue_rows if isinstance(row, Mapping)]
    if len(numbers) != len(set(numbers)):
        raise AuditError("duplicate issue identity row")
    if set(numbers) != expected_numbers:
        raise AuditError("issue identity denominator mismatch")
    by_number = {row["issue_number"]: row for row in issue_rows}
    for number, row in by_number.items():
        if row.get("object_kind") != "ISSUE":
            raise AuditError(f"issue #{number}: pull request treated as issue")
        for page_kind in ("comment_pages", "timeline_pages"):
            pages = row.get(page_kind)
            if not isinstance(pages, list) or not pages or any(not page.get("pagination_complete") for page in pages if isinstance(page, Mapping)):
                raise AuditError(f"issue #{number}: incomplete pagination")
        authority = row.get("authority_ceiling")
        if not isinstance(authority, Mapping) or authority.get("scientific_disposition") != "NONE" or authority.get("paper_authority_delta") != "NONE":
            raise AuditError(f"issue #{number}: scientific disposition or paper authority assigned")
        if any(value in FINAL_DISPOSITIONS for value in authority.values()):
            raise AuditError(f"issue #{number}: forbidden final scientific disposition")
    for lexical in (632, 1366):
        if lexical in expected_numbers:
            row = by_number.get(lexical)
            if not row or row.get("intake_class") != "LEXICAL_FALSE_POSITIVE" or not row.get("direct_denominator_exclusion_reason"):
                raise AuditError(f"lexical false-positive row #{lexical} was dropped or promoted")
    linked_rows = linked_doc.get("rows")
    if not isinstance(linked_rows, list):
        raise AuditError("linked PR rows missing")
    for row in linked_rows:
        evidence = row.get("link_evidence") if isinstance(row, Mapping) else None
        if not isinstance(evidence, list) or not evidence:
            raise AuditError("linked PR lacks explicit evidence")
        if any(item.get("evidence_kind") not in ALLOWED_LINK_EVIDENCE for item in evidence if isinstance(item, Mapping)):
            raise AuditError("lexical issue-number mention accepted as linked PR")
        if row.get("current_main_ancestry") is not True and row.get("current_main_authority"):
            raise AuditError("merge absent from main promoted to current-main authority")
        if row.get("current_main_authority"):
            raise AuditError("identity evidence promoted to scientific current-main authority")
    presence_rows = presence_doc.get("rows")
    if not isinstance(presence_rows, list):
        raise AuditError("current-main presence rows missing")
    for row in presence_rows:
        if not isinstance(row, Mapping):
            raise AuditError("malformed presence row")
        if row.get("current_main_presence") != "PRESENT_EXACT" and row.get("classified_as_current_main_evidence"):
            raise AuditError("branch-only result bytes promoted to current-main evidence")
    core_rows = core_doc.get("rows")
    if not isinstance(core_rows, list):
        raise AuditError("common-core rows missing")
    for row in core_rows:
        if row.get("administrative_mass_closure") is not False:
            raise AuditError("administrative mass closure attempted")
        if row.get("source_authority_transfer") != "NONE":
            raise AuditError("source quantum authority transferred to consumer")


def _run_negative_controls(documents: Mapping[str, Any], expected_numbers: set[int]) -> dict[str, Any]:
    controls: list[dict[str, str]] = []

    def reject(name: str, mutate: Callable[[dict[str, Any]], None]) -> None:
        mutated = copy.deepcopy(documents)
        mutate(mutated)
        try:
            validate_result_documents(mutated, expected_numbers=expected_numbers)
        except AuditError as exc:
            controls.append({"control": name, "status": "PASS_REJECTED", "rejection": str(exc)})
            return
        raise AuditError(f"negative control was accepted: {name}")

    reject("remove one of the 67 issue rows", lambda d: d["ISSUE_IDENTITY_LEDGER.json"]["rows"].pop())
    reject("duplicate an issue row", lambda d: d["ISSUE_IDENTITY_LEDGER.json"]["rows"].append(copy.deepcopy(d["ISSUE_IDENTITY_LEDGER.json"]["rows"][0])))
    reject("treat a pull request as an issue", lambda d: d["ISSUE_IDENTITY_LEDGER.json"]["rows"][0].update(object_kind="PULL_REQUEST"))
    reject("truncate a comment or timeline page", lambda d: d["ISSUE_IDENTITY_LEDGER.json"]["rows"][0]["comment_pages"][0].update(pagination_complete=False))
    if documents["LINKED_PR_COMMIT_LEDGER.json"]["rows"]:
        reject("accept a lexical issue-number mention as a linked PR without context", lambda d: d["LINKED_PR_COMMIT_LEDGER.json"]["rows"][0]["link_evidence"][0].update(evidence_kind="LEXICAL_NUMBER_MENTION"))
        reject("treat a merged PR whose merge commit is absent from main as current-main authority", lambda d: d["LINKED_PR_COMMIT_LEDGER.json"]["rows"][0].update(current_main_ancestry=False, current_main_authority=True))
    else:
        raise AuditError("no explicit linked PR exists; linked-PR negative controls cannot execute")
    if documents["CURRENT_MAIN_PRESENCE_LEDGER.json"]["rows"]:
        reject("promote branch-only result bytes", lambda d: d["CURRENT_MAIN_PRESENCE_LEDGER.json"]["rows"][0].update(current_main_presence="ABSENT_FROM_CURRENT_MAIN", classified_as_current_main_evidence=True))
    reject("assign a final scientific disposition from issue prose or checkbox state", lambda d: d["ISSUE_IDENTITY_LEDGER.json"]["rows"][0]["authority_ceiling"].update(scientific_disposition="PROVEN"))
    reject("drop #632 or #1366 instead of retaining explicit lexical-false-positive rows", lambda d: d["ISSUE_IDENTITY_LEDGER.json"].update(rows=[r for r in d["ISSUE_IDENTITY_LEDGER.json"]["rows"] if r["issue_number"] != 632]))
    reject("transfer source quantum authority to a discovery or publication consumer", lambda d: d["COMMON_CORE_ROUTE_LEDGER.json"]["rows"][0].update(source_authority_transfer="INHERITED"))

    first = documents["ISSUE_IDENTITY_LEDGER.json"]["rows"][0]
    same_length = "x" * int(first["census_body_bytes"])
    try:
        validate_body_identity(
            {"number": first["issue_number"], "body_sha256": first["census_body_sha256"]},
            {"body": same_length},
        )
    except AuditError as exc:
        controls.append({"control": "replace an issue body with same-length different bytes", "status": "PASS_REJECTED", "rejection": str(exc)})
    else:
        raise AuditError("same-length issue-body replacement was accepted")

    return {
        "schema": "ORION.V1.QuantumIdentityNegativeControls.v1",
        "packet_id": PACKET_ID,
        "count": len(controls),
        "all_rejected": len(controls) == 11,
        "controls": sorted(controls, key=lambda row: row["control"]),
        "authority_ceiling": AUTHORITY_CEILING,
    }


def verify_raw_archive(output_dir: Path, raw_manifest: Mapping[str, Any]) -> None:
    archive_path = output_dir / "RAW_RESPONSES.zip"
    expected_archive = raw_manifest.get("archive")
    if not isinstance(expected_archive, Mapping):
        raise AuditError("raw archive binding missing")
    actual = file_record(archive_path, "RAW_RESPONSES.zip")
    if any(actual[key] != expected_archive.get(key) for key in ("bytes", "sha256")):
        raise AuditError("raw response archive binding mismatch")
    with zipfile.ZipFile(archive_path) as archive:
        names = set(archive.namelist())
        for record in raw_manifest.get("responses", []):
            path = record.get("archive_entry")
            if path not in names:
                raise AuditError(f"raw response missing: {path}")
            data = archive.read(path)
            if len(data) != record.get("bytes") or sha256_bytes(data) != record.get("sha256"):
                raise AuditError(f"raw response bytes changed: {path}")
        for record in raw_manifest.get("derived_body_objects", []):
            path = record.get("archive_entry")
            if path not in names:
                raise AuditError(f"body custody object missing: {path}")
            data = archive.read(path)
            if len(data) != record.get("bytes") or sha256_bytes(data) != record.get("sha256"):
                raise AuditError(f"body custody bytes changed: {path}")


def check_output(output_dir: Path) -> None:
    missing = [name for name in REQUIRED_FILES if not (output_dir / name).is_file()]
    if missing:
        raise AuditError(f"required outputs missing: {missing}")
    documents = {name: json.loads((output_dir / name).read_text(encoding="utf-8")) for name in REQUIRED_FILES}
    freeze = documents["FREEZE.json"]
    expected_numbers = set(freeze.get("denominator_issue_numbers", []))
    if len(expected_numbers) != EXPECTED_CANDIDATE_COUNT:
        raise AuditError("freeze denominator is not the frozen 67")
    validate_result_documents(documents, expected_numbers=expected_numbers)
    negative = documents["NEGATIVE_CONTROLS.json"]
    if negative.get("count") != 11 or negative.get("all_rejected") is not True:
        raise AuditError("negative controls incomplete")
    verify_raw_archive(output_dir, documents["RAW_MANIFEST.json"])
    binding = documents["RESULT_BINDING_PACKET.json"]
    bound = binding.get("bound_files")
    if not isinstance(bound, list):
        raise AuditError("result binding file list missing")
    for record in bound:
        path = output_dir / record["path"]
        actual = file_record(path, record["path"])
        if actual != record:
            raise AuditError(f"result binding mismatch: {record['path']}")
    if binding.get("paper_authority_delta") != "NONE" or binding.get("grants_scientific_disposition") is not False:
        raise AuditError("result binding exceeds authority ceiling")


def execute(args: argparse.Namespace) -> None:
    started = time.monotonic()
    acquired_at = utc_now()
    output_dir = Path(args.output_dir)
    if output_dir.exists():
        for child in output_dir.iterdir():
            if child.is_file():
                child.unlink()
            elif child.is_dir():
                raise AuditError(f"unexpected prior directory in output: {child}")
    output_dir.mkdir(parents=True, exist_ok=True)
    semantic_path = Path(args.semantic_intake)
    semantic = json.loads(semantic_path.read_text(encoding="utf-8"))
    census_freeze, census_rows, census_raw, census_manifest = _load_census(Path(args.census_zip), semantic)
    mapping = validate_denominator(census_rows, semantic)
    expected_numbers = set(mapping)
    if len(expected_numbers) != EXPECTED_CANDIDATE_COUNT:
        raise AuditError("quantum candidate denominator mismatch")
    token = os.environ.get(args.github_token_env, "")
    client = GitHubClient(token)
    api = "https://api.github.com"
    responses: list[dict[str, Any]] = []
    derived_bodies: list[dict[str, Any]] = []
    issue_rows: list[dict[str, Any]] = []
    all_refs: dict[int, list[dict[str, Any]]] = {}
    issue_texts: dict[int, list[tuple[str, str]]] = {}
    raw_archive_path = output_dir / "RAW_RESPONSES.zip"

    with RawArchive(raw_archive_path) as raw:
        def retain(path: str, body: bytes) -> None:
            raw.add(path, body)

        current_main_sha, current_main_tree_sha, current_tree, current_tree_truncated = _current_tree(
            client, api, args.repository, "main", retain, responses, "current-main"
        )
        frozen_main_sha, frozen_main_tree_sha, frozen_tree, frozen_tree_truncated = _current_tree(
            client, api, args.repository, args.frozen_base_main, retain, responses, "frozen-base-main"
        )
        if frozen_main_sha != args.frozen_base_main:
            raise AuditError("frozen base main commit identity mismatch")

        for census in sorted(census_rows, key=lambda row: row["number"]):
            number = census["number"]
            intake_class, core_id = mapping[number]
            issue_url = f"{api}/repos/{args.repository}/issues/{number}"
            before_response = client.get(issue_url)
            before_path = f"raw/issues/{number:06d}-before.json"
            retain(before_path, before_response.body)
            before_record = response_record(before_response, before_path)
            responses.append(before_record)
            before = load_object_bytes(before_response.body, f"issue #{number} before")
            validate_issue_payload(before, number)

            census_body = body_bytes(census_raw[number])
            before_body = body_bytes(before)
            for label, value in (("census", census_body), ("current-before", before_body)):
                body_path = f"bodies/issues/{number:06d}-{label}.txt"
                retain(body_path, value)
                derived_bodies.append({
                    "archive_entry": body_path,
                    "issue_number": number,
                    "snapshot": label,
                    "bytes": len(value),
                    "sha256": sha256_bytes(value),
                })

            comments, comment_pages = fetch_all_pages(
                client,
                f"{api}/repos/{args.repository}/issues/{number}/comments?per_page=100&page=1",
                prefix=f"raw/comments/{number:06d}/page",
                retain=retain,
            )
            responses.extend(comment_pages)
            timelines, timeline_pages = fetch_all_pages(
                client,
                f"{api}/repos/{args.repository}/issues/{number}/timeline?per_page=100&page=1",
                prefix=f"raw/timeline/{number:06d}/page",
                retain=retain,
            )
            responses.extend(timeline_pages)

            comment_identities = []
            text_sources: list[tuple[str, str]] = [("issue-body", str(before.get("body") or ""))]
            refs = extract_explicit_pr_references(before.get("body"), args.repository, "issue-body")
            for comment in comments:
                if not isinstance(comment, Mapping):
                    raise AuditError(f"issue #{number}: malformed comment")
                identity = _comment_identity(comment)
                comment_identities.append(identity)
                comment_body = str(comment.get("body") or "")
                comment_path = f"bodies/comments/{number:06d}-{identity['comment_id']}.txt"
                comment_bytes = comment_body.encode("utf-8")
                retain(comment_path, comment_bytes)
                derived_bodies.append({
                    "archive_entry": comment_path,
                    "issue_number": number,
                    "comment_id": identity["comment_id"],
                    "snapshot": "comment",
                    "bytes": len(comment_bytes),
                    "sha256": sha256_bytes(comment_bytes),
                })
                source = f"comment:{identity['comment_id']}"
                text_sources.append((source, comment_body))
                refs.extend(extract_explicit_pr_references(comment_body, args.repository, source))
            refs.extend(timeline_pr_references(timelines, args.repository))

            after_response = client.get(issue_url + "?identity_audit=after")
            after_path = f"raw/issues/{number:06d}-after.json"
            retain(after_path, after_response.body)
            after_record = response_record(after_response, after_path)
            responses.append(after_record)
            after = load_object_bytes(after_response.body, f"issue #{number} after")
            validate_issue_payload(after, number)
            after_body = body_bytes(after)
            after_body_path = f"bodies/issues/{number:06d}-current-after.txt"
            retain(after_body_path, after_body)
            derived_bodies.append({
                "archive_entry": after_body_path,
                "issue_number": number,
                "snapshot": "current-after",
                "bytes": len(after_body),
                "sha256": sha256_bytes(after_body),
            })
            stable = (
                before.get("updated_at") == after.get("updated_at")
                and sha256_bytes(before_body) == sha256_bytes(after_body)
                and before.get("comments") == after.get("comments")
            )
            census_match = sha256_bytes(before_body) == census["body_sha256"]
            if not stable:
                identity_status = "UNSTABLE_ISSUE_REVISION_REQUIRES_SUCCESSOR_SNAPSHOT"
            elif not census_match:
                identity_status = "CENSUS_BODY_DRIFT_REQUIRES_SUCCESSOR_SNAPSHOT"
            elif intake_class == "LEXICAL_FALSE_POSITIVE":
                identity_status = "DIRECT_DENOMINATOR_EXCLUSION__ROW_RETAINED"
            else:
                identity_status = "FROZEN_CENSUS_BODY_BOUND__CURRENT_SNAPSHOT_STABLE"
            dedup_refs: dict[tuple[int, str, str], dict[str, Any]] = {}
            for ref in refs:
                key = (ref["pr_number"], ref["evidence_kind"], ref["source"])
                dedup_refs.setdefault(key, ref)
            refs = [dedup_refs[key] for key in sorted(dedup_refs)]
            all_refs[number] = refs
            issue_texts[number] = text_sources
            issue_rows.append({
                "issue_number": number,
                "object_kind": "ISSUE",
                "title": before.get("title"),
                "url": before.get("html_url"),
                "state_at_acquisition": before.get("state"),
                "census_acquired_at_utc": census_freeze.get("acquired_at_utc"),
                "census_updated_at": census.get("updated_at"),
                "current_updated_at_before": before.get("updated_at"),
                "current_updated_at_after": after.get("updated_at"),
                "census_body_bytes": census.get("body_bytes"),
                "census_body_sha256": census.get("body_sha256"),
                "current_body_bytes": len(before_body),
                "current_body_sha256": sha256_bytes(before_body),
                "issue_snapshot_before": before_record,
                "issue_snapshot_after": after_record,
                "comment_count": len(comment_identities),
                "comments": comment_identities,
                "comment_pages": comment_pages,
                "timeline_event_count": len(timelines),
                "timeline_pages": timeline_pages,
                "semantic_intake_class": intake_class,
                "intake_class": intake_class,
                "common_core_id": core_id,
                "explicit_linked_pr_numbers": sorted({ref["pr_number"] for ref in refs}),
                "identity_status": identity_status,
                "direct_denominator_exclusion_reason": LEXICAL_EXCLUSION_REASONS.get(number),
                "next_adjudication_route": _next_route(intake_class),
                "authority_ceiling": AUTHORITY_CEILING,
            })

        pr_numbers = sorted({ref["pr_number"] for refs in all_refs.values() for ref in refs})
        pr_objects: dict[int, dict[str, Any]] = {}
        pr_changed: dict[int, set[str]] = {}
        pr_ancestry: dict[int, tuple[bool | str, bool | str]] = {}
        for pr_number in pr_numbers:
            response = client.get(f"{api}/repos/{args.repository}/pulls/{pr_number}")
            path = f"raw/pulls/{pr_number:06d}.json"
            retain(path, response.body)
            responses.append(response_record(response, path))
            pr = load_object_bytes(response.body, f"pull request #{pr_number}")
            if pr.get("number") != pr_number or "pull_request" in pr:
                raise AuditError(f"linked PR identity mismatch: #{pr_number}")
            pr_objects[pr_number] = pr
            files, page_records = fetch_all_pages(
                client,
                f"{api}/repos/{args.repository}/pulls/{pr_number}/files?per_page=100&page=1",
                prefix=f"raw/pull-files/{pr_number:06d}/page",
                retain=retain,
            )
            responses.extend(page_records)
            pr_changed[pr_number] = {
                row.get("filename") for row in files
                if isinstance(row, Mapping) and isinstance(row.get("filename"), str)
            }
            merge_sha = pr.get("merge_commit_sha")
            if pr.get("merged_at") and isinstance(merge_sha, str):
                frozen_ancestry = _compare_ancestry(client, api, args.repository, merge_sha, args.frozen_base_main, retain, responses, f"pr-{pr_number:06d}-to-frozen")
                current_ancestry = _compare_ancestry(client, api, args.repository, merge_sha, current_main_sha, retain, responses, f"pr-{pr_number:06d}-to-current")
            else:
                frozen_ancestry = False
                current_ancestry = False
            pr_ancestry[pr_number] = (frozen_ancestry, current_ancestry)

        linked_rows: list[dict[str, Any]] = []
        presence_rows: list[dict[str, Any]] = []
        for issue in issue_rows:
            number = issue["issue_number"]
            refs_by_pr: dict[int, list[dict[str, Any]]] = {}
            for ref in all_refs[number]:
                refs_by_pr.setdefault(ref["pr_number"], []).append(ref)
            named_paths: set[str] = set()
            path_sources: dict[str, set[str]] = {}
            for source, text in issue_texts[number]:
                for named in extract_named_paths(text):
                    named_paths.add(named)
                    path_sources.setdefault(named, set()).add(source)
            branch_changed: set[str] = set()
            for pr_number, refs in sorted(refs_by_pr.items()):
                pr = pr_objects[pr_number]
                for named in extract_named_paths(pr.get("body")):
                    named_paths.add(named)
                    path_sources.setdefault(named, set()).add(f"pull:{pr_number}:body")
                branch_changed.update(pr_changed[pr_number])
                frozen_ancestry, current_ancestry = pr_ancestry[pr_number]
                head = pr.get("head") or {}
                base = pr.get("base") or {}
                linked_rows.append({
                    "issue_number": number,
                    "pr_number": pr_number,
                    "link_evidence": sorted(refs, key=lambda row: (row["evidence_kind"], row["source"])),
                    "pr_state": pr.get("state"),
                    "draft": pr.get("draft"),
                    "head_ref": head.get("ref") if isinstance(head, Mapping) else None,
                    "head_sha": head.get("sha") if isinstance(head, Mapping) else None,
                    "base_ref": base.get("ref") if isinstance(base, Mapping) else None,
                    "base_sha": base.get("sha") if isinstance(base, Mapping) else None,
                    "merged_at": pr.get("merged_at"),
                    "merge_commit_sha": pr.get("merge_commit_sha"),
                    "frozen_base_main_ancestry": frozen_ancestry,
                    "current_main_ancestry": current_ancestry,
                    "merge_present_in_current_main": current_ancestry is True,
                    "current_main_authority": False,
                    "changed_file_count": len(pr_changed[pr_number]),
                    "authority_ceiling": AUTHORITY_CEILING,
                })
            issue["named_artifact_paths"] = sorted(named_paths)
            issue_presence = classify_path_presence(named_paths, current_tree, branch_changed=branch_changed, frozen_tree=frozen_tree)
            if not issue_presence:
                issue_presence = [{
                    "path": None,
                    "frozen_base_main_presence": "NO_NAMED_REPOSITORY_PATH_IN_BOUND_TEXT",
                    "current_main_presence": "NO_NAMED_REPOSITORY_PATH_IN_BOUND_TEXT",
                    "branch_evidence": "NONE",
                    "classified_as_current_main_evidence": False,
                }]
            for row in issue_presence:
                row.update({
                    "issue_number": number,
                    "path_sources": sorted(path_sources.get(row["path"], set())) if row["path"] else [],
                    "authority_ceiling": AUTHORITY_CEILING,
                })
                presence_rows.append(row)

        common_rows = []
        for core_id, numbers in sorted(semantic["common_cores"].items()):
            classes = sorted({mapping[number][0] for number in numbers})
            common_rows.append({
                "common_core_id": core_id,
                "issue_numbers": sorted(numbers),
                "semantic_intake_classes": classes,
                "member_routes": {str(number): _next_route(mapping[number][0]) for number in sorted(numbers)},
                "grouping_scope": "SHARED_ADJUDICATION_ROUTE_ONLY__MEMBER_IDENTITIES_AND_OUTCOMES_REMAIN_ATOMIC",
                "administrative_mass_closure": False,
                "source_authority_transfer": "NONE",
                "authority_ceiling": AUTHORITY_CEILING,
            })

    raw_archive_record = file_record(raw_archive_path, "RAW_RESPONSES.zip")
    drift_rows = [row["issue_number"] for row in issue_rows if "DRIFT" in row["identity_status"] or "UNSTABLE" in row["identity_status"]]
    pagination_complete = all(
        all(page["pagination_complete"] for page in row["comment_pages"] + row["timeline_pages"])
        for row in issue_rows
    )
    ancestry_cannot_check = any(
        row["current_main_ancestry"] == "CANNOT_CHECK" or row["frozen_base_main_ancestry"] == "CANNOT_CHECK"
        for row in linked_rows
    )
    if drift_rows:
        terminal = "ISSUE_REVISION_DRIFT_REQUIRES_SUCCESSOR_SNAPSHOT"
    elif not pagination_complete:
        terminal = "COMMENT_OR_TIMELINE_PAGINATION_INCOMPLETE"
    elif ancestry_cannot_check or current_tree_truncated or frozen_tree_truncated:
        terminal = "CURRENT_MAIN_ANCESTRY_CANNOT_CHECK"
    else:
        terminal = "V1_QUANTUM_67_ISSUE_IDENTITY_AND_ROUTE_CENSUS_COMPLETE"

    freeze_doc = {
        "schema": "ORION.V1.QuantumIdentityFreeze.v1",
        "packet_id": PACKET_ID,
        "acquired_at_utc": acquired_at,
        "repository": args.repository,
        "frozen_source_commit": SOURCE_COMMIT,
        "frozen_source_tree": SOURCE_TREE,
        "frozen_base_main": args.frozen_base_main,
        "frozen_base_main_tree": frozen_main_tree_sha,
        "current_remote_main": current_main_sha,
        "current_remote_main_tree": current_main_tree_sha,
        "census_artifact_id": (semantic.get("census_binding") or {}).get("artifact_id"),
        "census_artifact_sha256": EXPECTED_CENSUS_SHA256,
        "semantic_intake_path": args.semantic_intake,
        "semantic_intake_sha256": sha256_bytes(Path(args.semantic_intake).read_bytes()),
        "denominator_count": len(expected_numbers),
        "denominator_issue_numbers": sorted(expected_numbers),
        "drift_issue_numbers": drift_rows,
        "terminal": terminal,
        "authority_ceiling": AUTHORITY_CEILING,
        "non_implications": [
            "V1_QUANTUM_FRONTIER_AUDIT_CLOSED",
            "ANY_QUANTUM_ISSUE_SCIENTIFICALLY_CLOSED",
            "PHYSICAL_QUANTUM_VALIDITY",
            "QUANTUM_ADVANTAGE",
            "EXTERNAL_NOVELTY",
            "P18_MANUSCRIPT_AUTHORIZATION",
            "ORION_V1_FROZEN",
        ],
    }
    raw_manifest_doc = {
        "schema": "ORION.V1.QuantumIdentityRawManifest.v1",
        "packet_id": PACKET_ID,
        "acquired_at_utc": acquired_at,
        "repository": args.repository,
        "archive": raw_archive_record,
        "response_count": len(responses),
        "responses": responses,
        "derived_body_object_count": len(derived_bodies),
        "derived_body_objects": derived_bodies,
        "pagination_complete": pagination_complete,
        "census_input_raw_manifest_sha256": sha256_bytes(canonical_bytes(census_manifest)),
    }
    issue_doc = {
        "schema": "ORION.V1.QuantumIssueIdentityLedger.v1",
        "packet_id": PACKET_ID,
        "row_count": len(issue_rows),
        "rows": issue_rows,
        "authority_ceiling": AUTHORITY_CEILING,
    }
    linked_doc = {
        "schema": "ORION.V1.QuantumLinkedPRCommitLedger.v1",
        "packet_id": PACKET_ID,
        "row_count": len(linked_rows),
        "rows": linked_rows,
        "issues_without_explicit_linked_pr": sorted(expected_numbers - {row["issue_number"] for row in linked_rows}),
        "authority_ceiling": AUTHORITY_CEILING,
    }
    presence_doc = {
        "schema": "ORION.V1.QuantumCurrentMainPresenceLedger.v1",
        "packet_id": PACKET_ID,
        "current_remote_main": current_main_sha,
        "current_remote_main_tree": current_main_tree_sha,
        "recursive_tree_truncated": current_tree_truncated,
        "row_count": len(presence_rows),
        "rows": presence_rows,
        "authority_ceiling": AUTHORITY_CEILING,
    }
    common_doc = {
        "schema": "ORION.V1.QuantumCommonCoreRouteLedger.v1",
        "packet_id": PACKET_ID,
        "row_count": len(common_rows),
        "rows": common_rows,
        "authority_ceiling": AUTHORITY_CEILING,
    }
    preliminary = {
        "ISSUE_IDENTITY_LEDGER.json": issue_doc,
        "LINKED_PR_COMMIT_LEDGER.json": linked_doc,
        "CURRENT_MAIN_PRESENCE_LEDGER.json": presence_doc,
        "COMMON_CORE_ROUTE_LEDGER.json": common_doc,
    }
    validate_result_documents(preliminary, expected_numbers=expected_numbers)
    negative_doc = _run_negative_controls(preliminary, expected_numbers)
    resource_doc = {
        "schema": "ORION.V1.QuantumIdentityResourceLedger.v1",
        "packet_id": PACKET_ID,
        "environment": "LOCAL_LINUX_OR_MACOS_EQUIVALENT__NO_LUNARC",
        "python": sys.version.split()[0],
        "http_request_count": client.request_count,
        "http_response_bytes": client.response_bytes,
        "rate_limit_remaining_min": min(client.rate_limit_remaining) if client.rate_limit_remaining else "CANNOT_CHECK",
        "raw_archive_bytes": raw_archive_record["bytes"],
        "wall_seconds": round(time.monotonic() - started, 6),
        "network_scope": "GITHUB_API_ONLY",
        "authority_ceiling": AUTHORITY_CEILING,
    }
    docs = {
        "FREEZE.json": freeze_doc,
        "RAW_MANIFEST.json": raw_manifest_doc,
        "ISSUE_IDENTITY_LEDGER.json": issue_doc,
        "LINKED_PR_COMMIT_LEDGER.json": linked_doc,
        "CURRENT_MAIN_PRESENCE_LEDGER.json": presence_doc,
        "COMMON_CORE_ROUTE_LEDGER.json": common_doc,
        "NEGATIVE_CONTROLS.json": negative_doc,
        "RESOURCE_LEDGER.json": resource_doc,
    }
    for name, document in docs.items():
        write_json(output_dir / name, document)
    bound_names = list(docs) + ["RAW_RESPONSES.zip"]
    bound_files = [file_record(output_dir / name, name) for name in bound_names]
    result_binding = {
        "schema": "ORION.V1.QuantumIdentityResultBindingPacket.v1",
        "packet_id": PACKET_ID,
        "terminal": terminal,
        "bound_files": bound_files,
        "denominator_count": len(expected_numbers),
        "issue_identity_row_count": len(issue_rows),
        "linked_pr_row_count": len(linked_rows),
        "presence_row_count": len(presence_rows),
        "common_core_row_count": len(common_rows),
        "grants_issue_closure": False,
        "grants_orion_v1_freeze": False,
        "grants_paper_authority": False,
        "grants_scientific_disposition": False,
        "paper_authority_delta": "NONE",
        "authority_ceiling": AUTHORITY_CEILING,
    }
    write_json(output_dir / "RESULT_BINDING_PACKET.json", result_binding)
    check_output(output_dir)
    print(terminal)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository")
    parser.add_argument("--census-zip")
    parser.add_argument("--semantic-intake")
    parser.add_argument("--frozen-base-main")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--github-token-env", default="GITHUB_TOKEN")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        missing = [name for name in ("repository", "census_zip", "semantic_intake", "frozen_base_main") if not getattr(args, name)]
        if missing:
            parser.error(f"execution arguments missing: {', '.join(missing)}")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.check:
            check_output(Path(args.output_dir))
            print("V1_QUANTUM_IDENTITY_RESULT_BINDING_OK")
        else:
            execute(args)
        return 0
    except RateLimitCensored as exc:
        print(f"RATE_LIMIT_CENSORED: {exc}", file=sys.stderr)
        return 3
    except AuditError as exc:
        print(f"CANNOT_CHECK: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
