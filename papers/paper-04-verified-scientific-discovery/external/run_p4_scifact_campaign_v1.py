#!/usr/bin/env python3
"""P4: full policy, strongest runnable baseline and component ablations on SciFact.

The policy under test is a governance layer, not a claim classifier. A gold
SciFact label clears the semantic-support coordinate only; PROMOTE additionally
requires every promotion obligation discharged, and any undischarged obligation
yields CANNOT_CHECK. That is the frozen rule from
SCIFACT_LABEL_STATE_MAP_V2.json, and this executes it rather than restating it.

The semantic coordinate is supplied from gold, declared and not hidden. This
study measures whether the governance layer withholds promotion when it should,
not whether a model can read a paper. Every arm receives the identical semantic
coordinate, so no arm gains from it and the arms differ only in governance.

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
MAP = REPO / "papers/paper-04-verified-scientific-discovery/protocol/SCIFACT_LABEL_STATE_MAP_V2.json"

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


def macro_f1(gold: list[str], pred: list[str]) -> float:
    labels = sorted(set(gold) | set(pred))
    scores = []
    for lab in labels:
        tp = sum(1 for g, p in zip(gold, pred) if g == lab and p == lab)
        fp = sum(1 for g, p in zip(gold, pred) if g != lab and p == lab)
        fn = sum(1 for g, p in zip(gold, pred) if g == lab and p != lab)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        scores.append(2 * prec * rec / (prec + rec) if prec + rec else 0.0)
    return sum(scores) / len(scores) if scores else 0.0


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

    gold = [terminal(r["verdict"], r["discharged"], OBLIGATIONS) for r in rows]

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
        "gold_terminal_support": dict(Counter(gold)),
        "arms": {},
    }
    for name, arm in arms.items():
        pred = arm["pred"]
        result["arms"][name] = {
            "status": arm["status"],
            "enforced_obligations": arm["enforced"],
            "macro_f1": round(macro_f1(gold, pred), 6),
            "accuracy": round(sum(int(a == b) for a, b in zip(gold, pred)) / len(gold), 6),
            "terminal_support": dict(Counter(pred)),
            "false_promotions": sum(
                1 for g, p in zip(gold, pred) if p == "PROMOTE" and g != "PROMOTE"
            ),
            "differs_from_full_policy_on": sum(1 for a, b in zip(pred, full) if a != b),
        }
        if arm.get("note"):
            result["arms"][name]["note"] = arm["note"]
    out = HERE / "P4_SCIFACT_CAMPAIGN_V1.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    print(f"held-out claims: {len(dev)}   gold terminals: {result['gold_terminal_support']}")
    print("\nobligation identifiability:")
    for o in OBLIGATIONS:
        i = result["obligation_identifiability"][o]
        print(f"  {o:44s} {i['discharged_on']:3d}/{i['of']}  {i['ablation']}")
    print(f"\n{'arm':46s}{'status':17s}{'macroF1':>9}{'acc':>8}{'falsePromo':>12}{'diff':>6}")
    for name, a in result["arms"].items():
        print(f"{name:46s}{a['status']:17s}{a['macro_f1']:9.4f}{a['accuracy']:8.4f}"
              f"{a['false_promotions']:12d}{a['differs_from_full_policy_on']:6d}")
    print(f"\nwrote {out} ({out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
