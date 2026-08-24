#!/usr/bin/env python3
"""Capture public target semantics and rerun the unchanged P1 R7 audit.

Remote source bodies are hashed in memory and discarded.  The handoff retains
only bounded public metadata, hashes, line references, occurrence hashes and
derived semantic assertions.  No case text, system output or protected datum
is opened.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import subprocess
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PUBLIC_COMMIT = "390267dfa9c6669e506ba67b5dde5dddd8f96232"
REPOSITORY = "SzeChunYiu/ORION"
API = f"https://api.github.com/repos/{REPOSITORY}"
RAW = f"https://raw.githubusercontent.com/{REPOSITORY}/{PUBLIC_COMMIT}"
USER_AGENT = "orion-p1-v8-public-semantic-audit/1.0"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def dump(name: str, obj: object) -> None:
    (HERE / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def git(repo: Path, *args: str, text: bool = False) -> bytes | str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=text)


def fetch(url: str) -> tuple[int, dict[str, str], bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, {k.lower(): v for k, v in response.headers.items()}, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, {k.lower(): v for k, v in exc.headers.items()}, exc.read()


def evidence(path: str, start: int, end: int, claim: str) -> dict:
    return {
        "path": path,
        "public_url": f"https://github.com/{REPOSITORY}/blob/{PUBLIC_COMMIT}/{path}#L{start}-L{end}",
        "line_start": start,
        "line_end": end,
        "claim": claim,
    }


def occurrence_census(repo: Path, tokens: list[str], corpus_paths: list[str]) -> dict:
    census = {}
    for token in tokens:
        proc = subprocess.run(
            ["git", "-C", str(repo), "grep", "-n", "-F", token, PUBLIC_COMMIT, "--", *corpus_paths],
            check=False, capture_output=True, text=True,
        )
        if proc.returncode not in (0, 1):
            raise RuntimeError(proc.stderr)
        rows = []
        for raw_line in proc.stdout.splitlines():
            _, path, line_no, line_text = raw_line.split(":", 3)
            rows.append({
                "path": path,
                "line": int(line_no),
                "line_sha256": sha(line_text.encode()),
                "payload_retained": False,
            })
        census[token] = {
            "occurrence_count": len(rows),
            "file_count": len({row["path"] for row in rows}),
            "locations": rows,
        }
    return census


def target_registry() -> dict:
    ard = "research/claim_expansion/p1/gpt_r1/ARD_PROTOCOL_V1.md"
    framework = "research/claim_expansion/p1/gpt_r1/FRAMEWORK_CONSISTENCY_V1.md"
    runner = "research/claim_expansion/p1/gpt_r1/run_ard_exact_pilot.py"
    shared = {
        "declared_sort": "SCIENTIFIC_DECISION",
        "postpublication_coordinate": "UNBOUND",
        "licensed_postpublication_operations": "UNBOUND",
        "forbidden_postpublication_operations": "UNBOUND",
        "error_timeout_terminal_semantics": "UNBOUND",
        "closed_world_exhaustive_denotation": False,
        "owner_ratified_postpublication_bridge": False,
        "authority": "PUBLIC_PRIMARY_REPOSITORY_SEMANTIC_ANCHOR_ONLY",
    }
    anchors = {
        "KEEP_SEARCH": {
            "scientific_process_anchor": "SEARCH.v1; search-universe and bounded-saturation substrate",
            "status": "IMPLEMENTED_SUBSTRATE",
            "rule": "Search failure alone cannot imply problem inadequacy.",
            "evidence": [evidence(framework, 23, 23, "process anchor and rule")],
        },
        "KEEP_COMPILE": {
            "scientific_process_anchor": "InterfaceAdequacyReport; representation/interface repair",
            "status": "IMPLEMENTED_OR_CANDIDATE_SUBSTRATE",
            "rule": "Interface repair precedes broader method/model revision where registered.",
            "evidence": [evidence(framework, 24, 24, "process anchor and rule")],
        },
        "KEEP_REPAIR": {
            "scientific_process_anchor": "responsibility binding plus minimal admissible mechanic selection",
            "status": "IMPLEMENTED_OR_CANDIDATE_SUBSTRATE",
            "rule": "Select a minimal admissible repair only when responsibility is identified.",
            "evidence": [evidence(framework, 25, 25, "process anchor and rule")],
        },
        "REVISE_MEASUREMENT": {
            "scientific_process_anchor": "measurement relation and responsibility mechanics",
            "status": "IMPLEMENTED_OR_CANDIDATE_SUBSTRATE",
            "rule": "Measurement change remains distinct from objective/problem change.",
            "evidence": [evidence(framework, 26, 26, "process anchor and rule")],
        },
        "REFORMULATE_OBJECTIVE": {
            "scientific_process_anchor": "REFRAME.v1; objective/model/hypothesis-basis revision",
            "status": "CORE_OPERATOR_PLUS_RESEARCH_SUBSTRATE",
            "rule": "Broad naturalistic objective reformulation remains prospective.",
            "evidence": [evidence(framework, 27, 27, "process anchor and rule")],
        },
        "REFORMULATE_BOUNDARY": {
            "scientific_process_anchor": "REFRAME.v1; problem/domain-boundary proposal",
            "status": "CORE_OPERATOR_PLUS_PROSPECTIVE_SCIENCE",
            "rule": "No universal problem-boundary inference claim is made.",
            "evidence": [evidence(framework, 28, 28, "process anchor and rule")],
        },
        "UNRESOLVED": {
            "scientific_process_anchor": "fail-closed status semantics",
            "status": "IMPLEMENTED_SUBSTRATE",
            "rule": "Missing evidence never becomes positive authority.",
            "evidence": [evidence(framework, 29, 29, "fail-closed anchor and rule")],
        },
    }
    targets = []
    for target, row in anchors.items():
        item = {"target_id": target, **shared, **row}
        if target == "UNRESOLVED":
            item.update({
                "declared_sort": "UNRESOLVED",
                "postpublication_coordinate": "NONE",
                "licensed_postpublication_operations": ["ABSTAIN"],
                "forbidden_postpublication_operations": ["ANY_POSITIVE_OR_BROADER_ACTION"],
                "closed_world_exhaustive_denotation": True,
            })
        targets.append(item)
    return {
        "schema_version": "orion.p1.r7.public-target-semantic-registry.v8",
        "registry_id": "P1.V8.PUBLIC.R7.TARGET.SEMANTIC.REGISTRY",
        "public_commit": PUBLIC_COMMIT,
        "authority": "PUBLIC_PRIMARY_OWNER_REPOSITORY__INTENSIONAL_PROCESS_ANCHORS_ONLY",
        "decision_vocabulary_evidence": [
            evidence(ard, 42, 52, "seven scientific-decision identifiers"),
            evidence(runner, 16, 23, "executable low/high/unresolved decision partition"),
        ],
        "diagnostic_probe_vocabulary_evidence": [
            evidence(ard, 54, 64, "separate diagnostic action vocabulary and enablement semantics"),
            evidence(runner, 25, 32, "executable diagnostic action identifiers"),
        ],
        "decision_probe_typing_result": {
            "status": "DECISIONS_AND_DIAGNOSTIC_PROBES_AUTHORITATIVELY_DISTINCT",
            "one_to_one_bridge": False,
            "proof_witnesses": [
                evidence(runner, 107, 115, "SEARCH_MORE is a probe whose outcomes discriminate KEEP_SEARCH from KEEP_COMPILE"),
                evidence(runner, 117, 125, "TEST_PROBLEM_BOUNDARY discriminates two distinct reformulation decisions"),
                evidence(runner, 127, 145, "compile and harness probes discriminate lower-level from higher-level decisions"),
            ],
            "interpretation": "A diagnostic probe gathers an observation used to choose a scientific decision; it is not the denotation of that decision.",
        },
        "authority_boundary": {
            "proposal_not_adoption": evidence(framework, 31, 31, "selected candidates carry no adoption, promotion or merge authority"),
            "ard_is_prospective": evidence(framework, 33, 35, "ARD/router/superiority remain prospective"),
            "public_r7_exposes_opaque_action_handles_not_postpublication_algebra": evidence("research/claim_expansion/p1/gpt_r7/R7_DESIGN_PROTOCOL_V1.json", 119, 140, "candidate visibility exposes opaque probe/action handles and forbids decision class"),
        },
        "targets": targets,
        "actionable_targets_with_complete_postpublication_denotation": 0,
        "target_count": 7,
        "actionable_target_count": 6,
        "terminal": "PUBLIC_R7_PROCESS_ANCHORS_AND_DECISION_PROBE_TYPE_SEPARATION_BOUND__POSTPUBLICATION_DENOTATIONS_UNBOUND",
    }


def enumerate_adapters(matrix: dict, semantic: dict) -> tuple[dict, dict]:
    sources = list(matrix["matrix"])
    targets = list(next(iter(matrix["matrix"].values())))
    counts = Counter()
    undecided_rows = []
    rejection_reasons = Counter()
    for values in itertools.product(targets, repeat=len(sources)):
        mapping = dict(zip(sources, values, strict=True))
        cell_statuses = [matrix["matrix"][source][target]["status"] for source, target in mapping.items()]
        reasons = []
        if len(set(values)) != len(values):
            reasons.append("G5_COLLISION_FREEDOM")
        if "REJECT" in cell_statuses:
            reasons.append("CELL_REJECT")
        if reasons:
            counts["known_rejected"] += 1
            for reason in set(reasons): rejection_reasons[reason] += 1
        elif all(status == "PASS" for status in cell_statuses):
            counts["fully_certified"] += 1
        else:
            counts["not_disproved_but_uncertified"] += 1
            actionable = {s: t for s, t in mapping.items() if s != "UNRESOLVED"}
            assert mapping["UNRESOLVED"] == "UNRESOLVED"
            assert len(actionable) == 5
            adapter_id = "P1V8-ADAPTER-" + sha(canonical(mapping))[:16]
            undecided_rows.append({
                "adapter_id": adapter_id,
                "mapping": mapping,
                "unchanged_gate_disposition": "NOT_DISPROVED__CANNOT_CHECK_TARGET_POSTPUBLICATION_DENOTATIONS",
                "actionable_image_count": 5,
                "public_target_fields_newly_bound": [
                    "SCIENTIFIC_DECISION_SORT",
                    "SCIENTIFIC_PROCESS_ANCHOR",
                    "DECISION_VERSUS_DIAGNOSTIC_PROBE_TYPING",
                    "PROPOSAL_NOT_ADOPTION_AUTHORITY_BOUNDARY",
                ],
                "essential_fields_still_missing_for_every_actionable_image": [
                    "EXHAUSTIVE_POSTPUBLICATION_COORDINATE",
                    "LICENSED_POSTPUBLICATION_OPERATIONS",
                    "FORBIDDEN_POSTPUBLICATION_OPERATIONS",
                    "OWNER_RATIFIED_DECISION_TO_POSTPUBLICATION_BRIDGE_OR_EXPLICIT_NONE",
                    "TARGET_ERROR_TIMEOUT_MALFORMED_UNSUPPORTED_TERMINAL_BEHAVIOR",
                ],
                "positive_status": "CANNOT_CHECK_UNTIL_OWNER_ALGEBRA",
                "negative_status": "NO_AUTHORITATIVE_CONTRADICTION_WITNESS__DO_NOT_INFER_IMPOSSIBILITY",
            })
    result = {
        "fully_certified": counts["fully_certified"],
        "known_rejected": counts["known_rejected"],
        "not_disproved_but_uncertified": counts["not_disproved_but_uncertified"],
        "total": sum(counts.values()),
        "rejection_reason_counts_nonexclusive": dict(sorted(rejection_reasons.items())),
    }
    registry = {
        "schema_version": "orion.p1.r7.not-disproved-adapter-registry.v8",
        "registry_id": "P1.V8.R7.720.NOT.DISPROVED.ADAPTERS",
        "authority": "UNCHANGED_FINITE_GATE_ENUMERATION_WITH_PUBLIC_TARGET_SEMANTIC_REFINEMENT",
        "row_count": len(undecided_rows),
        "independence_warning": "These are candidate total functions, not cases, outcomes or independent scientific units.",
        "rows": sorted(undecided_rows, key=lambda row: row["adapter_id"]),
    }
    return result, registry


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--predecessor", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    predecessor = args.predecessor.resolve()
    protocol = load(HERE / "P1_V8_PROTOCOL.json")
    assert protocol["outcome_boundary"] == {
        "case_text_accessed": False,
        "model_or_comparator_executed": False,
        "protected_data_accessed": False,
        "row_level_outcomes_accessed": False,
        "system_outputs_accessed": False,
    }
    assert git(repo, "rev-parse", f"{PUBLIC_COMMIT}^{{commit}}", text=True).strip() == PUBLIC_COMMIT
    assert git(repo, "rev-parse", f"{PUBLIC_COMMIT}^{{tree}}", text=True).strip() == protocol["frozen_public_target_corpus"]["tree"]

    captured_at = datetime.now(timezone.utc).isoformat()
    repo_status, repo_headers, repo_body = fetch(API)
    commit_status, commit_headers, commit_body = fetch(f"{API}/commits/{PUBLIC_COMMIT}")
    licence_status, licence_headers, licence_body = fetch(f"{API}/license")
    assert repo_status == 200 and commit_status == 200
    repo_meta = json.loads(repo_body)
    commit_meta = json.loads(commit_body)
    assert repo_meta["full_name"] == REPOSITORY and repo_meta["private"] is False
    assert commit_meta["sha"] == PUBLIC_COMMIT

    file_rows = []
    for path in protocol["frozen_public_target_corpus"]["files"]:
        status, headers, body = fetch(f"{RAW}/{path}")
        assert status == 200
        local = git(repo, "show", f"{PUBLIC_COMMIT}:{path}")
        assert isinstance(local, bytes) and body == local
        file_rows.append({
            "path": path,
            "public_raw_url": f"{RAW}/{path}",
            "public_blob_url": f"https://github.com/{REPOSITORY}/blob/{PUBLIC_COMMIT}/{path}",
            "http_status": status,
            "media_type": headers.get("content-type"),
            "etag": headers.get("etag"),
            "last_modified": headers.get("last-modified"),
            "bytes": len(body),
            "line_count": len(body.splitlines()),
            "sha256": sha(body),
            "git_blob_sha1": git(repo, "rev-parse", f"{PUBLIC_COMMIT}:{path}", text=True).strip(),
            "remote_equals_local_commit_bytes": True,
            "payload_retained_in_handoff": False,
        })

    tree_paths = git(repo, "ls-tree", "-r", "--name-only", PUBLIC_COMMIT, text=True).splitlines()
    licence_names = [path for path in tree_paths if Path(path).name.upper() in {"LICENSE", "LICENSE.MD", "LICENSE.TXT", "COPYING", "COPYING.MD", "NOTICE", "COPYRIGHT"}]
    licence_candidates = [
        {
            "path": path,
            "scope_status": "SCOPED_TO_OTHER_SUBTREE__NOT_ASSUMED_TO_APPLY_TO_FROZEN_TARGET_CORPUS",
        }
        for path in licence_names
    ]
    decisions = ["KEEP_SEARCH", "KEEP_COMPILE", "KEEP_REPAIR", "REVISE_MEASUREMENT", "REFORMULATE_OBJECTIVE", "REFORMULATE_BOUNDARY", "UNRESOLVED"]
    actions = ["SEARCH_MORE", "COMPILE_OR_REPRESENT", "REPAIR_ENV_OR_HARNESS", "REMEASURE", "TEST_OBJECTIVE_BASIS", "TEST_PROBLEM_BOUNDARY", "ABSTAIN"]
    census = occurrence_census(repo, decisions + actions, protocol["frozen_public_target_corpus"]["files"])

    source_registry = {
        "schema_version": "orion.p1.public-target-source-provenance-registry.v8",
        "registry_id": "P1.V8.PUBLIC.TARGET.SOURCE.PROVENANCE",
        "captured_at_utc": captured_at,
        "repository": {
            "full_name": repo_meta["full_name"],
            "html_url": repo_meta["html_url"],
            "visibility": repo_meta.get("visibility"),
            "private": repo_meta["private"],
            "default_branch": repo_meta["default_branch"],
            "api_http_status": repo_status,
            "api_etag": repo_headers.get("etag"),
            "license_field": repo_meta.get("license"),
        },
        "commit": {
            "sha": commit_meta["sha"],
            "tree_sha": commit_meta["commit"]["tree"]["sha"],
            "html_url": commit_meta["html_url"],
            "author_name": commit_meta["commit"]["author"]["name"],
            "authored_at": commit_meta["commit"]["author"]["date"],
            "message": commit_meta["commit"]["message"],
            "signature_verified": commit_meta["commit"]["verification"]["verified"],
            "signature_reason": commit_meta["commit"]["verification"]["reason"],
            "api_http_status": commit_status,
            "api_etag": commit_headers.get("etag"),
        },
        "files": file_rows,
        "occurrence_census": census,
        "occurrence_census_scope": "The seven frozen target-semantic source files only; unrelated repository occurrences are excluded.",
        "payload_policy": {
            "remote_bodies_fetched_for_hash_and_byte_equality_only": True,
            "remote_bodies_written_to_handoff": False,
            "source_line_payloads_written_to_handoff": False,
            "occurrence_line_hashes_only": True,
            "case_or_outcome_payloads_accessed": False,
        },
        "terminal": "PUBLIC_ORION_TARGET_CORPUS_COMMIT_AND_BYTES_BOUND__REMOTE_PAYLOAD_NOT_RETAINED",
    }
    dump("P1_V8_PUBLIC_TARGET_SOURCE_REGISTRY.json", source_registry)

    predecessor_provenance = load(predecessor / "PROVENANCE_URLS_V1.json")
    rights = {
        "schema_version": "orion.p1.public-target-source-rights-registry.v8",
        "registry_id": "P1.V8.PUBLIC.TARGET.SOURCE.RIGHTS",
        "captured_at_utc": captured_at,
        "target_repository": {
            "public_read_access": True,
            "repository_visibility": repo_meta.get("visibility"),
            "github_repository_license_field": repo_meta.get("license"),
            "github_license_endpoint_http_status": licence_status,
            "github_license_endpoint_message": json.loads(licence_body).get("message") if licence_body else None,
            "license_file_candidates_at_pinned_tree": licence_candidates,
            "license_file_candidate_count": len(licence_names),
            "applicable_target_corpus_license_file_count": 0,
            "reuse_or_redistribution_licence_status": "NO_REUSE_LICENCE_FOUND__CANNOT_CHECK_PERMISSION",
            "semantic_authority_status": "PRIMARY_OWNER_REPOSITORY_PUBLICLY_ACCESSIBLE_AT_IMMUTABLE_COMMIT",
            "separation_rule": "Semantic provenance and reuse rights are separate. Public visibility and authorship do not supply a reuse licence or owner ratification of missing denotation fields.",
            "retention_rule": "No source body is copied into V8; only hashes, byte counts, public URLs, line anchors and conservative paraphrases are retained.",
            "api_license_headers": {k: licence_headers.get(k) for k in ["content-type", "etag", "last-modified"]},
        },
        "inherited_source_taxonomy_rights": predecessor_provenance["rights_evidence_summary"],
        "inherited_source_taxonomy_terminal": predecessor_provenance["terminal"],
        "rights_sufficient_for": [
            "hash and public-URL provenance",
            "bounded semantic inspection and conservative paraphrase in this research record",
            "independent refetch by a reviewer subject to their own rights determination",
        ],
        "rights_not_established_for": [
            "redistribution of the target repository source bodies in this handoff",
            "publication of substantial copied target text",
            "derivative relicensing",
            "owner ratification of target semantics",
        ],
        "terminal": "P1_V8_PUBLIC_TARGET_READ_ACCESS_AND_PROVENANCE_BOUND__TARGET_REUSE_LICENCE_NOT_FOUND",
    }
    dump("P1_V8_RIGHTS_REGISTRY.json", rights)

    semantic = target_registry()
    semantic["source_registry_sha256"] = sha((HERE / "P1_V8_PUBLIC_TARGET_SOURCE_REGISTRY.json").read_bytes())
    semantic["rights_registry_sha256"] = sha((HERE / "P1_V8_RIGHTS_REGISTRY.json").read_bytes())
    dump("P1_V8_TARGET_SEMANTIC_REGISTRY.json", semantic)

    matrix_path = predecessor / "ADAPTER_COMPATIBILITY_MATRIX_V2.json"
    assert sha(matrix_path.read_bytes()) == "64d44ae85dc54411ae083c35f53090ac6776ec81e57a2425113c437f3fd746d5"
    matrix = load(matrix_path)
    enumeration, adapter_registry = enumerate_adapters(matrix, semantic)
    assert enumeration["total"] == 7 ** 6 == 117649
    assert enumeration["fully_certified"] == 0
    assert enumeration["known_rejected"] == 116929
    assert enumeration["not_disproved_but_uncertified"] == 720
    dump("P1_V8_720_ADAPTER_REGISTRY.json", adapter_registry)

    cell_rows = []
    for source in matrix["matrix"]:
        for target, predecessor_cell in matrix["matrix"][source].items():
            if source == "UNRESOLVED" or target == "UNRESOLVED":
                v8_status = predecessor_cell["status"]
                missing = predecessor_cell.get("missing_bindings", [])
            else:
                v8_status = "CANNOT_CHECK"
                missing = [
                    "EXHAUSTIVE_POSTPUBLICATION_COORDINATE",
                    "LICENSED_POSTPUBLICATION_OPERATIONS",
                    "FORBIDDEN_POSTPUBLICATION_OPERATIONS",
                    "OWNER_RATIFIED_DECISION_TO_POSTPUBLICATION_BRIDGE_OR_EXPLICIT_NONE",
                    "TARGET_ERROR_TIMEOUT_MALFORMED_UNSUPPORTED_TERMINAL_BEHAVIOR",
                ]
            cell_rows.append({
                "source_terminal": source,
                "target_decision": target,
                "predecessor_status": predecessor_cell["status"],
                "v8_status": v8_status,
                "newly_bound_target_facts": ["SCIENTIFIC_DECISION_SORT", "SCIENTIFIC_PROCESS_ANCHOR", "DIAGNOSTIC_PROBE_IS_SEPARATE_TYPED_OBJECT"] if target != "UNRESOLVED" else ["FAIL_CLOSED_UNRESOLVED"],
                "missing_bindings": missing,
                "reason": "Public primary artifacts bind an intensional scientific-process anchor and prove probe/decision type separation, but do not supply exhaustive postpublication licensed/forbidden operations or an owner-ratified bridge. Lexical or causal overlap is not extensional equivalence." if v8_status == "CANNOT_CHECK" else predecessor_cell["reason"],
            })

    adjudication = {
        "schema_version": "orion.p1.public-target-semantics-adapter-adjudication.v8",
        "result_id": "P1.V8.PUBLIC.TARGET.SEMANTICS.ADJUDICATION",
        "protocol_id": protocol["protocol_id"],
        "authority": "UNCHANGED_GATES_PLUS_PUBLIC_PRIMARY_TARGET_SEMANTIC_AND_RIGHTS_EVIDENCE",
        "predecessor_matrix_sha256": sha(matrix_path.read_bytes()),
        "target_semantic_registry_sha256": sha((HERE / "P1_V8_TARGET_SEMANTIC_REGISTRY.json").read_bytes()),
        "adapter_registry_sha256": sha((HERE / "P1_V8_720_ADAPTER_REGISTRY.json").read_bytes()),
        "enumeration": enumeration,
        "change_from_r7": {
            "fully_certified_delta": 0,
            "known_rejected_delta": 0,
            "not_disproved_but_uncertified_delta": 0,
            "new_positive_semantic_result": "PUBLIC_PRIMARY_ARTIFACTS_BIND_R7_AS_SEVEN_SCIENTIFIC_DECISIONS_SEPARATE_FROM_DIAGNOSTIC_PROBES",
            "unresolved_residual": "ZERO_OF_SIX_ACTIONABLE_TARGETS_HAS_AN_EXHAUSTIVE_POSTPUBLICATION_DENOTATION",
        },
        "pair_matrix": {
            "row_count": len(cell_rows),
            "status_counts": dict(sorted(Counter(row["v8_status"] for row in cell_rows).items())),
            "rows": cell_rows,
        },
        "not_disproved_adapter_disposition": {
            "input_count": 720,
            "certified_by_v8_public_evidence": 0,
            "authoritatively_rejected_by_v8_public_evidence": 0,
            "remain_cannot_check": 720,
            "minimum_missing_actionable_images_per_map": 5,
            "reason": "Every not-disproved function fixes UNRESOLVED and maps five actionable source terminals injectively into six actionable target decisions. Every one of those five images lacks essential postpublication denotation fields.",
        },
        "no_missing_evidence_as_impossibility": True,
        "terminal": protocol["terminals"]["cannot_check"],
    }
    assert adjudication["pair_matrix"]["status_counts"] == {"CANNOT_CHECK": 30, "PASS": 1, "REJECT": 11}
    dump("P1_V8_ADAPTER_ADJUDICATION_RESULT.json", adjudication)

    theorem = {
        "schema_version": "orion.p1.public-target-semantic-underdetermination-theorem.v8",
        "theorem_id": "P1.V8.PUBLIC.TARGET.SEMANTIC.UNDERDETERMINATION",
        "authority": "FORMAL_RESULT_RELATIVE_TO_FROZEN_PUBLIC_CORPUS_AND_UNCHANGED_GATES",
        "parts": [
            {
                "id": "V8.T1.DECISION_PROBE_SEPARATION",
                "status": "PROVED_WITHIN_PUBLIC_ARD_PROTOCOL",
                "statement": "The seven R7 scientific decisions and seven diagnostic actions are separate types; no inherited one-to-one decision/action pairing exists.",
                "proof": "The protocol declares separate vocabularies. Executable templates use a single diagnostic probe to distinguish two different terminal decisions, providing direct non-functionality witnesses.",
            },
            {
                "id": "V8.T2.PUBLIC_EVIDENCE_NONIDENTIFICATION",
                "status": "PROVED_RELATIVE_TO_V8_REGISTRY",
                "statement": "Under G2-G4, public process anchors without exhaustive postpublication operation profiles identify neither equality nor inequality for any of the 30 actionable source-target cells.",
                "proof": "Equality requires licensed/forbidden operation and coordinate equality; authoritative rejection requires contradiction or inequality. Each target lacks all exhaustive postpublication fields, and the protocol forbids converting absence or lexical mismatch into inequality.",
            },
            {
                "id": "V8.T3.ENUMERATION_INVARIANCE",
                "status": "PROVED_BY_EXHAUSTIVE_ENUMERATION",
                "statement": "Consequently the unchanged seven-gate audit retains 0 fully certified, 116,929 rejected and 720 not-disproved but uncertified maps.",
                "proof": "Direct enumeration of all 117,649 functions reproduces the predecessor partition; each of the 720 survivors contains five CANNOT_CHECK actionable images and UNRESOLVED->UNRESOLVED.",
            },
            {
                "id": "V8.T4.OWNER_ALGEBRA_EQUIVALENCE",
                "status": "CONDITIONAL_EQUIVALENCE",
                "statement": "A survivor f is certifiable exactly when an owner-ratified closed-world target algebra supplies target profiles and terminal behavior that make every image of f pass G2-G7; if every target profile forbids one source-required operation, no total adapter exists under that algebra.",
                "caveat": "The antecedent is unbound. This is not owner ratification and not an impossibility claim about inherited R7 semantics.",
            },
        ],
        "strongest_conclusion": "Public repository evidence resolves target intent and probe/decision typing but is logically insufficient for source-native postpublication transport. Source-side taxonomy expansion cannot close G16; only target-owner semantic authority can change the 720-map partition.",
        "terminal": "P1_V8_PUBLIC_TARGET_SEMANTIC_UNDERDETERMINATION_PROVED__OWNER_ALGEBRA_REQUIRED",
    }
    dump("P1_V8_CONDITIONAL_EQUIVALENCE_THEOREM.json", theorem)

    result = {
        "schema_version": "orion.p1.source-native-target-semantics-result.v8",
        "result_id": "P1.R7.PUBLIC.TARGET.SEMANTICS.V8.RESULT",
        "successor_identity": protocol["successor_identity"],
        "terminal": protocol["terminals"]["cannot_check"],
        "authority": "PUBLIC_PRIMARY_TARGET_SEMANTIC_PROVENANCE_RIGHTS_AND_FORMAL_ADJUDICATION_ONLY",
        "artifact_bindings": {
            name: sha((HERE / name).read_bytes())
            for name in [
                "P1_V8_PROTOCOL.json",
                "P1_V8_PUBLIC_TARGET_SOURCE_REGISTRY.json",
                "P1_V8_RIGHTS_REGISTRY.json",
                "P1_V8_TARGET_SEMANTIC_REGISTRY.json",
                "P1_V8_720_ADAPTER_REGISTRY.json",
                "P1_V8_ADAPTER_ADJUDICATION_RESULT.json",
                "P1_V8_CONDITIONAL_EQUIVALENCE_THEOREM.json",
                "P1_V8_REQUIRED_OWNER_ALGEBRA_SCHEMA.json",
                "P1_V8_REQUIRED_FIELD_CUSTODIAN_REGISTRY.json",
            ]
        },
        "positive_successor_evidence": {
            "public_repository_bound": True,
            "immutable_public_commit_bound": True,
            "remote_local_bytes_equal_for_all_semantic_sources": True,
            "target_decision_identifiers_bound": 7,
            "target_scientific_process_anchors_bound": 7,
            "decision_probe_type_separation_proved": True,
            "raw_public_payloads_retained": 0,
        },
        "adapter_result": adjudication["not_disproved_adapter_disposition"],
        "execution_or_claim_authority": False,
        "rights_result": rights["terminal"],
        "owner_algebra_status": "ABSENT__SCHEMA_ONLY",
        "preserved_r7_negatives": {
            "fully_certified": 0,
            "known_rejected": 116929,
            "not_disproved_but_uncertified": 720,
            "partial_adapter": {"UNRESOLVED": "UNRESOLVED"},
            "conditional_full_withdrawal_impossibility_only": True,
            "missing_evidence_is_not_impossibility": True,
        },
        "manuscript_integration": {
            "warranted": False,
            "disposition": "NO_MAIN_MANUSCRIPT_CHANGE__DEVELOPMENT_AND_CLAIM_LEDGER_REFERENCE_ONLY_IF_USEFUL",
            "reason": "The current manuscript already states decision/action type separation and CANNOT_CHECK target semantics. V8 strengthens provenance, rights and formal sufficiency evidence but does not change the scientific terminal, adapter count or title-level authority.",
        },
        "next_discriminator": "The R7 vocabulary owner or formally delegated custodian must complete, licence, content-address and sign P1_V8_REQUIRED_OWNER_ALGEBRA_SCHEMA.json, including exhaustive target postpublication coordinates, licensed/forbidden operations, probe/decision typing, error/timeout behavior and authority limits. An independent semantic reviewer then reruns the unchanged 117,649-map audit. Until then, retain all 720 as CANNOT_CHECK.",
    }
    dump("P1_RESULT_V8.json", result)
    print(json.dumps({
        "terminal": result["terminal"],
        "public_sources": len(file_rows),
        "remote_local_byte_matches": sum(row["remote_equals_local_commit_bytes"] for row in file_rows),
        "target_decisions": 7,
        "actionable_postpublication_denotations": 0,
        "maps_certified": 0,
        "maps_rejected_new": 0,
        "maps_remain_cannot_check": 720,
        "payloads_retained": 0,
        "manuscript_integration_warranted": False,
    }, indent=2))


if __name__ == "__main__":
    main()
