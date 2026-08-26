"""Reproduce the frozen P3 confirmatory mapping result into a hashed receipt.

The V1 confirmatory analysis remains immutable. This module only *reads* those
artifacts, regenerates the predeclared comparisons, and content-addresses the
reproduction. A missing or drifted gold file is ``CANNOT_CHECK``, never PASS.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from orion.study.p3_public_reference import load_jsonl, sha256_json, summarize
from orion.study.p3_public_reference_confirmatory import analyze_confirmatory
from orion.study.p3_public_reference_publication import generate

REPO_ROOT = Path(__file__).resolve().parents[3]
PAPER03 = REPO_ROOT / "papers" / "orion-13-global-knowledge-portrait"
CONFIRMATORY_GOLD = (
    PAPER03 / "gold" / "adjudicated" / "public-reference-v1.1-confirmatory" / "PUBLIC_REFERENCE_GOLD_V1.jsonl"
)
PRIMARY_GOLD = (
    PAPER03 / "gold" / "adjudicated" / "public-reference-v1" / "PUBLIC_REFERENCE_GOLD_V1.jsonl"
)
FROZEN_ANALYSIS = (
    PAPER03 / "evidence" / "public-reference-v1.1-confirmatory" / "CONFIRMATORY_ANALYSIS.json"
)
PUBLICATION_DIR = PAPER03 / "evidence" / "public-reference-v1.1-confirmatory" / "publication"
RECEIPT_DIR = PAPER03 / "evidence" / "coordinate-obstruction-v2"
RECEIPT_PATH = RECEIPT_DIR / "CONFIRMATORY_REPRODUCTION_RECEIPT.json"

CONFIRMATORY_GOLD_SHA256 = "13a76c68c149c2552f3543babeca6e1ad5afe23c45ea9c0dc365c1445cf2782b"
PRIMARY_GOLD_SHA256 = "35f9e39b75ff53b7f0ec82cd03ebcaaa82509ee0aea3f5b96aac3fd62c854ed8"

FROZEN_CLAIM = {
    "n": 32,
    "orion_false_merge": 0.0,
    "flat_false_merge": 0.1875,
    "false_merge_difference": -0.1875,
    "false_merge_ci95": [-0.34375, -0.0625],
    "false_split_difference": 0.0,
    "false_split_ci95": [0.0, 0.0],
    "primary_verdict": "PASS",
}

SCHEMA_VERSION = "orion.p3.confirmatory-reproduction-receipt.v1"


class GoldUnavailableError(FileNotFoundError):
    """Required frozen gold is missing or drifted; fail closed."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"CANNOT_CHECK: {detail}")
        self.status = "CANNOT_CHECK"
        self.detail = detail


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_gold_file(path: Path, expected_sha256: str) -> Path:
    if not path.is_file():
        raise GoldUnavailableError(f"gold file missing: {path}")
    digest = sha256_file(path)
    if digest != expected_sha256:
        raise GoldUnavailableError(
            f"gold hash mismatch for {path}: got {digest}, expected {expected_sha256}"
        )
    return path


def load_confirmatory_gold() -> list[dict[str, object]]:
    return load_jsonl(require_gold_file(CONFIRMATORY_GOLD, CONFIRMATORY_GOLD_SHA256))


def load_primary_gold() -> list[dict[str, object]]:
    return load_jsonl(require_gold_file(PRIMARY_GOLD, PRIMARY_GOLD_SHA256))


def _as_float_pair(value: Mapping[str, object]) -> tuple[float, float, float]:
    return (
        float(value["candidate_minus_baseline"]),
        float(value["ci95_low"]),
        float(value["ci95_high"]),
    )


def reproduction_checks(analysis: Mapping[str, object], summary: Mapping[str, object]) -> dict[str, object]:
    pooled = analysis["pooled"]
    assert isinstance(pooled, Mapping)
    primary = pooled["primary_comparisons"]
    assert isinstance(primary, Mapping)
    verdict = analysis["confirmatory_verdict"]
    assert isinstance(verdict, Mapping)
    orion = summary["orion"]
    flat = summary["flat_predicate_canonicalization"]
    assert isinstance(orion, Mapping) and isinstance(flat, Mapping)

    fm_point, fm_low, fm_high = _as_float_pair(primary["false_merge_orion_minus_flat"])  # type: ignore[arg-type]
    fs_point, fs_low, fs_high = _as_float_pair(primary["false_split_orion_minus_exact"])  # type: ignore[arg-type]

    mismatches: list[str] = []
    if int(analysis["case_count"]) != FROZEN_CLAIM["n"]:
        mismatches.append(f"n={analysis['case_count']}")
    if float(orion["false_merge_rate"]) != FROZEN_CLAIM["orion_false_merge"]:
        mismatches.append(f"orion_false_merge={orion['false_merge_rate']}")
    if float(flat["false_merge_rate"]) != FROZEN_CLAIM["flat_false_merge"]:
        mismatches.append(f"flat_false_merge={flat['false_merge_rate']}")
    if fm_point != FROZEN_CLAIM["false_merge_difference"]:
        mismatches.append(f"false_merge_difference={fm_point}")
    expected_fm_ci = FROZEN_CLAIM["false_merge_ci95"]
    if [fm_low, fm_high] != expected_fm_ci:
        mismatches.append(f"false_merge_ci95=[{fm_low},{fm_high}]")
    if fs_point != FROZEN_CLAIM["false_split_difference"]:
        mismatches.append(f"false_split_difference={fs_point}")
    expected_fs_ci = FROZEN_CLAIM["false_split_ci95"]
    if [fs_low, fs_high] != expected_fs_ci:
        mismatches.append(f"false_split_ci95=[{fs_low},{fs_high}]")
    if verdict["confirmatory_primary_pass"] is not True:
        mismatches.append("primary_verdict!=PASS")
    return {
        "matched": not mismatches,
        "mismatches": mismatches,
        "observed": {
            "n": int(analysis["case_count"]),
            "orion_false_merge": float(orion["false_merge_rate"]),
            "flat_false_merge": float(flat["false_merge_rate"]),
            "false_merge_difference": fm_point,
            "false_merge_ci95": [fm_low, fm_high],
            "false_split_difference": fs_point,
            "false_split_ci95": [fs_low, fs_high],
            "primary_verdict": "PASS" if verdict["confirmatory_primary_pass"] else "FAIL",
        },
    }


def overlap_report(
    confirmatory: list[dict[str, object]],
    primary: list[dict[str, object]],
) -> dict[str, object]:
    conf_ids = {str(case["case_id"]) for case in confirmatory}
    prim_ids = {str(case["case_id"]) for case in primary}
    overlap_ids = sorted(conf_ids & prim_ids)

    def locators(cases: list[dict[str, object]]) -> set[tuple[str, str, str]]:
        keys: set[tuple[str, str, str]] = set()
        for case in cases:
            for source in case["source_records"]:  # type: ignore[union-attr]
                assert isinstance(source, dict)
                keys.add(
                    (
                        str(source["dataset"]),
                        str(source["locator"]),
                        str(source["content_hash"]),
                    )
                )
        return keys

    locator_overlap = sorted(
        f"{dataset}:{locator}:{digest[:12]}"
        for dataset, locator, digest in (locators(confirmatory) & locators(primary))
    )
    return {
        "confirmatory_n": len(confirmatory),
        "primary_n": len(primary),
        "case_id_overlap": overlap_ids,
        "case_id_overlap_count": len(overlap_ids),
        "source_locator_hash_overlap_count": len(locator_overlap),
        "source_locator_hash_overlap": locator_overlap,
    }


def build_receipt(*, write: bool = False) -> dict[str, object]:
    confirmatory = load_confirmatory_gold()
    primary = load_primary_gold()
    analysis = analyze_confirmatory(confirmatory)
    summary = summarize(confirmatory)
    checks = reproduction_checks(analysis, summary)
    overlap = overlap_report(confirmatory, primary)
    frozen_analysis_sha256 = sha256_file(FROZEN_ANALYSIS) if FROZEN_ANALYSIS.is_file() else "CANNOT_CHECK"
    regenerated_analysis_sha256 = sha256_json(analysis)
    regenerated_summary_sha256 = sha256_json(summary)
    frozen_analysis_canonical_sha256 = (
        sha256_json(json.loads(FROZEN_ANALYSIS.read_text(encoding="utf-8")))
        if FROZEN_ANALYSIS.is_file()
        else "CANNOT_CHECK"
    )

    publication_ok = False
    publication_mismatches: list[str] = []
    if PUBLICATION_DIR.is_dir() and FROZEN_ANALYSIS.is_file():
        frozen = json.loads(FROZEN_ANALYSIS.read_text(encoding="utf-8"))
        tmp = RECEIPT_DIR / "_publication_regen"
        generate(frozen, tmp)
        for name in (
            "PR3-F1_false_merge_by_system.svg",
            "PR3-F2_flat_false_merge_by_case_family.svg",
            "PR3-F3_ablation_false_merge_deltas.svg",
            "PUBLIC_REFERENCE_CONFIRMATORY_TABLES_V1.md",
        ):
            produced = tmp / name
            committed = PUBLICATION_DIR / name
            if not committed.is_file() or not produced.is_file():
                publication_mismatches.append(f"missing:{name}")
                continue
            if sha256_file(produced) != sha256_file(committed):
                publication_mismatches.append(f"hash_mismatch:{name}")
        publication_ok = not publication_mismatches
        for leftover in tmp.glob("*"):
            leftover.unlink()
        tmp.rmdir()

    overlap_clean = overlap["case_id_overlap_count"] == 0
    reproduced = bool(checks["matched"] and overlap_clean)
    receipt: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "protocol_id": "P3.public-reference-mapping.v1.1-confirmatory",
        "reproduction_verdict": "REPRODUCED" if reproduced else "CANNOT_CHECK",
        "v1_confirmatory_immutable": True,
        "claim_boundary": (
            "This receipt restates the frozen confirmatory mapping result. "
            "It does not promote generic schema induction, ontology fusion, or V2 gold."
        ),
        "frozen_claim": FROZEN_CLAIM,
        "gold": {
            "confirmatory_path": str(CONFIRMATORY_GOLD.relative_to(REPO_ROOT)),
            "confirmatory_sha256": CONFIRMATORY_GOLD_SHA256,
            "primary_path": str(PRIMARY_GOLD.relative_to(REPO_ROOT)),
            "primary_sha256": PRIMARY_GOLD_SHA256,
        },
        "regenerated": {
            "analysis_sha256": regenerated_analysis_sha256,
            "summary_sha256": regenerated_summary_sha256,
            "frozen_analysis_sha256": frozen_analysis_sha256,
            "frozen_analysis_canonical_sha256": frozen_analysis_canonical_sha256,
            "frozen_analysis_canonical_match": regenerated_analysis_sha256
            == frozen_analysis_canonical_sha256,
        },
        "checks": checks,
        "overlap": overlap,
        "publication_regeneration": {
            "matched": publication_ok,
            "mismatches": publication_mismatches,
        },
    }
    receipt["receipt_sha256"] = sha256_json({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    if write:
        RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    try:
        receipt = build_receipt(write=True)
    except GoldUnavailableError as exc:
        print(str(exc))
        return 3
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["reproduction_verdict"] == "REPRODUCED" else 3


if __name__ == "__main__":
    raise SystemExit(main())
