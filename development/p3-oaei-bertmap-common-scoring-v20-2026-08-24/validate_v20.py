#!/usr/bin/env python3
"""Read-only validation of immutable P3 V20 artifacts."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    result = json.loads((ROOT / "BERTMAP_RESULT_V20.json").read_text())
    preflight = json.loads((ROOT / "RUNTIME_PREFLIGHT_V20.json").read_text())
    checks = [
        preflight["native_execution_authorized"] is True,
        preflight["checks_passed"] == preflight["checks_total"],
        result["attempts"] == 1 and result["retries"] == 0,
        result["native_exit_code"] == 0 and result["native_success"] is True,
        result["class_surface_binding_pass"] is True,
        result["direct_logmap_child_exit_codes"] == [0],
        result["five_regular_non_symlink_artifacts"] is True,
        len(result["native_artifacts"]) == 5,
        result["typed_decoder_pass"] is False,
        result["typed_decoder"]["error"] == "ValueError: source surface string violates frozen typed grammar",
        result["reference_semantically_opened"] is False,
        result["common_scoring_authorized"] is False,
        result["terminal"] == "P3_V20_BERTMAP_NATIVE_PASS__TYPED_DECODER_OR_STRUCTURAL_CONTRACT_FAIL__COMMON_SCORING_NOT_AUTHORIZED",
    ]
    for item in result["native_artifacts"].values():
        path = Path(item["path"])
        checks.append(path.is_file() and not path.is_symlink() and path.stat().st_size == item["bytes"] and sha(path) == item["sha256"])
    sums_ok = True
    for line in (ROOT / "SHA256SUMS").read_text().splitlines():
        expected, relative = line.split("  ", 1)
        path = ROOT / relative
        sums_ok = sums_ok and path.is_file() and not path.is_symlink() and sha(path) == expected
    checks.append(sums_ok)
    if not all(checks):
        print("P3_V20_VALIDATION_FAIL")
        return 1
    print(f"P3_V20_PACKET_VALID__NATIVE_AND_FIVE_ARTIFACT_PASS__TYPED_DECODER_FAILURE_PRESERVED__REFERENCE_UNOPENED__{len(checks)}_CHECKS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
