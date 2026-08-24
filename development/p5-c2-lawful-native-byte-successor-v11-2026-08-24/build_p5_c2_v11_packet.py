#!/usr/bin/env python3
"""Build/finalize the execution-free P5 C2 V11 successor packet.

Phase ``freeze`` authors and content-addresses the six required byte classes.
Phase ``finalize`` is permitted only after the separate route adapter writes a
six-class PASS receipt.  Neither phase executes MOSS, a model, an evaluator, a
benchmark, a scorer, protected data, repository CI, or a test framework.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
DEVELOPMENT = HERE.parent
FROZEN_AT = "2026-08-24T05:58:00Z"
SEARCHED_AT = "2026-08-24T05:47:08Z"
IDENTITY = "C2_LAWFUL_NATIVE_BYTE_SUCCESSOR__ORION_V11"
PROTOCOL_ID = "P5.C2.LAWFUL.NATIVE.BYTE.SUCCESSOR.V11"
MOSS_COMMIT = "5453f1feebad44c199f5887f852fc5bc7fb7d4da"
MOSS_TAG_COMMIT = "9f1b2929a6a1b6d405e0ce378d52cc8c8293618c"
SOURCE_ARCHIVE_SHA = "f97c316795a6ba124f693bce9e8019b1735bc976affa9bce8d4c52f668575f08"
SOURCE_TREE_MANIFEST_SHA = "4fbe1517b1bf3c549986272fe16fead6a8e4eb6f3cfa47f09c3a92bf94162abc"
V3_DOMAIN_SHA = "b9486f227fc46513b9ab9547598e301869380310cab2e1a60a87bd19fe585a04"
V3_PROOF_SHA = "30adb98d2f580c4fcd77695269451547e44e6bb230b6dd290d73dab61733b026"
V10_CONTRACT_SHA = "411068074fb2292519f14ea8886c3071a9d35ad627b46229a4f4ae182aca0088"
V10_RESULT_SHA = "b459e5d4f6cfc10a0b09ccb237714dbf84601bec88e353f2c988e247d0c8fc95"
TARGET = "src/main/java/org/apache/commons/lang3/math/NumberUtils.java"

V6 = DEVELOPMENT / "p5-common-visible-case-rights-v6-2026-08-23"
V3 = DEVELOPMENT / "p5-six-arm-adapter-refinement-v3-2026-08-23"
V4 = DEVELOPMENT / "p5-moss-execution-binding-v4-2026-08-23"
V10 = DEVELOPMENT / "p5-c2-authoritative-route-discriminator-v10-2026-08-23"
SOURCE_ARCHIVE = V6 / "candidate_visible/source/commons-lang-396afc3e4693cfee182efe582455f2d97058c068.tar.gz"
JDK_HOME = Path("/opt/homebrew/Cellar/openjdk@17/17.0.19/libexec/openjdk.jdk/Contents/Home")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical(value), encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return value


def packet_ref(path: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(HERE).as_posix(),
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size,
    }


def repo_ref(path: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(REPO_ROOT).as_posix(),
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size,
    }


def assert_hash(path: Path, expected: str) -> None:
    actual = sha256(path)
    if actual != expected:
        raise RuntimeError(f"identity mismatch for {path}: {actual} != {expected}")


def freeze() -> None:
    assert_hash(SOURCE_ARCHIVE, SOURCE_ARCHIVE_SHA)
    assert_hash(V3 / "P5_V3_DECLARED_SYNTHETIC_DOMAIN.json", V3_DOMAIN_SHA)
    assert_hash(V3 / "P5_V3_SYNTHETIC_CONFORMANCE_RECEIPT.json", V3_PROOF_SHA)
    assert_hash(V10 / "P5_C2_V10_SUCCESSOR_BYTE_CONTRACT.json", V10_CONTRACT_SHA)
    assert_hash(V10 / "P5_C2_V10_RESULT.json", V10_RESULT_SHA)
    for required in (
        HERE / "p5_c2_v11_route_adapter.py",
        HERE / "evaluator/public_hex_classifier_evaluator.py",
        HERE / "licenses/CC0-1.0.txt",
        HERE / "licenses/APACHE-2.0.txt",
        HERE / "licenses/APACHE-NOTICE.txt",
        HERE / "licenses/OPENJDK-17-LICENSE.txt",
    ):
        if not required.is_file():
            raise RuntimeError(f"required authored/copied byte missing: {required}")

    case_body = load(V6 / "candidate_visible/CASE_BODY_V6.json")
    problem = case_body["problem"]["statement"]
    chunk = {
        "schema_version": "orion.p5.c2.authored-session-chunk.v11",
        "sequence": 1,
        "role": "user",
        "content": problem,
        "source": "V6 candidate-visible authored public-development case body",
        "candidate_outcome_or_evaluator_feedback_present": False,
    }
    write_json(HERE / "session/chunk-0001.json", chunk)
    flag = {
        "flag_id": "P5-C2-V11-LANG1-AUTHORED-001",
        "batch_id": "P5-C2-V11-LAWFUL-NATIVE-BYTE-SUCCESSOR",
        "flagged_at": 1787551080000,
        "flagged_by": "orion-v11-packet-author",
        "user_prompt": {"text": problem, "language": "en"},
        "agent_trace": [
            {
                "role": "user",
                "content": [{"type": "text", "text": problem}],
            }
        ],
        "tool_dispatches": [],
        "agent_tool_registry_at_flag_time": [],
        "optional_reason": "Frozen public-development task materialization only; no run or outcome selected this session.",
        "source_session_id": "P5-V11-AUTHORED-PUBLIC-DEVELOPMENT-SESSION",
        "source_turn_range": [0, 0],
        "source_user_message_index": 0,
    }
    write_json(HERE / "session/FLAG_SNAPSHOT_V11.json", flag)
    session_manifest = {
        "schema_version": "orion.p5.c2.authored-session-manifest.v11",
        "session_id": flag["source_session_id"],
        "authority": "AUTHORED_PUBLIC_DEVELOPMENT_SESSION_ONLY",
        "flag_snapshot_sha256": sha256(HERE / "session/FLAG_SNAPSHOT_V11.json"),
        "chunk_count": 1,
        "chunks": [packet_ref(HERE / "session/chunk-0001.json")],
        "complete_chunk_enumeration": True,
        "candidate_outcome_selected": False,
        "outcome_or_feedback_bytes_present": False,
        "case_selection_boundary": "INHERITED_POST_OUTCOME_PUBLIC_DEVELOPMENT_CASE__NOT_CONFIRMATORY",
        "selection_note": "The session was authored from the already frozen V6 public-development case, not chosen by a V11 candidate result. V6 case selection remains known post-outcome and cannot support confirmatory claims.",
        "rights": "CC0-1.0 for newly authored session bytes",
    }
    write_json(HERE / "session/P5_C2_V11_SESSION_MANIFEST.json", session_manifest)

    cases = {
        "schema_version": "orion.p5.c2.public-hex-classification-cases.v11",
        "authority": "PUBLIC_DEVELOPMENT_ONLY",
        "case_selection": "Mechanistically exhaustive public boundary probes derived from the candidate-visible V6 task statement before any V11 candidate action.",
        "protected_or_hidden_cases_present": False,
        "cases": [
            {"case_id": "HEX_INT_MAX", "input": "0x7fffffff", "expected_class": "Integer", "mechanism": "signed Integer positive boundary"},
            {"case_id": "HEX_INT_OVER", "input": "0x80000000", "expected_class": "Long", "mechanism": "first positive magnitude above Integer"},
            {"case_id": "HEX_LONG_MAX", "input": "0x7fffffffffffffff", "expected_class": "Long", "mechanism": "signed Long positive boundary"},
            {"case_id": "HEX_LONG_OVER", "input": "0x8000000000000000", "expected_class": "BigInteger", "mechanism": "first positive magnitude above Long"},
            {"case_id": "HEX_LEADING_ZERO_INT_OVER", "input": "0x0000000080000000", "expected_class": "Long", "mechanism": "leading-zero invariance above Integer"},
            {"case_id": "HEX_LEADING_ZERO_LONG_OVER", "input": "0x00008000000000000000", "expected_class": "BigInteger", "mechanism": "leading-zero invariance above Long"},
        ],
    }
    write_json(HERE / "evaluator/PUBLIC_HEX_CLASSIFICATION_CASES_V11.json", cases)

    runtime = {
        "schema_version": "orion.p5.c2.jdk-runtime-lock.v11",
        "runtime": "OpenJDK 17.0.19 Homebrew formula",
        "java_home": str(JDK_HOME),
        "executables": {
            "java": {"path": str(JDK_HOME / "bin/java"), "sha256": sha256(JDK_HOME / "bin/java")},
            "javac": {"path": str(JDK_HOME / "bin/javac"), "sha256": sha256(JDK_HOME / "bin/javac")},
        },
        "release_file": {"path": str(JDK_HOME / "release"), "sha256": sha256(JDK_HOME / "release")},
        "license": {
            "spdx": "GPL-2.0-only WITH Classpath-exception-2.0",
            "packet_path": "licenses/OPENJDK-17-LICENSE.txt",
            "sha256": sha256(HERE / "licenses/OPENJDK-17-LICENSE.txt"),
        },
        "path_fallback_allowed": False,
        "network_required": False,
        "evaluator_executed_by_v11_route_gate": False,
    }
    if runtime["executables"]["java"]["sha256"] != "7db0dd5c0c4dc931244875d0723783a32cc7912922e6aaac1dbb744bf8ae837f":
        raise RuntimeError("java lock drift")
    if runtime["executables"]["javac"]["sha256"] != "a7905f0d4944e3aee8aa20673f199a688b815545f930ee537b3d28a578ae2861":
        raise RuntimeError("javac lock drift")
    write_json(HERE / "P5_C2_V11_JDK_RUNTIME_LOCK.json", runtime)

    raw_dir = HERE / "upstream_search"
    raw_files = sorted(raw_dir.glob("*.json"))
    branches = json.loads((raw_dir / "branches.json").read_text())
    tags = json.loads((raw_dir / "tags.json").read_text())
    releases = json.loads((raw_dir / "releases.json").read_text())
    forks = json.loads((raw_dir / "forks.json").read_text())
    owner_repos = json.loads((raw_dir / "owner_repos.json").read_text())
    issue = json.loads((raw_dir / "issue3.json").read_text())
    comments = json.loads((raw_dir / "issue3_comments.json").read_text())
    exact_search = json.loads((raw_dir / "code_search_exact.json").read_text())
    if not (
        len(branches) == 1
        and branches[0]["name"] == "main"
        and branches[0]["commit"]["sha"] == MOSS_COMMIT
        and len(tags) == 1
        and tags[0]["commit"]["sha"] == MOSS_TAG_COMMIT
        and releases == []
        and len(forks) == 3
        and issue["state"] == "open"
        and issue["comments"] == 0
        and comments == []
        and exact_search["total_count"] == 0
    ):
        raise RuntimeError("upstream snapshot observations drifted")
    upstream = {
        "schema_version": "orion.p5.c2.upstream-successor-search-receipt.v11",
        "searched_at_utc": SEARCHED_AT,
        "authority": "PUBLIC_UPSTREAM_DISCOVERY_ONLY",
        "queries": [
            "MOSS branches, tags, releases and forks",
            "maintainer repository enumeration",
            "issue 3 state/comments",
            "exact public code search for benchmark/claw-eval/runner/benchmark.py",
            "repository and code searches for MOSS/claw-eval companions",
        ],
        "observations": {
            "main_commit": MOSS_COMMIT,
            "public_tag_count": 1,
            "only_tag": "v0.1.0",
            "public_release_count": 0,
            "returned_fork_count": len(forks),
            "maintainer_repository_count": len(owner_repos),
            "maintainer_companion_found": False,
            "issue_3_state": issue["state"],
            "issue_3_comment_count": issue["comments"],
            "exact_runner_code_search_count": exact_search["total_count"],
        },
        "raw_snapshots": [packet_ref(path) for path in raw_files],
        "verdict": "NO_LAWFUL_UPSTREAM_COMPANION_FOUND__PROCEED_ONLY_AS_DISTINCT_AUTHORED_SUCCESSOR",
        "released_moss_state_changed": False,
    }
    write_json(HERE / "P5_C2_V11_UPSTREAM_SEARCH_RECEIPT.json", upstream)

    protocol = {
        "schema_version": "orion.p5.c2.lawful-native-byte-successor-protocol.v11",
        "protocol_id": PROTOCOL_ID,
        "frozen_at_utc": FROZEN_AT,
        "authority": "EXECUTION_FREE_BYTE_ROUTE_AND_RUNTIME_TASK_ENVIRONMENT_ONLY",
        "development_question": "Can a distinctly named lawful successor materialize and route all six V10 byte classes for the V6 LANG-1 public-development task without executing any candidate or outcome-producing component?",
        "atomic_questions": [
            "Are authored session bytes complete, hashed, licensed, and free of candidate outcome/feedback bytes?",
            "Is the exact V6 source both read-only and overlaid with only NumberUtils.java writable?",
            "Is one V3-compatible certificate issued by the host before candidate action with its synthetic authority boundary explicit?",
            "Are evaluator, public cases, runtime and rights bytes closed outside candidate writes?",
            "Are every allowed/forbidden root, before/after digest, reset and destruction rule executable?",
            "Does a distinct content-addressed adapter actually mount all preceding classes without claiming released MOSS identity?",
        ],
        "saturation_assessment": {
            "knowledge": "V10 exhausted both released MOSS routes; V11 refreshed branches, tags, releases, forks, maintainer repositories, issue state and exact code search.",
            "search_universe": "Public GitHub publication surfaces and the complete locally frozen V6/V3/V10 predecessor packets.",
            "formulation": "The target is narrowed only to one byte-level field instance; no performance or natural-case responsibility question is silently substituted.",
        },
        "saturation_challenge": "A private or newly published upstream companion could exist outside the captured public surfaces; any such bytes reopen the released-route question but do not invalidate the distinct successor receipt.",
        "why_prior_searches_could_miss": [
            "companion may be private, unindexed, or newly released after the search timestamp",
            "repository naming may omit MOSS/claw-eval vocabulary",
            "maintainer response may arrive later on issue 3",
        ],
        "frozen_hypothesis": "If and only if all six content-addressed classes pass one execution-free materialization/destruction gate, runtime.task_environment becomes BOUND for the distinct successor on the owner-specified C2 21-field basis.",
        "acceptance_rules": [
            "six and only six V10 required classes pass",
            "all local/external byte references match SHA-256 and size",
            "forbidden recursive keys and attempt roots are absent",
            "only NumberUtils.java is writable in the ephemeral candidate overlay",
            "before/after content digests match because no candidate action is authorized",
            "attempt destruction is verified",
        ],
        "reopen_triggers": [
            "any frozen hash or runtime path changes",
            "any undeclared writable path, fallback, network dependency or forbidden key appears",
            "a V11 candidate/evaluator/model/benchmark/scorer is executed during the route gate",
            "successor evidence is attributed to released MOSS",
            "the public-development case is promoted to fresh or confirmatory evidence",
        ],
        "forbidden": [
            "C3 or C4 work",
            "MOSS/model/coding-agent execution",
            "public evaluator or benchmark outcome execution",
            "protected/gold/scorer data access",
            "repository CI or test-framework execution",
            "performance, superiority, readiness, or H1-H4 promotion",
        ],
    }
    write_json(HERE / "P5_C2_V11_FROZEN_PROTOCOL.json", protocol)

    write_policy = {
        "schema_version": "orion.p5.c2.write-reset-policy.v11",
        "successor_identity": IDENTITY,
        "attempt_root": "host-created unique temporary directory",
        "candidate_writable_root": "candidate_work/source",
        "candidate_writable_paths": [TARGET],
        "candidate_read_only_roots": ["source_readonly", "candidate_inputs"],
        "host_only_roots": ["host_controlled"],
        "forbidden_roots": ["protected", "gold", "hidden_panel", "scorer", "reference_solution", "outcome_cache"],
        "before_after_digest": {
            "algorithm": "SHA-256",
            "coverage": "every regular file under candidate_work/source plus the sole mutable target separately",
            "receipt_required": True,
            "no_action_expectation": "before and after digests must match during the V11 route gate",
        },
        "directory_policy": "No candidate-writable directories; all directories are 0555 after materialization.",
        "file_policy": "All files are 0444 except NumberUtils.java at 0644 in the ephemeral candidate overlay.",
        "attempt_destruction_required": True,
        "reset_method": "recursively restore owner permissions solely for host cleanup, delete the unique attempt parent, and assert nonexistence",
        "candidate_action_authorized": False,
        "evaluator_execution_authorized": False,
    }
    write_json(HERE / "P5_C2_V11_WRITE_RESET_POLICY.json", write_policy)

    certificate = {
        "schema_version": "orion.p5.candidate-visible-class-certificate.v3",
        "certificate_id": "P5V3-CERT-C2.V11.EXECUTION.REPAIR",
        "arm_id": "C2_DIRECT_SELF_EDIT__MOSS",
        "observation_id": "P5V3-OBS-C2.V11.LANG1.INPUT",
        "declared_class": "EXECUTION_REPAIR",
        "issuance": {
            "issuer_role": "HOST_INPUT_VALIDATOR",
            "phase": "BEFORE_CANDIDATE_ACTION",
            "candidate_visible": True,
            "input_native": True,
            "native_output_access": False,
            "protected_outcome_access": False,
            "sequence": 0,
        },
        "basis": {
            "predicate_id": "SYNTHETIC_P5_C2_V11_INPUT_BINDING",
            "source_ref_sha256": [
                SOURCE_ARCHIVE_SHA,
                sha256(HERE / "session/FLAG_SNAPSHOT_V11.json"),
                sha256(HERE / "evaluator/PUBLIC_HEX_CLASSIFICATION_CASES_V11.json"),
            ],
            "domain_scope_sha256": V3_DOMAIN_SHA,
            "fibre_constancy_attestation": {
                "status": "PROVED_ON_DECLARED_SYNTHETIC_DOMAIN",
                "declared_class": "EXECUTION_REPAIR",
                "proof_ref_sha256": V3_PROOF_SHA,
            },
        },
        "complete": True,
    }
    write_json(HERE / "P5_C2_V11_PRE_ACTION_CERTIFICATE.json", certificate)
    boundary = {
        "schema_version": "orion.p5.c2.certificate-authority-boundary.v11",
        "certificate_sha256": sha256(HERE / "P5_C2_V11_PRE_ACTION_CERTIFICATE.json"),
        "certificate_schema_sha256": sha256(V3 / "P5_V3_CANDIDATE_VISIBLE_CERTIFICATE_SCHEMA.json"),
        "supplied_authority": "STRUCTURAL_AND_INPUT_BINDING_TO_THE_DECLARED_V3_SYNTHETIC_DOMAIN_ONLY",
        "natural_case_fibre_proof": "NOT_SUPPLIED",
        "natural_case_minimal_class_truth": "NOT_SUPPLIED",
        "revision_authority": "NOT_SUPPLIED",
        "performance_authority": "NOT_SUPPLIED",
        "released_moss_authority": "NOT_SUPPLIED",
        "successor_mapping": "The V3 arm enum retains the C2 predecessor identifier for schema compatibility; this separate receipt binds its use only to the distinctly named ORION V11 successor.",
    }
    write_json(HERE / "P5_C2_V11_CERTIFICATE_AUTHORITY_BOUNDARY.json", boundary)

    rights = {
        "schema_version": "orion.p5.c2.lawful-successor-rights-manifest.v11",
        "successor_identity": IDENTITY,
        "legal_advice": False,
        "components": [
            {
                "component": "V6 Apache Commons Lang source archive",
                "artifact": repo_ref(SOURCE_ARCHIVE),
                "spdx": "Apache-2.0",
                "license": packet_ref(HERE / "licenses/APACHE-2.0.txt"),
                "notice": packet_ref(HERE / "licenses/APACHE-NOTICE.txt"),
                "boundary": "Use/modification/distribution subject to retained Apache-2.0 terms and NOTICE.",
            },
            {
                "component": "V6 authored case body and task specification",
                "artifacts": [repo_ref(V6 / "candidate_visible/CASE_BODY_V6.json"), repo_ref(V6 / "candidate_visible/TASK_SPECIFICATION_V6.md")],
                "spdx": "CC0-1.0",
                "license": packet_ref(HERE / "licenses/CC0-1.0.txt"),
                "boundary": "Inherited V6 local authorship assertion; public-development and post-outcome selection boundary retained.",
            },
            {
                "component": "V11 session, certificate, evaluator, cases, protocol, policy and adapter",
                "spdx": "CC0-1.0",
                "license": packet_ref(HERE / "licenses/CC0-1.0.txt"),
                "rights_holder": "Authors of the V11 packet acting through the repository owner",
                "boundary": "Applies only to newly authored V11 bytes, not to predecessor or runtime components.",
            },
            {
                "component": "Pinned OpenJDK runtime",
                "spdx": "GPL-2.0-only WITH Classpath-exception-2.0",
                "license": packet_ref(HERE / "licenses/OPENJDK-17-LICENSE.txt"),
                "binary_paths": [str(JDK_HOME / "bin/java"), str(JDK_HOME / "bin/javac")],
                "boundary": "Host runtime is referenced by exact local path/hash and is not redistributed in this packet.",
            },
        ],
        "excluded": [
            "released MOSS identity or benchmark companion",
            "known fixed source tree or fix patch",
            "Defects4J generated evaluator/prepared environment",
            "model or service bytes and generated solver output",
            "protected panel, scorer, hidden outcome or feedback",
        ],
        "status": "BOUND_FOR_EXACT_LISTED_SUCCESSOR_COMPONENTS_ONLY",
    }
    write_json(HERE / "P5_C2_V11_RIGHTS_MANIFEST.json", rights)

    packet_artifacts = {
        "flag_snapshot": packet_ref(HERE / "session/FLAG_SNAPSHOT_V11.json"),
        "session_manifest": packet_ref(HERE / "session/P5_C2_V11_SESSION_MANIFEST.json"),
        "session_chunk_0001": packet_ref(HERE / "session/chunk-0001.json"),
        "certificate": packet_ref(HERE / "P5_C2_V11_PRE_ACTION_CERTIFICATE.json"),
        "certificate_authority_boundary": packet_ref(HERE / "P5_C2_V11_CERTIFICATE_AUTHORITY_BOUNDARY.json"),
        "public_evaluator": packet_ref(HERE / "evaluator/public_hex_classifier_evaluator.py"),
        "public_cases": packet_ref(HERE / "evaluator/PUBLIC_HEX_CLASSIFICATION_CASES_V11.json"),
        "runtime_lock": packet_ref(HERE / "P5_C2_V11_JDK_RUNTIME_LOCK.json"),
        "rights_manifest": packet_ref(HERE / "P5_C2_V11_RIGHTS_MANIFEST.json"),
        "write_reset_policy": packet_ref(HERE / "P5_C2_V11_WRITE_RESET_POLICY.json"),
        "upstream_search_receipt": packet_ref(HERE / "P5_C2_V11_UPSTREAM_SEARCH_RECEIPT.json"),
        "frozen_protocol": packet_ref(HERE / "P5_C2_V11_FROZEN_PROTOCOL.json"),
        "route_adapter": packet_ref(HERE / "p5_c2_v11_route_adapter.py"),
        "license_cc0": packet_ref(HERE / "licenses/CC0-1.0.txt"),
        "license_apache": packet_ref(HERE / "licenses/APACHE-2.0.txt"),
        "notice_apache": packet_ref(HERE / "licenses/APACHE-NOTICE.txt"),
        "license_openjdk": packet_ref(HERE / "licenses/OPENJDK-17-LICENSE.txt"),
    }
    external_inputs = {
        "v6_source_archive": repo_ref(SOURCE_ARCHIVE),
        "v6_source_tree_manifest": repo_ref(V6 / "P5_SOURCE_TREE_CONTENT_MANIFEST_V6.json"),
        "v6_case_body": repo_ref(V6 / "candidate_visible/CASE_BODY_V6.json"),
        "v6_task_specification": repo_ref(V6 / "candidate_visible/TASK_SPECIFICATION_V6.md"),
        "v6_rights_manifest": repo_ref(V6 / "P5_SHARED_CASE_RIGHTS_MANIFEST_V6.json"),
        "v3_certificate_schema": repo_ref(V3 / "P5_V3_CANDIDATE_VISIBLE_CERTIFICATE_SCHEMA.json"),
        "v3_synthetic_domain": repo_ref(V3 / "P5_V3_DECLARED_SYNTHETIC_DOMAIN.json"),
        "v3_synthetic_conformance": repo_ref(V3 / "P5_V3_SYNTHETIC_CONFORMANCE_RECEIPT.json"),
        "v10_successor_contract": repo_ref(V10 / "P5_C2_V10_SUCCESSOR_BYTE_CONTRACT.json"),
        "v10_result": repo_ref(V10 / "P5_C2_V10_RESULT.json"),
    }
    freeze_doc = {
        "schema_version": "orion.p5.c2.execution-freeze.v11",
        "protocol_id": PROTOCOL_ID,
        "frozen_at_utc": FROZEN_AT,
        "successor_identity": IDENTITY,
        "predecessor_arm_id": "C2_DIRECT_SELF_EDIT__MOSS",
        "released_moss_commit": MOSS_COMMIT,
        "released_moss_identity_claimed": False,
        "released_moss_state_changed": False,
        "field_target": "runtime.task_environment",
        "authority": "BYTE_ROUTE_PREFLIGHT_ONLY__NOT_PERFORMANCE",
        "packet_artifacts": packet_artifacts,
        "external_inputs": external_inputs,
        "required_byte_classes": [
            {"id": "session", "accept": "authored/licensed FlagSnapshot plus complete chunk hashes and no candidate outcome/feedback bytes"},
            {"id": "source_mount", "accept": "exact V6 archive/tree read-only plus one-file writable ephemeral overlay"},
            {"id": "pre_action_certificate", "accept": "V3-compatible host-issued sequence-0 input certificate with synthetic authority boundary"},
            {"id": "public_evaluator", "accept": "closed public evaluator/cases/runtime bytes outside candidate writes and not executed"},
            {"id": "write_reset_policy", "accept": "complete roots, before/after digests and verified destruction"},
            {"id": "route_adapter", "accept": "distinct content-addressed adapter mounts/forwards every prior class"},
        ],
        "forbidden_keys_recursive": ["protected_score", "gold_patch", "gold", "hidden_panel_id", "expected_patch", "scorer_feedback"],
        "forbidden_attempt_path_components": ["protected", "gold", "hidden_panel", "scorer", "reference_solution", "outcome_cache"],
        "no_fallback_predicates": {
            "network": "DENY",
            "path_lookup": "DENY",
            "runtime_binary_fallback": "DENY",
            "source_archive_substitution": "DENY",
            "evaluator_substitution": "DENY",
        },
        "evaluator_execution_authorized": False,
        "candidate_execution_authorized": False,
        "expected_gate_terminal": "P5_C2_V11_SIX_OF_SIX_FROZEN_BYTE_CLASSES_PASS__DISTINCT_SUCCESSOR_ROUTE_MATERIALIZED__NO_MODEL_BENCHMARK_SCORER_OR_OUTCOME_EXECUTED",
    }
    write_json(HERE / "P5_C2_V11_EXECUTION_FREEZE.json", freeze_doc)
    print("P5_C2_V11_EXECUTION_FREEZE_SEALED")


def finalize() -> None:
    freeze_doc = load(HERE / "P5_C2_V11_EXECUTION_FREEZE.json")
    for ref in freeze_doc["packet_artifacts"].values():
        path = HERE / ref["path"]
        if sha256(path) != ref["sha256"] or path.stat().st_size != ref["size_bytes"]:
            raise RuntimeError(f"frozen packet artifact drifted: {path}")
    for ref in freeze_doc["external_inputs"].values():
        path = REPO_ROOT / ref["path"]
        if sha256(path) != ref["sha256"] or path.stat().st_size != ref["size_bytes"]:
            raise RuntimeError(f"frozen external artifact drifted: {path}")
    gate = load(HERE / "P5_C2_V11_SIX_CLASS_GATE_RECEIPT.json")
    if not (
        gate["status"] == "PASS"
        and gate["required_class_count"] == 6
        and gate["passed_class_count"] == 6
        and gate["attempt_destruction_verified"] is True
        and all(row["passed"] for row in gate["class_receipts"])
    ):
        raise RuntimeError("six-class frozen gate did not genuinely pass")
    if gate["executed"] != {
        "benchmark": False,
        "coding_agent": False,
        "model": False,
        "moss": False,
        "protected_data": False,
        "protected_scorer": False,
        "public_evaluator": False,
        "repository_ci": False,
        "route_gate": True,
        "test_framework": False,
    }:
        raise RuntimeError("route gate execution boundary drifted")

    v4_registry = load(V4 / "P5_C2_V4_FIELD_REGISTRY.json")
    if v4_registry["bound_field_count"] != 7 or v4_registry["blocking_field_count"] != 14:
        raise RuntimeError("owner-specified predecessor count basis drifted")
    remaining_fields = [field for field in v4_registry["blocking_fields"] if field != "runtime.task_environment"]
    if len(remaining_fields) != 13:
        raise RuntimeError("one-field successor arithmetic failed")
    result = {
        "schema_version": "orion.p5.c2.lawful-native-byte-successor-result.v11",
        "protocol_id": PROTOCOL_ID,
        "successor_identity": IDENTITY,
        "predecessor_arm_id": "C2_DIRECT_SELF_EDIT__MOSS",
        "status": "BOUND_ONE_FIELD_FOR_DISTINCT_SUCCESSOR",
        "field_target": "runtime.task_environment",
        "field_instances_closed": 1,
        "six_class_gate": packet_ref(HERE / "P5_C2_V11_SIX_CLASS_GATE_RECEIPT.json"),
        "successor_count_basis": {
            "authority": "OWNER_SPECIFIED_C2_V4_TWENTY_ONE_FIELD_BASIS",
            "predecessor_bound": 7,
            "predecessor_blocking": 14,
            "successor_bound": 8,
            "successor_blocking": 13,
            "only_state_transition": "runtime.task_environment: BLOCKING -> BOUND",
        },
        "released_moss_preserved": {
            "commit": MOSS_COMMIT,
            "bound": 7,
            "blocking": 14,
            "runtime_task_environment": "BLOCKING",
            "reason": "V11 is a distinctly named authored successor, not a released MOSS companion or execution result.",
        },
        "panel_and_claim_boundaries": {
            "ready_arms": "0/6",
            "global_panel_field_delta": "NOT_CLAIMED__COUNT_BASES_NOT_SILENTLY_MERGED",
            "H1": "CANNOT_CHECK",
            "H2": "CANNOT_CHECK",
            "H3": "CANNOT_CHECK",
            "H4": "CANNOT_CHECK",
            "performance": "CANNOT_CHECK",
            "superiority": "CANNOT_CHECK",
            "top_tier_peer_review_ready": "NOT_ESTABLISHED",
        },
        "public_case_authority": "POST_OUTCOME_PUBLIC_DEVELOPMENT_ONLY__NOT_FRESH_OR_CONFIRMATORY",
        "manuscript_or_claim_ledger_edited": False,
        "next_discriminator": "Resolve the remaining 13 successor field obligations; independently obtain fresh external custody/scorer/panel evidence before any H1-H4, performance, superiority, readiness, or top-tier claim.",
        "terminal": "P5_C2_V11_SIX_OF_SIX_SUCCESSOR_BYTE_CLASSES_BOUND__DISTINCT_ORION_LAWFUL_NATIVE_SUCCESSOR__RUNTIME_TASK_ENVIRONMENT_BOUND_ON_C2_V4_COUNT_BASIS__EIGHT_OF_TWENTY_ONE_BOUND__THIRTEEN_BLOCKING__RELEASED_MOSS_UNCHANGED__ZERO_OF_SIX_READY__PERFORMANCE_AND_SUPERIORITY_CANNOT_CHECK",
    }
    write_json(HERE / "P5_C2_V11_RESULT.json", result)

    ledger_rows: list[dict[str, Any]] = [
        {
            "id": "P5.C2.V11.RELEASED.MOSS.ROUTE",
            "negative_result": "No lawful upstream MOSS companion was found and the released route still lacks the required task environment.",
            "positive_resolution": "A separately named, content-addressed successor now passes all six byte-route classes without borrowing released MOSS identity.",
            "residual": "Released MOSS remains 7/21 bound and 14/21 blocking.",
            "next_discriminator": "Recheck only when maintainers publish the exact companion/rights or answer issue 3 with content-addressed bytes.",
        },
        {
            "id": "P5.C2.V11.PUBLIC.DEVELOPMENT.AUTHORITY",
            "negative_result": "The V6 LANG-1 case was selected after a public fix and predecessor outcomes were known.",
            "positive_resolution": "V11 closes byte-route reproducibility while preserving the post-outcome boundary explicitly in session, certificate and result artifacts.",
            "residual": "The route receipt is not fresh, protected, confirmatory, performance or superiority evidence.",
            "next_discriminator": "Use a prospectively frozen source-disjoint case under independent custody after protocol lock.",
        },
    ]
    for field in remaining_fields:
        entry = v4_registry["fields"][field]
        ledger_rows.append(
            {
                "id": "P5.C2.V11.REMAINING." + field.upper().replace(".", "_"),
                "field": field,
                "negative_result": entry["cause"],
                "positive_resolution": "runtime.task_environment is no longer co-mingled with this distinct obligation; it remains an independently testable research lane.",
                "residual": entry["residual"],
                "next_discriminator": entry["next_discriminator"],
            }
        )
    ledger = {
        "schema_version": "orion.p5.c2.recursive-negative-ledger.v11",
        "successor_identity": IDENTITY,
        "resolved_in_v11": ["runtime.task_environment"],
        "remaining_successor_blocker_count": 13,
        "entries": ledger_rows,
    }
    write_json(HERE / "P5_C2_V11_RECURSIVE_NEGATIVE_LEDGER.json", ledger)
    md = [
        "# P5 C2 V11 recursive negative-result ledger",
        "",
        "| ID | Negative result | Positive resolution | Residual | Next discriminator |",
        "|---|---|---|---|---|",
    ]
    for row in ledger_rows:
        clean = lambda value: str(value or "").replace("|", "\\|").replace("\n", " ")
        md.append(
            "| " + " | ".join(clean(row[key]) for key in ("id", "negative_result", "positive_resolution", "residual", "next_discriminator")) + " |"
        )
    write_text(HERE / "P5_C2_V11_RECURSIVE_NEGATIVE_LEDGER.md", "\n".join(md))

    report = f"""# P5 C2 lawful native-byte successor V11

## Terminal

`{result['terminal']}`

## Positive scientific delta

V11 resolves the exact V10 prospective-byte question. A distinctly named
successor now contains and content-addresses an authored MOSS-compatible
FlagSnapshot/session, the exact rights-cleared V6 LANG-1 source archive, a
host-issued V3-compatible pre-action certificate, a frozen public evaluator
and six mechanistic hexadecimal boundary cases, an exact OpenJDK runtime lock,
a complete write/reset policy, and a route adapter that physically
materializes their candidate/host split. The frozen gate passes **6/6** byte
classes. It verifies the 302-file V6 tree manifest, permits writes only to
`{TARGET}`, records equal before/after content digests, and verifies attempt
destruction.

This is a real closure of `runtime.task_environment` for
`{IDENTITY}` on the owner-specified C2 V4 count basis: the successor projection
moves from **7/21 bound and 14/21 blocking** to **8/21 bound and 13/21
blocking**. No global panel arithmetic is invented or silently merged with the
different V6/V7 programme basis.

## Identity and authority boundary

V11 is **not released MOSS**. Fresh public search at `{SEARCHED_AT}` found the
same MOSS main commit `{MOSS_COMMIT}`, one tag, no releases, three returned
forks, no maintainer companion, an open unanswered issue 3, and zero exact
public code-search hits for the missing runner. Released MOSS therefore remains
7/21 bound and 14/21 blocking; V11's positive gate belongs only to the distinct
successor.

The V3 certificate supplies structural/input binding on its declared synthetic
domain only. It supplies no natural-case fibre proof, minimal-class truth, or
revision authority. The V6 LANG-1 case remains post-outcome public development,
not fresh or confirmatory.

## Execution boundary

Only the content-addressed route gate ran. It did not invoke MOSS, a model, a
coding agent, the public evaluator, a benchmark, a scorer, protected data,
repository CI, or a test framework. Consequently the panel remains **0/6
ready**; H1-H4, performance and superiority remain `CANNOT_CHECK`; top-tier
peer-review readiness is not established. The manuscript and claim ledger were
not edited by this additive lane.

## Recursive continuation

`P5_C2_V11_RECURSIVE_NEGATIVE_LEDGER.json` decomposes the remaining 13 successor
field obligations and preserves an exact next discriminator for each. The next
scientific priority is not another runtime byte audit: it is to close the
remaining isolation, custody, provider/resource, rights, compute and container
obligations, followed by genuinely fresh external-custody evidence.
"""
    write_text(HERE / "SCIENTIFIC_REPORT_V11.md", report)
    readme = """# P5 C2 lawful native-byte successor V11

Start with `SCIENTIFIC_REPORT_V11.md`, `P5_C2_V11_RESULT.json`, and
`P5_C2_V11_SIX_CLASS_GATE_RECEIPT.json`.

This additive packet closes only `runtime.task_environment` for the distinctly
named ORION V11 successor on the owner-specified C2 V4 count basis. It does not
alter or impersonate released MOSS, execute an outcome-producing component, or
establish panel readiness, H1-H4, performance, superiority, or top-tier
publication readiness.

Reproduction order (no test framework):

1. `python build_p5_c2_v11_packet.py --phase freeze`
2. `python p5_c2_v11_route_adapter.py`
3. `python build_p5_c2_v11_packet.py --phase finalize`
4. `python validate_p5_c2_v11_packet.py`

The public evaluator is frozen but is intentionally not part of that route
gate execution sequence.
"""
    write_text(HERE / "README.md", readme)

    excluded = {"ARTIFACT_MANIFEST_V11.json", "SHA256SUMS"}
    artifacts = []
    for path in sorted(HERE.rglob("*")):
        if not path.is_file() or path.name in excluded or "__pycache__" in path.parts:
            continue
        artifacts.append(packet_ref(path))
    manifest = {
        "schema_version": "orion.p5.c2.artifact-manifest.v11",
        "successor_identity": IDENTITY,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "exclusions": ["ARTIFACT_MANIFEST_V11.json (self-reference)", "SHA256SUMS (generated after manifest)"],
    }
    write_json(HERE / "ARTIFACT_MANIFEST_V11.json", manifest)
    sum_paths = [path for path in sorted(HERE.rglob("*")) if path.is_file() and path.name != "SHA256SUMS" and "__pycache__" not in path.parts]
    write_text(HERE / "SHA256SUMS", "\n".join(f"{sha256(path)}  {path.relative_to(HERE).as_posix()}" for path in sum_paths))
    print(result["terminal"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("freeze", "finalize"), required=True)
    args = parser.parse_args()
    if args.phase == "freeze":
        freeze()
    else:
        finalize()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
