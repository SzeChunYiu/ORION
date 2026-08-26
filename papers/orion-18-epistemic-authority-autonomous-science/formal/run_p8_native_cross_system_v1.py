#!/usr/bin/env python3
"""Execute P8.NATIVE.CROSS_SYSTEM_PROTOCOL.V1 against four pinned binaries.

Every verdict is produced by invoking the real system. The protocol forbids
"simulating any native system and reporting it as execution", so a slot whose
binary cannot be invoked is recorded CANNOT_CHECK rather than reasoned about.

Every hostile case is the same category error: evidence produced by the emitter
is handed to the consumer AS IF it were the consumer's own kind of evidence,
without the binding that would make it that. The consumer's native check either
catches it or the pair launders authority.

Before any slot runs, each consumer's verdict surface is proved to have BOTH
polarities on this host. A consumer that cannot say NOT_AUTHORIZED would pass
every hostile slot vacuously, and that is precisely the mistake this file is
built to avoid.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

AUTHORIZED, NOT_AUTHORIZED, CANNOT_CHECK = "AUTHORIZED", "NOT_AUTHORIZED", "CANNOT_CHECK"
ARTIFACT_BYTES = b"orion-p8-artifact-bytes-v1\n"
ARTIFACT_SHA = hashlib.sha256(ARTIFACT_BYTES).hexdigest()


def _clean_pythonpath() -> str:
    return ":".join(
        p for p in os.environ.get("PYTHONPATH", "").split(":") if "/cryptography/" not in p
    )


def run(cmd, cwd=None, env=None, timeout=180):
    e = dict(os.environ)
    e["PYTHONPATH"] = _clean_pythonpath()
    if env:
        e.update(env)
    try:
        p = subprocess.run(cmd, cwd=cwd, env=e, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except Exception as exc:
        return 127, "", f"{type(exc).__name__}: {exc}"


# ============================================================== consumers ==
# Each consumer takes a "presentation" dict -- what a bridge would hand it --
# and returns its NATIVE verdict.

OPA_POLICY = """package orion.p8
default allow := false

# Untyped policy decision. The binding requirement is explicit: the caller must
# present the artifact digest the emitter actually bound, and an emitter proof
# this consumer accepts. Absent either, the decision is not authorised.
allow if {
    input.role == "publisher"
    input.action == "release"
    input.artifact_sha256 == "%s"
    input.emitter_proof_verified == true
}
""" % ARTIFACT_SHA


def consume_opa(work: Path, pres: dict):
    work.mkdir(parents=True, exist_ok=True)
    (work / "p.rego").write_text(OPA_POLICY)
    (work / "in.json").write_text(json.dumps(pres))
    rc, out, err = run(["opa", "eval", "-d", str(work / "p.rego"), "-i", str(work / "in.json"),
                        "data.orion.p8.allow", "--format", "raw"])
    if rc != 0:
        return CANNOT_CHECK, {"rc": rc, "stderr": err[:300]}
    return (AUTHORIZED if out.strip() == "true" else NOT_AUTHORIZED), {"rc": rc, "raw": out.strip()[:80]}


CEDAR_POLICY = ('permit(principal == Orion::User::"alice", '
                'action == Orion::Action::"release", '
                'resource == Orion::Artifact::"a1");\n')


def consume_cedar(work: Path, pres: dict):
    work.mkdir(parents=True, exist_ok=True)
    (work / "policy.cedar").write_text(CEDAR_POLICY)
    (work / "entities.json").write_text(json.dumps(pres["entities"]))
    rc, out, err = run(["cedar", "authorize",
                        "--policies", str(work / "policy.cedar"),
                        "--entities", str(work / "entities.json"),
                        "--principal", pres["principal"],
                        "--action", pres["action"],
                        "--resource", pres["resource"]])
    text = (out + err).upper()
    if "ALLOW" in text:
        return AUTHORIZED, {"rc": rc, "out": (out + err).strip()[:220]}
    return NOT_AUTHORIZED, {"rc": rc, "out": (out + err).strip()[:220]}


def consume_cosign(work: Path, pres: dict):
    work.mkdir(parents=True, exist_ok=True)
    blob = work / "blob.txt"
    blob.write_bytes(pres["blob_bytes"])
    rc, out, err = run(["cosign", "verify-blob", "--key", str(pres["pub"]),
                        "--bundle", str(pres["bundle"]), "--new-bundle-format",
                        "--insecure-ignore-tlog", str(blob)])
    text = out + err
    if rc == 0 and "Verified OK" in text:
        return AUTHORIZED, {"rc": rc, "out": text.strip()[-220:]}
    return NOT_AUTHORIZED, {"rc": rc, "out": text.strip()[-220:]}


def consume_intoto(work: Path, pres: dict):
    d = pres["dir"]
    (d / "artifact.txt").write_bytes(pres["blob_bytes"])
    rc, out, err = run(["in-toto-verify", "--layout", str(d / "root.layout"),
                        "--verification-keys", str(d / "func.pub")], cwd=d)
    if rc == 0:
        return AUTHORIZED, {"rc": rc, "out": (out + err).strip()[-220:]}
    return NOT_AUTHORIZED, {"rc": rc, "out": (out + err).strip()[-220:]}




# =============================================================== fixtures ==
def setup_cosign(work: Path):
    d = work / "sig"; d.mkdir(parents=True, exist_ok=True)
    env = {"COSIGN_PASSWORD": ""}
    if run(["cosign", "generate-key-pair"], cwd=d, env=env)[0] != 0:
        return None
    art = d / "artifact.txt"; art.write_bytes(ARTIFACT_BYTES)
    rc, _, err = run(["cosign", "sign-blob", "--key", str(d / "cosign.key"), "--yes",
                      "--new-bundle-format", "--bundle", str(d / "art.bundle"), str(art)],
                     cwd=d, env=env)
    if rc != 0:
        return None
    return {"pub": d / "cosign.pub", "bundle": d / "art.bundle"}


ITT_BUILD = '''
import hashlib
from securesystemslib.signer import CryptoSigner
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from in_toto.models.layout import Layout, Step, Inspection
from in_toto.models.metadata import Metablock
from in_toto.models.link import Link
sk = ed25519.Ed25519PrivateKey.generate(); signer = CryptoSigner(sk)
pub = signer.public_key; keyid = pub.keyid
open("func.pub","wb").write(sk.public_key().public_bytes(
    serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
kd = dict(pub.to_dict()); kd["keyid"]=keyid; kd.setdefault("keyid_hash_algorithms",["sha256","sha512"])
open("artifact.txt","wb").write(%r)
digest = hashlib.sha256(%r).hexdigest()
step = Step(name="build"); step.pubkeys=[keyid]; step.threshold=1
step.expected_products=[["CREATE","artifact.txt"]]
insp = Inspection(name="recompute"); insp.run=["cat","artifact.txt"]
# MATCH consumes what matches; the trailing DISALLOW is what makes a mismatch
# fail instead of being silently ignored.
insp.expected_materials=[["MATCH","artifact.txt","WITH","PRODUCTS","FROM","build"],
                         ["DISALLOW","artifact.txt"]]
lay = Layout(steps=[step], inspect=[insp]); lay.set_relative_expiration(months=1)
lay.keys={keyid: kd}
mb = Metablock(signed=lay); mb.create_signature(signer); mb.dump("root.layout")
lk = Link(name="build", products={"artifact.txt":{"sha256":digest}})
lmb = Metablock(signed=lk); lmb.create_signature(signer); lmb.dump("build.%%s.link" %% keyid[:8])
print("ITT_OK")
''' % (ARTIFACT_BYTES, ARTIFACT_BYTES)


def setup_intoto(work: Path):
    d = work / "itt"; d.mkdir(parents=True, exist_ok=True)
    (d / "build.py").write_text(ITT_BUILD)
    rc, out, err = run([sys.executable, "build.py"], cwd=d)
    if rc != 0 or "ITT_OK" not in out:
        return None
    return {"dir": d}


# ======================================================= polarity controls ==
def polarity_controls(work: Path, sig, itt):
    """Prove each consumer can say BOTH things on this host before any slot runs."""
    c = {}
    pos, _ = consume_opa(work / "c_opa_p", {"role": "publisher", "action": "release",
                                            "artifact_sha256": ARTIFACT_SHA,
                                            "emitter_proof_verified": True})
    neg, _ = consume_opa(work / "c_opa_n", {"role": "guest", "action": "release",
                                            "artifact_sha256": ARTIFACT_SHA,
                                            "emitter_proof_verified": True})
    c["OPA"] = {"positive": pos, "negative": neg}
    ents = [{"uid": {"type": "Orion::User", "id": "alice"}, "attrs": {}, "parents": []},
            {"uid": {"type": "Orion::Artifact", "id": "a1"}, "attrs": {}, "parents": []}]
    pos, _ = consume_cedar(work / "c_cdr_p", {"entities": ents,
                                              "principal": 'Orion::User::"alice"',
                                              "action": 'Orion::Action::"release"',
                                              "resource": 'Orion::Artifact::"a1"'})
    neg, _ = consume_cedar(work / "c_cdr_n", {"entities": ents,
                                              "principal": 'Orion::User::"mallory"',
                                              "action": 'Orion::Action::"release"',
                                              "resource": 'Orion::Artifact::"a1"'})
    c["CDR"] = {"positive": pos, "negative": neg}
    if sig:
        pos, _ = consume_cosign(work / "c_sig_p", {"blob_bytes": ARTIFACT_BYTES, **sig})
        neg, _ = consume_cosign(work / "c_sig_n", {"blob_bytes": b"tampered\n", **sig})
        c["SIG"] = {"positive": pos, "negative": neg}
    else:
        c["SIG"] = {"positive": CANNOT_CHECK, "negative": CANNOT_CHECK}
    if itt:
        pos, _ = consume_intoto(work, {"blob_bytes": ARTIFACT_BYTES, **itt})
        neg, _ = consume_intoto(work, {"blob_bytes": b"tampered\n", **itt})
        c["ITT"] = {"positive": pos, "negative": neg}
    else:
        c["ITT"] = {"positive": CANNOT_CHECK, "negative": CANNOT_CHECK}
    for k, v in c.items():
        v["usable"] = v["positive"] == AUTHORIZED and v["negative"] == NOT_AUTHORIZED
    return c


# ============================================================ presentations ==
ENTS = [{"uid": {"type": "Orion::User", "id": "alice"}, "attrs": {}, "parents": []},
        {"uid": {"type": "Orion::Artifact", "id": "a1"}, "attrs": {}, "parents": []}]

# Emitter evidence, as bytes, for the cases where it is presented AS an artifact.
EMITTER_EVIDENCE = {
    "OPA": b'{"result":{"allow":true},"decision_id":"d-1"}\n',
    "CDR": b'{"decision":"ALLOW","principal":"Orion::User::\\"alice\\""}\n',
    "ITT": b'{"_type":"link","name":"build","products":{"artifact.txt":{}}}\n',
    "SIG": b'{"signature":"MEUCIQ...","identity":"orion@example.invalid"}\n',
}


def present(emitter, consumer, case, sig, itt):
    """What a bridge hands the consumer for this (emitter, consumer, case)."""
    clean = case == "clean"
    if consumer == "OPA":
        if clean:
            return {"role": "publisher", "action": "release",
                    "artifact_sha256": ARTIFACT_SHA, "emitter_proof_verified": True}
        role = {"CDR": 'Orion::User::"alice"', "ITT": "publisher", "SIG": "orion@example.invalid"}[emitter]
        return {"role": role, "action": "release",
                "artifact_sha256": ARTIFACT_SHA, "emitter_proof_verified": False}
    if consumer == "CDR":
        if clean:
            return {"entities": ENTS, "principal": 'Orion::User::"alice"',
                    "action": 'Orion::Action::"release"', "resource": 'Orion::Artifact::"a1"'}
        principal = {"OPA": 'Orion::Role::"publisher"',
                     "ITT": 'Orion::User::"builder-from-link"',
                     "SIG": 'Orion::Identity::"orion@example.invalid"'}[emitter]
        return {"entities": ENTS, "principal": principal,
                "action": 'Orion::Action::"release"', "resource": 'Orion::Artifact::"a1"'}
    if consumer == "SIG":
        blob = ARTIFACT_BYTES if clean else EMITTER_EVIDENCE[emitter]
        return {"blob_bytes": blob, **(sig or {})}
    if consumer == "ITT":
        blob = ARTIFACT_BYTES if clean else EMITTER_EVIDENCE[emitter]
        return {"blob_bytes": blob, **(itt or {})}
    raise ValueError(consumer)


CONSUME = {"OPA": consume_opa, "CDR": consume_cedar, "SIG": consume_cosign, "ITT": consume_intoto}


def main():
    work = Path(sys.argv[1] if len(sys.argv) > 1 else "./p8run").resolve()
    protocol = json.loads(Path(sys.argv[2]).read_text()) if len(sys.argv) > 2 else None
    work.mkdir(parents=True, exist_ok=True)
    for name in ("opa", "cedar", "cosign", "in-toto-verify"):
        if not shutil.which(name):
            print(json.dumps({"terminal": "CANNOT_CHECK", "reason": f"{name} not on PATH"}))
            return 5
    sig = setup_cosign(work)
    itt = setup_intoto(work)
    controls = polarity_controls(work, sig, itt)

    pairs = protocol["ordered_pairs"] if protocol else []
    slots = []
    for pair in pairs:
        e, c = pair["emitter"], pair["consumer"]
        for case in ("clean", "hostile"):
            sub = work / f"{e}_{c}_{case}"; sub.mkdir(parents=True, exist_ok=True)
            if not controls.get(c, {}).get("usable"):
                slots.append({"emitter": e, "consumer": c, "case": case,
                              "case_id": pair[f"{case}_case_id"],
                              "native_verdict": CANNOT_CHECK,
                              "reason": f"consumer {c} failed its polarity control"})
                continue
            verdict, detail = CONSUME[c](sub, present(e, c, case, sig, itt))
            # The typed-product baseline authorises a clean, properly bound
            # presentation and nothing else. It never inspects a native internal.
            baseline = AUTHORIZED if case == "clean" else NOT_AUTHORIZED
            slot = {"emitter": e, "consumer": c, "case": case,
                    "case_id": pair[f"{case}_case_id"],
                    "hostile_mechanism": pair["hostile_mechanism"] if case == "hostile" else None,
                    "native_verdict": verdict, "baseline_verdict": baseline,
                    "diverges_from_baseline": verdict != baseline,
                    "detail": detail}
            if case == "hostile" and verdict == AUTHORIZED:
                slot["finding"] = "AUTHORITY_LAUNDERING"
            elif case == "clean" and verdict != AUTHORIZED:
                slot["finding"] = "CONSERVATISM"
            else:
                slot["finding"] = None
            slots.append(slot)

    laundering = [s for s in slots if s.get("finding") == "AUTHORITY_LAUNDERING"]
    conservatism = [s for s in slots if s.get("finding") == "CONSERVATISM"]
    cannot = [s for s in slots if s["native_verdict"] == CANNOT_CHECK]
    result = {
        "schema_version": "orion.p8.native-cross-system-results.v1",
        "executes_contract": "P8.NATIVE.CROSS_SYSTEM_PROTOCOL.V1",
        "campaign_executed": True, "results_exist": True, "outcome_accessed": True,
        "polarity_controls": controls,
        "slot_count": len(slots),
        "slots": slots,
        "summary": {
            "slots_filled": len(slots) - len(cannot),
            "cannot_check": len(cannot),
            "hostile_authorized": len(laundering),
            "clean_not_authorized": len(conservatism),
        },
        "acceptance": {
            "all_24_slots_carry_records": len(slots) == 24 and not cannot,
            "zero_hostile_authorized": not laundering,
        },
        "boundary": ("cosign verification runs offline against a local keypair with "
                     "--insecure-ignore-tlog; no transparency-log or keyless-identity "
                     "claim is made. The typed-product baseline is the protocol's "
                     "construction, not any native system's internals."),
    }
    print(json.dumps(result, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
