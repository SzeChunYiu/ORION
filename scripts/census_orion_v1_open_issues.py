#!/usr/bin/env python3
"""Acquire a denominator-complete, content-bound census of open ORION issues."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping, Sequence

API_VERSION = "2022-11-28"
USER_AGENT = "ORION-V1-open-issue-census/1"
QUANTUM_PATTERN = re.compile(
    r"(?ix)"
    r"\bquantum\b|"
    r"\borion[- ]?q(?:n|g)?\b|"
    r"\bqg[- ]?\d+[a-z]?\b|"
    r"\bqn[- ]?\d*[a-z]?\b|"
    r"\bqldpc\b|"
    r"\bqubit(?:s)?\b|"
    r"\bpauli\b|"
    r"\bclifford\b|"
    r"\bfault[- ]?tolerant\b|"
    r"\btare\b|"
    r"\bsixlcu\b|"
    r"\bstabprep\b|"
    r"\bqsvt\b|"
    r"\bquantum[- ]native\b"
)


class CensusError(RuntimeError):
    """Raised when acquisition or denominator validation fails."""


@dataclass(frozen=True)
class Response:
    url: str
    status: int
    headers: Mapping[str, str]
    body: bytes

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.body).hexdigest()


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def request_json(
    url: str,
    *,
    token: str,
    retries: int = 4,
    timeout: int = 60,
) -> Response:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": API_VERSION,
    }
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read()
                result = Response(
                    url=response.geturl(),
                    status=response.status,
                    headers={key.lower(): value for key, value in response.headers.items()},
                    body=body,
                )
                if result.status != 200:
                    raise CensusError(f"unexpected HTTP status {result.status}: {url}")
                json.loads(body)
                return result
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            status = getattr(exc, "code", None)
            retryable = status is None or status == 429 or 500 <= int(status) < 600
            if not retryable or attempt == retries:
                break
            time.sleep(min(2 ** (attempt - 1), 8))
    raise CensusError(f"request failed after {retries} attempts: {url}: {last_error}")


def response_record(response: Response, path: str) -> dict[str, Any]:
    selected_headers = {
        key: response.headers.get(key)
        for key in (
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
        if response.headers.get(key) is not None
    }
    return {
        "path": path,
        "url": response.url,
        "status": response.status,
        "bytes": len(response.body),
        "sha256": response.sha256,
        "headers": selected_headers,
    }


def search_url(api_url: str, repository: str) -> str:
    query = urllib.parse.urlencode(
        {"q": f"repo:{repository} is:issue is:open", "per_page": 1, "page": 1}
    )
    return f"{api_url.rstrip('/')}/search/issues?{query}"


def issue_page_url(api_url: str, repository: str, page: int) -> str:
    owner, repo = repository.split("/", 1)
    query = urllib.parse.urlencode(
        {
            "state": "open",
            "per_page": 100,
            "page": page,
            "sort": "created",
            "direction": "asc",
        }
    )
    return f"{api_url.rstrip('/')}/repos/{owner}/{repo}/issues?{query}"


def load_object(response: Response, label: str) -> dict[str, Any]:
    value = json.loads(response.body)
    if not isinstance(value, dict):
        raise CensusError(f"{label}: object required")
    return value


def load_array(response: Response, label: str) -> list[dict[str, Any]]:
    value = json.loads(response.body)
    if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
        raise CensusError(f"{label}: array of objects required")
    return value


def normalize_issue(row: Mapping[str, Any]) -> dict[str, Any]:
    number = row.get("number")
    if type(number) is not int or number <= 0:
        raise CensusError(f"invalid issue number: {number!r}")
    title = row.get("title")
    url = row.get("html_url")
    state = row.get("state")
    if not isinstance(title, str) or not title.strip():
        raise CensusError(f"issue #{number}: title missing")
    if not isinstance(url, str) or not url.startswith("https://github.com/"):
        raise CensusError(f"issue #{number}: canonical URL missing")
    if state != "open":
        raise CensusError(f"issue #{number}: non-open row in open census")
    body = row.get("body")
    if body is None:
        body = ""
    if not isinstance(body, str):
        raise CensusError(f"issue #{number}: body must be text/null")
    labels = row.get("labels") or []
    label_names: list[str] = []
    for label in labels:
        if isinstance(label, str):
            label_names.append(label)
        elif isinstance(label, Mapping) and isinstance(label.get("name"), str):
            label_names.append(label["name"])
        else:
            raise CensusError(f"issue #{number}: malformed label")
    user = row.get("user") or {}
    assignees = row.get("assignees") or []
    milestone = row.get("milestone")
    return {
        "number": number,
        "title": title,
        "url": url,
        "state": state,
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
        "author": user.get("login") if isinstance(user, Mapping) else None,
        "assignees": [
            item.get("login")
            for item in assignees
            if isinstance(item, Mapping) and isinstance(item.get("login"), str)
        ],
        "labels": sorted(set(label_names), key=str.casefold),
        "comments": row.get("comments"),
        "locked": row.get("locked"),
        "milestone": (
            milestone.get("title")
            if isinstance(milestone, Mapping) and isinstance(milestone.get("title"), str)
            else None
        ),
        "body_bytes": len(body.encode("utf-8")),
        "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
    }


def quantum_reasons(row: Mapping[str, Any]) -> list[str]:
    fields = {
        "title": str(row.get("title") or ""),
        "body": str(row.get("body") or ""),
        "labels": " ".join(
            (
                str(label.get("name") or "")
                if isinstance(label, Mapping)
                else str(label)
            )
            for label in (row.get("labels") or [])
        ),
    }
    return [
        field
        for field, value in fields.items()
        if QUANTUM_PATTERN.search(value)
    ]


def acquire_once(
    *,
    api_url: str,
    repository: str,
    token: str,
    attempt_dir: Path,
    frozen_base_main: str,
) -> dict[str, Any]:
    started = time.monotonic()
    acquired_at = utc_now()
    raw_dir = attempt_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []

    before = request_json(search_url(api_url, repository), token=token)
    (raw_dir / "search-before.json").write_bytes(before.body)
    records.append(response_record(before, "raw/search-before.json"))
    before_count = load_object(before, "search-before").get("total_count")
    if type(before_count) is not int or before_count < 0:
        raise CensusError("search-before: invalid total_count")

    raw_rows: list[dict[str, Any]] = []
    excluded_pull_requests = 0
    page = 1
    while True:
        response = request_json(issue_page_url(api_url, repository, page), token=token)
        relative = f"raw/issues-page-{page:04d}.json"
        (attempt_dir / relative).write_bytes(response.body)
        records.append(response_record(response, relative))
        rows = load_array(response, f"issues page {page}")
        for row in rows:
            if "pull_request" in row:
                excluded_pull_requests += 1
            else:
                raw_rows.append(row)
        link = response.headers.get("link", "")
        if len(rows) < 100 and 'rel="next"' not in link:
            break
        if 'rel="next"' not in link:
            raise CensusError(f"issues page {page}: full page without next link")
        page += 1
        if page > 100:
            raise CensusError("pagination exceeded fail-closed page cap")

    after = request_json(search_url(api_url, repository), token=token)
    (raw_dir / "search-after.json").write_bytes(after.body)
    records.append(response_record(after, "raw/search-after.json"))
    after_count = load_object(after, "search-after").get("total_count")
    if type(after_count) is not int or after_count < 0:
        raise CensusError("search-after: invalid total_count")
    if before_count != after_count:
        raise CensusError(
            f"open-issue denominator changed during acquisition: {before_count} -> {after_count}"
        )

    normalized = [normalize_issue(row) for row in raw_rows]
    normalized.sort(key=lambda row: row["number"])
    numbers = [row["number"] for row in normalized]
    if len(numbers) != len(set(numbers)):
        raise CensusError("duplicate issue number in paginated acquisition")
    if len(normalized) != before_count:
        raise CensusError(
            f"paginated issue denominator {len(normalized)} != search denominator {before_count}"
        )

    quantum_rows: list[dict[str, Any]] = []
    for raw, row in sorted(
        zip(raw_rows, [normalize_issue(item) for item in raw_rows], strict=True),
        key=lambda pair: pair[1]["number"],
    ):
        reasons = quantum_reasons(raw)
        if reasons:
            quantum_rows.append(
                {
                    "number": row["number"],
                    "title": row["title"],
                    "url": row["url"],
                    "labels": row["labels"],
                    "candidate_reasons": reasons,
                }
            )

    checkout_commit = git("rev-parse", "HEAD")
    checkout_tree = git("rev-parse", "HEAD^{tree}")
    issue_payload = {
        "schema": "ORION.V1.OpenIssueCensus.v1",
        "repository": repository,
        "frozen_base_main": frozen_base_main,
        "checkout_commit": checkout_commit,
        "checkout_tree": checkout_tree,
        "acquired_at_utc": acquired_at,
        "count": len(normalized),
        "issues": normalized,
    }
    quantum_payload = {
        "schema": "ORION.V1.QuantumIssueCandidateCensus.v1",
        "repository": repository,
        "acquired_at_utc": acquired_at,
        "classification": (
            "LEXICAL_ACQUISITION_CANDIDATES_ONLY__NO_SCIENTIFIC_DISPOSITION"
        ),
        "count": len(quantum_rows),
        "issues": quantum_rows,
    }
    write_json(attempt_dir / "OPEN_ISSUES.json", issue_payload)
    write_json(attempt_dir / "QUANTUM_CANDIDATES.json", quantum_payload)

    rate_remaining = [
        int(record["headers"]["x-ratelimit-remaining"])
        for record in records
        if record["headers"].get("x-ratelimit-remaining", "").isdigit()
    ]
    raw_manifest = {
        "schema": "ORION.V1.OpenIssueRawManifest.v1",
        "repository": repository,
        "acquired_at_utc": acquired_at,
        "search_count_before": before_count,
        "search_count_after": after_count,
        "pages": page,
        "responses": records,
    }
    freeze = {
        "schema": "ORION.V1.OpenIssueCensusFreeze.v1",
        "repository": repository,
        "frozen_base_main": frozen_base_main,
        "checkout_commit": checkout_commit,
        "checkout_tree": checkout_tree,
        "acquired_at_utc": acquired_at,
        "query": "is:issue is:open",
        "authority_ceiling": {
            "complete_open_issue_identity_census": "AUDITABLE",
            "scientific_disposition": "NONE",
            "issue_closure_authority": "NONE",
            "external_novelty": "CANNOT_CHECK",
            "paper_authority_delta": "NONE",
        },
    }
    primary = {
        "schema": "ORION.V1.OpenIssueCensusPrimaryResult.v1",
        "terminal": "V1_OPEN_ISSUE_CENSUS_COMPLETE",
        "open_issue_count": len(normalized),
        "quantum_candidate_count": len(quantum_rows),
        "excluded_pull_request_count": excluded_pull_requests,
        "search_denominator_stable": before_count == after_count,
        "pagination_complete": True,
    }
    donor = {
        "schema": "ORION.V1.OpenIssueCensusDonorResult.v1",
        "source": "GITHUB_REST_ISSUES_AND_SEARCH_APIS",
        "native_semantics": (
            "pull requests excluded by the API pull_request field, not by title"
        ),
        "scientific_donor_result": "NOT_APPLICABLE_TO_IDENTITY_ACQUISITION",
    }
    negatives = {
        "schema": "ORION.V1.OpenIssueCensusNegativeControls.v1",
        "duplicate_issue_numbers": 0,
        "non_open_rows": 0,
        "pull_requests_excluded": excluded_pull_requests,
        "search_denominator_drift": False,
        "lexical_quantum_candidate_is_scientific_disposition": False,
        "issue_state_is_scientific_authority": False,
    }
    resources = {
        "schema": "ORION.V1.OpenIssueCensusResourceLedger.v1",
        "http_request_count": len(records),
        "raw_response_bytes": sum(record["bytes"] for record in records),
        "wall_seconds": round(time.monotonic() - started, 6),
        "rate_limit_remaining_min": min(rate_remaining) if rate_remaining else None,
    }
    transfer = {
        "schema": "ORION.V1.OpenIssueCensusTransferResult.v1",
        "next_job": "V1-Q-CENSUS-01",
        "quantum_candidate_rows_ready": len(quantum_rows),
        "automatic_issue_closure": "FORBIDDEN",
        "paper_authority_delta": "NONE",
    }
    for name, value in (
        ("FREEZE.json", freeze),
        ("RAW_MANIFEST.json", raw_manifest),
        ("PRIMARY_RESULT.json", primary),
        ("DONOR_RESULT.json", donor),
        ("NEGATIVE_CONTROLS.json", negatives),
        ("RESOURCE_LEDGER.json", resources),
        ("TRANSFER_RESULT.json", transfer),
    ):
        write_json(attempt_dir / name, value)

    bound_files: list[dict[str, Any]] = []
    for path in sorted(attempt_dir.rglob("*")):
        if not path.is_file() or path.name == "RESULT_BINDING_PACKET.json":
            continue
        raw = path.read_bytes()
        bound_files.append(
            {
                "path": path.relative_to(attempt_dir).as_posix(),
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
    binding = {
        "schema": "ORION.V1.OpenIssueCensusResultBindingPacket.v1",
        "terminal": "V1_OPEN_ISSUE_CENSUS_COMPLETE",
        "frozen_base_main": frozen_base_main,
        "checkout_commit": checkout_commit,
        "checkout_tree": checkout_tree,
        "open_issue_count": len(normalized),
        "quantum_candidate_count": len(quantum_rows),
        "bound_files": bound_files,
        "authority_ceiling": freeze["authority_ceiling"],
    }
    write_json(attempt_dir / "RESULT_BINDING_PACKET.json", binding)
    return {
        "open_issue_count": len(normalized),
        "quantum_candidate_count": len(quantum_rows),
        "pages": page,
        "requests": len(records),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    repository = args.repository or os.environ.get("GITHUB_REPOSITORY")
    if not repository or repository.count("/") != 1:
        raise CensusError("--repository owner/name is required")
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise CensusError("GITHUB_TOKEN is required")
    if not re.fullmatch(r"[0-9a-f]{40}", args.frozen_base_main):
        raise CensusError("--frozen-base-main must be a lowercase 40-character SHA")
    output = args.output_dir.resolve()
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    failures: list[dict[str, Any]] = []
    for attempt in range(1, args.acquisition_attempts + 1):
        attempt_dir = output / f"attempt-{attempt}"
        attempt_dir.mkdir()
        try:
            summary = acquire_once(
                api_url=args.api_url,
                repository=repository,
                token=token,
                attempt_dir=attempt_dir,
                frozen_base_main=args.frozen_base_main,
            )
        except CensusError as exc:
            failure = {
                "attempt": attempt,
                "failed_at_utc": utc_now(),
                "error": str(exc),
            }
            failures.append(failure)
            write_json(attempt_dir / "FAILED_ACQUISITION.json", failure)
            continue
        final_dir = output / "complete"
        attempt_dir.rename(final_dir)
        write_json(output / "ACQUISITION_ATTEMPTS.json", {
            "schema": "ORION.V1.OpenIssueCensusAttempts.v1",
            "successful_attempt": attempt,
            "failed_attempts": failures,
        })
        return summary
    write_json(output / "ACQUISITION_ATTEMPTS.json", {
        "schema": "ORION.V1.OpenIssueCensusAttempts.v1",
        "successful_attempt": None,
        "failed_attempts": failures,
    })
    raise CensusError("all acquisition attempts failed")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository")
    parser.add_argument("--api-url", default="https://api.github.com")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--frozen-base-main", required=True)
    parser.add_argument("--acquisition-attempts", type=int, default=3)
    args = parser.parse_args(argv)
    if not 1 <= args.acquisition_attempts <= 5:
        parser.error("--acquisition-attempts must be between 1 and 5")
    try:
        summary = run(args)
    except CensusError as exc:
        print(f"ORION_V1_OPEN_ISSUE_CENSUS_INVALID: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
