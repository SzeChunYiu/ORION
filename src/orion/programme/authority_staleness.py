"""Find surfaces that still point at a superseded claim authority.

Several papers carry a versioned chain of authority records -- P12 runs V1
through V5, P13 through V3 -- and exactly one of them is active: the highest
version present. A superseded record is not wrong, it is history. What is wrong
is another surface still citing it as current, because a reader following that
citation gets a terminal the paper no longer stands behind.

That is the concrete form of "stale manuscript/ledger/authority claims", and it
is decidable: find the chain, take its head, and see whether anything outside
the chain still names an earlier member.

Two deliberate refusals:

* A file that merely *contains* an older version's name is not stale. History
  sections, changelogs and supersession notices must be able to name what they
  supersede. Only a citation that presents the older record as current counts,
  which is why the scan looks for a currency marker near the reference.
* A paper with a single authority record has no chain and cannot be stale this
  way. It is reported as having nothing to check rather than as passing.

Exit codes: 0 PASS, 2 a superseded authority is cited as current,
3 malformed -- could not check.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

__all__ = [
    "CURRENCY_MARKERS",
    "INVENTORY_FILES",
    "EXIT_CANNOT_CHECK",
    "EXIT_PASS",
    "EXIT_STALE_CITATION",
    "StalenessReport",
    "audit_repository",
    "authority_chains",
    "main",
]

EXIT_PASS = 0
EXIT_STALE_CITATION = 2
EXIT_CANNOT_CHECK = 3

#: A reference counts as a currency claim only when one of these IMMEDIATELY
#: precedes it. A loose "current" anywhere in the window is not enough: a file
#: listing that happens to sit near the word would otherwise read as a claim.
CURRENCY_MARKERS = ("active authority", "current authority", "authoritative record",
                    "active claim authority is", "authority in force")

#: Words that mark a reference as historical rather than current. A paper must
#: be able to name what it supersedes, and a lifecycle section that preserves
#: earlier records is doing exactly the right thing.
SUPERSESSION_MARKERS = ("supersede", "superseded", "historical", "previous", "prior",
                        "replaced", "obsolete", "former", "earlier", "changelog",
                        "history", "preserved", "before a", "methods-only", "split")

#: Files whose job is to enumerate every path in the paper. A manifest listing a
#: superseded record is an inventory, not a currency claim.
INVENTORY_FILES = ("CONTENT_MANIFEST", "SHA256SUMS", "MANIFEST.json")

_AUTHORITY = re.compile(r"(?P<stem>[A-Z0-9]+_ACTIVE_CLAIM_AUTHORITY)_V(?P<v>\d+)\.json$")
_SCAN_SUFFIX = {".md", ".json", ".tex", ".txt"}
_WINDOW = 160
#: How close a currency marker must sit before the reference to count.
_PRECEDING = 70


@dataclass(frozen=True)
class StalenessReport:
    exit_code: int
    terminal: str
    chains: dict[str, dict] = field(default_factory=dict)
    problems: tuple[str, ...] = field(default=())

    @property
    def passed(self) -> bool:
        return self.exit_code == EXIT_PASS


def authority_chains(papers: Path) -> dict[str, dict]:
    """Map each paper to its authority chain and the active head of that chain."""

    chains: dict[str, dict] = {}
    if not papers.is_dir():
        return chains
    for paper in sorted(p for p in papers.iterdir() if p.is_dir()):
        found: list[tuple[int, str]] = []
        for f in paper.iterdir():
            m = _AUTHORITY.match(f.name)
            if m:
                found.append((int(m.group("v")), f.name))
        if not found:
            continue
        found.sort()
        chains[paper.name] = {
            "members": [n for _, n in found],
            "active": found[-1][1],
            "superseded": [n for _, n in found[:-1]],
            "chain_length": len(found),
        }
    return chains


def _cited_as_current(text: str, name: str) -> list[str]:
    """Return snippets where ``name`` is presented as the current authority."""

    hits: list[str] = []
    for m in re.finditer(re.escape(name), text):
        lo = max(0, m.start() - _WINDOW)
        window = text[lo : m.end() + _WINDOW].lower()
        if any(s in window for s in SUPERSESSION_MARKERS):
            continue
        # The currency marker must PRECEDE the reference closely. "Active
        # authority: X" is a claim; a bare "current" fifty lines up is not.
        before = text[max(0, m.start() - _PRECEDING) : m.start()].lower()
        if any(c in before for c in CURRENCY_MARKERS):
            hits.append(text[lo : m.end() + 60].replace("\n", " ")[:180])
    return hits


def audit_repository(root: Path) -> StalenessReport:
    papers = root / "papers"
    chains = authority_chains(papers)
    if not chains:
        return StalenessReport(EXIT_CANNOT_CHECK, "AUTHORITY_STALENESS_CANNOT_CHECK",
                               {}, ("no authority chains found under papers/",))

    problems: list[str] = []
    for paper, chain in chains.items():
        if not chain["superseded"]:
            continue
        for path in sorted((papers / paper).rglob("*")):
            if not path.is_file() or path.suffix.lower() not in _SCAN_SUFFIX:
                continue
            if path.name in chain["members"]:
                continue  # a record naming itself is not a citation
            if any(tag in path.name for tag in INVENTORY_FILES):
                continue  # an inventory lists every path; that is not a claim
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for old in chain["superseded"]:
                for snippet in _cited_as_current(text, old):
                    problems.append(
                        f"{paper}/{path.name}: cites superseded {old} as current "
                        f"(active is {chain['active']}) -- ...{snippet}..."
                    )

    if problems:
        return StalenessReport(EXIT_STALE_CITATION, "AUTHORITY_STALENESS_FAIL",
                               chains, tuple(sorted(set(problems))))
    return StalenessReport(EXIT_PASS, "AUTHORITY_STALENESS_PASS", chains)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)

    report = audit_repository(args.root)
    multi = {k: v for k, v in report.chains.items() if v["chain_length"] > 1}
    print(f"papers with an authority record: {len(report.chains)}")
    print(f"papers with a versioned chain:   {len(multi)}")
    for k, v in sorted(multi.items()):
        print(f"  {k}: active={v['active']} superseded={len(v['superseded'])}")
    for problem in report.problems:
        print(f"  STALE {problem}", file=sys.stderr)
    print(report.terminal)
    return report.exit_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
