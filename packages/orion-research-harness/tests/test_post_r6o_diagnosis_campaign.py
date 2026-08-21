from __future__ import annotations

from orion_research_harness.campaign_control import validate_manifest
from orion_research_harness.domains.registry import (
    builtin_campaign_ids,
    load_builtin_campaign,
)

_CAMPAIGN_ID = "orion-q:post-r6o-diagnosis"

_FORBIDDEN_AUTHORITY_KEYS = {
    "r6_authority",
    "grants_scientific_authority",
    "grants_novelty_authority",
    "grants_revision_authority",
    "grants_adoption_authority",
    "grants_promotion_authority",
    "grants_merge_authority",
    "grants_global_task_stop_authority",
}


def _manifest():
    return load_builtin_campaign(_CAMPAIGN_ID)


def test_manifest_is_registered_and_valid():
    assert _CAMPAIGN_ID in builtin_campaign_ids()
    manifest = _manifest()
    validate_manifest(manifest)
    assert manifest["campaign_id"] == _CAMPAIGN_ID
    assert manifest["initial_phase"] == "D0"


def test_single_decision_phase_plus_terminal():
    phases = _manifest()["phases"]
    assert set(phases) == {"D0", "DIAGNOSIS_RECORDED"}
    assert phases["D0"].get("terminal") is not True
    assert phases["DIAGNOSIS_RECORDED"]["terminal"] is True
    assert (
        phases["DIAGNOSIS_RECORDED"]["terminal_name"]
        == "POST_R6O_DIAGNOSIS_RECORDED__NOT_SELF_AUTHORIZING"
    )


def test_receipt_transcribed_observations_present():
    observations = _manifest()["initial_observations"]
    assert observations["R6_EARNED"] == "NO"
    assert observations["R6_PROTECTED_SUBJECT_ACCESSED"] == "NO"
    assert (
        observations["SUPPORT_DOMINANCE_LOCAL_INEQUALITY"]
        == "VERIFIED_ZERO_VIOLATIONS"
    )
    assert (
        observations["SUPPORT_DOMINANCE_FAMILY_CLOSURE"] == "REFUTED_TAG_ANCHOR_REGIME"
    )
    assert observations["DPLUS_CLOSURE"] == "REFUTED_SECOND_COUPLING_REGIME"
    assert observations["CHEMISTRY_DONOR_EXACT"] == "YES_ALL_30"
    assert observations["EXACT_DP_VERIFICATION"] == "HOSTILE_EXACT_ALL_PANELS"
    assert observations["REGIME_MEMBERSHIP_PREDICATE"] == "ABSENT"
    assert observations["WEIGHT2_CLOSURE"] == "UNTESTED"
    assert all(isinstance(value, str) and value for value in observations.values())


def test_at_least_four_materially_different_hypotheses():
    phase = _manifest()["phases"]["D0"]
    hypotheses = phase["responsibility_hypotheses"]
    ids = [row["hypothesis_id"] for row in hypotheses]
    assert len(ids) >= 4
    assert len(ids) == len(set(ids))
    assert {
        "RESP:CURRENT_SEARCH_INCOMPLETE",
        "RESP:DONOR_FAMILY_INCOMPLETE",
        "RESP:REPRESENTATION_REGIME_UNCHARACTERIZED",
        "RESP:METHOD_LANGUAGE_INADEQUATE",
    } <= set(ids)
    # Every hypothesis is bound to a typed move, and the bound moves are
    # materially different across the layer set.
    bindings = phase["responsibility_bindings"]
    assert set(bindings) == set(ids)
    bound_moves = set()
    for hypothesis_id in ids:
        bound = bindings[hypothesis_id]
        assert bound, hypothesis_id
        bound_moves.update(bound)
    assert len(bound_moves) >= 4


def test_hypotheses_discriminate_on_observation_values_not_by_fiat():
    manifest = _manifest()
    phase = manifest["phases"]["D0"]
    observed = manifest["initial_observations"]
    # The manifest must not hardcode a resolution: every hypothesis carries a
    # non-empty expected-observation set over transcribed discriminators, and no
    # hypothesis row carries a selection/priority marker.
    for row in phase["responsibility_hypotheses"]:
        expected = row["expected_observations"]
        assert expected
        assert "identified" not in row
        assert "selected" not in row
        assert "priority" not in row
        for key, allowed in expected.items():
            assert allowed, key
        # Each hypothesis has a genuine survival region: for each hypothesis
        # there exists at least one discriminator whose allowed set differs from
        # some other hypothesis's allowed set for the same discriminator, or is
        # unique to it (i.e. hypotheses are not clones).
    expectation_sets = [
        {
            (key, tuple(sorted(values)))
            for key, values in row["expected_observations"].items()
        }
        for row in phase["responsibility_hypotheses"]
    ]
    for index, left in enumerate(expectation_sets):
        for right in expectation_sets[index + 1 :]:
            assert left != right
    # Every expected discriminator key is an actually transcribed observation,
    # so discrimination happens on real receipt values inside the production
    # responsibility module, not on unobservable free variables.
    for row in phase["responsibility_hypotheses"]:
        for key in row["expected_observations"]:
            assert key in observed, key


def test_decision_phase_does_not_pre_select_a_winner():
    phase = _manifest()["phases"]["D0"]
    # No phase-wide hard computation obligation: such an obligation would force
    # one fixed computation at control stage 1 regardless of which hypothesis
    # the production modules identify.
    assert phase["active_hard_obligations"] == []
    # Every selectable move (all revision mechanics and all computation actions)
    # is mapped to a capability, so any native outcome can complete the cycle.
    mechanic_ids = {row["mechanic_id"] for row in phase["revision_mechanics"]}
    action_ids = {row["action_id"] for row in phase["computation_actions"]}
    selected = phase["selected_capabilities"]
    assert set(selected) == mechanic_ids | action_ids
    # More than one computation action is registered, so the computation
    # selection is a genuine value comparison rather than a single fixed choice.
    assert len(action_ids) >= 2


def test_computation_before_revision_is_framework_derived():
    phase = _manifest()["phases"]["D0"]
    split = next(
        row
        for row in phase["revision_mechanics"]
        if row["mechanic_id"] == "REV:SPLIT_REPRESENTATION_REGIME"
    )
    # The regime-splitting revision carries the hard requirement; its obligation
    # state is UNRESOLVED, so the production gate itself withholds the revision
    # and the regime-characterization computation is selected on net value only
    # when this hypothesis is the identified survivor.
    assert split["hard_requirements"] == [
        "OBLIGATION:REGIME_MEMBERSHIP_PREDICATE_FROZEN"
    ]
    assert (
        phase["mechanic_obligation_states"][
            "OBLIGATION:REGIME_MEMBERSHIP_PREDICATE_FROZEN"
        ]
        == "UNRESOLVED"
    )
    characterize = next(
        row
        for row in phase["computation_actions"]
        if row["action_id"] == "COMPUTE:REGIME_CHARACTERIZATION"
    )
    assert characterize["discharges_obligations"] == [
        "OBLIGATION:REGIME_MEMBERSHIP_PREDICATE_FROZEN"
    ]
    # Other layers' bound revisions carry no such requirement, so a different
    # identified hypothesis would yield a directly selectable revision.
    for row in phase["revision_mechanics"]:
        if row["mechanic_id"] != "REV:SPLIT_REPRESENTATION_REGIME":
            assert not row.get("hard_requirements")


def _walk(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key, item
            yield from _walk(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _walk(item)


def test_no_capability_grants_authority():
    manifest = _manifest()
    assert manifest["authority_ceiling"] == "BENCHMARK_DIAGNOSTIC_ONLY__BELOW_R6"
    for capability_id, spec in manifest["capabilities"].items():
        for key, item in _walk(spec):
            if key in _FORBIDDEN_AUTHORITY_KEYS:
                assert item is not True, (capability_id, key)
        contract = spec["result_contract"]
        required = {tuple(row["path"]): row["equals"] for row in contract["required_payload_values"]}
        assert (
            required[("authority",)]
            == "POST_R6O_DIAGNOSIS_MOVE_RECORDED__NOT_EXECUTED__NOT_R6"
        )
        assert required[("reserved_stretched_n2_accessed",)] is False
        assert required[("fresh_r6_subject_coefficients_accessed",)] is False
        assert spec["next_phase"] == "DIAGNOSIS_RECORDED"
        # The protected stretched-N2 subject is never named by any capability.
        protected = manifest["protected_refs"][0]
        assert protected["path"] not in spec["payload"]["code"]
        assert protected["blob"] not in spec["payload"]["code"]


def test_protected_subject_remains_unreleased():
    manifest = _manifest()
    ref = manifest["protected_refs"][0]
    assert ref["ref_id"] == "FRESH:R6:STRETCHED_N2_DUCC2"
    assert ref["released"] is False
    for spec in manifest["capabilities"].values():
        assert "release_protected_refs_on_success" not in spec
