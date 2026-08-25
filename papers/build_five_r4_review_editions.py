#!/usr/bin/env python3
"""Build single-file R4 review editions from the canonical V3+R4 sources.

The generated files are review conveniences, not automatically renumbered
journal submissions.  The source of truth remains each V3 manuscript plus its
R4 mathematical addendum.

Run from the repository root:

    python papers/build_five_r4_review_editions.py

Optional output directory:

    python papers/build_five_r4_review_editions.py --output-dir /tmp/r4-review
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPERS = ROOT / "papers"

SOURCES = {
    "paper-A": PAPERS / "theory-A-multitag-constraint-rank",
    "paper-B": PAPERS / "theory-B-certificate-complexity",
    "paper-C": PAPERS / "theory-C-low-order-information",
    "paper-D": PAPERS / "theory-D-falsification-authority",
    "nonquantum": PAPERS / "nonquantum-c5cubed-davenport",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, object] = {
        "source_branch_contract": "V3 baseline plus R4 theorem addendum",
        "generated": [],
    }

    for slug, directory in SOURCES.items():
        baseline = directory / "MANUSCRIPT_V3_PIPELINE.md"
        extension = directory / "MATHEMATICAL_EXTENSIONS_R4.md"
        if not baseline.is_file() or not extension.is_file():
            raise FileNotFoundError(f"missing canonical source in {directory}")

        output = output_dir / f"{slug}-R4-REVIEW-EDITION.md"
        text = (
            "# R4 Review Edition\n\n"
            "> Mechanically assembled for mathematical review. The first part is the recovered "
            "V3 manuscript; the second is the R4 theorem addendum. The addendum must be "
            "editorially integrated and theorem numbering reconciled before journal submission.\n\n"
            f"> Baseline SHA-256: `{sha256(baseline)}`  \n"
            f"> Addendum SHA-256: `{sha256(extension)}`\n\n"
            "---\n\n"
            "## Part I — Recovered V3 manuscript\n\n"
            f"{baseline.read_text(encoding='utf-8').rstrip()}\n\n"
            "---\n\n"
            "## Part II — R4 mathematical extension\n\n"
            f"{extension.read_text(encoding='utf-8').rstrip()}\n"
        )
        output.write_text(text, encoding="utf-8")

        manifest["generated"].append(
            {
                "paper": slug,
                "output": str(output),
                "output_sha256": sha256(output),
                "baseline": str(baseline.relative_to(ROOT)),
                "baseline_sha256": sha256(baseline),
                "extension": str(extension.relative_to(ROOT)),
                "extension_sha256": sha256(extension),
            }
        )

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PAPERS / "generated-r4-review",
        help="directory for generated review editions",
    )
    args = parser.parse_args()
    manifest = build(args.output_dir.resolve())
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
