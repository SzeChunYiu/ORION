#!/usr/bin/env python3
"""One post-discovery, outcome-blind reproduction of the V14 source identity gate."""

import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


LANE = Path(__file__).resolve().parent
ROOT = LANE.parents[1]
ONLINE = LANE / "ONLINE_SOURCE_RECEIPT_V14.json"
GATE = LANE / "IDENTITY_MISMATCH_GATE_RECEIPT_V14.json"
TERMINAL = (
    "P2_V14_FROZEN_INDEX_IDENTITY_MISMATCH__PINNED_COMMIT_PATH_RESOLVES_"
    "F4F5007_BLOB_SHA256_F34C17B3__EXPECTED_ADA2668_BLOB_SHA256_5D829C66_"
    "BELONGS_TO_DC2DADF__STOP_BEFORE_CENSUS_AND_PERFORMANCE"
)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    return sha256_bytes(path.read_bytes())


def git_blob_sha1(data):
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def load(name):
    return json.loads((LANE / name).read_text())


def must(condition, message):
    if not condition:
        raise AssertionError(message)


def selected_headers(headers):
    wanted = (
        "content-length",
        "content-type",
        "etag",
        "last-modified",
        "x-github-request-id",
    )
    return {key: headers.get(key) for key in wanted if headers.get(key) is not None}


def fetch(url, accept):
    request = urllib.request.Request(
        url,
        headers={
            "Accept": accept,
            "User-Agent": "ORION-P2-V14-source-identity-gate",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read()
        return body, {
            "requested_url": url,
            "final_url": response.geturl(),
            "http_status": response.status,
            "response_headers": selected_headers(response.headers),
            "response_bytes": len(body),
            "response_sha256": sha256_bytes(body),
        }


def route_receipt(repository, commit, path, requests):
    api = f"https://api.github.com/repos/{repository}"
    commit_url = f"{api}/git/commits/{commit}"
    commit_body, commit_request = fetch(commit_url, "application/vnd.github+json")
    requests.append({"kind": "commit_metadata", **commit_request})
    commit_json = json.loads(commit_body)
    must(commit_json["sha"] == commit, "commit identity")
    tree_sha = commit_json["tree"]["sha"]

    tree_url = f"{api}/git/trees/{tree_sha}?recursive=1"
    tree_body, tree_request = fetch(tree_url, "application/vnd.github+json")
    requests.append({"kind": "root_tree", **tree_request})
    tree_json = json.loads(tree_body)
    must(tree_json["sha"] == tree_sha, "root tree identity")
    must(tree_json.get("truncated") is False, "complete root tree")
    entries = [item for item in tree_json["tree"] if item["path"] == path]
    must(len(entries) == 1, "one index entry")
    entry = entries[0]
    must(entry["type"] == "blob", "index is blob")

    raw_url = f"https://raw.githubusercontent.com/{repository}/{commit}/{path}"
    raw_body, raw_request = fetch(raw_url, "application/octet-stream")
    requests.append({"kind": "raw_index_bytes_not_retained", **raw_request})
    raw = {
        "bytes": len(raw_body),
        "sha256": sha256_bytes(raw_body),
        "git_blob_sha1": git_blob_sha1(raw_body),
        "body_retained": False,
        "body_parsed": False,
    }
    must(raw["git_blob_sha1"] == entry["sha"], "raw/tree blob identity")
    return {
        "repository": repository,
        "commit": commit,
        "commit_api_url": commit_url,
        "root_tree_sha1": tree_sha,
        "root_tree_api_url": tree_url,
        "index_path": path,
        "tree_entry": {
            "mode": entry["mode"],
            "type": entry["type"],
            "git_blob_sha1": entry["sha"],
            "bytes": entry["size"],
            "api_url": entry["url"],
        },
        "raw_url": raw_url,
        "raw_identity": raw,
    }


def main():
    must(not ONLINE.exists() and not GATE.exists(), "V14 gate outputs already exist")
    protocol = load("PROTOCOL_V14.json")
    freeze = load("PROTOCOL_FREEZE_RECEIPT_V14.json")
    must(sha256_file(LANE / "PROTOCOL_V14.json") == freeze["protocol_sha256"], "protocol freeze")
    must(sha256_file(Path(__file__)) == freeze["runner_sha256"], "runner freeze")

    repository = protocol["frozen_first_route"]["repository"]
    path = protocol["frozen_first_route"]["index_path"]
    requests = []
    frozen = route_receipt(repository, protocol["frozen_first_route"]["commit"], path, requests)
    owner = route_receipt(repository, protocol["historical_corroboration_target"]["commit"], path, requests)
    must(len(requests) == protocol["single_post_discovery_reproducibility_gate"]["network_requests"], "request count")

    frozen_expected = protocol["frozen_first_route"]
    owner_expected = protocol["historical_corroboration_target"]
    frozen_observed = frozen["raw_identity"]
    owner_observed = owner["raw_identity"]
    frozen_route_passed = (
        frozen["tree_entry"]["git_blob_sha1"] == frozen_expected["expected_index_git_blob_sha1"]
        and frozen["tree_entry"]["bytes"] == frozen_expected["expected_index_bytes"]
        and frozen_observed["sha256"] == frozen_expected["expected_index_sha256"]
        and frozen_observed["git_blob_sha1"] == frozen_expected["expected_index_git_blob_sha1"]
        and frozen_observed["bytes"] == frozen_expected["expected_index_bytes"]
    )
    owner_provenance_passed = (
        owner["tree_entry"]["git_blob_sha1"] == owner_expected["expected_index_git_blob_sha1"]
        and owner["tree_entry"]["bytes"] == owner_expected["expected_index_bytes"]
        and owner_observed["sha256"] == owner_expected["expected_index_sha256"]
        and owner_observed["git_blob_sha1"] == owner_expected["expected_index_git_blob_sha1"]
        and owner_observed["bytes"] == owner_expected["expected_index_bytes"]
    )
    must(not frozen_route_passed, "expected frozen route identity mismatch")
    must(owner_provenance_passed, "expected bytes owner provenance")

    fetched_at = datetime.now(timezone.utc).isoformat()
    online = {
        "schema_version": "orion.p2.state-expanding-acquisition.online-source-receipt.v14",
        "fetched_at_utc": fetched_at,
        "official_gate_execution_number": 1,
        "pre_freeze_source_probes": "NONZERO_NOT_INDEPENDENTLY_AUDITED",
        "network_requests_in_official_gate": len(requests),
        "requests": requests,
        "raw_index_bodies_parsed": False,
        "raw_index_bodies_retained": False,
        "label_values_or_class_counts_inspected_or_retained": False,
        "review_csv_requests": 0,
    }
    ONLINE.write_text(json.dumps(online, indent=2, sort_keys=True) + "\n")

    gate = {
        "schema_version": "orion.p2.state-expanding-acquisition.identity-mismatch-gate-receipt.v14",
        "executed_at_utc": fetched_at,
        "gate_id": "G1_COMMIT_TREE_BLOB_INDEX_IDENTITY",
        "diagnostic_reproduction_passed": True,
        "frozen_route_acquisition_passed": False,
        "causal_code": "FROZEN_INDEX_SHA_DOES_NOT_MATCH_PINNED_COMMIT_PATH",
        "frozen_route": frozen,
        "frozen_expected_identity": {
            "bytes": frozen_expected["expected_index_bytes"],
            "git_blob_sha1": frozen_expected["expected_index_git_blob_sha1"],
            "sha256": frozen_expected["expected_index_sha256"],
        },
        "historical_owner_route": owner,
        "historical_expected_identity": {
            "bytes": owner_expected["expected_index_bytes"],
            "git_blob_sha1": owner_expected["expected_index_git_blob_sha1"],
            "sha256": owner_expected["expected_index_sha256"],
        },
        "historical_owner_provenance_passed": owner_provenance_passed,
        "historical_owner_authorized_as_v14_substitute": False,
        "stopped_before_index_parse": True,
        "stopped_before_review_census": True,
        "stopped_before_review_csv_download": True,
        "stopped_before_labels_models_rankings_metrics": True,
        "terminal": TERMINAL,
    }
    GATE.write_text(json.dumps(gate, indent=2, sort_keys=True) + "\n")
    print(TERMINAL)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"P2_V14_IDENTITY_GATE_ERROR__{type(exc).__name__}__{exc}", file=sys.stderr)
        raise
