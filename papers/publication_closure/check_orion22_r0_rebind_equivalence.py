#!/usr/bin/env python3
"""Bridge pre-R0 ORION-22/P12 evidence bindings to the unified namespace.

This checker does not rewrite historical authority files and grants no new
scientific authority.  It proves that any raw SHA-256 mismatch accepted here is
explained exactly by the repository's R0 namespace-only rebind, then runs the
existing lifecycle and stop/go semantic audits against the reverse-normalized
bytes.  Current live bytes are separately checked against the paper's current
SHA256SUMS.

Fail closed: any mismatch that cannot be reduced to the allowed R0 token map is
an error and must reopen scientific/evidence verification.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "papers/orion-22-adaptive-state-reasoning"
V4 = PAPER / "P12_ACTIVE_CLAIM_AUTHORITY_V4.json"
V5 = PAPER / "P12_ACTIVE_CLAIM_AUTHORITY_V5.json"
SUMS = PAPER / "SHA256SUMS"
MANIFEST = PAPER / "CONTENT_MANIFEST_V1.json"

# Exact reverse map for the R0 paper-namespace unification.  These are naming
# substitutions only; numerical values, terminals, protocol ids, dates, run ids
# and scientific prose outside these identifiers are not normalized.
R0_REVERSE_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("papers/orion-22-adaptive-state-reasoning", "papers/paper-12-adaptive-state-reasoning"),
    ("orion-22-adaptive-state-reasoning", "paper-12-adaptive-state-reasoning"),
    ("ORION-22", "P12"),
    ("ORION-19", "P9"),
    ("ORION-16", "P6"),
)


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _actual_sha(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


def _reverse_r0_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw
    for current, historical in R0_REVERSE_REPLACEMENTS:
        text = text.replace(current, historical)
    return text.encode("utf-8")


def _reverse_r0_sha(path: Path) -> str:
    return _sha_bytes(_reverse_r0_bytes(path))


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _collect_declared_bindings(*documents: dict[str, Any]) -> dict[Path, set[str]]:
    out: dict[Path, set[str]] = {}
    for document in documents:
        bindings = document.get("evidence_bindings", {})
        if not isinstance(bindings, dict):
            continue
        for item in bindings.values():
            if not isinstance(item, dict):
                continue
            artifact = item.get("artifact")
            digest = item.get("sha256")
            if isinstance(artifact, str) and isinstance(digest, str):
                out.setdefault(ROOT / artifact, set()).add(digest)
    return out


def _validate_current_sums(errors: list[str]) -> tuple[int, int]:
    parsed = 0
    checked = 0
    declared: dict[str, str] = {}
    try:
        lines = SUMS.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        errors.append(f"cannot read current SHA256SUMS: {exc}")
        return 0, 0
    for line in lines:
        if not line.strip():
            continue
        try:
            digest, rel = line.split("  ", 1)
        except ValueError:
            errors.append(f"malformed SHA256SUMS line: {line!r}")
            continue
        parsed += 1
        declared[rel] = digest
        target = ROOT / rel
        if not target.is_file():
            errors.append(f"SHA256SUMS target missing: {rel}")
            continue
        checked += 1
        observed = _actual_sha(target)
        if observed != digest:
            errors.append(
                f"current SHA256SUMS mismatch: {rel}: expected={digest} observed={observed}"
            )

    try:
        manifest = _load_json(MANIFEST)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"cannot parse current content manifest: {exc}")
        return parsed, checked
    bound_files = manifest.get("bound_files", [])
    if not isinstance(bound_files, list):
        errors.append("CONTENT_MANIFEST_V1 bound_files must be an array")
        return parsed, checked
    for item in bound_files:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            errors.append("CONTENT_MANIFEST_V1 contains malformed bound_files entry")
            continue
        rel = item["path"]
        if rel not in declared:
            errors.append(f"content manifest path missing from current SHA256SUMS: {rel}")
    return parsed, checked


def main() -> int:
    errors: list[str] = []
    bridged: list[dict[str, str]] = []

    try:
        v4 = _load_json(V4)
        v5 = _load_json(V5)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAIL", "errors": [str(exc)]}, indent=2))
        return 1

    lifecycle = _load_module(
        "orion22_lifecycle_v4_bridge",
        PAPER / "check_p12_lifecycle_integration_v4.py",
    )
    stopgo = _load_module(
        "orion22_stopgo_v1_bridge",
        PAPER / "check_p12_stopgo_integration_v1.py",
    )

    declared_by_path = _collect_declared_bindings(v4, v5)
    for artifact, (digest, _terminal) in stopgo.PRIOR_BINDINGS.items():
        declared_by_path.setdefault(ROOT / artifact, set()).add(digest)

    # First prove each non-current historical binding is exactly R0-equivalent.
    for path, declared_digests in sorted(
        declared_by_path.items(), key=lambda item: str(item[0])
    ):
        if not path.is_file():
            errors.append(f"bound artifact missing: {path.relative_to(ROOT)}")
            continue
        actual = _actual_sha(path)
        if actual in declared_digests:
            continue
        reverse = _reverse_r0_sha(path)
        if reverse not in declared_digests:
            errors.append(
                "non-R0 evidence drift: "
                f"{path.relative_to(ROOT)} actual={actual} reverse_r0={reverse} "
                f"declared={sorted(declared_digests)}"
            )
            continue
        bridged.append(
            {
                "artifact": str(path.relative_to(ROOT)),
                "current_sha256": actual,
                "historical_declared_sha256": reverse,
                "equivalence": "R0_NAMESPACE_ONLY_REVERSE_NORMALIZATION",
            }
        )

    def compat_sha(path_like: Path) -> str:
        path = Path(path_like)
        actual = _actual_sha(path)
        declared = declared_by_path.get(path, set())
        if not declared or actual in declared:
            return actual
        reverse = _reverse_r0_sha(path)
        if reverse in declared:
            return reverse
        return actual

    # Run the original semantic gates without their package-level raw-digest
    # check.  Current package byte integrity is verified separately below.
    lifecycle._sha = compat_sha
    lifecycle_report = lifecycle.audit(check_package=False)
    if lifecycle_report.get("status") != "PASS":
        errors.extend(
            f"lifecycle: {item}" for item in lifecycle_report.get("errors", [])
        )

    stopgo._sha = compat_sha
    stopgo_report = stopgo.audit(check_package=False)
    if stopgo_report.get("status") != "PASS":
        errors.extend(f"stopgo: {item}" for item in stopgo_report.get("errors", []))

    sums_parsed, sums_checked = _validate_current_sums(errors)

    report = {
        "schema": "ORION22.R0RebindEquivalenceBridge.v1",
        "status": "PASS" if not errors else "FAIL",
        "scientific_authority_delta": "NONE",
        "external_validation": "CANNOT_CHECK",
        "historical_authority_policy": "PRESERVE_V4_V5_BYTES_DO_NOT_REWRITE_HISTORY",
        "bridge_scope": "R0_NAMESPACE_ONLY",
        "bridged_binding_count": len(bridged),
        "bridged_bindings": bridged,
        "current_sha256sums_parsed": sums_parsed,
        "current_sha256sums_checked": sums_checked,
        "lifecycle_semantic_status": lifecycle_report.get("status"),
        "stopgo_semantic_status": stopgo_report.get("status"),
        "errors": errors,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
