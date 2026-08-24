"""Does every surviving paper declare one unique primary endpoint?

Issue #1086's definition of done requires it. This derives each paper's
endpoint from its own active-authority record rather than asserting one:
inventing an endpoint for a paper that never declared it would manufacture the
very thing the box asks to verify.

Two results are possible and they are different. If a paper declares an
endpoint, uniqueness across papers can be checked. If it declares none, the
answer is not "unique by default" -- it is that the question cannot be asked,
and this reports that separately rather than counting silence as compliance.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

EXIT_PASS = 0
EXIT_NOT_UNIQUE = 2
EXIT_CANNOT_CHECK = 3
EXIT_UNDECLARED = 4

#: The fifteen papers the definition of done speaks about.
CANONICAL = tuple(f"paper-{i:02d}" for i in range(1, 16))


@dataclass
class Endpoint:
    paper: str
    terminal: str | None
    source: str | None


@dataclass
class Report:
    endpoints: list[Endpoint] = field(default_factory=list)

    @property
    def declared(self) -> list[Endpoint]:
        return [e for e in self.endpoints if e.terminal]

    @property
    def undeclared(self) -> list[Endpoint]:
        return [e for e in self.endpoints if not e.terminal]

    @property
    def collisions(self) -> dict[str, int]:
        counts = Counter(e.terminal for e in self.declared)
        return {t: n for t, n in counts.items() if n > 1 and t}


def _version(path: Path) -> tuple[int, str]:
    """Sort authority records by version number, not by filename.

    Alphabetical order puts V10 before V9, so the highest-numbered record stops
    being the one read as soon as a paper reaches ten versions. No paper has yet
    -- P12's V5 is the furthest along -- which is exactly why this would have
    surfaced as a wrong terminal rather than as an error.
    """
    m = re.search(r"_V(\d+)\.json$", path.name)
    return (int(m.group(1)) if m else -1, path.name)


def _terminal_of(rec: dict) -> str | None:
    """Read the endpoint under any of the shapes papers actually use.

    Six papers carry an authority record and they do not share a schema: P10 and
    P15 put the endpoint in ``active_terminal``, while P14 nests it as
    ``active_claim.scientific_terminal``. Keying on ``active_terminal`` alone
    reported P14 as declaring none, printed identically to the nine papers that
    genuinely have no record -- a parsing miss and a real absence counted as one.
    """
    terminal = rec.get("active_terminal")
    if isinstance(terminal, str) and terminal:
        return terminal
    claim = rec.get("active_claim")
    if isinstance(claim, dict):
        nested = claim.get("scientific_terminal") or claim.get("terminal")
        if isinstance(nested, str) and nested:
            return nested
    return None


def audit_repository(root: Path | None = None) -> Report:
    root = root or Path(__file__).resolve().parents[3]
    papers = root / "papers"
    if not papers.is_dir():
        raise FileNotFoundError(papers)
    report = Report()
    for prefix in CANONICAL:
        matches = sorted(d for d in papers.iterdir() if d.is_dir() and d.name.startswith(prefix))
        if not matches:
            report.endpoints.append(Endpoint(prefix, None, None))
            continue
        # a paper number may map to more than one directory; take the first that
        # declares an authority, and record none if no directory does
        chosen: Endpoint | None = None
        for d in matches:
            records = sorted(d.glob("*ACTIVE_CLAIM_AUTHORITY*.json"), key=_version)
            if not records:
                continue
            try:
                rec = json.loads(records[-1].read_text())
            except (json.JSONDecodeError, OSError):
                continue
            terminal = _terminal_of(rec)
            if terminal:
                chosen = Endpoint(d.name, terminal, records[-1].name)
                break
        report.endpoints.append(chosen or Endpoint(matches[0].name, None, None))
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None)
    args = ap.parse_args(argv)
    try:
        report = audit_repository(args.root)
    except FileNotFoundError as exc:
        print(f"PRIMARY_ENDPOINT_CANNOT_CHECK: {exc}")
        return EXIT_CANNOT_CHECK
    print(f"canonical papers:      {len(report.endpoints)}")
    print(f"declare an endpoint:   {len(report.declared)}")
    print(f"declare none:          {len(report.undeclared)}")
    for e in report.endpoints:
        mark = "OK  " if e.terminal else "NONE"
        print(f"  {mark} {e.paper:44s} {e.terminal or '(no active-authority record)'}")
    if report.collisions:
        print(f"PRIMARY_ENDPOINT_NOT_UNIQUE: {report.collisions}")
        return EXIT_NOT_UNIQUE
    if report.undeclared:
        print(
            f"PRIMARY_ENDPOINT_UNDECLARED: {len(report.undeclared)} papers declare none. "
            "Silence is not uniqueness; the question cannot be asked of them."
        )
        return EXIT_UNDECLARED
    print("PRIMARY_ENDPOINT_UNIQUE_PASS")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
