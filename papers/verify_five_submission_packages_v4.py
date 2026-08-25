#!/usr/bin/env python3
"""Verify the five ORION V4 journal-submission packages without network access."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PAPERS = ROOT / "papers"

PACKAGES = {
    "A": PAPERS / "theory-A-multitag-constraint-rank",
    "B": PAPERS / "theory-B-certificate-complexity",
    "C": PAPERS / "theory-C-low-order-information",
    "D": PAPERS / "theory-D-falsification-authority",
    "N": PAPERS / "nonquantum-c5cubed-davenport",
}

REQUIRED_SUBMISSION_FILES = {
    "README.md",
    "cover_letter.md",
    "main.pdf",
    "main.tex",
    "source.zip",
    "submission_checklist.md",
}

FORBIDDEN_MANUSCRIPT_SURFACE = re.compile(
    r"unified[ -]calculus|universal[ -]calculus|workflow cut|scientific cut|"
    r"publication decision|pull request|PR #[0-9]+|/workspace/|development/",
    re.IGNORECASE,
)


def run(command: list[str], *, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def main() -> int:
    checks: dict[str, bool] = {}
    details: dict[str, object] = {}

    manuscript_text = {
        key: (directory / "MANUSCRIPT_V3_PIPELINE.md").read_text(encoding="utf-8")
        for key, directory in PACKAGES.items()
    }
    control_text = {
        key: (directory / "PIPELINE_CONTROL_V3.md").read_text(encoding="utf-8")
        for key, directory in PACKAGES.items()
    }

    checks["five_manuscripts_present"] = len(manuscript_text) == 5
    checks["closure_frozen_in_five_controls"] = all(
        "FORMAL_COMPONENTS_ONLY_NO_UNIFIED_CALCULUS" in text
        for text in control_text.values()
    )

    surface_hits = {
        key: sorted(set(match.group(0) for match in FORBIDDEN_MANUSCRIPT_SURFACE.finditer(text)))
        for key, text in manuscript_text.items()
    }
    surface_hits = {key: hits for key, hits in surface_hits.items() if hits}
    checks["submission_manuscript_surface_clean"] = not surface_hits
    details["surface_hits"] = surface_hits

    checks["incorrect_freeze_schmid_doi_absent"] = all(
        "10.1016/j.disc.2010.07.032" not in text for text in manuscript_text.values()
    )
    checks["correct_freeze_schmid_doi_present_twice"] = sum(
        text.count("10.1016/j.disc.2010.07.028") for text in manuscript_text.values()
    ) == 2
    checks["stale_tare_title_absent"] = (
        "Without Ancilla State Preparation" not in manuscript_text["A"]
    )
    checks["data_code_availability_in_all_five"] = all(
        "## Data and code availability" in text for text in manuscript_text.values()
    )
    checks["keywords_in_all_five"] = all("**Keywords:**" in text for text in manuscript_text.values())

    package_inventory = {}
    pdf_pages = {}
    pdf_integrity = {}
    archive_integrity = {}
    generated_surface = {}
    for key, directory in PACKAGES.items():
        submission = directory / "submission"
        names = {path.name for path in submission.iterdir() if path.is_file()}
        package_inventory[key] = sorted(names)

        pdf = submission / "main.pdf"
        info = run(["pdfinfo", str(pdf)])
        page_match = re.search(r"^Pages:\s+(\d+)$", info.stdout, re.MULTILINE)
        pages = int(page_match.group(1)) if page_match else 0
        pdf_pages[key] = pages

        text_result = run(["pdftotext", str(pdf), "-"])
        tail = pdf.read_bytes()[-1024:]
        pdf_integrity[key] = {
            "pdfinfo": info.returncode == 0,
            "pdftotext": text_result.returncode == 0,
            "eof": b"%%EOF" in tail,
            "author_placeholder": text_result.stdout.count(
                "Author information to be supplied before submission"
            ) == 1,
        }

        archive = run(["unzip", "-t", str(submission / "source.zip")])
        archive_integrity[key] = archive.returncode == 0
        generated_tex = (submission / "main.tex").read_text(encoding="utf-8")
        generated_surface[key] = (
            "\\textbackslash DeclareUnicodeCharacter" not in generated_tex
            and r"\(C\_5\^3\)" not in generated_tex
        )

    checks["all_submission_files_present"] = all(
        REQUIRED_SUBMISSION_FILES <= set(names) for names in package_inventory.values()
    )
    checks["paper_d_artifact_archive_present"] = (
        PACKAGES["D"] / "submission" / "artifact.zip"
    ).is_file()
    checks["all_pdf_integrity_checks_pass"] = all(
        all(result.values()) for result in pdf_integrity.values()
    )
    checks["all_pdf_page_counts_plausible"] = all(4 <= pages <= 12 for pages in pdf_pages.values())
    checks["all_source_archives_valid"] = all(archive_integrity.values())
    checks["generated_tex_surface_clean"] = all(generated_surface.values())
    details["package_inventory"] = package_inventory
    details["pdf_pages"] = pdf_pages
    details["pdf_integrity"] = pdf_integrity
    details["archive_integrity"] = archive_integrity

    d_tests = run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            str(PACKAGES["D"]),
            "-p",
            "test_*.py",
        ]
    )
    checks["paper_d_nine_tests_pass"] = d_tests.returncode == 0 and "Ran 9 tests" in d_tests.stderr
    details["paper_d_test_summary"] = d_tests.stderr.strip().splitlines()[-4:]

    schema = json.loads((PACKAGES["D"] / "evidence_license_schema.json").read_text())
    checks["paper_d_structural_semantic_contract_documented"] = (
        set(schema["required"]) == {"version", "licenses", "claims", "rules", "refutations"}
        and len(schema.get("x-semanticValidation", [])) == 4
        and "$comment" in schema
    )

    r3 = run([sys.executable, str(PAPERS / "verify_five_publication_pipeline_r3.py")])
    r3_result = json.loads(r3.stdout) if r3.stdout else {}
    checks["inherited_r3_scientific_gates_pass"] = r3.returncode == 0 and r3_result.get("all_checks") is True

    build_script = PAPERS / "build_five_submission_packages_v4.sh"
    checks["reproducible_build_script_executable"] = build_script.is_file() and os.access(
        build_script, os.X_OK
    )
    checks["v4_control_and_reference_reports_present"] = all(
        (PAPERS / name).is_file()
        for name in (
            "FIVE_PAPER_SUBMISSION_CONTROL_V4_2026-08-25.md",
            "FIVE_PAPER_REFERENCE_VERIFICATION_V4_2026-08-25.md",
        )
    )
    checksum_result = run(
        ["sha256sum", "--check", str(PAPERS / "FIVE_PAPER_SUBMISSION_CHECKSUMS_V4.sha256")]
    )
    checks["submission_package_checksums_match"] = checksum_result.returncode == 0
    details["checksum_summary"] = checksum_result.stdout.strip().splitlines()

    output = {
        "schema": "orion.five-paper-submission-packages-v4.v1",
        "all_checks": all(checks.values()),
        "terminal_state": "TECHNICALLY_PACKAGED_AUTHOR_SIGNOFF_REQUIRED",
        "checks": checks,
        "details": details,
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if output["all_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
