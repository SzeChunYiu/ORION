"""The masking intervention must be deterministic, and its gaps must be visible."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

FREEZE = (
    Path(__file__).resolve().parents[3]
    / "papers/orion-11-recursive-epistemic-reconstruction/masking/P1_MASKING_FREEZE_V1.json"
)


def _freeze() -> dict:
    return json.loads(FREEZE.read_text())


def test_freeze_declares_it_predates_scoring() -> None:
    assert _freeze()["outcome_accessed"] is False


def test_selection_is_reproducible_from_the_recorded_rule() -> None:
    """Recompute every mask from the recorded salt and rule; they must match.

    If the recorded rule cannot reproduce the recorded masks, the mask was
    chosen some other way and the freeze does not constrain anything.
    """
    freeze = _freeze()
    rule = freeze["selection_rule"]
    salt, fraction = rule["salt"], rule["mask_fraction"]
    minimum = rule["min_sentences_to_mask"]
    for entry in freeze["entries"]:
        if entry["status"] != "MASKED":
            continue
        count = entry["sentence_count"]
        k = max(1, round(count * fraction))
        ranked = sorted(
            range(count),
            key=lambda i: hashlib.blake2b(
                f"{salt}|{entry['instance_id']}|{i}".encode(), digest_size=8
            ).hexdigest(),
        )
        assert count >= minimum
        assert sorted(ranked[:k]) == entry["masked_indices"]


def test_unmaskable_instances_are_named_not_dropped() -> None:
    """8 instances cannot be masked. They must be a recorded state."""
    freeze = _freeze()
    unmaskable = [e for e in freeze["entries"] if e["status"] == "NOT_MASKABLE"]
    assert unmaskable, "the unmaskable set must be represented explicitly"
    assert len(freeze["entries"]) == freeze["totals"]["instances"]
    assert len(unmaskable) == freeze["totals"]["not_maskable"]
    for entry in unmaskable:
        assert entry["reason"]
        assert "masked_indices" not in entry


def test_the_instruction_is_never_masked() -> None:
    freeze = _freeze()
    assert freeze["masked_field"] == "domain_knowledge"
    assert "task_inst" in freeze["unmasked_fields_and_why"]


def test_every_discipline_survives_masking() -> None:
    """A discipline masked out of existence could not report a discipline result."""
    by_domain = _freeze()["by_domain"]
    assert len(by_domain) == 4
    for domain, counts in by_domain.items():
        assert counts["MASKED"] > 0, domain


def test_budget_is_matched_across_arms() -> None:
    budget = _freeze()["budget"]
    assert budget["identical_model"] is True
    assert budget["identical_tool_access"] is True
    assert budget["max_attempts"] >= 1


def test_arms_include_a_ceiling_and_a_no_reconstruction_control() -> None:
    arms = _freeze()["arms"]
    assert {"unmasked_ceiling", "no_reconstruction", "one_shot_reconstruction",
            "recursive_reconstruction"} <= set(arms)


def test_masked_content_is_recorded_by_hash_not_in_the_clear() -> None:
    """The freeze must not carry the answers it removed."""
    for entry in _freeze()["entries"]:
        if entry["status"] != "MASKED":
            continue
        assert len(entry["masked_text_sha256"]) == 64
        assert "masked_text" not in entry
