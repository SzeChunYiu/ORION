#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"
UA = "ORION-P4-exact-edge-authority-v10/1.0 (public research evidence audit)"


def capture(url: str, slug: str, accept: str = "application/json") -> dict:
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    request = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    body = b""
    status = None
    final_url = url
    headers = {}
    error = None
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            status = response.status
            final_url = response.geturl()
            headers = dict(response.headers)
            body = response.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        final_url = exc.geturl()
        headers = dict(exc.headers)
        body = exc.read()
        error = f"HTTPError:{exc.code}"
    except Exception as exc:
        error = f"{type(exc).__name__}:{exc}"
    path = EVIDENCE / f"{slug}.body"
    path.write_bytes(body)
    receipt = {
        "url": url,
        "started_at": started,
        "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": status,
        "final_url": final_url,
        "headers": {key: value for key, value in headers.items() if key.lower() in {"content-type", "content-length", "etag", "last-modified"}},
        "body_path": str(path.relative_to(ROOT)),
        "body_bytes": len(body),
        "body_sha256": hashlib.sha256(body).hexdigest(),
        "error": error,
    }
    (EVIDENCE / f"{slug}.receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    time.sleep(0.2)
    return receipt


canonical_origin = urllib.parse.quote("https://github.com/TARGENE/targene-pipeline", safe="")
requests = [
    capture(f"https://archive.softwareheritage.org/api/1/origin/{canonical_origin}/visits/", "199_swh_canonical_origin_visits"),
    capture("https://archive.softwareheritage.org/api/1/snapshot/4cc32f66bbfae46d9d3ee0bfd210a46619f0e895/", "199_swh_canonical_origin_snapshot"),
    capture("https://archive.softwareheritage.org/api/1/revision/a85df681d29a5cf3406d529144a7c0645e543e61/", "199_swh_v0_13_5_revision"),
    capture("https://archive.softwareheritage.org/api/1/revision/a85df681d29a5cf3406d529144a7c0645e543e61/log/?limit=100", "199_swh_v0_13_5_revision_log"),
    capture("https://archive.softwareheritage.org/api/1/revision/0f8b2dbca06a3bb7031de9058ee9882995e04412/", "199_swh_v0_13_4_revision_retry"),
    capture("https://archive.softwareheritage.org/api/1/content/sha1_git:a2bc6f7644e165ad7c9b0c6215ba20bdbe634728/raw/", "199_swh_exact_license_retry", "*/*"),
]

receipt = {
    "schema_version": "orion.p4.exact-edge-lineage-authority.v10.swh-canonical-probe-receipt",
    "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "protocol_sha256": hashlib.sha256((ROOT / "PROTOCOL_V10.json").read_bytes()).hexdigest(),
    "requests": requests,
}
(ROOT / "SWH_CANONICAL_PROBE_RECEIPT_V10.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
print(json.dumps({"requests": len(requests), "statuses": [request["status"] for request in requests]}))
