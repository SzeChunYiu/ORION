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
from orion.programme.commitment_custody import CustodyReason, DisclosureKind
from orion.programme.records import Outcome
from orion.study.p5.freeze import (
    ROOT_CAUSES,
    freeze_protected_suite,
    mint_root_cause_nonce,
    nonce_weakness,
    ordinal_independence_report,
    sha256_json,
)
from orion.study.p5.hidden_cause_custody import (
    DISCLOSURE_BUDGET_DIGESTS,
    FREEZE_CANARY,
    P5_DISCLOSURE_PROBES,
    SHIPPED_SUITE_PATH,
    audit_hidden_cause_suite,
    audit_root_cause_identifiability,
    audit_suite_custody,
    default_fit_case_ids,
    disclosure_probes_for,
    extract_hidden_cause_cues,
    labelled_case,
    main,
    root_cause_commitment,
    sealed_root_causes,
    unenforceable_nonces,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FAMILIES = sorted(ROOT_CAUSES)

#: The order ``_freezable_suite`` emits its eight cases in.
#:
#: Not ``FAMILIES``: with one case per family, "family = alphabetical slot of the
#: ordinal" is free to compute and right eight times out of eight, so
#: ``validate_protected_suite`` refuses such a suite -- correctly, because its
#: commitments would open themselves off the packet. These fixtures exist to
#: exercise the *nonce* scheme, so they need an order that gets past the ordinal
#: condition; ``test_the_fixture_order_is_not_readable_off_the_ordinal`` holds
#: this one to it.
FREEZE_ORDER = [
    "METHOD_BASIS_GAP",
    "MEASUREMENT_SPECIFICATION_GAP",
    "ENVIRONMENT_DEPENDENCY_TOOL_FAILURE",
    "REPRESENTATION_GAP",
    "EVALUATOR_METRIC_BUG",
    "RETRIEVAL_MISS",
    "ROUTING_PLANNING_MISS",
    "IMPLEMENTATION_BUG",
]
assert set(FREEZE_ORDER) == set(FAMILIES)


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


def test_the_fixture_order_is_not_readable_off_the_ordinal() -> None:
    """The fixtures must clear the condition they are not testing.

    If a future rule reads ``FREEZE_ORDER``, every freeze in this file starts
    raising and the cause is this constant, not the nonce scheme under test. Say
    so here rather than leaving it to be rediscovered from eleven failures.
    """

    assert ordinal_independence_report(FREEZE_ORDER)["independent"] is True
    assert ordinal_independence_report(FAMILIES)["rules_recovering_every_predicted_case"] == [
        "alphabetical/stride-1"
    ]


class TestSchemeBinding:
    def test_the_modelled_scheme_matches_what_the_real_freeze_publishes(self) -> None:
        # The audit models freeze._root_commitment rather than importing it. If
        # that model drifts, every probe opens nothing and the suite reads as
        # protected, so the binding is pinned against a live freeze.
        nonces = [_high_entropy_nonce(index) for index in range(1, 9)]
        suite = _freezable_suite(nonces, FREEZE_ORDER)
        _, manifest = freeze_protected_suite(suite)
        for case, nonce, family in zip(manifest["cases"], nonces, FREEZE_ORDER, strict=True):
            assert case["root_cause_commitment"] == root_cause_commitment(family, nonce)

    def test_the_canary_is_a_digest_the_real_freeze_would_emit(self) -> None:
        nonces = [_high_entropy_nonce(index) for index in range(1, 9)]
        nonces[FREEZE_ORDER.index(FREEZE_CANARY.secret)] = FREEZE_CANARY.nonce
        suite = _freezable_suite(nonces, FREEZE_ORDER)
        _, manifest = freeze_protected_suite(suite)
        emitted = {
            case["case_id"]: case["root_cause_commitment"] for case in manifest["cases"]
        }
        canary_case = f"P5-HC-{FREEZE_ORDER.index(FREEZE_CANARY.secret) + 1:03d}"
        assert emitted[canary_case] == FREEZE_CANARY.digest
        assert FREEZE_CANARY.reproduced_by(root_cause_commitment)


class TestShippedSuiteDefect:
    def test_every_opening_nonce_is_the_case_ordinal(self, shipped_cases) -> None:
        assert [int(case["root_cause_nonce"], 16) for case in shipped_cases] == list(
            range(1, len(shipped_cases) + 1)
        )

    def test_the_validator_now_refuses_those_nonces(self, shipped_cases) -> None:
        """The gap that let the shipped suite through is closed.

        This test previously asserted the opposite: `freeze_protected_suite`
        accepted nonces `0...01` through `0...08` without complaint, because
        `_require_nonce` rejected exactly one value out of 2^256 -- the all-zero
        one. That is why the leak survived nine fail-closed conditions.

        `validate_protected_suite` now rejects any nonce below 2**64. A CSPRNG
        draw lands there with probability 2**-192, so the floor costs nothing
        real and stops every counter, ordinal and small integer. The historical
        21/24 result is untouched and keeps its recorded defect; what changes is
        that the next freeze cannot repeat it.
        """

        nonces = [f"{index:064x}" for index in range(1, 9)]
        with pytest.raises(ValueError, match="below 2\\*\\*64"):
            freeze_protected_suite(_freezable_suite(nonces, FREEZE_ORDER))

    def test_a_full_width_nonce_still_freezes(self, shipped_cases) -> None:
        """The floor rejects weakness, not the scheme: real nonces still pass."""

        nonces = [
            hashlib.sha256(f"p5-full-width-{index}".encode()).hexdigest() for index in range(1, 9)
        ]
        freeze_protected_suite(_freezable_suite(nonces, FREEZE_ORDER))

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

    def test_every_registered_probe_states_its_cost(self, shipped_cases) -> None:
        probes = disclosure_probes_for(shipped_cases, suite_id="shipped")
        assert len(P5_DISCLOSURE_PROBES) == 5
        assert len(probes) == 7
        assert all(probe.cost_rationale.strip() for probe in probes)

    def test_every_way_of_not_guessing_a_nonce_has_a_probe(self, shipped_cases) -> None:
        # DisclosureKind enumerates five ways of obtaining a nonce without
        # cryptanalysis. A kind with no probe behind it is a class of attack the
        # audit reports zero disclosures for because nobody ran it.
        probes = disclosure_probes_for(shipped_cases, suite_id="shipped")
        assert {probe.kind for probe in probes} == set(DisclosureKind)


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


# ---------------------------------------------------------------------------
# The attack, the repair, and the proof that the two are about the same thing.
#
# A test suite that only pinned "the probe recovers nothing" would pass equally
# well if the probe had been deleted. Every claim below is therefore stated
# twice: once as the attack succeeding against the scheme as shipped, and once
# as the same attack, at the same budget, failing against the repaired one.
# ---------------------------------------------------------------------------


def _floor_evading_nonces(count: int) -> list[str]:
    """Nonces that clear a magnitude floor and carry nothing.

    ``2**255 + ordinal`` is 64 hex characters, non-zero, unique per case and
    2**191 times above the 2**64 floor the freeze used to enforce. It also opens
    to one guess, which is the whole point: a floor rejects values that look
    small, and this does not look small.
    """

    return [f"{(1 << 255) + index:064x}" for index in range(1, count + 1)]


@pytest.fixture(scope="module")
def repaired_cases(shipped_cases) -> list[dict[str, Any]]:
    """The shipped cases with their nonces redrawn from the CSPRNG.

    Real draws rather than a fixed fixture: the claim under test is about what
    ``mint_root_cause_nonce`` produces, and a hard-coded "high entropy" constant
    would only establish that one lucky value survives.
    """

    return [dict(case, root_cause_nonce=mint_root_cause_nonce()) for case in shipped_cases]


@pytest.fixture(scope="module")
def repaired_audit(repaired_cases):
    return audit_suite_custody(repaired_cases, suite_id="repaired")


class TestTheAttackWorksOnTheSchemeAsShipped:
    """Each of these must keep passing, or the repair below proves nothing."""

    def test_the_ordinal_nonce_still_opens_all_24_at_4_5_digests_each(
        self, shipped_cases
    ) -> None:
        audit = audit_suite_custody(shipped_cases, suite_id="shipped")
        ordinal = {item.probe_id: item for item in audit.attempts}["ordinal-nonce"]
        assert (ordinal.disclosed, ordinal.sealed) == (24, 24)
        assert ordinal.digests_computed == 108
        assert audit.outcome is Outcome.FAIL

    def test_a_magnitude_floor_alone_would_not_have_stopped_it(self) -> None:
        """The repair the shipped scheme first received, and why it was not one.

        Every nonce here is above 2**64, so the floor that ``_require_nonce``
        enforced accepts all eight. The floor-evading probe opens all eight
        anyway, because the entropy a floor measures is not the entropy a
        commitment needs.
        """

        nonces = _floor_evading_nonces(8)
        assert all(int(nonce, 16) >= 1 << 64 for nonce in nonces)

        cases = _freezable_suite(nonces, FREEZE_ORDER)["cases"]
        audit = audit_suite_custody(cases, suite_id="floor-evading")
        attempt = {item.probe_id: item for item in audit.attempts}[
            "floor-evading-counter-nonce"
        ]
        assert audit.outcome is Outcome.FAIL
        assert (attempt.disclosed, attempt.sealed) == (8, 8)

    def test_one_salt_shared_across_the_suite_opens_the_whole_suite(self) -> None:
        """Per-item is not decoration. A shared salt has full entropy and no custody.

        Every shape rule clears this nonce --- it is a CSPRNG draw. What it is
        not is *per case*, so the first authorised opening hands the adversary
        the other twenty-three, which is what ``reused-nonce`` measures.
        """

        shared = mint_root_cause_nonce()
        cases = _freezable_suite([shared] * 8, FREEZE_ORDER)["cases"]
        assert nonce_weakness(shared) is None

        audit = audit_suite_custody(cases, suite_id="shared-salt")
        attempt = {item.probe_id: item for item in audit.attempts}["reused-nonce"]
        assert audit.outcome is Outcome.FAIL
        assert (attempt.disclosed, attempt.sealed) == (8, 8)


class TestTheRepairDefeatsTheAttack:
    def test_the_probes_open_0_of_24_under_csprng_salts(self, repaired_audit) -> None:
        assert repaired_audit.outcome is Outcome.PASS
        assert repaired_audit.reason is CustodyReason.WITHHELD_UNDER_ENUMERATION
        assert repaired_audit.worst_disclosure_rate == 0.0
        assert not repaired_audit.blocks
        for attempt in repaired_audit.attempts:
            assert attempt.disclosed == 0, attempt.probe_id
            assert attempt.disclosed_ids == (), attempt.probe_id

    def test_the_pass_states_a_budget_that_no_probe_ran_out_of(
        self, repaired_audit
    ) -> None:
        """A probe that stopped looking reports the same zero as one that looked.

        ``BUDGET_EXHAUSTED`` is the reason that separates them, and it blocks.
        Asserting that no attempt hit the ceiling is what makes the zero above a
        finding rather than an interruption.
        """

        for attempt in repaired_audit.attempts:
            assert not attempt.budget_exhausted, attempt.probe_id
            assert attempt.budget_digests == DISCLOSURE_BUDGET_DIGESTS
            assert attempt.attempted, attempt.probe_id

    def test_the_attack_spent_millions_of_digests_to_recover_nothing(
        self, repaired_audit
    ) -> None:
        spent = sum(attempt.digests_computed for attempt in repaired_audit.attempts)
        # 16384 counters + 8192 floor-evading counters + the bounded families,
        # against 8 candidate labels and 24 commitments.
        assert spent > 4_000_000
        assert f"{spent} digest evaluations" in repaired_audit.detail

    def test_no_repaired_nonce_is_one_the_freeze_would_refuse(
        self, repaired_cases
    ) -> None:
        assert unenforceable_nonces(repaired_cases, suite_id="repaired") == ()

    def test_every_shipped_nonce_is_one_the_freeze_would_refuse(
        self, shipped_cases
    ) -> None:
        findings = unenforceable_nonces(shipped_cases, suite_id="shipped")
        assert len(findings) == 24
        assert all("below 2**64" in weakness for _, weakness in findings)


class TestTheFreezeRefusesWhatTheProbeTries:
    """The binding that keeps the two halves from drifting apart.

    A repair is only a repair if the thing that accepts nonces refuses exactly
    what the thing that attacks them generates. These tests walk the probes'
    candidate lists and require the validator to name a weakness for every one.
    """

    def test_no_shape_probe_can_generate_a_nonce_the_freeze_accepts(
        self, shipped_cases
    ) -> None:
        case = shipped_cases[0]
        sealed = sealed_root_causes(shipped_cases)[0]
        probes = {
            probe.probe_id: probe
            for probe in disclosure_probes_for(shipped_cases, suite_id="shipped")
        }
        # reused-nonce is excluded on purpose: its candidates are other cases'
        # real nonces, which are strong values. Uniqueness and the shared-affix
        # rule are what refuse it, and they are tested separately below.
        checked = 0
        for probe_id, probe in probes.items():
            if probe_id == "reused-nonce":
                continue
            for candidate in probe.nonce_candidates(sealed):
                weakness = nonce_weakness(
                    candidate, case=case, ordinal=1, suite_id="shipped"
                )
                assert weakness is not None, f"{probe_id} generated {candidate}"
                checked += 1
        assert checked > 20_000

    def test_the_freeze_refuses_a_reused_salt(self) -> None:
        shared = mint_root_cause_nonce()
        with pytest.raises(ValueError, match="unique across cases"):
            freeze_protected_suite(_freezable_suite([shared] * 8, FREEZE_ORDER))

    def test_the_freeze_refuses_one_salt_with_a_per_case_tail(self) -> None:
        """Distinct is not independent, and only the affix rule sees that."""

        head = mint_root_cause_nonce()[:48]
        nonces = [head + f"{index:016x}" for index in range(1, 9)]
        assert len(set(nonces)) == 8
        with pytest.raises(ValueError, match="not a per-case salt"):
            freeze_protected_suite(_freezable_suite(nonces, FREEZE_ORDER))

    def test_the_freeze_refuses_a_floor_evading_counter(self) -> None:
        with pytest.raises(ValueError, match="enumerable"):
            freeze_protected_suite(_freezable_suite(_floor_evading_nonces(8), FREEZE_ORDER))

    def test_the_freeze_refuses_a_nonce_derived_from_the_case_id(self) -> None:
        nonces = [
            hashlib.sha256(f"P5-HC-{index:03d}".encode()).hexdigest()
            for index in range(1, 9)
        ]
        with pytest.raises(ValueError, match="publishes beside the commitment"):
            freeze_protected_suite(_freezable_suite(nonces, FREEZE_ORDER))

    def test_minted_nonces_freeze_and_their_commitments_hold(self) -> None:
        nonces = [mint_root_cause_nonce() for _ in range(8)]
        suite = _freezable_suite(nonces, FREEZE_ORDER)
        _, manifest = freeze_protected_suite(suite)

        published = {
            case["case_id"]: case["root_cause_commitment"] for case in manifest["cases"]
        }
        for case, nonce, family in zip(suite["cases"], nonces, FREEZE_ORDER, strict=True):
            assert published[case["case_id"]] == root_cause_commitment(family, nonce)

        audit = audit_suite_custody(suite["cases"], suite_id=suite["suite_id"])
        assert audit.outcome is Outcome.PASS
        assert audit.worst_disclosure_rate == 0.0


class TestTheRollUpReportsItsCost:
    def test_the_shipped_report_names_the_nonces_the_freeze_would_refuse(
        self, shipped_cases
    ) -> None:
        report = audit_hidden_cause_suite(
            {"suite_id": "shipped", "cases": shipped_cases}
        )
        assert report["overall_outcome"] == Outcome.FAIL.value
        assert len(report["enumerable_nonces"]) == 24
        assert report["probes_run"] == 7
        assert report["disclosure_budget_digests"] == DISCLOSURE_BUDGET_DIGESTS
        assert report["digests_computed"] > 0
