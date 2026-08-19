#!/usr/bin/env python3
"""Operative P2 claim-ledger checker with additive P2-X ledger binding.

The original checker is preserved byte-for-byte as ``check_claim_ledger_v1.py``.
This wrapper merges ``protocol/CLAIM_LEDGER_P2X_ADDENDUM_V1.json`` into the
frozen V1 ledger before delegating to the original implementation.  The overlay
is additive only: existing artifact aliases and claim IDs cannot be replaced.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import check_claim_ledger_v1 as _v1


ADDENDUM_RELATIVE = Path("protocol") / "CLAIM_LEDGER_P2X_ADDENDUM_V1.json"
_ORIGINAL_LOAD_JSON = _v1._load_json


def _merge_addendum(base: dict[str, Any], addendum: dict[str, Any]) -> dict[str, Any]:
    if addendum.get("schema_version") != "orion.p2.claim-ledger.p2x-addendum.v1":
        raise _v1.HarnessError("unexpected P2-X claim-ledger addendum schema")
    if addendum.get("base_ledger") != _v1.LEDGER_RELATIVE.name:
        raise _v1.HarnessError("P2-X addendum does not bind the operative V1 ledger")

    merged = copy.deepcopy(base)
    artifacts = addendum.get("artifacts", {})
    claims = addendum.get("claims", [])
    if not isinstance(artifacts, dict) or not isinstance(claims, list):
        raise _v1.HarnessError("P2-X addendum artifacts/claims have invalid shape")

    artifact_collisions = sorted(set(merged.get("artifacts", {})) & set(artifacts))
    if artifact_collisions:
        raise _v1.HarnessError(
            "P2-X addendum may not replace V1 artifact aliases: "
            + ", ".join(artifact_collisions)
        )

    existing_ids = {str(row.get("claim_id", "")) for row in merged.get("claims", [])}
    added_ids = [str(row.get("claim_id", "")) for row in claims if isinstance(row, dict)]
    if any(not item for item in added_ids) or len(added_ids) != len(set(added_ids)):
        raise _v1.HarnessError("P2-X addendum claim IDs must be non-empty and unique")
    collisions = sorted(existing_ids & set(added_ids))
    if collisions:
        raise _v1.HarnessError(
            "P2-X addendum may not replace V1 claims: " + ", ".join(collisions)
        )

    merged["artifacts"].update(copy.deepcopy(artifacts))
    merged["claims"].extend(copy.deepcopy(claims))
    merged.setdefault("non_claim_sentences", []).extend(
        copy.deepcopy(addendum.get("non_claim_sentences", []))
    )
    merged.setdefault("known_defects", []).extend(
        copy.deepcopy(addendum.get("known_defects", []))
    )
    return merged


def _load_json_with_addendum(path: Path, label: str) -> Any:
    payload = _ORIGINAL_LOAD_JSON(path, label)
    if path.name != _v1.LEDGER_RELATIVE.name:
        return payload
    addendum_path = path.parent / ADDENDUM_RELATIVE.name
    if not addendum_path.is_file():
        return payload
    addendum = _ORIGINAL_LOAD_JSON(addendum_path, "P2-X claim-ledger addendum")
    if not isinstance(payload, dict) or not isinstance(addendum, dict):
        raise _v1.HarnessError("claim ledger and addendum must both be JSON objects")
    return _merge_addendum(payload, addendum)


_v1._load_json = _load_json_with_addendum

# Re-export the original checker surface so direct imports keep working.
for _name in dir(_v1):
    if _name.startswith("__"):
        continue
    globals().setdefault(_name, getattr(_v1, _name))


def main(argv: list[str] | None = None) -> int:
    return _v1.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
