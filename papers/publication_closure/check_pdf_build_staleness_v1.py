#!/usr/bin/env python3
"""Is a committed manuscript PDF stale in CONTENT, or only in provenance?

The audit workflow derives a manuscript's render epoch from the whole directory:

    git log -1 --format=%ct -- <manuscript_dir> ":(exclude)<manuscript_dir>/main.pdf"

That glob includes companion files the LaTeX build never reads. Several manuscripts
keep `.md` drafts and separately-rendered `FINAL_V*.pdf` next to the `.tex` sources, so
editing a companion `.md` moves the epoch and marks `main.pdf` stale even though the
bytes it was built from did not change.

This separates the two cases:

  FRESH                    no input changed after the PDF was committed
  STALE_CONTENT            a real build input (.tex/.bib/.sty/.cls, figures) changed
                           after the PDF -> the PDF shows something other than the source
  STALE_PROVENANCE_ONLY    only non-input files changed -> the render is still correct,
                           but CI's epoch check will not reproduce these bytes, so the
                           fix is a fresh CI-built import, not a content correction

The distinction matters because the two need different work, and calling the second a
content defect sends someone to rewrite a manuscript that is already right.

Exit codes: 0 nothing stale in content · 1 at least one STALE_CONTENT · 3 CANNOT_CHECK
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

EXIT_OK, EXIT_STALE_CONTENT, EXIT_CANNOT_CHECK = 0, 1, 3

# What a LaTeX build actually reads. Anything else in the directory is a companion.
BUILD_INPUT_SUFFIXES = (".tex", ".bib", ".sty", ".cls", ".bst",
                        ".pdf_tex", ".png", ".jpg", ".jpeg", ".eps", ".pdf")
COMPANION_PDF_HINT = "main.pdf"


def git(*a: str) -> str:
    r = subprocess.run(["/usr/bin/git", *a], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def is_build_input(rel: str) -> bool:
    """A .pdf under figures/ is an input; a sibling FINAL_V4.pdf is a companion."""
    base = os.path.basename(rel)
    if base == COMPANION_PDF_HINT:
        return False
    if rel.endswith(".pdf"):
        return "/figures/" in rel or "/fig/" in rel
    return rel.endswith(BUILD_INPUT_SUFFIXES)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="origin/main")
    ap.add_argument("--json-out", default="")
    args = ap.parse_args()

    papers = sorted(
        {p.split("/")[1] for p in git("ls-tree", "-r", "--name-only", args.ref, "--", "papers/").splitlines()
         if p.startswith("papers/orion-")}
    )
    if not papers:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": "NO_PAPERS_FOUND"}))
        return EXIT_CANNOT_CHECK

    rows, stale_content = [], []
    for p in papers:
        md = f"papers/{p}/manuscript"
        pdf = f"{md}/{COMPANION_PDF_HINT}"
        if not git("rev-parse", "--verify", "-q", f"{args.ref}:{pdf}").strip():
            continue
        pdf_commit = git("log", "-1", "--format=%H", args.ref, "--", pdf).strip()
        if not pdf_commit:
            continue
        # every commit that touched the directory after the PDF commit
        later = [c for c in git(
            "log", "--format=%H", f"{pdf_commit}..{args.ref}", "--", md,
            f":(exclude){pdf}").splitlines() if c]
        changed_inputs, changed_companions = set(), set()
        for c in later:
            for f in git("show", "--name-only", "--format=", c, "--", md).splitlines():
                if not f or f == pdf:
                    continue
                rel = f[len(md) + 1:] if f.startswith(md + "/") else f
                (changed_inputs if is_build_input(rel) else changed_companions).add(rel)
        if not later:
            state = "FRESH"
        elif changed_inputs:
            state = "STALE_CONTENT"
            stale_content.append(p)
        else:
            state = "STALE_PROVENANCE_ONLY"
        rows.append({
            "paper": p,
            "state": state,
            "pdf_commit": pdf_commit[:9],
            "commits_after": len(later),
            "changed_build_inputs": sorted(changed_inputs),
            "changed_companions_only": sorted(changed_companions),
        })

    out = {
        "ref": args.ref,
        "manuscripts_with_pdf": len(rows),
        "summary": {s: sum(1 for r in rows if r["state"] == s)
                    for s in ("FRESH", "STALE_CONTENT", "STALE_PROVENANCE_ONLY")},
        "stale_content": stale_content,
        "rows": rows,
        "status": "STALE_CONTENT_PRESENT" if stale_content else "NO_CONTENT_STALENESS",
    }
    print(json.dumps(out, indent=2))
    if args.json_out:
        with open(args.json_out, "w") as fh:
            json.dump(out, fh, indent=2)
            fh.write("\n")
    return EXIT_STALE_CONTENT if stale_content else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
