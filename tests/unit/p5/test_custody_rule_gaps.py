"""The custody rule's own gaps, closed and measured against the artifact that found them.

``PROTECTED_SUITE_FREEZE_V1.md`` states what a freeze may publish and what it must
seal. Six places where that rule ran out were recorded in
``sound_hidden_cause_suite.CUSTODY_RULE_GAPS`` by trying to build a suite from it.
Each is now a fail-closed condition, and each condition is held here to the same
standard the ordinal one was: it must reject the artifact that motivated it, with a
number. Every check below is therefore stated twice --- once on
``PROTECTED_SUITE_V1``, where it must fire, and once on a generated sound suite,
where it must be silent. A check that only ever passes is not evidence.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from orion.study.p5.freeze import (
    COMMITMENT_KINDS,
    PUBLISHED_CASE_FIELDS,
    PUBLISHED_IDENTIFIER_CASE_FIELDS,
    ROOT_CAUSES,
    SEALED_CASE_FIELDS,
    case_commitment_kinds,
    freeze_protected_suite,
    opening_disclosure_report,
    opening_nonce,
    published_field_independence_report,
    published_field_reading_rules,
    published_surface_leaks,
    read_family_from_strings,
    require_opening_separation,
    sha256_json,
    validate_protected_suite,
)
from orion.study.p5.hidden_cause_custody import (
    SHIPPED_SUITE_PATH,
    audit_commitment_kind_domains,
)
from orion.study.p5.sound_hidden_cause_suite import (
    CUSTODY_RULE_GAPS,
    CUSTODY_RULE_GAPS_CLOSED,
    SoundSuite,
    generate_sound_suite,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
PROTOCOL_PATH = REPO_ROOT / "papers/orion-15-self-orion/protocol/PROTECTED_SUITE_FREEZE_V1.md"

#: Eight distinct axis signatures, one per family, each carrying an independent
#: axis so the fresh-transfer condition still passes. This is the generator the
#: document permitted before the identifiers were bound: it follows every stated
#: rule and publishes the answer key in ``changed_axes``.
FAMILY_DEPENDENT_AXES: dict[str, list[str]] = {
    family: axes
    for family, axes in zip(
        sorted(ROOT_CAUSES),
        [
            ["TASK"],
            ["DOMAIN"],
            ["MODEL"],
            ["ENVIRONMENT"],
            ["DATA", "TASK"],
            ["DATA", "DOMAIN"],
            ["DATA", "MODEL"],
            ["TASK", "TOOL"],
        ],
    )
}


@pytest.fixture(scope="module")
def shipped_suite() -> dict[str, Any]:
    return json.loads((REPO_ROOT / SHIPPED_SUITE_PATH).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def shipped_cases(shipped_suite: dict[str, Any]) -> list[dict[str, Any]]:
    return list(shipped_suite["cases"])


@pytest.fixture(scope="module")
def shipped_families(shipped_cases: list[dict[str, Any]]) -> list[str]:
    return [str(case["protected_root_cause"]) for case in shipped_cases]


@pytest.fixture(scope="module")
def sound_suite() -> SoundSuite:
    """One real draw. A baked-in fixture would only establish that one suite is clean."""

    return generate_sound_suite()


# --- Gap 1: the two lists are complements, and every field is classified ------


class TestTheCustodyRuleClassifiesEveryCaseField:
    def test_the_three_lists_are_disjoint(self) -> None:
        assert not PUBLISHED_CASE_FIELDS & SEALED_CASE_FIELDS
        assert not PUBLISHED_CASE_FIELDS & PUBLISHED_IDENTIFIER_CASE_FIELDS
        assert not SEALED_CASE_FIELDS & PUBLISHED_IDENTIFIER_CASE_FIELDS

    def test_every_shipped_case_field_is_classified(
        self, shipped_cases: list[dict[str, Any]]
    ) -> None:
        """The rule has to cover the artifact it was written for, field by field."""

        classified = (
            PUBLISHED_CASE_FIELDS | PUBLISHED_IDENTIFIER_CASE_FIELDS | SEALED_CASE_FIELDS
        )
        for case in shipped_cases:
            assert set(case) - classified == set()
            assert len(case) == 14
        assert (len(PUBLISHED_CASE_FIELDS), len(PUBLISHED_IDENTIFIER_CASE_FIELDS)) == (6, 2)
        assert len(SEALED_CASE_FIELDS) == 6

    def test_an_unclassified_field_fails_the_freeze_closed(self, sound_suite) -> None:
        """A field nobody classified is a field whose custody nobody decided."""

        suite = copy.deepcopy(sound_suite.sealed_suite)
        suite["cases"][0]["analyst_note"] = "the mechanism is in the retriever"

        with pytest.raises(ValueError, match="classifies as neither published"):
            validate_protected_suite(suite)

    def test_the_document_and_the_code_state_the_same_classification(self) -> None:
        """The lists are data so a disagreement is a diff; this is the diff."""

        rows = {
            line.split("|")[1].strip(): line
            for line in PROTOCOL_PATH.read_text(encoding="utf-8").splitlines()
            if line.startswith("| ") and line.count("|") == 4
        }
        for field in PUBLISHED_CASE_FIELDS:
            assert f"`{field}`" in rows["published"]
        for field in PUBLISHED_IDENTIFIER_CASE_FIELDS:
            assert f"`{field}`" in rows["published as identifier"]
        for field in SEALED_CASE_FIELDS:
            assert f"`{field}`" in rows["sealed"]


# --- Gap 2: competing_cause_set, and everything else the packet must not carry


class TestSealedMaterialCannotReachThePublishedSurface:
    def test_the_shipped_suite_publishes_every_sealed_field_in_the_clear(
        self, shipped_suite: dict[str, Any], shipped_cases: list[dict[str, Any]]
    ) -> None:
        """The artifact the seal check refutes, and the count.

        ``PROTECTED_SUITE_V1.json`` is a candidate-readable file, so the search
        for sealed material in a published surface has it to report on: seven
        sealed values per case, 24 cases, 168 findings.
        """

        leaks = published_surface_leaks(shipped_suite, cases=shipped_cases)

        assert len(leaks) == 168
        for field in SEALED_CASE_FIELDS:
            assert sum(1 for leak in leaks if leak.startswith(f"{field}@")) == 24
        assert sum(1 for leak in leaks if leak.startswith("fresh_tasks.content_hash@")) == 24

    def test_the_shipped_competing_cause_set_names_the_answer_first(
        self, shipped_cases: list[dict[str, Any]]
    ) -> None:
        """The gap said eight to three. On this artifact it is eight to one."""

        first_is_the_answer = sum(
            1
            for case in shipped_cases
            if case["competing_cause_set"][0] == case["protected_root_cause"]
        )
        assert first_is_the_answer == 24
        assert {len(case["competing_cause_set"]) for case in shipped_cases} == {2}

    def test_a_freeze_that_would_publish_a_sealed_value_fails_closed(
        self, sound_suite
    ) -> None:
        """The packet's own fields are searched, not just the ones a reviewer expects.

        ``visible_symptom`` is published verbatim, so a suite whose symptom
        repeats the sealed rubric publishes the rubric. Nothing in the emitter
        writes ``success_rubric`` into the packet; the leak is in the content.
        """

        suite = copy.deepcopy(sound_suite.sealed_suite)
        suite["cases"][0]["visible_symptom"] = str(suite["cases"][0]["success_rubric"])

        with pytest.raises(ValueError, match="would publish sealed material"):
            freeze_protected_suite(suite)

    def test_a_clean_freeze_publishes_nothing_sealed(self, sound_suite) -> None:
        published = {
            "candidate_packet": sound_suite.candidate_packet,
            "commitment_manifest": sound_suite.commitment_manifest,
        }

        assert published_surface_leaks(published, cases=sound_suite.cases) == ()


# --- Gap 3: allowed_change_surface named the answer --------------------------


class TestNoPublishedFieldNamesTheFamily:
    def test_the_declared_readers_read_the_shipped_suite(
        self, shipped_cases: list[dict[str, Any]], shipped_families: list[str]
    ) -> None:
        """Refutation capacity: the guard must read the suite that motivated it."""

        report = published_field_independence_report(shipped_cases, shipped_families)

        assert report["rules_declared"] == 35
        assert report["cases_disclosed"] == 12
        assert report["families_disclosed"] == 7
        assert report["independent"] is False
        assert report["strongest_rule"] == "label-token-prefix-4/all-published-fields"
        assert report["strongest_rule_disclosed"] == 12

    def test_the_allowed_change_surface_alone_states_the_label(
        self, shipped_cases: list[dict[str, Any]], shipped_families: list[str]
    ) -> None:
        """The field the gap named, scored on its own and charged nothing."""

        rules = {
            rule.name: rule
            for rule in published_field_reading_rules(shipped_cases, shipped_families)
        }
        exact = rules["label-token-exact/allowed_change_surface"]
        prefix = rules["label-token-prefix-4/allowed_change_surface"]

        assert exact.agreement(shipped_families) == (6, 7)
        assert prefix.agreement(shipped_families) == (11, 13)
        assert exact.charge == "nothing: the eight family labels are a public enum"
        assert read_family_from_strings(["src/retrieval/index.py"], prefix=0) == "RETRIEVAL_MISS"
        assert (
            read_family_from_strings(["src/causal/representation.py"], prefix=0)
            == "REPRESENTATION_GAP"
        )
        assert (
            read_family_from_strings(["src/measurement/spec.py"], prefix=0)
            == "MEASUREMENT_SPECIFICATION_GAP"
        )

    def test_the_family_no_reader_recovers_is_reported_not_tuned_away(
        self, shipped_cases: list[dict[str, Any]], shipped_families: list[str]
    ) -> None:
        """Eight of eight would be a better headline and a worse measurement."""

        report = published_field_independence_report(shipped_cases, shipped_families)
        by_id = {str(case["case_id"]): str(case["protected_root_cause"]) for case in shipped_cases}
        disclosed = {
            by_id[case_id]
            for rule in report["rules_disclosing_a_case"]
            for case_id in rule["case_ids"]
        }

        assert sorted(set(ROOT_CAUSES) - disclosed) == ["IMPLEMENTATION_BUG"]

    def test_the_sound_suite_defeats_every_declared_reader(self, sound_suite) -> None:
        report = published_field_independence_report(sound_suite.cases, list(sound_suite.families))

        assert report["rules_declared"] == 35
        assert report["cases_disclosed"] == 0
        assert report["independent"] is True

    def test_naming_the_surface_after_the_mechanism_fails_the_freeze_closed(
        self, sound_suite
    ) -> None:
        suite = copy.deepcopy(sound_suite.sealed_suite)
        for case in suite["cases"]:
            family = str(case["protected_root_cause"]).split("_")[0].lower()
            case["allowed_change_surface"] = [f"src/{family}/patch.py"]

        with pytest.raises(ValueError, match="fields name the root cause they seal"):
            validate_protected_suite(suite)

    def test_a_reader_that_names_nothing_abstains(self) -> None:
        """Silence is the reader's answer on a surface named after the case."""

        assert read_family_from_strings(["src/candidate/case_001.py"], prefix=4) is None
        assert read_family_from_strings([], prefix=0) is None
        assert read_family_from_strings(["sound-fresh-001"], prefix=4) is None


# --- Gap 5: the manifest publishes task_id, changed_axes and variant_id ------


class TestPublishedIdentifiersAreIndependentOfTheFamily:
    def test_the_shipped_axes_do_not_partition_by_family(
        self, shipped_cases: list[dict[str, Any]], shipped_families: list[str]
    ) -> None:
        """The shipped suite is clean here, which is why the refutation is built."""

        rules = {
            rule.name: rule
            for rule in published_field_reading_rules(shipped_cases, shipped_families)
        }

        assert rules["signature-leave-one-out/changed_axes"].agreement(shipped_families) == (0, 0)

    def test_axes_chosen_per_family_are_read_and_refused(self, sound_suite) -> None:
        """The generator the document permitted: it breaks no stated rule and leaks all 24."""

        suite = copy.deepcopy(sound_suite.sealed_suite)
        for case in suite["cases"]:
            for fresh in case["fresh_tasks"]:
                fresh["changed_axes"] = list(
                    FAMILY_DEPENDENT_AXES[str(case["protected_root_cause"])]
                )
        families = [str(case["protected_root_cause"]) for case in suite["cases"]]
        rules = {
            rule.name: rule for rule in published_field_reading_rules(suite["cases"], families)
        }

        assert rules["signature-leave-one-out/changed_axes"].agreement(families) == (24, 24)
        with pytest.raises(ValueError, match="signature-leave-one-out/changed_axes"):
            validate_protected_suite(suite)

    def test_a_constant_identifier_discloses_nothing(self, sound_suite) -> None:
        """Guard against vacuity: the reader must abstain where it knows nothing.

        Every sound case carries ``changed_axes == ["TASK"]``, so the reader is
        told twenty-three families that disagree and predicts none of them. A
        reader that called that a disclosure would reject every suite.
        """

        rules = {
            rule.name: rule
            for rule in published_field_reading_rules(sound_suite.cases, list(sound_suite.families))
        }

        assert rules["signature-leave-one-out/changed_axes"].agreement(
            list(sound_suite.families)
        ) == (0, 0)
        assert rules["signature-leave-one-out/task_id"].agreement(list(sound_suite.families)) == (
            0,
            0,
        )


# --- Gap 6: one nonce per case was one nonce for seven commitment kinds ------


class TestOneOpeningNoncePerCommitmentKind:
    def test_every_case_publishes_the_seven_declared_kinds(self, sound_suite) -> None:
        for case in sound_suite.cases:
            kinds = case_commitment_kinds(case)
            assert len(kinds) == len(COMMITMENT_KINDS) == 7
            assert len(set(kinds)) == 7

    def test_one_opening_discloses_one_commitment(self, sound_suite) -> None:
        for case in sound_suite.cases:
            report = opening_disclosure_report(case)
            assert report["separated"] is True
            assert report["worst_non_root_release_opens"] == 1
            assert report["non_root_releases_opening_the_root_cause"] == 0
            root = next(
                row for row in report["released"] if row["released"] == "root-cause"
            )
            assert root["opens_count"] == 7

    def test_the_shared_nonce_manifest_is_refused(self, sound_suite) -> None:
        """The artifact this check rejects is the manifest the freeze used to emit.

        Rebuilt here exactly as it was: every commitment kind bound under the
        case's own ``root_cause_nonce``. Releasing any one of its openings
        discloses the other six, including the root cause.
        """

        case = dict(sound_suite.cases[0])
        nonce = str(case["root_cause_nonce"])
        fresh = case["fresh_tasks"][0]
        task_id = str(fresh["task_id"])
        variant_id = str(case["negative_variant_ids"][0])
        payloads = sound_suite.sealed_suite["fresh_task_payloads"]
        negatives = sound_suite.sealed_suite["negative_variant_payloads"]

        def shared(payload: Any, kind: str) -> str:
            return sha256_json(
                {"kind": kind, "payload_hash": sha256_json(payload), "nonce": nonce}
            )

        legacy = {
            "case_id": case["case_id"],
            "case_artifact_commitment": shared(case, f"case:{case['case_id']}"),
            "root_cause_commitment": sha256_json(
                {"protected_root_cause": case["protected_root_cause"], "nonce": nonce}
            ),
            "fresh_tasks": [
                {
                    "task_id": task_id,
                    "content_commitment": shared(payloads[task_id], f"fresh-task:{task_id}"),
                }
            ],
            "negative_variants": [
                {
                    "variant_id": variant_id,
                    "content_commitment": shared(
                        negatives[variant_id], f"negative-variant:{variant_id}"
                    ),
                }
            ],
            "protected_surface_commitment": shared(
                sorted(case["protected_surface"]), "protected-surface"
            ),
            "success_rubric_commitment": shared(case["success_rubric"], "success-rubric"),
            "harm_rubric_commitment": shared(case["harm_rubric"], "harm-rubric"),
        }

        with pytest.raises(ValueError, match="also opens 6 of the 7 commitments"):
            require_opening_separation(
                case,
                legacy,
                fresh_payloads=payloads,
                negative_payloads=negatives,
                prefix="legacy",
            )

    def test_the_derived_openings_are_distinct_and_do_not_reveal_the_case_nonce(
        self, sound_suite
    ) -> None:
        case = sound_suite.cases[0]
        nonce = str(case["root_cause_nonce"])
        kinds = case_commitment_kinds(case)
        openings = {kind: opening_nonce(nonce, kind=kind) for kind in kinds}

        assert len(set(openings.values())) == len(kinds)
        assert openings["root-cause"] == nonce
        assert nonce not in [value for kind, value in openings.items() if kind != "root-cause"]

    def test_the_cheapest_shipped_kind_is_not_the_one_the_probes_attack(
        self, shipped_suite: dict[str, Any]
    ) -> None:
        """The measurement the gap asked for, on the artifact that motivated it.

        ``root-cause`` re-derives the custody audit's own 108 digests from the
        other end, which is the check that this cost model and that one are the
        same model. The rubrics cost a twenty-fourth of it.
        """

        report = audit_commitment_kind_domains(shipped_suite)
        rows = {row["kind"]: row for row in report["kinds"]}

        assert report["cases_with_an_enumerable_nonce"] == 24
        assert rows["root-cause"]["payloads_opened"] == 24
        assert rows["root-cause"]["digests_to_open_every_payload_found"] == 108
        assert rows["success-rubric"]["digests_to_open_every_payload_found"] == 24
        assert rows["harm-rubric"]["digests_to_open_every_payload_found"] == 24
        assert rows["protected-surface"]["payloads_a_candidate_reproduces"] == 22
        assert report["cheapest_kind"] in {"harm-rubric", "success-rubric"}
        assert report["cheapest_kind_digests_for_the_suite"] == 24
        assert report["root_cause_digests_for_the_suite"] == 108

    def test_nothing_opens_on_the_sound_suite(self, sound_suite) -> None:
        """The payload domains stay small; the nonce is what is protecting them."""

        report = audit_commitment_kind_domains(sound_suite.sealed_suite)
        rows = {row["kind"]: row for row in report["kinds"]}

        assert report["cases_with_an_enumerable_nonce"] == 0
        assert report["cheapest_kind"] is None
        assert all(row["payloads_opened"] == 0 for row in report["kinds"])
        assert rows["protected-surface"]["payloads_a_candidate_reproduces"] == 24


# --- The record ---------------------------------------------------------------


class TestTheGapRecord:
    def test_every_closed_gap_says_what_closed_it(self) -> None:
        assert len(CUSTODY_RULE_GAPS_CLOSED) == 6
        for entry in CUSTODY_RULE_GAPS_CLOSED:
            assert "CLOSED" in entry

    def test_the_gaps_that_remain_open_are_not_claimed_as_closed(self) -> None:
        """Two, both found by closing the others, and neither has a check."""

        assert len(CUSTODY_RULE_GAPS) == 2
        assert any("visible_symptom" in gap for gap in CUSTODY_RULE_GAPS)
        assert any("case_artifact_commitment" in gap for gap in CUSTODY_RULE_GAPS)
        for gap in CUSTODY_RULE_GAPS:
            assert "CLOSED" not in gap
