#!/usr/bin/env python3
"""Is the A6 donor subtraction complete over both formal cores?

Issue #49 asks that *every* theorem be restated and marked `DONOR`,
`SPECIALIZATION` or `SURVIVING_NEW_CONSEQUENCE`. "Every" is the load-bearing
word, and a prose claim to have covered everything is not checkable. This is.

It enumerates the result headings in ORION-16's and ORION-18's V2.1 cores and
requires each to carry a verdict in the two subtraction documents. If a core
gains a result later, this fails until the subtraction catches up -- which is the
point, since an uncovered result is exactly where an unearned novelty claim hides.

Exit 0 complete, 1 incomplete, 3 could not check (a core or document is missing --
distinct from "checked and found nothing missing").
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

CORES = {
    "ORION-16": ROOT
    / "papers/orion-16-formal-epistemic-structures-and-mechanics/manuscript/FORMAL_CORE_V2_1.md",
    "ORION-18": ROOT
    / "papers/orion-18-epistemic-authority-autonomous-science/manuscript/FORMAL_CORE_V2_1.md",
}
SUBTRACTIONS = (
    HERE / "A6_DONOR_SUBTRACTION_V1.md",
    HERE / "A6_DONOR_SUBTRACTION_COMPLETION_V1.md",
)

VERDICTS = ("DONOR", "SPECIALIZATION", "SURVIVING_NEW_CONSEQUENCE")

#: A result is a `###` heading naming one. Definitions are not results: they fix
#: vocabulary and carry no claim to subtract.
RESULT_HEADING = re.compile(
    r"^###\s+(Theorem|Proposition|Propositions|Lemma|Corollary|Countermodel)\s+([\d.]+(?:\s*[-–]+\s*\d+)?)",
    re.MULTILINE,
)


def results_in(path: Path) -> list[str]:
    """Result labels, normalised to `Kind N`, singularised and range-expanded."""

    found: list[str] = []
    for kind, number in RESULT_HEADING.findall(path.read_text(encoding="utf-8")):
        singular = "Proposition" if kind == "Propositions" else kind
        parts = re.split(r"\s*[-–]+\s*", number.strip())
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            # "Propositions 15-16" is two results stated together.
            for n in range(int(parts[0]), int(parts[1]) + 1):
                found.append(f"{singular} {n}")
        else:
            found.append(f"{singular} {number.strip()}")
    return found


def verdicted(label: str, blocks: list[str]) -> bool:
    """A result is covered when some block names it AND carries a verdict.

    Matching on the block rather than the whole document matters: a document-wide
    search would count a result mentioned in another result's discussion.
    """

    kind, number = label.split(" ", 1)
    plural = f"{kind}s"
    for block in blocks:
        head = block.split("\n", 1)[0]
        names = re.search(rf"\b(?:{kind}|{plural})\s+([\d.,\s–-]+)", head)
        if not names:
            continue
        span = names.group(1)
        hit = number in re.split(r"[,\s–-]+", span.strip())
        if not hit and re.fullmatch(r"\d+", number):
            rng = re.match(r"(\d+)\s*[-–]+\s*(\d+)", span.strip())
            hit = bool(rng) and int(rng.group(1)) <= int(number) <= int(rng.group(2))
        if hit and any(f"Verdict: `{v}`" in block for v in VERDICTS):
            return True
    return False


def main() -> int:
    missing_files = [str(p) for p in (*CORES.values(), *SUBTRACTIONS) if not p.is_file()]
    if missing_files:
        print(
            json.dumps(
                {
                    "status": "CANNOT_CHECK",
                    "reason": "a core or subtraction document is absent, so coverage "
                    "cannot be decided",
                    "missing": missing_files,
                },
                indent=2,
            )
        )
        return 3

    blocks: list[str] = []
    for path in SUBTRACTIONS:
        blocks += ["### " + b for b in path.read_text(encoding="utf-8").split("\n### ")[1:]]

    report: dict[str, list[str]] = {}
    uncovered: list[str] = []
    for paper, core in CORES.items():
        labels = results_in(core)
        report[paper] = labels
        uncovered += [f"{paper} {x}" for x in labels if not verdicted(x, blocks)]

    payload = {
        "schema": "A6.SubtractionCoverage.v1",
        "results_by_core": report,
        "results_total": sum(len(v) for v in report.values()),
        "verdict_blocks_scanned": len(blocks),
        "uncovered": uncovered,
        "scientific_authority_delta": "NONE",
        "status": "COMPLETE" if not uncovered else "INCOMPLETE",
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not uncovered else 1


if __name__ == "__main__":
    raise SystemExit(main())
