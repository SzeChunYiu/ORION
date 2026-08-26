from __future__ import annotations

import json
import pathlib

from orion.study.p1.execution_freeze import (
    STATISTICAL_MODULES,
    FreezeStatus,
    build_manifest,
    statistical_code_hash,
)
from orion.study.p1.precision_tier import TierRule, achieved_tier

REPO = pathlib.Path(__file__).resolve().parents[4]


def test_the_real_protocol_is_execution_frozen() -> None:
    """Every scientific identity is bound: protocol, subject revision, both
    suite fingerprints, subject model, statistical code, evaluator, provider,
    and the precision tier."""

    manifest = build_manifest(repo_root=REPO)
    assert manifest.status is FreezeStatus.EXECUTION_FROZEN, manifest.unresolved
    assert manifest.permits_outcome_access
    # Verify the precision tier is computed correctly
    assert manifest.precision_tier.n == 48  # TEST split has 48 cases
    assert manifest.precision_tier.underpowered  # N=48 cannot power H1 +0.05


def test_a_credential_is_not_a_scientific_identity() -> None:
    """Deliberately absent from the manifest. A credential is a runtime secret,
    and requiring it here would conflate "we do not know what we are measuring"
    with "we cannot reach the provider" — two states this study has to keep
    apart, since only the first should block a freeze."""

    fields = set(build_manifest(repo_root=REPO).to_dict())
    assert not any("credential" in name or "api_key" in name for name in fields)


def test_an_unbound_dataset_blocks_the_freeze(tmp_path) -> None:
    protocol = tmp_path / "PROTOCOL.json"
    protocol.write_text(
        json.dumps(
            {
                "protocol_version": "test",
                "outcome_accessed": False,
                "execution_bindings": {
                    "subject_model": "m",
                    "dataset_revisions": {"hidden_shift_suite_test": "UNBOUND_FINAL_HASH"},
                },
            }
        )
    )
    manifest = build_manifest(repo_root=REPO, protocol_path=protocol)
    assert manifest.status is FreezeStatus.IDENTITIES_UNRESOLVED
    assert any("dataset_unbound" in item for item in manifest.unresolved)
    assert not manifest.permits_outcome_access


def test_a_bound_hash_that_contradicts_the_suite_is_worse_than_an_unbound_one(tmp_path) -> None:
    """An unbound dataset says nothing. A bound hash that does not match the
    files on disk asserts an identity the artifacts contradict, which is a
    stronger and more misleading claim."""

    protocol = tmp_path / "PROTOCOL.json"
    protocol.write_text(
        json.dumps(
            {
                "protocol_version": "test",
                "outcome_accessed": False,
                "execution_bindings": {
                    "subject_model": "m",
                    "dataset_revisions": {
                        "hidden_shift_suite_pilot": "0" * 64,
                        "hidden_shift_suite_test": "0" * 64,
                    },
                },
            }
        )
    )
    manifest = build_manifest(repo_root=REPO, protocol_path=protocol)
    assert any("dataset_hash_mismatch" in item for item in manifest.unresolved)


def test_outcome_access_cannot_be_undone(tmp_path) -> None:
    """Nothing re-freezes after outcomes are read. The honest record is that
    the run is not outcome-blind, and no later binding changes that."""

    protocol = tmp_path / "PROTOCOL.json"
    protocol.write_text(
        json.dumps({"protocol_version": "t", "outcome_accessed": True, "execution_bindings": {}})
    )
    manifest = build_manifest(repo_root=REPO, protocol_path=protocol)
    assert manifest.status is FreezeStatus.OUTCOME_ALREADY_ACCESSED
    assert not manifest.permits_outcome_access


def test_the_statistical_code_is_part_of_the_identity() -> None:
    """The same archive scored by different statistics is a different result.
    A manifest pinning only the data would not say so."""

    baseline = statistical_code_hash(REPO)
    assert len(baseline) == 64
    assert statistical_code_hash(REPO) == baseline
    assert any("statistics.py" in item for item in STATISTICAL_MODULES)


def test_the_frozen_split_is_gated_and_the_pilot_is_not() -> None:
    """PILOT is exempt by design: the protocol designates it for debugging and
    variance estimation, and gating it would make the freeze unreachable, since
    the pilot is how the machinery gets working at all."""

    import inspect

    from orion.study.p1 import run_trial

    source = inspect.getsource(run_trial)
    assert "if split is Split.TEST:" in source
    assert "permits_outcome_access" in source


def test_precision_tier_computed_from_frozen_n() -> None:
    """The precision tier must follow from the frozen TEST split N, not be
    asserted independently. N=48 gives half-width ±0.136, which is BELOW_TIER_D."""

    from orion.study.p1.precision_tier import achieved_tier

    manifest = build_manifest(repo_root=REPO)
    tier_rule = manifest.precision_tier

    # N=48 should give a specific tier and half-width
    assert tier_rule.n == 48
    # At N=48, half-width at p=0.5 is about ±0.136
    assert 0.13 < tier_rule.half_width < 0.15
    # This is BELOW_TIER_D (threshold is 0.10)
    assert "BELOW" in tier_rule.tier.value
    # And it's UNDERPOWERED for H1 +0.05
    assert tier_rule.underpowered
    # H1 superiority cannot be licensed at this N
    assert not tier_rule.licenses_h1_superiority
    # H2 non-inferiority also cannot be licensed
    assert not tier_rule.licenses_h2_non_inferiority


def test_evaluator_hash_is_computed_from_rubric_content() -> None:
    """The evaluator hash must be the SHA256 of the adjudication rubric."""

    manifest = build_manifest(repo_root=REPO)
    assert len(manifest.evaluator_hash) == 64

    # Should match the rubric file hash
    rubric_path = REPO / "papers/orion-11-recursive-epistemic-reconstruction/protocol/ADJUDICATION_RUBRIC_V1.md"
    if rubric_path.exists():
        import hashlib

        expected = hashlib.sha256(rubric_path.read_text(encoding="utf-8").encode()).hexdigest()
        assert manifest.evaluator_hash == expected


def test_model_provider_revisions_follows_glm_relay_pattern() -> None:
    """The provider binding must reference the GLM relay pattern, not a
    hardcoded deployment."""

    manifest = build_manifest(repo_root=REPO)
    # The provider should mention GLM and the relay endpoint
    assert "glm-5.2" in manifest.model_provider_revisions.lower()
    assert "relay" in manifest.model_provider_revisions.lower()
    assert "api2.cmkey.cn" in manifest.model_provider_revisions


def test_unbound_provider_blocks_the_freeze(tmp_path) -> None:
    """model_provider_revisions must be bound, not UNBOUND."""

    protocol = tmp_path / "PROTOCOL.json"
    protocol.write_text(
        json.dumps(
            {
                "protocol_version": "test",
                "outcome_accessed": False,
                "execution_bindings": {
                    "subject_model": "glm-5.2",
                    "dataset_revisions": {"hidden_shift_suite_test": "UNBOUND"},
                    "model_provider_revisions": "UNBOUND",
                },
            }
        )
    )
    manifest = build_manifest(repo_root=REPO, protocol_path=protocol)
    assert manifest.status is FreezeStatus.IDENTITIES_UNRESOLVED
    assert any("model_provider_revisions_unbound" in item for item in manifest.unresolved)


def test_unbound_evaluator_blocks_the_freeze(tmp_path) -> None:
    """evaluator_hash must be bound, not UNBOUND."""

    protocol = tmp_path / "PROTOCOL.json"
    protocol.write_text(
        json.dumps(
            {
                "protocol_version": "test",
                "outcome_accessed": False,
                "execution_bindings": {
                    "subject_model": "glm-5.2",
                    "dataset_revisions": {"hidden_shift_suite_test": "UNBOUND"},
                    "evaluator_hash": "UNBOUND",
                },
            }
        )
    )
    manifest = build_manifest(repo_root=REPO, protocol_path=protocol)
    assert manifest.status is FreezeStatus.IDENTITIES_UNRESOLVED
    assert any("evaluator_hash_unbound" in item for item in manifest.unresolved)


def test_achieved_tier_follows_p2_conventions() -> None:
    """Tier thresholds should match P2's STATISTICAL_PLAN_V1.json conventions
    for consistency across the paper family."""

    from orion.study.p1.precision_tier import achieved_tier

    # TIER_A: half-width ≤ 0.03
    _, hw_a = achieved_tier(1068)
    assert hw_a <= 0.03

    # TIER_B: half-width ≤ 0.05
    _, hw_b = achieved_tier(385)
    assert hw_b <= 0.05

    # TIER_C: half-width ≤ 0.075
    _, hw_c = achieved_tier(171)
    assert hw_c <= 0.075

    # TIER_D: half-width ≤ 0.10
    _, hw_d = achieved_tier(97)
    assert hw_d <= 0.10

    # Below TIER_D: N=48
    tier, hw = achieved_tier(48)
    assert "BELOW" in tier
    assert hw > 0.10
