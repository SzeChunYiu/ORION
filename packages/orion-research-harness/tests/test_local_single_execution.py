from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace
from typing import Any


LOCAL_TOOLS = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "orion_research_harness"
    / "local_tools.py"
)


class _Workspace:
    def __init__(self) -> None:
        self.request = SimpleNamespace(capability="FILE_WRITE", payload={"content": "x"})
        self.ingested: list[dict[str, Any]] = []

    def load_request(self, request_id: str) -> SimpleNamespace:
        assert request_id == "request-1"
        return self.request

    def ingest_result(self, request_id: str, **payload: Any) -> dict[str, Any]:
        row = {"request_id": request_id, **payload}
        self.ingested.append(row)
        return row


def _load_service_function(execute_local):
    source = LOCAL_TOOLS.read_text()
    module = ast.parse(source)
    node = next(
        item
        for item in module.body
        if isinstance(item, ast.FunctionDef) and item.name == "service_local_request"
    )
    segment = ast.get_source_segment(source, node)
    assert segment is not None
    namespace = {
        "_LOCAL_CAPABILITIES": {"FILE_WRITE"},
        "execute_local": execute_local,
    }
    exec("from __future__ import annotations\n" + segment, namespace)
    return namespace["service_local_request"]


def test_serviced_request_invokes_executor_once_per_service_call() -> None:
    calls: list[tuple[str, dict[str, str]]] = []

    def execute_local(workspace, capability, payload):
        calls.append((capability, payload))
        return {"bytes_written": 1}

    workspace = _Workspace()
    service = _load_service_function(execute_local)

    result = service(workspace, "request-1")

    assert calls == [("FILE_WRITE", {"content": "x"})]
    assert result["success"] is True
    assert result["output"] == {"bytes_written": 1}
    assert len(workspace.ingested) == 1
