#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
V14 = ROOT.parent / "p2-state-expanding-acquisition-v14-2026-08-24"
PROTOCOL_SHA256 = "a492bf47620651b35542b64ac9bc1da115ef793d0998e14a3fa43ab98f64c29c"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text())


def write_json(name: str, value: object) -> None:
    (ROOT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


protocol = load("PROTOCOL_V15.json")
freeze = load("PROTOCOL_FREEZE_RECEIPT_V15.json")
probe = load("PROBE_RECEIPT_V15.json")
qualification = load("PROVIDER_QUALIFICATION_V15.json")
assert sha(ROOT / "PROTOCOL_V15.json") == freeze["protocol_sha256"] == PROTOCOL_SHA256
assert sha(V14 / "RESULT_V14.json") == protocol["predecessor"]["result_sha256"]
assert qualification["gates"]["coherent_commit_tree"] is True
assert qualification["gates"]["coherent_index_tree_entry"] is True
assert qualification["gates"]["provider_signature_valid"] is True
assert qualification["gates"]["independent_source_custody"] is False

v14_protocol = json.loads((V14 / "PROTOCOL_V14.json").read_text())
v14_template = v14_protocol["frozen_first_route"]["seven_review_candidate_template"]
v15_frozen_template = protocol["coherent_single_snapshot_repair"]["candidate_dataset_template"]
assert v14_template == "https://raw.githubusercontent.com/asreview/synergy-dataset/38b35218e4d0f99621cec5a8a25a0147bb88c654/datasets/{review}/output/{review}.csv"
assert v15_frozen_template != v14_template
correction = {
    "schema_version": "orion.p2.state-expanding-acquisition.v15b.implementation-correction",
    "chronology": "The V15 provider gate completed before the candidate-template transcription error was checked against immutable V14. The frozen V15 protocol remains unchanged.",
    "v15_protocol_sha256": PROTOCOL_SHA256,
    "error": "FROZEN_V15_CANDIDATE_TEMPLATE_DIVERGES_FROM_IMMUTABLE_V14_TEMPLATE",
    "v15_frozen_template": v15_frozen_template,
    "immutable_v14_template": v14_template,
    "corrected_successor_template": v14_template,
    "scientific_effect": "No index or candidate body was requested, no census or outcome occurred, and the erroneous template was never executed. The seven provider metadata responses are not reinterpreted as prospective evidence under the correction.",
    "authorization": {
        "reuse_provider_metadata_as_descriptive_witness": True,
        "index_parse": False,
        "candidate_request": False,
        "census": False,
        "performance": False,
    },
}
write_json("IMPLEMENTATION_CORRECTION_V15B.json", correction)

dataset_manifest = qualification["same_snapshot_dataset_path_manifest"]["manifest"]
dataset_manifest_sha = canonical_sha(dataset_manifest)
custody_request = {
    "schema_version": "orion.p2.state-expanding-acquisition.v15.independent-source-custody-request",
    "contract_identity": "P2_V15_INDEPENDENT_SOURCE_POPULATION_CUSTODY_V1",
    "candidate_author_session_must_not_sign": True,
    "frozen_tuple": protocol["coherent_single_snapshot_repair"],
    "provider_witness": {
        "commit_signature_valid": True,
        "commit_signature_reason": "valid",
        "provider_tag": "refs/tags/metadata-v1-final",
        "provider_tag_target": protocol["coherent_single_snapshot_repair"]["commit"],
        "recursive_tree_entry_count": qualification["recursive_tree"]["entry_count"],
        "same_snapshot_dataset_csv_count": len(dataset_manifest),
        "same_snapshot_dataset_manifest_sha256": dataset_manifest_sha,
        "root_license_blob": qualification["rights_witness"]["git_blob_sha1"],
        "root_license_sha256": qualification["rights_witness"]["decoded_sha256"],
        "root_license_spdx": qualification["rights_witness"]["license"]["spdx_id"],
        "current_repository_metadata_license_spdx_not_snapshot_bound": qualification["rights_witness"]["repository_api_license"]["spdx_id"],
    },
    "required_independent_acts": [
        "Verify and sign the exact commit/tree/index tuple and the 61-entry dataset path/blob manifest without candidate-author involvement.",
        "Use the immutable V14 candidate template, not the erroneous frozen V15 transcription, and attest that no candidate request has yet occurred.",
        "Adjudicate exact per-review third-party rights for all candidate identities needed by the unchanged label-blind rule; the root MIT file and current CC0 repository metadata must not be blended or substituted for per-review CC-BY-4.0/CC0 evidence.",
        "Attest that dc2dadf... and every other source/route remain disallowed after the lock.",
        "Sign independence from labels, class counts, screening outcomes, models and candidate authorship.",
    ],
    "acceptance_gate": "Every tuple, manifest, exact rights and independence clause must be signed by a source-population custodian not controlled by the candidate-author session. Generic commit verification, tag existence or a self-attestation does not pass.",
    "post_acceptance_authorization": "Only a valid signature authorizes one unchanged label-blind census. It does not authorize performance; outcome and result custody remain separately required.",
}
write_json("INDEPENDENT_SOURCE_CUSTODY_REQUEST_V15.json", custody_request)

(ROOT / "INDEPENDENT_SOURCE_CUSTODY_REQUEST_V15.md").write_text(
    f"""# P2 V15 independent source-custody request

This packet requests one external, outcome-blind signature. The candidate-author session cannot sign it.

## Exact source lock

- Commit/tree: `{custody_request['frozen_tuple']['commit']}` / `{custody_request['frozen_tuple']['root_tree_sha1']}`
- Index: `{custody_request['frozen_tuple']['index_path']}`, blob `{custody_request['frozen_tuple']['index_git_blob_sha1']}`, {custody_request['frozen_tuple']['index_bytes']:,} bytes, SHA-256 `{custody_request['frozen_tuple']['index_sha256']}`
- Dataset manifest: {len(dataset_manifest)} exact CSV blobs, canonical SHA-256 `{dataset_manifest_sha}`
- Required candidate route: `{v14_template}`
- Disallowed later route: `dc2dadf...`

## Rights and independence

The exact snapshot has a root MIT license blob. Current repository metadata reports CC0 but is not bound to this historical commit. Neither substitutes for exact per-review CC-BY-4.0/CC0 adjudication. The custodian must sign the full path/blob manifest, per-review rights, no-route-switch condition, and independence from labels/outcomes.

Only then may one unchanged label-blind seven-review census run. Performance remains unauthorized until separate outcome and result custody exists.
"""
)

negative = {
    "schema_version": "orion.p2.state-expanding-acquisition.v15.negative-result-ledger",
    "preserved_v14_terminal": protocol["predecessor"]["adverse_terminal"],
    "rows": [
        {
            "issue": "V15 candidate-template transcription",
            "observation": "The frozen V15 template omitted immutable V14's /output/{review}.csv structure. It was never executed; V15B records the correction without rewriting chronology.",
            "verdict": "IMPLEMENTATION_FREEZE_MISMATCH_FAIL_CLOSED",
            "next_discriminator": "Use only the exact immutable V14 template in a future independently signed custody packet.",
        },
        {
            "issue": "independent source-population custody",
            "observation": "The commit is validly signed and metadata-v1-final targets it, but no provider-native predicate signs the V15 tuple, 61-blob candidate manifest, per-review rights and no-route-switch contract; the exact index attestation endpoint returned 404.",
            "verdict": "CANNOT_CHECK",
            "next_discriminator": "Satisfy INDEPENDENT_SOURCE_CUSTODY_REQUEST_V15.json with an external outcome-blind signature.",
        },
        {
            "issue": "same-snapshot rights scope",
            "observation": "The exact historical commit's LICENSE is MIT; current repository metadata says CC0 but is not historical-snapshot bound. Neither establishes every candidate review's required CC-BY-4.0/CC0 rights.",
            "verdict": "CANNOT_CHECK_PER_REVIEW_RIGHTS",
            "next_discriminator": "Independent custodian binds exact per-review rights without blending root and current metadata licenses.",
        },
    ],
}
write_json("NEGATIVE_RESULT_LEDGER_V15.json", negative)

report = f"""# P2 coherent single-snapshot provider qualification V15

## Question and chronology

V15 tests the minimal V14 repair: preserve commit `38b35218...` and replace only the incompatible inherited index hash with the bytes actually owned by that commit. V14's mismatch and exact terminal remain immutable.

V15 prospectively froze seven provider-metadata requests and a fail-closed custody boundary. After the provider gate, an implementation audit found that the V15 protocol had transcribed V14's candidate URL template incorrectly. `IMPLEMENTATION_CORRECTION_V15B.json` preserves this error and the exact V14 template; no candidate URL was executed, and no index or dataset body was read.

## Genuine positive source result

GitHub's official commit endpoint authenticates commit `38b35218...` and root tree `49f437c...`; its verification is **valid**. The exact provider tag `metadata-v1-final` points to the same commit. The non-truncated recursive tree has **169 entries / 140 blobs** and contains exactly one `index_v1.json` entry at blob `f4f5007...`, **22,135 bytes**, matching V14's coherent SHA-256 lineage. The same tree exposes **61 exact dataset CSV blobs**; their complete path/blob/size manifest has SHA-256 `{dataset_manifest_sha}`.

This is a real provider-authenticated state-expansion witness: the repaired source tuple is coherent and a finite same-snapshot dataset population exists. It does not establish seven eligible keyword-capable reviews or screening benefit.

## Rights and custody result

The historical snapshot's exact `LICENSE` blob is classified MIT (1,064 bytes; SHA-256 `{qualification['rights_witness']['decoded_sha256']}`). Current repository metadata reports CC0, but that current-state field is not bound to the historical commit. Neither generic root license evidence nor a valid commit signature supplies the required per-review CC-BY-4.0/CC0 adjudication.

The exact index attestation endpoint returns **404**. No provider predicate binds the V15 tuple, complete 61-blob manifest, exact rights, no-route-switch rule and outcome-blind independence. Independent source custody therefore remains **0/1**, so V15 stopped before index parsing, review CSV requests, census and performance.

## Widest defensible claim

The V14 repair target is provider-authenticated and content coherent: a validly signed commit and matching provider tag bind one tree containing the exact index entry and 61 dataset blobs. This supports source-state availability only. It does not authorize an eligible seven-review population, labels, class counts, models, rankings, metrics, performance or superiority.

## Exact terminal

`P2_V15_SIGNED_COHERENT_SINGLE_SNAPSHOT_PASS__INDEX_F4F5007_AND_61_DATASET_BLOBS_BOUND__V15_TEMPLATE_TRANSCRIPTION_FAIL_CLOSED_AND_V14_TEMPLATE_RESTORED_FOR_SUCCESSOR_ONLY__EXACT_ROOT_LICENSE_MIT_CURRENT_METADATA_CC0_NOT_BLENDED__ATTESTATION_404__INDEPENDENT_CUSTODY_NOT_CLOSED__STOP_BEFORE_INDEX_PARSE_CENSUS_PERFORMANCE`
"""
(ROOT / "SCIENTIFIC_REPORT_V15.md").write_text(report)

(ROOT / "HANDOFF_V15.md").write_text(
    f"""# P2 V15 handoff

- Positive: GitHub-valid signed commit `38b35218...` -> tree `49f437c...` -> exact index blob `f4f5007...`; provider tag `metadata-v1-final` targets the commit.
- State expansion: complete non-truncated tree exposes 61 exact dataset CSV blobs; manifest SHA-256 `{dataset_manifest_sha}`.
- Preserved adverse: V14 mismatch/terminal unchanged; later `dc2dadf...` never substituted.
- Implementation correction: V15 froze the candidate template incorrectly; it was never executed. V15B preserves the error and restores immutable V14's `/output/{{review}}.csv` template for successor use only.
- Custody/rights: exact root license is MIT; current metadata CC0 is not snapshot-bound; per-review CC-BY/CC0 remains unsigned. Index attestation 404. Independent source custody false.
- Stop: 0 index parses, 0 CSV requests/censuses, 0 labels/models/metrics, no pytest/CI.
- Next: external outcome-blind custodian signs `INDEPENDENT_SOURCE_CUSTODY_REQUEST_V15.json`; only then run one unchanged label-blind census.
"""
)

evidence_names = [
    "HANDOFF_V15.md",
    "IMPLEMENTATION_CORRECTION_V15B.json",
    "INDEPENDENT_SOURCE_CUSTODY_REQUEST_V15.json",
    "INDEPENDENT_SOURCE_CUSTODY_REQUEST_V15.md",
    "NEGATIVE_RESULT_LEDGER_V15.json",
    "PROBE_RECEIPT_V15.json",
    "PROTOCOL_FREEZE_RECEIPT_V15.json",
    "PROTOCOL_V15.json",
    "PROVIDER_QUALIFICATION_V15.json",
    "SCIENTIFIC_REPORT_V15.md",
]
evidence = {
    name: {"bytes": (ROOT / name).stat().st_size, "sha256": sha(ROOT / name)}
    for name in evidence_names
}
evidence["development/p2-state-expanding-acquisition-v14-2026-08-24/RESULT_V14.json"] = {
    "bytes": (V14 / "RESULT_V14.json").stat().st_size,
    "sha256": sha(V14 / "RESULT_V14.json"),
}

result = {
    "schema_version": "orion.p2.state-expanding-acquisition.v15.result",
    "identity": protocol["identity"],
    "protocol_sha256": PROTOCOL_SHA256,
    "adjudicated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    "authority": "PROVIDER_AUTHENTICATED_COHERENT_SINGLE_SNAPSHOT_METADATA_WITNESS_ONLY",
    "preserved_v14": {
        "result_sha256": protocol["predecessor"]["result_sha256"],
        "adverse_terminal": protocol["predecessor"]["adverse_terminal"],
        "historical_owner_substituted": False,
    },
    "positive_result": {
        "commit_tree_index_coherent": True,
        "provider_commit_signature_valid": True,
        "provider_tag_exact": "refs/tags/metadata-v1-final",
        "provider_tag_target": protocol["coherent_single_snapshot_repair"]["commit"],
        "recursive_tree_complete": True,
        "tree_entry_count": 169,
        "tree_blob_count": 140,
        "same_snapshot_dataset_csv_count": 61,
        "same_snapshot_dataset_manifest_sha256": dataset_manifest_sha,
        "index_body_requested_or_parsed": False,
        "dataset_bodies_requested": False,
    },
    "rights": {
        "exact_snapshot_root_license_spdx": "MIT",
        "exact_snapshot_root_license_sha256": qualification["rights_witness"]["decoded_sha256"],
        "current_repository_metadata_license_spdx": "CC0-1.0",
        "current_metadata_substituted_as_historical_rights": False,
        "per_review_exact_rights_closed": False,
    },
    "custody": {
        "provider_snapshot_authentication": True,
        "independent_source_population_custody": False,
        "independent_outcome_custody": False,
        "independent_result_verifier": False,
        "closed_roles": 0,
        "required_roles": 3,
    },
    "implementation_correction": correction,
    "actions": probe["actions"] | {
        "performance_arms": 0,
        "manuscript_updated": False,
        "shared_ledger_updated": False,
    },
    "gates": {
        "coherent_provider_snapshot": True,
        "independent_source_custody": False,
        "label_blind_census_authorized": False,
        "matched_performance_authorized": False,
    },
    "claim_boundary": "A validly signed provider commit/tree contains the exact repaired index entry and 61 dataset blobs. This is source-state availability, not an eligible population or performance result.",
    "verdict": "POSITIVE_COHERENT_PROVIDER_SNAPSHOT__CENSUS_AND_PERFORMANCE_WITHHELD",
    "exact_terminal": "P2_V15_SIGNED_COHERENT_SINGLE_SNAPSHOT_PASS__INDEX_F4F5007_AND_61_DATASET_BLOBS_BOUND__V15_TEMPLATE_TRANSCRIPTION_FAIL_CLOSED_AND_V14_TEMPLATE_RESTORED_FOR_SUCCESSOR_ONLY__EXACT_ROOT_LICENSE_MIT_CURRENT_METADATA_CC0_NOT_BLENDED__ATTESTATION_404__INDEPENDENT_CUSTODY_NOT_CLOSED__STOP_BEFORE_INDEX_PARSE_CENSUS_PERFORMANCE",
    "next_causal_discriminator": "An external outcome-blind source-population custodian signs the coherent tuple, exact immutable-V14 route, 61-blob manifest, per-review CC-BY-4.0/CC0 rights and no-route-switch contract; only then execute one unchanged label-blind census.",
    "evidence": evidence,
}
write_json("RESULT_V15.json", result)
print(json.dumps({"verdict": result["verdict"], "dataset_csvs": 61, "custody": False, "index_parses": 0}, sort_keys=True))
