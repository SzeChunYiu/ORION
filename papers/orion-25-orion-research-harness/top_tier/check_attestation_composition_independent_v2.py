#!/usr/bin/env python3
"""Independent chain/disposition audit for P15 attestation composition V2.

Re-derives keys, signatures, digests, replay/stale attacks, full-compromise
chains and scientific endpoints from the frozen fixtures plus the primary's
stored base chains. Shares no code with the primary runner.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

HERE = Path(__file__).resolve().parent
FAULTS = HERE / "sei_fault_cases_v1.jsonl"
GOLD = HERE / "sei_fault_gold_v1.json"
REAL = HERE / "p15_real_workflow_receipts_v1.json"
ROLES = ("execution", "environment", "publication")
SCI = (
    "scientific_contract_available",
    "scientific_contract_valid",
    "claim_authority_available",
    "claim_authority",
    "scientific_disposition",
)
EXECF = (
    "execution_id",
    "occurrence_id",
    "tool_id",
    "input_digest",
    "output_digest",
    "spawn_ok",
    "host_ok",
    "timeout",
    "exit_zero",
    "output_present",
    "output_complete",
    "reaped",
    "finalized_after_reap",
    "cleanup_complete",
    "retry_accounting_valid",
    "invocation_match",
    "input_digest_match",
    "result_digest_match",
    "occurrence_unique",
    "fresh",
    "coverage_complete",
    "replay_match",
    "lane_applicable",
    "lane_agree",
)
INTEG = (
    "spawn_ok",
    "host_ok",
    "timeout",
    "exit_zero",
    "output_present",
    "output_complete",
    "reaped",
    "finalized_after_reap",
    "cleanup_complete",
    "retry_accounting_valid",
    "invocation_match",
    "input_digest_match",
    "result_digest_match",
    "occurrence_unique",
    "fresh",
    "coverage_complete",
)
COMPROMISE_CASES = (
    "SEI-NONZERO-MISLEADING",
    "SEI-TRUNCATED",
    "SEI-PRE-REAP-FINAL",
    "SEI-CLEANUP-OMIT",
    "SEI-STALE-REPLAY",
    "SEI-DUP-OCCURRENCE",
)
GEN = hashlib.sha256(b"P15-ATTESTATION-COMPOSITION-V2-GENESIS").hexdigest()


def cj(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def kpriv(role, cid):
    seed = hashlib.sha256(
        b"P15-ATTESTATION-COMPOSITION-V2-KEY-" + role.encode() + b"-" + cid.encode()
    ).digest()
    return Ed25519PrivateKey.from_private_bytes(seed)


def kpub(role, cid):
    return kpriv(role, cid).public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()


def ldigest(link):
    return hashlib.sha256(
        cj(
            {
                "payload": link["payload"],
                "signature": link["signature"],
                "public_key_hex": link["public_key_hex"],
            }
        )
    ).hexdigest()


def role_facts(role, cid, execution):
    if role == "execution":
        return {key: execution[key] for key in EXECF}
    if role == "environment":
        return {
            "runner_class": "github-hosted-ubuntu-latest",
            "os_image": "ubuntu-24.04-x86_64",
            "python_version": "3.12",
            "tool_id": execution["tool_id"],
            "input_digest": execution["input_digest"],
            "output_digest": execution["output_digest"],
        }
    return {
        "claimed_execution_id": execution["execution_id"],
        "claimed_occurrence_id": execution["occurrence_id"],
        "reaped": execution["reaped"],
        "finalized_after_reap": execution["finalized_after_reap"],
        "cleanup_complete": execution["cleanup_complete"],
        "retry_accounting_valid": execution["retry_accounting_valid"],
        "coverage_complete": execution["coverage_complete"],
        "artifact_uri": "orion-att-v2:" + cid,
    }


def compose(cid, execution):
    running = GEN
    chain = []
    for role in ROLES:
        payload = {
            "role": role,
            "previous_digest": running,
            "facts": role_facts(role, cid, execution),
        }
        private = kpriv(role, cid)
        link = {
            "payload": payload,
            "signature": private.sign(cj(payload)).hex(),
            "public_key_hex": private.public_key()
            .public_bytes(Encoding.Raw, PublicFormat.Raw)
            .hex(),
        }
        chain.append(link)
        running = ldigest(link)
    return chain


def vchain_detail(chain, cid, *, claimed_occurrence=None, consumed=None):
    if len(chain) != len(ROLES):
        return False, "length"
    if [link["payload"]["role"] for link in chain] != list(ROLES):
        return False, "role-order"
    running = GEN
    for link in chain:
        role = link["payload"]["role"]
        if link["payload"]["previous_digest"] != running:
            return False, "chaining"
        if link["public_key_hex"] != kpub(role, cid):
            return False, "key-substitution"
        try:
            Ed25519PublicKey.from_public_bytes(bytes.fromhex(link["public_key_hex"])).verify(
                bytes.fromhex(link["signature"]), cj(link["payload"])
            )
        except (InvalidSignature, ValueError):
            return False, "signature"
        running = ldigest(link)

    execution = chain[0]["payload"]["facts"]
    publication = chain[2]["payload"]["facts"]
    if not (
        publication["claimed_execution_id"] == execution["execution_id"]
        and publication["claimed_occurrence_id"] == execution["occurrence_id"]
        and all(
            publication[key] == execution[key]
            for key in (
                "reaped",
                "finalized_after_reap",
                "cleanup_complete",
                "retry_accounting_valid",
                "coverage_complete",
            )
        )
    ):
        return False, "publication-consistency"

    bound = publication["claimed_occurrence_id"]
    if claimed_occurrence is not None and bound != claimed_occurrence:
        return False, "replay-binding"
    if consumed is not None and bound in consumed:
        return False, "consumed-occurrence"
    return True, "ok"


def vchain(chain, cid, **kwargs):
    return vchain_detail(chain, cid, **kwargs)[0]


def integ(execution):
    return all(
        (
            execution["spawn_ok"],
            execution["host_ok"],
            not execution["timeout"],
            execution["exit_zero"],
            execution["output_present"],
            execution["output_complete"],
            execution["reaped"],
            execution["finalized_after_reap"],
            execution["cleanup_complete"],
            execution["retry_accounting_valid"],
            execution["invocation_match"],
            execution["input_digest_match"],
            execution["result_digest_match"],
            execution["occurrence_unique"],
            execution["fresh"],
            execution["coverage_complete"],
        )
    )


def sei(execution, science):
    if not integ(execution):
        return "EXECUTION_INVALID"
    if not science.get("scientific_contract_available"):
        return "CANNOT_CHECK"
    if not science["scientific_contract_valid"]:
        return "INVALID_SCIENCE"
    if not science.get("claim_authority_available"):
        return "CANNOT_CHECK"
    return "AUTHORIZED_SCIENCE" if science["claim_authority"] else "VALID_BUT_NOT_AUTHORIZED"


def frozen_case(row):
    """Reconstruct execution/science/expected values from frozen source fixtures."""
    cid = row["id"]
    if row["group"] == "real":
        records = json.loads(REAL.read_text())["receipts"]
        source = next(record for record in records if record["id"] == cid)
        execution = {key: source[key] for key in EXECF}
        science = {key: source[key] for key in SCI if key in source}
        expected = source["expected_disposition"]
        return execution, science, expected

    source = next(
        record
        for record in (json.loads(line) for line in FAULTS.read_text().splitlines() if line.strip())
        if record["id"] == cid
    )
    normalized = {
        key: source[key]
        for key in source
        if key not in SCI and key not in ("id", "case_type")
    }
    normalized.update(
        {
            "execution_id": f"fault:{cid}",
            "occurrence_id": f"fault:{cid}:1",
            "tool_id": "p15-sei-fault-fixture",
            "input_digest": "sha256:" + hashlib.sha256((cid + ":input").encode()).hexdigest(),
            "output_digest": "sha256:" + hashlib.sha256((cid + ":output").encode()).hexdigest(),
        }
    )
    execution = {key: normalized[key] for key in EXECF}
    science = {key: source[key] for key in SCI if key in source}
    expected = json.loads(GOLD.read_text())[cid]
    return execution, science, expected


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "p15_attestation_composition_v2.json"
    primary = json.load(open(path))
    rows = primary["rows"]

    # 1. Re-verify every stored chain and derive dispositions from frozen fixtures.
    base_ok = gold_ok = leakage = 0
    reconstructed = {}
    for row in rows:
        execution, science, expected = frozen_case(row)
        reconstructed[row["id"]] = execution
        chain = row["chain"]
        assert vchain(chain, row["id"]), row["id"]
        assert ldigest(chain[-1]) == row["final_chain_digest"], row["id"]
        base_ok += 1
        signed_execution = chain[0]["payload"]["facts"]
        assert signed_execution == execution, row["id"]
        leakage += sum(any(key in link["payload"]["facts"] for key in SCI) for link in chain)
        gold_ok += int(sei(execution, science) == expected == row["chain_plus_sei"])
    assert base_ok == len(rows) == primary["case_count"]

    # 2. Re-execute structural attacks against stored chains.
    truncate = substitute = reorder = splice = 0
    for row in rows:
        chain = row["chain"]
        for link in chain:
            try:
                Ed25519PublicKey.from_public_bytes(bytes.fromhex(link["public_key_hex"])).verify(
                    bytes.fromhex(link["signature"]), cj(link["payload"])[:-1]
                )
            except InvalidSignature:
                truncate += 1

        bad = json.loads(json.dumps(chain))
        bad[0]["payload"]["facts"]["exit_zero"] = not bad[0]["payload"]["facts"]["exit_zero"]
        substitute += int(not vchain(bad, row["id"]))
        reorder += int(not vchain(list(reversed(json.loads(json.dumps(chain)))), row["id"]))

        spl = json.loads(json.dumps(chain))
        spl[0]["payload"]["facts"]["exit_zero"] = not spl[0]["payload"]["facts"]["exit_zero"]
        running = GEN
        for index, link in enumerate(spl):
            link["payload"]["previous_digest"] = running
            if index > 0:
                private = kpriv(link["payload"]["role"], row["id"])
                link["signature"] = private.sign(cj(link["payload"])).hex()
            running = ldigest(link)
        splice += int(not vchain(spl, row["id"]))

    # Replay detection must bind a genuine chain to the claimant occurrence.
    replay = 0
    for index, row in enumerate(rows):
        other = rows[(index + 1) % len(rows)]
        claimed = reconstructed[row["id"]]["occurrence_id"]
        ok, reason = vchain_detail(
            other["chain"], other["id"], claimed_occurrence=claimed
        )
        replay += int(not ok and reason == "replay-binding")

    # Stale detection must reject a genuinely valid occurrence after consumption.
    consumed = {execution["occurrence_id"] for execution in reconstructed.values()}
    stale = 0
    for row in rows:
        ok, reason = vchain_detail(row["chain"], row["id"], consumed=consumed)
        stale += int(not ok and reason == "consumed-occurrence")

    # 3. Rebuild full-compromise chains from frozen fixtures; do not trust primary rows.
    by_id = {row["id"]: row for row in rows}
    compromise_rows = []
    for cid in COMPROMISE_CASES:
        execution, science, expected = frozen_case(by_id[cid])
        forged = dict(execution)
        for field in INTEG:
            forged[field] = field != "timeout"
        chain = compose(cid, forged)
        ok, _ = vchain_detail(chain, cid)
        compromise_rows.append(
            {
                "id": cid,
                "expected": expected,
                "signature_layer_detected": not ok,
                "chain_as_science": (
                    "AUTHORIZED_SCIENCE" if ok and integ(forged) else "EXECUTION_INVALID"
                ),
                "chain_plus_sei": sei(forged, science),
            }
        )
    compromise = {
        "attempts": len(compromise_rows),
        "signature_layer_detections": sum(row["signature_layer_detected"] for row in compromise_rows),
        "chain_as_science_false_promotions": sum(
            row["chain_as_science"] == "AUTHORIZED_SCIENCE"
            and row["expected"] != "AUTHORIZED_SCIENCE"
            for row in compromise_rows
        ),
        "chain_plus_sei_false_promotions": sum(
            row["chain_plus_sei"] == "AUTHORIZED_SCIENCE"
            and row["expected"] != "AUTHORIZED_SCIENCE"
            for row in compromise_rows
        ),
    }
    compromise_ok = (
        compromise["signature_layer_detections"] == 0
        and compromise["chain_as_science_false_promotions"] > 0
        and compromise["chain_plus_sei_false_promotions"] > 0
    )

    # 4. Endpoint agreement table.
    valid = [row for row in rows if frozen_case(row)[2] != "EXECUTION_INVALID"]
    false_reject_chain = sum(not vchain(row["chain"], row["id"]) for row in valid)
    false_reject_disposition = sum(
        frozen_case(row)[2] == "AUTHORIZED_SCIENCE"
        and row["chain_plus_sei"] != "AUTHORIZED_SCIENCE"
        for row in rows
    )
    primary_compromise = primary["arms"]["A-COMPROMISE-FULL"]
    table = {
        "case_count": (primary["case_count"], len(rows)),
        "base_chain_verification_rate": (primary["base_chain_verification_rate"], base_ok / len(rows)),
        "chain_plus_sei_gold_agreement_count": (primary["chain_plus_sei_gold_agreement_count"], gold_ok),
        "scientific_field_leakage_count": (primary["scientific_field_leakage_count"], leakage),
        "A-TRUNCATE detections": (primary["arms"]["A-TRUNCATE"]["detections"], truncate),
        "A-SUBSTITUTE detections": (primary["arms"]["A-SUBSTITUTE"]["detections"], substitute),
        "A-SPLICE detections": (primary["arms"]["A-SPLICE"]["detections"], splice),
        "A-REORDER detections": (primary["arms"]["A-REORDER"]["detections"], reorder),
        "A-REPLAY detections": (primary["arms"]["A-REPLAY"]["detections"], replay),
        "A-STALE detections": (primary["arms"]["A-STALE"]["detections"], stale),
        "A-COMPROMISE-FULL attempts": (primary_compromise["attempts"], compromise["attempts"]),
        "A-COMPROMISE-FULL signature_layer_detections": (
            primary_compromise["signature_layer_detections"],
            compromise["signature_layer_detections"],
        ),
        "A-COMPROMISE-FULL chain_as_science_false_promotions": (
            primary_compromise["chain_as_science_false_promotions"],
            compromise["chain_as_science_false_promotions"],
        ),
        "A-COMPROMISE-FULL chain_plus_sei_false_promotions": (
            primary_compromise["chain_plus_sei_false_promotions"],
            compromise["chain_plus_sei_false_promotions"],
        ),
        "chain_layer_false_rejection_count": (
            primary["chain_layer_false_rejection_count"],
            false_reject_chain,
        ),
        "disposition_false_rejection_count": (
            primary["disposition_false_rejection_count"],
            false_reject_disposition,
        ),
        "chain_crypto_only_false_scientific_success_count": (
            primary["chain_crypto_only_false_scientific_success_count"],
            sum(row["chain_crypto_only"] == "AUTHORIZED_SCIENCE" for row in rows),
        ),
    }
    agree = all(left == right for left, right in table.values())
    green = (
        agree
        and compromise_ok
        and primary["terminal"] == "P15_ATTESTATION_COMPOSITION_V2_SUPPORTED"
    )
    receipt = {
        "schema": "P15.AttestationCompositionIndependent.v2",
        "source_sha256": hashlib.sha256(open(path, "rb").read()).hexdigest(),
        "case_count": len(rows),
        "endpoint_agreement_table": table,
        "full_compromise_boundary_confirmed": compromise_ok,
        "terminal": (
            "P15_ATTESTATION_COMPOSITION_V2_SECOND_CHECKER_GREEN"
            if green
            else "P15_ATTESTATION_COMPOSITION_V2_SECOND_CHECKER_RED"
        ),
    }
    receipt["receipt_sha256"] = hashlib.sha256(cj(receipt)).hexdigest()
    print(json.dumps(receipt, indent=2, sort_keys=True))
    assert green, receipt
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
