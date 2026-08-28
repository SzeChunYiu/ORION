#!/usr/bin/env python3
"""Guarded local-control and batch execution entry point for NQ Engine B."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import batch_engine_b as batch
import engine_b as eb


def build_fixture_receipt(*, source_manifest_sha256: str) -> dict[str, object]:
    if not batch.SHA256.fullmatch(source_manifest_sha256):
        raise ValueError("source manifest digest is invalid")
    e1 = eb.encode_element((1, 0, 0))
    positive = (e1, eb.negate(e1), e1, eb.negate(e1))
    negative = (e1, eb.negate(e1), e1)
    positive_model = eb.solve_cnf_dpll(eb.build_factorization_cnf(positive, 2).cnf)
    negative_model = eb.solve_cnf_dpll(eb.build_factorization_cnf(negative, 2).cnf)
    checks = {
        "all_125_elements_round_trip": all(
            eb.encode_element(eb.decode_element(element)) == element
            for element in eb.GROUP_ELEMENTS
        ),
        "primitive_inverse_law": all(
            eb.add(element, eb.negate(element)) == eb.ZERO for element in eb.GROUP_ELEMENTS
        ),
        "positive_control_sat": positive_model is not None,
        "negative_control_unsat": negative_model is None,
        "positive_matches_slow_reference": eb.has_k_disjoint_zero_sums_bruteforce(positive, 2),
        "negative_matches_slow_reference": not eb.has_k_disjoint_zero_sums_bruteforce(negative, 2),
    }
    if not all(checks.values()):
        raise RuntimeError("an Engine B non-outcome control failed")
    return batch.seal_receipt(
        {
            "terminal": "NQ_ENGINE_B_NON_OUTCOME_FIXTURES_VALIDATED",
            "checks": checks,
            "full_scientific_execution": "NOT_RUN",
            "lunarc_submission": "NOT_SUBMITTED",
            "d4_c5_cubed": "OPEN",
            "full_strata_closed": False,
            "blinded_independence": "NOT_CLAIMED",
            "blinding_disclosure": "PUBLIC_PROGRAMME_EXPECTED_OUTCOMES_EXPOSED",
        },
        {"source_manifest_sha256": source_manifest_sha256},
    )


def write_json_atomic(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, path)


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("fixtures", "execute"), required=True)
    parser.add_argument("--subject-commit", required=True)
    parser.add_argument("--source-manifest", type=Path, default=root / "SOURCE_MANIFEST.json")
    parser.add_argument("--input-root", type=Path)
    parser.add_argument("--input-manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--certificates", type=Path)
    parser.add_argument("--proof-root", type=Path)
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--max-wall-seconds", type=int, default=82_800)
    parser.add_argument("--solver", default="g4")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.subject_commit != eb.SUBJECT_COMMIT:
        raise SystemExit("subject commit mismatch")
    source_manifest = json.loads(args.source_manifest.read_text())
    source_digest = source_manifest["manifest_sha256"]
    if args.mode == "fixtures":
        receipt = build_fixture_receipt(source_manifest_sha256=source_digest)
    else:
        if not all((args.input_root, args.input_manifest, args.certificates, args.proof_root)):
            raise SystemExit("execute mode requires input and certificate paths")
        input_manifest = json.loads(args.input_manifest.read_text())
        bundle = batch.verify_input_manifest(args.input_root, input_manifest)
        try:
            payload = batch.execute_bundle(
                bundle,
                certificates_path=args.certificates,
                proof_root=args.proof_root,
                threads=args.threads,
                max_wall_seconds=args.max_wall_seconds,
                solver_name=args.solver,
            )
            receipt = batch.seal_receipt(
                payload,
                {
                    "source_manifest_sha256": source_digest,
                    "input_manifest_sha256": bundle.manifest_sha256,
                },
            )
        except batch.ResourceBound as error:
            receipt = batch.build_resource_bound_receipt(
                source_manifest_sha256=source_digest,
                input_manifest_sha256=bundle.manifest_sha256,
                processed_records=0,
                total_records=bundle.record_count,
                reason=str(error),
            )
        except batch.SolverEnvironmentUnavailable as error:
            receipt = batch.build_environment_receipt(
                source_manifest_sha256=source_digest,
                input_manifest_sha256=bundle.manifest_sha256,
                total_records=bundle.record_count,
                reason=str(error),
            )
    write_json_atomic(args.output, receipt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
