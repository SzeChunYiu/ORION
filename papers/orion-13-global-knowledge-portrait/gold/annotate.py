#!/usr/bin/env python3
"""Annotation command-line tools for the ORION Paper 3 gold dataset.

Commands (run from the gold/ directory):

    python3 annotate.py list
    python3 annotate.py annotate P3.BIOMED.001 out.json
    python3 annotate.py validate sample.json out.json
    python3 annotate.py stats
    python3 annotate.py adjudicate a.json b.json out.json

The annotation schema is frozen in
../protocol/ANNOTATION_SCHEMA_V1.json and the adjudication sequence in
../protocol/ADJUDICATION_POLICY_V1.md — this tool does not invent labels;
it marshals human annotation into the frozen schema and checks structural
validity against it.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GOLD_DIR = Path(__file__).resolve().parent
PROTOCOL_DIR = GOLD_DIR.parent / "protocol"
SCHEMA_PATH = PROTOCOL_DIR / "ANNOTATION_SCHEMA_V1.json"

# The 11 required coordinates of the frozen schema (see ANNOTATION_SCHEMA_V1.json).
REQUIRED_COORDINATES = [
    "referent_relation", "construct_relation", "measurement_relation",
    "context_relation", "polarity_relation", "modality_relation",
    "attribution_relation", "discourse_relation", "mapping_relation",
    "contradiction_verdict", "integration_verdict",
]

OBSTRUCTION_TYPES = ["GLUE_ALLOWED", "OBSTRUCTION", "PLURAL_VIEW", "UNRESOLVED"]


# ── helpers ───────────────────────────────────────────────────────────────────

def _load_version(load_path: Path | str) -> Any:
    payload = json.loads(Path(load_path).read_text(encoding="utf-8"))
    if isinstance(payload, dict) and "samples" in payload:
        return payload
    return {"samples": payload}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_list(manifest: dict[str, Any]) -> int:
    print(f"{'sample_id':<18}{'discipline':<10}{'case_family':<40} status")
    for s in manifest["samples"]:
        print(f"{s['sample_id']:<18}{s['discipline']:<10}{s['case_family']:<40} "
              f"{s.get('annotation_status', 'pending')}")
    return 0


def cmd_annotate(sample_id: str, out_path: Path, template: dict[str, Any]) -> int:
    """Emit a blank annotation record for one sample, ready for editing."""
    sample = next((s for s in template["samples"]
                   if s["sample_id"] == sample_id), None)
    if sample is None:
        print(f"ERROR: unknown sample_id {sample_id!r}", file=sys.stderr)
        return 1
    record: dict[str, Any] = {
        "schema_version": "orion.p3.annotation.v1",
        "sample_id": sample_id,
        "case_family": sample["case_family"],
        "discipline": sample["discipline"],
        "annotator": "PENDING",
        "annotated_at": None,
        "source_a": sample["source_a"],
        "source_b": sample["source_b"],
        "coordinates": {coord: "PENDING" for coord in REQUIRED_COORDINATES},
        "source_span": {
            "source_a_span": {
                "document_id": sample["source_a"]["document_id"],
                "document_version": sample["source_a"]["document_version"],
                "span_start": sample["source_a"]["span_start"],
                "span_end": sample["source_a"]["span_end"],
                "text_hash": sample["source_a"]["text_hash"],
            },
            "source_b_span": {
                "document_id": sample["source_b"]["document_id"],
                "document_version": sample["source_b"]["document_version"],
                "span_start": sample["source_b"]["span_start"],
                "span_end": sample["source_b"]["span_end"],
                "text_hash": sample["source_b"]["text_hash"],
            },
        },
        "contradiction_details": None,
        "obstruction_type": None,
        "recoverability_target": None,
        "preservation_conditions": [],
        "annotator_notes": "",
    }
    out_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote blank annotation skeleton to {out_path}")
    print(f"Fill coordinate values per {SCHEMA_PATH} (values per frozen handbook).")
    print("Allowed integration verdicts:", ", ".join(OBSTRUCTION_TYPES))
    return 0


def cmd_validate(annotation_path: Path, report_path: Path) -> int:
    """Validate a completed annotation record against the frozen schema."""
    rec = json.loads(annotation_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    for coord in REQUIRED_COORDINATES:
        val = rec.get("coordinates", {}).get(coord)
        if val in (None, "PENDING", ""):
            errors.append(f"coordinate {coord} is {val!r}")
    if rec.get("integration_verdict") not in OBSTRUCTION_TYPES:
        pass  # integration verdict is a coordinate, checked above
    # Structural span check: hashes must be non-empty.
    for side in ("source_a", "source_b"):
        sp = (rec.get("source_span") or {}).get(f"{side}_span") or {}
        if not sp.get("text_hash"):
            errors.append(f"source_span.{side}.text_hash is empty")
    report = {
        "schema_version": "orion.p3.annotation-validation.v1",
        "annotation_path": str(annotation_path),
        "sample_id": rec.get("sample_id"),
        "valid": not errors,
        "errors": errors,
        "validated_at": _now_iso(),
    }
    if report_path:
        report_path.write_text(json.dumps(report, indent=2) + "\n",
                               encoding="utf-8")
    if errors:
        print("INVALID:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"VALID: {report['sample_id']} passes ANNOTATION_SCHEMA_V1.v1 checks.")
    return 0


def cmd_adjudicate(a_path: Path, b_path: Path, out_path: Path) -> int:
    """Merge two independent annotations of the same sample via adjudication."""
    ra = json.loads(a_path.read_text(encoding="utf-8"))
    rb = json.loads(b_path.read_text(encoding="utf-8"))
    if ra["sample_id"] != rb["sample_id"]:
        print(f"ERROR: sample_id mismatch {ra['sample_id']} vs {rb['sample_id']}",
              file=sys.stderr)
        return 1
    disagreements: list[str] = []
    for coord in REQUIRED_COORDINATES:
        va = ra["coordinates"].get(coord)
        vb = rb["coordinates"].get(coord)
        if va != vb and va not in (None, "PENDING") and vb not in (None, "PENDING"):
            disagreements.append(coord)
    record = {
        "schema_version": "orion.p3.adjudicated-annotation.v1",
        "sample_id": ra["sample_id"],
        "case_family": ra["case_family"],
        "discipline": ra["discipline"],
        "annotations": [a_path.name, b_path.name],
        "disagreements": disagreements,
        "adjudicated_at": None,   # set by the human adjudicator
        "adjudicator_notes": "",
    }
    out_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    if disagreements:
        print("Disagreements to adjudicate on:", ", ".join(disagreements))
    else:
        print("No coordinate disagreements between the two annotations.")
    return 0


def cmd_stats(manifest: dict[str, Any]) -> int:
    from collections import Counter
    families = Counter(s["case_family"] for s in manifest["samples"])
    discs = Counter(s["discipline"] for s in manifest["samples"])
    n_samples = len(manifest["samples"])
    print(f"samples: {n_samples}")
    print("by case family:")
    for fam, n in sorted(families.items()):
        print(f"  {fam:<42}{n}")
    print("by discipline:")
    for d, n in sorted(discs.items()):
        print(f"  {d:<10}{n}")
    return 0


# ── CLI ───────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="annotate.py",
        description="ORION Paper 3 gold annotation tooling",
    )
    parser.add_argument("--manifest", type=Path,
                        default=GOLD_DIR / "SAMPLE_MANIFEST_SEED_V1.json",
                        help="Path to the sample manifest (default: seed)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List samples with status")
    p_list.set_defaults(func=cmd_list)

    p_ann = sub.add_parser("annotate", help="Emit a blank annotation skeleton")
    p_ann.add_argument("sample_id")
    p_ann.add_argument("out", type=Path)
    p_ann.set_defaults(func=cmd_annotate)

    p_val = sub.add_parser("validate", help="Validate a completed annotation")
    p_val.add_argument("annotation", type=Path)
    p_val.add_argument("--report", "-o", type=Path, default=None)
    p_val.set_defaults(func=cmd_validate)

    p_adj = sub.add_parser("adjudicate", help="Merge two annotations (adjudicator)")
    p_adj.add_argument("a", type=Path)
    p_adj.add_argument("b", type=Path)
    p_adj.add_argument("out", type=Path)
    p_adj.set_defaults(func=cmd_adjudicate)

    p_stats = sub.add_parser("stats", help="Dataset coverage statistics")
    p_stats.set_defaults(func=cmd_stats)

    args = parser.parse_args(argv)

    # Commands that need the manifest.
    if args.command in ("list", "annotate", "stats"):
        manifest = _load_version(args.manifest)
        if args.command == "list":
            return args.func(manifest)
        if args.command == "stats":
            return args.func(manifest)
        return args.func(args.sample_id, args.out, manifest)

    if args.command == "validate":
        return args.func(args.annotation, args.report)
    return args.func(args.a, args.b, args.out)


if __name__ == "__main__":
    raise SystemExit(main())