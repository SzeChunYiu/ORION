from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Mapping, Sequence

from orion.study.p3_public_reference import canonical_json, validate_case


def _rewrite(value: object, replacements: Mapping[str, str]) -> object:
    if isinstance(value, str):
        for old, new in replacements.items():
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [_rewrite(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: _rewrite(item, replacements) for key, item in value.items()}
    return value


def finalize(cases_path: Path, report_path: Path, replacements: Mapping[str, str]) -> None:
    cases = []
    for line in cases_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        case = _rewrite(json.loads(line), replacements)
        assert isinstance(case, dict)
        validate_case(case)
        rendered = canonical_json(case).decode("utf-8")
        if "/tmp/" in rendered:
            raise ValueError("runner-local /tmp path remains in frozen case provenance")
        cases.append(case)

    raw = b"\n".join(canonical_json(case) for case in cases) + (b"\n" if cases else b"")
    cases_path.write_bytes(raw)

    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["cases_hash"] = hashlib.sha256(raw).hexdigest()
    report["provenance_paths_canonicalized"] = True
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--muse-root", required=True)
    parser.add_argument("--scifact-file", required=True)
    parser.add_argument("--scischema-root", required=True)
    args = parser.parse_args(argv)
    finalize(
        args.cases,
        args.report,
        {
            args.muse_root.rstrip("/") + "/": "dataset/human_Expert_annotations/",
            args.scifact_file: "data/claims_dev.jsonl",
            args.scischema_root.rstrip("/") + "/": "schemas/",
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
