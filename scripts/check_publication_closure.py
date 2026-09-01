#!/usr/bin/env python3
"""Fail-closed verification for registry-bound publication packages."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "papers/publication_closure/orion_13_24_final/CLOSURE_REGISTRY.json"
AUTHOR = "Sze Chun Yiu"
EMAIL = "sze-chun.yiu@fysik.su.se"
IDENTITY_TOKENS = (AUTHOR, EMAIL, "Independent Researcher", "Stockholm University")
REQUIRED_PAYLOAD = {
    "AI_USE_DISCLOSURE.md",
    "DATA_AND_CODE_AVAILABILITY.md",
    "HUMAN_INPUTS_REQUIRED.md",
    "RESULT_RETENTION.md",
    "VENUE_REQUIREMENTS.md",
    "manuscript.pdf",
    "review_materials.zip",
    "source.zip",
}
CLAIM_TOKENS = {
    "ORION-13": ("0.1875", "400/400", "250/400", "50/400", "information-equivalent", "fixed-panel", "raw-text"),
    "ORION-14": ("0/360", "180/360", "60/60", "30/30", "not supported", "39-case", "12 attack families"),
    "ORION-19": ("4/5", "versus one", "wine is a null", "qwen2.5", "symbol-reminting", "fails its own half-sample stability condition"),
    "ORION-21": ("seed (n=3)", "width-three", "3/10", "5/10", "8/10", "technical repeats"),
    "ORION-23": ("12,288", "2,457", "0.97933", "0.95247", "0.98063", "330 unsafe", "123 adversary-induced", "finite world"),
    "ORION-24": ("eight required external-input artifact classes", "execution was never authorized", "external scientific endpoints remain undetermined", "not a completed harness"),
}
FORBIDDEN = {
    "ORION-21": ("nine independent replicates", "digits supports the frozen"),
    "ORION-23": ("population-level safety", "externally validated safety"),
    "ORION-24": ("negative acquisition result", "eight attempted external", "eight external cases", "we implemented an end-to-end harness"),
}
ALLOWED_NEGATED_BOUNDARIES = {
    "ORION-23": {
        "population-level safety": (
            "do not establish external or population-level safety",
            "does not establish population-level safety",
        ),
    },
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def run(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = "315532800"
    return subprocess.run(args, cwd=cwd or ROOT, env=env, text=True,
                          encoding="utf-8", errors="replace",
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          check=False)


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def check(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def zip_text(path: Path, failures: list[str]) -> str:
    text: list[str] = []
    try:
        with zipfile.ZipFile(path) as archive:
            check(archive.testzip() is None, f"{path}: corrupt archive", failures)
            names = archive.namelist()
            check(names == sorted(names), f"{path}: members are not canonical-sorted", failures)
            for info in archive.infolist():
                member = PurePosixPath(info.filename)
                check(not member.is_absolute() and ".." not in member.parts,
                      f"{path}: unsafe member path {info.filename}", failures)
                check(info.date_time == (1980, 1, 1, 0, 0, 0),
                      f"{path}: non-deterministic member timestamp {info.filename}", failures)
                mode = info.external_attr >> 16
                check(not (mode & 0o170000) == 0o120000,
                      f"{path}: symlink member {info.filename}", failures)
                if not info.is_dir():
                    try:
                        text.append(archive.read(info).decode("utf-8"))
                    except UnicodeDecodeError:
                        pass
    except (OSError, zipfile.BadZipFile) as exc:
        failures.append(f"{path}: unreadable archive: {exc}")
    return "\n".join(text)


def verify_checksums(package: Path, failures: list[str]) -> None:
    checksum_file = package / "SHA256SUMS"
    check(checksum_file.is_file(), f"{package}: missing SHA256SUMS", failures)
    if not checksum_file.is_file():
        return
    declared: dict[str, str] = {}
    for line in checksum_file.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        parts = line.split("  ", 1)
        check(len(parts) == 2, f"{package}: malformed checksum line", failures)
        if len(parts) != 2:
            continue
        digest, rel = parts
        declared[rel] = digest
        path = package / rel
        check(path.is_file(), f"{package}: checksum target missing: {rel}", failures)
        if path.is_file():
            check(sha256(path) == digest, f"{package}: checksum mismatch: {rel}", failures)
    actual = {p.name for p in package.iterdir() if p.is_file() and p.name != "SHA256SUMS"}
    check(set(declared) == actual, f"{package}: checksum inventory drift", failures)


def pdf_text(pdf: Path, failures: list[str]) -> tuple[str, int]:
    check(pdf.is_file(), f"{pdf}: missing PDF", failures)
    if not pdf.is_file():
        return "", 0
    check(b"%%EOF" in pdf.read_bytes()[-4096:], f"{pdf}: missing EOF marker", failures)
    info = run(["pdfinfo", str(pdf)])
    check(info.returncode == 0, f"{pdf}: pdfinfo failed", failures)
    pages_match = re.search(r"^Pages:\s+(\d+)", info.stdout, flags=re.M)
    pages = int(pages_match.group(1)) if pages_match else 0
    extract = run(["pdftotext", str(pdf), "-"])
    check(extract.returncode == 0 and bool(extract.stdout.strip()),
          f"{pdf}: text extraction failed or empty", failures)
    return extract.stdout, pages


def rebuild_from_source(paper: str, package: Path, expected_text: str,
                        expected_pages: int, failures: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix=f"publication-{paper.lower()}-") as tmp:
        root = Path(tmp)
        try:
            with zipfile.ZipFile(package / "source.zip") as archive:
                archive.extractall(root)
        except (OSError, zipfile.BadZipFile) as exc:
            failures.append(f"{paper}: source extraction failed: {exc}")
            return
        candidates = sorted(root.rglob("main.tex"))
        check(len(candidates) == 1, f"{paper}: source archive must contain exactly one main.tex", failures)
        if len(candidates) != 1:
            return
        main = candidates[0]
        engine = "-xelatex" if paper == "ORION-24" else "-pdf"
        command = ["latexmk", engine, "-interaction=nonstopmode", "-halt-on-error"]
        if paper in {"ORION-21", "ORION-23"}:
            command.append("-shell-escape")
        command.append("main.tex")
        result = run(command, cwd=main.parent)
        check(result.returncode == 0, f"{paper}: clean source rebuild failed: {result.stdout[-2000:]}{result.stderr[-2000:]}", failures)
        rebuilt = main.with_suffix(".pdf")
        if result.returncode or not rebuilt.is_file():
            return
        rebuilt_text, rebuilt_pages = pdf_text(rebuilt, failures)
        check(rebuilt_pages == expected_pages, f"{paper}: rebuilt page count differs", failures)
        check(normalized(rebuilt_text) == normalized(expected_text),
              f"{paper}: rebuilt PDF text differs from packaged PDF", failures)


def verify_paper(paper: str, manifest_path: Path, rebuild: bool) -> list[str]:
    failures: list[str] = []
    package = manifest_path.parent
    check(package.is_dir(), f"{paper}: package directory missing", failures)
    if not package.is_dir() or not manifest_path.is_file():
        return failures or [f"{paper}: manifest missing"]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{paper}: invalid manifest: {exc}"]

    required_fields = {
        "schema", "paper", "title", "venue", "article_type", "identity_policy",
        "active_authority", "active_authority_sha256", "terminal", "package_status",
        "blocker_classification", "scientific_authority_delta", "pdf_pages",
        "skills_applied", "publication_closure_skill", "verifier",
        "build_environment", "inferential_units", "payload",
    }
    check(required_fields <= set(manifest), f"{paper}: manifest fields missing: {sorted(required_fields - set(manifest))}", failures)
    check(manifest.get("schema") == "ORION.PublicationClosure.v1", f"{paper}: wrong schema", failures)
    check(manifest.get("paper") == paper, f"{paper}: manifest paper mismatch", failures)
    check(manifest.get("scientific_authority_delta") == "NONE", f"{paper}: scientific authority changed", failures)
    blockers = manifest.get("blocker_classification", {})
    check(blockers.get("current_claim_blocker") is False, f"{paper}: unresolved current-claim blocker", failures)
    check(blockers.get("package_blocker") is False, f"{paper}: unresolved package blocker", failures)

    authority = ROOT / str(manifest.get("active_authority", ""))
    check(authority.is_file(), f"{paper}: active authority missing", failures)
    if authority.is_file():
        check(sha256(authority) == manifest.get("active_authority_sha256"),
              f"{paper}: active authority digest drift", failures)
    for label in ("publication_closure_skill", "verifier"):
        binding = manifest.get(label, {})
        bound_path = ROOT / str(binding.get("path", ""))
        check(bound_path.is_file(), f"{paper}: {label} binding path missing", failures)
        if bound_path.is_file():
            check(sha256(bound_path) == binding.get("sha256"), f"{paper}: {label} digest drift", failures)

    payload = manifest.get("payload", {})
    check(isinstance(payload, dict), f"{paper}: payload is not an object", failures)
    expected_payload = {p.name for p in package.iterdir() if p.is_file() and p.name not in {"PACKAGE_MANIFEST.json", "SHA256SUMS"}}
    check(set(payload) == expected_payload, f"{paper}: manifest payload inventory drift", failures)
    check(REQUIRED_PAYLOAD <= set(payload), f"{paper}: required package artifact missing", failures)
    if manifest.get("venue") == "Autonomous Agents and Multi-Agent Systems":
        check("INFORMATION_SHEET.md" in payload, f"{paper}: JAAMAS information sheet missing", failures)
    for rel, metadata in payload.items():
        path = package / rel
        check(path.is_file(), f"{paper}: payload missing: {rel}", failures)
        if path.is_file() and isinstance(metadata, dict):
            check(sha256(path) == metadata.get("sha256"), f"{paper}: payload digest mismatch: {rel}", failures)
            check(path.stat().st_size == metadata.get("bytes"), f"{paper}: payload byte count mismatch: {rel}", failures)
    verify_checksums(package, failures)

    source_text = zip_text(package / "source.zip", failures)
    review_text = zip_text(package / "review_materials.zip", failures)
    rendered, pages = pdf_text(package / "manuscript.pdf", failures)
    metadata = run(["pdfinfo", str(package / "manuscript.pdf")]).stdout
    check(pages == manifest.get("pdf_pages"), f"{paper}: PDF page count drift", failures)
    combined = normalized(rendered)
    for token in CLAIM_TOKENS.get(paper, ()):
        check(normalized(token) in combined, f"{paper}: retained claim/boundary missing from PDF: {token}", failures)
    for token in FORBIDDEN.get(paper, ()):
        screened = combined
        for boundary in ALLOWED_NEGATED_BOUNDARIES.get(paper, {}).get(token, ()):
            screened = screened.replace(normalized(boundary), "")
        check(normalized(token) not in screened, f"{paper}: forbidden promotion in PDF: {token}", failures)

    identity = manifest.get("identity_policy")
    if identity == "double_blind":
        anonymous_surface = normalized(rendered + "\n" + source_text + "\n" + review_text + "\n" + metadata)
        for token in IDENTITY_TOKENS:
            check(normalized(token) not in anonymous_surface, f"{paper}: identity leak in reviewer surface: {token}", failures)
    else:
        identified_surface = normalized(rendered + "\n" + source_text)
        for token in (AUTHOR, EMAIL):
            check(normalized(token) in identified_surface, f"{paper}: identified package missing {token}", failures)

    notice = package.parents[1] / "PUBLICATION_SUPERSESSION_NOTICE_2026-08-31.md"
    check(notice.is_file() and "submission/final-20260831/PACKAGE_MANIFEST.json" in notice.read_text(encoding="utf-8"),
          f"{paper}: supersession notice missing or stale", failures)
    if rebuild and not failures:
        rebuild_from_source(paper, package, rendered, pages, failures)
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("papers", nargs="+", help="Explicit ORION paper identifiers")
    parser.add_argument("--rebuild", action="store_true", help="Clean-build every source archive and compare rendered text")
    args = parser.parse_args(argv)

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    records = {record["paper"]: record for record in registry.get("papers", [])}
    requested = args.papers
    setup_failures: list[str] = []
    check(len(requested) == len(set(requested)), "duplicate paper requested", setup_failures)
    unknown = sorted(set(requested) - set(records))
    check(not unknown, f"unregistered requested papers: {unknown}", setup_failures)
    results: dict[str, dict[str, object]] = {}
    failures = list(setup_failures)
    for paper in requested:
        if paper not in records:
            continue
        before = len(failures)
        manifest = ROOT / records[paper]["package_manifest"]
        failures.extend(verify_paper(paper, manifest, args.rebuild))
        results[paper] = {"ok": len(failures) == before, "failures": failures[before:]}
    check(set(results) == set(requested) - set(unknown), "requested/result coverage mismatch", failures)
    output = {
        "schema": "ORION.PublicationClosureVerification.v1",
        "requested_papers": requested,
        "rebuild": args.rebuild,
        "results": results,
        "all_checks": not failures,
        "failures": failures,
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
