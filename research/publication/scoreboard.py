#!/usr/bin/env python3
"""Derive and validate the ORION P1–P5 publication scoreboard.

Readiness is computed from repository artifacts (the paper's declared current
readiness record, falling back to JOURNAL_READINESS.md,
claim ledgers, protocol freeze JSON). A paper cannot be labelled
PEER_REVIEW_READY unless JOURNAL_READINESS declares that terminal and the
supporting protocol/ledger files exist. This module refuses to invent
readiness from closed GitHub issues, local falsifiers, or stale READMEs.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable

from orion.publication.peer_review_ready import evaluate_paper

SCHEMA_VERSION = "orion.publication-status.v1"
STATUSES = ("PEER_REVIEW_READY", "BLOCKED", "CANNOT_CHECK")
PAPER_IDS = ("P1", "P2", "P3", "P4", "P5")

TERMINAL_LINE = re.compile(r"^\*\*(?:Current )?Terminal:\*\*\s*(.+)$", re.IGNORECASE)
# `PEER_REVIEW_READY` must not match inside a longer terminal such as
# `PEER_REVIEW_READY_NARROWED`. A substring test reads a deliberately weaker
# terminal as the full one, which is the single thing this scoreboard exists to
# prevent, and it fails in the inflating direction where nothing downstream
# would catch it.
PEER_REVIEW_READY_TOKEN = re.compile(r"PEER_REVIEW_READY(?![A-Za-z0-9_])")
READY_DECLARATION = re.compile(r"^\*\*`?ORION-P(?P<n>[1-5])\s*=\s*PEER_REVIEW_READY`?\.\*\*$")
STATUS_LINE = re.compile(r"^\*\*Status:\*\*\s*(.+)$", re.IGNORECASE)

PAPER_SPECS: tuple[dict[str, Any], ...] = (
    {
        "paper_id": "P1",
        "issue": 98,
        "title": "Recursive Epistemic Reconstruction",
        "root": "papers/paper-01-recursive-epistemic-reconstruction",
        "claim_ledgers": (
            "evidence/CLAIM_LEDGER_V1.md",
            "evidence/CLAIM_LEDGER.md",
        ),
    },
    {
        "paper_id": "P2",
        "issue": 99,
        "title": "Open-World Scientific Knowledge Discovery",
        "root": "papers/paper-02-open-world-scientific-discovery",
        "claim_ledgers": (
            "evidence/CLAIM_LEDGER_V1.md",
            "protocol/CLAIM_LEDGER_V1.json",
        ),
    },
    {
        "paper_id": "P3",
        "issue": 100,
        "title": "Global Knowledge Portrait",
        "root": "papers/paper-03-global-knowledge-portrait",
        "claim_ledgers": (
            "CLAIM_LEDGER_V1.md",
        ),
    },
    {
        "paper_id": "P4",
        "issue": 101,
        "title": "Verified Scientific Discovery",
        "root": "papers/paper-04-verified-scientific-discovery",
        "journal_readiness": "CURRENT_JOURNAL_READINESS_V1.md",
        "claim_ledgers": (
            "evidence/CLAIM_LEDGER_V1.md",
        ),
    },
    {
        "paper_id": "P5",
        "issue": 102,
        "title": "Self-ORION",
        "root": "papers/paper-05-self-orion",
        "claim_ledgers": (
            "evidence/CLAIM_LEDGER_V1.md",
            "CLAIM_LEDGER_V1.md",
            "protocol/CLAIM_LEDGER_V1.json",
        ),
    },
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def status_paths(root: Path | None = None) -> dict[str, Path]:
    base = root or repo_root()
    directory = base / "research" / "publication"
    return {
        "root": base,
        "directory": directory,
        "json": directory / "publication_status.json",
        "schema": directory / "publication_status.schema.json",
        "module": directory / "scoreboard.py",
    }


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def parse_journal_readiness_terminal(text: str) -> str | None:
    """Return PEER_REVIEW_READY, CANNOT_CHECK, or None if unparseable."""
    for raw in text.splitlines()[:24]:
        match = TERMINAL_LINE.match(raw.strip())
        if not match:
            continue
        value = match.group(1)
        ready_match = PEER_REVIEW_READY_TOKEN.search(value)
        cannot_match = re.search(r"\bCANNOT_CHECK\b", value)
        negated = re.search(
            r"\bnot\b[^*\n]*(?:PEER_REVIEW_READY(?![A-Za-z0-9_])|peer[- ]review[- ]ready)",
            value,
            re.IGNORECASE,
        )
        conditional = re.search(r"\b(?:when|once|after|until|if)\b", value, re.IGNORECASE)
        if negated or conditional:
            return "CANNOT_CHECK"
        # One machine-scored line must declare one terminal.  A line naming
        # both readiness and CANNOT_CHECK is unresolved and therefore fails
        # closed, irrespective of token order.  Scope qualifications belong on
        # an adjacent, non-terminal line where they remain visible to readers.
        if ready_match and cannot_match:
            return "CANNOT_CHECK"
        if ready_match:
            return "PEER_REVIEW_READY"
        if cannot_match:
            return "CANNOT_CHECK"
        return None
    return None


def terminal_line_is_ambiguous(text: str) -> str | None:
    """Describe a terminal line that names mutually exclusive terminals."""
    for raw in text.splitlines()[:24]:
        match = TERMINAL_LINE.match(raw.strip())
        if not match:
            continue
        value = match.group(1)
        if PEER_REVIEW_READY_TOKEN.search(value) and re.search(r"\bCANNOT_CHECK\b", value):
            return (
                "terminal line names both PEER_REVIEW_READY and CANNOT_CHECK: "
                f"{value}"
            )
        return None
    return None


def journal_readiness_declares_complete(text: str, paper_id: str) -> bool:
    expected = paper_id[-1]
    for raw in text.splitlines():
        match = READY_DECLARATION.match(raw.strip())
        if match and match.group("n") == expected:
            return True
    return False


def readme_records_peer_review_ready(text: str) -> bool:
    for raw in text.splitlines()[:12]:
        match = STATUS_LINE.match(raw.strip())
        if match:
            value = match.group(1)
            return (
                PEER_REVIEW_READY_TOKEN.search(value) is not None
                and "CANNOT_CHECK" not in value
            )
    return (
        PEER_REVIEW_READY_TOKEN.search(text.splitlines()[0]) is not None
        if text
        else False
    )


def _iter_unbound(value: Any, path: str = "$") -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _iter_unbound(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _iter_unbound(child, f"{path}[{index}]")
    elif isinstance(value, str) and "UNBOUND" in value.upper():
        yield path


def unbound_paths(payload: Any) -> list[str]:
    return sorted(_iter_unbound(payload))


def _ledger_status_is_cannot_check(status: str) -> bool:
    compact = " ".join(status.split())
    if "CANNOT_CHECK" not in compact:
        return False
    # Honest-boundary rows that *record* CANNOT_CHECK as the supported claim
    # still count: they mean the empirical coordinate is unresolved.
    if re.search(r"\bNOT[_ ]CLAIMED\b", compact, re.IGNORECASE):
        return False
    return True


def extract_markdown_cannot_check(text: str) -> list[str]:
    rows: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("|") or re.match(r"^\|[\s:-]+\|", line):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        status = cells[-1]
        blob = " | ".join(cells)
        blocking = _ledger_status_is_cannot_check(status) or "EXTERNAL NOT EXECUTED" in blob.upper()
        if not blocking:
            continue
        label = cells[0]
        if label.lower() in {"id", "claim", "#", "claim surface"}:
            continue
        detail = status if _ledger_status_is_cannot_check(status) else "EXTERNAL NOT EXECUTED"
        rows.append(f"{label}: {detail}")
    return rows


def extract_json_cannot_check(payload: Any) -> list[str]:
    rows: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            strength = node.get("strength") or node.get("status") or node.get("authority")
            if isinstance(strength, str) and _ledger_status_is_cannot_check(strength):
                claim_id = node.get("claim_id") or node.get("id") or node.get("region") or "claim"
                rows.append(f"{claim_id}: {strength}")
            for child in node.values():
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(payload)
    # Deduplicate while preserving order.
    seen: set[str] = set()
    unique: list[str] = []
    for row in rows:
        if row not in seen:
            seen.add(row)
            unique.append(row)
    return unique


def load_claim_ledger_cannot_check(path: Path) -> list[str]:
    if path.suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        return extract_json_cannot_check(payload)
    return extract_markdown_cannot_check(path.read_text(encoding="utf-8"))


def load_protocol(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a JSON object")
    return payload


def attestation_paths(paper_root: Path, repo: Path) -> list[str]:
    found = sorted(paper_root.rglob("PEER_REVIEW_READY*.md"))
    return [_rel(path, repo) for path in found if path.is_file()]


def derive_paper(spec: dict[str, Any], repo: Path) -> dict[str, Any]:
    paper_id = spec["paper_id"]
    paper_root = repo / spec["root"]
    jr_path = paper_root / spec.get("journal_readiness", "JOURNAL_READINESS.md")
    protocol_path = paper_root / "protocol" / "PROTOCOL_V1.json"
    readme_path = paper_root / "README.md"
    v2_path = repo / "research" / "paper-programme-v2" / "protocols" / f"{paper_id}_V2.json"
    notes: list[str] = []
    missing: list[str] = []
    warnings: list[str] = []

    record: dict[str, Any] = {
        "paper_id": paper_id,
        "issue": spec["issue"],
        "title": spec["title"],
        "root": spec["root"],
        "status": "CANNOT_CHECK",
        "journal_readiness": _rel(jr_path, repo),
        "journal_readiness_terminal": None,
        "protocol": _rel(protocol_path, repo),
        "protocol_id": None,
        "protocol_status": None,
        "outcome_accessed": None,
        "unbound_execution_bindings": [],
        "v2_protocol_status": None,
        "claim_ledgers": [],
        "claim_ledger_cannot_check": [],
        "readme": _rel(readme_path, repo),
        "readme_records_peer_review_ready": False,
        "attestation_paths": [],
        "missing_artifacts": missing,
        "warnings": warnings,
        "notes": notes,
    }

    if not jr_path.is_file():
        missing.append(f"{record['journal_readiness']}: current readiness record is absent")
        notes.append("Cannot score the paper without JOURNAL_READINESS.md.")
        return record

    jr_text = jr_path.read_text(encoding="utf-8")
    terminal = parse_journal_readiness_terminal(jr_text)
    record["journal_readiness_terminal"] = terminal
    if terminal is None:
        missing.append(
            f"{record['journal_readiness']}: first Terminal/Current terminal line is unparseable"
        )
        notes.append("JOURNAL_READINESS.md exists but does not declare a scorable terminal.")
        return record

    existing_ledgers: list[Path] = []
    for relative in spec["claim_ledgers"]:
        path = paper_root / relative
        if path.is_file():
            existing_ledgers.append(path)
            record["claim_ledgers"].append(_rel(path, repo))
            record["claim_ledger_cannot_check"].extend(
                f"{_rel(path, repo)} :: {item}" for item in load_claim_ledger_cannot_check(path)
            )

    protocol = load_protocol(protocol_path) if protocol_path.is_file() else None
    if protocol is None:
        missing.append(f"{record['protocol']}: protocol JSON is absent")
    else:
        record["protocol_id"] = protocol.get("protocol_id")
        record["protocol_status"] = protocol.get("protocol_status")
        record["outcome_accessed"] = protocol.get("outcome_accessed")
        bindings = protocol.get("execution_bindings", {})
        record["unbound_execution_bindings"] = unbound_paths(bindings)

    if v2_path.is_file():
        v2 = json.loads(v2_path.read_text(encoding="utf-8"))
        record["v2_protocol_status"] = v2.get("protocol_status")
        record["v2_protocol"] = _rel(v2_path, repo)

    if readme_path.is_file():
        record["readme_records_peer_review_ready"] = readme_records_peer_review_ready(
            readme_path.read_text(encoding="utf-8")
        )
    else:
        warnings.append(f"{record['readme']}: README.md is absent")

    record["attestation_paths"] = attestation_paths(paper_root, repo)

    if terminal == "PEER_REVIEW_READY":
        if protocol is None:
            record["status"] = "CANNOT_CHECK"
            notes.append("JOURNAL_READINESS declares PEER_REVIEW_READY but the V1 protocol is missing.")
            return record
        if not existing_ledgers:
            missing.append(f"{spec['root']}: no claim ledger file found")
            record["status"] = "CANNOT_CHECK"
            notes.append("JOURNAL_READINESS declares PEER_REVIEW_READY but no claim ledger exists to audit.")
            return record
        declared_complete = journal_readiness_declares_complete(jr_text, paper_id)
        if not record["attestation_paths"] and not declared_complete:
            missing.append(
                f"{spec['root']}: PEER_REVIEW_READY declared without attestation file or completed-terminal line"
            )
            record["status"] = "CANNOT_CHECK"
            notes.append("A PEER_REVIEW_READY declaration must be backed by an attestation or completed-terminal line.")
            return record
        mechanical_gate = evaluate_paper(paper_root)
        if not mechanical_gate.ok:
            missing.extend(
                f"{spec['root']}: {blocker}" for blocker in mechanical_gate.blockers
            )
            record["status"] = "CANNOT_CHECK"
            notes.append(
                "JOURNAL_READINESS declares PEER_REVIEW_READY but the fail-closed "
                "paper-specific evidence gate did not corroborate it."
            )
            return record
        if not record["readme_records_peer_review_ready"]:
            warnings.append(
                f"{record['readme']}: canonical README does not yet record PEER_REVIEW_READY "
                "(programme close still wants this; JOURNAL_READINESS remains the scoring terminal)"
            )
        record["status"] = "PEER_REVIEW_READY"
        notes.append(
            "JOURNAL_READINESS declares PEER_REVIEW_READY and the paper-specific "
            "artifact/evidence gate corroborates it."
        )
        return record

    # terminal is CANNOT_CHECK or otherwise not ready → BLOCKED if we can name gaps.
    missing.append(
        f"{record['journal_readiness']}: current terminal is {terminal}, not PEER_REVIEW_READY"
    )
    if protocol is None:
        pass
    elif protocol.get("protocol_status") == "DESIGN_FROZEN":
        unbound = record["unbound_execution_bindings"] or ["<execution_bindings>"]
        missing.append(
            f"{record['protocol']}: protocol_status=DESIGN_FROZEN; UNBOUND identities remain: "
            + ", ".join(unbound)
        )
    elif protocol.get("outcome_accessed") is False:
        missing.append(
            f"{record['protocol']}: protocol_status={protocol.get('protocol_status')} with "
            "outcome_accessed=false; V1 protocol has not authorized outcome access"
        )
    if not existing_ledgers:
        missing.append(f"{spec['root']}: no claim ledger file found")
    for item in record["claim_ledger_cannot_check"]:
        missing.append(item)
    if not record["readme_records_peer_review_ready"] and readme_path.is_file():
        warnings.append(f"{record['readme']}: README does not record PEER_REVIEW_READY")
    record["status"] = "BLOCKED"
    notes.append(
        "Artifacts exist and the paper is not PEER_REVIEW_READY; listed missing_artifacts are the blockers."
    )
    return record


def derive_scoreboard(repo: Path | None = None) -> dict[str, Any]:
    root = repo or repo_root()
    papers = [derive_paper(spec, root) for spec in PAPER_SPECS]
    ready = [paper["paper_id"] for paper in papers if paper["status"] == "PEER_REVIEW_READY"]
    unknown = [paper["paper_id"] for paper in papers if paper["status"] == "CANNOT_CHECK"]
    blocked = [paper["paper_id"] for paper in papers if paper["status"] == "BLOCKED"]
    if unknown and not blocked and not ready:
        programme_status = "CANNOT_CHECK"
    elif len(ready) == 5:
        programme_status = "PEER_REVIEW_READY"
    else:
        programme_status = "BLOCKED"
    close_allowed = programme_status == "PEER_REVIEW_READY" and not unknown and not blocked
    if close_allowed:
        reason = "All five papers are PEER_REVIEW_READY on repository artifacts."
    else:
        parts = []
        if ready:
            parts.append("ready=" + ",".join(ready))
        if blocked:
            parts.append("blocked=" + ",".join(blocked))
        if unknown:
            parts.append("cannot_check=" + ",".join(unknown))
        reason = (
            "Issue #97 may close only when P1–P5 are PEER_REVIEW_READY on main. "
            + "; ".join(parts)
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_from": {
            "rule": (
                "Derive each paper from its declared current readiness terminal, PROTOCOL_V1.json freeze "
                "state, and claim-ledger CANNOT_CHECK rows. Do not invent PEER_REVIEW_READY."
            )
        },
        "programme": {
            "issue": 97,
            "status": programme_status,
            "close_allowed": close_allowed,
            "papers_peer_review_ready": ready,
            "reason": reason,
        },
        "papers": papers,
    }


def canonical_dumps(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def validate_scoreboard(payload: dict[str, Any], repo: Path | None = None) -> list[str]:
    root = repo or repo_root()
    errors: list[str] = []
    if payload.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"wrong schema_version: {payload.get('schema_version')!r}")
    derived = derive_scoreboard(root)
    if payload.get("programme", {}).get("close_allowed") is True and derived["programme"]["status"] != "PEER_REVIEW_READY":
        errors.append("close_allowed=true is forbidden unless every paper is PEER_REVIEW_READY")
    derived_by_id = {paper["paper_id"]: paper for paper in derived["papers"]}
    papers = payload.get("papers")
    if not isinstance(papers, list) or len(papers) != 5:
        errors.append("publication_status.json must contain exactly five papers")
        return errors
    seen: list[str] = []
    for paper in papers:
        paper_id = paper.get("paper_id")
        seen.append(paper_id)
        derived_paper = derived_by_id.get(paper_id)
        if derived_paper is None:
            errors.append(f"unknown paper_id: {paper_id!r}")
            continue
        status = paper.get("status")
        if status not in STATUSES:
            errors.append(f"{paper_id}: invalid status {status!r}")
        if status != derived_paper["status"]:
            errors.append(
                f"{paper_id}: committed status {status!r} does not match derived "
                f"{derived_paper['status']!r}"
            )
        if status == "PEER_REVIEW_READY" and derived_paper["journal_readiness_terminal"] != "PEER_REVIEW_READY":
            errors.append(
                f"{paper_id}: PEER_REVIEW_READY is invented; JOURNAL_READINESS terminal is "
                f"{derived_paper['journal_readiness_terminal']!r}"
            )
        if status == "PEER_REVIEW_READY" and derived_paper["status"] != "PEER_REVIEW_READY":
            errors.append(f"{paper_id}: supporting artifacts do not corroborate PEER_REVIEW_READY")
    if tuple(seen) != PAPER_IDS:
        errors.append(f"papers must be ordered P1–P5, got {seen}")
    if payload.get("programme", {}).get("status") != derived["programme"]["status"]:
        errors.append(
            "programme.status "
            f"{payload.get('programme', {}).get('status')!r} does not match derived "
            f"{derived['programme']['status']!r}"
        )
    if payload.get("programme", {}).get("close_allowed") != derived["programme"]["close_allowed"]:
        errors.append("programme.close_allowed does not match derived scoreboard")
    return errors


def write_scoreboard(repo: Path | None = None) -> Path:
    paths = status_paths(repo)
    payload = derive_scoreboard(paths["root"])
    paths["json"].write_text(canonical_dumps(payload), encoding="utf-8")
    return paths["json"]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate the committed publication_status.json against derived artifacts",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="rewrite publication_status.json from the current tree",
    )
    return parser


def main() -> None:
    args = _parser().parse_args()
    paths = status_paths()
    if args.write:
        path = write_scoreboard()
        print(path)
        return
    if args.check:
        payload = json.loads(paths["json"].read_text(encoding="utf-8"))
        errors = validate_scoreboard(payload, paths["root"])
        if errors:
            raise SystemExit("publication_status.json is not honest:\n- " + "\n- ".join(errors))
        print("publication_status.json matches derived artifact state")
        return
    print(canonical_dumps(derive_scoreboard()), end="")


if __name__ == "__main__":
    main()
