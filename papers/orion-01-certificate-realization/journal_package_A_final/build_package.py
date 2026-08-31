#!/usr/bin/env python3
"""Build one exact ORION-01 Quantum/arXiv handoff package."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PAPER_ROOT = REPO / "papers" / "orion-01-certificate-realization"
SKILL_REVISION = "0d0be4a9b69ebe709cb40e79d0ef197dc1debf2d"
TERMINAL = "PACKAGE_COMPLETE_PENDING_FINAL_AUTHOR_CONFIRMATION_AND_ARXIV_POSTING"
SOURCE_DATE_EPOCH = "1788134400"  # 2026-08-31T00:00:00Z


CONFIG = {
    "journal_package_A_final": {
        "paper": "ORION-01A",
        "canonical": "theory-A-MANUSCRIPT_V3.md",
        "ledger": "theory-A-CLAIM_LEDGER_V3.md",
        "stem": "Restore-Sensitive_Support_Normal_Forms_for_Multi-Tag_Quantum_Compilation",
        "control": "finite_records.json",
    },
    "journal_package_B_final": {
        "paper": "ORION-01B",
        "canonical": "theory-B-MANUSCRIPT_V3.md",
        "ledger": "theory-B-CLAIM_LEDGER_V3.md",
        "stem": "Certifiable_Support_Budgets_versus_Intrinsic_Support_in_Quantum_Compilation",
        "control": "certificate_control_records.json",
    },
}[HERE.name]


def run(*args: str, cwd: Path | None = None, capture: bool = False) -> str:
    completed = subprocess.run(
        args,
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
        env={**os.environ, "SOURCE_DATE_EPOCH": SOURCE_DATE_EPOCH},
    )
    return completed.stdout or ""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path: Path) -> dict[str, object]:
    return {"bytes": path.stat().st_size, "sha256": sha256(path)}


def split_manuscript(markdown: str) -> tuple[str, str, str, str]:
    lines = markdown.splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValueError("canonical manuscript must start with a level-one title")
    title = lines[0][2:].strip()
    try:
        abstract_index = lines.index("## Abstract")
        keyword_index = next(
            index
            for index in range(abstract_index + 1, len(lines))
            if lines[index].startswith("**Keywords:**")
        )
    except (ValueError, StopIteration) as exc:
        raise ValueError("canonical manuscript lacks the expected Abstract/Keywords surface") from exc
    abstract = "\n".join(lines[abstract_index + 1 : keyword_index]).strip()
    keywords = lines[keyword_index].removeprefix("**Keywords:**").strip()
    body = "\n".join(lines[keyword_index + 1 :]).strip() + "\n"
    return title, abstract, keywords, body


def tex_fragment(markdown: str, *, shift: bool = False) -> str:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        source = root / "fragment.md"
        target = root / "fragment.tex"
        source.write_text(markdown + "\n", encoding="utf-8")
        command = [
            "pandoc",
            str(source),
            "--from=markdown+pipe_tables+tex_math_single_backslash+raw_tex",
            "--to=latex",
            "--wrap=preserve",
            "--output",
            str(target),
        ]
        if shift:
            command.append("--shift-heading-level-by=-1")
        run(*command)
        rendered = target.read_text(encoding="utf-8").strip()
        # The canonical Markdown carries explicit section numbers.  Star the
        # generated LaTeX headings so the PDF does not print each number twice.
        return re.sub(
            r"\\(section|subsection|subsubsection)\{",
            lambda match: f"\\{match.group(1)}*{{",
            rendered,
        )


def latex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    return "".join(replacements.get(character, character) for character in value)


def render_tex(markdown: str) -> str:
    title, abstract, keywords, body = split_manuscript(markdown)
    abstract_tex = tex_fragment(abstract)
    body_tex = tex_fragment(body, shift=True)
    return f"""\\documentclass[11pt]{{article}}
\\usepackage[margin=1in]{{geometry}}
\\usepackage{{amsmath,amssymb,mathtools}}
\\usepackage[T1]{{fontenc}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{lmodern}}
\\usepackage{{microtype}}
\\usepackage{{booktabs,longtable,array}}
\\usepackage{{xurl}}
\\usepackage[hidelinks]{{hyperref}}
\\setlength{{\\emergencystretch}}{{3em}}
\\providecommand{{\\tightlist}}{{\\setlength{{\\itemsep}}{{0pt}}\\setlength{{\\parskip}}{{0pt}}}}
\\title{{{latex_escape(title)}}}
\\author{{Sze Chun Yiu}}
\\date{{}}
\\hypersetup{{pdftitle={{{latex_escape(title)}}},pdfauthor={{Sze Chun Yiu}}}}
\\begin{{document}}
\\maketitle
\\begin{{abstract}}
{abstract_tex}
\\end{{abstract}}
\\noindent\\textbf{{Keywords:}} {latex_escape(keywords)}

{body_tex}
\\end{{document}}
"""


def zip_deterministically(output: Path, members: list[tuple[str, Path]]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, path in sorted(members):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())


def copy_common_ancillary(ancillary: Path) -> None:
    closeout = PAPER_ROOT / "v3-bounded-closeout-2026-08-29"
    for name in ("proof_checker_v3.py", "test_proof_checker_v3.py", "PROOF_CHECK_RESULT_V3.json"):
        shutil.copy2(closeout / name, ancillary / name)
    adverse_source = PAPER_ROOT / "experiments" / "r11-pyzx-full-reduce"
    adverse_target = ancillary / "adverse-pyzx-round1"
    adverse_target.mkdir(parents=True, exist_ok=True)
    for name in (
        "ORION01_R11_PYZX_RESULTS.json",
        "ORION01_R11_ROUND1_STATUS.json",
        "ORION01_R11_PYZX_ADVERSE_INTERPRETATION.md",
        "ORION01_R11_PYZX_COUNTEREXAMPLE_BEFORE.json",
        "ORION01_R11_PYZX_COUNTEREXAMPLE_AFTER.json",
    ):
        shutil.copy2(adverse_source / name, adverse_target / name)


def build() -> None:
    for cache in sorted(HERE.rglob("__pycache__"), reverse=True):
        if cache.is_dir():
            shutil.rmtree(cache)
    for bytecode in HERE.rglob("*.pyc"):
        bytecode.unlink()

    canonical = PAPER_ROOT / str(CONFIG["canonical"])
    claim_ledger = PAPER_ROOT / str(CONFIG["ledger"])
    manuscript = HERE / "MANUSCRIPT.md"
    packaged_ledger = HERE / "CLAIM_LEDGER.md"
    submission = HERE / "submission"
    ancillary = submission / "anc"
    submission.mkdir(parents=True, exist_ok=True)
    ancillary.mkdir(parents=True, exist_ok=True)

    shutil.copy2(canonical, manuscript)
    shutil.copy2(claim_ledger, packaged_ledger)
    copy_common_ancillary(ancillary)

    stem = str(CONFIG["stem"])
    tex_path = submission / f"{stem}.tex"
    pdf_path = submission / f"{stem}.pdf"
    tex_path.write_text(render_tex(manuscript.read_text(encoding="utf-8")), encoding="utf-8")

    with tempfile.TemporaryDirectory() as temporary:
        output = Path(temporary)
        log = run(
            "tectonic",
            str(tex_path),
            "--outdir",
            str(output),
            "--keep-logs",
            "--keep-intermediates",
            capture=True,
        )
        built_pdf = output / f"{stem}.pdf"
        built_log = output / f"{stem}.log"
        if not built_pdf.is_file():
            raise FileNotFoundError("tectonic did not produce the expected PDF")
        combined_log = log + (built_log.read_text(encoding="utf-8", errors="replace") if built_log.is_file() else "")
        forbidden = ("Undefined control sequence", "LaTeX Error", "Overfull \\hbox", "Overfull \\vbox")
        found = [token for token in forbidden if token in combined_log]
        if found:
            raise RuntimeError("render log contains blocking diagnostics: " + ", ".join(found))
        shutil.copy2(built_pdf, pdf_path)

    archive_members = [("main.tex", tex_path)]
    for path in sorted(ancillary.rglob("*")):
        if path.is_file():
            archive_members.append((path.relative_to(submission).as_posix(), path))
    arxiv_zip = submission / f"{stem}_arxiv_source.zip"
    journal_zip = submission / f"{stem}_journal_source.zip"
    zip_deterministically(arxiv_zip, archive_members)
    journal_members = list(archive_members)
    for name in ("README.md", "submission_checklist.md"):
        journal_members.append((name, submission / name))
    zip_deterministically(journal_zip, journal_members)

    tectonic_version_output = run("tectonic", "--version", capture=True)
    tectonic_match = re.search(r"(?i)tectonic\s+\d+(?:\.\d+)+", tectonic_version_output)
    tool_versions = {
        "pandoc": run("pandoc", "--version", capture=True).splitlines()[0],
        "tectonic": tectonic_match.group(0) if tectonic_match else tectonic_version_output.strip(),
        "python": run("python3", "--version", capture=True).strip(),
    }
    receipt = {
        "schema": "ORION.PublicationClosure.BuildReceipt.v2",
        "paper": CONFIG["paper"],
        "source_date_epoch": SOURCE_DATE_EPOCH,
        "tools": tool_versions,
        "canonical_source": {"path": canonical.relative_to(REPO).as_posix(), **record(canonical)},
        "packaged_source": {"path": "MANUSCRIPT.md", **record(manuscript)},
        "tex": {"path": tex_path.relative_to(HERE).as_posix(), **record(tex_path)},
        "pdf": {"path": pdf_path.relative_to(HERE).as_posix(), **record(pdf_path)},
        "arxiv_source_zip": {"path": arxiv_zip.relative_to(HERE).as_posix(), **record(arxiv_zip)},
        "journal_source_zip": {"path": journal_zip.relative_to(HERE).as_posix(), **record(journal_zip)},
        "source_pdf_binding": "PASS__TEX_GENERATED_FROM_EXACT_PACKAGED_MARKDOWN_AND_PDF_COMPILED_FROM_EXACT_TEX",
    }
    (HERE / "BUILD_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    excluded = {"PACKAGE_MANIFEST.json", "SHA256SUMS", "PUBLICATION_RELEASE_MANIFEST.json"}
    package_files: dict[str, str] = {}
    for path in sorted(HERE.rglob("*")):
        relative = path.relative_to(HERE).as_posix()
        if (
            path.is_file()
            and relative not in excluded
            and "/.tectonic/" not in relative
            and "__pycache__" not in path.parts
            and path.suffix != ".pyc"
        ):
            package_files[relative] = sha256(path)
    manifest = {
        "schema": "ORION.PublicationClosure.FinalJournalPackage.v2",
        "paper": CONFIG["paper"],
        "primary_target": "Quantum",
        "terminal": TERMINAL,
        "academic_paper_skills_revision": SKILL_REVISION,
        "canonical_science_path": canonical.relative_to(REPO).as_posix(),
        "canonical_science_sha256": sha256(canonical),
        "canonical_science_bytes": canonical.stat().st_size,
        "claim_ledger_path": claim_ledger.relative_to(REPO).as_posix(),
        "claim_ledger_sha256": sha256(claim_ledger),
        "claim_ledger_bytes": claim_ledger.stat().st_size,
        "publication_surface_sha256": sha256(manuscript),
        "reader_pdf_sha256": sha256(pdf_path),
        "reader_pdf_bytes": pdf_path.stat().st_size,
        "scientific_authority_delta": "NONE__SCIENTIFIC_DEFINITION_CORRECTION_AND_EDITORIAL_PACKAGE_CLOSURE_ONLY",
        "submission_authority": False,
        "external_peer_review_claimed": False,
        "files": package_files,
    }
    manifest_path = HERE / "PACKAGE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    checksum_paths = [
        path
        for path in sorted(HERE.rglob("*"))
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
    ]
    checksum_paths = [path for path in checksum_paths if path.name != "SHA256SUMS"]
    checksum_text = "".join(f"{sha256(path)}  {path.relative_to(HERE).as_posix()}\n" for path in checksum_paths)
    (HERE / "SHA256SUMS").write_text(checksum_text, encoding="utf-8")

    if manuscript.read_bytes() != canonical.read_bytes():
        raise AssertionError("packaged Markdown is not byte-identical to canonical science")
    if packaged_ledger.read_bytes() != claim_ledger.read_bytes():
        raise AssertionError("packaged claim ledger is not byte-identical to canonical ledger")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    build()
