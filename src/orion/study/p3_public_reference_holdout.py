from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from orion.study.p3_public_reference import canonical_json, load_jsonl, validate_case
from orion.study.p3_public_reference_build import (
    muse_coreference_cases,
    scifact_claim_cases,
    scischema_identity_cases,
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _balanced_window(
    pools: Mapping[str, Sequence[dict[str, object]]], *, offset: int, total: int
) -> list[dict[str, object]]:
    """Take a deterministic window from the same outcome-blind round-robin order.

    `offset=32,total=32` is therefore disjoint from the original first-32 atlas
    without inspecting any system output or expected relation during selection.
    """
    if offset < 0 or total < 0:
        raise ValueError("offset and total must be non-negative")
    ordered_names = sorted(pools)
    positions = {name: 0 for name in ordered_names}
    seen = 0
    chosen: list[dict[str, object]] = []
    target_end = offset + total
    while seen < target_end:
        progressed = False
        for name in ordered_names:
            seq = pools[name]
            pos = positions[name]
            if pos >= len(seq):
                continue
            case = seq[pos]
            positions[name] += 1
            if seen >= offset:
                chosen.append(case)
            seen += 1
            progressed = True
            if seen >= target_end:
                break
        if not progressed:
            break
    return chosen


def build_holdout(
    *,
    muse_root: Path | None,
    scifact_claims: Path | None,
    scischema_root: Path | None,
    exclude_cases: Path,
    offset: int = 32,
    target_n: int = 32,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    pools: dict[str, list[dict[str, object]]] = {}
    if muse_root is not None:
        pools["MUSE"] = muse_coreference_cases(muse_root)
    if scifact_claims is not None:
        pools["SciFact"] = scifact_claim_cases(scifact_claims)
    if scischema_root is not None:
        pools["SciSchema"] = scischema_identity_cases(scischema_root)

    excluded = load_jsonl(exclude_cases)
    excluded_ids = {str(case["case_id"]) for case in excluded}
    chosen = _balanced_window(pools, offset=offset, total=target_n)
    overlap = sorted(str(case["case_id"]) for case in chosen if str(case["case_id"]) in excluded_ids)

    for case in chosen:
        validate_case(case)

    disciplines = sorted({str(case["discipline"]) for case in chosen})
    families = sorted({str(case["case_family"]) for case in chosen})
    authorities = sorted({str(case["expected"]["authority"]["kind"]) for case in chosen})
    relations = sorted({str(case["expected"]["meaning_relation"]) for case in chosen})
    has_merge = "COMPATIBLE" in relations
    has_nonmerge = any(value != "COMPATIBLE" for value in relations)
    ready = (
        len(chosen) == target_n
        and not overlap
        and len(disciplines) >= 3
        and len(families) >= 2
        and has_merge
        and has_nonmerge
    )

    rendered = b"\n".join(canonical_json(case) for case in chosen)
    if rendered:
        rendered += b"\n"
    report: dict[str, object] = {
        "schema_version": "orion.p3.public-reference-confirmatory-holdout-report.v1",
        "status": "READY_FOR_CONFIRMATORY_FREEZE" if ready else "CANNOT_CHECK",
        "selection_rule": "outcome-blind round-robin window",
        "selection_offset": offset,
        "target_n": target_n,
        "built_n": len(chosen),
        "excluded_primary_n": len(excluded),
        "overlap_count": len(overlap),
        "overlap_case_ids": overlap,
        "pool_counts": {name: len(records) for name, records in sorted(pools.items())},
        "disciplines": disciplines,
        "case_families": families,
        "authority_kinds": authorities,
        "expected_relations": relations,
        "cases_sha256": _sha256(rendered) if chosen else None,
        "blockers": [],
    }
    blockers = report["blockers"]
    assert isinstance(blockers, list)
    if len(chosen) != target_n:
        blockers.append(f"holdout produced {len(chosen)} cases, expected {target_n}")
    if overlap:
        blockers.append(f"holdout overlaps primary atlas on {len(overlap)} case ids")
    if len(disciplines) < 3:
        blockers.append(f"only {len(disciplines)} strata available; need at least 3")
    if len(families) < 2:
        blockers.append(f"only {len(families)} case families available; need at least 2")
    if not has_merge or not has_nonmerge:
        blockers.append("holdout must contain both merge-compatible and non-merge cases")
    return chosen, report


def write_jsonl(path: Path, cases: Iterable[Mapping[str, object]]) -> None:
    rendered = b"\n".join(canonical_json(case) for case in cases)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(rendered + (b"\n" if rendered else b""))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Freeze candidate cases for a disjoint P3 confirmatory holdout.")
    parser.add_argument("--muse-root", type=Path)
    parser.add_argument("--scifact-claims", type=Path)
    parser.add_argument("--scischema-root", type=Path)
    parser.add_argument("--exclude-cases", required=True, type=Path)
    parser.add_argument("--offset", type=int, default=32)
    parser.add_argument("--target-n", type=int, default=32)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    cases, report = build_holdout(
        muse_root=args.muse_root,
        scifact_claims=args.scifact_claims,
        scischema_root=args.scischema_root,
        exclude_cases=args.exclude_cases,
        offset=args.offset,
        target_n=args.target_n,
    )
    args.out.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out / "cases.jsonl", cases)
    (args.out / "HOLDOUT_BUILD_REPORT.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "READY_FOR_CONFIRMATORY_FREEZE" else 3


if __name__ == "__main__":
    raise SystemExit(main())
