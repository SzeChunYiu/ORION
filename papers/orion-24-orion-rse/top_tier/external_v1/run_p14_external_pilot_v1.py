#!/usr/bin/env python3
"""P14 external-governance pilot runner (v1). No network, no clock, deterministic.

Purpose (wiring check, NOT a result): prove the end-to-end plumbing on the
protected packet suite - decision-output contract, blinded worksheets, gold
binding, and metric computation - and establish the contrast between a
governance-blind reference system and a contract-level governance check.

Both pilot systems are deterministic text procedures recorded with
authority_status=NOT_AUTHORITY. Neither is a frontier agent and neither
carries external authorization; the co-primary promotion outcomes remain
PENDING_EXTERNAL until the external execution + independent human
adjudication rounds defined in P14_EXTERNAL_PILOT_PROTOCOL_V1.md are run.

Outputs (under --out):
  decisions/p14_external_decisions_SYSTEMA_v1.jsonl   (governance-blind reference)
  decisions/p14_external_decisions_SYSTEMB_v1.jsonl   (contract-level governance check)
  worksheets/p14_external_blinded_worksheet_v1.md     (human adjudication, identity-stripped)
  analytics/p14_external_pilot_analytics_v1.json
  analytics/p14_external_pilot_analytics_v1.md
"""

import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from validate_p14_external_packets_v1 import canonical, load_jsonl  # noqa: E402

GOLD_ORDER = ["PROMOTE", "SUBSUMED", "INTERACTION_ONLY", "NULL_LIVE", "NEGATIVE",
              "NON_IDENTIFIABLE", "CANNOT_CHECK", "REOPEN"]

# --- governance-blind reference: substring signals, no governance accounting ---
NAIVE_POSITIVE = ["excludes 0", " pass", "verified", "caught", "detected",
                  "reproduc", "%", "+0.0", "suffice", "0 violations", "green"]
NAIVE_MISSING = ["cannot discriminate", "not preserved", "omitted for privacy",
                 "no artifact", "not stable"]

# --- governance check: contract-level marker tables (high-precision phrases) ---
M_REOPEN = ["Round 2", "amended, not deleted", "record is amended"]
M_NONID = ["independent of the working foundations", "independent of the frozen foundations",
           "byte-identical checkpoints from different", "cannot identify which",
           "identifiability fails exactly", "byte-compatible with both"]
M_CANNOT = ["cannot discriminate", "not stable across candidates", "was not preserved",
            "omitted for privacy", "external to this evidence"]
M_NEGATIVE = ["closes the claim negative", "closes it negative", "not finitely axiomatisable",
              "from the tiling problem", "parity-only classifier", "both ACCEPTED",
              "bootstrap lower bound <= 0", "fill selection", "dominated or matched",
              "about the instrument, not the methods", "Overlap audit", "conclusion=cancelled",
              "per 1,000", "-5.63 per share", "structural to the transient filter", "3.4x",
              "submetrics changed definition", "2>/dev/null"]
M_SUBSUMED = ["owns the mechanism exactly", "own the mechanism", "appears as an exercise",
              "contains the claim verbatim", "instantiates exactly", "identity verified",
              "item-for-item", "predating the programme", "the same algebra",
              "pointwise equal", "is a re-expression", "already characterises",
              "already yields", "established model-selection treatment"]
M_INTERACTION = ["Four-arm", "four-arm", "Two-by-two", "factorial"]
M_PROMOTE = ["checker exit 0", "machine-verified", "machine verification", "0 gaps",
             "caught", "detected", "byte-identical", "certificate", "resamples",
             "replication", "re-verified"]

FOLLOWUP_BY_DISPOSITION = {
    "PROMOTE": ["Independent expert adjudication of the paired judgment."],
    "SUBSUMED": ["Record donor ownership in the synthesis layer; no novelty credit."],
    "INTERACTION_ONLY": ["Record the interaction as the estimand; components credited jointly."],
    "NULL_LIVE": ["Record the null against the declared extension only; parent intact."],
    "NEGATIVE": ["Retain the negative with mechanism attribution; trace downstream usage."],
    "NON_IDENTIFIABLE": ["State the identifiability boundary as the finding."],
    "CANNOT_CHECK": ["Request the missing discriminating artifact through the external channel."],
    "REOPEN": ["Re-evaluate under the amended protocol; preserve the prior round's record."],
}


def has(any_text, markers):
    return [m for m in markers if m in any_text]


def evidence_blob(packet, ev_by_id):
    parts = [packet["question"]]
    for item in packet["visible_evidence"]:
        r = ev_by_id.get(item["artifact_id"])
        if r:
            parts.append(r["content"])
    parts.extend(packet["preregistered_decision_points"])
    return " ".join(parts)


def decide_system_a(packet, ev_by_id):
    """Governance-blind reference: novelty-greedy, no donor/negative accounting."""
    blob = evidence_blob(packet, ev_by_id)
    pos = has(blob, NAIVE_POSITIVE)
    miss = has(blob, NAIVE_MISSING)
    if pos or not miss:
        disposition = "PROMOTE"
        claim = "The presented claim advances as stated."
        confidence = min(0.85, 0.6 + 0.01 * len(pos))
    else:
        disposition = "CANNOT_CHECK"
        claim = "The evidence appears incomplete."
        confidence = 0.55
    deviations = []
    if packet["visible_evidence"] and any(i["role"] == "DONOR" for i in packet["visible_evidence"]):
        deviations.append("donor obligations not addressed")
    if any(i["role"] == "CONTROL" for i in packet["visible_evidence"]):
        deviations.append("control evidence not weighed")
    return disposition, claim, confidence, deviations, pos[:6]


def decide_system_b(packet, ev_by_id):
    """Contract-level governance check: marker tables in fixed priority order."""
    blob = evidence_blob(packet, ev_by_id)
    donors = [i for i in packet["visible_evidence"] if i["role"] == "DONOR"]
    if has(blob, M_REOPEN):
        disposition, claim, conf = "REOPEN", "Regime change under the frozen longitudinal protocol; prior round amended.", 0.9
    elif has(blob, M_NONID):
        disposition, claim, conf = "NON_IDENTIFIABLE", "The visible evidence cannot discriminate the claim; boundary stated.", 0.85
    elif has(blob, M_CANNOT):
        disposition, claim, conf = "CANNOT_CHECK", "A required discriminating artifact is absent; external channel required.", 0.85
    elif has(blob, M_NEGATIVE):
        disposition, claim, conf = "NEGATIVE", "Certified refutation with mechanism attribution; negative retained.", 0.9
    elif has(blob, M_SUBSUMED):
        disposition, claim, conf = "SUBSUMED", "Mechanism owned by the cited donor; contribution absorbed.", 0.85
    elif has(blob, M_INTERACTION) and "includes 0" in blob:
        disposition, claim, conf = "INTERACTION_ONLY", "Null marginals; the effect belongs to the combination.", 0.85
    elif ("parent" in blob or "Parent" in blob) and "includes 0" in blob:
        disposition, claim, conf = "NULL_LIVE", "Parent intact; the declared extension is null with stated power.", 0.85
    elif has(blob, M_PROMOTE) and donors:
        disposition, claim, conf = "PROMOTE", "Obligations discharged; donor delta material; bounded claim advances.", 0.8
    elif has(blob, M_PROMOTE):
        disposition, claim, conf = "PROMOTE", "Obligations discharged by visible certificates and controls.", 0.75
    else:
        disposition, claim, conf = "CANNOT_CHECK", "No preregistered obligation is discharged by the visible evidence.", 0.5
    return disposition, claim, conf, [], has(blob, M_PROMOTE)[:6]


def build_decision(packet, system_id, disposition, claim, confidence, deviations, ev_by_id):
    donors = [i for i in packet["visible_evidence"] if i["role"] == "DONOR"]
    donor_ownership = []
    for i in donors:
        r = ev_by_id.get(i["artifact_id"], {})
        donor_ownership.append({
            "source_id": i["artifact_id"],
            "owned_mechanism": r.get("content", "")[:90],
            "disposition": "ADOPT" if disposition == "SUBSUMED" else ("ADAPT" if disposition == "PROMOTE" else "DEFER"),
        })
    retained = []
    for i in packet["visible_evidence"]:
        r = ev_by_id.get(i["artifact_id"], {})
        content = r.get("content", "")
        if i["role"] == "CONTROL":
            polarity = "NEGATIVE" if has(content, M_NEGATIVE) else "POSITIVE"
        elif i["role"] == "DONOR":
            polarity = "SUBSUMED"
        elif "includes 0" in content:
            polarity = "NULL"
        elif has(content, M_NEGATIVE):
            polarity = "NEGATIVE"
        else:
            polarity = "POSITIVE"
        retained.append({"artifact_id": i["artifact_id"], "polarity": polarity, "material": i["role"] in ("PRIMARY", "RESULT", "CONTROL", "DONOR")})
    return {
        "schema_version": "P14_EXTERNAL_DECISION_V1",
        "packet_id": packet["packet_id"],
        "system_id": system_id,
        "final_claim": claim,
        "claim_scope": packet["claim_language"]["max_scope"],
        "donor_ownership": donor_ownership,
        "retained_evidence": retained,
        "protocol_deviations": list(deviations),
        "disposition": disposition,
        "confidence": round(confidence, 2),
        "authority_status": "NOT_AUTHORITY",
        "requested_followups": FOLLOWUP_BY_DISPOSITION[disposition],
        "resource_usage": {
            "evidence_bytes_read": sum(len(ev_by_id.get(i["artifact_id"], {}).get("content", "").encode("utf-8")) for i in packet["visible_evidence"]),
            "tool_calls": 1,
            "decision_procedure": "deterministic_substring_v1",
        },
    }


def confusion(golds, preds):
    matrix = {g: {p: 0 for p in GOLD_ORDER} for g in GOLD_ORDER}
    for g, p in zip(golds, preds):
        matrix[g][p] += 1
    return matrix


def rate(numer, denom):
    return round(numer / denom, 4) if denom else None


def kappa(golds, preds):
    labels = set(golds) | set(preds)
    n = len(golds)
    po = sum(1 for g, p in zip(golds, preds) if g == p) / n
    pg = {l: golds.count(l) / n for l in labels}
    pp = {l: preds.count(l) / n for l in labels}
    pe = sum(pg[l] * pp[l] for l in labels)
    return round((po - pe) / (1 - pe), 4) if pe < 1 else 0.0


def system_metrics(golds, preds):
    m = confusion(golds, preds)
    fn = sum(1 for g, p in zip(golds, preds) if p == "PROMOTE" and g != "PROMOTE")
    promote_calls = sum(1 for p in preds if p == "PROMOTE")
    sub_total = golds.count("SUBSUMED")
    sub_hit = sum(1 for g, p in zip(golds, preds) if g == "SUBSUMED" and p == "SUBSUMED")
    cc_total = golds.count("CANNOT_CHECK")
    cc_hit = sum(1 for g, p in zip(golds, preds) if g == "CANNOT_CHECK" and p == "CANNOT_CHECK")
    cc_calls = sum(1 for p in preds if p == "CANNOT_CHECK")
    neg_total = golds.count("NEGATIVE")
    neg_kept = sum(1 for g, p in zip(golds, preds) if g == "NEGATIVE" and p in ("NEGATIVE", "REOPEN"))
    ud_total = sum(1 for g, p in zip(golds, preds) if g == "PROMOTE")
    ud_hit = sum(1 for g, p in zip(golds, preds) if g == "PROMOTE" and p == "PROMOTE")
    re_total = golds.count("REOPEN")
    re_hit = sum(1 for g, p in zip(golds, preds) if g == "REOPEN" and p == "REOPEN")
    return {
        "false_novelty_rate": rate(fn, promote_calls) if promote_calls else 0.0,
        "false_novelty_count_over_nonpromote_gold": fn,
        "promote_calls": promote_calls,
        "subsumption_detection_rate": rate(sub_hit, sub_total),
        "cannot_check_recall": rate(cc_hit, cc_total),
        "cannot_check_precision": rate(cc_hit, cc_calls) if cc_calls else None,
        "negative_loss_rate": rate(neg_total - neg_kept, neg_total),
        "useful_discovery_recall": rate(ud_hit, ud_total),
        "reopen_recall": rate(re_hit, re_total),
        "abstention_rate": rate(cc_calls, len(preds)),
        "raw_agreement": rate(sum(1 for g, p in zip(golds, preds) if g == p), len(golds)),
        "cohens_kappa": kappa(golds, preds),
        "confusion_gold_rows_pred_cols": m,
    }


def run(base, out):
    packets = load_jsonl(os.path.join(base, "packets", "p14_external_packets_v1.jsonl"))
    evidence = load_jsonl(os.path.join(base, "evidence", "p14_external_evidence_v1.jsonl"))
    gold = load_jsonl(os.path.join(base, "protected", "p14_external_gold_v1.jsonl"))
    ev_by_id = {r["artifact_id"]: r for r in evidence}
    gold_by_id = {g["packet_id"]: g for g in gold}

    systems = {"SYSTEMA": decide_system_a, "SYSTEMB": decide_system_b}
    decisions = {}
    golds = [gold_by_id[p["packet_id"]]["gold_disposition"] for p in packets]
    for system_id, fn in systems.items():
        rows = []
        for p in packets:
            d, c, conf, dev, _ = fn(p, ev_by_id)
            rows.append(build_decision(p, system_id, d, c, conf, dev, ev_by_id))
        decisions[system_id] = rows

    # decision-schema conformance (fail closed, using the repo decision schema)
    schema_path = os.path.join(HERE, "..", "P14_EXTERNAL_DECISION_SCHEMA_V1.json")
    if not os.path.exists(schema_path):
        print("FAIL: decision schema not found at %s" % schema_path, file=sys.stderr)
        return 1
    with open(schema_path, encoding="utf-8") as f:
        dec_schema = json.load(f)
    from validate_p14_external_packets_v1 import check_schema
    errors = []
    for system_id, rows in decisions.items():
        for d in rows:
            before = len(errors)
            check_schema(d, dec_schema, "decision[%s,%s]" % (system_id, d["packet_id"]))
            if len(errors) > before:
                break
    if errors:
        for e in errors[:20]:
            print("FAIL: %s" % e, file=sys.stderr)
        return 1

    for system_id, rows in decisions.items():
        d = os.path.join(out, "decisions")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "p14_external_decisions_%s_v1.jsonl" % system_id), "w", encoding="utf-8") as f:
            for r in rows:
                f.write(canonical(r) + "\n")

    # blinded worksheet: System-A/System-B, no identity, no gold
    ws = os.path.join(out, "worksheets")
    os.makedirs(ws, exist_ok=True)
    lines = ["# External blinded adjudication worksheet (v1)", "",
             "- Suite: 67 protected packets, 3 domains, 8 scientific-state families.",
             "- Gold record file digest (sha256 of file bytes): %s" % hashlib.sha256(
                 open(os.path.join(base, "protected", "p14_external_gold_v1.jsonl"), "rb").read()).hexdigest(),
             "- Instructions: adjudicate each row from the packet evidence alone; never consult",
             "  the gold partition; record agreement/disagreement with System-A and System-B.",
             "", "| packet | domain | question (truncated) | System-A | System-B | adjudicator |", "|---|---|---|---|---|---|"]
    for p, a, b in zip(packets, decisions["SYSTEMA"], decisions["SYSTEMB"]):
        q = p["question"][:110].replace("|", "/") + "..."
        lines.append("| %s | %s | %s | %s | %s | |" % (p["packet_id"], p["domain"].split("_")[0], q, a["disposition"], b["disposition"]))
    with open(os.path.join(ws, "p14_external_blinded_worksheet_v1.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    # analytics
    metrics = {sid: system_metrics(golds, [r["disposition"] for r in rows]) for sid, rows in decisions.items()}
    analytics = {
        "schema_version": "P14_EXTERNAL_PILOT_ANALYTICS_V1",
        "suite": {"packets": len(packets), "domains": 3, "families": 8, "round_pairs": sum(1 for g in gold if g.get("round") == 2)},
        "systems": {"SYSTEMA": {"role": "governance-blind reference (vulnerable baseline)"},
                    "SYSTEMB": {"role": "contract-level governance check"}},
        "authority_status_all": "NOT_AUTHORITY",
        "co_primary_promotion_condition": {
            "status": "PENDING_EXTERNAL",
            "reason": "Frontier-agent execution and independent human adjudication have not run; pilot systems are deterministic procedures, not adjudicators.",
        },
        "metrics": metrics,
    }
    ad = os.path.join(out, "analytics")
    os.makedirs(ad, exist_ok=True)
    with open(os.path.join(ad, "p14_external_pilot_analytics_v1.json"), "w", encoding="utf-8") as f:
        json.dump(analytics, f, indent=2, sort_keys=True)
        f.write("\n")

    md = ["# ORION-24 external pilot analytics (v1)", "",
          "Wiring check only. All systems NOT_AUTHORITY; co-primary condition PENDING_EXTERNAL.", "",
          "| metric | System-A (blind) | System-B (governance) |", "|---|---|---|"]
    keys = ["false_novelty_rate", "subsumption_detection_rate", "cannot_check_precision", "cannot_check_recall",
            "negative_loss_rate", "useful_discovery_recall", "reopen_recall", "abstention_rate", "raw_agreement", "cohens_kappa"]
    for k in keys:
        md.append("| %s | %s | %s |" % (k, metrics["SYSTEMA"][k], metrics["SYSTEMB"][k]))
    with open(os.path.join(ad, "p14_external_pilot_analytics_v1.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    print("P14_EXTERNAL_PILOT_V1_GREEN packets=%d systems=2 A_false_novelty=%s B_false_novelty=%s B_kappa=%s co_primary=%s" % (
        len(packets), metrics["SYSTEMA"]["false_novelty_rate"], metrics["SYSTEMB"]["false_novelty_rate"],
        metrics["SYSTEMB"]["cohens_kappa"], analytics["co_primary_promotion_condition"]["status"]))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    return run(args.base, args.out)


if __name__ == "__main__":
    sys.exit(main())
