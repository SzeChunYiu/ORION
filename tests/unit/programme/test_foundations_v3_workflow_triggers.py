"""The foundations V3 lane must not fire on archive pushes or audit one-commit slices.

Two trigger defects, both observed on live `archive/*` pushes:

1. The `push:` trigger had no branch filter, so snapshotting a branch to
   `archive/<name>` fired a theory lane that cannot meaningfully audit it.
   Archive pushes are new-branch pushes whose authored delta is a snapshot,
   not a theory change.

2. On any new-branch push GitHub reports `github.event.before` as the
   all-zero SHA. The old fallback `base="$head^"` audited only the tip
   commit diff: a multi-commit branch was audited on 1/N of its authored
   delta. The correct range for a brand-new branch is the merge-base diff
   against the default branch, exactly what the pull_request lane computes.

These tests pin the workflow text structurally (no YAML dependency: CI
installs only `.[dev,candidates]`, which ships no parser).
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "orion-foundations-v3.yml"
ZERO_SHA = "0000000000000000000000000000000000000000"


def _text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def _trigger_block(event: str) -> str:
    """The `on: <event>:` mapping, from its key line to the next `on:`-level key."""
    text = _text()
    start = text.index(f"\n  {event}:")
    on_block_end = text.index("\njobs:")
    for follower in ("pull_request:", "push:", "schedule:", "workflow_dispatch:"):
        candidate = text.find(f"\n  {follower}", start + 1)
        if candidate != -1 and candidate < on_block_end:
            on_block_end = min(on_block_end, candidate)
    return text[start:on_block_end]


def test_push_trigger_ignores_archive_branches() -> None:
    push = _trigger_block("push")
    # Exact indentation pins the ignore list to the push event, not to paths.
    assert "\n    branches-ignore:\n" in push
    assert '\n      - "archive/**"\n' in push


def test_push_trigger_keeps_the_theory_paths_filter() -> None:
    push = _trigger_block("push")
    assert '- "research/orion-foundations-v3/**"' in push
    assert '- ".github/workflows/orion-foundations-v3.yml"' in push


def test_pull_request_trigger_has_no_branch_ignore() -> None:
    # The archive guard is scoped to pushes; the PR lane already audits the
    # merge-base diff and needs no branch filter.
    assert "branches-ignore" not in _trigger_block("pull_request")


def _new_branch_fallback_block() -> str:
    """The `if` branch taken when `github.event.before` is the zero SHA."""
    text = _text()
    marker = f'if [[ -z "$base" || "$base" == "{ZERO_SHA}" ]]; then'
    start = text.index(marker)
    end = text.index("fi", start)
    return text[start : end + len("fi")]


def test_new_branch_fallback_audits_merge_base_against_default_branch() -> None:
    block = _new_branch_fallback_block()
    assert "git fetch origin main" in block
    assert 'base="$(git merge-base origin/main "$head")"' in block


def test_new_branch_fallback_no_longer_audits_only_the_tip_commit() -> None:
    assert 'base="$head^"' not in _text()
