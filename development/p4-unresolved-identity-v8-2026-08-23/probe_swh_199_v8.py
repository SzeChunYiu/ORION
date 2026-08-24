#!/usr/bin/env python3
"""Exact Software Heritage release probe for frozen V8 target 199 only."""

from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"
RELEASE_ID = "0c3cbaebb9ca41133e5705792b1388336c34a43e"
URL = f"https://archive.softwareheritage.org/api/1/release/{RELEASE_ID}/"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> None:
    started_at = now()
    clock = time.monotonic()
    request = urllib.request.Request(
        URL,
        headers={"Accept": "application/json", "User-Agent": "orion-p4-v8-exact-identity/1.0"},
    )
    body = b""
    status = None
    final_url = URL
    error = None
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read()
            status = response.status
            final_url = response.geturl()
    except urllib.error.HTTPError as exc:
        body = exc.read()
        status = exc.code
        final_url = exc.geturl()
        error = f"HTTPError:{exc.code}"
    except Exception as exc:  # fail closed and receipt the exact exception
        error = f"{type(exc).__name__}:{exc}"

    response_json = None
    try:
        response_json = json.loads(body)
    except Exception:
        pass

    evidence_path = EVIDENCE / f"199_swh_release_{RELEASE_ID}.json"
    if body:
        evidence_path.write_bytes(body)

    receipt = {
        "schema_version": "orion.p4.swh-release-exact-probe.v8",
        "frozen_index": 199,
        "repository": "targene/targene-pipeline",
        "publication_version": "v0.13.4",
        "archive_doi": "10.5281/zenodo.19202203",
        "provider_swh_anchor": f"swh:1:rel:{RELEASE_ID}",
        "request": {
            "url": URL,
            "final_url": final_url,
            "http_status": status,
            "error": error,
            "body_bytes": len(body),
            "body_sha256": hashlib.sha256(body).hexdigest() if body else None,
            "started_at": started_at,
            "finished_at": now(),
        },
        "response": response_json,
        "evidence_path": str(evidence_path.relative_to(HERE)) if body else None,
        "runtime_seconds": round(time.monotonic() - clock, 6),
        "scope_expanded": False,
    }
    (HERE / "SWH_199_PROBE_RECEIPT_V8.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    print(
        "P4_V8_SWH_199_PROBE_COMPLETE__"
        f"HTTP={status}__TARGET={response_json.get('target') if isinstance(response_json, dict) else None}__"
        f"RUNTIME_SECONDS={time.monotonic() - clock:.6f}"
    )


if __name__ == "__main__":
    main()
