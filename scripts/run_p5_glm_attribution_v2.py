#!/usr/bin/env python3
"""P5 NR-01 revival driver: V1-prompt replay control + V2 licensed-evidence staged attribution.

Frozen protocol: papers/paper-05-self-orion/protocol/P5_ATTRIBUTION_INSTRUMENT_V2_PROTOCOL.json
(pre-registered before any V2 outcome was produced).

Runs the frozen 24-case suite (PROTECTED_SUITE_V1.json, untouched) in two arms under
identical serving conditions:

  control   -- verbatim V1 ATTRIBUTION_PROMPT (imported from run_p5_glm_attribution.py)
  treatment -- Stage A licensed-evidence extraction + deterministic Stage B mapping

Outputs to papers/paper-05-self-orion/evidence/glm-5.2-attribution-v2/ (new directory;
the historical V1 evidence dir is never written).

Usage: python3 scripts/run_p5_glm_attribution_v2.py [--arm control|treatment|both]
Stdlib only. Resumable: existing per-case rows in the output jsonl are kept.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SUITE_PATH = REPO / "papers/paper-05-self-orion/evidence/hidden-cause-suite/PROTECTED_SUITE_V1.json"
PROTOCOL_PATH = REPO / "papers/paper-05-self-orion/protocol/P5_ATTRIBUTION_INSTRUMENT_V2_PROTOCOL.json"
OUT_DIR = REPO / "papers/paper-05-self-orion/evidence/glm-5.2-attribution-v2"
V1_SCRIPT = REPO / "scripts/run_p5_glm_attribution.py"

ENDPOINT = "https://api.z.ai/api/anthropic/v1/messages"
MODEL = os.environ.get("GLM_MODEL", "glm-5.2")
TEMPERATURE = 0.0
MAX_TOKENS = 2048
RETRIES = 2

LOCUS_TO_FAMILY = {
    "SEARCH_RETRIEVAL_LOOKUP": "RETRIEVAL_MISS",
    "PLANNING_ROUTING": "ROUTING_PLANNING_MISS",
    "CODE_LOGIC_IMPLEMENTATION": "IMPLEMENTATION_BUG",
    "EXTERNAL_DEPENDENCY_ENVIRONMENT_TOOL": "ENVIRONMENT_DEPENDENCY_TOOL_FAILURE",
    "EVALUATOR_MEASUREMENT_SYSTEM": "EVALUATOR_METRIC_BUG",
    "REPRESENTATION_ENCODING_FORMAT": "REPRESENTATION_GAP",
    "PROTOCOL_SPECIFICATION_MEASUREMENT_DESIGN": "MEASUREMENT_SPECIFICATION_GAP",
    "FOUNDATIONAL_METHOD": "METHOD_BASIS_GAP",
}
LOCUS_VOCAB = set(LOCUS_TO_FAMILY) | {"NONE"}
FAMILIES = sorted(set(LOCUS_TO_FAMILY.values()))

FAMILY_DEFINITIONS = """1. RETRIEVAL_MISS - Search, retrieval, or lookup system fails to find relevant content that exists
2. ROUTING_PLANNING_MISS - Agent correctly identifies a problem but routes or plans the solution incorrectly
3. IMPLEMENTATION_BUG - Code has a concrete bug (off-by-one, wrong logic, incorrect implementation)
4. ENVIRONMENT_DEPENDENCY_TOOL_FAILURE - Failure due to external dependency, environment, or tool compatibility
5. EVALUATOR_METRIC_BUG - Measurement, evaluation, or benchmarking system is flawed or misaligned
6. REPRESENTATION_GAP - Correct algorithm/data but wrong representation, encoding, or format choice
7. MEASUREMENT_SPECIFICATION_GAP - Evaluation protocol or metric specification doesn't capture intended outcome
8. METHOD_BASIS_GAP - Foundational method or approach cannot handle required generalization"""

# Stage A: extraction only. No diagnosis, no family names, no outside knowledge.
EXTRACTION_PROMPT = """You are a precise evidence extractor. You do NOT diagnose. You extract, as verbatim quotes, only what the case text itself states.

SYSTEM LOCUS CATEGORIES (each restates one published root-cause family definition; pick by which system the quoted span asserts a defect, failure or infeasibility IN):
- SEARCH_RETRIEVAL_LOOKUP: a search, retrieval or lookup system failing to find content that exists
- PLANNING_ROUTING: a planning or routing mechanism chose the wrong route/plan/sequence
- CODE_LOGIC_IMPLEMENTATION: the code's logic/implementation itself is defective (wrong logic, incorrect assumption, bad accumulation, inefficient implementation)
- EXTERNAL_DEPENDENCY_ENVIRONMENT_TOOL: an external dependency, environment property, or tool compatibility is what the failure is due to
- EVALUATOR_MEASUREMENT_SYSTEM: the measurement/evaluation/benchmarking machinery is flawed or produces wrong/inconsistent numbers
- REPRESENTATION_ENCODING_FORMAT: the algorithm/data is correct but the representation, encoding, format or data-structure CHOICE is wrong
- PROTOCOL_SPECIFICATION_MEASUREMENT_DESIGN: the evaluation protocol / metric specification does not capture the intended outcome, or is infeasible to implement as specified
- FOUNDATIONAL_METHOD: the foundational method or approach cannot handle a required generalization/scaling
- NONE: no licensed statement supports any category

HARD RULES:
- Use ONLY what the symptom and context state. No outside knowledge, no inferred mechanisms, no world model about how such systems usually fail.
- Every non-absent field must carry a verbatim quote from the symptom or context.
- Never name a root-cause family. Never diagnose. Extract only.

Extract these four fields:

1. failing_subject: the system/component the failure sentence asserts is failing (quote + locus category).
2. stated_cause: an explicit causal clause in the text ("because X", "due to X", "since X", or an appositive naming the defect), classified by the locus category of the system whose failure or defect the clause asserts. absent=true if the text contains no explicit causal clause.
3. working_failing_delta: present only if the SAME system/code is described as working in one regime and failing in another. differs_by="ENVIRONMENT_OR_DATA_PROPERTY" only when the property that differs between the regimes belongs to the environment or the input data (a code change or two different measurements disagreeing is NOT such a delta). absent=true otherwise.
4. stated_code_defect: value="YES" only if the text itself asserts the code's logic/implementation is defective. A wrong choice of representation/format/data-structure with the algorithm otherwise correct is NOT a code defect (that is a REPRESENTATION_ENCODING_FORMAT locus). value="NO" otherwise; quote only when YES.

Respond in JSON format only:
{
  "failing_subject": {"quote": "...", "locus": "CATEGORY or NONE"},
  "stated_cause": {"absent": false, "quote": "...", "locus": "CATEGORY or NONE"},
  "working_failing_delta": {"absent": true, "quote": "", "differs_by": "NONE"},
  "stated_code_defect": {"value": "NO", "quote": ""},
  "notes": "one sentence, extraction remarks only"
}

---

Case {CASE_ID}:

VISIBLE SYMPTOM:
{VISIBLE_SYMPTOM}

CONTEXT:
{CONTEXT}

Extract the licensed evidence:"""


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_v1_prompt() -> str:
    """Import ATTRIBUTION_PROMPT verbatim from the V1 driver."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("run_p5_glm_attribution", V1_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod.ATTRIBUTION_PROMPT


def call_glm(prompt: str) -> tuple[str, str, int, int, float]:
    """Direct Anthropic-messages call to the z.ai backend (same backend the original
    campaign reached through the local 127.0.0.1:8765 adapter). Returns
    (text, served_model, prompt_tokens, completion_tokens, latency)."""
    token = ""
    try:
        with open(os.path.expanduser("~/.claude-cn/settings.json")) as f:
            token = json.load(f)["env"]["ANTHROPIC_AUTH_TOKEN"]
    except Exception as e:
        raise RuntimeError(f"cannot load ANTHROPIC_AUTH_TOKEN: {e}") from e
    body = json.dumps({
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(ENDPOINT, data=body, headers={
        "x-api-key": token,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    })
    start = time.time()
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.load(r)
    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    usage = data.get("usage", {})
    return (
        text,
        data.get("model", MODEL),
        usage.get("input_tokens", 0),
        usage.get("output_tokens", 0),
        time.time() - start,
    )


def parse_json_block(raw: str) -> dict:
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0]
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0]
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if m:
        raw = m.group(0)
    return json.loads(raw.strip())


def call_with_retry(prompt: str) -> dict:
    """Returns {ok, text, served_model, prompt_tokens, completion_tokens, latency, error}."""
    last_err = None
    for attempt in range(RETRIES + 1):
        try:
            text, served, pt, ct, lat = call_glm(prompt)
            return {"ok": True, "text": text, "served_model": served,
                    "prompt_tokens": pt, "completion_tokens": ct, "latency": lat, "error": None}
        except Exception as e:  # noqa: BLE001 - recorded, never dropped
            last_err = str(e)[:400]
            time.sleep(3 * (attempt + 1))
    return {"ok": False, "text": "", "served_model": MODEL, "prompt_tokens": 0,
            "completion_tokens": 0, "latency": 0.0, "error": last_err}


def sanitize_locus(value, field_name, flags):
    if value in LOCUS_VOCAB:
        return value
    if value is not None:
        flags.append(f"locus_out_of_vocabulary:{field_name}:{value!r}")
    return "NONE"


def stage_b_map(ext: dict) -> tuple[str, str, list[str]]:
    """Deterministic Stage B mapping, exactly the pre-registered rules R1-R6."""
    flags: list[str] = []
    subj = ext.get("failing_subject") or {}
    cause = ext.get("stated_cause") or {}
    delta = ext.get("working_failing_delta") or {}
    defect = ext.get("stated_code_defect") or {}

    subj_locus = sanitize_locus(subj.get("locus"), "failing_subject", flags)
    cause_present = not cause.get("absent", True) and bool(cause.get("quote"))
    cause_locus = sanitize_locus(cause.get("locus"), "stated_cause", flags)
    delta_present = not delta.get("absent", True) and delta.get("differs_by") == "ENVIRONMENT_OR_DATA_PROPERTY"
    defect_yes = defect.get("value") == "YES"

    # R1: self-contradictory licensed evidence -> CANNOT_DISTINGUISH
    if defect_yes and cause_present and cause_locus in LOCUS_TO_FAMILY \
            and LOCUS_TO_FAMILY[cause_locus] != "IMPLEMENTATION_BUG":
        return "CANNOT_DISTINGUISH", "R1_conflict", flags
    # R2: asserted concrete code defect
    if defect_yes:
        return "IMPLEMENTATION_BUG", "R2_stated_code_defect", flags
    # R3: explicit stated-cause clause determines the locus
    if cause_present and cause_locus in LOCUS_TO_FAMILY:
        return LOCUS_TO_FAMILY[cause_locus], "R3_stated_cause", flags
    # R4: regime delta on an environment/data property
    if delta_present:
        return "ENVIRONMENT_DEPENDENCY_TOOL_FAILURE", "R4_working_failing_delta", flags
    # R5: failing subject component class
    if subj_locus in LOCUS_TO_FAMILY:
        return LOCUS_TO_FAMILY[subj_locus], "R5_failing_subject", flags
    # R6: no licensed evidence
    return "CANNOT_DISTINGUISH", "R6_no_licensed_evidence", flags


def run_arm(arm: str, cases: list[dict], v1_prompt: str) -> list[dict]:
    out_path = OUT_DIR / ("results_control_v1replay.jsonl" if arm == "control" else "results_treatment_v2.jsonl")
    done: dict[str, dict] = {}
    if out_path.exists():
        for line in out_path.read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                done[row["case_id"]] = row
    rows: list[dict] = []
    for i, case in enumerate(cases, 1):
        cid = case["case_id"]
        if cid in done:
            rows.append(done[cid])
            print(f"[{i}/{len(cases)}] {cid}: resumed {done[cid].get('outcome', done[cid].get('attributed_root_cause'))}")
            continue
        symptom = case["visible_symptom"]
        context = json.dumps(case["candidate_visible_context"], indent=2)
        if arm == "control":
            prompt = v1_prompt.replace("{CASE_ID}", cid).replace("{VISIBLE_SYMPTOM}", symptom).replace("{CONTEXT}", context)
        else:
            prompt = EXTRACTION_PROMPT.replace("{CASE_ID}", cid).replace("{VISIBLE_SYMPTOM}", symptom).replace("{CONTEXT}", context)
        res = call_with_retry(prompt)
        row = {
            "case_id": cid,
            "arm": arm,
            "gold_root_cause": case["protected_root_cause"],
            "requested_model": MODEL,
            "served_model": res["served_model"],
            "prompt_tokens": res["prompt_tokens"],
            "completion_tokens": res["completion_tokens"],
            "latency_seconds": round(res["latency"], 3),
        }
        if not res["ok"]:
            row.update({"outcome": "ERROR", "error": res["error"], "raw": ""})
            print(f"[{i}/{len(cases)}] {cid}: ERROR {res['error'][:80]}")
        elif arm == "control":
            try:
                parsed = parse_json_block(res["text"])
                attributed = parsed.get("attributed_root_cause", "")
                row.update({
                    "outcome": "ATTRIBUTED" if attributed in FAMILIES else "INVALID_LABEL",
                    "attributed_root_cause": attributed,
                    "confidence": parsed.get("confidence", "LOW"),
                    "competing_causes": parsed.get("competing_causes", []),
                    "intervention_prediction": parsed.get("intervention_prediction", ""),
                    "reasoning": parsed.get("reasoning", ""),
                    "raw": res["text"],
                })
                print(f"[{i}/{len(cases)}] {cid}: {attributed} ({row['outcome']})")
            except Exception as e:  # noqa: BLE001
                row.update({"outcome": "PARSE_ERROR", "error": str(e)[:400], "raw": res["text"]})
                print(f"[{i}/{len(cases)}] {cid}: PARSE_ERROR")
        else:
            try:
                ext = parse_json_block(res["text"])
                family, rule, flags = stage_b_map(ext)
                row.update({
                    "outcome": "ATTRIBUTED" if family in FAMILIES else "CANNOT_DISTINGUISH",
                    "attributed_root_cause": family,
                    "fired_rule": rule,
                    "extraction_flags": flags,
                    "extraction": ext,
                    "raw": res["text"],
                })
                print(f"[{i}/{len(cases)}] {cid}: {family} via {rule}")
            except Exception as e:  # noqa: BLE001
                row.update({"outcome": "PARSE_ERROR", "error": str(e)[:400], "raw": res["text"]})
                print(f"[{i}/{len(cases)}] {cid}: PARSE_ERROR")
        rows.append(row)
        with open(out_path, "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
    return rows


def score(rows: list[dict]) -> dict:
    """Accuracy + standard one-vs-rest macro-F1; CANNOT_DISTINGUISH and errors reported
    separately (never counted as success), per the pre-registered scoring rule."""
    scored = [r for r in rows if r.get("outcome") == "ATTRIBUTED"]
    cd = [r["case_id"] for r in rows if r.get("outcome") == "CANNOT_DISTINGUISH"]
    errs = [r["case_id"] for r in rows if r.get("outcome") in ("ERROR", "PARSE_ERROR", "INVALID_LABEL")]
    correct = [r for r in scored if r["attributed_root_cause"] == r["gold_root_cause"]]
    wrong = [{"case_id": r["case_id"], "gold": r["gold_root_cause"],
              "attributed": r["attributed_root_cause"]} for r in scored
             if r["attributed_root_cause"] != r["gold_root_cause"]]
    tp = {f: 0 for f in FAMILIES}
    fp = {f: 0 for f in FAMILIES}
    fn = {f: 0 for f in FAMILIES}
    for r in scored:
        a, g = r["attributed_root_cause"], r["gold_root_cause"]
        if a == g:
            tp[a] += 1
        else:
            fp[a] += 1
            fn[g] += 1
    f1s = []
    for f in FAMILIES:
        denom = 2 * tp[f] + fp[f] + fn[f]
        f1s.append((2 * tp[f] / denom) if denom else 0.0)
    macro_f1 = sum(f1s) / len(f1s)
    n = len(rows)
    return {
        "n": n,
        "scored": len(scored),
        "correct": len(correct),
        "accuracy": len(correct) / n if n else 0.0,
        "accuracy_over_scored": len(correct) / len(scored) if scored else 0.0,
        "standard_macro_f1": macro_f1,
        "cannot_distinguish": cd,
        "runtime_or_parse_errors": errs,
        "errors_detail": wrong,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["control", "treatment", "both"], default="both")
    args = ap.parse_args()

    suite = json.loads(SUITE_PATH.read_text())
    cases = suite["cases"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    v1_prompt = load_v1_prompt()

    arms = ["control", "treatment"] if args.arm == "both" else [args.arm]
    report: dict = {
        "campaign_id": "p5-glm-attribution-instrument-v2-nr01",
        "lane": "NR-01",
        "protocol_path": str(PROTOCOL_PATH.relative_to(REPO)),
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "suite_path": str(SUITE_PATH.relative_to(REPO)),
        "suite_sha256": sha256_file(SUITE_PATH),
        "v1_prompt_sha256": hashlib.sha256(v1_prompt.encode()).hexdigest(),
        "requested_model": MODEL,
        "temperature": TEMPERATURE,
        "timestamp": time.time(),
        "arms": {},
    }
    for arm in arms:
        print(f"=== arm: {arm} ===")
        rows = run_arm(arm, cases, v1_prompt)
        (OUT_DIR / ("results_control_v1replay.jsonl" if arm == "control" else "results_treatment_v2.jsonl")).write_text(
            "".join(json.dumps(r) + "\n" for r in rows))
        report["arms"][arm] = score(rows)
        served = sorted({r.get("served_model") for r in rows})
        report["arms"][arm]["served_models"] = served
        print(json.dumps(report["arms"][arm], indent=1))

    (OUT_DIR / "report.json").write_text(json.dumps(report, indent=2))
    print("report written:", OUT_DIR / "report.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
