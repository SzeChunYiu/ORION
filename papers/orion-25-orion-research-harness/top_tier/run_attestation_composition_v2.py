#!/usr/bin/env python3
"""Execute frozen P15 Ed25519 attestation chain-composition study V2."""
from __future__ import annotations
import hashlib, json, platform
from pathlib import Path
from cryptography import __version__ as CRYPTOGRAPHY_VERSION
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

HERE = Path(__file__).resolve().parent
FAULTS = HERE / 'sei_fault_cases_v1.jsonl'
GOLD = HERE / 'sei_fault_gold_v1.json'
REAL = HERE / 'p15_real_workflow_receipts_v1.json'
PROTOCOL = HERE / 'P15_ATTESTATION_COMPOSITION_PROTOCOL_V2.md'

EXEC_FIELDS = ("execution_id", "occurrence_id", "tool_id", "input_digest", "output_digest", "spawn_ok", "host_ok",
               "timeout", "exit_zero", "output_present", "output_complete", "reaped", "finalized_after_reap",
               "cleanup_complete", "retry_accounting_valid", "invocation_match", "input_digest_match",
               "result_digest_match", "occurrence_unique", "fresh", "coverage_complete", "replay_match",
               "lane_applicable", "lane_agree")
SCI_FIELDS = ("scientific_contract_available", "scientific_contract_valid", "claim_authority_available",
              "claim_authority", "scientific_disposition")
INTEGRITY_FIELDS = ("spawn_ok", "host_ok", "timeout", "exit_zero", "output_present", "output_complete", "reaped",
                    "finalized_after_reap", "cleanup_complete", "retry_accounting_valid", "invocation_match",
                    "input_digest_match", "result_digest_match", "occurrence_unique", "fresh", "coverage_complete")
ROLES = ("execution", "environment", "publication")
GENESIS = hashlib.sha256(b"P15-ATTESTATION-COMPOSITION-V2-GENESIS").hexdigest()
COMPROMISE_CASES = ("SEI-NONZERO-MISLEADING", "SEI-TRUNCATED", "SEI-PRE-REAP-FINAL", "SEI-CLEANUP-OMIT",
                    "SEI-STALE-REPLAY", "SEI-DUP-OCCURRENCE")


def execution_integrity(e):
    return all((e['spawn_ok'], e['host_ok'], not e['timeout'], e['exit_zero'], e['output_present'],
                e['output_complete'], e['reaped'], e['finalized_after_reap'], e['cleanup_complete'],
                e['retry_accounting_valid'], e['invocation_match'], e['input_digest_match'],
                e['result_digest_match'], e['occurrence_unique'], e['fresh'], e['coverage_complete']))


def sei(e, s):
    if not execution_integrity(e):
        return 'EXECUTION_INVALID'
    if s is None or not s['scientific_contract_available']:
        return 'CANNOT_CHECK'
    if not s['scientific_contract_valid']:
        return 'INVALID_SCIENCE'
    if not s['claim_authority_available']:
        return 'CANNOT_CHECK'
    if not s['claim_authority']:
        return 'VALID_BUT_NOT_AUTHORIZED'
    return 'AUTHORIZED_SCIENCE'


def norm_fault(c):
    x = {k: c[k] for k in c if k not in SCI_FIELDS and k not in ('id', 'case_type')}
    x.update({'execution_id': f"fault:{c['id']}", 'occurrence_id': f"fault:{c['id']}:1",
              'tool_id': 'p15-sei-fault-fixture',
              'input_digest': 'sha256:' + hashlib.sha256((c['id'] + ':input').encode()).hexdigest(),
              'output_digest': 'sha256:' + hashlib.sha256((c['id'] + ':output').encode()).hexdigest()})
    return {k: x[k] for k in EXEC_FIELDS}, {k: c[k] for k in SCI_FIELDS if k in c}


def norm_real(c):
    return {k: c[k] for k in EXEC_FIELDS}, {k: c[k] for k in SCI_FIELDS if k in c}


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()


def role_key(role, cid):
    seed = hashlib.sha256(b"P15-ATTESTATION-COMPOSITION-V2-KEY-" + role.encode() + b"-" + cid.encode()).digest()
    return Ed25519PrivateKey.from_private_bytes(seed)


def role_public_hex(role, cid):
    return role_key(role, cid).public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()


def facts_for(role, cid, e):
    if role == 'execution':
        return {k: e[k] for k in EXEC_FIELDS}
    if role == 'environment':
        return {'runner_class': 'github-hosted-ubuntu-latest', 'os_image': 'ubuntu-24.04-x86_64',
                'python_version': '3.12', 'tool_id': e['tool_id'], 'input_digest': e['input_digest'],
                'output_digest': e['output_digest']}
    return {'claimed_execution_id': e['execution_id'], 'claimed_occurrence_id': e['occurrence_id'],
            'reaped': e['reaped'], 'finalized_after_reap': e['finalized_after_reap'],
            'cleanup_complete': e['cleanup_complete'], 'retry_accounting_valid': e['retry_accounting_valid'],
            'coverage_complete': e['coverage_complete'], 'artifact_uri': 'orion-att-v2:' + cid}


def link_digest(link):
    return hashlib.sha256(canonical({'payload': link['payload'], 'signature': link['signature'],
                                      'public_key_hex': link['public_key_hex']})).hexdigest()


def compose(cid, e):
    """Build the three-link chain from the (possibly forged) normalized record e."""
    running, links = GENESIS, []
    for role in ROLES:
        payload = {'role': role, 'previous_digest': running, 'facts': facts_for(role, cid, e)}
        priv = role_key(role, cid)
        sig = priv.sign(canonical(payload))
        link = {'payload': payload, 'signature': sig.hex(),
                'public_key_hex': priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()}
        links.append(link)
        running = link_digest(link)
    return links


def verify_chain(chain, cid, claimed_occurrence=None, consumed=None):
    """Return (ok, reason). Checks length, role order, digest chaining, signatures,
    expected role keys, publication consistency and occurrence binding/consumption."""
    if len(chain) != len(ROLES):
        return False, 'length'
    running = GENESIS
    for i, link in enumerate(chain):
        payload = link['payload']
        if payload['role'] != ROLES[i]:
            return False, 'role-order'
        if payload['previous_digest'] != running:
            return False, 'chaining'
        if link['public_key_hex'] != role_public_hex(ROLES[i], cid):
            return False, 'key-substitution'
        try:
            Ed25519PublicKey.from_public_bytes(bytes.fromhex(link['public_key_hex'])).verify(
                bytes.fromhex(link['signature']), canonical(payload))
        except (InvalidSignature, ValueError):
            return False, 'signature'
        running = link_digest(link)
    ex, pub = chain[0]['payload']['facts'], chain[2]['payload']['facts']
    if pub['claimed_execution_id'] != ex['execution_id'] or pub['claimed_occurrence_id'] != ex['occurrence_id'] \
            or any(pub[k] != ex[k] for k in ('reaped', 'finalized_after_reap', 'cleanup_complete',
                                             'retry_accounting_valid', 'coverage_complete')):
        return False, 'publication-consistency'
    bound = chain[2]['payload']['facts']['claimed_occurrence_id']
    if claimed_occurrence is not None and bound != claimed_occurrence:
        return False, 'replay-binding'
    if consumed is not None and bound in consumed:
        return False, 'consumed-occurrence'
    return True, 'ok'


def crypto_only(chain_ok, e):
    return 'CANNOT_CHECK' if (chain_ok and execution_integrity(e)) else 'EXECUTION_INVALID'


def main():
    faults = [json.loads(x) for x in FAULTS.read_text().splitlines() if x.strip()]
    gold = json.loads(GOLD.read_text())
    real = json.loads(REAL.read_text())['receipts']
    cases = []
    for c in faults:
        e, s = norm_fault(c)
        cases.append(('fault', c['id'], e, s, gold[c['id']]))
    for c in real:
        e, s = norm_real(c)
        cases.append(('real', c['id'], e, s, c['expected_disposition']))

    leakage, rows, consumed = 0, [], set()
    for group, cid, e, s, expected in cases:
        chain = compose(cid, e)
        ok, reason = verify_chain(chain, cid)
        assert ok, (cid, reason)
        consumed.add(chain[2]['payload']['facts']['claimed_occurrence_id'])
        signed_keys = set()
        for link in chain:
            signed_keys |= set(link['payload']['facts'])
        leakage += sum(k in signed_keys for k in SCI_FIELDS)
        native = sei(e, s)
        rows.append({'group': group, 'id': cid, 'expected': expected, 'native': native,
                     'chain_crypto_only': crypto_only(True, e), 'chain_as_science':
                     'AUTHORIZED_SCIENCE' if execution_integrity(e) else 'EXECUTION_INVALID',
                     'chain_plus_sei': native, 'final_chain_digest': link_digest(chain[-1]),
                     'chain': chain})

    by_id = {r['id']: r for r in rows}
    chains = {cid: compose(cid, e) for _, cid, e, _, _ in cases}
    arms = {}

    # A-TRUNCATE: last byte dropped from each signed payload.
    det = att = 0
    for cid, chain in chains.items():
        for link in chain:
            att += 1
            try:
                Ed25519PublicKey.from_public_bytes(bytes.fromhex(link['public_key_hex'])).verify(
                    bytes.fromhex(link['signature']), canonical(link['payload'])[:-1])
            except InvalidSignature:
                det += 1
    arms['A-TRUNCATE'] = {'attempts': att, 'detections': det}

    # A-SUBSTITUTE: one bound execution fact flipped after signing, signatures kept.
    det = att = 0
    for cid, chain in chains.items():
        att += 1
        tampered = json.loads(json.dumps(chain))
        tampered[0]['payload']['facts']['exit_zero'] = not tampered[0]['payload']['facts']['exit_zero']
        ok, reason = verify_chain(tampered, cid)
        det += int(not ok)
    arms['A-SUBSTITUTE'] = {'attempts': att, 'detections': det}

    # A-SPLICE: execution facts tampered, only environment+publication links re-signed.
    det = att = 0
    for cid, chain in chains.items():
        att += 1
        e = next(e for _, c, e, _, _ in cases if c == cid)
        forged = dict(e)
        forged['exit_zero'] = not e['exit_zero']  # guaranteed fact change so the splice always differs
        forged['output_complete'] = not e['output_complete']
        splice = []
        running = GENESIS
        for role in ROLES:
            facts = dict(facts_for(role, cid, forged if role == 'execution' else e))
            payload = {'role': role, 'previous_digest': running, 'facts': facts}
            if role == 'execution':
                payload = dict(chain[0]['payload'])
                payload['facts'] = facts
                link = {'payload': payload, 'signature': chain[0]['signature'],
                        'public_key_hex': chain[0]['public_key_hex']}
            else:
                priv = role_key(role, cid)
                sig = priv.sign(canonical(payload))
                link = {'payload': payload, 'signature': sig.hex(),
                        'public_key_hex': priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()}
            splice.append(link)
            running = link_digest(link)
        ok, reason = verify_chain(splice, cid)
        det += int(not ok and reason == 'signature')
    arms['A-SPLICE'] = {'attempts': att, 'detections': det}

    # A-REORDER: genuine links presented in reversed order.
    det = att = 0
    for cid, chain in chains.items():
        att += 1
        ok, reason = verify_chain(list(reversed([json.loads(json.dumps(l)) for l in chain])), cid)
        det += int(not ok)
    arms['A-REORDER'] = {'attempts': att, 'detections': det}

    # A-REPLAY: case X's genuine chain presented for case Y's claimed occurrence.
    det = att = 0
    ordered = [cid for _, cid, _, _, _ in cases]
    for i, cid in enumerate(ordered):
        att += 1
        other = ordered[(i + 1) % len(ordered)]
        e_claimant = next(e for _, c, e, _, _ in cases if c == cid)
        ok, reason = verify_chain(chains[other], other, claimed_occurrence=e_claimant['occurrence_id'])
        det += int(not ok and reason == 'replay-binding')
    arms['A-REPLAY'] = {'attempts': att, 'detections': det}

    # A-STALE: an already-consumed genuine chain re-presented.
    det = att = 0
    for cid, chain in chains.items():
        att += 1
        ok, reason = verify_chain(chain, cid, consumed=consumed)
        det += int(not ok and reason == 'consumed-occurrence')
    arms['A-STALE'] = {'attempts': att, 'detections': det}

    # A-COMPROMISE-FULL: execution facts forged clean, every link re-signed with genuine keys.
    comp_rows = []
    for cid in COMPROMISE_CASES:
        e, s, expected = next((e, s, exp) for _, c, e, s, exp in cases if c == cid)
        forged = dict(e)
        for f in INTEGRITY_FIELDS:
            forged[f] = f != 'timeout'
        # full key-set compromise: every link (execution, environment, publication) is
        # re-signed consistently from the forged record, not spliced against original facts
        chain = compose(cid, forged)
        ok, reason = verify_chain(chain, cid)
        comp_rows.append({'id': cid, 'expected': expected, 'signature_layer_detected': not ok,
                          'chain_crypto_only': crypto_only(ok, forged),
                          'chain_as_science': 'AUTHORIZED_SCIENCE' if (ok and execution_integrity(forged)) else 'EXECUTION_INVALID',
                          'chain_plus_sei': sei(forged, s), 'final_chain_digest': link_digest(chain[-1])})
    arms['A-COMPROMISE-FULL'] = {
        'attempts': len(comp_rows),
        'signature_layer_detections': sum(r['signature_layer_detected'] for r in comp_rows),
        'chain_as_science_false_promotions': sum(r['chain_as_science'] == 'AUTHORIZED_SCIENCE' and r['expected'] != 'AUTHORIZED_SCIENCE' for r in comp_rows),
        'chain_plus_sei_false_promotions': sum(r['chain_plus_sei'] == 'AUTHORIZED_SCIENCE' and r['expected'] != 'AUTHORIZED_SCIENCE' for r in comp_rows)}

    valid_ids = [r['id'] for r in rows if r['expected'] != 'EXECUTION_INVALID']
    chain_false_reject = sum(not verify_chain(chains[r], r)[0] for r in valid_ids)
    disp_false_reject = sum(r['expected'] == 'AUTHORIZED_SCIENCE' and r['chain_plus_sei'] != 'AUTHORIZED_SCIENCE' for r in rows)
    real_false_promote = sum(r['group'] == 'real' and r['expected'] != 'AUTHORIZED_SCIENCE' and r['chain_plus_sei'] == 'AUTHORIZED_SCIENCE' for r in rows)
    base_ok = sum(verify_chain(chains[r], r)[0] for r in [x['id'] for x in rows])
    gold_agree = sum(r['chain_plus_sei'] == r['expected'] == r['native'] for r in rows)
    crypto_false = sum(r['chain_crypto_only'] == 'AUTHORIZED_SCIENCE' for r in rows) + \
        sum(r['chain_crypto_only'] == 'AUTHORIZED_SCIENCE' for r in comp_rows)
    misuse_total = sum(r['chain_as_science'] == 'AUTHORIZED_SCIENCE' and r['expected'] != 'AUTHORIZED_SCIENCE' for r in rows) \
        + arms['A-COMPROMISE-FULL']['chain_as_science_false_promotions']
    detected_arms = ('A-TRUNCATE', 'A-SUBSTITUTE', 'A-SPLICE', 'A-REORDER', 'A-REPLAY', 'A-STALE')
    positive = (base_ok == len(rows) and gold_agree == len(rows) and leakage == 0
                and all(arms[a]['detections'] == arms[a]['attempts'] for a in detected_arms)
                and arms['A-COMPROMISE-FULL']['signature_layer_detections'] == 0
                and arms['A-COMPROMISE-FULL']['chain_as_science_false_promotions'] > 0
                and crypto_false == 0 and chain_false_reject == 0 and disp_false_reject == 0
                and real_false_promote == 0)
    receipt = {'schema': 'P15.AttestationCompositionChainResult.v2',
               'protocol_sha256': hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
               'case_count': len(rows), 'chain_length': len(ROLES), 'arms': arms,
               'base_chain_verification_rate': base_ok / len(rows),
               'chain_plus_sei_gold_agreement_count': gold_agree,
               'scientific_field_leakage_count': leakage,
               'chain_crypto_only_false_scientific_success_count': crypto_false,
               'chain_as_science_false_promotion_count_total': misuse_total,
               'valid_workload_case_count': len(valid_ids),
               'chain_layer_false_rejection_count': chain_false_reject,
               'disposition_false_rejection_count': disp_false_reject,
               'real_false_promotion_count': real_false_promote,
               'compromise_full_boundary': 'composed-signature validity is evidence about the key set, not about key custody or fact truth; chain_plus_sei inherits key custody as an unregistered premise',
               'compromise_case_rows': comp_rows,
               'observed_environment': {'python_version': platform.python_version(),
                                        'cryptography_version': CRYPTOGRAPHY_VERSION,
                                        'machine': platform.machine()},
               'rows': rows,
               'terminal': 'P15_ATTESTATION_COMPOSITION_V2_SUPPORTED' if positive else 'P15_ATTESTATION_COMPOSITION_V2_GATE_NOT_MET'}
    raw = json.dumps(receipt, sort_keys=True, separators=(',', ':')).encode()
    receipt['receipt_sha256'] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(receipt, indent=2, sort_keys=True))
    assert positive, {k: receipt[k] for k in ('arms', 'terminal')}
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
