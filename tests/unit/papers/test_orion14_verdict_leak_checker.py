"""The verdict-leak checker must point at the battery in force, and keep its teeth.

`ATTACK_MANIFEST_V1.jsonl` leaks its verdict in three INSUFFICIENT_EVIDENCE cases
and is deliberately never repaired: the supersession note is explicit that a
benchmark whose construction is repaired is a new benchmark, and the old one has
to stay a reproducible record of what was measured. V2 is that repair.

With the default pointed at V1, the checker reported FAIL forever -- on a battery
nobody scores, for a leak already found and fixed. A red that can never go green
stops being read, which is worse than no check at all.

Three exit codes, three different worlds: 0 clean, 1 a real leak, 2 could not
decide.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = ROOT / "papers/orion-14-verified-scientific-discovery/protocol"
CHECKER = PROTOCOL / "check_verdict_leak_v1.py"
V1 = PROTOCOL / "ATTACK_MANIFEST_V1.jsonl"
V2 = PROTOCOL / "ATTACK_MANIFEST_V2.jsonl"

LEAKING_CASES = (
    "P4-INSUFFICIENT_EVIDENCE-001",
    "P4-INSUFFICIENT_EVIDENCE-002",
    "P4-INSUFFICIENT_EVIDENCE-003",
)


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _cases(path: Path) -> dict[str, dict]:
    return {
        json.loads(line)["case_id"]: json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def test_the_default_battery_is_clean() -> None:
    result = _run()
    assert result.returncode == 0, result.stdout + result.stderr
    assert "clean" in result.stdout
    assert "ATTACK_MANIFEST_V2.jsonl" in result.stdout


def test_the_clean_verdict_reports_its_own_control() -> None:
    """A pass that does not say what would have failed is not evidence."""

    assert "control: 3 leaks still detected" in _run().stdout


def test_the_frozen_historical_battery_still_fails() -> None:
    """V1 is preserved as it was scored. If it ever passes, something rewrote it."""

    result = _run("--manifest", str(V1))
    assert result.returncode == 1
    assert "3/39 cases state the verdict" in result.stdout
    for case_id in LEAKING_CASES:
        assert case_id in result.stdout


def test_v2_repairs_only_the_verdict_sentence() -> None:
    """The supersession note claims a pure suffix trim. Check it rather than trust it."""

    v1, v2 = _cases(V1), _cases(V2)
    assert set(v1) == set(v2)
    changed = [k for k in v1 if v1[k] != v2[k]]
    assert sorted(changed) == sorted(LEAKING_CASES)

    for case_id in LEAKING_CASES:
        before, after = v1[case_id], v2[case_id]
        # Only the visible evidence text and the recomputed hash may differ.
        assert {
            key for key in set(before) | set(after) if before.get(key) != after.get(key)
        } == {"candidate_visible", "artifact_hash"}
        vis_before, vis_after = before["candidate_visible"], after["candidate_visible"]
        assert {
            key
            for key in set(vis_before) | set(vis_after)
            if vis_before.get(key) != vis_after.get(key)
        } == {"evidence_text"}
        # A pure tail deletion: nothing was reworded, only the verdict removed.
        assert vis_before["evidence_text"].startswith(vis_after["evidence_text"])
        removed = vis_before["evidence_text"][len(vis_after["evidence_text"]) :]
        assert "insufficient" in removed.lower()


@pytest.mark.parametrize("manifest", [V1, V2])
def test_every_artifact_hash_recomputes(manifest: Path) -> None:
    """Hand-edited cases with stale hashes would make either battery unciteable."""

    import hashlib

    for case in _cases(manifest).values():
        body = {k: v for k, v in case.items() if k != "artifact_hash"}
        digest = hashlib.sha256(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        assert digest == case["artifact_hash"], case["case_id"]


def test_a_broken_phrase_list_yields_cannot_check_not_a_pass(tmp_path: Path) -> None:
    """The failure this guards against: the checker goes green by losing its teeth.

    Validated against the real batteries, not a fixture -- gut the three phrases
    that catch the historical leak and the clean verdict must become exit 2.
    """

    source = CHECKER.read_text(encoding="utf-8")
    gutted = source
    for phrase in (
        'r"is genuinely insufficient",',
        'r"is insufficient to support",',
        'r"evidence is insufficient",',
    ):
        assert phrase in gutted, phrase
        gutted = gutted.replace(phrase, "")

    copy = PROTOCOL / "_check_verdict_leak_gutted_tmp.py"
    copy.write_text(gutted, encoding="utf-8")
    try:
        result = subprocess.run(
            [sys.executable, str(copy)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        assert result.returncode == 2, result.stdout + result.stderr
        assert "CANNOT_CHECK" in result.stderr
        assert "proves nothing" in result.stderr
    finally:
        copy.unlink()
