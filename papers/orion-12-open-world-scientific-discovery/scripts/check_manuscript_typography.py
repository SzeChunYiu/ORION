#!/usr/bin/env python3
"""Fail when the manuscript runs into the margin, and when an allowance rots.

The manuscript audit already compiles the paper and gates on undefined citations
and references. It does not gate on overfull boxes, so text running past the
margin — which a reviewer sees immediately in the PDF — can land and stay. Every
overfull box in this paper traced to one cause: long ``snake_case`` identifiers
cannot break inside ``\\texttt``, which is why ``\\idt`` exists.

The allowance below behaves like the conformance module's known violations: it
suppresses a failure that is owned by someone else *and fails the run once that
file becomes clean*, so it cannot quietly become a lie about the current state.

Usage::

    check_manuscript_typography.py --log main.log [--max-points 0.0]
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

#: file basename -> why it is allowed to be overfull, and who owns clearing it.
#: A file listed here that is now clean FAILS the run: delete the entry instead.
ALLOWED_OVERFULL: dict[str, str] = {}

OVERFULL = re.compile(r"Overfull \\hbox \(([0-9.]+)pt too wide\)")
#: A real LaTeX log writes "(sections/results [7]" — the extension is elided when
#: the file was reached by \input{sections/results}, and there is no "./" prefix.
#: The first version of this regex required "\.tex", so on the real log every
#: warning came back <unattributed> even though the fixtures passed. Match any
#: parenthesised token that looks like a path: it contains a slash, or it ends in
#: .tex. Anything starting with a digit is log arithmetic, not a filename.
FILE_PUSH = re.compile(r"\((?![0-9])((?:\.?/)?[\w.-]+(?:/[\w.-]+)+|[\w.-]+\.tex)")


@dataclass(frozen=True)
class Overfull:
    source: str
    points: float


def parse(log_text: str) -> list[Overfull]:
    """Attribute each overfull box to a source file via TeX's file stack.

    TeX pushes ``(path`` when it opens a file and pops ``)`` when it closes one,
    but the log is full of parentheses that are not files — font substitutions,
    package banners, arithmetic. Two earlier versions of this got it wrong in
    ways only the real log revealed:

    * requiring ``.tex`` in the pushed path missed ``(sections/results [7]``,
      where the extension is elided, so every warning came back unattributed;
    * pushing only path-like parens while popping *every* close is unbalanced by
      construction, and the stack drained to empty long before the warnings.

    So every parenthesis is a stack operation; only path-like ones carry a name.
    An unattributable warning is reported as ``<unattributed>`` and counted as an
    offence rather than dropped, because a parser that silently loses a warning
    turns a gate into decoration.
    """

    stack: list[str | None] = []
    found: list[Overfull] = []
    for line in log_text.splitlines():
        hit = OVERFULL.search(line)
        if hit:
            named = [item for item in stack if item]
            found.append(Overfull(named[-1] if named else "<unattributed>", float(hit.group(1))))
            continue
        index = 0
        while index < len(line):
            char = line[index]
            if char == "(":
                match = FILE_PUSH.match(line, index)
                if match:
                    stack.append(Path(match.group(1)).name.removesuffix(".tex") + ".tex")
                    index = match.end()
                    continue
                stack.append(None)
            elif char == ")" and stack:
                stack.pop()
            index += 1
    return found


def evaluate(
    boxes: list[Overfull], *, max_points: float, allowed: dict[str, str]
) -> tuple[int, list[str]]:
    messages: list[str] = []
    offences = 0
    seen_files = {box.source for box in boxes}

    for box in boxes:
        if box.points <= max_points:
            continue
        if box.source in allowed:
            messages.append(
                f"ALLOWED  {box.source}: {box.points}pt overfull — {allowed[box.source]}"
            )
            continue
        offences += 1
        messages.append(
            f"OVERFULL {box.source}: {box.points}pt past the margin. Long identifiers "
            "belong in \\idt{...}, which breaks them at underscores."
        )

    for name, reason in sorted(allowed.items()):
        if name not in seen_files:
            offences += 1
            messages.append(
                f"STALE    {name} is allowed to be overfull but no longer is. Delete the "
                f"allowance ({reason})."
            )
    return offences, messages


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, required=True, help="LaTeX .log to inspect")
    parser.add_argument(
        "--max-points",
        type=float,
        default=0.0,
        help="tolerated overflow in points; 0 means any overfull box fails",
    )
    args = parser.parse_args(argv)

    if not args.log.is_file():
        print(f"TYPOGRAPHY cannot check: no log at {args.log}")
        return 1

    boxes = parse(args.log.read_text(encoding="utf-8", errors="replace"))
    offences, messages = evaluate(boxes, max_points=args.max_points, allowed=ALLOWED_OVERFULL)
    for message in messages:
        print(message)
    print(f"TYPOGRAPHY {len(boxes)} overfull boxes, {offences} unaccounted for")
    return 1 if offences else 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
