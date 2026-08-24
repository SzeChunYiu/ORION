#!/usr/bin/env python3
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"
PROTOCOL_SHA256 = "a492bf47620651b35542b64ac9bc1da115ef793d0998e14a3fa43ab98f64c29c"
API = "https://api.github.com/repos/asreview/synergy-dataset"


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha_bytes(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def request(name: str, url: str) -> tuple[int, bytes, dict]:
    started = now()
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "orion-p2-v15-coherent-snapshot-qualification",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    error = None
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            status = response.status
            body = response.read()
            final_url = response.geturl()
            headers = response.headers
    except urllib.error.HTTPError as exc:
        status = exc.code
        body = exc.read()
        final_url = exc.geturl()
        headers = exc.headers
        error = f"HTTPError: {exc.code} {exc.reason}"
    retained_headers = {
        key.lower(): value
        for key, value in headers.items()
        if key.lower()
        in {
            "content-type",
            "etag",
            "last-modified",
            "x-github-request-id",
            "x-ratelimit-limit",
            "x-ratelimit-remaining",
            "x-ratelimit-reset",
        }
    }
    body_path = EVIDENCE / f"{name}.body"
    body_path.write_bytes(body)
    receipt = {
        "name": name,
        "url": url,
        "final_url": final_url,
        "started_at": started,
        "finished_at": now(),
        "status": status,
        "error": error,
        "headers": retained_headers,
        "body_path": f"evidence/{body_path.name}",
        "body_bytes": len(body),
        "body_sha256": sha_bytes(body),
    }
    write_json(EVIDENCE / f"{name}.receipt.json", receipt)
    return status, body, receipt


EVIDENCE.mkdir(exist_ok=True)
protocol = json.loads((ROOT / "PROTOCOL_V15.json").read_text())
freeze = json.loads((ROOT / "PROTOCOL_FREEZE_RECEIPT_V15.json").read_text())
assert sha(ROOT / "PROTOCOL_V15.json") == freeze["protocol_sha256"] == PROTOCOL_SHA256
frozen = protocol["coherent_single_snapshot_repair"]
commit = frozen["commit"]
tree_sha = frozen["root_tree_sha1"]
index_digest = frozen["index_sha256"]
urls = [
    ("github_commit", f"{API}/git/commits/{commit}"),
    ("github_recursive_tree", f"{API}/git/trees/{tree_sha}?recursive=1"),
    ("github_license", f"{API}/license?ref={commit}"),
    ("github_repository", API),
    ("github_releases", f"{API}/releases?per_page=100"),
    ("github_tag_refs", f"{API}/git/matching-refs/tags/"),
    ("github_index_attestation", f"{API}/attestations/sha256:{index_digest}"),
]
requests = []
bodies: dict[str, object] = {}
for name, url in urls:
    status, body, receipt = request(name, url)
    requests.append(receipt)
    parsed = None
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        pass
    bodies[name] = parsed

commit_body = bodies["github_commit"] if isinstance(bodies["github_commit"], dict) else {}
tree_body = bodies["github_recursive_tree"] if isinstance(bodies["github_recursive_tree"], dict) else {}
tree_entries = tree_body.get("tree", []) if isinstance(tree_body.get("tree"), list) else []
index_entries = [entry for entry in tree_entries if entry.get("path") == frozen["index_path"]]
blob_entries = [entry for entry in tree_entries if entry.get("type") == "blob"]
dataset_entries = [
    entry
    for entry in blob_entries
    if entry.get("path", "").lower().endswith(".csv")
    and (
        entry.get("path", "").startswith("datasets/")
        or entry.get("path", "").startswith("dataset/")
        or "/datasets/" in entry.get("path", "")
        or "/dataset/" in entry.get("path", "")
    )
]
dataset_manifest = [
    {
        "path": entry["path"],
        "mode": entry.get("mode"),
        "git_blob_sha1": entry.get("sha"),
        "bytes": entry.get("size"),
    }
    for entry in sorted(dataset_entries, key=lambda item: item["path"])
]
license_entries = [
    {
        "path": entry["path"],
        "mode": entry.get("mode"),
        "git_blob_sha1": entry.get("sha"),
        "bytes": entry.get("size"),
    }
    for entry in blob_entries
    if Path(entry.get("path", "")).name.lower().startswith(("license", "copying"))
]
license_body = bodies["github_license"] if isinstance(bodies["github_license"], dict) else {}
license_decoded = b""
if isinstance(license_body.get("content"), str) and license_body.get("encoding") == "base64":
    license_decoded = base64.b64decode(license_body["content"], validate=False)
repository_body = bodies["github_repository"] if isinstance(bodies["github_repository"], dict) else {}
releases_body = bodies["github_releases"] if isinstance(bodies["github_releases"], list) else []
tags_body = bodies["github_tag_refs"] if isinstance(bodies["github_tag_refs"], list) else []
attestation_body = bodies["github_index_attestation"]

commit_tree_pass = commit_body.get("sha") == commit and commit_body.get("tree", {}).get("sha") == tree_sha
verification = commit_body.get("verification") if isinstance(commit_body.get("verification"), dict) else {}
signature_valid = verification.get("verified") is True
recursive_tree_pass = tree_body.get("sha") == tree_sha and tree_body.get("truncated") is False
index_tree_pass = index_entries == [
    {
        "path": frozen["index_path"],
        "mode": "100644",
        "type": "blob",
        "sha": frozen["index_git_blob_sha1"],
        "size": frozen["index_bytes"],
        "url": index_entries[0]["url"] if len(index_entries) == 1 else None,
    }
]
license_pass = (
    next(item for item in requests if item["name"] == "github_license")["status"] == 200
    and license_body.get("sha") is not None
    and len(license_decoded) > 0
    and license_body.get("license", {}).get("spdx_id") not in {None, "NOASSERTION"}
)
attestation_status = next(
    item["status"] for item in requests if item["name"] == "github_index_attestation"
)
contract_identity = protocol["identity"]
provider_contract_predicate = False
if attestation_status == 200 and isinstance(attestation_body, dict):
    provider_contract_predicate = contract_identity in json.dumps(attestation_body, sort_keys=True)

qualification = {
    "schema_version": "orion.p2.state-expanding-acquisition.v15.provider-qualification",
    "protocol_sha256": PROTOCOL_SHA256,
    "coherent_snapshot": frozen,
    "commit": {
        "status": next(item["status"] for item in requests if item["name"] == "github_commit"),
        "sha": commit_body.get("sha"),
        "tree_sha1": commit_body.get("tree", {}).get("sha"),
        "verification": verification,
        "commit_tree_pass": commit_tree_pass,
        "signature_valid": signature_valid,
    },
    "recursive_tree": {
        "status": next(item["status"] for item in requests if item["name"] == "github_recursive_tree"),
        "sha": tree_body.get("sha"),
        "truncated": tree_body.get("truncated"),
        "entry_count": len(tree_entries),
        "blob_count": len(blob_entries),
        "pass": recursive_tree_pass,
    },
    "index_entry": {
        "matching_entry_count": len(index_entries),
        "entry": index_entries[0] if len(index_entries) == 1 else None,
        "pass": index_tree_pass,
        "body_requested": False,
        "json_parsed": False,
    },
    "same_snapshot_dataset_path_manifest": {
        "count": len(dataset_manifest),
        "manifest": dataset_manifest,
        "bodies_requested": False,
        "labels_or_class_counts_inspected": False,
    },
    "rights_witness": {
        "status": next(item["status"] for item in requests if item["name"] == "github_license"),
        "api_path": license_body.get("path"),
        "git_blob_sha1": license_body.get("sha"),
        "decoded_bytes": len(license_decoded),
        "decoded_sha256": sha_bytes(license_decoded) if license_decoded else None,
        "license": license_body.get("license"),
        "tree_license_entries": license_entries,
        "repository_api_license": repository_body.get("license"),
        "pass": license_pass,
        "boundary": "Repository-level license witness only; per-review third-party dataset rights remain for the independent custodian.",
    },
    "provider_relations": {
        "release_count": len(releases_body),
        "releases": [
            {
                "id": row.get("id"),
                "tag_name": row.get("tag_name"),
                "target_commitish": row.get("target_commitish"),
                "draft": row.get("draft"),
                "prerelease": row.get("prerelease"),
                "asset_count": len(row.get("assets", [])),
            }
            for row in releases_body
        ],
        "tag_ref_count": len(tags_body),
        "tag_refs": [
            {"ref": row.get("ref"), "object": row.get("object")} for row in tags_body
        ],
        "index_attestation_status": attestation_status,
        "v15_contract_predicate_present": provider_contract_predicate,
    },
    "gates": {
        "coherent_commit_tree": commit_tree_pass,
        "provider_signature_valid": signature_valid,
        "recursive_tree_complete": recursive_tree_pass,
        "coherent_index_tree_entry": index_tree_pass,
        "same_snapshot_dataset_path_manifest_nonempty": len(dataset_manifest) > 0,
        "repository_rights_witness": license_pass,
        "provider_native_v15_contract_predicate": provider_contract_predicate,
        "independent_source_custody": provider_contract_predicate,
    },
    "widest_positive": "Provider-authenticated coherent same-snapshot metadata only; generic signature/rights/path witnesses are not independent V15 contract custody.",
}
write_json(ROOT / "PROVIDER_QUALIFICATION_V15.json", qualification)

probe = {
    "schema_version": "orion.p2.state-expanding-acquisition.v15.probe-receipt",
    "protocol_sha256": PROTOCOL_SHA256,
    "finished_at_utc": now(),
    "request_count": len(requests),
    "requests": requests,
    "actions": {
        "network_requests": len(requests),
        "commit_json_parses": 1,
        "tree_json_parses": 1,
        "license_json_parses": 1,
        "repository_json_parses": 1,
        "release_json_parses": 1,
        "tag_json_parses": 1,
        "attestation_json_parses": 1 if isinstance(attestation_body, (dict, list)) else 0,
        "index_json_requests": 0,
        "index_json_parses": 0,
        "review_csv_requests": 0,
        "review_population_censuses": 0,
        "label_values_inspected_or_retained": False,
        "class_counts_inspected_or_retained": False,
        "learner_or_model_runs": 0,
        "ranking_or_metric_runs": 0,
        "pytest_or_repository_ci_runs": 0,
    },
}
write_json(ROOT / "PROBE_RECEIPT_V15.json", probe)
print(
    json.dumps(
        {
            "requests": len(requests),
            "coherent": commit_tree_pass and recursive_tree_pass and index_tree_pass,
            "signature_valid": signature_valid,
            "dataset_paths": len(dataset_manifest),
            "license_pass": license_pass,
            "independent_custody": provider_contract_predicate,
        },
        sort_keys=True,
    )
)
