"""Fail-closed publication contract for the ORION P6-P15 top-tier promotion wave.

This module does not decide scientific truth.  It checks that every candidate paper
keeps an explicit upward-claim contract and that no contract can look complete merely
because a planning file exists.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PAPER_SPECS: tuple[tuple[int, str, str], ...] = (
    (6, "paper-06-formal-epistemic-structures-and-mechanics", "Epistemic Transition"),
    (7, "paper-07-epistemic-navigation-open-worlds", "Regime Transport"),
    (8, "paper-08-epistemic-authority-autonomous-science", "Scientific authorization"),
    (9, "paper-09-structured-epistemic-learning", "Representation Accessibility"),
    (10, "paper-10-structured-problem-solving", "Obstruction-Certified Method Expansion"),
    (11, "paper-11-state-as-computation", "computational placement"),
    (12, "paper-12-adaptive-state-reasoning", "Resource-Location Metareasoning"),
    (13, "paper-13-responsibility-carrying-state", "Responsibility-Scoped"),
    (14, "paper-14-orion-rse", "Scientific Governance"),
    (15, "paper-15-orion-research-harness", "Scientific Execution Integrity"),
)

PROGRAMME_FILE = Path("papers/TOP_TIER_PROMOTION_PROGRAM_V1.md")
PROMOTION_FILE = "TOP_TIER_PROMOTION_V1.md"

REQUIRED_PROGRAMME_MARKERS: tuple[str, ...] = (
    "nearest work -> absorb strongest mechanism",
    "IGNORE_TO_PRESERVE_NOVELTY",
    "No self-authority",
    "Negative-history rule",
    "TOP_TIER_SUBMISSION_READY",
    "Shared external validation worlds",
    "Common resource vector",
)

REQUIRED_PAPER_MARKERS: tuple[str, ...] = (
    "## Maximum claim to earn",
    "## Top-tier promotion gate",
    "TOP_TIER_SUBMISSION_READY",
    "Strongest hostile attacks",
)


@dataclass(frozen=True)
class PromotionFinding:
    code: str
    path: str
    detail: str


def _read(root: Path, rel: Path) -> str:
    path = root / rel
    if not path.is_file():
        raise FileNotFoundError(rel.as_posix())
    return path.read_text(encoding="utf-8")


def audit_top_tier_promotion(root: Path) -> list[PromotionFinding]:
    """Return all structural publication-contract findings.

    Empty findings mean only that the repository carries the required fail-closed
    planning contract.  They do *not* authorize any scientific or publication claim.
    """

    findings: list[PromotionFinding] = []

    try:
        programme = _read(root, PROGRAMME_FILE)
    except FileNotFoundError:
        return [
            PromotionFinding(
                "TT-PROGRAMME-MISSING",
                PROGRAMME_FILE.as_posix(),
                "programme-wide promotion constitution is missing",
            )
        ]

    for marker in REQUIRED_PROGRAMME_MARKERS:
        if marker not in programme:
            findings.append(
                PromotionFinding(
                    "TT-PROGRAMME-MARKER-MISSING",
                    PROGRAMME_FILE.as_posix(),
                    marker,
                )
            )

    for number, directory, upward_marker in PAPER_SPECS:
        rel = Path("papers") / directory / PROMOTION_FILE
        try:
            text = _read(root, rel)
        except FileNotFoundError:
            findings.append(
                PromotionFinding(
                    "TT-PAPER-CONTRACT-MISSING",
                    rel.as_posix(),
                    f"P{number} promotion contract is missing",
                )
            )
            continue

        for marker in REQUIRED_PAPER_MARKERS:
            if marker not in text:
                findings.append(
                    PromotionFinding(
                        "TT-PAPER-MARKER-MISSING",
                        rel.as_posix(),
                        marker,
                    )
                )

        if upward_marker.casefold() not in text.casefold():
            findings.append(
                PromotionFinding(
                    "TT-UPWARD-CLAIM-MISSING",
                    rel.as_posix(),
                    upward_marker,
                )
            )

        if "Top-tier state:" not in text:
            findings.append(
                PromotionFinding(
                    "TT-STATE-MISSING",
                    rel.as_posix(),
                    "explicit top-tier state is required",
                )
            )

        # A planning contract must not self-promote.  Scientific promotion requires
        # separate protected-result authority, never prose in this file alone.
        if "**Top-tier state:** `TOP_TIER_SUBMISSION_READY`" in text:
            findings.append(
                PromotionFinding(
                    "TT-SELF-PROMOTION-FORBIDDEN",
                    rel.as_posix(),
                    "promotion protocol cannot itself authorize submission readiness",
                )
            )

    return findings


def assert_top_tier_promotion_contract(root: Path) -> None:
    findings = audit_top_tier_promotion(root)
    if findings:
        rendered = "\n".join(
            f"{finding.code}: {finding.path}: {finding.detail}" for finding in findings
        )
        raise AssertionError(rendered)
