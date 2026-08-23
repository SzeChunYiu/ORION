#!/usr/bin/env python3
"""Validate the generated P14 external packet suite (v1). Fail-closed.

Layers:
  1. Schema layer  - every packet validates against P14_EXTERNAL_PACKET_SCHEMA_V1.json
                     (minimal validator: type/const/enum/pattern/required/properties/
                     additionalProperties/items/minItems/minLength).
  2. Suite layer   - >=60 packets, >=3 domains, every required family >=2,
                     >=3 longitudinal round-pairs, evidence digest match,
                     gold digest match, evidence referenced <===> evidence present.
  3. Leakage layer - no adjudication token, programme name, or terminal label in any
                     agent-visible byte (packets + evidence records).

Exit codes: 0 green, 1 any failure. Absence of output is failure downstream.
"""

import argparse
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

REQUIRED_FAMILIES = [
    "STRONG_PROMOTABLE", "APPARENT_POSITIVE_SUBSUMED", "INTERACTION_ONLY",
    "NULL_LIVE_PARENT", "NEGATIVE_RETAINED", "LEAKY_OR_CORRUPT_BENCHMARK",
    "NON_IDENTIFIABLE", "REGIME_CHANGE_REOPEN",
]
MIN_PER_FAMILY = 2
MIN_PACKETS = 60
MIN_DOMAINS = 3
MIN_ROUND_PAIRS = 3

ENUM_TOKENS = [
    "PROMOTE", "SUBSUMED", "INTERACTION_ONLY", "NULL_LIVE", "NON_IDENTIFIABLE",
    "CANNOT_CHECK", "REOPEN", "STOP", "NOT_AUTHORITY", "EXTERNALLY_AUTHORIZED",
]
FORBIDDEN_VISIBLE_STRINGS = ["orion", "Orion", "ORION", "top_tier", "top-tier", "Top-Tier"]
GOLD_ONLY_KEYS = ["gold_disposition", "gold_claim", "gold_novelty", "rationale", "key_discriminator"]

_errors = []


def err(msg):
    _errors.append(msg)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def check_schema(obj, schema, path):
    if "const" in schema and obj != schema["const"]:
        err("%s: expected const %r, got %r" % (path, schema["const"], obj))
        return
    if "enum" in schema and obj not in schema["enum"]:
        err("%s: %r not in enum %r" % (path, obj, schema["enum"]))
        return
    t = schema.get("type")
    if t:
        types = t if isinstance(t, list) else [t]
        ok = False
        for ty in types:
            if ty == "object":
                ok = ok or isinstance(obj, dict)
            elif ty == "array":
                ok = ok or isinstance(obj, list)
            elif ty == "string":
                ok = ok or isinstance(obj, str)
            elif ty == "integer":
                ok = ok or (isinstance(obj, int) and not isinstance(obj, bool))
            elif ty == "number":
                ok = ok or (isinstance(obj, (int, float)) and not isinstance(obj, bool))
            elif ty == "boolean":
                ok = ok or isinstance(obj, bool)
        if not ok:
            err("%s: type %r not in %r" % (path, type(obj).__name__, types))
            return
    if isinstance(obj, str):
        if "minLength" in schema and len(obj) < schema["minLength"]:
            err("%s: shorter than minLength %d" % (path, schema["minLength"]))
        if "pattern" in schema and not re.search(schema["pattern"], obj):
            err("%s: %r fails pattern %r" % (path, obj, schema["pattern"]))
    if isinstance(obj, list) and "minItems" in schema and len(obj) < schema["minItems"]:
        err("%s: fewer than minItems %d" % (path, schema["minItems"]))
    if isinstance(obj, dict):
        for key in schema.get("required", []):
            if key not in obj:
                err("%s: missing required %r" % (path, key))
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in obj:
                if key not in props:
                    err("%s: additional property %r (schema is closed)" % (path, key))
        for key, sub in props.items():
            if key in obj:
                check_schema(obj[key], sub, "%s.%s" % (path, key))
    if isinstance(obj, list) and "items" in schema:
        for i, item in enumerate(obj):
            check_schema(item, schema["items"], "%s[%d]" % (path, i))


def load_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def validate(base):
    packet_path = os.path.join(base, "packets", "p14_external_packets_v1.jsonl")
    evidence_path = os.path.join(base, "evidence", "p14_external_evidence_v1.jsonl")
    gold_path = os.path.join(base, "protected", "p14_external_gold_v1.jsonl")
    schema_path = os.path.join(HERE, "..", "P14_EXTERNAL_PACKET_SCHEMA_V1.json")
    for p in (packet_path, evidence_path, gold_path, schema_path):
        if not os.path.exists(p):
            err("missing file: %s" % p)
            return
    packets = load_jsonl(packet_path)
    evidence = load_jsonl(evidence_path)
    gold = load_jsonl(gold_path)
    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)

    # Layer 1: schema
    for p in packets:
        check_schema(p, schema, "packet[%s]" % p.get("packet_id", "?"))

    # Layer 2: suite
    if len(packets) < MIN_PACKETS:
        err("packet count %d < %d" % (len(packets), MIN_PACKETS))
    domains = {p["domain"] for p in packets}
    if len(domains) < MIN_DOMAINS:
        err("domain count %d < %d" % (len(domains), MIN_DOMAINS))
    gold_by_id = {g["packet_id"]: g for g in gold}
    fam_counts = {}
    for p in packets:
        g = gold_by_id.get(p["packet_id"])
        if g is None:
            err("no gold record for %s" % p["packet_id"])
            continue
        fam_counts[g["family"]] = fam_counts.get(g["family"], 0) + 1
        if p["gold_record_digest"] != sha256_hex(canonical(g)):
            err("gold digest mismatch for %s" % p["packet_id"])
    for fam in REQUIRED_FAMILIES:
        if fam_counts.get(fam, 0) < MIN_PER_FAMILY:
            err("family %s has %d packets < %d" % (fam, fam_counts.get(fam, 0), MIN_PER_FAMILY))
    round_pairs = sum(1 for g in gold if g.get("round") == 2)
    if round_pairs < MIN_ROUND_PAIRS:
        err("longitudinal round-2 count %d < %d" % (round_pairs, MIN_ROUND_PAIRS))
    ev_by_id = {r["artifact_id"]: r for r in evidence}
    for p in packets:
        for item in p["visible_evidence"]:
            r = ev_by_id.get(item["artifact_id"])
            if r is None:
                err("%s references absent evidence %s" % (p["packet_id"], item["artifact_id"]))
                continue
            if r["sha256"] != item["sha256"]:
                err("%s: digest mismatch on %s" % (p["packet_id"], item["artifact_id"]))
            if r["role"] != item["role"]:
                err("%s: role mismatch on %s" % (p["packet_id"], item["artifact_id"]))
            expect_loc = "evidence/p14_external_evidence_v1.jsonl#%s" % item["artifact_id"]
            if item["content_location"] != expect_loc:
                err("%s: content_location mismatch on %s" % (p["packet_id"], item["artifact_id"]))
    referenced = {i["artifact_id"] for p in packets for i in p["visible_evidence"]}
    orphans = sorted(set(ev_by_id) - referenced)
    if orphans:
        err("orphan evidence records: %s" % ", ".join(orphans[:5]))

    # Layer 3: leakage (agent-visible bytes only: packets + evidence records)
    visible_texts = [canonical(p) for p in packets] + [canonical(r) for r in evidence]
    for tok in ENUM_TOKENS + FORBIDDEN_VISIBLE_STRINGS + GOLD_ONLY_KEYS:
        for text in visible_texts:
            if tok in text:
                i = text.index(tok)
                err("leakage: token %r at byte %d near ...%s..." % (tok, i, text[max(0, i - 40):i + 40]))
                break

    if _errors:
        for e in _errors[:40]:
            print("FAIL: %s" % e, file=sys.stderr)
        print("P14_EXTERNAL_PACKETS_V1_RED errors=%d" % len(_errors), file=sys.stderr)
        return 1
    print("P14_EXTERNAL_PACKETS_V1_GREEN packets=%d evidence=%d domains=%d families=%d round_pairs=%d" % (
        len(packets), len(evidence), len(domains), len(fam_counts), round_pairs))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", required=True, help="external_v1 directory containing packets/ evidence/ protected/")
    args = ap.parse_args()
    return validate(args.base)


if __name__ == "__main__":
    sys.exit(main())
