from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping
from uuid import uuid4

from .protocol import (
    CapabilityRequest,
    CapabilityResult,
    canonical_json,
    content_digest,
    utc_now,
)

_META = ".orion-harness"
_SESSION_SCHEMA_V1 = "ORION.ResearchHarnessSession.v1"
_SESSION_SCHEMA_V2 = "ORION.ResearchHarnessSession.v2"
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,159}$")


def _serialized_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _write_json_create(path: Path, value: Mapping[str, Any]) -> bool:
    """Publish one immutable JSON object without ever replacing an existing object.

    The payload is fully written and fsynced to a same-directory temporary file before
    `os.link` atomically publishes the destination name. Competing publishers therefore
    cannot overwrite a deterministic identity or observe a partial JSON file.
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f".tmp-{uuid4().hex}")
    try:
        with temp.open("x", encoding="utf-8") as handle:
            handle.write(_serialized_json(value))
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temp, path)
        except FileExistsError:
            return False
        return True
    finally:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass


def _read_json(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text())
    if not isinstance(raw, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return raw


def _validate_id(value: str, *, name: str) -> str:
    if not isinstance(value, str) or not _SAFE_ID.fullmatch(value):
        raise ValueError(f"invalid {name}: {value!r}")
    return value


def _disk_name(identifier: str) -> str:
    return hashlib.sha256(identifier.encode("utf-8")).hexdigest() + ".json"


def _session_base(
    *,
    session_id: str,
    project_root: str,
    created_at: str,
    allow_process_tools: bool,
) -> dict[str, Any]:
    return {
        "schema": _SESSION_SCHEMA_V2,
        "session_id": session_id,
        "project_root": project_root,
        "created_at": created_at,
        "allow_process_tools": allow_process_tools,
    }


def _session_payload(
    *,
    session_id: str,
    project_root: str,
    created_at: str,
    allow_process_tools: bool,
) -> dict[str, Any]:
    base = _session_base(
        session_id=session_id,
        project_root=project_root,
        created_at=created_at,
        allow_process_tools=allow_process_tools,
    )
    return {**base, "session_digest": content_digest(base)}


def _strict_session_fields(data: Mapping[str, Any]) -> tuple[str, str, str, bool]:
    session_id = data.get("session_id")
    project_root = data.get("project_root")
    created_at = data.get("created_at")
    allow_process_tools = data.get("allow_process_tools", False)
    if not isinstance(session_id, str):
        raise TypeError("session_id must be a string")
    _validate_id(session_id, name="session_id")
    if not isinstance(project_root, str) or not project_root.strip():
        raise TypeError("project_root must be a non-empty string")
    if not isinstance(created_at, str) or not created_at.strip():
        raise TypeError("created_at must be a non-empty string")
    if not isinstance(allow_process_tools, bool):
        raise TypeError("allow_process_tools must be a boolean")
    return session_id, project_root, created_at, allow_process_tools


@dataclass(frozen=True)
class ResearchWorkspace:
    root: Path
    session_id: str
    project_root: Path
    created_at: str
    allow_process_tools: bool = False

    @property
    def meta_root(self) -> Path:
        return self.root / _META

    @property
    def requests_dir(self) -> Path:
        return self.meta_root / "requests"

    @property
    def results_dir(self) -> Path:
        return self.meta_root / "results"

    @property
    def problems_dir(self) -> Path:
        return self.meta_root / "problems"

    @property
    def runs_dir(self) -> Path:
        return self.meta_root / "runs"

    @property
    def notes_dir(self) -> Path:
        return self.meta_root / "notes"

    @classmethod
    def initialize(
        cls,
        root: str | Path,
        *,
        project_root: str | Path | None = None,
        allow_process_tools: bool = False,
    ) -> "ResearchWorkspace":
        if not isinstance(allow_process_tools, bool):
            raise TypeError("allow_process_tools must be a boolean")
        root_path = Path(root).expanduser().resolve()
        project_path = Path(project_root or Path.cwd()).expanduser().resolve()
        meta = root_path / _META
        session_path = meta / "session.json"
        if session_path.exists():
            return cls.load(root_path)
        session_id = "session:" + uuid4().hex
        created_at = utc_now()
        for child in ("requests", "results", "problems", "runs", "notes"):
            (meta / child).mkdir(parents=True, exist_ok=True)
        payload = _session_payload(
            session_id=session_id,
            project_root=str(project_path),
            created_at=created_at,
            allow_process_tools=allow_process_tools,
        )
        if not _write_json_create(session_path, payload):
            return cls.load(root_path)
        return cls(root_path, session_id, project_path, created_at, allow_process_tools)

    @classmethod
    def load(cls, root: str | Path) -> "ResearchWorkspace":
        root_path = Path(root).expanduser().resolve()
        data = _read_json(root_path / _META / "session.json")
        schema = data.get("schema")
        if not isinstance(schema, str):
            raise TypeError("session schema must be a string")
        if schema not in {_SESSION_SCHEMA_V1, _SESSION_SCHEMA_V2}:
            raise ValueError("unsupported ORION research harness workspace")
        session_id, project_root_raw, created_at, allow_process_tools = _strict_session_fields(data)
        if schema == _SESSION_SCHEMA_V2:
            session_digest = data.get("session_digest")
            if not isinstance(session_digest, str):
                raise TypeError("session_digest must be a string")
            base = _session_base(
                session_id=session_id,
                project_root=project_root_raw,
                created_at=created_at,
                allow_process_tools=allow_process_tools,
            )
            if session_digest != content_digest(base):
                raise ValueError("research harness session digest mismatch")
        return cls(
            root=root_path,
            session_id=session_id,
            project_root=Path(project_root_raw).expanduser().resolve(),
            created_at=created_at,
            allow_process_tools=allow_process_tools,
        )

    def _request_path(self, request_id: str) -> Path:
        _validate_id(request_id, name="request_id")
        return self.requests_dir / _disk_name(request_id)

    def _result_path(self, request_id: str) -> Path:
        _validate_id(request_id, name="request_id")
        return self.results_dir / _disk_name(request_id)

    def _validated_existing_request(
        self, path: Path, candidate: CapabilityRequest
    ) -> CapabilityRequest:
        existing = CapabilityRequest.from_dict(_read_json(path))
        if existing.session_id != self.session_id:
            raise ValueError("request belongs to another harness session")
        if (
            existing.capability != candidate.capability
            or canonical_json(existing.payload) != canonical_json(candidate.payload)
        ):
            raise ValueError("deterministic request identity collision")
        return existing

    def get_or_create_request(
        self,
        *,
        capability: str,
        payload: Mapping[str, Any],
    ) -> CapabilityRequest:
        candidate = CapabilityRequest.create(
            session_id=self.session_id,
            capability=str(capability),
            payload=dict(payload),
        )
        path = self._request_path(candidate.request_id)
        if path.exists():
            return self._validated_existing_request(path, candidate)
        if _write_json_create(path, candidate.as_dict()):
            return candidate
        return self._validated_existing_request(path, candidate)

    def load_request(self, request_id: str) -> CapabilityRequest:
        request = CapabilityRequest.from_dict(_read_json(self._request_path(request_id)))
        if request.session_id != self.session_id:
            raise ValueError("request belongs to another harness session")
        return request

    def load_result(self, request_id: str) -> CapabilityResult | None:
        path = self._result_path(request_id)
        if not path.exists():
            return None
        request = self.load_request(request_id)
        result = CapabilityResult.from_dict(_read_json(path))
        result.validate(request)
        return result

    @staticmethod
    def _validated_existing_result(
        path: Path,
        request: CapabilityRequest,
        candidate: CapabilityResult,
    ) -> CapabilityResult:
        existing = CapabilityResult.from_dict(_read_json(path))
        existing.validate(request)
        if (
            existing.success != candidate.success
            or canonical_json(existing.output) != canonical_json(candidate.output)
            or existing.error != candidate.error
            or existing.executor != candidate.executor
        ):
            raise ValueError("result already exists with different content or executor")
        return existing

    def ingest_result(
        self,
        request_id: str,
        *,
        success: bool,
        output: Any = None,
        error: str = "",
        executor: str = "external-host",
    ) -> CapabilityResult:
        request = self.load_request(request_id)
        candidate = CapabilityResult.create(
            request,
            success=success,
            output=output,
            error=error,
            executor=executor,
        )
        path = self._result_path(request_id)
        if path.exists():
            return self._validated_existing_result(path, request, candidate)
        if _write_json_create(path, candidate.as_dict()):
            return candidate
        return self._validated_existing_result(path, request, candidate)

    def pending_requests(self) -> tuple[CapabilityRequest, ...]:
        pending: list[CapabilityRequest] = []
        if not self.requests_dir.exists():
            return ()
        for path in sorted(self.requests_dir.glob("*.json")):
            request = CapabilityRequest.from_dict(_read_json(path))
            if request.session_id != self.session_id:
                raise ValueError("request belongs to another harness session")
            if self.load_result(request.request_id) is None:
                pending.append(request)
        return tuple(pending)

    def save_problem(
        self,
        *,
        problem_id: str,
        question: str,
        scope: str = "",
        initial_domain_ids: Iterable[str] = (),
        success_criteria: Iterable[str] = (),
    ) -> Path:
        problem_id = _validate_id(problem_id, name="problem_id")
        if not question.strip():
            raise ValueError("question is required")
        path = self.problems_dir / _disk_name(problem_id)
        payload = {
            "schema": "ORION.HarnessProblem.v1",
            "problem_id": problem_id,
            "question": question,
            "scope": scope,
            "initial_domain_ids": list(initial_domain_ids),
            "success_criteria": list(success_criteria),
        }
        if path.exists():
            existing = _read_json(path)
            if existing != payload:
                raise ValueError("problem already exists with different content")
            return path
        if _write_json_create(path, payload):
            return path
        existing = _read_json(path)
        if existing != payload:
            raise ValueError("problem already exists with different content")
        return path

    def load_problem(self, problem_id: str) -> dict[str, Any]:
        problem_id = _validate_id(problem_id, name="problem_id")
        data = _read_json(self.problems_dir / _disk_name(problem_id))
        if data.get("schema") != "ORION.HarnessProblem.v1":
            raise ValueError("unsupported harness problem schema")
        if data.get("problem_id") != problem_id:
            raise ValueError("harness problem identity mismatch")
        return data

    def problem_ids(self) -> tuple[str, ...]:
        if not self.problems_dir.exists():
            return ()
        return tuple(str(_read_json(path)["problem_id"]) for path in sorted(self.problems_dir.glob("*.json")))

    def save_run(self, run_id: str, record: Mapping[str, Any]) -> Path:
        run_id = _validate_id(run_id, name="run_id")
        path = self.runs_dir / _disk_name(run_id)
        payload = dict(record)
        if payload.get("run_id", run_id) != run_id:
            raise ValueError("run record identity mismatch")
        if not _write_json_create(path, payload):
            raise ValueError(f"run already exists: {run_id}")
        return path

    def run_ids(self) -> tuple[str, ...]:
        if not self.runs_dir.exists():
            return ()
        return tuple(str(_read_json(path)["run_id"]) for path in sorted(self.runs_dir.glob("*.json")))

    def load_run(self, run_id: str) -> dict[str, Any]:
        run_id = _validate_id(run_id, name="run_id")
        data = _read_json(self.runs_dir / _disk_name(run_id))
        if data.get("run_id") != run_id:
            raise ValueError("run record identity mismatch")
        return data

    def append_note(self, name: str, text: str) -> Path:
        name = _validate_id(name, name="note name")
        path = self.notes_dir / f"{name}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(text)
            if not text.endswith("\n"):
                handle.write("\n")
        return path
