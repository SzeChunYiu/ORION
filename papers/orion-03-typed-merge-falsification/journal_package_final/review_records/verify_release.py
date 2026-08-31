#!/usr/bin/env python3
"""Fail-closed verification for the exact ORION-03 filing package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile


PDF_NAME = "Typed_Evidence_Licenses_for_Fail_Closed_Nonpromotion.pdf"
SOURCE_ZIP = "Typed_Evidence_Licenses_for_Fail_Closed_Nonpromotion_source.zip"
ARTIFACT_ZIP = "Typed_Evidence_Licenses_for_Fail_Closed_Nonpromotion_artifact.zip"
REVIEW_PROVENANCE = "INDEPENDENT_RELEASE_REVIEW_PROVENANCE.json"
REVIEW_RECEIPT = "INDEPENDENT_RELEASE_REVIEW_V1.json"
EXPECTED_HISTORICAL_MANUSCRIPT_HASHES = {
    "ORION-03-BASE-V3-SOURCE": (
        "sha256:968c9fed9d370af8551e0ced3588569975649409ce627b869da30844229de8d8"
    ),
    "ORION-03-HISTORICAL-JOURNAL-SOURCE": (
        "sha256:9b9abc02bcf9d7bb6690c7c5f8b54928603922f949bc2c4f27e97e5ff5bdbd71"
    ),
    "ORION-03-HISTORICAL-JOURNAL-PDF": (
        "sha256:ab046f403ea64459f0d162c56887c5e80e6b9483b294e25c85c9261b0d2bf893"
    ),
}


class VerificationError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def verify_historical_candidate_hashes(release: dict[str, object]) -> None:
    candidates = {
        str(candidate["manuscript_id"]): candidate
        for candidate in release.get("manuscript_candidates", [])  # type: ignore[union-attr]
    }
    for manuscript_id, expected_hash in EXPECTED_HISTORICAL_MANUSCRIPT_HASHES.items():
        candidate = candidates.get(manuscript_id)
        require(candidate is not None, f"historical manuscript candidate missing: {manuscript_id}")
        require(
            candidate.get("sha256") == expected_hash,
            f"historical manuscript candidate hash mismatch: {manuscript_id}",
        )


def run(command: list[str], cwd: Path, *, capture: bool = True) -> str:
    env = os.environ.copy()
    env.setdefault("SOURCE_DATE_EPOCH", "1788177600")
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        check=False,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
        text=True,
    )
    output = result.stdout or ""
    if result.returncode != 0:
        raise VerificationError(
            f"command failed ({result.returncode}): {' '.join(command)}\n{output[-4000:]}"
        )
    return output


def verify_archive(
    archive_path: Path,
    manifest_record: dict[str, object],
    expanded_root: Path,
) -> int:
    require(sha256_file(archive_path) == manifest_record["sha256"], f"archive hash mismatch: {archive_path.name}")
    require(archive_path.stat().st_size == manifest_record["byte_count"], f"archive size mismatch: {archive_path.name}")
    expected = {str(item["member_path"]): item for item in manifest_record["members"]}  # type: ignore[index]
    with zipfile.ZipFile(archive_path) as archive:
        # Inspect every central-directory entry.  Filtering ``is_dir()`` would
        # let an undeclared payload-bearing name ending in ``/`` evade the exact
        # member-set check.
        infos = archive.infolist()
        names = [info.filename for info in infos]
        require(len(names) == len(set(names)), f"duplicate ZIP member: {archive_path.name}")
        require(set(names) == set(expected), f"ZIP membership mismatch: {archive_path.name}")
        for name in names:
            data = archive.read(name)
            record = expected[name]
            require(sha256_bytes(data) == record["sha256"], f"ZIP member hash mismatch: {name}")
            require(len(data) == record["byte_count"], f"ZIP member size mismatch: {name}")
            expanded = (expanded_root / name).resolve()
            require(
                expanded_root.resolve() in expanded.parents,
                f"expanded archive member escapes root: {name}",
            )
            require(expanded.is_file(), f"expanded archive member missing: {expanded}")
            require(expanded.read_bytes() == data, f"expanded member differs from ZIP: {name}")
    return len(expected)


def abstract_and_keyword_checks(manuscript_text: str) -> tuple[int, int]:
    match = re.search(r"^abstract:\s*\|\n(?P<body>(?:^  .+\n)+)", manuscript_text, re.MULTILINE)
    require(match is not None, "YAML abstract not found")
    abstract = " ".join(line.strip() for line in match.group("body").splitlines())
    words = re.findall(r"\b[\w’-]+\b", abstract)
    require(150 <= len(words) <= 250, f"abstract word count outside JAR range: {len(words)}")
    keyword_match = re.search(
        r"^keywords:\s*\n(?P<body>(?:^  - .+\n)+)", manuscript_text, re.MULTILINE
    )
    require(keyword_match is not None, "YAML keywords not found")
    keywords = [line[4:].strip() for line in keyword_match.group("body").splitlines()]
    require(4 <= len(keywords) <= 6, f"keyword count outside JAR range: {len(keywords)}")
    return len(words), len(keywords)


def verify_review_receipt_disposition(
    *, repo: Path, closure: Path, package: Path, submission: Path
) -> None:
    """Keep review provenance bindable without publishing workstation paths."""

    receipt = closure / REVIEW_RECEIPT
    provenance_path = package / REVIEW_PROVENANCE
    require(receipt.is_file(), "repository-side independent-review receipt missing")
    require(
        not (package / REVIEW_RECEIPT).exists(),
        "signed independent-review receipt leaked into final package",
    )
    require(provenance_path.is_file(), "independent-review provenance record missing")
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    expected_locator = receipt.relative_to(repo).as_posix()
    require(
        provenance.get("disposition")
        == "REPOSITORY_SIDE_PROVENANCE__EXCLUDED_FROM_UPLOAD_SET",
        "independent-review receipt disposition is not upload-excluded",
    )
    require(
        provenance.get("repository_relative_path") == expected_locator,
        "independent-review repository locator mismatch",
    )
    require(
        provenance.get("sha256") == sha256_file(receipt),
        "independent-review provenance digest mismatch",
    )
    require(
        provenance.get("byte_count") == receipt.stat().st_size,
        "independent-review provenance byte count mismatch",
    )

    receipt_digest = sha256_file(receipt)
    # Construct the markers so the packaged verifier does not trigger its own
    # payload scan merely by naming the forbidden patterns.
    forbidden_local_markers = (
        b"/" + b"Users" + b"/",
        b"/" + b"home" + b"/",
        b"C:" + bytes((92,)),
    )
    receipt_bytes = receipt.read_bytes()
    for marker in forbidden_local_markers:
        require(
            marker not in receipt_bytes,
            "absolute local path leaked into repository receipt",
        )
    for path in sorted(p for p in package.rglob("*") if p.is_file()):
        data = path.read_bytes()
        require(
            sha256_bytes(data) != receipt_digest,
            f"signed independent-review receipt bytes leaked into package: {path.relative_to(package)}",
        )
        # Compressed byte streams can contain these short byte patterns by
        # chance; inspect every decoded ZIP member below instead.
        if not zipfile.is_zipfile(path):
            for marker in forbidden_local_markers:
                require(
                    marker not in data,
                    f"absolute local path leaked into package: {path.relative_to(package)}",
                )
    for archive_path in sorted(submission.glob("*.zip")):
        with zipfile.ZipFile(archive_path) as archive:
            for info in archive.infolist():
                data = archive.read(info.filename)
                require(
                    sha256_bytes(data) != receipt_digest,
                    f"signed independent-review receipt bytes leaked into archive: {archive_path.name}:{info.filename}",
                )
                for marker in forbidden_local_markers:
                    require(
                        marker not in data,
                        f"absolute local path leaked into archive: {archive_path.name}:{info.filename}",
                    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skill-root",
        type=Path,
        required=True,
        help="Checkout of the exact academic-paper-skills revision recorded in the package.",
    )
    args = parser.parse_args()

    closure = Path(__file__).resolve().parent
    paper = closure.parent
    repo = paper.parents[1]
    package = paper / "journal_package_final"
    submission = package / "submission"
    source = submission / "source"
    artifact = submission / "artifact"
    canonical = paper / "MANUSCRIPT_V3.md"
    ledger = paper / "CLAIM_LEDGER_V3.md"
    pdf = submission / PDF_NAME

    require(package.is_dir(), "journal package missing")
    require(pdf.is_file(), "reader PDF missing")
    require((package / "MANUSCRIPT.md").read_bytes() == canonical.read_bytes(), "package manuscript is not canonical bytes")
    require((source / "MANUSCRIPT.md").read_bytes() == canonical.read_bytes(), "source manuscript is not canonical bytes")
    require((package / "CLAIM_LEDGER.md").read_bytes() == ledger.read_bytes(), "package claim ledger is not canonical bytes")

    manuscript_text = canonical.read_text(encoding="utf-8")
    abstract_words, keyword_count = abstract_and_keyword_checks(manuscript_text)
    require(not re.search(r"^### ", manuscript_text, re.MULTILINE), "JAR three-level heading ceiling exceeded")
    for required_text in (
        "The outcome was recorded as null or adverse",
        "zero-request setup failure",
        "186 of 191",
        "five disagreements",
        "analytic identities",
        "implementation-level reproduction, not external human peer review",
        "not an estimate of production prevalence",
        "Ethics approval and consent to participate",
        "Use of generative artificial intelligence",
        "Materials availability",
    ):
        require(required_text in manuscript_text, f"required manuscript boundary missing: {required_text}")
    require("deployed certificate material" not in manuscript_text, "production/deployment overclaim remains")
    require("`openssl-3.6.4`" not in manuscript_text, "code-style source tag leaked into manuscript")

    package_manifest = json.loads((package / "PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))
    require(package_manifest["academic_paper_skills_revision"] != "", "skill revision missing")
    require(package_manifest["canonical_science"]["sha256"] == sha256_file(canonical), "canonical manuscript hash mismatch")
    require(package_manifest["canonical_claim_ledger"]["sha256"] == sha256_file(ledger), "canonical ledger hash mismatch")
    require(package_manifest["reader_pdf"]["sha256"] == sha256_file(pdf), "PDF package-manifest hash mismatch")
    verify_review_receipt_disposition(
        repo=repo,
        closure=closure,
        package=package,
        submission=submission,
    )
    review_provenance = package / REVIEW_PROVENANCE
    require(
        package_manifest["independent_review_provenance"]["sha256"]
        == sha256_file(review_provenance),
        "independent-review provenance package-manifest hash mismatch",
    )
    integrity_ledger = package / "RESEARCH_INTEGRITY_LEDGER.json"
    integrity_report = package / "RESEARCH_INTEGRITY_REPORT.json"
    require(integrity_ledger.is_file(), "research-integrity ledger missing")
    require(integrity_report.is_file(), "research-integrity report missing")
    require(
        package_manifest["research_integrity_ledger"]["sha256"] == sha256_file(integrity_ledger),
        "research-integrity ledger package-manifest hash mismatch",
    )
    require(
        package_manifest["research_integrity_report"]["sha256"] == sha256_file(integrity_report),
        "research-integrity report package-manifest hash mismatch",
    )
    integrity_state = json.loads(integrity_ledger.read_text(encoding="utf-8"))
    for receipt in integrity_state.get("evidence_receipts", []):
        pointer = receipt.get("artifact_pointer")
        if not pointer:
            continue
        pointer_path = str(pointer).split("#", 1)[0]
        require(
            (package / pointer_path).exists(),
            f"research-integrity artifact pointer missing: {pointer}",
        )

    source_count = verify_archive(
        submission / SOURCE_ZIP, package_manifest["source_archive"], source
    )
    artifact_count = verify_archive(
        submission / ARTIFACT_ZIP, package_manifest["artifact_archive"], artifact
    )

    replay_recipe = artifact / (
        "papers/orion-03-typed-merge-falsification/evidence/"
        "round2-x509-truststore/PINNED_OPENSSL_BUILD.md"
    )
    require(replay_recipe.is_file(), "pinned OpenSSL replay recipe missing")
    replay_text = replay_recipe.read_text(encoding="utf-8")
    logical_replay_text = replay_text.replace("\\\n", " ")
    unsafe_replays = [
        line.strip()
        for line in logical_replay_text.splitlines()
        if line.strip().startswith("python run_round2.py")
        and "--check-final" not in line
    ]
    require(
        not unsafe_replays,
        "replay recipe contains a receipt-overwriting evaluator invocation",
    )
    for required_replay_guard in (
        'mkdir "$replay/frozen" "$replay/run"',
        'ROUND2_RESULTS_V2.json COST_ROUND2_V2.json "$replay/frozen/"',
        'cp generate_tasks.py run_round2.py "$replay/run/"',
        'ln -s "$evidence_dir/third_party" "$replay/run/third_party"',
        'cd "$replay/run"',
        'cmp "$replay/frozen/TASK_MANIFEST_V2.json" TASK_MANIFEST_V2.json',
        'cmp "$replay/frozen/UPSTREAM_TABLE_V2.json" UPSTREAM_TABLE_V2.json',
        '--results "$replay/frozen/ROUND2_RESULTS_V2.json"',
        '--cost-out "$replay/frozen/COST_ROUND2_V2.json"',
        'trap cleanup EXIT',
        'rm -rf "$replay"',
    ):
        require(
            required_replay_guard in replay_text,
            f"replay recipe guard missing: {required_replay_guard}",
        )
    require(
        'cp "$replay/' not in replay_text,
        "replay cleanup can copy disposable bytes into published receipts",
    )

    # The top-level checksum list binds every file other than itself.
    checksum_lines = (package / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
    checksum_paths: set[str] = set()
    for line in checksum_lines:
        digest, rel = line.split("  ", 1)
        path = package / rel
        require(path.is_file(), f"SHA256SUMS path missing: {rel}")
        require(sha256_file(path) == digest, f"SHA256SUMS mismatch: {rel}")
        checksum_paths.add(rel)
    actual_paths = {
        path.relative_to(package).as_posix()
        for path in package.rglob("*")
        if path.is_file() and path != package / "SHA256SUMS"
    }
    require(checksum_paths == actual_paths, "SHA256SUMS membership mismatch")

    release_manifest = package / "PUBLICATION_RELEASE_MANIFEST.json"
    release = json.loads(release_manifest.read_text(encoding="utf-8"))
    verify_historical_candidate_hashes(release)
    require(release["requested_state"] == "submission_ready", "wrong release state")
    authoritative = [c for c in release["manuscript_candidates"] if c["disposition"] == "authoritative"]
    require(len(authoritative) == 1, "reader authority is ambiguous")
    require(authoritative[0]["sha256"] == f"sha256:{sha256_file(pdf)}", "reader authority hash mismatch")
    candidates = {str(c["manuscript_id"]): c for c in release["manuscript_candidates"]}
    expected_candidate_ids = {
        "ORION-03-JAR-20260831",
        "ORION-03-V3-EDITABLE-SOURCE",
        "ORION-03-V2",
        "ORION-03-V3-PIPELINE-DRAFT",
        "ORION-03-BASE-V3-SOURCE",
        "ORION-03-HISTORICAL-JOURNAL-SOURCE",
        "ORION-03-HISTORICAL-JOURNAL-PDF",
        "ORION-03-HISTORICAL-MANUSCRIPT-BUILD-PDF",
        "ORION-03-HISTORICAL-SUBMISSION-PDF",
        "ORION-03-SOURCE-TREE-BUILD-DERIVATIVE",
    }
    require(set(candidates) == expected_candidate_ids, "plausible-manuscript disposition set drift")
    require(
        all(candidates[cid]["disposition"] != "authoritative" for cid in expected_candidate_ids - {"ORION-03-JAR-20260831"}),
        "a predecessor or build derivative retained reader authority",
    )
    release_ledger = json.loads((package / "CLAIM_LEDGER_RELEASE.json").read_text(encoding="utf-8"))
    require(release_ledger["manuscript_fingerprint"] == f"sha256:{sha256_file(pdf)}", "release-ledger PDF binding mismatch")
    require(release_ledger["canonical_claim_ledger"]["sha256"] == f"sha256:{sha256_file(ledger)}", "release-ledger scientific-ledger binding mismatch")

    release_decision = json.loads((package / "RELEASE_DECISION.json").read_text(encoding="utf-8"))
    require(release_decision["manifest_sha256"] == sha256_file(release_manifest), "release-decision manifest hash mismatch")
    require(release_decision["manifest_byte_count"] == release_manifest.stat().st_size, "release-decision manifest size mismatch")

    skill_root = args.skill_root.resolve()
    research_verifier = (
        skill_root / "skills" / "nature-shared" / "scripts" / "verify_research_integrity.py"
    )
    require(research_verifier.is_file(), "skill research-integrity verifier path missing")
    skill_head = run(["git", "rev-parse", "HEAD"], skill_root).strip()
    require(
        skill_head == package_manifest["academic_paper_skills_revision"],
        "academic-paper-skills checkout does not match the package revision",
    )
    integrity_output = run(
        [
            sys.executable,
            str(research_verifier),
            str(integrity_ledger),
            "--manuscript",
            str(pdf),
            "--max-status-age-days",
            "30",
            "--pretty",
        ],
        package,
    )
    integrity_rerun = json.loads(integrity_output)
    require(integrity_rerun["decision"] == "PASS", f"research-integrity verifier failed: {integrity_output}")
    require(
        json.loads(integrity_report.read_text(encoding="utf-8"))["decision"] == "PASS",
        "packaged research-integrity report is non-passing",
    )

    # Compile twice from independent extracted source archives and compare final bytes.
    with tempfile.TemporaryDirectory(prefix="orion03-rebuild-") as temp_name:
        rebuild_hashes = []
        for index in (1, 2):
            rebuild = Path(temp_name) / f"build-{index}"
            rebuild.mkdir()
            with zipfile.ZipFile(submission / SOURCE_ZIP) as archive:
                archive.extractall(rebuild)
            run(["sh", "build.sh"], rebuild)
            rebuilt_pdf = rebuild / "main.pdf"
            require(rebuilt_pdf.is_file(), "rebuild did not produce PDF")
            rebuild_hashes.append(sha256_file(rebuilt_pdf))
            log = (rebuild / "main.log").read_text(encoding="utf-8", errors="replace")
            for forbidden in ("Undefined control sequence", "Citation `", "Reference `", "Overfull \\hbox", "Overfull \\vbox"):
                require(forbidden not in log, f"render log contains {forbidden}")
        require(rebuild_hashes[0] == rebuild_hashes[1] == sha256_file(pdf), "two-pass PDF rebuild is not byte-identical")

    fd, pdf_text_name = tempfile.mkstemp(prefix="orion03-pdf-", suffix=".txt")
    os.close(fd)
    pdf_text_path = Path(pdf_text_name)
    try:
        run(["pdftotext", str(pdf), str(pdf_text_path)], package)
        pdf_text = pdf_text_path.read_text(encoding="utf-8", errors="replace")
    finally:
        pdf_text_path.unlink(missing_ok=True)
    normalized_pdf_text = re.sub(r"\s+", " ", pdf_text)
    for required_pdf_text in (
        "Typed Evidence Licenses for Fail-Closed Nonpromotion",
        "Sze Chun Yiu",
        "Independent Researcher",
        "Cedar multi-policy fixtures",
        "186 of 191",
        "Materials availability",
        "References",
    ):
        require(required_pdf_text in normalized_pdf_text, f"reader PDF text missing: {required_pdf_text}")
    require("??" not in normalized_pdf_text, "unresolved marker in reader PDF")

    pdfinfo = run(["pdfinfo", str(pdf)], package)
    require("Title:" in pdfinfo and "Typed Evidence Licenses" in pdfinfo, "PDF title metadata missing")
    require("Author:" in pdfinfo and "Sze Chun Yiu" in pdfinfo, "PDF author metadata missing")
    pages_match = re.search(r"^Pages:\s+(\d+)", pdfinfo, re.MULTILINE)
    require(pages_match is not None and int(pages_match.group(1)) > 0, "PDF page count invalid")

    tex = (source / "main.tex").read_text(encoding="utf-8")
    require("\\section{1." not in tex and "\\subsection{1." not in tex, "doubled heading numbering remains")
    require("\\backmatter" in tex, "Springer backmatter marker missing")
    bbl = (source / "main.bbl").read_text(encoding="utf-8")
    require(bbl.count("\\bibitem") == 16, "unexpected resolved-reference count")

    # Scientific executable checks that do not require optional native
    # toolchains. The ZIP is extracted outside the ORION project so `uv` does
    # not synchronize against a repository environment or a stale `.venv`.
    run([sys.executable, "-m", "unittest", "-v", "test_evidence_license_evaluator.py"], paper)
    run(
        [
            "uv", "run", "--no-project", "--with", "pytest", "python", "-m", "pytest",
            "packages/typed-merge-evaluator/tests/test_typed_merge_evaluator.py", "-q",
        ],
        repo,
    )
    run(
        [
            sys.executable,
            "papers/orion-03-typed-merge-falsification/evidence/round1-cedar-multipolicy/verify_round1.py",
            "--check-final",
        ],
        repo,
    )
    run(
        [sys.executable, "papers/orion-03-typed-merge-falsification/evidence/current-main-revalidation-v1/check_orion03_round2_binding_v1.py"],
        repo,
    )

    with tempfile.TemporaryDirectory(prefix="orion03-artifact-test-") as temp_name:
        extracted = Path(temp_name) / "artifact"
        extracted.mkdir()
        with zipfile.ZipFile(submission / ARTIFACT_ZIP) as archive:
            archive.extractall(extracted)
        packaged_tests = run(
            [
                "uv", "run", "--no-project", "--with", "pytest", "python", "-m", "pytest",
                "packages/typed-merge-evaluator/tests/test_typed_merge_evaluator.py", "-q",
            ],
            extracted,
        )
        require("32 passed" in packaged_tests, "packaged typed-merge suite did not run all 32 tests")
        packaged_paper = extracted / "papers" / "orion-03-typed-merge-falsification"
        run(
            [sys.executable, "-m", "unittest", "-v", "test_evidence_license_evaluator.py"],
            packaged_paper,
        )
        packaged_root = extracted / "packages" / "typed-merge-evaluator"
        example_paths = sorted(
            str(path.relative_to(packaged_root))
            for path in (packaged_root / "examples").glob("*/*.json")
        )
        require(len(example_paths) == 13, f"unexpected packaged example count: {len(example_paths)}")
        example_output = run(
            [sys.executable, "-m", "typed_merge_evaluator", *example_paths],
            packaged_root,
        )
        require(example_output.count("PASS ") == 13, "not all 13 packaged instances passed")
        binding_output = run(
            [
                sys.executable,
                "papers/orion-03-typed-merge-falsification/evidence/current-main-revalidation-v1/check_orion03_round2_binding_v1.py",
            ],
            extracted,
        )
        require('\"verified\": 269' in binding_output, "packaged Round-2 binding count drift")
        binding = json.loads(
            (
                packaged_paper
                / "evidence"
                / "round2-x509-truststore"
                / "SOURCE_BINDING_V2.json"
            ).read_text(encoding="utf-8")
        )
        require(len(binding["vendored_files"]) == 252, "packaged OpenSSL selected-file count drift")

    report = {
        "decision": "PASS",
        "paper": "ORION-03",
        "reader_pdf_sha256": sha256_file(pdf),
        "reader_pdf_pages": int(pages_match.group(1)),
        "abstract_words": abstract_words,
        "keyword_count": keyword_count,
        "source_archive_members": source_count,
        "artifact_archive_members": artifact_count,
        "skill_revision": package_manifest["academic_paper_skills_revision"],
        "research_integrity_claims": integrity_rerun["summary"]["claims"],
        "research_integrity_sources": integrity_rerun["summary"]["sources"],
        "does_not_certify": [
            "external_replication",
            "external_peer_review",
            "portal_upload",
            "journal_acceptance",
        ],
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except VerificationError as exc:
        print(json.dumps({"decision": "BLOCKED", "error": str(exc)}, indent=2), file=sys.stderr)
        raise SystemExit(1)
