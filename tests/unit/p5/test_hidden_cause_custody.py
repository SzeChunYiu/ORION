"""The P5 hidden-cause suite audited against the artifact it actually ships.

An instrument that only ever runs on its own fixture is the failure it was
written to catch, so the shipped
``evidence/hidden-cause-suite/PROTECTED_SUITE_V1.json`` is loaded here and the
measured numbers in the failure record are pinned as assertions.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from orion.programme.benchmark_identifiability import CaseSplit
from orion.programme.commitment_custody import CustodyReason
from orion.programme.records import Outcome
from orion.study.p5.freeze import ROOT_CAUSES, freeze_protected_suite, sha256_json
from orion.study.p5.hidden_cause_custody import (
    FREEZE_CANARY,
    P5_DISCLOSURE_PROBES,
    SHIPPED_SUITE_PATH,
    audit_hidden_cause_suite,
    audit_root_cause_identifiability,
    audit_suite_custody,
    default_fit_case_ids,
    extract_hidden_cause_cues,
    labelled_case,
    main,
    root_cause_commitment,
    sealed_root_causes,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FAMILIES = sorted(ROOT_CAUSES)


@pytest.fixture(scope="module")
def shipped_cases() -> list[dict[str, Any]]:
    suite = json.loads((REPO_ROOT / SHIPPED_SUITE_PATH).read_text(encoding="utf-8"))
    return list(suite["cases"])


def _freezable_suite(nonces: list[str], families: list[str]) -> dict[str, Any]:
    """A suite that passes ``validate_protected_suite``, parameterised by its nonces.

    The shipped suite does not validate --- its ``fresh_task_payloads`` map is
    empty and every ``content_hash`` is the literal string
    ``placeholder_hash_for_fresh_task_NNN`` --- so the binding between this
    module's modelled scheme and the real freeze has to be shown on a suite the
    validator accepts. The nonces are the only thing that varies between the
    leaking and the repaired variants.
    """

    cases = []
    fresh_payloads: dict[str, Any] = {}
    negative_payloads: dict[str, Any] = {}
    for index, (nonce, family) in enumerate(zip(nonces, families, strict=True), start=1):
        task_id = f"fresh-{index:03d}"
        variant_id = f"negative-{index:03d}"
        fresh_payloads[task_id] = {"task_id": task_id}
        negative_payloads[variant_id] = {"variant_id": variant_id}
        cases.append(
            {
                "case_id": f"P5-HC-{index:03d}",
                "visible_symptom": f"symptom {index}",
                "candidate_visible_context": {"system": f"system-{index}"},
                "protected_root_cause": family,
                "root_cause_nonce": nonce,
                "competing_cause_set": [family]
                + [other for other in FAMILIES if other != family][:2],
                "motivating_tasks": [f"motivating-{index:03d}"],
                "replay_tasks": [f"replay-{index:03d}"],
                "fresh_tasks": [
                    {
                        "task_id": task_id,
                        "changed_axes": ["TASK"],
                        "content_hash": sha256_json(fresh_payloads[task_id]),
                    }
                ],
                "allowed_change_surface": [f"src/candidate/{index:03d}.py"],
                "protected_surface": [f"protected/evaluator/{index:03d}.json"],
                "success_rubric": f"SECRET_SUCCESS_{index:03d}",
                "harm_rubric": f"SECRET_HARM_{index:03d}",
                "negative_variant_ids": [variant_id],
            }
        )
    return {
        "schema_version": "orion.p5.protected-hidden-cause-suite.v1",
        "suite_id": "custody-fixture",
        "created_before_outcome_access": True,
        "evaluator_hash": "b" * 64,
        "cases": cases,
        "fresh_task_payloads": fresh_payloads,
        "negative_variant_payloads": negative_payloads,
    }


def _high_entropy_nonce(index: int) -> str:
    return hashlib.sha256(f"withheld-seed|{index}".encode()).hexdigest()


class TestSchemeBinding:
    def test_the_modelled_scheme_matches_what_the_real_freeze_publishes(self) -> None:
        # The audit models freeze._root_commitment rather than importing it. If
        # that model drifts, every probe opens nothing and the suite reads as
        # protected, so the binding is pinned against a live freeze.
        nonces = [_high_entropy_nonce(index) for index in range(1, 9)]
        suite = _freezable_suite(nonces, FAMILIES)
        _, manifest = freeze_protected_suite(suite)
        for case, nonce, family in zip(manifest["cases"], nonces, FAMILIES, strict=True):
            assert case["root_cause_commitment"] == root_cause_commitment(family, nonce)

    def test_the_canary_is_a_digest_the_real_freeze_would_emit(self) -> None:
        nonces = [_high_entropy_nonce(index) for index in range(1, 9)]
        nonces[FAMILIES.index(FREEZE_CANARY.secret)] = FREEZE_CANARY.nonce
        suite = _freezable_suite(nonces, FAMILIES)
        _, manifest = freeze_protected_suite(suite)
        emitted = {
            case["case_id"]: case["root_cause_commitment"] for case in manifest["cases"]
        }
        canary_case = f"P5-HC-{FAMILIES.index(FREEZE_CANARY.secret) + 1:03d}"
        assert emitted[canary_case] == FREEZE_CANARY.digest
        assert FREEZE_CANARY.reproduced_by(root_cause_commitment)


class TestShippedSuiteDefect:
    def test_every_opening_nonce_is_the_case_ordinal(self, shipped_cases) -> None:
        assert [int(case["root_cause_nonce"], 16) for case in shipped_cases] == list(
            range(1, len(shipped_cases) + 1)
        )

    def test_the_validator_accepts_those_nonces(self, shipped_cases) -> None:
        # validate_protected_suite rejects exactly one nonce value out of 2^256,
        # which is why the leak survives nine fail-closed conditions.
        nonces = [f"{index:064x}" for index in range(1, 9)]
        freeze_protected_suite(_freezable_suite(nonces, FAMILIES))

    def test_the_gold_label_is_the_case_ordinal_divided_by_three(self, shipped_cases) -> None:
        prompt_order = [
            "RETRIEVAL_MISS",
            "ROUTING_PLANNING_MISS",
            "IMPLEMENTATION_BUG",
            "ENVIRONMENT_DEPENDENCY_TOOL_FAILURE",
            "EVALUATOR_METRIC_BUG",
            "REPRESENTATION_GAP",
            "MEASUREMENT_SPECIFICATION_GAP",
            "METHOD_BASIS_GAP",
        ]
        recovered = sum(
            prompt_order[(index - 1) // 3] == case["protected_root_cause"]
            for index, case in enumerate(shipped_cases, start=1)
        )
        assert recovered == 24


class TestCommitmentCustody:
    def test_the_shipped_suite_discloses_every_root_cause(self, shipped_cases) -> None:
        audit = audit_suite_custody(shipped_cases)
        assert audit.outcome is Outcome.FAIL
        assert audit.reason is CustodyReason.SECRET_DISCLOSED
        assert audit.worst_disclosure_rate == 1.0
        assert audit.blocks

    def test_the_ordinal_probe_opens_all_24_in_108_digests(self, shipped_cases) -> None:
        audit = audit_suite_custody(shipped_cases)
        attempts = {item.probe_id: item for item in audit.attempts}
        ordinal = attempts["ordinal-nonce"]
        assert (ordinal.disclosed, ordinal.sealed) == (24, 24)
        assert ordinal.digests_computed == 108
        assert attempts["small-integer-nonce"].disclosed == 24

    def test_the_probe_set_is_not_all_positive(self, shipped_cases) -> None:
        # A probe set that opens everything cannot distinguish a leaking manifest
        # from an over-eager instrument, so two probes are kept that recover none.
        audit = audit_suite_custody(shipped_cases)
        attempts = {item.probe_id: item for item in audit.attempts}
        assert attempts["constant-nonce"].disclosed == 0
        assert attempts["case-id-digest-nonce"].disclosed == 0

    def test_high_entropy_nonces_withhold_the_same_labels(self, shipped_cases) -> None:
        repaired = [
            dict(case, root_cause_nonce=_high_entropy_nonce(index))
            for index, case in enumerate(shipped_cases, start=1)
        ]
        audit = audit_suite_custody(repaired)
        assert audit.outcome is Outcome.PASS
        assert audit.reason is CustodyReason.WITHHELD_UNDER_ENUMERATION
        assert audit.worst_disclosure_rate == 0.0

    def test_sealed_secrets_carry_the_published_domain_and_order(self, shipped_cases) -> None:
        secrets = sealed_root_causes(shipped_cases)
        assert len(secrets) == 24
        assert secrets[0].ordinal == 1 and secrets[-1].ordinal == 24
        assert secrets[0].domain == tuple(FAMILIES)
        assert secrets[0].domain_size == 8

    def test_every_registered_probe_states_its_cost(self) -> None:
        assert len(P5_DISCLOSURE_PROBES) == 4
        assert all(probe.cost_rationale.strip() for probe in P5_DISCLOSURE_PROBES)


class TestRootCauseIdentifiability:
    def test_cues_read_only_the_construction(self, shipped_cases) -> None:
        cues = extract_hidden_cause_cues(shipped_cases[7])
        assert cues == {
            "case_ordinal_block": 2,
            "nonce_ordinal_block": 2,
            "visible_context_key_count": 3,
        }

    def test_the_default_fit_split_is_one_case_per_family(self, shipped_cases) -> None:
        fit = default_fit_case_ids(shipped_cases)
        assert len(fit) == 8
        assert fit == frozenset(f"P5-HC-{index:03d}" for index in (1, 4, 7, 10, 13, 16, 19, 22))

    def test_every_family_is_recovered_from_the_ordinal_alone(self, shipped_cases) -> None:
        for family in FAMILIES:
            audit = audit_root_cause_identifiability(shipped_cases, label=family)
            assert audit.outcome is Outcome.FAIL, family
            assert audit.worst_recovery == 1.0, family

    def test_the_count_control_probe_recovers_nothing(self, shipped_cases) -> None:
        # The instrument has to be able to clear an axis, or a FAIL says nothing.
        audit = audit_root_cause_identifiability(shipped_cases, label="RETRIEVAL_MISS")
        control = {item.probe_id: item for item in audit.results}["visible-context-key-count"]
        assert control.recovery == 0.0
        assert control.unscored == 0

    def test_interleaving_the_families_breaks_the_ordinal_cue(self, shipped_cases) -> None:
        interleaved = [
            dict(case, protected_root_cause=FAMILIES[(index - 1) % 8])
            for index, case in enumerate(shipped_cases, start=1)
        ]
        fit = frozenset(f"P5-HC-{index:03d}" for index in (1, 4, 7, 10, 13, 16, 19, 22))
        worst = max(
            audit_root_cause_identifiability(
                interleaved, label=family, fit_case_ids=fit
            ).worst_recovery
            or 0.0
            for family in FAMILIES
        )
        assert worst == 0.0

    def test_labelled_case_carries_the_split_it_was_given(self, shipped_cases) -> None:
        case = labelled_case(shipped_cases[0], split=CaseSplit.EVAL)
        assert case.split is CaseSplit.EVAL
        assert case.label == "RETRIEVAL_MISS"


class TestSuiteRollUp:
    def test_the_shipped_suite_fails_overall(self, shipped_cases) -> None:
        suite = {"suite_id": "shipped", "cases": shipped_cases}
        report = audit_hidden_cause_suite(suite)
        assert report["overall_outcome"] == Outcome.FAIL.value
        assert report["n_cases"] == 24
        assert len(report["root_cause_identifiability"]) == 8

    def test_a_roll_up_over_no_cases_blocks_rather_than_passes(self) -> None:
        report = audit_hidden_cause_suite({"suite_id": "empty", "cases": []})
        assert report["overall_outcome"] == Outcome.CANNOT_CHECK.value
        assert report["commitment_custody"]["reason"] == CustodyReason.NO_SEALED_SECRET.value


class TestCli:
    def test_auditing_the_shipped_suite_exits_non_zero(self, tmp_path, capsys) -> None:
        output = tmp_path / "audit.json"
        code = main(
            [
                "--suite",
                str(REPO_ROOT / SHIPPED_SUITE_PATH),
                "--output",
                str(output),
                "--budget-digests",
                "100000",
            ]
        )
        capsys.readouterr()
        assert code == 3
        report = json.loads(output.read_text(encoding="utf-8"))
        assert report["overall_outcome"] == Outcome.FAIL.value
        assert report["commitment_custody"]["outcome"] == Outcome.FAIL.value
