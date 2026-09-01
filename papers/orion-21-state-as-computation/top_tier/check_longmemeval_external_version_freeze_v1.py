#!/usr/bin/env python3
"""Fail-closed static verifier for the pre-outcome LongMemEval version freeze."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
FREEZE = HERE / "LONGMEMEVAL_EXTERNAL_VERSION_FREEZE_V1.json"
P11 = ROOT / "papers/orion-21-state-as-computation/P11_EXTERNAL_VALIDATION_REQUIREMENTS_V1.md"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def git_blob(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], cwd=ROOT, text=True).strip()


def main() -> int:
    p = json.loads(FREEZE.read_text(encoding="utf-8"))
    l1 = p["longmemeval"]
    l2 = p["longmemeval_v2"]
    checks: dict[str, bool] = {}
    checks["schema"] = p["schema"] == "ORION.A2.LongMemEvalExternalVersionFreeze.v1"
    checks["outcome_blind"] = (
        p["protected_outcomes_accessed"] is False
        and p["benchmark_evaluation_executed"] is False
        and p["scientific_authority_delta"] == "NONE__VERSION_FREEZE_ONLY"
    )
    checks["p11_authority_unchanged"] = git_blob(P11) == "f8ba0680dc5fd0fd0acef8b5926b093cb84b26cc"
    checks["longmemeval_code_bound"] = all(HEX40.fullmatch(l1[k]) for k in ("code_commit", "code_tree"))
    checks["longmemeval_dataset_revision_bound"] = bool(HEX40.fullmatch(l1["dataset_revision"]))
    checks["longmemeval_cleaned_selected"] = (
        l1["dataset_repository"] == "xiaowu0162/longmemeval-cleaned"
        and l1["deprecated_dataset_excluded"]["dataset_repository"] == "xiaowu0162/longmemeval"
    )
    checks["longmemeval_mit"] = l1["code_license"] == l1["dataset_license"] == "MIT"
    checks["known_cleaned_s_hash_bound"] = bool(
        HEX64.fullmatch(l1["known_file_hashes"]["longmemeval_s_cleaned.json"])
    )
    checks["longmemeval_v2_code_bound"] = all(HEX40.fullmatch(l2[k]) for k in ("code_commit", "code_tree"))
    checks["longmemeval_v2_dataset_revision_bound"] = bool(HEX40.fullmatch(l2["dataset_revision"]))
    checks["longmemeval_v2_apache"] = l2["code_license"] == l2["dataset_license"] == "Apache-2.0"
    checks["v2_core_hashes_complete"] = set(l2["dataset_core_sha256"]) == {
        "questions.jsonl", "trajectories.jsonl",
        "haystacks/lme_v2_small.json", "haystacks/lme_v2_medium.json"
    } and all(HEX64.fullmatch(v) for v in l2["dataset_core_sha256"].values())
    checks["v2_scope_bound"] = (
        l2["public_scope"]["questions"] == 451
        and l2["public_scope"]["trajectories"] == 1870
        and l2["public_scope"]["domains"] == ["web", "enterprise"]
        and l2["public_scope"]["memory_abilities"] == 5
    )
    checks["immutable_semantics"] = (
        "exact upstream commit/revision" in p["freeze_semantics"]["version_identity"]
        and "no version substitution" in p["freeze_semantics"]["future_upstream_changes"]
        and "CANNOT_CHECK_VERSION_BINDING" in p["freeze_semantics"]["materialization_check"]
    )
    checks["terminal"] = p["terminal"] == "VERSIONS_AND_HASHES_FROZEN__OUTCOMES_UNRUN"

    good = all(checks.values())
    print(json.dumps({"decision": "GREEN" if good else "REJECT", "checks": checks}, indent=2, sort_keys=True))
    return 0 if good else 1


if __name__ == "__main__":
    raise SystemExit(main())
