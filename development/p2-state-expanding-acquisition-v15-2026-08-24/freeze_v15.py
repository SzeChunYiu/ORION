#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
V14 = ROOT.parent / "p2-state-expanding-acquisition-v14-2026-08-24"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert sha(V14 / "RESULT_V14.json") == "95496f053d762173285b9fbb436ff19bad08f47a82e278bb44715b565a0cd333"
assert sha(V14 / "SHA256SUMS") == "8bb23e1c91d59328b64c70fc04af39840c78830f4d4cea1d588f2698495234e6"
assert sha(V14 / "NEXT_DISCRIMINATOR_V15.json") == "a4b56974558bf93692ca13aa90ccb9839466636b352a1eab90e67774e989e0b6"
head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, check=True, capture_output=True, text=True).stdout.strip()
frozen_at = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
commit = "38b35218e4d0f99621cec5a8a25a0147bb88c654"
tree = "49f437c367cc45a90867418fcef77c9ff3614456"
index_blob = "f4f5007156cb71e7d54e99057037fb75d44f87c4"
index_sha256 = "f34c17b3dca9d609585e5fcc9d24c5433d4ad240ef91e5c2e9a48edee1e0959a"
protocol = {
    "schema_version": "orion.p2.state-expanding-acquisition.v15.protocol",
    "identity": "P2_V15_COHERENT_SINGLE_COMMIT_INDEX_AND_DATASET_LOCK_WITH_PROVIDER_QUALIFICATION",
    "frozen_at_utc": frozen_at,
    "repository_head_at_freeze": head,
    "outcome_informed": True,
    "historical_results_immutable": True,
    "predecessor": {
        "result_path": "development/p2-state-expanding-acquisition-v14-2026-08-24/RESULT_V14.json",
        "result_sha256": sha(V14 / "RESULT_V14.json"),
        "sha256sums_sha256": sha(V14 / "SHA256SUMS"),
        "next_discriminator_sha256": sha(V14 / "NEXT_DISCRIMINATOR_V15.json"),
        "adverse_terminal": "P2_V14_FROZEN_INDEX_IDENTITY_MISMATCH__PINNED_COMMIT_PATH_RESOLVES_F4F5007_BLOB_SHA256_F34C17B3__EXPECTED_ADA2668_BLOB_SHA256_5D829C66_BELONGS_TO_DC2DADF__STOP_BEFORE_CENSUS_AND_PERFORMANCE",
    },
    "coherent_single_snapshot_repair": {
        "repository": "asreview/synergy-dataset",
        "commit": commit,
        "root_tree_sha1": tree,
        "index_path": "index_v1.json",
        "index_git_blob_sha1": index_blob,
        "index_bytes": 22135,
        "index_sha256": index_sha256,
        "candidate_dataset_template": f"https://raw.githubusercontent.com/asreview/synergy-dataset/{commit}/datasets/{{review_id}}.csv",
        "repair_boundary": "Preserve the V13/V14 frozen commit and candidate-dataset route; replace only the incompatible inherited index byte identity in this new protocol.",
    },
    "preserved_adverse_lineage": {
        "later_owner_commit": "dc2dadfdbb98eb1b4259604789abd640aa3b693e",
        "later_owner_tree": "217353505197c45a52cc0fa1eb0829e9c72c9a2c",
        "later_index_blob": "ada2668adfbb33d61e11a6bec02b10637e419bde",
        "later_index_bytes": 23118,
        "later_index_sha256": "5d829c669f744cc6e91165b15dd3364554320d684398b841764b2609bb857d4b",
        "substitution_allowed": False,
        "causal_code": "FROZEN_INDEX_SHA_DOES_NOT_MATCH_PINNED_COMMIT_PATH",
    },
    "custody_boundary": {
        "candidate_author_session_may_prepare_and_execute_provider_qualification": True,
        "candidate_author_session_may_self_attest_independence": False,
        "generic_commit_signature_is_snapshot_authentication_not_v15_contract_custody": True,
        "independent_source_population_custodian_required_before_index_parse_or_census": True,
        "independent_outcome_custodian_required_before_performance": True,
        "independent_result_verifier_required_after_performance": True,
    },
    "predeclared_provider_requests": [
        f"GET https://api.github.com/repos/asreview/synergy-dataset/git/commits/{commit}",
        f"GET https://api.github.com/repos/asreview/synergy-dataset/git/trees/{tree}?recursive=1",
        f"GET https://api.github.com/repos/asreview/synergy-dataset/license?ref={commit}",
        "GET https://api.github.com/repos/asreview/synergy-dataset",
        "GET https://api.github.com/repos/asreview/synergy-dataset/releases?per_page=100",
        "GET https://api.github.com/repos/asreview/synergy-dataset/git/matching-refs/tags/",
        f"GET https://api.github.com/repos/asreview/synergy-dataset/attestations/sha256:{index_sha256}",
    ],
    "provider_qualification_gates": {
        "commit_tree": f"Commit endpoint must return full commit {commit} with tree {tree}.",
        "signature": "Record GitHub verification exactly. A valid signature is a positive snapshot-authentication witness but cannot by itself sign the V15 selection/custody contract.",
        "recursive_tree": "The exact tree must be non-truncated, contain index_v1.json exactly once at blob f4f5007..., mode 100644 and 22,135 bytes, and expose a finite same-snapshot dataset path set without reading any dataset bytes.",
        "rights": "The official license endpoint must bind one tracked license blob to the same commit and expose an SPDX identity. Repository-level rights are retained as a snapshot witness only; they do not silently establish per-review third-party dataset rights.",
        "release_or_attestation": "Record any exact release/tag/attestation relation. Independent source custody passes only if a provider-native signed predicate explicitly binds the coherent tuple, same-snapshot candidate set, rights adjudication and no-route-switch V15 contract.",
    },
    "independent_source_custody_contract": [
        "Bind repository, commit, root tree, index path, index Git blob SHA-1, index bytes and SHA-256 as one exact tuple.",
        "Bind the complete same-snapshot candidate dataset path/blob manifest and the exact rights evidence required for every candidate before any index or dataset body is parsed.",
        "Attest that dc2dadf... and its index bytes are provenance only and cannot be substituted.",
        "Attest independence from candidate authorship and from any label, class-count, screening or model outcome.",
    ],
    "conditional_label_blind_census": {
        "authorized_only_if_independent_source_custody_passes": True,
        "rule": [
            "Parse the complete pinned index without retaining label values, class counts or model outcomes.",
            "Exclude every SWIFT, SYNERGY V5, KIFMS V7 and V9/V10 identity and every prior content identity.",
            "Require title, abstract, provider-native keywords, binary label schema and exact CC-BY-4.0 or CC0 rights.",
            "Require nonempty provider-native keywords; never impute keywords from title/abstract.",
            "Select the seven smallest eligible label-blind raw row counts, tie-breaking by review identity.",
        ],
    },
    "matched_performance_contract_unchanged": {
        "active_loop": "V10 exact",
        "u4": "title + abstract only",
        "keyword_only_u4_plus": "provider-native keywords only",
        "balancer": 9.8,
        "fallback": "exact u4 on any binding or signal failure",
        "costs": "all parsing, vectorization, fitting and ranking costs charged",
        "performance_authorized_in_provider_qualification": False,
    },
    "stop_rule": "If no provider-native predicate satisfies every independent source custody clause, stop before index JSON parsing, candidate CSV requests, review census, labels, class counts, models, rankings and metrics. Produce the narrowest custodian signature request; do not switch sources.",
    "widest_allowed_positive": "A coherent GitHub-authenticated same-snapshot commit/tree/index/dataset-path/rights witness. Unless the V15-specific independent custody predicate is signed, it is not an eligible seven-review population and grants no performance claim.",
    "forbidden": [
        "modify or reinterpret V13/V14 adverse history",
        "substitute commit dc2dadf... or another source",
        "parse or retain index JSON before custody",
        "request candidate review CSV bodies before custody",
        "inspect labels, class counts, outcomes or screening metrics",
        "run pytest or repository CI",
        "claim generic provider authentication as independent V15 contract custody",
    ],
}
ROOT.mkdir(parents=True, exist_ok=True)
protocol_path = ROOT / "PROTOCOL_V15.json"
protocol_path.write_text(json.dumps(protocol, indent=2, sort_keys=True) + "\n")
receipt = {
    "schema_version": "orion.p2.state-expanding-acquisition.v15.protocol-freeze-receipt",
    "identity": protocol["identity"],
    "frozen_at_utc": frozen_at,
    "repository_head_at_freeze": head,
    "outcome_informed": True,
    "predecessor_result_sha256": protocol["predecessor"]["result_sha256"],
    "protocol_path": protocol_path.name,
    "protocol_bytes": protocol_path.stat().st_size,
    "protocol_sha256": sha(protocol_path),
    "network_requests_before_freeze": 0,
    "index_json_parses_before_freeze": 0,
    "review_csv_requests_before_freeze": 0,
}
(ROOT / "PROTOCOL_FREEZE_RECEIPT_V15.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
print(json.dumps(receipt, sort_keys=True))
