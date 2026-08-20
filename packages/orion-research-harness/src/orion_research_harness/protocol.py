from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Mapping

REQUEST_SCHEMA = "ORION.HostCapabilityRequest.v1"
RESULT_SCHEMA = "ORION.HostCapabilityResult.v1"
_HEX = set("0123456789abcdef")


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def content_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _require_string(raw: Mapping[str, Any], key: str, *, nonempty: bool = True) -> str:
    value = raw.get(key)
    if not isinstance(value, str):
        raise TypeError(f"{key} must be a string")
    if nonempty and not value.strip():
        raise ValueError(f"{key} must be non-empty")
    return value


def _validate_digest(value: str, *, name: str) -> None:
    if len(value) != 64 or any(character not in _HEX for character in value):
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")


def request_id_for(session_id: str, capability: str, payload: Mapping[str, Any]) -> str:
    if not isinstance(session_id, str) or not session_id.strip():
        raise ValueError("session_id must be a non-empty string")
    if not isinstance(capability, str) or not capability.strip():
        raise ValueError("capability must be a non-empty string")
    if not isinstance(payload, Mapping):
        raise TypeError("payload must be an object")
    stable = {
        "session_id": session_id,
        "capability": capability,
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
        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError("session_id must be a non-empty string")
        if not isinstance(capability, str) or not capability.strip():
            raise ValueError("capability must be a non-empty string")
        if not isinstance(payload, Mapping):
            raise TypeError("payload must be an object")
        clean_payload = dict(payload)
        request_id = request_id_for(session_id, capability, clean_payload)
        created_at = utc_now()
        base = {
            "schema": REQUEST_SCHEMA,
            "request_id": request_id,
            "session_id": session_id,
            "capability": capability,
            "payload": clean_payload,
            "created_at": created_at,
        }
        obj = cls(
            request_id=request_id,
            session_id=session_id,
            capability=capability,
            payload=clean_payload,
            created_at=created_at,
            request_digest=content_digest(base),
        )
        obj.validate()
        return obj

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
        if not isinstance(raw, Mapping):
            raise TypeError("host capability request must be an object")
        payload = raw.get("payload")
        if not isinstance(payload, Mapping):
            raise TypeError("payload must be an object")
        obj = cls(
            schema=_require_string(raw, "schema"),
            request_id=_require_string(raw, "request_id"),
            session_id=_require_string(raw, "session_id"),
            capability=_require_string(raw, "capability"),
            payload=dict(payload),
            created_at=_require_string(raw, "created_at"),
            request_digest=_require_string(raw, "request_digest"),
        )
        obj.validate()
        return obj

    def validate(self) -> None:
        if self.schema != REQUEST_SCHEMA:
            raise ValueError("unsupported host capability request schema")
        if not self.session_id.strip() or not self.capability.strip():
            raise ValueError("request session and capability are required")
        _validate_digest(self.request_digest, name="request_digest")
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
        request.validate()
        if not isinstance(success, bool):
            raise TypeError("success must be a boolean")
        if not isinstance(error, str):
            raise TypeError("error must be a string")
        if success and error:
            raise ValueError("successful result cannot carry an error")
        if not isinstance(executor, str) or not executor.strip():
            raise ValueError("executor must be a non-empty string")
        completed_at = utc_now()
        base = {
            "schema": RESULT_SCHEMA,
            "request_id": request.request_id,
            "request_digest": request.request_digest,
            "success": success,
            "output": output,
            "error": error,
            "executor": executor,
            "completed_at": completed_at,
        }
        obj = cls(
            request_id=request.request_id,
            request_digest=request.request_digest,
            success=success,
            output=output,
            error=error,
            executor=executor,
            completed_at=completed_at,
            result_digest=content_digest(base),
        )
        obj.validate(request)
        return obj

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
        if not isinstance(raw, Mapping):
            raise TypeError("host capability result must be an object")
        success = raw.get("success")
        if not isinstance(success, bool):
            raise TypeError("success must be a boolean")
        error = raw.get("error", "")
        if not isinstance(error, str):
            raise TypeError("error must be a string")
        obj = cls(
            schema=_require_string(raw, "schema"),
            request_id=_require_string(raw, "request_id"),
            request_digest=_require_string(raw, "request_digest"),
            success=success,
            output=raw.get("output"),
            error=error,
            executor=_require_string(raw, "executor"),
            completed_at=_require_string(raw, "completed_at"),
            result_digest=_require_string(raw, "result_digest"),
        )
        obj.validate()
        return obj

    def validate(self, request: CapabilityRequest | None = None) -> None:
        if self.schema != RESULT_SCHEMA:
            raise ValueError("unsupported host capability result schema")
        if not isinstance(self.success, bool):
            raise TypeError("success must be a boolean")
        if self.success and self.error:
            raise ValueError("successful result cannot carry an error")
        if not self.executor.strip():
            raise ValueError("executor must be non-empty")
        _validate_digest(self.request_digest, name="request_digest")
        _validate_digest(self.result_digest, name="result_digest")
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
