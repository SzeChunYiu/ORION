#!/usr/bin/env python3
"""Fail-closed prospective checker for ORION-25's external successor."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent


def load(name: str) -> Any:
    with (HERE / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def all_null_slots(value: Any) -> bool:
    if isinstance(value, dict):
        return all(all_null_slots(v) for k, v in value.items() if k not in {
            "slot", "threshold", "tuf_root_threshold", "targets_threshold",
            "in_toto_layout_threshold"
        })
    if isinstance(value, list):
        return all(all_null_slots(v) for v in value)
    return value is None


def main() -> int:
    protocol = load("PROTOCOL.json")
    software = load("SOFTWARE_LOCK.json")
    corpus = load("CORPUS_MANIFEST.json")
    identity = load("IDENTITY_BINDING.json")
    inclusion = load("INCLUSION_EXCLUSION.json")
    baselines = load("BASELINES.json")
    resources = load("RESOURCE_ACCOUNTING.json")
    expected = load("EXPECTED_TERMINALS.json")

    assert protocol["status"] == "ACQUISITION_PROTOCOL_FROZEN__IDENTITY_BINDING_REQUIRED"
    assert protocol["outcome_status"] == "NO_OUTCOMES_COMMITTED"
    assert protocol["scientific_authority_delta"] == "NONE"
    assert len(protocol["systems"]) == resources["systems"] == 2
    assert {s["id"] for s in protocol["systems"]} == {
        "SYS-COSIGN-DUAL-IDENTITY",
        "SYS-TUF-IN-TOTO-THRESHOLD",
    }

    tools = software["tools"]
    assert tools["cosign"]["tag"] == "v3.1.3"
    assert tools["cosign"]["commit_sha"] == "11926fa5bbbbde47e88fc006b625a17769b743b2"
    assert tools["python_tuf"]["tag"] == "v7.0.0"
    assert tools["python_tuf"]["commit_sha"] == "353bdb767db56fd4667c9bcf56b710d50fdc2ac0"
    assert tools["in_toto"]["tag"] == "v3.1.0"
    assert tools["in_toto"]["commit_sha"] == "c82fe5d21aaa61c7f1a213db20a46f10bb3f411a"

    assert corpus["corpus_size"] == resources["subjects"] == 7
    subjects = corpus["subjects"]
    assert len(subjects) == len({item["id"] for item in subjects}) == 7
    assert len({item["blob_sha"] for item in subjects}) == 7
    assert all(len(item["blob_sha"]) == 40 for item in subjects)

    families = {arm["family"] for arm in protocol["registered_arms"]}
    assert {
        "clean_control",
        "corruption",
        "benign_reencoding",
        "single_domain_compromise",
        "multi_domain_compromise",
        "stale_replay",
        "revocation_rotation",
        "process_liveness",
    } == families

    assert protocol["independent_implementations"]["minimum"] >= 2
    assert resources["minimum_independent_implementations"] >= 2
    assert len(baselines["baselines"]) == 4
    assert any("one operator" in item for item in inclusion["exclude"])

    assert identity["status"] == "PENDING_EXTERNAL_CUSTODY_BINDING"
    assert identity["execution_blocked"] is True
    assert identity["private_key_material_permitted_in_repository"] is False
    assert identity["minimum_distinct_administrative_custodians"] >= 3
    assert all_null_slots(identity["required_bindings"])

    for forbidden in expected["forbidden_current_files"]:
        assert not (HERE / forbidden).exists(), forbidden
    assert not any(path.name.startswith("RESULT") for path in HERE.iterdir())
    assert resources["outcomes_observed"] == 0

    adverse = [
        json.loads(line)
        for line in (HERE / "ADVERSE_AND_CANNOT_CHECK.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    ids = {item["id"] for item in adverse}
    assert {
        "E15-CC-EXTERNAL-CUSTODY",
        "E15-ADV-SIGSTORE-INFRASTRUCTURE-NOT-SEMANTIC-APPROVAL",
        "E15-ADV-FULL-THRESHOLD-COMPROMISE",
        "E15-ADV-NATIVE-SIGNATURE-LIVENESS",
        "E15-CC-OUTCOMES",
    } <= ids

    print(expected["current_checker_terminal"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
