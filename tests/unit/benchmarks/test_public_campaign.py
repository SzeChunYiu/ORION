from __future__ import annotations

from dataclasses import replace
import hashlib
import json

from orion.benchmarks.public_campaign import (
    ArmRole,
    ArmSpec,
    AuthoritySurface,
    CampaignFreeze,
    CampaignTerminal,
    CustodyBinding,
    CustodyMode,
    EvaluatorBinding,
    GateResult,
    GoldBinding,
    InferenceUnit,
    IntervalMethod,
    Observation,
    ObservationOutcome,
    ReplayBinding,
    SourceBinding,
    SurfaceKind,
    fetch_and_hash_sources,
    run_fail_closed_campaign,
)


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _source(**overrides: object) -> SourceBinding:
    values: dict[str, object] = {
        "source_id": "public-source-v1",
        "url": "https://example.org/archive/public-source-v1.tar.gz",
        "pinned_revision": "release-v1",
        "sha256": _digest("dataset"),
        "license_expression": "CC-BY-4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "citation": "Example Consortium (2026), Public Source v1",
        "redistribution_allowed": False,
        "redistributed_content": False,
        "retrieved_at_utc": "2026-08-24T09:00:00+00:00",
        "task_ids": ("task-1", "task-2"),
        "exclusions": ("upstream full text is not redistributed",),
    }
    values.update(overrides)
    return SourceBinding(**values)  # type: ignore[arg-type]


def _arm(arm_id: str, role: ArmRole, **overrides: object) -> ArmSpec:
    values: dict[str, object] = {
        "arm_id": arm_id,
        "role": role,
        "implementation_sha256": _digest(f"implementation:{arm_id}"),
        "resource_budget": (("attempts", 1.0), ("tokens", 1000.0)),
        "model_id": "model-frozen-v1",
        "tool_access": ("official-evaluator", "source-reader"),
    }
    values.update(overrides)
    return ArmSpec(**values)  # type: ignore[arg-type]


def _freeze(**overrides: object) -> CampaignFreeze:
    values: dict[str, object] = {
        "campaign_id": "p6-p15-public-campaign-fixture-v1",
        "paper_ids": ("P6", "P9", "P15"),
        "protocol_sha256": _digest("protocol"),
        "frozen_at_utc": "2026-08-24T10:00:00+00:00",
        "inference_unit": InferenceUnit.TASK_FAMILY,
        "inference_unit_assignments": (
            ("task-1", "family:task-1"),
            ("task-2", "family:task-2"),
        ),
        "split_assignments": (("task-1", "test"), ("task-2", "test")),
        "estimand": "paired treatment-minus-baseline quality by task family",
        "gate": "lower confidence bound above zero with adverse guards",
        "sources": (_source(),),
        "arms": (
            _arm("orion", ArmRole.TREATMENT),
            _arm("strong-baseline", ArmRole.BASELINE),
        ),
        "evaluator": EvaluatorBinding(
            evaluator_id="official-evaluator",
            version="1.0.0",
            artifact_sha256=_digest("official-evaluator"),
            official=True,
        ),
        "gold": GoldBinding(
            gold_id="official-gold-v1",
            artifact_sha256=_digest("gold"),
            label_schema_sha256=_digest("gold-label-schema"),
            task_ids=("task-1", "task-2"),
            access_scope="PUBLIC_HELD_OUT_TEST_LABELS",
        ),
        "custody": CustodyBinding(
            mode=CustodyMode.SAME_OWNER_PUBLIC,
            execution_owner_id="orion-author-session",
            evaluator_custodian_id="orion-author-session",
            attestation_sha256="",
        ),
        "seeds": (7,),
    }
    values.update(overrides)
    return CampaignFreeze(**values)  # type: ignore[arg-type]


def _environment() -> tuple[tuple[str, str], ...]:
    return (
        ("container_image_sha256", _digest("container")),
        ("dependency_lock_sha256", _digest("lock")),
        ("os", "linux-amd64"),
        ("runtime", "python-3.12"),
    )


def _observations() -> tuple[Observation, ...]:
    rows: list[Observation] = []
    for task_id in ("task-1", "task-2"):
        for arm_id in ("orion", "strong-baseline"):
            outcome = (
                ObservationOutcome.HARMFUL
                if task_id == "task-2" and arm_id == "orion"
                else ObservationOutcome.PASS
            )
            rows.append(
                Observation(
                    task_id=task_id,
                    split_id="test",
                    arm_id=arm_id,
                    seed=7,
                    inference_unit_id=f"family:{task_id}",
                    outcome=outcome,
                    raw_output_sha256=_digest(f"raw:{task_id}:{arm_id}"),
                    raw_output_retained=True,
                    evaluator_version="1.0.0",
                    environment=_environment(),
                    resource_usage=(("attempts", 1.0), ("cost", 0.25), ("tokens", 800.0)),
                )
            )
    return tuple(rows)


def _gate(
    terminal: CampaignTerminal = CampaignTerminal.PASS,
    included: int = 4,
) -> GateResult:
    observations = _observations()
    return GateResult(
        terminal=terminal,
        decision_id="official-gate-v1",
        evaluator_output_sha256=_digest("gate-output"),
        included_record_count=included,
        included_record_ids_sha256=_bundle_digest(
            sorted(item.record_id for item in observations)
        ),
        included_raw_outputs_sha256=_bundle_digest(
            sorted(item.raw_output_sha256 for item in observations)
        ),
        included_observations_sha256=_bundle_digest(_observation_rows(observations)),
        subject_arm_id="orion",
        comparator_arm_id="strong-baseline",
        interval_method=IntervalMethod.PAIRED_BLOCK_BOOTSTRAP,
        confidence_level=0.95,
        inference_unit_count=2,
        effect_estimate=0.10,
        ci_lower=0.01,
        ci_upper=0.19,
        subject_cost=0.50,
        comparator_cost=0.50,
        cost_ratio=1.0,
        omitted_record_ids=(),
        rationale="frozen gate applied to every retained row",
    )


def _bundle_digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _observation_rows(
    observations: tuple[Observation, ...],
) -> list[tuple[str, str, str, str]]:
    return sorted(
        (
            item.record_id,
            item.raw_output_sha256,
            item.outcome.value,
            item.inference_unit_id,
        )
        for item in observations
    )


def _environment_bundle_digest(observations: tuple[Observation, ...]) -> str:
    return _bundle_digest(
        sorted((item.record_id, sorted(item.environment)) for item in observations)
    )


def _replay(**overrides: object) -> ReplayBinding:
    observations = _observations()
    values: dict[str, object] = {
        "fresh_container": True,
        "container_image_sha256": _digest("container"),
        "original_environment_sha256": _environment_bundle_digest(observations),
        "replay_environment_sha256": _environment_bundle_digest(observations),
        "original_predictions_sha256": _bundle_digest(_observation_rows(observations)),
        "replay_predictions_sha256": _bundle_digest(_observation_rows(observations)),
        "original_result_sha256": _digest("gate-output"),
        "replay_result_sha256": _digest("gate-output"),
    }
    values.update(overrides)
    return ReplayBinding(**values)  # type: ignore[arg-type]


def _surfaces(
    terminal: CampaignTerminal = CampaignTerminal.PASS,
) -> tuple[AuthoritySurface, ...]:
    suffixes = {
        SurfaceKind.MANUSCRIPT: ".md",
        SurfaceKind.ACTIVE_AUTHORITY: ".json",
        SurfaceKind.CLAIM_LEDGER: ".json",
        SurfaceKind.RESULT: ".json",
        SurfaceKind.RENDERED_PDF: ".pdf",
    }
    return tuple(
        AuthoritySurface(
            kind=kind,
            path=f"publication/{kind.value.lower()}{suffixes[kind]}",
            file_sha256=_digest(f"file:{kind.value}"),
            declared_terminal=terminal,
            evidence_sha256=_digest("gate-output"),
        )
        for kind in SurfaceKind
    )


def _surface_reader(path: str) -> bytes:
    surface = next(item for item in _surfaces() if item.path == path)
    return f"file:{surface.kind.value}".encode("utf-8")


def _run(
    *,
    freeze: CampaignFreeze | None = None,
    observations: tuple[Observation, ...] | None = None,
    gate: GateResult | None = None,
    replay: ReplayBinding | None = None,
    surfaces: tuple[AuthoritySurface, ...] | None = None,
    result_created_at_utc: str = "2026-08-24T11:00:00+00:00",
):
    freeze = freeze or _freeze()
    receipts = fetch_and_hash_sources(freeze, lambda _: b"dataset")
    return run_fail_closed_campaign(
        freeze=freeze,
        source_receipts=receipts,
        observations=observations if observations is not None else _observations(),
        gate_result=gate or _gate(),
        replay=replay or _replay(),
        authority_surfaces=surfaces if surfaces is not None else _surfaces(),
        surface_reader=_surface_reader,
        result_created_at_utc=result_created_at_utc,
    )


def test_complete_bundle_passes_local_gate_but_never_claims_independence() -> None:
    receipt = _run()
    assert receipt.terminal is CampaignTerminal.PASS
    assert receipt.blockers == ()
    assert dict(receipt.observation_counts) == {"HARMFUL": 1, "PASS": 3}
    assert receipt.independent_authority == "CANNOT_CHECK"
    assert "same-owner replay do not establish" in receipt.authority_boundary
    assert len(receipt.receipt_sha256) == 64
    assert all(
        len(digest) == 64
        for digest in (
            receipt.freeze_sha256,
            receipt.observations_sha256,
            receipt.gate_result_sha256,
            receipt.replay_sha256,
            receipt.authority_surfaces_sha256,
        )
    )


def test_receipt_digest_is_stable_under_bundle_input_order() -> None:
    freeze = _freeze()
    receipts = fetch_and_hash_sources(freeze, lambda _: b"dataset")
    forward = run_fail_closed_campaign(
        freeze=freeze,
        source_receipts=receipts,
        observations=_observations(),
        gate_result=_gate(),
        replay=_replay(),
        authority_surfaces=_surfaces(),
        surface_reader=_surface_reader,
        result_created_at_utc="2026-08-24T11:00:00+00:00",
    )
    reverse = run_fail_closed_campaign(
        freeze=freeze,
        source_receipts=tuple(reversed(receipts)),
        observations=tuple(reversed(_observations())),
        gate_result=_gate(),
        replay=_replay(),
        authority_surfaces=tuple(reversed(_surfaces())),
        surface_reader=_surface_reader,
        result_created_at_utc="2026-08-24T11:00:00+00:00",
    )
    assert reverse.receipt_sha256 == forward.receipt_sha256


def test_gate_metrics_are_cryptographically_bound_into_receipt() -> None:
    first = _run()
    changed_gate = replace(
        _gate(), effect_estimate=0.5, ci_lower=0.4, ci_upper=0.6
    )
    second = _run(gate=changed_gate)
    assert first.terminal is CampaignTerminal.PASS
    assert second.terminal is CampaignTerminal.PASS
    assert second.receipt_sha256 != first.receipt_sha256
    assert second.gate_result_sha256 != first.gate_result_sha256


def test_ambiguous_license_prevents_fetch_and_fails_closed() -> None:
    calls = 0

    def fetcher(_: SourceBinding) -> bytes:
        nonlocal calls
        calls += 1
        return b"dataset"

    freeze = _freeze(sources=(_source(license_expression="CANNOT_CHECK"),))
    receipts = fetch_and_hash_sources(freeze, fetcher)
    assert calls == 0
    assert receipts[0].terminal is CampaignTerminal.CANNOT_CHECK
    assert "license_ambiguous" in receipts[0].blocker


def test_hash_mismatch_and_prohibited_redistribution_cannot_check() -> None:
    freeze = _freeze(
        sources=(
            _source(
                redistributed_content=True,
                redistribution_allowed=False,
            ),
        )
    )
    receipt = _run(freeze=freeze)
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    assert any("redistribution_prohibited" in blocker for blocker in receipt.blockers)

    valid = _freeze()
    source_receipts = fetch_and_hash_sources(valid, lambda _: b"wrong bytes")
    receipt = run_fail_closed_campaign(
        freeze=valid,
        source_receipts=source_receipts,
        observations=_observations(),
        gate_result=_gate(),
        replay=_replay(),
        authority_surfaces=_surfaces(),
        surface_reader=_surface_reader,
        result_created_at_utc="2026-08-24T11:00:00+00:00",
    )
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    assert any("fetch_or_hash_not_pass" in blocker for blocker in receipt.blockers)


def test_pass_source_receipt_cannot_retain_a_blocker() -> None:
    freeze = _freeze()
    receipts = fetch_and_hash_sources(freeze, lambda _: b"dataset")
    receipts = (replace(receipts[0], blocker="source_hash_mismatch"),)
    receipt = run_fail_closed_campaign(
        freeze=freeze,
        source_receipts=receipts,
        observations=_observations(),
        gate_result=_gate(),
        replay=_replay(),
        authority_surfaces=_surfaces(),
        surface_reader=_surface_reader,
        result_created_at_utc="2026-08-24T11:00:00+00:00",
    )
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    assert "source:public-source-v1:pass_receipt_contains_blocker" in receipt.blockers


def test_unmatched_budgets_and_generated_row_unit_cannot_check() -> None:
    arms = (
        _arm("orion", ArmRole.TREATMENT),
        _arm(
            "strong-baseline",
            ArmRole.BASELINE,
            resource_budget=(("attempts", 2.0), ("tokens", 1000.0)),
        ),
    )
    freeze = _freeze(arms=arms, inference_unit="generated_row")
    receipt = _run(freeze=freeze)
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    assert "arm_resource_budgets_not_exactly_matched" in receipt.blockers
    assert "inference_unit_not_allowed" in receipt.blockers


def test_execution_identity_and_every_usage_dimension_must_be_frozen() -> None:
    arms = (
        _arm("orion", ArmRole.TREATMENT, model_id="", tool_access=()),
        _arm("strong-baseline", ArmRole.BASELINE, model_id="", tool_access=()),
    )
    observations = list(_observations())
    observations[0] = replace(
        observations[0],
        resource_usage=observations[0].resource_usage + (("gpu_hours", 99999.0),),
    )
    receipt = _run(freeze=_freeze(arms=arms), observations=tuple(observations))
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    assert any("model_identity_missing" in blocker for blocker in receipt.blockers)
    assert any(
        "tool_access_missing_or_invalid" in blocker for blocker in receipt.blockers
    )
    assert any("unfrozen_resource_dimension" in blocker for blocker in receipt.blockers)


def test_missing_gold_or_custody_binding_cannot_check() -> None:
    freeze = _freeze(
        gold=GoldBinding(
            gold_id="",
            artifact_sha256="",
            label_schema_sha256="",
            task_ids=(),
            access_scope="",
        ),
        custody=CustodyBinding(
            mode="",
            execution_owner_id="",
            evaluator_custodian_id="",
            attestation_sha256="",
        ),
    )
    receipt = _run(freeze=freeze)
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    expected = {
        "gold_identity_or_access_scope_missing",
        "gold_artifact_sha256_invalid",
        "gold_label_schema_sha256_invalid",
        "gold_task_coverage_mismatch",
        "custody_mode_missing_or_invalid",
        "custody_identity_missing",
    }
    assert expected.issubset(receipt.blockers)


def test_external_custody_claim_needs_attestation_but_still_is_not_self_proving() -> None:
    freeze = _freeze(
        custody=CustodyBinding(
            mode=CustodyMode.INDEPENDENT_ATTESTED,
            execution_owner_id="author",
            evaluator_custodian_id="external-host",
            attestation_sha256="",
        )
    )
    receipt = _run(freeze=freeze)
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    assert "external_custody_attestation_sha256_invalid" in receipt.blockers

    bound = replace(
        freeze,
        custody=replace(freeze.custody, attestation_sha256=_digest("attestation")),
    )
    receipt = _run(freeze=bound)
    assert receipt.terminal is CampaignTerminal.PASS
    assert receipt.independent_authority == "CANNOT_CHECK"

    contradictory = replace(
        bound,
        custody=replace(
            bound.custody,
            execution_owner_id="same-owner",
            evaluator_custodian_id="same-owner",
        ),
    )
    receipt = _run(freeze=contradictory)
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    assert "external_custody_owner_and_custodian_must_differ" in receipt.blockers


def test_missing_or_duplicate_record_cannot_hide_adverse_output() -> None:
    observations = _observations()
    without_harm = tuple(
        row for row in observations if row.outcome is not ObservationOutcome.HARMFUL
    )
    receipt = _run(observations=without_harm, gate=_gate(included=3))
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    assert "execution_record_cartesian_coverage_mismatch" in receipt.blockers

    duplicated = observations + (observations[0],)
    receipt = _run(observations=duplicated, gate=_gate(included=5))
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    assert "execution_records_duplicated" in receipt.blockers


def test_evaluator_and_environment_drift_cannot_check() -> None:
    observations = list(_observations())
    observations[0] = replace(
        observations[0],
        evaluator_version="2.0.0",
        environment=(("os", "linux-amd64"),),
    )
    receipt = _run(observations=tuple(observations))
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    assert any("evaluator_version_drift" in blocker for blocker in receipt.blockers)
    assert any("environment_incomplete" in blocker for blocker in receipt.blockers)


def test_post_outcome_freeze_cannot_check() -> None:
    receipt = _run(result_created_at_utc="2026-08-24T09:59:59+00:00")
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    assert "protocol_not_frozen_before_result" in receipt.blockers


def test_source_retrieved_after_result_cannot_check() -> None:
    freeze = _freeze(
        sources=(_source(retrieved_at_utc="2026-08-24T12:00:00+00:00"),)
    )
    receipt = _run(freeze=freeze)
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    assert "source:public-source-v1:retrieved_not_before_result" in receipt.blockers


def test_replay_mismatch_or_nonfresh_container_cannot_check() -> None:
    replay = _replay(
        fresh_container=False,
        replay_predictions_sha256=_digest("different-predictions"),
    )
    receipt = _run(replay=replay)
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    assert "replay:not_fresh_container" in receipt.blockers
    assert "replay:prediction_digest_mismatch" in receipt.blockers


def test_replay_result_must_equal_gate_and_environment_must_equal_execution() -> None:
    unrelated = _digest("unrelated-result")
    replay = _replay(
        original_result_sha256=unrelated,
        replay_result_sha256=unrelated,
        original_environment_sha256=_digest("unrelated-environment"),
        replay_environment_sha256=_digest("unrelated-environment"),
    )
    receipt = _run(replay=replay)
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    assert "replay:original_result_not_bound_to_gate" in receipt.blockers
    assert "replay:replay_result_not_bound_to_gate" in receipt.blockers
    assert "replay:original_environment_not_bound_to_execution_records" in receipt.blockers
    assert "replay:environment_digest_mismatch" in receipt.blockers


def test_authority_surface_mismatch_cannot_check() -> None:
    surfaces = list(_surfaces())
    surfaces[0] = replace(
        surfaces[0], declared_terminal=CampaignTerminal.FAIL, evidence_sha256=_digest("other")
    )
    receipt = _run(surfaces=tuple(surfaces))
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    assert any("terminal_mismatch" in blocker for blocker in receipt.blockers)
    assert any("evidence_digest_mismatch" in blocker for blocker in receipt.blockers)


def test_authority_surfaces_require_unique_canonical_paths_and_verified_bytes() -> None:
    aliased = tuple(
        replace(
            surface,
            path="publication/same.file",
            file_sha256=_digest("fabricated-same-file"),
        )
        for surface in _surfaces()
    )
    receipt = _run(surfaces=aliased)
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    assert "authority_surface_paths_aliased" in receipt.blockers
    assert "authority_surface_file_hashes_aliased" in receipt.blockers
    assert any("read_failed" in blocker for blocker in receipt.blockers)

    noncanonical = list(_surfaces())
    noncanonical[0] = replace(noncanonical[0], path="publication/../escape.md")
    receipt = _run(surfaces=tuple(noncanonical))
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    assert any("path_or_file_sha256_invalid" in blocker for blocker in receipt.blockers)


def test_gate_must_bind_exact_record_and_raw_output_identities() -> None:
    gate = replace(
        _gate(),
        included_record_ids_sha256=_digest("wrong-record-set"),
        included_raw_outputs_sha256=_digest("wrong-raw-output-set"),
    )
    receipt = _run(gate=gate)
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    assert "gate_record_identity_binding_mismatch" in receipt.blockers
    assert "gate_raw_output_binding_mismatch" in receipt.blockers


def test_swapping_raw_outputs_between_records_breaks_association_binding() -> None:
    observations = list(_observations())
    observations[0] = replace(
        observations[0], raw_output_sha256=observations[1].raw_output_sha256
    )
    observations[1] = replace(
        observations[1], raw_output_sha256=_observations()[0].raw_output_sha256
    )
    receipt = _run(observations=tuple(observations))
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    assert "gate_observation_association_binding_mismatch" in receipt.blockers
    assert "replay:predictions_not_bound_to_execution_records" in receipt.blockers


def test_gate_must_use_paired_units_valid_interval_and_observed_costs() -> None:
    observations = list(_observations())
    observations[1] = replace(observations[1], inference_unit_id="family:drift")
    gate = replace(
        _gate(),
        interval_method="row-bootstrap",
        confidence_level=0.90,
        inference_unit_count=99,
        effect_estimate=0.5,
        ci_lower=0.6,
        ci_upper=0.4,
        subject_cost=9.0,
        cost_ratio=17.0,
    )
    receipt = _run(observations=tuple(observations), gate=gate)
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    expected = {
        "paired_arms_disagree_on_inference_unit_identity",
        "gate_interval_method_not_paired_or_blocked",
        "gate_confidence_level_not_95_percent",
        "gate_confidence_interval_order_invalid",
        "gate_inference_unit_count_mismatch",
        "gate_subject_cost_mismatch",
        "gate_cost_ratio_mismatch",
    }
    assert expected.issubset(receipt.blockers)


def test_budget_overrun_nan_duplicate_budget_and_environment_drift_cannot_pass() -> None:
    observations = list(_observations())
    observations[0] = replace(
        observations[0],
        resource_usage=(("attempts", 999.0), ("cost", 0.25), ("tokens", 999999.0)),
    )
    drifted_environment = dict(observations[1].environment)
    drifted_environment["container_image_sha256"] = _digest("other-container")
    observations[1] = replace(
        observations[1], environment=tuple(sorted(drifted_environment.items()))
    )
    arms = (
        _arm(
            "orion",
            ArmRole.TREATMENT,
            resource_budget=(("attempts", float("nan")), ("attempts", 1.0)),
        ),
        _arm(
            "strong-baseline",
            ArmRole.BASELINE,
            resource_budget=(("attempts", float("nan")), ("attempts", 1.0)),
        ),
    )
    receipt = _run(freeze=_freeze(arms=arms), observations=tuple(observations))
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    assert any("resource_budget_fields_duplicated" in item for item in receipt.blockers)
    assert any("resource_budget_invalid" in item for item in receipt.blockers)
    assert any("resource_budget_exceeded" in item for item in receipt.blockers)
    assert "paired_arms_disagree_on_environment" in receipt.blockers
    assert any("container_image_not_bound_to_replay" in item for item in receipt.blockers)


def test_source_task_inference_units_cannot_be_collapsed_or_relabelled() -> None:
    freeze = _freeze(
        inference_unit=InferenceUnit.SOURCE_TASK,
        inference_unit_assignments=(("task-1", "one-unit"), ("task-2", "one-unit")),
    )
    observations = tuple(replace(item, inference_unit_id="one-unit") for item in _observations())
    gate = replace(_gate(), inference_unit_count=1)
    receipt = _run(freeze=freeze, observations=observations, gate=gate)
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    assert "source_task_inference_units_must_equal_frozen_task_ids" in receipt.blockers

    valid_freeze = _freeze()
    drifted = list(_observations())
    drifted[0] = replace(drifted[0], inference_unit_id="unfrozen-unit")
    receipt = _run(freeze=valid_freeze, observations=tuple(drifted))
    assert receipt.terminal is CampaignTerminal.CANNOT_CHECK
    assert any("inference_unit_identity_drift" in item for item in receipt.blockers)


def test_verified_adverse_gate_remains_fail_and_all_rows_remain_counted() -> None:
    receipt = _run(
        gate=_gate(CampaignTerminal.FAIL),
        surfaces=_surfaces(CampaignTerminal.FAIL),
    )
    assert receipt.terminal is CampaignTerminal.FAIL
    assert receipt.blockers == ()
    assert dict(receipt.observation_counts)["HARMFUL"] == 1
    assert receipt.independent_authority == "CANNOT_CHECK"
