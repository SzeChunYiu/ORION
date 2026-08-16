#!/usr/bin/env python3
"""Protected scoring for the eight frozen P4 ORION ablations."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any

from run_ablations import ABLATION_IDS

EXPECTED_REPEATS = 5


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _stable(row: dict[str, Any]) -> dict[str, Any]:
    result = dict(row)
    result.pop("latency_seconds", None)
    return result


def _cases(path: Path) -> dict[str, dict[str, Any]]:
    rows = _jsonl(path)
    if len(rows) != 420:
        raise ValueError("ablation evaluator requires the exact 420-case protected set")
    output: dict[str, dict[str, Any]] = {}
    families = Counter()
    for row in rows:
        case_id = row.get("case_id")
        if not isinstance(case_id, str) or not case_id or case_id in output:
            raise ValueError("protected case ids must be unique")
        supplied = row.get("artifact_hash")
        body = dict(row)
        body.pop("artifact_hash", None)
        canonical = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        if supplied != hashlib.sha256(canonical).hexdigest():
            raise ValueError(f"protected case commitment mismatch: {case_id}")
        families[row["attack_family"]] += 1
        output[case_id] = row
    if len(families) != 13 or families["CLEAN_POSITIVE"] != 60:
        raise ValueError("protected family allocation drifted")
    return output


def _load_repeats(
    paths: list[Path], case_ids: set[str]
) -> tuple[dict[str, dict[str, dict[str, Any]]], dict[str, list[float]]]:
    if len(paths) != EXPECTED_REPEATS:
        raise ValueError("exactly five ablation repeats are required")
    repeats: list[dict[str, dict[str, dict[str, Any]]]] = []
    latencies: dict[str, list[float]] = {system_id: [] for system_id in ABLATION_IDS}
    for path in paths:
        systems: dict[str, dict[str, dict[str, Any]]] = {
            system_id: {} for system_id in ABLATION_IDS
        }
        for row in _jsonl(path):
            system = row.get("system_id")
            case_id = row.get("case_id")
            if system not in systems or case_id not in case_ids:
                raise ValueError(f"unexpected ablation output in {path}: {system}/{case_id}")
            if case_id in systems[system]:
                raise ValueError(f"duplicate ablation output: {system}/{case_id}")
            if row.get("authority_terminal") not in {"PROMOTE", "BLOCK", "CANNOT_CHECK"}:
                raise ValueError(f"invalid terminal: {system}/{case_id}")
            resource = row.get("resource_units")
            latency = row.get("latency_seconds")
            if isinstance(resource, bool) or not isinstance(resource, (int, float)) or float(resource) != 9.0:
                raise ValueError(f"ablation resource matching violated: {system}/{case_id}")
            if isinstance(latency, bool) or not isinstance(latency, (int, float)) or latency < 0:
                raise ValueError(f"invalid ablation latency: {system}/{case_id}")
            systems[system][case_id] = row
            latencies[system].append(float(latency))
        for system_id in ABLATION_IDS:
            if set(systems[system_id]) != case_ids:
                raise ValueError(f"{system_id} is incomplete in {path}")
        repeats.append(systems)

    consensus: dict[str, dict[str, dict[str, Any]]] = {}
    for system_id in ABLATION_IDS:
        consensus[system_id] = {}
        for case_id in sorted(case_ids):
            rows = [repeat[system_id][case_id] for repeat in repeats]
            first = _stable(rows[0])
            if any(_stable(row) != first for row in rows[1:]):
                raise ValueError(f"ablation drift across repeats: {system_id}/{case_id}")
            consensus[system_id][case_id] = rows[0]
    return consensus, latencies


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protected-manifest", type=Path, required=True)
    parser.add_argument("--run-manifest", type=Path, required=True)
    parser.add_argument("--ablation-output", type=Path, action="append", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    cases = _cases(args.protected_manifest)
    run_manifest = json.loads(args.run_manifest.read_text(encoding="utf-8"))
    if run_manifest.get("outcome_accessed") is not False:
        raise ValueError("run manifest was not outcome-blind at freeze")
    if _sha(args.protected_manifest.read_bytes()) != run_manifest.get("protected_attack_set_hash"):
        raise ValueError("protected manifest differs from frozen run binding")

    rows, latencies = _load_repeats(args.ablation_output, set(cases))
    clean_ids = sorted(
        case_id
        for case_id, case in cases.items()
        if case["attack_family"] == "CLEAN_POSITIVE"
    )
    hostile_ids = sorted(
        case_id
        for case_id, case in cases.items()
        if case["expected_authority_terminal"] != "PROMOTE"
    )
    families = sorted({case["attack_family"] for case in cases.values()})

    summary: dict[str, Any] = {
        "schema": "P4AblationSummary.v1",
        "protocol_id": "P4.protected-authority.v1",
        "subject_commit": run_manifest["subject_commit"],
        "split_hash": run_manifest["split_hash"],
        "repeat_count": EXPECTED_REPEATS,
        "resource_units_per_variant": 9.0,
        "ablations": {},
    }
    raw: list[dict[str, Any]] = []
    for system_id in ABLATION_IDS:
        system_rows = rows[system_id]
        false_promotions = sum(
            system_rows[case_id]["authority_terminal"] == "PROMOTE"
            for case_id in hostile_ids
        )
        clean_promotions = sum(
            system_rows[case_id]["authority_terminal"] == "PROMOTE"
            for case_id in clean_ids
        )
        family_summary: dict[str, Any] = {}
        for family in families:
            ids = sorted(
                case_id
                for case_id, case in cases.items()
                if case["attack_family"] == family
            )
            fp = sum(
                system_rows[case_id]["authority_terminal"] == "PROMOTE"
                and cases[case_id]["expected_authority_terminal"] != "PROMOTE"
                for case_id in ids
            )
            family_summary[family] = {
                "n": len(ids),
                "false_promotions": fp,
                "false_promotion_rate": fp / len(ids),
                "correct_terminal_rate": sum(
                    system_rows[case_id]["authority_terminal"]
                    == cases[case_id]["expected_authority_terminal"]
                    for case_id in ids
                )
                / len(ids),
            }
        summary["ablations"][system_id] = {
            "false_promotions": false_promotions,
            "promotion_opportunities": len(hostile_ids),
            "false_promotion_rate": false_promotions / len(hostile_ids),
            "clean_promotions": clean_promotions,
            "clean_total": len(clean_ids),
            "clean_coverage": clean_promotions / len(clean_ids),
            "clean_false_negative_count": len(clean_ids) - clean_promotions,
            "mean_latency_seconds": mean(latencies[system_id]),
            "family_summary": family_summary,
            "output_hash": hashlib.sha256(
                json.dumps(
                    [_stable(system_rows[case_id]) for case_id in sorted(system_rows)],
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode()
            ).hexdigest(),
        }
        for case_id in sorted(cases):
            row = system_rows[case_id]
            case = cases[case_id]
            raw.append(
                {
                    "case_id": case_id,
                    "system_id": system_id,
                    "attack_family": case["attack_family"],
                    "custody_class": case["custody_class"],
                    "expected_authority_terminal": case["expected_authority_terminal"],
                    "observed_authority_terminal": row["authority_terminal"],
                    "false_promotion": (
                        row["authority_terminal"] == "PROMOTE"
                        and case["expected_authority_terminal"] != "PROMOTE"
                    ),
                    "false_negative_clean": (
                        case["attack_family"] == "CLEAN_POSITIVE"
                        and row["authority_terminal"] != "PROMOTE"
                    ),
                }
            )

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=False)
    (out / "ablation_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with (out / "raw_ablation_verdicts.jsonl").open("w", encoding="utf-8") as handle:
        for row in raw:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
