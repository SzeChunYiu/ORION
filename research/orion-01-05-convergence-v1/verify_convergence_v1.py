#!/usr/bin/env python3
"""Fail-closed verifier for the ORION-01--05 convergence evidence layer."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "DONOR_MANIFEST_V1.json"
STATUS = HERE / "SCIENCE_STATUS_V1.json"

CONVERGENCE_TERMINAL = (
    "ORION_01_05_CONVERGENCE_V1_EVIDENCE_BOUND__SCIENCE_CLOSURE_OPEN__"
    "SUBMISSION_NOT_YET_AUTHORIZED"
)
R30_TERMINAL = "R30_NOT_MATERIALIZED__CUSTODY_AND_FINAL_BINDING_FAILED"
R18_TERMINAL = "FIBERGUARD_R18_NO_PAIRED_ROUTE_VALUE"
R19_TERMINAL = "FIBERGUARD_JOINT_ROUTE_R19_REPLACEMENT_PASS"
BNSL_NULL = "C_R20_BNSL_ADAPTIVE_NULL__FREE_STATIC_REPRESENTATION_ALREADY_VBS"
BNSL_QUARANTINE = "QUARANTINED_OVERLAPPING_MATERIAL_AND_NULL_PREDICATES_AT_ZERO"
NQ_FAILURE = (
    "NQ_CRB_FULL_REPLAY_JOB_3544056_FAILED_CENSUS_RECEIPT_SERIALIZATION__"
    "D2_D3_AUTHORITY_CANNOT_CHECK"
)

ALLOWED_EXACT_PATHS = {
    ".github/workflows/orion-01-05-convergence-v1.yml",
    "papers/README.md",
}
ALLOWED_ADDITIVE_PREFIXES = (
    "papers/orion-01-certificate-realization/evidence/convergence-v1/",
    "papers/orion-02-fiberguard-finite-fibre/extensions/r11/",
    "papers/orion-02-fiberguard-finite-fibre/extensions/r14/",
    "papers/orion-02-fiberguard-finite-fibre/extensions/r15/",
    "papers/orion-02-fiberguard-finite-fibre/extensions/r16/",
    "papers/orion-02-fiberguard-finite-fibre/extensions/r17/",
    "papers/orion-02-fiberguard-finite-fibre/extensions/r18-relative/",
    "papers/orion-02-fiberguard-finite-fibre/extensions/r18/",
    "papers/orion-02-fiberguard-finite-fibre/extensions/r19/",
    "papers/orion-02-fiberguard-finite-fibre/extensions/r20/",
    "papers/orion-03-typed-merge-falsification/evidence/convergence-v1/",
    "papers/orion-04-rooted-completion-certificates/evidence/convergence-v1/",
    "papers/orion-04-rooted-completion-certificates/evidence/crb-full-replay/"
    "post-execution/job-3544056/",
    "papers/orion-05-tare-expressivity/evidence/convergence-v1/",
    "research/orion-01-05-convergence-v1/",
)


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def git(repo: Path, *args: str, binary: bool = False) -> str | bytes:
    return subprocess.check_output(
        ["git", *args], cwd=repo, text=not binary
    )


def git_object_exists(repo: Path, spec: str) -> bool:
    return (
        subprocess.run(
            ["git", "cat-file", "-e", spec],
            cwd=repo,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        == 0
    )


def validate_entry(repo: Path, entry: dict[str, Any]) -> None:
    destination = repo / entry["destination"]
    require(destination.is_file(), f"missing destination: {entry['destination']}")
    payload = destination.read_bytes()
    require(len(payload) == entry["bytes"], f"byte count drift: {entry['destination']}")
    require(
        sha256_bytes(payload) == entry["sha256"],
        f"SHA-256 drift: {entry['destination']}",
    )

    source = entry["source"]
    if source["kind"] == "git":
        # The Git blob OID is a content hash, so it remains verifiable after a
        # historical donor branch is closed and its commit is no longer fetched
        # into a shallow/restricted checkout.
        destination_blob = git(repo, "hash-object", entry["destination"])
        require(
            str(destination_blob).strip() == source["blob"],
            f"donor blob drift: {entry['destination']}",
        )
        source_spec = f"{source['commit']}:{source['path']}"
        if git_object_exists(repo, source_spec):
            source_payload = git(
                repo, "show", source_spec, binary=True
            )
            require(source_payload == payload, f"donor byte drift: {entry['destination']}")
        else:
            require(
                source.get("object_required_in_checkout") is False,
                f"required donor object unavailable: {entry['destination']}",
            )
    elif source["kind"] == "github_actions_artifact":
        require(source["run"] > 0 and source["artifact_id"] > 0, "artifact identity absent")
        require(bool(source.get("artifact_name")), "artifact name absent")
        require(
            len(source.get("artifact_zip_sha256", "")) == 64,
            "artifact ZIP SHA-256 absent",
        )
        require(
            bool(source.get("member"))
            and source.get("member_bytes") == entry["bytes"]
            and source.get("member_sha256") == entry["sha256"],
            "artifact member binding absent or inconsistent",
        )
    elif source["kind"] == "convergence_generated":
        require(source["generator"] == "ORION-01-05 convergence V1", "bad generator")
    else:
        raise AssertionError(f"unknown source kind: {source['kind']}")


def validate_manifest(repo: Path) -> dict[str, Any]:
    manifest = load(repo / MANIFEST.relative_to(ROOT))
    require(
        manifest["schema"] == "ORION.ORION0105.ScienceConvergenceDonorManifest.v1",
        "manifest schema",
    )
    require(manifest["terminal"] == CONVERGENCE_TERMINAL, "manifest terminal")
    destinations = [row["destination"] for row in manifest["files"]]
    require(len(destinations) == len(set(destinations)), "duplicate manifest destinations")
    manifest_path = MANIFEST.relative_to(ROOT).as_posix()
    self_binding = manifest["manifest_self_binding"]
    require(self_binding.get("path") == manifest_path, "manifest self-binding path")
    require(
        self_binding.get("excluded_from_own_hash_list") is True
        and self_binding.get("reason") == "SELF_REFERENTIAL_HASH_IS_NOT_WELL_DEFINED",
        "manifest self-binding rule",
    )
    require(manifest_path not in destinations, "manifest self listed as ordinary file")
    expected_paths = set(manifest["expected_changed_paths"])
    require(
        set(destinations) | {manifest_path} == expected_paths,
        "manifest destination coverage mismatch",
    )
    baseline = manifest["baseline"]
    observed_baseline_tree = str(
        git(repo, "rev-parse", f"{baseline['commit']}^{{tree}}")
    ).strip()
    require(observed_baseline_tree == baseline["tree"], "baseline tree mismatch")

    artifact_member_mappings: set[tuple[int, int, str]] = set()
    for row in manifest["files"]:
        source = row["source"]
        if source["kind"] == "github_actions_artifact":
            mapping = (source["run"], source["artifact_id"], source["member"])
            require(
                mapping not in artifact_member_mappings,
                "duplicate artifact member mapping",
            )
            artifact_member_mappings.add(mapping)
    for row in manifest["files"]:
        validate_entry(repo, row)

    for row in manifest["bound_existing_files"]:
        path = row["path"]
        current = repo / path
        require(current.is_file(), f"missing existing binding: {path}")
        require(current.stat().st_size == row["bytes"], f"existing byte drift: {path}")
        require(sha256(current) == row["sha256"], f"existing SHA drift: {path}")
        base_blob = str(git(repo, "rev-parse", f"{manifest['baseline']['commit']}:{path}")).strip()
        head_blob = str(git(repo, "rev-parse", f"HEAD:{path}")).strip()
        require(base_blob == row["blob"] == head_blob, f"existing blob drift: {path}")
    return manifest


def json_pointer(document: Any, pointer: str) -> Any:
    """Resolve the small RFC 6901 subset used by exact-terminal bindings."""
    require(pointer.startswith("/"), f"invalid JSON pointer: {pointer}")
    current = document
    for raw_token in pointer[1:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict):
            require(token in current, f"JSON pointer key absent: {pointer}")
            current = current[token]
        elif isinstance(current, list):
            require(token.isdigit(), f"JSON pointer index invalid: {pointer}")
            index = int(token)
            require(index < len(current), f"JSON pointer index absent: {pointer}")
            current = current[index]
        else:
            raise AssertionError(f"JSON pointer traverses scalar: {pointer}")
    return current


def validate_preserved_exact_terminals(repo: Path, status: dict[str, Any]) -> None:
    allowed_kinds = {
        "RAW_SCIENCE_TERMINAL",
        "AUDIT_DISPOSITION",
        "AUTHORITY_VERDICT",
        "COMPOSITE_INTERPRETATION",
    }
    noncontrolling_dispositions = {
        "PRESERVED_NONCONTROLLING_KNOWN_PREDICATE_DEFECT",
        "RETRACTED_UNSUPPORTED_EXECUTION_IDENTITY",
        "QUARANTINED_OVERLAPPING_MATERIAL_AND_NULL_PREDICATES_AT_ZERO",
    }

    for paper_id in (f"ORION-{index:02d}" for index in range(1, 6)):
        evidence = status["papers"][paper_id].get("evidence_status", {})
        summary = evidence.get("convergence_summary", {})
        require(
            summary.get("label", "").startswith(f"{paper_id}_")
            and summary.get("kind") == "CONVERGENCE_GENERATED_SUMMARY"
            and summary.get("is_exact_donor_terminal") is False,
            f"{paper_id} convergence summary label",
        )
        records = evidence.get("preserved_records", [])
        require(records, f"{paper_id} exact evidence records absent")
        ids = [record["id"] for record in records]
        require(len(ids) == len(set(ids)), f"{paper_id} duplicate evidence record IDs")
        require(
            set(summary.get("derived_from", [])) <= set(ids),
            f"{paper_id} summary references unknown record",
        )

        for record in records:
            require(record["record_kind"] in allowed_kinds, "evidence record kind")
            source = record["source"]
            canonical = repo / source["canonical_copy"]
            require(canonical.is_file(), f"evidence canonical copy absent: {canonical}")
            require(
                json_pointer(load(canonical), source["json_pointer"])
                == record["value"],
                f"evidence record pointer mismatch: {record['id']}",
            )

            if source["kind"] == "git_donor_canonical_copy":
                require(
                    set(source) >= {"commit", "path", "blob"},
                    f"evidence donor source incomplete: {record['id']}",
                )
                canonical_blob = str(
                    git(repo, "hash-object", source["canonical_copy"])
                ).strip()
                require(
                    canonical_blob == source["blob"],
                    f"evidence canonical blob drift: {record['id']}",
                )
                source_spec = f"{source['commit']}:{source['path']}"
                if git_object_exists(repo, source_spec):
                    require(
                        str(git(repo, "rev-parse", source_spec)).strip()
                        == source["blob"],
                        f"evidence donor source drift: {record['id']}",
                    )
                    require(
                        git(repo, "show", source_spec, binary=True)
                        == canonical.read_bytes(),
                        f"evidence donor byte drift: {record['id']}",
                    )
            elif source["kind"] == "canonical_convergence_file":
                require(
                    sha256(canonical) == source["sha256"],
                    f"evidence convergence SHA drift: {record['id']}",
                )
            else:
                raise AssertionError(f"unknown evidence source kind: {source['kind']}")

            if record["disposition"] in noncontrolling_dispositions:
                require(
                    record["controls_current_science_status"] is False,
                    f"noncontrolling evidence promoted: {record['id']}",
                )

        for candidate in evidence.get("pending_candidates", []):
            require(candidate.get("emitted_terminal") is None, "candidate terminal promoted")


def validate_science(repo: Path) -> None:
    status = load(repo / STATUS.relative_to(ROOT))
    require(status["terminal"] == CONVERGENCE_TERMINAL, "status terminal")
    require(set(status["papers"]) == {f"ORION-{i:02d}" for i in range(1, 6)}, "paper IDs")
    require(all(not row["science_closed"] for row in status["readiness"].values()), "science closure")
    require(
        all(not row["top_tier_submission_ready"] for row in status["readiness"].values()),
        "top-tier readiness",
    )
    require(
        all(not row["specialist_submission_ready"] for row in status["readiness"].values()),
        "specialist readiness",
    )
    require(not any(status["global_authority"].values()), "global authority promoted")
    validate_preserved_exact_terminals(repo, status)
    require(
        status["current_main_baseline"]["commit"]
        == "b1e65d4445a9b2ef5aa44f7adc2838f968f84ff1",
        "current-main baseline drift",
    )

    aliases = (repo / "papers/PAPER_ALIASES.md").read_text(encoding="utf-8")
    for old, new in (
        ("NQ", "ORION-04"),
        ("theory-A", "ORION-01"),
        ("theory-B", "ORION-01"),
        ("theory-C", "ORION-02"),
        ("theory-D", "ORION-03"),
        ("Q1", "ORION-05"),
    ):
        require(f"old: {old}" in aliases and f"new: {new}" in aliases, f"alias {old}")
    paper_readme = (repo / "papers/README.md").read_text(encoding="utf-8")
    require("### ORION-05 theorem status" in paper_readme, "TARE heading identity")
    require("pre-review for ORION-05" in paper_readme, "TARE review identity")
    require("### ORION-01 theorem status" not in paper_readme, "stale TARE heading")

    d = status["papers"]["ORION-03"]
    d_records = {
        record["value"]: record
        for record in d["evidence_status"]["preserved_records"]
    }
    require(
        "TYPED_AUTHORITY_FIRST_MIXING_R12_PASS" in d_records,
        "ORION-03 raw theorem terminal erased",
    )
    require(
        d_records["D_PR1466_THEOREM_AUTHORITY_NOT_ESTABLISHED"]["disposition"]
        == "PRESERVED_NONCONTROLLING_KNOWN_PREDICATE_DEFECT",
        "ORION-03 conflicting wrapper audit disposition",
    )
    require(
        d["authority"]["bounded_internal_first_mixing_theorem"] is True
        and d["authority"]["external_domain_validation_established"] is False,
        "ORION-03 authority boundary drift",
    )
    audit_dispositions = load(
        repo / "research/orion-01-05-convergence-v1/AUDIT_DISPOSITIONS_V1.json"
    )
    require(
        audit_dispositions["known_conflicts"][0]["disposition"]
        == "KNOWN_PREDICATE_FALSE_NEGATIVE",
        "ORION-03 audit defect custody",
    )

    croot = repo / "papers/orion-02-fiberguard-finite-fibre"
    r18root = croot / "extensions/r18"
    r18 = load(r18root / "FIBERGUARD_PAIRED_ROUTE_R18_RECOVERY_RESULTS.json")
    r18_custody = load(r18root / "R18_RECOVERY_CUSTODY_V2.json")
    require(r18["terminal"] == R18_TERMINAL, "R18 terminal")
    require(r18["development"]["candidate_count"] == 99, "R18 candidate denominator")
    require(r18["development"]["feasible_candidate_count"] == 0, "R18 feasible denominator")
    require(
        all(r18[panel]["selected_route"]["metrics"]["route_change_coverage"] == 0.0
            for panel in ("development", "validation", "test")),
        "R18 zero route coverage",
    )
    require(r18["authority"]["external_independence"] is False, "R18 external ceiling")
    require(r18["authority"]["grants_journal_authority"] is False, "R18 journal ceiling")
    require(r18_custody["terminal"] == R18_TERMINAL, "R18 custody terminal")
    require(
        r18_custody["former_positive_terminal"]["disposition"]
        == "RETRACTED_UNSUPPORTED_EXECUTION_IDENTITY",
        "R18 positive retraction",
    )
    r18_registered = r18_custody["artifact"]["files"][
        "FIBERGUARD_PAIRED_ROUTE_R18_RECOVERY_RESULTS.json"
    ]
    require(r18_registered["sha256"] == sha256(r18root / "FIBERGUARD_PAIRED_ROUTE_R18_RECOVERY_RESULTS.json"), "R18 custody SHA")

    r19root = croot / "extensions/r19"
    r19 = load(r19root / "JOINT_ROUTE_R19_RESULTS.json")
    require(r19["terminal"] == R19_TERMINAL, "R19 terminal")
    require(r19["invalid_R19_pairing_counterexample"]["original_randomized_value"] == "35", "R19 35")
    require(r19["invalid_R19_pairing_counterexample"]["shortcut_randomized_value"] == "70", "R19 70")
    require(r19["same_marginals_different_joint_system"]["full_pair_randomized_value"] == "0", "R19 0")
    require(r19["same_marginals_different_joint_system"]["diagonal_pair_randomized_value"] == "50", "R19 50")
    require(r19["authority"]["paired_ASlib_experiment_executed"] is False, "R19 application ceiling")
    require(r19["authority"]["grants_journal_authority"] is False, "R19 journal ceiling")

    r20root = croot / "extensions/r20"
    bnsl = load(r20root / "FIBERGUARD_BNSL_ADAPTIVE_R20_RESULTS.json")
    bnsl_custody = load(r20root / "BNSL_R20_CUSTODY_V1.json")
    require(bnsl["terminal"] == "C_R20_BNSL_ADAPTIVE_MATERIAL_VALUE", "BNSL raw terminal")
    require(bnsl["corpus"]["instance_count"] == 1179, "BNSL denominator")
    require(bnsl["best_static"]["fibre_count"] == 1179, "BNSL fibre count")
    require(bnsl["best_static"]["maximum_fibre_size"] == 1, "BNSL singleton fibres")
    require(bnsl["best_static"]["robust_total_excess_cost"] == 0.0, "BNSL static zero")
    require(bnsl["adaptive_one_step"]["robust_total_excess_cost"] == 0.0, "BNSL adaptive zero")
    require(bnsl_custody["raw_terminal_disposition"] == BNSL_QUARANTINE, "BNSL quarantine")
    require(bnsl_custody["additive_interpretation"] == BNSL_NULL, "BNSL null interpretation")
    require(bnsl_custody["authority"]["adaptive_superiority"] is False, "BNSL superiority ceiling")

    results = croot / "experiments/results"
    cnbr = load(results / "CERTIFIED_NEIGHBORHOOD_RESULT_V1.json")
    cnbr2 = load(results / "CERTIFIED_NEIGHBORHOOD_CONFORMAL_RECOVERY_RESULT_V2.json")
    cnbr2_custody = load(results / "CERTIFIED_NEIGHBORHOOD_CONFORMAL_RECOVERY_CUSTODY_V2.json")
    require(cnbr["overall_verdict"] == "CERTIFICATE_INVALID", "C-NBR terminal")
    require(cnbr2["overall_verdict"] == "VALID_WITHOUT_COVERAGE_OR_VALUE", "C-NBR2 terminal")
    require(cnbr2_custody["terminal"] == "VALID_WITHOUT_COVERAGE_OR_VALUE", "C-NBR2 custody")
    require(cnbr2_custody["authority"]["production_value"] is False, "C-NBR2 value ceiling")
    require(cnbr2_custody["authority"]["former_V1_result"] == "QUARANTINED_IMPLEMENTATION_DEVIATION", "C-NBR2 quarantine")

    nqroot = repo / "papers/orion-04-rooted-completion-certificates/evidence/crb-full-replay/post-execution/job-3544056"
    nq = load(nqroot / "POST_EXECUTION_FAILURE_RECEIPT.json")
    require(nq["terminal"] == NQ_FAILURE, "ORION-04 failure terminal")
    require(nq["execution"]["job_id"] == 3544056, "ORION-04 job")
    require(nq["execution"]["elapsed_seconds"] == 29322, "ORION-04 elapsed")
    require(nq["failure"]["observed_exception"] == "TypeError: value is not canonical JSON: float", "ORION-04 exception")
    require(nq["phase_status"]["phase_2_per_record_sat_execution"] == "NOT_RUN", "ORION-04 SAT ceiling")
    require(nq["phase_status"]["phase_3_external_drup_verification"] == "NOT_RUN", "ORION-04 DRUP ceiling")
    require(nq["authority"]["d2_numerical_replay_authority"] is False, "ORION-04 D2 ceiling")
    require(nq["authority"]["d3_numerical_replay_authority"] is False, "ORION-04 D3 ceiling")
    require(nq["supersession"]["d4_rounds_consumed"] == 0, "ORION-04 D4 rounds")

    r30runs = load(repo / "research/orion-01-05-convergence-v1/R30_FAILURE_RUNS_V1.json")
    r30 = load(repo / "research/orion-01-05-convergence-v1/R30_FAILURE_CUSTODY_V1.json")
    require(r30runs["disposition"] == R30_TERMINAL, "R30 run disposition")
    require(len(r30runs["r30_runs"]) == 6, "R30 run denominator")
    require(all(row["conclusion"] == "failure" for row in r30runs["r30_runs"]), "R30 failures")
    require(33048978721 not in {row["run"] for row in r30runs["r30_runs"]}, "R18 mixed into R30")
    require(r30["terminal"] == R30_TERMINAL, "R30 custody terminal")
    require(r30["related_non_r30_custody_failure"]["run"] == 33048978721, "R18 custody separation")
    require(r30["live_repository_observations"]["intended_clean_branch_exists"] is False, "R30 branch")
    require(r30["live_repository_observations"]["final_outputs_present_on_current_main"] is False, "R30 outputs")

    supersession = load(
        repo / "research/orion-01-05-convergence-v1/SUPERSESSION_PLAN_V1.json"
    )
    require(
        supersession["global_rule"]
        == "CLOSE_ONLY_AFTER_SUCCESSOR_MERGE_AND_MERGED_MAIN_VERIFICATION",
        "premature supersession rule",
    )
    require(supersession["protected_task3_touched"] is False, "supersession touches Task-3")


def diff_records(repo: Path, base: str) -> list[tuple[str, str]]:
    raw = str(git(repo, "diff", "--name-status", "-M", f"{base}..HEAD"))
    records: list[tuple[str, str]] = []
    for line in raw.splitlines():
        fields = line.split("\t")
        require(len(fields) == 2, f"rename/copy/delete not allowed: {line}")
        records.append((fields[0], fields[1]))
    return records


def validate_changed_paths(records: list[tuple[str, str]], expected: set[str]) -> None:
    actual: set[str] = set()
    for status, path in records:
        require(status in {"A", "M"}, f"destructive diff status: {status} {path}")
        require(path not in actual, f"duplicate changed path: {path}")
        require(
            path in ALLOWED_EXACT_PATHS or path.startswith(ALLOWED_ADDITIVE_PREFIXES),
            f"path outside strict convergence allowlist: {path}",
        )
        actual.add(path)
        if path == "papers/README.md":
            require(status == "M", "papers README must be the sole modified existing file")
        else:
            require(status == "A", f"non-additive convergence path: {path}")
    require(actual == expected, f"changed-path mismatch: missing={sorted(expected-actual)} extra={sorted(actual-expected)}")


def validate_diff(repo: Path, manifest: dict[str, Any]) -> None:
    base = manifest["baseline"]["commit"]
    expected = set(manifest["expected_changed_paths"])
    validate_changed_paths(diff_records(repo, base), expected)

    forbidden_prefixes = tuple(manifest["protected_path_policy"]["forbidden_prefixes"])
    require(not any(path.startswith(forbidden_prefixes) for path in expected), "protected path in allowlist")
    for row in manifest["protected_blob_guards"]:
        base_blob = str(git(repo, "rev-parse", f"{base}:{row['path']}")).strip()
        head_blob = str(git(repo, "rev-parse", f"HEAD:{row['path']}")).strip()
        require(base_blob == row["blob"] == head_blob, f"protected blob changed: {row['path']}")


def validate_pr_base(repo: Path, manifest: dict[str, Any], pr_base: str) -> None:
    observed_tree = str(git(repo, "rev-parse", f"{pr_base}^{{tree}}")).strip()
    require(observed_tree == manifest["baseline"]["tree"], "PR base tree mismatch")


def verify(repo: Path, check_diff: bool, pr_base: str | None = None) -> None:
    manifest_path = repo / MANIFEST.relative_to(ROOT)
    raw_manifest = load(manifest_path)
    if check_diff:
        require(pr_base is not None, "PR base is required for diff verification")
        validate_pr_base(repo, raw_manifest, pr_base)
    manifest = validate_manifest(repo)
    validate_science(repo)
    if check_diff:
        validate_diff(repo, manifest)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--check-diff", action="store_true")
    parser.add_argument("--pr-base")
    args = parser.parse_args()
    verify(args.repo.resolve(), args.check_diff, args.pr_base)
    print(CONVERGENCE_TERMINAL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
