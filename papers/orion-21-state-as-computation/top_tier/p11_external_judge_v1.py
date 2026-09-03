#!/usr/bin/env python3
"""P11 external campaign — outcome scoring (judge layer), upstream-verbatim.

LONGMEMEVAL_CLEANED: the per-question-type yes/no answer-check templates are copied
BYTE-EXACT from the frozen repo (src/evaluation/evaluate_qa.py @ pinned commit,
blob recorded in LONGMEMEVAL_EXTERNAL_VERSION_FREEZE_V1.json); the judge model is
the frozen GPT_CLASS lane. abstention branch: '_abs' in question_id (upstream rule).

LONGMEMEVAL_V2: scoring functions are IMPORTED from the materialized frozen repo
(evaluation/qa_eval_metrics.py @ pinned commit) — no reimplementation. Deterministic
matchers run directly; llm_abstention_checker / llm_gotchas_checker use the repo's
_build_*_judge_messages and _parse_llm_binary_judgement with the GPT lane as the
evaluator transport (identical rubric text, CLI instead of an OpenAI client).

Judge cost is recorded but NOT charged to arms (the judge is campaign
infrastructure; its per-call resources go to the campaign resource ledger).
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

BASE = Path(os.environ.get("P11_BASE", str(Path.home() / "orion-p11-campaign")))
V2_REPO = BASE / "data" / "code_LongMemEval-V2"

if str(V2_REPO / "evaluation") not in sys.path:
    sys.path.insert(0, str(V2_REPO / "evaluation"))

qa_eval_metrics = __import__("qa_eval_metrics")  # frozen upstream module

from p11_external_lanes_v1 import call  # noqa: E402

JUDGE_LANE = "gpt-5.5-codexcli"


# ------------------------------------------------- v1 templates (verbatim copy)
# byte-exact from code_LongMemEval/src/evaluation/evaluate_qa.py get_anscheck_prompt

def get_anscheck_prompt(task, question, answer, response, abstention=False):
    if not abstention:
        if task in ['single-session-user', 'single-session-assistant', 'multi-session']:
            template = "I will give you a question, a correct answer, and a response from a model. Please answer yes if the response contains the correct answer. Otherwise, answer no. If the response is equivalent to the correct answer or contains all the intermediate steps to get the correct answer, you should also answer yes. If the response only contains a subset of the information required by the answer, answer no. \n\nQuestion: {}\n\nCorrect Answer: {}\n\nModel Response: {}\n\nIs the model response correct? Answer yes or no only."
            prompt = template.format(question, answer, response)
        elif task == 'temporal-reasoning':
            template = "I will give you a question, a correct answer, and a response from a model. Please answer yes if the response contains the correct answer. Otherwise, answer no. If the response is equivalent to the correct answer or contains all the intermediate steps to get the correct answer, you should also answer yes. If the response only contains a subset of the information required by the answer, answer no. In addition, do not penalize off-by-one errors for the number of days. If the question asks for the number of days/weeks/months, etc., and the model makes off-by-one errors (e.g., predicting 19 days when the answer is 18), the model's response is still correct. \n\nQuestion: {}\n\nCorrect Answer: {}\n\nModel Response: {}\n\nIs the model response correct? Answer yes or no only."
            prompt = template.format(question, answer, response)
        elif task == 'knowledge-update':
            template = "I will give you a question, a correct answer, and a response from a model. Please answer yes if the response contains the correct answer. Otherwise, answer no. If the response contains some previous information along with an updated answer, the response should be considered as correct as long as the updated answer is the required answer.\n\nQuestion: {}\n\nCorrect Answer: {}\n\nModel Response: {}\n\nIs the model response correct? Answer yes or no only."
            prompt = template.format(question, answer, response)
        elif task == 'single-session-preference':
            template = "I will give you a question, a rubric for desired personalized response, and a response from a model. Please answer yes if the response satisfies the desired response. Otherwise, answer no. The model does not need to reflect all the points in the rubric. The response is correct as long as it recalls and utilizes the user's personal information correctly.\n\nQuestion: {}\n\nRubric: {}\n\nModel Response: {}\n\nIs the model response correct? Answer yes or no only."
            prompt = template.format(question, answer, response)
        else:
            raise NotImplementedError
    else:
        template = "I will give you an unanswerable question, an explanation, and a response from a model. Please answer yes if the model correctly identifies the question as unanswerable. The model could say that the information is incomplete, or some other information is given but the asked information is not.\n\nQuestion: {}\n\nExplanation: {}\n\nModel Response: {}\n\nDoes the model correctly identify the question as unanswerable? Answer yes or no only."
        prompt = template.format(question, answer, response)
    return prompt


# ------------------------------------------------------------------ v1 scoring

def v1_score(qid: str, question_type: str, question: str, answer: str,
             response: str | None) -> dict:
    if response is None or not str(response).strip():
        return {"score": None, "cannot_check_reason": "no arm response",
                "judge": "none", "judge_input_tokens": 0, "judge_output_tokens": 0}
    abstention = "_abs" in qid
    prompt = get_anscheck_prompt(question_type, question, answer, str(response)[:4000],
                                 abstention=abstention)
    rec = call(JUDGE_LANE, prompt)
    raw = rec["output"].strip().lower()
    yes = bool(re.match(r"^\s*yes\b", raw))
    no = bool(re.match(r"^\s*no\b", raw))
    if not (yes or no):
        # upstream requires a yes/no answer; non-conforming judge output is a
        # recorded failure, never reinterpreted
        return {"score": None, "cannot_check_reason": f"judge nonconforming: {raw[:120]}",
                "judge": "llm_yes_no", "judge_raw": raw[:400],
                "judge_input_tokens": rec["input_tokens"],
                "judge_output_tokens": rec["output_tokens"]}
    return {"score": 1 if yes else 0, "judge": "llm_yes_no",
            "judge_raw": raw[:80], "judge_input_tokens": rec["input_tokens"],
            "judge_output_tokens": rec["output_tokens"]}


# ------------------------------------------------------------------ v2 scoring

_V2_LLM_CHECKERS = {"llm_abstention_checker", "llm_gotchas_checker"}


def _messages_to_prompt(messages: list[dict]) -> str:
    parts = []
    for m in messages:
        role = m.get("role", "user")
        parts.append(f"[{role}]\n{m.get('content', '')}")
    return "\n\n".join(parts)


def v2_score(question_item: dict, response: str | None) -> dict:
    if response is None or not str(response).strip():
        return {"score": None, "cannot_check_reason": "no arm response",
                "judge": "none", "judge_input_tokens": 0, "judge_output_tokens": 0}
    spec = question_item["eval_function"]
    func, kwargs = qa_eval_metrics.parse_eval_function_spec(spec)
    name = qa_eval_metrics.eval_name(spec)
    if name not in _V2_LLM_CHECKERS:
        ok = func(str(response), question_item["answer"], **kwargs)
        return {"score": int(bool(ok)), "judge": name,
                "judge_input_tokens": 0, "judge_output_tokens": 0}
    if name == "llm_abstention_checker":
        messages = qa_eval_metrics._build_abstention_judge_messages(
            question_text=qa_eval_metrics._extract_question_text(question_item),
            reference_answer=str(question_item.get("answer", "")),
            model_full_response=str(response)[:8000],
            model_final_answer=str(response)[:2000])
    else:
        messages = qa_eval_metrics._build_gotchas_judge_messages(
            question_text=qa_eval_metrics._extract_question_text(question_item),
            reference_answer=str(question_item.get("answer", "")),
            model_full_response=str(response)[:8000],
            model_final_answer=str(response)[:2000])
    rec = call(JUDGE_LANE, _messages_to_prompt(messages))
    try:
        label, reason = qa_eval_metrics._parse_llm_binary_judgement(rec["output"])
        return {"score": int(label), "judge": name, "judge_reason": reason[:400],
                "judge_input_tokens": rec["input_tokens"],
                "judge_output_tokens": rec["output_tokens"]}
    except ValueError as exc:
        return {"score": None, "cannot_check_reason": f"judge parse failure: {exc}"[:200],
                "judge": name, "judge_raw": rec["output"][:400],
                "judge_input_tokens": rec["input_tokens"],
                "judge_output_tokens": rec["output_tokens"]}


JUDGE_LEDGER: dict = {"v1_calls": 0, "v2_llm_calls": 0,
                      "judge_input_tokens": 0, "judge_output_tokens": 0}


def record_judge(result: dict, benchmark: str) -> None:
    if benchmark == "LONGMEMEVAL_CLEANED" and result.get("score") is not None:
        JUDGE_LEDGER["v1_calls"] += 1
    if benchmark == "LONGMEMEVAL_V2" and result.get("judge", "").startswith("llm_") \
            and result.get("score") is not None:
        JUDGE_LEDGER["v2_llm_calls"] += 1
    JUDGE_LEDGER["judge_input_tokens"] += result.get("judge_input_tokens", 0) or 0
    JUDGE_LEDGER["judge_output_tokens"] += result.get("judge_output_tokens", 0) or 0


def score(benchmark: str, question_item: dict, response: str | None) -> dict:
    if benchmark == "LONGMEMEVAL_CLEANED":
        r = v1_score(question_item["question_id"], question_item["question_type"],
                     question_item["question"], question_item["answer"], response)
    elif benchmark == "LONGMEMEVAL_V2":
        r = v2_score(question_item, response)
    else:
        raise ValueError(benchmark)
    record_judge(r, benchmark)
    return r


if __name__ == "__main__":
    # self-test: deterministic matchers on synthetic strings (no lanes needed)
    q = {"eval_function": "norm_phrase_set_match|lower=true|normalize_hyphen=true|strip_punct=true|separators=,;|require_non_empty=true",
         "answer": "Denver; Boulder", "question": "x", "id": "t1"}
    print("det match TRUE:", v2_score(q, "denver and boulder")["score"])
    print("det match FALSE:", v2_score(q, "Denver only")["score"])
    print("v1 template len:",
          len(get_anscheck_prompt("multi-session", "q", "a", "r")),
          len(get_anscheck_prompt("temporal-reasoning", "q", "a", "r", abstention=True)))
