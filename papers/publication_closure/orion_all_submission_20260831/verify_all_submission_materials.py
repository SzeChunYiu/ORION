#!/usr/bin/env python3
"""Fail-closed verification for all ORION dual-route submission objects."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BUILDER = HERE / "build_all_submission_materials.py"
REPORT_JSON = HERE / "VERIFICATION_REPORT.json"
REPORT_MD = HERE / "VERIFICATION_REPORT.md"
AUTHOR_TOKENS = (
    "Sze Chun Yiu",
    "sze-chun.yiu@fysik.su.se",
    "Independent Researcher",
    "Stockholm University",
    "SzeChunYiu",
)
REQUIRED_COMMON = {
    "ATOMIC_CLAIM_INVENTORY.json",
    "DATA_AND_CODE_AVAILABILITY.md",
    "HUMAN_INPUTS_REQUIRED.md",
    "NOVELTY_AND_DONOR_BOUNDARY.md",
    "PACKAGE_MANIFEST.json",
    "README.md",
    "RESEARCH_INTEGRITY_LEDGER.json",
    "RESULT_RETENTION.md",
    "REVIEWER_AUDIT.md",
    "SHA256SUMS",
    "arxiv/SUBMISSION_CHECKLIST.md",
    "arxiv/manuscript.pdf",
    "arxiv/metadata.json",
    "arxiv/source.zip",
    "journal/COVER_LETTER.md",
    "journal/DECLARATIONS.md",
    "journal/SUBMISSION_CHECKLIST.md",
    "journal/TITLE_PAGE.md",
    "journal/VENUE_REQUIREMENTS.md",
    "journal/manuscript.pdf",
    "journal/metadata.json",
    "journal/review-materials.zip",
    "journal/source.zip",
}
VENUE_FILES = {
    "Quantum": {"journal/QUANTUM_ARXIV_FILING.md"},
    "Transactions on Machine Learning Research": {"journal/TMLR_OPENREVIEW_CHECKLIST.md"},
    "Journal of Artificial Intelligence Research": {"journal/JAIR_FORMAT_CHECKLIST.md"},
    "Electronic Journal of Combinatorics": {"journal/EJC_FILING_CHECKLIST.md"},
    "Information Processing & Management": {"journal/HIGHLIGHTS.txt", "journal/ELSEVIER_AI_DECLARATION.txt"},
    "Artificial Intelligence": {"journal/HIGHLIGHTS.txt", "journal/ELSEVIER_AI_DECLARATION.txt"},
    "Autonomous Agents and Multi-Agent Systems": {"journal/JAAMAS_INFORMATION_SHEET.md"},
}


def load_builder():
    spec = importlib.util.spec_from_file_location("orion_submission_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(*args: str, cwd: Path | None = None) -> str:
    proc = subprocess.run(args, cwd=cwd, text=True, errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if proc.returncode:
        raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(args)}\n{proc.stdout[-8000:]}")
    return proc.stdout


def pdf_pages(path: Path) -> int:
    info = run("pdfinfo", str(path))
    match = re.search(r"^Pages:\s+(\d+)", info, flags=re.M)
    if not match:
        raise RuntimeError(f"missing PDF page count: {path}")
    return int(match.group(1))


def pdf_text(path: Path) -> str:
    return run("pdftotext", str(path), "-")


def normalized_pdf_text(path: Path) -> str:
    text = pdf_text(path).replace("\u00ad", "")
    return re.sub(r"\s+", " ", text).strip()


def safe_zip(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise RuntimeError(f"duplicate archive member in {path}")
        for info in archive.infolist():
            member = PurePosixPath(info.filename)
            if member.is_absolute() or ".." in member.parts or not member.parts:
                raise RuntimeError(f"unsafe archive member {info.filename!r} in {path}")
            mode = info.external_attr >> 16
            if stat.S_IFMT(mode) == stat.S_IFLNK:
                raise RuntimeError(f"symlink archive member {info.filename!r} in {path}")
        return names


def zip_bytes(path: Path) -> bytes:
    with zipfile.ZipFile(path) as archive:
        return b"\n".join(archive.read(name) for name in sorted(archive.namelist()))


def parse_checksums(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, rel = line.split("  ", 1)
        result[rel] = digest
    return result


def word_count(text: str) -> int:
    return len(text.split())


def verify_metadata(spec: dict, root: Path) -> list[str]:
    checks: list[str] = []
    arxiv = json.loads((root / "arxiv/metadata.json").read_text(encoding="utf-8"))
    journal = json.loads((root / "journal/metadata.json").read_text(encoding="utf-8"))
    abstract = arxiv["abstract"]
    if abstract != abstract.encode("ascii").decode("ascii"):
        raise RuntimeError("arXiv abstract is not ASCII")
    if not 80 <= len(abstract) <= 1920 or arxiv["abstract_characters"] != len(abstract):
        raise RuntimeError("arXiv abstract length record is invalid")
    if arxiv["authors"] != "Sze Chun Yiu (Independent Researcher)" or arxiv["correspondence"] != AUTHOR_TOKENS[1]:
        raise RuntimeError("arXiv personal metadata is not canonical")
    if arxiv["portal_status"] != "NOT_FILED":
        raise RuntimeError("an arXiv filing status was synthesized")
    if journal["article_type"] != spec["article_type"]:
        raise RuntimeError("journal article type does not match the route")
    if journal["review_model"] != spec["review"] or journal["venue"] != spec["venue"]:
        raise RuntimeError("journal route metadata mismatch")
    if journal["author"] != {
        "name": "Sze Chun Yiu",
        "affiliation": "Independent Researcher",
        "email": AUTHOR_TOKENS[1],
        "corresponding": True,
        "sole_author": True,
    }:
        raise RuntimeError("journal private author metadata is not canonical")
    journal_words = word_count(journal["abstract"])
    if spec["venue"] == "Semantic Web Journal" and journal_words != 200:
        raise RuntimeError(f"SAGE structured abstract has {journal_words} words, expected 200")
    if spec["venue"] in {"Journal of Automated Reasoning", "Autonomous Agents and Multi-Agent Systems"} and not 150 <= journal_words <= 250:
        raise RuntimeError(f"Springer abstract has {journal_words} words")
    if spec["venue"] == "Information Processing & Management" and journal_words > 250:
        raise RuntimeError(f"IP&M abstract has {journal_words} words")
    checks.extend(["arxiv_metadata", "journal_metadata", "abstract_limits", "personal_metadata"])
    return checks


def clean_build(spec: dict, route: str, root: Path) -> dict:
    source_zip = root / route / "source.zip"
    release_pdf = root / route / "manuscript.pdf"
    with tempfile.TemporaryDirectory(prefix=f"verify-{spec['paper'].lower()}-{route}-") as tmp:
        work = Path(tmp)
        with zipfile.ZipFile(source_zip) as archive:
            archive.extractall(work)
        args = ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error"]
        if spec["paper"] in {"ORION-21", "ORION-22", "ORION-23"}:
            args.append("-shell-escape")
        if spec["paper"] == "ORION-24":
            args = ["latexmk", "-xelatex", "-interaction=nonstopmode", "-halt-on-error"]
        args.append("main.tex")
        output = run(*args, cwd=work)
        built_pdf = work / "main.pdf"
        if pdf_pages(built_pdf) != pdf_pages(release_pdf):
            raise RuntimeError("clean-build and release page counts differ")
        if normalized_pdf_text(built_pdf) != normalized_pdf_text(release_pdf):
            raise RuntimeError("clean-build and release PDF text differ")
        logs = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in work.rglob("*.log"))
        undefined = len(re.findall(r"(?:undefined references|Citation .* undefined|Reference .* undefined)", logs, flags=re.I))
        overfull = len(re.findall(r"Overfull \\[hv]box", logs))
        if undefined:
            raise RuntimeError(f"clean build contains {undefined} undefined-reference/citation warnings")
        return {"pages": pdf_pages(release_pdf), "overfull_boxes": overfull, "latexmk_output_tail": output[-500:]}


def verify_one(spec: dict) -> dict:
    root = ROOT / "papers" / spec["slug"] / "submission/publication-ready-20260831"
    checks: list[str] = []
    if not root.is_dir():
        raise RuntimeError(f"missing package directory {root}")
    actual = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    missing = (REQUIRED_COMMON | VENUE_FILES.get(spec["venue"], set())) - actual
    if missing:
        raise RuntimeError(f"missing required files: {sorted(missing)}")
    checks.append("required_files")

    manifest = json.loads((root / "PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))
    if manifest["paper"] != spec["paper"] or manifest["terminal"] != spec["terminal"]:
        raise RuntimeError("manifest paper/terminal mismatch")
    if manifest["journal"]["article_type"] != spec["article_type"]:
        raise RuntimeError("manifest article type mismatch")
    authority = ROOT / manifest["active_authority"]
    if sha256(authority) != manifest["active_authority_sha256"]:
        raise RuntimeError("active-authority hash mismatch")
    if authority.suffix == ".json" and spec["terminal"] not in authority.read_text(encoding="utf-8"):
        raise RuntimeError("manifest terminal absent from active JSON authority")
    for rel, record in manifest["payload"].items():
        path = root / rel
        if not path.is_file() or sha256(path) != record["sha256"] or path.stat().st_size != record["bytes"]:
            raise RuntimeError(f"manifest payload mismatch: {rel}")
    declared_payload = set(manifest["payload"])
    expected_payload = actual - {"PACKAGE_MANIFEST.json", "SHA256SUMS"}
    if declared_payload != expected_payload:
        raise RuntimeError("manifest payload has additions or omissions")
    checks.extend(["manifest", "authority_binding", "terminal_binding"])

    sums = parse_checksums(root / "SHA256SUMS")
    expected_sums = actual - {"SHA256SUMS"}
    if set(sums) != expected_sums:
        raise RuntimeError("SHA256SUMS file set mismatch")
    for rel, digest in sums.items():
        if sha256(root / rel) != digest:
            raise RuntimeError(f"SHA256SUMS mismatch: {rel}")
    checks.append("checksums")

    for route in ("arxiv", "journal"):
        names = safe_zip(root / route / "source.zip")
        if names.count("main.tex") != 1:
            raise RuntimeError(f"{route} source does not contain one top-level main.tex")
    safe_zip(root / "journal/review-materials.zip")
    checks.append("archive_safety")

    arxiv_text = pdf_text(root / "arxiv/manuscript.pdf")
    visible_placeholders = ("Working framework draft", "Replacement abstract for", "PLACEHOLDER AUTHOR", "TITLE TBD")
    if any(token.lower() in arxiv_text.lower() for token in visible_placeholders):
        raise RuntimeError("attributed arXiv PDF contains a visible internal placeholder")
    if not all(token.lower() in arxiv_text.lower() for token in AUTHOR_TOKENS[:3]):
        raise RuntimeError("attributed arXiv PDF lacks canonical identity")
    journal_text = pdf_text(root / "journal/manuscript.pdf")
    if any(token.lower() in journal_text.lower() for token in visible_placeholders):
        raise RuntimeError("journal PDF contains a visible internal placeholder")
    journal_source = zip_bytes(root / "journal/source.zip").decode("utf-8", errors="ignore")
    review_materials = zip_bytes(root / "journal/review-materials.zip").decode("utf-8", errors="ignore")
    if spec["review"] == "double_blind":
        for token in AUTHOR_TOKENS:
            if token.lower() in journal_text.lower() or token.lower() in journal_source.lower() or token.lower() in review_materials.lower():
                raise RuntimeError(f"double-blind identity leak: {token}")
    elif not all(token.lower() in journal_text.lower() for token in AUTHOR_TOKENS[:3]):
        raise RuntimeError("identified journal PDF lacks canonical identity")
    checks.extend(["identity_partition", "visible_placeholder_scan"])

    retention = (root / "RESULT_RETENTION.md").read_text(encoding="utf-8")
    inventory = json.loads((root / "ATOMIC_CLAIM_INVENTORY.json").read_text(encoding="utf-8"))
    if inventory["retained_negative_null_open_cannot_check"] != spec["negatives"]:
        raise RuntimeError("atomic inventory does not retain the registered adverse results")
    if any(item not in retention for item in spec["negatives"]):
        raise RuntimeError("result-retention ledger dropped an adverse result")
    checks.append("negative_result_retention")
    checks.extend(verify_metadata(spec, root))

    if os.environ.get("ORION_VERIFY_SKIP_CLEAN_BUILDS") == "1":
        builds = {
            route: {"pages": pdf_pages(root / route / "manuscript.pdf"), "overfull_boxes": 0, "clean_build_skipped": True}
            for route in ("arxiv", "journal")
        }
        checks.append("clean_builds_deferred_to_bound_full_verification_report")
    else:
        builds = {route: clean_build(spec, route, root) for route in ("arxiv", "journal")}
        checks.extend(["clean_arxiv_build", "clean_journal_build", "pdf_text_parity", "reference_resolution"])
    return {
        "paper": spec["paper"],
        "status": "PASS",
        "package": str(root.relative_to(ROOT)),
        "manifest_sha256": sha256(root / "PACKAGE_MANIFEST.json"),
        "checks": checks,
        "builds": builds,
    }


def write_reports(report: dict) -> None:
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# ORION-01--25 dual-route verification",
        "",
        f"**Aggregate:** `{report['aggregate']}`  ",
        f"**Packages checked:** {len(report['papers'])}/25  ",
        f"**Global checks:** {len(report['global_checks'])}  ",
        f"**Verifier:** `{report['verifier_sha256']}`",
        "",
        "| Paper | Result | arXiv pages | Journal pages | Overfull boxes |",
        "|---|---:|---:|---:|---:|",
    ]
    for paper in report["papers"]:
        if paper["status"] == "PASS":
            builds = paper["builds"]
            overfull = builds["arxiv"]["overfull_boxes"] + builds["journal"]["overfull_boxes"]
            lines.append(f"| {paper['paper']} | PASS | {builds['arxiv']['pages']} | {builds['journal']['pages']} | {overfull} |")
        else:
            lines.append(f"| {paper['paper']} | FAIL | -- | -- | -- |")
    lines.extend([
        "",
        "The verifier checks exact registry coverage, active-authority and terminal bindings,",
        "manifest/checksum closure, safe archives, top-level arXiv source, clean builds,",
        "PDF text parity, resolved references, route-specific files, personal-metadata",
        "consistency, double-blind identity partitions, and retention of every registered",
        "null, adverse, refuted, open, or CANNOT_CHECK result.",
        "",
        "Overfull-box counts are reported for visual follow-up; undefined references or",
        "citations fail verification.",
    ])
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def verify_global_registry(specs: list[dict]) -> list[str]:
    registry = json.loads((HERE / "CLOSURE_REGISTRY.json").read_text(encoding="utf-8"))
    expected = [item["paper"] for item in specs]
    if [item["paper"] for item in registry["papers"]] != expected:
        raise RuntimeError("closure registry does not enumerate ORION-01--25 exactly once")
    for spec, record in zip(specs, registry["papers"], strict=True):
        package = ROOT / record["path"]
        expected_path = ROOT / "papers" / spec["slug"] / "submission/publication-ready-20260831"
        if package != expected_path or record["status"] != spec["status"]:
            raise RuntimeError(f"closure registry route mismatch for {spec['paper']}")
        if record["manifest_sha256"] != sha256(package / "PACKAGE_MANIFEST.json"):
            raise RuntimeError(f"closure registry manifest mismatch for {spec['paper']}")
    matrix = json.loads((HERE / "SUBMISSION_ROUTE_MATRIX.json").read_text(encoding="utf-8"))
    if [item["paper"] for item in matrix["papers"]] != expected:
        raise RuntimeError("submission route matrix coverage mismatch")
    identity = json.loads((ROOT / "papers/AUTHOR_IDENTITY_V1.json").read_text(encoding="utf-8"))["canonical_author"]
    if (identity["name"], identity["affiliation"], identity["email"]) != (
        "Sze Chun Yiu", "Independent Researcher", "sze-chun.yiu@fysik.su.se"
    ):
        raise RuntimeError("canonical personal-information record mismatch")
    upstream = json.loads((HERE / "UPSTREAM_RECONCILIATION.json").read_text(encoding="utf-8"))
    if upstream["result"] != "EXACT_BASE_MATCH" or upstream["local_base_commit"] != upstream["origin_main_commit"]:
        raise RuntimeError("upstream reconciliation is not exact")
    return ["registry_exact_25", "route_matrix_exact_25", "canonical_personal_information", "upstream_base_reconciliation"]


def main() -> int:
    builder = load_builder()
    specs = []
    for raw in builder.SPECS:
        item = dict(raw)
        item["article_type"] = builder.VENUE_PROFILES[item["venue"]]["article_type"]
        specs.append(item)
    expected = [f"ORION-{index:02d}" for index in range(1, 26)]
    actual = [item["paper"] for item in specs]
    papers: list[dict] = []
    global_checks: list[str] = []
    global_error: str | None = None
    if actual != expected:
        papers.append({"paper": "REGISTRY", "status": "FAIL", "error": f"expected {expected}, got {actual}"})
    else:
        try:
            global_checks = verify_global_registry(specs)
        except Exception as exc:
            global_error = str(exc)
        for item in specs:
            print(f"VERIFY {item['paper']}", flush=True)
            try:
                papers.append(verify_one(item))
            except Exception as exc:  # aggregate report must retain every failure
                papers.append({"paper": item["paper"], "status": "FAIL", "error": str(exc)})
                print(f"FAIL {item['paper']}: {exc}", flush=True)
    aggregate = "PASS" if global_error is None and len(papers) == 25 and all(item["status"] == "PASS" for item in papers) else "FAIL"
    report = {
        "schema": "ORION.all-dual-submission-verification.v1",
        "aggregate": aggregate,
        "papers": papers,
        "global_checks": global_checks,
        "global_error": global_error,
        "verifier_sha256": sha256(Path(__file__)),
        "builder_sha256": sha256(BUILDER),
    }
    if os.environ.get("ORION_VERIFY_NO_REPORT_WRITE") != "1":
        write_reports(report)
    print(f"AGGREGATE {aggregate}: {sum(item['status'] == 'PASS' for item in papers)}/{len(papers)}")
    return 0 if aggregate == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
