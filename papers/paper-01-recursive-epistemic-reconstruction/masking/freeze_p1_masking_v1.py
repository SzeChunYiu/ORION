#!/usr/bin/env python3
"""Freeze P1's deterministic masking/recovery intervention, before any scoring.

P1 asks whether *recursive reconstruction* of a missing task specification beats
a matched one-shot attempt and a no-reconstruction control. That question only
means something if the masking is fixed in advance: a mask chosen after seeing
which tasks an arm failed would be an outcome-tuned intervention wearing the
name of a protocol.

What is masked
--------------
``domain_knowledge`` -- the paper-derived knowledge ScienceAgentBench hands the
agent alongside the task instruction. It is the field whose removal creates a
genuine reconstruction problem: the task stays well posed, but the knowledge
needed to solve it must be recovered rather than read.

``task_inst`` is deliberately NOT masked. Masking the instruction would change
what is being asked, and an arm that then failed would have failed a different
task, not the same task with less support.

How the mask is chosen
----------------------
Per instance, deterministically: sentences are split on a fixed rule, ordered,
and selected by ``blake2b(instance_id + SALT)``. The same instance always
yields the same mask on any machine, and no human picked which sentences go.
The salt is recorded here, so the selection is reproducible and auditable but
was not searched over.

Instances whose ``domain_knowledge`` is empty or single-sentence are recorded
as ``NOT_MASKABLE`` and carry no mask. That is a distinct state from "masked
with zero spans", and it must not be silently folded into the scored set.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

SAB = Path.home() / "orion-work/sab/ScienceAgentBench.csv"
OUT = Path(__file__).resolve().parent / "P1_MASKING_FREEZE_V1.json"

#: Fixed before any arm was run. Not searched over.
SALT = "orion-p1-recursive-reconstruction-v1"
MASK_FRACTION = 0.5
MIN_SENTENCES_TO_MASK = 2

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")

ARMS = {
    "unmasked_ceiling": (
        "full domain_knowledge, no recovery step. Not a competitor: it is the "
        "attainable ceiling this intervention removes support from."
    ),
    "no_reconstruction": (
        "masked domain_knowledge, no recovery step. Isolates how much the "
        "masked knowledge was worth."
    ),
    "one_shot_reconstruction": (
        "masked, one single recovery attempt before solving."
    ),
    "recursive_reconstruction": (
        "masked, iterative recover -> check -> refine before solving. The arm "
        "under test."
    ),
}

#: Matched across every arm. An arm that wins by spending more has not won.
BUDGET = {
    "max_attempts": 3,
    "max_model_tokens_per_task": 60000,
    "max_tool_calls_per_task": 40,
    "identical_tool_access": True,
    "identical_model": True,
}


def sentences(text: str) -> list[str]:
    parts = [s.strip() for s in SENTENCE_SPLIT.split(text.strip()) if s.strip()]
    return parts


def mask_indices(instance_id: str, count: int) -> list[int]:
    """Deterministic, instance-keyed selection. No search, no human choice."""
    if count < MIN_SENTENCES_TO_MASK:
        return []
    k = max(1, round(count * MASK_FRACTION))
    # rank sentences by a keyed digest and take the first k; stable everywhere
    ranked = sorted(
        range(count),
        key=lambda i: hashlib.blake2b(
            f"{SALT}|{instance_id}|{i}".encode(), digest_size=8
        ).hexdigest(),
    )
    return sorted(ranked[:k])


def main() -> int:
    if not SAB.is_file():
        print(f"P1_MASKING_FREEZE_CANNOT_CHECK: annotation sheet missing at {SAB}")
        return 3
    raw = SAB.read_bytes()
    rows = list(csv.DictReader(SAB.open(encoding="utf-8")))

    entries = []
    not_maskable = 0
    total_masked = total_sentences = 0
    for row in rows:
        iid = row["instance_id"]
        dk = (row.get("domain_knowledge") or "").strip()
        sents = sentences(dk)
        idx = mask_indices(iid, len(sents))
        if not idx:
            not_maskable += 1
            entries.append(
                {
                    "instance_id": iid,
                    "domain": row.get("domain", ""),
                    "status": "NOT_MASKABLE",
                    "reason": (
                        "domain_knowledge is empty"
                        if not sents
                        else f"only {len(sents)} sentence(s); minimum is {MIN_SENTENCES_TO_MASK}"
                    ),
                    "sentence_count": len(sents),
                }
            )
            continue
        masked_text = " ".join(sents[i] for i in idx)
        total_masked += len(idx)
        total_sentences += len(sents)
        entries.append(
            {
                "instance_id": iid,
                "domain": row.get("domain", ""),
                "status": "MASKED",
                "sentence_count": len(sents),
                "masked_indices": idx,
                "masked_sentence_count": len(idx),
                # the exact removed content, by hash, so recovery can be scored
                # without the freeze itself carrying the answer in the clear
                "masked_text_sha256": hashlib.sha256(masked_text.encode()).hexdigest(),
                "retained_text_sha256": hashlib.sha256(
                    " ".join(s for i, s in enumerate(sents) if i not in set(idx)).encode()
                ).hexdigest(),
            }
        )

    by_domain: dict[str, dict[str, int]] = {}
    for e in entries:
        d = by_domain.setdefault(e["domain"], {"MASKED": 0, "NOT_MASKABLE": 0})
        d[e["status"]] += 1

    freeze = {
        "schema": "P1.MaskingFreeze.v1",
        "purpose": "deterministic masking/recovery intervention, frozen before any scoring",
        "outcome_accessed": False,
        "source": {
            "dataset": "osunlp/ScienceAgentBench (HuggingFace annotation sheet)",
            "file": "ScienceAgentBench.csv",
            "sha256": hashlib.sha256(raw).hexdigest(),
            "rows": len(rows),
        },
        "masked_field": "domain_knowledge",
        "unmasked_fields_and_why": {
            "task_inst": (
                "masking the instruction would change what is asked; a failure "
                "there would be a failure at a different task"
            )
        },
        "selection_rule": {
            "granularity": "sentence",
            "split": SENTENCE_SPLIT.pattern,
            "salt": SALT,
            "mask_fraction": MASK_FRACTION,
            "min_sentences_to_mask": MIN_SENTENCES_TO_MASK,
            "method": "rank sentence indices by blake2b(salt|instance_id|index), take first k",
            "searched_over": False,
        },
        "arms": ARMS,
        "budget": BUDGET,
        "totals": {
            "instances": len(entries),
            "maskable": len(entries) - not_maskable,
            "not_maskable": not_maskable,
            "sentences_in_maskable": total_sentences,
            "sentences_masked": total_masked,
            "masked_fraction_realised": round(total_masked / total_sentences, 6)
            if total_sentences
            else None,
        },
        "by_domain": by_domain,
        "entries": entries,
    }
    body = json.dumps(freeze, indent=2, sort_keys=True) + "\n"
    OUT.write_text(body)
    print(f"instances: {len(entries)}  maskable: {len(entries)-not_maskable}  not maskable: {not_maskable}")
    print(f"sentences masked: {total_masked}/{total_sentences} = {freeze['totals']['masked_fraction_realised']}")
    for d, c in sorted(by_domain.items()):
        print(f"  {d:36s} masked={c['MASKED']:3d} not_maskable={c['NOT_MASKABLE']:3d}")
    print(f"wrote {OUT}")
    print(f"FREEZE_SHA256 {hashlib.sha256(body.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
