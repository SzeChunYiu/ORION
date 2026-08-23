"""Locked-environment P12B revalidation without changing the V1 estimand."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

from .equal_action_successor import (
    ACTIONS,
    EPISODES_PER_FAMILY,
    N_FAMILIES,
    NOT_SUPPORTED,
    OneSignalObservation,
    SIGMAS,
    SUPPORTED,
    TwoSignalObservation,
    adjudicate as adjudicate_v1,
    build_core as build_core_v1,
    canonical_text,
    file_sha256,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
PAPER = REPO_ROOT / "papers/paper-12-adaptive-state-reasoning"
REVALIDATION = PAPER / "P12B_LOCKED_ENVIRONMENT_REVALIDATION_V1_1.md"
UV_LOCK = REPO_ROOT / "uv.lock"

LOCKED_PYTHON_IMPLEMENTATION = "CPython"
LOCKED_PYTHON_VERSION = "3.12.13"
LOCKED_NUMPY_VERSION = "2.5.2"
LOCKED_UV_LOCK_SHA256 = (
    "4e0f595c568cf7cfdf15bb88518ad2fc5951a1cf9f03bb3c4b307471f852dade"
)


def expected_environment() -> dict[str, str]:
    return {
        "python_implementation": LOCKED_PYTHON_IMPLEMENTATION,
        "python_version": LOCKED_PYTHON_VERSION,
        "numpy_version": LOCKED_NUMPY_VERSION,
        "uv_lock_path": "uv.lock",
        "uv_lock_sha256": LOCKED_UV_LOCK_SHA256,
    }


def build_core() -> dict[str, Any]:
    core = build_core_v1()
    core["schema"] = "ORION.P12B.EqualActionSignalComplementarity.Core.v1.1"
    core["locked_environment_revalidation"] = str(REVALIDATION.relative_to(REPO_ROOT))
    core["locked_environment_revalidation_sha256"] = file_sha256(REVALIDATION)
    core["environment"].update(
        {
            "uv_lock_path": "uv.lock",
            "uv_lock_sha256": file_sha256(UV_LOCK),
        }
    )
    return core


def adjudicate(core: Mapping[str, Any], *, byte_identical_replay: bool) -> dict[str, Any]:
    result = adjudicate_v1(deepcopy(core), byte_identical_replay=byte_identical_replay)
    result["schema"] = "ORION.P12B.EqualActionSignalComplementarity.Result.v1.1"
    result["gates"]["locked_environment_identity_matches_v1_1"] = (
        result["core"].get("environment") == expected_environment()
    )
    result["terminal"] = SUPPORTED if all(result["gates"].values()) else NOT_SUPPORTED
    return result


__all__ = [
    "ACTIONS",
    "EPISODES_PER_FAMILY",
    "LOCKED_NUMPY_VERSION",
    "LOCKED_PYTHON_IMPLEMENTATION",
    "LOCKED_PYTHON_VERSION",
    "LOCKED_UV_LOCK_SHA256",
    "N_FAMILIES",
    "NOT_SUPPORTED",
    "OneSignalObservation",
    "SIGMAS",
    "SUPPORTED",
    "TwoSignalObservation",
    "adjudicate",
    "build_core",
    "canonical_text",
    "expected_environment",
]

