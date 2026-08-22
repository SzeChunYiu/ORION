from __future__ import annotations

import os
import signal
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any, BinaryIO, Mapping

from .workspace import ResearchWorkspace

_LOCAL_CAPABILITIES = {"FILE_READ", "FILE_WRITE", "FILE_LIST", "SHELL", "PYTHON"}
_MAX_TEXT_CHARS = 1_000_000
_MAX_LIST_ENTRIES = 10_000
_MAX_PROCESS_OUTPUT_BYTES = 100_000
_DEFAULT_MAX_PROCESS_TIMEOUT_SECONDS = 120
_MAX_PROCESS_TIMEOUT_OVERRIDE_LIMIT_SECONDS = 600
_DRAIN_JOIN_SECONDS = 1.0


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


def _process_timeout_ceiling() -> int:
    raw = os.environ.get("ORION_HARNESS_MAX_PROCESS_TIMEOUT_SECONDS")
    if raw is None:
        return _DEFAULT_MAX_PROCESS_TIMEOUT_SECONDS
    ceiling = int(raw)
    if not 1 <= ceiling <= _MAX_PROCESS_TIMEOUT_OVERRIDE_LIMIT_SECONDS:
        raise ValueError(
            "ORION_HARNESS_MAX_PROCESS_TIMEOUT_SECONDS must be between 1 and "
            f"{_MAX_PROCESS_TIMEOUT_OVERRIDE_LIMIT_SECONDS}"
        )
    return ceiling


def _validated_process_timeout(value: Any) -> int:
    return min(max(int(value), 1), _process_timeout_ceiling())


def _read_text_bounded(path: Path, max_chars: int) -> str:
    with path.open("r", encoding="utf-8") as handle:
        value = handle.read(max_chars + 1)
    if len(value) <= max_chars:
        return value
    return value[:max_chars] + "\n...[truncated additional file content]"


def _drain_pipe(pipe: BinaryIO, output: bytearray, total: list[int], *, max_bytes: int = _MAX_PROCESS_OUTPUT_BYTES) -> None:
    try:
        while True:
            chunk = pipe.read(64 * 1024)
            if not chunk:
                return
            total[0] += len(chunk)
            remaining = max_bytes - len(output)
            if remaining > 0:
                output.extend(chunk[:remaining])
    except (OSError, ValueError):
        return
    finally:
        try:
            pipe.close()
        except (OSError, ValueError):
            pass


def _render_process_output(data: bytearray, total: int, max_bytes: int) -> str:
    text = bytes(data).decode("utf-8", errors="replace")
    if total > max_bytes:
        text += f"\n...[truncated {total - max_bytes} bytes]"
    return text


def _terminate_process_tree(process: subprocess.Popen[bytes]) -> None:
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
            return
        except ProcessLookupError:
            return
    if process.poll() is None:
        process.kill()


def _finish_drainers(process: subprocess.Popen[bytes], threads: tuple[threading.Thread, threading.Thread]) -> None:
    for thread in threads:
        thread.join(timeout=_DRAIN_JOIN_SECONDS)
    if any(thread.is_alive() for thread in threads):
        _terminate_process_tree(process)
        for pipe in (process.stdout, process.stderr):
            if pipe is not None:
                try:
                    pipe.close()
                except (OSError, ValueError):
                    pass
        for thread in threads:
            thread.join(timeout=0.1)


def execute_local(workspace: ResearchWorkspace, capability: str, payload: Mapping[str, Any]) -> Any:
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
        return {"path": str(path), "bytes_written": len(content.encode("utf-8")), "append": append}

    if capability == "FILE_LIST":
        path = _confined(root, str(payload.get("path", ".")))
        if not path.is_dir():
            raise NotADirectoryError(path)
        entries: list[str] = []
        with os.scandir(path) as iterator:
            for entry in iterator:
                if len(entries) >= _MAX_LIST_ENTRIES:
                    raise OverflowError(f"directory exceeds {_MAX_LIST_ENTRIES} entries; narrow the listing scope")
                entries.append(entry.name)
        entries.sort()
        return {"path": str(path), "entries": entries}

    if capability in {"SHELL", "PYTHON"}:
        if not workspace.allow_process_tools:
            raise PermissionError(
                "SHELL/PYTHON local execution is disabled for this workspace; "
                "reinitialize with --allow-process-tools to opt in"
            )
        timeout = _validated_process_timeout(payload.get("timeout", 60))
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

        process = subprocess.Popen(
            argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL, start_new_session=(os.name == "posix"),
        )
        assert process.stdout is not None and process.stderr is not None
        stdout_buffer=bytearray();stderr_buffer=bytearray();stdout_total=[0];stderr_total=[0]
        stdout_thread=threading.Thread(target=_drain_pipe,args=(process.stdout,stdout_buffer,stdout_total),daemon=True)
        stderr_thread=threading.Thread(target=_drain_pipe,args=(process.stderr,stderr_buffer,stderr_total),daemon=True)
        threads=(stdout_thread,stderr_thread)
        for thread in threads: thread.start()
        try:
            returncode=process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            _terminate_process_tree(process)
            try: process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                process.kill();process.wait()
            _finish_drainers(process,threads)
            raise
        _finish_drainers(process,threads)
        return {
            "argv":argv,"cwd":str(cwd),"returncode":returncode,
            "stdout":_render_process_output(stdout_buffer,stdout_total[0],_MAX_PROCESS_OUTPUT_BYTES),
            "stderr":_render_process_output(stderr_buffer,stderr_total[0],_MAX_PROCESS_OUTPUT_BYTES),
            "sandboxed":False,
        }
    raise AssertionError(capability)


def service_local_request(workspace: ResearchWorkspace, request_id: str):
    request=workspace.load_request(request_id)
    if request.capability not in _LOCAL_CAPABILITIES:
        raise KeyError(f"{request.capability} requires an external host")
    try:
        output=execute_local(workspace,request.capability,request.payload)
    except Exception as exc:
        return workspace.ingest_result(request_id,success=False,error=f"{type(exc).__name__}: {exc}",executor="orion-harness-local")
    if request.capability in {"SHELL","PYTHON"}:
        returncode=output.get("returncode") if isinstance(output,Mapping) else None
        if not isinstance(returncode,int):
            return workspace.ingest_result(request_id,success=False,output=output,error="local process result is missing an integer returncode",executor="orion-harness-local")
        if returncode!=0:
            return workspace.ingest_result(request_id,success=False,output=output,error=f"local process exited with status {returncode}",executor="orion-harness-local")
    return workspace.ingest_result(request_id,success=True,output=output,executor="orion-harness-local")
