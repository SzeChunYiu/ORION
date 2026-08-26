from __future__ import annotations

import hashlib

import copy
import json
from pathlib import Path

import pytest

from orion.study.p5.freeze import (
    ROOT_CAUSES,
    freeze_protected_suite,
    main,
    ordinal_independence_report,
    ordinal_reading_rules,
    sha256_json,
    validate_protected_suite,
)



def _test_nonce(index: int) -> str:
    """A deterministic nonce with real width, for fixtures only.

    These fixtures used to be `f"{index:064x}"` -- the case ordinal -- which is
    what the shipped PROTECTED_SUITE_V1 did, and why its 24 commitments opened in
    108 SHA-256 evaluations. `validate_protected_suite` now rejects anything below
    2**64, so the fixture has to carry a realistic value.

    A digest of the index is fine *here* because a fixture protects nothing. A
    real suite must use `secrets.token_hex(32)`: a nonce derived from a value the
    candidate can see is guessable by anyone who knows the derivation, which is
    the same failure one step removed.
    """

    return hashlib.sha256(f"p5-fixture-nonce-{index}".encode()).hexdigest()


#: The eight families in an order no declared ordinal rule reads.
#:
#: This fixture used to be `sorted(ROOT_CAUSES)`, which `validate_protected_suite`
#: now rejects and should: with one case per family, "family = alphabetical slot
#: of the ordinal" is free to compute and right eight times out of eight, so every
#: commitment in the frozen packet would open itself. The order below is a fixed
#: shuffle chosen to defeat all twenty-four rules the family declares at this
#: length; `test_the_fixture_order_defeats_every_declared_ordinal_rule` holds it
#: to that, so a future rule that reads this order fails here rather than silently
#: making the fixture the thing under test.
CAUSES = [
    "METHOD_BASIS_GAP",
    "MEASUREMENT_SPECIFICATION_GAP",
    "ENVIRONMENT_DEPENDENCY_TOOL_FAILURE",
    "REPRESENTATION_GAP",
    "EVALUATOR_METRIC_BUG",
    "RETRIEVAL_MISS",
    "ROUTING_PLANNING_MISS",
    "IMPLEMENTATION_BUG",
]
assert set(CAUSES) == set(ROOT_CAUSES)


def _suite() -> dict:
    fresh_payloads = {}
    negative_payloads = {}
    cases = []
    for index, cause in enumerate(CAUSES, start=1):
        fresh_id = f"fresh-{index}"
        negative_id = f"negative-{index}"
        fresh_payload = {
            "secret_marker": f"FRESH_SECRET_{index}",
            "prompt": f"protected fresh task {index}",
        }
        negative_payload = {
            "secret_marker": f"NEGATIVE_SECRET_{index}",
            "outcome": "harmful-or-null-retained",
        }
        fresh_payloads[fresh_id] = fresh_payload
        negative_payloads[negative_id] = negative_payload
        cases.append(
            {
                "case_id": f"p5-c{index:02d}",
                "visible_symptom": "same visible symptom family",
                "candidate_visible_context": {"public_marker": f"PUBLIC_{index}"},
                "protected_root_cause": cause,
                "root_cause_nonce": _test_nonce(index),
                "competing_cause_set": [cause, CAUSES[index % len(CAUSES)]],
                "motivating_tasks": [f"mot-{index}"],
                "replay_tasks": [f"replay-{index}"],
                "fresh_tasks": [
                    {
                        "task_id": fresh_id,
                        "changed_axes": ["TASK", "DATA"],
                        "content_hash": sha256_json(fresh_payload),
                    }
                ],
                "allowed_change_surface": [f"src/allowed/{index}.py"],
                "protected_surface": [f"protected/evaluator/{index}.json"],
                "success_rubric": f"SECRET_SUCCESS_RUBRIC_{index}",
                "harm_rubric": f"SECRET_HARM_RUBRIC_{index}",
                "negative_variant_ids": [negative_id],
            }
        )
    return {
        "schema_version": "orion.p5.protected-hidden-cause-suite.v1",
        "suite_id": "p5-hidden-cause-test-v1",
        "created_before_outcome_access": True,
        "evaluator_hash": "a" * 64,
        "cases": cases,
        "fresh_task_payloads": fresh_payloads,
        "negative_variant_payloads": negative_payloads,
    }


def test_uppercase_digest_is_rejected_as_noncanonical() -> None:
    suite = _suite()
    suite["evaluator_hash"] = "A" * 64

    with pytest.raises(ValueError, match="lowercase SHA-256"):
        freeze_protected_suite(suite)


def test_freeze_covers_all_families_and_emits_content_bound_artifacts() -> None:
    suite = _suite()
    candidate, commitment = freeze_protected_suite(suite)

    assert commitment["root_cause_family_count"] == 8
    assert commitment["case_count"] == 8
    assert commitment["full_protected_suite_hash"] == sha256_json(suite)
    assert commitment["candidate_packet_hash"] == sha256_json(candidate)
    assert len(commitment["motivating_replay_split_hash"]) == 64
    assert len(commitment["fresh_transfer_split_hash"]) == 64
    assert candidate["empirical_authority"] == "NONE"
    assert commitment["empirical_authority"] == "CANNOT_CHECK"


def test_candidate_packet_does_not_leak_protected_truth_fresh_payloads_or_rubrics() -> None:
    candidate, _ = freeze_protected_suite(_suite())
    rendered = json.dumps(candidate, sort_keys=True)

    for cause in ROOT_CAUSES:
        assert cause not in rendered
    assert "FRESH_SECRET_" not in rendered
    assert "NEGATIVE_SECRET_" not in rendered
    assert "SECRET_SUCCESS_RUBRIC_" not in rendered
    assert "SECRET_HARM_RUBRIC_" not in rendered
    assert "protected_root_cause" not in rendered
    assert "fresh_tasks" not in rendered
    assert "protected_surface" not in rendered
    assert "root_cause_nonce" not in rendered


def test_root_commitment_is_not_dictionary_hash_of_eight_public_labels() -> None:
    suite = _suite()
    _, commitment = freeze_protected_suite(suite)
    unsalted = {sha256_json({"protected_root_cause": cause}) for cause in ROOT_CAUSES}

    for case in commitment["cases"]:
        assert case["root_cause_commitment"] not in unsalted


def test_commitment_manifest_does_not_publish_unsalted_private_content_hashes() -> None:
    suite = _suite()
    _, commitment = freeze_protected_suite(suite)
    rendered = json.dumps(commitment, sort_keys=True)

    for payload in suite["fresh_task_payloads"].values():
        assert sha256_json(payload) not in rendered
    for payload in suite["negative_variant_payloads"].values():
        assert sha256_json(payload) not in rendered
    for case in suite["cases"]:
        assert sha256_json(case["success_rubric"]) not in rendered
        assert sha256_json(case["harm_rubric"]) not in rendered
        assert sha256_json(sorted(case["protected_surface"])) not in rendered


def test_fresh_payload_mutation_fails_closed() -> None:
    suite = _suite()
    suite["fresh_task_payloads"]["fresh-1"]["prompt"] = "mutated after freeze declaration"

    with pytest.raises(ValueError, match="fresh payload hash mismatch"):
        freeze_protected_suite(suite)


def test_fresh_transfer_requires_independent_task_domain_model_or_environment_axis() -> None:
    suite = _suite()
    suite["cases"][0]["fresh_tasks"][0]["changed_axes"] = ["DATA", "TOOL"]

    with pytest.raises(ValueError, match="must change TASK, DOMAIN, MODEL, or ENVIRONMENT"):
        freeze_protected_suite(suite)


def test_fresh_ids_cannot_overlap_motivating_or_replay_ids() -> None:
    suite = _suite()
    suite["cases"][0]["fresh_tasks"][0]["task_id"] = "replay-1"
    suite["fresh_task_payloads"]["replay-1"] = suite["fresh_task_payloads"].pop("fresh-1")
    suite["cases"][0]["fresh_tasks"][0]["content_hash"] = sha256_json(
        suite["fresh_task_payloads"]["replay-1"]
    )

    with pytest.raises(ValueError, match="overlap the fresh set"):
        freeze_protected_suite(suite)


def test_fresh_ids_cannot_overlap_nonfresh_ids_in_other_cases() -> None:
    suite = _suite()
    suite["cases"][0]["motivating_tasks"] = ["fresh-2"]

    with pytest.raises(ValueError, match="globally disjoint from fresh task ids"):
        freeze_protected_suite(suite)


def test_missing_root_cause_family_fails_closed() -> None:
    suite = _suite()
    suite["cases"].pop()
    suite["fresh_task_payloads"].pop("fresh-8")
    suite["negative_variant_payloads"].pop("negative-8")

    with pytest.raises(ValueError, match="cover all eight root-cause families"):
        freeze_protected_suite(suite)


def test_negative_variant_must_be_retained_and_referenced() -> None:
    suite = _suite()
    suite["negative_variant_payloads"].pop("negative-1")

    with pytest.raises(ValueError, match="missing retained negative variant payload"):
        freeze_protected_suite(suite)


def test_nonce_reuse_fails_closed() -> None:
    suite = _suite()
    suite["cases"][1]["root_cause_nonce"] = suite["cases"][0]["root_cause_nonce"]

    with pytest.raises(ValueError, match="must be unique"):
        freeze_protected_suite(suite)


def test_allowed_and_protected_write_surfaces_cannot_overlap() -> None:
    suite = _suite()
    suite["cases"][0]["protected_surface"] = suite["cases"][0]["allowed_change_surface"][:]

    with pytest.raises(ValueError, match="overlaps protected_surface"):
        freeze_protected_suite(suite)


def test_cross_case_write_surface_overlap_fails_closed() -> None:
    suite = _suite()
    suite["cases"][0]["allowed_change_surface"] = ["protected/evaluator/2.json"]

    with pytest.raises(ValueError, match="overlaps protected_surface across cases"):
        freeze_protected_suite(suite)


def test_parent_child_write_surface_overlap_fails_closed() -> None:
    suite = _suite()
    suite["cases"][0]["allowed_change_surface"] = ["protected"]
    suite["cases"][0]["protected_surface"] = ["protected/evaluator/model.json"]

    with pytest.raises(ValueError, match="overlaps protected_surface"):
        freeze_protected_suite(suite)


def test_write_surface_path_traversal_fails_closed() -> None:
    suite = _suite()
    suite["cases"][0]["allowed_change_surface"] = ["src/../protected/evaluator"]

    with pytest.raises(ValueError, match="relative non-traversing surface"):
        freeze_protected_suite(suite)


def test_freeze_is_deterministic_for_semantically_identical_json_key_order() -> None:
    first = _suite()
    second = copy.deepcopy(first)
    second = dict(reversed(list(second.items())))

    assert freeze_protected_suite(first) == freeze_protected_suite(second)


def test_cli_writes_only_candidate_and_commitment_outputs(tmp_path: Path) -> None:
    protected_path = tmp_path / "protected.json"
    candidate_path = tmp_path / "candidate.json"
    commitment_path = tmp_path / "commitment.json"
    protected_path.write_text(json.dumps(_suite()), encoding="utf-8")

    assert (
        main(
            [
                "--protected-suite",
                str(protected_path),
                "--candidate-packet",
                str(candidate_path),
                "--commitment",
                str(commitment_path),
            ]
        )
        == 0
    )
    assert candidate_path.exists()
    assert commitment_path.exists()
    assert "FRESH_SECRET_" not in candidate_path.read_text(encoding="utf-8")
    assert "protected_root_cause" not in candidate_path.read_text(encoding="utf-8")


# --- The ordinal is a published field, and the family must not be a function of it.


def _shipped_suite_families() -> list[str]:
    shipped = Path("papers/orion-15-self-orion/evidence/hidden-cause-suite/PROTECTED_SUITE_V1.json")
    cases = json.loads(shipped.read_text(encoding="utf-8"))["cases"]
    return [str(case["protected_root_cause"]) for case in cases]


def _independent_assignment() -> list[str]:
    """Twenty-four cases, three per family, in an order no declared rule reads.

    Found by deterministic search rather than written down, so the search itself
    is the evidence that such orders exist and are not rare -- the guard rejects
    a readable order, not every order.
    """

    multiset = [cause for cause in CAUSES for _ in range(3)]
    for salt in range(2048):
        keyed = sorted(
            enumerate(multiset),
            key=lambda pair: hashlib.sha256(f"{salt}:{pair[0]}".encode()).hexdigest(),
        )
        candidate = [cause for _, cause in keyed]
        if ordinal_independence_report(candidate)["independent"]:
            return candidate
    raise AssertionError("no independent assignment found in 2048 deterministic draws")



def test_the_shipped_suite_ordering_is_refuted_by_a_named_rule() -> None:
    """Refutation capacity: the guard must reject the suite that motivated it.

    PROTECTED_SUITE_V1 is eight families in eight consecutive blocks of three.
    Eight openings buy the block ordering; the remaining sixteen cases follow
    without opening anything. A guard that could not say so would be decoration.
    """

    report = ordinal_independence_report(_shipped_suite_families())

    assert report["rules_recovering_every_predicted_case"] == ["first-appearance/blocks-of-3"]
    assert (report["strongest_rule_correct"], report["strongest_rule_predicted"]) == (16, 16)
    assert report["independent"] is False


def test_a_rule_is_scored_only_on_the_cases_it_was_not_shown() -> None:
    """The openings that instantiate an ordering are not evidence that it works.

    Reading families off their own first appearances reproduces any assignment.
    Charging those positions to the rule is what stops the guard from rejecting
    every suite, including sound ones.
    """

    one_per_family = list(CAUSES)
    by_name = {rule.name: rule for rule in ordinal_reading_rules(one_per_family)}
    first_appearance = by_name["first-appearance/stride-1"]

    assert first_appearance.predicted == tuple(one_per_family)
    assert first_appearance.scored_positions(len(one_per_family)) == ()
    assert first_appearance.recovers(one_per_family) is False


def test_the_fixture_order_defeats_every_declared_ordinal_rule() -> None:
    report = ordinal_independence_report(list(CAUSES))

    assert report["rules_recovering_every_predicted_case"] == []
    assert report["independent"] is True


def test_alphabetical_order_with_one_case_per_family_fails_closed() -> None:
    """The order this fixture used to be in is a free answer key, and is rejected."""

    suite = _suite()
    for case, cause in zip(suite["cases"], sorted(ROOT_CAUSES)):
        case["protected_root_cause"] = cause
        case["competing_cause_set"] = [cause, "METHOD_BASIS_GAP" if cause != "METHOD_BASIS_GAP" else "RETRIEVAL_MISS"]

    with pytest.raises(ValueError, match="hands over every family it was not shown"):
        validate_protected_suite(suite)


def test_emitting_a_sound_suite_in_family_blocks_fails_closed() -> None:
    """Same cases, same nonces, same payloads -- only the emission order changes."""

    suite = _suite()
    validate_protected_suite(suite)

    blocked = copy.deepcopy(suite)
    blocked["cases"] = sorted(
        blocked["cases"], key=lambda case: (case["protected_root_cause"], case["case_id"])
    )

    with pytest.raises(ValueError, match="hands over every family it was not shown"):
        validate_protected_suite(blocked)


def test_a_leak_in_published_order_alone_fails_closed() -> None:
    """The ordinal a candidate reads is the position in the *published* packet.

    ``freeze_protected_suite`` emits cases in sorted ``case_id`` order, so a suite
    whose ``cases`` array is shuffled can still hand the packet an answer key.
    """

    suite = _suite()
    rank = {
        case["case_id"]: index
        for index, case in enumerate(
            sorted(suite["cases"], key=lambda case: case["protected_root_cause"])
        )
    }
    for case in suite["cases"]:
        case["case_id"] = f"p5-c{rank[case['case_id']] + 1:02d}"

    emitted = [case["protected_root_cause"] for case in suite["cases"]]
    published = [
        case["protected_root_cause"]
        for case in sorted(suite["cases"], key=lambda case: case["case_id"])
    ]
    assert ordinal_independence_report(emitted)["independent"] is True
    assert ordinal_independence_report(published)["independent"] is False

    with pytest.raises(ValueError, match="the published case order"):
        validate_protected_suite(suite)


def test_a_family_repeated_inside_a_block_fails_closed() -> None:
    """A realised correlation is a realised leak, whatever drew it."""

    # `CAUSES * 3` is periodic, so a stride rule reads it; start from an order no
    # declared rule reads, then make one swap that puts two cases of one family
    # inside block one. Counts stay even, so the block size stays three.
    assignment = _independent_assignment()
    assert ordinal_independence_report(assignment)["independent"] is True
    duplicate = assignment[0]
    elsewhere = next(
        index for index in range(3, len(assignment)) if assignment[index] == duplicate
    )
    assignment[1], assignment[elsewhere] = assignment[elsewhere], assignment[1]

    report = ordinal_independence_report(assignment)
    assert report["rules_recovering_every_predicted_case"] == []
    assert report["even_block_size"] is not None
    assert report["first_block_repeating_a_family"] == 1
    assert report["independent"] is False


def test_the_rule_family_is_declared_and_every_rule_is_named() -> None:
    rules = ordinal_reading_rules([cause for cause in CAUSES for _ in range(3)])

    assert len(rules) == 40
    assert len({rule.name for rule in rules}) == len(rules)
    assert all(len(rule.predicted) == 24 for rule in rules)
    assert any(rule.name.endswith("/blocks-of-3") for rule in rules)
    assert any(rule.name.startswith("alphabetical/") for rule in rules)
