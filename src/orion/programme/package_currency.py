"""Does a submission package still describe the source it was built from?

A journal package is an assertion: these exact bytes are what would be sent. It
carries a manifest of digests to make that assertion checkable. When the source
moves and the manifest does not, the package silently becomes a historical
snapshot still labelled as the current submission -- and the manifest, which
exists to detect exactly that, reports nothing because nobody runs it.

All five packages were stale when this was written, on files no one had noticed:
four on their readiness report and P3's additionally on ``manuscript/main.tex``
and ``bibliography.bib``, which are result-bearing. Turning that into a hard
failure would fail CI on five packages at once and end with the check disabled,
so this is a ratchet against a pinned baseline: new staleness fails, existing
debt is recorded and visible.

A stale entry is not the same as a missing one. Missing means the package claims
a file that is not there; stale means the file is there and has moved. Both are
counted, separately, because they need different fixes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

EXIT_PASS = 0
EXIT_REGRESSED = 2
EXIT_CANNOT_CHECK = 3

ENTRY = re.compile(r"^([0-9a-f]{64})  (.+)$")


@dataclass
class PackageState:
    paper: str
    entries: int = 0
    stale: int = 0
    missing: int = 0
    stale_paths: tuple[str, ...] = ()

    @property
    def current(self) -> bool:
        return self.stale == 0 and self.missing == 0


def survey(root: Path | None = None) -> list[PackageState]:
    root = root or Path(__file__).resolve().parents[3]
    papers = root / "papers"
    if not papers.is_dir():
        raise FileNotFoundError(papers)
    out: list[PackageState] = []
    for sums in sorted(papers.glob("*/journal_package/SHA256SUMS")):
        paper_dir = sums.parent.parent
        rec = PackageState(paper=paper_dir.name)
        stale: list[str] = []
        for line in sums.read_text(errors="replace").splitlines():
            m = ENTRY.match(line)
            if not m:
                continue
            rec.entries += 1
            target = paper_dir / m.group(2)
            if not target.is_file():
                rec.missing += 1
                continue
            if hashlib.sha256(target.read_bytes()).hexdigest() != m.group(1):
                rec.stale += 1
                stale.append(m.group(2))
        rec.stale_paths = tuple(sorted(stale))
        out.append(rec)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--write-baseline", type=Path, default=None)
    args = ap.parse_args(argv)
    try:
        rows = survey(args.root)
    except FileNotFoundError as exc:
        print(f"PACKAGE_CURRENCY_CANNOT_CHECK: {exc}")
        return EXIT_CANNOT_CHECK

    if args.write_baseline:
        doc = {
            "schema": "JOURNAL_PACKAGE_STALENESS_BASELINE_V1",
            "purpose": (
                "Debt record, not approval. Each entry is a submission package whose "
                "manifest no longer describes its own source. Recorded so CI can fail "
                "on new staleness without first failing on staleness that predates "
                "the check."
            ),
            "not_to_be_regenerated": (
                "Refreshing a package manifest to match moved source deletes the "
                "evidence that the package is no longer what it claims to be. Entries "
                "leave this file by rebuilding the package, never by rewriting digests."
            ),
            "packages": {
                r.paper: {"stale": r.stale, "missing": r.missing, "entries": r.entries}
                for r in rows
            },
        }
        args.write_baseline.write_text(json.dumps(doc, indent=2) + "\n")
        print(f"baseline written: {args.write_baseline}")

    bad = 0
    for r in rows:
        if r.current:
            print(f"  CURRENT   {r.paper:52s} {r.entries:3d} entries")
        else:
            bad += 1
            print(f"  STALE     {r.paper:52s} {r.entries:3d} entries  "
                  f"stale={r.stale} missing={r.missing}")
            for p in r.stale_paths[:3]:
                print(f"                e.g. {p}")
    print(f"\npackages: {len(rows)}   not describing their own source: {bad}")
    if bad:
        print("PACKAGE_CURRENCY_STALE: a package labelled as the submission no longer")
        print("describes the source it was built from")
        return EXIT_REGRESSED
    print("PACKAGE_CURRENCY_PASS")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
