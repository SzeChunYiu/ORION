#!/usr/bin/env python3
"""ORION25.INDEPENDENT_TRUST_DOMAIN_LAW.v1 -- exhaustive (alpha, C) sweep.

Tests Theorem T: an adversary compromising exactly the domains in C can forge an accepted
chain IFF supp(alpha) is a subset of C.

Sweeps EVERY assignment alpha of the three frozen roles to d domains and EVERY subset C,
so both directions of the iff are exercised and collapsing assignments (d_eff < d) are
included -- without those, corollary T2 is untested.

No new attestation role is invented. Uses the frozen runner and real receipts.

  0 = measured    3 = could not check
"""
import importlib.util, itertools, json, pathlib, sys
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.exceptions import InvalidSignature

HERE = pathlib.Path(__file__).resolve().parent
SIB = HERE.parent / "execution-integrity-v1"
RUNNER = HERE.parent.parent / "top_tier" / "run_attestation_composition_v2.py"
RECEIPTS = HERE.parent.parent / "top_tier" / "p15_real_workflow_receipts_v1.json"
DOMAINS = [1, 2, 3]


def load():
    spec = importlib.util.spec_from_file_location("frozen_runner", RUNNER)
    m = importlib.util.module_from_spec(spec); sys.modules["frozen_runner"] = m
    spec.loader.exec_module(m); return m


def pub_hex(priv):
    return priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()


def make_keys(M, cid, alpha, d):
    """One key per role. d == 1 reproduces the frozen shared-seed scheme exactly;
    d > 1 uses independent randomness so no domain can derive another's secret."""
    if d == 1:
        return {r: M.role_key(r, cid) for r in M.ROLES}
    return {r: Ed25519PrivateKey.generate() for r in M.ROLES}


def compose(M, cid, e, keys, alpha):
    running, links = M.GENESIS, []
    for role in M.ROLES:
        priv = keys[role]
        payload = {"role": role, "previous_digest": running,
                   "facts": M.facts_for(role, cid, e)}
        link = {"payload": payload, "signature": priv.sign(M.canonical(payload)).hex(),
                "domain": alpha[role], "public_key_hex": pub_hex(priv)}
        links.append(link); running = M.link_digest(link)
    return links


def verify(M, chain, expected_pub):
    if len(chain) != len(M.ROLES):
        return False
    running = M.GENESIS
    for i, link in enumerate(chain):
        p = link["payload"]
        if p["role"] != M.ROLES[i] or p["previous_digest"] != running:
            return False
        if link["public_key_hex"] != expected_pub[M.ROLES[i]]:
            return False
        try:
            Ed25519PublicKey.from_public_bytes(bytes.fromhex(link["public_key_hex"])).verify(
                bytes.fromhex(link["signature"]), M.canonical(p))
        except (InvalidSignature, ValueError):
            return False
        running = M.link_digest(link)
    return True


def forge(M, cid, e, keys, alpha, C):
    """Adversary rewrites the chain to a favourable claim, signing each role with that
    role's key when its domain is compromised and with a rogue key otherwise."""
    running, links = M.GENESIS, []
    for role in M.ROLES:
        payload = {"role": role, "previous_digest": running,
                   "facts": {"tampered_claim": True} if role == M.ROLES[0]
                            else M.facts_for(role, cid, e)}
        priv = keys[role] if alpha[role] in C else Ed25519PrivateKey.generate()
        link = {"payload": payload, "signature": priv.sign(M.canonical(payload)).hex(),
                "domain": alpha[role], "public_key_hex": pub_hex(priv)}
        links.append(link); running = M.link_digest(link)
    return links


def main() -> int:
    if not RUNNER.exists() or not RECEIPTS.exists():
        print(json.dumps({"terminal": "T4_CANNOT_CHECK_ATTACK_INERT",
                          "reason": "frozen runner or receipts absent"}, indent=2))
        return 3
    M = load()
    cases = []
    for c in json.loads(RECEIPTS.read_text())["receipts"]:
        try:
            e, _ = M.norm_real(c); cases.append((c["id"], e))
        except Exception:
            pass
    if not cases:
        print(json.dumps({"terminal": "T4_CANNOT_CHECK_ATTACK_INERT",
                          "reason": "no usable receipts"}, indent=2))
        return 3

    cells, sufficiency_fail, necessity_fail = [], [], []
    c1_elig = c1_ok = 0
    c2_checked = c2_ok = 0
    c3_elig = c3_ok = 0
    collapse_seen = 0

    for d in DOMAINS:
        for assign in itertools.product(range(d), repeat=len(M.ROLES)):
            alpha = dict(zip(M.ROLES, assign))
            supp = set(alpha.values())
            d_eff = len(supp)
            if d > 1 and d_eff == 1:
                collapse_seen += 1
            for rC in range(d + 1):
                for C in itertools.combinations(range(d), rC):
                    C = set(C)
                    predicted = supp.issubset(C)
                    for cid, e in cases:
                        keys = make_keys(M, cid, alpha, d)
                        pub = {r: pub_hex(k) for r, k in keys.items()}

                        # C2: the honest chain must always verify
                        c2_checked += 1
                        if verify(M, compose(M, cid, e, keys, alpha), pub):
                            c2_ok += 1
                        else:
                            print(json.dumps({"terminal": "T4_CANNOT_CHECK_ATTACK_INERT",
                                              "reason": "honest chain rejected",
                                              "d": d, "alpha": alpha, "case": cid}, indent=2))
                            return 3

                        accepted = verify(M, forge(M, cid, e, keys, alpha, C), pub)
                        cells.append({"d": d, "d_eff": d_eff, "alpha": alpha,
                                      "C": sorted(C), "predicted": predicted,
                                      "forged_accepted": accepted})
                        if predicted:
                            c1_elig += 1
                            if accepted:
                                c1_ok += 1
                            else:
                                sufficiency_fail.append(cells[-1])
                        else:
                            if accepted:
                                necessity_fail.append(cells[-1])
                        if not C:
                            c3_elig += 1
                            if not accepted:
                                c3_ok += 1

    c1_pass = c1_elig > 0 and c1_ok == c1_elig
    c2_pass = c2_checked > 0 and c2_ok == c2_checked
    c3_pass = c3_elig > 0 and c3_ok == c3_elig
    c4_pass = collapse_seen > 0

    if not (c1_pass and c2_pass and c4_pass):
        terminal, rc = "T4_CANNOT_CHECK_ATTACK_INERT", 3
    elif sufficiency_fail:
        terminal, rc = "T2_LAW_FAILS_SUFFICIENCY", 0
    elif necessity_fail:
        terminal, rc = "T3_LAW_FAILS_NECESSITY", 0
    else:
        terminal, rc = "T1_LAW_HOLDS_EXACTLY", 0

    agree = sum(1 for c in cells if c["predicted"] == c["forged_accepted"])
    print(json.dumps({
        "schema": "ORION.ORION25.IndependentTrustDomainLaw.Result.v1",
        "protocol_identity": "ORION25.INDEPENDENT_TRUST_DOMAIN_LAW.v1",
        "authority": "MEASUREMENT_ONLY", "scientific_authority_delta": "NONE",
        "cases": len(cases), "roles": list(M.ROLES), "domains_swept": DOMAINS,
        "cells_total": len(cells), "cells_matching_theorem_T": agree,
        "sufficiency_failures": len(sufficiency_fail),
        "necessity_failures": len(necessity_fail),
        "failure_examples": (sufficiency_fail[:3] + necessity_fail[:3]),
        "controls": {
            "C1_planted_full_compromise_must_forge": {"eligible": c1_elig, "forged": c1_ok, "passed": c1_pass},
            "C2_honest_chain_always_accepted": {"checked": c2_checked, "accepted": c2_ok, "passed": c2_pass},
            "C3_empty_compromise_never_forges": {"eligible": c3_elig, "clean": c3_ok, "passed": c3_pass},
            "C4_collapse_case_present": {"collapsing_assignments": collapse_seen, "passed": c4_pass,
                                         "note": "d > 1 with d_eff == 1; without these T2 is untested"}},
        "custody_limit": ("Domain independence here is CRYPTOGRAPHIC only. Every domain "
                          "remains under this programme's custody, so per #1649's stop rule "
                          "general trust-domain resilience is NOT claimed."),
        "terminal": terminal,
        "promotion_status": ("LAW_ESTABLISHED_UNDER_CRYPTOGRAPHIC_INDEPENDENCE__PROMOTION_NOT_EARNED"
                             if terminal == "T1_LAW_HOLDS_EXACTLY" else "PROMOTION_FAILED"),
    }, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
