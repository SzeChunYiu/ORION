#!/usr/bin/env python3
"""Generate realistic source texts for all 32 P3 gold samples.

Uses the frozen evaluation model (deepseek-v4-pro via cmkey proxy) to generate
3-5 sentence source passages from the SEED manifest retrieval hints, then
updates each gold annotation file with the generated text.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from orion.providers.llm import AnthropicMessagesConfig, AnthropicMessagesLLMProvider, LLMRequest

GOLD_DIR = Path(__file__).resolve().parent / "adjudicated"
MANIFEST_PATH = Path(__file__).resolve().parent / "SAMPLE_MANIFEST_SEED_V1.json"


def main() -> int:
    provider = AnthropicMessagesLLMProvider(
        AnthropicMessagesConfig.from_env(model="deepseek-v4-pro", max_tokens=4096)
    )

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    samples = manifest["samples"]

    errors = 0
    for i, sample in enumerate(samples):
        sid = sample["sample_id"]
        case_family = sample["case_family"]
        hint_a = sample["source_a"].get("retrieval_hint", "")
        hint_b = sample["source_b"].get("retrieval_hint", "")
        gold_path = GOLD_DIR / f"{sid}.gold.json"

        if not gold_path.exists():
            print(f"SKIP {sid}: gold file not found")
            errors += 1
            continue

        # Check if text already exists and is non-trivial
        gold = json.loads(gold_path.read_text(encoding="utf-8"))
        existing_a = gold["source_a"].get("text", "")
        existing_b = gold["source_b"].get("text", "")
        if len(existing_a.strip()) > 300 and len(existing_b.strip()) > 300:
            print(f"  ✓ {sid} already has text (a={len(existing_a)} b={len(existing_b)})")
            continue

        # Generate source texts
        prompt = f"""Generate two realistic scientific source passages (A and B) for a cross-domain integration challenge.

CASE: {case_family}
DISCIPLINE: {sample["source_a"]["discipline"]}

RETRIEVAL HINT A: {hint_a}
RETRIEVAL HINT B: {hint_b}

GOLD LABELS (these are the correct integration decisions):
- referent_relation: {gold["referent_relation"]}
- construct_relation: {gold["construct_relation"]}
- measurement_relation: {gold["measurement_relation"]}
- context_relation: {gold["context_relation"]}
- mapping_relation: {gold["mapping_relation"]}
- integration_verdict: {gold["integration_verdict"]}

REQUIREMENTS:
1. Source A: 3-5 sentences of realistic scientific text based on Retrieval Hint A
2. Source B: 3-5 sentences of realistic scientific text based on Retrieval Hint B
3. The passages must clearly illustrate WHY the gold labels are correct (e.g., for same_name_different_referent, both passages should use the same name for different referents)
4. Use realistic scientific language, terminology, and citation style
5. Each passage should be self-contained and read like an excerpt from a real paper
6. Output ONLY valid JSON: {{"source_a": "text here", "source_b": "text here"}}"""

        system = "You are a scientific writing assistant. Generate realistic, concise source passages. Output ONLY valid JSON."

        schema = r"""{"type":"object","properties":{"source_a":{"type":"string","minLength":100},"source_b":{"type":"string","minLength":100}},"required":["source_a","source_b"],"additionalProperties":false}"""

        print(f"  → {sid} ({case_family}) generating...", end=" ", flush=True)
        try:
            resp = provider.complete(LLMRequest(
                task="Generate source passages",
                system=system,
                user=prompt,
                response_schema=schema,
            ))
            parsed = json.loads(resp.content)
            text_a = parsed["source_a"].strip()
            text_b = parsed["source_b"].strip()
        except Exception as exc:
            print(f"ERROR: {exc}")
            errors += 1
            time.sleep(2)
            continue

        # Update gold annotation
        gold["source_a"]["text"] = text_a
        gold["source_b"]["text"] = text_b
        gold_path.write_text(json.dumps(gold, indent=2) + "\n", encoding="utf-8")
        print(f"a={len(text_a)} b={len(text_b)}")

        # Rate limiting — be nice to the proxy
        time.sleep(1.5)

    print(f"\nDone. Errors: {errors}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())