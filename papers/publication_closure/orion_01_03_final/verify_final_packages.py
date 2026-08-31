#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PAPERS = ROOT / "papers"
SKILLS_REVISION = "a45568215d648e5d446a03980277d282b19e57d7"
AUTHOR = "Sze Chun Yiu"
EMAIL = "sze-chun.yiu@fysik.su.se"


@dataclass(frozen=True)
class Package:
    key: str
    root: Path
    canonical: Path
    ledger: Path
    stem: str
    mode: str


PACKAGES = [
    Package(
        "ORION-01A",
        PAPERS / "orion-01-certificate-realization/journal_package_A_final",
        PAPERS / "orion-01-certificate-realization/theory-A-MANUSCRIPT_V3.md",
        PAPERS / "orion-01-certificate-realization/theory-A-CLAIM_LEDGER_V3.md",
        "Restore-Sensitive_Support_Normal_Forms_for_Multi-Tag_Quantum_Compilation",
        "quantum",
    ),
    Package(
        "ORION-01B",
        PAPERS / "orion-01-certificate-realization/journal_package_B_final",
        PAPERS / "orion-01-certificate-realization/theory-B-MANUSCRIPT_V3.md",
        PAPERS / "orion-01-certificate-realization/theory-B-CLAIM_LEDGER_V3.md",
        "Certifiable_Support_Budgets_versus_Intrinsic_Support_in_Quantum_Compilation",
        "quantum",
    ),
    Package(
        "ORION-02",
        PAPERS / "orion-02-fiberguard-finite-fibre/journal_package_final",
        PAPERS / "orion-02-fiberguard-finite-fibre/MANUSCRIPT_V3.md",
        PAPERS / "orion-02-fiberguard-finite-fibre/CLAIM_LEDGER_V3.md",
        "When_a_Representation_Can_Certify",
        "tmlr",
    ),
    Package(
        "ORION-03",
        PAPERS / "orion-03-typed-merge-falsification/journal_package_final",
        PAPERS / "orion-03-typed-merge-falsification/MANUSCRIPT_V3.md",
        PAPERS / "orion-03-typed-merge-falsification/CLAIM_LEDGER_V3.md",
        "Typed_Scientific_Authority_with_Fail-Closed_Nonpromotion",
        "springer",
    ),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def verify_checksums(root: Path, failures: list[str]) -> None:
    checksum_file = root / "SHA256SUMS"
    check(checksum_file.is_file(), f"{root}: missing SHA256SUMS", failures)
    if not checksum_file.is_file():
        return
    seen: set[str] = set()
    for line in checksum_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, rel = line.split("  ", 1)
        path = root / rel
        seen.add(rel)
        check(path.is_file(), f"{root}: checksum path missing: {rel}", failures)
        if path.is_file():
            check(sha256(path) == digest, f"{root}: checksum mismatch: {rel}", failures)
    actual = {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and p.name != "SHA256SUMS"
    }
    check(seen == actual, f"{root}: checksum inventory differs from package inventory", failures)


def archive_texts(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    with zipfile.ZipFile(path) as zf:
        bad = zf.testzip()
        if bad is not None:
            raise RuntimeError(f"corrupt zip member {bad} in {path}")
        for name in zf.namelist():
            if name.endswith("/"):
                continue
            try:
                result[name] = zf.read(name).decode("utf-8")
            except UnicodeDecodeError:
                pass
    return result


def verify_common(pkg: Package, failures: list[str]) -> tuple[str, str]:
    root = pkg.root
    check(root.is_dir(), f"{pkg.key}: final package directory missing", failures)
    if not root.is_dir():
        return "", ""
    verify_checksums(root, failures)

    manifest_path = root / "PACKAGE_MANIFEST.json"
    check(manifest_path.is_file(), f"{pkg.key}: missing package manifest", failures)
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        check(manifest.get("academic_paper_skills_revision") == SKILLS_REVISION, f"{pkg.key}: wrong academic-paper-skills revision", failures)
        check(manifest.get("canonical_science_sha256") == sha256(pkg.canonical), f"{pkg.key}: canonical science binding drift", failures)
        check(manifest.get("claim_ledger_sha256") == sha256(pkg.ledger), f"{pkg.key}: claim ledger binding drift", failures)
        check(manifest.get("scientific_authority_delta") == "NONE__EDITORIAL_AND_PACKAGE_CLOSURE_ONLY", f"{pkg.key}: package claims a scientific authority delta", failures)
        files = manifest.get("files", {})
        for rel, digest in files.items():
            p = root / rel
            check(p.is_file(), f"{pkg.key}: manifest path missing: {rel}", failures)
            if p.is_file():
                check(sha256(p) == digest, f"{pkg.key}: manifest digest mismatch: {rel}", failures)

    ledger_copy = root / "CLAIM_LEDGER.md"
    check(ledger_copy.is_file() and ledger_copy.read_bytes() == pkg.ledger.read_bytes(), f"{pkg.key}: final claim ledger is not byte-identical to live ledger", failures)

    manuscript_path = root / "MANUSCRIPT.md"
    check(manuscript_path.is_file(), f"{pkg.key}: missing publication manuscript", failures)
    manuscript = manuscript_path.read_text(encoding="utf-8") if manuscript_path.is_file() else ""
    forbidden = [
        "canonical submission manuscript V3",
        "scientific successor manuscript V3",
        "## Publication decision record",
        "C_R23_PMLB_BACKOFF_COVERAGE_IMPROVED_BELOW_GATE",
        "C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID",
        "rounds/r23-density-backoff-revival",
        "packages/typed-merge-evaluator",
        "M4_OURS_B",
        "PARITY_PARTITION",
    ]
    for token in forbidden:
        check(token not in manuscript, f"{pkg.key}: internal control token leaked into publication surface: {token}", failures)

    submission = root / "submission"
    tex = submission / f"{pkg.stem}.tex"
    pdf = submission / f"{pkg.stem}.pdf"
    check(tex.is_file(), f"{pkg.key}: missing TeX", failures)
    check(pdf.is_file(), f"{pkg.key}: missing PDF", failures)
    tex_text = tex.read_text(encoding="utf-8") if tex.is_file() else ""
    pdf_text = ""
    if pdf.is_file():
        info = run(["pdfinfo", str(pdf)])
        check(info.returncode == 0, f"{pkg.key}: pdfinfo failed", failures)
        extract = run(["pdftotext", str(pdf), "-"])
        check(extract.returncode == 0 and bool(extract.stdout.strip()), f"{pkg.key}: PDF text extraction failed/empty", failures)
        pdf_text = extract.stdout
        check(b"%%EOF" in pdf.read_bytes()[-2048:], f"{pkg.key}: PDF EOF marker missing", failures)
    return manuscript, tex_text + "\n" + pdf_text


def verify_claim_boundaries(pkg: Package, manuscript: str, rendered: str, failures: list[str]) -> None:
    if pkg.key == "ORION-01A":
        for token in ("mu >= (b-1)t_R", "kappa_R6M=2", "General MultiTag sharpness is open", "physical quantum advantage"):
            check(token in manuscript, f"{pkg.key}: bounded claim/limitation missing: {token}", failures)
        check("General MultiTag intrinsic support equals" not in manuscript, f"{pkg.key}: forbidden general intrinsic-support promotion", failures)
    elif pkg.key == "ORION-01B":
        for token in ("beta_rank-only(R6I)=5", "kappa_R6I=1", "Theta(n^(4t))", "not an algorithm-independent"):
            check(token in manuscript, f"{pkg.key}: bounded support-separation claim missing: {token}", failures)
        check("every local" in manuscript and "No lower bound is proved for every local" in manuscript, f"{pkg.key}: proof-system limitation missing", failures)
    elif pkg.key == "ORION-02":
        required = (
            "44/44",
            "20/44",
            "14 versus 20",
            "11/44",
            "0.061381",
            "0.016837",
            "-0.1442",
            "p=0.3528",
            "does not directly measure `D(z)`",
            "not a claim of broad empirical transfer",
            "in-repository checkers",
            "not external replication",
        )
        for token in required:
            check(token in manuscript, f"{pkg.key}: preserved adverse/boundary statement missing: {token}", failures)
        check("Exhaustive independent checks" not in manuscript, f"{pkg.key}: ambiguous external-independence wording survived", failures)
    elif pkg.key == "ORION-03":
        required = (
            "46 registered hybrid merge obstructions among 1,962",
            "4 unsafe merges",
            "63 needless rejections",
            "incurs 14",
            "analytic consequence",
            "not a security evaluation",
            "Generic fixed-point, provenance and retraction mathematics is donor-owned",
        )
        for token in required:
            check(token in manuscript, f"{pkg.key}: measured/analytic authority boundary missing: {token}", failures)
        check("detector-performance measurements" in manuscript, f"{pkg.key}: analytic-metric nonpromotion warning missing", failures)

    check("broad empirical superiority" not in rendered.lower() or "no broad empirical superiority" in manuscript.lower(), f"{pkg.key}: broad superiority phrasing not bounded", failures)


def verify_venue_surface(pkg: Package, rendered: str, failures: list[str]) -> None:
    submission = pkg.root / "submission"
    if pkg.mode == "tmlr":
        check("Anonymous authors" in rendered, "ORION-02: TMLR PDF/source is not anonymized", failures)
        check(AUTHOR not in rendered and EMAIL not in rendered, "ORION-02: author identity leaked into TMLR manuscript surface", failures)
        for name in ("tmlr.sty", "tmlr.bst", f"{pkg.stem}_tmlr_source.zip", f"{pkg.stem}_supplementary_anonymous.zip"):
            check((submission / name).is_file(), f"ORION-02: TMLR package missing {name}", failures)
        supp = submission / f"{pkg.stem}_supplementary_anonymous.zip"
        if supp.is_file():
            texts = archive_texts(supp)
            joined = "\n".join(texts.values())
            for token in (AUTHOR, EMAIL, "ORION", "orion-"):
                check(token.lower() not in joined.lower(), f"ORION-02: anonymity leak in supplement: {token}", failures)
            check("check_fibre_diameter_floor.py" in texts and "check_refinement_to_certifiability.py" in texts, "ORION-02: live V3 finite checkers absent from supplement", failures)
            check("verify_public_claims.py" not in texts, "ORION-02: superseded low-order-information verifier leaked into final supplement", failures)
    elif pkg.mode == "quantum":
        check(AUTHOR in rendered, f"{pkg.key}: author missing from single-blind Quantum manuscript", failures)
        check("Tool-use disclosure" in rendered, f"{pkg.key}: tool-use disclosure missing", failures)
        check(not (submission / "cover_letter.md").exists(), f"{pkg.key}: unnecessary Quantum cover letter included", failures)
        check((submission / f"{pkg.stem}_arxiv_source.zip").is_file(), f"{pkg.key}: arXiv source archive missing", failures)
    else:
        check(AUTHOR in rendered, "ORION-03: author missing from journal manuscript", failures)
        check((submission / "cover_letter.md").is_file(), "ORION-03: cover-letter draft missing", failures)
        check((submission / f"{pkg.stem}_artifact.zip").is_file(), "ORION-03: artifact archive missing", failures)


def main() -> int:
    failures: list[str] = []
    results: dict[str, dict[str, object]] = {}
    for pkg in PACKAGES:
        before = len(failures)
        manuscript, rendered = verify_common(pkg, failures)
        verify_claim_boundaries(pkg, manuscript, rendered, failures)
        verify_venue_surface(pkg, rendered, failures)
        results[pkg.key] = {"ok": len(failures) == before, "new_failures": failures[before:]}

    result = {
        "schema": "ORION.PublicationClosure.ORION01_03.FinalVerification.v1",
        "academic_paper_skills_revision": SKILLS_REVISION,
        "scientific_authority_delta": "NONE__EDITORIAL_AND_PACKAGE_CLOSURE_ONLY",
        "packages": results,
        "all_checks": not failures,
        "failures": failures,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
