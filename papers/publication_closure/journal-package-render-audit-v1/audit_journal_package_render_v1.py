#!/usr/bin/env python3
"""Report, per journal package, whether its render closure can be computed at all.

PUBLICATION_DISPOSITION_MATRIX_V1 records ORION-01's render closure as never
computed and attributes it to the packages sitting outside the generator's glob.
That is true and it is not the whole reason, so this separates the cases a
package can be in. They need different work and only one of them is a stale PDF.

COMPUTED   -- the package ships manuscript.pdf and the paper has a built
              manuscript/main.pdf, so write_render_closure_state can compare them.
              CURRENT or SUPERSEDED is then a real answer.
NO_PACKAGED_PDF -- the package ships no PDF at all. Nothing is stale, because
              nothing was packaged. A reviewer downloading this package gets no
              manuscript.
UNEXPECTED_PDF_NAME -- the package ships a PDF under another name, so the
              generator looks for a file that is there under a name it does not
              check.
NO_BUILT_MANUSCRIPT -- there is no papers/<paper>/manuscript/main.pdf to compare
              against, usually because the paper carries more than one manuscript
              and does not fit one-package-one-manuscript.

The distinction matters: "closure not computed" reads like a staleness problem,
and for five packages here it is actually a missing manuscript.

Exit codes: 0 every package computable, 2 at least one is not, 3 no packages found.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

EXPECTED_PACKAGED = "manuscript.pdf"
BUILT = Path("manuscript") / "main.pdf"


def classify(package: Path, root: Path) -> dict:
    pdfs = sorted(p.name for p in package.glob("*.pdf"))
    packaged = package / EXPECTED_PACKAGED
    built = package.parent / BUILT
    row = {
        "package": package.relative_to(root).as_posix(),
        "pdfs_shipped": pdfs,
        "has_expected_packaged_pdf": packaged.exists(),
        "has_built_manuscript": built.exists(),
        "closure_state_committed": (package / "RENDER_CLOSURE_STATE.json").exists(),
    }
    if packaged.exists() and built.exists():
        row["case"] = "COMPUTED"
    elif not pdfs:
        row["case"] = "NO_PACKAGED_PDF"
    elif not packaged.exists():
        row["case"] = "UNEXPECTED_PDF_NAME"
    else:
        row["case"] = "NO_BUILT_MANUSCRIPT"
    if row["case"] == "NO_BUILT_MANUSCRIPT" or (pdfs and not built.exists()):
        row["case"] = "NO_BUILT_MANUSCRIPT" if not built.exists() else row["case"]
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--emit", default="")
    a = ap.parse_args()
    root = Path(a.root).resolve()

    packages = sorted(p for p in root.glob("papers/*/journal_package*") if p.is_dir())
    if not packages:
        print("no journal packages found", file=sys.stderr)
        return 3

    rows = [classify(p, root) for p in packages]
    by_case: dict[str, list[str]] = {}
    for r in rows:
        by_case.setdefault(r["case"], []).append(r["package"])

    out = {
        "schema": "ORION.JOURNAL_PACKAGE_RENDER_AUDIT.v1",
        "packages": len(rows),
        "by_case": {k: sorted(v) for k, v in sorted(by_case.items())},
        "rows": rows,
        "reading": (
            "NO_PACKAGED_PDF is not a staleness problem: the package ships no "
            "manuscript, so a reviewer downloading it receives none. "
            "UNEXPECTED_PDF_NAME and NO_BUILT_MANUSCRIPT are why a closure reads as "
            "never computed rather than as drifted."
        ),
    }
    if a.emit:
        Path(a.emit).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"journal packages: {len(rows)}")
    for case in sorted(by_case):
        print(f"  {case:<22} {len(by_case[case])}")
        for p in by_case[case]:
            print(f"      {p}")
    return 0 if set(by_case) == {"COMPUTED"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
