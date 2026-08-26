from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "research" / "paper-programme-v1" / "protocols" / "publication_manifest.py"
PAPER_PROTOCOLS = [
    ROOT / "papers" / "orion-11-recursive-epistemic-reconstruction" / "protocol" / "PROTOCOL_V1.json",
    ROOT / "papers" / "orion-12-open-world-scientific-discovery" / "protocol" / "PROTOCOL_V1.json",
    ROOT / "papers" / "orion-13-global-knowledge-portrait" / "protocol" / "PROTOCOL_V1.json",
    ROOT / "papers" / "orion-14-verified-scientific-discovery" / "protocol" / "PROTOCOL_V1.json",
    ROOT / "papers" / "orion-15-self-orion" / "protocol" / "PROTOCOL_V1.json",
]


def _load_module():
    spec = importlib.util.spec_from_file_location("publication_manifest", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_current_frozen_protocols_are_valid_and_content_addressable():
    module = _load_module()
    digests = set()
    for path in PAPER_PROTOCOLS:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert module.validate_protocol(payload) == []
        assert payload["outcome_accessed"] is False
        status = payload["protocol_status"]
        assert status in {"DESIGN_FROZEN", "EXECUTION_FROZEN"}
        unbound = module.unbound_paths(payload["execution_bindings"])
        if status == "DESIGN_FROZEN":
            assert unbound, f"{path} DESIGN_FROZEN protocol must retain prospective UNBOUND identities"
        else:
            assert not unbound, f"{path} EXECUTION_FROZEN protocol must have no UNBOUND identities"
        digest = module.sha256_digest(payload)
        assert len(digest) == 64
        digests.add(digest)
    assert len(digests) == 5


def test_execution_frozen_protocol_rejects_unbound_bindings():
    """Test that EXECUTION_FROZEN status requires all bindings to be bound.

    Uses P2 as the test fixture because P1 is now EXECUTION_FROZEN with fully
    bound bindings. The test simulates promoting P2 to EXECUTION_FROZEN while
    leaving bindings UNBOUND, and verifies that the validator rejects it.
    """
    module = _load_module()
    # Use P2 (paper-02) which is DESIGN_FROZEN with UNBOUND bindings
    payload = json.loads(PAPER_PROTOCOLS[1].read_text(encoding="utf-8"))
    payload["protocol_status"] = "EXECUTION_FROZEN"
    errors = module.validate_protocol(payload)
    assert any("UNBOUND" in error for error in errors)


def test_execution_frozen_protocol_accepts_fully_bound_subject_and_bindings():
    module = _load_module()
    payload = json.loads(PAPER_PROTOCOLS[0].read_text(encoding="utf-8"))
    payload["protocol_status"] = "EXECUTION_FROZEN"
    payload["execution_bindings"] = {
        "subject_revision": "a" * 40,
        "dataset_revisions": {"suite": "sha256:" + "b" * 64},
        "model_provider_revisions": {"candidate": "provider/model@revision"},
        "baseline_config_hashes": {"baseline": "sha256:" + "c" * 64},
        "evaluator_hash": "sha256:" + "d" * 64,
        "split_hashes": {"test": "sha256:" + "e" * 64},
        "evaluation_epoch": "2026-08-16T16:00:00+02:00",
    }
    assert module.validate_protocol(payload) == []


def test_run_manifest_requires_prospective_complete_bindings_and_hashes():
    module = _load_module()
    protocol = json.loads(PAPER_PROTOCOLS[0].read_text(encoding="utf-8"))
    run = {
        "schema_version": "orion.publication-run-manifest.v1",
        "paper_id": "P1",
        "protocol_id": protocol["protocol_id"],
        "protocol_digest": module.sha256_digest(protocol),
        "subject_revision": "a" * 40,
        "data_artifacts": [{"name": "suite", "revision_or_hash": "sha256:" + "b" * 64, "access": "PROTECTED"}],
        "model_provider_revisions": {"candidate": "provider/model@revision"},
        "baseline_config_hashes": {"baseline": "sha256:" + "c" * 64},
        "evaluator_hash": "sha256:" + "d" * 64,
        "split_hashes": {"test": "sha256:" + "e" * 64},
        "evaluation_epoch": "2026-08-16T16:00:00+02:00",
        "seeds": [1, 2, 3],
        "resource_limits": {"tool_calls": 100},
        "environment": {"python": "3.12", "dependencies_hash": "sha256:" + "f" * 64, "runner": "host", "hardware": "cpu"},
        "access_policy_hash": "sha256:" + "1" * 64,
        "artifact_root": "artifact://paper1/run-v1",
        "created_before_outcome_access": True,
    }
    assert module.validate_run_manifest(run) == []
    assert module.sha256_digest(run) == module.sha256_digest(json.loads(json.dumps(run)))

    run["evaluator_hash"] = "UNBOUND"
    errors = module.validate_run_manifest(run)
    assert any("UNBOUND" in error for error in errors)
