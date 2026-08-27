#!/usr/bin/env python3
"""Content-bound GitHub audit of the active five-paper blocker programme.

The audit grants no scientific authority. It records exact live GitHub objects,
requires explicit positive receipts for every promotion, and otherwise remains
fail-closed. It is intentionally read-only with respect to scientific branches.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import urllib.request
from typing import Any

REPO = "SzeChunYiu/ORION"
ISSUES = (1377, 1383, 1384, 1385, 1386, 1387, 1416, 1418, 1421)
PRS = (1392, 1394, 1402, 1413, 1419, 1450, 1457, 1461, 1466, 1469, 1471, 1472, 1485, 1486)
BRANCH = "codex/five-paper-top-tier-r8-20260826"


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def api(path: str) -> Any:
    token = os.environ.get("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "ORION-R20-blocker-audit",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/{path}", headers=headers
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def pages(path: str) -> list[Any]:
    result: list[Any] = []
    page = 1
    while True:
        separator = "&" if "?" in path else "?"
        rows = api(f"{path}{separator}per_page=100&page={page}")
        if not isinstance(rows, list):
            raise TypeError(path)
        result.extend(rows)
        if len(rows) < 100:
            return result
        page += 1


def digest_text(text: str | None) -> str:
    return hashlib.sha256((text or "").encode()).hexdigest()


def terminal_tokens(text: str) -> list[str]:
    return sorted(
        set(
            re.findall(
                r"\b(?:FIBERGUARD|NQ|Q1|AB|D|APP|CANNOT|PRODUCTION|CERTIFICATE|ORION)[A-Z0-9_]{5,}\b",
                text or "",
            )
        )
    )


def issue_record(number: int) -> dict[str, Any]:
    issue = api(f"issues/{number}")
    comments = pages(f"issues/{number}/comments")
    return {
        "number": number,
        "title": issue["title"],
        "state": issue["state"],
        "updated_at": issue["updated_at"],
        "body_sha256": digest_text(issue.get("body")),
        "comment_count": len(comments),
        "last_comment": (
            {
                "id": comments[-1]["id"],
                "created_at": comments[-1]["created_at"],
                "body_sha256": digest_text(comments[-1].get("body")),
                "terminal_tokens": terminal_tokens(comments[-1].get("body") or ""),
            }
            if comments
            else None
        ),
        "all_terminal_tokens": terminal_tokens(
            "\n".join([issue.get("body") or ""] + [row.get("body") or "" for row in comments])
        ),
    }


def pr_record(number: int) -> dict[str, Any]:
    pull = api(f"pulls/{number}")
    files = pages(f"pulls/{number}/files")
    comments = pages(f"issues/{number}/comments")
    reviews = pages(f"pulls/{number}/reviews")
    text = "\n".join(
        [pull.get("title") or "", pull.get("body") or ""]
        + [row.get("body") or "" for row in comments]
        + [row.get("body") or "" for row in reviews]
    )
    runs = api(f"actions/runs?head_sha={pull['head']['sha']}&per_page=100")["workflow_runs"]
    return {
        "number": number,
        "title": pull["title"],
        "state": pull["state"],
        "draft": pull["draft"],
        "merged": pull["merged"],
        "mergeable": pull.get("mergeable"),
        "base_ref": pull["base"]["ref"],
        "base_sha": pull["base"]["sha"],
        "head_ref": pull["head"]["ref"],
        "head_sha": pull["head"]["sha"],
        "updated_at": pull["updated_at"],
        "body_sha256": digest_text(pull.get("body")),
        "files": sorted(row["filename"] for row in files),
        "terminal_tokens": terminal_tokens(text),
        "workflow_runs": sorted(
            (
                {
                    "id": row["id"],
                    "name": row["name"],
                    "status": row["status"],
                    "conclusion": row["conclusion"],
                    "event": row["event"],
                }
                for row in runs
            ),
            key=lambda row: (row["name"], row["id"]),
        ),
    }


def contains(records: list[dict[str, Any]], token: str) -> bool:
    return any(token in row["terminal_tokens"] for row in records)


def classify(prs: list[dict[str, Any]], issues: list[dict[str, Any]]) -> dict[str, Any]:
    all_records = prs + issues
    nq_full = contains(all_records, "NQ_CR_B_FULL_REPLAY_PASS") or contains(
        all_records, "NQ_D2_D3_INDEPENDENT_REPLAY_PASS"
    )
    ab_blocked = contains(all_records, "PRODUCTION_REGISTRY_NOT_DECLARED_COMPLETE")
    ab_pass = contains(all_records, "PRODUCTION_EXACT_TRANSFER_PASS") and not ab_blocked
    d_external = contains(all_records, "D_EXTERNAL_DOMAIN_VALIDATION_PASS") or contains(
        all_records, "APP_D_TYPED_AUTHORITY_PREVENTS_REVIEWED_OPERATIONAL_ERROR"
    )
    q1_resource = contains(all_records, "Q1_PRODUCTION_RESOURCE_MAPPING_MATERIAL") or contains(
        all_records, "APP_Q1_PRODUCTION_RESOURCE_MAPPING_MATERIAL"
    )
    c_story = contains(all_records, "FIBERGUARD_R18_NO_PAIRED_ROUTE_VALUE") and contains(
        all_records, "FIBERGUARD_JOINT_ROUTE_R19_REPLACEMENT_PASS"
    ) and contains(all_records, "CERTIFICATE_INVALID")
    return {
        "NQ": {
            "internal_gate": "PASS" if nq_full else "OPEN",
            "required": "full proof-clean CR-B replay over complete registered denominator",
            "external_gate": "OPEN",
        },
        "AB": {
            "internal_gate": "PASS" if ab_pass else "OPEN",
            "blocking_terminal_seen": ab_blocked,
            "required": "content-bound extensional production registry and omission-hostile completeness",
            "external_gate": "OPEN",
        },
        "D": {
            "internal_gate": "PASS" if d_external else "OPEN",
            "required": "independently maintained multi-record integration and external adjudication",
            "external_gate": "OPEN",
        },
        "Q1": {
            "internal_gate": "PASS" if q1_resource else "OPEN",
            "required": "matched current-compiler resource benchmark with routing and synthesis",
            "external_gate": "OPEN",
        },
        "C": {
            "internal_story_gate": "PASS" if c_story else "OPEN",
            "required": "R20 evidence integration and external specialist review",
            "external_gate": "OPEN",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    branch = api(f"branches/{BRANCH.replace('/', '%2F')}")
    issues = [issue_record(number) for number in ISSUES]
    prs = [pr_record(number) for number in PRS]
    result = {
        "schema": "ORION.FivePaper.BlockerAudit.R20.v1",
        "repository": REPO,
        "programme_branch": {"name": BRANCH, "head_sha": branch["commit"]["sha"]},
        "issues": issues,
        "pull_requests": prs,
        "classification": classify(prs, issues),
        "authority": {
            "scientific_promotion": False,
            "external_independence": False,
            "novelty": False,
            "journal_authority": False,
        },
    }
    payload = canonical(result) + "\n"
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(payload)
    print(
        "FIVE_PAPER_BLOCKER_AUDIT_R20_PASS",
        hashlib.sha256(payload.encode()).hexdigest(),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
