#!/usr/bin/env python3
"""Build or verify the deterministic ORION-13 Wave-1 review package."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path


SCRIPT = Path(__file__).resolve()
PAPER = SCRIPT.parents[1]
REPO = SCRIPT.parents[3]
MANUSCRIPT = PAPER / "manuscript"
OUTPUT = PAPER / "journal_package" / "wave1_current"
ZIP_TIME = (2026, 8, 28, 0, 0, 0)

STATIC_PACKAGE_FILES = (
    "COVER_LETTER.md",
    "AVAILABILITY_STATEMENT.md",
    "HUMAN_INPUTS_REQUIRED.md",
    "REVIEW_RESOURCES_README.md",
)

SOURCE_FILES = (
    "manuscript/main.tex",
    "manuscript/bibliography.bib",
    "manuscript/generate_tables.py",
    "manuscript/sections/00-abstract.tex",
    "manuscript/sections/06-results.tex",
    "manuscript/sections/07-limitations.tex",
    "manuscript/sections/08-conclusion.tex",
    "manuscript/sections/10-introduction.tex",
    "manuscript/sections/20-related-work.tex",
    "manuscript/sections/30-method.tex",
    "manuscript/sections/40-dataset.tex",
    "manuscript/sections/50-evaluation.tex",
    "manuscript/sections/60-availability.tex",
    "manuscript/tables/confirmatory_case_families.tex",
    "manuscript/tables/confirmatory_primary_results.tex",
    "scripts/build_wave1_package.py",
)

TEX_INPUT_FILES = (
    "manuscript/main.tex",
    "manuscript/bibliography.bib",
    "manuscript/sections/00-abstract.tex",
    "manuscript/sections/06-results.tex",
    "manuscript/sections/07-limitations.tex",
    "manuscript/sections/08-conclusion.tex",
    "manuscript/sections/10-introduction.tex",
    "manuscript/sections/20-related-work.tex",
    "manuscript/sections/30-method.tex",
    "manuscript/sections/40-dataset.tex",
    "manuscript/sections/50-evaluation.tex",
    "manuscript/sections/60-availability.tex",
    "manuscript/tables/confirmatory_case_families.tex",
    "manuscript/tables/confirmatory_primary_results.tex",
)

REVIEW_FILES = (
    "journal_package/wave1_current/REVIEW_RESOURCES_README.md",
    "REPRODUCE.md",
    "journal_package/LICENSE.md",
    "gold/PUBLIC_REFERENCE_SOURCE_REGISTRY_V1.json",
    "gold/adjudicated/public-reference-v1/PUBLIC_REFERENCE_FREEZE_MANIFEST_V1.json",
    "gold/adjudicated/public-reference-v1/PUBLIC_REFERENCE_GOLD_V1.jsonl",
    "gold/adjudicated/public-reference-v1.1-confirmatory/PUBLIC_REFERENCE_FREEZE_MANIFEST_V1.json",
    "gold/adjudicated/public-reference-v1.1-confirmatory/PUBLIC_REFERENCE_GOLD_V1.jsonl",
    "protocol/PUBLIC_REFERENCE_CONFIRMATORY_EXECUTION_V1.json",
    "evidence/public-reference-v1.1-confirmatory/CONFIRMATORY_ANALYSIS.json",
    "evidence/public-reference-v1.1-confirmatory/EXECUTION_MANIFEST.json",
    "evidence/public-reference-v1.1-confirmatory/SUMMARY.json",
    "evidence/public-reference-v1.1-confirmatory/SHA256SUMS",
    "evidence/coordinate-obstruction-v2/CONFIRMATORY_REPRODUCTION_RECEIPT.json",
    "evidence/coordinate-obstruction-v2/REPRODUCTION_RECEIPT_R0_REBIND_CORRECTION_2026-08-28.json",
    "evidence/coordinate-obstruction-v2/SHA256SUMS",
    "scripts/verify_confirmatory_independent.py",
    "editorial/INDEPENDENT_CONFIRMATORY_REPLAY.json",
    "manuscript/generate_tables.py",
    "manuscript/tables/confirmatory_case_families.tex",
    "manuscript/tables/confirmatory_primary_results.tex",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_record(path: Path, *, relative_to: Path) -> dict[str, object]:
    return {
        "path": str(path.relative_to(relative_to)),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
    }


def require_files(relative_paths: tuple[str, ...]) -> list[Path]:
    paths = [PAPER / item for item in relative_paths]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing package inputs: " + ", ".join(missing))
    return paths


def zip_files(destination: Path, paths: list[Path]) -> None:
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(paths, key=lambda item: str(item.relative_to(PAPER))):
            name = str(path.relative_to(PAPER))
            info = zipfile.ZipInfo(name, ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            mode = 0o755 if path.suffix == ".py" else 0o644
            info.external_attr = (mode & 0xFFFF) << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def pdf_pages(path: Path) -> int:
    output = subprocess.check_output(["pdfinfo", str(path)], text=True)
    for line in output.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise ValueError("pdfinfo did not report a page count")


def manifest(output: Path, source_paths: list[Path], review_paths: list[Path]) -> dict[str, object]:
    pdf = output / "manuscript.pdf"
    source_zip = output / "ORION13_SWJ_SOURCE.zip"
    review_zip = output / "ORION13_SWJ_REVIEW_RESOURCES.zip"
    artifacts = [
        pdf,
        source_zip,
        review_zip,
        *(output / name for name in STATIC_PACKAGE_FILES),
    ]
    tex_input_paths = require_files(TEX_INPUT_FILES)
    tex_input_closure = [file_record(path, relative_to=PAPER) for path in tex_input_paths]
    tex_input_digest = hashlib.sha256(
        json.dumps(tex_input_closure, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "schema_version": "orion.orion13.wave1-submission-manifest.v1",
        "paper_id": "ORION-13",
        "title": "Coordinate-Governed Mapping of Source-Local Scientific Projections",
        "primary_venue": "Semantic Web Journal",
        "fallback_venue": "Journal of Web Semantics",
        "article_type": "full paper",
        "scientific_terminal": "PASS_BOUNDED_STRUCTURED_MAPPING",
        "submission_terminal": "BLOCKED_BY_INTEGRITY_OR_COMPLIANCE",
        "submission_authorized": False,
        "readiness_judgments": {
            "top_tier_or_external_authority": "NOT_ESTABLISHED",
            "strong_specialist_submission": "BLOCKED_BY_INTEGRITY_OR_COMPLIANCE",
        },
        "claim_boundary": (
            "C5/C9 already-structured mapping only; all six observed comparator errors are polarity "
            "contrasts. No raw-text, expert-atlas, downstream, universal-coordinate, current-system "
            "superiority, external-replication, or cross-host claim."
        ),
        "author": {
            "name": "Sze Chun Yiu",
            "email": "sze-chun.yiu@fysik.su.se",
            "human_only_fields_open": [
                "affiliation",
                "ORCID",
                "funding",
                "conflicts",
                "contributions",
                "final acknowledgements",
            ],
        },
        "pdf": {
            **file_record(pdf, relative_to=output),
            "pages": pdf_pages(pdf),
            "source_pdf_sha256": sha256(MANUSCRIPT / "main.pdf"),
            "source_pdf_exact_byte_match": pdf.read_bytes() == (MANUSCRIPT / "main.pdf").read_bytes(),
            "template_compliance": False,
            "template_blocker": "official linked Sage LaTeX ZIP resolves to an HTML 404 page",
        },
        "artifacts": [file_record(path, relative_to=output) for path in artifacts],
        "tex_input_closure": tex_input_closure,
        "tex_input_closure_sha256": tex_input_digest,
        "source_closure": [file_record(path, relative_to=PAPER) for path in source_paths],
        "review_resource_closure": [file_record(path, relative_to=PAPER) for path in review_paths],
        "review_archive_url": None,
        "blockers": [
            {
                "id": "ORION13-B1",
                "class": "PUBLICATION_CRITERIA",
                "detail": "SWJ full-paper significance is not established by a 32-case polarity-localized comparison against a deliberately weak baseline.",
                "resolution": "fair same-universe current comparator, affirmative editor fit indication, or defensible retargeting",
            },
            {
                "id": "ORION13-B2",
                "class": "OPEN_SCIENCE",
                "detail": "No long-term stable immutable URL is bound to the exact review-resource ZIP.",
                "resolution": "deposit these exact bytes and record the stable URL without rebuilding the ZIP",
            },
            {
                "id": "ORION13-B3",
                "class": "TARGET_TEMPLATE",
                "detail": "The official linked Sage LaTeX template URL returns an HTML 404 artifact.",
                "resolution": "obtain a working current template or written editor guidance, then rebuild exact filing bytes",
            },
            {
                "id": "ORION13-B4",
                "class": "HUMAN_AUTHORSHIP_POLICY",
                "detail": "SWJ FAQ Q28 human-writing compliance cannot be attested by the editing system.",
                "resolution": "human rewrite/verification as needed plus exact assistance disclosure and author attestation",
            },
            {
                "id": "ORION13-B5",
                "class": "HUMAN_METADATA",
                "detail": "Affiliation and filing declarations are incomplete.",
                "resolution": "human author completes every field or explicitly marks it not applicable",
            },
        ],
        "round1_review_pdf_sha256": "b843d9ef8cd399c3e186e3a05edca582a2bd9de08f3c22d192b7187b42ac4c19",
        "skills_applied": [
            "nature-writing",
            "nature-polishing",
            "nature-figure",
            "nature-citation",
            "nature-academic-search",
            "nature-literature-pipeline",
            "nature-data",
            "nature-reviewer",
        ],
    }


def build(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    source_paths = require_files(SOURCE_FILES)
    review_paths = require_files(REVIEW_FILES)
    source_pdf = MANUSCRIPT / "main.pdf"
    if not source_pdf.is_file():
        raise FileNotFoundError("canonical manuscript PDF is missing")
    shutil.copyfile(source_pdf, output / "manuscript.pdf")
    zip_files(output / "ORION13_SWJ_SOURCE.zip", source_paths)
    zip_files(output / "ORION13_SWJ_REVIEW_RESOURCES.zip", review_paths)
    data = manifest(output, source_paths, review_paths)
    (output / "SUBMISSION_MANIFEST.json").write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    checksum_targets = [
        *(output / name for name in STATIC_PACKAGE_FILES),
        output / "manuscript.pdf",
        output / "ORION13_SWJ_SOURCE.zip",
        output / "ORION13_SWJ_REVIEW_RESOURCES.zip",
        output / "SUBMISSION_MANIFEST.json",
    ]
    lines = [f"{sha256(path)}  {path.name}" for path in sorted(checksum_targets, key=lambda x: x.name)]
    (output / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")


def verify() -> None:
    with tempfile.TemporaryDirectory(prefix="orion13-wave1-package-") as tmp_name:
        tmp = Path(tmp_name)
        for name in STATIC_PACKAGE_FILES:
            shutil.copyfile(OUTPUT / name, tmp / name)
        build(tmp)
        expected_names = sorted((*STATIC_PACKAGE_FILES, "manuscript.pdf", "ORION13_SWJ_SOURCE.zip", "ORION13_SWJ_REVIEW_RESOURCES.zip", "SUBMISSION_MANIFEST.json", "SHA256SUMS"))
        for name in expected_names:
            expected, observed = tmp / name, OUTPUT / name
            if not observed.is_file() or expected.read_bytes() != observed.read_bytes():
                raise ValueError(f"current package drifted: {name}")
    subprocess.run(["shasum", "-a", "256", "-c", "SHA256SUMS"], cwd=OUTPUT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.write:
            build(OUTPUT)
        else:
            verify()
    except (FileNotFoundError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"PACKAGE_CANNOT_CHECK: {exc}")
        return 3
    print("ORION13_WAVE1_PACKAGE_VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
