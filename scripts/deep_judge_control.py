#!/usr/bin/env python3
"""Positive/negative control for the ORION Deep judge pipeline.

Uses the EXACT system prompt, user template, model, temperature, and parser
from scripts/run_deep_official_scoring.py (cbd9a95 worktree copy) against the
running localhost adapter. A judge validated only on 0-hit items cannot be
distinguished from an always-no-match bug; this control closes that gap.
"""
import json
from pathlib import Path
import re
import time
import urllib.request

ADAPTER = "http://127.0.0.1:8765/v1/chat/completions"
MODEL = "glm-5.3"
TEMPERATURE = 0.5

# Extract prompts AT RUNTIME from the actual scorer script — no transcription
# (a hand-copied template lost the GT slot once via display-filter compression).
SCORER = str(Path(__file__).resolve().parent / "run_deep_official_scoring.py")
_src = open(SCORER).read()
SYSTEM = re.search(
    r'JUDGE_PROMPT_SYSTEM = """(.*?)"""', _src, re.S).group(1)
USER_TMPL = re.search(
    r'JUDGE_PROMPT_USER_TEMPLATE = """(.*?)"""', _src, re.S).group(1)
assert "{ground_truth_title}" in USER_TMPL, "GT placeholder missing!"
assert "{candidate_title}" in USER_TMPL, "candidate placeholder missing!"
print(f"template extracted: {len(USER_TMPL)} chars, "
      f"gt_slot=True cand_slot=True", flush=True)


def parse_judge_output(output: str) -> bool:
    try:
        data = json.loads(output)
        if isinstance(data, dict) and "is_match" in data:
            return bool(data["is_match"])
    except (json.JSONDecodeError, TypeError):
        return "true" in output.lower()
    return False


def judge(gt: str, cand: str) -> tuple[bool, str]:
    body = json.dumps({
        "model": MODEL,
        "temperature": TEMPERATURE,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": USER_TMPL.format(
                ground_truth_title=gt, candidate_title=cand)},
        ],
    }).encode()
    req = urllib.request.Request(
        ADAPTER, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.load(r)
    raw = resp["choices"][0]["message"]["content"]
    return parse_judge_output(raw), raw[:160]


CASES = [
    # (expected, label, gt, candidate)
    (True, "pos-verbatim-1",
     "Attention Is All You Need",
     "Attention Is All You Need"),
    (True, "pos-verbatim-2",
     "Deep Residual Learning for Image Recognition",
     "Deep Residual Learning for Image Recognition"),
    (True, "pos-verbatim-3",
     "A Policy Gradient Method for Relational Domain Adaptation",
     "A Policy Gradient Method for Relational Domain Adaptation"),
    (True, "pos-truncation-1",
     "The effects of external planets on inner systems: multiplicities, inclinations, and pathways to eccentric warm Jupiters",
     "The effects of external planets on inner systems: multiplicities ..."),
    (True, "pos-truncation-2",
     "Neural Machine Translation by Jointly Learning to Align and Translate",
     "Neural Machine Translation by Jointly Learning to Align and ..."),
    (True, "pos-casing-punct",
     "ImageNet Classification with Deep Convolutional Neural Networks",
     "imagenet classification with deep convolutional neural networks"),
    (False, "neg-different-1",
     "Attention Is All You Need",
     "Sequence to Sequence Learning with Neural Networks"),
    (False, "neg-different-2",
     "Deep Residual Learning for Image Recognition",
     "Going Deeper with Convolutions"),
    (False, "neg-different-3",
     "Mastering the Game of Go with Deep Neural Networks and Tree Search",
     "Human-level control through deep reinforcement learning"),
]


def main() -> None:
    results = []
    for expected, label, gt, cand in CASES:
        t0 = time.time()
        try:
            got, raw = judge(gt, cand)
            err = ""
        except Exception as exc:  # noqa: BLE001
            got, raw, err = None, "", f"ERROR {exc}"
        ok = "PASS" if got == expected else "FAIL"
        results.append((label, expected, got, ok))
        print(f"{ok} {label}: expected={expected} got={got} "
              f"({time.time()-t0:.1f}s) {err} {raw if not expected and got else ''}",
              flush=True)
    n_pass = sum(1 for *_, ok in results if ok == "PASS")
    pos_pass = sum(1 for l, e, g, ok in results
                   if ok == "PASS" and e is True)
    pos_tot = sum(1 for _, e, _, _ in results if e is True)
    neg_pass = sum(1 for l, e, g, ok in results
                   if ok == "PASS" and e is False)
    neg_tot = sum(1 for _, e, _, _ in results if e is False)
    print(f"\nTOTAL {n_pass}/{len(results)} | "
          f"positives {pos_pass}/{pos_tot} | negatives {neg_pass}/{neg_tot}")
    print("VERDICT:", "CONTROL_PASSED" if n_pass == len(results)
          else ("CONTROL_FAILED_JUDGE_BROKEN" if pos_pass < pos_tot - 1
                else "CONTROL_PARTIAL_INSPECT"))


if __name__ == "__main__":
    main()
