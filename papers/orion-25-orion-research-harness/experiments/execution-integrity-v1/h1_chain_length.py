#!/usr/bin/env python3
"""ORION-25 H1: does chain-layer detection improve with chain length k, at fixed d?

The discriminator in PROTOCOL.json:
  M1 (chain length)  predicts detection IMPROVES with k at fixed d
  M2 (trust-domain)  predicts detection is FLAT in k at fixed d, and steps with d

This varies k over STRICT SUBSETS of the frozen roles -- ROLES[:1], ROLES[:2], ROLES[:3].
No new role is invented; PROTOCOL.json forbids padding k with filler, and k=5 is
therefore still out of scope. Trust-domain count is fixed at d=1 throughout: every role
key is derived in one process from one seed family.

The frozen role_key / role_public_hex / canonical / link_digest / facts_for are imported
and reused, so the cryptography and payload bytes are the frozen ones.

verify_chain() in the frozen runner is hardcoded to len(ROLES) and indexes chain[2] for
its publication cross-check, so it cannot serve a k-varying test. The verifier here
checks the CHAIN LAYER only -- length, role order, digest chaining, expected key,
signature. That is precisely the layer H1 asks about. The k=3-only semantic cross-check
is out of scope and is not counted in either direction.

  0 = measured
  3 = could not check
"""
import copy, hashlib, importlib.util, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
RUNNER = HERE / "run_attestation_composition_v2.py"


def load():
    spec = importlib.util.spec_from_file_location("frozen_runner", RUNNER)
    m = importlib.util.module_from_spec(spec); sys.modules["frozen_runner"] = m
    spec.loader.exec_module(m); return m


def compose_k(M, cid, e, k):
    running, links = M.GENESIS, []
    for role in M.ROLES[:k]:
        payload = {"role": role, "previous_digest": running, "facts": M.facts_for(role, cid, e)}
        priv = M.role_key(role, cid)
        sig = priv.sign(M.canonical(payload))
        link = {"payload": payload, "signature": sig.hex(),
                "public_key_hex": priv.public_key().public_bytes(
                    M.Encoding.Raw, M.PublicFormat.Raw).hex()}
        links.append(link); running = M.link_digest(link)
    return links


def verify_k(M, chain, cid, k):
    """Chain-layer verification only, generalised to k."""
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    if len(chain) != k: return False, "length"
    running = M.GENESIS
    for i, link in enumerate(chain):
        p = link["payload"]
        if p["role"] != M.ROLES[i]: return False, "role-order"
        if p["previous_digest"] != running: return False, "chaining"
        if link["public_key_hex"] != M.role_public_hex(M.ROLES[i], cid):
            return False, "key-substitution"
        try:
            Ed25519PublicKey.from_public_bytes(bytes.fromhex(link["public_key_hex"])).verify(
                bytes.fromhex(link["signature"]), M.canonical(p))
        except (InvalidSignature, ValueError):
            return False, "signature"
        running = M.link_digest(link)
    return True, "ok"


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
    if len(cases) < 2:
        print(json.dumps({"terminal": "CANNOT_CHECK_TOO_FEW_CASES"})); return 3

    def attacks(chain, k, cid, other_chain):
        out = {}
        c = copy.deepcopy(chain); s = c[k // 2]["signature"]
        c[k // 2]["signature"] = ("0" if s[0] != "0" else "1") + s[1:]
        out["A_SIGNATURE_FLIP"] = c
        c = copy.deepcopy(chain); h = c[k // 2]["public_key_hex"]
        c[k // 2]["public_key_hex"] = h[2:4] + h[0:2] + h[4:]
        out["A_KEY_SUBSTITUTION"] = c
        c = copy.deepcopy(chain); c = c[:-1] if k > 1 else []
        out["A_LINK_DROP"] = c
        if k >= 2:
            c = copy.deepcopy(chain); c[0], c[1] = c[1], c[0]
            out["A_REORDER"] = c
        c = copy.deepcopy(chain); c[k // 2] = copy.deepcopy(other_chain[min(k // 2, len(other_chain) - 1)])
        out["A_SPLICE_FOREIGN_LINK"] = c
        c = copy.deepcopy(chain)
        c[k // 2]["payload"]["facts"] = {"tampered": True}
        out["A_FACT_TAMPER"] = c
        return out

    per_k = {}
    for k in (1, 2, 3):
        det = tot = 0
        clean_ok = 0
        detail = {}
        for idx, (cid, e) in enumerate(cases):
            chain = compose_k(M, cid, e, k)
            ok, _ = verify_k(M, chain, cid, k)
            clean_ok += ok                      # no-alarm control
            ocid, oe = cases[(idx + 1) % len(cases)]
            other = compose_k(M, ocid, oe, k)
            for name, bad in attacks(chain, k, cid, other).items():
                good, _reason = verify_k(M, bad, cid, k)
                tot += 1; det += (not good)
                d = detail.setdefault(name, {"n": 0, "detected": 0})
                d["n"] += 1; d["detected"] += (not good)
        per_k[k] = {"attacks": tot, "detected": det,
                    "detection_rate": det / tot if tot else None,
                    "clean_chains_verified": clean_ok, "clean_chains_total": len(cases),
                    "by_attack": detail}

    rates = [per_k[k]["detection_rate"] for k in (1, 2, 3)]
    improves = all(rates[i] < rates[i + 1] - 1e-12 for i in range(2))
    flat = max(rates) - min(rates) < 1e-12
    if any(per_k[k]["clean_chains_verified"] != per_k[k]["clean_chains_total"] for k in (1, 2, 3)):
        print(json.dumps({"terminal": "CANNOT_CHECK_CLEAN_CHAIN_FAILED_VERIFICATION"})); return 3

    print(json.dumps({
        "schema": "orion.orion25.h1-chain-length.v1",
        "successor_id": "ORION25.EXECUTION_INTEGRITY.v1",
        "hypothesis": "H1: does chain-layer detection improve with k at fixed d?",
        "authority": "MEASUREMENT_ONLY", "scientific_authority_delta": "NONE",
        "d_trust_domains": 1,
        "k_values_tested": [1, 2, 3],
        "k_5_out_of_scope": ("would require two NEW attestation roles with real semantics; "
                             "PROTOCOL.json forbids padding k with filler roles"),
        "roles_used": {str(k): list(M.ROLES[:k]) for k in (1, 2, 3)},
        "per_k": per_k,
        "detection_rates": {str(k): per_k[k]["detection_rate"] for k in (1, 2, 3)},
        "M1_chain_length_predicts_improvement": improves,
        "M2_trust_domain_predicts_flat": flat,
        "verdict": ("M1_SUPPORTED__DETECTION_IMPROVES_WITH_K" if improves else
                    "M2_SUPPORTED__DETECTION_FLAT_IN_K" if flat else
                    "NEITHER__NON_MONOTONIC"),
        "scope": ("Chain-layer detection only: length, role order, chaining, expected key, "
                  "signature. The frozen verify_chain is hardcoded to len(ROLES) and "
                  "indexes chain[2], so it cannot serve a k-varying test; its k=3-only "
                  "publication cross-check is excluded and not counted in either "
                  "direction. Does not address the full-compromise regime, where the "
                  "committed receipt already records 6 chain_as_science false promotions."),
        "terminal": "H1_MEASURED_FOR_K_1_2_3_AT_D_1",
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
