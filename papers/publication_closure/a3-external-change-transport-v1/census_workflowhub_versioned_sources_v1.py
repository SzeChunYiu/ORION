#!/usr/bin/env python3
"""Outcome-blind WorkflowHub versioned/licensed source-family census.

Counts at most one candidate cluster per WorkflowHub workflow ID. The script
uses only public TRS + landing metadata and does not classify change strata or
read any ORION prediction/gold outcome.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

UA = "ORION-A3-source-census-v1/1.0 (+https://github.com/SzeChunYiu/ORION)"
TRS_TOOLS = "https://workflowhub.eu/ga4gh/trs/v2/tools"
LANDING = "https://workflowhub.eu/workflows/{tool_id}?version={version_id}"
SCRIPT_JSONLD = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.I | re.S)


def request_bytes(url: str, *, accept: str, timeout: float = 30.0, retries: int = 3) -> tuple[bytes, dict[str, str]]:
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if getattr(response, "status", 200) != 200:
                    raise RuntimeError(f"HTTP {response.status} for {url}")
                data = response.read(8 * 1024 * 1024 + 1)
                if len(data) > 8 * 1024 * 1024:
                    raise RuntimeError(f"response too large for census: {url}")
                headers = {k.lower(): v for k, v in response.headers.items()}
                return data, headers
        except (urllib.error.URLError, TimeoutError, RuntimeError) as exc:
            last = exc
            if attempt + 1 < retries:
                time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"failed to fetch {url}: {last}")


def fetch_json(url: str) -> tuple[Any, dict[str, str]]:
    raw, headers = request_bytes(url, accept="application/json")
    try:
        return json.loads(raw), headers
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"non-JSON response from {url}") from exc


def fetch_all_tools(max_pages: int = 20, limit: int = 1000) -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = []
    offset = 0
    seen_offsets: set[int] = set()
    for _page in range(max_pages):
        if offset in seen_offsets:
            raise RuntimeError("TRS pagination repeated an offset")
        seen_offsets.add(offset)
        url = f"{TRS_TOOLS}?limit={limit}&offset={offset}"
        payload, headers = fetch_json(url)
        if not isinstance(payload, list):
            raise RuntimeError("TRS /tools did not return a list")
        for item in payload:
            if not isinstance(item, dict):
                raise RuntimeError("TRS tool item is not an object")
            tools.append(item)
        if not payload:
            break
        next_page = headers.get("next_page")
        if next_page:
            parsed = urllib.parse.urlparse(next_page)
            q = urllib.parse.parse_qs(parsed.query)
            raw_offset = q.get("offset", [None])[0]
            if raw_offset is not None:
                try:
                    offset = int(raw_offset)
                    continue
                except ValueError:
                    pass
        if len(payload) < limit:
            break
        offset += len(payload)
    else:
        raise RuntimeError("TRS pagination hit max_pages before exhaustion")
    return tools


def integer_versions(tool: dict[str, Any]) -> list[int]:
    versions = tool.get("versions")
    if not isinstance(versions, list):
        return []
    out: set[int] = set()
    for v in versions:
        if not isinstance(v, dict):
            continue
        vid = v.get("id")
        if isinstance(vid, int) and not isinstance(vid, bool):
            out.add(vid)
        elif isinstance(vid, str) and vid.isdigit():
            out.add(int(vid))
    return sorted(out)


def extract_jsonld(raw: bytes) -> Any:
    text = raw.decode("utf-8", "strict")
    stripped = text.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        return json.loads(stripped)
    matches = SCRIPT_JSONLD.findall(text)
    if not matches:
        raise RuntimeError("landing page exposes no application/ld+json metadata")
    # Prefer the first document that describes a workflow/software object.
    docs = []
    for m in matches:
        try:
            docs.append(json.loads(html.unescape(m).strip()))
        except json.JSONDecodeError:
            continue
    if not docs:
        raise RuntimeError("landing page JSON-LD blocks are unparseable")
    for doc in docs:
        encoded = json.dumps(doc, sort_keys=True)
        if "ComputationalWorkflow" in encoded or "SoftwareSourceCode" in encoded:
            return doc
    return docs[0]


def find_license(obj: Any) -> str | None:
    if isinstance(obj, dict):
        if "license" in obj:
            value = obj["license"]
            if isinstance(value, str) and value.strip():
                return value.strip()
            if isinstance(value, dict):
                for key in ("@id", "identifier", "name"):
                    val = value.get(key)
                    if isinstance(val, str) and val.strip():
                        return val.strip()
        for value in obj.values():
            got = find_license(value)
            if got:
                return got
    elif isinstance(obj, list):
        for value in obj:
            got = find_license(value)
            if got:
                return got
    return None


def fetch_license(tool_id: str, version_id: int) -> tuple[str, str]:
    url = LANDING.format(tool_id=urllib.parse.quote(tool_id, safe=""), version_id=version_id)
    raw, _headers = request_bytes(url, accept="application/ld+json,text/html;q=0.8")
    doc = extract_jsonld(raw)
    license_value = find_license(doc)
    if not license_value:
        raise RuntimeError("missing licence in version landing metadata")
    digest = hashlib.sha256(json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return license_value, digest


def tool_sort_key(tool: dict[str, Any]) -> tuple[int, str]:
    tid = tool.get("id")
    text = str(tid)
    return (int(text) if text.isdigit() else 10**18, text)


def census(target: int, polite_delay: float = 0.03) -> dict[str, Any]:
    tools = fetch_all_tools()
    ids = [str(t.get("id")) for t in tools]
    if len(ids) != len(set(ids)):
        raise RuntimeError("TRS /tools returned duplicate tool IDs")
    tools.sort(key=tool_sort_key)

    multiversion = 0
    public_version_metadata_failures = []
    candidates = []
    for tool in tools:
        versions = integer_versions(tool)
        if len(versions) < 2:
            continue
        multiversion += 1
        tool_id = str(tool.get("id"))
        before, after = versions[-2], versions[-1]
        try:
            lic_before, meta_before = fetch_license(tool_id, before)
            time.sleep(polite_delay)
            lic_after, meta_after = fetch_license(tool_id, after)
            time.sleep(polite_delay)
        except Exception as exc:
            public_version_metadata_failures.append({"tool_id": tool_id, "reason": str(exc)[:240]})
            continue
        candidates.append({
            "workflow_id": tool_id,
            "workflow_name": tool.get("name"),
            "version_before": before,
            "version_after": after,
            "license_before": lic_before,
            "license_after": lic_after,
            "metadata_sha256_before": meta_before,
            "metadata_sha256_after": meta_after,
        })
        if len(candidates) >= target:
            break

    digest = hashlib.sha256(json.dumps(candidates, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        "schema": "ORION.A3.WorkflowHubVersionedSourceCensusResult.v1",
        "trs_tools_seen": len(tools),
        "multiversion_workflow_families_seen_before_stop": multiversion,
        "versioned_public_licensed_candidate_families": len(candidates),
        "target_candidate_families": target,
        "capacity_floor_reached": len(candidates) >= target,
        "candidate_manifest_sha256": digest,
        "candidate_workflows": candidates,
        "public_metadata_failures_before_stop": public_version_metadata_failures,
        "one_candidate_per_workflow_family": True,
        "stratum_eligibility_adjudicated": False,
        "gold_adjudicated": False,
        "protected_orion_predictions_accessed": False,
        "scientific_authority_delta": "NONE__SOURCE_UNIVERSE_CAPACITY_PREFLIGHT_ONLY",
        "decision": "WORKFLOWHUB_VERSIONED_LICENSED_FAMILY_CAPACITY_AT_LEAST_128" if len(candidates) >= target else "CANNOT_CHECK_WORKFLOWHUB_VERSIONED_LICENSED_FAMILY_CAPACITY",
    }


def self_test() -> dict[str, Any]:
    assert integer_versions({"versions": [{"id": "1"}, {"id": "2"}, {"id": "2"}, {"id": "x"}]}) == [1, 2]
    doc = {"@type": ["SoftwareSourceCode", "ComputationalWorkflow"], "license": {"@id": "https://spdx.org/licenses/MIT"}}
    assert find_license(doc) == "https://spdx.org/licenses/MIT"
    nested = {"@graph": [{"@type": "ComputationalWorkflow", "license": "MIT"}]}
    assert find_license(nested) == "MIT"
    assert tool_sort_key({"id": "9"}) < tool_sort_key({"id": "10"})
    return {"decision": "GREEN", "network_accessed": False}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=128)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    if args.self_test:
        result = self_test()
    else:
        if args.target < 1:
            ap.error("--target must be >=1")
        result = census(args.target)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    if not args.self_test and result["decision"].startswith("CANNOT_CHECK"):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
