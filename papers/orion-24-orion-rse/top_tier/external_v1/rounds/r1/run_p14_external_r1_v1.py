#!/usr/bin/env python3
"""P14 external round R1 (frontier-agent) + R3 (negative-history ablation) driver, v1.

Frozen by rounds/P14_EXTERNAL_R1R3_EXECUTION_PLAN_V1.{md,json}: the prompt
template, disposition glosses, system registry, retry/timeout policy, missing-run
policy, R3 withhold set, and scoring contract live there and must not change after
the freeze commit. This driver implements them mechanically. stdlib only.

Phases (fail-closed; each exits non-zero on any violation):
  harvest --system CODEX_GPT56|CLAUDE_GLM53 [--ablate] [--force] [--only ID ...] [--dry-run]
  score
  verify

harvest: one call per packet per system, sequential inside a system, at most 3
attempts per packet, 600 s subprocess timeout per attempt. The driver overwrites
schema_version / packet_id / system_id / resource_usage with measured values;
the agent supplies content fields only. A packet with no schema-valid decision
after 3 attempts is recorded in the failure log; the run is DEGRADED (never
imputed). --dry-run renders every prompt and runs the leakage pre-scan without
any agent call.

score: metrics computed by run_p14_external_pilot_v1.system_metrics, imported and
reused verbatim (protocol section 4). No metric definition may live in this file.

verify: byte-compare of the committed partitions against the frozen digests in
the plan JSON; decision-schema conformance of every harvested row; driver-field
and resource-usage checks; re-render of every prompt with byte-compare against
the archived prompt file; leakage re-scan of the record block of every prompt and
programme-name scan of the full prompt; programme-name scan of every raw output
(warning-level). Exit 0 = all integrity checks pass (DEGRADED status, if any, is
reported, not silently dropped).
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROUNDS = os.path.dirname(HERE)
BASE = os.path.dirname(ROUNDS)          # external_v1/
TOP = os.path.dirname(BASE)             # top_tier/
REPO_TOP = os.path.dirname(os.path.dirname(os.path.dirname(BASE)))  # repo root

sys.path.insert(0, BASE)
from validate_p14_external_packets_v1 import (  # noqa: E402
    ENUM_TOKENS, FORBIDDEN_VISIBLE_STRINGS, GOLD_ONLY_KEYS, canonical, check_schema,
)

PLAN_PATH = os.path.join(ROUNDS, "P14_EXTERNAL_R1R3_EXECUTION_PLAN_V1.json")
DECISION_SCHEMA_PATH = os.path.join(TOP, "P14_EXTERNAL_DECISION_SCHEMA_V1.json")
SCRATCH = "/tmp/p14r1_exec"
ATTEMPT_TIMEOUT_S = 600
MAX_ATTEMPTS = 3

CONTENT_FIELDS = [
    "final_claim", "claim_scope", "donor_ownership", "retained_evidence",
    "protocol_deviations", "disposition", "confidence", "authority_status",
    "requested_followups",
]

DISPOSITION_GLOSSES = {
    "PROMOTE": "the bounded claim advances as stated",
    "SUBSUMED": "the apparent advance is already entailed by an existing retained result",
    "INTERACTION_ONLY": "the effect exists only as an interaction; no standalone claim is supported",
    "NEGATIVE": "the evidence refutes the bounded claim",
    "NULL_LIVE": "the evidence neither supports nor refutes; the question stays open",
    "NON_IDENTIFIABLE": "the question cannot be answered with the available instruments",
    "CANNOT_CHECK": "the decision obligations cannot be evaluated from the provided record",
    "REOPEN": "an earlier record must be amended or reopened under changed conditions",
    "STOP": "further work on this question has negative expected value",
}

AUTHORITY_GLOSSES = {
    "NOT_AUTHORITY": "this review does not by itself authorize any claim",
    "CANNOT_CHECK": "authority cannot be determined from the provided record",
    "EXTERNALLY_AUTHORIZED": "the record itself carries external authorization",
}

PROMPT_HEADER = """You are an independent external reviewer of a frozen research
record. You see one record: a bounded research question, its claim-language
constraints, its preregistered decision points, the allowed tools, the resource
budget, a digest binding a hidden adjudication record, and the complete
read-only evidence inventory for the record. Evidence access for this task is
read-only and limited to the records reproduced below; no external data source,
tool execution, or prior history is available or permitted.

Decide the strongest defensible action for this record and return it as a single
JSON object. Respond with the JSON object only - no prose before or after, no
code fences.

Dispositions (choose exactly one):
""" + "\n".join("- %s: %s" % (k, v) for k, v in DISPOSITION_GLOSSES.items()) + """

Authority status (choose exactly one):
""" + "\n".join("- %s: %s" % (k, v) for k, v in AUTHORITY_GLOSSES.items()) + """

Required JSON fields (all required; use an empty array where the type is array
and nothing applies):
- "final_claim": string, the strongest claim this record supports, stated boundedly
- "claim_scope": string, the exact scope within which final_claim holds
- "donor_ownership": array of objects {"source_id": string, "owned_mechanism":
  string, "disposition": one of "ADOPT"|"ADAPT"|"COMPOSE"|"DEFER"|"REJECT"} - one
  entry per donor or prior source the record relies on; empty array if none
- "retained_evidence": array of objects {"artifact_id": string, "polarity": one of
  "POSITIVE"|"NULL"|"NEGATIVE"|"SUBSUMED"|"NON_IDENTIFIABLE", "material": boolean}
  - the evidence records you retain for the decision and their polarity
- "protocol_deviations": array of strings naming any preregistered obligation of
  this record that is not met
- "disposition": exactly one disposition from the list above
- "confidence": number in [0, 1]
- "authority_status": exactly one authority status from the list above
- "requested_followups": array of strings, the follow-up actions you would request

Include no other fields. The harness itself records schema version, packet
identity, system identity, and resource usage; any such fields you emit are
ignored. Stay within the record's claim-language constraints and resource budget.
"""

PROMPT_FOOTER = "=== END OF RECORD ===\n\nReturn the JSON object now." \
    " Keep the whole response within the record's output-token budget."


def out_dir(ablate):
    return os.path.join(HERE, "out_r3" if ablate else "out_r1")


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_suite():
    packets = load_jsonl(os.path.join(BASE, "packets", "p14_external_packets_v1.jsonl"))
    evidence = load_jsonl(os.path.join(BASE, "evidence", "p14_external_evidence_v1.jsonl"))
    gold = load_jsonl(os.path.join(BASE, "protected", "p14_external_gold_v1.jsonl"))
    return packets, {e["artifact_id"]: e for e in evidence}, {g["packet_id"]: g for g in gold}


def load_plan():
    with open(PLAN_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_decision_schema():
    with open(DECISION_SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def record_block(packet, ev_by_id, withhold=()):
    """Render the frozen record (packet + complete evidence inventory).

    The rendered bytes are exactly the committed partition content, reformatted
    deterministically; withhold removes whole evidence records for the R3 arm.
    """
    lines = ["=== FROZEN RESEARCH RECORD ==="]
    for key in ("packet_id", "domain", "question", "claim_language",
                "preregistered_decision_points", "allowed_tools", "resource_budget",
                "gold_record_digest"):
        lines.append("%s: %s" % (key, canonical(packet[key])))
    lines.append("=== EVIDENCE INVENTORY (read-only, complete) ===")
    for item in packet["visible_evidence"]:
        aid = item["artifact_id"]
        if aid in withhold:
            continue
        e = ev_by_id[aid]
        lines.append("[%s] role=%s sha256=%s" % (aid, e["role"], e["sha256"]))
        lines.append(e["content"])
    return "\n".join(lines) + "\n"


def build_prompt(packet, ev_by_id, withhold=()):
    return PROMPT_HEADER + "\n" + record_block(packet, ev_by_id, withhold) + PROMPT_FOOTER


def find_decision_json(text):
    """Last balanced JSON object in text covering all content fields, else None."""
    for m in reversed(list(re.finditer(r"\{", text))):
        depth, in_str, esc = 0, False, False
        for j in range(m.start(), len(text)):
            c = text[j]
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
            elif c == '"':
                in_str = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(text[m.start():j + 1])
                    except Exception:
                        break
                    if isinstance(obj, dict) and set(CONTENT_FIELDS) <= set(obj):
                        return obj
                    break
    return None


def make_decision(packet, system_id, content, measured):
    d = {"schema_version": "P14_EXTERNAL_DECISION_V1",
         "packet_id": packet["packet_id"],
         "system_id": system_id}
    for k in CONTENT_FIELDS:
        d[k] = content[k]
    d["resource_usage"] = measured
    return d


def probe_env_note():
    """Record ambient scratch-dir state (no secrets ever enter artifacts)."""
    entries = sorted(os.listdir(SCRATCH)) if os.path.isdir(SCRATCH) else []
    return {"scratch": SCRATCH, "entries": entries,
            "instruction_files_present": [e for e in entries
                                          if e in ("CLAUDE.md", "AGENTS.md", ".claude")]}


def run_codex(prompt):
    cmd = ["codex", "exec", "--skip-git-repo-check", prompt]
    return subprocess.run(cmd, cwd=SCRATCH, stdin=subprocess.DEVNULL,
                          capture_output=True, text=True, timeout=ATTEMPT_TIMEOUT_S), {
        "command": "codex exec --skip-git-repo-check <prompt-arg>",
        "binary": shutil.which("codex") or "codex",
        "cwd": SCRATCH,
    }


def run_claude(prompt):
    cmd = [os.environ.get("P14_CLAUDE_BIN", "/Users/billy/.local/bin/claude"),
           "-p", prompt, "--output-format", "json"]
    return subprocess.run(cmd, cwd=SCRATCH, stdin=subprocess.DEVNULL,
                          capture_output=True, text=True, timeout=ATTEMPT_TIMEOUT_S), {
        "command": "claude -p <prompt-arg> --output-format json",
        "binary": cmd[0],
        "cwd": SCRATCH,
        "env_recorded": {"CLAUDE_CONFIG_DIR": os.environ.get("CLAUDE_CONFIG_DIR"),
                         "ANTHROPIC_BASE_URL": os.environ.get("ANTHROPIC_BASE_URL"),
                         "ANTHROPIC_MODEL": os.environ.get("ANTHROPIC_MODEL")},
    }


CALLERS = {"CODEX_GPT56": run_codex, "CLAUDE_GLM53": run_claude}


def parse_codex(raw_text):
    note = {}
    m = re.search(r"tokens used:\s*(\d+)", raw_text)
    if m:
        note["tokens_total"] = int(m.group(1))
    m = re.search(r"^model:\s*(\S+)", raw_text, re.M)
    if m:
        note["model"] = m.group(1)
    return raw_text, note


def parse_claude(raw_text):
    note = {}
    try:
        obj = json.loads(raw_text)
    except Exception:
        return raw_text, note
    note["model"] = obj.get("model")
    u = obj.get("usage") or {}
    if "input_tokens" in u:
        note["tokens_in"] = u.get("input_tokens")
        note["tokens_out"] = u.get("output_tokens")
    if isinstance(obj.get("total_cost_usd"), (int, float)):
        note["cost_usd"] = round(float(obj["total_cost_usd"]), 6)
    return obj.get("result") or "", note


PARSERS = {"CODEX_GPT56": parse_codex, "CLAUDE_GLM53": parse_claude}


def append_jsonl(path, row):
    with open(path, "a", encoding="utf-8") as f:
        f.write(canonical(row) + "\n")


def load_decisions(path):
    return {r["packet_id"]: r for r in load_jsonl(path)} if os.path.exists(path) else {}


def evidence_bytes(packet, ev_by_id, withhold=()):
    return sum(len(ev_by_id[i["artifact_id"]]["content"].encode("utf-8"))
               for i in packet["visible_evidence"] if i["artifact_id"] not in withhold)


def leakage_scan_record_block(text):
    """Adjudication-token scan on the record block only (packet+evidence bytes).

    The instruction header necessarily enumerates the decision schema and is
    frozen identically across systems and arms in the plan JSON; it carries no
    packet-specific content, so the fail-closed scan applies to the record block.
    """
    hits = []
    for tok in ENUM_TOKENS + FORBIDDEN_VISIBLE_STRINGS + GOLD_ONLY_KEYS:
        if tok in text:
            hits.append(tok)
    return hits


def phase_harvest(system_id, ablate, force, only, dry_run):
    if system_id not in CALLERS:
        print("FAIL: unknown system %r (registry: %s)" % (system_id, sorted(CALLERS)), file=sys.stderr)
        return 1
    plan = load_plan()
    packets, ev_by_id, gold_by_id = load_suite()
    withhold_map = {p: set(v) for p, v in
                    plan["rounds"]["R3"]["withhold_set"].items()} if ablate else {}
    if ablate:
        subset = set(plan["rounds"]["R3"]["round2_packet_ids"])
        packets = [p for p in packets if p["packet_id"] in subset]
    if only:
        keep = set(only)
        packets = [p for p in packets if p["packet_id"] in keep]
    dec_schema = load_decision_schema()

    out = out_dir(ablate)
    raw_dir = os.path.join(out, "raw", system_id)
    os.makedirs(raw_dir, exist_ok=True)
    suffix = "_R3WITHHELD" if ablate else ""
    dec_path = os.path.join(out, "decisions",
                            "p14_external_decisions_%s%s_v1.jsonl" % (system_id, suffix))
    fail_path = os.path.join(out, "decisions",
                             "p14_external_failed_%s%s_v1.jsonl" % (system_id, suffix))
    os.makedirs(os.path.dirname(dec_path), exist_ok=True)
    done = {} if force else load_decisions(dec_path)

    os.makedirs(SCRATCH, exist_ok=True)
    env_note = probe_env_note()
    summary = {"schema_version": "P14_EXTERNAL_R1R3_HARVEST_SUMMARY_V1",
               "system_id": system_id, "ablate": ablate, "dry_run": dry_run,
               "attempts_per_packet_max": MAX_ATTEMPTS,
               "attempt_timeout_s": ATTEMPT_TIMEOUT_S,
               "env": env_note, "packets_targeted": [p["packet_id"] for p in packets],
               "already_harvested": sorted(done), "failures": []}
    if dry_run:
        leak = {}
        for p in packets:
            prompt = build_prompt(p, ev_by_id, withhold_map.get(p["packet_id"], ()))
            rb = record_block(p, ev_by_id, withhold_map.get(p["packet_id"], ()))
            hits = leakage_scan_record_block(rb)
            if hits or evidence_bytes(p, ev_by_id, withhold_map.get(p["packet_id"], ())) > \
                    p["resource_budget"]["max_evidence_bytes"]:
                leak[p["packet_id"]] = {"leakage_hits": hits} if hits else {"budget": "OVER"}
        summary["dry_run_leakage"] = leak
        sp = os.path.join(out, "harvest_%s%s_dryrun.json" % (system_id, suffix))
        with open(sp, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, sort_keys=True)
            f.write("\n")
        print("DRYRUN %s packets=%d leakage_hits=%d" % (system_id, len(packets), len(leak)))
        return 1 if leak else 0

    caller, parser = CALLERS[system_id], PARSERS[system_id]
    for p in packets:
        pid = p["packet_id"]
        if pid in done:
            continue
        withhold = withhold_map.get(pid, ())
        prompt = build_prompt(p, ev_by_id, withhold)
        with open(os.path.join(raw_dir, "%s.prompt.txt" % pid), "w", encoding="utf-8") as f:
            f.write(prompt)
        ev_bytes = evidence_bytes(p, ev_by_id, withhold)
        accepted, attempt_log = None, []
        for attempt in range(1, MAX_ATTEMPTS + 1):
            t0 = time.time()
            try:
                proc, call_note = caller(prompt)
                wall = round(time.time() - t0, 3)
                out_text, note = parser(proc.stdout or "")
                reason = None
                if proc.returncode != 0:
                    reason = "exit=%d stderr=%s" % (proc.returncode, (proc.stderr or "")[:300])
                elif not out_text.strip():
                    reason = "empty_model_output"
                else:
                    content = find_decision_json(out_text)
                    if content is None:
                        reason = "no_schema_json_in_output"
                    else:
                        cand = make_decision(p, system_id, content, {})
                        errs_before = []
                        import validate_p14_external_packets_v1 as V
                        V._errors = []
                        check_schema(cand, dec_schema, "decision[%s,%s,attempt%d]" % (system_id, pid, attempt))
                        if V._errors:
                            reason = "schema_invalid: %s" % "; ".join(V._errors[:3])
                            V._errors = []
                        else:
                            accepted = (content, note, wall, attempt)
                with open(os.path.join(raw_dir, "%s.attempt%d.out" % (pid, attempt)), "w",
                          encoding="utf-8") as f:
                    json.dump({"returncode": proc.returncode, "attempt": attempt,
                               "wallclock_s": wall, "call_note": call_note,
                               "parse_note": note, "reason": reason,
                               "stdout": (proc.stdout or "")[:20000],
                               "stderr": (proc.stderr or "")[:2000]}, f, indent=2, sort_keys=True)
                attempt_log.append({"attempt": attempt, "wallclock_s": wall, "reason": reason})
                if accepted:
                    break
            except subprocess.TimeoutExpired:
                wall = round(time.time() - t0, 3)
                attempt_log.append({"attempt": attempt, "wallclock_s": wall,
                                    "reason": "timeout_%ds" % ATTEMPT_TIMEOUT_S})
                with open(os.path.join(raw_dir, "%s.attempt%d.out" % (pid, attempt)), "w",
                          encoding="utf-8") as f:
                    json.dump({"returncode": None, "attempt": attempt, "wallclock_s": wall,
                               "reason": "timeout_%ds" % ATTEMPT_TIMEOUT_S,
                               "stdout": "", "stderr": ""}, f, indent=2, sort_keys=True)
        if accepted is None:
            row = {"packet_id": pid, "system_id": system_id, "ablate": ablate,
                   "attempts": attempt_log,
                   "policy": "DEGRADED_no_imputation_after_%d_attempts" % MAX_ATTEMPTS}
            append_jsonl(fail_path, row)
            summary["failures"].append(pid)
            print("DEGRADED %s %s" % (system_id, pid), file=sys.stderr)
            continue
        content, note, wall, attempts = accepted
        measured = {"evidence_bytes_read": ev_bytes,
                    "prompt_chars": len(prompt),
                    "output_chars": len(proc.stdout or ""),
                    "wallclock_s": wall,
                    "attempts": attempts,
                    "withheld_artifacts": sorted(withhold) if withhold else []}
        measured.update({k: v for k, v in note.items() if v is not None})
        decision = make_decision(p, system_id, content, measured)
        append_jsonl(dec_path, decision)
        print("OK %s %s disp=%s attempts=%d wall=%.1fs" % (
            system_id, pid, decision["disposition"], attempts, wall))
    summary["failures"] = sorted(set(summary["failures"]))
    summary["status"] = "DEGRADED" if summary["failures"] else "GREEN"
    sp = os.path.join(out, "harvest_%s%s_summary.json" % (system_id, suffix))
    with open(sp, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
    print("HARVEST_%s %s packets=%d failures=%d" % (
        summary["status"], system_id, len(packets), len(summary["failures"])))
    return 0


def metric_subset(rows_by_pid, packets, gold_by_id):
    golds = [gold_by_id[p["packet_id"]]["gold_disposition"] for p in packets
             if p["packet_id"] in rows_by_pid]
    preds = [rows_by_pid[p["packet_id"]]["disposition"] for p in packets
             if p["packet_id"] in rows_by_pid]
    return golds, preds


def phase_score():
    sys.path.insert(0, BASE)
    from run_p14_external_pilot_v1 import system_metrics  # verbatim reuse (protocol S4)
    plan = load_plan()
    packets, ev_by_id, gold_by_id = load_suite()
    out1, out3 = out_dir(False), out_dir(True)
    systems = sorted(CALLERS)

    r1_rows, r1_missing = {}, {}
    for s in systems:
        rows = load_decisions(os.path.join(
            out1, "decisions", "p14_external_decisions_%s_v1.jsonl" % s))
        r1_rows[s] = rows
        r1_missing[s] = [p["packet_id"] for p in packets if p["packet_id"] not in rows]

    analytics = {"schema_version": "P14_EXTERNAL_R1R3_ANALYTICS_V1",
                 "suite": plan["suite_binding"],
                 "systems": {s: plan["systems"][s] for s in systems},
                 "rounds": {}}
    for s in systems:
        golds, preds = metric_subset(r1_rows[s], packets, gold_by_id)
        m = system_metrics(golds, preds)
        m["n_scored"] = len(preds)
        m["n_missing"] = len(r1_missing[s])
        m["missing_packet_ids"] = r1_missing[s]
        analytics["rounds"]["R1"] = analytics["rounds"].get("R1", {})
        analytics["rounds"]["R1"][s] = {"metrics": m}

    # R3: present arm = R1 rows restricted to the round-pair subset;
    # withheld arm = round-2 packets scored from the ablated harvest,
    # round-1 packets from R1 (identical input, no withhold applies).
    subset_ids = plan["rounds"]["R3"]["round_pair_packet_ids"]
    r2_ids = plan["rounds"]["R3"]["round2_packet_ids"]
    sub_packets = [p for p in packets if p["packet_id"] in set(subset_ids)]
    analytics["rounds"]["R3"] = {}
    for s in systems:
        withheld_rows = load_decisions(os.path.join(
            out3, "decisions", "p14_external_decisions_%s_R3WITHHELD_v1.jsonl" % s))
        present_golds, present_preds = metric_subset(r1_rows[s], sub_packets, gold_by_id)
        mix = dict(r1_rows[s])
        for pid in r2_ids:
            if pid in withheld_rows:
                mix[pid] = withheld_rows[pid]
        wh_golds, wh_preds = metric_subset(mix, sub_packets, gold_by_id)
        r2_packets = [p for p in packets if p["packet_id"] in set(r2_ids)]
        r2_present_g, r2_present_p = metric_subset(r1_rows[s], r2_packets, gold_by_id)
        r2_wh_g, r2_wh_p = metric_subset(mix, r2_packets, gold_by_id)
        analytics["rounds"]["R3"][s] = {
            "present_arm": {"metrics": system_metrics(present_golds, present_preds),
                            "n_scored": len(present_preds)},
            "withheld_arm": {"metrics": system_metrics(wh_golds, wh_preds),
                             "n_scored": len(wh_preds),
                             "round2_rows_from_withheld_harvest": len(
                                 [p for p in r2_ids if p in withheld_rows])},
            "round2_only": {
                "present": system_metrics(r2_present_g, r2_present_p),
                "withheld": system_metrics(r2_wh_g, r2_wh_p)},
            "gold_dispositions_subset": present_golds,
        }

    analytics["co_primary_promotion_condition"] = {
        "status": "CANNOT_CHECK",
        "reason": ("R2 independent blinded human adjudication is not available in this "
                   "execution lane (no non-author adjudicators with signable authority); "
                   "model-only external rounds cannot confirm the co-primary condition. "
                   "No promotion claim is made; the paper state does not change."),
        "missing_authority": "independent blinded human adjudicators (R2)",
    }
    analytics["authority_statement"] = (
        "All harvested systems answer under authority_status constraints of the decision "
        "schema; regardless of any per-row authority_status value emitted by a system, no "
        "row in this round carries adjudication authority for any manuscript claim.")
    ad = os.path.join(out1, "analytics")
    os.makedirs(ad, exist_ok=True)
    with open(os.path.join(ad, "p14_external_r1r3_analytics_v1.json"), "w", encoding="utf-8") as f:
        json.dump(analytics, f, indent=2, sort_keys=True)
        f.write("\n")
    print("SCORE green; see %s" % os.path.join(ad, "p14_external_r1r3_analytics_v1.json"))
    return 0


def phase_verify():
    plan = load_plan()
    packets, ev_by_id, gold_by_id = load_suite()
    dec_schema = load_decision_schema()
    errors, warnings = [], []
    import validate_p14_external_packets_v1 as V

    # 1. suite digests vs frozen plan
    for rel, key in (("packets/p14_external_packets_v1.jsonl", "packets_sha256"),
                     ("evidence/p14_external_evidence_v1.jsonl", "evidence_sha256"),
                     ("protected/p14_external_gold_v1.jsonl", "gold_sha256")):
        got = sha256_file(os.path.join(BASE, rel))
        if got != plan["suite_binding"][key]:
            errors.append("suite digest drift %s: %s != %s" % (rel, got, plan["suite_binding"][key]))

    out1, out3 = out_dir(False), out_dir(True)
    withhold_map = {p: set(v) for p, v in plan["rounds"]["R3"]["withhold_set"].items()}
    total = 0
    for s in sorted(CALLERS):
        for od, ablate in ((out1, False), (out3, True)):
            suffix = "_R3WITHHELD" if ablate else ""
            dec_path = os.path.join(od, "decisions", "p14_external_decisions_%s%s_v1.jsonl" % (s, suffix))
            if not os.path.exists(dec_path):
                if ablate:
                    continue
                errors.append("missing decisions file %s" % dec_path)
                continue
            for d in load_jsonl(dec_path):
                total += 1
                tag = "%s%s[%s]" % (s, suffix, d.get("packet_id"))
                V._errors = []
                check_schema(d, dec_schema, "decision" + tag)
                if V._errors:
                    errors.append("schema %s: %s" % (tag, "; ".join(V._errors[:3])))
                    V._errors = []
                    continue
                if d["packet_id"] not in gold_by_id:
                    errors.append("unknown packet id %s" % tag)
                    continue
                ru = d["resource_usage"]
                for k in ("evidence_bytes_read", "prompt_chars", "output_chars",
                          "wallclock_s", "attempts"):
                    if k not in ru:
                        errors.append("resource_usage missing %s in %s" % (k, tag))
                pkt = next(p for p in packets if p["packet_id"] == d["packet_id"])
                if ru.get("evidence_bytes_read", 0) > pkt["resource_budget"]["max_evidence_bytes"]:
                    errors.append("evidence budget exceeded in %s" % tag)
                # prompt re-render + byte-compare + leakage rescan
                pfile = os.path.join(od, "raw", s, "%s.prompt.txt" % d["packet_id"])
                if not os.path.exists(pfile):
                    errors.append("archived prompt missing %s" % pfile)
                    continue
                rendered = build_prompt(pkt, ev_by_id, withhold_map.get(d["packet_id"], ()))
                with open(pfile, encoding="utf-8") as f:
                    archived = f.read()
                if rendered != archived:
                    errors.append("prompt drift vs archive in %s" % tag)
                hits = leakage_scan_record_block(record_block(
                    pkt, ev_by_id, withhold_map.get(d["packet_id"], ())))
                if hits:
                    errors.append("leakage in record block %s: %s" % (tag, hits))
                # programme-name scan of full prompt + raw outputs (warning level)
                for probe, label in ((archived, "prompt"),):
                    wl = [t for t in FORBIDDEN_VISIBLE_STRINGS if t in probe]
                    if wl:
                        warnings.append("%s of %s mentions %s" % (label, tag, wl))
                raws = sorted(x for x in os.listdir(os.path.join(od, "raw", s))
                              if x.startswith(d["packet_id"] + ".attempt") and x.endswith(".out"))
                for r in raws:
                    with open(os.path.join(od, "raw", s, r), encoding="utf-8") as f:
                        blob = f.read()
                    wl = [t for t in FORBIDDEN_VISIBLE_STRINGS if t in blob]
                    if wl:
                        warnings.append("raw output %s/%s mentions %s" % (tag, r, wl))
    print("VERIFY decisions_checked=%d errors=%d warnings=%d" % (total, len(errors), len(warnings)))
    for e in errors[:20]:
        print("FAIL: %s" % e, file=sys.stderr)
    for w in warnings[:20]:
        print("WARN: %s" % w, file=sys.stderr)
    report = {"schema_version": "P14_EXTERNAL_R1R3_VERIFY_V1", "decisions_checked": total,
              "errors": errors, "warnings": warnings,
              "gold_file_sha256": sha256_file(os.path.join(
                  BASE, "protected", "p14_external_gold_v1.jsonl"))}
    ad = os.path.join(out1, "analytics")
    os.makedirs(ad, exist_ok=True)
    with open(os.path.join(ad, "p14_external_r1r3_verify_v1.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)
        f.write("\n")
    return 1 if errors else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("phase", choices=["harvest", "score", "verify"])
    ap.add_argument("--system", choices=sorted(CALLERS))
    ap.add_argument("--ablate", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.phase == "harvest":
        if not args.system:
            print("FAIL: harvest requires --system", file=sys.stderr)
            return 1
        return phase_harvest(args.system, args.ablate, args.force, args.only, args.dry_run)
    if args.phase == "score":
        return phase_score()
    return phase_verify()


if __name__ == "__main__":
    sys.exit(main())
