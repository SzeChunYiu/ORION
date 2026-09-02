"""A CANONICAL_* decision and the newest freeze addendum must name the same versions.

On 2026-09-02 three Tier-B papers drifted in the same way: a successor
manuscript/ledger pair was adopted by a new ``CANONICAL_*`` decision file while
the paper's top-level ``PUBLICATION_FREEZE_ADDENDUM_V*_*.md`` still froze the
predecessor pair by name. Nothing compared the two surfaces, so the drift sat
silent until issue SzeChunYiu/ORION-paper#78 itemised it.

This checker reads, per paper directory:

- every top-level ``CANONICAL_*.md`` (and a ``submission/CANONICAL_*.md`` if
  the paper keeps its decision nested there) — the authority side;
- the highest-``V`` numbered top-level ``PUBLICATION_FREEZE_ADDENDUM_V*.md``
  (a successor addendum supersedes lower versions that remain on disk) —
  the freeze side.

From each side it extracts backticked filenames whose stem carries a
manuscript-family core token (``MANUSCRIPT``, ``FINAL``, ``CLAIM_LEDGER`` —
contiguous, so ``CLAIM_RETRACTION_LEDGER`` does not match) and reduces them to
(family, version). A mention counts as **current** unless its own sentence
reads as supersession/historical context (``superseded``, ``historical``,
``immutable``, ``drafts``, ``must not be used``, ...) — sentence, not line:
a freeze addendum routinely packs "the packet is `MANUSCRIPT_V2.md`" and
"historical records remain immutable" into one line, and only the second
sentence is about history. Per side and family the
current version is the maximum named; theory-A/theory-B prefixed ledger names
stay their own families rather than folding into ``CLAIM_LEDGER``.

The check that matters: a family the **canonical side names as current at one
version while the freeze side names the same family current at a different
version**. That is exactly the 2026-09-02 drift (canonical ``MANUSCRIPT_V3``
vs frozen ``MANUSCRIPT_V2``). Families named by only one side are reported as
informational notes, not failures — a freeze may add a filing surface
(``MANUSCRIPT_SHORT_V1``) the canonical decision predates, and a canonical
decision may govern a LaTeX tree with no versioned ``.md`` name at all.

Exit codes
----------
0   every shared family agrees; papers without either surface are skipped
2   at least one shared family is named at different current versions
3   CANNOT_CHECK -- the papers tree could not be read
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPERS = ROOT / "papers"
EXCLUDED_DIRS = {"candidates"}

CORE_TOKENS = ("MANUSCRIPT", "FINAL", "CLAIM_LEDGER")
SUPERSESSION_MARKERS = re.compile(
    r"superseded|supersedes|historical|immutable|earlier ledger|remain on disk"
    r"|must not be (used|submitted)|prior (?:version|frozen)|drafts?\b|pre-retraction",
    re.IGNORECASE,
)
BACKTICKED = re.compile(r"`([^`\n]+)`")
# Dot followed by whitespace: sentence-ish boundary. A dot inside a filename
# (`MANUSCRIPT_V2.md`) is never followed by whitespace, so names stay intact.
SENTENCE_SPLIT = re.compile(r"(?<=\.)\s+")
VERSIONED_SUFFIX = re.compile(r"^(?P<family>.+?)_V(?P<major>\d+)(?:_(?P<minor>\d+))?$")
REVISED_SUFFIX = re.compile(r"^(?P<family>.+?)_R(?P<rev>\d+)$")

# Series ordering for max-selection: an unversioned name is the base (0),
# an _R name is a revision (1), a _V name is a full version (2).
SERIES_BASE, SERIES_R, SERIES_V = 0, 1, 2


class CannotCheck(Exception):
    """The check could not run. Distinct from a clean result."""


def has_core_token(stem: str) -> bool:
    return any(re.search(rf"(?:^|[_A-Z]){token}(?:$|[_A-Z])", stem.upper()) for token in CORE_TOKENS)


def parse_name(raw: str) -> tuple[str, str, tuple[int, int, int]] | None:
    """Map a backticked filename to (family, display, version key) or None."""
    name = Path(raw).name
    if not name.endswith(".md"):
        return None
    stem = name[:-3]
    if not has_core_token(stem):
        return None
    if m := VERSIONED_SUFFIX.match(stem):
        family, major = m.group("family"), int(m.group("major"))
        minor = int(m.group("minor")) if m.group("minor") else 0
        return family, name, (SERIES_V, major, minor)
    if m := REVISED_SUFFIX.match(stem):
        return m.group("family"), name, (SERIES_R, int(m.group("rev")), 0)
    return stem, name, (SERIES_BASE, 0, 0)


def extract_current_families(text: str) -> dict[str, tuple[str, tuple[int, int, int]]]:
    """Family -> (newest current filename, version key) for current mentions."""
    best: dict[str, tuple[str, tuple[int, int, int]]] = {}
    for line in text.splitlines():
        for segment in SENTENCE_SPLIT.split(line):
            if SUPERSESSION_MARKERS.search(segment):
                continue
            for raw in BACKTICKED.findall(segment):
                parsed = parse_name(raw)
                if parsed is None:
                    continue
                family, name, key = parsed
                if family not in best or key > best[family][1]:
                    best[family] = (name, key)
    return best


def paper_surfaces(paper: Path) -> tuple[list[Path], Path | None]:
    canonicals = sorted(paper.glob("CANONICAL_*.md"))
    submission = paper / "submission"
    if submission.is_dir():
        canonicals += sorted((s for s in submission.glob("CANONICAL_*.md") if s.parent == submission), key=lambda p: p.name)
    freezes = sorted(
        (f for f in paper.glob("PUBLICATION_FREEZE_ADDENDUM_V*.md") if f.parent == paper),
        key=lambda f: (int(re.search(r"_V(\d+)", f.name).group(1)) if re.search(r"_V(\d+)", f.name) else 0),
    )
    latest_freeze = freezes[-1] if freezes else None
    return canonicals, latest_freeze


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CannotCheck(f"unreadable authority surface {path}: {exc}") from exc


def check(papers_root: Path) -> tuple[list[str], list[str]]:
    findings: list[str] = []
    notes: list[str] = []
    if not papers_root.is_dir():
        raise CannotCheck(f"papers directory absent: {papers_root}")
    paired = 0
    for paper in sorted(p for p in papers_root.iterdir() if p.is_dir() and p.name not in EXCLUDED_DIRS and not p.name.startswith("publication_closure")):
        canonicals, latest_freeze = paper_surfaces(paper)
        if not canonicals or latest_freeze is None:
            continue
        paired += 1
        canonical_side: dict[str, tuple[str, tuple[int, int, int]]] = {}
        for path in canonicals:
            for family, entry in extract_current_families(read(path)).items():
                if family not in canonical_side or entry[1] > canonical_side[family][1]:
                    canonical_side[family] = entry
        freeze_side = extract_current_families(read(latest_freeze))
        for family in sorted(set(canonical_side) & set(freeze_side)):
            c_name = canonical_side[family][0]
            f_name = freeze_side[family][0]
            if canonical_side[family][1] != freeze_side[family][1]:
                findings.append(
                    f"{paper.name}: family {family} is current at different versions — "
                    f"canonical names {c_name}, freeze addendum {latest_freeze.name} names {f_name}"
                )
        for family in sorted(set(canonical_side) ^ set(freeze_side)):
            side = "canonical" if family in canonical_side else "freeze"
            name = (canonical_side.get(family) or freeze_side.get(family))[0]
            notes.append(f"{paper.name}: family {family} ({name}) named only by the {side} side")
    if paired == 0:
        raise CannotCheck(f"no paper under {papers_root} pairs a canonical decision with a freeze addendum; nothing was checked")
    return findings, notes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--papers", type=Path, default=PAPERS, help="papers root to scan (tests may override)")
    args = parser.parse_args(argv)
    try:
        findings, notes = check(args.papers.resolve())
    except CannotCheck as exc:
        print(f"CANNOT_CHECK: {exc}")
        return 3
    for note in notes:
        print(f"note: {note}")
    for finding in findings:
        print(f"DRIFT: {finding}")
    if findings:
        print(f"{len(findings)} canonical/freeze version drift(s) found")
        return 2
    print("every shared manuscript family agrees between canonical decisions and newest freeze addenda")
    return 0


if __name__ == "__main__":
    sys.exit(main())
