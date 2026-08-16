import hashlib
import json

import pytest

from orion.self_orion.phase2_campaign import (
    Phase2CampaignCriterion,
    Phase2ExternalObservation,
    Phase2ExternalObservationBundle,
    Phase2ExternalObservationStatus,
)
from orion.self_orion.phase2_campaign_io import (
    load_external_observation_bundle,
    write_external_observation_bundle,
)


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode()).hexdigest()


def _bundle():
    subject = _digest("subject")
    evaluator = _digest("evaluator")
    return Phase2ExternalObservationBundle(
        bundle_id="phase2:observations",
        subject_revision_hash=subject,
        evaluator_artifact_hash=evaluator,
        evaluation_epoch_id="epoch:frozen",
        observations=tuple(
            Phase2ExternalObservation(
                criterion=criterion,
                evidence_artifact_id=f"artifact:{criterion.value}",
                evidence_artifact_hash=_digest(f"artifact:{criterion.value}"),
                subject_revision_hash=subject,
                evaluator_artifact_hash=evaluator,
                producer_process_lineage_hash=_digest("producer"),
                verifier_process_lineage_hash=_digest("verifier"),
                evaluation_epoch_id="epoch:frozen",
                split_id=f"split:{criterion.value.lower()}",
                status=Phase2ExternalObservationStatus.COMPLETE,
                frozen_before_candidate=True,
                fresh_split=True,
                note="protected external observation",
            )
            for criterion in Phase2CampaignCriterion
        ),
    )


def test_external_observation_bundle_roundtrips_with_content_identity(tmp_path):
    bundle = _bundle()
    path = tmp_path / "observations.json"
    write_external_observation_bundle(bundle, path)

    loaded = load_external_observation_bundle(path)
    assert loaded == bundle
    assert loaded.artifact_hash == bundle.artifact_hash
    assert len(loaded.observations) == 6


def test_external_observation_bundle_rejects_tampered_content(tmp_path):
    bundle = _bundle()
    path = tmp_path / "observations.json"
    write_external_observation_bundle(bundle, path)
    raw = json.loads(path.read_text())
    raw["observations"][0]["note"] = "post-hoc rewritten note"
    path.write_text(json.dumps(raw))

    with pytest.raises(ValueError, match="artifact hash mismatch"):
        load_external_observation_bundle(path)


def test_external_observation_bundle_rejects_unknown_schema(tmp_path):
    bundle = _bundle()
    path = tmp_path / "observations.json"
    write_external_observation_bundle(bundle, path)
    raw = json.loads(path.read_text())
    raw["schema"] = "Phase2ExternalObservationBundle.v0"
    path.write_text(json.dumps(raw))

    with pytest.raises(ValueError, match="observation schema"):
        load_external_observation_bundle(path)
