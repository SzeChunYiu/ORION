"""Refuse PEER_REVIEW_READY claims that lack required artifacts.

Issue #153 owns the publication-closure wave. This module is the mechanical
gate: a paper that *claims* ``PEER_REVIEW_READY`` without the required
manuscript/ledger/protocol/attestation/reproducibility bundle fails closed.
An honest non-claim (``CANNOT_CHECK`` / not ready) does not.

P1 H1 on the frozen 48-case TEST arm is prospectively underpowered. A
non-finding there is ``NOT_SUPPORTED`` / ``UNDERPOWERED`` evidence, not a
box that may be promoted to a confirmatory finding or to the journal
terminal.
"""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from orion.study.p1.precision_tier import TierRule

_PAPER_ID = re.compile(r"ORION-P(\d)")
_SUPPORTED = {"SUPPORTED", "PASS"}


@dataclass(frozen=True)
class PaperGate:
    paper_id: str
    paper_root: Path
    claims_ready: bool
    missing_artifacts: tuple[str, ...]
    blockers: tuple[str, ...]
    h1_verdict: str | None = None
    h1_powered: bool | None = None

    @property
    def ok(self) -> bool:
        return not self.missing_artifacts and not self.blockers


def claims_peer_review_ready(text: str) -> bool:
    """True only for an asserted terminal, never a done-definition.

    ``ORION-P1 = PEER_REVIEW_READY only when …`` is a predicate, not a claim.
    ``**not** PEER_REVIEW_READY`` on a current-terminal line is a non-claim.
    """

    for raw in text.splitlines():
        line = raw.strip()
        if "PEER_REVIEW_READY" not in line:
            continue
        lower = line.lower()
        if "only when" in lower or "only after" in lower:
            continue
        if re.search(r"\bnot\b.*PEER_REVIEW_READY", line, flags=re.IGNORECASE):
            continue
        if "not peer-review ready" in lower:
            continue
        if "**Terminal:**" in line or "**Readiness:**" in line:
            return True
        if re.search(r"ORION-P\d\s*=\s*PEER_REVIEW_READY", line) and "only" not in lower:
            return True
    return False


def _paper_id(paper_root: Path, readiness_text: str) -> str:
    protocol = paper_root / "protocol" / "PROTOCOL_V1.json"
    if protocol.is_file():
        try:
            payload = json.loads(protocol.read_text())
        except (OSError, json.JSONDecodeError):
            payload = {}
        paper_id = payload.get("paper_id")
        if isinstance(paper_id, str) and paper_id:
            return paper_id
    match = _PAPER_ID.search(readiness_text)
    if match:
        return f"P{match.group(1)}"
    return paper_root.name


def _exists(root: Path, relative: str) -> bool:
    return (root / relative).is_file()


def _any(root: Path, pattern: str) -> bool:
    return any(path.is_file() for path in root.glob(pattern))


def missing_ready_artifacts(paper_root: Path) -> tuple[str, ...]:
    """Artifacts required of any paper that claims PEER_REVIEW_READY."""

    missing: list[str] = []
    if not _exists(paper_root, "JOURNAL_READINESS.md"):
        missing.append("JOURNAL_READINESS.md")
    if not _exists(paper_root, "manuscript/main.tex"):
        missing.append("manuscript/main.tex")
    if not (
        _any(paper_root, "**/CLAIM_LEDGER*")
        or _any(paper_root, "evidence/CLAIM_LEDGER*")
        or _any(paper_root, "CLAIM_LEDGER*")
    ):
        missing.append("claim ledger")
    if not _exists(paper_root, "protocol/PROTOCOL_V1.json"):
        missing.append("protocol/PROTOCOL_V1.json")
    if not any(path.is_file() for path in paper_root.rglob("*PEER_REVIEW_READY*")):
        missing.append("PEER_REVIEW_READY attestation")
    if not (
        _exists(paper_root, "REPRODUCE.md")
        or (paper_root / "reproducibility").is_dir()
    ):
        missing.append("reproducibility binding")
    if not any(path.is_file() for path in (paper_root / "evidence").rglob("*") if path.is_file()):
        missing.append("evidence/")
    return tuple(missing)


def _p1_h1_row(paper_root: Path) -> dict | None:
    table = paper_root / "results" / "P1-T2_baseline_ablation_results.json"
    if not table.is_file():
        return None
    try:
        payload = json.loads(table.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    rows = payload.get("rows") or []
    for row in rows:
        if not isinstance(row, dict):
            continue
        assessment = (row.get("difference_vs_comparator") or {}).get("assessment") or {}
        if assessment.get("hypothesis_id") == "P1.H1" and row.get("system_id") == "orion_full":
            return row
    return None


def _p1_h1_status(paper_root: Path) -> tuple[str | None, bool | None]:
    """Return (verdict, powered) for P1 H1. Powered is False on the frozen n=48 arm."""

    row = _p1_h1_row(paper_root)
    n = 48
    if row is not None:
        n = int(row.get("n_cases_scored") or n)
        assessment = (row.get("difference_vs_comparator") or {}).get("assessment") or {}
        verdict = str(assessment.get("verdict") or "")
    else:
        verdict = None
    powered = not TierRule.from_n(n).underpowered
    return verdict, powered


def _paper_claims_ready(paper_root: Path, readiness_text: str | None) -> bool:
    text = readiness_text
    if text is None:
        path = paper_root / "JOURNAL_READINESS.md"
        text = path.read_text() if path.is_file() else ""
    if claims_peer_review_ready(text):
        return True
    for path in paper_root.rglob("*PEER_REVIEW_READY*"):
        if path.is_file() and claims_peer_review_ready(path.read_text()):
            return True
    return False


def evaluate_paper(paper_root: Path, readiness_text: str | None = None) -> PaperGate:
    readiness_path = paper_root / "JOURNAL_READINESS.md"
    text = readiness_text
    if text is None:
        text = readiness_path.read_text() if readiness_path.is_file() else ""
    paper_id = _paper_id(paper_root, text)
    claims_ready = _paper_claims_ready(paper_root, text)
    missing = missing_ready_artifacts(paper_root) if claims_ready else ()
    blockers: list[str] = []
    h1_verdict: str | None = None
    h1_powered: bool | None = None

    if paper_id == "P1" or paper_root.name == "paper-01-recursive-epistemic-reconstruction":
        h1_verdict, h1_powered = _p1_h1_status(paper_root)
        if h1_powered is False:
            if claims_ready:
                blockers.append(
                    "P1 H1 is underpowered on the frozen 48-case TEST arm and "
                    "cannot authorize PEER_REVIEW_READY"
                )
            if h1_verdict in _SUPPORTED:
                blockers.append(
                    "P1 H1 is reported "
                    f"{h1_verdict} while the frozen arm is underpowered; "
                    "the honest labels are NOT_SUPPORTED / UNDERPOWERED"
                )

    if claims_ready and missing:
        blockers.append(
            "claimed PEER_REVIEW_READY without required artifacts: "
            + ", ".join(missing)
        )

    return PaperGate(
        paper_id=paper_id,
        paper_root=paper_root,
        claims_ready=claims_ready,
        missing_artifacts=missing,
        blockers=tuple(blockers),
        h1_verdict=h1_verdict,
        h1_powered=h1_powered,
    )


def evaluate_tree(papers_root: Path) -> tuple[PaperGate, ...]:
    reports: list[PaperGate] = []
    for readiness in sorted(papers_root.glob("*/JOURNAL_READINESS.md")):
        reports.append(evaluate_paper(readiness.parent))
    return tuple(reports)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail if a paper claims PEER_REVIEW_READY without required artifacts."
    )
    parser.add_argument("--papers", type=Path, default=Path("papers"))
    args = parser.parse_args(argv)
    reports = evaluate_tree(args.papers)
    if not reports:
        print(f"no JOURNAL_READINESS.md files found under {args.papers}", flush=True)
        return 1
    failed = 0
    for item in reports:
        status = "PASS" if item.ok else "FAIL"
        claim = "PEER_REVIEW_READY" if item.claims_ready else "not claimed"
        extra = ""
        if item.paper_id == "P1":
            extra = f" H1={item.h1_verdict or 'ABSENT'} powered={item.h1_powered}"
        print(f"[{status}] {item.paper_id} claim={claim}{extra}")
        for missing in item.missing_artifacts:
            print(f"         missing: {missing}")
        for blocker in item.blockers:
            print(f"         blocker: {blocker}")
        if not item.ok:
            failed += 1
    print(f"\n{len(reports)} papers, {failed} failed", flush=True)
    return 1 if failed else 0


__all__ = [
    "PaperGate",
    "claims_peer_review_ready",
    "evaluate_paper",
    "evaluate_tree",
    "main",
    "missing_ready_artifacts",
]


if __name__ == "__main__":
    raise SystemExit(main())
