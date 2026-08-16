from __future__ import annotations

import argparse
import json
from pathlib import Path

from orion.benchmarks.external_evidence import empty_external_manifest
from orion.benchmarks.external_io import load_external_manifest
from orion.benchmarks.flagship import current_flagship_evidence_state


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m orion.benchmarks")
    subcommands = parser.add_subparsers(dest="command", required=True)
    status = subcommands.add_parser(
        "external-status",
        help="Assess P1-P5 external evidence from a frozen manifest JSON file.",
    )
    status.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Host-produced ExternalEvidenceManifest JSON. Omit to show the repository-only CANNOT_CHECK boundary.",
    )
    return parser


def _status_payload(manifest_path: Path | None) -> dict[str, object]:
    manifest = empty_external_manifest() if manifest_path is None else load_external_manifest(manifest_path)
    state = current_flagship_evidence_state(manifest)
    return {
        "manifest_id": manifest.manifest_id,
        "subject_revision_hash": manifest.subject_revision_hash,
        "evaluation_epoch_id": manifest.evaluation_epoch_id,
        "local_all_pass": state.local_all_pass,
        "external_all_pass": state.external_all_pass,
        "publication_ready": state.publication_ready,
        "external": [
            {
                "paper_id": report.paper_id,
                "case_id": report.case_id,
                "status": report.status.value,
                "blockers": list(report.blockers),
                "metrics": dict(report.metrics),
            }
            for report in state.external_reports
        ],
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "external-status":
        print(json.dumps(_status_payload(args.manifest), indent=2, sort_keys=True))
        return 0
    raise AssertionError("unreachable command")


__all__ = ["main"]
