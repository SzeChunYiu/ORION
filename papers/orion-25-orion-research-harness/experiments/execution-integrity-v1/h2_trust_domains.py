#!/usr/bin/env python3
"""ORION-25 H2: does resistance to compromise step with trust-domain count d?

M1 (chain length)  : security comes from k. Compromise resistance should not depend on d.
M2 (trust-domain)  : security comes from d. Compromising j of d domains should forge only
                     the roles those domains hold; the rest still fail verification.

WHAT A TRUST DOMAIN IS HERE. The frozen runner derives every role key from a shared
deterministic seed, sha256(b"P15-...-KEY-" + role + cid). Anyone who can run the runner
can derive EVERY role key, so all k roles live in ONE trust domain: d = 1 by
construction, whatever k is.

d > 1 is modelled by generating each domain's key from independent randomness
(os.urandom via Ed25519PrivateKey.generate), so no party can derive another domain's
private key. That is what domain independence means cryptographically. Physical
separation is one implementation of it, and the cross-site replay result
(CROSS_SITE_REPLAY_RESULT_V1.json) demonstrates the composition already runs unchanged
across two hosts with different interpreters and crypto versions.

THREAT MODEL, stated before the numbers: an attacker compromises j domains, learns those
domains' private keys, and rewrites the whole chain to a favourable claim. A case is a
FALSE PROMOTION if the verifier still accepts the rewritten chain.

No new attestation role is invented; roles remain the frozen three, and k is held at 3.

  0 = measured    3 = could not check
"""
import copy, importlib.util, json, pathlib, sys
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.exceptions import InvalidSignature

HERE = pathlib.Path(__file__).resolve().parent
RUNNER = HERE / "run_attestation_composition_v2.py"


def load():
    spec = importlib.util.spec_from_file_location("frozen_runner", RUNNER)
    m = importlib.util.module_from_spec(spec); sys.modules["frozen_runner"] = m
    spec.loader.exec_module(m); return m


def domain_keys(M, cid, d):
    """Assign each of the 3 roles to one of d domains.

    d == 1 reproduces the frozen scheme exactly: every key derived from the shared seed.
    d  > 1 gives each domain an independently generated key that nobody else can derive.
    """
    if d == 1:
        return {r: (M.role_key(r, cid), 0) for r in M.ROLES}
    gen = {}
    out = {}
    for i, r in enumerate(M.ROLES):
        dom = i % d
        if dom not in gen:
            gen[dom] = {}
        if r not in gen[dom]:
            gen[dom][r] = Ed25519PrivateKey.generate()   # independent randomness
        out[r] = (gen[dom][r], dom)
    return out


def compose(M, cid, e, keys):
    running, links = M.GENESIS, []
    for role in M.ROLES:
        priv, dom = keys[role]
        payload = {"role": role, "previous_digest": running, "facts": M.facts_for(role, cid, e)}
        sig = priv.sign(M.canonical(payload))
        link = {"payload": payload, "signature": sig.hex(), "domain": dom,
                "public_key_hex": priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()}
        links.append(link); running = M.link_digest(link)
    return links


def verify(M, chain, expected_pub):
    """Verify against the PUBLISHED public keys -- the verifier's fixed reference."""
    if len(chain) != len(M.ROLES): return False
    running = M.GENESIS
    for i, link in enumerate(chain):
        p = link["payload"]
        if p["role"] != M.ROLES[i] or p["previous_digest"] != running: return False
        if link["public_key_hex"] != expected_pub[M.ROLES[i]]: return False
        try:
            Ed25519PublicKey.from_public_bytes(bytes.fromhex(link["public_key_hex"])).verify(
                bytes.fromhex(link["signature"]), M.canonical(p))
        except (InvalidSignature, ValueError):
            return False
        running = M.link_digest(link)
    return True


def main() -> int:
    if not RUNNER.exists():
        print(json.dumps({"terminal": "CANNOT_CHECK_RUNNER_ABSENT"})); return 3
    M = load()
    real = json.loads((HERE / "p15_real_workflow_receipts_v1.json").read_text())["receipts"]
    cases = []
    for c in real:
        try:
            e, _ = M.norm_real(c); cases.append((c["id"], e))
        except Exception:
            pass
    if not cases:
        print(json.dumps({"terminal": "CANNOT_CHECK_NO_CASES"})); return 3

    forged_facts = {"tampered_claim": True}
    per_d = {}
    for d in (1, 2, 3):
        rows = []
        for cid, e in cases:
            keys = domain_keys(M, cid, d)
            pub = {r: k.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()
                   for r, (k, _) in keys.items()}
            clean = compose(M, cid, e, keys)
            if not verify(M, clean, pub):
                print(json.dumps({"terminal": "CANNOT_CHECK_CLEAN_CHAIN_REJECTED",
                                  "d": d, "case": cid})); return 3
            # attacker compromises domain 0 only
            comp = {dom for r, (k, dom) in keys.items() if dom == 0}
            running, forged = M.GENESIS, []
            ok_forge = True
            for role in M.ROLES:
                priv, dom = keys[role]
                payload = {"role": role, "previous_digest": running,
                           "facts": forged_facts if role == M.ROLES[0] else M.facts_for(role, cid, e)}
                if dom in comp:
                    sig = priv.sign(M.canonical(payload))          # attacker holds this key
                    pk = priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()
                else:
                    rogue = Ed25519PrivateKey.generate()           # must fabricate
                    sig = rogue.sign(M.canonical(payload))
                    pk = rogue.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()
                    ok_forge = False
                link = {"payload": payload, "signature": sig.hex(),
                        "public_key_hex": pk, "domain": dom}
                forged.append(link); running = M.link_digest(link)
            accepted = verify(M, forged, pub)
            rows.append({"case": cid, "domains_compromised": 1, "of": d,
                         "roles_attacker_could_sign": sum(1 for r in M.ROLES if keys[r][1] in comp),
                         "forged_chain_accepted": accepted})
        fp = sum(1 for r in rows if r["forged_chain_accepted"])
        per_d[d] = {"cases": len(rows), "false_promotions": fp,
                    "false_promotion_rate": fp / len(rows), "detail": rows}

    rates = [per_d[d]["false_promotion_rate"] for d in (1, 2, 3)]
    steps = rates[0] > rates[1] or rates[1] > rates[2]
    flat = max(rates) - min(rates) < 1e-12
    print(json.dumps({
        "schema": "orion.orion25.h2-trust-domains.v1",
        "successor_id": "ORION25.EXECUTION_INTEGRITY.v1",
        "hypothesis": "H2: does compromise resistance step with trust-domain count d, at fixed k?",
        "authority": "MEASUREMENT_ONLY", "scientific_authority_delta": "NONE",
        "k_fixed": len(M.ROLES), "roles": list(M.ROLES),
        "threat_model": ("attacker compromises 1 domain, learns its private keys, and "
                         "rewrites the whole chain to a favourable claim; a case is a "
                         "false promotion if the verifier still accepts it"),
        "trust_domain_definition": ("d=1 reproduces the frozen shared-seed derivation, so "
                                    "one compromise yields every role key. d>1 gives each "
                                    "domain independently generated keys nobody else can "
                                    "derive."),
        "per_d": per_d,
        "false_promotion_rate_by_d": {str(d): per_d[d]["false_promotion_rate"] for d in (1, 2, 3)},
        "M1_predicts_no_d_dependence": flat,
        "M2_predicts_steps_with_d": steps,
        "verdict": ("M2_SUPPORTED__RESISTANCE_STEPS_WITH_D" if steps and not flat else
                    "M1_SUPPORTED__NO_D_DEPENDENCE" if flat else "NEITHER"),
        "limits": ("Domain independence is modelled by independent key generation, which "
                   "is the cryptographic content of the property. Physical separation is "
                   "one implementation; CROSS_SITE_REPLAY_RESULT_V1.json shows the "
                   "composition runs unchanged across two hosts. Single-domain compromise "
                   "only; n=" + str(len(cases)) + " real receipts; k held at 3."),
        "terminal": "H2_MEASURED_FOR_D_1_2_3_AT_K_3",
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
