#!/usr/bin/env python3
"""Hostile validator for issue #1701 ORION-14 through ORION-10 recovery packet."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

LIVE_MAIN = "b8fd5d2ca8eb1f6547592893591ba3aa93bf96c8"
LIVE_TREE = "e4a89bd9a1679e15bc4d4989438597909013813c"
PARENT_COMMIT = "7ed14b2ef7463e9f41b1372fc9d1bdbb382aa978"
PARENT_TREE = "ba24d731ac1a5d10577b8f003ffb96a38cbf016d"
EXPECTED_ORDER = [14, 13, 12, 11, 10]
EXPECTED_HEADS = {
    "claude/orion14-promotion-reduct-20260828": "bee9829ae05fb317e1d381d50c64b7f7d2a430a2",
    "codex/wave1-orion14-closeout-20260828": "a5c5225f039a51809f81a015e1aa3fab80bd1c9e",
    "claude/orion13-minimal-semantic-separator-20260828": "b6dd5ed5c57562acaa2d47b1f7b1d7e49837c3b4",
    "codex/wave1-orion12-closeout-20260828": "ae670d943228ea07b53de28a1a1c174a4f1494c5",
    "claude/orion10-explanation-gap-20260828": "424756c05fde5ae05a95bd9a3fdd7849bbf92fe4",
}
REQUIRED_FILES = {
    "README.md", "QUESTION.md", "PROTOCOL.json", "RECOVERY_MANIFEST.json",
    "BRANCH_DIVERGENCE_V1.json", "LIVE_MAIN_RECONCILIATION.json",
    "PAPER_STATUS_V1.json", "ADVERSE_AND_CANNOT_CHECK.jsonl",
    "ORION14_PACKAGE_AND_REDUCT_HANDOFF.md", "ORION12_PACKAGE_HANDOFF.md",
    "ORION11_CANONICAL_EVIDENCE_RECEIPT.md", "EXPERT_REVIEW_MATRIX.md",
    "CLAIM_DISPOSITION.md", "RESULT.json", "COMMIT_BASE.json", "APPLY.md",
    "check_descending_recovery.py", "test_check_descending_recovery.py",
    "SHA256SUMS",
}
REQUIRED_ADVERSE = {
    "ORION14_400_CASE_TABLE_ABSENT",
    "ORION14_H3_NULL_RETAINED",
    "ORION14_TRANSPORT_HTTP400_RETAINED",
    "ORION14_OLD_FILING_BYTES_STALE",
    "ORION13_OTHER_COORDINATE_NECESSITY_UNTESTED",
    "ORION13_POLARITY_CONFOUND_RETAINED",
    "ORION12_RECALL_GATE_ADVERSE",
    "ORION12_COST_GATE_ADVERSE",
    "ORION12_TWO_ROUTES_UNAVAILABLE",
    "ORION12_NDCG_NON_GATING",
    "ORION12_OLD_FILING_BYTES_STALE",
    "ORION11_ORIGINAL_REPLICATION_INSTRUMENT_FAULT",
    "ORION11_FAITHFUL_COMPARATOR_FALSIFIES_SUPERIORITY",
    "ORION11_COSTED_ORDERING_FALSIFIED",
    "ORION10_ALL_N_THEOREM_CANNOT_CHECK",
    "ORION10_BTRIPLEPRIME_UNFOUND",
    "ORION10_PHYSICAL_ADVANTAGE_UNCLAIMED",
}
EXPECTED_RECOVERABLE = {
    14: ("claude/orion14-promotion-reduct-20260828", 7),
    13: ("claude/orion13-minimal-semantic-separator-20260828", 8),
    10: ("claude/orion10-explanation-gap-20260828", 7),
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
    rows: list[dict[str, Any]] = []
    try:
        for lineno, line in enumerate(
            (root / "ADVERSE_AND_CANNOT_CHECK.jsonl").read_text(
                encoding="utf-8"
            ).splitlines(),
            1,
        ):
            if not line.strip():
                continue
            row = json.loads(line)
            require(isinstance(row, dict), f"adverse line {lineno}: not object")
            rows.append(row)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"ADVERSE_AND_CANNOT_CHECK.jsonl: {exc}") from exc
    return rows

def verify_checksums(root: Path) -> None:
    try:
        lines = (root / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ValidationError(f"SHA256SUMS unreadable: {exc}") from exc
    recorded: dict[str, str] = {}
    for lineno, line in enumerate(lines, 1):
        parts = line.split("  ", 1)
        require(len(parts) == 2, f"SHA256SUMS line {lineno}: malformed")
        digest, rel = parts
        require(rel != "SHA256SUMS", "SHA256SUMS must not self-hash")
        require(rel not in recorded, f"SHA256SUMS duplicate path: {rel}")
        require(
            len(digest) == 64 and all(c in "0123456789abcdef" for c in digest),
            f"SHA256SUMS line {lineno}: bad digest",
        )
        recorded[rel] = digest
    expected = sorted(
        p.name for p in root.iterdir() if p.is_file() and p.name != "SHA256SUMS"
    )
    require(sorted(recorded) == expected, "SHA256SUMS file set mismatch")
    for rel, expected_digest in recorded.items():
        actual = hashlib.sha256((root / rel).read_bytes()).hexdigest()
        require(actual == expected_digest, f"checksum mismatch: {rel}")

def validate(root: Path, *, check_checksums: bool = True) -> list[str]:
    root = root.resolve()
    require(root.is_dir(), f"packet root is not a directory: {root}")
    names = {p.name for p in root.iterdir() if p.is_file()}
    require(not (REQUIRED_FILES - names), f"missing files: {sorted(REQUIRED_FILES - names)}")
    if check_checksums:
        verify_checksums(root)

    protocol = load_json(root, "PROTOCOL.json")
    manifest = load_json(root, "RECOVERY_MANIFEST.json")
    divergence = load_json(root, "BRANCH_DIVERGENCE_V1.json")
    recon = load_json(root, "LIVE_MAIN_RECONCILIATION.json")
    status = load_json(root, "PAPER_STATUS_V1.json")
    result = load_json(root, "RESULT.json")
    base = load_json(root, "COMMIT_BASE.json")
    adverse = read_adverse(root)
    checks: list[str] = []

    require(protocol["base_chain"]["live_main_commit"] == LIVE_MAIN, "live main drift")
    require(protocol["base_chain"]["live_main_tree"] == LIVE_TREE, "live tree drift")
    require(protocol["base_chain"]["parent_commit"] == PARENT_COMMIT, "parent commit drift")
    require(protocol["base_chain"]["parent_tree"] == PARENT_TREE, "parent tree drift")
    require(base["parent_commit_sha"] == PARENT_COMMIT, "commit base parent drift")
    require(base["parent_tree_sha"] == PARENT_TREE, "commit base tree drift")
    require(base["direct_main_commit"] is False, "direct main commit forbidden")
    require(base["remote_push_performed"] is False, "remote push fabricated")
    checks.append("exact base chain and protected branch")

    require(protocol["paper_order"] == EXPECTED_ORDER, "protocol order drift")
    require(status["paper_order"] == EXPECTED_ORDER, "status order drift")
    require(status["next_descending_cursor"] == 9, "next cursor must be 9")
    papers = status["papers"]
    require([p["paper"] for p in papers] == EXPECTED_ORDER, "paper records not descending")
    require(len({p["paper"] for p in papers}) == 5, "duplicate paper record")
    require(all(p["packet_authority_delta"] == "NONE" for p in papers), "authority inflation")
    require(protocol["packet_authority"]["scientific_authority_delta"] == "NONE", "packet authority drift")
    require(result["scientific_authority_delta"] == "NONE", "result authority drift")
    checks.append("descending order 14 through 10 and zero authority delta")

    rules = protocol["recovery_rules"]
    for key in (
        "path_by_path_only", "whole_branch_merge_forbidden",
        "package_bytes_may_not_cross_source_tree",
        "status_only_closeout_artifacts_may_not_be_filed",
        "cannot_check_may_not_be_converted_without_native_authority",
        "adverse_history_must_remain_visible", "post_outcome_rescue_forbidden",
    ):
        require(rules[key] is True, f"recovery rule disabled: {key}")
    require(rules["manuscript_edits_in_this_packet"] is False, "manuscript edits claimed")
    require(rules["same_research_team_is_external_investigator"] is False, "same team promoted")
    require(manifest["whole_branch_merge_performed"] is False, "whole branch merge performed")
    require(manifest["whole_branch_merge_allowed"] is False, "whole branch merge allowed")
    require(manifest["manuscript_or_package_bytes_imported"] is False, "stale package imported")
    require(divergence["whole_branch_merge_allowed"] is False, "divergence allows wholesale merge")
    checks.append("pathwise-only, no stale package or post-outcome rescue")

    seen_nonmain: set[str] = set()
    for artifact in manifest["artifacts"]:
        require(len(artifact["blob_sha"]) == 40, f"bad blob sha: {artifact['path']}")
        require(len(artifact["branch_head"]) == 40, f"bad head: {artifact['path']}")
        if artifact["branch"] == "main":
            require(artifact["branch_head"] == LIVE_MAIN, "main artifact head drift")
            require(artifact["present_on_live_main"] is True, "main artifact marked absent")
            require(artifact["mode"].startswith("ALREADY_CANONICAL"), "main artifact misclassified")
        else:
            branch = artifact["branch"]
            require(branch in EXPECTED_HEADS, f"unregistered branch: {branch}")
            require(artifact["branch_head"] == EXPECTED_HEADS[branch], f"head drift: {branch}")
            seen_nonmain.add(branch)
    require(seen_nonmain == set(EXPECTED_HEADS), "not all source heads bound")
    require(len(manifest["artifacts"]) == 16, "artifact count drift")
    checks.append("exact source heads and key artifact blobs")

    rec = {row["paper"]: row for row in manifest["recoverable_directories"]}
    require(set(rec) == set(EXPECTED_RECOVERABLE), "recoverable paper set drift")
    for paper, (branch, count) in EXPECTED_RECOVERABLE.items():
        require(rec[paper]["branch"] == branch, f"ORION-{paper} recovery branch drift")
        require(rec[paper]["head"] == EXPECTED_HEADS[branch], f"ORION-{paper} head drift")
        require(rec[paper]["file_count_from_compare"] == count, f"ORION-{paper} file count drift")
        require(rec[paper]["path"].startswith(f"papers/orion-{paper:02d}-"), f"ORION-{paper} path drift")
    checks.append("three additive pathwise recoveries only")

    direct = recon["direct_path_checks"]
    require(direct["orion14_promotion_reduct_result_present"] is False, "ORION-14 absent path promoted")
    require(direct["orion13_separator_result_present"] is False, "ORION-13 absent path promoted")
    require(direct["orion10_explanation_gap_result_present"] is False, "ORION-10 absent path promoted")
    for key in (
        "orion11_primary_result_present",
        "orion11_original_replication_present",
        "orion11_parameterised_replication_present",
        "orion11_anchor_repair_present",
        "orion11_costed_ordering_present",
    ):
        require(direct[key] is True, f"live-main ORION-11 evidence lost: {key}")
    require(direct["orion12_current_revision_closeout_package_present"] is False, "ORION-12 stale package promoted")
    checks.append("direct live-main presence and absence classification")

    by_paper = {p["paper"]: p for p in papers}

    p14 = by_paper[14]
    r14 = p14["optional_reduct"]
    require(r14["terminal"] == "PARTIAL__SCOPE_GATED__COMPUTED_ON_THE_COMMITTED_CORPUS", "ORION-14 terminal drift")
    require(r14["requested_400_case_table_committed"] is False, "ORION-14 400-case table fabricated")
    require(r14["actual_case_count"] == 10 and r14["promotable_cases"] == 3, "ORION-14 bench drift")
    require(r14["feature_count"] == 17 and r14["k_star_ternary"] == 3, "ORION-14 reduct drift")
    require(r14["binary_encoding_admits_no_sufficient_set"] is True, "ORION-14 null collapse hidden")
    require(r14["core"] == ["known_composition", "prior_art_found"], "ORION-14 core drift")
    require(r14["submission_blocker"] is False, "optional ORION-14 lane blocks submission")
    checks.append("ORION-14 partial reduct and absent 400-case table")

    h14 = recon["package_hash_boundaries"]["orion14"]
    require(h14["source_bytes_match"] is False, "ORION-14 source mismatch erased")
    require(h14["old_filing_bytes_valid_for_live_main"] is False, "ORION-14 stale PDF promoted")
    require(h14["live_main_manuscript_pdf_sha256"] != h14["closeout_manuscript_pdf_sha256"], "ORION-14 PDFs unexpectedly equal")
    require(p14["closeout"]["live_main_filing_ready_from_old_bytes"] is False, "ORION-14 filing falsely ready")
    checks.append("ORION-14 stale filing-byte rejection")

    p13 = by_paper[13]["separator"]
    require(p13["derivation_cases"] == 32 and p13["challenge_cases"] == 32, "ORION-13 set size drift")
    require(p13["shared_case_ids"] == 0, "ORION-13 holdout overlap")
    require(p13["k_star"] == 1 and p13["unique_reduct"] == ["polarity"], "ORION-13 reduct drift")
    require(p13["challenge_collisions"] == 0, "ORION-13 collisions drift")
    require(p13["permutation_trials"] == 20000 and p13["permutation_hits"] == 0, "ORION-13 null drift")
    require(p13["flat_false_merges"] == 6 and p13["flat_false_merge_rate"] == 0.1875, "ORION-13 headline drift")
    require(p13["full_coordinate_necessity_determined"] is False, "ORION-13 necessity falsely solved")
    require(p13["other_coordinates_proved_unnecessary"] is False, "ORION-13 coordinates falsely discarded")
    checks.append("ORION-13 polarity result without necessity inflation")

    p12 = by_paper[12]
    e12 = p12["external_gate"]
    require(e12["recall_difference_orion_minus_strongest"] == -0.0177, "ORION-12 recall drift")
    require(e12["recall_bootstrap_ci95"] == [-0.0273, -0.0091], "ORION-12 recall interval drift")
    require(e12["recall_gate_passed"] is False, "ORION-12 recall gate rescued")
    require(e12["read_cost_ratio"] == 2.8 and e12["cost_gate_passed"] is False, "ORION-12 cost gate rescued")
    require(e12["ndcg10_difference"] == 0.1488 and e12["topics_ahead_ndcg10"] == 42, "ORION-12 nDCG drift")
    require(e12["ndcg_can_rescue_primary_gate"] is False, "ORION-12 nDCG falsely compensatory")
    require(e12["unavailable_routes"] == 2 and e12["total_routes"] == 5, "ORION-12 route state drift")
    h12 = recon["package_hash_boundaries"]["orion12"]
    require(h12["source_bytes_match"] is False, "ORION-12 package mismatch erased")
    require(h12["old_filing_bytes_valid_for_live_main"] is False, "ORION-12 stale package promoted")
    require(p12["package"]["old_filing_bytes_valid_for_live_main"] is False, "ORION-12 filing falsely ready")
    checks.append("ORION-12 adverse recall/cost and stale package rejection")

    p11 = by_paper[11]
    f11 = p11["faithful_comparator"]
    require(p11["integration_terminal"] == "ALREADY_CANONICAL_ON_LIVE_MAIN__NO_RECOVERY_NEEDED", "ORION-11 duplicate recovery")
    require(f11["primary_anchor_gate_passed"] is True, "ORION-11 primary anchor drift")
    require(f11["primary_n_worlds"] == 2882 and f11["primary_n_hidden_shift"] == 480, "ORION-11 denominator drift")
    require(f11["primary_orion_joint_success"] == 1.0, "ORION-11 ORION score drift")
    require(f11["primary_activevoi_joint_success"] == 1.0, "ORION-11 comparator score drift")
    require(f11["primary_activevoi_forbidden_rate"] == 0.0, "ORION-11 comparator safety drift")
    require(f11["primary_terminal"] == "H_R4_FALSIFIED__FAITHFUL_COMPARATOR_MATCHES_ORION", "ORION-11 primary terminal drift")
    require(f11["original_replication_terminal"] == "INSTRUMENT_FAULT__ANCHOR_REPRODUCTION_FAILED__NO_CLAIM_READ", "ORION-11 adverse history erased")
    require(f11["original_replication_history_retained"] is True, "ORION-11 original CANNOT_CHECK hidden")
    require(f11["parameterised_replication_anchor_gate_passed"] is True, "ORION-11 repaired anchor drift")
    require(f11["parameterised_replication_terminal"] == "H_R4_FALSIFIED__FAITHFUL_COMPARATOR_MATCHES_ORION", "ORION-11 replication terminal drift")
    require(f11["repair_changed_scientific_thresholds"] is False, "ORION-11 repair changed science")
    require(f11["stage1_executes_new_arms"] is False, "ORION-11 stage 1 leaks outcomes")
    checks.append("ORION-11 canonical falsification and instrument-only repair")

    c11 = p11["costed_ordering"]
    require(c11["terminal"] == "H_FALSIFIED__PC_BASELINE_MATCHES_OR_BEATS_ORION", "ORION-11 costed terminal drift")
    require(c11["anchor_gate_passed"] is True, "ORION-11 costed anchor drift")
    require(c11["bootstrap_seed_terminal_stable"] is True, "ORION-11 seed instability hidden")
    require(c11["g3_cost_ratio_passed"] is False, "ORION-11 cost ratio falsely passed")
    require(c11["g4_dp_gap_passed"] is False, "ORION-11 DP gap falsely passed")
    require(c11["donor_baseline_gate_passed"] is False, "ORION-11 donor gate falsely passed")
    checks.append("ORION-11 costed-ordering falsification retained")

    p10 = by_paper[10]["explanation_gap"]
    require(p10["structures_checked"] == 21501, "ORION-10 structure count drift")
    require(p10["exact_explanation_iff_fibre_constancy"] is True, "ORION-10 theorem drift")
    require(p10["mixed_fibre_blocks_every_function_of_psi"] is True, "ORION-10 mixed-fibre theorem drift")
    require(p10["expression_size_can_rescue_mixed_fibre"] is False, "ORION-10 size rescue fabricated")
    require(p10["negative_controls_passed"] == 3 and p10["negative_controls_total"] == 3, "ORION-10 controls drift")
    require(p10["counts_reproduced"] == {
        "fifth_configuration_confirmed": 0,
        "fourth_configuration_witnesses": 64,
        "instances_evaluated": 740,
        "rows_closed_by_hybrid_family": 10481,
    }, "ORION-10 manuscript counts drift")
    require(p10["all_n_theorem_authority"] is False, "ORION-10 all-n authority inflated")
    require(p10["btripleprime_found"] is False, "ORION-10 b-triple-prime fabricated")
    require(p10["physical_quantum_advantage_claim"] is False, "ORION-10 physical advantage fabricated")
    require(p10["novelty_authority"] is False, "ORION-10 novelty authority fabricated")
    checks.append("ORION-10 exact theorem without all-n or novelty inflation")

    adverse_ids = {row["id"] for row in adverse}
    require(adverse_ids == REQUIRED_ADVERSE, "adverse/CANNOT_CHECK ledger drift")
    require(all(row["retained"] is True for row in adverse), "adverse row not retained")
    require(result["status"] == "PASS", "result status drift")
    require(result["paper_count"] == 5, "result paper count drift")
    require(result["chain_paper_count_after_commit"] == 16, "chain count drift")
    require(result["chain_papers_after_commit"] == list(range(25, 9, -1)), "chain coverage drift")
    require(result["new_empirical_outcomes_generated"] == 0, "new outcomes fabricated")
    require(result["manuscripts_modified"] == 0, "manuscript edit fabricated")
    require(result["package_filing_bytes_imported"] == 0, "filing bytes imported")
    require(result["whole_branches_merged"] == 0, "whole branch merge fabricated")
    checks.append("adverse ledger and majority-chain accounting")

    return checks

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=Path(__file__).resolve().parent)
    parser.add_argument("--no-checksums", action="store_true")
    args = parser.parse_args()
    try:
        checks = validate(Path(args.root), check_checksums=not args.no_checksums)
    except ValidationError as exc:
        print(f"FAIL: {exc}")
        return 1
    print(json.dumps({
        "status": "PASS",
        "invariant_groups": len(checks),
        "checks": checks,
    }, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
