#!/usr/bin/env python3
"""Build the outcome-blind P5 V6 common public case/rights packet.

This script does not execute a comparator, model, benchmark, test suite, or
protected scorer.  It inventories already-frozen public source bytes and emits
control-plane receipts for the two shared arm fields that those bytes can bind.
"""

from __future__ import annotations

import hashlib
import io
import json
import tarfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
VISIBLE = HERE / "candidate_visible"
SOURCE_ARCHIVE = VISIBLE / "source/commons-lang-396afc3e4693cfee182efe582455f2d97058c068.tar.gz"
FROZEN_AT = "2026-08-23T19:47:41Z"
BASE_COMMIT = "396afc3e4693cfee182efe582455f2d97058c068"
BASE_TREE = "34e33cca607f33ffcf8661e3a6c4b7fc5aca9701"
FIX_COMMIT = "d1a45e9738de5b3e299bb51e987565dcce55fee6"
KNOWN_PUBLIC_FIX_PATCH_SHA256 = "2bacab48cc56c962cc906a3e95878735cacb2f231d4a64717a8798f1eb41090f"
CASE_ID = "P5-PUBLIC-LANG1-COMMON-001"
TERMINAL = (
    "P5_V6_SUBSTANTIVE_PUBLIC_LANG1_CASE_AND_RIGHTS_CORE_BOUND__"
    "TWELVE_SHARED_INPUT_AND_CONTENT_RIGHTS_FIELDS_CLOSED__"
    "SIX_NATIVE_TASK_ENVIRONMENTS_BLOCKING__"
    "FIFTY_FOUR_OF_ONE_HUNDRED_TWENTY_SIX_FIELDS_BOUND__"
    "SEVENTY_TWO_BLOCKING__ZERO_OF_SIX_READY__"
    "PERFORMANCE_AND_SUPERIORITY_CANNOT_CHECK"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def dump(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def rel(path: Path) -> str:
    return path.relative_to(HERE).as_posix()


def source_tree_manifest() -> dict:
    members: list[dict] = []
    root_prefix = f"commons-lang-{BASE_COMMIT}/"
    with tarfile.open(SOURCE_ARCHIVE, "r:gz") as tf:
        for member in tf.getmembers():
            if member.name == root_prefix.rstrip("/"):
                continue
            if not member.name.startswith(root_prefix):
                raise RuntimeError(f"archive member outside frozen root: {member.name}")
            if member.issym() or member.islnk():
                raise RuntimeError(f"link member not permitted: {member.name}")
            if member.isdir():
                continue
            if not member.isfile():
                raise RuntimeError(f"unsupported archive member: {member.name}")
            stream = tf.extractfile(member)
            if stream is None:
                raise RuntimeError(f"cannot read archive member: {member.name}")
            data = stream.read()
            members.append(
                {
                    "path": member.name[len(root_prefix) :],
                    "mode": oct(member.mode),
                    "size_bytes": len(data),
                    "sha256": sha256_bytes(data),
                }
            )
    members.sort(key=lambda row: row["path"])
    canonical = b"".join(
        (
            row["path"].encode()
            + b"\0"
            + row["mode"].encode()
            + b"\0"
            + str(row["size_bytes"]).encode()
            + b"\0"
            + row["sha256"].encode()
            + b"\n"
        )
        for row in members
    )
    return {
        "schema_version": "orion.p5.public-source-tree-content-manifest.v6",
        "source_archive_path": rel(SOURCE_ARCHIVE),
        "source_archive_sha256": sha256(SOURCE_ARCHIVE),
        "upstream_repository": "https://github.com/apache/commons-lang",
        "upstream_commit": BASE_COMMIT,
        "upstream_tree": BASE_TREE,
        "archive_download_url": f"https://github.com/apache/commons-lang/archive/{BASE_COMMIT}.tar.gz",
        "archive_root": root_prefix,
        "regular_file_count": len(members),
        "regular_file_bytes": sum(row["size_bytes"] for row in members),
        "link_member_count": 0,
        "canonical_member_manifest_sha256": sha256_bytes(canonical),
        "members": members,
    }


def component(path: str, licence: str, role: str) -> dict:
    p = HERE / path
    return {
        "path": path,
        "sha256": sha256(p),
        "size_bytes": p.stat().st_size,
        "license_spdx_id": licence,
        "role": role,
    }


def main() -> int:
    case_body = {
        "schema_version": "orion.p5.arm-neutral-public-development-case.v6",
        "case_id": CASE_ID,
        "task_id": "DEFECTS4J-LANG-1__LANG-747__PUBLIC-DEVELOPMENT",
        "campaign_role": "PUBLIC_DEVELOPMENT_ONLY",
        "selection": {
            "source_family": "Defects4J Lang-1 / Apache Commons Lang LANG-747",
            "issue_identifier": "LANG-747",
            "copied_issue_prose_or_attachments": False,
            "split_id": "P5_PUBLIC_DEVELOPMENT_V6",
            "split_membership": [CASE_ID],
        },
        "source": {
            "repository": "https://github.com/apache/commons-lang",
            "commit": BASE_COMMIT,
            "tree": BASE_TREE,
            "archive_path": rel(SOURCE_ARCHIVE),
            "archive_sha256": sha256(SOURCE_ARCHIVE),
            "archive_root": f"commons-lang-{BASE_COMMIT}/",
            "mutable_paths": [
                "src/main/java/org/apache/commons/lang3/math/NumberUtils.java"
            ],
            "read_only_path_policy": "Every other archive member is read-only for this case.",
        },
        "problem": {
            "statement": (
                "Repair Apache Commons Lang NumberUtils.createNumber so positive hexadecimal "
                "magnitudes are classified by the signed positive capacity of Integer and Long "
                "rather than by raw hexadecimal width alone. Values that exceed Integer but fit "
                "Long must remain representable as Long; values above signed Long capacity must "
                "remain representable as BigInteger; leading zeroes must not change the effective "
                "magnitude class. Preserve the public API and unrelated numeric parsing behavior."
            ),
            "target_symbol": "org.apache.commons.lang3.math.NumberUtils.createNumber(String)",
            "allowed_change_surface": [
                "src/main/java/org/apache/commons/lang3/math/NumberUtils.java"
            ],
            "disallowed_change_surface": [
                "src/test/**",
                "LICENSE.txt",
                "NOTICE.txt",
            ],
            "success_interface": (
                "A later arm-native public-development adapter must compile the frozen source and "
                "evaluate a separately frozen public test interface. That environment is not part "
                "of this shared case core."
            ),
        },
        "candidate_interface": {
            "arm_neutral": True,
            "candidate_receives": [
                "this case body",
                "the task specification",
                "the frozen buggy-source archive",
                "the component licence and notice bytes",
            ],
            "candidate_does_not_receive": [
                "the known public fix patch or fixed source tree",
                "expected patch bytes",
                "run outputs or per-case rewards",
                "hidden test bodies or evaluator feedback",
                "any final-panel case identifier or result",
            ],
            "seed": "NOT_APPLICABLE__DETERMINISTIC_SOURCE_TASK",
            "feedback": "NONE_IN_SHARED_CORE",
        },
    }
    dump(VISIBLE / "CASE_BODY_V6.json", case_body)

    task_md = f"""# Public development task {CASE_ID}

Repair `org.apache.commons.lang3.math.NumberUtils.createNumber(String)` in the
frozen Apache Commons Lang source archive at commit `{BASE_COMMIT}`.

For positive hexadecimal inputs, choose the narrowest supported numeric type by
the signed positive capacity of `Integer` and `Long`, not by raw hexadecimal
width alone.  A magnitude that exceeds `Integer` but fits `Long` must remain
representable as `Long`; a magnitude above signed `Long` capacity must remain
representable as `BigInteger`.  Leading zeroes must not change the effective
magnitude class.  Preserve the public API and unrelated numeric parsing.

Only `src/main/java/org/apache/commons/lang3/math/NumberUtils.java` is mutable.
Do not edit tests, licence, notice, or other source files.  This packet includes
no solution patch, fixed tree, hidden test body, run output, reward, or final
panel identifier.  Compilation and evaluation belong to a later native
environment receipt and are not authorized by this content packet.
"""
    (VISIBLE / "TASK_SPECIFICATION_V6.md").write_text(task_md)

    tree = source_tree_manifest()
    dump(HERE / "P5_SOURCE_TREE_CONTENT_MANIFEST_V6.json", tree)

    provenance = {
        "schema_version": "orion.p5.public-case-provenance.v6",
        "frozen_at_utc": FROZEN_AT,
        "case_id": CASE_ID,
        "source_identity": {
            "apache_repository": "https://github.com/apache/commons-lang",
            "buggy_commit": BASE_COMMIT,
            "buggy_tree": BASE_TREE,
            "fixed_commit_known_to_packet_builder": FIX_COMMIT,
            "known_public_fix_patch_sha256": KNOWN_PUBLIC_FIX_PATCH_SHA256,
            "known_public_fix_bytes_in_candidate_core": False,
            "defects4j_repository": "https://github.com/rjust/defects4j",
            "defects4j_commit": "8c16da8230843cdc918eaf4ddb449637f02b83c6",
            "mapping_source_path": "framework/projects/Lang/commit-db:1",
            "mapping_source_file_sha256": "373e86f5ae96329058f13e45944d01b1636732a9184afded514339791c192175",
        },
        "predecessor_public_development_evidence": {
            "selection_is_post_outcome": True,
            "authority": "PUBLIC_DEVELOPMENT_AND_PROVENANCE_CONTEXT_ONLY",
            "preregistration_v3": {
                "path": "development/p5-rd02-defects4j-public-factorial-2026-08-23/PREREGISTRATION_V3.json",
                "sha256": "5cd056ea54357cab9d341b57fa8b4fbd8a063011c4de983aa707e88de6e1959e",
            },
            "result_v2": {
                "path": "development/p5-rd02-defects4j-public-factorial-2026-08-23/RESULT_V2.json",
                "sha256": "ef3f8893299578c071e8cad46d1c73cbe507d426a805ac772e9ae955092fab98",
                "retained_log_negative": "V2 checkout streams were overwritten; exact checkout-stream preservation remains CANNOT_CHECK.",
            },
            "result_v3": {
                "path": "development/p5-rd02-defects4j-public-factorial-2026-08-23/RESULT_V3.json",
                "sha256": "e743ebb77a31c4c4606f7eded8045a60c78fa2f251c13908051156cfd4a1fb6e",
                "boundary": "Post-outcome archival replay only; not independent or confirmatory.",
            },
            "audit_receipt": {
                "path": "development/p5-rd02-defects4j-public-factorial-2026-08-23/AUDIT_RECEIPT.json",
                "sha256": "aeed753b5eab56f828a8192717e18ba6953ae41ed4196f8b155960e67a70e528",
            },
        },
    }
    dump(HERE / "P5_PUBLIC_CASE_PROVENANCE_V6.json", provenance)

    rights = {
        "schema_version": "orion.p5.shared-case-rights-manifest.v6",
        "case_id": CASE_ID,
        "rights_status": "BOUND_FOR_LISTED_SHARED_CASE_COMPONENTS",
        "legal_advice": False,
        "reuse_condition": (
            "The binding applies only when future arm adapters use exactly the listed common-case "
            "components. Any native dataset, benchmark, issue attachment, skill corpus, generated "
            "solver output, container layer, model service, or newly fetched content requires a "
            "separate rights disposition and reopens the affected field."
        ),
        "components": [
            {
                "component_id": "APACHE_COMMONS_LANG_BUGGY_SOURCE_ARCHIVE",
                "path": rel(SOURCE_ARCHIVE),
                "sha256": sha256(SOURCE_ARCHIVE),
                "rights_holder": "Apache Software Foundation and contributors as stated in retained NOTICE/source headers",
                "license_spdx_id": "Apache-2.0",
                "license_path": "candidate_visible/APACHE-2.0-LICENSE.txt",
                "license_sha256": sha256(VISIBLE / "APACHE-2.0-LICENSE.txt"),
                "notice_path": "candidate_visible/APACHE-NOTICE.txt",
                "notice_sha256": sha256(VISIBLE / "APACHE-NOTICE.txt"),
                "grant": "Use, reproduction, modification and distribution subject to Apache-2.0 terms, notices and attribution conditions.",
                "territory": "No territorial limitation stated in the retained licence text.",
                "purpose": "No field-of-use limitation stated in the retained licence text.",
                "retention": "May be retained and redistributed subject to the retained licence and notice conditions.",
            },
            {
                "component_id": "DEFECTS4J_LANG1_SOURCE_IDENTITY_MAPPING",
                "path": "source_provenance/DEFECTS4J-LANG1-SOURCE-MAPPING.csv",
                "sha256": sha256(HERE / "source_provenance/DEFECTS4J-LANG1-SOURCE-MAPPING.csv"),
                "rights_holder": "Defects4J copyright holders and contributors as stated in retained licence",
                "license_spdx_id": "MIT",
                "license_path": "source_provenance/DEFECTS4J-MIT-LICENSE.txt",
                "license_sha256": sha256(HERE / "source_provenance/DEFECTS4J-MIT-LICENSE.txt"),
                "grant": "Use, copy, modify, merge, publish, distribute, sublicense and sell subject to the retained MIT notice.",
                "territory": "No territorial limitation stated in the retained licence text.",
                "purpose": "No field-of-use limitation stated in the retained licence text.",
                "retention": "May be retained subject to preservation of the copyright and permission notice.",
            },
            {
                "component_id": "V6_AUTHORED_CASE_BODY_AND_TASK_SPECIFICATION",
                "paths": [
                    "candidate_visible/CASE_BODY_V6.json",
                    "candidate_visible/TASK_SPECIFICATION_V6.md",
                ],
                "sha256_by_path": {
                    "candidate_visible/CASE_BODY_V6.json": sha256(VISIBLE / "CASE_BODY_V6.json"),
                    "candidate_visible/TASK_SPECIFICATION_V6.md": sha256(VISIBLE / "TASK_SPECIFICATION_V6.md"),
                },
                "rights_holder": "Authors of the V6 packet acting through the repository owner",
                "license_spdx_id": "CC0-1.0",
                "license_path": "candidate_visible/PACKET-CONTENT-CC0-1.0.txt",
                "license_sha256": sha256(VISIBLE / "PACKET-CONTENT-CC0-1.0.txt"),
                "grant": "CC0-1.0 dedication for newly authored case-body and task-specification text only.",
                "territory": "Worldwide to the extent described by CC0-1.0.",
                "purpose": "Unrestricted to the extent described by CC0-1.0.",
                "retention": "Unrestricted to the extent described by CC0-1.0.",
                "authorship_assertion_is_local_not_independent": True,
            },
        ],
        "explicitly_excluded": [
            "Apache issue prose and attachments",
            "the fixed source tree and public fix patch",
            "Defects4J generated/prepared environments and evaluator scripts",
            "all arm-native datasets, tasks, examples, skills and prior-result payloads",
            "all model/service content and generated solver outputs",
        ],
    }
    dump(HERE / "P5_SHARED_CASE_RIGHTS_MANIFEST_V6.json", rights)

    visible_components = [
        component("candidate_visible/CASE_BODY_V6.json", "CC0-1.0", "arm-neutral structured case body"),
        component("candidate_visible/TASK_SPECIFICATION_V6.md", "CC0-1.0", "human-readable task bytes"),
        component("candidate_visible/source/commons-lang-396afc3e4693cfee182efe582455f2d97058c068.tar.gz", "Apache-2.0", "complete buggy source snapshot"),
        component("candidate_visible/APACHE-2.0-LICENSE.txt", "Apache-2.0", "source licence bytes"),
        component("candidate_visible/APACHE-NOTICE.txt", "Apache-2.0", "source notice bytes"),
        component("candidate_visible/PACKET-CONTENT-CC0-1.0.txt", "CC0-1.0", "authored-content licence bytes"),
    ]
    canonical = b"".join(
        x["path"].encode() + b"\0" + x["sha256"].encode() + b"\0" + str(x["size_bytes"]).encode() + b"\n"
        for x in sorted(visible_components, key=lambda row: row["path"])
    )
    core_index = {
        "schema_version": "orion.p5.shared-case-core-index.v6",
        "case_id": CASE_ID,
        "candidate_visible_component_count": len(visible_components),
        "candidate_visible_bytes": sum(x["size_bytes"] for x in visible_components),
        "candidate_visible_core_sha256": sha256_bytes(canonical),
        "components": visible_components,
        "source_tree_content_manifest": {
            "path": "P5_SOURCE_TREE_CONTENT_MANIFEST_V6.json",
            "sha256": sha256(HERE / "P5_SOURCE_TREE_CONTENT_MANIFEST_V6.json"),
            "regular_file_count": tree["regular_file_count"],
            "canonical_member_manifest_sha256": tree["canonical_member_manifest_sha256"],
        },
        "rights_manifest": {
            "path": "P5_SHARED_CASE_RIGHTS_MANIFEST_V6.json",
            "sha256": sha256(HERE / "P5_SHARED_CASE_RIGHTS_MANIFEST_V6.json"),
        },
    }
    dump(HERE / "P5_SHARED_CASE_CORE_INDEX_V6.json", core_index)

    arm_residuals = {
        "C1": "SWE-agent image, setup/run config, tool policy and native acceptance environment remain unbound.",
        "C2": "The released MOSS benchmark companion is absent; a P5-native session/replay environment and host certificate remain unbound.",
        "C3": "Mutable-agent/immutable-host tree split, input-native class certificate, endpoint policy and DGM-native environment remain unbound.",
        "C4": "ADIAS domain adapter, task IDs/seeds, turn/evaluation limits and environment bytes remain unbound; bundled native task data stays excluded.",
        "C5": "Frozen solver outputs, solver/prompts bytes, development memberships and metric-only native environment remain unbound.",
        "C6": "ScienceClaw profile, allowed skills/tools, source-filtered seed, fallback closure and native topic/case environment remain unbound.",
    }
    arm_ids = {
        "C1": "C1_FIXED_AGENT__SWE_AGENT",
        "C2": "C2_DIRECT_SELF_EDIT__MOSS",
        "C3": "C3_ARCHIVE_BASED_SELF_EDIT__DGM",
        "C4": "C4_ISSUE_CENTRIC_OPTIMIZATION__ADIAS",
        "C5": "C5_EVALUATOR_ONLY__DOUBLE_RATCHET_METRIC_ONLY",
        "C6": "C6_MODERN_SOURCE_GROUNDED__SCIENCECLAW",
    }
    prior = {"C1": (9, 12), "C2": (7, 14), "C3": (6, 15), "C4": (6, 15), "C5": (9, 12), "C6": (5, 16)}
    index_sha = sha256(HERE / "P5_SHARED_CASE_CORE_INDEX_V6.json")
    rights_sha = sha256(HERE / "P5_SHARED_CASE_RIGHTS_MANIFEST_V6.json")
    receipts = []
    for code, arm_id in arm_ids.items():
        before_bound, before_blocking = prior[code]
        receipts.append(
            {
                "arm_code": code,
                "arm_id": arm_id,
                "acceptance_status": "ACCEPTED_SHARED_CASE_AND_RIGHTS_CORE_ONLY__NATIVE_ENVIRONMENT_BLOCKING",
                "same_candidate_visible_core_sha256": core_index["candidate_visible_core_sha256"],
                "core_index_sha256": index_sha,
                "field_bindings": {
                    "inputs.candidate_visible_case_bytes": {
                        "status": "BOUND",
                        "case_id": CASE_ID,
                        "core_index_sha256": index_sha,
                    },
                    "rights.task_and_benchmark_content": {
                        "status": "BOUND",
                        "rights_manifest_sha256": rights_sha,
                        "condition": "Only listed shared-core content may be used; all native/bundled content is excluded unless separately licensed.",
                    },
                    "runtime.task_environment": {
                        "status": "BLOCKING",
                        "binding": None,
                        "residual": arm_residuals[code],
                    },
                },
                "before": {"bound": before_bound, "blocking": before_blocking},
                "after_shared_core_only": {"bound": before_bound + 2, "blocking": before_blocking - 2},
                "arm_or_model_executed": False,
            }
        )
    acceptance = {
        "schema_version": "orion.p5.six-arm-shared-core-acceptance.v6",
        "authority": "OUTCOME_BLIND_BYTE_RIGHTS_AND_FIELD_ACCEPTANCE_ONLY",
        "case_id": CASE_ID,
        "core_index_sha256": index_sha,
        "rights_manifest_sha256": rights_sha,
        "same_core_for_all_six": True,
        "shared_field_instances_closed": 12,
        "native_task_environment_instances_closed": 0,
        "receipts": receipts,
    }
    dump(HERE / "P5_SIX_ARM_SHARED_CORE_ACCEPTANCE_V6.json", acceptance)

    protocol = {
        "schema_version": "orion.p5.common-visible-case-rights-protocol.v6",
        "protocol_id": "P5-V6-COMMON-VISIBLE-CASE-RIGHTS",
        "frozen_at_utc": FROZEN_AT,
        "authority": "OUTCOME_BLIND_PUBLIC_SOURCE_BYTE_RIGHTS_AND_PREFLIGHT_ONLY",
        "predecessor_v5_registry": {
            "path": "development/p5-panelwide-root-closure-v5-2026-08-23/P5_PANELWIDE_BLOCKER_EQUIVALENCE_REGISTRY_V5.json",
            "sha256": "63257a4276b5ec52f26e65c12e6a7d414d6d9bdbdb84ce9ccdf6394847e265c7",
            "before_bound": 42,
            "before_blocking": 84,
        },
        "target": {
            "root_id": "R2_COMMON_CASE_RIGHTS_AND_NATIVE_TASK_ADAPTATION",
            "equivalence_ids": ["E2_CANDIDATE_VISIBLE_CASE", "E8_TASK_AND_BENCHMARK_CONTENT_RIGHTS"],
            "field_paths": ["inputs.candidate_visible_case_bytes", "rights.task_and_benchmark_content"],
            "arm_count": 6,
            "targeted_field_instances": 12,
        },
        "acceptance_rules": [
            "One identical candidate-visible core digest must be accepted by C1--C6.",
            "Every component must have exact bytes, provenance and a retained licence/notice disposition.",
            "The fixed tree, fix patch, run outputs, hidden tests, scorer feedback and final-panel identities must be absent.",
            "All bundled/native arm content is excluded unless separately licensed.",
            "Native environment, runtime, model, custody and execution fields remain blocking.",
        ],
        "execution_prohibitions": {
            "arm_executions": 0,
            "model_executions": 0,
            "benchmark_executions": 0,
            "protected_scorer_executions": 0,
        },
    }
    dump(HERE / "P5_COMMON_VISIBLE_CASE_RIGHTS_PROTOCOL_V6.json", protocol)

    protocol_md = f"""# P5 V6 Common Visible Case and Rights Protocol

**Authority:** `{protocol['authority']}`  
**Case:** `{CASE_ID}`  
**Freeze:** `{FROZEN_AT}`  
**Executed arms/models/benchmarks/protected scorers:** 0 / 0 / 0 / 0

## Target

V5 identified one directly authorable common artifact targeting twelve repeated
field instances: `inputs.candidate_visible_case_bytes` and
`rights.task_and_benchmark_content` for each of C1--C6.  V6 selects a real
public-development source defect, freezes the complete buggy Apache Commons Lang
tree, authors an arm-neutral task statement, retains Apache/MIT/CC0 licence
bytes, and issues six packet-local shared-core acceptance receipts.

## No-inflation rule

The twelve bindings apply only to the listed common-case components.  Original
arm datasets, benchmarks, issue attachments, skills, generated outputs and
services are excluded.  All six `runtime.task_environment` fields remain
blocking.  No byte manifest supplies an image, model, protected scorer,
independent custody, outcome or performance estimate.
"""
    (HERE / "P5_COMMON_VISIBLE_CASE_RIGHTS_PROTOCOL_V6.md").write_text(protocol_md)

    after = {row["arm_code"]: row["after_shared_core_only"] for row in receipts}
    result = {
        "schema_version": "orion.p5.common-visible-case-rights-result.v6",
        "authority": protocol["authority"],
        "case_id": CASE_ID,
        "source": {
            "regular_files": tree["regular_file_count"],
            "uncompressed_regular_file_bytes": tree["regular_file_bytes"],
            "archive_sha256": tree["source_archive_sha256"],
            "canonical_tree_manifest_sha256": tree["canonical_member_manifest_sha256"],
        },
        "field_delta": {
            "before_bound": 42,
            "before_blocking": 84,
            "new_bindings": 12,
            "after_bound": 54,
            "after_blocking": 72,
            "per_arm": after,
            "ready_arms": 0,
        },
        "root_r2": {
            "before_blocking_instances": 18,
            "shared_input_rights_instances_closed": 12,
            "native_environment_instances_closed": 0,
            "after_blocking_instances": 6,
        },
        "executions": {
            "arms": 0,
            "models": 0,
            "benchmarks": 0,
            "protected_scorers": 0,
            "outcomes_accessed": 0,
        },
        "preserved_claims": {
            "H1_H4": "CANNOT_CHECK",
            "performance": "CANNOT_CHECK",
            "superiority": "CANNOT_CHECK",
            "top_tier_publication_readiness": "NOT_ESTABLISHED",
        },
        "terminal": TERMINAL,
    }
    dump(HERE / "P5_COMMON_VISIBLE_CASE_RIGHTS_RESULT_V6.json", result)

    negatives = {
        "schema_version": "orion.p5.common-visible-case-rights-negative-ledger.v6",
        "case_id": CASE_ID,
        "records": [
            {
                "id": "V6-N1-SELECTION-NOT-FRESH",
                "cause": "Lang-1 public fix and V2/V3 outcomes were known before V6 construction.",
                "residual": "The packet is a public-development preflight case, not a fresh or confirmatory case.",
                "next_discriminator": "Freeze a source-disjoint case under independent pre-outcome custody for the final campaign.",
            },
            {
                "id": "V6-N2-NATIVE-ENVIRONMENTS-ABSENT",
                "cause": "One source/task core does not instantiate six incompatible native interfaces.",
                "residual": "Six runtime.task_environment fields remain blocking; 0/6 arms are ready.",
                "next_discriminator": "Build six content-addressed native adapters/environments and obtain six byte-level acceptance receipts without adding unlicensed content.",
            },
            {
                "id": "V6-N3-NATIVE-CONTENT-EXCLUDED",
                "cause": "The packet does not grant rights to bundled arm datasets, benchmarks, skills, issue attachments or generated outputs.",
                "residual": "Any adapter that reintroduces those bytes reopens rights.task_and_benchmark_content.",
                "next_discriminator": "Keep native content excluded or acquire component-level grants and inventories before use.",
            },
            {
                "id": "V6-N4-V2-LOG-NEGATIVE-PRESERVED",
                "cause": "The predecessor V2 runner overwrote checkout streams by path collision.",
                "residual": "Exact V2 checkout-stream preservation remains CANNOT_CHECK; V3 is post-outcome archival replay only.",
                "next_discriminator": "Do not use V2 checkout logs as byte-level evidence; retain V3 only for archival mechanics.",
            },
            {
                "id": "V6-N5-NO-SCIENTIFIC-OUTCOME",
                "cause": "V6 inventories bytes and rights without executing an arm or evaluator.",
                "residual": "H1--H4, performance, harm, transfer and superiority remain CANNOT_CHECK.",
                "next_discriminator": "Complete all remaining fields, then run a prospectively frozen independently scored campaign.",
            },
        ],
        "terminal": TERMINAL,
    }
    dump(HERE / "P5_COMMON_VISIBLE_CASE_RIGHTS_NEGATIVE_LEDGER_V6.json", negatives)
    negative_md = "# P5 V6 Recursive Negative Ledger\n\n" + "\n".join(
        f"## {row['id']}\n\n- **Cause:** {row['cause']}\n- **Residual:** {row['residual']}\n- **Next discriminator:** {row['next_discriminator']}\n"
        for row in negatives["records"]
    ) + f"\nExact terminal: `{TERMINAL}`\n"
    (HERE / "P5_COMMON_VISIBLE_CASE_RIGHTS_NEGATIVE_LEDGER_V6.md").write_text(negative_md)

    report = f"""# P5 V6 Common Visible Case and Rights Scientific Report

## Material closure

V6 freezes one substantive arm-neutral public-development case around Defects4J
Lang-1 / Apache Commons Lang LANG-747.  The candidate core contains the complete
buggy source snapshot at `{BASE_COMMIT}`: {tree['regular_file_count']} regular
files and {tree['regular_file_bytes']:,} uncompressed bytes, plus an authored
task, Apache-2.0 licence/NOTICE and CC0-1.0 authored-content grant.  Control-side
provenance retains the exact Defects4J source mapping and its MIT licence.  The
candidate core contains no fixed tree, fixed-commit identifier or fix patch.

Six packet-local acceptance receipts bind the same core digest to two fields per
arm: `inputs.candidate_visible_case_bytes` and
`rights.task_and_benchmark_content`.  This materially closes 12 repeated field
instances.  The panel moves from 42/126 bound and 84/126 blocking to **54/126
bound and 72/126 blocking**.  Root R2 moves from 18 blockers to six.

## Residual boundary

All six residual R2 blockers are `runtime.task_environment`.  No C1 image, C2
benchmark companion, C3 host/agent split, C4 domain environment, C5 frozen
solver-output environment or C6 profile/skill/tool environment is bound.  Native
arm content is excluded unless separately licensed; reintroducing it reopens the
corresponding rights field.  Therefore 0/6 arms are execution-ready.

The public fix and predecessor V2/V3 outcomes were known before V6 selection.
This is not a fresh, independent or confirmatory case.  The V2 checkout-log
overwrite remains adverse provenance, and V3 remains post-outcome archival
replay only.  No arm, model, benchmark, protected scorer or outcome was run or
opened.  H1--H4, performance and superiority remain `CANNOT_CHECK`.

## Exact terminal

`{TERMINAL}`
"""
    (HERE / "SCIENTIFIC_REPORT_V6.md").write_text(report)
    (HERE / "TERMINAL_V6.txt").write_text(TERMINAL + "\n")
    print(json.dumps({"status": "BUILT", "new_bindings": 12, "after_bound": 54, "after_blocking": 72, "terminal": TERMINAL}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
