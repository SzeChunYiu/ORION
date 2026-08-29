#!/usr/bin/env python3
"""Hostile validator for issue #1701 ORION-19 through ORION-15 recovery packet."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

LIVE_MAIN = "b8fd5d2ca8eb1f6547592893591ba3aa93bf96c8"
LIVE_TREE = "e4a89bd9a1679e15bc4d4989438597909013813c"
PARENT_COMMIT = "7974125ff7c36b3827170f81f121d60fc07467eb"
PARENT_TREE = "b20fd7d14356f57e0d561f73ea95429258089966"
EXPECTED_ORDER = [19, 18, 17, 16, 15]
EXPECTED_BRANCH_HEADS = {
    "claude/r5-revival-orion19-18-20260828": "a2fe9d6a10aa27cb1deda5a90c680ed5bf45e8f8",
    "claude/w1-final-submission-20260828": "d2484d59c1ec5561a7920049158668be0eacf86e",
    "chatgpt/all-paper-consolidation-authoritative-20260828": "b4a8212479018162629676b36ddeef3cfa28c19c",
    "chatgpt/orion15-v4-independent-verification-20260827": "765adaab44b3af1a7c4640e0f94b8caede58e8a0",
    "codex/orion15-bounded-harvest-adopt-20260828": "be4f67656f11c37d773ea6eb530226dfc57a91f8",
}
REQUIRED_FILES = {
    "README.md", "QUESTION.md", "PROTOCOL.json", "RECOVERY_MANIFEST.json",
    "BRANCH_DIVERGENCE_V1.json", "ACTIVE_LANES.json", "PAPER_STATUS_V1.json",
    "ADVERSE_AND_CANNOT_CHECK.jsonl", "ORION17_CHRONOLOGY_RECEIPT.md",
    "ORION16_GOVERNANCE_RECONCILIATION.md", "EXPERT_REVIEW_MATRIX.md",
    "CLAIM_DISPOSITION.md", "RESULT.json", "COMMIT_BASE.json", "APPLY.md",
    "check_descending_recovery.py", "test_check_descending_recovery.py", "SHA256SUMS",
}
REQUIRED_ADVERSE = {
    "ORION19_V2_GATE_NOT_MET", "ORION19_DA_CANNOT_CHECK",
    "ORION19_QWEN_SCALE_NEGATIVE", "ORION19_ORBIT_ZERO_PROTECTED_COVERAGE",
    "ORION19_UT3_ZERO_CELLS", "ORION18_EXTERNAL_VALIDATION_CANNOT_CHECK",
    "ORION18_SEVEN_GOLD_CANNOT_CHECK", "ORION17_ARBITRARY_CHAIN_RETRACTION_RETAINED",
    "ORION17_GOVERNANCE_NOT_SELF_ADJUDICATED", "ORION17_FILING_BLOCKED_NO_STANDALONE_MANUSCRIPT",
    "ORION16_NFCORE_NULL_RETAINED", "ORION16_EXTERNAL_INDEPENDENT_VALIDATION_CANNOT_CHECK",
    "ORION16_PR1695_OWNS_CANONICAL_ACQUISITION", "ORION15_V3_NEGATIVE_RETAINED",
    "ORION15_RULE_DEFECT_RETAINED", "ORION15_PERFECT_CEILING_NOT_REPRODUCED",
    "ORION15_LIVE_PROVIDER_AUTHORITY_BLOCKED", "ORION15_EXTERNAL_REPLICATION_NOT_RUN",
}

class ValidationError(RuntimeError):
    pass

def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)

def load_json(root: Path, name: str) -> Any:
    try:
        return json.loads((root / name).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"{name}: unreadable JSON: {exc}") from exc

def read_adverse(root: Path) -> list[dict[str, Any]]:
    rows = []
    try:
        for lineno, line in enumerate((root / "ADVERSE_AND_CANNOT_CHECK.jsonl").read_text(encoding="utf-8").splitlines(), 1):
            if line.strip():
                rows.append(json.loads(line))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"ADVERSE_AND_CANNOT_CHECK.jsonl: {exc}") from exc
    return rows

def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)

def verify_checksums(root: Path) -> None:
    recorded: dict[str, str] = {}
    try:
        lines = (root / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ValidationError(f"SHA256SUMS unreadable: {exc}") from exc
    for lineno, line in enumerate(lines, 1):
        parts = line.split("  ", 1)
        require(len(parts) == 2, f"SHA256SUMS line {lineno}: malformed")
        digest, rel = parts
        require(rel != "SHA256SUMS", "SHA256SUMS must not self-hash")
        require(rel not in recorded, f"SHA256SUMS duplicate path: {rel}")
        require(len(digest) == 64 and all(c in "0123456789abcdef" for c in digest), f"SHA256SUMS line {lineno}: bad digest")
        recorded[rel] = digest
    expected = sorted(p.name for p in root.iterdir() if p.is_file() and p.name != "SHA256SUMS")
    require(sorted(recorded) == expected, "SHA256SUMS file set does not match packet file set")
    for rel, expected_digest in recorded.items():
        actual = hashlib.sha256((root / rel).read_bytes()).hexdigest()
        require(actual == expected_digest, f"checksum mismatch: {rel}")

def validate(root: Path, *, check_checksums: bool = True) -> list[str]:
    root = root.resolve()
    require(root.is_dir(), f"packet root is not a directory: {root}")
    names = {p.name for p in root.iterdir() if p.is_file()}
    missing = REQUIRED_FILES - names
    require(not missing, f"required files missing: {sorted(missing)}")
    if check_checksums:
        verify_checksums(root)

    protocol = load_json(root, "PROTOCOL.json")
    manifest = load_json(root, "RECOVERY_MANIFEST.json")
    divergence = load_json(root, "BRANCH_DIVERGENCE_V1.json")
    lanes = load_json(root, "ACTIVE_LANES.json")
    status = load_json(root, "PAPER_STATUS_V1.json")
    result = load_json(root, "RESULT.json")
    base = load_json(root, "COMMIT_BASE.json")
    adverse = read_adverse(root)
    checks: list[str] = []

    require(protocol["base_chain"]["live_main_commit"] == LIVE_MAIN, "live main commit drift")
    require(protocol["base_chain"]["live_main_tree"] == LIVE_TREE, "live main tree drift")
    require(protocol["base_chain"]["parent_commit"] == PARENT_COMMIT, "protocol parent commit drift")
    require(protocol["base_chain"]["parent_tree"] == PARENT_TREE, "protocol parent tree drift")
    require(base["parent_commit_sha"] == PARENT_COMMIT, "commit parent drift")
    require(base["parent_tree_sha"] == PARENT_TREE, "commit parent tree drift")
    require(base["direct_main_commit"] is False, "direct main commit is forbidden")
    require(base["remote_push_performed"] is False, "remote push must not be fabricated")
    checks.append("exact base chain and branch discipline")

    require(protocol["paper_order"] == EXPECTED_ORDER, "protocol descending order changed")
    require(status["paper_order"] == EXPECTED_ORDER, "status descending order changed")
    require(status["next_descending_cursor"] == 14, "next descending cursor must be 14")
    papers = status["papers"]
    require([p["paper"] for p in papers] == EXPECTED_ORDER, "paper records are not in descending order")
    require(len({p["paper"] for p in papers}) == 5, "duplicate paper record")
    by_paper = {p["paper"]: p for p in papers}
    for paper in papers:
        require(paper["packet_authority_delta"] == "NONE", f"ORION-{paper['paper']}: packet authority inflation")
    checks.append("descending order 19 through 15 and zero packet authority")

    require(protocol["recovery_rules"]["path_by_path_only"] is True, "pathwise recovery disabled")
    require(protocol["recovery_rules"]["whole_branch_merge_forbidden"] is True, "whole branch merge enabled")
    require(protocol["recovery_rules"]["manuscript_edits_in_this_packet"] is False, "manuscript edit falsely claimed")
    require(protocol["recovery_rules"]["same_research_team_is_external_investigator"] is False, "same team promoted to external investigator")
    require(manifest["whole_branch_merge_performed"] is False, "whole branch merge performed")
    checks.append("path-by-path recovery only")

    seen_heads: dict[str, str] = {}
    for artifact in manifest["artifacts"]:
        require(len(artifact["blob_sha"]) == 40, f"bad blob SHA for {artifact['path']}")
        branch = artifact["branch"]
        if branch != "main":
            expected = EXPECTED_BRANCH_HEADS.get(branch)
            require(expected is not None, f"unregistered recovery branch: {branch}")
            require(artifact["branch_head"] == expected, f"branch head drift: {branch}")
            seen_heads[branch] = artifact["branch_head"]
        else:
            require(artifact["branch_head"] == LIVE_MAIN, "main artifact head drift")
    require(seen_heads == EXPECTED_BRANCH_HEADS, "not all recovery branch heads are bound")
    require(len(manifest["artifacts"]) == 15, "recovery artifact count drift")
    require(divergence["whole_branch_merge_allowed"] is False, "divergent branch wholesale merge permitted")
    checks.append("exact source branch heads and artifact blobs")

    lane_by_pr = {lane["pull_request"]: lane for lane in lanes["lanes"]}
    require(set(lane_by_pr) == {1692, 1695, 1698}, "active lane set drift")
    for pr, lane in lane_by_pr.items():
        require(lane["state"] == "OPEN", f"PR #{pr} state drift")
        require(lane["duplicate_lane_created"] is False, f"PR #{pr} duplicated")
    require(lane_by_pr[1695]["head"] == "8a04e08020ab27ca19afe2a05959bc9900570cc8", "PR #1695 head drift")
    require(lane_by_pr[1698]["head"] == "173b1b0c5818b9d9ecd7aa3b46058e28aa473920", "PR #1698 head drift")
    require(lane_by_pr[1698]["current_empirical_authority"] is False, "PR #1698 conformance promoted")
    checks.append("canonical active-lane routing")

    adverse_ids = {row["id"] for row in adverse}
    require(adverse_ids == REQUIRED_ADVERSE, "adverse/CANNOT_CHECK ledger drift")
    checks.append("all adverse and CANNOT_CHECK states retained")

    p19 = by_paper[19]
    v3 = p19["v3"]
    require(v3["terminal"] == "P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V3_SUPPORTED", "ORION-19 V3 terminal drift")
    require(v3["task_count"] == 5 and v3["diagnosis_accuracy"] == 1.0, "ORION-19 V3 metrics drift")
    require(v3["generic_accuracy"] == 0.2, "ORION-19 generic baseline drift")
    require(v3["probe_protected_agreement_all_cells"] is True, "ORION-19 agreement lost")
    require(v3["half_draw_stability_all_digits"] is True, "ORION-19 stability lost")
    require(v3["d_a_decision"] == "CANNOT_CHECK", "ORION-19 D-A CANNOT_CHECK erased")
    require(v3["d_a_converted_to_pass"] is False, "ORION-19 D-A falsely promoted")
    require(v3["v2_terminal_retained"] == "P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V2_GATE_NOT_MET", "ORION-19 V2 failure erased")
    require(p19["coverage_gate"]["protected_orbit_coverage"] == 0.0, "ORION-19 protected coverage inflated")
    require(p19["coverage_gate"]["representation_only_successor_indicated"] is False, "ORION-19 representation rescue invented")
    require(p19["ut3"]["declared_cells"] == 1344 and p19["ut3"]["cells_executed"] == 0, "ORION-19 UT3 execution fabricated")
    require(p19["qwen_scaling_frontier_supported"] is False, "ORION-19 Qwen negative erased")
    require(p19["new_threshold_retuning"] is False, "ORION-19 post-outcome retuning")
    checks.append("ORION-19 V3 plus retained negatives and blockers")

    p18 = by_paper[18]
    rev = p18["reverification"]
    require(rev["binding_checker_status"] == "PASS" and rev["binding_checker_errors"] == [], "ORION-18 binding reverification drift")
    require(rev["case_count"] == 20, "ORION-18 case count drift")
    require(rev["domain_counts"] == {"empirical": 5, "formal": 5, "multiple_support": 5, "systems": 5}, "ORION-18 domain counts drift")
    require(rev["native_system_executed"] is False and rev["native_output_simulated"] is False, "ORION-18 native execution fabricated")
    require(p18["external_validation"].startswith("CANNOT_CHECK"), "ORION-18 external validation self-certified")
    require(p18["correct_by_design_gold_cannot_check_count"] == 7, "ORION-18 gold CANNOT_CHECK count drift")
    checks.append("ORION-18 bounded reverification and authority boundary")

    p17 = by_paper[17]
    chronology = p17["chronology"]
    graph_t = parse_time(chronology["graph_only_time_utc"])
    prediction_t = parse_time(chronology["prediction_commit_time_utc"])
    outcome_t = parse_time(chronology["outcome_time_utc"])
    require(graph_t < prediction_t < outcome_t, "ORION-17 prospective chronology violated")
    require(chronology["threshold"] == 1.5, "ORION-17 threshold drift")
    held = p17["held_out"]
    require(held["predictions_correct"] == held["prediction_count"] == 5, "ORION-17 5/5 result drift")
    require(held["tornado_load_bearing"] is True and held["tornado_donor_false_retentions"] == 12773, "ORION-17 Tornado disambiguator drift")
    require(all(v == 0 for v in held["exact_false_retentions"].values()), "ORION-17 exact-containment false retention")
    require(p17["governance"]["issue_1649_reconciliation_required"] is True, "ORION-17 governance requirement erased")
    require(p17["governance"]["governance_adjudicated_by_this_packet"] is False, "ORION-17 governance self-adjudicated")
    require(p17["governance"]["arbitrary_chain_duplicate_retraction_retained"] is True, "ORION-17 duplicate theorem retraction erased")
    require(p17["filing_terminal"] == "BLOCKED__NO_STANDALONE_MANUSCRIPT" and p17["filing_ready"] is False, "ORION-17 filing blocker erased")
    checks.append("ORION-17 prospective chronology, result and filing/governance limits")

    p16 = by_paper[16]
    result16 = p16["pr1692_result"]
    require(result16["classification"] == "BOUNDED_SECOND_TIER_EVIDENCE", "ORION-16 result overpromoted")
    require(result16["systems_evaluable"] == 3, "ORION-16 system count drift")
    require(result16["top_tier_authority"] is False, "ORION-16 top-tier authority self-awarded")
    require(result16["external_independent_validation"] == "CANNOT_CHECK", "ORION-16 external validation self-certified")
    require(result16["mathlib4"]["nodes"] == 8409 and result16["mathlib4"]["conservative_1pct_median_cost"] == 8372.0, "ORION-16 Mathlib metrics drift")
    require(result16["nf_core_rnaseq"]["null_retained"] is True and result16["nf_core_rnaseq"]["direct_neighbours_stranded_total"] == 0, "ORION-16 nf-core null erased")
    canonical = p16["canonical_acquisition"]
    require(canonical["pull_request"] == 1695 and canonical["duplicate_protocol_created"] is False, "ORION-16 canonical acquisition duplicated")
    require(canonical["outcome_claimed_by_this_packet"] is False, "ORION-16 acquisition outcome fabricated")
    checks.append("ORION-16 bounded result versus canonical authoritative acquisition")

    p15 = by_paper[15]
    v4 = p15["v4"]
    require(v4["case_count"] == 180 and v4["subject_accuracy"] == 1.0, "ORION-15 V4 metrics drift")
    require(v4["false_broad"] == v4["authority_violations"] == v4["harm"] == 0, "ORION-15 V4 safety drift")
    require(v4["preservation_refusal"] == 1.0 and v4["fresh_transfer"] == 0.8888888888888888, "ORION-15 V4 boundary metrics drift")
    require(v4["v3_negative_retained"] == "NO_TERMINAL_UNDER_FROZEN_RULES", "ORION-15 V3 negative erased")
    iv = p15["independent_verification"]
    require(iv["rule_defect_detected"] is True, "ORION-15 rule defect hidden")
    require(iv["rule_defect_controlling"] is False, "ORION-15 rule defect misclassified")
    require(iv["post_outcome_in_place_repair_permitted"] is False, "ORION-15 post-outcome repair enabled")
    require(iv["live_provider_authority"] is False and iv["external_real_world_validity"] is False, "ORION-15 bounded result overgeneralized")
    glm = p15["glm53_harvest"]
    require((glm["control_correct"], glm["treatment_correct"], glm["denominator"]) == (22, 23, 24), "ORION-15 GLM harvest counts drift")
    require(glm["treatment_beats_control"] is True, "ORION-15 treatment direction lost")
    require(glm["former_perfect_treatment_ceiling_reproduced"] is False, "ORION-15 perfect ceiling falsely restored")
    require(glm["external_investigator_replication"] is False, "ORION-15 same-team harvest promoted to external replication")
    lane15 = p15["canonical_longitudinal_lane"]
    require(lane15["pull_request"] == 1698 and lane15["formal_conformance_only"] is True, "ORION-15 canonical longitudinal lane drift")
    require(lane15["empirical_campaign_run"] is False and lane15["duplicate_lane_created"] is False, "ORION-15 longitudinal execution or duplication fabricated")
    checks.append("ORION-15 V4, defect disclosure, GLM boundary and longitudinal routing")

    require(result["papers_audited"] == EXPECTED_ORDER and result["paper_count"] == 5, "result paper set drift")
    require(result["recovery_artifact_count"] == 15, "result artifact count drift")
    require(result["whole_branch_merges"] == result["manuscripts_modified"] == result["new_scientific_outcomes"] == result["active_lanes_duplicated"] == 0, "integration-only result violated")
    require(result["packet_scientific_authority_delta"] == "NONE", "packet authority inflation")
    require(result["submission_authority"] is False and result["external_investigator_authority"] is False, "unearned authority")
    require(result["remote_push_performed"] is False, "remote push fabricated")
    require(result["terminal"] == "DESCENDING_19_15_RECOVERY_PACKET_GREEN__SCOPED_EVIDENCE_ONLY", "packet terminal drift")
    checks.append("scoped integration-only terminal")
    return checks

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--skip-checksums", action="store_true")
    args = parser.parse_args()
    try:
        checks = validate(args.root, check_checksums=not args.skip_checksums)
    except ValidationError as exc:
        print(f"RED: {exc}")
        return 1
    print("GREEN: DESCENDING_19_15_RECOVERY_PACKET_GREEN__SCOPED_EVIDENCE_ONLY")
    for check in checks:
        print(f"  - {check}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
