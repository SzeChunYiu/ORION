#!/usr/bin/env python3
"""Execute the frozen V2 P5-RD-02 public Defects4J factorial."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import time
from pathlib import Path


STUDY_ID = "P5-RD-02.DEFECTS4J.LANG1.V2"
ROOT = Path("/tmp/p5-rd02-defects4j")
D4J = ROOT / "defects4j"
D4J_BIN = D4J / "framework/bin/defects4j"
RUN_ROOT = ROOT / "factorial-runs-v2"
OUT = Path(__file__).resolve().parent
TIMEOUT = 1200
TRIGGER = "org.apache.commons.lang3.math.NumberUtilsTest::TestLang747"
EXPECTED = {
    "C0": {
        "version": "1b",
        "upstream_revision": "396afc3e4693cfee182efe582455f2d97058c068",
        "prepared_tree": "eaec8f08f7e0fc2d10a39a6480878a338e1a7090",
        "config_sha256": "9f566faf05152c1365d5af98e8815dc6adf386318bf9017ce4b6ac31b6b3a984",
    },
    "C1": {
        "version": "1f",
        "upstream_revision": "d1a45e9738de5b3e299bb51e987565dcce55fee6",
        "prepared_tree": "5890638f92d023d4bb6df6625508326009924c76",
        "config_sha256": "d9eaa4710bebdc29e3c4d4323344756c135c90032f13b05112583cbae970cc87",
    },
}
ENVIRONMENTS = {
    "E0": {
        "java_home": "/opt/homebrew/Cellar/openjdk@11/11.0.32.1/libexec/openjdk.jdk/Contents/Home",
        "java_version": "11.0.32.1+0",
        "java_binary_sha256": "c7ec15111335d5c7ef3c9a3ddcb67642ef3cfbbd8efc98d90b90526628b245b4",
    },
    "E1": {
        "java_home": "/tmp/p5-rd02-defects4j/jdk11/Contents/Home",
        "java_version": "11.0.32+9",
        "java_binary_sha256": "e561d7ba57da3bb04df5db5da06a7a164811fa3981c1cfaed0516c70f784b301",
    },
}
ORDER = ("C1E0", "C0E0", "C0E1", "C1E1")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str], *, cwd: Path, env: dict[str, str], stem: Path, timeout: int) -> dict[str, object]:
    started = time.time()
    timed_out = False
    try:
        result = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, timeout=timeout, check=False)
        exit_code = result.returncode
        stdout = result.stdout
        stderr = result.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        exit_code = None
        stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
    elapsed = time.time() - started
    stdout_path = stem.with_suffix(".stdout.txt")
    stderr_path = stem.with_suffix(".stderr.txt")
    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")
    return {
        "command": command,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "elapsed_seconds": elapsed,
        "stdout_path": stdout_path.name,
        "stdout_sha256": sha256(stdout_path),
        "stderr_path": stderr_path.name,
        "stderr_sha256": sha256(stderr_path),
    }


def git_value(workspace: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=workspace, text=True).strip()


def parse_failing_tests(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [line[4:].strip() for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("--- ")]


def environment(level: str) -> dict[str, str]:
    java_home = ENVIRONMENTS[level]["java_home"]
    env = dict(os.environ)
    env.update(
        {
            "JAVA_HOME": java_home,
            "PATH": f"{java_home}/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin",
            "PERL5LIB": "/Users/billy/perl5/lib/perl5",
            "TZ": "America/Los_Angeles",
            "LC_ALL": "C",
            "LANG": "C",
        }
    )
    return env


def execute_cell(cell_id: str) -> dict[str, object]:
    candidate = cell_id[:2]
    runtime = cell_id[2:]
    workspace = RUN_ROOT / cell_id
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.parent.mkdir(parents=True, exist_ok=True)
    env = environment(runtime)
    java_binary = Path(env["JAVA_HOME"]) / "bin/java"
    java_sha = sha256(java_binary)
    environment_identity_ok = java_sha == ENVIRONMENTS[runtime]["java_binary_sha256"]

    checkout = run(
        [str(D4J_BIN), "checkout", "-p", "Lang", "-v", EXPECTED[candidate]["version"], "-w", str(workspace)],
        cwd=D4J,
        env=env,
        stem=OUT / f"V2.{cell_id}.checkout",
        timeout=TIMEOUT,
    )
    local_head = None
    prepared_tree = None
    license_sha = None
    config_sha = None
    checkout_identity_ok = False
    if checkout["exit_code"] == 0 and not checkout["timed_out"] and workspace.exists():
        local_head = git_value(workspace, "rev-parse", "HEAD")
        prepared_tree = git_value(workspace, "rev-parse", "HEAD^{tree}")
        license_path = workspace / "LICENSE.txt"
        config_path = workspace / ".defects4j.config"
        license_sha = sha256(license_path) if license_path.exists() else None
        config_sha = sha256(config_path) if config_path.exists() else None
        checkout_identity_ok = (
            prepared_tree == EXPECTED[candidate]["prepared_tree"]
            and config_sha == EXPECTED[candidate]["config_sha256"]
            and license_sha == "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"
        )

    if checkout_identity_ok and environment_identity_ok:
        test = run(
            [str(D4J_BIN), "test"],
            cwd=workspace,
            env=env,
            stem=OUT / f"V2.{cell_id}.test",
            timeout=TIMEOUT,
        )
    else:
        test = {
            "command": [str(D4J_BIN), "test"],
            "exit_code": None,
            "timed_out": False,
            "elapsed_seconds": 0.0,
            "stdout_path": None,
            "stdout_sha256": None,
            "stderr_path": None,
            "stderr_sha256": None,
            "not_run_reason": "checkout_or_environment_identity_failed",
        }

    failing_path = workspace / "failing_tests"
    failures = parse_failing_tests(failing_path)
    failing_sha = sha256(failing_path) if failing_path.exists() else None
    valid = bool(
        checkout_identity_ok
        and environment_identity_ok
        and test["exit_code"] == 0
        and not test["timed_out"]
        and failing_path.exists()
    )
    success = (len(failures) == 0) if valid else None
    expected_failures = {TRIGGER} if candidate == "C0" else set()
    unexpected = sorted(set(failures) - expected_failures)
    adverse = bool(not valid or (candidate == "C1" and failures) or unexpected)
    return {
        "cell_id": cell_id,
        "candidate_level": candidate,
        "environment_level": runtime,
        "workspace": str(workspace),
        "checkout": checkout,
        "local_prepared_head": local_head,
        "prepared_tree": prepared_tree,
        "license_sha256": license_sha,
        "defects4j_config_sha256": config_sha,
        "checkout_identity_ok": checkout_identity_ok,
        "java_home": env["JAVA_HOME"],
        "java_version_registered": ENVIRONMENTS[runtime]["java_version"],
        "java_binary_sha256": java_sha,
        "environment_identity_ok": environment_identity_ok,
        "test": test,
        "failing_tests_path": str(failing_path) if failing_path.exists() else None,
        "failing_tests_sha256": failing_sha,
        "failing_test_count": len(failures) if failing_path.exists() else None,
        "failing_tests": failures,
        "registered_trigger_present": TRIGGER in failures,
        "unexpected_failures": unexpected,
        "valid_cell": valid,
        "cell_success": success,
        "adverse_or_harmful": adverse,
    }


def classify(cells: list[dict[str, object]]) -> dict[str, object]:
    by_id = {str(cell["cell_id"]): cell for cell in cells}
    if any(not cell["valid_cell"] for cell in cells):
        return {
            "primary_terminal": "CANNOT_CHECK",
            "implementation_effect": None,
            "environment_effect": None,
            "interaction": None,
            "harm_modifier": "HARMFUL_OR_ADVERSE_CELL_PRESENT" if any(cell["adverse_or_harmful"] for cell in cells) else "NO_ADVERSE_CELL",
        }
    y = {key: int(bool(by_id[key]["cell_success"])) for key in by_id}
    implementation = ((y["C1E0"] + y["C1E1"]) - (y["C0E0"] + y["C0E1"])) / 2
    environment_effect = ((y["C0E1"] + y["C1E1"]) - (y["C0E0"] + y["C1E0"])) / 2
    interaction = (y["C1E1"] - y["C0E1"]) - (y["C1E0"] - y["C0E0"])
    if interaction != 0 or (implementation != 0 and environment_effect != 0):
        terminal = "COUPLED_INTERACTION"
    elif environment_effect != 0:
        terminal = "ENVIRONMENT_MAIN_EFFECT"
    elif implementation != 0:
        terminal = "IMPLEMENTATION_MAIN_EFFECT"
    else:
        terminal = "JOINT_NULL_UNRESOLVED"
    return {
        "primary_terminal": terminal,
        "implementation_effect": implementation,
        "environment_effect": environment_effect,
        "interaction": interaction,
        "harm_modifier": "HARMFUL_OR_ADVERSE_CELL_PRESENT" if any(cell["adverse_or_harmful"] for cell in cells) else "NO_ADVERSE_CELL",
    }


def main() -> None:
    prereg = OUT / "PREREGISTRATION_V2.json"
    prereg_payload = json.loads(prereg.read_text(encoding="utf-8"))
    if prereg_payload["outcomes_accessed_at_freeze"] is not False or prereg_payload["run_order"] != list(ORDER):
        raise SystemExit("V2 preregistration mismatch")
    cells = [execute_cell(cell_id) for cell_id in ORDER]
    analysis = classify(cells)
    payload = {
        "schema_version": "orion.p5.rd02.public-development-result.v2",
        "study_id": STUDY_ID,
        "parent_study_id": "P5-RD-02",
        "successor_of": "P5-RD-02.DEFECTS4J.LANG1.V1",
        "bridge_identity": "P5.PUBLIC_DEVELOPMENT_TO_PROTECTED_FRESHNESS_BRIDGE.V1",
        "preregistration_path": str(prereg.relative_to(OUT.parent.parent)),
        "preregistration_sha256": sha256(prereg),
        "runner_sha256": sha256(Path(__file__)),
        "outcomes_accessed": True,
        "protected_outcomes_accessed": False,
        "public_development_only": True,
        "run_order": list(ORDER),
        "cells": cells,
        "analysis": analysis,
        "n_independent_units": 1,
        "h1_h4_status": "CANNOT_CHECK",
        "protected_freshness_status": "CANNOT_CHECK",
        "grants_scientific_authority": False,
        "possible_authority": "LOCAL_RIGHTS_BOUND_PUBLIC_DEVELOPMENT_FACTORIAL_ONLY",
        "predecessor_result_changed": False,
    }
    (OUT / "RESULT_V2.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"study_id": STUDY_ID, "analysis": analysis, "cells": [{"cell_id": c["cell_id"], "valid": c["valid_cell"], "success": c["cell_success"], "failures": c["failing_test_count"]} for c in cells]}, indent=2))


if __name__ == "__main__":
    main()
