#!/usr/bin/env python3
"""Apply the frozen Wide V2 analysis without changing V1 scientific statistics."""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
V1_PATH = HERE / "analyze_autoresearchbench_wide_openaire_matched.py"
V2_SCHEMA = "orion.p2.wide-openaire-matched-freeze.v2"
V1_SCHEMA = "orion.p2.wide-openaire-matched-freeze.v1"
PROBE_TERMINAL = "OPENAIRE_REPEATED_PID_TRANSPORT_VALID"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module at {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


v1 = _load_module("orion_p2_wide_openaire_analysis_v1_for_v2", V1_PATH)


def analyze_v2(**kwargs: Any) -> dict[str, Any]:
    freeze_path = Path(kwargs["freeze_path"])
    manifest_path = Path(kwargs["manifest_path"])
    output_path = Path(kwargs["output_path"])
    freeze_actual = json.loads(freeze_path.read_text(encoding="utf-8"))
    if freeze_actual.get("schema_version") != V2_SCHEMA:
        raise ValueError("unexpected Wide V2 freeze schema")

    original_load_json = v1.load_json

    def load_json_compatible(path: Path) -> dict[str, Any]:
        value = original_load_json(path)
        if Path(path) == freeze_path:
            value = copy.deepcopy(value)
            value["schema_version"] = V1_SCHEMA
        return value

    v1.load_json = load_json_compatible
    try:
        result = v1.analyze(**kwargs)
    finally:
        v1.load_json = original_load_json

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    transport_valid = (
        int(manifest.get("campaign_version", 0)) == 2
        and manifest.get("transport_encoding") == "repeated_pid_parameters"
        and manifest.get("transport_probe_terminal") == PROBE_TERMINAL
        and bool(manifest.get("transport_probe_sha256"))
    )
    result["schema_version"] = "orion.p2.wide-openaire-matched-result.v2"
    result["campaign_version"] = 2
    result["authority"] = "PINNED_OFFICIAL_WIDE_PLUS_PROSPECTIVE_PAIRED_ANALYSIS_V2"
    result["validity"]["v2_repeated_pid_transport_probe"] = transport_valid
    result["validity"]["v2_transport_encoding"] = manifest.get("transport_encoding")
    result["validity"]["v2_transport_probe_sha256"] = manifest.get("transport_probe_sha256")
    result["all_validity_conditions"] = bool(result["all_validity_conditions"] and transport_valid)
    if not result["all_validity_conditions"]:
        result["terminal"] = freeze_actual["terminal_rule"]["invalid_or_transport_terminal"]
    elif result["scientific_supported"]:
        result["terminal"] = freeze_actual["terminal_rule"]["positive_terminal"]
    else:
        result["terminal"] = freeze_actual["terminal_rule"]["negative_valid_terminal"]
    result["claim_boundary"] = freeze_actual["claim_boundary"]
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("P2_WIDE_OPENAIRE_MATCHED_V2=" + json.dumps(result, sort_keys=True), flush=True)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--baseline-eval", required=True, type=Path)
    parser.add_argument("--orion-eval", required=True, type=Path)
    parser.add_argument("--diagnostic-eval", required=True, type=Path)
    parser.add_argument("--baseline-candidate", required=True, type=Path)
    parser.add_argument("--orion-candidate", required=True, type=Path)
    parser.add_argument("--diagnostic-candidate", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    analyze_v2(
        freeze_path=args.freeze,
        manifest_path=args.manifest,
        baseline_eval_path=args.baseline_eval,
        orion_eval_path=args.orion_eval,
        diagnostic_eval_path=args.diagnostic_eval,
        baseline_candidate_path=args.baseline_candidate,
        orion_candidate_path=args.orion_candidate,
        diagnostic_candidate_path=args.diagnostic_candidate,
        output_path=args.output,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
