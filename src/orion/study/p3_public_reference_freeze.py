from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Mapping, Sequence

from orion.study.p3_public_reference import canonical_json, validate_case

MUSE_REVISION = "f7a40317db46145d0c90b221311d8324db5da1b9"
SCIFACT_REVISION = "68b98a56d93e0f9da0d2aab4e6c3294699a0f72e"
SCISCHEMA_REVISION = "55b6197cdb0b66c3123df16d0b0c70b02c4bde8b"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _rewrite(value: object, replacements: Mapping[str, str]) -> object:
    """Recursively replace machine-local source roots with portable locators."""
    if isinstance(value, str):
        rendered = value
        for old, new in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
            rendered = rendered.replace(old, new)
        return rendered
    if isinstance(value, list):
        return [_rewrite(item, replacements) for item in value]
    if isinstance(value, tuple):
        return [_rewrite(item, replacements) for item in value]
    if isinstance(value, Mapping):
        return {str(key): _rewrite(item, replacements) for key, item in value.items()}
    return value


def _read_cases(path: Path) -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"case line {line_number} is not an object")
        cases.append(value)
    return cases


def freeze_cases(
    *,
    source_cases: Path,
    out_dir: Path,
    muse_root: Path | None = None,
    scifact_claims: Path | None = None,
    scischema_root: Path | None = None,
) -> dict[str, object]:
    """Create the portable, content-addressed public-reference gold artifact."""
    input_bytes = source_cases.read_bytes()
    replacements: dict[str, str] = {}
    normalization_rules: dict[str, str] = {}
    if muse_root is not None:
        replacements[muse_root.as_posix()] = "dataset/human_Expert_annotations"
        normalization_rules["MUSE"] = "dataset/human_Expert_annotations"
    if scifact_claims is not None:
        replacements[scifact_claims.as_posix()] = "data/claims_train.jsonl"
        normalization_rules["SciFact"] = "data/claims_train.jsonl"
    if scischema_root is not None:
        replacements[scischema_root.as_posix()] = "schemas"
        normalization_rules["SciSchema"] = "schemas"

    original = _read_cases(source_cases)
    frozen: list[dict[str, object]] = []
    for case in original:
        rewritten = _rewrite(case, replacements)
        if not isinstance(rewritten, dict):  # pragma: no cover
            raise TypeError("rewritten case is not an object")
        rendered = json.dumps(rewritten, sort_keys=True)
        for local_root in replacements:
            if local_root in rendered:
                raise ValueError(f"machine-local path survived freeze: {local_root}")
        validate_case(rewritten)
        frozen.append(rewritten)

    case_bytes = b"\n".join(canonical_json(case) for case in frozen)
    if case_bytes:
        case_bytes += b"\n"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "PUBLIC_REFERENCE_GOLD_V1.jsonl").write_bytes(case_bytes)

    manifest: dict[str, object] = {
        "schema_version": "orion.p3.public-reference-freeze-manifest.v1",
        "status": "PUBLIC_REFERENCE_GOLD_FROZEN" if frozen else "CANNOT_CHECK",
        "case_count": len(frozen),
        "input_cases_sha256": _sha256(input_bytes),
        "portable_cases_sha256": _sha256(case_bytes),
        "upstream_revisions": {
            "MUSE": MUSE_REVISION,
            "SciFact": SCIFACT_REVISION,
            "SciSchema": SCISCHEMA_REVISION,
        },
        "locator_policy": "upstream-relative path plus immutable revision/content hash",
        "normalization_rules": normalization_rules,
    }
    (out_dir / "PUBLIC_REFERENCE_FREEZE_MANIFEST_V1.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Freeze a portable ORION-P3 public-reference atlas.")
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--muse-root", type=Path)
    parser.add_argument("--scifact-claims", type=Path)
    parser.add_argument("--scischema-root", type=Path)
    args = parser.parse_args(argv)
    manifest = freeze_cases(
        source_cases=args.cases,
        out_dir=args.out,
        muse_root=args.muse_root,
        scifact_claims=args.scifact_claims,
        scischema_root=args.scischema_root,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0 if manifest["status"] == "PUBLIC_REFERENCE_GOLD_FROZEN" else 3


if __name__ == "__main__":
    raise SystemExit(main())
