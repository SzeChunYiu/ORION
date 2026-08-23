#!/usr/bin/env python3
"""Render ORION manuscript-section markdown into LaTeX markdown-package
renderer-token form (the ``.md.tex`` fragment files under
``manuscript/_markdown_main/``).

Covers exactly the construct set the manuscript sections use: ATX H1/H2
headings, paragraphs (soft line breaks join with a single space; a trailing
backslash or 2+ trailing spaces mark a hard line break, which renders as the
hard-line-break macro), pipe tables, tight ordered lists, code spans, strong
emphasis / emphasis, and the package's special-character macros. Anything
else raises instead of silently producing wrong bytes.

Note on history: a handful of 2026-08 fragments contain bare ``\\n{}``
separators where clean grammar demands a space or the full interblock macro.
Those mark stacked-write seams in the damaged corpus (the same corruption as
the manifest seam), not renderer grammar; ``--check`` reports them as
explained divergence instead of silently accepting them.

Usage:
    render_md_tex.py SRC.md                 # render to stdout
    render_md_tex.py SRC.md --check X.md.tex
    render_md_tex.py SRC.md --write X.md.tex
"""

from __future__ import annotations

import argparse
import re
import sys

ESCAPES = {
    "_": r"\markdownRendererUnderscore{}",
    "%": r"\markdownRendererPercentSign{}",
    "&": r"\markdownRendererAmpersand{}",
    "^": r"\markdownRendererCircumflex{}",
    "{": r"\markdownRendererLeftBrace{}",
    "}": r"\markdownRendererRightBrace{}",
    "|": r"\markdownRendererPipe{}",
}

INTERBLOCK = "\\markdownRendererInterblockSeparator\n{}"
SECTION_CLOSE = "\n\\markdownRendererSectionEnd "
OL_ITEM_END = "\\markdownRendererOlItemEnd \n"
HARD_BREAK = "\\markdownRendererHardLineBreak\n{}"


class Unsupported(Exception):
    pass


def render_inline(text: str) -> str:
    out = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == "`":
            j = text.find("`", i + 1)
            if j < 0:
                raise Unsupported("unterminated code span")
            out.append(r"\markdownRendererCodeSpan{" + escape(text[i + 1 : j]) + "}")
            i = j + 1
        elif c == "*":
            if i + 1 < n and text[i + 1] == "*":
                j = text.find("**", i + 2)
                if j < 0:
                    raise Unsupported("unterminated strong emphasis")
                out.append(
                    r"\markdownRendererStrongEmphasis{"
                    + render_inline(text[i + 2 : j])
                    + "}"
                )
                i = j + 2
            else:
                j = text.find("*", i + 1)
                if j < 0:
                    raise Unsupported("unterminated emphasis")
                out.append(
                    r"\markdownRendererEmphasis{" + render_inline(text[i + 1 : j]) + "}"
                )
                i = j + 1
        elif c in ESCAPES:
            out.append(ESCAPES[c])
            i += 1
        elif c == "\\":
            raise Unsupported(
                "stray backslash in text (only a trailing hard-break marker is defined)"
            )
        else:
            out.append(c)
            i += 1
    return "".join(out)


def escape(text: str) -> str:
    return "".join(ESCAPES.get(c, c) for c in text)


def strip_break_marker(line: str) -> tuple[str, bool]:
    """Split a source line into (text, is_hard_break).

    A hard break is a trailing backslash or two-or-more trailing spaces
    (CommonMark). The marker is consumed, not rendered."""
    if line.endswith("\\"):
        return line[:-1].rstrip(), True
    stripped = line.rstrip(" ")
    if len(line) - len(stripped) >= 2:
        return stripped.rstrip(), True
    return line.rstrip(), False


SOFT_JOIN = "\x00"  # placeholder expanded after inline rendering
HARD_JOIN = "\x01"


def render_para(para_lines: list[str]) -> str:
    # Emphasis spans may open on one source line and close on another, so the
    # join tokens must survive inline rendering as inert placeholders.
    parts: list[str] = []
    pending_break = False
    for idx, raw in enumerate(para_lines):
        text, hard = strip_break_marker(raw)
        if idx:
            parts.append(HARD_JOIN if pending_break else SOFT_JOIN)
        parts.append(text)
        pending_break = hard
    rendered = render_inline("".join(parts))
    return rendered.replace(HARD_JOIN, HARD_BREAK).replace(SOFT_JOIN, " ")


def parse_blocks(lines: list[str]) -> list[tuple[str, object]]:
    blocks: list[tuple[str, object]] = []
    para: list[str] = []

    def flush() -> None:
        if para:
            blocks.append(("para", list(para)))
            para.clear()

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        s = line.strip()
        if not s:
            flush()
            i += 1
        elif s.startswith("# ") or s.startswith("## "):
            flush()
            level = 2 if s.startswith("## ") else 1
            title = s[level + 1 :].strip().rstrip("#").strip()
            blocks.append(("heading", (level, title)))
            i += 1
        elif s.startswith("|"):
            flush()
            rows: list[list[str]] = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(split_table_row(lines[i]))
                i += 1
            blocks.append(("table", rows))
        elif re.match(r"^\d+\. ", s):
            flush()
            items: list[str] = []
            while i < n:
                cur = lines[i]
                cs = cur.strip()
                if re.match(r"^\d+\. ", cs):
                    items.append(re.sub(r"^\d+\. ", "", cs))
                    i += 1
                elif cs and not cs.startswith(("#", "|", ">")) and items:
                    items[-1] += " " + cs  # wrapped continuation line
                    i += 1
                else:
                    break
            blocks.append(("ol", items))
        elif s.startswith(">") or s.startswith("- ") or s.startswith("* "):
            raise Unsupported(f"construct not used by sections: {s[:20]!r}")
        else:
            # Keep trailing whitespace: a 2-space tail is a hard-break marker.
            para.append(line.lstrip())
            i += 1
    flush()
    return blocks


def split_table_row(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def align_code(delimiter_cell: str) -> str:
    d = delimiter_cell.strip()
    body = d.replace(":", "").replace("-", "")
    if body:
        raise Unsupported(f"odd table delimiter {d!r}")
    left = d.startswith(":")
    right = d.endswith(":")
    if left and right:
        return "c"
    if right:
        return "r"
    if left:
        return "l"
    return "d"


def render(md_text: str) -> str:
    lines = md_text.split("\n")
    blocks = parse_blocks(lines)

    out = ["\\markdownRendererDocumentBegin\n"]
    depth = 0  # 0 none, 1 inside H1 section, 2 inside H2 subsection

    def close_to(target: int) -> None:
        nonlocal depth
        while depth > target:
            out.append(SECTION_CLOSE)
            depth -= 1

    first = True
    for kind, payload in blocks:
        if not first:
            out.append(INTERBLOCK)
        first = False
        if kind == "heading":
            level, title = payload
            close_to(level - 1)
            out.append("\\markdownRendererSectionBegin\n")
            macro = "HeadingOne" if level == 1 else "HeadingTwo"
            out.append(f"\\markdownRenderer{macro}{{{render_inline(title)}}}")
            depth = level
        elif kind == "para":
            out.append(render_para(payload))
        elif kind == "ol":
            out.append("\\markdownRendererOlBeginTight\n")
            for k, item in enumerate(payload, 1):
                out.append(f"\\markdownRendererOlItemWithNumber{{{k}}}")
                out.append(render_inline(item))
                out.append(OL_ITEM_END)
            out.append("\\markdownRendererOlEndTight ")
        elif kind == "table":
            rows = payload
            if len(rows) < 2:
                raise Unsupported("table without delimiter row")
            header, delim, body = rows[0], rows[1], rows[2:]
            if len(header) != len(delim):
                raise Unsupported("table header/delimiter column mismatch")
            align = "".join(align_code(c) for c in delim)
            out.append(
                "\\markdownRendererTable{}{%d}{%d}{%s}"
                % (len(rows), len(header), align)
            )
            for row in [header] + body:
                if len(row) != len(header):
                    raise Unsupported(f"table row width mismatch: {row}")
                out.append("{" + "".join(f"{{{render_inline(c)}}}" for c in row) + "}")
        else:
            raise Unsupported(kind)
    close_to(0)
    out.append("\\markdownRendererDocumentEnd")
    return "".join(out)


def normalize_seams(text: str) -> tuple[str, int]:
    """Rewrite historical stacked-write seam tokens.

    A bare ``\\n{}`` that does not close a renderer macro name is a seam
    artifact from the 2026-08 stacked writes; clean grammar wants a space
    there. Returns (normalized_text, seam_count)."""
    out = []
    n = 0
    i = 0
    tail = ""
    while i < len(text):
        if text.startswith("\n{}", i) and not tail.endswith(
            ("InterblockSeparator", "HardLineBreak")
        ):
            out.append(" ")
            tail += " "
            n += 1
            i += 3
            continue
        c = text[i]
        out.append(c)
        tail = (tail + c)[-22:]
        i += 1
    return "".join(out), n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", help="markdown source file")
    ap.add_argument("--check", metavar="FRAGMENT", help="compare against fragment")
    ap.add_argument("--write", metavar="FRAGMENT", help="write fragment file")
    args = ap.parse_args()
    try:
        rendered = render(open(args.source, encoding="utf-8").read())
    except Unsupported as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if args.check:
        expected = open(args.check, encoding="utf-8").read()
        if rendered == expected:
            print(f"OK byte-exact: {args.check}")
            return 0
        norm, seams = normalize_seams(expected)
        if rendered == norm:
            print(
                f"OK modulo {seams} stacked-write seam token(s) "
                f"(explained divergence): {args.check}"
            )
            return 0
        for i, (a, b) in enumerate(zip(rendered, norm)):
            if a != b:
                print(
                    f"DIFF at byte {i}:\n  rendered: {rendered[max(0,i-50):i+50]!r}\n"
                    f"  expected: {norm[max(0,i-50):i+50]!r}"
                )
                break
        print(
            f"len rendered={len(rendered)} expected={len(expected)} "
            f"(seams={seams}) ({args.check})"
        )
        return 1
    if args.write:
        with open(args.write, "w", encoding="utf-8") as fh:
            fh.write(rendered)
        print(f"wrote {args.write} ({len(rendered)} bytes)")
        return 0
    sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
