from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any

# Import the verified runtime amendment first: it patches the base D1 generator's
# dependency mutation semantics before any new LLM evaluation item is created.
from orion.study.p9 import d1_data_runtime as _d1_runtime  # noqa: F401
from orion.study.p9 import d1 as d1_base
from orion.study.p9.d1 import D1Domain, D1Split, D1View

SEED = "p9-llm-structure-scaling-gguf-v1"
SYSTEM = (
    "Classify the relationship between LEFT and RIGHT as exactly one label: "
    "ALIGNED, OBSTRUCTION, or UNRESOLVED. Return only the label."
)
BUDGETS = (8, 32, 96)
PRIMARY_BUDGET = 32
TARGET_QUALITIES = (0.50, 0.70, 0.85)
LABELS = {"ALIGNED", "OBSTRUCTION", "UNRESOLVED"}
DOMAIN_MARKERS = {"numerical_methods", "graph_algorithms", "transactional_workflows"}
PADDING = "NEUTRAL_PADDING"
MODELS = {
    "0.5B": {
        "params": 500_000_000,
        "repo": "Qwen/Qwen2.5-0.5B-Instruct-GGUF",
        "file": "qwen2.5-0.5b-instruct-q4_k_m.gguf",
        "sha256": "74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db",
    },
    "1.5B": {
        "params": 1_500_000_000,
        "repo": "Qwen/Qwen2.5-1.5B-Instruct-GGUF",
        "file": "qwen2.5-1.5b-instruct-q4_k_m.gguf",
        "sha256": "6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e",
    },
    "3B": {
        "params": 3_000_000_000,
        "repo": "Qwen/Qwen2.5-3B-Instruct-GGUF",
        "file": "qwen2.5-3b-instruct-q4_k_m.gguf",
        "sha256": "626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d",
    },
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cjson(value: Any, *, sort_keys: bool = True) -> str:
    return json.dumps(value, sort_keys=sort_keys, separators=(",", ":"), ensure_ascii=False)


def prompt(user: str) -> str:
    return (
        f"<|im_start|>system\n{SYSTEM}<|im_end|>\n"
        f"<|im_start|>user\n{user}<|im_end|>\n"
        "<|im_start|>assistant\n"
    )


def post_json(base: str, route: str, payload: dict[str, Any], *, timeout: int = 180) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        base.rstrip("/") + route,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            value = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"server HTTP {exc.code} {route}: {detail[:2000]}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"unexpected server response on {route}: {type(value)}")
    return value


def token_count(base: str, text: str) -> int:
    value = post_json(base, "/tokenize", {"content": text, "add_special": False})
    tokens = value.get("tokens")
    if not isinstance(tokens, list):
        raise RuntimeError(f"tokenize response lacks tokens: {value}")
    return len(tokens)


def parse_label(text: str) -> str | None:
    tokens = re.sub(r"[^A-Za-z_]", " ", text.upper()).split()
    found = [token for token in tokens if token in LABELS]
    return found[0] if len(found) == 1 else None


def reorder_structure_keys(value: Any) -> Any:
    """Change mapping presentation order without changing sequence semantics."""
    if isinstance(value, dict):
        return {key: reorder_structure_keys(value[key]) for key in reversed(list(value.keys()))}
    if isinstance(value, list):
        # Sequence order is semantic for dependency endpoints and can be semantic
        # elsewhere; keep every list exactly intact while recursively copying it.
        return [reorder_structure_keys(child) for child in value]
    return value


def serialized_group_key(line: str) -> str:
    """Return the coordinate-level path so groups can move without internal reorder."""
    path = line.split("=", 1)[0].split(":", 1)[0]
    parts = path.split(".")
    # root.left.<coordinate> / root.right.<coordinate> / root.schema
    return ".".join(parts[:3]) if len(parts) >= 3 else path


def reorder_same_info_groups(lines: list[str]) -> list[str]:
    groups: list[tuple[str, list[str]]] = []
    current_key: str | None = None
    current: list[str] = []
    for line in lines:
        key = serialized_group_key(line)
        if current_key is None or key == current_key:
            current_key = key
            current.append(line)
            continue
        groups.append((current_key, current))
        current_key = key
        current = [line]
    if current_key is not None:
        groups.append((current_key, current))
    reordered = [line for _, group in reversed(groups) for line in group]
    if sorted(reordered) != sorted(lines):
        raise RuntimeError("order control changed serialized fact multiset")
    return reordered


def opaque_symbol(value: str, item_id: str) -> str:
    return "v_" + hashlib.sha256(f"{item_id}|{value}".encode()).hexdigest()[:14]


def rename_symbols(value: Any, item_id: str, *, parent_key: str | None = None) -> Any:
    if isinstance(value, dict):
        return {key: rename_symbols(child, item_id, parent_key=key) for key, child in value.items()}
    if isinstance(value, list):
        if parent_key == "unknown_coordinates":
            return list(value)
        return [rename_symbols(child, item_id, parent_key=parent_key) for child in value]
    if isinstance(value, str):
        if parent_key == "schema":
            return value
        return opaque_symbol(value, item_id)
    return value


def leak_scan(text: str) -> list[str]:
    lower = text.lower()
    failures: list[str] = []
    for label in sorted(LABELS):
        if re.search(rf"\b{re.escape(label.lower())}\b", lower):
            failures.append(f"label:{label}")
    for marker in sorted(DOMAIN_MARKERS):
        if marker.lower() in lower:
            failures.append(f"domain:{marker}")
    for marker in ("mutation_count", "gold_label", "evaluator_gold"):
        if marker in lower:
            failures.append(f"metadata:{marker}")
    return failures


def build_population() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for domain in (D1Domain.NUMERICAL, D1Domain.GRAPH, D1Domain.WORKFLOW):
        for index in range(16):
            local = f"{SEED}|{domain.value}|{index}"
            single = d1_base.SINGLE_MUTATIONS[index % len(d1_base.SINGLE_MUTATIONS)]
            double = tuple(d1_base.DOUBLE_MUTATIONS[index % len(d1_base.DOUBLE_MUTATIONS)])
            variants = [
                ("aligned", (), False),
                (f"single-{single}", (single,), False),
                ("unresolved", (), True),
                (f"double-{double[0]}-{double[1]}", double, False),
            ]
            for variant, mutations, unresolved in variants:
                instance = d1_base._instance(
                    domain=domain,
                    split=D1Split.TEST,
                    seed=local,
                    variant=variant,
                    mutation_coordinates=mutations,
                    unresolved=unresolved,
                )
                typed = instance.model_payload(D1View.TYPED)
                serialized = instance.model_payload(D1View.TYPED_SERIALIZED)
                expected = d1_base._serialize_typed(typed)
                if expected != serialized["sequence"]:
                    raise RuntimeError(f"same-information renderer mismatch: {instance.instance_id}")
                fact_digest = sha("\n".join(sorted(expected)).encode())
                rows.append(
                    {
                        "item_id": instance.instance_id,
                        "domain": domain.value,
                        "gold": instance.label.value,
                        "typed": typed,
                        "same_info_lines": list(serialized["sequence"]),
                        "facts_sha256": fact_digest,
                    }
                )
    if len(rows) != 192:
        raise RuntimeError(f"unexpected population size: {len(rows)}")
    return rows


def length_control(base: str, r1_user: str, r2_user: str) -> dict[str, Any]:
    r1_tokens = token_count(base, prompt(r1_user))
    r2_tokens = token_count(base, prompt(r2_user))
    padding_count = 0
    controlled = r2_user
    while r2_tokens < r1_tokens:
        controlled += "\n" + PADDING
        padding_count += 1
        r2_tokens = token_count(base, prompt(controlled))
        if padding_count > 4096:
            raise RuntimeError("length-control padding did not converge")
    if r1_tokens >= 4096 or r2_tokens >= 4096:
        raise RuntimeError(f"context limit exceeded: R1={r1_tokens}, R2={r2_tokens}")
    return {
        "R1_user": r1_user,
        "R2_user": controlled,
        "R1_input_tokens": r1_tokens,
        "R2_input_tokens": r2_tokens,
        "R2_padding_count": padding_count,
    }


def completion(base: str, user: str, budget: int) -> dict[str, Any]:
    started = time.time()
    value = post_json(
        base,
        "/completion",
        {"prompt": prompt(user), "n_predict": budget, "temperature": 0.0, "seed": 914101, "cache_prompt": True},
    )
    elapsed = time.time() - started
    raw = value.get("content")
    if not isinstance(raw, str):
        raise RuntimeError(f"completion response lacks content: {value}")
    predicted = value.get("tokens_predicted")
    if not isinstance(predicted, int):
        predicted = token_count(base, raw)
    return {
        "raw": raw.strip(),
        "parsed": parse_label(raw),
        "output_tokens": predicted,
        "wall_seconds": elapsed,
        "stop_type": value.get("stop_type"),
    }


def control_ids(population: list[dict[str, Any]]) -> set[str]:
    by_domain: dict[str, list[str]] = defaultdict(list)
    for row in population:
        by_domain[row["domain"]].append(row["item_id"])
    selected: set[str] = set()
    for domain, ids in by_domain.items():
        chosen = sorted(ids)[:16]
        if len(chosen) != 16:
            raise RuntimeError(f"control-set cardinality failure for {domain}")
        selected.update(chosen)
    if len(selected) != 48:
        raise RuntimeError(f"control population size {len(selected)}")
    return selected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-url", required=True)
    parser.add_argument("--model-scale", choices=tuple(MODELS), required=True)
    parser.add_argument("--model-sha256", required=True)
    parser.add_argument("--llama-commit", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    spec = MODELS[args.model_scale]
    if args.model_sha256 != spec["sha256"]:
        raise SystemExit("INVALID_MODEL_IDENTITY")

    population = build_population()
    selected_controls = control_ids(population)
    leak_failures: list[dict[str, Any]] = []
    primary_records: list[dict[str, Any]] = []
    control_records: list[dict[str, Any]] = []
    token_receipts: list[dict[str, Any]] = []

    for row in population:
        typed = row["typed"]
        r1 = "\n".join(row["same_info_lines"])
        r2 = cjson(typed, sort_keys=True)
        leaks = {"R1": leak_scan(r1), "R2": leak_scan(r2)}
        if leaks["R1"] or leaks["R2"]:
            leak_failures.append({"item_id": row["item_id"], **leaks})
            continue
        controlled = length_control(args.server_url, r1, r2)
        token_receipts.append(
            {
                "item_id": row["item_id"],
                "domain": row["domain"],
                "R1_input_tokens": controlled["R1_input_tokens"],
                "R2_input_tokens": controlled["R2_input_tokens"],
                "R2_padding_count": controlled["R2_padding_count"],
            }
        )
        for representation, user, input_tokens in (
            ("R1_SAME_INFO", controlled["R1_user"], controlled["R1_input_tokens"]),
            ("R2_TYPED_STATE", controlled["R2_user"], controlled["R2_input_tokens"]),
        ):
            for budget in BUDGETS:
                result = completion(args.server_url, user, budget)
                primary_records.append(
                    {
                        "item_id": row["item_id"],
                        "domain": row["domain"],
                        "gold": row["gold"],
                        "facts_sha256": row["facts_sha256"],
                        "representation": representation,
                        "budget": budget,
                        "input_tokens": input_tokens,
                        **result,
                        "correct": result["parsed"] == row["gold"],
                    }
                )

        if row["item_id"] not in selected_controls:
            continue

        # Semantics-preserving order hostile control. Reorder coordinate groups
        # but never reorder values within a coordinate or dependency endpoints.
        order_lines = reorder_same_info_groups(row["same_info_lines"])
        order_r1 = "\n".join(order_lines)
        order_structured = reorder_structure_keys(typed)
        if order_structured != typed:
            raise RuntimeError("order control changed structured semantic object")
        order_r2 = cjson(order_structured, sort_keys=False)
        order_controlled = length_control(args.server_url, order_r1, order_r2)
        for representation, user, input_tokens in (
            ("R1_SAME_INFO", order_controlled["R1_user"], order_controlled["R1_input_tokens"]),
            ("R2_TYPED_STATE", order_controlled["R2_user"], order_controlled["R2_input_tokens"]),
        ):
            result = completion(args.server_url, user, PRIMARY_BUDGET)
            control_records.append(
                {
                    "control": "ORDER",
                    "item_id": row["item_id"],
                    "domain": row["domain"],
                    "gold": row["gold"],
                    "representation": representation,
                    "budget": PRIMARY_BUDGET,
                    "input_tokens": input_tokens,
                    **result,
                    "correct": result["parsed"] == row["gold"],
                }
            )

        # Symbol hostile control, generated from one renamed typed object.
        renamed = rename_symbols(typed, row["item_id"])
        symbol_lines = d1_base._serialize_typed(renamed)
        symbol_r1 = "\n".join(symbol_lines)
        symbol_r2 = cjson(renamed, sort_keys=True)
        symbol_controlled = length_control(args.server_url, symbol_r1, symbol_r2)
        for representation, user, input_tokens in (
            ("R1_SAME_INFO", symbol_controlled["R1_user"], symbol_controlled["R1_input_tokens"]),
            ("R2_TYPED_STATE", symbol_controlled["R2_user"], symbol_controlled["R2_input_tokens"]),
        ):
            result = completion(args.server_url, user, PRIMARY_BUDGET)
            control_records.append(
                {
                    "control": "SYMBOL",
                    "item_id": row["item_id"],
                    "domain": row["domain"],
                    "gold": row["gold"],
                    "representation": representation,
                    "budget": PRIMARY_BUDGET,
                    "input_tokens": input_tokens,
                    **result,
                    "correct": result["parsed"] == row["gold"],
                }
            )

    terminal = "INVALID_RENDERER_LEAKAGE" if leak_failures else "RUN_COMPLETE_PENDING_CROSS_SIZE_ANALYSIS"
    manifest = [
        {
            "item_id": row["item_id"],
            "domain": row["domain"],
            "gold": row["gold"],
            "facts_sha256": row["facts_sha256"],
        }
        for row in population
    ]
    output = {
        "schema": "P9.LLMGGUFServerRuns.v1",
        "protocol": "P9_LLM_GGUF_EXECUTION_AMENDMENT_V1.md",
        "hostile_control_amendment": "P9_LLM_GGUF_HOSTILE_CONTROL_AMENDMENT_V1.md",
        "model_scale": args.model_scale,
        "model_parameter_count": spec["params"],
        "model_repo": spec["repo"],
        "model_file": spec["file"],
        "model_sha256": spec["sha256"],
        "llama_commit": args.llama_commit,
        "prompt_sha256": sha(SYSTEM.encode()),
        "item_manifest_sha256": sha(cjson(manifest).encode()),
        "population_n": len(population),
        "control_population_n": len(selected_controls),
        "budgets": list(BUDGETS),
        "target_qualities": list(TARGET_QUALITIES),
        "equivalence_failures": 0,
        "leakage_failures": leak_failures,
        "token_receipts": token_receipts,
        "records": primary_records,
        "control_records": control_records,
        "terminal": terminal,
    }
    Path(args.output).write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "model_scale": args.model_scale,
                "population_n": len(population),
                "primary_records": len(primary_records),
                "control_records": len(control_records),
                "leakage_failures": len(leak_failures),
                "terminal": terminal,
            },
            indent=2,
            sort_keys=True,
        )
    )
    if terminal != "RUN_COMPLETE_PENDING_CROSS_SIZE_ANALYSIS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
