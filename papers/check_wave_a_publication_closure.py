#!/usr/bin/env python3
"""Fail-closed structural checker for ORION Publication Closure Wave A.

This checker validates the specialist-first control plane. It intentionally does
not infer scientific readiness from prose keywords: paper-native replay, package,
and claim gates are checked separately. A PASS grants no scientific, novelty,
journal, or submission authority.
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
    top_packet = papers_root / TOP_LEVEL_PACKET
    manifest_path = papers_root / MANIFEST

    require(papers_root.is_dir(), f"missing papers directory: {papers_root}", errors)
    require(top_packet.is_file(), f"missing top-level packet: {top_packet}", errors)
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
        "specialist-first closure policy missing",
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
    require(isinstance(papers, list), "papers must be a list", errors)
    if not isinstance(papers, list):
        papers = []
    require(len(papers) == 8, "Wave A must contain exactly 8 papers", errors)

    seen_ids: set[str] = set()
    seen_dirs: set[str] = set()
    priorities: list[int] = []

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
        require(lane in {"PACKAGE_ONLY", "SPECIALIST_PACKAGE"}, f"{prefix}: invalid lane", errors)
        require(isinstance(phases, list) and bool(phases), f"{prefix}: required_phases missing", errors)
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
            priorities.append(priority)

        paper_dir = root / directory if isinstance(directory, str) else root / "__invalid__"
        require(paper_dir.is_dir(), f"missing paper directory: {paper_dir}", errors)
        packet_value = item.get("control_packet")
        if packet_value is None:
            packet = paper_dir / DEFAULT_PAPER_PACKET
        elif isinstance(packet_value, str):
            packet = root / packet_value
        else:
            packet = root / "__invalid_control_packet__"
            errors.append(f"{prefix}: control_packet must be a string when present")
        require(packet.is_file(), f"missing control packet: {packet}", errors)
        text = packet.read_text(encoding="utf-8") if packet.is_file() else ""
        require(len(text.strip()) >= 200, f"{paper_id}: control packet is unexpectedly empty", errors)
        for phrase in FORBIDDEN_PROMOTION_PHRASES:
            require(phrase not in text, f"{paper_id}: forbidden promotion phrase: {phrase}", errors)

        records.append(
            {
                "paper_id": paper_id,
                "priority": priority,
                "lane": lane,
                "specialist_gate": specialist_gate,
                "top_tier_gate": top_tier_gate,
                "required_phases": phases,
                "control_packet": str(packet.relative_to(root)) if packet.is_file() else None,
                "control_packet_sha256": sha256(packet) if packet.is_file() else None,
            }
        )

    require(sorted(priorities) == list(range(1, 9)), "priorities must be exactly 1..8", errors)
    for path in (top_packet, manifest_path):
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            for phrase in FORBIDDEN_PROMOTION_PHRASES:
                require(phrase not in text, f"forbidden promotion phrase in {path}: {phrase}", errors)

    return {
        "schema": "ORION.PublicationClosureWaveA.CheckResult.v1",
        "ok": not errors,
        "git_head": git_head(root),
        "paper_count": len(records),
        "manifest_sha256": sha256(manifest_path) if manifest_path.is_file() else None,
        "top_level_packet_sha256": sha256(top_packet) if top_packet.is_file() else None,
        "papers": sorted(records, key=lambda row: row.get("priority") or 999),
        "errors": errors,
        "authority_delta": "NONE",
        "note": "Control-plane structural PASS only; paper-native specialist closure is checked separately.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = check(args.root.resolve())
    print(json.dumps(result, sort_keys=args.json, separators=(",", ":") if args.json else None, indent=None if args.json else 2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
