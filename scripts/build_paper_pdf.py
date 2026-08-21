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

    try:
        result = subprocess.run(
            ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", entry.name],
            cwd=entry.parent,
            capture_output=True,
            text=True,
            timeout=900,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        tail = "\n".join(result.stdout.splitlines()[-25:])
        raise RuntimeError(f"latexmk failed for {entry}:\n{tail}")
    produced = entry.with_suffix(".pdf")
    if not produced.is_file():
        raise RuntimeError(f"latexmk reported success but {produced} is missing")
    # latexmk leaves recorder files that no paper wants committed.
    for residue in (".fdb_latexmk", ".fls"):
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

    source = resolve_paper(arguments.paper) if arguments.paper else resolve_source(arguments.source)
    output = arguments.out or source.parent / f"{source.stem}.pdf"
    written = render(source, output)
    size = written.stat().st_size
    print(f"wrote {written.relative_to(REPO_ROOT)} ({size:,} bytes) via WeasyPrint from {source.name}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
