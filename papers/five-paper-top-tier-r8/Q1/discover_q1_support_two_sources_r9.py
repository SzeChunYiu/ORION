#!/usr/bin/env python3
"""Discover and content-bind candidate ORION-Q1 support-two sources.

This script intentionally does not choose the authoritative theorem. It emits a
candidate inventory that the independent proof auditor and portfolio owner must
bind before scientific execution.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

SCHEMA = "ORION.Q1.SupportTwoSourceDiscoveryR9.v1"
PATTERNS = (
    re.compile(r"support[- ]?two", re.IGNORECASE),
    re.compile(r"support\s*(?:<=|≤|at most)\s*2", re.IGNORECASE),
    re.compile(r"support number", re.IGNORECASE),
    re.compile(r"shared[- ]?tag", re.IGNORECASE),
    re.compile(r"TARE", re.IGNORECASE),
)
ALLOWED_SUFFIXES = {".md", ".tex", ".json", ".py", ".toml", ".yaml", ".yml"}
EXCLUDED_PARTS = {".git", ".orion-harness", "node_modules", ".venv", "dist", "build"}


def run(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        args,
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(args)}\n{completed.stderr}")
    return completed.stdout.strip()


def candidate_record(repo: Path, path: Path) -> dict[str, Any] | None:
    relative = path.relative_to(repo)
    if path.suffix.lower() not in ALLOWED_SUFFIXES:
        return None
    if any(part in EXCLUDED_PARTS for part in relative.parts):
        return None
    try:
        data = path.read_bytes()
        text = data.decode("utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    matches: list[dict[str, Any]] = []
    score = 0
    for number, line in enumerate(text.splitlines(), start=1):
        hit_names = [pattern.pattern for pattern in PATTERNS if pattern.search(line)]
        if hit_names:
            score += len(hit_names)
            matches.append({
                "line": number,
                "patterns": hit_names,
                "excerpt": line[:300],
            })
    if not matches:
        return None
    blob_sha = run(repo, "git", "rev-parse", f"HEAD:{relative.as_posix()}")
    return {
        "path": relative.as_posix(),
        "blob_sha": blob_sha,
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "match_score": score,
        "matches": matches[:50],
        "matches_truncated": len(matches) > 50,
    }


def main() -> None:
    here = Path(__file__).resolve()
    repo = Path(run(here.parent, "git", "rev-parse", "--show-toplevel"))
    head = run(repo, "git", "rev-parse", "HEAD")
    branch = run(repo, "git", "branch", "--show-current") or "DETACHED"
    tracked = run(repo, "git", "ls-files").splitlines()
    candidates: list[dict[str, Any]] = []
    for relative in tracked:
        record = candidate_record(repo, repo / relative)
        if record is not None:
            candidates.append(record)
    candidates.sort(key=lambda row: (-int(row["match_score"]), str(row["path"])))
    result = {
        "schema": SCHEMA,
        "repository": "SzeChunYiu/ORION",
        "head_commit": head,
        "checked_out_branch": branch,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "selection_status": "BINDING_REQUIRED",
        "selection_rule": (
            "The independent proof auditor and portfolio owner must jointly select and digest the "
            "authoritative manuscript, definitions, claim ledger, implementation tree, and result manifest."
        ),
        "authority": {
            "discovers_content_bound_candidates": True,
            "selects_authoritative_theorem": False,
            "proves_support_two": False,
            "grants_journal_authority": False,
        },
        "terminal": "Q1_SOURCE_CANDIDATES_DISCOVERED__AUTHORITATIVE_BINDING_REQUIRED",
    }
    output = here.with_name("Q1_SUPPORT_TWO_SOURCE_CANDIDATES_R9.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
