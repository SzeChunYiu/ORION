#!/usr/bin/env python3
"""Fail-closed filing preflight for the bounded ORION-14 paper.

This program checks repository-available publication authorities only. It does
not submit the paper, infer author declarations, certify novelty, or promote the
bounded scientific claim. A PASS means the repository source/package is ready
for the remaining human portal operations on the declared as-of date.

The native p4-tmlr-submission-audit workflow remains the rendering authority for
the current anonymous PDF. Historical tracked PDF hashes are provenance, not an
immutable requirement after source-preserving re-rendering.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

PASS_TERMINAL = "ORION_14_REPOSITORY_FILING_PREFLIGHT_PASS"
FAIL_TERMINAL = "ORION_14_REPOSITORY_FILING_PREFLIGHT_CANNOT_CHECK"
EXPECTED_SCIENTIFIC_TERMINAL = "ORION-14 = PEER_REVIEW_READY"
HISTORICAL_AUDITED_PDF_SHA256 = "f2ede371e254e37cf57c309565a5ede09ab3d61f9feba75b67eccca2a4893ccf"
FRESHNESS_DATE = dt.date(2026, 8, 17)
FRESHNESS_LAST_VALID_DATE = dt.date(2026, 8, 31)
HASH_LINE = re.compile(r"^([0-9a-fA-F]{64})\s+[* ]?(.+?)\s*$")
PLACEHOLDER = re.compile(
    r"(?i)(?:\bTODO\b|\bTBD\b|\bPLACEHOLDER\b|\bFIXME\b|"
    r"INSERT\s+(?:AUTHOR|AFFILIATION|FUNDING|SUBMISSION)|"
    r"OPENREVIEW\s+SUBMISSION\s+ID\s*[:=]\s*(?:TBD|PLACEHOLDER|XXX))"
)
STALE_STATES = {"STALE", "DRIFTED", "INVALID", "UNBOUND"}


@dataclass(frozen=True)
class Finding:
    check: str
    ok: bool
    detail: str
    path: str | None = None


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(root: Path, *args: str) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *args],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except OSError as exc:
        return False, str(exc)
    return proc.returncode == 0, proc.stdout.strip()


def tracked_files(root: Path, paper: Path) -> list[Path]:
    ok, out = git(root, "ls-files", "-z", str(paper.relative_to(root)))
    if not ok:
        return []
    return [root / rel for rel in out.split("\0") if rel]


def parse_checksum_manifest(root: Path, paper: Path, manifest: Path) -> list[Finding]:
    findings: list[Finding] = []
    parsed = 0
    for line_no, raw in enumerate(manifest.read_text(errors="replace").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = HASH_LINE.match(line)
        if not match:
            findings.append(Finding("checksum_manifest_syntax", False, f"unparseable line {line_no}", str(manifest.relative_to(root))))
            continue
        parsed += 1
        expected, raw_name = match.groups()
        name = raw_name.strip()
        candidates = [manifest.parent / name, paper / name, root / name]
        target = next((p for p in candidates if p.is_file()), None)
        if target is None:
            findings.append(Finding("checksum_manifest_target", False, f"missing target at line {line_no}: {name}", str(manifest.relative_to(root))))
            continue
        observed = sha256(target)
        findings.append(Finding("checksum_manifest_digest", observed.lower() == expected.lower(), f"{name}: expected={expected.lower()} observed={observed}", str(manifest.relative_to(root))))
    findings.append(Finding("checksum_manifest_nonempty", parsed > 0, f"parsed_rows={parsed}", str(manifest.relative_to(root))))
    return findings


def iter_json_objects(value: object) -> Iterable[object]:
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from iter_json_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_json_objects(child)


def stale_json_states(path: Path) -> list[str]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return ["UNREADABLE_JSON"]
    bad: list[str] = []
    for obj in iter_json_objects(value):
        if isinstance(obj, str) and obj.upper() in STALE_STATES:
            bad.append(obj.upper())
    return sorted(set(bad))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2], help="repository root")
    parser.add_argument("--as-of", type=dt.date.fromisoformat, default=dt.datetime.now(dt.timezone.utc).date(), help="filing/preflight date in YYYY-MM-DD")
    parser.add_argument("--write-json", type=Path, default=None)
    parser.add_argument("--write-md", type=Path, default=None)
    args = parser.parse_args(argv)

    root = args.root.resolve()
    paper = root / "papers" / "orion-14-verified-scientific-discovery"
    readiness = paper / "JOURNAL_READINESS.md"
    findings: list[Finding] = []

    findings.append(Finding("paper_directory", paper.is_dir(), str(paper)))
    findings.append(Finding("readiness_document", readiness.is_file(), str(readiness)))
    readiness_text = readiness.read_text(errors="replace") if readiness.is_file() else ""
    findings.append(Finding("bounded_scientific_terminal", EXPECTED_SCIENTIFIC_TERMINAL in readiness_text, EXPECTED_SCIENTIFIC_TERMINAL, str(readiness.relative_to(root)) if readiness.is_file() else None))

    within_window = FRESHNESS_DATE <= args.as_of <= FRESHNESS_LAST_VALID_DATE
    findings.append(Finding("filing_time_literature_window", within_window, f"as_of={args.as_of.isoformat()} valid={FRESHNESS_DATE.isoformat()}..{FRESHNESS_LAST_VALID_DATE.isoformat()}", str(readiness.relative_to(root)) if readiness.is_file() else None))

    ok_head, head = git(root, "rev-parse", "HEAD")
    findings.append(Finding("git_head", ok_head and bool(head), head or "unavailable"))
    cited_commits = sorted(set(re.findall(r"\b[0-9a-f]{40}\b", readiness_text)))
    findings.append(Finding("readiness_commit_denominator", bool(cited_commits), f"cited_full_commits={len(cited_commits)}", str(readiness.relative_to(root)) if readiness.is_file() else None))
    for commit in cited_commits:
        ok, out = git(root, "cat-file", "-e", f"{commit}^{{commit}}")
        findings.append(Finding("readiness_commit_resolves", ok, f"{commit}: {out or 'commit exists'}", str(readiness.relative_to(root)) if readiness.is_file() else None))

    tracked = tracked_files(root, paper)
    findings.append(Finding("tracked_paper_inventory", bool(tracked), f"tracked_files={len(tracked)}", str(paper.relative_to(root))))
    pdfs = [p for p in tracked if p.suffix.lower() == ".pdf" and p.is_file()]
    findings.append(Finding("tracked_pdf_inventory", bool(pdfs), f"tracked_pdfs={len(pdfs)}; historical_audited_sha256={HISTORICAL_AUDITED_PDF_SHA256}", str(pdfs[0].relative_to(root)) if pdfs else None))
    historical_match = next((p for p in pdfs if sha256(p) == HISTORICAL_AUDITED_PDF_SHA256), None)
    findings.append(Finding("historical_pdf_reference_is_non_authoritative", True, "historical digest still present" if historical_match else "current tracked PDF differs; native TMLR audit must render the current source", str(historical_match.relative_to(root)) if historical_match else None))

    current_sources = [p for p in tracked if p.is_file() and p.suffix.lower() in {".tex", ".md", ".bib"} and any(part in {"manuscript", "journal_package"} for part in p.parts)]
    placeholder_hits: list[str] = []
    for source in current_sources:
        for line_no, line in enumerate(source.read_text(errors="replace").splitlines(), 1):
            if PLACEHOLDER.search(line):
                placeholder_hits.append(f"{source.relative_to(root)}:{line_no}")
    findings.append(Finding("submission_source_placeholders", not placeholder_hits, "none" if not placeholder_hits else ", ".join(placeholder_hits[:50])))

    manifest_paths = sorted(p for p in tracked if p.is_file() and p.name == "SHA256SUMS" and "journal_package" in p.parts)
    findings.append(Finding("journal_checksum_manifest", bool(manifest_paths), f"manifests={len(manifest_paths)}"))
    for manifest in manifest_paths:
        findings.extend(parse_checksum_manifest(root, paper, manifest))

    state_files = sorted(p for p in tracked if p.is_file() and p.suffix.lower() == ".json" and any(token in p.name.upper() for token in ("MANIFEST", "STATE", "CLOSURE")) and "archive" not in p.parts)
    for path in state_files:
        bad = stale_json_states(path)
        findings.append(Finding("current_package_not_stale", not bad, "no stale terminal" if not bad else f"stale_states={bad}", str(path.relative_to(root))))

    for pdf in pdfs:
        raw = pdf.read_bytes()
        findings.append(Finding("pdf_header_and_eof", raw.startswith(b"%PDF-") and b"%%EOF" in raw[-4096:], f"bytes={len(raw)}", str(pdf.relative_to(root))))
        if shutil.which("pdfinfo"):
            proc = subprocess.run(["pdfinfo", str(pdf)], check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            findings.append(Finding("pdfinfo_parse", proc.returncode == 0, proc.stdout.strip()[-1000:], str(pdf.relative_to(root))))

    ok_diff, diff = git(root, "diff", "--check")
    findings.append(Finding("git_diff_check", ok_diff, diff or "clean"))
    hard_failures = [f for f in findings if not f.ok]
    result = {
        "schema": "ORION14.RepositoryFilingPreflight.v1",
        "as_of": args.as_of.isoformat(),
        "git_head": head if ok_head else None,
        "scientific_authority_delta": "NONE",
        "submission_authority": False,
        "native_render_authority": "p4-tmlr-submission-audit",
        "human_filing_attestations_required": ["authors_and_affiliations", "CRediT", "funding", "competing_interests", "acknowledgements", "AI_use_declaration", "no_parallel_submission", "real_portal_submission_id"],
        "terminal": PASS_TERMINAL if not hard_failures else FAIL_TERMINAL,
        "ok": not hard_failures,
        "finding_count": len(findings),
        "failure_count": len(hard_failures),
        "findings": [asdict(f) for f in findings],
    }

    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    print(rendered, end="")
    if args.write_json:
        args.write_json.parent.mkdir(parents=True, exist_ok=True)
        args.write_json.write_text(rendered)
    if args.write_md:
        args.write_md.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# ORION-14 repository filing preflight", "", f"- As of: `{result['as_of']}`", f"- Git head: `{result['git_head']}`", f"- Terminal: `{result['terminal']}`", f"- Findings: `{result['finding_count']}`", f"- Failures: `{result['failure_count']}`", "- Scientific authority delta: `NONE`", "- Submission authority: `false`", "- Native render authority: `p4-tmlr-submission-audit`", "", "## Findings", ""]
        for finding in findings:
            marker = "PASS" if finding.ok else "FAIL"
            location = f" — `{finding.path}`" if finding.path else ""
            lines.append(f"- **{marker}** `{finding.check}`: {finding.detail}{location}")
        lines.extend(["", "## Remaining human portal operations", ""])
        lines.extend(f"- {item}" for item in result["human_filing_attestations_required"])
        args.write_md.write_text("\n".join(lines) + "\n")
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
