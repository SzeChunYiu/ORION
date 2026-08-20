from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

from .workspace import ResearchWorkspace

_LOCAL_CAPABILITIES = {
    "FILE_READ",
    "FILE_WRITE",
    "FILE_LIST",
    "SHELL",
    "PYTHON",
}


def _confined(project_root: Path, raw: str | Path) -> Path:
    candidate = (project_root / raw).resolve() if not Path(raw).is_absolute() else Path(raw).resolve()
    try:
        common = Path(os.path.commonpath([str(project_root), str(candidate)]))
    except ValueError as exc:
        raise PermissionError("path is outside project root") from exc
    if common != project_root:
        raise PermissionError("path is outside project root")
    return candidate


def _bounded_text(value: str, max_chars: int = 100_000) -> str:
    if len(value) <= max_chars:
        return value
    return value[:max_chars] + f"\n...[truncated {len(value) - max_chars} chars]"


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
        max_chars = int(payload.get("max_chars", 100_000))
        return {"path": str(path), "content": _bounded_text(path.read_text(), max_chars)}

    if capability == "FILE_WRITE":
        path = _confined(root, str(payload["path"]))
        content = str(payload.get("content", ""))
        append = bool(payload.get("append", False))
        path.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if append else "w"
        with path.open(mode, encoding="utf-8") as handle:
            handle.write(content)
        return {"path": str(path), "bytes_written": len(content.encode("utf-8")), "append": append}

    if capability == "FILE_LIST":
        path = _confined(root, str(payload.get("path", ".")))
        if not path.is_dir():
            raise NotADirectoryError(path)
        entries = sorted(child.name for child in path.iterdir())
        return {"path": str(path), "entries": entries}

    if capability in {"SHELL", "PYTHON"}:
        timeout = min(max(int(payload.get("timeout", 60)), 1), 120)
        cwd = _confined(root, str(payload.get("cwd", ".")))
        if capability == "PYTHON":
            argv = [sys.executable, "-c", str(payload["code"])]
        else:
            raw_argv = payload.get("argv")
            if not isinstance(raw_argv, list) or not raw_argv:
                raise ValueError("SHELL requires non-empty argv list; shell=True is never used")
            argv = [str(value) for value in raw_argv]
        completed = subprocess.run(
            argv,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "argv": argv,
            "cwd": str(cwd),
            "returncode": completed.returncode,
            "stdout": _bounded_text(completed.stdout),
            "stderr": _bounded_text(completed.stderr),
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
