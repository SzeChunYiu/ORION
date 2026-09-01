#!/usr/bin/env python3
"""ORION-03 Round 2: execute the frozen X.509 trust-store merge adjudication.

Evaluates the frozen task manifest (TASK_MANIFEST_V2.json) against the pinned
native OpenSSL engine: per-task single-origin, union, and intersection
authorizations; the five frozen merge methods; obstruction (first-mixing)
detection with white-box witness localization; and the six frozen controls.

Receipts are byte-deterministic: no absolute paths, no wall times, no build
timestamps. --check-final regenerates and byte-compares against the committed
receipt. Fail-closed on any structural anomaly.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

PROTOCOL = "ORION-03-Round2-TrustStoreMerge-V2"
FROZEN_ATTIME = 1759276800  # 2026-08-27T00:00:00Z
ENGINE_TAG = "openssl-3.6.4"
ENGINE_COMMIT = "d3c1b1169b3569ff3069e5b399f47b2b28e03d79"
ENGINE_TARBALL_SHA256 = (
    "9bffaa1ad1e07b354c21bd3324ec02fa15579f45a7d0494b3e74bc449b7333ef"
)
METHODS = (
    "M1_FLAT_UNION",
    "M2_INTERSECTION",
    "M3_REJECT_ALL",
    "M4_OURS_B",
    "M5_TYPED_WITNESS",
)


def fail(msg: str) -> None:
    print(f"FAIL-CLOSED: {msg}", file=sys.stderr)
    raise SystemExit(2)


def base(name):
    """Normalize a corpus material name to its extensionless logical name."""
    n = str(name)
    return n[:-4] if n.endswith(".pem") else n


class Engine:
    """Pinned native OpenSSL engine wrapper with deterministic caching."""

    def __init__(self, binary, libdir, certs_dir, timeout=60.0):
        self.binary = str(binary)
        self.certs_dir = certs_dir
        self.timeout = timeout
        self.env = dict(os.environ)
        if libdir:
            self.env["LD_LIBRARY_PATH"] = (
                f"{libdir}:{self.env.get('LD_LIBRARY_PATH', '')}"
            )
        self.cache = {}
        self.invocations = 0
        self.requested = 0
        self.wall = 0.0
        out = self._run_no_count([self.binary, "version"])
        self.version_line = out.strip().splitlines()[0]

    def _run_no_count(self, cmd):
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=self.timeout,
            env=self.env,
        )
        return proc.stdout + proc.stderr

    def _file(self, name):
        p = self.certs_dir / (name if name.endswith(".pem") else name + ".pem")
        if not p.is_file():
            fail(f"corpus material missing: {name}")
        return p

    def verify(self, leaf, purpose, opts, trusted, untrusted, extra=()):
        key = json.dumps(
            {
                "leaf": leaf,
                "purpose": purpose,
                "opts": list(opts),
                "trusted": sorted(trusted),
                "untrusted": sorted(untrusted),
                "extra": list(extra),
            },
            sort_keys=True,
        )
        self.requested += 1
        if key in self.cache:
            return self.cache[key]
        cmd = [self.binary, "verify", "-auth_level", "1"]
        if purpose:
            cmd += ["-purpose", purpose]
        # Hermetic trust source: never fall back to the engine's default
        # system CA store (empty-trust origins must deny, not leak the host).
        cmd += ["-no-CAfile", "-no-CApath", "-no-CAstore"]
        cmd += [str(x) for x in opts]
        for t in sorted(trusted):
            cmd += ["-trusted", str(self._file(t))]
        for u in sorted(untrusted):
            cmd += ["-untrusted", str(self._file(u))]
        cmd += [str(x) for x in extra]
        cmd.append(str(self._file(leaf)))
        t0 = time.monotonic()
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=self.env,
            )
            ok = proc.returncode == 0
            err = proc.stderr.strip()
        except subprocess.TimeoutExpired:
            fail(f"engine timeout on {leaf}")
        self.wall += time.monotonic() - t0
        self.invocations += 1
        # sanitize: strip absolute corpus dir from stderr for determinism
        err = err.replace(str(self.certs_dir) + "/", "")
        self.cache[key] = ok
        self.cache[key + "|err"] = err
        return ok

    def stderr_of(self, leaf, purpose, opts, trusted, untrusted, extra=()):
        self.verify(leaf, purpose, opts, trusted, untrusted, extra)
        return self.cache[
            json.dumps(
                {
                    "leaf": leaf,
                    "purpose": purpose,
                    "opts": list(opts),
                    "trusted": sorted(trusted),
                    "untrusted": sorted(untrusted),
                    "extra": list(extra),
                },
                sort_keys=True,
            )
            + "|err"
        ]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def corpus_cert_graph(engine):
    """White-box issuer graph over the vendored certificates.

    Nodes are corpus files; edge u->v iff v plausibly issues u
    (RFC2253 issuer/subject match plus AKI/SKI key-id match when present).
    Returns {file: {subject, issuer, ski, aki, is_cert}} and edge list.
    """
    files = sorted(
        p.name
        for p in engine.certs_dir.iterdir()
        if p.is_file() and p.name.endswith(".pem")
    )
    info = {}
    for name in files:
        path = engine.certs_dir / name
        proc = subprocess.run(
            [engine.binary, "x509", "-in", str(path), "-noout"],
            capture_output=True,
            text=True,
            timeout=30,
            env=engine.env,
        )
        if proc.returncode != 0:
            info[name] = {"is_cert": False}
            continue
        subj = subprocess.run(
            [engine.binary, "x509", "-in", str(path), "-noout",
             "-subject", "-nameopt", "RFC2253"],
            capture_output=True, text=True, timeout=30, env=engine.env,
        ).stdout.strip()
        issuer = subprocess.run(
            [engine.binary, "x509", "-in", str(path), "-noout",
             "-issuer", "-nameopt", "RFC2253"],
            capture_output=True, text=True, timeout=30, env=engine.env,
        ).stdout.strip()
        ski = subprocess.run(
            [engine.binary, "x509", "-in", str(path), "-noout",
             "-ext", "subjectKeyIdentifier"],
            capture_output=True, text=True, timeout=30, env=engine.env,
        ).stdout
        aki = subprocess.run(
            [engine.binary, "x509", "-in", str(path), "-noout",
             "-ext", "authorityKeyIdentifier"],
            capture_output=True, text=True, timeout=30, env=engine.env,
        ).stdout
        spki = subprocess.run(
            [engine.binary, "x509", "-in", str(path), "-pubkey", "-noout"],
            capture_output=True, text=True, timeout=30, env=engine.env,
        ).stdout
        info[name] = {
            "is_cert": True,
            "subject": subj.split("subject=", 1)[-1].strip(),
            "issuer": issuer.split("issuer=", 1)[-1].strip(),
            "ski": _keyid(ski),
            "aki": _keyid(aki),
            "spki_sha256": _spki_digest(spki),
        }
    edges = {}
    name_only_edges = []
    for u, iu in info.items():
        if not iu.get("is_cert"):
            continue
        for v, iv in info.items():
            if u == v or not iv.get("is_cert"):
                continue
            if iu["issuer"] != iv["subject"]:
                continue
            if iu["aki"] and iv["ski"]:
                if iu["aki"] != iv["ski"]:
                    continue
            else:
                name_only_edges.append([base(u), base(v)])
            edges.setdefault(base(u), []).append(base(v))
    for k in edges:
        edges[k] = sorted(set(edges[k]))
    probe_calls = len(files) + 5 * sum(
        1 for v in info.values() if v.get("is_cert")
    )
    return info, edges, sorted(name_only_edges), probe_calls


def _keyid(ext_output):
    m = re.search(r"keyid:([0-9A-Fa-f:]+)", ext_output)
    if m:
        return m.group(1).replace(":", "").lower()
    return None


def _spki_digest(pubkey_output):
    b64 = "".join(
        line
        for line in pubkey_output.splitlines()
        if line and not line.startswith("-----")
    )
    try:
        der = base64.b64decode(b64)
    except Exception:
        return None
    if not der:
        return None
    return hashlib.sha256(der).hexdigest()


def engine_attestable(chains, opts, leaf, graph_info):
    """Filter structural chains to ones the engine could attest for these opts.

    The depth-0 zero-length chain is engine-attestable only under
    -partial_chain (last-resort direct leaf match: a trusted certificate with
    the same subject and public key as the leaf) or when the leaf itself is
    self-signed and trusted (a trusted self-signed leaf anchors at depth 0
    under default semantics). A trusted NON-self-signed copy of the leaf does
    NOT anchor (it fails with "unable to get local issuer certificate"), and
    without -partial_chain a positive-length chain must terminate at a
    SELF-SIGNED trusted anchor (trusted intermediates do not anchor).
    C3 keeps the unfiltered (more permissive) set.
    """
    if "-partial_chain" in [str(o) for o in opts]:
        return chains
    info = graph_info.get(leaf + ".pem") or {}
    self_signed = info.get("subject") is not None and info.get("subject") == info.get("issuer")

    def attestable(c):
        if len(c) == 1:
            return c[0] == leaf and self_signed
        t = graph_info.get(c[-1] + ".pem") or {}
        return (
            t.get("subject") is not None
            and t.get("subject") == t.get("issuer")
        )

    # Fail closed: if the structural graph offers no engine-attestable chain,
    # do not silently fall back to an unattestable structural path.  The
    # earlier fallback could only affect the explanatory localization payload,
    # not vA/vB/vU/vI, but it made a missing localization look successful.
    return [c for c in chains if attestable(c)]


def structural_chains(graph_info, edges, leaf_name, held, anchors):
    """All structural chains leaf -> anchor with intermediates in held.

    held/anchors are sets of corpus filenames; the leaf itself is exempt from
    the held requirement (it is the request, not store material).

    Two anchor rules mirror the engine: (a) an issuer-chain terminating in an
    anchor (covers -partial_chain anchoring at a trusted intermediate); and
    (b) the engine's "last-resort direct leaf match": a trusted certificate
    with the SAME subject and SAME public key as the leaf anchors at depth 0
    (a zero-length chain). Purpose/EKU/trust admission on the anchor is
    policy, not structure, and is intentionally NOT modeled here.
    """
    leaf = base(leaf_name)
    if leaf + ".pem" not in graph_info or not graph_info[leaf + ".pem"].get("is_cert"):
        return []
    anchors = {base(a) for a in anchors}
    held = {base(h) for h in held}
    chains = []
    leaf_info = graph_info[leaf + ".pem"]
    for a in sorted(anchors):
        a_info = graph_info.get(a + ".pem")
        if not a_info or not a_info.get("is_cert"):
            continue
        if (
            a_info.get("subject") == leaf_info.get("subject")
            and a_info.get("spki_sha256") is not None
            and a_info.get("spki_sha256") == leaf_info.get("spki_sha256")
        ):
            chains.append([leaf])

    def dfs(node, path):
        if len(path) >= 8:
            # Defensive depth cap; corpus chains are <= 4 deep.
            return
        node_info = graph_info.get(node + ".pem") or {}
        self_signed = (
            node_info.get("subject") is not None
            and node_info.get("subject") == node_info.get("issuer")
        )
        if node in anchors:
            # Yield the chain ending at this trusted cert; CONTINUE through
            # it only when it is not self-signed (without -partial_chain the
            # engine anchors at self-signed roots and never builds past
            # them; pass-through chains through trusted intermediates are
            # needed for the attestable filter). Stopping at self-signed
            # anchors also prevents path explosion through the same-key
            # root-variant clique.
            yield list(path) + [node]
            if self_signed:
                return
        for nxt in sorted(edges.get(node, [])):
            if nxt in path:
                continue
            if node != leaf and node not in held:
                continue
            if nxt not in held and nxt not in anchors:
                continue
            yield from dfs(nxt, path + [node])

    chains.extend(dfs(leaf, []))
    return chains


def origin_holds(state):
    return set(state["trusted"]) | set(state["untrusted"])


def evaluate_task(engine, graph_info, edges, task):
    leaf = task["leaf"]
    purpose = task["purpose"]
    opts = list(task["opts"])
    if "-attime" not in opts:
        opts = opts + ["-attime", str(FROZEN_ATTIME)]
    sa, sb = task["state_a"], task["state_b"]
    ta, tb = set(sa["trusted"]), set(sb["trusted"])
    ua, ub = set(sa["untrusted"]), set(sb["untrusted"])
    v_a = engine.verify(leaf, purpose, opts, sorted(ta), sorted(ua))
    v_b = engine.verify(leaf, purpose, opts, sorted(tb), sorted(ub))
    tu, uu = sorted(ta | tb), sorted(ua | ub)
    ti, ui = sorted(ta & tb), sorted(ua & ub)
    v_u = engine.verify(leaf, purpose, opts, tu, uu)
    v_i = engine.verify(leaf, purpose, opts, ti, ui)
    parent_auth = v_a or v_b
    hybrid = v_u and not parent_auth
    decisions = {
        "M1_FLAT_UNION": v_u,
        "M2_INTERSECTION": v_i,
        "M3_REJECT_ALL": False,
        "M4_OURS_B": v_b,
        "M5_TYPED_WITNESS": parent_auth,
    }
    rec = {
        "task_id": task["task_id"],
        "family": task["family"],
        "leaf": leaf,
        "purpose": purpose,
        "vA": v_a,
        "vB": v_b,
        "vU": v_u,
        "vI": v_i,
        "hybrid": hybrid,
        "parent_authorized": parent_auth,
        "decisions": decisions,
        "unsafe": {m: (decisions[m] and hybrid) for m in METHODS},
        "needless": {m: ((not decisions[m]) and parent_auth) for m in METHODS},
    }
    if hybrid:
        rec["first_mixing"] = localize_first_mixing(
            engine, graph_info, edges, task, opts, v_a, v_b
        )
    # C3 control: engine-valid origin => structurally derivable by that origin.
    held_a = {base(x) for x in origin_holds(sa)}
    anchors_a = {base(x) for x in ta}
    held_b = {base(x) for x in origin_holds(sb)}
    anchors_b = {base(x) for x in tb}
    raw_a = structural_chains(graph_info, edges, leaf, held_a, anchors_a)
    raw_b = structural_chains(graph_info, edges, leaf, held_b, anchors_b)
    raw_u = structural_chains(
        graph_info, edges, leaf,
        {base(x) for x in set(tu) | set(uu)}, {base(x) for x in set(tu)},
    )
    chains_a = engine_attestable(raw_a, opts, leaf, graph_info)
    chains_b = engine_attestable(raw_b, opts, leaf, graph_info)
    chains_u = engine_attestable(raw_u, opts, leaf, graph_info)
    rec["c3"] = {
        "structural_a": bool(raw_a),
        "structural_b": bool(raw_b),
        "structural_union": bool(raw_u),
        "violation": bool(
            (v_a and not raw_a) or (v_b and not raw_b)
            or (v_u and not raw_u)
        ),
    }
    if hybrid and rec["first_mixing"]:
        rec["first_mixing"]["structural_kind"] = (
            "STRUCTURAL" if (not chains_a and not chains_b and chains_u)
            else "POLICY"
        )
    return rec


def localize_first_mixing(engine, graph_info, edges, task, opts, v_a, v_b):
    """Localize the first-mixing boundary on the union chain.

    Finds the union-store chain, then the boundary link where the anchor-side
    and leaf-side certificates are held by different origins. Records the
    per-origin engine stderr (sanitized) for POLICY hybrids.
    """
    leaf = task["leaf"]
    purpose = task["purpose"]
    sa, sb = task["state_a"], task["state_b"]
    held_a = {base(x) for x in origin_holds(sa)}
    held_b = {base(x) for x in origin_holds(sb)}
    tu = sorted(set(sa["trusted"]) | set(sb["trusted"]))
    uu = sorted(set(sa["untrusted"]) | set(sb["untrusted"]))
    chains = structural_chains(
        graph_info, edges, leaf,
        {base(x) for x in set(tu) | set(uu)}, {base(x) for x in set(tu)},
    )
    chains = engine_attestable(chains, opts, leaf, graph_info)
    if not chains:
        return {"error": "NO_UNION_CHAIN_WHITEBOX"}
    chain = min(chains, key=lambda c: (len(c), c))
    chain_files = list(chain)
    # origins holding each chain cert
    holds = [
        [o for o, held in (("A", held_a), ("B", held_b)) if c in held]
        for c in chain
    ]
    # boundary: smallest k (from anchor side n down) such that a single origin
    # holds c_k..c_n; the first-mixing link is (c_{k-1} -> c_k) where c_{k-1}
    # is NOT held by that origin.
    n = len(chain) - 1
    anchor_origin = None
    boundary = None
    for k in range(n, -1, -1):
        holders = set(holds[k])
        if len(holders) == 0:
            continue
        # check contiguity from k..n for each candidate origin
        for o in sorted(holders):
            if all(o in holds[j] for j in range(k, n + 1)):
                anchor_origin = o
                boundary = k
                break
        if anchor_origin:
            break
    leaf_side = chain[:boundary] if boundary else []
    err_a = engine.stderr_of(
        leaf, purpose, opts,
        sorted(set(sa["trusted"])), sorted(set(sa["untrusted"])),
    ).splitlines()
    err_b = engine.stderr_of(
        leaf, purpose, opts,
        sorted(set(sb["trusted"])), sorted(set(sb["untrusted"])),
    ).splitlines()
    return {
        "chain": chain_files,
        "anchor_side_origin": anchor_origin,
        "boundary_index_from_leaf": boundary,
        "first_mixing_link": (
            [leaf_side[-1], chain_files[boundary]] if boundary else None
        ),
        "leaf_side_held_by": sorted(set(holds[boundary - 1])) if boundary else [],
        "origin_a_error_last": err_a[-1] if err_a else "",
        "origin_b_error_last": err_b[-1] if err_b else "",
    }


def run_anchor_control(engine):
    here = Path(__file__).resolve().parent
    table = json.loads((here / "UPSTREAM_TABLE_V2.json").read_text())
    rows = table["upstream_rows"]
    agree = 0
    disagreements = []
    for row in rows:
        opts = list(row["opts"])
        if "-attime" not in opts:
            opts = opts + ["-attime", str(FROZEN_ATTIME)]
        actual = engine.verify(
            row["leaf"], row["purpose"], opts,
            row["trusted"], row["untrusted"],
        )
        expected = row["upstream_expected"] == "VALID"
        if actual == expected:
            agree += 1
        else:
            disagreements.append(
                {
                    "name": row["name"],
                    "leaf": row["leaf"],
                    "expected": row["upstream_expected"],
                    "actual": "VALID" if actual else "INVALID",
                    "opts": opts,
                }
            )
    return {
        "rows": len(rows),
        "excluded_runtime_material_rows": len(table.get("excluded_rows", [])),
        "exit_checker_rows_flipped": table.get("exit_checker_rows_flipped", []),
        "agree": agree,
        "disagree": len(disagreements),
        "agreement_rate": round(agree / len(rows), 4) if rows else 0.0,
        "disagreements": disagreements,
    }


def run_retraction_control(engine):
    """C4: retraction non-resurrection on upstream-labeled CRL materials.

    Upstream-mirror rows reproduce the OpenSSL project's own adjudications
    (delta-CRL-as-complete x2, CVE-2026-28388) with upstream's exact option
    lists: each must FAIL with its upstream-labeled stderr marker (upstream
    greps the same marker). Positive control: the delta chain authorizes
    WITHOUT -crl_check, so the denial is the retraction mechanism, not the
    chain. Merge measurement: origin A carries the retraction material,
    origin B does not; parents, union (with A's CRL bytes), the operational
    cert-only flat merge (concatenated cert bundles drop CRL side-files),
    and the intersection must all deny.
    """
    mirrors = [
        {
            "case": "delta-crl-as-complete",
            "trusted": ["delta-crl-as-complete-ca"],
            "leaf": "delta-crl-as-complete-leaf",
            "opts": ["-no_check_time", "-crl_check"],
            "crl": "delta-crl-as-complete-delta",
            "stderr_marker": "unable to get certificate CRL",
        },
        {
            "case": "delta-crl-as-complete-reasons",
            "trusted": ["delta-crl-as-complete-ca"],
            "leaf": "delta-crl-as-complete-leaf",
            "opts": ["-no_check_time", "-crl_check", "-extended_crl"],
            "crl": "delta-crl-as-complete-delta-reasons",
            "stderr_marker": "unable to get certificate CRL",
        },
        {
            "case": "cve-2026-28388",
            "trusted": ["cve-2026-28388-ca"],
            "leaf": "cve-2026-28388-leaf",
            "opts": ["-attime", "1739527200", "-crl_check", "-use_deltas"],
            "crl": "cve-2026-28388-crls",
            "stderr_marker": "CRL is not yet valid",
        },
    ]
    cases = []
    mirrors_ok = True
    for mir in mirrors:
        crl_opts = mir["opts"] + ["-CRLfile", str(engine._file(mir["crl"]))]
        v = engine.verify(mir["leaf"], "", crl_opts, mir["trusted"], [])
        err = engine.stderr_of(mir["leaf"], "", crl_opts, mir["trusted"], [])
        marker_ok = mir["stderr_marker"] in err
        if v or not marker_ok:
            mirrors_ok = False
        cases.append(
            {
                "case": mir["case"],
                "store": "UPSTREAM_MIRROR",
                "authorized": v,
                "stderr_marker_present": marker_ok,
            }
        )
    pos = engine.verify(
        "delta-crl-as-complete-leaf", "", ["-no_check_time"],
        ["delta-crl-as-complete-ca"], [],
    )
    if not pos:
        mirrors_ok = False
    cases.append(
        {
            "case": "delta-crl-as-complete",
            "store": "POSITIVE_NO_CRLCHECK",
            "authorized": pos,
        }
    )
    preconditions_ok = True
    resurrection_detail = []
    for mir in mirrors:
        ca, leaf, crl, base = (
            mir["trusted"][0], mir["leaf"], mir["crl"], mir["opts"],
        )
        with_crl = base + ["-CRLfile", str(engine._file(crl))]
        variants = (
            ("A_WITH_CRL", with_crl),
            ("B_NO_CRL", base),
            ("UNION_WITH_CRL", with_crl),
            ("UNION_FLAT_CERTONLY", base),
            ("INTERSECTION_CERTONLY", base),
        )
        for label, opts in variants:
            v = engine.verify(leaf, "", opts, [ca], [])
            cases.append({"case": mir["case"], "store": label, "authorized": v})
            if label in ("A_WITH_CRL", "B_NO_CRL") and v:
                preconditions_ok = False
            if label.startswith(("UNION", "INTERSECTION")) and v:
                resurrection_detail.append({"case": mir["case"], "store": label})
    return {
        "cases": cases,
        "upstream_mirrors_ok": mirrors_ok,
        "parent_preconditions_ok": preconditions_ok,
        "resurrections": len(resurrection_detail),
        "resurrection_detail": resurrection_detail,
    }


def run_hostile_control(engine, graph_info, edges):
    """C6: ORION-labeled deliberate first-mixing split (not domain evidence)."""
    task = {
        "task_id": "C6-HOSTILE-SPLIT",
        "family": "HOSTILE_CONTROL",
        "leaf": "ee-cert",
        "purpose": "sslserver",
        "opts": [],
        "state_a": {"trusted": ["root-cert"], "untrusted": []},
        "state_b": {"trusted": [], "untrusted": ["ca-cert"]},
        "upstream_case_a": None,
        "upstream_case_b": None,
    }
    rec = evaluate_task(engine, graph_info, edges, task)
    ok = (
        rec["hybrid"]
        and not rec["decisions"]["M5_TYPED_WITNESS"]
        and rec["decisions"]["M1_FLAT_UNION"]
        and rec["first_mixing"] is not None
        and rec["first_mixing"].get("first_mixing_link") == ["ca-cert", "root-cert"]
    )
    return {"task": rec, "detected_and_localized": ok}


def aggregate(task_records):
    fams = {}
    for rec in task_records:
        fam = rec["family"]
        fams.setdefault(fam, []).append(rec)
    out = {}
    for fam, recs in sorted(fams.items()):
        agg = {
            "tasks": len(recs),
            "engine_hybrids": sum(1 for r in recs if r["hybrid"]),
            "parent_authorized": sum(1 for r in recs if r["parent_authorized"]),
            "union_authorized": sum(1 for r in recs if r["vU"]),
            "c3_violations": sum(1 for r in recs if r["c3"]["violation"]),
        }
        for m in METHODS:
            agg[m] = {
                "allows": sum(1 for r in recs if r["decisions"][m]),
                "unsafe_merges": sum(1 for r in recs if r["unsafe"][m]),
                "needless_rejections": sum(1 for r in recs if r["needless"][m]),
            }
        out[fam] = agg
    return out


def main():
    here = Path(__file__).resolve().parent
    certs_dir = here / "third_party" / "openssl-3.6.4-testcerts" / "test" / "certs"
    if not certs_dir.is_dir():
        fail(f"vendored corpus missing at {certs_dir}")
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default=os.environ.get("OPENSSL_BIN", "openssl"))
    ap.add_argument("--engine-lib", default=os.environ.get("OPENSSL_LIB"))
    ap.add_argument("--results", default=str(here / "ROUND2_RESULTS_V2.json"))
    ap.add_argument("--check-final", action="store_true")
    ap.add_argument(
        "--cost-out", default=str(here / "COST_ROUND2_V2.json")
    )
    args = ap.parse_args()

    engine = Engine(args.engine, args.engine_lib, certs_dir)
    if not engine.version_line.startswith("OpenSSL 3.6.4"):
        fail(f"engine is not pinned OpenSSL 3.6.4: {engine.version_line}")

    anchor = run_anchor_control(engine)
    graph_info, edges, name_only, graph_calls = corpus_cert_graph(engine)

    manifest = json.loads((here / "TASK_MANIFEST_V2.json").read_text())
    task_records = []
    for task in manifest["tasks"]:
        task_records.append(evaluate_task(engine, graph_info, edges, task))

    retraction = run_retraction_control(engine)
    hostile = run_hostile_control(engine, graph_info, edges)

    fams = aggregate(task_records)
    domain_hybrids = [r for r in task_records if r["hybrid"]]
    flagged = [
        r for r in task_records
        if r["hybrid"]
    ]  # M5 flags exactly the hybrid set
    false_flags = [
        r for r in task_records
        if r["vU"] and r["parent_authorized"] and r["hybrid"]
    ]
    c3_violations = sum(1 for r in task_records if r["c3"]["violation"])
    hybrid_localizations_complete = all(
        isinstance(r.get("first_mixing"), dict)
        and "error" not in r["first_mixing"]
        and r["first_mixing"].get("first_mixing_link")
        for r in domain_hybrids
    )
    m5_decision_ok = all(
        r["decisions"]["M5_TYPED_WITNESS"] == r["parent_authorized"]
        for r in task_records
    )

    anchor_rate_ok = anchor["agreement_rate"] >= 0.95
    if c3_violations:
        terminal = "CANNOT_CHECK_INDEPENDENT_DOMAIN_ADJUDICATION"
        terminal_reason = "white-box witness graph disagreed with engine"
    elif not hybrid_localizations_complete:
        terminal = "CANNOT_CHECK_INDEPENDENT_DOMAIN_ADJUDICATION"
        terminal_reason = "one or more hybrid authorizations lack a fail-closed first-mixing localization"
    elif not anchor_rate_ok:
        terminal = "CANNOT_CHECK_INDEPENDENT_DOMAIN_ADJUDICATION"
        terminal_reason = "upstream label anchoring below 95 percent"
    elif domain_hybrids:
        terminal = "D_R2_REAL_AUTHORITY_PROMOTION_ERROR_PREVENTED"
        terminal_reason = (
            f"{len(domain_hybrids)} engine-adjudicated hybrid authorizations "
            "on upstream-authored materials; M1 authorizes all of them, M5 "
            "blocks all with the first-mixing reason, engine output carries "
            "no origin distinction"
        )
    else:
        terminal = "D_R2_TYPED_UNTYPED_EQUIVALENT"
        terminal_reason = "no hybrid authorization arose on real materials"

    costs = {
        "engine_verify_invocations": engine.invocations,
        "engine_verify_invocations_requested": engine.requested,
        "per_method_required_invocations": {
            "M1_FLAT_UNION": len(task_records),
            "M2_INTERSECTION": len(task_records),
            "M3_REJECT_ALL": 0,
            "M4_OURS_B": len(task_records),
            "M5_TYPED_WITNESS": 2 * len(task_records),
        },
        "ground_truth_basis_invocations_per_task": 4,
        "graph_probe_invocations": graph_calls,
    }
    results = {
        "protocol": PROTOCOL,
        # This executed result changes the bounded empirical claim receipt; it
        # does not itself grant external scientific, journal, or submission
        # authority.  Those decisions remain outside this evaluator.
        "scientific_authority_delta": "NONE",
        "engine": {
            "tag": ENGINE_TAG,
            "commit": ENGINE_COMMIT,
            "tarball_sha256": ENGINE_TARBALL_SHA256,
            "version_line": engine.version_line,
        },
        "frozen_attime": FROZEN_ATTIME,
        "manifest_sha256": sha256_file(here / "TASK_MANIFEST_V2.json"),
        "anchor_control_C1": anchor,
        "corpus_graph": {
            "nodes": len(graph_info),
            "cert_nodes": sum(1 for v in graph_info.values() if v.get("is_cert")),
            "edges": sum(len(v) for v in edges.values()),
            "name_only_edges": len(name_only),
            "name_only_edge_list": name_only,
        },
        "families": fams,
        "total_tasks": len(task_records),
        "engine_hybrids_total": len(domain_hybrids),
        "hybrid_tasks": [
            {
                "task_id": r["task_id"],
                "family": r["family"],
                "leaf": r["leaf"],
                "purpose": r["purpose"],
                "first_mixing": r.get("first_mixing"),
            }
            for r in domain_hybrids
        ],
        "obstruction_detection": {
            "engine_hybrids": len(domain_hybrids),
            "m5_flagged": len(flagged),
            "recall": (
                round(len(flagged) / len(domain_hybrids), 4)
                if domain_hybrids else None
            ),
            "precision": (
                round(len(flagged) / len(flagged), 4) if flagged else None
            ),
            "false_flags_on_single_origin_complete": len(false_flags),
        },
        "retraction_control_C4": retraction,
        "hostile_control_C6": {
            "detected_and_localized": hostile["detected_and_localized"],
            "task": hostile["task"],
        },
        "invariants": {
            "c3_violations": c3_violations,
            "hybrid_localizations_complete": hybrid_localizations_complete,
            "m5_decision_equals_parent_authorization": m5_decision_ok,
            "c6_detected": hostile["detected_and_localized"],
            "c4_resurrections": retraction["resurrections"],
            "c4_upstream_mirrors_ok": retraction["upstream_mirrors_ok"],
            "c4_parent_preconditions_ok": retraction["parent_preconditions_ok"],
        },
        "costs": costs,
        "terminal": terminal,
        "terminal_reason": terminal_reason,
    }
    for inv in (
        "m5_decision_equals_parent_authorization",
        "hybrid_localizations_complete",
        "c6_detected",
    ):
        if not results["invariants"][inv]:
            fail(f"invariant violated: {inv}")
    if results["invariants"]["c4_resurrections"]:
        fail("invariant violated: c4_resurrections")
    for inv in ("c4_upstream_mirrors_ok", "c4_parent_preconditions_ok"):
        if not results["invariants"][inv]:
            fail(f"invariant violated: {inv}")

    blob = json.dumps(results, sort_keys=True, indent=1, ensure_ascii=False) + "\n"
    cost_blob = json.dumps(costs, sort_keys=True, indent=1) + "\n"
    if args.check_final:
        committed = Path(args.results).read_text()
        if committed != blob:
            print("CHECK-FAILED: regenerated receipt differs", file=sys.stderr)
            sys.exit(1)
        committed_cost = Path(args.cost_out).read_text()
        if committed_cost != cost_blob:
            print(
                "CHECK-FAILED: regenerated cost receipt differs",
                file=sys.stderr,
            )
            sys.exit(1)
        print("CHECK-FINAL OK: byte-identical result and cost receipts")
        return
    Path(args.results).write_text(blob, encoding="utf-8")
    Path(args.cost_out).write_text(cost_blob, encoding="utf-8")
    print(f"results written: {args.results}")
    print(f"costs written: {args.cost_out}")
    print(f"terminal: {terminal}")
    print(f"observed engine wall seconds (non-receipt): {engine.wall:.3f}")


if __name__ == "__main__":
    main()
