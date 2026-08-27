#!/usr/bin/env python3
"""Fail-closed audit that withdrawn FiberGuard claims cannot regain authority."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import urllib.request
from typing import Any

POSITIVE_R18 = "FIBERGUARD_R18_PAIRED_ROUTE_PASS_MAXSAT_VALIDATION_AND_QBF_TEST"
INVALID_R19 = "R19_DIAGONAL_PAIR_SHORTCUT"
REPO = "SzeChunYiu/ORION"
LIVE_SUBJECTS = (1377, 1386, 1421, 1471)


def api(path: str) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "ORION-02-R20-retraction-audit",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(
        urllib.request.Request(f"https://api.github.com/repos/{REPO}/{path}", headers=headers),
        timeout=60,
    ) as response:
        return json.load(response)


def pages(path: str) -> list[Any]:
    rows: list[Any] = []
    page = 1
    while True:
        separator = "&" if "?" in path else "?"
        batch = api(f"{path}{separator}per_page=100&page={page}")
        rows.extend(batch)
        if len(batch) < 100:
            return rows
        page += 1


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def corrected_context(text: str, start: int, end: int) -> bool:
    context = text[max(0, start - 500) : min(len(text), end + 500)].lower()
    markers = (
        "retract",
        "withdraw",
        "unsupported",
        "cannot_check",
        "cannot check",
        "not positive evidence",
        "allowed terminal",
        "protocol",
        "former positive",
        "invalid shortcut",
        "falsified",
        "revoked",
    )
    return any(marker in context for marker in markers)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    local_occurrences: list[dict[str, Any]] = []
    local_violations: list[dict[str, Any]] = []
    for path in sorted(args.root.rglob("*")):
        if not path.is_file() or path.stat().st_size > 20_000_000:
            continue
        if path.suffix.lower() not in {".md", ".json", ".tex", ".yml", ".yaml", ".py", ".rs", ".txt"}:
            continue
        text = path.read_text(errors="replace")
        for token in (POSITIVE_R18, INVALID_R19):
            for match in re.finditer(re.escape(token), text):
                protocol_object = (
                    "protocol" in path.name.lower()
                    or path.suffix.lower() in {".yml", ".yaml"}
                    and any(marker in text.lower() for marker in ("allowed", "terminals", "protocol"))
                )
                corrected = protocol_object or corrected_context(text, match.start(), match.end())
                row = {
                    "path": path.relative_to(args.root).as_posix(),
                    "token": token,
                    "offset": match.start(),
                    "corrected_or_protocol_context": corrected,
                }
                local_occurrences.append(row)
                if not corrected:
                    local_violations.append(row)

    live_rows: list[dict[str, Any]] = []
    live_violations: list[dict[str, Any]] = []
    for number in LIVE_SUBJECTS:
        issue = api(f"issues/{number}")
        comments = pages(f"issues/{number}/comments")
        items = [
            {
                "kind": "issue_or_pr_body",
                "created_at": issue["created_at"],
                "updated_at": issue["updated_at"],
                "text": issue.get("body") or "",
            }
        ] + [
            {
                "kind": "comment",
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "text": row.get("body") or "",
            }
            for row in comments
        ]
        positive_items = [row for row in items if POSITIVE_R18 in row["text"]]
        correction_items = [
            row
            for row in items
            if (
                "FIBERGUARD_R18_NO_PAIRED_ROUTE_VALUE" in row["text"]
                or "FIBERGUARD_R18_CANNOT_CHECK_EXECUTION_SUBJECT_AND_RUN_ABSENT" in row["text"]
            )
            and any(marker in row["text"].lower() for marker in ("retract", "withdraw", "null", "cannot_check", "cannot check"))
        ]
        latest_positive = max((row["created_at"] for row in positive_items), default=None)
        latest_correction = max((row["created_at"] for row in correction_items), default=None)
        corrected = not positive_items or (
            latest_correction is not None
            and latest_positive is not None
            and latest_correction >= latest_positive
        )
        row = {
            "number": number,
            "positive_occurrences": len(positive_items),
            "correction_occurrences": len(correction_items),
            "latest_positive": latest_positive,
            "latest_correction": latest_correction,
            "current_body_sha256": hashlib.sha256((issue.get("body") or "").encode()).hexdigest(),
            "corrected": corrected,
        }
        live_rows.append(row)
        if not corrected:
            live_violations.append(row)

    passed = not local_violations and not live_violations
    result = {
        "schema": "ORION.ORION02.RetractionAudit.R20.v1",
        "terminal": (
            "ORION02_R20_RETRACTION_AUTHORITY_CLOSED"
            if passed
            else "ORION02_R20_RETRACTION_AUTHORITY_VIOLATION"
        ),
        "local_occurrences": local_occurrences,
        "local_violations": local_violations,
        "live_subjects": live_rows,
        "live_violations": live_violations,
        "authority": {
            "former_R18_positive_terminal": "RETRACTED",
            "invalid_R19_diagonal_shortcut": "REVOKED",
            "external_independence": False,
            "novelty": False,
            "journal_authority": False,
        },
    }
    payload = canonical(result) + "\n"
    args.output.write_text(payload)
    print(result["terminal"], hashlib.sha256(payload.encode()).hexdigest())
    if not passed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
