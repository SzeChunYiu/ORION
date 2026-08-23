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
V2_RUNNER_PATH = HERE / "run_autoresearchbench_wide_openaire_matched_v2.py"
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
v2_runner = _load_module("orion_p2_wide_openaire_runner_v2_for_analysis", V2_RUNNER_PATH)


def _invalid_transport_evidence(error: str, manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "valid": False,
        "manifest_metadata_valid": False,
        "receipt_valid": False,
        "response_valid": False,
        "manifest_probe_sha256": str(manifest.get("transport_probe_sha256") or ""),
        "actual_probe_sha256": None,
        "probe_hash_matches_manifest": False,
        "manifest_response_sha256": str(manifest.get("transport_probe_response_sha256") or ""),
        "actual_response_sha256": None,
        "response_hash_matches_manifest": False,
        "validation_error": error,
    }


def transport_evidence_validity(
    freeze_actual: dict[str, Any],
    manifest: dict[str, Any],
    transport_probe_path: Path,
    transport_response_path: Path,
) -> dict[str, Any]:
    """Revalidate exact pre-benchmark transport receipt and raw response at score time.

    Acquisition must not be the sole authority for the transport prerequisite: the
    evaluator independently checks the archived receipt bytes, archived provider
    response bytes, both manifest hashes, requested structured DOI identity matches,
    and the frozen request/no-gold/non-promotion contract. Invalid evidence remains a
    scientific CANNOT_CHECK input rather than being converted into a zero outcome.
    """
    expected_probe_sha = str(manifest.get("transport_probe_sha256") or "")
    expected_response_sha = str(manifest.get("transport_probe_response_sha256") or "")
    actual_probe_sha: str | None = None
    actual_response_sha: str | None = None
    receipt_valid = False
    response_valid = False
    validation_errors: list[str] = []
    probe: dict[str, Any] | None = None
    try:
        actual_probe_sha = v2_runner.sha256_file(transport_probe_path)
        probe = v2_runner.validate_transport_probe(transport_probe_path, freeze_actual)
        receipt_valid = True
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        validation_errors.append(f"receipt:{type(exc).__name__}: {exc}")
    if probe is not None:
        try:
            actual_response_sha = v2_runner.sha256_file(transport_response_path)
            v2_runner.validate_transport_response(transport_response_path, probe, freeze_actual)
            response_valid = True
        except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
            validation_errors.append(f"response:{type(exc).__name__}: {exc}")

    probe_hash_matches = bool(
        expected_probe_sha and actual_probe_sha and expected_probe_sha == actual_probe_sha
    )
    response_hash_matches = bool(
        expected_response_sha
        and actual_response_sha
        and expected_response_sha == actual_response_sha
        and probe is not None
        and probe.get("response_sha256") == actual_response_sha
    )
    metadata_valid = (
        int(manifest.get("campaign_version", 0)) == 2
        and manifest.get("transport_encoding") == "repeated_pid_parameters"
        and manifest.get("transport_probe_terminal") == PROBE_TERMINAL
        and bool(expected_response_sha)
    )
    return {
        "valid": bool(
            metadata_valid
            and receipt_valid
            and response_valid
            and probe_hash_matches
            and response_hash_matches
        ),
        "manifest_metadata_valid": metadata_valid,
        "receipt_valid": receipt_valid,
        "response_valid": response_valid,
        "manifest_probe_sha256": expected_probe_sha,
        "actual_probe_sha256": actual_probe_sha,
        "probe_hash_matches_manifest": probe_hash_matches,
        "manifest_response_sha256": expected_response_sha,
        "actual_response_sha256": actual_response_sha,
        "response_hash_matches_manifest": response_hash_matches,
        "validation_error": "; ".join(validation_errors) if validation_errors else None,
    }


def discover_transport_probe_bundle(manifest_path: Path) -> tuple[Path, Path]:
    """Find the one archived receipt/raw-response pair inside the capture boundary.

    Artifact extraction may place the pair either beside the manifest or one directory
    above its capture directory. Searching beyond that boundary risks importing a
    sibling run/test bundle into score-time authority, so wider ancestor fallback is
    deliberately forbidden.
    """
    checked: set[Path] = set()
    for root in (manifest_path.parent, manifest_path.parent.parent):
        root = root.resolve()
        if root in checked or not root.exists():
            continue
        checked.add(root)
        probes = sorted(path for path in root.rglob("transport_probe.json") if path.is_file())
        responses = sorted(
            path for path in root.rglob("transport_probe_response.json") if path.is_file()
        )
        if len(probes) > 1 or len(responses) > 1:
            raise ValueError(
                f"ambiguous archived transport bundle under {root}: "
                f"receipts={len(probes)} responses={len(responses)}"
            )
        if len(probes) == 1 and len(responses) == 1:
            if probes[0].parent != responses[0].parent:
                raise ValueError("archived transport receipt and response are not co-located")
            return probes[0], responses[0]
    raise ValueError("archived transport receipt/response bundle not found near capture manifest")


def resolve_transport_evidence(
    freeze_actual: dict[str, Any],
    manifest: dict[str, Any],
    manifest_path: Path,
    probe_arg: object,
    response_arg: object = None,
) -> dict[str, Any]:
    """Resolve score-time custody without allowing absent evidence to crash authority."""
    if probe_arg is not None:
        probe_path = Path(probe_arg)
        response_path = (
            Path(response_arg)
            if response_arg is not None
            else probe_path.with_name("transport_probe_response.json")
        )
        return transport_evidence_validity(
            freeze_actual, manifest, probe_path, response_path
        )
    try:
        probe_path, response_path = discover_transport_probe_bundle(manifest_path)
    except (OSError, ValueError, TypeError) as exc:
        return _invalid_transport_evidence(f"{type(exc).__name__}: {exc}", manifest)
    return transport_evidence_validity(
        freeze_actual, manifest, probe_path, response_path
    )


def analyze_v2(**kwargs: Any) -> dict[str, Any]:
    freeze_path = Path(kwargs["freeze_path"])
    manifest_path = Path(kwargs["manifest_path"])
    probe_arg = kwargs.pop("transport_probe_path", None)
    response_arg = kwargs.pop("transport_probe_response_path", None)
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
    transport = resolve_transport_evidence(
        freeze_actual, manifest, manifest_path, probe_arg, response_arg
    )
    transport_valid = bool(transport["valid"])
    result["schema_version"] = "orion.p2.wide-openaire-matched-result.v2"
    result["campaign_version"] = 2
    result["authority"] = "PINNED_OFFICIAL_WIDE_PLUS_PROSPECTIVE_PAIRED_ANALYSIS_V2"
    result["validity"]["v2_repeated_pid_transport_probe"] = transport_valid
    result["validity"]["v2_transport_encoding"] = manifest.get("transport_encoding")
    result["validity"]["v2_transport_probe_sha256"] = manifest.get("transport_probe_sha256")
    result["validity"]["v2_transport_probe_actual_sha256"] = transport["actual_probe_sha256"]
    result["validity"]["v2_transport_probe_hash_matches_manifest"] = transport[
        "probe_hash_matches_manifest"
    ]
    result["validity"]["v2_transport_probe_receipt_valid"] = transport["receipt_valid"]
    result["validity"]["v2_transport_probe_response_sha256"] = manifest.get(
        "transport_probe_response_sha256"
    )
    result["validity"]["v2_transport_probe_response_actual_sha256"] = transport[
        "actual_response_sha256"
    ]
    result["validity"]["v2_transport_probe_response_hash_matches_manifest"] = transport[
        "response_hash_matches_manifest"
    ]
    result["validity"]["v2_transport_probe_response_valid"] = transport["response_valid"]
    result["validity"]["v2_transport_probe_validation_error"] = transport["validation_error"]
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
    parser.add_argument("--transport-probe", type=Path)
    parser.add_argument("--transport-probe-response", type=Path)
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
        transport_probe_path=args.transport_probe,
        transport_probe_response_path=args.transport_probe_response,
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
