#!/usr/bin/env python3
"""Build the exact ORION-03 Journal of Automated Reasoning release package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile

from build_integrity_ledger import build_ledger
from atomic_claim_inventory import citation_uses, claim_specs


FIXED_ZIP_TIME = (2026, 8, 31, 12, 0, 0)
PDF_NAME = "Typed_Evidence_Licenses_for_Fail_Closed_Nonpromotion.pdf"
SOURCE_ZIP = "Typed_Evidence_Licenses_for_Fail_Closed_Nonpromotion_source.zip"
ARTIFACT_ZIP = "Typed_Evidence_Licenses_for_Fail_Closed_Nonpromotion_artifact.zip"
MANUSCRIPT_ID = "ORION-03-JAR-20260831"
HISTORICAL_BASE_REVISION = "b4d00a36a6681aa920c994d0783970135ab576a3"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def file_record(path: Path, root: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(root).as_posix(),
        "sha256": sha256_file(path),
        "byte_count": path.stat().st_size,
    }


def copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def copy_tree(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
    )


def write_text(path: Path, text: str, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    if executable:
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def run(command: list[str], cwd: Path) -> None:
    env = os.environ.copy()
    env.setdefault("SOURCE_DATE_EPOCH", "1788177600")
    subprocess.run(command, cwd=cwd, env=env, check=True)


def zip_tree(source: Path, target: Path, prefix: str = "") -> list[dict[str, object]]:
    members: list[dict[str, object]] = []
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(p for p in source.rglob("*") if p.is_file()):
            rel = path.relative_to(source).as_posix()
            member = f"{prefix.rstrip('/')}/{rel}" if prefix else rel
            data = path.read_bytes()
            info = zipfile.ZipInfo(member, FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if os.access(path, os.X_OK) else 0o644) << 16
            info.create_system = 3
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
            members.append(
                {"member_path": member, "sha256": sha256_bytes(data), "byte_count": len(data)}
            )
    return members


def historical_file_hash(repo: Path, revision: str, relative_path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{revision}:{relative_path}"],
        cwd=repo,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        raise RuntimeError(f"missing historical object: {revision}:{relative_path}")
    return sha256_bytes(result.stdout)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-revision", required=True)
    parser.add_argument("--skill-root", type=Path, required=True)
    parser.add_argument(
        "--candidate-only",
        action="store_true",
        help="Build a non-releasable checksum-bound package for independent review.",
    )
    args = parser.parse_args()

    closure = Path(__file__).resolve().parent
    paper = closure.parent
    repo = paper.parents[1]
    output = paper / "journal_package_final"
    manuscript = paper / "MANUSCRIPT_V3.md"
    ledger = paper / "CLAIM_LEDGER_V3.md"
    previous = paper / "MANUSCRIPT_V2.md"
    refs = closure / "references.bib"
    template = closure / "jar-pandoc-template.tex"
    cls = closure / "vendor" / "sn-jnl.cls"
    bst = closure / "vendor" / "sn-mathphys-num.bst"
    openssl_license = closure / "OPENSSL_LICENSE.txt"
    for required in (manuscript, ledger, previous, refs, template, cls, bst, openssl_license):
        if not required.is_file():
            raise SystemExit(f"missing release input: {required}")

    skill_root = args.skill_root.resolve()
    integrity_verifier = (
        skill_root / "skills" / "nature-shared" / "scripts" / "verify_research_integrity.py"
    )
    if not integrity_verifier.is_file():
        raise SystemExit(f"missing research-integrity verifier: {integrity_verifier}")
    skill_head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=skill_root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()
    if skill_head != args.skill_revision:
        raise SystemExit(
            f"skill revision mismatch: requested {args.skill_revision}, checkout is {skill_head}"
        )

    old_pdf_rel = (
        "papers/orion-03-typed-merge-falsification/journal_package_final/submission/"
        "Typed_Scientific_Authority_with_Fail-Closed_Nonpromotion.pdf"
    )
    old_pdf_sha = historical_file_hash(
        repo, HISTORICAL_BASE_REVISION, old_pdf_rel
    )

    with tempfile.TemporaryDirectory(prefix="orion03-release-", dir=paper) as temp_name:
        stage = Path(temp_name) / "journal_package_final"
        submission = stage / "submission"
        source = submission / "source"
        artifact = submission / "artifact"
        source.mkdir(parents=True)
        artifact.mkdir(parents=True)

        copy_file(manuscript, stage / "MANUSCRIPT.md")
        copy_file(ledger, stage / "CLAIM_LEDGER.md")
        review_records = stage / "review_records"
        for name in (
            "AUTHOR_CONFIRMATION_V1.json",
            "CITATION_VERIFICATION_V1.md",
            "VENUE_REQUIREMENTS_V1.md",
            "VENUE_DECISION_CONTRACT.json",
            "verify_release.py",
        ):
            copy_file(closure / name, review_records / name)
        copy_tree(closure / "audits", review_records / "audits")
        copy_file(manuscript, source / "MANUSCRIPT.md")
        copy_file(refs, source / "references.bib")
        copy_file(template, source / "jar-pandoc-template.tex")
        copy_file(cls, source / "sn-jnl.cls")
        copy_file(bst, source / "sn-mathphys-num.bst")

        build_sh = """#!/bin/sh
set -eu
PANDOC="${PANDOC:-pandoc}"
TECTONIC="${TECTONIC:-tectonic}"
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-1788177600}"
"$PANDOC" MANUSCRIPT.md \\
  --from=markdown+yaml_metadata_block \\
  --to=latex \\
  --natbib \\
  --top-level-division=section \\
  --template=jar-pandoc-template.tex \\
  --wrap=preserve \\
  --output=main.tex
python3 - <<'PY'
from pathlib import Path
p = Path('main.tex')
s = p.read_text(encoding='utf-8')
s = s.replace('\\\\section*{Statements and Declarations}',
              '\\\\backmatter\\n\\n\\\\section*{Statements and Declarations}', 1)
p.write_text(s, encoding='utf-8', newline='\\n')
PY
"$TECTONIC" --keep-logs --keep-intermediates main.tex
"""
        write_text(source / "build.sh", build_sh, executable=True)
        write_text(
            source / "README.md",
            """# Editable Journal of Automated Reasoning source

This archive contains the canonical Markdown source, generated single-file LaTeX,
numeric bibliography, and the official December 2024 Springer Nature class/style.
Run `./build.sh` with Pandoc 3.9 or compatible and Tectonic 0.15 or compatible.
The checked-in PDF is rebuilt and byte-compared by the release verifier.
""",
        )
        run(["./build.sh"], source)
        if not (source / "main.pdf").is_file():
            raise SystemExit("Tectonic did not produce main.pdf")
        copy_file(source / "main.pdf", submission / PDF_NAME)

        # The source archive contains only editable/rebuild inputs and the generated TeX.
        source_archive_dir = Path(temp_name) / "source-archive"
        source_archive_dir.mkdir()
        for name in (
            "MANUSCRIPT.md",
            "README.md",
            "build.sh",
            "jar-pandoc-template.tex",
            "main.tex",
            "references.bib",
            "sn-jnl.cls",
            "sn-mathphys-num.bst",
        ):
            copy_file(source / name, source_archive_dir / name)

        # Preserve the repository-relative layout so the shipped tests locate
        # the paper evidence exactly as they do in a clean ORION checkout.
        # This is a reproducibility binding, not a new scientific result.
        artifact_paper = artifact / "papers" / "orion-03-typed-merge-falsification"
        copy_file(
            paper / "evidence_license_evaluator.py",
            artifact_paper / "evidence_license_evaluator.py",
        )
        copy_file(
            paper / "evidence_license_schema.json",
            artifact_paper / "evidence_license_schema.json",
        )
        copy_file(
            paper / "test_evidence_license_evaluator.py",
            artifact_paper / "test_evidence_license_evaluator.py",
        )
        copy_tree(paper / "examples", artifact_paper / "examples")
        copy_tree(
            repo / "packages" / "typed-merge-evaluator",
            artifact / "packages" / "typed-merge-evaluator",
        )
        copy_tree(paper / "evidence", artifact_paper / "evidence")
        # Boundary files remain at their repository-relative paper paths.
        # The shipped revalidation script reads the historical V2 manuscript
        # and freeze addendum from this exact directory.
        for name in (
            "MANUSCRIPT_V2.md",
            "CLAIM_LEDGER_V3.md",
            "ROUND2_METRIC_STATUS_FINDING.md",
            "NOVELTY_SUBTRACTION_20260828.md",
            "PUBLICATION_FREEZE_ADDENDUM_V1.md",
        ):
            copy_file(paper / name, artifact_paper / name)
        copy_file(openssl_license, artifact / "licenses" / "OPENSSL_LICENSE.txt")
        copy_file(
            paper / "evidence" / "round2-x509-truststore" / "THIRD_PARTY_SOURCE.md",
            artifact / "licenses" / "OPENSSL_ATTRIBUTION.md",
        )
        write_text(
            artifact / "README.md",
            """# ORION-03 executable and evidence artifact

This archive contains the finite evaluator and fixtures, the reusable typed-merge
evaluator, the full Cedar null/adverse record, the full OpenSSL-derived evidence
record including selected third-party test material, and the live scientific
boundary documents. Paths mirror the ORION repository. Start with
`packages/typed-merge-evaluator/REPRODUCTION.md`.

The archive preserves `CANNOT_CHECK` distinctions. Without the named native
Cedar, Lean, and pinned OpenSSL toolchains, the package verifies committed
digests and bounded computations but does not claim a fresh native replay of
every engine-derived result. The Cedar study remains null for the intended
evidence-license residual; the five OpenSSL anchor disagreements remain adverse;
and the origin-witness perfect row remains an analytic identity rather than
detector performance.

The OpenSSL files retain their upstream attribution and Apache License 2.0.
""",
        )

        source_members = zip_tree(source_archive_dir, submission / SOURCE_ZIP)
        artifact_members = zip_tree(artifact, submission / ARTIFACT_ZIP)

        component_binding_manifest = {
            "schema": "ORION.PublicationClosure.ComponentBindingManifest.v1",
            "paper": "ORION-03",
            "state": "CHECKSUM_BOUND_COMPONENT_SET",
            "canonical_science": file_record(stage / "MANUSCRIPT.md", stage),
            "canonical_claim_ledger": file_record(stage / "CLAIM_LEDGER.md", stage),
            "reader_pdf": file_record(submission / PDF_NAME, stage),
            "source_archive": {
                **file_record(submission / SOURCE_ZIP, stage),
                "members": source_members,
            },
            "artifact_archive": {
                **file_record(submission / ARTIFACT_ZIP, stage),
                "members": artifact_members,
            },
            "does_not_certify": [
                "independent_review",
                "scientific_truth",
                "external_replication",
                "portal_upload",
                "journal_acceptance",
            ],
        }
        write_text(
            stage / "COMPONENT_BINDING_MANIFEST.json",
            json.dumps(component_binding_manifest, indent=2, sort_keys=True) + "\n",
        )
        atomic_inventory = {
            "schema": "ORION.PublicationClosure.AtomicClaimInventory.v1",
            "paper": "ORION-03",
            "state": "IMMUTABLE_INDEPENDENT_REVIEW_INPUT",
            "canonical_science": file_record(stage / "MANUSCRIPT.md", stage),
            "canonical_claim_ledger": file_record(stage / "CLAIM_LEDGER.md", stage),
            "reader_pdf": file_record(submission / PDF_NAME, stage),
            "component_binding_manifest": file_record(
                stage / "COMPONENT_BINDING_MANIFEST.json", stage
            ),
            "claim_count": len(claim_specs()),
            "citation_use_count": len(citation_uses()),
            "claims": claim_specs(),
            "citation_uses": citation_uses(),
            "independent_review_status": "PENDING",
            "does_not_certify": [
                "independent_review_pass",
                "submission_readiness",
                "scientific_truth",
                "external_replication",
            ],
        }
        for claim in atomic_inventory["claims"]:
            pointer = claim.get("artifact_pointer")
            if not pointer:
                continue
            pointer_path = (stage / str(pointer).split("#", 1)[0]).resolve()
            try:
                pointer_path.relative_to(stage.resolve())
            except ValueError as exc:
                raise SystemExit(f"atomic pointer escapes candidate: {pointer}") from exc
            if not pointer_path.exists():
                raise SystemExit(f"atomic pointer does not resolve in candidate: {pointer}")
        write_text(
            stage / "ATOMIC_CLAIM_INVENTORY.json",
            json.dumps(atomic_inventory, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        )

        cover = """# Cover-letter draft — Journal of Automated Reasoning

Dear Editors,

Please consider the manuscript *Typed Evidence Licenses for Fail-Closed Nonpromotion in Finite Rule Systems* as an original research article. It defines a finite positive conjunctive system in which evidence licenses propagate only through permitted rule caps and directly refuted claims fail closed. The manuscript proves least-fixed-point, proof-tree, refutation-monotonicity, and exact relative-retraction results for this declared algebra, and supplies a deterministic evaluator.

The external instantiation uses frozen OpenSSL test material and native engine decisions. It identifies 46 hybrid authorizations among 1,962 merge tasks and compares the costs of five fixed merge policies. The definitionally perfect origin-witness row is presented as an analytic identity with a two-parent evaluation cost, not as detector performance. This combination of formal semantics, executable reasoning, and bounded native-engine evaluation is intended to fit the scope of the *Journal of Automated Reasoning*.

The contribution is deliberately narrower than generic provenance, causality, or belief-revision theory and makes no security or deployment claim. The accompanying archives retain the complete evidence record, including the null Cedar transfer, the 186-of-191 OpenSSL anchoring result, all five disagreements, source bindings, executable cases, and explicit limits on native replay when required external toolchains are unavailable.

Sincerely,  
Sze Chun Yiu
"""
        write_text(submission / "cover_letter.md", cover)

        independent_review_line = (
            "- [ ] Independent atomic-claim and package review is pending; this candidate is not releasable."
            if args.candidate_only
            else "- [x] Independent checksum-bound atomic-claim coverage and research-integrity verification passed."
        )
        release_receipt_line = (
            "- [ ] Final release manifests and research-integrity ledger/report are intentionally absent until review passes."
            if args.candidate_only
            else "- [x] Package manifest, release manifest, research-integrity ledger/report, and `SHA256SUMS` generated from the final bytes."
        )
        checklist = f"""# ORION-03 repository-side filing checklist

- [x] Canonical V3 science, live claim ledger, and final reader PDF bound by SHA-256 and byte count.
- [x] Exactly one reader-facing manuscript authority designated; plausible predecessors have explicit dispositions.
- [x] Cedar null/adverse result, zero-request failure, OpenSSL 186/191 anchor, analytic identity, two-parent cost, and unavailable-native-replay limits retained.
- [x] PDF rebuilt twice with byte-identical output; extracted text is non-empty; no undefined references or overfull boxes.
- [x] Every PDF page visually inspected, including the policy table, declarations, references, and final page.
- [x] Editable Springer Nature source archive and complete reproducibility artifact included.
- [x] Deterministic source/artifact ZIPs have exact member inventories; extra, missing, or stale members fail closed.
- [x] Final `academic-paper-skills` revision `{args.skill_revision}` recorded and applicable audits rerun.
{independent_review_line}
{release_receipt_line}
- [ ] Complete external portal/account metadata and upload (human action).
- [ ] Confirm the corresponding-author identity and all portal declarations at filing time (human action).
"""
        write_text(submission / "submission_checklist.md", checklist)

        package_readme = (
            """# ORION-03 independent-review candidate

This checksum-bound candidate exists only so an independent reviewer can inspect
the exact manuscript, PDF, source archive, artifact archive, and retained adverse
evidence before a release ledger is generated. It is not a filing package and
must not be described as submission-ready, independently verified, or released.
"""
            if args.candidate_only
            else """# ORION-03 Journal of Automated Reasoning package

The reader authority is the PDF identified in `PUBLICATION_RELEASE_MANIFEST.json`.
`MANUSCRIPT.md` and `CLAIM_LEDGER.md` are byte-identical copies of the canonical
repository source and scientific claim ledger. The source and artifact archives
have exact, hash-bound member inventories.

`RESEARCH_INTEGRITY_LEDGER.json` binds the exact reader PDF to the independent
atomic-claim/source coverage review; `RESEARCH_INTEGRITY_REPORT.json` is the
released skill verifier's fail-closed result for those exact bytes.

This package is ready for author filing, not already filed or accepted. It does
not claim external replication, external peer review, security evaluation,
production validity, or authority beyond the bounded manuscript and ledger.
"""
        )
        write_text(stage / "README.md", package_readme)
        copy_file(stage / "README.md", submission / "README.md")

        pdf = submission / PDF_NAME
        if args.candidate_only:
            for stale in (
                closure / "BUILD_SUMMARY.json",
                closure / "FINAL_RELEASE_VERIFICATION.json",
                closure / "VISUAL_QA_V1.md",
            ):
                stale.unlink(missing_ok=True)
            candidate_manifest = {
                "schema": "ORION.PublicationClosure.IndependentReviewCandidate.v1",
                "paper": "ORION-03",
                "state": "CANDIDATE_ONLY__NOT_RELEASE_READY",
                "academic_paper_skills_revision": args.skill_revision,
                "canonical_science": file_record(stage / "MANUSCRIPT.md", stage),
                "canonical_claim_ledger": file_record(stage / "CLAIM_LEDGER.md", stage),
                "reader_pdf": file_record(pdf, stage),
                "atomic_claim_inventory": file_record(
                    stage / "ATOMIC_CLAIM_INVENTORY.json", stage
                ),
                "component_binding_manifest": file_record(
                    stage / "COMPONENT_BINDING_MANIFEST.json", stage
                ),
                "source_archive": {
                    **file_record(submission / SOURCE_ZIP, stage),
                    "members": source_members,
                },
                "artifact_archive": {
                    **file_record(submission / ARTIFACT_ZIP, stage),
                    "members": artifact_members,
                },
                "preserved_terminals": [
                    "CEDAR_EXTERNAL_TRANSFER_NULL",
                    "CEDAR_ZERO_REQUEST_PATH_BINDING_FAILURE",
                    "OPENSSL_ANCHOR_186_OF_191_WITH_FIVE_DISAGREEMENTS",
                    "ORIGIN_WITNESS_PERFECT_ROW_IS_ANALYTIC_IDENTITY",
                    "ORIGIN_WITNESS_TWO_PARENT_EVALUATION_COST",
                    "PACKAGE_NATIVE_REPLAY_CANNOT_CHECK_BOUNDARIES",
                ],
                "does_not_certify": [
                    "independent_review",
                    "research_integrity_pass",
                    "submission_readiness",
                    "portal_upload",
                    "journal_acceptance",
                ],
            }
            write_text(
                stage / "CANDIDATE_REVIEW_MANIFEST.json",
                json.dumps(candidate_manifest, indent=2, sort_keys=True) + "\n",
            )
            checksum_files = sorted(
                p for p in stage.rglob("*")
                if p.is_file() and p != stage / "SHA256SUMS"
            )
            write_text(
                stage / "SHA256SUMS",
                "".join(
                    f"{sha256_file(path)}  {path.relative_to(stage).as_posix()}\n"
                    for path in checksum_files
                ),
            )
            candidate_output = closure / "candidate_package"
            if candidate_output.exists():
                shutil.rmtree(candidate_output)
            shutil.copytree(stage, candidate_output)
            write_text(
                closure / "CANDIDATE_BUILD_SUMMARY.json",
                json.dumps(
                    {
                        "schema": "ORION.PublicationClosure.CandidateBuildSummary.v1",
                        "paper": "ORION-03",
                        "state": "CANDIDATE_ONLY__NOT_RELEASE_READY",
                        "canonical_science": file_record(candidate_output / "MANUSCRIPT.md", candidate_output),
                        "reader_pdf": file_record(candidate_output / "submission" / PDF_NAME, candidate_output),
                        "atomic_claim_inventory": file_record(candidate_output / "ATOMIC_CLAIM_INVENTORY.json", candidate_output),
                        "component_binding_manifest": file_record(candidate_output / "COMPONENT_BINDING_MANIFEST.json", candidate_output),
                        "candidate_manifest": file_record(candidate_output / "CANDIDATE_REVIEW_MANIFEST.json", candidate_output),
                        "top_level_checksums": file_record(candidate_output / "SHA256SUMS", candidate_output),
                        "source_zip": file_record(candidate_output / "submission" / SOURCE_ZIP, candidate_output),
                        "artifact_zip": file_record(candidate_output / "submission" / ARTIFACT_ZIP, candidate_output),
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
            )
            print(json.dumps(candidate_manifest, indent=2, sort_keys=True))
            return

        # Keep the sanitized independent-review receipt as repository-side
        # provenance and exclude the receipt itself from the journal upload
        # set.  The public package carries only a digest and repository-relative
        # locator, so both the package and exact public mirror remain free of
        # review-worktree paths.
        independent_review = closure / "INDEPENDENT_RELEASE_REVIEW_V1.json"
        independent_review_locator = independent_review.relative_to(repo).as_posix()
        independent_review_provenance = stage / "INDEPENDENT_RELEASE_REVIEW_PROVENANCE.json"
        write_text(
            independent_review_provenance,
            json.dumps(
                {
                    "schema": "ORION.PublicationClosure.IndependentReviewProvenance.v1",
                    "paper": "ORION-03",
                    "disposition": "REPOSITORY_SIDE_PROVENANCE__EXCLUDED_FROM_UPLOAD_SET",
                    "repository_relative_path": independent_review_locator,
                    "sha256": sha256_file(independent_review),
                    "byte_count": independent_review.stat().st_size,
                    "does_not_certify": [
                        "external_peer_review",
                        "journal_acceptance",
                        "portal_upload",
                    ],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        pdf_fingerprint = f"sha256:{sha256_file(pdf)}"
        research_integrity_ledger = build_ledger(
            closure=closure,
            paper=paper,
            pdf=pdf,
        )
        write_text(
            stage / "RESEARCH_INTEGRITY_LEDGER.json",
            json.dumps(research_integrity_ledger, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        )
        run(
            [
                sys.executable,
                str(integrity_verifier),
                str(stage / "RESEARCH_INTEGRITY_LEDGER.json"),
                "--manuscript",
                str(pdf),
                "--max-status-age-days",
                "30",
                "--report",
                str(stage / "RESEARCH_INTEGRITY_REPORT.json"),
                "--pretty",
            ],
            closure,
        )
        integrity_report = json.loads(
            (stage / "RESEARCH_INTEGRITY_REPORT.json").read_text(encoding="utf-8")
        )
        if integrity_report.get("decision") != "PASS":
            raise SystemExit("research-integrity verification did not pass")
        release_ledger = {
            "schema_version": "1.0",
            "manuscript_id": MANUSCRIPT_ID,
            "manuscript_fingerprint": pdf_fingerprint,
            "release": {"requested_state": "submission_ready"},
            "canonical_scientific_source": {
                "path": "MANUSCRIPT.md",
                "sha256": f"sha256:{sha256_file(stage / 'MANUSCRIPT.md')}",
            },
            "canonical_claim_ledger": {
                "path": "CLAIM_LEDGER.md",
                "sha256": f"sha256:{sha256_file(stage / 'CLAIM_LEDGER.md')}",
            },
            "preserved_terminals": [
                "CEDAR_EXTERNAL_TRANSFER_NULL",
                "CEDAR_ZERO_REQUEST_PATH_BINDING_FAILURE",
                "OPENSSL_ANCHOR_186_OF_191_WITH_FIVE_DISAGREEMENTS",
                "ORIGIN_WITNESS_PERFECT_ROW_IS_ANALYTIC_IDENTITY",
                "ORIGIN_WITNESS_TWO_PARENT_EVALUATION_COST",
                "PACKAGE_NATIVE_REPLAY_CANNOT_CHECK_BOUNDARIES",
            ],
            "does_not_certify": [
                "scientific_truth",
                "external_replication",
                "security",
                "deployment",
                "portal_upload",
                "journal_acceptance",
            ],
        }
        write_text(stage / "CLAIM_LEDGER_RELEASE.json", json.dumps(release_ledger, indent=2, sort_keys=True) + "\n")

        artifacts: list[dict[str, object]] = []
        artifact_specs = [
            ("reader-pdf", "reader_manuscript", pdf),
            ("atomic-claim-inventory", "release_receipt", stage / "ATOMIC_CLAIM_INVENTORY.json"),
            ("component-binding-manifest", "release_receipt", stage / "COMPONENT_BINDING_MANIFEST.json"),
            (
                "independent-release-review-provenance",
                "release_receipt",
                independent_review_provenance,
            ),
            ("release-claim-ledger", "release_receipt", stage / "CLAIM_LEDGER_RELEASE.json"),
            ("research-integrity-ledger", "claim_ledger", stage / "RESEARCH_INTEGRITY_LEDGER.json"),
            ("research-integrity-report", "release_receipt", stage / "RESEARCH_INTEGRITY_REPORT.json"),
            ("canonical-source", "manuscript_source", stage / "MANUSCRIPT.md"),
            ("scientific-claim-ledger", "release_receipt", stage / "CLAIM_LEDGER.md"),
            ("source-archive", "submission_component", submission / SOURCE_ZIP),
            ("artifact-archive", "reproducibility_component", submission / ARTIFACT_ZIP),
            ("cover-letter", "submission_component", submission / "cover_letter.md"),
            ("filing-checklist", "submission_component", submission / "submission_checklist.md"),
        ]
        for artifact_id, role, path in artifact_specs:
            artifacts.append(
                {
                    "artifact_id": artifact_id,
                    "role": role,
                    "path": path.relative_to(stage).as_posix(),
                    "sha256": f"sha256:{sha256_file(path)}",
                    "byte_count": path.stat().st_size,
                }
            )

        authority_pdf = next(a for a in artifacts if a["artifact_id"] == "reader-pdf")
        release_manifest = {
            "schema_version": "1.0",
            "release_id": "ORION-03-JAR-PUBLICATION-CLOSURE-20260831",
            "canonical_paper_id": "ORION-03",
            "requested_state": "submission_ready",
            "authority": {
                "manuscript_id": MANUSCRIPT_ID,
                "manuscript_artifact_id": "reader-pdf",
                "claim_ledger_artifact_id": "research-integrity-ledger",
            },
            "manuscript_candidates": [
                {
                    "manuscript_id": MANUSCRIPT_ID,
                    "artifact_id": "reader-pdf",
                    "sha256": authority_pdf["sha256"],
                    "disposition": "authoritative",
                    "reason": "Exact reader-facing PDF governing the filing package.",
                },
                {
                    "manuscript_id": "ORION-03-V3-EDITABLE-SOURCE",
                    "sha256": f"sha256:{sha256_file(manuscript)}",
                    "disposition": "historical_provenance",
                    "reason": "Canonical editable scientific source bound to the PDF; not a competing reader artifact.",
                },
                {
                    "manuscript_id": "ORION-03-V2",
                    "sha256": f"sha256:{sha256_file(previous)}",
                    "disposition": "superseded",
                    "superseded_by": MANUSCRIPT_ID,
                    "reason": "Earlier scientific manuscript retained only for provenance.",
                },
                {
                    "manuscript_id": "ORION-03-V3-PIPELINE-DRAFT",
                    "sha256": f"sha256:{sha256_file(paper / 'MANUSCRIPT_V3_PIPELINE.md')}",
                    "disposition": "superseded",
                    "superseded_by": MANUSCRIPT_ID,
                    "reason": "Pipeline draft retained only as historical provenance; excluded from the upload set.",
                },
                {
                    "manuscript_id": "ORION-03-BASE-V3-SOURCE",
                    "sha256": f"sha256:{historical_file_hash(repo, HISTORICAL_BASE_REVISION, 'papers/orion-03-typed-merge-falsification/MANUSCRIPT_V3.md')}",
                    "disposition": "superseded",
                    "superseded_by": MANUSCRIPT_ID,
                    "reason": "Pre-closure V3 source bytes from the branch base; retained only in Git history.",
                },
                {
                    "manuscript_id": "ORION-03-HISTORICAL-JOURNAL-SOURCE",
                    "sha256": f"sha256:{historical_file_hash(repo, HISTORICAL_BASE_REVISION, 'papers/orion-03-typed-merge-falsification/journal_package_final/MANUSCRIPT.md')}",
                    "disposition": "superseded",
                    "superseded_by": MANUSCRIPT_ID,
                    "reason": "Pre-closure journal-package source; replaced by the byte-identical final canonical source.",
                },
                {
                    "manuscript_id": "ORION-03-HISTORICAL-JOURNAL-PDF",
                    "sha256": f"sha256:{old_pdf_sha}",
                    "disposition": "superseded",
                    "superseded_by": MANUSCRIPT_ID,
                    "reason": "Earlier malformed and incomplete journal package; excluded from the upload set.",
                },
                {
                    "manuscript_id": "ORION-03-HISTORICAL-MANUSCRIPT-BUILD-PDF",
                    "sha256": f"sha256:{sha256_file(paper / 'manuscript' / 'main.pdf')}",
                    "disposition": "superseded",
                    "superseded_by": MANUSCRIPT_ID,
                    "reason": "Historical repository build outside the final filing package.",
                },
                {
                    "manuscript_id": "ORION-03-HISTORICAL-SUBMISSION-PDF",
                    "sha256": f"sha256:{sha256_file(paper / 'submission' / 'Typed_Evidence_Licenses_for_Finite_Positive_Rule_Graphs.pdf')}",
                    "disposition": "superseded",
                    "superseded_by": MANUSCRIPT_ID,
                    "reason": "Historical submission rendering with predecessor title; excluded from the final upload set.",
                },
                {
                    "manuscript_id": "ORION-03-SOURCE-TREE-BUILD-DERIVATIVE",
                    "sha256": f"sha256:{sha256_file(source / 'main.pdf')}",
                    "disposition": "historical_provenance",
                    "reason": "Byte-identical rebuild retained inside the editable source tree; not a separate reader authority or upload target.",
                },
            ],
            "artifacts": artifacts,
            "package": {
                "format": "file_set",
                "members": [
                    {"member_path": f"submission/{PDF_NAME}", "artifact_id": "reader-pdf"},
                    {"member_path": f"submission/{SOURCE_ZIP}", "artifact_id": "source-archive"},
                    {"member_path": f"submission/{ARTIFACT_ZIP}", "artifact_id": "artifact-archive"},
                    {"member_path": "submission/cover_letter.md", "artifact_id": "cover-letter"},
                    {"member_path": "submission/submission_checklist.md", "artifact_id": "filing-checklist"},
                    {"member_path": "ATOMIC_CLAIM_INVENTORY.json", "artifact_id": "atomic-claim-inventory"},
                    {"member_path": "COMPONENT_BINDING_MANIFEST.json", "artifact_id": "component-binding-manifest"},
                    {
                        "member_path": "INDEPENDENT_RELEASE_REVIEW_PROVENANCE.json",
                        "artifact_id": "independent-release-review-provenance",
                    },
                    {"member_path": "RESEARCH_INTEGRITY_LEDGER.json", "artifact_id": "research-integrity-ledger"},
                    {"member_path": "RESEARCH_INTEGRITY_REPORT.json", "artifact_id": "research-integrity-report"},
                ],
            },
        }
        write_text(
            stage / "PUBLICATION_RELEASE_MANIFEST.json",
            json.dumps(release_manifest, indent=2, sort_keys=True) + "\n",
        )

        package_manifest = {
            "schema": "ORION.PublicationClosure.FinalJournalPackage.v2",
            "paper": "ORION-03",
            "primary_target": "Journal of Automated Reasoning",
            "academic_paper_skills_revision": args.skill_revision,
            "scientific_authority_delta": "NONE__EDITORIAL_AND_PACKAGE_CLOSURE_ONLY",
            "canonical_science": file_record(stage / "MANUSCRIPT.md", stage),
            "canonical_claim_ledger": file_record(stage / "CLAIM_LEDGER.md", stage),
            "reader_pdf": file_record(pdf, stage),
            "independent_review_provenance": file_record(
                independent_review_provenance, stage
            ),
            "research_integrity_ledger": file_record(
                stage / "RESEARCH_INTEGRITY_LEDGER.json", stage
            ),
            "research_integrity_report": file_record(
                stage / "RESEARCH_INTEGRITY_REPORT.json", stage
            ),
            "source_archive": {
                **file_record(submission / SOURCE_ZIP, stage),
                "members": source_members,
            },
            "artifact_archive": {
                **file_record(submission / ARTIFACT_ZIP, stage),
                "members": artifact_members,
            },
            "vendor": {
                "template_release": "Springer Nature article template v3.1, December 2024",
                "official_download": "https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/18782940/data/v12",
                "sn-jnl.cls": sha256_file(cls),
                "sn-mathphys-num.bst": sha256_file(bst),
            },
            "does_not_certify": [
                "external_replication",
                "external_peer_review",
                "portal_upload",
                "acceptance",
                "security_or_deployment_validity",
            ],
        }
        write_text(stage / "PACKAGE_MANIFEST.json", json.dumps(package_manifest, indent=2, sort_keys=True) + "\n")

        release_manifest_path = stage / "PUBLICATION_RELEASE_MANIFEST.json"
        release_decision = {
            "schema": "ORION.PublicationClosure.ReleaseDecision.v1",
            "paper": "ORION-03",
            "requested_state": "submission_ready",
            "manifest_sha256": sha256_file(release_manifest_path),
            "manifest_byte_count": release_manifest_path.stat().st_size,
            "verification_command": "python publication_closure_20260831/verify_release.py",
            "portal_upload_complete": False,
            "external_review_complete": False,
        }
        write_text(stage / "RELEASE_DECISION.json", json.dumps(release_decision, indent=2, sort_keys=True) + "\n")

        checksum_files = sorted(
            p for p in stage.rglob("*")
            if p.is_file() and p != stage / "SHA256SUMS"
        )
        checksum_text = "".join(
            f"{sha256_file(path)}  {path.relative_to(stage).as_posix()}\n" for path in checksum_files
        )
        write_text(stage / "SHA256SUMS", checksum_text)

        if output.exists():
            shutil.rmtree(output)
        shutil.copytree(stage, output)

        # Keep the closure-side build summary bound to the same bytes. This
        # file is intentionally outside the upload package and is regenerated
        # on every build so it cannot retain predecessor names or hashes.
        build_summary = {
            "schema": "ORION.PublicationClosure.BuildSummary.v2",
            "paper": "ORION-03",
            "academic_paper_skills_revision": args.skill_revision,
            "reader_pdf": file_record(output / "submission" / PDF_NAME, output),
            "independent_review_provenance": file_record(
                output / "INDEPENDENT_RELEASE_REVIEW_PROVENANCE.json", output
            ),
            "source_zip": {
                **file_record(output / "submission" / SOURCE_ZIP, output),
                "member_count": len(source_members),
            },
            "artifact_zip": {
                **file_record(output / "submission" / ARTIFACT_ZIP, output),
                "member_count": len(artifact_members),
            },
        }
        write_text(
            closure / "BUILD_SUMMARY.json",
            json.dumps(build_summary, indent=2, sort_keys=True) + "\n",
        )


if __name__ == "__main__":
    main()
