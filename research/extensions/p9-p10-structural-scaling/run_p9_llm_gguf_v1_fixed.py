from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
import urllib.request
from pathlib import Path
from typing import Any

from orion.study.p9.d1 import D1Domain, D1Split, D1View
from orion.study.p9 import d1 as d1_base

SEED = "p9-llm-structure-scaling-gguf-v1"
SYSTEM = "Classify the relationship between LEFT and RIGHT as exactly one label: ALIGNED, OBSTRUCTION, or UNRESOLVED. Return only the label."
BUDGETS = (8, 32, 96)
TARGET_QUALITIES = (0.50, 0.70, 0.85)
MODELS = {
    "0.5B": {"params": 500_000_000,"repo":"Qwen/Qwen2.5-0.5B-Instruct-GGUF","file":"qwen2.5-0.5b-instruct-q4_k_m.gguf","sha256":"74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db"},
    "1.5B": {"params": 1_500_000_000,"repo":"Qwen/Qwen2.5-1.5B-Instruct-GGUF","file":"qwen2.5-1.5b-instruct-q4_k_m.gguf","sha256":"6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e"},
    "3B": {"params": 3_000_000_000,"repo":"Qwen/Qwen2.5-3B-Instruct-GGUF","file":"qwen2.5-3b-instruct-q4_k_m.gguf","sha256":"626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d"},
}

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def cjson(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def flatten(value: Any, path: str = "root") -> list[str]:
    out: list[str] = []
    if isinstance(value, dict):
        for k in sorted(value):
            out.extend(flatten(value[k], f"{path}.{k}"))
    elif isinstance(value, list):
        out.append(f"{path}:LEN={len(value)}")
        for child in value:
            out.extend(flatten(child, f"{path}[]"))
    elif value is None:
        out.append(f"{path}=<NONE>")
    else:
        out.append(f"{path}={value}")
    return out

def build_population() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for domain in (D1Domain.NUMERICAL, D1Domain.GRAPH, D1Domain.WORKFLOW):
        for i in range(16):
            local = f"{SEED}|{domain.value}|{i}"
            single = d1_base.SINGLE_MUTATIONS[i % len(d1_base.SINGLE_MUTATIONS)]
            double = tuple(d1_base.DOUBLE_MUTATIONS[i % len(d1_base.DOUBLE_MUTATIONS)])
            variants = [
                ("aligned", (), False),
                (f"single-{single}", (single,), False),
                ("unresolved", (), True),
                (f"double-{double[0]}-{double[1]}", double, False),
            ]
            for variant, mutations, unresolved in variants:
                inst = d1_base._instance(
                    domain=domain,
                    split=D1Split.TEST,
                    seed=local,
                    variant=variant,
                    mutation_coordinates=mutations,
                    unresolved=unresolved,
                )
                typed = inst.model_payload(D1View.TYPED)
                serialized = inst.model_payload(D1View.TYPED_SERIALIZED)
                exact_sequence = flatten(typed)
                if exact_sequence != serialized["sequence"]:
                    raise RuntimeError(f"renderer equivalence failure {inst.instance_id}")
                facts = sorted(exact_sequence)
                rows.append({
                    "item_id": inst.instance_id,
                    "domain": domain.value,
                    "gold": inst.label.value,
                    "facts_sha256": sha("\n".join(facts).encode()),
                    "R1_SAME_INFO": "\n".join(serialized["sequence"]),
                    "R2_TYPED_STATE": cjson(typed),
                })
    if len(rows) != 192:
        raise RuntimeError(f"unexpected population {len(rows)}")
    return rows

def parse_label(text: str) -> str | None:
    toks = re.sub(r"[^A-Za-z_]", " ", text.upper()).split()
    labels = [x for x in toks if x in {"ALIGNED", "OBSTRUCTION", "UNRESOLVED"}]
    return labels[0] if len(labels) == 1 else None

def ensure_model(model_dir: Path, spec: dict[str, Any]) -> Path:
    path = model_dir / spec["file"]
    if not path.exists():
        urllib.request.urlretrieve(f"https://huggingface.co/{spec['repo']}/resolve/main/{spec['file']}?download=true", path)
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != spec["sha256"]:
        raise RuntimeError(f"INVALID_MODEL_IDENTITY {path.name}: {actual}")
    return path

def llama_response(cli: Path, model: Path, user: str, budget: int) -> tuple[str, float]:
    prompt = f"<|im_start|>system\n{SYSTEM}<|im_end|>\n<|im_start|>user\n{user}<|im_end|>\n<|im_start|>assistant\n"
    cmd = [str(cli), "-m", str(model), "-p", prompt, "-n", str(budget), "--temp", "0", "--seed", "914101", "--ctx-size", "4096", "--no-display-prompt", "--simple-io", "--no-conversation"]
    started = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    elapsed = time.time() - started
    if proc.returncode != 0:
        raise RuntimeError(f"llama-cli failed: {proc.stderr[-2000:]}")
    return proc.stdout.strip(), elapsed

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--llama-cli", required=True)
    ap.add_argument("--model-dir", required=True)
    ap.add_argument("--model-scale", choices=tuple(MODELS), required=True)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    spec = MODELS[a.model_scale]
    model = ensure_model(Path(a.model_dir), spec)
    pop = build_population()
    manifest = [{k: r[k] for k in ("item_id", "domain", "gold", "facts_sha256")} for r in pop]
    records: list[dict[str, Any]] = []
    for row in pop:
        for rep in ("R1_SAME_INFO", "R2_TYPED_STATE"):
            for budget in BUDGETS:
                raw, elapsed = llama_response(Path(a.llama_cli), model, row[rep], budget)
                parsed = parse_label(raw)
                records.append({
                    "item_id": row["item_id"], "domain": row["domain"], "gold": row["gold"],
                    "representation": rep, "budget": budget, "raw": raw, "parsed": parsed,
                    "correct": parsed == row["gold"], "wall_seconds": elapsed,
                    "facts_sha256": row["facts_sha256"],
                })
    result = {
        "schema": "P9.LLMGGUFRuns.v1",
        "protocol": "P9_LLM_GGUF_EXECUTION_AMENDMENT_V1.md",
        "model_scale": a.model_scale,
        "model_parameter_count": spec["params"],
        "model_repo": spec["repo"],
        "model_file": spec["file"],
        "model_sha256": spec["sha256"],
        "prompt_sha256": sha(SYSTEM.encode()),
        "item_manifest_sha256": sha(cjson(manifest).encode()),
        "population_n": len(pop),
        "budgets": list(BUDGETS),
        "target_qualities": list(TARGET_QUALITIES),
        "equivalence_failures": 0,
        "records": records,
    }
    Path(a.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "records"}, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
