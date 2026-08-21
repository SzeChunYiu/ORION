#!/usr/bin/env python3
"""Render one paper to PDF, preferring its LaTeX tree.

A paper's `.tex` tree is authoritative when it has one: `latexmk` on
`manuscript/main.tex` (or `paper/main.tex`) is what the repo's own Makefiles
call, and it is what this runs first.

Five registered papers have no LaTeX tree at all -- P6, P7, P8, P10 and P15 --
and `latexmk` is absent from some environments this runs in. So there is a
second path: Markdown -> HTML -> PDF via WeasyPrint, no TeX required. It is a
fallback, never a substitute: if a `.tex` tree exists and `latexmk` is present,
the fallback is not used, and the PDF records which path produced it so a reader
is never left guessing whether they are holding the typeset paper or a
rendering of its Markdown.

The PDF carries a provenance block naming the source file, its sha256, and the
commit the render was taken from. A rendered artifact whose source cannot be
identified is not evidence of anything -- the same rule the content-binding work
applies to every other artifact in this repository.

Usage:
    python scripts/build_paper_pdf.py papers/paper-02-.../MANUSCRIPT.md
    python scripts/build_paper_pdf.py --paper P2
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]

#: Manuscript filenames tried in order when a directory is given. A paper that
#: names its manuscript something else must be passed explicitly rather than
#: guessed at, so a silent fallback cannot render the wrong file.
_MANUSCRIPT_NAMES = ("MANUSCRIPT.md", "PAPER.md", "README.md")

#: Papers whose manuscript is a versioned file under ``manuscript/`` rather than
#: one of the names above. P6 keeps ``manuscript/FINAL_V4.md``; asked for a PDF
#: of P6, the resolver fell through to the paper's ``README.md`` and produced a
#: perfectly valid PDF of the wrong document, announcing only the filename it
#: used. A fallback that yields a plausible artifact without saying it fell back
#: is the same shape as a guard that reports "nothing failed" for "nothing ran".
_VERSIONED_MANUSCRIPT_GLOB = "FINAL_V*.md"
_VERSIONED_MANUSCRIPT_FALLBACK = "FINAL.md"


def find_versioned_manuscript(paper_dir: Path) -> Path | None:
    """The highest-numbered ``manuscript/FINAL_V*.md``, or ``FINAL.md``.

    Sorted by the integer in the name rather than lexically, so ``FINAL_V10``
    would beat ``FINAL_V9`` instead of losing to it.
    """

    manuscript_dir = paper_dir / "manuscript"
    if not manuscript_dir.is_dir():
        return None

    def version_of(path: Path) -> tuple[int, ...]:
        """Version as a tuple, so V2_1 sorts below V4 rather than above it.

        Concatenating the digits reads ``FINAL_V2_1`` as twenty-one and picks it
        over ``FINAL_V4``, which is how the first version of this chose the wrong
        manuscript. A dotted version is a tuple, not an integer.
        """

        tail = path.stem.rsplit("_V", 1)[-1]
        parts = [chunk for chunk in tail.replace(".", "_").split("_") if chunk.isdigit()]
        return tuple(int(chunk) for chunk in parts) if parts else (-1,)

    versioned = sorted(manuscript_dir.glob(_VERSIONED_MANUSCRIPT_GLOB), key=version_of)
    if versioned:
        return versioned[-1]
    plain = manuscript_dir / _VERSIONED_MANUSCRIPT_FALLBACK
    return plain if plain.is_file() else None

_CSS = """
@page { size: A4; margin: 22mm 20mm; @bottom-center { content: counter(page);
  font-family: 'DejaVu Serif', Georgia, serif; font-size: 9pt; color: #555; } }
body { font-family: 'DejaVu Serif', Georgia, serif; font-size: 10.5pt;
  line-height: 1.45; color: #111; }
h1 { font-size: 19pt; margin: 0 0 4pt; line-height: 1.2; }
h2 { font-size: 13pt; margin: 16pt 0 4pt; border-bottom: 0.5pt solid #bbb;
  padding-bottom: 2pt; }
h3 { font-size: 11pt; margin: 12pt 0 3pt; }
code, pre { font-family: 'DejaVu Sans Mono', monospace; font-size: 8.6pt; }
pre { background: #f6f6f6; border-left: 2pt solid #ccc; padding: 6pt 8pt;
  white-space: pre-wrap; word-wrap: break-word; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0; font-size: 9pt; }
th, td { border: 0.5pt solid #999; padding: 3pt 5pt; text-align: left;
  vertical-align: top; }
th { background: #eee; }
blockquote { border-left: 2pt solid #999; margin-left: 0; padding-left: 10pt;
  color: #333; }
.provenance { margin-top: 18pt; padding-top: 6pt; border-top: 0.5pt solid #bbb;
  font-size: 8pt; color: #555; font-family: 'DejaVu Sans Mono', monospace; }
"""


def _git(*args: str) -> str:
    try:
        out = subprocess.run(
            ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, timeout=30
        )
        return out.stdout.strip() or "UNKNOWN"
    except (OSError, subprocess.SubprocessError):
        return "UNKNOWN"


#: Where a paper's LaTeX entry point lives, in the two layouts the repo uses.
_TEX_ENTRY_POINTS = ("manuscript/main.tex", "paper/main.tex")

#: Build residue latexmk leaves beside the entry point. None of it is tracked by
#: any paper in this repo, and none of it is in `.gitignore` either, so a build
#: used to leave six untracked files behind and the next `git status` read as a
#: dirty tree. Removing two of them and calling that cleanup is the same defect
#: one level down: a partial sweep reported as a sweep.
_LATEXMK_RESIDUE = (".aux", ".bbl", ".blg", ".fdb_latexmk", ".fls", ".log", ".out", ".toc")

#: The one latexmk failure this script retries. The LaTeX `markdown`
#: package shells out; without -shell-escape it stops with exactly this.
_NEEDS_SHELL_ESCAPE = "I can not access the shell"


def find_tex_entry(paper_dir: Path) -> Path | None:
    """The paper's LaTeX entry point, or None if it has no tree."""

    for relative in _TEX_ENTRY_POINTS:
        candidate = paper_dir / relative
        if candidate.is_file():
            return candidate
    return None


def build_with_latexmk(entry: Path) -> Path | None:
    """Build via latexmk. Returns None if the toolchain is absent.

    A build failure is not swallowed: latexmk exiting non-zero raises, because a
    paper whose LaTeX does not compile must not quietly fall back to a Markdown
    rendering that hides the breakage.
    """

    def _run(shell_escape: bool) -> subprocess.CompletedProcess[str]:
        command = ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error"]
        if shell_escape:
            command.append("-shell-escape")
        command.append(entry.name)
        return subprocess.run(
            command, cwd=entry.parent, capture_output=True, text=True, timeout=900
        )

    try:
        result = _run(shell_escape=False)
    except FileNotFoundError:
        return None

    # P11-P14 use the LaTeX `markdown` package, which shells out and fails with
    # "I can not access the shell" unless -shell-escape is given. That flag lets
    # a document run arbitrary commands, so it is not on by default and is not
    # applied to every paper: it is a retry, triggered only by that specific
    # error, for documents already in this repository. A build that fails for any
    # other reason is not retried and still raises.
    # latexmk writes the package error to main.log rather than stdout, so the
    # trigger reads both. Looking only at stdout meant the retry never fired.
    log = entry.with_suffix(".log")
    log_text = log.read_text(errors="replace") if log.is_file() else ""
    if result.returncode != 0 and _NEEDS_SHELL_ESCAPE in (result.stdout + log_text):
        # The failed first pass leaves a .fdb_latexmk recording the error, and
        # latexmk then answers the retry with "All targets are up-to-date" and
        # re-reports the previous failure. Its state has to go before the retry
        # means anything.
        for residue in _LATEXMK_RESIDUE:
            entry.with_suffix(residue).unlink(missing_ok=True)
        result = _run(shell_escape=True)

    if result.returncode != 0:
        tail = "\n".join(result.stdout.splitlines()[-25:])
        raise RuntimeError(f"latexmk failed for {entry}:\n{tail}")
    produced = entry.with_suffix(".pdf")
    if not produced.is_file():
        raise RuntimeError(f"latexmk reported success but {produced} is missing")
    for residue in _LATEXMK_RESIDUE:
        entry.with_suffix(residue).unlink(missing_ok=True)
    return produced


def resolve_source(target: str) -> Path:
    """Accept a file, a paper directory, or a `P<n>` identifier."""

    candidate = Path(target)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    if candidate.is_file():
        return candidate
    if candidate.is_dir():
        for name in _MANUSCRIPT_NAMES:
            if (candidate / name).is_file():
                return candidate / name
        raise FileNotFoundError(
            f"{candidate} holds none of {_MANUSCRIPT_NAMES}; pass the file explicitly"
        )
    raise FileNotFoundError(target)


def resolve_paper_dir(paper_id: str) -> Path:
    """Map `P2` to its directory via the programme registry, not by guessing."""

    sys.path.insert(0, str(REPO_ROOT / "src"))
    from orion.programme.superiority_terminals import (  # noqa: PLC0415
        FUTURE_PAPER_DIRECTORIES,
        PAPER_DIRECTORIES,
    )

    # PAPER_DIRECTORIES is a tuple of PaperDirectories records, not a mapping;
    # FUTURE_PAPER_DIRECTORIES is a plain dict. Normalise both rather than
    # assuming a shape -- guessing is what put a paper's own id in the wrong
    # place elsewhere in this programme.
    directories = {item.paper_id: item.active for item in PAPER_DIRECTORIES}
    directories.update(FUTURE_PAPER_DIRECTORIES)
    key = paper_id.upper()
    if key not in directories:
        raise KeyError(f"{paper_id} is not a registered paper; known: {sorted(directories)}")
    return REPO_ROOT / directories[key]


def resolve_paper(paper_id: str) -> Path:
    """The paper's Markdown manuscript, for the fallback path."""

    sys.path.insert(0, str(REPO_ROOT / "src"))
    from orion.programme.superiority_terminals import (  # noqa: PLC0415
        FUTURE_PAPER_DIRECTORIES,
        PAPER_DIRECTORIES,
    )

    directories = {item.paper_id: item.active for item in PAPER_DIRECTORIES}
    directories.update(FUTURE_PAPER_DIRECTORIES)
    key = paper_id.upper()
    if key not in directories:
        raise KeyError(f"{paper_id} is not a registered paper; known: {sorted(directories)}")
    return resolve_source(directories[key])


def render(source: Path, output: Path) -> Path:
    import markdown as markdown_lib
    from weasyprint import CSS, HTML

    text = source.read_text(encoding="utf-8")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    body = markdown_lib.markdown(
        text, extensions=["tables", "fenced_code", "toc", "sane_lists"]
    )
    provenance = (
        f'<div class="provenance">source: {source.relative_to(REPO_ROOT)}<br>'
        f"sha256: {digest}<br>"
        f"commit: {_git('rev-parse', 'HEAD')}<br>"
        f"rendered: {datetime.now(timezone.utc).isoformat(timespec='seconds')} "
        f"by scripts/build_paper_pdf.py (WeasyPrint; not the LaTeX tree)</div>"
    )
    html = f"<html><head><meta charset='utf-8'></head><body>{body}{provenance}</body></html>"

    output.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html, base_url=str(source.parent)).write_pdf(
        str(output), stylesheets=[CSS(string=_CSS)]
    )
    return output


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", help="manuscript file or paper directory")
    parser.add_argument("--paper", help="registered paper id, e.g. P2")
    parser.add_argument("--out", type=Path, help="output pdf path")
    arguments = parser.parse_args(argv)

    if not arguments.source and not arguments.paper:
        parser.error("give a source path or --paper")

    if arguments.paper:
        paper_dir = resolve_paper_dir(arguments.paper)
    else:
        given = Path(arguments.source)
        paper_dir = (REPO_ROOT / given) if not given.is_absolute() else given
        if paper_dir.is_file():
            paper_dir = paper_dir.parent

    entry = find_tex_entry(paper_dir)
    if entry is not None:
        built = build_with_latexmk(entry)
        if built is not None:
            size = built.stat().st_size
            print(f"wrote {built.relative_to(REPO_ROOT)} ({size:,} bytes) via latexmk from {entry.name}")
            return 0
        print(f"latexmk unavailable; falling back to Markdown for {paper_dir.name}", file=sys.stderr)

    source = find_versioned_manuscript(paper_dir)
    if source is None:
        source = (
            resolve_paper(arguments.paper) if arguments.paper else resolve_source(arguments.source)
        )
        if source.name == "README.md":
            print(
                f"note: {paper_dir.name} has no LaTeX tree and no manuscript/FINAL*.md; "
                "rendering its README, which is probably not the manuscript",
                file=sys.stderr,
            )
    output = arguments.out or source.parent / f"{source.stem}.pdf"
    written = render(source, output)
    size = written.stat().st_size
    print(f"wrote {written.relative_to(REPO_ROOT)} ({size:,} bytes) via WeasyPrint from {source.name}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
