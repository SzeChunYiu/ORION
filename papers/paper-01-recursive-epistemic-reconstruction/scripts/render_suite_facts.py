#!/usr/bin/env python3
"""Derive the manuscript's scale facts from the artifacts instead of retyping them.

Every count that describes the frozen TEST suite — cases, systems, repeats,
achieved precision tier, half-width — appears as a literal in the manuscript
and protocol prose. Changing the suite would silently falsify those numbers.

This is the root-cause fix: the facts are read from the frozen cases and the
precision_tier module, emitted as LaTeX macros, and the manuscript uses the
macros. A stale number then becomes a failing test rather than a sentence a
reviewer catches.

``--check`` re-renders and exits non-zero if the committed macro file disagrees,
which is what CI and the test suite use.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

# Import from the study module
import sys

# Add src to path for imports
REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from orion.study.p1.cases import load_cases, suite_fingerprint, Split
from orion.study.p1.precision_tier import (
    Z_95,
    H1_SUPERIORITY_MARGIN,
    H2_NON_INFERIORITY_MARGIN,
    TierRule,
    achieved_tier,
    required_n_for_half_width,
)

PAPER = Path(__file__).resolve().parent.parent
CASES_ROOT = PAPER / "protocol" / "cases"
PROTOCOL_PATH = PAPER / "protocol" / "PROTOCOL_V1.json"
OUTPUT = PAPER / "manuscript" / "generated" / "suite_facts.tex"

# Z-score for 95% confidence
Z = Z_95

# Tier thresholds (half-widths at p=0.5)
TIERS = [
    ("TIER_A_full", 0.03),
    ("TIER_B_committed", 0.05),
    ("TIER_C_reduced", 0.075),
    ("TIER_D_minimum_inferential", 0.10),
]


class _FamilyMacros(dict):
    """Family name -> macro name, matched with separators normalised.

    An unregistered family raises instead of falling back to a derived name: a
    derived name would contain underscores or digits, which TeX cannot use in a
    control sequence, so the failure would surface as an uncompilable manuscript
    rather than as a missing entry here.
    """

    @staticmethod
    def _key(family: str) -> str:
        return family.replace("-", "_").lower()

    def __getitem__(self, family: str) -> str:
        try:
            return super().__getitem__(self._key(family))
        except KeyError:
            raise KeyError(
                f"no LaTeX macro registered for task family {family!r}; "
                "add one to FAMILY_MACROS rather than deriving it"
            ) from None


#: Registered task family -> the LaTeX macro the manuscript cites for its count.
FAMILY_MACROS = _FamilyMacros({
    "execution_only_negative_control": "ExecutionOnlyCount",
    "evidence_only_negative_control": "EvidenceOnlyCount",
    "hidden_decomposition_or_interface": "HiddenDecompositionCount",
    "hidden_parent_domain": "HiddenParentDomainCount",
    "hidden_representation_or_coordinate_system": "HiddenRepresentationCount",
    "hidden_measurement_or_operationalization": "HiddenMeasurementCount",
})


def _fmt_int(value: int) -> str:
    """Thousands separators, so 16,380 reads as a count rather than a serial."""
    return f"{value:,}".replace(",", "{,}")


def _render_tier_table() -> str:
    """Render the tier table as LaTeX for the manuscript."""
    lines = ["\\begin{table}[ht]", "\\centering", "\\caption{Precision tiers and required N}"]
    lines.append("\\label{tab:precision_tiers}")
    lines.append("\\begin{tabular}{llcc}")
    lines.append("\\toprule")
    lines.append("Tier & Half-width & Required N (p=0.5) & Resolves H1 \\\\")
    lines.append("\\midrule")

    for tier_name, half_width in TIERS:
        n = required_n_for_half_width(half_width, assumed_p=0.5)
        resolves = "Yes" if half_width <= H1_SUPERIORITY_MARGIN else "No"
        lines.append(f"{tier_name} & $\\pm{half_width:.3f}$ & {_fmt_int(n)} & {resolves} \\\\")

    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("\\end{table}")
    return "\n".join(lines)


def collect() -> dict[str, Any]:
    """Collect all facts from the frozen artifacts."""
    # Load cases
    pilot_cases = load_cases(CASES_ROOT, split=Split.PILOT)
    test_cases = load_cases(CASES_ROOT, split=Split.TEST)

    # Compute fingerprints
    pilot_fp = suite_fingerprint(pilot_cases)
    test_fp = suite_fingerprint(test_cases)

    # Count cases by family
    from orion.study.p1.cases import TaskFamily

    family_counts: dict[str, int] = {}
    for case in test_cases:
        family_counts[case.task_family.value] = family_counts.get(case.task_family.value, 0) + 1

    # Compute precision tier
    tier, half_width = achieved_tier(len(test_cases))
    tier_rule = TierRule.from_n(len(test_cases))

    # Read stochastic_repeats from protocol
    protocol = json.loads(PROTOCOL_PATH.read_text()) if PROTOCOL_PATH.exists() else {}
    stochastic_repeats = protocol.get("statistics", {}).get("stochastic_repeats", 5)

    facts: dict[str, Any] = {
        # Suite counts
        "PilotCaseCount": len(pilot_cases),
        "TestCaseCount": len(test_cases),
        # Fingerprints
        "PilotSuiteFingerprintShort": str(pilot_fp)[:12],
        "TestSuiteFingerprintShort": str(test_fp)[:12],
        # Precision tier
        "AchievedTier": tier,
        "AchievedHalfWidth": f"{half_width:.4f}",
        "RequiredNForHOne": _fmt_int(required_n_for_half_width(H1_SUPERIORITY_MARGIN)),
        "RequiredNForHTwo": _fmt_int(required_n_for_half_width(H2_NON_INFERIORITY_MARGIN)),
        # Stochastic repeats
        "StochasticRepeats": stochastic_repeats,
        # Underpowered flag
        "Underpowered": "yes" if half_width > H1_SUPERIORITY_MARGIN else "no",
        # H1/H2 margins
        "POneHOneMargin": f"{H1_SUPERIORITY_MARGIN:.2f}",
        "POneHTwoMargin": f"{H2_NON_INFERIORITY_MARGIN:.2f}",
        # Family breakdown (for descriptive reporting)
    }

    # Add family-specific counts. A LaTeX control sequence is letters only, so a
    # family key cannot be used as a macro name directly: `\hidden_parent_domain_count`
    # and `\RequiredNForH1` are not names TeX can define, and a file full of them
    # would fail to compile rather than drift quietly. The mapping below is the
    # registry of the names the manuscript actually uses.
    for family, count in family_counts.items():
        facts[FAMILY_MACROS[family]] = count

    return facts


def render(facts: dict[str, Any]) -> str:
    """Render facts as LaTeX macros."""
    lines = [
        "% Generated by scripts/render_suite_facts.py. Do not edit by hand.",
        "% Regenerate after any change to the frozen suite:",
        "%   python3 scripts/render_suite_facts.py",
        "% The manuscript must cite these macros rather than literal counts.",
    ]

    for key, value in facts.items():
        if isinstance(value, int):
            rendered = _fmt_int(value)
        else:
            rendered = str(value).replace("_", "\\_")
        lines.append(f"\\newcommand{{\\{key}}}{{{rendered}}}")

    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the committed file is stale")
    parser.add_argument("--out", type=Path, default=OUTPUT)
    parser.add_argument("--tier-table", action="store_true", help="print the tier table as LaTeX")
    args = parser.parse_args(argv)

    if args.tier_table:
        print(_render_tier_table())
        return 0

    text = render(collect())
    if args.check:
        if not args.out.is_file():
            print(f"SUITE_FACTS missing: {args.out}")
            return 1
        current = args.out.read_text(encoding="utf-8")
        if current != text:
            print("SUITE_FACTS stale: regenerate with scripts/render_suite_facts.py")
            return 1
        print("SUITE_FACTS ok")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
