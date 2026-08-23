#!/usr/bin/env python3
"""Re-run the R6 primary with role-free episode identifiers.

Protocol: ``FREEZE_2026-08-21_ROLE_FREE_IDENTIFIERS_V1.md`` beside this file.

Nothing about the scoring is re-implemented here. ``evaluate_native.evaluate``
is imported and called exactly as it stands, with the same corpus, the same
comparator and the same thresholds; the only difference between this run and the
one in ``claude_t3/REPAIRED_GUARD_RUN_V1.json`` is that the episode identifier
crossing the provider boundary is an opaque handle.

The two freeze preconditions are checked **before** the evaluator runs and abort
the run on failure, because a leakage repair that only partly lands would
otherwise produce arm numbers that look like a result.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
R6 = HERE.parent / "gpt_r6"
DR1 = HERE.parent / "gpt_r6_dr1"
REPO_ROOT = HERE.parents[3]

FREEZE_DOCUMENT = "FREEZE_2026-08-21_ROLE_FREE_IDENTIFIERS_V4.md"
SCHEMA_VERSION = "P1U.RoleFreeRerun.v1"


def _load(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _bootstrap() -> tuple[Any, Any, Any, Any]:
    if str(REPO_ROOT / "src") not in sys.path:
        sys.path.insert(0, str(REPO_ROOT / "src"))
    evaluator = _load(R6 / "evaluate_native.py", "p1_r6_anon_evaluator")
    # `evaluator.NATIVE` is `native_orion.py`, which re-exports the core rather
    # than being it. `run_native_ard` lives in `native_orion_core_v1` and
    # resolves `run_root_runtime` from *that* module's globals, so patching the
    # re-export has no effect -- a first attempt did exactly that and minted zero
    # handles while the audit reported the same 96 of 96 failures.
    core = getattr(evaluator.NATIVE, "_CORE", evaluator.NATIVE)
    repaired = _load(DR1 / "repaired_root_v1.py", "p1_r6_anon_repaired_root")
    anon = _load(HERE / "anonymous_root_v1.py", "p1_r6_anon_root")
    return evaluator, core, repaired, anon


def check_preconditions(evaluator: Any, anon: Any) -> dict[str, Any]:
    """Freeze section 4. Both are properties of the payloads, not of an outcome."""

    pairs, unresolved = evaluator.fixed_corpus()
    episode_ids: list[str] = []
    roles: list[str] = []
    for pair in pairs:
        for member in ("adverse", "control"):
            episode_ids.append(str(pair[member]["id"]))
            roles.append(member)
    for episode in unresolved:
        episode_ids.append(str(episode["id"]))
        roles.append("unresolved")

    role_free = anon.handle_is_role_free(episode_ids, roles)
    return {
        "episodes": len(episode_ids),
        "handle_is_role_free": role_free,
        "passed": bool(role_free["passed"]),
    }


def run(*, payloads_out: Path | None = None) -> dict[str, Any]:
    evaluator, core, repaired, anon = _bootstrap()

    preconditions = check_preconditions(evaluator, anon)
    if not preconditions["passed"]:
        return {
            "schema_version": SCHEMA_VERSION,
            "freeze_document": FREEZE_DOCUMENT,
            "preconditions": preconditions,
            "arms_executed": False,
            "terminal": "P1_R6_ROLE_FREE_CANNOT_CHECK_PRECONDITION",
        }

    # Patch the core's own module-global entry point. `evaluate` scores the
    # frozen 2020 primary through `run_native_ard`/`run_native_base`, which
    # resolve `run_root_runtime` as a global at call time -- so this reaches the
    # path the evaluator actually takes. A first attempt patched the DR1
    # repaired-root context manager instead, which `evaluate` never touches, and
    # the leakage audit correctly reported the same 96 of 96 failures as before.
    # Restored afterwards, so importing this module changes nothing else.
    mapping: dict[str, str] = {}
    native = evaluator.NATIVE
    originals = {
        "run_native_ard": native.run_native_ard,
        "run_native_base": native.run_native_base,
    }
    native.run_native_ard = anon.wrap_arm(originals["run_native_ard"], mapping_out=mapping)
    native.run_native_base = anon.wrap_arm(originals["run_native_base"], mapping_out=mapping)
    payload_sink: dict[str, list[dict[str, str]]] = {}
    try:
        result = evaluator.evaluate(
            *evaluator.fixed_corpus(), payload_sink=payload_sink
        )
    finally:
        for name, value in originals.items():
            setattr(native, name, value)

    if payloads_out is not None:
        payloads_out.parent.mkdir(parents=True, exist_ok=True)
        payloads_out.write_text(
            json.dumps(payload_sink, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    checks = dict(result.get("checks", {}))
    return {
        "schema_version": SCHEMA_VERSION,
        "freeze_document": FREEZE_DOCUMENT,
        "claim_scope": "FROZEN_DETERMINISTIC_HOST_ONLY",
        "preconditions": preconditions,
        "episode_to_handle": dict(sorted(mapping.items())),
        "arms_executed": True,
        "checks": checks,
        "leakage_check_passed": bool(checks.get("no_candidate_metadata_leakage")),
        "all_checks_passed": all(bool(value) for value in checks.values()),
        "result": result,
        "not_licensed": [
            "any superiority claim on a semantic model; this host is a frozen "
            "deterministic provider",
            "discharge of P1-U-T2's 2019 replication, separately blocked by the "
            "evaluator hardcoding source_year == 2020",
            "any claim that the leaked identifier is harmless in general",
        ],
    }


def main(argv: list[str]) -> int:
    """CLI entry point. ``argv`` is required: there is no implicit run."""

    import argparse

    parser = argparse.ArgumentParser(
        prog="p1-role-free-rerun",
        description="Re-run the R6 primary with role-free episode identifiers.",
    )
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--payloads-out", type=Path, default=None)
    args = parser.parse_args(argv)

    report = run(payloads_out=args.payloads_out)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"written: {args.out}")

    if not report["preconditions"]["passed"]:
        print("PRECONDITION FAILED; no arm was scored")
        return 3
    for name, value in sorted(report["checks"].items()):
        print(f"  {'PASS' if value else 'FAIL'}  {name}")
    print(f"terminal: {report['result'].get('terminal')}")
    return 0 if report["all_checks_passed"] else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
