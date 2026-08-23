"""The suite the seven probes cannot open, checked against the suite they open in 108.

Every claim here is stated twice, once on each artifact, because a test file that
only pinned "the probes recover nothing" would pass just as well if the probes had
been deleted. ``TestTheShippedSuiteStillOpens`` is therefore not redundant with
``tests/unit/p5/test_hidden_cause_custody.py``: it is the control that gives the
zeros below their meaning, and it must keep failing the artifact P5 ships.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from orion.programme.commitment_custody import CustodyReason
from orion.programme.records import Outcome
from orion.study.p5.freeze import (
    ROOT_CAUSES,
    mint_root_cause_nonce,
    ordinal_independence_report,
    validate_protected_suite,
)
from orion.study.p5.hidden_cause_custody import (
    DISCLOSURE_BUDGET_DIGESTS,
    SHIPPED_SUITE_PATH,
    audit_root_cause_identifiability,
    audit_suite_custody,
    disclosure_probes_for,
    unenforceable_nonces,
)
from orion.study.p5.hidden_cause_custody import main as custody_main
from orion.study.p5.sound_hidden_cause_suite import (
    CASE_ID_PREFIX,
    CUSTODY_RULE_GAPS,
    CUSTODY_RULE_GAPS_CLOSED,
    OPENING_MATERIAL_CASE_FIELDS,
    PUBLISHED_CASE_FIELDS,
    SEALED_CASE_FIELDS,
    SoundSuite,
    assign_families,
    assignment_seed_commitment,
    audit_sound_suite,
    block_covering_fit_case_ids,
    block_repeats_a_family,
    contrast_report,
    generate_sound_suite,
    label_pairings_in,
    sealed_material_in,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FAMILIES = sorted(ROOT_CAUSES)


@pytest.fixture(scope="module")
def shipped_cases() -> list[dict[str, Any]]:
    suite = json.loads((REPO_ROOT / SHIPPED_SUITE_PATH).read_text(encoding="utf-8"))
    return list(suite["cases"])


@pytest.fixture(scope="module")
def sound_suite() -> SoundSuite:
    """One real draw, not a fixture with baked-in nonces.

    The claim under test is about what the generator produces, and a hard-coded
    suite would only establish that one lucky assignment and twenty-four lucky
    nonces survive. Module-scoped because the full-budget audit below costs about
    4.7 million SHA-256 evaluations and there is no reason to pay it twice.
    """

    return generate_sound_suite()


@pytest.fixture(scope="module")
def sound_report(sound_suite: SoundSuite) -> dict[str, Any]:
    return audit_sound_suite(sound_suite)


# ---------------------------------------------------------------------------
# The control: the artifact P5 ships is still open, and still says so.
# ---------------------------------------------------------------------------


class TestTheShippedSuiteStillOpens:
    def test_the_ordinal_probe_opens_all_24_in_108_digests(self, shipped_cases) -> None:
        audit = audit_suite_custody(shipped_cases, suite_id="shipped")
        ordinal = {item.probe_id: item for item in audit.attempts}["ordinal-nonce"]
        assert (ordinal.disclosed, ordinal.sealed) == (24, 24)
        assert ordinal.digests_computed == 108
        assert audit.outcome is Outcome.FAIL
        assert audit.reason is CustodyReason.SECRET_DISCLOSED
        assert audit.worst_disclosure_rate == 1.0

    def test_every_shipped_nonce_is_one_the_freeze_refuses(self, shipped_cases) -> None:
        assert len(unenforceable_nonces(shipped_cases, suite_id="shipped")) == 24

    def test_the_ordinal_recovers_all_eight_families(self, shipped_cases) -> None:
        for family in FAMILIES:
            audit = audit_root_cause_identifiability(shipped_cases, label=family)
            assert audit.outcome is Outcome.FAIL, family
            assert audit.worst_recovery == 1.0, family


# ---------------------------------------------------------------------------
# The demonstration: same probes, same budget, a suite built under the rule.
# ---------------------------------------------------------------------------


class TestTheSoundSuiteResistsEveryProbe:
    def test_all_seven_probes_open_nothing_at_the_full_budget(self, sound_report) -> None:
        custody = sound_report["commitment_custody"]
        assert custody["outcome"] == Outcome.PASS.value
        assert custody["reason"] == CustodyReason.WITHHELD_UNDER_ENUMERATION.value
        assert custody["worst_disclosure_rate"] == 0.0
        assert len(custody["attempts"]) == 7
        for attempt in custody["attempts"]:
            assert attempt["disclosed"] == 0, attempt["probe_id"]
            assert attempt["disclosed_ids"] == [], attempt["probe_id"]

    def test_no_probe_ran_out_of_money(self, sound_report) -> None:
        """A probe that stopped looking reports the same zero as one that finished."""

        for attempt in sound_report["commitment_custody"]["attempts"]:
            assert not attempt["budget_exhausted"], attempt["probe_id"]
            assert attempt["budget_digests"] == DISCLOSURE_BUDGET_DIGESTS
            assert attempt["digests_computed"] > 0, attempt["probe_id"]

    def test_the_zero_cost_millions_of_digests(self, sound_report) -> None:
        """The work is half the finding, so the exact bill is pinned, not bounded.

        "Nothing was opened" and "nothing was opened in 4 734 336 SHA-256
        evaluations across seven declared adversaries" are different claims, and
        only the second one is a result. The per-probe split is fixed by the probe
        definitions and the 24-case, 8-label shape, so a change to either shows up
        here rather than quietly making the demonstration cheaper.
        """

        spent = {
            attempt["probe_id"]: attempt["digests_computed"]
            for attempt in sound_report["commitment_custody"]["attempts"]
        }
        assert spent == {
            "ordinal-nonce": 192,
            "small-integer-nonce": 3_145_728,
            "floor-evading-counter-nonce": 1_572_864,
            "constant-nonce": 6_720,
            "case-id-digest-nonce": 384,
            "published-field-nonce": 4_032,
            "reused-nonce": 4_416,
        }
        assert sound_report["digests_computed"] == 4_734_336
        assert sound_report["probes_run"] == 7

    def test_the_ordinal_probe_is_the_one_that_opened_the_shipped_suite(
        self, sound_suite, shipped_cases
    ) -> None:
        # Same probe objects, not a re-registered set: a demonstration attacked by
        # a different adversary than the one that won is not a contrast.
        sound_ids = {probe.probe_id for probe in disclosure_probes_for(sound_suite.cases)}
        shipped_ids = {probe.probe_id for probe in disclosure_probes_for(shipped_cases)}
        assert sound_ids == shipped_ids
        assert "ordinal-nonce" in sound_ids

    def test_the_freeze_would_refuse_none_of_its_nonces(self, sound_report) -> None:
        assert sound_report["enumerable_nonces"] == []

    def test_the_generated_suite_passes_the_freeze_validator(self, sound_suite) -> None:
        validate_protected_suite(sound_suite.sealed_suite)
        assert sound_suite.commitment_manifest["case_count"] == 24
        assert len(sound_suite.candidate_packet["cases"]) == 24


class TestTheFamiliesDoNotFallOutOfTheOrdinal:
    def test_no_ordinal_block_repeats_a_family(self, sound_suite) -> None:
        assert not block_repeats_a_family(sound_suite.families, block_size=3)

    def test_the_families_are_not_in_blocks(self, sound_suite) -> None:
        blocked = [family for family in FAMILIES for _ in range(3)]
        assert list(sound_suite.families) != blocked

    def test_no_family_is_recovered_under_either_fit_split(self, sound_report) -> None:
        rows = sound_report["root_cause_identifiability"]
        assert rows["default_fit"]["families_recovered"] == 0
        assert rows["block_covering_fit"]["families_recovered"] == 0
        for split in ("default_fit", "block_covering_fit"):
            for audit in rows[split]["audits"]:
                assert (audit["worst_recovery"] or 0.0) <= 0.0, (split, audit["label"])

    def test_the_block_cue_scores_every_eval_case_and_finds_nothing(
        self, sound_suite
    ) -> None:
        """The covering split is the harder test, and it is the one that scores.

        One authorised opening in every ordinal block, all of distinct families ---
        more than a sound freeze discloses to anybody. The block rule then predicts
        on all sixteen eval cases instead of abstaining, and gets none of them.
        """

        fit = sorted(block_covering_fit_case_ids(sound_suite.cases))
        assert len(fit) == 8
        for family in FAMILIES:
            audit = audit_root_cause_identifiability(
                sound_suite.cases, label=family, fit_case_ids=fit
            )
            block = {item.probe_id: item for item in audit.results}["case-id-ordinal-block"]
            assert block.scored == 16, family
            assert block.unscored == 0, family
            assert block.true_positive == 0, family
            assert block.recovery is not None and block.recovery <= 0.0, family

    def test_the_control_probe_still_clears_the_axis(self, sound_suite) -> None:
        # An instrument that failed everything would say nothing about this suite.
        for family in FAMILIES:
            audit = audit_root_cause_identifiability(sound_suite.cases, label=family)
            control = {item.probe_id: item for item in audit.results}[
                "visible-context-key-count"
            ]
            assert control.recovery == 0.0, family

    def test_the_nonce_cue_cannot_be_scored_against_a_csprng_salt(
        self, sound_report
    ) -> None:
        """The instrument limit, pinned so a silent change to the cue is noticed.

        ``nonce_ordinal_block`` is ``(int(nonce, 16) - 1) // 3``. Every case of a
        correctly salted suite has its own signature, so the fitted rule abstains
        everywhere and informedness is undefined --- which the audit reports as
        ``NO_PROBE_SCORED`` and ``CANNOT_CHECK``. No correctly salted suite can
        pass that audit, which is why the roll-up below is ``CANNOT_CHECK`` while
        nothing was recovered and nothing was opened.
        """

        rows = sound_report["root_cause_identifiability"]
        assert rows["block_covering_fit"]["probes_that_could_not_be_scored"] == [
            "nonce-ordinal-block"
        ]
        for audit in rows["block_covering_fit"]["audits"]:
            assert audit["outcome"] == Outcome.CANNOT_CHECK.value
            assert audit["reason"] == "NO_PROBE_SCORED"
        assert sound_report["overall_outcome"] == Outcome.CANNOT_CHECK.value


class TestThePublishedSurfaceCarriesNoOpeningMaterial:
    def test_the_candidate_packet_carries_only_the_publishable_fields(
        self, sound_suite
    ) -> None:
        for case in sound_suite.candidate_packet["cases"]:
            assert set(case) == PUBLISHED_CASE_FIELDS
            assert not SEALED_CASE_FIELDS & set(case)

    def test_no_sealed_value_reaches_the_published_surface(self, sound_suite) -> None:
        assert sealed_material_in(sound_suite.published_surface(), suite=sound_suite) == ()

    def test_the_leak_check_names_a_leak_when_there_is_one(self, sound_suite) -> None:
        """The check has to be able to fire, or its silence is not evidence."""

        leaked = dict(sound_suite.published_surface())
        first = sound_suite.cases[0]
        leaked["accidentally_published"] = {
            "case_id": first["case_id"],
            "root_cause_nonce": first["root_cause_nonce"],
            "success_rubric": first["success_rubric"],
        }
        found = sealed_material_in(leaked, suite=sound_suite)
        assert f"root_cause_nonce@{first['case_id']}" in found
        assert f"success_rubric@{first['case_id']}" in found

    def test_the_audit_report_carries_no_opening_material(
        self, sound_suite, sound_report
    ) -> None:
        """The report is the one artifact of this module a caller might commit.

        Narrower than the check on the published surface, and deliberately so: an
        audit report names all eight families, once per audited label, and a
        substring search would call that a leak. What must not appear is a value
        that is a secret in itself -- a nonce, a rubric, a protected path, the
        assignment seed, a payload -- or a family sitting in the same object as a
        case id, which is the pairing the whole scheme exists to withhold.
        """

        assert (
            sealed_material_in(
                sound_report, suite=sound_suite, case_fields=OPENING_MATERIAL_CASE_FIELDS
            )
            == ()
        )
        assert label_pairings_in(sound_report, suite=sound_suite) == ()

    def test_the_pairing_check_names_a_pairing_when_there_is_one(
        self, sound_suite, sound_report
    ) -> None:
        first = sound_suite.cases[0]
        leaked = dict(sound_report)
        leaked["accidentally_published"] = [
            {
                "case_id": str(first["case_id"]),
                "protected_root_cause": str(first["protected_root_cause"]),
            }
        ]
        assert label_pairings_in(leaked, suite=sound_suite) == (str(first["case_id"]),)

    def test_the_assignment_seed_is_bound_but_not_published(
        self, sound_suite, sound_report
    ) -> None:
        assert sound_report["assignment"]["seed_published"] is False
        assert sound_report["assignment"]["seed_commitment"] == assignment_seed_commitment(
            sound_suite.assignment_seed
        )
        assert sound_suite.assignment_seed not in json.dumps(sound_suite.published_surface())

    def test_a_published_seed_would_hand_over_every_family(self, sound_suite) -> None:
        """Why the seed is sealed, demonstrated rather than asserted.

        The assignment is a deterministic function of the seed. Publishing it
        beside the packet would make ``family(ordinal)`` computable from what the
        manifest carries --- the shipped suite's defect reached by a longer route,
        and one no nonce repairs.
        """

        replayed, _ = assign_families(sound_suite.assignment_seed, families=FAMILIES)
        assert replayed == sound_suite.families

    def test_nothing_under_paper_05_carries_a_generated_case(self) -> None:
        """The sealed half is not in the repository, checked rather than intended."""

        paper = REPO_ROOT / "papers" / "paper-05-self-orion"
        hits = [
            path
            for path in paper.rglob("*")
            if path.is_file()
            and path.suffix in {".json", ".md", ".tex"}
            and CASE_ID_PREFIX in path.read_text(encoding="utf-8", errors="ignore")
        ]
        assert hits == []


class TestTheDemonstrationClaimsNothing:
    def test_it_declares_no_authority_and_closes_no_gate(self, sound_report) -> None:
        assert sound_report["grants_authority"] == "NONE"
        assert sound_report["closes_gate"] is None
        assert sound_report["is_scientific_result"] is False
        assert "no campaign" in sound_report["authority_note"]

    def test_its_case_ids_cannot_be_mistaken_for_the_manuscript_s(
        self, sound_suite, shipped_cases
    ) -> None:
        shipped_ids = {str(case["case_id"]) for case in shipped_cases}
        generated = {str(case["case_id"]) for case in sound_suite.cases}
        assert not shipped_ids & generated
        assert all(case_id.startswith(CASE_ID_PREFIX) for case_id in generated)


@pytest.fixture(scope="module")
def report(sound_suite: SoundSuite) -> dict[str, Any]:
    shipped = json.loads((REPO_ROOT / SHIPPED_SUITE_PATH).read_text(encoding="utf-8"))
    return contrast_report(shipped_suite=shipped, sound_suite=sound_suite)


class TestTheContrastIsRunnable:
    def test_it_reports_both_artifacts_under_one_instrument(self, report) -> None:
        custody = report["contrast"]["commitment_custody"]
        assert custody["shipped"]["outcome"] == Outcome.FAIL.value
        assert custody["shipped"]["ordinal_probe_disclosed"] == 24
        assert custody["shipped"]["ordinal_probe_digests"] == 108
        assert custody["sound"]["outcome"] == Outcome.PASS.value
        assert custody["sound"]["ordinal_probe_disclosed"] == 0
        assert custody["sound"]["digests_computed"] > 4_000_000

    def test_the_families_line_reads_eight_against_zero(self, report) -> None:
        families = report["contrast"]["families_recovered_by_a_competence_free_cue"]
        assert families == {
            "of": 8,
            "shipped": 8,
            "sound_default_fit": 0,
            "sound_block_covering_fit": 0,
        }

    def test_the_verdict_is_the_shipped_suite_s(self, report) -> None:
        assert report["verdict_source"] == "shipped_suite"
        assert report["shipped_suite"]["overall_outcome"] == Outcome.FAIL.value
        assert report["grants_authority"] == "NONE"


class TestTheCustodyCliStillFailsTheShippedSuite:
    def test_the_contrast_flag_does_not_lower_the_exit_code(self, tmp_path, capsys) -> None:
        output = tmp_path / "audit.json"
        code = custody_main(
            [
                "--suite",
                str(REPO_ROOT / SHIPPED_SUITE_PATH),
                "--output",
                str(output),
                "--contrast-sound-suite",
            ]
        )
        capsys.readouterr()
        assert code == 3
        report = json.loads(output.read_text(encoding="utf-8"))
        assert report["overall_outcome"] == Outcome.FAIL.value
        assert report["commitment_custody"]["outcome"] == Outcome.FAIL.value
        demonstration = report["sound_suite_demonstration"]
        assert demonstration["commitment_custody"]["outcome"] == Outcome.PASS.value
        assert demonstration["grants_authority"] == "NONE"


class TestTheGeneratorItself:
    def test_the_block_constraint_can_fire(self) -> None:
        blocked = tuple(family for family in FAMILIES for _ in range(3))
        assert block_repeats_a_family(blocked, block_size=3)
        assert not block_repeats_a_family(tuple(FAMILIES * 3), block_size=3)

    def test_the_generator_accepts_exactly_what_the_validator_accepts(self) -> None:
        """The rejection loop tests the validator's predicate, not a cousin of it.

        Before this, the generator enforced ordinal independence by construction
        and the validator enforced nothing, so "sound" meant "produced by this
        function". Now both read ``ordinal_independence_report``, and a suite the
        generator emits is one ``validate_protected_suite`` accepts by the same
        rule rather than by coincidence.
        """

        assignment, rejected = assign_families("e" * 64, families=FAMILIES)

        assert rejected > 0, "the constraint must have refused at least one draw"
        assert ordinal_independence_report(assignment)["independent"] is True

    def test_the_shipped_order_is_a_draw_the_generator_would_refuse(self) -> None:
        blocked = tuple(family for family in FAMILIES for _ in range(3))
        report = ordinal_independence_report(blocked)

        assert report["independent"] is False
        # FAMILIES is the sorted enum, so the block order is readable both ways:
        # free from the public labels, and from eight paid openings.
        assert report["rules_recovering_every_predicted_case"] == [
            "alphabetical/blocks-of-3",
            "first-appearance/blocks-of-3",
        ]

    def test_the_closed_gaps_are_kept_as_a_record_not_deleted(self) -> None:
        """Each entry keeps what the hole was, so the repair can be checked against it.

        The gaps a condition closes are held with their numbers in
        ``tests/unit/p5/test_custody_rule_gaps.py``; what this asserts is that the
        record of the hole survives the repair rather than being deleted with it.
        """

        assert len(CUSTODY_RULE_GAPS_CLOSED) == 6
        ordinal = next(entry for entry in CUSTODY_RULE_GAPS_CLOSED if "emission order" in entry)
        assert "CLOSED:" in ordinal
        assert all("CLOSED" not in gap for gap in CUSTODY_RULE_GAPS)
        assert all("emission order" not in gap for gap in CUSTODY_RULE_GAPS)

    def test_the_assignment_is_reproducible_from_its_seed(self) -> None:
        seed = "c" * 63 + "d"
        first, rejected = assign_families(seed, families=FAMILIES)
        second, again = assign_families(seed, families=FAMILIES)
        assert first == second
        assert rejected == again
        assert not block_repeats_a_family(first, block_size=3)

    def test_two_suites_share_no_nonce(self) -> None:
        left = generate_sound_suite()
        right = generate_sound_suite()
        left_nonces = {case["root_cause_nonce"] for case in left.cases}
        right_nonces = {case["root_cause_nonce"] for case in right.cases}
        assert len(left_nonces) == 24
        assert not left_nonces & right_nonces
        assert left.assignment_seed != right.assignment_seed

    def test_a_minted_nonce_is_what_the_generator_uses(self, sound_suite) -> None:
        # Shape, not provenance: every generated nonce must be the same 64-hex
        # object mint_root_cause_nonce returns, or the freeze would refuse it.
        sample = mint_root_cause_nonce()
        for case in sound_suite.cases:
            nonce = str(case["root_cause_nonce"])
            assert len(nonce) == len(sample) == 64
            assert int(nonce, 16) >= 1 << 64
