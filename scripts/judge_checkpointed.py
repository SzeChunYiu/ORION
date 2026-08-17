#!/usr/bin/env python3
"""Checkpointed wrapper around the pinned official Deep scorer.

Imports run_deep_official_scoring and reuses its EXACT judge semantics
(JUDGE_PROMPT_SYSTEM / JUDGE_PROMPT_USER_TEMPLATE / MODEL / TEMPERATURE /
parse_judge_output / judge_title_match / evaluate_single_item). The only
difference is execution robustness: results append to a JSONL checkpoint
after every item and the run resumes from the checkpoint, so a crash or
restart never loses completed items and never re-judges them.

Usage:
    python scripts/judge_checkpointed.py <official_input.jsonl> \
        <checkpoint.jsonl> <official_evaluation.json>
"""
import asyncio
import importlib.util
import json
import sys
from pathlib import Path

SCORER_PATH = Path(__file__).resolve().parent / "run_deep_official_scoring.py"

_spec = importlib.util.spec_from_file_location("deep_official_scorer", SCORER_PATH)
scorer = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(scorer)


def load_checkpoint(path: Path) -> dict[int, dict]:
    done: dict[int, dict] = {}
    if path.exists():
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    if "index" in rec and "error" not in rec:
                        done[rec["index"]] = rec
                    elif "index" in rec:
                        # errored items are retried on resume
                        pass
    return done


async def main() -> None:
    input_file = Path(sys.argv[1])
    checkpoint_file = Path(sys.argv[2])
    output_file = Path(sys.argv[3])

    items = []
    with open(input_file) as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    total = len(items)

    done = load_checkpoint(checkpoint_file)
    print(f"input={total} already_done={len(done)}", flush=True)

    import aiohttp

    semaphore = asyncio.Semaphore(3)  # same concurrency cap as the scorer

    async def guarded(session, item, index):
        async with semaphore:
            try:
                return await scorer.evaluate_single_item(
                    session, item, index, total, 5
                )
            except Exception as exc:  # noqa: BLE001
                return {"index": index, "question": item.get("input_data", {}).get("question", ""), "error": str(exc)}

    pending = [i for i in range(total) if i not in done]
    checkpoint_file.parent.mkdir(parents=True, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        with open(checkpoint_file, "a") as ckpt:
            batch: list[asyncio.Task] = []
            BATCH_SIZE = 12
            for count, idx in enumerate(pending, 1):
                batch.append(asyncio.create_task(guarded(session, items[idx], idx)))
                if len(batch) >= BATCH_SIZE or count == len(pending):
                    for result in await asyncio.gather(*batch):
                        ckpt.write(json.dumps(result) + "\n")
                    ckpt.flush()
                    batch = []
                    print(f"progress {min(len(done) + count, total)}/{total}", flush=True)

    # Recompute metrics over ALL items from the checkpoint (ordered)
    final = load_checkpoint(checkpoint_file)
    results = []
    for i in range(total):
        if i in final:
            results.append(final[i])
        else:
            results.append({"index": i, "question": items[i].get("input_data", {}).get("question", ""), "error": "missing"})
    hits = sum(1 for r in results if r.get("hit", False))
    attempted = len(results)
    metrics = {
        "total_items": attempted,
        "hits": hits,
        "hit_rate": hits / attempted if attempted else 0.0,
        "items": results,
        "checkpoint_reused": len(done),
    }
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"DONE {hits}/{attempted} = {metrics['hit_rate']:.3%}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
