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
import hashlib
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
    p1_successor_valid: bool | None = None

    @property
    def ok(self) -> bool:
        return not self.missing_artifacts and not self.blockers


#: ``PEER_REVIEW_READY`` as a whole token, never as the prefix of a longer one.
#:
#: ``PEER_REVIEW_READY_NARROWED`` is a deliberately *weaker* terminal: a paper that
#: has narrowed its claim rather than met the full bar. A plain substring test reads
#: it as the full terminal, which is the one direction a readiness gate must never
#: fail in. ``research/publication/scoreboard.py`` already draws this distinction
#: with the same negative lookahead; this module now agrees with it rather than
#: quietly scoring the two terminals the same.
PEER_REVIEW_READY_TOKEN = re.compile(r"PEER_REVIEW_READY(?![A-Za-z0-9_])")

#: Words that make a line a condition on some future state rather than an assertion
#: about the present one. "only" alone was too narrow: P2 states its bar as
#: ``ORION-P2 = PEER_REVIEW_READY_NARROWED when the narrowed manuscript compiles``,
#: which is a definition of done and not a claim of being done.
_CONDITIONAL_MARKERS = (" when ", " once ", " after ", " until ", " if ")


def claims_peer_review_ready(text: str) -> bool:
    """True only for an asserted terminal, never a done-definition.

    ``ORION-P1 = PEER_REVIEW_READY only when …`` is a predicate, not a claim.
    ``**not** PEER_REVIEW_READY`` on a current-terminal line is a non-claim.
    ``ORION-P2 = PEER_REVIEW_READY_NARROWED`` is a different, weaker terminal and
    is not a claim of this one.
    """

    for raw in text.splitlines():
        line = raw.strip()
        if not PEER_REVIEW_READY_TOKEN.search(line):
            continue
        lower = line.lower()
        if any(marker in lower for marker in _CONDITIONAL_MARKERS):
            continue
        if re.search(r"\bnot\b.*PEER_REVIEW_READY", line, flags=re.IGNORECASE):
            continue
        if "not peer-review ready" in lower:
            continue
        if "**Terminal:**" in line or "**Readiness:**" in line:
            return True
        if re.search(r"ORION-P\d\s*=\s*PEER_REVIEW_READY(?![A-Za-z0-9_])", line):
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


_P1_SUCCESSOR_PROTOCOL = "P1.epistemic-mutation-necessity.v2.2.4"
_P1_SUCCESSOR_TERMINAL = "P1_MUTATION_NECESSITY_SUPPORTED"
_P1_SUCCESSOR_BOUNDARY = "NO_MODEL_GENERAL_OR_OPEN_ENDED_SUPERIORITY"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_object(path: Path, blockers: list[str]) -> dict:
    if not path.is_file():
        blockers.append(f"P1 successor artifact is absent: {path.name}")
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        blockers.append(f"P1 successor artifact is unreadable: {path.name}: {exc}")
        return {}
    if not isinstance(value, dict):
        blockers.append(f"P1 successor artifact is not a JSON object: {path.name}")
        return {}
    return value


def _verify_sha256_manifest(directory: Path, blockers: list[str]) -> None:
    manifest = directory / "SHA256SUMS"
    if not manifest.is_file():
        blockers.append(f"P1 successor checksum manifest is absent: {manifest}")
        return
    for number, raw in enumerate(manifest.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            expected, name = raw.split(maxsplit=1)
        except ValueError:
            blockers.append(f"P1 successor checksum line {number} is malformed: {manifest}")
            continue
        path = directory / name.strip()
        if not path.is_file():
            blockers.append(f"P1 successor checksum target is absent: {path.name}")
        elif _sha256(path) != expected:
            blockers.append(f"P1 successor checksum mismatch: {path.name}")


def p1_successor_blockers(paper_root: Path) -> tuple[str, ...]:
    """Validate the prospective P1 successor without rewriting negative V1 history.

    The old 48-case H1 remains underpowered and NOT_SUPPORTED.  Readiness for the
    narrower mechanical claim is authorized only by the separately versioned,
    prospectively frozen primary and disjoint-replication evidence bundle.
    """

    blockers: list[str] = []
    repo = paper_root.parents[1]
    evidence = repo / "research" / "revival" / "p1" / "confirmatory" / "v2.2"
    primary_dir = evidence / "primary"
    replication_dir = evidence / "replication"
    primary_path = primary_dir / "PRIMARY_RESULT.json"
    replication_path = replication_dir / "REPLICATION_RESULT.json"
    primary = _read_object(primary_path, blockers)
    replication = _read_object(replication_path, blockers)
    primary_verification = _read_object(primary_dir / "INDEPENDENT_VERIFICATION.json", blockers)
    replication_verification = _read_object(
        replication_dir / "INDEPENDENT_VERIFICATION.json", blockers
    )
    concordance = _read_object(evidence / "PRIMARY_REPLICATION_CONCORDANCE.json", blockers)
    amendment = _read_object(evidence / "EXECUTION_BINDING_AMENDMENT_V2.json", blockers)
    primary_freeze_path = evidence / "PRIMARY_EXECUTION_FREEZE_V3.json"
    primary_freeze = _read_object(primary_freeze_path, blockers)
    replication_freeze = _read_object(
        replication_dir / "REPLICATION_EXECUTION_FREEZE.json", blockers
    )

    _verify_sha256_manifest(primary_dir, blockers)
    _verify_sha256_manifest(replication_dir, blockers)

    for label, result in (("primary", primary), ("replication", replication)):
        analysis = result.get("analysis") or {}
        gates = analysis.get("gates") or {}
        if result.get("terminal") != _P1_SUCCESSOR_TERMINAL:
            blockers.append(f"P1 successor {label} terminal is not supported")
        if result.get("n_worlds") != 2882 or result.get("n_runnable_arms") != 9:
            blockers.append(f"P1 successor {label} does not bind the frozen 2,882-world/9-arm design")
        if analysis.get("all_support_gates_pass") is not True:
            blockers.append(f"P1 successor {label} has a failed support gate")
        if not gates or not all(value is True for value in gates.values()):
            blockers.append(f"P1 successor {label} gate vector is incomplete or failed")
        if _P1_SUCCESSOR_BOUNDARY not in str(result.get("claim_boundary", "")):
            blockers.append(f"P1 successor {label} is missing the bounded-claim exclusion")

    for label, verification in (
        ("primary", primary_verification),
        ("replication", replication_verification),
    ):
        if verification.get("protocol_version") != _P1_SUCCESSOR_PROTOCOL:
            blockers.append(f"P1 successor {label} verifier protocol mismatch")
        if (
            verification.get("verdict") != "PASS"
            or verification.get("terminal_matches") is not True
            or verification.get("score_mismatch_count") != 0
            or verification.get("analysis_mismatch_count") != 0
            or verification.get("n_raw_rows") != 40348
            or verification.get("expected_rows") != 40348
        ):
            blockers.append(f"P1 successor {label} independent verification is not exact")

    required_concordance = concordance.get("required_concordance") or {}
    if concordance.get("protocol_version") != _P1_SUCCESSOR_PROTOCOL:
        blockers.append("P1 successor concordance protocol mismatch")
    if not required_concordance or not all(value is True for value in required_concordance.values()):
        blockers.append("P1 successor primary/replication concordance is incomplete or failed")
    if _P1_SUCCESSOR_BOUNDARY not in str(concordance.get("claim_boundary", "")):
        blockers.append("P1 successor concordance is missing the bounded-claim exclusion")
    for key, path in (("primary_result", primary_path), ("replication_result", replication_path)):
        expected = (concordance.get(key) or {}).get("sha256")
        if path.is_file() and expected != _sha256(path):
            blockers.append(f"P1 successor concordance hash mismatch: {path.name}")

    for label, freeze in (("primary", primary_freeze), ("replication", replication_freeze)):
        if (
            freeze.get("protocol_version") != _P1_SUCCESSOR_PROTOCOL
            or freeze.get("arms_executed") is not False
            or freeze.get("outcome_accessed") is not False
            or freeze.get("n") != 2882
            or freeze.get("hidden_shift_n") != 480
            or freeze.get("negative_control_n") != 2402
        ):
            blockers.append(f"P1 successor {label} execution freeze is invalid")

    if (
        amendment.get("protocol_version") != _P1_SUCCESSOR_PROTOCOL
        or amendment.get("arms_executed_before_correction") is not False
        or amendment.get("scientific_terminal_observed_before_correction") is not False
        or amendment.get("confirmatory_worlds_changed") is not False
        or amendment.get("protocol_or_margin_changed") is not False
        or amendment.get("new_execution_receipt") != primary_freeze_path.name
        or (
            primary_freeze_path.is_file()
            and amendment.get("new_execution_receipt_sha256") != _sha256(primary_freeze_path)
        )
    ):
        blockers.append("P1 successor pre-outcome execution amendment is invalid")

    return tuple(dict.fromkeys(blockers))


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
    p1_successor_valid: bool | None = None

    if paper_id == "P1" or paper_root.name == "paper-01-recursive-epistemic-reconstruction":
        h1_verdict, h1_powered = _p1_h1_status(paper_root)
        successor_blockers = p1_successor_blockers(paper_root)
        p1_successor_valid = not successor_blockers
        if h1_powered is False:
            if claims_ready and not p1_successor_valid:
                blockers.append(
                    "P1 H1 is underpowered on the frozen 48-case TEST arm and "
                    "cannot authorize PEER_REVIEW_READY without the valid powered successor"
                )
            if h1_verdict in _SUPPORTED:
                blockers.append(
                    "P1 H1 is reported "
                    f"{h1_verdict} while the frozen arm is underpowered; "
                    "the honest labels are NOT_SUPPORTED / UNDERPOWERED"
                )
        if claims_ready:
            blockers.extend(successor_blockers)

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
        p1_successor_valid=p1_successor_valid,
    )


def evaluate_tree(papers_root: Path) -> tuple[PaperGate, ...]:
    reports: list[PaperGate] = []
    for readiness in sorted(papers_root.glob("*/JOURNAL_READINESS.md")):
        report = evaluate_paper(readiness.parent)
        # This gate governs the flagship P<n> packages only. Candidate paper
        # packages promoted alongside them into papers/ carry their own
        # readiness CI (p6-p8-candidate-ci, the P9/P10 closure workflows) and
        # identify by directory name rather than a canonical P<n> id.
        if re.fullmatch(r"P\d+", report.paper_id):
            reports.append(report)
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
            extra = (
                f" H1={item.h1_verdict or 'ABSENT'} powered={item.h1_powered}"
                f" successor_valid={item.p1_successor_valid}"
            )
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
    "p1_successor_blockers",
]


if __name__ == "__main__":
    raise SystemExit(main())
