"""No rule that ignores the evidence may classify the battery perfectly.

P4's H3 returned `correct_cannot_check_rate` 1.0 for all eleven panel systems.
The cause was in the battery, not the systems: `INSUFFICIENT_EVIDENCE` was
constructed by emitting an *empty* evidence list, and every other family carried
exactly one evidence object. So

    predict CANNOT_CHECK iff len(evidence) == 0

classified all 420 cases correctly. Detecting an empty list is not judgement, so
every system scored 1.0 and H3 could not have observed a difference had one
existed.

The repair keeps the gold terminal and changes what must be reasoned about. Two
subtypes, fifteen each:

* **A -- no support anywhere.** Evidence is present and was read; it does not
  establish the claim, and nothing in the pool does. One step from
  `POOLED_SUPPORT_WRONG_OWNER`, which is identical except that support *does*
  exist elsewhere and the terminal is `BLOCK`.
* **B -- support present, authenticity undecidable.** The record carries its
  `SUPPORT::` token but no declared hash, so it can be neither confirmed nor
  refuted. Distinct from `CONTENT_SUBSTITUTION`, where the hashes disagree,
  tampering is *provable*, and the terminal is `BLOCK`.

Subtype B exists because A alone left a second perfect rule: with insufficiency
the only reason support could be absent, "no `SUPPORT::` token in the pool"
classified at 420/420 too. Fixing one shortcut and shipping without re-checking
for others is how a benchmark keeps its ceiling.

These tests are generator-level and run the real generator, so they measure the
battery a campaign would actually receive rather than a fixture standing in for
it.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
GENERATOR = (
    ROOT / "papers" / "paper-04-verified-scientific-discovery" / "host" / "generate_protected_cases.py"
)
ZERO = "0" * 64


@pytest.fixture(scope="module")
def battery() -> tuple[list[dict], dict[str, dict]]:
    """Generate a real battery once and reuse it across the checks."""

    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "battery"
        completed = subprocess.run(
            [
                sys.executable, str(GENERATOR),
                "--output-dir", str(out),
                "--seed", "20260818",
                "--subject-commit", commit,
                "--subject-archive-sha256", ZERO,
                "--evaluator-artifact-sha256", ZERO,
                "--baseline-config-sha256", ZERO,
                "--host-run-id", "pytest-headroom",
                "--evaluation-epoch", "2026-08-18T00:00:00Z",
            ],
            cwd=ROOT, capture_output=True, text=True, timeout=300,
        )
        assert completed.returncode == 0, completed.stderr[-2000:]
        protected = [
            json.loads(line)
            for line in (out / "protected_manifest.jsonl").read_text().splitlines()
            if line.strip()
        ]
        visible = {
            json.loads(line)["case_id"]: json.loads(line)["candidate_visible"]
            for line in (out / "candidate_manifest.jsonl").read_text().splitlines()
            if line.strip()
        }
    return protected, visible


#: Rules a system could apply without reasoning about whether evidence supports a
#: claim. None may be a perfect classifier for the CANNOT_CHECK terminal.
SHORTCUTS = {
    "evidence list is empty": lambda v: not (v.get("evidence") or []),
    "retrieval pool is empty": lambda v: not (v.get("retrieval_pool") or []),
    "no evidence was used": lambda v: not (v.get("behavioral_trace") or {}).get("used_evidence_ids"),
    "pool contains no SUPPORT token": lambda v: not any(
        "SUPPORT::" in str(e.get("content", "")) for e in (v.get("retrieval_pool") or [])
    ),
    "some record lacks a declared hash": lambda v: any(
        e.get("declared_content_hash") is None for e in (v.get("retrieval_pool") or [])
    ),
}


def test_no_evidence_free_shortcut_classifies_the_battery(battery) -> None:
    protected, visible = battery
    perfect = []
    for name, rule in SHORTCUTS.items():
        hits = sum(
            1
            for p in protected
            if rule(visible[p["case_id"]])
            == (p["protected_gold"]["expected_authority_terminal"] == "CANNOT_CHECK")
        )
        if hits == len(protected):
            perfect.append(name)
    assert not perfect, (
        f"these rules classify all {len(protected)} cases without judging support: "
        f"{perfect}. A system implementing one scores correct_cannot_check_rate 1.0 "
        f"without reasoning, which is what flattened H3."
    )


def test_both_insufficiency_subtypes_are_present_and_balanced(battery) -> None:
    """One subtype alone leaves a perfect rule; the pair is what removes it."""

    protected, visible = battery
    cases = [p for p in protected if p["attack_family"] == "INSUFFICIENT_EVIDENCE"]
    assert cases, "the INSUFFICIENT_EVIDENCE family disappeared"

    no_support = unverifiable = 0
    for case in cases:
        pool = visible[case["case_id"]].get("retrieval_pool") or []
        assert pool, f"{case['case_id']} has an empty pool; that is the defect being repaired"
        record = pool[0]
        has_support = "SUPPORT::" in str(record.get("content", ""))
        undecidable = record.get("declared_content_hash") is None
        if has_support and undecidable:
            unverifiable += 1
        elif not has_support and not undecidable:
            no_support += 1
        else:
            pytest.fail(f"{case['case_id']} is neither subtype cleanly")

    assert no_support and unverifiable, (
        f"both subtypes must be populated (no-support={no_support}, "
        f"unverifiable={unverifiable}); a single subtype reinstates a perfect rule"
    )
    assert abs(no_support - unverifiable) <= 1, (
        f"subtypes are unbalanced ({no_support} vs {unverifiable})"
    )


def test_the_repair_did_not_move_any_gold_label(battery) -> None:
    """Changing what must be judged must not change what the answer is."""

    protected, _ = battery
    assert len(protected) == 420, f"battery size changed to {len(protected)}"
    terminals: dict[str, int] = {}
    for case in protected:
        terminals[case["protected_gold"]["expected_authority_terminal"]] = (
            terminals.get(case["protected_gold"]["expected_authority_terminal"], 0) + 1
        )
    assert terminals == {"BLOCK": 330, "PROMOTE": 60, "CANNOT_CHECK": 30}, terminals
    insufficient = [p for p in protected if p["attack_family"] == "INSUFFICIENT_EVIDENCE"]
    assert all(
        p["protected_gold"]["semantic_support"] == "INSUFFICIENT" for p in insufficient
    )
    assert all(
        p["protected_gold"]["expected_authority_terminal"] == "CANNOT_CHECK"
        for p in insufficient
    )


def test_other_families_were_not_disturbed(battery) -> None:
    """The repair is confined to one family."""

    protected, visible = battery
    for case in protected:
        if case["attack_family"] == "INSUFFICIENT_EVIDENCE":
            continue
        count = len(visible[case["case_id"]].get("evidence") or [])
        assert count == 1, (
            f"{case['case_id']} ({case['attack_family']}) now carries {count} evidence "
            f"objects; the repair should not have touched it"
        )
