from __future__ import annotations

import copy

import pytest

from orion_research_harness.protocol import CapabilityRequest, CapabilityResult


def _request() -> CapabilityRequest:
    return CapabilityRequest.create(
        session_id="session:strict",
        capability="CUSTOM",
        payload={"x": 1},
    )


def test_request_schema_rejects_type_coercion():
    request = _request()
    raw = request.as_dict()
    bad = copy.deepcopy(raw)
    bad["capability"] = 7
    with pytest.raises(TypeError, match="capability must be a string"):
        CapabilityRequest.from_dict(bad)

    bad = copy.deepcopy(raw)
    bad["payload"] = ["not", "an", "object"]
    with pytest.raises(TypeError, match="payload must be an object"):
        CapabilityRequest.from_dict(bad)


def test_result_schema_rejects_truthy_string_success_and_empty_executor():
    request = _request()
    result = CapabilityResult.create(
        request,
        success=False,
        error="failed",
        executor="host",
    )
    raw = result.as_dict()

    bad = copy.deepcopy(raw)
    bad["success"] = "false"
    with pytest.raises(TypeError, match="success must be a boolean"):
        CapabilityResult.from_dict(bad)

    bad = copy.deepcopy(raw)
    bad["executor"] = ""
    with pytest.raises(ValueError, match="executor must be non-empty"):
        CapabilityResult.from_dict(bad)


def test_result_creation_requires_real_boolean_and_executor_identity():
    request = _request()
    with pytest.raises(TypeError, match="success must be a boolean"):
        CapabilityResult.create(request, success=1, executor="host")
    with pytest.raises(ValueError, match="executor must be a non-empty string"):
        CapabilityResult.create(request, success=True, executor="")


def test_successful_result_cannot_carry_error_text():
    request = _request()
    with pytest.raises(ValueError, match="successful result cannot carry an error"):
        CapabilityResult.create(
            request,
            success=True,
            output={"ok": True},
            error="contradictory",
            executor="host",
        )
