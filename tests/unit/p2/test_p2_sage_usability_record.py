"""The audit must distinguish an unusable family from an unofficially-scored one.

An earlier reading of this audit treated SAGE as removed from the paper because
its corpus and evaluator are unpublished. Those two facts are true and are
recorded correctly; what did not follow is that the family is unusable. Its 1200
queries and their gold are obtainable, and short-form alone is the largest
external task set this paper has. These tests keep the two questions separate, so
neither the pessimistic nor the optimistic reading can be reached by accident
again.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "orion-12-open-world-scientific-discovery"
AUDIT_PATH = PAPER / "protocol" / "EXTERNAL_ACCESS_AUDIT_V1.json"
PROTOCOL_PATH = PAPER / "protocol" / "PROTOCOL_V1.json"


def _audit() -> dict:
    return json.loads(AUDIT_PATH.read_text(encoding="utf-8"))


def test_usability_block_answers_for_every_protocol_task_family():
    audit = _audit()
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    block = audit["usable_task_family_under_declared_deviation"]
    assert set(block["families"]) == set(protocol["task_families"]), (
        "usability must be answered for exactly the protocol's task families"
    )
    for family, verdict in block["families"].items():
        assert verdict in block["enum"], f"{family}: undeclared usability verdict {verdict!r}"


def test_official_runnability_and_usability_are_separate_axes():
    """The whole point: unusable is a stronger claim than not-officially-scorable."""

    audit = _audit()
    official = audit["official_evaluation_runnable_by_family"]["families"]
    usable = audit["usable_task_family_under_declared_deviation"]["families"]
    assert official["sage_scientific_retrieval"] == "NO_ARTIFACT_MISSING"
    assert usable["sage_scientific_retrieval"] == "USABLE_WITH_DECLARED_SCORING"
    # No family may be officially runnable while being marked unusable — that
    # combination would be incoherent rather than merely pessimistic.
    for family, verdict in official.items():
        if verdict.startswith("YES"):
            assert usable[family] != "NOT_USABLE", (
                f"{family}: officially runnable but marked unusable"
            )


def test_sage_detail_records_what_exists_what_is_missing_and_the_n():
    audit = _audit()
    detail = audit["usable_task_family_under_declared_deviation"]["sage_scientific_retrieval_detail"]

    obtainable = detail["obtainable"]
    assert obtainable["short_form_records"] == 600
    assert obtainable["open_ended_records"] == 600
    assert "complete_query" in obtainable["short_form_fields"]
    assert any("ground_truth" in field for field in obtainable["short_form_fields"])
    assert "parsed" in obtainable["verified_by"], (
        "the counts must be attributed to parsing the files, not to the README"
    )

    missing = detail["missing"]
    for key in ("retrieval_corpus", "official_evaluator", "open_ended_tier_weights"):
        assert missing[key].strip(), f"{key} must state what is missing and why it matters"

    # The reason this family is worth keeping has to be recorded, not implied.
    assert "TIER_B" in detail["consequence_for_statistics"]
    assert "600" in detail["consequence_for_statistics"]
    # And the reason it is dangerous has to survive the good news.
    contamination = detail["consequence_for_contamination"].lower()
    assert "contamination" in contamination and "measure" in contamination
    assert detail["redistribution"].lower().startswith("still blocked")


def test_the_correction_of_the_correction_is_on_the_record():
    """A wrong orchestrator claim is retracted in the artifact, not just in chat."""

    audit = _audit()
    entries = [
        item
        for item in audit.get("revision_history", [])
        if "correction_of_a_correction" in item
    ]
    assert entries, "the retraction must be recorded in revision_history"
    text = entries[-1]["correction_of_a_correction"]
    assert "777" in text and "11 tree entries" in text, (
        "the retraction must name the specific claim it withdraws"
    )
