#!/usr/bin/env python3
"""Build and verify the current IP&M review package.

The editable source and review-material archives are deliberately reader-facing
objects. They are prepared with generic scientific names and are scanned here
before the private byte-binding manifest is refreshed. Earlier archives made
directly from repository paths are private audit evidence and must never be
reintroduced by this builder.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path


PAPER = Path(__file__).resolve().parents[1]
REPO = PAPER.parents[1]
MANUSCRIPT = PAPER / "manuscript"
OUT = PAPER / "journal_package" / "current_revision"
SOURCE_DATE_EPOCH = "1787918400"
FIXED_ZIP_TIME = (2026, 8, 28, 12, 0, 0)

SOURCE_FILES = (
    "manuscript/main.tex",
    "manuscript/ipm_submission.tex",
    "manuscript/bibliography.bib",
    "manuscript/novelty_refresh_2026.bib",
    "manuscript/generated/suite_facts.tex",
    "manuscript/generated/suite_facts.json",
    "manuscript/sections/acquisition_authority.tex",
    "manuscript/sections/formalism.tex",
    "manuscript/sections/methods.tex",
    "manuscript/sections/results.tex",
    "manuscript/sections/availability.tex",
    "manuscript/figures/P2-1_pipeline.tex",
    "manuscript/figures/P2-2_recall_vs_queries.tex",
    "manuscript/figures/P2-6_stopping_failures.tex",
)

COMPANION_FILES = (
    "TITLE_PAGE.md",
    "COVER_LETTER.md",
    "GLOSSARY.md",
    "FIGURE_CAPTIONS.md",
    "AI_ASSISTANCE_DECLARATION.md",
    "HUMAN_INPUTS_REQUIRED.md",
    "CREDIT_TEMPLATE.md",
    "LICENSE_AND_THIRD_PARTY_TERMS.md",
    "ANONYMOUS_REVIEW_README.md",
)

IDENTITY_MARKERS = (
    b"Sze Chun Yiu",
    b"SzeChunYiu",
    b"sze-chun.yiu@",
    b"/Users/",
    b"\\Users\\",
)

FORBIDDEN_READER_PATTERNS = (
    re.compile(rb"\bORION[-_ ]?\d+(?:[-_.][A-Za-z0-9]+)*\b", re.I),
    re.compile(rb"\bP\d+(?:[-_.][A-Za-z0-9]+)+\b", re.I),
    re.compile(rb"(?<![A-Za-z0-9_-])R\d{1,2}(?:[-_.][A-Za-z0-9]+)*\b"),
    re.compile(rb"\b(?:CANNOT_CHECK|PEER_REVIEW_READY|TIER_[A-Z0-9_]+)\b"),
    re.compile(rb"\b(?:github|gitlab)\b|\.git(?:hub)?/|/Users/|\\Users\\", re.I),
    re.compile(rb"\b(?:commit|branch|pull request|merge request|CI run|issue #)\b", re.I),
    re.compile(rb"\b[0-9a-f]{40,64}\b", re.I),
    re.compile(rb"\b(?:sha-?256|checksum)\b", re.I),
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def entry(path: Path, relative_to: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(relative_to).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def check_files(paths: tuple[str, ...]) -> list[Path]:
    resolved = [PAPER / p for p in paths]
    missing = [p for p in resolved if not p.is_file()]
    if missing:
        raise FileNotFoundError("missing package inputs: " + ", ".join(map(str, missing)))
    return resolved


def identity_scan(paths: list[Path]) -> None:
    for path in paths:
        data = path.read_bytes()
        for marker in IDENTITY_MARKERS:
            if marker.lower() in data.lower():
                raise ValueError(f"identity/private-path marker in anonymous file {path}: {marker!r}")


def archive_members(path: Path) -> list[dict[str, object]]:
    members: list[dict[str, object]] = []
    with zipfile.ZipFile(path) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            name = info.filename.encode()
            data = zf.read(info)
            for pattern in FORBIDDEN_READER_PATTERNS:
                if pattern.search(name) or pattern.search(data):
                    raise ValueError(
                        f"private project marker in reader-facing archive {path.name}:{info.filename}: "
                        f"{pattern.pattern!r}"
                    )
            members.append(
                {
                    "path": info.filename,
                    "bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                }
            )
    if not members:
        raise ValueError(f"empty reader-facing archive: {path}")
    return members


def build_pdf() -> tuple[Path, list[dict[str, object]]]:
    subprocess.run(
        ["python", str(PAPER / "scripts" / "build_ipm_submission.py")],
        cwd=REPO,
        check=True,
    )
    subprocess.run(
        ["python", str(PAPER / "scripts" / "build_ipm_submission.py"), "--check"],
        cwd=REPO,
        check=True,
    )
    env = dict(os.environ, SOURCE_DATE_EPOCH=SOURCE_DATE_EPOCH)
    with tempfile.TemporaryDirectory(prefix="orion12-ipm-build-") as tmp:
        first = Path(tmp) / "first.pdf"
        for destination in (first, OUT / "manuscript.pdf"):
            (MANUSCRIPT / "ipm_submission.pdf").unlink(missing_ok=True)
            subprocess.run(
                ["tectonic", "ipm_submission.tex"],
                cwd=MANUSCRIPT,
                env=env,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            shutil.copyfile(MANUSCRIPT / "ipm_submission.pdf", destination)
        if first.read_bytes() != (OUT / "manuscript.pdf").read_bytes():
            raise ValueError("two clean target builds are not byte-identical")
    closure = [entry(PAPER / p, PAPER) for p in SOURCE_FILES]
    return OUT / "manuscript.pdf", closure


def build() -> dict[str, object]:
    OUT.mkdir(parents=True, exist_ok=True)
    source_paths = check_files(SOURCE_FILES)
    identity_scan(source_paths)

    pdf, closure = build_pdf()
    source_zip = OUT / "source.zip"
    review_zip = OUT / "review_materials.zip"
    if not source_zip.is_file() or not review_zip.is_file():
        raise FileNotFoundError("sanitized source.zip and review_materials.zip are required")
    source_members = archive_members(source_zip)
    review_members = archive_members(review_zip)

    objects = [pdf, source_zip, review_zip] + [OUT / p for p in COMPANION_FILES]
    artifacts = [entry(p, OUT) for p in objects]
    manifest = {
        "schema": "orion12.ipm.wave1.private-byte-binding.v2",
        "distribution": "private audit evidence; reader-facing uploads are named separately below",
        "date": "2026-08-29",
        "paper_id": "ORION-12",
        "title": "Acquisition Is Not Closure: Fail-Closed Control for Open-World Scientific-Literature Discovery",
        "primary_target": "Information Processing & Management",
        "fallback_target": "Journal of the Association for Information Science and Technology",
        "article_type": "full research article; methods / critical system design",
        "canonical_content_source": "manuscript/main.tex",
        "target_adapter": "manuscript/ipm_submission.tex",
        "source_date_epoch": int(SOURCE_DATE_EPOCH),
        "double_build_byte_identical": True,
        "claim_boundary": "bounded acquisition-authority control; no external retrieval superiority or open-world completeness",
        "registered_external_decision": "TREC-COVID recall and cost gate failed; favorable nDCG is secondary only",
        "declared_paper_terminal": "simulated_publication_ready_for_target",
        "artifacts": artifacts,
        "reader_facing_uploads": [
            "manuscript.pdf",
            "source.zip",
            "review_materials.zip",
            "TITLE_PAGE.md",
            "COVER_LETTER.md",
            "AI_ASSISTANCE_DECLARATION.md",
            "CREDIT_TEMPLATE.md",
        ],
        "pdf_source_closure": closure,
        "source_zip_members": source_members,
        "review_zip_members": review_members,
        "human_only_fields_open": [
            "department/unit, street/postal address or phone only if the submission portal mandates them",
            "ORCID if later supplied",
            "submission-system classifications, suggested reviewers and submission ID",
            "originality/non-concurrent-submission checkbox re-confirmed at filing",
            "future permanent archive URL/DOI if deposited later",
        ],
        "author_fields_supplied": {
            "name": "SzeChunYiu",
            "affiliation": "Stockholm University, Stockholm, Sweden",
            "email": "sze-chun.yiu@fysik.su.se",
            "corresponding_author_designation": "none",
            "orcid": None,
            "funding": "The author received no specific funding for this work.",
            "competing_interests": "The author declares no competing interests.",
            "public_arxiv_release_approved": True,
            "patent_ip_timing_conflict": False,
        },
        "historical_package_rule": "Earlier archives and root-package objects are private audit evidence and must not be distributed.",
    }
    (OUT / "SUBMISSION_MANIFEST.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    checksum_paths = objects + [OUT / "SUBMISSION_MANIFEST.json"]
    (OUT / "SHA256SUMS").write_text(
        "".join(f"{sha256(p)}  {p.name}\n" for p in checksum_paths), encoding="utf-8"
    )
    return manifest


def check() -> dict[str, object]:
    before = {p.name: sha256(p) for p in OUT.iterdir() if p.is_file()}
    manifest = build()
    after = {p.name: sha256(p) for p in OUT.iterdir() if p.is_file()}
    for name in ("manuscript.pdf", "source.zip", "review_materials.zip"):
        if before and before.get(name) != after.get(name):
            raise ValueError(f"deterministic package drift for {name}")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    manifest = check() if args.check else build()
    print(json.dumps({"terminal": manifest["declared_paper_terminal"], "artifacts": manifest["artifacts"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
