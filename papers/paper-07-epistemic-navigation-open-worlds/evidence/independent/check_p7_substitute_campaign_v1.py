#!/usr/bin/env python3
"""Independent verifier for the P7 substitute campaign (V1).

Second reviewer under the substitute protocol's dual-independent-review gate.
This checker imports NOTHING from the custodian or the campaign unit and shares
no helper with either; every assertion in the receipt chain is re-derived here
with independently chosen algorithms:

  * signatures: its own Ed25519 verification of both keys and its own
    deterministic-key re-derivation;
  * seals: its own hashing loop for corpus/protocol/labels digests;
  * label law: re-encoded as an explicit priority rule table over latents
    (the custodian uses a nested if-chain);
  * observable faithfulness: its own latent<->observable consistency map;
  * contenders: re-implemented as data-driven decision tables evaluated by a
    priority loop (the campaign unit uses per-contender functions), proving the
    committed predictions are a pure function of the PUBLIC corpus alone;
  * metrics: recomputed with Counter-based aggregation (the campaign unit uses
    per-domain setdefault loops).

``--self-test`` proves the checker has detection power: six targeted in-memory
mutations (flipped label, flipped prediction, unfaithful observable, broken
digest binding, forged signature, invented donor accuracy) must each make the
corresponding check fail.  A checker that cannot fail is not a checker.

Exit 0 iff every check passes (or every self-test mutation is caught).
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "P7_SUBSTITUTE_CORPUS_V1.jsonl"
SEALED = HERE / "P7_SUBSTITUTE_SEALED_LABELS_V1.json"
PREDICTIONS = HERE / "P7_SUBSTITUTE_PREDICTIONS_V1.json"
REVEALED = HERE / "P7_SUBSTITUTE_LABELS_REVEALED_V1.json"
RECEIPT = HERE / "P7_SUBSTITUTE_CAMPAIGN_RECEIPT_V1.json"
PROTOCOL = HERE / "P7_SUBSTITUTE_CAMPAIGN_PROTOCOL_V1.md"

CUSTODIAN_KEY_DOMAIN = "P7-SUBSTITUTE-CUSTODIAN-V1-KEY"
EVALUATOR_KEY_DOMAIN = "P7-SUBSTITUTE-EVALUATOR-V1-KEY"

TERMINALS = ("TASK_STOP", "ROUTE_STOP", "REFRAME", "CANNOT_CHECK")
LABEL_BEARING_KEYS = {"family", "latent", "terminal", "negative_control"}


def cbytes(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def chash(obj) -> str:
    return hashlib.sha256(obj if isinstance(obj, bytes) else cbytes(obj)).hexdigest()


def expected_pub_hex(domain: str) -> str:
    seed = hashlib.sha256(domain.encode()).digest()
    return (
        Ed25519PrivateKey.from_private_bytes(seed)
        .public_key()
        .public_bytes(Encoding.Raw, PublicFormat.Raw)
        .hex()
    )


def signature_ok(payload: dict, domain: str) -> bool:
    key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(payload["public_key_hex"]))
    try:
        key.verify(bytes.fromhex(payload["signature_ed25519_hex"]), cbytes(payload["facts"]))
        return True
    except InvalidSignature:
        return False


# --- this checker's own contender semantics: data-driven priority tables ------

NAVIGATOR_RULES = [
    (lambda r: r["censoring_events"] > 0 or r["coverage_denominator"] == "UNKNOWN", "CANNOT_CHECK"),
    (lambda r: r["prior_closure_support_mapping"] == "PARTIAL", "CANNOT_CHECK"),
    (lambda r: r["solution_probe"] == "UNREACHABLE" and r["reframe_action_available"], "REFRAME"),
    (lambda r: len(r["route_backend_signatures"]) > 1 and len(set(r["route_backend_signatures"])) == 1, "ROUTE_STOP"),
]

B1_RULES = [
    (lambda r: len(r["route_backend_signatures"]) > 1 and len(set(r["route_backend_signatures"])) == 1, "ROUTE_STOP"),
]

B3_RULES = [
    (
        lambda r: r["solution_probe"] == "UNREACHABLE"
        or not r["unexpanded_frontier_nonempty"]
        or bool(r["outstanding_obligations"]),
        "REFRAME",
    ),
]


def decide(rules: list, row: dict) -> str:
    for matches, terminal in rules:
        if matches(row):
            return terminal
    return "TASK_STOP"


CHECKER_CONTENDERS = {
    "P7_ATLAS_NAVIGATOR": NAVIGATOR_RULES,
    "B0_FIXED_CHART_EXHAUSTIVE": [],
    "B1_FIXED_CHART_ROUTE_PRUNING": B1_RULES,
    "B3_REPRESENTATION_CHANGE_DONOR": B3_RULES,
}

# --- this checker's own label law: explicit priority table over latents -------

LABEL_RULES = [
    (lambda lat: lat["requires_topology_change"] and not lat["goal_reachable_current_chart"], "REFRAME"),
    (lambda lat: not lat["coverage_denominator_known"], "CANNOT_CHECK"),
    (lambda lat: lat["censoring_observed"], "CANNOT_CHECK"),
    (lambda lat: lat["prior_support_mapping_partial"], "CANNOT_CHECK"),
    (lambda lat: lat["open_routes_share_critical_backend"], "ROUTE_STOP"),
]

# --- this checker's own latent <-> observable faithfulness map ----------------

FAITHFULNESS = [
    ("solution_probe", lambda r, lat: (r["solution_probe"] == "UNREACHABLE") == lat["requires_topology_change"]),
    ("coverage_denominator", lambda r, lat: (r["coverage_denominator"] == "UNKNOWN") == (not lat["coverage_denominator_known"])),
    ("censoring_events", lambda r, lat: (r["censoring_events"] > 0) == lat["censoring_observed"]),
    ("support_mapping", lambda r, lat: (r["prior_closure_support_mapping"] == "PARTIAL") == lat["prior_support_mapping_partial"]),
    (
        "backend_sharing",
        lambda r, lat: (len(set(r["route_backend_signatures"])) == 1) == lat["open_routes_share_critical_backend"],
    ),
]


class Fails:
    """Collects failure labels; `guard` runs one check group."""

    def __init__(self) -> None:
        self.items: list[str] = []

    def guard(self, ok: bool, label: str) -> None:
        if not ok:
            self.items.append(label)


def verify_all(sealed: dict, corpus_rows: list[dict], reveal: dict, predictions: dict, receipt: dict, corpus_digest: str) -> Fails:
    f = Fails()

    # [1] seals and signatures
    f.guard(signature_ok(sealed, CUSTODIAN_KEY_DOMAIN), "custodian signature verifies")
    f.guard(sealed["public_key_hex"] == expected_pub_hex(CUSTODIAN_KEY_DOMAIN), "custodian key is the committed deterministic key")
    f.guard(chash(sealed["facts"]) == sealed["payload_digest"].removeprefix("sha256:"), "sealed facts digest matches")
    f.guard(signature_ok(predictions, EVALUATOR_KEY_DOMAIN), "evaluator signature verifies")
    f.guard(predictions["public_key_hex"] == expected_pub_hex(EVALUATOR_KEY_DOMAIN), "evaluator key is the committed deterministic key")
    f.guard(signature_ok(receipt, EVALUATOR_KEY_DOMAIN), "receipt signature verifies")
    f.guard(chash(receipt["facts"]) == receipt["payload_digest"].removeprefix("sha256:"), "receipt facts digest matches")

    # [2] digest bindings across the chain
    f.guard("sha256:" + corpus_digest == sealed["facts"]["corpus_sha256"], "sealed manifest binds the corpus bytes")
    f.guard("sha256:" + chash(PROTOCOL.read_bytes()) == sealed["facts"]["protocol_sha256"], "sealed manifest binds the frozen protocol bytes")
    f.guard("sha256:" + chash(cbytes(reveal)) == sealed["facts"]["labels_payload_digest"], "reveal payload hashes to the committed digest")
    f.guard(predictions["facts"]["corpus_sha256"] == "sha256:" + corpus_digest, "predictions bind the corpus digest")
    f.guard(predictions["facts"]["sealed_manifest_facts_digest"] == sealed["payload_digest"], "predictions bind the sealed manifest digest")

    # [3] structural blindness of the public corpus
    leaked = sorted({key for row in corpus_rows for key in row} & LABEL_BEARING_KEYS)
    f.guard(not leaked, f"corpus carries no label-bearing keys (found {leaked})")
    f.guard(len(corpus_rows) == 432, "corpus holds 432 rows")

    # [4] reveal integrity: own label law + own faithfulness map
    labels = reveal["labels"]
    ids_corpus = [row["id"] for row in corpus_rows]
    ids_labels = [rec["id"] for rec in labels]
    f.guard(Counter(ids_corpus) == Counter(ids_labels), "corpus ids and label ids are the same multiset")
    by_id = {row["id"]: row for row in corpus_rows}
    bad_law = [rec["id"] for rec in labels if decide(LABEL_RULES, rec["latent"]) != rec["terminal"]]
    f.guard(not bad_law, f"own label law reproduces every sealed terminal (violations: {bad_law[:3]})")
    unfaithful = []
    for rec in labels:
        row = by_id[rec["id"]]
        for _, test in FAITHFULNESS:
            if not test(row, rec["latent"]):
                unfaithful.append(rec["id"])
                break
    f.guard(not unfaithful, f"observables are a faithful measurement of the latents (violations: {unfaithful[:3]})")
    nc = sum(1 for rec in labels if rec["negative_control"])
    f.guard(nc == sealed["facts"]["power_counts"]["negative_controls"], "negative-control count matches the sealed power counts")
    term_counts = Counter(rec["terminal"] for rec in labels)
    f.guard(
        dict(term_counts) == sealed["facts"]["power_counts"]["terminals"],
        "terminal counts match the sealed power counts",
    )

    # [5] predictions are a pure function of the public corpus (own contenders)
    committed = predictions["facts"]["predictions"]
    f.guard(sorted(committed) == sorted(CHECKER_CONTENDERS), "all four contenders are present")
    for name, rules in CHECKER_CONTENDERS.items():
        derived = {row["id"]: decide(rules, row) for row in corpus_rows}
        mismatch = [p["id"] for p in committed[name] if derived[p["id"]] != p["prediction"]]
        f.guard(not mismatch, f"{name} predictions re-derive from the public corpus alone (mismatches: {mismatch[:3]})")
        f.guard(len(committed[name]) == 432, f"{name} judged 432 opportunities")

    # [6] metrics recomputed with Counter aggregation
    truth = {rec["id"]: rec["terminal"] for rec in labels}
    nc_ids = {rec["id"] for rec in labels if rec["negative_control"]}
    receipt_results = receipt["facts"]["results"]["contenders"]
    for name in CHECKER_CONTENDERS:
        per_domain_correct = Counter(p["domain"] for p in committed[name] if p["prediction"] == truth[p["id"]])
        per_domain_total = Counter(p["domain"] for p in committed[name])
        accs = {d: per_domain_correct[d] / per_domain_total[d] for d in per_domain_total}
        overall = sum(per_domain_correct.values()) / sum(per_domain_total.values())
        row = receipt_results[name]
        f.guard(abs(row["overall_accuracy"] - overall) < 1e-12, f"{name} overall accuracy recomputes")
        f.guard(abs(row["worst_domain_accuracy"] - min(accs.values())) < 1e-12, f"{name} worst-domain accuracy recomputes")
        wrong_by_domain = {d: per_domain_total[d] - per_domain_correct[d] for d in per_domain_total}
        f.guard(min(wrong_by_domain.values()) == row["min_wrong_per_domain"], f"{name} min wrong-per-domain recomputes")
        premature_pool = [p for p in committed[name] if truth[p["id"]] in ("CANNOT_CHECK", "REFRAME")]
        premature = sum(1 for p in premature_pool if p["prediction"] == "TASK_STOP")
        f.guard(
            row["premature_stop_rate"] == (premature / len(premature_pool) if premature_pool else None),
            f"{name} premature-stop rate recomputes",
        )
        nc_reframe = sum(1 for p in committed[name] if p["id"] in nc_ids and p["prediction"] == "REFRAME")
        f.guard(
            row["unnecessary_reframe_rate_on_negative_controls"] == nc_reframe / len(nc_ids),
            f"{name} unnecessary-reframe rate recomputes",
        )
        wrong_classes = sorted({truth[p["id"]] for p in committed[name] if p["prediction"] != truth[p["id"]]})
        f.guard(wrong_classes == row["wrong_true_classes"], f"{name} wrong-class set recomputes")

    # [7] prespecified gates hold on the recomputed numbers
    nav = receipt_results["P7_ATLAS_NAVIGATOR"]
    donors = {k: v for k, v in receipt_results.items() if k != "P7_ATLAS_NAVIGATOR"}
    f.guard(nav["overall_accuracy"] == 1.0, "navigator agrees with all 432 sealed labels")
    f.guard(nav["worst_domain_accuracy"] == 1.0, "navigator worst-domain accuracy is 1.0")
    f.guard(
        all(d["overall_accuracy"] < 1.0 and len(d["wrong_true_classes"]) >= 2 and d["min_wrong_per_domain"] >= 24 for d in donors.values()),
        "every donor is strictly worse on >=2 true classes and >=24 instances per domain",
    )
    f.guard(nav["premature_stop_rate"] == 0.0, "navigator premature-stop rate is zero")
    f.guard(
        donors["B0_FIXED_CHART_EXHAUSTIVE"]["premature_stop_rate"] > 0
        and donors["B1_FIXED_CHART_ROUTE_PRUNING"]["premature_stop_rate"] > 0,
        "B0 and B1 both exhibit premature stopping",
    )
    f.guard(nav["unnecessary_reframe_rate_on_negative_controls"] == 0.0, "navigator never reframes negative controls")
    f.guard(donors["B3_REPRESENTATION_CHANGE_DONOR"]["unnecessary_reframe_rate_on_negative_controls"] > 0, "B3 exhibits unnecessary reframing")
    for dom, terms in nav["predicted_terminals_per_domain"].items():
        f.guard(sorted(terms) == sorted(TERMINALS), f"navigator emits all terminals in {dom}")

    # [8] receipt gate table and boundary
    f.guard(all(v is True for v in receipt["facts"]["gates"].values()), "receipt records every gate as True")
    f.guard(receipt["outcome"] == "P7_SUBSTITUTE_CAMPAIGN_GREEN", "receipt outcome is GREEN")
    boundary = receipt["facts"]["authority_boundary"].lower()
    f.guard(
        "grants no naturalistic-corpus" in boundary and "live-agent" in boundary,
        "authority boundary denies naturalistic-corpus and live-agent authority",
    )
    return f


def self_test(sealed: dict, corpus_rows: list[dict], reveal: dict, predictions: dict, receipt: dict, corpus_digest: str) -> int:
    """Each targeted mutation must be caught; a miss means the checker is blind."""
    caught: list[str] = []

    m = deepcopy(sealed)
    m["facts"]["corpus_sha256"] = "sha256:" + "0" * 64
    caught.append(("corrupt corpus seal", any("corpus" in x for x in verify_all(m, corpus_rows, reveal, predictions, receipt, corpus_digest).items)))

    m = deepcopy(reveal)
    m["labels"][0]["terminal"] = "REFRAME" if m["labels"][0]["terminal"] != "REFRAME" else "TASK_STOP"
    fails = verify_all(sealed, corpus_rows, m, predictions, receipt, corpus_digest).items
    caught.append(("flipped sealed label", any("reveal payload" in x or "label law" in x or "digest" in x for x in fails)))

    m = deepcopy(predictions)
    m["facts"]["predictions"]["P7_ATLAS_NAVIGATOR"][7]["prediction"] = "DEFER"
    caught.append(("flipped prediction", any("re-derive" in x for x in verify_all(sealed, corpus_rows, reveal, m, receipt, corpus_digest).items)))

    m = deepcopy(reveal)
    for rec in m["labels"]:
        if rec["latent"]["censoring_observed"]:
            rec["latent"]["censoring_observed"] = False
            break
    caught.append(("unfaithful latent", any("faithful" in x for x in verify_all(sealed, corpus_rows, m, predictions, receipt, corpus_digest).items)))

    m = deepcopy(receipt)
    m["facts"]["results"]["contenders"]["B0_FIXED_CHART_EXHAUSTIVE"]["overall_accuracy"] = 0.99
    caught.append(("invented donor accuracy", any("B0_FIXED_CHART_EXHAUSTIVE overall" in x for x in verify_all(sealed, corpus_rows, reveal, predictions, m, corpus_digest).items)))

    m = deepcopy(predictions)
    m["signature_ed25519_hex"] = "00" * 64
    caught.append(("forged signature", any("signature" in x for x in verify_all(sealed, corpus_rows, reveal, m, receipt, corpus_digest).items)))

    escaped = [name for name, found in caught if not found]
    for name, found in caught:
        print(f"  {'caught ' if found else 'MISSED '} {name}")
    if escaped:
        print(f"\nSELF-TEST FAILED: mutations escaped detection: {escaped}")
        return 1
    print("\nSELF-TEST PASSED: every targeted mutation is detected")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        corpus_rows = [json.loads(line) for line in CORPUS.read_text(encoding="utf-8").splitlines() if line]
        return self_test(
            json.loads(SEALED.read_text()),
            corpus_rows,
            json.loads(REVEALED.read_text()),
            json.loads(PREDICTIONS.read_text()),
            json.loads(RECEIPT.read_text()),
            chash(CORPUS.read_bytes()),
        )

    corpus_rows = [json.loads(line) for line in CORPUS.read_text(encoding="utf-8").splitlines() if line]
    f = verify_all(
        json.loads(SEALED.read_text()),
        corpus_rows,
        json.loads(REVEALED.read_text()),
        json.loads(PREDICTIONS.read_text()),
        json.loads(RECEIPT.read_text()),
        chash(CORPUS.read_bytes()),
    )
    if f.items:
        print(f"CHECK FAILED: {len(f.items)} failing checks:")
        for item in f.items:
            print(f"  FAIL {item}")
        return 1
    print("CHECK PASSED: independent verifier confirms the P7 substitute campaign chain")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
