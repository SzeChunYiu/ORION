from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, BinaryIO, Mapping

from .workspace import ResearchWorkspace

_LOCAL_CAPABILITIES = {
    "FILE_READ",
    "FILE_WRITE",
    "FILE_LIST",
    "SHELL",
    "PYTHON",
}
_MAX_TEXT_CHARS = 1_000_000
_MAX_PROCESS_OUTPUT_BYTES = 100_000


def _confined(project_root: Path, raw: str | Path) -> Path:
    candidate = (project_root / raw).resolve() if not Path(raw).is_absolute() else Path(raw).resolve()
    try:
        common = Path(os.path.commonpath([str(project_root), str(candidate)]))
    except ValueError as exc:
        raise PermissionError("path is outside project root") from exc
    if common != project_root:
        raise PermissionError("path is outside project root")
    return candidate


def _validated_max_chars(value: Any) -> int:
    max_chars = int(value)
    if max_chars < 1 or max_chars > _MAX_TEXT_CHARS:
        raise ValueError(f"max_chars must be between 1 and {_MAX_TEXT_CHARS}")
    return max_chars


def _read_text_bounded(path: Path, max_chars: int) -> str:
    with path.open("r", encoding="utf-8") as handle:
        value = handle.read(max_chars + 1)
    if len(value) <= max_chars:
        return value
    return value[:max_chars] + "\n...[truncated additional file content]"


def _read_process_output(handle: BinaryIO, max_bytes: int = _MAX_PROCESS_OUTPUT_BYTES) -> str:
    handle.seek(0, os.SEEK_END)
    total = handle.tell()
    handle.seek(0)
    data = handle.read(max_bytes)
    text = data.decode("utf-8", errors="replace")
    if total > max_bytes:
        text += f"\n...[truncated {total - max_bytes} bytes]"
    return text


def execute_local(
    workspace: ResearchWorkspace,
    capability: str,
    payload: Mapping[str, Any],
) -> Any:
    capability = str(capability)
    if capability not in _LOCAL_CAPABILITIES:
        raise KeyError(f"not a local capability: {capability}")
    root = workspace.project_root

    if capability == "FILE_READ":
        path = _confined(root, str(payload["path"]))
        max_chars = _validated_max_chars(payload.get("max_chars", 100_000))
        return {"path": str(path), "content": _read_text_bounded(path, max_chars)}

    if capability == "FILE_WRITE":
        path = _confined(root, str(payload["path"]))
        content = str(payload.get("content", ""))
        append = bool(payload.get("append", False))
        path.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if append else "w"
        with path.open(mode, encoding="utf-8") as handle:
            handle.write(content)
        return {
            "path": str(path),
            "bytes_written": len(content.encode("utf-8")),
            "append": append,
        }

    if capability == "FILE_LIST":
        path = _confined(root, str(payload.get("path", ".")))
        if not path.is_dir():
            raise NotADirectoryError(path)
        entries = sorted(child.name for child in path.iterdir())
        return {"path": str(path), "entries": entries}

    if capability in {"SHELL", "PYTHON"}:
        if not workspace.allow_process_tools:
            raise PermissionError(
                "SHELL/PYTHON local execution is disabled for this workspace; "
                "reinitialize with --allow-process-tools to opt in"
            )
        timeout = min(max(int(payload.get("timeout", 60)), 1), 120)
        cwd = _confined(root, str(payload.get("cwd", ".")))
        if not cwd.is_dir():
            raise NotADirectoryError(cwd)
        if capability == "PYTHON":
            argv = [sys.executable, "-c", str(payload["code"])]
        else:
            raw_argv = payload.get("argv")
            if not isinstance(raw_argv, list) or not raw_argv:
                raise ValueError("SHELL requires non-empty argv list; shell=True is never used")
            argv = [str(value) for value in raw_argv]

        with tempfile.TemporaryFile() as stdout_file, tempfile.TemporaryFile() as stderr_file:
            process = subprocess.Popen(
                argv,
                cwd=cwd,
                stdout=stdout_file,
                stderr=stderr_file,
                stdin=subprocess.DEVNULL,
            )
            try:
                returncode = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                raise
            stdout = _read_process_output(stdout_file)
            stderr = _read_process_output(stderr_file)

        return {
            "argv": argv,
            "cwd": str(cwd),
            "returncode": returncode,
            "stdout": stdout,
            "stderr": stderr,
            "sandboxed": False,
        }

    raise AssertionError(capability)


def service_local_request(workspace: ResearchWorkspace, request_id: str):
    request = workspace.load_request(request_id)
    if request.capability not in _LOCAL_CAPABILITIES:
        raise KeyError(f"{request.capability} requires an external host")
    try:
        output = execute_local(workspace, request.capability, request.payload)
    except Exception as exc:
        return workspace.ingest_result(
            request_id,
            success=False,
            error=f"{type(exc).__name__}: {exc}",
            executor="orion-harness-local",
        )
    return workspace.ingest_result(
        request_id,
        success=True,
        output=output,
        executor="orion-harness-local",
    )
