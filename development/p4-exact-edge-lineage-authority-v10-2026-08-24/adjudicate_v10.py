#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
V9 = ROOT.parent / "p4-exact-edge-lineage-authority-v9-2026-08-23"


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


v9 = load(V9 / "RESULT_V9.json")
if sha(V9 / "RESULT_V9.json") != "b9507beca0bc653e99e6281a4f47df10d600851be6c8b1750a0beab4b8aa2111":
    raise AssertionError("immutable V9 result hash mismatch")
if sha(V9 / "SHA256SUMS") != "caae0bb5fabd064f8c76d33270c97afe2659a45da9a050118bf68fd7bace4cb7":
    raise AssertionError("immutable V9 SHA256SUMS hash mismatch")

protocol = load(ROOT / "PROTOCOL_V10.json")
freeze = load(ROOT / "PROTOCOL_FREEZE_RECEIPT_V10.json")
if sha(ROOT / "PROTOCOL_V10.json") != freeze["protocol_sha256"]:
    raise AssertionError("V10 protocol freeze mismatch")
provider = load(ROOT / "PROVIDER_AUTHORITY_PROBE_RECEIPT_V10.json")
if provider["protocol_sha256"] != freeze["protocol_sha256"]:
    raise AssertionError("V10 provider probe protocol mismatch")
swh = load(ROOT / "SWH_CANONICAL_PROBE_RECEIPT_V10.json")
if swh["protocol_sha256"] != freeze["protocol_sha256"]:
    raise AssertionError("V10 SWH probe protocol mismatch")

protocol_b = load(ROOT / "PROTOCOL_V10B.json")
freeze_b = load(ROOT / "PROTOCOL_FREEZE_RECEIPT_V10B.json")
if sha(ROOT / "PROTOCOL_V10B.json") != freeze_b["sha256"]:
    raise AssertionError("V10B protocol freeze mismatch")
edge199 = load(ROOT / "EDGE_199_CONTENT_IDENTITY_V10B.json")
if not edge199["all_closure_gates_pass"] or not all(edge199["gates"].values()):
    raise AssertionError("index 199 V10B conjunction did not pass")
if edge199["comparison"] != {
    "common_entry_count": 165,
    "differing": [],
    "differing_count": 0,
    "exact": True,
    "left_entry_count": 165,
    "only_left": [],
    "only_left_count": 0,
    "only_right": [],
    "only_right_count": 0,
    "right_entry_count": 165,
}:
    raise AssertionError("index 199 exact manifest comparison changed")

provider_rows = {row["frozen_index"]: row for row in provider["rows"]}


def request(index: int, contains: str) -> dict:
    matches = [item for item in provider_rows[index]["requests"] if contains in item["url"]]
    if len(matches) != 1:
        raise AssertionError(f"index {index}: expected one request containing {contains!r}, got {len(matches)}")
    return matches[0]


z36 = load(ROOT / "evidence/36_zenodo_record.body")
ref36 = load(ROOT / "evidence/36_github_ref_0.body")
if not (
    z36.get("doi") == "10.5281/zenodo.21221062"
    and (z36.get("metadata") or {}).get("version") is None
    and ((ref36.get("object") or {}).get("sha") == "069ab4f56d100d765d46c594ac1b06add7e49f9e")
):
    raise AssertionError("index 36 evidence changed")

z91 = load(ROOT / "evidence/91_zenodo_record.body")
ref91 = load(ROOT / "evidence/91_github_ref_0.body")
v9e91 = load(V9 / "EDGE_91_EMBEDDED_GIT_AUTHORITY_V9.json")
if not (
    (z91.get("metadata") or {}).get("version") == "v1.0.0"
    and ((ref91.get("object") or {}).get("sha") == "9fa30e9f405de4446c792bd59cb7c5a4bb7ecb59")
    and v9e91["head"] == "aa021231cdafb6d74ce9ab5f55f824a3032058a4"
    and not v9e91["accepted_commit_object_present"]
):
    raise AssertionError("index 91 evidence changed")

if not (
    request(133, "/integrity/")["status"] == 404
    and request(133, "/attestations/")["status"] == 404
    and request(185, "/integrity/")["status"] == 404
    and request(185, "/attestations/")["status"] == 404
):
    raise AssertionError("indices 133/185 provenance endpoints no longer have frozen 404 responses")

rows = [
    {
        "frozen_index": 36,
        "domain": "SCIENTIFIC_SOFTWARE",
        "repository": "jaxionproject/jaxion",
        "verdict": "REMAINS_CANNOT_CHECK",
        "residual": "EXACT_ARCHIVE_VERSION_DOI_RELATION_AND_ARCHIVE_ROOT_TO_TAG_COMMIT_IDENTITY_CANNOT_CHECK",
        "new_evidence": "The exact concept DOI request still returns child record 10.5281/zenodo.21221062, whose metadata has no version and whose sole jaxion.zip file is 85,369,480 bytes with MD5 825cae8912147ba8a5415c6a73d95818. GitHub still binds tag 0.0.3 to full commit 069ab4f56d100d765d46c594ac1b06add7e49f9e. No provider correction binds the frozen archive to version 0.0.3 or that commit.",
        "terminal_gate": "provider_corrected_version_and_archive_to_commit_identity",
        "next_discriminator": "A Zenodo/provider correction must bind the frozen DOI and exact archive bytes to version 0.0.3 and full commit 069ab4f56d100d765d46c594ac1b06add7e49f9e.",
    },
    {
        "frozen_index": 91,
        "domain": "SCIENTIFIC_SOFTWARE",
        "repository": "nutritionallungimmunity/pai",
        "verdict": "REMAINS_CANNOT_CHECK",
        "residual": "ARCHIVE_TO_ACCEPTED_TAG_COMMIT_IDENTITY_CONTRADICTED_BY_EMBEDDED_GIT_HEAD",
        "new_evidence": "Zenodo still identifies the checksum-bound record as v1.0.0 and GitHub still binds tag v1.0.0 to 9fa30e9f405de4446c792bd59cb7c5a4bb7ecb59. No corrected archive or provider statement supersedes the immutable V9 archive evidence: embedded HEAD, main and origin/main are aa021231cdafb6d74ce9ab5f55f824a3032058a4, while the accepted tag commit is absent from the embedded object store.",
        "terminal_gate": "corrected_archive_or_provider_statement_superseding_adverse_embedded_git_authority",
        "next_discriminator": "A corrected exact v1.0.0 archive or authenticated provider statement must bind the frozen bytes to 9fa30e9f405de4446c792bd59cb7c5a4bb7ecb59 and resolve the adverse embedded Git authority.",
    },
    {
        "frozen_index": 133,
        "domain": "SCIENTIFIC_SOFTWARE",
        "repository": "artefactory/woodtapper",
        "verdict": "REMAINS_CANNOT_CHECK",
        "residual": "SDIST_TO_FULL_COMMIT_AUTHENTICATED_BUILD_PROVENANCE_CANNOT_CHECK",
        "new_evidence": "Zenodo and PyPI still bind woodtapper-0.0.13.tar.gz to SHA-256 b509f6469b9ff8888195751c811d689559f45e24aeb35bb173b9680c99c8dbf3, and GitHub binds tag v0.0.13 to 7ac6d23d504404c4004faad663f6b889427109e6. The exact PyPI Integrity request returns 404 with 'No provenance available for woodtapper-0.0.13.tar.gz'; the exact GitHub artifact-attestation subject also returns 404. V9 local reconstruction differed in two generated C files and cannot substitute for provider provenance.",
        "terminal_gate": "provider_native_sdist_to_full_commit_provenance",
        "next_discriminator": "PyPI trusted-publisher/Sigstore provenance or another provider-native exact build attestation must bind SHA-256 b509f646... to commit 7ac6d23d..., including the generated-C toolchain.",
    },
    {
        "frozen_index": 185,
        "domain": "PHYSICAL_ENGINEERING",
        "repository": "mit-psfc/disruption-py",
        "verdict": "REMAINS_CANNOT_CHECK",
        "residual": "SDIST_PROJECTION_TO_TAG_COMMIT_AUTHENTICATED_BUILD_PROVENANCE_CANNOT_CHECK",
        "new_evidence": "Zenodo and PyPI still bind disruption_py-0.14.0.tar.gz to SHA-256 775f92dbcbd6d1523db241494998e4b0867d51a84236feb7accc86b63b033a19, and GitHub binds source tag v0.14 to dec5c58a3e3970bc6817f33efb615fea11057fce. The exact PyPI Integrity request returns 404 with no provenance and the exact GitHub artifact-attestation subject returns 404. V9 showed common-file equality only: the sdist is a projection and a local rebuild omitted three tracked ignored CSV files.",
        "terminal_gate": "provider_native_projected_sdist_to_full_commit_provenance",
        "next_discriminator": "A provider-native build attestation must bind SHA-256 775f92db... to commit dec5c58..., including the tracked-ignored CSV inclusion state.",
    },
    {
        "frozen_index": 199,
        "domain": "LIFE_BIOMEDICAL",
        "repository": "targene/targene-pipeline",
        "verdict": "RESOLVED_SAME_CONTENT_IDENTITY",
        "residual": None,
        "accepted_identity_method": "EXACT_NORMALIZED_ZENODO_ARCHIVE_TO_GITHUB_IMMUTABLE_COMMIT_MANIFEST_EQUALITY",
        "v10_primary_discriminator": "FAILED_AS_FROZEN: the source-origin snapshot has no v0.13.4 branch and exact revision 0f8b2dbca06a3bb7031de9058ee9882995e04412 remains absent from current GitHub and Software Heritage.",
        "v10b_successor_status": "OUTCOME_INFORMED_PROTOCOL_FROZEN_BEFORE_NEW_ARCHIVE_DOWNLOAD_OR_COMPARISON",
        "new_evidence": "A separately frozen V10B successor verifies that current GitHub tag v0.13.5 points to full immutable revision a85df681d29a5cf3406d529144a7c0645e543e61 and that GitHub authenticates tree 178315b57afafc1f20ab9929b4de893430524c62. The official Software Heritage source-origin snapshot independently binds the same tag, revision and directory. The 4,237,826-byte checksum-bound Zenodo v0.13.4 ZIP (MD5 3409352bdc0926acfafc39bf121f4263; SHA-256 5eaf4bc23f11cf14d6b1f41510a7b99cf3107cb906a7b7e9aa2945a2a64baeba) and the 4,247,426-byte immutable GitHub revision codeload ZIP (SHA-256 b468f53c66e751ae242a039ba94c43788ec059363f8d2a2691207b4d4015a0b7) normalize to the same 165-path manifest: no missing, extra or differing entry, identical file bytes/types/executable bits, manifest SHA-256 32decf39f38d4652e184bef077625ce8e22fa44ec37afb98746ddce178f5364e. Exact LICENSE bytes are MIT.",
        "repaired_gates": [
            "exact_source_native_full_commit_identity",
            "archive_to_commit_content_identity",
            "accepted_archive_and_commit_software_rights",
        ],
        "version_label_boundary": "The later v0.13.5 revision is an immutable witness of identical content only. It is not asserted to be, descend from or restore the deleted v0.13.4 commit.",
        "terminal_gate": "closed_exact_source_content_identity",
        "next_discriminator": "Closed for exact source content identity.",
    },
]

negative_rows = [row for row in rows if row["verdict"] == "REMAINS_CANNOT_CHECK"]
negative = {
    "schema_version": "orion.p4.exact-edge-lineage-authority.v10.negative-result-ledger",
    "identity": "P4.M6.JOSS.EXACT.EDGE.LINEAGE.AUTHORITY.V10.NEGATIVE.RESULTS",
    "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "preserved_predecessor": "development/p4-exact-edge-lineage-authority-v9-2026-08-23/NEGATIVE_RESULT_LEDGER_V9.json",
    "remaining_count": len(negative_rows),
    "remaining_indices": [row["frozen_index"] for row in negative_rows],
    "rows": negative_rows,
    "noncompensatory_rule": "No later gate, score, local reconstruction, subset equality or source-frame progress compensates for the named terminal failure.",
}
(ROOT / "NEGATIVE_RESULT_LEDGER_V10.json").write_text(json.dumps(negative, indent=2, sort_keys=True) + "\n")

ledger_md = [
    "# V10 preserved negative-result ledger",
    "",
    "The four unresolved frozen identities remain `CANNOT_CHECK`; no ambiguity or absence is relabelled as closure.",
    "",
    "| Index | Repository | Terminal residual | Next discriminator |",
    "|---:|---|---|---|",
]
for row in negative_rows:
    ledger_md.append(
        f"| {row['frozen_index']} | `{row['repository']}` | `{row['residual']}` | {row['next_discriminator']} |"
    )
ledger_md += [
    "",
    "Index 199 is not a negative row: it closed only through the separately frozen, outcome-informed V10B exact-content protocol. The failed original V10 target-specific discriminator is preserved in `RESULT_V10.json`.",
]
(ROOT / "NEGATIVE_RESULT_LEDGER_V10.md").write_text("\n".join(ledger_md) + "\n")

evidence_paths = [
    (V9 / "RESULT_V9.json"),
    (V9 / "SHA256SUMS"),
    (ROOT / "PROTOCOL_V10.json"),
    (ROOT / "PROTOCOL_FREEZE_RECEIPT_V10.json"),
    (ROOT / "PROVIDER_AUTHORITY_PROBE_RECEIPT_V10.json"),
    (ROOT / "SWH_CANONICAL_PROBE_RECEIPT_V10.json"),
    (ROOT / "PROTOCOL_V10B.json"),
    (ROOT / "PROTOCOL_FREEZE_RECEIPT_V10B.json"),
    (ROOT / "PROBE_RECEIPT_V10B.json"),
    (ROOT / "EDGE_199_CONTENT_IDENTITY_V10B.json"),
    (ROOT / "EDGE_199_NORMALIZED_MANIFESTS_V10B.json"),
    (ROOT / "NEGATIVE_RESULT_LEDGER_V10.json"),
]
evidence = {}
for path in evidence_paths:
    if path.parent == ROOT:
        name = path.name
    else:
        name = str(path.relative_to(ROOT.parent.parent))
    evidence[name] = {"bytes": path.stat().st_size, "sha256": sha(path)}

result = {
    "schema_version": "orion.p4.exact-edge-lineage-authority.v10.result",
    "identity": "P4.M6.JOSS.EXACT.EDGE.LINEAGE.AUTHORITY.V10",
    "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "predecessor": {
        "identity": v9["identity"],
        "result_sha256": sha(V9 / "RESULT_V9.json"),
        "sha256sums_sha256": sha(V9 / "SHA256SUMS"),
        "cumulative_exact_bridge": v9["cumulative_exact_bridge"],
        "remaining_indices": v9["v9_remaining_indices"],
    },
    "protocol_chronology": {
        "v10_primary": {
            "outcome_informed": False,
            "status": "ALL_FIVE_FROZEN_TARGET_DISCRIMINATORS_ADJUDICATED",
            "index_199_target_specific_discriminator": "FAILED_AS_FROZEN",
        },
        "v10b_successor": {
            "outcome_informed": True,
            "frozen_before_v10b_archive_download_or_comparison": True,
            "scope": "index 199 exact content identity only",
            "status": "PASSED_ALL_EIGHT_NONCOMPENSATORY_GATES",
        },
    },
    "predecessor_exact_bridge": "75/80",
    "v10_closed_count": 1,
    "v10_closed_indices": [199],
    "v10_remaining_count": 4,
    "v10_remaining_indices": [36, 91, 133, 185],
    "cumulative_exact_bridge": "76/80",
    "cumulative_exact_by_domain": {
        "EARTH_ENVIRONMENT": 5,
        "LIFE_BIOMEDICAL": 7,
        "PHYSICAL_ENGINEERING": 4,
        "SCIENTIFIC_SOFTWARE": 60,
    },
    "rows": rows,
    "evidence": evidence,
    "natural_pair_and_scientific_boundary": {
        "eligible_natural_pairs_added": 0,
        "author_lineage_adjudications_added": 0,
        "external_custody_added": False,
        "comparator_outcomes_accessed": False,
        "scientific_authority_granted": False,
        "programme_terminal": "P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK",
    },
    "claim_boundary": [
        "Same five frozen residual identities only; no replacement or proxy unit.",
        "V10B is explicitly outcome-informed and repairs one exact source-content edge only.",
        "The original V10 index-199 target-specific discriminator failed and is not reinterpreted.",
        "The later v0.13.5 revision is only an immutable exact-content witness for the checksum-bound v0.13.4 archive.",
        "No natural-pair eligibility, author-lineage independence, source-disjoint replication, external custody, comparator outcome, performance or superiority claim follows.",
    ],
    "next_discriminator": "For indices 36 and 91, require provider correction of the exact frozen archive relation. For indices 133 and 185, require provider-native artifact-to-commit build provenance. Separately complete the full 76-edge author-conflict/replication partition and natural-pair/custody gates; exact-edge count alone is not confirmatory evidence.",
}
(ROOT / "RESULT_V10.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

results_md = [
    "# P4 exact-edge lineage/authority V10 results",
    "",
    "## Verdict",
    "",
    "One of the five V9 residual exact-source edges closed. The cumulative exact bridge increases from **75/80** to **76/80**; the same 80 frozen units are retained.",
    "",
    "| Index | Repository | V10/V10B verdict | Terminal gate |",
    "|---:|---|---|---|",
]
for row in rows:
    results_md.append(
        f"| {row['frozen_index']} | `{row['repository']}` | `{row['verdict']}` | `{row['terminal_gate']}` |"
    )
results_md += [
    "",
    "## Genuine index-199 repair",
    "",
    "The original frozen V10 discriminator failed: neither current GitHub nor Software Heritage authenticates the deleted `v0.13.4` revision `0f8b2dbca06a3bb7031de9058ee9882995e04412`, and the SWH origin snapshot has no `v0.13.4` branch.",
    "",
    "A separately named, outcome-informed V10B protocol was then frozen **before** new archive download or comparison. Under it:",
    "",
    "- GitHub tag `v0.13.5` and the exact commit API authenticate revision `a85df681d29a5cf3406d529144a7c0645e543e61` with tree `178315b57afafc1f20ab9929b4de893430524c62`.",
    "- The official Software Heritage source-origin snapshot independently binds the same tag, full revision and directory.",
    "- The checksum-bound Zenodo `v0.13.4` ZIP and immutable GitHub revision codeload ZIP each normalize to **165 paths**. The manifests have zero missing, extra or differing entries, including file bytes, entry type and executable bits; both manifest hashes are `32decf39f38d4652e184bef077625ce8e22fa44ec37afb98746ddce178f5364e`.",
    "- The exact LICENSE bytes are MIT.",
    "",
    "This is content identity only. It does **not** identify the later revision as the deleted `v0.13.4` commit or establish ancestry.",
    "",
    "## Remaining exact-edge discriminators",
    "",
]
for row in negative_rows:
    results_md += [f"### Index {row['frozen_index']} — `{row['repository']}`", "", row["new_evidence"], "", f"**Next:** {row['next_discriminator']}", ""]
results_md += [
    "## Scientific boundary",
    "",
    "The exact-edge bridge is a source-frame prerequisite only. V10/V10B adds no natural pair, author-lineage adjudication, source-disjoint replication, external custody, comparator outcome, performance result or superiority authority. The programme therefore remains `P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK`.",
]
(ROOT / "RESULTS_V10.md").write_text("\n".join(results_md) + "\n")

omitted = """# Omitted large artifacts — V10/V10B

The downloaded ZIP bodies were used transiently and are not retained in this bounded packet. Their exact identities are recorded in `PROBE_RECEIPT_V10B.json` and their complete normalized per-entry manifests are retained in `EDGE_199_NORMALIZED_MANIFESTS_V10B.json`.

| Artifact | Bytes | MD5 | SHA-256 |
|---|---:|---|---|
| Zenodo `TARGENE/targene-pipeline-v0.13.4.zip` | 4,237,826 | `3409352bdc0926acfafc39bf121f4263` | `5eaf4bc23f11cf14d6b1f41510a7b99cf3107cb906a7b7e9aa2945a2a64baeba` |
| GitHub codeload `a85df681d29a5cf3406d529144a7c0645e543e61` | 4,247,426 | `a316dd8374fb6ba8b6e27c24ddf3a9d6` | `b468f53c66e751ae242a039ba94c43788ec059363f8d2a2691207b4d4015a0b7` |

No private payload was used or retained.
"""
(ROOT / "OMITTED_LARGE_ARTIFACTS_V10.md").write_text(omitted)

handoff = """# P4 exact-edge V10 handoff

- Immutable repository HEAD at protocol freeze: `8d47c546591a3c96dc5cf202f7e227d13251221c`.
- V9 predecessor: `75/80`; residual indices `36, 91, 133, 185, 199`.
- V10/V10B: index `199` genuinely closes by exact 165-path normalized archive-to-immutable-revision content identity.
- New cumulative exact bridge: `76/80`; remaining indices `36, 91, 133, 185`.
- The original frozen V10 discriminator for index 199 failed. V10B is a separately frozen, explicitly outcome-informed successor; do not collapse their chronology.
- No natural pair, lineage adjudication, source-disjoint replication, custody, comparator outcome, performance or superiority authority was added.
- No pytest or repository CI was run.
"""
(ROOT / "HANDOFF_V10.md").write_text(handoff)

print(
    json.dumps(
        {
            "closed": [199],
            "remaining": [36, 91, 133, 185],
            "cumulative_exact_bridge": "76/80",
            "negative_rows": len(negative_rows),
        },
        sort_keys=True,
    )
)
