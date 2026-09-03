#!/usr/bin/env python3
"""Deterministic intervention transforms for the A4 hidden-cause study.

Implements exactly the two static context transforms frozen by
A4_INTERVENTION_PREREG_V1.json (this directory):

  INFORMATION   append ``metadata.solution_steps`` verbatim as a context block
  ACCESSIBILITY serve the task's ``usage_tool_protocol`` through the gym's
                text-ReAct channel (native tools channel omitted), with the
                frozen access-path instruction prepended

COMPUTATION (rounds cap 50 -> 100) and RECONSTRUCTION (one registered replan:
context cleared, task re-served fresh, remaining budget) change no context
bytes; they are episode-structure arms operationalised in the run harness and
are deliberately NOT implemented here.

Pure functions over a dataset record dict. No model calls, no network, no
randomness. Grounding citations live in A4_INTERVENTION_PREREG_V1.json.

Usage:
  a4_intervention_transforms_v1.py --self-test
  a4_intervention_transforms_v1.py --verify-dataset multi.json single.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Optional

# --- frozen template bytes -------------------------------------------------

INFORMATION_HEADER = "### Reference solution steps (benchmark-provided, verbatim)\n"

# The text tool-call format documented by the pinned gym itself
# (gym/test_executor.py::_parse_glm_text_tool_calls, lines 638-737:
#  "Action: tool_name" followed by <arg_key>/<arg_value> pairs, optionally
#  closed by </tool_call>).  The instruction block is the only added text in
# the ACCESSIBILITY arm; the protocol block below it is the task's own bytes.
ACCESSIBILITY_INSTRUCTION = (
    "### Tool access via text protocol\n"
    "Tools are NOT offered through the native function-calling channel in this run.\n"
    "The complete tool protocol for this task is provided verbatim below.\n"
    "To call a tool, emit exactly this text format:\n"
    "Action: <tool_name>\n"
    "<arg_key>parameter_name</arg_key>\n"
    "<arg_value>value</arg_value>\n"
    "(one arg_key/arg_value pair per parameter, then optionally </tool_call>)\n"
    "The evaluation system parses this text and returns the tool result as an\n"
    "Observation, exactly as in the gym's ReAct flow.\n"
    "Verbatim tool protocol (object-identical to usage_tool_protocol):\n"
)


def information_block(record: Dict[str, Any]) -> Optional[str]:
    """INFORMATION arm context block, or None when the arm is vacuous.

    Frozen rule: expose ``metadata.solution_steps`` verbatim (the benchmark's
    reference solution steps), nothing else.  Records without a non-empty
    ``metadata.solution_steps`` make the arm vacuous for that task
    (pre-declared terminal INFORMATION_ITEM_ABSENT in the prereg).
    """
    steps = (record.get("metadata") or {}).get("solution_steps")
    if not steps:
        return None
    return INFORMATION_HEADER + json.dumps(steps, ensure_ascii=False)


def accessibility_block(record: Dict[str, Any]) -> Optional[str]:
    """ACCESSIBILITY arm context block, or None when the arm is vacuous.

    Frozen rule: frozen instruction block + the task's ``usage_tool_protocol``
    serialized deterministically (ensure_ascii=False).  The native tools
    parameter is omitted by the harness in this arm; tool calls arrive as
    Action-text and route through the unchanged run_tool_call path.
    """
    protocols = record.get("usage_tool_protocol")
    if not protocols:
        return None
    return ACCESSIBILITY_INSTRUCTION + json.dumps(protocols, ensure_ascii=False)


def accessibility_protocol_roundtrip(block: str) -> Any:
    """Inverse of the protocol serialization (checker/self-test helper)."""
    marker = "Verbatim tool protocol (object-identical to usage_tool_protocol):\n"
    idx = block.index(marker) + len(marker)
    return json.loads(block[idx:])


def information_roundtrip(block: str) -> Any:
    """Inverse of the solution_steps serialization (checker/self-test helper)."""
    return json.loads(block[len(INFORMATION_HEADER):])


# --- verification -----------------------------------------------------------

def verify_dataset(paths: list[Path]) -> int:
    total_info = 0
    total_rec = 0
    failures: list[str] = []
    for p in paths:
        records = json.loads(p.read_text())
        n_info = 0
        for rec in records:
            total_rec += 1
            ib = information_block(rec)
            if ib is not None:
                n_info += 1
                total_info += 1
                if information_roundtrip(ib) != rec["metadata"]["solution_steps"]:
                    failures.append(f"{p.name}:{rec.get('id')}: information round-trip mismatch")
            ab = accessibility_block(rec)
            if ab is None:
                failures.append(f"{p.name}:{rec.get('id')}: no usage_tool_protocol (accessibility vacuous)")
                continue
            if accessibility_protocol_roundtrip(ab) != rec["usage_tool_protocol"]:
                failures.append(f"{p.name}:{rec.get('id')}: accessibility round-trip mismatch")
            # determinism: byte-identical on recomputation
            if accessibility_block(rec) != ab or (
                ib is not None and information_block(rec) != ib
            ):
                failures.append(f"{p.name}:{rec.get('id')}: transform not deterministic")
        print(f"{p.name}: records={len(records)} information_defined={n_info}")
    print(f"TOTAL: records={total_rec} information_defined={total_info}")
    if failures:
        for f in failures:
            print("FAIL:", f)
        return 1
    print("A4_INTERVENTION_TRANSFORMS_VERIFY_GREEN")
    return 0


def self_test() -> None:
    synthetic = {
        "id": "single:1",
        "question": "What is 1+1?",
        "metadata": {
            "subject": "Statistics",
            "topic": "Arithmetic",
            "tool_expected": ["add"],
            "golden_answer": [{"numerical": 2}],
            "solution_steps": ["call add(1,1)", "report the result"],
        },
        "usage_tool_protocol": [
            {
                "type": "function",
                "function": {
                    "name": "add",
                    "description": "Add two numbers.",
                    "strict": True,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "a": {"type": "number", "description": "first"},
                            "b": {"type": "number", "description": "second"},
                        },
                        "required": ["a", "b"],
                    },
                },
                "additionalProperties": {"function_path": "./tools/add.py"},
            }
        ],
    }

    ib = information_block(synthetic)
    assert ib is not None and ib.startswith(INFORMATION_HEADER)
    assert information_roundtrip(ib) == synthetic["metadata"]["solution_steps"]

    ab = accessibility_block(synthetic)
    assert ab is not None and ab.startswith(ACCESSIBILITY_INSTRUCTION)
    assert accessibility_protocol_roundtrip(ab) == synthetic["usage_tool_protocol"]

    # determinism
    assert accessibility_block(synthetic) == ab
    assert information_block(synthetic) == ib

    # vacuity: no solution_steps -> INFORMATION undefined
    no_steps = json.loads(json.dumps(synthetic))
    del no_steps["metadata"]["solution_steps"]
    assert information_block(no_steps) is None
    assert accessibility_block(no_steps) is not None

    # hostile: a mutated protocol block must fail round-trip
    forged = ab.replace('"Add two numbers."', '"Subtract two numbers."')
    try:
        rt = accessibility_protocol_roundtrip(forged)
    except json.JSONDecodeError:
        rt = None
    assert rt != synthetic["usage_tool_protocol"] or rt is None or (
        rt[0]["function"]["description"] != "Add two numbers."
    )

    # frozen template bytes must be stable
    assert ACCESSIBILITY_INSTRUCTION.endswith(
        "Verbatim tool protocol (object-identical to usage_tool_protocol):\n"
    )
    assert INFORMATION_HEADER.endswith("(benchmark-provided, verbatim)\n")

    print("A4_INTERVENTION_TRANSFORMS_SELF_TEST_GREEN")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--verify-dataset", nargs="+", type=Path)
    a = ap.parse_args()
    if a.self_test:
        self_test()
        return 0
    if a.verify_dataset:
        return verify_dataset(a.verify_dataset)
    ap.error("--self-test or --verify-dataset required")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
