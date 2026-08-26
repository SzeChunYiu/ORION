#!/usr/bin/env python3
"""Campaign unit for the P7 substitute navigation campaign (V1).

Two phases over the corpus sealed by ``p7_substitute_custodian_v1.py``:

``--phase predict`` (blinded): reads ONLY the public corpus and the sealed
manifest.  Runs the atlas navigator and the three donor comparators, and writes
a signed predictions file binding the corpus digest and the sealed-manifest
digest.  This unit does NOT import the custodian in this phase and cannot see a
single label: the corpus file carries no family, no latent, and no terminal.

``--phase adjudicate`` (reveal + score): reconstructs the revealed labels with
the custodian's frozen law, requires the reconstructed payload to hash exactly
to the digest committed in the sealed manifest, writes the reveal file, scores
all four contenders against the revealed labels, evaluates the prespecified
gate table from the protocol, and writes the signed campaign receipt.

Run from the repository root:

    python papers/orion-17-epistemic-navigation-open-worlds/evidence/independent/p7_substitute_campaign_v1.py --phase predict
    python papers/orion-17-epistemic-navigation-open-worlds/evidence/independent/p7_substitute_campaign_v1.py --phase adjudicate
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "P7_SUBSTITUTE_CORPUS_V1.jsonl"
SEALED = HERE / "P7_SUBSTITUTE_SEALED_LABELS_V1.json"
PREDICTIONS = HERE / "P7_SUBSTITUTE_PREDICTIONS_V1.json"
REVEALED = HERE / "P7_SUBSTITUTE_LABELS_REVEALED_V1.json"
RECEIPT = HERE / "P7_SUBSTITUTE_CAMPAIGN_RECEIPT_V1.json"

EVALUATOR_DOMAIN_KEY = "P7-SUBSTITUTE-EVALUATOR-V1-KEY"

TERMINALS = ("TASK_STOP", "ROUTE_STOP", "REFRAME", "CANNOT_CHECK")


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(obj) -> str:
    return "sha256:" + hashlib.sha256(obj if isinstance(obj, bytes) else canon(obj)).hexdigest()


def evaluator_key() -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(hashlib.sha256(EVALUATOR_DOMAIN_KEY.encode()).digest())


def evaluator_pub_hex() -> str:
    return evaluator_key().public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()


def load_corpus() -> list[dict]:
    rows = [json.loads(line) for line in CORPUS.read_text(encoding="utf-8").splitlines() if line]
    if len(rows) != 432:
        raise SystemExit(f"campaign: corpus must hold 432 rows, found {len(rows)}")
    return rows


def load_sealed() -> dict:
    return json.loads(SEALED.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Contenders.  All four are pure functions of the PUBLIC observable row.
# ---------------------------------------------------------------------------


def atlas_navigator(row: dict) -> str:
    """P7 navigator (protocol section 5): fail-closed coverage first, then
    reframe authority, then structural route independence, then task stop."""
    if row["censoring_events"] > 0 or row["coverage_denominator"] == "UNKNOWN":
        return "CANNOT_CHECK"
    if row["prior_closure_support_mapping"] == "PARTIAL":
        return "CANNOT_CHECK"
    if row["solution_probe"] == "UNREACHABLE" and row["reframe_action_available"]:
        return "REFRAME"
    signatures = row["route_backend_signatures"]
    if len(signatures) > 1 and len(set(signatures)) == 1:
        return "ROUTE_STOP"
    return "TASK_STOP"


def b0_fixed_chart_exhaustive(row: dict) -> str:
    """No reframe authority, no coverage semantics, no independence test."""
    return "TASK_STOP"


def b1_fixed_chart_route_pruning(row: dict) -> str:
    signatures = row["route_backend_signatures"]
    if len(signatures) > 1 and len(set(signatures)) == 1:
        return "ROUTE_STOP"
    return "TASK_STOP"


def b3_representation_change_donor(row: dict) -> str:
    """Reframes when provably stuck or merely stalled; no fail-closed semantics."""
    stalled = (not row["unexpanded_frontier_nonempty"]) or bool(row["outstanding_obligations"])
    if row["solution_probe"] == "UNREACHABLE" or stalled:
        return "REFRAME"
    return "TASK_STOP"


CONTENDERS = {
    "P7_ATLAS_NAVIGATOR": atlas_navigator,
    "B0_FIXED_CHART_EXHAUSTIVE": b0_fixed_chart_exhaustive,
    "B1_FIXED_CHART_ROUTE_PRUNING": b1_fixed_chart_route_pruning,
    "B3_REPRESENTATION_CHANGE_DONOR": b3_representation_change_donor,
}


# ---------------------------------------------------------------------------
# Phase 1: blinded predictions.
# ---------------------------------------------------------------------------


def phase_predict() -> int:
    rows = load_corpus()
    sealed = load_sealed()
    corpus_digest = digest(CORPUS.read_bytes())
    if corpus_digest != sealed["facts"]["corpus_sha256"]:
        raise SystemExit("campaign: corpus bytes do not match the sealed manifest")

    per_contender: dict[str, list[dict]] = {}
    for name, policy in CONTENDERS.items():
        per_contender[name] = [
            {"id": row["id"], "domain": row["domain"], "prediction": policy(row)} for row in rows
        ]
    opportunities = {name: len(preds) for name, preds in per_contender.items()}
    if set(opportunities.values()) != {432}:
        raise SystemExit(f"campaign: every contender must judge 432 opportunities: {opportunities}")

    facts = {
        "schema_version": "orion.p7.substitute-predictions.v1",
        "phase": "PREDICT",
        "paper_id": "P7",
        "evaluator_unit": "p7_substitute_campaign_v1",
        "corpus_sha256": corpus_digest,
        "sealed_manifest_facts_digest": sealed["payload_digest"],
        "sealed_manifest_outcome": sealed["outcome"],
        "commit_phase_context": git_head(),
        "contenders": sorted(CONTENDERS),
        "opportunities_per_contender": opportunities,
        "predicted_terminal_counts": {
            name: {t: sum(1 for p in preds if p["prediction"] == t) for t in TERMINALS}
            for name, preds in per_contender.items()
        },
        "predictions": per_contender,
        "label_fields_present": [],
        "blindness_statement": (
            "predictions are a pure function of the public corpus file; this phase "
            "opens no other data file and imports no custodian code"
        ),
    }
    payload = {
        "facts": facts,
        "payload_digest": digest(facts),
        "signature_ed25519_hex": evaluator_key().sign(canon(facts)).hex(),
        "public_key_hex": evaluator_pub_hex(),
        "key_derivation": f"sha256('{EVALUATOR_DOMAIN_KEY}') as Ed25519 seed",
        "outcome": "P7_SUBSTITUTE_PREDICTIONS_COMMITTED",
    }
    PREDICTIONS.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"outcome": payload["outcome"], "opportunities": opportunities}, indent=2))
    return 0


def git_head() -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True, cwd=HERE
        )
        return out.stdout.strip()
    except Exception:  # noqa: BLE001 - informational field only
        return None


# ---------------------------------------------------------------------------
# Phase 2: reveal + adjudication.
# ---------------------------------------------------------------------------


def verify_predictions_signature() -> dict:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    payload = json.loads(PREDICTIONS.read_text(encoding="utf-8"))
    key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(payload["public_key_hex"]))
    try:
        key.verify(bytes.fromhex(payload["signature_ed25519_hex"]), canon(payload["facts"]))
        ok = True
    except InvalidSignature:
        ok = False
    if not ok:
        raise SystemExit("campaign: predictions signature does not verify")
    if digest(payload["facts"]) != payload["payload_digest"]:
        raise SystemExit("campaign: predictions payload digest mismatch")
    return payload


def reconstruct_reveal() -> dict:
    """Rebuild the labels with the custodian's frozen law; the rebuild must
    hash to the committed digest or the seal is broken."""
    import p7_substitute_custodian_v1 as custodian

    rows, labels = custodian.build_corpus()
    revealed = {
        "schema_version": "orion.p7.substitute-labels-revealed.v1",
        "labels": labels,
    }
    if digest(revealed) != load_sealed()["facts"]["labels_payload_digest"]:
        raise SystemExit("campaign: reconstructed labels do not match the sealed commitment")
    return revealed


def score(revealed: dict, predictions_payload: dict) -> dict:
    labels = {rec["id"]: rec for rec in revealed["labels"]}
    truth = {rid: rec["terminal"] for rid, rec in labels.items()}
    negative_controls = [rid for rid, rec in labels.items() if rec["negative_control"]]

    per_contender: dict[str, dict] = {}
    for name, preds in predictions_payload["facts"]["predictions"].items():
        by_domain: dict[str, dict] = {}
        wrong_classes: set[str] = set()
        for pred in preds:
            dom = by_domain.setdefault(pred["domain"], {"correct": 0, "total": 0})
            dom["total"] += 1
            if pred["prediction"] == truth[pred["id"]]:
                dom["correct"] += 1
            else:
                wrong_classes.add(truth[pred["id"]])
        for dom in by_domain.values():
            dom["accuracy"] = dom["correct"] / dom["total"]
            dom["wrong"] = dom["total"] - dom["correct"]
        total = sum(d["total"] for d in by_domain.values())
        correct = sum(d["correct"] for d in by_domain.values())
        premature_den = sum(1 for p in preds if truth[p["id"]] in ("CANNOT_CHECK", "REFRAME"))
        premature = sum(
            1 for p in preds if truth[p["id"]] in ("CANNOT_CHECK", "REFRAME") and p["prediction"] == "TASK_STOP"
        )
        nc_reframes = sum(
            1 for p in preds if labels[p["id"]]["negative_control"] and p["prediction"] == "REFRAME"
        )
        predicted_terminals_per_domain = {
            dom: sorted({p["prediction"] for p in preds if p["domain"] == dom})
            for dom in sorted(by_domain)
        }
        per_contender[name] = {
            "per_domain": by_domain,
            "overall_accuracy": correct / total,
            "correct": correct,
            "total": total,
            "worst_domain_accuracy": min(d["accuracy"] for d in by_domain.values()),
            "min_wrong_per_domain": min(d["wrong"] for d in by_domain.values()),
            "wrong_true_classes": sorted(wrong_classes),
            "premature_stop_rate": (premature / premature_den) if premature_den else None,
            "unnecessary_reframe_rate_on_negative_controls": (
                nc_reframes / len(negative_controls) if negative_controls else None
            ),
            "predicted_terminals_per_domain": predicted_terminals_per_domain,
            "predicts_all_terminals_every_domain": all(
                v == sorted(TERMINALS) for v in predicted_terminals_per_domain.values()
            ),
        }
    return {"contenders": per_contender, "negative_control_count": len(negative_controls)}


def evaluate_gates(sealed: dict, predictions_payload: dict, table: dict) -> dict:
    nav = table["contenders"]["P7_ATLAS_NAVIGATOR"]
    donors = {
        name: row
        for name, row in table["contenders"].items()
        if name != "P7_ATLAS_NAVIGATOR"
    }
    corpus_digest = digest(CORPUS.read_bytes())
    seal_ok = corpus_digest == sealed["facts"]["corpus_sha256"]
    protocol_ok = digest((HERE / "P7_SUBSTITUTE_CAMPAIGN_PROTOCOL_V1.md").read_bytes()) == sealed["facts"]["protocol_sha256"]
    bound_ok = (
        predictions_payload["facts"]["corpus_sha256"] == corpus_digest
        and predictions_payload["facts"]["sealed_manifest_facts_digest"] == sealed["payload_digest"]
    )
    return {
        "seal_chain_corpus_matches_sealed_manifest": seal_ok,
        "seal_chain_protocol_digest_matches_sealed_manifest": protocol_ok,
        "seal_chain_predictions_bound_corpus_and_manifest": bound_ok,
        "label_agreement_all_432": nav["overall_accuracy"] == 1.0,
        "worst_domain_accuracy_is_one": nav["worst_domain_accuracy"] == 1.0,
        "donor_discrimination": all(
            row["overall_accuracy"] < nav["overall_accuracy"]
            and len(row["wrong_true_classes"]) >= 2
            and row["min_wrong_per_domain"] >= 24
            for row in donors.values()
        ),
        "navigator_premature_stop_rate_zero": nav["premature_stop_rate"] == 0.0,
        "donor_premature_stop_present": all(
            donors[n]["premature_stop_rate"] is not None and donors[n]["premature_stop_rate"] > 0
            for n in ("B0_FIXED_CHART_EXHAUSTIVE", "B1_FIXED_CHART_ROUTE_PRUNING")
        ),
        "navigator_unnecessary_reframe_rate_zero": nav["unnecessary_reframe_rate_on_negative_controls"] == 0.0,
        "b3_unnecessary_reframe_present": (
            donors["B3_REPRESENTATION_CHANGE_DONOR"]["unnecessary_reframe_rate_on_negative_controls"] or 0
        ) > 0,
        "navigator_terminal_coverage_complete_every_domain": nav["predicts_all_terminals_every_domain"],
    }


def phase_adjudicate() -> int:
    sealed = load_sealed()
    predictions_payload = verify_predictions_signature()
    revealed = reconstruct_reveal()
    REVEALED.write_text(json.dumps(revealed, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    table = score(revealed, predictions_payload)
    gates = evaluate_gates(sealed, predictions_payload, table)
    nav = table["contenders"]["P7_ATLAS_NAVIGATOR"]

    facts = {
        "schema_version": "orion.p7.substitute-campaign-receipt.v1",
        "receipt_date": "2026-08-24",
        "paper_id": "P7",
        "claim_id": "P7.SUBSTITUTE_NAVIGATION_CAMPAIGN.MULTI_DOMAIN_V1",
        "execution_kind": "SUBSTITUTE_SEALED_LABEL_CAMPAIGN",
        "campaign_unit": "p7_substitute_campaign_v1",
        "commit_phase_commit": sealed.get("commit_phase_context") or predictions_payload["facts"].get("commit_phase_context"),
        "sealed_manifest": {
            "outcome": sealed["outcome"],
            "payload_digest": sealed["payload_digest"],
            "public_key_hex": sealed["public_key_hex"],
            "power_counts": sealed["facts"]["power_counts"],
        },
        "predictions": {
            "payload_digest": predictions_payload["payload_digest"],
            "public_key_hex": predictions_payload["public_key_hex"],
            "commit_phase_context": predictions_payload["facts"].get("commit_phase_context"),
        },
        "reveal": {
            "labels_payload_digest": sealed["facts"]["labels_payload_digest"],
            "revealed_rows": len(revealed["labels"]),
        },
        "results": table,
        "gates": gates,
        "headline": {
            "navigator_overall_accuracy": nav["overall_accuracy"],
            "navigator_worst_domain_accuracy": nav["worst_domain_accuracy"],
            "donor_overall_accuracy": {
                name: row["overall_accuracy"] for name, row in table["contenders"].items()
                if name != "P7_ATLAS_NAVIGATOR"
            },
            "domains": sorted({rec["domain"] for rec in revealed["labels"]}),
            "instances": nav["total"],
        },
        "disjoint_code_path": {
            "predict_phase_imports": ["stdlib", "cryptography", "corpus file only"],
            "notes": [
                "predict phase imports no custodian code and opens no label-bearing file",
                "adjudicate phase reconstructs the reveal through the frozen custodian law, verified against the committed digest",
            ],
        },
        "authority_boundary": (
            "Converts P7.OPEN_WORLD.NAVIGATION.EMPIRICAL.V1 from EXTERNAL_EVIDENCE_BLOCKER "
            "to SUBSTITUTE_SEALED_LABEL_CAMPAIGN_GREEN under the operator-approved substitute "
            "protocol: synthetic-grounded six-domain corpus, donor-complete comparison, sealed "
            "hidden labels, independently implemented custodian/evaluator/checker. Grants no "
            "naturalistic-corpus, live-agent, or deployed-system authority; the original "
            "external requirement remains separately tracked."
        ),
    }
    receipt = {
        "facts": facts,
        "payload_digest": digest(facts),
        "signature_ed25519_hex": evaluator_key().sign(canon(facts)).hex(),
        "public_key_hex": evaluator_pub_hex(),
        "key_derivation": f"sha256('{EVALUATOR_DOMAIN_KEY}') as Ed25519 seed",
        "outcome": "P7_SUBSTITUTE_CAMPAIGN_GREEN" if all(gates.values()) else "P7_SUBSTITUTE_CAMPAIGN_GATE_FAILED",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "outcome": receipt["outcome"],
                "gates": gates,
                "headline": facts["headline"],
            },
            indent=2,
        )
    )
    return 0 if all(gates.values()) else 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("predict", "adjudicate"), required=True)
    args = parser.parse_args(argv)
    return phase_predict() if args.phase == "predict" else phase_adjudicate()


if __name__ == "__main__":
    raise SystemExit(main())
