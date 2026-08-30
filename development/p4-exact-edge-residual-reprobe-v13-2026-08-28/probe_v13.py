#!/usr/bin/env python3
"""P4 V13 residual-edge reprobe: edges 36, 133, 185 (metadata-only provider-state probes).

Revival lane for ORION-14.NAT.M6.JOSS_EXACT_EDGE_LINEAGE_AUTHORITY.V11 residuals.
Attribution (V11): each edge failed at a distinct provider-state stage. This probe
re-tests each edge with estimators V10/V11 did not use:

- edge 36: Zenodo concept-version enumeration (a corrected/replacement deposit would
  appear as a new child of concept 10.5281/zenodo.21221061) plus the frozen child/
  DataCite recheck;
- edges 133/185: the dedicated PyPI attestations surface (/_attestations/) and the
  independent Sigstore Rekor transparency-log retrieval by artifact digest, neither
  of which V10/V11 queried, plus the frozen PEP 691 recheck.

Outcome-blind: no case, label, or protected material is touched.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
EVID = ROOT / "evidence"
UA = "ORION-P4-public-source-feasibility/1.0 (bounded metadata audit)"


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def capture(slug: str, url: str, *, accept: str = "application/json", method: str = "GET", body: bytes | None = None) -> dict:
    EVID.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept}, method=method, data=body)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    row: dict = {"slug": slug, "url": url, "method": method, "started_at": now()}
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read()
            row.update(status=resp.status, final_url=resp.geturl(), body_bytes=len(raw), body_sha256=sha256(raw))
            (EVID / f"{slug}.body").write_bytes(raw)
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        row.update(status=exc.code, final_url=exc.geturl(), error=f"HTTPError:{exc.code}", body_bytes=len(raw), body_sha256=sha256(raw) if raw else None)
        if raw:
            (EVID / f"{slug}.body").write_bytes(raw)
    except Exception as exc:  # noqa: BLE001 - transport failures are recorded, never fatal
        row.update(error=f"{type(exc).__name__}:{exc}")
    row["finished_at"] = now()
    return row


def load(slug: str) -> object:
    path = EVID / f"{slug}.body"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_bytes())
    except json.JSONDecodeError:
        return None


def main() -> None:
    requests: list[dict] = []

    # ---------- Edge 36: jaxionproject/jaxion ----------
    # Frozen rechecks (V10/V11 surface): Zenodo child record + versions, DataCite concept/child.
    requests.append(capture("36_zenodo_child", "https://zenodo.org/api/records/21221062"))
    requests.append(capture("36_zenodo_child_versions", "https://zenodo.org/api/records/21221062/versions"))
    requests.append(capture("36_zenodo_concept", "https://zenodo.org/api/records/21221061"))
    # New estimators: enumerate the concept's version chain directly.
    q = urllib.parse.quote('conceptrecid:"21221061"', safe="")
    requests.append(capture("36_zenodo_concept_children_search", f"https://zenodo.org/api/records?q={q}&size=50&sort=most_recent"))
    q2 = urllib.parse.quote("10.5281/zenodo.21221061", safe="")
    requests.append(capture("36_zenodo_conceptdoi_search", f"https://zenodo.org/api/records?q=conceptdoi:{q2}&size=50&sort=most_recent"))
    requests.append(capture("36_datacite_concept", "https://api.datacite.org/dois/10.5281%2Fzenodo.21221061"))
    requests.append(capture("36_datacite_child", "https://api.datacite.org/dois/10.5281%2Fzenodo.21221062"))

    # ---------- Edges 133 / 185: PyPI signed provenance ----------
    pypi_edges = [
        {"index": 133, "project": "woodtapper", "version": "0.0.13",
         "sha256": "b509f6469b9ff8888195751c811d689559f45e24aeb35bb173b9680c99c8dbf3"},
        {"index": 185, "project": "disruption-py", "version": "0.14.0",
         "sha256": "775f92dbcbd6d1523db241494998e4b0867d51a84236feb7accc86b63b033a19"},
    ]
    for edge in pypi_edges:
        tag = edge["index"]
        # Frozen rechecks: PEP 691 Simple API file-object provenance field.
        requests.append(capture(f"{tag}_pypi_simple", f"https://pypi.org/simple/{edge['project']}/",
                                accept="application/vnd.pypi.simple.v1+json"))
        # New estimator 1: dedicated PyPI attestations surface used by pip.
        requests.append(capture(f"{tag}_pypi_attestations", f"https://pypi.org/_attestations/{edge['project']}/{edge['version']}/"))
        # New estimator 2: independent Sigstore Rekor transparency log by artifact digest.
        rekor_query = json.dumps({"hashes": [f"sha256:{edge['sha256']}"]}).encode()
        requests.append(capture(f"{tag}_rekor_retrieve_by_digest",
                                "https://rekor.sigstore.dev/api/v1/log/entries/retrieve",
                                method="POST", body=rekor_query))
        requests.append(capture(f"{tag}_rekor_get_by_digest",
                                f"https://rekor.sigstore.dev/api/v1/log/entries?digest=sha256:{edge['sha256']}"))

    receipt = {
        "schema_version": "orion.p4.exact-edge.residual-reprobe.v13.receipt.v1",
        "finished_at": now(),
        "public_development_evidence_only": True,
        "outcomes_accessed": False,
        "requests": requests,
    }
    (ROOT / "PROBE_RECEIPT_V13.json").write_bytes(
        (json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    )
    print(json.dumps({"request_count": len(requests),
                      "errors": sum(1 for r in requests if r.get("error"))}, indent=2))


if __name__ == "__main__":
    main()
