#!/usr/bin/env python3
"""P4: full policy, strongest runnable baseline and component ablations on SciFact.

The policy under test is a governance layer, not a claim classifier. A gold
SciFact label clears the semantic-support coordinate only; PROMOTE additionally
requires every promotion obligation discharged, and any undischarged obligation
yields CANNOT_CHECK. That is the frozen rule from
SCIFACT_LABEL_STATE_MAP_V2.json, and this executes it rather than restating it.

What can and cannot be scored here
----------------------------------
SciFact supplies external gold for the SEMANTIC coordinate: whether the cited
evidence supports, contradicts, or fails to settle the claim. That is scored.

It supplies no gold for the promotion TERMINAL. "Should this be promoted" is
ORION's own construct, so any gold terminal must be computed by the same rule
the policy applies -- and a policy scored against its own definition returns
1.000 by identity, not by performance. An earlier draft of this file did
exactly that and reported a perfect full_policy. It is the defect P14 was
criticised for, one file over, and the number is deleted rather than explained.

The terminal is therefore CANNOT_CHECK against this corpus, which is what P4's
own boundary already says: the external labels validate claim/evidence status,
and ORION's governance action is an operationalization, not independent policy
truth. What remains measurable, and is measured, is how far each arm's terminal
DIVERGES from the full policy, and whether an obligation is identifiable at
all.

Identifiability is reported per ablation rather than assumed. Three of the five
obligations are constant-true across the held-out split, so dropping them
cannot change a single verdict: those ablations are NOT_IDENTIFIABLE on this
data, and reporting a 0.000 difference for them as though it were a measured
null would be dressing an arithmetic identity as a finding.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

DATA = Path.home() / "orion-work/scifact/data"
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
MAP = REPO / "papers/orion-14-verified-scientific-discovery/protocol/SCIFACT_LABEL_STATE_MAP_V2.json"

OBLIGATIONS = (
    "claim_scope_conformance",
    "evidence_independence",
    "provenance_and_artifact_version_binding",
    "contamination_defense",
    "scientific_authority_resolution",
)


def compose_verdict(evidence: dict) -> str:
    """The frozen composition rule: contradiction dominates, then support."""
    labels = {r.get("label") for rows in evidence.values() for r in rows}
    if not evidence:
        return "NOT_ENOUGH_INFO"
    if "CONTRADICT" in labels:
        return "CONTRADICT"
    if "SUPPORT" in labels:
        return "SUPPORT"
    return "NOT_ENOUGH_INFO"


def obligations_for(claim: dict, corpus: set[int], train_text: set[str]) -> dict[str, bool]:
    evidence = claim.get("evidence") or {}
    cited = {str(x) for x in claim.get("cited_doc_ids", [])}
    labels = {r.get("label") for rows in evidence.values() for r in rows}
    return {
        "claim_scope_conformance": set(evidence) <= cited,
        # corroboration by more than one document; a single document supports
        # itself and cannot evidence independence
        "evidence_independence": len(evidence) >= 2,
        "provenance_and_artifact_version_binding": all(int(d) in corpus for d in cited)
        if cited
        else False,
        "contamination_defense": claim["claim"].strip().lower() not in train_text,
        "scientific_authority_resolution": len(labels) <= 1,
    }


def terminal(verdict: str, discharged: dict[str, bool], enforced: tuple[str, ...]) -> str:
    """The frozen mapping, applied under a given set of enforced obligations."""
    if verdict == "CONTRADICT":
        return "BLOCK"  # decisive for the semantic coordinate; never promotable
    if verdict == "NOT_ENOUGH_INFO":
        return "CANNOT_CHECK"
    if all(discharged[o] for o in enforced):
        return "PROMOTE"
    return "CANNOT_CHECK"


def main() -> int:
    if not MAP.is_file():
        print(f"P4_CAMPAIGN_CANNOT_CHECK: frozen map missing at {MAP}")
        return 3
    frozen = json.loads(MAP.read_text())
    if frozen["scifact_label_vocabulary"]["evidence_document_labels"] != ["SUPPORT", "CONTRADICT"]:
        print("ABORT: frozen map does not carry the corrected label vocabulary")
        return 4
    dev_path = DATA / "claims_dev.jsonl"
    if not dev_path.is_file():
        print(f"P4_CAMPAIGN_CANNOT_CHECK: held-out split missing at {dev_path}")
        return 3

    dev = [json.loads(l) for l in dev_path.open()]
    train = [json.loads(l) for l in (DATA / "claims_train.jsonl").open()]
    train_text = {c["claim"].strip().lower() for c in train}
    corpus = {json.loads(l)["doc_id"] for l in (DATA / "corpus.jsonl").open()}

    rows = []
    for claim in dev:
        verdict = compose_verdict(claim.get("evidence") or {})
        discharged = obligations_for(claim, corpus, train_text)
        rows.append({"id": claim["id"], "verdict": verdict, "discharged": discharged})

    # identifiability: an obligation constant across the split cannot change any
    # verdict when dropped, so its ablation measures nothing
    variation = {
        o: len({r["discharged"][o] for r in rows}) > 1 for o in OBLIGATIONS
    }
    counts = {o: sum(r["discharged"][o] for r in rows) for o in OBLIGATIONS}

    # The only externally gold-backed coordinate.
    semantic_gold = [r["verdict"] for r in rows]

    arms: dict[str, dict] = {}
    full = [terminal(r["verdict"], r["discharged"], OBLIGATIONS) for r in rows]
    arms["full_policy"] = {"status": "SCORED", "enforced": list(OBLIGATIONS), "pred": full}
    # strongest runnable baseline: semantic support alone licenses promotion
    base = [terminal(r["verdict"], r["discharged"], ()) for r in rows]
    arms["semantic_support_only_baseline"] = {
        "status": "SCORED",
        "enforced": [],
        "pred": base,
        "note": "promotes on semantic support alone; enforces no obligation",
    }
    for dropped in OBLIGATIONS:
        enforced = tuple(o for o in OBLIGATIONS if o != dropped)
        pred = [terminal(r["verdict"], r["discharged"], enforced) for r in rows]
        arms[f"ablate__{dropped}"] = {
            "status": "SCORED" if variation[dropped] else "NOT_IDENTIFIABLE",
            "enforced": list(enforced),
            "pred": pred,
            "note": (
                f"{dropped} is discharged on {counts[dropped]}/{len(rows)} held-out "
                "claims and never varies, so dropping it cannot change any verdict; "
                "a 0.000 difference here is an arithmetic identity, not a measured null"
            )
            if not variation[dropped]
            else f"{dropped} varies: discharged on {counts[dropped]}/{len(rows)}",
        }

    result = {
        "schema": "P4.SciFactGovernanceCampaign.v1",
        "frozen_map": {"artifact": MAP.name, "sha256": hashlib.sha256(MAP.read_bytes()).hexdigest()},
        "held_out_split": {
            "file": "claims_dev.jsonl",
            "claims": len(dev),
            "note": "claims_test.jsonl carries no labels; dev is the labelled held-out split",
        },
        "semantic_coordinate_source": {
            "value": "GOLD_ORACLE_SUPPLIED_IDENTICALLY_TO_EVERY_ARM",
            "why": (
                "P4's boundary states the external labels validate claim/evidence status "
                "and ORION's governance action is an operationalization. Supplying the "
                "coordinate identically to every arm isolates the governance layer; no "
                "arm gains from it and the arms differ only in obligation enforcement"
            ),
        },
        "obligation_identifiability": {
            o: {
                "discharged_on": counts[o],
                "of": len(rows),
                "varies": variation[o],
                "ablation": "SCORED" if variation[o] else "NOT_IDENTIFIABLE",
            }
            for o in OBLIGATIONS
        },
        "semantic_coordinate_gold_support": dict(Counter(semantic_gold)),
        "terminal_scoring": {
            "status": "CANNOT_CHECK",
            "reason": (
                "SciFact provides no external gold for the promotion terminal. Any gold "
                "terminal would be computed by the same frozen rule the policy applies, "
                "so the full policy would score 1.000 by identity. An earlier draft did "
                "this and is corrected here rather than reported."
            ),
        },
        "arms": {},
    }
    for name, arm in arms.items():
        pred = arm["pred"]
        result["arms"][name] = {
            "status": arm["status"],
            "enforced_obligations": arm["enforced"],
            "terminal_scored_against_gold": "CANNOT_CHECK__NO_EXTERNAL_TERMINAL_GOLD",
            "terminal_support": dict(Counter(pred)),
            # measurable without circularity: divergence from the full policy,
            # and promotions issued where an obligation was undischarged
            "differs_from_full_policy_on": sum(1 for a, b in zip(pred, full) if a != b),
            "promotes_with_an_undischarged_obligation": sum(
                1
                for r, p in zip(rows, pred)
                if p == "PROMOTE" and not all(r["discharged"][o] for o in OBLIGATIONS)
            ),
        }
        if arm.get("note"):
            result["arms"][name]["note"] = arm["note"]
    out = HERE / "P4_SCIFACT_CAMPAIGN_V1.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    print(f"held-out claims: {len(dev)}")
    print(f"semantic gold (externally backed): {result['semantic_coordinate_gold_support']}")
    print(f"terminal scoring: {result['terminal_scoring']['status']} -- no external gold exists")
    print("\nobligation identifiability:")
    for o in OBLIGATIONS:
        i = result["obligation_identifiability"][o]
        print(f"  {o:44s} {i['discharged_on']:3d}/{i['of']}  {i['ablation']}")
    print(f"\n{'arm':46s}{'status':17s}{'diverges':>10}{'unsafe_promotions':>19}")
    for name, a in result["arms"].items():
        print(f"{name:46s}{a['status']:17s}{a['differs_from_full_policy_on']:10d}"
              f"{a['promotes_with_an_undischarged_obligation']:19d}")
    print(f"\nwrote {out} ({out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
