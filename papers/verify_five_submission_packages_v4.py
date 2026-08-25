#!/usr/bin/env python3
"""Verify the five corrected journal and arXiv manuscript packages."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PAPERS = ROOT / "papers"
AUTHOR = "Sze Chun Yiu"
EMAIL = "sze-chun.yiu@fysik.su.se"

PACKAGES = {
    "A": (
        PAPERS / "theory-A-multitag-constraint-rank",
        "Zero-Sum Deletion Normal Forms for a Multi-Tag Pauli Grammar",
        "Zero-Sum_Deletion_Normal_Forms_for_a_Multi-Tag_Pauli_Grammar",
    ),
    "B": (
        PAPERS / "theory-B-certificate-complexity",
        "Abstract Zero-Sum Deletion Complexity and Support-One Normalization in a Pauli Model",
        "Abstract_Zero-Sum_Deletion_Complexity_and_Support-One_Normalization_in_a_Pauli_Model",
    ),
    "C": (
        PAPERS / "theory-C-low-order-information",
        "Low-Order Decision Certificates and Value Limits in a Pauli-String Partition Model",
        "Low-Order_Decision_Certificates_and_Value_Limits_in_a_Pauli-String_Partition_Model",
    ),
    "D": (
        PAPERS / "theory-D-falsification-authority",
        "Typed Evidence Licenses for Finite Positive Rule Graphs",
        "Typed_Evidence_Licenses_for_Finite_Positive_Rule_Graphs",
    ),
    "N": (
        PAPERS / "nonquantum-c5cubed-davenport",
        r"Conditional Davenport Corridors and Saturated Obstructions in \(C_5^3\)",
        "Conditional_Davenport_Corridors_and_Saturated_Obstructions_in_C5_Cubed",
    ),
}

LEGACY_STEMS = {
    "A": ("Zero-Sum_Deletion_Normal_Forms_for_Multi-Tag_Quantum_Compilation",),
    "B": (
        "Zero-Sum_Deletion_Certificates_versus_Intrinsic_Support_in_Quantum_Compilation",
        "Zero-Sum_Deletion_Certificates_versus_Intrinsic_Support_in_Pauli_Compiler_Models",
    ),
    "C": ("Low-Order_Decision_Certificates_and_Value-Estimation_Limits_in_Structured_Quantum_Compilation",),
    "D": ("Typed_Evidence_Licenses_for_Finite_Positive_Rule_Graphs",),
    "N": ("Conditional_Width-One_Bounds_for_Generalized_Davenport_Constants_of_C5_Cubed",),
}

ANCILLARY_EXPECTED = {
    "A": {
        "anc/LICENSE_CODE.txt",
        "anc/README.md",
        "anc/finite_records.json",
    },
    "B": {
        "anc/LICENSE_CODE.txt",
        "anc/README.md",
        "anc/certificate_control_records.json",
        "anc/verify_dependent_triple_lemmas.py",
    },
    "C": {
        "anc/LICENSE_CODE.txt",
        "anc/README.md",
        "anc/verify_public_claims.py",
    },
    "D": {
        "anc/LICENSE_CODE.txt",
        "anc/README.md",
        "anc/evidence_license_evaluator.py",
        "anc/evidence_license_schema.json",
        "anc/test_evidence_license_evaluator.py",
        "anc/examples/bounded_frontier.json",
        "anc/examples/forecast_falsification.json",
        "anc/examples/query_specific_falsification.json",
    },
    "N": {
        "anc/LICENSE_CODE.txt",
        "anc/README.md",
        "anc/bounded_search_expected.json",
        "anc/support_eight_search.c",
        "anc/support_nine_search.c",
        "anc/support_ten_search_bytes.c",
        "anc/support_ten_search_u128.c",
        "anc/verify_bounded_search.py",
    },
}

FORBIDDEN_MANUSCRIPT_SURFACE = re.compile(
    r"\bunified[ -]calculus\b|\buniversal[ -]calculus\b|workflow cut|"
    r"scientific cut|publication decision|pull request|PR #[0-9]+|/workspace/|"
    r"\bdevelopment/|\bORION\b|\bR6[A-Z0-9_-]*\b|\bQG[A-Z0-9_-]*\b|"
    r"orion\.invalid|registered product|Author information to be supplied|\[AUTHOR",
    re.IGNORECASE,
)

FORBIDDEN_PUBLIC_ANCILLARY_SURFACE = re.compile(
    r"\bORION\b|\bR6[A-Z0-9_-]*\b|\bQG[A-Z0-9_-]*\b|\bX1K[A-Z0-9_-]*\b|"
    r"/workspace/|\bdevelopment/|\bresearch/|"
    r"FORMAL_COMPONENTS_ONLY_NO_UNIFIED_CALCULUS|orion\.invalid",
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


def abstract_from_markdown(text: str) -> str:
    return text.split("## Abstract", 1)[1].split("**Keywords:**", 1)[0].strip()


def abstract_has_display_math(text: str) -> bool:
    return any(token in text for token in (r"\[", "$$", r"\begin{equation", r"\begin{align"))


def main() -> int:
    checks: dict[str, bool] = {}
    details: dict[str, object] = {}

    manuscripts = {
        key: (directory / "MANUSCRIPT_V3_PIPELINE.md").read_text(encoding="utf-8")
        for key, (directory, _title, _stem) in PACKAGES.items()
    }
    controls = {
        key: (directory / "PIPELINE_CONTROL_V3.md").read_text(encoding="utf-8")
        for key, (directory, _title, _stem) in PACKAGES.items()
    }

    checks["five_manuscripts_present"] = len(manuscripts) == 5
    checks["closure_constraint_preserved"] = all(
        "FORMAL_COMPONENTS_ONLY_NO_UNIFIED_CALCULUS" in text
        for text in controls.values()
    )
    checks["precise_titles_match"] = all(
        text.splitlines()[0] == f"# {title}"
        for key, text in manuscripts.items()
        for _directory, title, _stem in (PACKAGES[key],)
    )

    surface_hits = {
        key: sorted({match.group(0) for match in FORBIDDEN_MANUSCRIPT_SURFACE.finditer(text)})
        for key, text in manuscripts.items()
    }
    surface_hits = {key: hits for key, hits in surface_hits.items() if hits}
    checks["manuscript_surface_has_no_internal_labels"] = not surface_hits
    details["surface_hits"] = surface_hits

    abstracts = {key: abstract_from_markdown(text) for key, text in manuscripts.items()}
    abstract_lengths = {key: len(text) for key, text in abstracts.items()}
    checks["abstracts_use_inline_math_only"] = all(
        not abstract_has_display_math(text) for text in abstracts.values()
    )
    checks["abstracts_fit_arxiv_limit"] = all(length <= 1920 for length in abstract_lengths.values())
    checks["abstracts_fit_internal_1750_target"] = all(length <= 1750 for length in abstract_lengths.values())
    details["abstract_character_counts"] = abstract_lengths

    checks["binary_rank_contradiction_removed"] = (
        r"\operatorname{zsf}(H; A)=d" in manuscripts["A"]
        and "strict alphabet-versus-realized-rank refinement is claimed" not in manuscripts["A"]
        and r"zsf}(H_R; A_R)<" not in manuscripts["A"]
    )
    checks["paper_a_binary_equality_explained"] = (
        re.search(r"spanning set.*contains a basis", manuscripts["A"]) is not None
        or "contains a basis" in manuscripts["A"]
    )
    checks["unified_calculus_claim_absent"] = all(
        not re.search(r"unified[ -]calculus|universal[ -]calculus", text, re.IGNORECASE)
        for text in manuscripts.values()
    )
    checks["data_code_availability_in_all_five"] = all(
        "## Data and code availability" in text for text in manuscripts.values()
    )
    checks["keywords_in_all_five"] = all("**Keywords:**" in text for text in manuscripts.values())

    inventories: dict[str, list[str]] = {}
    pdf_pages: dict[str, int] = {}
    pdf_integrity: dict[str, dict[str, bool]] = {}
    archive_integrity: dict[str, dict[str, bool]] = {}
    generated_surface: dict[str, dict[str, bool]] = {}

    for key, (directory, title, stem) in PACKAGES.items():
        submission = directory / "submission"
        expected = {
            "README.md",
            "cover_letter.md",
            "submission_checklist.md",
            f"{stem}.pdf",
            f"{stem}.tex",
            f"{stem}_journal_source.zip",
            f"{stem}_arxiv_source.zip",
        }
        names = {path.name for path in submission.iterdir() if path.is_file()}
        inventories[key] = sorted(names)
        checks[f"package_{key}_expected_files_present"] = expected <= names
        checks[f"package_{key}_legacy_title_files_absent"] = (
            all(
                legacy == stem
                or not any(
                    name in names
                    for name in {
                        f"{legacy}.pdf",
                        f"{legacy}.tex",
                        f"{legacy}_journal_source.zip",
                        f"{legacy}_arxiv_source.zip",
                    }
                )
                for legacy in LEGACY_STEMS[key]
            )
        )

        pdf = submission / f"{stem}.pdf"
        info = run(["pdfinfo", str(pdf)])
        page_match = re.search(r"^Pages:\s+(\d+)$", info.stdout, re.MULTILINE)
        pages = int(page_match.group(1)) if page_match else 0
        pdf_pages[key] = pages
        pdf_text = run(["pdftotext", str(pdf), "-"])
        tail = pdf.read_bytes()[-1024:] if pdf.is_file() else b""
        pdf_integrity[key] = {
            "pdfinfo": info.returncode == 0,
            "pdftotext": pdf_text.returncode == 0,
            "eof": b"%%EOF" in tail,
            "author": AUTHOR in pdf_text.stdout,
            "email": EMAIL in pdf_text.stdout,
            "no_placeholder": "Author information to be supplied" not in pdf_text.stdout,
            "no_internal_labels": FORBIDDEN_MANUSCRIPT_SURFACE.search(pdf_text.stdout) is None,
        }

        tex = submission / f"{stem}.tex"
        tex_text = tex.read_text(encoding="utf-8")
        tex_abstract = tex_text.split(r"\begin{abstract}", 1)[1].split(r"\end{abstract}", 1)[0]
        generated_surface[key] = {
            "true_abstract_environment": r"\begin{abstract}" in tex_text
            and r"\section{Abstract}" not in tex_text,
            "abstract_inline_math_only": not abstract_has_display_math(tex_abstract),
            "author": AUTHOR in tex_text,
            "email": EMAIL in tex_text,
            "title": title.replace(r"\(", "").replace(r"\)", "")[:30] in tex_text.replace("$", ""),
            "no_internal_labels": FORBIDDEN_MANUSCRIPT_SURFACE.search(tex_text) is None,
            "unicode_macro_valid": r"\DeclareUnicodeCharacter{220E}" in tex_text,
        }

        archive_integrity[key] = {}
        for kind in ("journal", "arxiv"):
            archive_path = submission / f"{stem}_{kind}_source.zip"
            test = run(["unzip", "-t", str(archive_path)])
            archive_integrity[key][f"{kind}_zip_valid"] = test.returncode == 0
            with zipfile.ZipFile(archive_path) as archive:
                archive_names = set(archive.namelist())
                archive_surface_hits: dict[str, list[str]] = {}
                ancillary_surface_hits: dict[str, list[str]] = {}
                for name in archive_names:
                    is_reader_surface = name in {
                        "main.tex",
                        "README.md",
                        "cover_letter.md",
                        "submission_checklist.md",
                    }
                    is_public_ancillary = (
                        name.startswith("anc/")
                        and not name.endswith("/")
                        and name != "anc/LICENSE_CODE.txt"
                    )
                    if not is_reader_surface and not is_public_ancillary:
                        continue
                    try:
                        archive_text = archive.read(name).decode("utf-8")
                    except UnicodeDecodeError:
                        continue
                    if is_reader_surface:
                        hits = sorted(
                            {
                                match.group(0)
                                for match in FORBIDDEN_MANUSCRIPT_SURFACE.finditer(
                                    archive_text
                                )
                            }
                        )
                        if hits:
                            archive_surface_hits[name] = hits
                    if is_public_ancillary:
                        hits = sorted(
                            {
                                match.group(0)
                                for match in FORBIDDEN_PUBLIC_ANCILLARY_SURFACE.finditer(
                                    archive_text
                                )
                            }
                        )
                        if hits:
                            ancillary_surface_hits[name] = hits
            actual_ancillary_files = {
                name
                for name in archive_names
                if name.startswith("anc/") and not name.endswith("/")
            }
            archive_integrity[key][f"{kind}_has_main_tex"] = "main.tex" in archive_names
            archive_integrity[key][f"{kind}_has_ancillary_license"] = "anc/LICENSE_CODE.txt" in archive_names
            archive_integrity[key][f"{kind}_reader_surface_clean"] = not archive_surface_hits
            archive_integrity[key][f"{kind}_ancillary_inventory_exact"] = (
                actual_ancillary_files == ANCILLARY_EXPECTED[key]
            )
            archive_integrity[key][f"{kind}_ancillary_surface_clean"] = (
                not ancillary_surface_hits
            )
            archive_integrity[key][f"{kind}_has_no_compiled_cache"] = not any(
                "__pycache__" in name or name.endswith(".pyc")
                for name in archive_names
            )
            if kind == "arxiv":
                archive_integrity[key]["arxiv_excludes_editor_files"] = not any(
                    name in archive_names
                    for name in ("cover_letter.md", "submission_checklist.md", "README.md")
                )

    checks["all_pdf_integrity_checks_pass"] = all(
        all(result.values()) for result in pdf_integrity.values()
    )
    checks["all_pdf_page_counts_plausible"] = all(4 <= pages <= 25 for pages in pdf_pages.values())
    checks["all_generated_tex_surface_checks_pass"] = all(
        all(result.values()) for result in generated_surface.values()
    )
    checks["all_source_archives_valid_and_scoped"] = all(
        all(result.values()) for result in archive_integrity.values()
    )
    details["package_inventory"] = inventories
    details["pdf_pages"] = pdf_pages
    details["pdf_integrity"] = pdf_integrity
    details["generated_surface"] = generated_surface
    details["archive_integrity"] = archive_integrity

    d_tests = run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            str(PACKAGES["D"][0]),
            "-p",
            "test_*.py",
        ]
    )
    checks["paper_d_nine_tests_pass"] = d_tests.returncode == 0 and "Ran 9 tests" in d_tests.stderr
    details["paper_d_test_summary"] = d_tests.stderr.strip().splitlines()[-4:]

    schema = json.loads((PACKAGES["D"][0] / "evidence_license_schema.json").read_text())
    checks["paper_d_schema_has_no_placeholder_uri"] = "orion.invalid" not in json.dumps(schema)
    checks["paper_d_structural_semantic_contract_documented"] = (
        set(schema["required"]) == {"version", "licenses", "claims", "rules", "refutations"}
        and len(schema.get("x-semanticValidation", [])) == 4
        and "$comment" in schema
    )

    r2 = run([sys.executable, str(PAPERS / "verify_five_theory_hardening_r2.py")])
    r2_result = json.loads(r2.stdout) if r2.stdout else {}
    checks["inherited_r2_scientific_gates_pass"] = r2.returncode == 0 and r2_result.get("all_checks") is True

    r3 = run([sys.executable, str(PAPERS / "verify_five_publication_pipeline_r3.py")])
    r3_result = json.loads(r3.stdout) if r3.stdout else {}
    checks["inherited_r3_scientific_gates_pass"] = r3.returncode == 0 and r3_result.get("all_checks") is True

    build_script = PAPERS / "build_five_submission_packages_v4.sh"
    checks["reproducible_build_script_executable"] = build_script.is_file() and os.access(build_script, os.X_OK)

    checksum_file = PAPERS / "FIVE_PAPER_ARXIV_CHECKSUMS_V7.sha256"
    checksum_result = run(["sha256sum", "--check", str(checksum_file)]) if checksum_file.is_file() else None
    checks["v7_checksums_present_and_match"] = checksum_result is not None and checksum_result.returncode == 0
    details["checksum_summary"] = (
        checksum_result.stdout.strip().splitlines() if checksum_result is not None else []
    )

    output = {
        "schema": "orion.five-paper-mechanical-packages-v7.v1",
        "all_checks": all(checks.values()),
        "terminal_state": "MECHANICAL_PACKAGE_CHECKS_ONLY_NO_SCIENTIFIC_READINESS_AUTHORITY",
        "checks": checks,
        "details": details,
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if output["all_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
