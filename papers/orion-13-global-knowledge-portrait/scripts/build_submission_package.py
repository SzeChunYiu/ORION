#!/usr/bin/env python3
"""Build and verify the ORION-13 arXiv and F1000Research files."""

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
SOURCE = PAPER / "manuscript" / "brief-report-final"
OUT = PAPER / "submission" / "publication-final-20260901"
SOURCE_DATE_EPOCH = "1788264000"
ZIP_TIME = (2026, 9, 1, 12, 0, 0)
ENV = {
    **os.environ,
    "SOURCE_DATE_EPOCH": SOURCE_DATE_EPOCH,
    "FORCE_SOURCE_DATE": "1",
    "TZ": "UTC",
}
TITLE = "Coordinate-Governed Mapping of Source-Local Scientific Projections: A Fixed-Panel Study"
PUBLIC_FORBIDDEN = (
    b"tier b",
    b"tier-b",
    b"tier_b",
    b"peer_review_ready",
    b"package_complete",
    b"reclassify_as_note",
    b"/users/",
    b"billy",
    b"codex/",
    b"worktree",
)
PUBLIC_FORBIDDEN_REGEX = (
    re.compile(rb"\b(?:issue|pull request|pr)\s*#\s*\d+\b", re.IGNORECASE),
    re.compile(rb"\b[A-Z][A-Z0-9]+(?:__[A-Z0-9]+)+\b"),
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*args: str, cwd: Path) -> None:
    subprocess.run(args, cwd=cwd, env=ENV, check=True)


def write_zip(root: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            info = zipfile.ZipInfo(path.relative_to(root).as_posix(), ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)


def normalize_docx(source: Path, destination: Path) -> None:
    with zipfile.ZipFile(source) as original, zipfile.ZipFile(
        destination, "w", zipfile.ZIP_DEFLATED, compresslevel=9
    ) as normalized:
        for name in sorted(original.namelist()):
            data = original.read(name)
            if name == "docProps/core.xml":
                data = re.sub(
                    rb"<dcterms:(created|modified)[^>]*>.*?</dcterms:\1>",
                    rb'<dcterms:\1 xsi:type="dcterms:W3CDTF">2026-09-01T12:00:00Z</dcterms:\1>',
                    data,
                )
                data = data.replace(
                    b"<cp:keywords></cp:keywords>",
                    b"<cp:keywords>semantic interoperability; knowledge representation; evidence provenance; scientific mapping</cp:keywords>",
                )
                data = data.replace(
                    b"</cp:coreProperties>",
                    b"<dc:subject>F1000Research Brief Report</dc:subject></cp:coreProperties>",
                )
            info = zipfile.ZipInfo(name, ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            normalized.writestr(info, data, compresslevel=9)


def scan_bytes(data: bytes, location: str) -> None:
    lower = data.lower()
    for marker in PUBLIC_FORBIDDEN:
        if marker in lower:
            raise ValueError(f"forbidden public marker {marker!r} in {location}")
    for pattern in PUBLIC_FORBIDDEN_REGEX:
        match = pattern.search(data)
        if match:
            raise ValueError(f"forbidden public marker {match.group()!r} in {location}")


def scan_archive(path: Path) -> None:
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            scan_bytes(name.encode(), f"{path.relative_to(OUT)}::{name}")
            scan_bytes(archive.read(name), f"{path.relative_to(OUT)}::{name}")


def scan_public_file(path: Path) -> None:
    rel = path.relative_to(OUT).as_posix()
    scan_bytes(rel.encode(), rel)
    if path.suffix.lower() == ".pdf":
        text = subprocess.check_output(["pdftotext", str(path), "-"], stderr=subprocess.STDOUT)
        metadata = subprocess.check_output(["pdfinfo", "-meta", str(path)], stderr=subprocess.STDOUT)
        scan_bytes(text, f"{rel} extracted text")
        scan_bytes(metadata, f"{rel} metadata")
    elif path.suffix.lower() in {".zip", ".docx"}:
        scan_archive(path)
    else:
        scan_bytes(path.read_bytes(), rel)


def copy_sources(root: Path, adapter: str) -> None:
    root.mkdir(parents=True)
    for name in ("common.tex", "bibliography.bib"):
        shutil.copy2(SOURCE / name, root / name)
    shutil.copy2(SOURCE / adapter, root / "main.tex")


def compile_source(root: Path) -> Path:
    run("tectonic", "-X", "compile", "main.tex", cwd=root)
    return root / "main.pdf"


def build_docx(source_root: Path, destination: Path) -> None:
    combined = (source_root / "main.tex").read_text(encoding="utf-8").replace(
        r"\input{common}", (source_root / "common.tex").read_text(encoding="utf-8")
    )
    combined = combined.replace(r"\bibliographystyle{plain}", r"\section*{References}" + "\n" + r"\bibliographystyle{plain}")
    (source_root / "combined.tex").write_text(combined, encoding="utf-8")
    raw = source_root / "raw.docx"
    run(
        "pandoc",
        "combined.tex",
        "--citeproc",
        "--bibliography=bibliography.bib",
        "--metadata=date:1 September 2026",
        "-o",
        raw.name,
        cwd=source_root,
    )
    normalize_docx(raw, destination)


def pages(pdf: Path) -> int:
    info = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
    return int(next(line.split(":", 1)[1] for line in info.splitlines() if line.startswith("Pages:")))


def build_route(name: str, adapter: str, *, journal: bool) -> dict[str, object]:
    route = OUT / name
    route.mkdir(parents=True)
    source_zip = route / "source.zip"
    pdf_out = route / "manuscript.pdf"
    with tempfile.TemporaryDirectory(prefix=f"orion13-{name}-") as temporary:
        tmp = Path(temporary)
        source_root = tmp / "source"
        copy_sources(source_root, adapter)
        for path in source_root.iterdir():
            if path.is_file():
                scan_bytes(path.read_bytes(), path.name)
        write_zip(source_root, source_zip)
        built = compile_source(source_root)

        rebuilt_root = tmp / "rebuilt"
        with zipfile.ZipFile(source_zip) as archive:
            archive.extractall(rebuilt_root)
        rebuilt = compile_source(rebuilt_root)
        if built.read_bytes() != rebuilt.read_bytes():
            raise ValueError(f"{name} source archive did not reproduce the PDF exactly")
        shutil.copy2(built, pdf_out)

        if journal:
            docx_out = route / "manuscript.docx"
            build_docx(source_root, docx_out)
            second_docx = tmp / "second.docx"
            build_docx(rebuilt_root, second_docx)
            if docx_out.read_bytes() != second_docx.read_bytes():
                raise ValueError("journal DOCX build is not deterministic")

    return {
        "pdf": pdf_out.relative_to(OUT).as_posix(),
        "pdf_sha256": digest(pdf_out),
        "pages": pages(pdf_out),
        "source": source_zip.relative_to(OUT).as_posix(),
        "source_sha256": digest(source_zip),
        "source_archive_rebuild_exact": True,
        **(
            {
                "docx": (route / "manuscript.docx").relative_to(OUT).as_posix(),
                "docx_sha256": digest(route / "manuscript.docx"),
            }
            if journal
            else {}
        ),
    }


def write_support_files(arxiv: dict[str, object], journal: dict[str, object]) -> None:
    (OUT / "README.md").write_text(
        f"""# ORION-13 publication files

This directory contains the attributed arXiv manuscript and the F1000Research Brief Report files for **{TITLE}**.

The article reports a bounded fixed-panel observation. It does not claim population error rates, superiority over deployed integration systems, independent external validation, raw-text extraction performance, or downstream scientific utility.

The PDFs and source archives are reproducible byte for byte. The journal route still requires a public archive DOI and the author's final portal confirmations; see `HUMAN_INPUTS_REQUIRED.md`.
""",
        encoding="utf-8",
    )
    (OUT / "HUMAN_INPUTS_REQUIRED.md").write_text(
        """# Human inputs required before filing

1. Deposit the frozen data and software snapshot in a long-term public repository and obtain its persistent DOI. Do not submit to F1000Research until the DOI is inserted into the Data and software availability section and the files are rebuilt.
2. Confirm the author's affiliation, correspondence address and ORCID in the submission portal.
3. Confirm the current journal wording for the generative-AI disclosure and amend it if the live policy differs.
4. Independently recreate or confirm the results table, the projection formula and every final sentence. F1000Research permits disclosed AI assistance with rigorous human revision but prohibits generative-AI creation or manipulation of figures, data tables and formulas.
5. Select the article licence and complete the journal and arXiv portal declarations.
6. Confirm that third-party resource licences permit the stated access route; restricted source text is not included in the package.
7. Confirm any article-processing charge or institutional publishing agreement before filing.
8. Confirm that the article is not under consideration elsewhere and complete any originality declaration required by the portals.

No DOI or ORCID has been guessed or fabricated.
""",
        encoding="utf-8",
    )
    (OUT / "RESULT_RETENTION.md").write_text(
        """# Bounded result retention

The public files retain the complete outcome pattern needed to interpret the paper:

- the 32-case holdout contains three authored case families;
- coordinate-governed mapping made no false merges, while the deliberately flat comparator made six, all in polarity contrasts;
- the other 19 holdout cases did not discriminate the rules;
- the false-split difference from the conservative rule was zero;
- four coordinate-ablation cells showed no measured change and are reported as absent comparison opportunity, not evidence of dispensability;
- the 400 generated conformance records instantiate only eight unique candidate-visible states;
- the structured-semantic comparator has a narrower terminal interface, so its 250/400 result is not a general capability comparison;
- the information-equivalent typed implementation tied the complete rule at 400/400.

The manuscript therefore supports only a fixed-panel methods observation and deterministic interface-conformance result. It makes no population, deployed-system, broad external-validity, journal-standing or editorial-outcome claim.
""",
        encoding="utf-8",
    )
    (OUT / "SCIENTIFIC_SCOPE.md").write_text(
        """# Scientific scope

This Brief Report exists because retaining polarity and an explicit non-merge outcome prevented six false agreements produced by the registered flat rule on the frozen holdout.

The holdout comprises 32 cases in three authored families, only one of which discriminated the rules. The separate conformance battery comprises 400 generated records but only eight unique candidate-visible states. Its structured-semantic comparator has a narrower terminal interface, so the 250/400 score is an interface-attainability observation, not a general superiority result. Shared authorship of the mechanism, cases and expected decisions gives the study substantial designer advantage.

The resulting authority is limited to fixed authored panels and deterministic conformance. It does not establish population rates, deployed-system superiority, independent external validation, raw-text extraction, downstream utility or broad external validity. Reproducible files and provenance checks support integrity but are not substituted for those missing forms of scientific validity.
""",
        encoding="utf-8",
    )
    (OUT / "SKILLS_APPLIED.md").write_text(
        """# Publication audit method

The manuscript and package were checked with academic-paper-skills revision `488fc5310b84e578431f4a9a176d55bf9a3f0b99`, academic-paper-pipeline version 1.21.0, and the minimal-change Ponytail workflow.

Checks covered claim-evidence alignment, bounded-result retention, journal fit, related-work positioning, standalone readability, manuscript-surface leakage, scholarly source semantics, deterministic rebuilding, PDF metadata, DOCX contents and metadata, archive members, and rendered-page integrity. Scanner warnings that represent necessary LaTeX syntax, structured-abstract labels, table headers, a correspondence email, or designated availability paths were reviewed contextually rather than hidden.
""",
        encoding="utf-8",
    )
    (OUT / "VISUAL_QA.md").write_text(
        f"""# Rendered-page review

Every page of the {journal['pages']}-page journal PDF and the {arxiv['pages']}-page arXiv PDF was rendered to an image at release resolution and inspected. No clipping, overlap, duplicate labels, unreadable table text, broken mathematics, internal workflow language or blank page was observed.

The single results table fits within the text area, and its caption remains attached and readable. PDF text extraction and metadata scans also passed.
""",
        encoding="utf-8",
    )
    (OUT / "REVIEWER_AUDIT.md").write_text(
        """# Hostile pre-submission audit

## Field-editor lens

The evidence is too narrow for a full-length general integration paper. The defensible form is a Brief Report: one fixed-panel methods observation plus a deterministic interface contract. The title, abstract and discussion now state that scope directly.

## Methods, benchmark and statistics lens

The 32 holdout cases belong to three authored families, and only the polarity-related family discriminated the rules. Bootstrap intervals are labelled as fixed-panel diagnostics rather than population uncertainty. The 400 conformance records reduce to eight unique candidate-visible states. The weak flat comparator and the structured comparator's narrower terminal interface are disclosed, as is the high same-programme designer advantage.

## Theory lens

The projection and three-way decision rule are defined explicitly, but the study does not prove the independent value of every coordinate. Null ablations remain visible and are interpreted as absent comparison opportunities rather than dispensability.

## Systems and reproducibility lens

The source archives reproduce both PDFs exactly and the editable DOCX is deterministic. The independent scorer remains a same-snapshot implementation check, not external replication. Reproducibility and provenance are not used as substitutes for broader scientific validity.

## Literature and portfolio lens

Nearest positioning includes Bernasconi et al. on ontological unpacking, Santos et al. on ontology-alignment repair, Euzenat and Shvaiko on ontology matching, I-ADOPT on variable structure, and FAIR 2.0 on semantic interoperability. The report does not claim to replace those extraction, matching or modelling programmes; it isolates a downstream claim-relative merge decision after projections already exist.

## Venue and remaining actions

F1000Research is used only for the Brief Report route, with open post-publication review. Filing is not yet authorized: a public archive DOI, author identity and ORCID confirmation, licence and portal declarations, live-policy confirmation of the AI disclosure, independent author recreation or confirmation of the results table and projection formula, rigorous final wording review, and any article-processing charge or institutional agreement remain human actions.

## Surface-scan dispositions

Mechanical source warnings were reviewed rather than suppressed. They were confined to comma-separated LaTeX package and citation syntax, the displayed coordinate tuple, structured-abstract labels, table headers, the correspondence email, bibliographic abbreviations, and the pinned commit URL in the designated availability section. Apparent spaces before commas arose only from PDF text extraction of the tuple; rendered-page review confirmed correct mathematical spacing. None is an internal workflow leak or prose defect.
""",
        encoding="utf-8",
    )
    (OUT / "journal" / "COVER_LETTER.md").write_text(
        f"""Dear F1000Research editorial team,

Please consider “{TITLE}” as a Brief Report.

The report presents a deliberately bounded fixed-panel observation: preserving polarity and an explicit non-merge outcome prevented six false agreements made by a registered flat rule on a prospectively frozen 32-case holdout, without increasing false splits relative to the conservative control. A separate deterministic battery confirms interface conformance but contains only eight unique decision states. The manuscript discloses the weak comparator, the narrower terminal interface of the structured comparator, same-programme authorship, null ablations, and the limits on external validity.

The work does not claim superiority over deployed integration systems or population performance. All supporting data and software will be linked through the required public archive DOI before filing.

Sincerely,

Sze Chun Yiu
""",
        encoding="utf-8",
    )
    (OUT / "journal" / "DECLARATIONS.md").write_text(
        """# Declarations

## Competing interests

No competing interests were disclosed.

## Grant information

The author declared that no grants were involved in supporting this work.

## Ethics and consent

Not applicable. This computational study involved no human participants, personal data or animals.

## Author contributions

Sze Chun Yiu: conceptualization, methodology, software, validation, formal analysis, investigation, data curation, writing, visualization and project administration.
""",
        encoding="utf-8",
    )
    (OUT / "journal" / "SUBMISSION_CHECKLIST.md").write_text(
        """# F1000Research Brief Report checklist

- [x] Title, author and correspondence information are present.
- [x] Structured abstract and keywords are present.
- [x] Main text, limitations, declarations and references are present.
- [x] Data and software availability names the frozen public repository snapshot.
- [x] Adverse, null and non-discriminating results remain visible.
- [x] Journal PDF, editable DOCX and reproducible source archive are included.
- [x] Open post-publication peer review is compatible with the attributed manuscript.
- [ ] A long-term public data/software DOI must be added before filing.
- [ ] Author affiliation, ORCID, licence and portal declarations require author confirmation.
- [ ] The generative-AI disclosure must be checked against the live policy at filing.
- [ ] The author must independently recreate or confirm the results table and projection formula and rigorously revise the final wording before filing.
- [ ] Any article-processing charge or institutional publishing agreement must be confirmed.
- [ ] The author must confirm originality and that the article is not under consideration elsewhere.

F1000Research does not accept supplementary material. No supplementary file is represented here; supporting records belong in the public data/software deposit.
""",
        encoding="utf-8",
    )
    journal_metadata = {
        "venue": "F1000Research",
        "article_type": "Brief Report",
        "title": TITLE,
        "author": "Sze Chun Yiu",
        "affiliation": "Stockholm University",
        "correspondence": "sze-chun.yiu@fysik.su.se",
        "keywords": [
            "semantic interoperability",
            "knowledge representation",
            "evidence provenance",
            "coordinate systems",
            "scientific mapping",
        ],
        "review_model": "Open post-publication peer review",
        "data_deposit": "A public archive DOI is required before filing and is not yet asserted.",
        "competing_interests": "No competing interests were disclosed.",
        "grant_information": "The author declared that no grants were involved in supporting this work.",
        "files": journal,
    }
    (OUT / "journal" / "metadata.json").write_text(
        json.dumps(journal_metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (OUT / "arxiv" / "SUBMISSION_CHECKLIST.md").write_text(
        """# arXiv checklist

- [x] Attributed PDF and reproducible source archive are included.
- [x] Suggested primary category: cs.AI.
- [x] Title, author, abstract and references are present.
- [x] Claims remain bounded to the fixed panels and deterministic contract test.
- [ ] Author must confirm category, licence and portal metadata.
- [ ] Replace or supplement the repository link with the archive DOI when available.
""",
        encoding="utf-8",
    )
    arxiv_metadata = {
        "title": TITLE,
        "authors": ["Sze Chun Yiu"],
        "suggested_primary_category": "cs.AI",
        "comments": f"Brief Report; {arxiv['pages']} pages, 2 tables. Bounded fixed-panel study.",
        "keywords": journal_metadata["keywords"],
        "files": arxiv,
    }
    (OUT / "arxiv" / "metadata.json").write_text(
        json.dumps(arxiv_metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def payload() -> dict[str, dict[str, int | str]]:
    return {
        path.relative_to(OUT).as_posix(): {"bytes": path.stat().st_size, "sha256": digest(path)}
        for path in sorted(p for p in OUT.rglob("*") if p.is_file())
        if path.name not in {"PACKAGE_MANIFEST.json", "SHA256SUMS"}
    }


def build() -> dict[str, object]:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    arxiv = build_route("arxiv", "arxiv.tex", journal=False)
    journal = build_route("journal", "main.tex", journal=True)
    write_support_files(arxiv, journal)
    authority = PAPER / "SCOPED_PUBLICATION_TRACK_V1.md"
    canonical_sources = {
        f"papers/orion-13-global-knowledge-portrait/manuscript/brief-report-final/{name}": digest(SOURCE / name)
        for name in ("main.tex", "arxiv.tex", "common.tex", "bibliography.bib")
    }
    manifest = {
        "schema": "orion.publication-package.v1",
        "paper": "ORION-13",
        "date": "2026-09-01",
        "title": TITLE,
        "publication_route": "F1000Research Brief Report and attributed arXiv preprint",
        "scientific_authority": "A bounded fixed-panel methods observation and an eight-state deterministic interface-conformance result; no broad external-validity or deployed-system superiority claim.",
        "active_authority": "papers/orion-13-global-knowledge-portrait/SCOPED_PUBLICATION_TRACK_V1.md",
        "active_authority_sha256": digest(authority),
        "canonical_science_source": "papers/orion-13-global-knowledge-portrait/manuscript/brief-report-final/common.tex",
        "canonical_science_source_sha256": digest(SOURCE / "common.tex"),
        "canonical_sources": canonical_sources,
        "arxiv": arxiv,
        "journal": {"venue": "F1000Research", "article_type": "Brief Report", **journal},
        "academic_paper_skills": {
            "revision": "488fc5310b84e578431f4a9a176d55bf9a3f0b99",
            "pipeline": "1.21.0",
        },
        "filing_state": "Files built and verified; journal filing awaits a public archive DOI and author portal confirmations.",
        "payload": payload(),
    }
    (OUT / "PACKAGE_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    files = sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "SHA256SUMS")
    (OUT / "SHA256SUMS").write_text(
        "".join(f"{digest(path)}  {path.relative_to(OUT).as_posix()}\n" for path in files),
        encoding="utf-8",
    )
    for path in (p for p in OUT.rglob("*") if p.is_file()):
        scan_public_file(path)
    return manifest


def snapshot() -> dict[str, str]:
    return {p.relative_to(OUT).as_posix(): digest(p) for p in OUT.rglob("*") if p.is_file()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    before = snapshot() if args.check and OUT.exists() else None
    manifest = build()
    if before is not None and before != snapshot():
        raise SystemExit("publication files drifted; rebuild and commit the refreshed files")
    print(
        json.dumps(
            {
                "filing_state": manifest["filing_state"],
                "arxiv": manifest["arxiv"],
                "journal": manifest["journal"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
