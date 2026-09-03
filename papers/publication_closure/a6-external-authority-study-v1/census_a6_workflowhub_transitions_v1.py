#!/usr/bin/env python3
"""Outcome-blind A6 stratum-2 census: WorkflowHub/RO-Crate workflow transitions.

Extends, and does not duplicate, the frozen A3 bound frame: the 128 versioned
WorkflowHub families already normalized-content-bound by
a3-external-change-transport-v1 (workflowhub-normalized-content-binding-v2 +
workflowhub-two-replacement-successor-v1) are reused as durable transition
receipts; only families outside that frame are freshly licensed and
RO-Crate content-bound here. Each row is an A6 packet candidate carrying the
3-way lineage trio. No stratum eligibility, gold label, prediction or outcome
is read or produced.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import html
import io
import json
import re
import stat
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A3_DIR = ROOT / "papers" / "publication_closure" / "a3-external-change-transport-v1"
SNAPSHOT = A3_DIR / "workflowhub-normalized-content-binding-v2" / "SNAPSHOT_V2.json"
SUCCESSOR = A3_DIR / "workflowhub-two-replacement-successor-v1" / "RESULT_V1.json"
SNAPSHOT_DIR = HERE / "workflowhub-census-v1"
STRATUM = "workflowhub_rocrate_versioned_workflow"
EXPECTED_SUCCESSOR_FRAME_SHA256 = "a47d9255aa37de056cb5cdd7c140bcccb487aa3285790655a48abb5e538c2993"
EXPECTED_BASE_SELECTED_ROWS_SHA256 = "2f36f8d5900c904d939e87f7c582281e27445f4045d520754b7b11dcbbc3b882"
UA = "ORION-A6-stratum2-census-v1/1.0 (+https://github.com/SzeChunYiu/ORION)"
TRS_TOOLS = "https://workflowhub.eu/ga4gh/trs/v2/tools"
LANDING = "https://workflowhub.eu/workflows/{tool_id}?version={version_id}"
MAX_BYTES = 256 * 1024 * 1024
SCRIPT_JSONLD = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.I | re.S)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def slugify(text: Any) -> str:
    lowered = str(text or "").strip().lower()
    out = re.sub(r"[^a-z0-9]+", "-", lowered, flags=re.ASCII).strip("-")
    return out or "unattributed"


# ---------------------------------------------------------------- A3 frozen frame (reused)


def load_a3_source_frame() -> dict[str, dict[str, Any]]:
    manifest = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    if manifest.get("schema") != "ORION.A3.WorkflowHubNormalizedContentBindingDurableSnapshot.v2":
        raise ValueError("A3 normalized snapshot schema mismatch")
    if manifest.get("selected_rows_sha256") != EXPECTED_BASE_SELECTED_ROWS_SHA256:
        raise ValueError("A3 normalized snapshot selected-row digest mismatch")
    rows: list[dict[str, Any]] = []
    for chunk in manifest["chunks"]:
        path = ROOT / chunk["path"]
        raw = path.read_bytes()
        if sha256_bytes(raw) != chunk["sha256"]:
            raise ValueError(f"A3 normalized snapshot chunk hash mismatch: {chunk['path']}")
        payload = json.loads(raw)
        chunk_rows = payload.get("rows")
        if not isinstance(chunk_rows, list) or len(chunk_rows) != chunk["rows"]:
            raise ValueError(f"A3 normalized snapshot chunk row mismatch: {chunk['path']}")
        rows.extend(chunk_rows)
    retained: dict[str, dict[str, Any]] = {}
    for row in rows:
        if row.get("status") == "NORMALIZED_CONTENT_BOUND_DIFFERENT":
            retained[str(row["workflow_id"])] = row
    if len(retained) != 126 or set(manifest.get("cannot_check_workflow_ids", [])) != {"402", "444"}:
        raise ValueError("A3 normalized 126/2 source-frame boundary mismatch")
    successor = json.loads(SUCCESSOR.read_text(encoding="utf-8"))
    if successor.get("schema") != "ORION.A3.WorkflowHubTwoReplacementSuccessorDurableResult.v1":
        raise ValueError("A3 successor result schema mismatch")
    if successor.get("terminal") != "WORKFLOWHUB_TWO_REPLACEMENT_SUCCESSOR_CONTENT_BOUND":
        raise ValueError("A3 successor result is not content-bound")
    if successor.get("successor_frame_sha256") != EXPECTED_SUCCESSOR_FRAME_SHA256:
        raise ValueError("A3 successor frame digest mismatch")
    for row in successor.get("replacements", []):
        wid = str(row["workflow_id"])
        if wid in retained:
            raise ValueError(f"A3 replacement collides with retained family: {wid}")
        retained[wid] = row
    if len(retained) != 128 or len(set(retained)) != 128:
        raise ValueError("A3 successor source frame is not 128 unique families")
    return retained


# ---------------------------------------------------------------- network helpers (ported from A3)


def request_bytes(url: str, *, accept: str, timeout: float = 30.0, retries: int = 3) -> bytes:
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if getattr(response, "status", 200) != 200:
                    raise RuntimeError(f"HTTP {response.status} for {url}")
                return response.read(MAX_BYTES + 1)
        except (urllib.error.URLError, TimeoutError, RuntimeError) as exc:
            last = exc
            if attempt + 1 < retries:
                time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"failed to fetch {url}: {last}")


def fetch_json(url: str) -> Any:
    try:
        return json.loads(request_bytes(url, accept="application/json"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"non-JSON response from {url}") from exc


def fetch_all_tools(max_pages: int = 40, limit: int = 1000) -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = []
    offset = 0
    seen_offsets: set[int] = set()
    for _page in range(max_pages):
        if offset in seen_offsets:
            raise RuntimeError("TRS pagination repeated an offset")
        seen_offsets.add(offset)
        payload = fetch_json(f"{TRS_TOOLS}?limit={limit}&offset={offset}")
        if not isinstance(payload, list):
            raise RuntimeError("TRS /tools did not return a list")
        tools.extend(item for item in payload if isinstance(item, dict))
        if not payload or len(payload) < limit:
            break
        offset += len(payload)
    else:
        raise RuntimeError("TRS pagination hit max_pages before exhaustion")
    return tools


def integer_versions(tool: dict[str, Any]) -> list[int]:
    out: set[int] = set()
    for v in tool.get("versions") or []:
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
    docs = []
    for m in SCRIPT_JSONLD.findall(text):
        try:
            docs.append(json.loads(html.unescape(m).strip()))
        except json.JSONDecodeError:
            continue
    if not docs:
        raise RuntimeError("landing page exposes no parseable application/ld+json metadata")
    for doc in docs:
        if "ComputationalWorkflow" in json.dumps(doc, sort_keys=True) or "SoftwareSourceCode" in json.dumps(doc, sort_keys=True):
            return doc
    return docs[0]


def find_license(obj: Any) -> str | None:
    if isinstance(obj, dict):
        value = obj.get("license")
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, dict):
            for key in ("@id", "identifier", "name"):
                val = value.get(key)
                if isinstance(val, str) and val.strip():
                    return val.strip()
        for sub in obj.values():
            got = find_license(sub)
            if got:
                return got
    elif isinstance(obj, list):
        for sub in obj:
            got = find_license(sub)
            if got:
                return got
    return None


def fetch_license(tool_id: str, version_id: int) -> tuple[str, str]:
    url = LANDING.format(tool_id=urllib.parse.quote(tool_id, safe=""), version_id=version_id)
    doc = extract_jsonld(request_bytes(url, accept="application/ld+json,text/html;q=0.8"))
    license_value = find_license(doc)
    if not license_value:
        raise RuntimeError("missing licence in version landing metadata")
    return license_value, canonical_json_sha(doc)


# ---------------------------------------------------------------- RO-Crate normalized binding (ported from A3)


def read_limited(response: Any, max_bytes: int = MAX_BYTES) -> bytes:
    declared = response.headers.get("Content-Length")
    if declared is not None and int(declared) > max_bytes:
        raise ValueError(f"RO-Crate Content-Length exceeds {max_bytes} bytes")
    data = response.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError(f"RO-Crate exceeds {max_bytes} bytes")
    return data


def canonical_member_path(name: str) -> str:
    if not name or "\\" in name:
        raise ValueError(f"non-canonical ZIP member path: {name!r}")
    p = PurePosixPath(name)
    if p.is_absolute() or ".." in p.parts or "." in p.parts:
        raise ValueError(f"unsafe ZIP member path: {name!r}")
    rendered = p.as_posix()
    if rendered != name.rstrip("/"):
        raise ValueError(f"non-canonical ZIP member path: {name!r}")
    return rendered


def member_semantics(info: zipfile.ZipInfo) -> tuple[str, bool]:
    mode = (info.external_attr >> 16) & 0xFFFF
    kind_bits = stat.S_IFMT(mode)
    kind = "symlink" if kind_bits == stat.S_IFLNK else ("regular" if kind_bits in (0, stat.S_IFREG) else f"other:{kind_bits:o}")
    return kind, bool(mode & 0o111)


def normalized_content_manifest(zf: zipfile.ZipFile) -> tuple[list[dict[str, Any]], bytes]:
    seen: set[str] = set()
    entries: list[dict[str, Any]] = []
    metadata_bytes: bytes | None = None
    metadata_count = 0
    for info in zf.infolist():
        path = canonical_member_path(info.filename)
        if path in seen:
            raise ValueError(f"duplicate ZIP member path: {path}")
        seen.add(path)
        if info.is_dir():
            continue
        data = zf.read(info)
        kind, executable = member_semantics(info)
        entries.append({"path": path, "bytes": len(data), "sha256": sha256_bytes(data), "kind": kind, "executable": executable})
        if path == "ro-crate-metadata.json":
            metadata_count += 1
            metadata_bytes = data
    if metadata_count != 1 or metadata_bytes is None:
        raise ValueError("RO-Crate zip must contain exactly one root ro-crate-metadata.json")
    entries.sort(key=lambda x: x["path"])
    return entries, metadata_bytes


def validate_rocrate_bytes(data: bytes) -> dict[str, Any]:
    if not data:
        raise ValueError("empty RO-Crate response")
    try:
        with zipfile.ZipFile(io.BytesIO(data), "r") as zf:
            if zf.testzip() is not None:
                raise ValueError("RO-Crate zip CRC failure")
            entries, metadata = normalized_content_manifest(zf)
    except zipfile.BadZipFile as exc:
        raise ValueError("response is not a valid ZIP") from exc
    return {
        "normalized_content_manifest_sha256": canonical_json_sha(entries),
        "ro_crate_metadata_sha256": sha256_bytes(metadata),
        "normalized_member_count": len(entries),
    }


def fetch_rocrate_binding(workflow_id: str, version: int, retries: int = 3, timeout: float = 120.0) -> dict[str, Any]:
    url = f"https://workflowhub.eu/workflows/{urllib.parse.quote(workflow_id, safe='')}/ro_crate?version={version}"
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if getattr(resp, "status", 200) != 200:
                    raise RuntimeError(f"HTTP {resp.status}")
                data = read_limited(resp)
                result = validate_rocrate_bytes(data)
                result["url"] = url
                return result
        except (urllib.error.URLError, TimeoutError, RuntimeError, ValueError, OSError) as exc:
            last = exc
            if attempt + 1 < retries:
                time.sleep(0.75 * (attempt + 1))
    raise RuntimeError(f"failed RO-Crate fetch after {retries} attempts: {last}")


# ---------------------------------------------------------------- A6 row assembly


def build_row(workflow_id: str, name: str | None, org_lineage: str, org_name: str | None, vb: int, va: int,
              lic_b: str, lic_a: str, meta_b: str, meta_a: str, before_sha: str, after_sha: str,
              provenance: str, a3_frame_sha: str | None) -> dict[str, Any]:
    row = {
        "packet_id": f"a6-s2-wh-{workflow_id}",
        "stratum": STRATUM,
        "source_family_id": f"workflowhub:workflow:{workflow_id}",
        "normalized_organization_lineage": org_lineage,
        "artifact_lineage_id": f"workflowhub:workflow-artifact:{workflow_id}",
        "before_version_id": str(vb),
        "after_version_id": str(va),
        "before_sha256": before_sha,
        "after_sha256": after_sha,
        "license_or_rights_receipt_id": (
            f"a3-workflowhub-normalized-content-binding-v2+successor-v1:workflow:{workflow_id}"
            if provenance == "A3_FROZEN_FRAME_REUSE"
            else f"a6-workflowhub-census-v1:landing-metadata:{meta_b}/{meta_a}"
        ),
        "license_before": lic_b,
        "license_after": lic_a,
        "workflow_name": name,
        "organization_name": org_name,
        "content_binding_provenance": provenance,
    }
    if a3_frame_sha:
        row["a3_successor_frame_sha256"] = a3_frame_sha
    return row


def bind_new_family(tool: dict[str, Any], a3_frame: dict[str, dict[str, Any]]) -> dict[str, Any]:
    tool_id = str(tool.get("id"))
    versions = integer_versions(tool)
    before, after = versions[-2], versions[-1]
    org_lineage, org_name = organization_lineage(tool, tool_id)
    lic_b, meta_b = fetch_license(tool_id, before)
    time.sleep(0.05)
    lic_a, meta_a = fetch_license(tool_id, after)
    time.sleep(0.05)
    crate_b = fetch_rocrate_binding(tool_id, before)
    crate_a = fetch_rocrate_binding(tool_id, after)
    if crate_b["normalized_content_manifest_sha256"] == crate_a["normalized_content_manifest_sha256"]:
        return {"workflow_id": tool_id, "status": "UNCHANGED_NORMALIZED_CONTENT"}
    return {
        "status": "BOUND",
        "row": build_row(
            tool_id, tool.get("name"), org_lineage, org_name, before, after, lic_b, lic_a, meta_b, meta_a,
            crate_b["normalized_content_manifest_sha256"], crate_a["normalized_content_manifest_sha256"],
            "A6_FRESH_ROCRATE_BINDING", None,
        ),
    }


def organization_lineage(tool: dict[str, Any], tool_id: str) -> tuple[str, str | None]:
    org = tool.get("organization")
    if isinstance(org, str) and org.strip():
        return f"workflowhub:organization:{slugify(org)}", org.strip()
    if isinstance(org, dict):
        for key in ("id", "name"):
            val = org.get(key)
            if isinstance(val, str) and val.strip():
                return f"workflowhub:organization:{slugify(val)}", val.strip()
    return f"workflowhub:workflow-owner:{tool_id}", None


def census(max_new_bindings: int, workers: int) -> dict[str, Any]:
    a3_frame = load_a3_source_frame()
    tools = fetch_all_tools()
    ids = [str(t.get("id")) for t in tools]
    if len(ids) != len(set(ids)):
        raise RuntimeError("TRS /tools returned duplicate tool IDs")
    tools.sort(key=lambda t: (int(str(t.get("id"))) if str(t.get("id")).isdigit() else 10**18, str(t.get("id"))))

    rows: list[dict[str, Any]] = []
    reused_ids: list[str] = []
    multiversion_total = 0
    unchanged: list[str] = []
    failures: list[dict[str, str]] = []
    fresh_tools: list[dict[str, Any]] = []
    for tool in tools:
        versions = integer_versions(tool)
        if len(versions) < 2:
            continue
        multiversion_total += 1
        tool_id = str(tool.get("id"))
        frozen = a3_frame.get(tool_id)
        if frozen is not None:
            org_lineage, org_name = organization_lineage(tool, tool_id)
            rows.append(build_row(
                tool_id, tool.get("name"), org_lineage, org_name,
                frozen["version_before"], frozen["version_after"],
                frozen["license_before"], frozen["license_after"],
                frozen.get("metadata_sha256_before", ""), frozen.get("metadata_sha256_after", ""),
                frozen["before_normalized_sha256"], frozen["after_normalized_sha256"],
                "A3_FROZEN_FRAME_REUSE", EXPECTED_SUCCESSOR_FRAME_SHA256,
            ))
            reused_ids.append(tool_id)
        else:
            if len(fresh_tools) < max_new_bindings:
                fresh_tools.append(tool)

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(bind_new_family, tool, a3_frame): str(tool.get("id")) for tool in fresh_tools}
        for future in concurrent.futures.as_completed(futures):
            wid = futures[future]
            try:
                result = future.result()
            except Exception as exc:  # recorded as CANNOT_CHECK-style failure, never padded
                failures.append({"workflow_id": wid, "reason": str(exc)[:240]})
                continue
            if result["status"] == "BOUND":
                rows.append(result["row"])
            else:
                unchanged.append(wid)

    rows.sort(key=lambda r: int(r["packet_id"].rsplit("-", 1)[1]))
    org_lineages = sorted({r["normalized_organization_lineage"] for r in rows})
    fresh_rows = [r for r in rows if r["content_binding_provenance"] == "A6_FRESH_ROCRATE_BINDING"]
    return {
        "schema": "ORION.A6.Stratum2WorkflowHubTransitionCensusResult.v1",
        "stratum": STRATUM,
        "trs_tools_seen": len(tools),
        "multiversion_workflow_families_seen": multiversion_total,
        "a3_frozen_frame_reused_n": len(reused_ids),
        "a3_successor_frame_sha256": EXPECTED_SUCCESSOR_FRAME_SHA256,
        "fresh_rocrate_bound_n": len(fresh_rows),
        "unchanged_normalized_content_excluded_n": len(unchanged),
        "cannot_check_binding_failure_n": len(failures),
        "cannot_check_binding_failures": failures,
        "packet_candidate_n": len(rows),
        "distinct_normalized_organization_lineage_n": len(org_lineages),
        "distinct_source_family_n": len({r["source_family_id"] for r in rows}),
        "distinct_artifact_lineage_n": len({r["artifact_lineage_id"] for r in rows}),
        "packet_candidates": rows,
        "stratum_eligibility_adjudicated": False,
        "gold_adjudicated": False,
        "protected_orion_predictions_accessed": False,
        "scientific_authority_delta": "NONE__OUTCOME_BLIND_SOURCE_CENSUS_ONLY",
    }


# ---------------------------------------------------------------- snapshot writing


def write_snapshot(result: dict[str, Any], chunk_size: int = 100) -> dict[str, Any]:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    rows = result.pop("packet_candidates")
    result.pop("cannot_check_binding_failures")
    chunks = []
    for i in range(0, len(rows), chunk_size):
        part = rows[i:i + chunk_size]
        name = f"ROWS_{i + 1:03d}_{i + len(part):03d}.json"
        path = SNAPSHOT_DIR / name
        path.write_text(json.dumps({"schema": "ORION.A6.Stratum2CensusChunk.v1", "rows": part}, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        chunks.append({
            "path": str(path.relative_to(ROOT)),
            "rows": len(part),
            "sha256": sha256_bytes(path.read_bytes()),
        })
    combined = canonical_json_sha(rows)
    capacity = result["packet_candidate_n"] >= 20 and result["distinct_normalized_organization_lineage_n"] >= 20
    manifest = {
        **result,
        "chunks": chunks,
        "packet_candidate_rows_sha256": combined,
        "decision": (
            "A6_STRATUM2_WORKFLOWHUB_TRANSITION_CAPACITY_AT_LEAST_20_DISJOINT_ORG_LINEAGES"
            if capacity else "CANNOT_CHECK_A6_STRATUM2_CAPACITY_OR_DISJOINT_ORG_LINEAGES"
        ),
        "quota_note": "capacity statement only; the 20/20/20 primary quota and replication quota stay unallocated until the eligible pool and externally frozen replication quotas exist",
    }
    manifest_path = SNAPSHOT_DIR / "A6_STRATUM2_CENSUS_MANIFEST_V1.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


# ---------------------------------------------------------------- self-test (offline)


def make_zip(entries: list[tuple[str, bytes]], *, compression: int, date: tuple[int, int, int, int, int, int]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=compression) as zf:
        for name, payload in entries:
            info = zipfile.ZipInfo(name, date_time=date)
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.compress_type = compression
            zf.writestr(info, payload)
    return buf.getvalue()


def self_test() -> dict[str, Any]:
    entries = [("ro-crate-metadata.json", b"{}"), ("workflow.cwl", b"cwlVersion: v1.2\n")]
    z1 = make_zip(entries, compression=zipfile.ZIP_STORED, date=(2020, 1, 1, 0, 0, 0))
    z2 = make_zip(list(reversed(entries)), compression=zipfile.ZIP_DEFLATED, date=(2026, 1, 1, 0, 0, 0))
    d1, d2 = validate_rocrate_bytes(z1), validate_rocrate_bytes(z2)
    assert d1["normalized_content_manifest_sha256"] == d2["normalized_content_manifest_sha256"]
    changed = make_zip([("ro-crate-metadata.json", b"{}"), ("workflow.cwl", b"changed\n")], compression=zipfile.ZIP_DEFLATED, date=(2026, 1, 1, 0, 0, 0))
    assert validate_rocrate_bytes(changed)["normalized_content_manifest_sha256"] != d1["normalized_content_manifest_sha256"]
    assert slugify("GalaxyProject SARS-CoV-2") == "galaxyproject-sars-cov-2"
    assert slugify("  École // Polytechnique  ") == "cole-polytechnique"
    assert slugify(None) == "unattributed"
    assert organization_lineage({"organization": "GalaxyProject SARS-CoV-2"}, "9") == ("workflowhub:organization:galaxyproject-sars-cov-2", "GalaxyProject SARS-CoV-2")
    assert organization_lineage({}, "77")[0] == "workflowhub:workflow-owner:77"
    assert integer_versions({"versions": [{"id": "1"}, {"id": 2}, {"id": 2}]}) == [1, 2]
    doc = {"@type": ["SoftwareSourceCode", "ComputationalWorkflow"], "license": {"@id": "https://spdx.org/licenses/MIT"}}
    assert find_license(doc) == "https://spdx.org/licenses/MIT"
    row = build_row("625", "w", "workflowhub:organization:x", "X", 30, 31, "L1", "L1", "mb", "ma", "b" * 64, "a" * 64, "A3_FROZEN_FRAME_REUSE", "f" * 64)
    assert row["packet_id"] == "a6-s2-wh-625" and row["stratum"] == STRATUM
    assert row["license_or_rights_receipt_id"].startswith("a3-workflowhub-normalized-content-binding-v2")
    fresh = build_row("999", "w", "workflowhub:organization:y", "Y", 1, 2, "L1", "L1", "mb", "ma", "b" * 64, "a" * 64, "A6_FRESH_ROCRATE_BINDING", None)
    assert fresh["license_or_rights_receipt_id"].startswith("a6-workflowhub-census-v1:landing-metadata:")
    assert "a3_successor_frame_sha256" not in fresh
    frame = load_a3_source_frame()
    assert len(frame) == 128
    return {
        "decision": "GREEN",
        "a3_frozen_frame_verified_n": len(frame),
        "zip_nuisance_normalized": True,
        "semantic_change_detected": True,
        "network_accessed": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--max-new-bindings", type=int, default=200)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--no-snapshot", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        result = self_test()
        code = 0
    else:
        if not 1 <= args.workers <= 2:
            ap.error("--workers must be 1..2")
        result = census(args.max_new_bindings, args.workers)
        if not args.no_snapshot:
            result = write_snapshot(result)
        code = 0 if result.get("decision", "CAPACITY_OK").startswith(("A6_STRATUM2", "CAPACITY_OK")) else 2
    print(json.dumps(result, indent=2, sort_keys=True)[:200000])
    return code


if __name__ == "__main__":
    raise SystemExit(main())
