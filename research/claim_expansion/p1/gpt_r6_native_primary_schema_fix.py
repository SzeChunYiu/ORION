from __future__ import annotations

import copy
import sys
from typing import Mapping

import gpt_r6_native_primary as primary

# Capture the immutable R6 v1 validator before main() installs the compatibility
# adapter. Delegation must never resolve through the monkey-patched module slot.
_ORIGINAL_NATIVE_ROW_VALID = primary._native_row_valid


def _raw_sha256_from_content_digest(value: object) -> str | None:
    text = str(value)
    prefix = "sha256:"
    if not text.startswith(prefix):
        return None
    raw = text[len(prefix):]
    if len(raw) != 64 or any(ch not in "0123456789abcdef" for ch in raw):
        return None
    return raw


def _native_row_valid_with_canonical_transfer_digests(native: Mapping[str, object]) -> bool:
    """Validate the two digest schemas without weakening either boundary.

    Harness state endpoint hashes are raw 64-hex SHA-256 values. ORION transfer-v2
    receipts intentionally use canonical ``sha256:<64-hex>`` content digests. R6 v1
    incorrectly applied the raw-hash validator to both representations, causing all
    otherwise valid native rows to be rejected after execution.
    """
    patched = copy.deepcopy(native)
    try:
        for arm_name in ("base", "ard"):
            arm = patched[arm_name]
            if not isinstance(arm, dict):
                return False
            for key in ("responsibility_digest", "interface_digest", "revision_gate_digest"):
                raw = _raw_sha256_from_content_digest(arm.get(key))
                if raw is None:
                    return False
                arm[key] = raw
            for key in ("mechanic_digests", "assessment_digests"):
                values = arm.get(key)
                if not isinstance(values, list) or not values:
                    return False
                normalized = []
                for value in values:
                    raw = _raw_sha256_from_content_digest(value)
                    if raw is None:
                        return False
                    normalized.append(raw)
                arm[key] = normalized
    except (KeyError, TypeError):
        return False
    return _ORIGINAL_NATIVE_ROW_VALID(patched)


def _valid_fixture() -> dict[str, object]:
    content = "sha256:" + "b" * 64
    return {
        "runtime": {
            "trace_id": "trace",
            "receipt_ids": ["receipt"],
            "pre_state_hash": "a" * 64,
            "post_state_hash": "c" * 64,
            "final_state_digest": "d" * 64,
            "operator_sequence": ["FRAME", "SEARCH", "ABSORB", "RECONSTRUCT"],
        },
        "base": {
            "responsibility_digest": content,
            "interface_digest": content,
            "revision_gate_digest": content,
            "mechanic_digests": [content],
            "assessment_digests": [content],
        },
        "ard": {
            "responsibility_digest": content,
            "interface_digest": content,
            "revision_gate_digest": content,
            "mechanic_digests": [content],
            "assessment_digests": [content],
        },
    }


def _self_test() -> None:
    native = _valid_fixture()
    assert _native_row_valid_with_canonical_transfer_digests(native)

    bad_transfer = copy.deepcopy(native)
    bad_transfer["base"]["responsibility_digest"] = "b" * 64
    assert not _native_row_valid_with_canonical_transfer_digests(bad_transfer)

    bad_runtime = copy.deepcopy(native)
    bad_runtime["runtime"]["pre_state_hash"] = "sha256:" + "a" * 64
    assert not _native_row_valid_with_canonical_transfer_digests(bad_runtime)

    # Exercise the exact production installation path. This catches accidental
    # recursion through primary._native_row_valid after monkey-patching.
    installed_before = primary._native_row_valid
    try:
        primary._native_row_valid = _native_row_valid_with_canonical_transfer_digests
        assert primary._native_row_valid(native)
        assert not primary._native_row_valid(bad_transfer)
        assert not primary._native_row_valid(bad_runtime)
    finally:
        primary._native_row_valid = installed_before

    print("P1_R6_DIGEST_SCHEMA_FIX=PASS")


def main() -> None:
    if sys.argv[1:] == ["--self-test"]:
        _self_test()
        return
    primary._native_row_valid = _native_row_valid_with_canonical_transfer_digests
    primary.main()


if __name__ == "__main__":
    main()
