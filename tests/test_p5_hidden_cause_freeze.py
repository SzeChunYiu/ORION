from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from orion.study.p5.freeze import ROOT_CAUSES, freeze_protected_suite, main, sha256_json


CAUSES = sorted(ROOT_CAUSES)


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
                "root_cause_nonce": f"{index:064x}",
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
