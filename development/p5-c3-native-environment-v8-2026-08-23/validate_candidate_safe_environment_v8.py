#!/usr/bin/env python3
"""Receipt-only validation; never imports or executes DGM source."""

from __future__ import annotations

import hashlib
import json
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    clock = time.monotonic()
    started_at = datetime.now(timezone.utc).isoformat()
    source = json.loads((HERE / "P5_C3_FILTERED_DGM_SOURCE_RECEIPT_V8.json").read_text())
    receipt = json.loads((HERE / "P5_C3_NATIVE_TASK_ENVIRONMENT_RECEIPT_V8.json").read_text())
    seed_path = HERE / receipt["candidate_seed"]["path"]
    assert sha256(seed_path.read_bytes()) == receipt["candidate_seed"]["sha256"]
    expected = {row["path"]: row for row in receipt["candidate_seed"]["members"]}
    observed = {}
    with tarfile.open(seed_path, "r:gz") as tar:
        for member in tar.getmembers():
            assert member.isfile()
            stream = tar.extractfile(member)
            assert stream is not None
            data = stream.read()
            assert member.name not in observed
            observed[member.name] = {
                "size_bytes": len(data),
                "sha256": sha256(data),
                "mode": oct(member.mode),
                "data": data,
            }
    assert set(observed) == set(expected)
    assert len(observed) == 69
    for path, row in expected.items():
        got = observed[path]
        assert (got["size_bytes"], got["sha256"], got["mode"]) == (
            row["size_bytes"], row["sha256"], row["mode"]
        )
    forbidden = ("/initial/", "/initial_polyglot/", "/swe_bench/ref_agent_results/")
    assert not [path for path in observed if any(token in path for token in forbidden)]
    assert len([path for path in observed if path.startswith("candidate/dgm/")]) == 55
    assert len([path for path in observed if path.startswith("candidate/shared_core/")]) == 6
    assert len([path for path in observed if path.startswith("candidate/control/")]) == 8
    assert source["filter"] == {
        "every_included_blob_matches_exact_git_tree": True,
        "excluded_blob_bytes": 49707333,
        "excluded_files": 1595,
        "excluded_payload_contents_opened": False,
        "excluded_prefixes": ["initial/", "initial_polyglot/", "swe_bench/ref_agent_results/"],
        "included_blob_bytes": 3488164,
        "included_files": 55,
    }
    assert receipt["executions"] == {"benchmark": 0, "dgm": 0, "model": 0, "outcomes": 0, "scorer": 0}
    assert receipt["status"] == "BLOCKING" and receipt["field_instances_closed"] == 0
    assert [key for key, passed in receipt["gates"].items() if not passed] == [
        "native_dgm_can_initialize_from_candidate_safe_seed"
    ]
    assert receipt["residual"] == "UNCHANGED_DGM_REQUIRES_EXCLUDED_INITIAL_OUTCOME_METADATA_TO_INITIALIZE"

    certificate = json.loads(observed["candidate/control/P5_C3_INPUT_NATIVE_CERTIFICATE_V8.json"]["data"])
    domain = observed["candidate/control/P5_C3_CASE_ACTION_DOMAIN_V8.json"]["data"]
    proof = observed["candidate/control/P5_C3_FIBRE_CONSTANCY_PROOF_V8.json"]["data"]
    assert certificate["issuance"] == {
        "candidate_visible": True,
        "input_native": True,
        "issuer_role": "HOST_INPUT_VALIDATOR",
        "native_output_access": False,
        "phase": "BEFORE_CANDIDATE_ACTION",
        "protected_outcome_access": False,
        "sequence": 0,
    }
    assert certificate["declared_class"] == "EXECUTION_REPAIR" and certificate["complete"] is True
    assert certificate["basis"]["domain_scope_sha256"] == sha256(domain)
    assert certificate["basis"]["fibre_constancy_attestation"]["proof_ref_sha256"] == sha256(proof)

    policy = json.loads(observed["candidate/control/P5_C3_ENDPOINT_TOOL_WRITE_POLICY_V8.json"]["data"])
    assert policy["network"]["default"] == "DENY"
    assert policy["network"]["candidate_visible_allowed_endpoints"] == []
    assert policy["execution_authorized"] is False
    invocation = json.loads(observed["candidate/control/P5_C3_INVOCATION_ENVIRONMENT_V8.json"]["data"])
    assert invocation["execution_authorized"] is False
    assert invocation["native_initialization_preflight"]["status"] == "BLOCKING"
    assert invocation["source_identity"]["entrypoint_sha256"] == "239bc76f0e1b78210b8f7b3757b1082f6ca07db3537d6af50a45bf97709795ed"
    rights = json.loads(observed["candidate/control/P5_C3_RIGHTS_MANIFEST_V8.json"]["data"])
    authored_paths = rights["components"][2]["paths"]
    assert authored_paths == sorted(path for path in observed if path.startswith("candidate/control/"))

    evidence = HERE / receipt["native_blocker_evidence"]["path"]
    assert sha256(evidence.read_bytes()) == receipt["native_blocker_evidence"]["sha256"]
    text = evidence.read_text()
    for fragment in [
        "19:         archive = ['initial']",
        "33:             raise RuntimeError",
        "63:                 'accuracy_score': metadata['overall_performance']['accuracy_score']",
        "66:                 'total_resolved_ids': metadata['overall_performance']['total_resolved_ids']",
    ]:
        assert fragment in text
    runtime = round(time.monotonic() - clock, 6)
    validation_receipt = {
        "schema_version": "orion.p5.c3.native-task-environment-validation.v8",
        "status": "PASS",
        "seed_sha256": receipt["candidate_seed"]["sha256"],
        "member_count": 69,
        "dgm_source_members": 55,
        "shared_lang1_core_members": 6,
        "control_members": 8,
        "excluded_files": 1595,
        "false_gates": ["native_dgm_can_initialize_from_candidate_safe_seed"],
        "executions": receipt["executions"],
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "runtime_seconds": runtime,
    }
    (HERE / "VALIDATION_RECEIPT_V8.json").write_text(
        json.dumps(validation_receipt, indent=2, sort_keys=True) + "\n"
    )
    print(
        "P5_C3_V8_RECEIPT_VALIDATION_PASS__69_MEMBERS__55_DGM__6_LANG1__8_CONTROL__"
        "1595_EXCLUDED__ONE_EXACT_RESIDUAL__ZERO_EXECUTIONS__"
        f"RUNTIME_SECONDS={runtime:.6f}"
    )


if __name__ == "__main__":
    main()
