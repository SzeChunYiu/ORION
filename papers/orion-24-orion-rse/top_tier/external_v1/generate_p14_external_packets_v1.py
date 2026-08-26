#!/usr/bin/env python3
"""Generate the P14 external evaluation packet suite (v1).

Deterministic: no clock, no network, no randomness. Same tree in, same bytes
out (verified byte-for-byte by the CI determinism gate).

Outputs (relative to --out):
  packets/p14_external_packets_v1.jsonl     agent-visible packets (schema P14_EXTERNAL_PACKET_V1)
  evidence/p14_external_evidence_v1.jsonl   consolidated, content-addressed evidence records
  protected/p14_external_gold_v1.jsonl      PROTECTED - adjudication gold, never agent-visible

Gold identity enters packets ONLY as gold_record_digest (sha256 of the
canonical gold record). The leakage guard at the end asserts no adjudication
token, programme name, or terminal label appears in any agent-visible byte.
"""

import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import p14_packet_specs_formal_v1 as S_FORMAL
import p14_packet_specs_empirical_v1 as S_EMPIRICAL
import p14_packet_specs_infra_v1 as S_INFRA

DOMAIN_CODE = {
    "FORMAL_COMBINATORICS_AND_ALGEBRA": "FC",
    "EMPIRICAL_ML_METHODOLOGY": "EM",
    "RESEARCH_SYSTEMS_INFRASTRUCTURE": "RI",
}

ALLOWED_TOOLS = [
    "read_only_evidence_access",
    "deterministic_calculator",
    "text_generation",
    "artifact_hash_verifier",
]

FAMILY_BUDGET_MINUTES = {
    "STRONG_PROMOTABLE": 60,
    "APPARENT_POSITIVE_SUBSUMED": 45,
    "INTERACTION_ONLY": 45,
    "NULL_LIVE_PARENT": 45,
    "NEGATIVE_RETAINED": 60,
    "LEAKY_OR_CORRUPT_BENCHMARK": 60,
    "NON_IDENTIFIABLE": 45,
    "REGIME_CHANGE_REOPEN": 45,
}

GOLD_RATIONALE = {
    "PROMOTE": "All preregistered decision points are discharged by visible evidence; donor delta is "
               "material and stated; controls and certificates are independent. The bounded claim advances.",
    "SUBSUMED": "The visible positive is real but its mechanism is owned by the cited donor; the identity "
                "check against the donor is discharged. The contribution is absorbed, not novel.",
    "INTERACTION_ONLY": "Both marginals are null (CIs include 0) and the combined arm is separated; the "
                        "effect belongs to the interaction, not to either component.",
    "NULL_LIVE": "The parent result is separately reproduced and intact; the declared extension/refinement "
                 "is null with adequate power and a mechanism-level explanation. Only the extension is null.",
    "NEGATIVE": "The claim is refuted by certified evidence (counterexample, forensic, or gate exclusion) "
                "with the failure attributed to a mechanism; the negative is retained as evidence.",
    "NON_IDENTIFIABLE": "Both-directions constructions show the visible evidence cannot discriminate the "
                        "claim's truth; the boundary of identifiability is itself the finding.",
    "CANNOT_CHECK": "A required discriminating artifact is absent from the visible evidence and cannot be "
                    "reconstructed; candidate reconstructions disagree on the claim's sign.",
    "REOPEN": "A preregistered regime change materially alters the evidence base; the prior round's record "
              "is amended (never deleted) and the claim is re-evaluated under the new protocol.",
}

KEY_DISCRIMINATOR = {
    "STRONG_PROMOTABLE": "independent certificate/checker output + donor delta + control",
    "APPARENT_POSITIVE_SUBSUMED": "donor mechanism-identity check discharged (symbolic or item-for-item)",
    "INTERACTION_ONLY": "null marginals + separated combined arm + shuffle/locating control",
    "NULL_LIVE_PARENT": "parent reproduced separately; extension CI includes 0 with stated power",
    "NEGATIVE_RETAINED": "certified refutation with mechanism attribution and parent separation",
    "LEAKY_OR_CORRUPT_BENCHMARK": "degeneracy/vacuity/definitional audit with isolation or 2x2 control",
    "NON_IDENTIFIABLE": "both-directions construction (or missing-artifact reconstruction instability)",
    "REGIME_CHANGE_REOPEN": "round-2 evidence under the pre-frozen escalated protocol",
}

REQUIRED_FAMILIES = sorted(FAMILY_BUDGET_MINUTES)
MIN_PER_FAMILY = 2
MIN_PACKETS = 60
REQUIRED_ROUND_PAIRS = 3

# Adjudication tokens that must NEVER appear in agent-visible bytes.
ENUM_TOKENS = [
    "PROMOTE", "SUBSUMED", "INTERACTION_ONLY", "NULL_LIVE", "NON_IDENTIFIABLE",
    "CANNOT_CHECK", "REOPEN", "STOP", "NOT_AUTHORITY", "EXTERNALLY_AUTHORIZED",
]
FORBIDDEN_VISIBLE_STRINGS = ["orion", "Orion", "ORION", "top_tier", "top-tier", "Top-Tier"]


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build(out_dir):
    modules = [S_FORMAL, S_EMPIRICAL, S_INFRA]
    packets, evidence_records, gold_records = [], [], []
    ev_counter = 0

    for mod in modules:
        domain = mod.DOMAIN
        code = DOMAIN_CODE[domain]
        pk_counter = 0
        for spec in mod.SPECS:
            pk_counter += 1
            packet_id = "PKT-%s-%04d" % (code, pk_counter)
            visible_evidence = []
            for role, content in spec["ev"]:
                ev_counter += 1
                artifact_id = "EV-%s-%05d" % (code, ev_counter)
                ev_record = {
                    "artifact_id": artifact_id,
                    "role": role,
                    "content": content,
                    "sha256": sha256_hex(canonical({"artifact_id": artifact_id, "role": role, "content": content})),
                }
                evidence_records.append(ev_record)
                visible_evidence.append({
                    "artifact_id": artifact_id,
                    "sha256": ev_record["sha256"],
                    "role": role,
                    "content_location": "evidence/p14_external_evidence_v1.jsonl#%s" % artifact_id,
                })
            evidence_bytes = sum(len(r["content"].encode("utf-8")) for r in evidence_records[-len(spec["ev"]):])

            gold = {
                "packet_id": packet_id,
                "domain": domain,
                "family": spec["family"],
                "round": spec.get("round_no", 1),
                "gold_disposition": spec["gold"],
                "rationale": GOLD_RATIONALE[spec["gold"]],
                "key_discriminator": KEY_DISCRIMINATOR[spec["family"]],
            }
            gold_records.append(gold)

            packet = {
                "schema_version": "P14_EXTERNAL_PACKET_V1",
                "packet_id": packet_id,
                "domain": domain,
                "question": spec["q"],
                "visible_evidence": visible_evidence,
                "allowed_tools": list(ALLOWED_TOOLS),
                "resource_budget": {
                    "max_wallclock_minutes": FAMILY_BUDGET_MINUTES[spec["family"]],
                    "max_output_tokens": 4000,
                    "max_evidence_bytes": evidence_bytes,
                },
                "claim_language": {
                    "max_scope": spec["scope"],
                    "forbidden_promotions": list(spec["forbid"]),
                },
                "preregistered_decision_points": list(spec["dp"]),
                "gold_record_digest": sha256_hex(canonical(gold)),
            }
            packets.append(packet)

    # ---- suite-level invariants (fail closed) ----
    assert len(packets) >= MIN_PACKETS, len(packets)
    domains = sorted({p["domain"] for p in packets})
    assert len(domains) >= 3, domains
    fam_counts = {}
    for p, g in zip(packets, gold_records):
        fam_counts[g["family"]] = fam_counts.get(g["family"], 0) + 1
    for fam in REQUIRED_FAMILIES:
        assert fam in fam_counts and fam_counts[fam] >= MIN_PER_FAMILY, (fam, fam_counts.get(fam))
    rounds = [g for g in gold_records if g["round"] == 2]
    assert len(rounds) >= REQUIRED_ROUND_PAIRS, len(rounds)
    # digest integrity
    for p, g in zip(packets, gold_records):
        assert p["gold_record_digest"] == sha256_hex(canonical(g)), p["packet_id"]
        assert p["packet_id"] == g["packet_id"]

    # ---- leakage guard: agent-visible bytes carry no adjudication signal ----
    for p in packets:
        visible = canonical(p)
        for tok in ENUM_TOKENS + FORBIDDEN_VISIBLE_STRINGS:
            assert tok not in visible, (p["packet_id"], tok)
    for r in evidence_records:
        visible = canonical(r)
        for tok in ENUM_TOKENS + FORBIDDEN_VISIBLE_STRINGS:
            assert tok not in visible, (r["artifact_id"], tok)

    # ---- write ----
    paths = {
        "packets": os.path.join(out_dir, "packets", "p14_external_packets_v1.jsonl"),
        "evidence": os.path.join(out_dir, "evidence", "p14_external_evidence_v1.jsonl"),
        "gold": os.path.join(out_dir, "protected", "p14_external_gold_v1.jsonl"),
    }
    for rel in paths.values():
        os.makedirs(os.path.dirname(rel), exist_ok=True)
    with open(paths["packets"], "w", encoding="utf-8") as f:
        for p in packets:
            f.write(canonical(p) + "\n")
    with open(paths["evidence"], "w", encoding="utf-8") as f:
        for r in evidence_records:
            f.write(canonical(r) + "\n")
    with open(paths["gold"], "w", encoding="utf-8") as f:
        for g in gold_records:
            f.write(canonical(g) + "\n")

    print("P14_EXTERNAL_PACKETS_V1_GENERATED packets=%d evidence=%d gold=%d domains=%d families=%s" % (
        len(packets), len(evidence_records), len(gold_records), len(domains),
        ",".join("%s=%d" % kv for kv in sorted(fam_counts.items()))))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True, help="output directory (e.g. papers/paper-14-orion-rse/top_tier/external_v1)")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    return build(args.out)


if __name__ == "__main__":
    sys.exit(main())
