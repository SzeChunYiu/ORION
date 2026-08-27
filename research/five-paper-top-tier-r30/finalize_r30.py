#!/usr/bin/env python3
"""Generate the non-self-referential R30 internal programme release receipts.

The script does not execute scientific solvers. It consumes already executed,
content-bound receipts from independent workflow steps, verifies their exact
terminals and authority ceilings, binds the frozen source subject, and emits
one internal-release packet. No external, novelty, rights, journal, or
submission authority is synthesized.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

ORION_ROOT = Path("papers/orion-02-fiberguard-finite-fibre")
PROGRAMME_ROOT = Path("research/five-paper-top-tier-r20")


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text())


def git_blob(repo: Path, subject: str, path: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"{subject}:{path.as_posix()}"],
        cwd=repo,
        text=True,
    ).strip()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate(
    repo: Path,
    subject: str,
    r18: Any,
    cnbr: Any,
    finite: Any,
    rust: Any,
    rights: Any,
    retraction: Any,
    audits: dict[str, Any],
    pdf: Path,
) -> dict[str, Any]:
    orion = repo / ORION_ROOT
    ledger = load(orion / "CLAIM_LEDGER_R20.json")
    evidence = load(orion / "EVIDENCE_MANIFEST_R20.json")
    journal = load(orion / "JOURNAL_GATE_R20.json")
    r18_custody = load(orion / "extensions/r18/R18_RECOVERY_CUSTODY.json")
    r19 = load(orion / "extensions/r19/JOINT_ROUTE_R19_RESULTS.json")
    fileset = load(orion / "RELEASE_FILESET_R20.json")
    manuscript = (orion / "MANUSCRIPT_R20.tex").read_text()
    prior = (orion / "PRIOR_ART_MATRIX_R20.md").read_text()

    require(ledger["schema"] == "ORION.ORION02.ClaimLedger.R20.v1", "claim ledger schema")
    require(len(ledger["claims"]) == 10, "claim denominator")
    require(len({row["claim_id"] for row in ledger["claims"]}) == 10, "claim IDs")
    require(
        ledger["global_authority"]
        == {
            "external_independence": "CANNOT_CHECK",
            "journal_authority": False,
            "novelty": "CANNOT_CHECK",
            "production_value": False,
            "submission_ready": False,
        },
        "claim authority ceiling",
    )
    require(evidence["schema"] == "ORION.ORION02.EvidenceManifest.R20.v1", "evidence schema")
    require(len(evidence["evidence"]) == 6, "evidence denominator")
    require(journal["gates"]["submission"]["status"] == "NOT_AUTHORIZED", "submission gate")
    require(journal["gates"]["novelty"]["status"] == "CANNOT_CHECK_EXTERNAL", "novelty gate")
    require(r18_custody["former_positive_terminal"] == "RETRACTED", "R18 retraction")
    require(r18_custody["current_terminal"] == "FIBERGUARD_R18_NO_PAIRED_ROUTE_VALUE", "R18 custody terminal")
    require(r18_custody["scientific_result"]["development_feasible_candidates"] == 0, "R18 feasible count")
    require(all(value == 0.0 for value in r18_custody["scientific_result"]["route_coverage"].values()), "R18 route coverage")
    require(r19["terminal"] == "FIBERGUARD_JOINT_ROUTE_R19_REPLACEMENT_PASS", "R19 terminal")
    require(r19["invalid_R19_pairing_counterexample"]["original_randomized_value"] == "35", "R19 original value")
    require(r19["invalid_R19_pairing_counterexample"]["shortcut_randomized_value"] == "70", "R19 shortcut value")
    require(r19["same_marginals_different_joint_system"]["full_pair_randomized_value"] == "0", "R19 full-pair value")
    require(r19["same_marginals_different_joint_system"]["diagonal_pair_randomized_value"] == "50", "R19 diagonal value")
    require(r19["authority"]["paired_ASlib_experiment_executed"] is False, "R19 application ceiling")
    require(r19["authority"]["grants_journal_authority"] is False, "R19 journal ceiling")

    require(r18["terminal"] == "FIBERGUARD_R18_NO_PAIRED_ROUTE_VALUE", "R18 result terminal")
    require(r18["development"]["candidate_count"] == 99, "R18 candidate denominator")
    require(r18["development"]["feasible_candidate_count"] == 0, "R18 feasible denominator")
    require(all(r18[key]["selected_route"]["metrics"]["route_change_coverage"] == 0.0 for key in ("development", "validation", "test")), "R18 zero route")
    require(r18["authority"]["recovery_status"] == "OUTCOME_EXPOSED_CORROBORATION", "R18 recovery authority")
    require(r18["authority"]["external_independence"] is False, "R18 external ceiling")
    require(r18["authority"]["grants_journal_authority"] is False, "R18 journal ceiling")

    require(cnbr["schema"] == "ORION02.CNBR.Result.v1", "CNBR schema")
    require(cnbr["overall_verdict"] == "CERTIFICATE_INVALID", "CNBR terminal")
    require([row["verdict"] for row in cnbr["splits"]] == ["CERTIFICATE_INVALID", "CERTIFICATE_INVALID"], "CNBR split terminals")
    official, family = cnbr["splits"]
    for representation in ("NBR_FULL", "NBR_PCA10"):
        require(official["representations"][representation]["certificate_heldout_violation_rate"] > 0.10, f"CNBR official violation {representation}")
        require(family["representations"][representation]["heldout_coverage"]["epsilon_5000"] == 0.0, f"CNBR family coverage {representation}")

    require(finite["terminal"] == "ORION02_R20_STORY_FINITE_CORROBORATION_PASS", "finite terminal")
    require(finite["deterministic_witnesses"]["systems"] == 1000, "finite witness denominator")
    require(finite["no_free_extension"] == {"extensions": 700, "maximum_forced_regret": 20}, "finite no-free denominator")
    require(finite["authority"]["external_independence"] is False, "finite external ceiling")
    require(finite["authority"]["journal_authority"] is False, "finite journal ceiling")

    require(rust["terminal"] == "ORION02_R20_RUST_CROSS_LANGUAGE_CHECKER_PASS", "Rust terminal")
    require(all(rust["controls"].values()), "Rust controls")
    require(rust["finite_checks"]["deterministic_witness_systems"] == 1000, "Rust witness denominator")
    require(rust["finite_checks"]["no_free_extension_cases"] == 700, "Rust no-free denominator")
    require(rust["finite_checks"]["fallback_alignment_cases"] == 33824, "Rust fallback denominator")
    require(rust["authority"]["cross_language"] is True, "Rust language authority")
    require(rust["authority"]["external_independence"] is False, "Rust external ceiling")
    require(rust["authority"]["journal_authority"] is False, "Rust journal ceiling")

    require(retraction["terminal"] == "ORION02_R20_RETRACTION_AUTHORITY_CLOSED", "retraction terminal")
    require(not retraction["local_violations"] and not retraction["live_violations"], "retraction violations")
    require(rights["authority"]["legal_interpretation_complete"] is False, "rights legal ceiling")
    require(rights["authority"]["redistribution_authorized"] is False, "rights redistribution ceiling")
    require(rights["authority"]["journal_data_rights_complete"] is False, "rights journal ceiling")

    expected_audits = {
        "NQ": "ORION.NQ.PR1472ExactSubjectAudit.R20.v2",
        "AB": "ORION.AB.PR1469ProductionRegistryAudit.R20.v1",
        "D": "ORION.D.PR1466FirstMixingAudit.R20.v1",
        "Q1": "ORION.Q1.PR1449ResourceAudit.R20.v1",
    }
    for lane, schema in expected_audits.items():
        require(audits[lane]["schema"] == schema, f"{lane} audit schema")
        require(audits[lane]["authority"]["journal_authority"] is False, f"{lane} journal ceiling")
        require(audits[lane]["authority"]["external_independence"] is False if "external_independence" in audits[lane]["authority"] else True, f"{lane} external ceiling")

    require("For each action $a\\in\\A$, add one unseen state" in manuscript, "exact no-free proof absent")
    require("standard-library-only Rust implementation" in manuscript, "Rust corroboration absent")
    require("FIBERGUARD\\_R18\\_NO\\_PAIRED\\_ROUTE\\_VALUE" in manuscript, "R18 null absent")
    require("CERTIFICATE\\_INVALID" in manuscript, "CNBR adverse absent")
    require("NOVELTY_NOT_ESTABLISHED__RESIDUAL_CLAIM_FROZEN_FOR_EXTERNAL_REVIEW" in prior, "novelty ceiling absent")
    require(pdf.is_file() and pdf.stat().st_size > 10_000, "compiled manuscript absent")

    bindings: dict[str, Any] = {}
    names = ["RELEASE_FILESET_R20.json"] + list(fileset["files"])
    require(len(names) == len(set(names)), "release fileset duplicates")
    for name in names:
        path = orion / name
        require(path.is_file(), f"release file absent: {name}")
        bindings[name] = {
            "git_blob": git_blob(repo, subject, path.relative_to(repo)),
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
        }

    return {
        "bindings": bindings,
        "file_count": len(bindings),
        "ledger": ledger,
        "evidence": evidence,
        "journal": journal,
        "r18_custody": r18_custody,
        "r19": r19,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--r18", type=Path, required=True)
    parser.add_argument("--cnbr", type=Path, required=True)
    parser.add_argument("--finite", type=Path, required=True)
    parser.add_argument("--rust", type=Path, required=True)
    parser.add_argument("--rights", type=Path, required=True)
    parser.add_argument("--retraction", type=Path, required=True)
    parser.add_argument("--nq", type=Path, required=True)
    parser.add_argument("--ab", type=Path, required=True)
    parser.add_argument("--d", type=Path, required=True)
    parser.add_argument("--q1", type=Path, required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--pdfinfo", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    repo = args.repo.resolve()
    audits = {
        "NQ": load(args.nq),
        "AB": load(args.ab),
        "D": load(args.d),
        "Q1": load(args.q1),
    }
    validated = validate(
        repo,
        args.subject,
        load(args.r18),
        load(args.cnbr),
        load(args.finite),
        load(args.rust),
        load(args.rights),
        load(args.retraction),
        audits,
        args.pdf,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    programme = {
        "schema": "ORION.FivePaper.InternalProgrammeTerminal.R30.v1",
        "terminal": "FIVE_PAPER_R30_INTERNAL_EXECUTABLE_WORK_COMPLETE__EXTERNAL_PRODUCTION_RIGHTS_AND_SUBMISSION_GATES_OPEN",
        "source_subject": args.subject,
        "ORION_02": {
            "terminal": "ORION02_R30_STRICT_INTERNAL_RELEASE_PASS__EXTERNAL_GATES_OPEN",
            "R18": "FIBERGUARD_R18_NO_PAIRED_ROUTE_VALUE",
            "R19": "FIBERGUARD_JOINT_ROUTE_R19_REPLACEMENT_PASS",
            "CNBR": "CERTIFICATE_INVALID",
            "Rust": "ORION02_R20_RUST_CROSS_LANGUAGE_CHECKER_PASS",
        },
        "lanes": {
            lane: {
                "terminal": result["terminal"],
                "gates": result["gates"],
                "authority": result["authority"],
            }
            for lane, result in audits.items()
        },
        "remaining_external_or_author_inputs": [
            "author order, affiliations, ORCID, corresponding author, funding, conflicts and contributions",
            "venue and article type",
            "ASlib and other source-data rights interpretation and release licences",
            "external specialist review and structurally independent external reproduction",
            "current-primary-source novelty adjudication",
            "production registry/case/resource inputs required by AB, D and Q1 protocols",
            "permanent DOI/archive and exact portal upload approval",
        ],
        "authority": {
            "internal_executable_work_complete_at_stated_lane_ceiling": True,
            "external_independence": False,
            "novelty": False,
            "rights_complete": False,
            "production_authority_for_all_lanes": False,
            "journal_authority": False,
            "submission_authorized": False,
        },
    }
    internal = {
        "schema": "ORION.ORION02.InternalReleaseReceipt.R30.v1",
        "executed_subject_commit": args.subject,
        "terminal": "ORION02_R30_STRICT_INTERNAL_RELEASE_PASS__EXTERNAL_REVIEW_NOVELTY_RIGHTS_AND_SUBMISSION_OPEN",
        "release_file_count": validated["file_count"],
        "bindings": validated["bindings"],
        "evidence": {
            "R18_result_sha256": sha256(args.r18),
            "R18_terminal": "FIBERGUARD_R18_NO_PAIRED_ROUTE_VALUE",
            "R19_terminal": "FIBERGUARD_JOINT_ROUTE_R19_REPLACEMENT_PASS",
            "CNBR_terminal": "CERTIFICATE_INVALID",
            "finite_terminal": "ORION02_R20_STORY_FINITE_CORROBORATION_PASS",
            "Rust_terminal": "ORION02_R20_RUST_CROSS_LANGUAGE_CHECKER_PASS",
            "retraction_terminal": "ORION02_R20_RETRACTION_AUTHORITY_CLOSED",
            "rights_terminal": load(args.rights)["terminal"],
            "manuscript_pdf_sha256": sha256(args.pdf),
            "manuscript_pdf_bytes": args.pdf.stat().st_size,
            "pdfinfo_sha256": sha256(args.pdfinfo),
        },
        "lane_terminals": {lane: result["terminal"] for lane, result in audits.items()},
        "authority": {
            "analytic_internal_review": True,
            "finite_implementation_corroboration": True,
            "cross_language_same_owner_corroboration": True,
            "prospective_adverse_results_preserved": True,
            "external_independence": False,
            "novelty": False,
            "data_rights_complete": False,
            "production_authority_for_all_lanes": False,
            "journal_authority": False,
            "submission_authorized": False,
        },
    }
    fileset_receipt = {
        "schema": "ORION.ORION02.ReleaseFilesetReceipt.R30.v1",
        "source_subject": args.subject,
        "file_count": validated["file_count"],
        "bindings": validated["bindings"],
        "terminal": "ORION02_R30_RELEASE_FILESET_RECEIPT_PASS",
        "authority": {
            "content_custody": True,
            "external_independence": False,
            "novelty": False,
            "rights_complete": False,
            "journal_authority": False,
            "submission_authorized": False,
        },
    }

    (args.output_dir / "PROGRAMME_INTERNAL_TERMINAL_R30.json").write_text(canonical(programme) + "\n")
    (args.output_dir / "INTERNAL_RELEASE_RECEIPT_R30.json").write_text(canonical(internal) + "\n")
    (args.output_dir / "RELEASE_FILESET_R30_RECEIPT.json").write_text(canonical(fileset_receipt) + "\n")
    lines = [
        "# Five-paper R30 internal terminal",
        "",
        f"`{programme['terminal']}`",
        "",
        f"Source subject: `{args.subject}`.",
        "",
        "All internally executable theorem, custody, adverse-result, cross-language, manuscript, rights-preflight and exact-subject audit work has completed at its stated lane ceiling. No external, novelty, production, legal, journal, or submission authority is synthesized.",
        "",
        "## Lane terminals",
        "",
        f"- ORION-02: `{programme['ORION_02']['terminal']}`",
    ]
    for lane in ("NQ", "AB", "D", "Q1"):
        lines.append(f"- {lane}: `{audits[lane]['terminal']}`")
    lines.extend(["", "## Remaining external or author inputs", ""])
    lines.extend(f"- {item}" for item in programme["remaining_external_or_author_inputs"])
    lines.extend(["", "Journal authority and submission authorization remain false.", ""])
    (args.output_dir / "PROGRAMME_INTERNAL_TERMINAL_R30.md").write_text("\n".join(lines))

    print(programme["terminal"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
