#!/usr/bin/env python3
"""Execute the prospectively frozen P2 Wide V3 campaign.

V3 inherits every scientific degree of freedom from the exact V2 freeze and
changes only the DOI->OpenAIRE crosswalk transport to the separately frozen V4
beta filter grammar.  The implementation deliberately delegates acquisition,
projection, budgets, identity admission and candidate freezing to the V2 runner
while replacing only the crosswalk URL builder and transport prerequisite.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
V2_RUNNER_PATH = HERE / "run_autoresearchbench_wide_openaire_matched_v2.py"
V4_PROBE_PATH = HERE / "probe_openaire_v4_doi_filter_transport.py"
DEFAULT_V3_FREEZE = PAPER / "protocol" / "P2_WIDE_OPENAIRE_MATCHED_FREEZE_V3.json"
DEFAULT_V2_FREEZE = PAPER / "protocol" / "P2_WIDE_OPENAIRE_MATCHED_FREEZE_V2.json"
DEFAULT_IDENTITY_RECEIPT = PAPER / "evidence" / "external_results" / "P2_OPENAIRE_IDENTITY_PROBE_V1.json"
V3_TRANSPORT_ENCODING = "v4_filter_ids_doi_or_list"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module at {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


v2 = _load_module("orion_p2_wide_openaire_runner_v2_for_v3", V2_RUNNER_PATH)
v4 = _load_module("orion_p2_v4_probe_for_v3_runner", V4_PROBE_PATH)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _validate_v3_transport_bundle(
    receipt_path: Path,
    response_path: Path,
    v3_freeze: dict[str, Any],
) -> dict[str, Any]:
    receipt = v4.validate_final_receipt(receipt_path, response_path, v3_freeze)
    if receipt.get("terminal") != v4.TERMINAL:
        raise ValueError("V3 transport prerequisite did not reach its frozen terminal")
    if receipt.get("promotion_authorized") is not False:
        raise ValueError("V3 transport prerequisite cannot grant scientific authority")
    return receipt


def run(
    public_path: Path,
    v3_freeze_path: Path,
    v2_freeze_path: Path,
    identity_receipt_path: Path,
    transport_probe_path: Path,
    transport_response_path: Path,
    out_dir: Path,
) -> dict[str, Any]:
    v3_freeze = v4.load_and_validate_freeze(v3_freeze_path)
    parent = v3_freeze["parent_v2"]
    if v4.git_blob_sha1(v2_freeze_path) != parent["git_blob_sha"]:
        raise ValueError("V3 execution is not bound to the exact frozen V2 parent blob")
    receipt = _validate_v3_transport_bundle(
        transport_probe_path, transport_response_path, v3_freeze
    )

    # The V2 runner owns every scientific/acquisition degree of freedom.  Patch
    # only the crosswalk URL constructor and transport-receipt validator for the
    # duration of the run.  acquire_task_v2 installs build_openaire_crosswalk_url
    # into the V1 acquisition core on each task, so this replacement reaches only
    # the DOI crosswalk call; direct/fallback discovery remains V2/V3 production.
    old_builder = v2.build_openaire_crosswalk_url
    old_validator = v2.validate_transport_probe

    def _v3_builder(dois, *, page_size: int) -> str:
        return v4.build_v4_crosswalk_url(dois, page_size=page_size)

    def _v3_probe_validator(path: Path, _parent_v2_freeze: dict[str, Any]) -> dict[str, Any]:
        if Path(path).resolve() != transport_probe_path.resolve():
            raise ValueError("V3 runner received an unexpected transport receipt path")
        return _validate_v3_transport_bundle(path, transport_response_path, v3_freeze)

    v2.build_openaire_crosswalk_url = _v3_builder
    v2.validate_transport_probe = _v3_probe_validator
    try:
        manifest = v2.run(
            public_path,
            v2_freeze_path,
            identity_receipt_path,
            transport_probe_path,
            out_dir,
        )
    finally:
        v2.build_openaire_crosswalk_url = old_builder
        v2.validate_transport_probe = old_validator

    # Rebind the shared-capture receipt to the V3 protocol. Candidate/acquisition
    # bytes are untouched; only authority/provenance metadata that V2 necessarily
    # wrote with V2 labels is corrected before the artifact is scoreable.
    manifest = dict(manifest)
    manifest["campaign_version"] = 3
    manifest["authority"] = "CANDIDATE_CAPTURE_FROZEN_BEFORE_EVALUATOR_GOLD_V3"
    manifest["parent_v2_freeze_sha256"] = sha256_file(v2_freeze_path)
    manifest["freeze_sha256"] = sha256_file(v3_freeze_path)
    manifest["transport_probe_sha256"] = sha256_file(transport_probe_path)
    manifest["transport_probe_response_sha256"] = sha256_file(transport_response_path)
    manifest["transport_probe_terminal"] = receipt["terminal"]
    manifest["transport_encoding"] = V3_TRANSPORT_ENCODING
    manifest["v3_crosswalk_endpoint"] = v4.V4_ENDPOINT
    manifest["v3_transport_only_change"] = True
    manifest["v3_beta_transport_is_scientific_evidence"] = False
    manifest_path = out_dir / "SHARED_ACQUISITION_MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("P2_WIDE_V3_CAPTURE_TERMINAL=" + json.dumps(manifest, sort_keys=True), flush=True)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public", required=True, type=Path)
    parser.add_argument("--v3-freeze", type=Path, default=DEFAULT_V3_FREEZE)
    parser.add_argument("--v2-freeze", type=Path, default=DEFAULT_V2_FREEZE)
    parser.add_argument("--identity-receipt", type=Path, default=DEFAULT_IDENTITY_RECEIPT)
    parser.add_argument("--transport-probe", required=True, type=Path)
    parser.add_argument("--transport-probe-response", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    run(
        args.public,
        args.v3_freeze,
        args.v2_freeze,
        args.identity_receipt,
        args.transport_probe,
        args.transport_probe_response,
        args.out_dir,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
