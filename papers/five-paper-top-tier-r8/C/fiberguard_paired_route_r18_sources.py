"""Source and protocol custody for the outcome-exposed R18 recovery replay."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import fiberguard_aslib_sat12_all_r11 as r11

EXPECTED_SCHEMA = "ORION.FiberGuard.PairedRoute.Protocol.R18.v1"
EXPECTED_PARENT = "f34b61e0051289588eaf144a580dca7bc9b7e707"
EXPECTED_UPSTREAM = "551b22beef8df17de59286b4822ef720e0aa4d6f"
EXPECTED_SCENARIOS = ("MAXSAT12-PMS", "MAXSAT19-UCMS", "QBF-2016")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def validate_protocol(protocol: dict[str, Any]) -> None:
    if protocol.get("schema") != EXPECTED_SCHEMA:
        raise ValueError("unexpected R18 protocol schema")
    if protocol.get("parent_commit") != EXPECTED_PARENT:
        raise ValueError("unexpected R18 protocol parent")
    if protocol.get("upstream", {}).get("commit") != EXPECTED_UPSTREAM:
        raise ValueError("unexpected ASlib source commit")
    scenarios = protocol.get("scenarios", {})
    observed = (
        scenarios.get("development", {}).get("name"),
        scenarios.get("validation", {}).get("name"),
        scenarios.get("test", {}).get("name"),
    )
    if observed != EXPECTED_SCENARIOS:
        raise ValueError(f"unexpected scenario ordering: {observed!r}")
    split = protocol.get("split", {})
    if int(split.get("official_cv_repetition", -1)) != 1:
        raise ValueError("only official CV repetition 1 is admissible")
    if int(split.get("expected_folds", -1)) != 10:
        raise ValueError("R18 requires ten official folds")
    if list(protocol.get("alpha", [])) != [0.05, 0.1, 0.2]:
        raise ValueError("R18 alpha denominator drift")
    if list(protocol.get("route_modes", [])) != [
        "paired_upper",
        "interval_no_harm",
        "direct_difference",
    ]:
        raise ValueError("R18 route-mode denominator drift")
    candidates = protocol.get("model_candidates", {})
    expected_models = (
        len(candidates.get("knn", {}).get("neighbors", []))
        + len(candidates.get("extra_trees", {}).get("min_samples_leaf", []))
        * len(candidates.get("extra_trees", {}).get("max_features", []))
        + len(candidates.get("random_forest", {}).get("min_samples_leaf", []))
        * len(candidates.get("random_forest", {}).get("max_features", []))
    )
    if expected_models != 11 or expected_models * 3 * 3 != 99:
        raise ValueError("R18 frozen 99-candidate denominator drift")
    authority = protocol.get("authority", {})
    required_true = (
        "result_must_be_absent_from_protocol_commit",
        "R16_scenarios_may_not_select_R18_parameters",
        "MAXSAT12_is_development_only",
        "MAXSAT19_is_validation_only",
        "QBF2016_is_untouched_test",
        "solver_models_are_refit_within_scenario",
        "model_route_alpha_tuple_transfers_without_retuning",
    )
    for key in required_true:
        if authority.get(key) is not True:
            raise ValueError(f"hard authority flag changed: {key}")


def verify_files(root: Path, expected: dict[str, str]) -> dict[str, Any]:
    audit: dict[str, Any] = {}
    for name, expected_blob in expected.items():
        path = root / name
        actual_blob = r11.git_blob_sha(path)
        if actual_blob != expected_blob:
            raise ValueError(
                f"source blob mismatch for {path}: {actual_blob} != {expected_blob}"
            )
        audit[name] = {
            "git_blob_sha1": actual_blob,
            "sha256": r11.sha256_file(path),
            "bytes": path.stat().st_size,
        }
    return audit
