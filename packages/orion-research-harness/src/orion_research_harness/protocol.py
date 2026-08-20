from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Mapping

REQUEST_SCHEMA = "ORION.HostCapabilityRequest.v1"
RESULT_SCHEMA = "ORION.HostCapabilityResult.v1"


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def content_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def request_id_for(session_id: str, capability: str, payload: Mapping[str, Any]) -> str:
    stable = {
        "session_id": str(session_id),
        "capability": str(capability),
        "payload": dict(payload),
    }
    return "hostreq:" + content_digest(stable)


@dataclass(frozen=True)
class CapabilityRequest:
    request_id: str
    session_id: str
    capability: str
    payload: dict[str, Any]
    created_at: str
    request_digest: str
    schema: str = REQUEST_SCHEMA

    @classmethod
    def create(
        cls,
        *,
        session_id: str,
        capability: str,
        payload: Mapping[str, Any],
    ) -> "CapabilityRequest":
        clean_payload = dict(payload)
        request_id = request_id_for(session_id, capability, clean_payload)
        created_at = utc_now()
        base = {
            "schema": REQUEST_SCHEMA,
            "request_id": request_id,
            "session_id": str(session_id),
            "capability": str(capability),
            "payload": clean_payload,
            "created_at": created_at,
        }
        return cls(
            request_id=request_id,
            session_id=str(session_id),
            capability=str(capability),
            payload=clean_payload,
            created_at=created_at,
            request_digest=content_digest(base),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "request_id": self.request_id,
            "session_id": self.session_id,
            "capability": self.capability,
            "payload": self.payload,
            "created_at": self.created_at,
            "request_digest": self.request_digest,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "CapabilityRequest":
        obj = cls(
            schema=str(raw.get("schema", "")),
            request_id=str(raw["request_id"]),
            session_id=str(raw["session_id"]),
            capability=str(raw["capability"]),
            payload=dict(raw["payload"]),
            created_at=str(raw["created_at"]),
            request_digest=str(raw["request_digest"]),
        )
        obj.validate()
        return obj

    def validate(self) -> None:
        if self.schema != REQUEST_SCHEMA:
            raise ValueError("unsupported host capability request schema")
        expected_id = request_id_for(self.session_id, self.capability, self.payload)
        if self.request_id != expected_id:
            raise ValueError("host capability request id mismatch")
        base = {
            "schema": self.schema,
            "request_id": self.request_id,
            "session_id": self.session_id,
            "capability": self.capability,
            "payload": self.payload,
            "created_at": self.created_at,
        }
        if self.request_digest != content_digest(base):
            raise ValueError("host capability request digest mismatch")


@dataclass(frozen=True)
class CapabilityResult:
    request_id: str
    request_digest: str
    success: bool
    output: Any
    error: str
    executor: str
    completed_at: str
    result_digest: str
    schema: str = RESULT_SCHEMA

    @classmethod
    def create(
        cls,
        request: CapabilityRequest,
        *,
        success: bool,
        output: Any = None,
        error: str = "",
        executor: str = "external-host",
    ) -> "CapabilityResult":
        completed_at = utc_now()
        base = {
            "schema": RESULT_SCHEMA,
            "request_id": request.request_id,
            "request_digest": request.request_digest,
            "success": bool(success),
            "output": output,
            "error": str(error),
            "executor": str(executor),
            "completed_at": completed_at,
        }
        return cls(
            request_id=request.request_id,
            request_digest=request.request_digest,
            success=bool(success),
            output=output,
            error=str(error),
            executor=str(executor),
            completed_at=completed_at,
            result_digest=content_digest(base),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "request_id": self.request_id,
            "request_digest": self.request_digest,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "executor": self.executor,
            "completed_at": self.completed_at,
            "result_digest": self.result_digest,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "CapabilityResult":
        obj = cls(
            schema=str(raw.get("schema", "")),
            request_id=str(raw["request_id"]),
            request_digest=str(raw["request_digest"]),
            success=bool(raw["success"]),
            output=raw.get("output"),
            error=str(raw.get("error", "")),
            executor=str(raw.get("executor", "")),
            completed_at=str(raw["completed_at"]),
            result_digest=str(raw["result_digest"]),
        )
        obj.validate()
        return obj

    def validate(self, request: CapabilityRequest | None = None) -> None:
        if self.schema != RESULT_SCHEMA:
            raise ValueError("unsupported host capability result schema")
        base = {
            "schema": self.schema,
            "request_id": self.request_id,
            "request_digest": self.request_digest,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "executor": self.executor,
            "completed_at": self.completed_at,
        }
        if self.result_digest != content_digest(base):
            raise ValueError("host capability result digest mismatch")
        if request is not None:
            request.validate()
            if self.request_id != request.request_id:
                raise ValueError("host capability result request id mismatch")
            if self.request_digest != request.request_digest:
                raise ValueError("host capability result request digest mismatch")
