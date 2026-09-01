#!/usr/bin/env python3
"""Build and verify the final attributed arXiv and anonymous IP&M packages."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path


PAPER = Path(__file__).resolve().parents[1]
MANUSCRIPT = PAPER / "manuscript"
OUT = PAPER / "submission" / "publication-final-20260901"
SOURCE_DATE_EPOCH = "1788264000"
ZIP_TIME = (2026, 9, 1, 12, 0, 0)
COMMON = (
    "bibliography.bib",
    "novelty_refresh_2026.bib",
    "generated/suite_facts.tex",
    "sections/acquisition_authority.tex",
    "sections/availability.tex",
    "sections/formalism.tex",
    "sections/methods.tex",
    "sections/p2x_unresolved_route_successor.tex",
    "sections/results.tex",
    "figures/P2-1_pipeline.tex",
    "figures/P2-2_recall_vs_queries.tex",
    "figures/P2-6_stopping_failures.tex",
    "figures/P2-7_acquisition_authority.tex",
)
PRIVATE_MARKERS = (b"Sze Chun Yiu", b"Stockholm University", b"sze-chun.yiu@", b"/Users/")
PUBLIC_FORBIDDEN = (
    b"TIER_B",
    b"TIER\\_B",
    b"tier-b",
    b"tier_b",
    b"tier b committed",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_sources(root: Path, entry: str, *, journal: bool) -> None:
    for rel in COMMON:
        destination = root / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(MANUSCRIPT / rel, destination)
    shutil.copy2(MANUSCRIPT / entry, root / "main.tex")
    if journal:
        shutil.copytree(MANUSCRIPT / "elsevier-cas", root / "elsevier-cas")


def write_zip(root: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            info = zipfile.ZipInfo(path.relative_to(root).as_posix(), ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)


def compile_source(root: Path, *, journal: bool) -> Path:
    env = dict(os.environ, SOURCE_DATE_EPOCH=SOURCE_DATE_EPOCH, FORCE_SOURCE_DATE="1", TZ="UTC")
    if journal:
        env["TEXINPUTS"] = "./elsevier-cas//:"
    process = subprocess.run(
        ["latexmk", "-g", "-xelatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
        cwd=root,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if process.returncode:
        raise RuntimeError(process.stdout[-6000:])
    return root / "main.pdf"


def extract_and_compile(archive: Path, root: Path, *, journal: bool) -> Path:
    with zipfile.ZipFile(archive) as source_zip:
        source_zip.extractall(root)
    return compile_source(root, journal=journal)


def text_of(pdf: Path) -> bytes:
    with tempfile.NamedTemporaryFile(suffix=".txt") as handle:
        subprocess.run(["pdftotext", str(pdf), handle.name], check=True)
        return Path(handle.name).read_bytes()


def pages(pdf: Path) -> int:
    info = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
    return int(next(line.split(":", 1)[1] for line in info.splitlines() if line.startswith("Pages:")))


def metadata_of(pdf: Path) -> bytes:
    return subprocess.check_output(["pdfinfo", str(pdf)])


def scan_tree(root: Path, markers: tuple[bytes, ...]) -> None:
    for path in (p for p in root.rglob("*") if p.is_file()):
        data = path.read_bytes().lower()
        for marker in markers:
            if marker.lower() in data:
                raise ValueError(f"forbidden marker {marker!r} in {path.relative_to(root)}")


def build_route(name: str, entry: str, *, journal: bool) -> dict[str, object]:
    route = OUT / name
    pdf_out = route / ("manuscript_anonymous.pdf" if journal else "manuscript.pdf")
    zip_out = route / ("source_anonymous.zip" if journal else "source.zip")
    with tempfile.TemporaryDirectory(prefix=f"orion12-{name}-") as temporary:
        tmp = Path(temporary)
        source = tmp / "source"
        source.mkdir()
        copy_sources(source, entry, journal=journal)
        scan_tree(source, PUBLIC_FORBIDDEN)
        if journal:
            scan_tree(source, PRIVATE_MARKERS)
        write_zip(source, zip_out)
        first = compile_source(source, journal=journal)
        rebuilt = extract_and_compile(zip_out, tmp / "rebuilt", journal=journal)
        if first.read_bytes() != rebuilt.read_bytes():
            raise ValueError(f"{name} source archive does not reproduce the built PDF exactly")
        route.mkdir(parents=True, exist_ok=True)
        shutil.copy2(first, pdf_out)
    pdf_surface = (text_of(pdf_out) + metadata_of(pdf_out)).lower()
    if journal and any(marker.lower() in pdf_surface for marker in PRIVATE_MARKERS):
        raise ValueError("author identity leaked into anonymous journal PDF")
    if not journal and b"sze chun yiu" not in pdf_surface:
        raise ValueError("attributed arXiv PDF is missing the author")
    if any(marker.lower() in pdf_surface for marker in PUBLIC_FORBIDDEN):
        raise ValueError(f"private analysis label leaked into {name} PDF text or metadata")
    return {
        "pdf": pdf_out.relative_to(OUT).as_posix(),
        "pdf_sha256": digest(pdf_out),
        "pages": pages(pdf_out),
        "source": zip_out.relative_to(OUT).as_posix(),
        "source_sha256": digest(zip_out),
        "source_archive_rebuild_exact": True,
        "anonymous": journal,
    }


def payload() -> dict[str, dict[str, object]]:
    entries: dict[str, dict[str, object]] = {}
    for path in sorted(p for p in OUT.rglob("*") if p.is_file()):
        rel = path.relative_to(OUT).as_posix()
        if rel in {"PACKAGE_MANIFEST.json", "SHA256SUMS"}:
            continue
        entries[rel] = {"bytes": path.stat().st_size, "sha256": digest(path)}
    return entries


def build() -> dict[str, object]:
    subprocess.run(["python", str(PAPER / "scripts" / "build_ipm_submission.py"), "--check"], check=True)
    arxiv = build_route("arxiv", "arxiv_submission.tex", journal=False)
    journal = build_route("journal", "ipm_submission.tex", journal=True)
    shutil.copy2(OUT / arxiv["pdf"], MANUSCRIPT / "arxiv_submission.pdf")
    shutil.copy2(OUT / journal["pdf"], MANUSCRIPT / "ipm_submission.pdf")
    manifest = {
        "schema": "orion.publication-package.v1",
        "paper": "ORION-12",
        "date": "2026-09-01",
        "title": "Acquisition Is Not Closure: Fail-Closed Control for Open-World Scientific-Literature Discovery",
        "scientific_authority": "bounded acquisition-authority control; no external retrieval superiority or open-world completeness",
        "canonical_science_source": "manuscript/ipm_submission.tex",
        "arxiv": arxiv,
        "journal": {"venue": "Information Processing & Management", **journal},
        "academic_paper_skills": {
            "revision": "488fc5310b84e578431f4a9a176d55bf9a3f0b99",
            "pipeline": "1.21.0",
        },
        "payload": payload(),
        "status": "READY_FOR_AUTHOR_PORTAL_CONFIRMATION",
    }
    manifest_path = OUT / "PACKAGE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    files = sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "SHA256SUMS")
    (OUT / "SHA256SUMS").write_text(
        "".join(f"{digest(path)}  {path.relative_to(OUT).as_posix()}\n" for path in files),
        encoding="utf-8",
    )
    scan_tree(OUT, PUBLIC_FORBIDDEN)
    return manifest


def snapshot() -> dict[str, str]:
    return {p.relative_to(OUT).as_posix(): digest(p) for p in OUT.rglob("*") if p.is_file()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    before = snapshot() if args.check else {}
    manifest = build()
    if args.check and before != snapshot():
        raise SystemExit("publication package drifted; run the builder and commit the refreshed package")
    print(json.dumps({"status": manifest["status"], "arxiv": manifest["arxiv"], "journal": manifest["journal"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
