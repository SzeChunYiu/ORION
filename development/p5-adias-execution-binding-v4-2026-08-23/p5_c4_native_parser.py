#!/usr/bin/env python3
"""Outcome-blind structural parser for one ADIAS generation directory.

This parser intentionally does not return native score, success-rate, reward,
progress, or token/cost values.  A structurally complete ADIAS report is an
execution artifact, not a P5 performance claim.  Protected/final-test material
is refused rather than redacted after reading.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "orion.p5.c4.adias-native-terminal.v4"
DOMAINS = {
    "alfworld",
    "taubench_return",
    "taubench_retail",
    "textcraft",
    "webshop",
    "scienceworld",
}
FORBIDDEN_PATH_PART = re.compile(
    r"(^|[_-])(final[_-]?test|protected|gold|holdout|hidden[_-]?test)([_-]|$)",
    re.IGNORECASE,
)
FORBIDDEN_KEYS = {
    "best_selection_score",
    "gold",
    "gold_patch",
    "gold_value",
    "hidden_test",
    "holdout",
    "mean_test_score",
    "mean_test_scores_across_runs",
    "pass_at_k",
    "per_run_test_scores",
    "protected",
    "protected_outcome",
    "protected_score",
    "reference_answer",
    "test_scores",
}


class Refusal(ValueError):
    """Fail-closed parser refusal."""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe_relative_path(root: Path, path: Path) -> str:
    resolved_root = root.resolve()
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise Refusal(f"artifact escapes generation directory: {path}") from exc
    if path.is_symlink() or any(part in {"..", ""} for part in relative.parts):
        raise Refusal(f"unsafe artifact path: {path}")
    if any(FORBIDDEN_PATH_PART.search(part) for part in relative.parts):
        raise Refusal(f"protected/final-test path refused: {relative.as_posix()}")
    return relative.as_posix()


def _load_json(root: Path, path: Path, *, max_bytes: int = 8 * 1024 * 1024) -> Any:
    _safe_relative_path(root, path)
    size = path.stat().st_size
    if size > max_bytes:
        raise Refusal(f"oversized JSON artifact: {path.name} ({size} bytes)")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Refusal(f"invalid JSON artifact {path.name}: {exc}") from exc
    _reject_forbidden_keys(value)
    return value


def _reject_forbidden_keys(value: Any, trail: tuple[str, ...] = ()) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            normalized = str(key).strip().lower()
            if normalized in FORBIDDEN_KEYS or FORBIDDEN_PATH_PART.search(normalized):
                dotted = ".".join((*trail, str(key)))
                raise Refusal(f"protected/final-test key refused: {dotted}")
            _reject_forbidden_keys(nested, (*trail, str(key)))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _reject_forbidden_keys(nested, (*trail, str(index)))


def _finite_unit(value: Any, key: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise Refusal(f"{key} must be numeric")
    if not math.isfinite(float(value)) or not 0.0 <= float(value) <= 1.0:
        raise Refusal(f"{key} must be finite and in [0,1]")


def _nonnegative_int(value: Any, key: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise Refusal(f"{key} must be a nonnegative integer")


def _validate_report(report: Any, domain: str) -> int:
    if not isinstance(report, dict):
        raise Refusal("native report must be an object")
    for key in ("score", "success_rate", "total", "steps", "task_agent_usage"):
        if key not in report:
            raise Refusal(f"native {domain} report missing {key}")
    _finite_unit(report["score"], "score")
    _finite_unit(report["success_rate"], "success_rate")
    _nonnegative_int(report["total"], "total")
    steps = report["steps"]
    if not isinstance(steps, dict) or "total" not in steps or "average" not in steps:
        raise Refusal("native report steps must contain total and average")
    _nonnegative_int(steps["total"], "steps.total")
    if isinstance(steps["average"], bool) or not isinstance(steps["average"], (int, float)):
        raise Refusal("steps.average must be numeric")
    if not math.isfinite(float(steps["average"])) or float(steps["average"]) < 0:
        raise Refusal("steps.average must be finite and nonnegative")
    if not isinstance(report["task_agent_usage"], dict):
        raise Refusal("task_agent_usage must be an object")
    if domain == "alfworld" and report.get("task_type") != "household":
        raise Refusal("alfworld task_type mismatch")
    expected_family = {
        "taubench_return": "retail_return",
        "taubench_retail": "retail",
        "textcraft": "textcraft",
        "webshop": "webshop_text",
        "scienceworld": "scienceworld",
    }.get(domain)
    if expected_family and report.get("task_family") != expected_family:
        raise Refusal(f"{domain} task_family mismatch")
    return report["total"]


def _discover_reports(root: Path) -> list[tuple[str, Path]]:
    found: list[tuple[str, Path]] = []
    for child in sorted(root.iterdir(), key=lambda item: item.name):
        if not child.is_dir() or child.is_symlink():
            continue
        match = re.fullmatch(
            r"(alfworld|taubench_return|taubench_retail|textcraft|webshop|scienceworld)_eval(?:_(train|val))?",
            child.name,
        )
        if not match:
            if FORBIDDEN_PATH_PART.search(child.name):
                raise Refusal(f"protected/final-test directory refused: {child.name}")
            continue
        report_path = child / "report.json"
        if report_path.is_file():
            found.append((match.group(1), report_path))
    return found


def parse_generation(generation_dir: Path, expected_domain: str) -> dict[str, Any]:
    root = generation_dir.resolve()
    if not root.is_dir() or root.is_symlink():
        raise Refusal("generation directory must be a real directory")
    if any(FORBIDDEN_PATH_PART.search(part) for part in root.parts):
        raise Refusal("protected/final-test generation path refused")

    metadata_path = root / "metadata.json"
    if not metadata_path.is_file():
        raise Refusal("native metadata.json is absent")
    metadata = _load_json(root, metadata_path)
    if not isinstance(metadata, dict):
        raise Refusal("metadata.json must be an object")
    for key in ("current_genid", "parent_genid", "run_eval", "valid_parent"):
        if key not in metadata:
            raise Refusal(f"metadata.json missing {key}")
    if not isinstance(metadata["run_eval"], bool) or not isinstance(metadata["valid_parent"], bool):
        raise Refusal("metadata run_eval/valid_parent must be booleans")

    reports = _discover_reports(root)
    report_receipts: list[dict[str, Any]] = []
    nonempty_reports = 0
    for domain, path in reports:
        if domain != expected_domain:
            raise Refusal(f"unexpected report domain {domain}; expected {expected_domain}")
        report = _load_json(root, path)
        total = _validate_report(report, domain)
        nonempty_reports += int(total > 0)
        report_receipts.append(
            {
                "domain": domain,
                "path": _safe_relative_path(root, path),
                "sha256": sha256(path),
                "record_count": total,
                "outcome_values_retained": False,
            }
        )

    compile_status = metadata.get("compile_status")
    compile_failed = (
        isinstance(compile_status, dict) and compile_status.get("ok") is False
    ) or (root / "agent_output" / "compile_failure_diagnosis.json").is_file()

    patch_summary_path = root / "agent_output" / "patch_summary.json"
    patch_summary = None
    if patch_summary_path.is_file():
        patch_summary = _load_json(root, patch_summary_path)
        if not isinstance(patch_summary, dict) or not isinstance(patch_summary.get("has_patch"), bool):
            raise Refusal("patch_summary.json must contain boolean has_patch")

    if compile_failed:
        native_terminal = "NATIVE_COMPILE_FAILURE"
    elif reports and nonempty_reports == 0:
        native_terminal = "NATIVE_EMPTY_EVALUATION"
    elif metadata["run_eval"] and nonempty_reports > 0:
        native_terminal = "NATIVE_EVALUATION_ARTIFACTS_RECORDED"
    elif patch_summary is not None and patch_summary["has_patch"] is False:
        native_terminal = "NATIVE_NO_EFFECTIVE_PATCH"
    else:
        native_terminal = "NATIVE_PARTIAL"

    return {
        "schema_version": SCHEMA_VERSION,
        "arm_id": "C4_ISSUE_CENTRIC_OPTIMIZATION__ADIAS",
        "adapter_terminal": "UNRESOLVED",
        "native_terminal": native_terminal,
        "generation_id": str(metadata["current_genid"]),
        "metadata_sha256": sha256(metadata_path),
        "report_count": len(report_receipts),
        "nonempty_report_count": nonempty_reports,
        "reports": report_receipts,
        "native_exit_status_is_sufficient": False,
        "performance_inference": "FORBIDDEN",
        "raw_native_singleton_licences": 0,
        "source_native_caveat": (
            "ADIAS report structure records an evaluation artifact only; source scores, "
            "valid_parent, and process exit do not establish P5 performance or responsibility."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generation-dir", type=Path, required=True)
    parser.add_argument("--expected-domain", choices=sorted(DOMAINS), required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        result = parse_generation(args.generation_dir, args.expected_domain)
    except Refusal as exc:
        print(json.dumps({"schema_version": SCHEMA_VERSION, "refused": True, "reason": str(exc)}))
        return 2
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
