from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


def run_lean(
    checkout: Path,
    path: Path,
    timeout: int,
) -> subprocess.CompletedProcess[str]:
    """Run Lean with structured JSON diagnostics/traces.

    The scientific extractor remains unchanged; this transport only replaces
    parsing of human-formatted CLI text with Lean's native SerialMessage JSON.
    """
    return subprocess.run(
        ["lake", "env", "lean", "--json", str(path)],
        cwd=checkout,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def parse_messages(output: str) -> list[dict[str, Any]]:
    """Parse newline-delimited Lean SerialMessage JSON conservatively.

    Non-JSON lines may come from the launcher/runtime and are ignored. Only
    messages with a valid structured position and a known Lean severity are
    admitted. Line numbers are preserved exactly for the frozen trace-line
    receipt join performed by ``states_from_messages``.
    """
    messages: list[dict[str, Any]] = []
    severity_map = {
        "information": "info",
        "warning": "warning",
        "error": "error",
    }
    for raw in output.splitlines():
        line = raw.strip()
        if not line.startswith("{"):
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(record, dict):
            continue
        kind = severity_map.get(str(record.get("severity", "")))
        pos = record.get("pos")
        if kind is None or not isinstance(pos, dict):
            continue
        source_line = pos.get("line")
        source_column = pos.get("column")
        if not isinstance(source_line, int) or not isinstance(source_column, int):
            continue
        data = record.get("data")
        if not isinstance(data, str):
            continue
        messages.append(
            {
                "line": source_line,
                "column": source_column,
                "kind": kind,
                "content": data.strip(),
            }
        )
    return messages


def assert_transport_contract() -> None:
    """Fail closed if the expected Lean JSON receipt shape stops parsing."""
    sample = json.dumps(
        {
            "severity": "information",
            "pos": {"line": 17, "column": 4},
            "kind": "[anonymous]",
            "keepFullRange": False,
            "isSilent": False,
            "fileName": "/tmp/Example.lean",
            "endPos": {"line": 17, "column": 15},
            "data": "x : Nat\n⊢ x = x",
            "caption": "",
        },
        separators=(",", ":"),
    )
    parsed = parse_messages(sample)
    expected = [
        {
            "line": 17,
            "column": 4,
            "kind": "info",
            "content": "x : Nat\n⊢ x = x",
        }
    ]
    if parsed != expected:
        raise RuntimeError(f"Lean JSON transport contract failed: {parsed!r}")


if __name__ == "__main__":
    assert_transport_contract()
    print("P10_LEAN_JSON_TRANSPORT_GREEN")
