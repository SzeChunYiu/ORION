#!/usr/bin/env python3
"""Render a restricted Markdown subset into markdown.sty renderer tokens.

This script intentionally implements only the syntax used by the paper section
sources that need deterministic regeneration in this repository. Unsupported
constructs fail closed rather than being approximated.
"""

from __future__ import annotations

import argparse
import re
import sys


class Unsupported(ValueError):
    pass


INTERBLOCK = "\\markdownRendererInterblockSeparator\n{}"
SECTION_CLOSE = "\\markdownRendererSectionEnd "
OL_ITEM_END = "\\markdownRendererOlItemEnd "


def render_inline(text: str) -> str:
    """Render the small inline subset used by the source sections."""
    out: list[str] = []
    i = 0
    while i < len(text):
        if text.startswith("**", i):
            end = text.find("**", i + 2)
            if end < 0:
                raise Unsupported("unclosed strong emphasis")
            out.append("\\markdownRendererStrongEmphasis{" + render_inline(text[i + 2 : end]) + "}")
            i = end + 2
            continue
        if text[i] == "`":
            end = text.find("`", i + 1)
            if end < 0:
                raise Unsupported("unclosed code span")
            out.append("\\markdownRendererCodeSpan{" + text[i + 1 : end] + "}")
            i = end + 1
            continue
        if text[i] == "[":
            close = text.find("](", i + 1)
            if close >= 0:
                end = text.find(")", close + 2)
                if end < 0:
                    raise Unsupported("unclosed link")
                label = render_inline(text[i + 1 : close])
                target = text[close + 2 : end]
                out.append(f"\\markdownRendererLink{{{label}}}{{{target}}}{{{target}}}{{}}")
                i = end + 1
                continue
        # markdown.sty renderer tokens consume plain text literally here. Keep
        # source punctuation rather than inventing TeX escaping; this matches
        # the healthy cached fragments used as controls for this tool.
        out.append(text[i])
        i += 1
    return "".join(out)


def render_para(lines: list[str]) -> str:
    return " ".join(render_inline(line.strip()) for line in lines)


def parse_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        raise Unsupported("table rows must use leading and trailing pipes")
    return [cell.strip() for cell in stripped[1:-1].split("|")]


def parse_blocks(lines: list[str]):
    blocks = []
    i = 0
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        line = lines[i]
        if line.startswith("### "):
            raise Unsupported("heading level > 2")
        if line.startswith("## "):
            blocks.append(("heading", (2, line[3:].strip())))
            i += 1
            continue
        if line.startswith("# "):
            blocks.append(("heading", (1, line[2:].strip())))
            i += 1
            continue
        if re.match(r"^\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i]).strip())
                i += 1
            blocks.append(("ol", items))
            continue
        if line.lstrip().startswith("|"):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(parse_table_row(lines[i]))
                i += 1
            blocks.append(("table", rows))
            continue
        para = []
        while i < len(lines):
            current = lines[i]
            if not current.strip():
                break
            if current.startswith("# ") or current.startswith("## "):
                break
            if re.match(r"^\d+\.\s+", current) or current.lstrip().startswith("|"):
                break
            para.append(current)
            i += 1
        if not para:
            raise Unsupported(f"unsupported line: {lines[i]!r}")
        blocks.append(("para", para))
    return blocks


def align_code(delimiter: str) -> str:
    d = delimiter.strip()
    if not re.fullmatch(r":?-{3,}:?", d):
        raise Unsupported(f"invalid table delimiter: {delimiter!r}")
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
            emitted_rows = [header] + body
            out.append(
                "\\markdownRendererTable{}{%d}{%d}{%s}"
                % (len(emitted_rows), len(header), align)
            )
            for row in emitted_rows:
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
            print(f"OK modulo {seams} historical seam token(s): {args.check}")
            return 0
        print(f"MISMATCH: {args.check}", file=sys.stderr)
        return 1
    if args.write:
        with open(args.write, "w", encoding="utf-8") as fh:
            fh.write(rendered)
        print(f"wrote {args.write}")
        return 0
    sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
