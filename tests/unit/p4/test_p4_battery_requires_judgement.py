"""No rule that ignores the evidence may classify the battery perfectly.

P4's H3 returned `correct_cannot_check_rate` 1.0 for all eleven panel systems.
The cause was in the battery, not the systems: `INSUFFICIENT_EVIDENCE` was
constructed by emitting an *empty* evidence list, and every other family carried
exactly one evidence object, so

    predict CANNOT_CHECK iff len(evidence) == 0

classified all 420 cases. That was repaired once, and the repair shipped a second
cue: `len(evidence[0]["content"])` took five values across the battery and two of
them occurred only on `CANNOT_CHECK` cases. Both are recorded under
`research/failures/2026-08-label-recoverable-from-construction-cue/`.

The construction the generator now emits by default is the second repair, frozen
in `research/campaigns/2026-08-21-p4-battery-v3-identifiable/FREEZE.md`. Its
governing property is that every case in the battery is shape-identical and
families differ only in the values of fields a hard gate is defined over: one
body template for all 840 records, a `SUPPORT::` marker on every one of them so
its presence carries nothing, fixed container lengths, and no nulls anywhere.

`CANNOT_CHECK` is two subtypes, fifteen each, shape-identical to each other and
to `POOLED_SUPPORT_WRONG_OWNER`:

* **A -- nothing supports the claim.** The assigned record carries a token that
  is not the claim's, and neither does the peer.
* **B -- support exists, from a third party.** The assigned record still does not
  support the claim; the peer does, and belongs to neither the cited source nor
  the claim.

`POOLED_SUPPORT_WRONG_OWNER` is the `BLOCK` case one step away: its assigned
record also fails to support, and is additionally mis-owned. So neither "nothing
in the pool supports" nor "the assigned record does not support" classifies the
family, and separating `CANNOT_CHECK` from `BLOCK` requires reading ownership as
well as support.

These tests are generator-level and run the real generator through its command
line, so they measure the battery a campaign would actually receive rather than a
fixture standing in for it. The exhaustive probe register lives next door in
`test_p4_promotion_cue_identifiability.py`; this file is the cheap standing guard.
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
    ROOT / "papers" / "orion-14-verified-scientific-discovery" / "host" / "generate_protected_cases.py"
)
ZERO = "0" * 64

#: The generator only requires a well-formed commit id, and a fixed one keeps the
#: test hermetic --- it neither shells out to git nor changes what it measures
#: when HEAD moves.
SUBJECT_COMMIT = "f6e51b5c8f905382b8e2f5568d9035fc14241aa1"


@pytest.fixture(scope="module")
def battery() -> tuple[list[dict], dict[str, dict]]:
    """Generate a real battery once, at the generator's default construction."""

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "battery"
        completed = subprocess.run(
            [
                sys.executable, str(GENERATOR),
                "--output-dir", str(out),
                "--seed", "20260818",
                "--subject-commit", SUBJECT_COMMIT,
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
        manifest = json.loads((out / "RUN_MANIFEST_V1.json").read_text())
    return protected, visible, manifest


def _supports(view: dict, record: dict) -> bool:
    return f"SUPPORT::{view['claim']['support_token']}" in str(record.get("content", ""))


#: Rules a system could apply without reasoning about whether evidence supports a
#: claim. None may be a perfect classifier for the CANNOT_CHECK terminal. The last
#: two are not judgement-free --- they read the support token --- and are here
#: because a family that *one* semantic rule classifies is barely better than one
#: a character count classifies.
SHORTCUTS = {
    "evidence list is empty": lambda v: not (v.get("evidence") or []),
    "retrieval pool is empty": lambda v: not (v.get("retrieval_pool") or []),
    "no evidence was used": lambda v: not (v.get("behavioral_trace") or {}).get("used_evidence_ids"),
    "pool contains no SUPPORT marker": lambda v: not any(
        "SUPPORT::" in str(e.get("content", "")) for e in (v.get("retrieval_pool") or [])
    ),
    "some record lacks a declared hash": lambda v: any(
        e.get("declared_content_hash") is None for e in (v.get("retrieval_pool") or [])
    ),
    "the evidence body has an unusual length": lambda v: len(
        str((v.get("evidence") or [{}])[0].get("content", ""))
    ) != 98,
    "nothing in the pool supports the claim": lambda v: not any(
        _supports(v, e) for e in (v.get("retrieval_pool") or [])
    ),
    "the assigned record does not support the claim": lambda v: not _supports(
        v, (v.get("evidence") or [{}])[0]
    ),
}


def test_the_default_construction_is_the_audited_one(battery) -> None:
    """A leaking construction must not be what a campaign gets by default.

    Both previous constructions remain selectable so the batteries whose results
    are already published stay reproducible. Neither may be what you get by
    forgetting to pass a flag.
    """

    _, _, manifest = battery
    assert manifest["case_construction"] == "v3", (
        f"the generator now defaults to {manifest['case_construction']!r}; v1 and v2 "
        f"both have a measured cue that recovers the CANNOT_CHECK label"
    )


def test_no_evidence_free_shortcut_classifies_the_battery(battery) -> None:
    protected, visible, _ = battery
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


def test_the_battery_is_shape_uniform(battery) -> None:
    """The property the repair is built on, checked on the emitted artifact.

    A character count separated V2's families. Here there is one length, one key
    tuple, one container size per field, and no nulls, so there is nothing for a
    character count to separate.
    """

    protected, visible, _ = battery
    lengths, keys, shapes = set(), set(), set()
    for case in protected:
        view = visible[case["case_id"]]
        pool = view["retrieval_pool"]
        shapes.add(
            (
                len(view["evidence"]),
                len(pool),
                len(view["behavioral_trace"]["used_evidence_ids"]),
                len(view["access_requests"]),
                len(view["search_trace"]),
                len({item["source_id"] for item in pool}),
            )
        )
        keys.add(tuple(view))
        for record in pool:
            lengths.add(len(record["content"]))
            keys.add(tuple(record))
            assert record["declared_content_hash"] is not None, case["case_id"]
            assert record["declared_provenance_hash"] is not None, case["case_id"]
    assert lengths == {98}, f"evidence bodies take lengths {sorted(lengths)}"
    assert shapes == {(1, 2, 1, 2, 1, 2)}, f"container shapes vary: {sorted(shapes)}"
    assert len(keys) == 2, "the view and the evidence object each have one key tuple"


def test_both_insufficiency_subtypes_are_present_and_balanced(battery) -> None:
    """One subtype alone leaves a perfect rule; the pair is what removes it."""

    protected, visible, _ = battery
    cases = [p for p in protected if p["attack_family"] == "INSUFFICIENT_EVIDENCE"]
    assert cases, "the INSUFFICIENT_EVIDENCE family disappeared"

    no_support = third_party = 0
    for case in cases:
        view = visible[case["case_id"]]
        pool = view["retrieval_pool"]
        assert len(pool) == 2, f"{case['case_id']} lost its peer record"
        assigned, peer = pool
        assert not _supports(view, assigned), (
            f"{case['case_id']}: the assigned record must not support the claim"
        )
        assert assigned["source_id"] == assigned["assigned_source_id"], (
            f"{case['case_id']}: a mis-owned assigned record is POOLED_SUPPORT_WRONG_OWNER, "
            f"which is BLOCK"
        )
        if _supports(view, peer):
            assert peer["source_id"] != assigned["source_id"]
            third_party += 1
        else:
            no_support += 1

    assert no_support and third_party, (
        f"both subtypes must be populated (no-support={no_support}, "
        f"third-party={third_party}); a single subtype reinstates a perfect rule"
    )
    assert abs(no_support - third_party) <= 1, (
        f"subtypes are unbalanced ({no_support} vs {third_party})"
    )


def test_the_neighbouring_block_family_is_one_field_away(battery) -> None:
    """What makes the family require judgement rather than a lookup.

    ``POOLED_SUPPORT_WRONG_OWNER`` presents the same shape and the same
    non-supporting assigned record. It is ``BLOCK`` because that record is
    mis-owned, and telling the two apart is reading ownership --- an obligation ---
    rather than reading a count, a length or a null.
    """

    protected, visible, _ = battery
    pooled = [p for p in protected if p["attack_family"] == "POOLED_SUPPORT_WRONG_OWNER"]
    assert len(pooled) == 30
    for case in pooled:
        view = visible[case["case_id"]]
        assigned = view["retrieval_pool"][0]
        assert not _supports(view, assigned)
        assert assigned["source_id"] != assigned["assigned_source_id"]
        assert case["protected_gold"]["expected_authority_terminal"] == "BLOCK"


def test_the_repair_did_not_move_any_gold_label(battery) -> None:
    """Changing what must be judged must not change what the answer is."""

    protected, _, _ = battery
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
    """The repair is uniform: no family carries a container the others do not."""

    protected, visible, _ = battery
    for case in protected:
        if case["attack_family"] == "INSUFFICIENT_EVIDENCE":
            continue
        count = len(visible[case["case_id"]].get("evidence") or [])
        assert count == 1, (
            f"{case['case_id']} ({case['attack_family']}) now carries {count} evidence "
            f"objects; every family carries exactly one"
        )
