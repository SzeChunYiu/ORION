#!/usr/bin/env python3
"""Fail-closed validator for the P1 v2.2.4 pre-outcome amendment chain.

The original world receipt intentionally retains the source identities that
preceded execution amendment V2.  Two source files were then changed before an
arm ran or a scientific terminal was observed.  A fresh world generation must
therefore match the frozen world geometry and the *amended* source identities;
requiring it to match the superseded source identities erases the amendment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


BASE_RELATIVE = Path("research/revival/p1/confirmatory/v2.2")
WORLD_IDENTITY_FIELDS = (
    "protocol_version",
    "confirmatory_seed",
    "replication_seed",
    "n",
    "hidden_shift_n",
    "negative_control_n",
    "public_sha256",
    "protected_response_matrix_sha256",
    "candidate_view_leak_count",
    "by_family",
)


class AmendmentValidationError(ValueError):
    """Raised when the frozen/amended identity chain is inconsistent."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AmendmentValidationError(message)


def _load(path: Path) -> dict[str, Any]:
    _require(path.is_file(), f"required record missing: {path}")
    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise AmendmentValidationError(f"invalid JSON record: {path}: {exc}") from exc
    _require(isinstance(payload, dict), f"JSON record is not an object: {path}")
    return payload


def _sha256(path: Path) -> str:
    _require(path.is_file(), f"bound file missing: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _pre_outcome(record: dict[str, Any], label: str) -> None:
    _require(
        record.get("arms_executed_before_correction") is False,
        f"{label} followed arm execution",
    )
    _require(
        record.get("scientific_terminal_observed_before_correction") is False,
        f"{label} followed scientific-terminal access",
    )
    _require(
        record.get("confirmatory_worlds_changed") is False,
        f"{label} changed confirmatory worlds",
    )
    _require(
        record.get("protocol_or_margin_changed") is False,
        f"{label} changed protocol or margin",
    )


def validate_amendment_chain(root: Path, fresh_world_freeze: Path) -> dict[str, Any]:
    root = root.resolve()
    base = root / BASE_RELATIVE
    world_path = base / "PRIMARY_WORLD_FREEZE.json"
    execution_v1_path = base / "PRIMARY_EXECUTION_FREEZE.json"
    execution_v2_path = base / "PRIMARY_EXECUTION_FREEZE_V2.json"
    execution_v3_path = base / "PRIMARY_EXECUTION_FREEZE_V3.json"
    amendment_v1_path = base / "EXECUTION_BINDING_AMENDMENT_V1.json"
    amendment_v2_path = base / "EXECUTION_BINDING_AMENDMENT_V2.json"

    world = _load(world_path)
    fresh = _load(fresh_world_freeze)
    execution_v1 = _load(execution_v1_path)
    execution_v2 = _load(execution_v2_path)
    execution_v3 = _load(execution_v3_path)
    amendment_v1 = _load(amendment_v1_path)
    amendment_v2 = _load(amendment_v2_path)

    world_sha = _sha256(world_path)
    execution_v1_sha = _sha256(execution_v1_path)
    execution_v2_sha = _sha256(execution_v2_path)
    execution_v3_sha = _sha256(execution_v3_path)

    _pre_outcome(amendment_v1, "execution-binding amendment V1")
    _pre_outcome(amendment_v2, "execution-binding amendment V2")
    _require(
        amendment_v1.get("scientific_fields_changed") == [],
        "execution-binding amendment V1 changed scientific fields",
    )
    _require(
        amendment_v1.get("source_hashes_changed") == [],
        "execution-binding amendment V1 changed source hashes",
    )
    _require(
        amendment_v2.get("amendment_sequence") == 2,
        "execution-binding amendment V2 sequence drift",
    )
    _require(
        amendment_v2.get("statistical_implementation_changed") is True,
        "execution-binding amendment V2 omits its implementation change",
    )

    _require(
        amendment_v1.get("old_execution_receipt_sha256") == execution_v1_sha,
        "execution-binding amendment V1 old receipt hash drift",
    )
    _require(
        amendment_v1.get("new_execution_receipt_sha256") == execution_v2_sha,
        "execution-binding amendment V1 new receipt hash drift",
    )
    _require(
        amendment_v1.get("committed_world_receipt_sha256") == world_sha,
        "execution-binding amendment V1 world receipt hash drift",
    )
    _require(
        amendment_v2.get("superseded_execution_receipt_sha256") == execution_v2_sha,
        "execution-binding amendment V2 superseded receipt hash drift",
    )
    _require(
        amendment_v2.get("new_execution_receipt_sha256") == execution_v3_sha,
        "execution-binding amendment V2 new receipt hash drift",
    )
    _require(
        amendment_v2.get("committed_world_receipt_sha256") == world_sha,
        "execution-binding amendment V2 world receipt hash drift",
    )

    v1_without_world_binding = dict(execution_v1)
    v2_without_world_binding = dict(execution_v2)
    v1_without_world_binding.pop("world_freeze_sha256", None)
    v2_without_world_binding.pop("world_freeze_sha256", None)
    _require(
        v1_without_world_binding == v2_without_world_binding,
        "execution V1/V2 differ outside the world-freeze amendment",
    )

    _require(
        execution_v2.get("world_freeze_sha256")
        == execution_v3.get("world_freeze_sha256")
        == world_sha,
        "execution/world receipt binding drift",
    )

    for label, execution in (("V2", execution_v2), ("V3", execution_v3)):
        _require(
            execution.get("arms_executed") is False
            and execution.get("outcome_accessed") is False,
            f"execution freeze {label} is not pre-output",
        )
        _require(
            execution.get("protocol_version") == "P1.epistemic-mutation-necessity.v2.2.4",
            f"execution freeze {label} protocol drift",
        )

    v2_without_sources = dict(execution_v2)
    v3_without_sources = dict(execution_v3)
    v2_sources = v2_without_sources.pop("source_sha256", None)
    v3_sources = v3_without_sources.pop("source_sha256", None)
    _require(
        isinstance(v2_sources, dict) and isinstance(v3_sources, dict),
        "execution freeze source maps missing",
    )
    _require(
        v2_without_sources == v3_without_sources,
        "execution V2/V3 differ outside the recorded source amendment",
    )

    changes = amendment_v2.get("source_hash_changes")
    _require(isinstance(changes, dict) and changes, "source amendment change set missing")
    observed_changes = {
        relative
        for relative in set(v2_sources) | set(v3_sources)
        if v2_sources.get(relative) != v3_sources.get(relative)
    }
    _require(
        observed_changes == set(changes),
        "execution source delta differs from amendment change set",
    )

    for field in WORLD_IDENTITY_FIELDS:
        _require(
            fresh.get(field) == world.get(field),
            f"fresh world identity drift: {field}",
        )
    _require(
        fresh.get("protocol_chain", {}).get("chain_sha256")
        == world.get("protocol_chain", {}).get("chain_sha256"),
        "fresh world protocol-chain drift",
    )
    _require(
        world.get("arms_executed") is False
        and world.get("outcome_accessed") is False,
        "world receipt is not pre-output",
    )

    world_sources = world.get("source_sha256")
    fresh_sources = fresh.get("source_sha256")
    _require(
        isinstance(world_sources, dict) and isinstance(fresh_sources, dict),
        "world source maps missing",
    )
    _require(
        set(world_sources) == set(fresh_sources),
        "fresh world source membership drift",
    )

    for relative, frozen_hash in world_sources.items():
        current_hash = _sha256(root / relative)
        fresh_hash = fresh_sources.get(relative)
        if relative in changes:
            change = changes[relative]
            _require(
                change.get("old") == frozen_hash == v2_sources.get(relative),
                f"recorded old source hash drift: {relative}",
            )
            _require(
                change.get("new") == fresh_hash == current_hash == v3_sources.get(relative),
                f"recorded amended source hash drift: {relative}",
            )
            _require(bool(change.get("effect")), f"source amendment effect missing: {relative}")
        else:
            _require(
                fresh_hash == frozen_hash,
                f"fresh world source mismatch: {relative}",
            )
            _require(
                current_hash == frozen_hash,
                f"unchanged world source drift: {relative}",
            )
            if relative in v2_sources or relative in v3_sources:
                _require(
                    v2_sources.get(relative) == v3_sources.get(relative) == frozen_hash,
                    f"unchanged execution/world source mismatch: {relative}",
                )

    for relative, expected in v3_sources.items():
        _require(
            _sha256(root / relative) == expected,
            f"current execution source drift: {relative}",
        )

    return {
        "schema": "ORION.P1.NecessityAmendmentChainValidation.v1",
        "status": "AMENDMENT_CHAIN_VALID",
        "world_rows_changed": False,
        "source_change_count": len(changes),
        "source_changes": sorted(changes),
        "bindings": {
            "world_freeze_sha256": world_sha,
            "execution_freeze_v2_sha256": execution_v2_sha,
            "execution_freeze_v3_sha256": execution_v3_sha,
        },
        "authority": {
            "scientific_authority_delta": "NONE",
            "freeze_authorized": False,
            "submission_authorized": False,
            "top_tier_gate_pass": False,
        },
        "claim_boundary": (
            "MECHANICAL_AMENDMENT_CHAIN_VALIDATION_ONLY__"
            "HISTORICAL_PROSPECTIVE_ORDER_NOT_ESTABLISHED"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--fresh-world-freeze", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    receipt = validate_amendment_chain(args.repo_root, args.fresh_world_freeze)
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered)
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
