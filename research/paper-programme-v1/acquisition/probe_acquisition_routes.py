#!/usr/bin/env python3
"""Probe every acquisition route named in the independent-researcher plan.

A plan that names a dataset, registry or checkpoint is worth nothing if the
resource has moved, become gated, or changed licence. This re-probes each one
and records what actually answered, so the plan rots loudly instead of quietly.

Routes are recorded with what they are *for* in the requirement taxonomy:

  A  artifact not authored by the candidate
  B  frozen before outcomes, third-party timestamped
  C  labels withheld from the candidate
  D  independent scorer or adjudicator
  E  checkpoints and compute
  F  a bespoke human panel adjudicating the candidate's own cases

F is the only class with no free route. Everything else has at least one.

Exit codes: 0 all probed routes answered, 2 a route failed, 3 no network.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

UA = "orion-acquisition-probe/1 (+research; contact via repository)"
TIMEOUT = 30

ROUTES = [
    # (id, requirement class, what it discharges, url, expectation)
    ("openalex", "A", "multi-domain source corpus and retraction ground truth",
     "https://api.openalex.org/works?per-page=1", "json"),
    ("openalex_retracted", "A", "independently authored adjudication outcomes",
     "https://api.openalex.org/works?filter=is_retracted:true&per-page=1", "json"),
    ("crossref", "A", "multi-domain bibliographic source snapshots",
     "https://api.crossref.org/works?rows=1", "json"),
    ("crossref_retractions", "A", "editor-authored retraction notices",
     "https://api.crossref.org/works?filter=update-type:retraction&rows=1", "json"),
    ("retraction_watch_data", "A", "the Retraction Watch database, free via Crossref Labs",
     "https://gitlab.com/crossref/retraction-watch-data", "head"),
    ("arxiv", "A", "full-text source snapshots",
     "http://export.arxiv.org/api/query?search_query=all:test&max_results=1", "head"),
    ("github", "A", "real project revision histories for a revision-class panel",
     "https://api.github.com/rate_limit", "json"),
    ("osf_registries", "B", "third-party timestamped preregistration of a frozen protocol",
     "https://api.osf.io/v2/registrations/?page%5Bsize%5D=1", "json"),
    ("aspredicted", "B", "third-party timestamped preregistration, lightweight",
     "https://aspredicted.org/", "head"),
    ("zenodo", "B", "immutable DOI-bound artifact custody",
     "https://zenodo.org/api/records/?size=1", "json"),
    ("software_heritage", "B", "independent source-code archival with content hashes",
     "https://archive.softwareheritage.org/api/1/", "json"),
    ("pci_registered_reports", "D", "free peer review of a protocol before results exist",
     "https://rr.peercommunityin.org/", "head"),
    ("ml_reproducibility_challenge", "D", "third parties reproducing the work at no cost",
     "https://reproml.org/", "head"),
    ("openreview", "D", "open independent review",
     "https://openreview.net/", "head"),
    ("tmlr", "D", "a venue whose scope admits bounded and negative results",
     "https://jmlr.org/tmlr/", "head"),
]

# The P9-U-T3 frozen grid names these ladder points. Gated ones are still free
# but need a licence acceptance, which is friction a plan must state.
CHECKPOINTS = [
    "meta-llama/Llama-3.2-1B",
    "meta-llama/Llama-3.2-3B",
    "Qwen/Qwen2.5-0.5B",
    "Qwen/Qwen2.5-1.5B",
    "Qwen/Qwen2.5-3B",
    "Qwen/Qwen2.5-7B",
]


def fetch(url: str, limit: int | None = 4096) -> tuple[int, bytes]:
    """Fetch a URL. ``limit=None`` reads the whole body.

    Route probes only need a prefix, but a model card must be read in full --
    a truncated read fails to parse and would be recorded as "did not resolve",
    which is a false alarm about a resource that is perfectly fine.
    """
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return response.status, (response.read() if limit is None else response.read(limit))
    except urllib.error.HTTPError as exc:
        return exc.code, b""


def probe_routes() -> list[dict]:
    results = []
    for route_id, requirement, purpose, url, kind in ROUTES:
        try:
            status, body = fetch(url)
            ok = status == 200
            note = ""
            if ok and kind == "json":
                try:
                    json.loads(body.decode("utf-8", "replace"))
                except ValueError:
                    note = "answered but body is not JSON at the sampled prefix"
        except Exception as exc:
            status, ok, note = None, False, str(exc)
        results.append(
            {
                "route": route_id,
                "requirement_class": requirement,
                "discharges": purpose,
                "url": url,
                "http_status": status,
                "answered": ok,
                "note": note,
            }
        )
    return results


def probe_checkpoints() -> list[dict]:
    results = []
    for repo in CHECKPOINTS:
        try:
            status, body = fetch(f"https://huggingface.co/api/models/{repo}", limit=None)
            card = json.loads(body.decode("utf-8", "replace")) if status == 200 else {}
        except Exception as exc:
            results.append({"repo": repo, "resolved": False, "note": str(exc)})
            continue
        gated = card.get("gated")
        results.append(
            {
                "repo": repo,
                "resolved": status == 200,
                "gated": gated,
                "license": (card.get("cardData") or {}).get("license"),
                # gated="manual" is free but needs an accepted licence on an
                # account, which is a step a plan must not silently omit.
                "friction": "licence acceptance required" if gated else "none",
            }
        )
    return results


def main() -> int:
    try:
        fetch("https://api.openalex.org/works?per-page=1")
    except Exception as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "error": f"no network: {exc}"}))
        return 3

    routes = probe_routes()
    checkpoints = probe_checkpoints()
    failed = [r["route"] for r in routes if not r["answered"]]
    unresolved = [c["repo"] for c in checkpoints if not c.get("resolved")]

    print(
        json.dumps(
            {
                "schema": "orion.acquisition.route-probe.v1",
                "routes": routes,
                "p9_t3_scale_ladder_checkpoints": checkpoints,
                "routes_answered": len(routes) - len(failed),
                "routes_total": len(routes),
                "checkpoints_resolved": len(checkpoints) - len(unresolved),
                "checkpoints_total": len(checkpoints),
                "gated_checkpoints": [c["repo"] for c in checkpoints if c.get("gated")],
                "failed_routes": failed,
                "unresolved_checkpoints": unresolved,
                "note": (
                    "Reachability and licence only. This says a route exists and answers; "
                    "it does not say the route's content satisfies any particular blocker."
                ),
            },
            indent=2,
        )
    )
    return 2 if (failed or unresolved) else 0


if __name__ == "__main__":
    sys.exit(main())
