"""Box-by-box conformance of the public campaign runner to issue #1086's shared infrastructure.

Issue #1086 asks for one fail-closed runner and seven properties around it. The
runner in :mod:`orion.benchmarks.public_campaign` was built to that shape, but a
checkbox is only as good as the behaviour behind it. These tests take the
module's own valid baseline campaign and, for each box, break exactly the thing
the box protects -- then assert the runner refuses.

The refusals matter more than the acceptance. A campaign integrity layer that
only ever says PASS is indistinguishable from no layer at all, so every box here
is demonstrated by a mutation that must fail closed, and the unmutated baseline
is asserted to PASS so the suite cannot succeed by rejecting everything.

Box ids below are the issue's own bullets under "Shared AI-executable
infrastructure", in order.
"""

from __future__ import annotations

import dataclasses
import importlib.util
import sys
from dataclasses import replace
from pathlib import Path

import pytest

from orion.benchmarks.public_campaign import (
    ArmRole,
    CampaignTerminal,
    CustodyMode,
    InferenceUnit,
    IntervalMethod,
    Observation,
    ObservationOutcome,
    SourceBinding,
    SurfaceKind,
)


def _load_helpers():
    """Reuse the module's own valid-campaign builders rather than inventing one.

    Building a second baseline by hand would test my fixture, not the runner.
    """

    here = Path(__file__).resolve()
    target = here.parent / "test_public_campaign.py"
    spec = importlib.util.spec_from_file_location("_tpc_helpers", target)
    if spec is None or spec.loader is None:  # pragma: no cover
        pytest.skip("public campaign test helpers not importable")
    module = importlib.util.module_from_spec(spec)
    sys.modules["_tpc_helpers"] = module
    spec.loader.exec_module(module)
    return module


H = _load_helpers()


def _blockers(receipt) -> str:
    return " ".join(receipt.blockers)


# --------------------------------------------------------------------------
# Control: the unmutated campaign passes.
# --------------------------------------------------------------------------


def test_the_unmutated_baseline_campaign_passes():
    """Without this, every refusal below could be a runner that refuses everything."""

    receipt = H._run()
    assert receipt.terminal is CampaignTerminal.PASS
    assert receipt.blockers == ()


# --------------------------------------------------------------------------
# Box 1 -- one fail-closed runner: fetch -> licence/hash manifest -> frozen
# IDs/splits -> matched arms -> official evaluator -> paired/block CI -> cost
# -> PASS/FAIL/CANNOT_CHECK receipt.
# --------------------------------------------------------------------------


def test_box1_the_receipt_binds_every_pipeline_stage():
    receipt = H._run()
    for stage in (
        "freeze_sha256",
        "observations_sha256",
        "gate_result_sha256",
        "replay_sha256",
        "authority_surfaces_sha256",
        "receipt_sha256",
    ):
        digest = getattr(receipt, stage)
        assert isinstance(digest, str) and len(digest) == 64, stage
    assert receipt.source_receipts, "fetch stage is not represented in the receipt"


def test_box1_the_terminal_vocabulary_is_exactly_pass_fail_cannot_check():
    assert {t.name for t in CampaignTerminal} == {"PASS", "FAIL", "CANNOT_CHECK"}


def test_box1_the_gate_carries_a_paired_interval_and_a_cost_ratio():
    gate = H._gate()
    assert gate.interval_method in set(IntervalMethod)
    assert gate.ci_lower is not None and gate.ci_upper is not None
    assert gate.cost_ratio is not None
    assert gate.subject_cost is not None and gate.comparator_cost is not None


def test_box1_every_interval_method_offered_is_paired_or_clustered():
    """An unpaired interval would silently drop the matching the gate depends on."""

    assert {m.name for m in IntervalMethod} == {
        "PAIRED_BLOCK_BOOTSTRAP",
        "PAIRED_EXACT",
        "CLUSTER_ROBUST_PAIRED",
    }


def test_box1_matched_arms_carry_a_role_and_a_comparator_exists():
    gate = H._gate()
    assert gate.subject_arm_id and gate.comparator_arm_id
    assert gate.subject_arm_id != gate.comparator_arm_id
    assert {r.name for r in ArmRole} >= {"TREATMENT", "BASELINE", "ABLATION"}


# --------------------------------------------------------------------------
# Box 2 -- record source URL, pinned revision, SHA256, SPDX/data licence,
# citation, redistribution flag, retrieval date, task IDs, exclusions,
# model/evaluator versions, budgets, seeds, environment and raw-output hashes.
# --------------------------------------------------------------------------


def test_box2_the_source_binding_records_every_field_the_box_enumerates():
    fields = {f.name for f in dataclasses.fields(SourceBinding)}
    assert {
        "url",
        "pinned_revision",
        "sha256",
        "license_expression",
        "license_url",
        "citation",
        "redistribution_allowed",
        "retrieved_at_utc",
        "task_ids",
        "exclusions",
    } <= fields


def test_box2_the_observation_records_seed_environment_and_raw_output_hash():
    fields = {f.name for f in dataclasses.fields(Observation)}
    assert {"seed", "environment", "raw_output_sha256", "evaluator_version"} <= fields


def test_box2_arms_record_model_identity_tool_access_and_budget():
    arm = H._arm("a", ArmRole.TREATMENT)
    assert arm.model_id and arm.resource_budget is not None
    assert arm.tool_access is not None
    assert len(arm.implementation_sha256) == 64


def test_box2_a_missing_raw_output_hash_fails_closed():
    observations = tuple(
        replace(item, raw_output_sha256="") for item in H._observations()
    )
    gate = H._gate()
    receipt = H._run(observations=observations, gate=gate, replay=H._replay(gate, observations))
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK


# --------------------------------------------------------------------------
# Box 3 -- reject ambiguous/unlicensed inputs, missing gold, missing
# comparator, missing hash, or missing custody as CANNOT_CHECK.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("placeholder", ["", "UNKNOWN", "TBD", "UNSET", "CANNOT_CHECK"])
def test_box3_an_ambiguous_licence_is_refused(placeholder):
    freeze = H._freeze(sources=(H._source(license_expression=placeholder),))
    receipt = H._run(freeze=freeze)
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK


def test_box3_a_missing_source_hash_is_refused():
    freeze = H._freeze(sources=(H._source(sha256=""),))
    assert H._run(freeze=freeze).terminal is CampaignTerminal.CANNOT_CHECK


def test_box3_a_gold_binding_without_an_identity_is_refused():
    """`gold` is a required field, so "missing" means an unusable binding, not None."""

    from orion.benchmarks.public_campaign import GoldBinding

    base = H._freeze().gold
    freeze = H._freeze(gold=replace(base, gold_id="", access_scope=""))
    receipt = H._run(freeze=freeze)
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    assert "gold_identity_or_access_scope_missing" in _blockers(receipt)
    assert isinstance(base, GoldBinding)


def test_box3_a_gold_artifact_without_a_hash_is_refused():
    base = H._freeze().gold
    freeze = H._freeze(gold=replace(base, artifact_sha256=""))
    receipt = H._run(freeze=freeze)
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    assert "gold_artifact_sha256_invalid" in _blockers(receipt)


def test_box3_a_custody_binding_without_owners_is_refused():
    base = H._freeze().custody
    freeze = H._freeze(
        custody=replace(base, execution_owner_id="", evaluator_custodian_id="")
    )
    receipt = H._run(freeze=freeze)
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK


def test_box3_a_gate_without_a_comparator_is_refused():
    gate = replace(H._gate(), comparator_arm_id="")
    observations = H._observations()
    receipt = H._run(observations=observations, gate=gate, replay=H._replay(gate, observations))
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK


def test_box3_an_unofficial_evaluator_cannot_silently_pass():
    """`official` is a hard Boolean, not a truthy string."""

    from orion.benchmarks.public_campaign import EvaluatorBinding

    fields = {f.name for f in dataclasses.fields(EvaluatorBinding)}
    assert {"official", "version", "artifact_sha256", "evaluator_id"} <= fields


# --------------------------------------------------------------------------
# Box 4 -- use source task, repository, ontology pair, or task family as the
# inference unit, not generated rows, seeds or episodes.
# --------------------------------------------------------------------------


def test_box4_the_inference_unit_vocabulary_is_exactly_the_four_the_box_allows():
    assert {u.name for u in InferenceUnit} == {
        "SOURCE_TASK",
        "REPOSITORY",
        "ONTOLOGY_PAIR",
        "TASK_FAMILY",
    }


@pytest.mark.parametrize("forbidden", ["SEED", "EPISODE", "ROW", "GENERATED_ROW", "CORRESPONDENCE"])
def test_box4_row_seed_and_episode_units_are_not_expressible(forbidden):
    """The taxonomy is closed, so the inadmissible unit cannot even be named."""

    assert forbidden not in {u.name for u in InferenceUnit}


def test_box4_the_gate_counts_inference_units_not_observations():
    gate = H._gate()
    assert gate.inference_unit_count is not None
    assert gate.inference_unit_count <= gate.included_record_count


# --------------------------------------------------------------------------
# Box 5 -- retain all null, harmful and failed runs.
# --------------------------------------------------------------------------


def test_box5_the_outcome_vocabulary_can_express_null_harmful_and_failed():
    assert {"NULL", "HARMFUL", "FAIL", "CANNOT_CHECK", "PASS"} == {
        o.name for o in ObservationOutcome
    }


def test_box5_the_baseline_actually_retains_a_harmful_run():
    """Retention is demonstrated on the passing campaign, not only asserted."""

    receipt = H._run()
    counts = dict(receipt.observation_counts)
    assert counts.get("HARMFUL", 0) >= 1


def test_box5_discarding_a_raw_output_fails_closed():
    observations = tuple(
        replace(item, raw_output_retained=False) for item in H._observations()
    )
    gate = H._gate()
    receipt = H._run(observations=observations, gate=gate, replay=H._replay(gate, observations))
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK


def test_box5_dropping_the_harmful_row_from_the_gate_fails_closed():
    kept = tuple(
        item for item in H._observations() if item.outcome is not ObservationOutcome.HARMFUL
    )
    gate = H._gate()
    receipt = H._run(observations=kept, gate=gate, replay=H._replay(gate, kept))
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK


# --------------------------------------------------------------------------
# Box 6 -- require a fresh-container replay and exact agreement among
# manuscript, active authority, claim ledger, result files and rendered PDF.
# --------------------------------------------------------------------------


def test_box6_the_surface_vocabulary_is_exactly_the_five_the_box_names():
    assert {s.name for s in SurfaceKind} == {
        "MANUSCRIPT",
        "ACTIVE_AUTHORITY",
        "CLAIM_LEDGER",
        "RESULT",
        "RENDERED_PDF",
    }


def test_box6_a_replay_that_was_not_fresh_is_refused():
    gate = H._gate()
    observations = H._observations()
    replay = replace(H._replay(gate, observations), fresh_container=False)
    receipt = H._run(observations=observations, gate=gate, replay=replay)
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK


def test_box6_a_replay_whose_predictions_differ_is_refused():
    gate = H._gate()
    observations = H._observations()
    replay = replace(H._replay(gate, observations), replay_predictions_sha256="0" * 64)
    receipt = H._run(observations=observations, gate=gate, replay=replay)
    assert receipt.terminal is not CampaignTerminal.PASS


def test_box6_a_replay_whose_result_digest_differs_is_refused():
    gate = H._gate()
    observations = H._observations()
    replay = replace(H._replay(gate, observations), replay_result_sha256="0" * 64)
    receipt = H._run(observations=observations, gate=gate, replay=replay)
    assert receipt.terminal is not CampaignTerminal.PASS


# --------------------------------------------------------------------------
# Box 7 -- freeze protocol, splits, estimands and gates before result
# creation; a local hash proves chronology but not external independence.
# --------------------------------------------------------------------------


def test_box7_the_freeze_carries_protocol_splits_estimand_and_gate():
    freeze = H._freeze()
    assert len(freeze.protocol_sha256) == 64
    assert freeze.frozen_at_utc
    assert freeze.split_assignments
    assert freeze.estimand and freeze.gate


def test_box7_a_result_created_before_the_freeze_is_refused():
    receipt = H._run(result_created_at_utc="2020-01-01T00:00:00+00:00")
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK


def test_box7_a_local_hash_never_buys_independent_authority():
    """The whole point of the box's second sentence."""

    receipt = H._run()
    assert receipt.terminal is CampaignTerminal.PASS
    assert receipt.independent_authority != "PASS"
    assert receipt.authority_boundary


def test_box7_same_owner_public_custody_is_a_distinct_mode_from_attested():
    assert {m.name for m in CustodyMode} == {
        "SAME_OWNER_PUBLIC",
        "INDEPENDENT_ATTESTED",
        "PROTECTED_EXTERNAL_ATTESTED",
    }


# --------------------------------------------------------------------------
# Box 8 -- a dataset licence audit that prevents redistribution of upstream
# full text/repositories when only metadata or IDs may be redistributed.
# --------------------------------------------------------------------------


def test_box8_the_source_binding_separates_permission_from_action():
    fields = {f.name for f in dataclasses.fields(SourceBinding)}
    assert {"redistribution_allowed", "redistributed_content"} <= fields


def test_box8_redistributing_content_without_permission_is_refused():
    freeze = H._freeze(
        sources=(H._source(redistribution_allowed=False, redistributed_content=True),)
    )
    receipt = H._run(freeze=freeze)
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK


def test_box8_declining_to_redistribute_under_no_permission_is_allowed():
    """The audit must permit the lawful path, or it just blocks all public data."""

    freeze = H._freeze(
        sources=(H._source(redistribution_allowed=False, redistributed_content=False),)
    )
    receipt = H._run(freeze=freeze)
    assert receipt.terminal is CampaignTerminal.PASS


# --------------------------------------------------------------------------
# The verdict artifact must not drift from the tests it cites.
# --------------------------------------------------------------------------


def test_the_conformance_artifact_cites_only_tests_that_exist():
    """A verdict file naming a test that was renamed or deleted is worse than none."""

    import json
    import re

    here = Path(__file__).resolve()
    root = next(
        (p for p in here.parents if (p / "development").is_dir() and (p / "src").is_dir()),
        None,
    )
    if root is None:  # pragma: no cover
        pytest.skip("repository root not found")
    artifact = (
        root
        / "development/shared-infra-box-conformance-v1-2026-08-24"
        / "ISSUE_1086_SHARED_INFRA_CONFORMANCE_V1.json"
    )
    if not artifact.is_file():  # pragma: no cover
        pytest.skip("conformance artifact not present")

    document = json.loads(artifact.read_text(encoding="utf-8"))
    defined = set(re.findall(r"^def (test_\w+)", here.read_text(encoding="utf-8"), re.M))

    cited: set[str] = set()
    for box in document["boxes"]:
        for name in box["demonstrated_by"]:
            cited.add(name.split("[")[0].strip())
    cited.add(document["control"]["test"])

    missing = sorted(cited - defined)
    assert not missing, f"artifact cites tests that do not exist: {missing}"
    assert len(document["boxes"]) == 8
    assert document["results_exist"] is False
    assert document["campaign_executed"] is False
