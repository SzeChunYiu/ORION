from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
P10 = ROOT / "papers" / "candidates" / "paper-10-content-bound-math-evaluation"
FRAMEWORK = ROOT / "papers" / "candidates" / "orion-learning-machine" / "framework"
sys.path.insert(0, str(FRAMEWORK))
from orion_learning_machine.adapters import lean_source  # noqa: E402

MANIFEST = P10 / "benchmark" / "MATHLIB_CORPUS_V2_MANIFEST.json"
MATHLIB_COMMIT = "e72c1e277f31441626621f7d0c7207862fc25569"
LEAN_TOOLCHAIN = "leanprover/lean4:v4.34.0-rc1"
EXTRACTOR_SCHEMA = "P10.NativeTraceStateShard.v1"
INFO_HEADER = re.compile(r"(?m)^.*?:(\d+):(\d+): (info|warning|error): ?(.*)$")
BULLET = re.compile(r"^(\s*)([·*-])\s+(.*)$")
IDENT = re.compile(r"\b[A-Za-z_][A-Za-z0-9_'.]*\b")
TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_'.]*|↔|→|∀|∃|∧|∨|≤|≥|≠|:=|[=<>+*/^()-]")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def bucket(value: int, bounds: tuple[int, ...]) -> str:
    previous = 0
    for bound in bounds:
        if value < bound:
            return f"{previous}-{bound-1}"
        previous = bound
    return f"{previous}+"


def shape(text: str) -> str:
    if "↔" in text:
        return "iff"
    if "∧" in text:
        return "conjunction"
    if "∨" in text:
        return "disjunction"
    if "∀" in text:
        return "forall"
    if "∃" in text:
        return "exists"
    if "→" in text or "->" in text:
        return "implication_function"
    if any(symbol in text for symbol in ("≤", "≥", "<", ">")):
        return "order_comparison"
    if "=" in text or "≠" in text:
        return "equality"
    if any(symbol in text for symbol in ("+", "*", "/", "^")):
        return "arithmetic_algebraic"
    if any(word in text for word in ("Prop", "Type", "Sort", "Class")):
        return "prop_type_sort"
    return "other"


def visible_depth(text: str) -> int:
    depth = maximum = 0
    for char in text:
        if char in "([{":
            depth += 1
            maximum = max(maximum, depth)
        elif char in ")]}":
            depth = max(0, depth - 1)
    return maximum


def parse_context(state: str) -> tuple[list[tuple[list[str], str]], list[str]]:
    declarations: list[tuple[list[str], str]] = []
    goals: list[str] = []
    for raw in state.splitlines():
        line = raw.strip()
        if not line or line.startswith("case "):
            continue
        if "⊢" in line:
            goals.append(line.split("⊢", 1)[1].strip())
            continue
        if " : " in line:
            lhs, rhs = line.split(" : ", 1)
            names = [name for name in IDENT.findall(lhs) if name not in {"let", "this"}]
            if names:
                declarations.append((names, rhs.strip()))
    return declarations, goals


def state_features(state: str) -> tuple[dict[str, Any], dict[str, Any], str]:
    declarations, goals = parse_context(state)
    context_names = [name for names, _ in declarations for name in names]
    context_set = set(context_names)
    goal_text = " ".join(goals)
    context_hist = Counter(shape(rhs) for _, rhs in declarations)

    edges: set[tuple[str, str]] = set()
    referencing_sources: set[str] = set()
    indegree: Counter[str] = Counter()
    for names, rhs in declarations:
        targets = set(IDENT.findall(rhs)) & context_set
        for source in names:
            local_targets = {target for target in targets if target != source}
            if local_targets:
                referencing_sources.add(source)
            for target in local_targets:
                edges.add((source, target))
                indegree[target] += 1
    goal_refs = set(IDENT.findall(goal_text)) & context_set

    state_vector = {
        "num_goals": max(1, len(goals)),
        "context_cardinality": len(context_names),
        "goal_shape": shape(goal_text),
        "context_shape_histogram": {
            key: context_hist.get(key, 0)
            for key in (
                "equality", "iff", "conjunction", "disjunction", "implication_function",
                "forall", "exists", "order_comparison", "arithmetic_algebraic",
                "prop_type_sort", "other",
            )
        },
        "has_equality": any(symbol in state for symbol in ("=", "≠")),
        "has_conjunction_disjunction": any(symbol in state for symbol in ("∧", "∨")),
        "has_implication_function": "→" in state or "->" in state,
        "has_quantification": "∀" in state or "∃" in state,
        "has_arithmetic_algebraic": any(symbol in state for symbol in ("+", "*", "/", "^")),
        "has_prop_type_sort": any(word in state for word in ("Prop", "Type", "Sort", "Class")),
        "state_token_bucket": bucket(len(TOKEN.findall(state)), (32, 64, 128, 256, 512)),
        "visible_depth_bucket": bucket(visible_depth(state), (3, 6, 10)),
    }
    dependency_vector = {
        "context_reference_edges": len(edges),
        "goal_context_references": len(goal_refs),
        "max_context_reference_indegree": max(indegree.values(), default=0),
        "referencing_declaration_fraction": (
            len(referencing_sources) / len(context_names) if context_names else 0.0
        ),
    }
    normalized = IDENT.sub("<ID>", state)
    normalized = re.sub(r"\b\d+\b", "<N>", normalized)
    normalized = " ".join(normalized.split())
    return state_vector, dependency_vector, sha_bytes(normalized.encode())


def parse_messages(output: str) -> list[dict[str, Any]]:
    matches = list(INFO_HEADER.finditer(output))
    messages: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(output)
        first = match.group(4)
        rest = output[match.end():end]
        if rest.startswith("\n"):
            rest = rest[1:]
        content = first + ("\n" + rest.rstrip("\n") if rest else "")
        messages.append({
            "line": int(match.group(1)),
            "column": int(match.group(2)),
            "kind": match.group(3),
            "content": content.strip(),
        })
    return messages


def source_events(text: str, source_id: str) -> tuple[list[dict[str, Any]], int]:
    events: list[dict[str, Any]] = []
    transitions = 0
    for theorem in lean_source.parse_lean_source(text, source_id):
        block = list(theorem.raw_lines)
        proof_start = lean_source._proof_start(block)
        if proof_start is None:
            continue
        last_family: str | None = None
        action_index = 0
        theorem_events: list[dict[str, Any]] = []
        for block_index in range(proof_start + 1, len(block)):
            family = lean_source.tactic_family(block[block_index])
            if family in (None, "unknown") or family == last_family:
                continue
            absolute_zero_index = theorem.proof_start_line - 1 + (block_index - proof_start)
            material = f"{source_id}|{theorem.theorem_name}|{action_index}"
            theorem_events.append({
                "transition_id": hashlib.sha256(material.encode()).hexdigest()[:32],
                "theorem_name": theorem.theorem_name,
                "action_index": action_index,
                "family": family,
                "line_zero_index": absolute_zero_index,
            })
            last_family = family
            action_index += 1
        transitions += max(0, len(theorem_events) - 1)
        for idx, event in enumerate(theorem_events):
            event["previous_family"] = theorem_events[idx - 1]["family"] if idx else None
            event["is_transition"] = idx >= 1
            events.append(event)
    return events, transitions


def instrument(text: str, events: list[dict[str, Any]]) -> tuple[str, dict[int, dict[str, Any]]]:
    """Insert only built-in trace_state and return instrumented line receipts."""
    lines = text.splitlines()
    transition_events = sorted(
        (event for event in events if event["is_transition"]),
        key=lambda event: int(event["line_zero_index"]),
    )
    line_receipts: dict[int, dict[str, Any]] = {}
    offset = 0
    for event in transition_events:
        original_index = int(event["line_zero_index"])
        current_index = original_index + offset
        original = lines[current_index]
        bullet = BULLET.match(original)
        trace_line_one_based = current_index + 1
        if bullet:
            indent, marker, command = bullet.groups()
            lines[current_index:current_index + 1] = [
                f"{indent}{marker} trace_state",
                f"{indent}  {command}",
            ]
        else:
            indent = original[: len(original) - len(original.lstrip())]
            lines[current_index:current_index] = [f"{indent}trace_state"]
        if trace_line_one_based in line_receipts:
            raise RuntimeError(f"instrumented trace line collision: {trace_line_one_based}")
        line_receipts[trace_line_one_based] = event
        offset += 1
    rendered = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
    return rendered, line_receipts


def states_from_messages(messages: list[dict[str, Any]], line_receipts: dict[int, dict[str, Any]]) -> dict[str, str]:
    states: dict[str, str] = {}
    for message in messages:
        if message["kind"] != "info":
            continue
        event = line_receipts.get(int(message["line"]))
        if event is None:
            continue
        content = str(message["content"])
        if "⊢" not in content and "no goals" not in content.lower():
            continue
        transition_id = str(event["transition_id"])
        if transition_id in states:
            raise RuntimeError(f"multiple native states for transition {transition_id}")
        states[transition_id] = content
    return states


def run_lean(checkout: Path, path: Path, timeout: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["lake", "env", "lean", str(path)],
        cwd=checkout,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mathlib-checkout", required=True)
    parser.add_argument("--shard-index", type=int, required=True)
    parser.add_argument("--shard-count", type=int, required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--file-timeout", type=int, default=240)
    args = parser.parse_args()
    if not 0 <= args.shard_index < args.shard_count:
        raise SystemExit("invalid shard index")

    checkout = Path(args.mathlib_checkout).resolve()
    manifest = json.loads(MANIFEST.read_text())
    if manifest["source"]["commit"] != MATHLIB_COMMIT:
        raise SystemExit("manifest Mathlib commit mismatch")
    if manifest["source"]["lean_toolchain"] != LEAN_TOOLCHAIN:
        raise SystemExit("manifest Lean toolchain mismatch")

    rows: list[dict[str, Any]] = []
    files: list[dict[str, Any]] = []
    denominator = 0
    eligible = 0
    selected = [
        item for item in manifest["files"]
        if int(hashlib.sha256(item["path"].encode()).hexdigest(), 16) % args.shard_count == args.shard_index
    ]

    for item in selected:
        path = checkout / item["path"]
        if not path.is_file() or sha_file(path) != item["sha256"]:
            raise SystemExit(f"source identity mismatch: {item['path']}")
        original = path.read_text(encoding="utf-8")
        events, transition_count = source_events(original, item["path"])
        denominator += transition_count
        instrumented, line_receipts = instrument(original, events)
        proc: subprocess.CompletedProcess[str] | None = None
        failure_reason: str | None = None
        try:
            path.write_text(instrumented, encoding="utf-8")
            proc = run_lean(checkout, path, args.file_timeout)
        except subprocess.TimeoutExpired:
            failure_reason = "INSTRUMENTED_TIMEOUT"
        finally:
            path.write_text(original, encoding="utf-8")
            if sha_file(path) != item["sha256"]:
                raise SystemExit(f"failed to restore exact source: {item['path']}")

        if proc is None or proc.returncode != 0:
            if failure_reason is None:
                failure_reason = "INSTRUMENTATION_UNSUPPORTED"
            try:
                original_proc = run_lean(checkout, path, args.file_timeout)
                original_green = original_proc.returncode == 0
            except subprocess.TimeoutExpired:
                original_green = False
                failure_reason = "ORIGINAL_TIMEOUT_AFTER_INSTRUMENTATION_FAILURE"
            files.append({
                "path": item["path"],
                "top_module": item["top_module"],
                "transitions": transition_count,
                "eligible_transitions": 0,
                "status": failure_reason,
                "original_green_after_restore": original_green,
                "instrumented_returncode": proc.returncode if proc else None,
                "stderr_tail": proc.stderr[-2000:] if proc else None,
            })
            continue

        combined = proc.stdout + "\n" + proc.stderr
        states = states_from_messages(parse_messages(combined), line_receipts)
        event_by_id = {event["transition_id"]: event for event in events}
        file_eligible = 0
        for transition_id, state in states.items():
            event = event_by_id.get(transition_id)
            if event is None or not event["is_transition"]:
                continue
            state_vector, dependency_vector, normalized_digest = state_features(state)
            state_digest = sha_bytes(state.encode())
            receipt_material = {
                "transition_id": transition_id,
                "source_path": item["path"],
                "source_sha256": item["sha256"],
                "theorem_name": event["theorem_name"],
                "action_index": event["action_index"],
                "previous_family": event["previous_family"],
                "true_action": event["family"],
                "state_sha256": state_digest,
                "mathlib_commit": MATHLIB_COMMIT,
                "lean_toolchain": LEAN_TOOLCHAIN,
            }
            receipt_sha = sha_bytes(json.dumps(receipt_material, sort_keys=True, separators=(",", ":")).encode())
            rows.append({
                **receipt_material,
                "top_module": item["top_module"],
                "normalized_state_sha256": normalized_digest,
                "state_features": state_vector,
                "dependency_features": dependency_vector,
                "receipt_sha256": receipt_sha,
            })
            file_eligible += 1
        eligible += file_eligible
        files.append({
            "path": item["path"],
            "top_module": item["top_module"],
            "transitions": transition_count,
            "eligible_transitions": file_eligible,
            "status": "TRACE_GREEN" if file_eligible == transition_count else "PARTIAL_TRACE",
            "expected_trace_count": transition_count,
            "native_trace_count": len(states),
            "instrumented_returncode": proc.returncode,
        })

    output = {
        "schema": EXTRACTOR_SCHEMA,
        "extractor_receipt_mode": "LEAN_DIAGNOSTIC_LINE_NUMBER",
        "shard_index": args.shard_index,
        "shard_count": args.shard_count,
        "mathlib_commit": MATHLIB_COMMIT,
        "lean_toolchain": LEAN_TOOLCHAIN,
        "selected_files": len(selected),
        "transition_denominator": denominator,
        "eligible_transitions": eligible,
        "rows": rows,
        "files": files,
    }
    Path(args.output).write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: output[key] for key in output if key not in {"rows", "files"}}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
