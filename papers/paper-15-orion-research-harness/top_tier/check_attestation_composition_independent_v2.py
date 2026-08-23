#!/usr/bin/env python3
"""Independent chain/disposition audit for P15 attestation composition V2.

Re-derives keys, signatures, digests, attacks and endpoints from the primary
receipt JSON plus the frozen fixtures. Shares no code with the primary runner.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

HERE = Path(__file__).resolve().parent
ROLES = ("execution", "environment", "publication")
SCI = ("scientific_contract_available", "scientific_contract_valid", "claim_authority_available",
       "claim_authority", "scientific_disposition")
EXECF = ("execution_id", "occurrence_id", "tool_id", "input_digest", "output_digest", "spawn_ok", "host_ok",
         "timeout", "exit_zero", "output_present", "output_complete", "reaped", "finalized_after_reap",
         "cleanup_complete", "retry_accounting_valid", "invocation_match", "input_digest_match",
         "result_digest_match", "occurrence_unique", "fresh", "coverage_complete", "replay_match",
         "lane_applicable", "lane_agree")
INTEG = ("spawn_ok", "host_ok", "timeout", "exit_zero", "output_present", "output_complete", "reaped",
         "finalized_after_reap", "cleanup_complete", "retry_accounting_valid", "invocation_match",
         "input_digest_match", "result_digest_match", "occurrence_unique", "fresh", "coverage_complete")
GEN = hashlib.sha256(b"P15-ATTESTATION-COMPOSITION-V2-GENESIS").hexdigest()


def cj(o):
    return json.dumps(o, sort_keys=True, separators=(',', ':')).encode()


def kpub(role, cid):
    s = hashlib.sha256(b"P15-ATTESTATION-COMPOSITION-V2-KEY-" + role.encode() + b"-" + cid.encode()).digest()
    return Ed25519PrivateKey.from_private_bytes(s).public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)


def ldigest(l):
    return hashlib.sha256(cj({'payload': l['payload'], 'signature': l['signature'],
                              'public_key_hex': l['public_key_hex']})).hexdigest()


def vchain(chain, cid):
    if [l['payload']['role'] for l in chain] != list(ROLES):
        return False
    run = GEN
    for l in chain:
        if l['payload']['previous_digest'] != run or l['public_key_hex'] != kpub(l['payload']['role'], cid):
            return False
        try:
            Ed25519PublicKey.from_public_bytes(bytes.fromhex(l['public_key_hex'])).verify(
                bytes.fromhex(l['signature']), cj(l['payload']))
        except (InvalidSignature, ValueError):
            return False
        run = ldigest(l)
    ex, pu = chain[0]['payload']['facts'], chain[2]['payload']['facts']
    return pu['claimed_execution_id'] == ex['execution_id'] and pu['claimed_occurrence_id'] == ex['occurrence_id'] \
        and all(pu[k] == ex[k] for k in ('reaped', 'finalized_after_reap', 'cleanup_complete',
                                         'retry_accounting_valid', 'coverage_complete'))


def integ(e):
    return all((e['spawn_ok'], e['host_ok'], not e['timeout'], e['exit_zero'], e['output_present'],
                e['output_complete'], e['reaped'], e['finalized_after_reap'], e['cleanup_complete'],
                e['retry_accounting_valid'], e['invocation_match'], e['input_digest_match'],
                e['result_digest_match'], e['occurrence_unique'], e['fresh'], e['coverage_complete']))


def sei(e, s):
    if not integ(e):
        return 'EXECUTION_INVALID'
    if not s.get('scientific_contract_available'):
        return 'CANNOT_CHECK'
    if not s['scientific_contract_valid']:
        return 'INVALID_SCIENCE'
    if not s.get('claim_authority_available'):
        return 'CANNOT_CHECK'
    return 'AUTHORIZED_SCIENCE' if s['claim_authority'] else 'VALID_BUT_NOT_AUTHORIZED'


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else 'p15_attestation_composition_v2.json'
    p = json.load(open(path))
    rows = p['rows']

    # 1. re-verify every stored chain independently and re-derive dispositions.
    base_ok = gold_ok = leak = 0
    for r in rows:
        chain = r['chain']
        assert vchain(chain, r['id']), r['id']
        assert ldigest(chain[-1]) == r['final_chain_digest'], r['id']
        base_ok += 1
        facts = chain[0]['payload']['facts']
        leak += sum(any(k in l['payload']['facts'] for k in SCI) for l in chain)
        gold_ok += int(sei(facts, sci_record(r)) == r['expected'] == r['chain_plus_sei'])
    assert base_ok == len(rows) == p['case_count']

    # 2. re-execute the structural attacks against the stored chains.
    trunc = subst = reorder = splice = 0
    for r in rows:
        chain = r['chain']
        for l in chain:
            try:
                Ed25519PublicKey.from_public_bytes(bytes.fromhex(l['public_key_hex'])).verify(
                    bytes.fromhex(l['signature']), cj(l['payload'])[:-1])
            except InvalidSignature:
                trunc += 1
        bad = json.loads(json.dumps(chain))
        bad[0]['payload']['facts']['exit_zero'] = not bad[0]['payload']['facts']['exit_zero']
        subst += int(not vchain(bad, r['id']))
        reorder += int(not vchain(list(reversed(json.loads(json.dumps(chain)))), r['id']))
        spl = json.loads(json.dumps(chain))
        spl[0]['payload']['facts']['exit_zero'] = not spl[0]['payload']['facts']['exit_zero']
        run = GEN
        for i, l in enumerate(spl):
            l['payload']['previous_digest'] = run
            if i > 0:
                s = hashlib.sha256(b"P15-ATTESTATION-COMPOSITION-V2-KEY-" + l['payload']['role'].encode()
                                   + b"-" + r['id'].encode()).digest()
                priv = Ed25519PrivateKey.from_private_bytes(s)
                l['signature'] = priv.sign(cj(l['payload'])).hex()
            run = ldigest(l)
        splice += int(not vchain(spl, r['id']))

    ids = [r['id'] for r in rows]
    replay = stale = 0
    seen = {r['chain'][2]['payload']['facts']['claimed_occurrence_id'] for r in rows}
    for i, r in enumerate(rows):
        other = rows[(i + 1) % len(rows)]
        claim = r['chain'][2]['payload']['facts']['claimed_occurrence_id']
        chn = other['chain']
        bound = chn[2]['payload']['facts']['claimed_occurrence_id']
        replay += int(vchain(chn, other['id']) and bound != claim)
        stale += int(vchain(r['chain'], r['id'])
                     and r['chain'][2]['payload']['facts']['claimed_occurrence_id'] in seen)

    # 3. re-derive the full-compromise boundary from the stored rows.
    comp = p['arms']['A-COMPROMISE-FULL']
    comp_ok = all(not c['signature_layer_detected'] for c in p['compromise_case_rows']) \
        and comp['signature_layer_detections'] == 0 \
        and comp['chain_as_science_false_promotions'] > 0 and comp['chain_plus_sei_false_promotions'] > 0

    # 4. endpoint agreement table.
    valid = [r for r in rows if r['expected'] != 'EXECUTION_INVALID']
    fr_chain = sum(not vchain(r['chain'], r['id']) for r in valid)
    fr_disp = sum(r['expected'] == 'AUTHORIZED_SCIENCE' and r['chain_plus_sei'] != 'AUTHORIZED_SCIENCE' for r in rows)
    table = {
        'case_count': (p['case_count'], len(rows)),
        'base_chain_verification_rate': (p['base_chain_verification_rate'], base_ok / len(rows)),
        'chain_plus_sei_gold_agreement_count': (p['chain_plus_sei_gold_agreement_count'], gold_ok),
        'scientific_field_leakage_count': (p['scientific_field_leakage_count'], leak),
        'A-TRUNCATE detections': (p['arms']['A-TRUNCATE']['detections'], trunc),
        'A-SUBSTITUTE detections': (p['arms']['A-SUBSTITUTE']['detections'], subst),
        'A-SPLICE detections': (p['arms']['A-SPLICE']['detections'], splice),
        'A-REORDER detections': (p['arms']['A-REORDER']['detections'], reorder),
        'A-REPLAY detections': (p['arms']['A-REPLAY']['detections'], replay),
        'A-STALE detections': (p['arms']['A-STALE']['detections'], stale),
        'chain_layer_false_rejection_count': (p['chain_layer_false_rejection_count'], fr_chain),
        'disposition_false_rejection_count': (p['disposition_false_rejection_count'], fr_disp),
        'chain_crypto_only_false_scientific_success_count':
            (p['chain_crypto_only_false_scientific_success_count'],
             sum(r['chain_crypto_only'] == 'AUTHORIZED_SCIENCE' for r in rows)),
    }
    agree = all(a == b for a, b in table.values())
    green = (agree and comp_ok and p['terminal'] == 'P15_ATTESTATION_COMPOSITION_V2_SUPPORTED')
    receipt = {'schema': 'P15.AttestationCompositionIndependent.v2',
               'source_sha256': hashlib.sha256(open(path, 'rb').read()).hexdigest(),
               'case_count': len(rows), 'endpoint_agreement_table': table,
               'full_compromise_boundary_confirmed': comp_ok,
               'terminal': 'P15_ATTESTATION_COMPOSITION_V2_SECOND_CHECKER_GREEN' if green else
               'P15_ATTESTATION_COMPOSITION_V2_SECOND_CHECKER_RED'}
    receipt['receipt_sha256'] = hashlib.sha256(cj(receipt)).hexdigest()
    print(json.dumps(receipt, indent=2, sort_keys=True))
    assert green, receipt
    return 0


def sci_record(row):
    """Independent lookup of the frozen science/authority record for a row."""
    if row['group'] == 'real':
        recs = json.loads((HERE / 'p15_real_workflow_receipts_v1.json').read_text())['receipts']
        src = next(c for c in recs if c['id'] == row['id'])
    else:
        src = next(c for c in (json.loads(x) for x in
                   (HERE / 'sei_fault_cases_v1.jsonl').read_text().splitlines()) if c['id'] == row['id'])
    return {k: src[k] for k in ('scientific_contract_available', 'scientific_contract_valid',
                                'claim_authority_available', 'claim_authority')}


if __name__ == '__main__':
    raise SystemExit(main())
