#!/usr/bin/env python3
"""Fail-closed P5 C4 gate for a future rights-cleared ADIAS run.

The frozen V4 registry is deliberately not execution-ready, so the current
packet can only preflight/refuse.  If a successor registry binds all 21 fields,
this gate also enforces a direct foreground entrypoint, a whole-run watchdog,
an environment allowlist, and cleanup against an explicitly dedicated Docker
daemon.  It never launches the upstream background/nohup scripts.
"""

from __future__ import annotations

import argparse
import json
import os
import resource
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "orion.p5.c4.adias-runner-terminal.v4"
REQUIRED_FIELDS = 21
FORBIDDEN_FLAGS = {
    "--final_test",
    "--enable_external_search",
    "--external_search_force",
    "--eval_test",
    "--resume_from",
}
REQUIRED_FLAGS = {"--no_final_test", "--no-enable_external_search"}
ENV_ALLOWLIST = {
    "PATH",
    "LANG",
    "LC_ALL",
    "OPENAI_API_KEY",
    "OPENAI_API_BASE",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "X_END_USER",
    "OPENAI_X_END_USER",
    "OPENAI_EXTRA_HEADERS",
}


class GateRefusal(ValueError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise GateRefusal(f"expected object in {path}")
    return value


def _registry_state(registry: dict[str, Any]) -> tuple[list[str], list[str]]:
    fields = registry.get("fields")
    if not isinstance(fields, dict) or len(fields) != REQUIRED_FIELDS:
        raise GateRefusal(f"registry must contain exactly {REQUIRED_FIELDS} fields")
    bound = sorted(key for key, value in fields.items() if value.get("status") == "BOUND")
    blocking = sorted(key for key, value in fields.items() if value.get("status") != "BOUND")
    if registry.get("bound_field_count") != len(bound):
        raise GateRefusal("bound_field_count mismatch")
    if registry.get("blocking_field_count") != len(blocking):
        raise GateRefusal("blocking_field_count mismatch")
    return bound, blocking


def _write_terminal(path: Path | None, terminal: dict[str, Any]) -> None:
    payload = json.dumps(terminal, indent=2, sort_keys=True) + "\n"
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)


def _preexec(limits: dict[str, int]) -> None:
    os.setsid()
    os.umask(0o077)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_NOFILE, (limits["open_files"], limits["open_files"]))
    resource.setrlimit(resource.RLIMIT_FSIZE, (limits["file_bytes"], limits["file_bytes"]))
    resource.setrlimit(resource.RLIMIT_NPROC, (limits["processes"], limits["processes"]))


def _docker_ids(docker_bin: str, docker_host: str) -> set[str]:
    completed = subprocess.run(
        [docker_bin, "--host", docker_host, "ps", "-aq"],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return {line.strip() for line in completed.stdout.splitlines() if line.strip()}


def _cleanup_new_containers(docker_bin: str, docker_host: str, baseline: set[str]) -> None:
    try:
        current = _docker_ids(docker_bin, docker_host)
        created = sorted(current - baseline)
        if created:
            subprocess.run(
                [docker_bin, "--host", docker_host, "rm", "-f", *created],
                check=False,
                capture_output=True,
                timeout=60,
            )
    except Exception:
        pass


def _validate_command(command: list[str], registry: dict[str, Any], output_root: Path) -> None:
    if len(command) < 3 or Path(command[0]).name not in {"python", "python3", "python3.12"}:
        raise GateRefusal("command must use a direct foreground Python entrypoint")
    if command[1:3] != ["-u", "generate_loop.py"]:
        raise GateRefusal("command must begin: python -u generate_loop.py")
    for flag in FORBIDDEN_FLAGS:
        if flag in command:
            raise GateRefusal(f"forbidden flag: {flag}")
    missing = sorted(REQUIRED_FLAGS - set(command))
    if missing:
        raise GateRefusal(f"required flags absent: {missing}")
    if "--output_dir_parent" not in command:
        raise GateRefusal("--output_dir_parent must bind the sole released output root")
    index = command.index("--output_dir_parent")
    if index + 1 >= len(command) or Path(command[index + 1]).resolve() != output_root.resolve():
        raise GateRefusal("--output_dir_parent does not equal the released output root")
    primary = registry["fields"]["model_provider.primary"]["binding"]
    model_id = primary.get("model_id")
    for flag in ("--meta_model", "--task_model"):
        if flag not in command:
            raise GateRefusal(f"{flag} is required")
        value = command[command.index(flag) + 1]
        if value != model_id:
            raise GateRefusal(f"{flag} differs from the single bound model")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--terminal-output", type=Path)
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--source", type=Path)
    parser.add_argument("--case", type=Path)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--scratch-root", type=Path)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)

    try:
        registry = _load_json(args.registry)
        bound, blocking = _registry_state(registry)
    except Exception as exc:
        _write_terminal(
            args.terminal_output,
            {"schema_version": SCHEMA_VERSION, "terminal": "REGISTRY_REFUSED", "reason": str(exc)},
        )
        return 2

    base_terminal = {
        "schema_version": SCHEMA_VERSION,
        "arm_id": "C4_ISSUE_CENTRIC_OPTIMIZATION__ADIAS",
        "bound_field_count": len(bound),
        "blocking_field_count": len(blocking),
        "blocking_fields": blocking,
    }
    if blocking:
        _write_terminal(
            args.terminal_output,
            {**base_terminal, "terminal": "EXECUTION_REFUSED_NONBOUND_FIELDS"},
        )
        return 3
    if args.preflight_only:
        _write_terminal(args.terminal_output, {**base_terminal, "terminal": "PREFLIGHT_BOUND"})
        return 0

    try:
        if not all((args.source, args.case, args.output_root, args.scratch_root)):
            raise GateRefusal("source, case, output-root, and scratch-root are required")
        source = args.source.resolve()
        case = args.case.resolve()
        output_root = args.output_root.resolve()
        scratch_root = args.scratch_root.resolve()
        if not source.is_dir() or source.is_symlink():
            raise GateRefusal("source must be a real directory")
        if not case.is_file() or case.is_symlink():
            raise GateRefusal("case must be a real file")
        for released in (output_root, scratch_root):
            released.mkdir(parents=True, exist_ok=True)
        if output_root == scratch_root or output_root in scratch_root.parents or scratch_root in output_root.parents:
            raise GateRefusal("output and scratch roots must be disjoint")
        if case == output_root or case == scratch_root:
            raise GateRefusal("case cannot be a write root")
        command = args.command[1:] if args.command[:1] == ["--"] else args.command
        _validate_command(command, registry, output_root)

        resources = registry["bound_execution_envelope"]["resources"]
        docker_host = resources["dedicated_docker_host"]
        if docker_host in {"unix:///var/run/docker.sock", "tcp://localhost:2375"}:
            raise GateRefusal("shared/default Docker daemon is forbidden")
        if not docker_host.startswith("unix://"):
            raise GateRefusal("only a dedicated Unix Docker socket is admissible")
        docker_socket = Path(docker_host.removeprefix("unix://")).resolve()
        if scratch_root not in docker_socket.parents:
            raise GateRefusal("dedicated Docker socket must live under scratch-root")
        docker_bin = shutil.which("docker")
        if not docker_bin:
            raise GateRefusal("docker CLI absent")

        output_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="p5-c4-adias-", dir=scratch_root) as tmp:
            work = Path(tmp) / "source"
            shutil.copytree(source, work, symlinks=False)
            os.chmod(work, 0o700)
            private_home = Path(tmp) / "home"
            private_tmp = Path(tmp) / "tmp"
            private_home.mkdir(mode=0o700)
            private_tmp.mkdir(mode=0o700)
            env = {key: value for key, value in os.environ.items() if key in ENV_ALLOWLIST}
            env.update(
                {
                    "HOME": str(private_home),
                    "TMPDIR": str(private_tmp),
                    "DOCKER_HOST": docker_host,
                    "PYTHONUNBUFFERED": "1",
                    "OPENBLAS_NUM_THREADS": "1",
                }
            )
            baseline = _docker_ids(docker_bin, docker_host)
            stdout_path = output_root / "native.stdout.log"
            stderr_path = output_root / "native.stderr.log"
            started = time.monotonic()
            with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
                process = subprocess.Popen(
                    command,
                    cwd=work,
                    env=env,
                    stdin=subprocess.DEVNULL,
                    stdout=stdout,
                    stderr=stderr,
                    preexec_fn=lambda: _preexec(resources["rlimits"]),
                )
                timed_out = False
                try:
                    exit_code = process.wait(timeout=resources["whole_run_seconds"])
                except subprocess.TimeoutExpired:
                    timed_out = True
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        process.wait(timeout=resources["termination_grace_seconds"])
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
                    exit_code = 124
                finally:
                    _cleanup_new_containers(docker_bin, docker_host, baseline)
            terminal = "TIMEOUT" if timed_out else ("NATIVE_EXIT_ZERO" if exit_code == 0 else "NATIVE_EXIT_NONZERO")
            _write_terminal(
                args.terminal_output or output_root / "runner_terminal.json",
                {
                    **base_terminal,
                    "terminal": terminal,
                    "native_exit_code": exit_code,
                    "elapsed_seconds": round(time.monotonic() - started, 6),
                    "performance_inference": "FORBIDDEN",
                },
            )
            return exit_code
    except Exception as exc:
        _write_terminal(
            args.terminal_output,
            {**base_terminal, "terminal": "EXECUTION_GATE_REFUSED", "reason": str(exc)},
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
