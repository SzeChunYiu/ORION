"""Three Definition-of-done properties of issue #1086, computed rather than asserted.

Each of these bullets is a statement about the *record*, not about an
experiment, so each can be checked without running anything:

* **P5 and P10 retain CANNOT_CHECK until protected/external custody exists.**
  Checked against P5's claim ledger and P10's active claim authority. The two
  papers use different conventions -- P5 carries ``empirical_authority`` in
  ``evidence/CLAIM_LEDGER_V1.json``, P10 carries ``active_terminal`` and
  ``promotion_allowed`` in a ``*_ACTIVE_CLAIM_AUTHORITY_*.json`` -- so both
  shapes are handled explicitly rather than guessed at.

* **Failed experiments generate bounded/null papers rather than silent
  retuning.** Checked against the negative revival backlog: every revived
  negative must name the successor that replaced it, and a negative marked
  protected must forbid repair. A negative that changed status with no named
  successor is exactly the silent retuning the bullet forbids.

* **No claim states that public online data, hashes, another AI session, or
  same-owner CI bypasses independent adjudication.** Checked by scanning the
  paper tree for affirmative bypass phrasings.

The scan is the delicate one, so it is built to be auditable rather than
clever. It carries a closed lexicon; it classifies a hit as a violation only
when no negation or prohibition marker precedes it in the same window; and it
excludes retrieved-corpus evidence, because a third-party paper title that
happens to say "demonstrates independent regulation of Rap1 and ERK" is not an
ORION claim about its own authority. Every exclusion is named in the result, so
a reader can see what the scan chose not to look at.

Run it::

    python -m orion.programme.claim_boundary_audit --root .

Exit codes: 0 PASS, 2 retention broken, 3 silent retuning, 4 bypass claim
found, 5 malformed input -- could not check.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

__all__ = [
    "BYPASS_LEXICON",
    "EXCLUDED_EVIDENCE_MARKERS",
    "EXIT_BYPASS_CLAIM",
    "EXIT_CANNOT_CHECK",
    "EXIT_PASS",
    "EXIT_RETENTION",
    "EXIT_SILENT_RETUNING",
    "NEGATION_MARKERS",
    "BoundaryAudit",
    "audit_cannot_check_retention",
    "audit_negative_revival",
    "scan_bypass_claims",
    "main",
]

#: Phrasings that would assert the bypass the bullet forbids. Closed list, kept
#: lowercase, matched case-insensitively.
BYPASS_LEXICON: tuple[str, ...] = (
    "establishes independen",
    "constitutes independen",
    "provides independen",
    "is independent validation",
    "counts as independen",
    "amounts to independen",
    "establishes protected",
    "provides protected confirmation",
    "bypasses independen",
    "substitutes for independen",
    "serves as independen",
    "demonstrates independen",
)

#: A hit qualified by any of these inside the window is a boundary statement, a
#: prohibition or a restriction -- the opposite of the claim being scanned for.
#:
#: The window is searched on BOTH sides of the hit, because the qualifier often
#: follows: "a route counts as independent *only* from content/provenance
#: evidence, *not* tool/provider naming" is a restriction, and a backward-only
#: window reads it as an assertion. That sentence was the scan's single false
#: positive on its first real run, and it is why "only" and "solely" are here.
NEGATION_MARKERS: tuple[str, ...] = (
    "only ",
    "solely",
    "unless",
    "not ",
    "never",
    "no ",
    "cannot",
    "forbidden",
    "rather than",
    "does not",
    "do not",
    "without",
    "neither",
    "nor ",
    "prohibit",
    "refus",
    "denied",
)

#: Path fragments holding retrieved third-party corpus rows. Text there is data
#: the system fetched, not a claim the system makes.
EXCLUDED_EVIDENCE_MARKERS: tuple[str, ...] = (
    "/offline_results/",
    "/raw_oai_pages/",
    "/candidates_",
    "/decoded-interface/",
    "/frozen-native-interface/",
)

_WINDOW = 90

EXIT_PASS = 0
EXIT_RETENTION = 2
EXIT_SILENT_RETUNING = 3
EXIT_BYPASS_CLAIM = 4
EXIT_CANNOT_CHECK = 5

_SCANNED_SUFFIXES = {".md", ".tex", ".json", ".txt"}


@dataclass(frozen=True)
class BoundaryAudit:
    exit_code: int
    terminal: str
    problems: tuple[str, ...] = field(default=())
    detail: tuple[str, ...] = field(default=())

    @property
    def passed(self) -> bool:
        return self.exit_code == EXIT_PASS


def audit_cannot_check_retention(p5_ledger: Any, p10_authority: Any) -> tuple[list[str], list[str]]:
    """P5 and P10 must not carry a promoted empirical claim."""

    problems: list[str] = []
    detail: list[str] = []

    if not isinstance(p5_ledger, dict):
        problems.append("P5 claim ledger is not an object")
    else:
        authority = p5_ledger.get("empirical_authority")
        detail.append(f"P5 empirical_authority={authority!r}")
        if authority != "CANNOT_CHECK":
            problems.append(f"P5 empirical_authority is {authority!r}, expected CANNOT_CHECK")
        if p5_ledger.get("peer_review_ready") is not False:
            problems.append("P5 is marked peer_review_ready while its authority is CANNOT_CHECK")

    if not isinstance(p10_authority, dict):
        problems.append("P10 active claim authority is not an object")
    else:
        claim = p10_authority.get("active_empirical_claim")
        terminal = p10_authority.get("active_terminal")
        detail.append(f"P10 active_empirical_claim={claim!r} active_terminal={terminal!r}")
        if claim is not None:
            problems.append(f"P10 carries an active empirical claim: {claim!r}")
        if p10_authority.get("promotion_allowed") is True:
            problems.append("P10 allows promotion while no protected custody exists")
        if p10_authority.get("execution_authorized") is True:
            problems.append("P10 authorizes execution while its protocol is prospective only")

    return problems, detail


def audit_negative_revival(backlog: Any) -> tuple[list[str], list[str]]:
    """Every revived negative names its successor; protected negatives forbid repair."""

    if not isinstance(backlog, dict):
        return ["negative revival backlog is not an object"], []

    problems: list[str] = []
    detail: list[str] = []

    revived = backlog.get("already_revived")
    if not isinstance(revived, list) or not revived:
        problems.append("backlog records no revived negatives, so revival cannot be evidenced")
    else:
        detail.append(f"revived negatives: {len(revived)}")
        for entry in revived:
            if not isinstance(entry, dict):
                problems.append("a revived entry is not an object")
                continue
            name = entry.get("negative", "<unnamed>")
            if not str(entry.get("successor", "")).strip():
                problems.append(
                    f"{name}: status changed with no named successor -- this is the silent retuning the bullet forbids"
                )

    protected = backlog.get("protected_negatives")
    if not isinstance(protected, list):
        problems.append("backlog carries no protected_negatives list")
    else:
        detail.append(f"protected negatives: {len(protected)}")
        for entry in protected:
            if not isinstance(entry, dict):
                problems.append("a protected entry is not an object")
                continue
            reason = str(entry.get("reason", "")).lower()
            if "forbid" not in reason and "protected" not in reason:
                problems.append(
                    f"{entry.get('claim', '<unnamed>')}: protected negative does not forbid repair or re-run"
                )

    directive = str(backlog.get("operator_directive", "")).lower()
    if directive:
        detail.append("operator directive present")
        if "never by tuning outcomes" not in directive and "tuning" not in directive:
            problems.append("operator directive does not forbid outcome tuning")
    else:
        problems.append("backlog carries no operator directive")

    return problems, detail


def _is_excluded(path: Path) -> bool:
    text = path.as_posix()
    return any(marker in text for marker in EXCLUDED_EVIDENCE_MARKERS)


def scan_bypass_claims(root: Path) -> tuple[list[str], list[str]]:
    """Scan the paper tree for affirmative bypass phrasings."""

    papers = root / "papers"
    if not papers.is_dir():
        return ["papers/ directory not found"], []

    violations: list[str] = []
    detail: list[str] = []
    scanned = 0
    excluded = 0
    negated = 0

    for path in sorted(papers.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in _SCANNED_SUFFIXES:
            continue
        if _is_excluded(path):
            excluded += 1
            continue
        try:
            body = path.read_text(encoding="utf-8", errors="replace").lower()
        except OSError:
            continue
        scanned += 1
        for phrase in BYPASS_LEXICON:
            for match in re.finditer(re.escape(phrase), body):
                window = body[
                    max(0, match.start() - _WINDOW) : match.end() + _WINDOW
                ]
                if any(marker in window for marker in NEGATION_MARKERS):
                    negated += 1
                    continue
                snippet = body[max(0, match.start() - 60) : match.start() + 60].replace("\n", " ")
                violations.append(f"{path.relative_to(root)}: ...{snippet}...")

    detail.append(f"files scanned: {scanned}; retrieved-corpus files excluded: {excluded}")
    detail.append(f"lexicon hits resolved as boundary or prohibition statements: {negated}")
    return violations, detail


def run_audit(root: Path) -> BoundaryAudit:
    problems: list[str] = []
    detail: list[str] = []
    worst = EXIT_PASS

    try:
        p5 = json.loads((root / "papers/paper-05-self-orion/evidence/CLAIM_LEDGER_V1.json").read_text(encoding="utf-8"))
        p10 = json.loads(
            (root / "papers/paper-10-structured-problem-solving/P10_ACTIVE_CLAIM_AUTHORITY_V1.json").read_text(
                encoding="utf-8"
            )
        )
        backlog = json.loads(
            (root / "research/paper-programme-v1/NEGATIVE_REVIVAL_BACKLOG_V1.json").read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as error:
        return BoundaryAudit(EXIT_CANNOT_CHECK, "CLAIM_BOUNDARY_CANNOT_CHECK", (str(error),))

    found, extra = audit_cannot_check_retention(p5, p10)
    problems += found
    detail += extra
    if found:
        worst = max(worst, EXIT_RETENTION)

    found, extra = audit_negative_revival(backlog)
    problems += found
    detail += extra
    if found:
        worst = max(worst, EXIT_SILENT_RETUNING)

    found, extra = scan_bypass_claims(root)
    problems += found
    detail += extra
    if found:
        worst = max(worst, EXIT_BYPASS_CLAIM)

    if worst == EXIT_PASS:
        return BoundaryAudit(EXIT_PASS, "CLAIM_BOUNDARY_PASS", (), tuple(detail))
    return BoundaryAudit(worst, "CLAIM_BOUNDARY_FAIL", tuple(problems), tuple(detail))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)

    audit = run_audit(args.root)
    for line in audit.detail:
        print(f"  {line}")
    for problem in audit.problems:
        print(f"  PROBLEM {problem}", file=sys.stderr)
    print(audit.terminal)
    return audit.exit_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
