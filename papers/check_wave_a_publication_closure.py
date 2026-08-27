#!/usr/bin/env python3
"""Fail-closed structural checker for ORION Publication Closure Wave A.

This checker validates coordination/protocol structure only. A PASS grants no
scientific, novelty, journal, peer-review, or submission authority. Specialist
closure is deliberately separate from optional top-tier promotion: a paper may
finish at the strongest bounded reproducible claim even when its top-tier
breadth discriminator remains open.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

SCHEMA = "ORION.PublicationClosureWaveA.v1"
MANIFEST = "WAVE_A_PUBLICATION_CLOSURE_MANIFEST_V1.json"
TOP_LEVEL_PACKET = "PUBLICATION_CLOSURE_WAVE_A_V1.md"
DEFAULT_PAPER_PACKET = "PUBLICATION_CLOSURE_WAVE_A_V1.md"

FORBIDDEN_PROMOTION_PHRASES = (
    "WAVE_A_TOP_TIER_EARNED",
    "TOP_TIER_CERTIFIED",
    "EXTERNALLY_PEER_REVIEWED",
    "JOURNAL_ACCEPTED",
)

COMMON_TOKENS = (
    "Maximum current claim",
    "Good specialist finish",
    "Required artifacts",
    "independent",
    "public",
)

OUTCOME_TOKENS = (
    "Registered terminals",
    "protocol",
    "baseline",
    "Hostile controls",
    "manuscript",
)

PACKAGE_ONLY_TOKENS = (
    "Current authority boundary",
    "Allowed work",
    "No new experiment rule",
    "Finish terminal",
    "filing",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head(root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing manifest: {path}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {path}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"manifest root must be an object: {path}")
        return {}
    return value


def check(root: Path) -> dict[str, Any]:
    papers_root = root / "papers"
    errors: list[str] = []
    records: list[dict[str, Any]] = []

    require(papers_root.is_dir(), f"missing papers directory: {papers_root}", errors)
    top_packet = papers_root / TOP_LEVEL_PACKET
    require(top_packet.is_file(), f"missing top-level packet: {top_packet}", errors)

    manifest_path = papers_root / MANIFEST
    manifest = load_json(manifest_path, errors)
    if not manifest:
        return {
            "schema": "ORION.PublicationClosureWaveA.CheckResult.v1",
            "ok": False,
            "git_head": git_head(root),
            "errors": errors,
            "papers": records,
            "authority_delta": "NONE",
        }

    require(manifest.get("schema") == SCHEMA, "wrong manifest schema", errors)
    require(manifest.get("authority_delta") == "NONE", "authority_delta must remain NONE", errors)
    require(
        manifest.get("closure_policy") == "GOOD_SPECIALIST_FIRST__TOP_TIER_OPTIONAL",
        "closure_policy must keep specialist closure primary",
        errors,
    )

    rules = manifest.get("rules")
    require(isinstance(rules, dict), "rules must be an object", errors)
    if isinstance(rules, dict):
        for key in (
            "text_only_promotion_forbidden",
            "negative_history_required",
            "public_external_authority_preferred",
            "protocol_before_outcomes",
            "independent_verification_required",
            "final_submission_bytes_required",
            "top_tier_discriminator_does_not_block_specialist_submission",
        ):
            require(rules.get(key) is True, f"rule must be true: {key}", errors)

    papers = manifest.get("papers")
    require(isinstance(papers, list) and bool(papers), "papers must be a non-empty list", errors)
    if not isinstance(papers, list):
        papers = []

    seen_ids: set[str] = set()
    seen_dirs: set[str] = set()
    seen_priorities: set[int] = set()

    for index, item in enumerate(papers):
        prefix = f"papers[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue

        paper_id = item.get("paper_id")
        directory = item.get("directory")
        priority = item.get("priority")
        lane = item.get("lane")
        phases = item.get("required_phases")
        specialist_gate = item.get("specialist_gate")
        top_tier_gate = item.get("top_tier_gate")

        require(isinstance(paper_id, str) and paper_id.startswith("ORION-"), f"{prefix}: invalid paper_id", errors)
        require(isinstance(directory, str) and directory.startswith("papers/orion-"), f"{prefix}: invalid directory", errors)
        require(isinstance(priority, int) and priority > 0, f"{prefix}: invalid priority", errors)
        require(lane in {"PACKAGE_ONLY", "SPECIALIST_PACKAGE"}, f"{prefix}: invalid specialist-first lane", errors)
        require(isinstance(phases, list) and bool(phases), f"{prefix}: required_phases must be non-empty", errors)
        require(isinstance(specialist_gate, str) and bool(specialist_gate), f"{prefix}: specialist_gate missing", errors)
        require(
            isinstance(top_tier_gate, str) and top_tier_gate.startswith("OPTIONAL"),
            f"{prefix}: top_tier_gate must be explicitly optional",
            errors,
        )

        if isinstance(paper_id, str):
            require(paper_id not in seen_ids, f"duplicate paper_id: {paper_id}", errors)
            seen_ids.add(paper_id)
        if isinstance(directory, str):
            require(directory not in seen_dirs, f"duplicate directory: {directory}", errors)
            seen_dirs.add(directory)
        if isinstance(priority, int):
            require(priority not in seen_priorities, f"duplicate priority: {priority}", errors)
            seen_priorities.add(priority)
        if isinstance(phases, list):
            require(len(phases) == len(set(phases)), f"{prefix}: duplicate required phase", errors)

        paper_dir = root / directory if isinstance(directory, str) else root / "__invalid__"
        packet_value = item.get("control_packet")
        if packet_value is None:
            packet = paper_dir / DEFAULT_PAPER_PACKET
        elif isinstance(packet_value, str):
            packet = root / packet_value
        else:
            packet = root / "__invalid_control_packet__"
            errors.append(f"{prefix}: control_packet must be a string when present")

        require(paper_dir.is_dir(), f"missing paper directory: {paper_dir}", errors)
        require(packet.is_file(), f"missing paper packet: {packet}", errors)

        text = packet.read_text(encoding="utf-8") if packet.is_file() else ""
        for token in COMMON_TOKENS:
            require(token.lower() in text.lower(), f"{paper_id}: packet missing token: {token}", errors)

        required = PACKAGE_ONLY_TOKENS if lane == "PACKAGE_ONLY" else OUTCOME_TOKENS
        for token in required:
            require(token.lower() in text.lower(), f"{paper_id}: packet missing token: {token}", errors)

        for phrase in FORBIDDEN_PROMOTION_PHRASES:
            require(phrase not in text, f"{paper_id}: forbidden promotion phrase: {phrase}", errors)

        if lane != "PACKAGE_ONLY":
            require("CANNOT_CHECK" in text or "cannot check" in text.lower(), f"{paper_id}: no fail-closed CANNOT_CHECK surface", errors)
            require("negative" in text.lower() or "adverse" in text.lower(), f"{paper_id}: negative/adverse history not required", errors)
            require("resource" in text.lower(), f"{paper_id}: resource matching/accounting absent", errors)

        records.append(
            {
                "paper_id": paper_id,
                "lane": lane,
                "priority": priority,
                "protocol_path": str(packet.relative_to(root)) if packet.is_file() else None,
                "protocol_sha256": sha256(packet) if packet.is_file() else None,
                "specialist_gate": specialist_gate,
                "top_tier_gate": top_tier_gate,
                "required_phases": phases,
            }
        )

    priorities = sorted(p for p in seen_priorities if isinstance(p, int))
    require(priorities == list(range(1, len(papers) + 1)), "priorities must be contiguous from 1", errors)
    require(len(papers) == 8, "Wave A must contain exactly 8 papers", errors)

    for path in (top_packet, manifest_path):
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            for phrase in FORBIDDEN_PROMOTION_PHRASES:
                require(phrase not in text, f"forbidden promotion phrase in {path}: {phrase}", errors)

    return {
        "schema": "ORION.PublicationClosureWaveA.CheckResult.v1",
        "ok": not errors,
        "git_head": git_head(root),
        "manifest_sha256": sha256(manifest_path) if manifest_path.is_file() else None,
        "top_level_packet_sha256": sha256(top_packet) if top_packet.is_file() else None,
        "paper_count": len(records),
        "papers": sorted(records, key=lambda row: row.get("priority") or 10**9),
        "errors": errors,
        "authority_delta": "NONE",
        "note": "Structural PASS only: specialist closure still requires paper-native scientific/reproduction/package gates on the same immutable head.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (default: derived from this file)",
    )
    parser.add_argument("--json", action="store_true", help="print compact JSON")
    args = parser.parse_args(argv)

    result = check(args.root.resolve())
    if args.json:
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
