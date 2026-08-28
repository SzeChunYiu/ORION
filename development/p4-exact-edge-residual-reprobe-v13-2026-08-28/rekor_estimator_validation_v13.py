#!/usr/bin/env python3
"""P4 V13 Rekor estimator validation (validate-the-checker amendment).

probe_v13.py queried POST /api/v1/log/entries/retrieve with {"hashes":[...]} for
edges 133/185 and observed []. Before using that as absence evidence, the
estimator is validated against a positive control: a PyPI file that provably
HAS attestations (PEP 691 provenance present). If the same query shape returns
[] for the control too, the shape is a false-negative estimator and its []
results are quarantined.

Three shapes are tested on the control:
  A: {"hashes": ["sha256:<digest>"]}                     (probe_v13 shape)
  B: {"entryQuerys": [{"hashes": ["sha256:<digest>"]}]}   (rekor documented field)
  C: GET /api/v1/log/entries?logIndex=<n>                 (direct, from the
     control attestation bundle's own transparency entry)

Shape B is then run on the frozen edge digests ONLY IF it validated on the
control (a shape that cannot see a known attestation has no discriminative
power and must not be cited for absence).

Development evidence only. No outcome, label or protected case is accessed.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
EVID = ROOT / "evidence"
UA = "ORION-P4-public-source-feasibility/1.0 (bounded metadata audit)"
EDGE_DIGESTS = [
    {"index": 133, "project": "woodtapper", "sha256": "b509f6469b9ff8888195751c811d689559f45e24aeb35bb173b9680c99c8dbf3"},
    {"index": 185, "project": "disruption-py", "sha256": "775f92dbcbd6d1523db241494998e4b0867d51a84236feb7accc86b63b033a19"},
]


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def call(slug: str, url: str, *, accept: str = "application/json", method: str = "GET", body: bytes | None = None) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept}, method=method, data=body)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    row: dict = {"slug": slug, "url": url, "method": method, "started_at": now()}
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read()
            row.update(status=resp.status, body_bytes=len(raw), body_sha256=sha256(raw))
            (EVID / f"{slug}.body").write_bytes(raw)
            row["json"] = json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        row.update(status=exc.code, error=f"HTTPError:{exc.code}", body_bytes=len(raw))
        if raw:
            (EVID / f"{slug}.body").write_bytes(raw)
    except Exception as exc:  # noqa: BLE001
        row.update(error=f"{type(exc).__name__}:{exc}")
    row["finished_at"] = now()
    return row


def main() -> None:
    EVID.mkdir(parents=True, exist_ok=True)
    log: dict = {"schema_version": "orion.p4.exact-edge.rekor-estimator-validation.v13.v1",
                 "started_at": now(), "public_development_evidence_only": True, "outcomes_accessed": False}

    # 1. Positive control: a PyPI file with provenance PRESENT.
    ctrl_simple = call("rekorval_control_pypi_simple", "https://pypi.org/simple/packaging/",
                       accept="application/vnd.pypi.simple.v1+json")
    control = None
    files = (ctrl_simple.get("json") or {}).get("files", [])
    with_prov = [f for f in files if f.get("provenance")]
    log["control_selection"] = {
        "project": "packaging", "file_count": len(files),
        "files_with_provenance": len(with_prov),
        "chosen": with_prov[-1]["filename"] if with_prov else None,
    }
    if with_prov:
        f = with_prov[-1]
        control = {"filename": f["filename"], "sha256": f["hashes"]["sha256"], "provenance": f["provenance"]}
    log["control"] = control
    if not control:
        log["error"] = "no positive control available (packaging has no provenance-bearing file)"
        (ROOT / "REKOR_ESTIMATOR_VALIDATION_V13.json").write_bytes(
            (json.dumps(log, indent=2, sort_keys=True) + "\n").encode())
        raise SystemExit("control selection failed")

    digest = control["sha256"]

    # 2. Control attestation bundle (proves the control really has attestations).
    bundle_rows = []
    prov = control["provenance"]
    log_indexes: list[int] = []
    bundle_url = prov if isinstance(prov, str) else prov.get("url")
    if bundle_url:
        bundle = call("rekorval_control_attestation_bundle", bundle_url)
        bundle_rows.append(bundle)
        data = bundle.get("json")
        atts = None
        if isinstance(data, dict):
            bundles = data.get("attestation_bundles")
            if isinstance(bundles, list) and bundles:
                atts = bundles[0].get("attestations")
            elif isinstance(data.get("attestations"), list):
                atts = data["attestations"]
        elif isinstance(data, list):
            atts = data
        for att in atts or []:
            vm = att.get("verification_material") or att.get("verificationMaterial") or {}
            tlog = (vm.get("transparency_entries") or vm.get("transparencyEntries")
                    or vm.get("tlogEntries") or [])
            for entry in tlog:
                li = entry.get("logIndex") or entry.get("log_index")
                if isinstance(li, int):
                    log_indexes.append(li)
                elif isinstance(li, str) and li.isdigit():
                    log_indexes.append(int(li))
    log["control_attestation_bundle"] = {
        "attestation_count": len((bundle_rows[0].get("json") or {}).get("attestations", [])) if bundle_rows else None,
        "tlog_log_indexes": log_indexes,
    }

    # 3. Shape A (probe_v13 shape) on the control.
    a_body = json.dumps({"hashes": [f"sha256:{digest}"]}).encode()
    shape_a = call("rekorval_control_shapeA_hashes", "https://rekor.sigstore.dev/api/v1/log/entries/retrieve",
                   method="POST", body=a_body)

    # 4. Shape B (documented entryQuerys field) on the control.
    b_body = json.dumps({"entryQuerys": [{"hashes": [f"sha256:{digest}"]}]}).encode()
    shape_b = call("rekorval_control_shapeB_entryquerys", "https://rekor.sigstore.dev/api/v1/log/entries/retrieve",
                   method="POST", body=b_body)

    # 5. Shape C (direct logIndex lookup) — ground truth that the log holds the entry.
    shape_c = None
    if log_indexes:
        shape_c = call("rekorval_control_shapeC_logindex",
                       f"https://rekor.sigstore.dev/api/v1/log/entries?logIndex={log_indexes[0]}")

    def entries_of(row: dict | None) -> int | None:
        if not row or row.get("error"):
            return None
        data = row.get("json")
        if isinstance(data, list):
            return len(data)
        if isinstance(data, dict):
            return len(data)
        return None

    a_n, b_n, c_n = entries_of(shape_a), entries_of(shape_b), entries_of(shape_c)
    shape_b_valid = b_n is not None and b_n > 0
    log["shape_results_control"] = {
        "A_hashes_list": {"entries": a_n, "status": shape_a.get("status")},
        "B_entryQuerys": {"entries": b_n, "status": shape_b.get("status")},
        "C_logIndex_direct": {"entries": c_n, "status": shape_c.get("status") if shape_c else "not_run"},
    }

    # 6. Edges under shape B only if it validated on the control.
    edge_results = []
    if shape_b_valid:
        for edge in EDGE_DIGESTS:
            body = json.dumps({"entryQuerys": [{"hashes": [f"sha256:{edge['sha256']}"]}]}).encode()
            row = call(f"{edge['index']}_rekor_shapeB_entryquerys",
                       "https://rekor.sigstore.dev/api/v1/log/entries/retrieve", method="POST", body=body)
            edge_results.append({"index": edge["index"], "entries": entries_of(row),
                                 "status": row.get("status"), "error": row.get("error")})
    log["edge_results_shapeB"] = edge_results

    # 7. Estimator verdict.
    if shape_b_valid and all(e.get("entries") == 0 for e in edge_results):
        verdict = ("REKOR_ABSENCE_VALIDATED: shape B retrieves the control's entries but none for the "
                   "frozen edge digests; the transparency log holds no entry for either digest.")
    elif shape_b_valid:
        present = [e["index"] for e in edge_results if (e.get("entries") or 0) > 0]
        verdict = f"REKOR_ENTRIES_PRESENT_FOR_EDGES {present}: shape B validated on control and retrieved edge entries."
    elif c_n is not None and c_n > 0 and (a_n == 0 or a_n is None):
        verdict = ("STRUCTURALLY_BLIND: the log provably holds the control's attestation (shape C) while "
                   "digest-shaped retrieval cannot see it (shapes A/B empty); Rekor digest retrieval is "
                   "structurally blind to PyPI dsse attestations and NO rekor result may be cited for or "
                   "against the edges. Absence rests on the PyPI/GitHub surfaces only.")
    else:
        verdict = ("INCONCLUSIVE: no retrieval shape both validated on the control and produced a "
                   "discriminative result; all rekor evidence is quarantined.")
    log["estimator_verdict"] = verdict
    log["finished_at"] = now()
    (ROOT / "REKOR_ESTIMATOR_VALIDATION_V13.json").write_bytes(
        (json.dumps(log, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode())
    print(json.dumps({"control_entries": {"A": a_n, "B": b_n, "C": c_n},
                      "shapeB_valid": shape_b_valid, "edges": edge_results, "verdict": verdict}, indent=2))


if __name__ == "__main__":
    main()
