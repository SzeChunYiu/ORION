from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping
from uuid import uuid4

from .protocol import CapabilityRequest, CapabilityResult, content_digest, utc_now

_META = ".orion-harness"
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,159}$")


def _write_json_atomic(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f".tmp-{uuid4().hex}")
    temp.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    os.replace(temp, path)


def _read_json(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text())
    if not isinstance(raw, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return raw


def _validate_id(value: str, *, name: str) -> str:
    if not _SAFE_ID.fullmatch(value):
        raise ValueError(f"invalid {name}: {value!r}")
    return value


def _disk_name(identifier: str) -> str:
    return hashlib.sha256(identifier.encode("utf-8")).hexdigest() + ".json"


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

    @property
    def campaigns_dir(self) -> Path:
        return self.meta_root / "campaigns"

    @property
    def campaign_states_dir(self) -> Path:
        return self.meta_root / "campaign-states"

    @property
    def campaign_cycles_dir(self) -> Path:
        return self.meta_root / "campaign-cycles"

    @classmethod
    def initialize(
        cls,
        root: str | Path,
        *,
        project_root: str | Path | None = None,
        allow_process_tools: bool = False,
    ) -> "ResearchWorkspace":
        root_path = Path(root).expanduser().resolve()
        project_path = Path(project_root or Path.cwd()).expanduser().resolve()
        meta = root_path / _META
        if (meta / "session.json").exists():
            return cls.load(root_path)
        session_id = "session:" + uuid4().hex
        created_at = utc_now()
        for child in (
            "requests", "results", "problems", "runs", "notes",
            "campaigns", "campaign-states", "campaign-cycles",
        ):
            (meta / child).mkdir(parents=True, exist_ok=True)
        _write_json_atomic(
            meta / "session.json",
            {
                "schema": "ORION.ResearchHarnessSession.v1",
                "session_id": session_id,
                "project_root": str(project_path),
                "created_at": created_at,
                "allow_process_tools": bool(allow_process_tools),
            },
        )
        return cls(root_path, session_id, project_path, created_at, bool(allow_process_tools))

    @classmethod
    def load(cls, root: str | Path) -> "ResearchWorkspace":
        root_path = Path(root).expanduser().resolve()
        data = _read_json(root_path / _META / "session.json")
        if data.get("schema") != "ORION.ResearchHarnessSession.v1":
            raise ValueError("unsupported ORION research harness workspace")
        return cls(
            root=root_path,
            session_id=str(data["session_id"]),
            project_root=Path(str(data["project_root"])).expanduser().resolve(),
            created_at=str(data["created_at"]),
            allow_process_tools=bool(data.get("allow_process_tools", False)),
        )

    def _request_path(self, request_id: str) -> Path:
        _validate_id(request_id, name="request_id")
        return self.requests_dir / _disk_name(request_id)

    def _result_path(self, request_id: str) -> Path:
        _validate_id(request_id, name="request_id")
        return self.results_dir / _disk_name(request_id)

    def get_or_create_request(self, *, capability: str, payload: Mapping[str, Any]) -> CapabilityRequest:
        candidate = CapabilityRequest.create(session_id=self.session_id, capability=capability, payload=payload)
        path = self._request_path(candidate.request_id)
        if path.exists():
            existing = CapabilityRequest.from_dict(_read_json(path))
            if existing.session_id != self.session_id:
                raise ValueError("request belongs to another harness session")
            return existing
        _write_json_atomic(path, candidate.as_dict())
        return candidate

    def load_request(self, request_id: str) -> CapabilityRequest:
        return CapabilityRequest.from_dict(_read_json(self._request_path(request_id)))

    def load_result(self, request_id: str) -> CapabilityResult | None:
        path = self._result_path(request_id)
        if not path.exists():
            return None
        request = self.load_request(request_id)
        result = CapabilityResult.from_dict(_read_json(path))
        result.validate(request)
        return result

    def ingest_result(
        self, request_id: str, *, success: bool, output: Any = None,
        error: str = "", executor: str = "external-host",
    ) -> CapabilityResult:
        request = self.load_request(request_id)
        result = CapabilityResult.create(request, success=success, output=output, error=error, executor=executor)
        path = self._result_path(request_id)
        if path.exists():
            existing = CapabilityResult.from_dict(_read_json(path))
            existing.validate(request)
            if existing.success != result.success or existing.output != result.output or existing.error != result.error:
                raise ValueError("result already exists with different content")
            return existing
        _write_json_atomic(path, result.as_dict())
        return result

    def pending_requests(self) -> tuple[CapabilityRequest, ...]:
        pending: list[CapabilityRequest] = []
        if not self.requests_dir.exists():
            return ()
        for path in sorted(self.requests_dir.glob("*.json")):
            request = CapabilityRequest.from_dict(_read_json(path))
            if self.load_result(request.request_id) is None:
                pending.append(request)
        return tuple(pending)

    def save_problem(
        self, *, problem_id: str, question: str, scope: str = "",
        initial_domain_ids: Iterable[str] = (), success_criteria: Iterable[str] = (),
    ) -> Path:
        problem_id = _validate_id(problem_id, name="problem_id")
        if not question.strip():
            raise ValueError("question is required")
        path = self.problems_dir / _disk_name(problem_id)
        payload = {
            "schema": "ORION.HarnessProblem.v1", "problem_id": problem_id,
            "question": question, "scope": scope,
            "initial_domain_ids": list(initial_domain_ids), "success_criteria": list(success_criteria),
        }
        if path.exists():
            existing = _read_json(path)
            if existing != payload:
                raise ValueError("problem already exists with different content")
            return path
        _write_json_atomic(path, payload)
        return path

    def load_problem(self, problem_id: str) -> dict[str, Any]:
        problem_id = _validate_id(problem_id, name="problem_id")
        data = _read_json(self.problems_dir / _disk_name(problem_id))
        if data.get("schema") != "ORION.HarnessProblem.v1":
            raise ValueError("unsupported harness problem schema")
        return data

    def problem_ids(self) -> tuple[str, ...]:
        if not self.problems_dir.exists():
            return ()
        return tuple(str(_read_json(path)["problem_id"]) for path in sorted(self.problems_dir.glob("*.json")))

    def save_run(self, run_id: str, record: Mapping[str, Any]) -> Path:
        run_id = _validate_id(run_id, name="run_id")
        path = self.runs_dir / _disk_name(run_id)
        if path.exists():
            raise ValueError(f"run already exists: {run_id}")
        _write_json_atomic(path, dict(record))
        return path

    def run_ids(self) -> tuple[str, ...]:
        if not self.runs_dir.exists():
            return ()
        return tuple(str(_read_json(path)["run_id"]) for path in sorted(self.runs_dir.glob("*.json")))

    def load_run(self, run_id: str) -> dict[str, Any]:
        run_id = _validate_id(run_id, name="run_id")
        return _read_json(self.runs_dir / _disk_name(run_id))

    def append_note(self, name: str, text: str) -> Path:
        name = _validate_id(name, name="note name")
        path = self.notes_dir / f"{name}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(text)
            if not text.endswith("\n"):
                handle.write("\n")
        return path

    def save_campaign_manifest(self, campaign_id: str, manifest: Mapping[str, Any]) -> Path:
        campaign_id = _validate_id(campaign_id, name="campaign_id")
        payload = dict(manifest)
        if str(payload.get("campaign_id", "")) != campaign_id:
            raise ValueError("campaign manifest identity mismatch")
        path = self.campaigns_dir / _disk_name(campaign_id)
        if path.exists():
            existing = _read_json(path)
            if existing != payload:
                raise ValueError("campaign manifest already frozen with different content")
            return path
        _write_json_atomic(path, payload)
        return path

    def load_campaign_manifest(self, campaign_id: str) -> dict[str, Any]:
        campaign_id = _validate_id(campaign_id, name="campaign_id")
        return _read_json(self.campaigns_dir / _disk_name(campaign_id))

    def campaign_ids(self) -> tuple[str, ...]:
        if not self.campaigns_dir.exists():
            return ()
        return tuple(str(_read_json(path)["campaign_id"]) for path in sorted(self.campaigns_dir.glob("*.json")))

    def _campaign_state_root(self, campaign_id: str) -> Path:
        campaign_id = _validate_id(campaign_id, name="campaign_id")
        return self.campaign_states_dir / hashlib.sha256(campaign_id.encode("utf-8")).hexdigest()

    def save_campaign_state(self, campaign_id: str, state: Mapping[str, Any]) -> Path:
        campaign_id = _validate_id(campaign_id, name="campaign_id")
        if str(state.get("campaign_id", "")) != campaign_id:
            raise ValueError("campaign state identity mismatch")
        cycle_index = int(state["cycle_index"])
        path = self._campaign_state_root(campaign_id) / f"{cycle_index:08d}.json"
        if path.exists():
            existing = _read_json(path)
            if existing != dict(state):
                raise ValueError("campaign cycle state already exists with different content")
            return path
        _write_json_atomic(path, dict(state))
        return path

    def load_latest_campaign_state(self, campaign_id: str) -> dict[str, Any] | None:
        root = self._campaign_state_root(campaign_id)
        paths = sorted(root.glob("*.json")) if root.exists() else []
        return None if not paths else _read_json(paths[-1])

    def save_campaign_cycle(self, campaign_id: str, transition: Mapping[str, Any]) -> Path:
        campaign_id = _validate_id(campaign_id, name="campaign_id")
        if str(transition.get("campaign_id", "")) != campaign_id:
            raise ValueError("campaign transition identity mismatch")
        cycle_index = int(transition["cycle_index"])
        root = self.campaign_cycles_dir / hashlib.sha256(campaign_id.encode("utf-8")).hexdigest()
        path = root / f"{cycle_index:08d}-{content_digest(transition)[:16]}.json"
        if path.exists():
            existing = _read_json(path)
            if existing != dict(transition):
                raise ValueError("campaign transition already exists with different content")
            return path
        _write_json_atomic(path, dict(transition))
        return path
