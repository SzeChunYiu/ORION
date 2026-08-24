#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
V10 = ROOT.parent / "p4-exact-edge-lineage-authority-v10-2026-08-24"


def load(path: Path | str) -> dict:
    if isinstance(path, str):
        path = ROOT / path
    return json.loads(path.read_text())


def sha(path: Path | str) -> str:
    if isinstance(path, str):
        path = ROOT / path
    return hashlib.sha256(path.read_bytes()).hexdigest()


if sha(V10 / "RESULT_V10.json") != "9cd19c2f2d3129f4789e5976395ce02f6cb08a29287614900c2b3bddbbaa20d1":
    raise AssertionError("V10 result hash mismatch")
if sha(V10 / "SHA256SUMS") != "b643beb8a740cc618bacc742f617e87f3eed3e1288afe1af87f6b49aff5d0449":
    raise AssertionError("V10 SHA256SUMS hash mismatch")

freeze = load("PROTOCOL_FREEZE_RECEIPT_V11.json")
if sha("PROTOCOL_V11.json") != freeze["protocol_sha256"]:
    raise AssertionError("V11 protocol freeze mismatch")
probe = load("PROBE_RECEIPT_V11.json")
if probe["protocol_sha256"] != freeze["protocol_sha256"]:
    raise AssertionError("V11 probe protocol mismatch")

e36 = load("EDGE_36_PROVIDER_CORRECTION_V11.json")
e91 = load("EDGE_91_EMBEDDED_HEAD_CONTENT_IDENTITY_V11.json")
pypi = load("PYPI_SIMPLE_PROVENANCE_V11.json")
pypi_rows = {row["frozen_index"]: row for row in pypi["rows"]}
if not (
    e36["zenodo"]["version"] is None
    and e36["datacite"]["child_version"] is None
    and not any(e36["gates"].values())
):
    raise AssertionError("index 36 discriminator changed")
if not (
    e91["github_commit"]["sha"] == e91["embedded_git"]["head"] == "aa021231cdafb6d74ce9ab5f55f824a3032058a4"
    and e91["github_commit"]["tree_sha"] == e91["embedded_git"]["tree"] == "d5620f3acf4e5a163cfdfdefc2432ebd5709008a"
    and e91["comparison"]["only_left_count"] == 106
    and e91["comparison"]["differing_count"] == 2
    and not e91["comparison"]["exact"]
):
    raise AssertionError("index 91 adverse exact comparison changed")
if not all(not pypi_rows[index]["provenance_field_present"] for index in (133, 185)):
    raise AssertionError("PyPI provenance field status changed")

rows = [
    {
        "frozen_index": 36,
        "domain": "SCIENTIFIC_SOFTWARE",
        "repository": "jaxionproject/jaxion",
        "verdict": "REMAINS_CANNOT_CHECK",
        "residual": "EXACT_ARCHIVE_VERSION_DOI_RELATION_AND_ARCHIVE_ROOT_TO_TAG_COMMIT_IDENTITY_CONTRADICTED",
        "new_evidence": "The exact Zenodo child and both official DataCite concept/child registrations still expose no version. The provider file remains the 85,369,480-byte jaxion.zip with MD5 825cae8912147ba8a5415c6a73d95818. Preserved checksum-bound archive evidence authenticates embedded worktree HEAD 3cd108c376faf9832373adfe3ab4688295aa42fa (tag 0.0.12), not publication version 0.0.3 commit 069ab4f56d100d765d46c594ac1b06add7e49f9e. Metadata absence and content contradiction are both terminal; the large archive was not redundantly downloaded.",
        "terminal_gate": "provider_corrected_exact_version_and_replacement_archive_root_to_accepted_commit",
        "next_discriminator": "A provider replacement/correction must bind an exact 0.0.3 archive checksum whose root is commit 069ab4f56d100d765d46c594ac1b06add7e49f9e; the current checksum-bound archive is an embedded 0.0.12 worktree.",
    },
    {
        "frozen_index": 91,
        "domain": "SCIENTIFIC_SOFTWARE",
        "repository": "nutritionallungimmunity/pai",
        "verdict": "REMAINS_CANNOT_CHECK",
        "residual": "EMBEDDED_HEAD_TREE_AUTHENTICATED_BUT_ARCHIVE_PAYLOAD_HAS_UNTRACKED_GENERATED_FILES_AND_MODE_DRIFT",
        "new_evidence": "The checksum-bound 17,147,954-byte Zenodo archive exactly authenticates embedded Git HEAD aa021231cdafb6d74ce9ab5f55f824a3032058a4 and tree d5620f3acf4e5a163cfdfdefc2432ebd5709008a; git fsck passes, and current GitHub independently authenticates the same full revision and tree. However the separately adjudicated non-.git archive payload has 444 paths versus 338 in immutable codeload: 106 untracked compiled Java .class files are archive-only, and cpp/PAIpp.exe plus run.sh have equal bytes but executable-bit drift. git diff-files is nonzero. Exact manifest equality therefore fails despite MIT rights, and the accepted v1.0.0 tag still points to a different absent-from-archive commit.",
        "terminal_gate": "exact_full_archive_payload_to_immutable_revision_or_provider_native_build_attestation",
        "next_discriminator": "A corrected checksum-bound archive must exactly equal an immutable source revision, or provider-native signed build provenance must bind all 106 compiled classes and the two mode changes to full revision aa021231...; subset/source-tree equality is insufficient.",
    },
    {
        "frozen_index": 133,
        "domain": "SCIENTIFIC_SOFTWARE",
        "repository": "artefactory/woodtapper",
        "verdict": "REMAINS_CANNOT_CHECK",
        "residual": "SDIST_TO_FULL_COMMIT_AUTHENTICATED_BUILD_PROVENANCE_CANNOT_CHECK",
        "new_evidence": "PyPI's official PEP 691 exact file object binds woodtapper-0.0.13.tar.gz to SHA-256 b509f6469b9ff8888195751c811d689559f45e24aeb35bb173b9680c99c8dbf3 but exposes provenance: null. This independently agrees with V10's exact Integrity and GitHub artifact-attestation 404s; no provider-native statement binds the sdist to commit 7ac6d23d504404c4004faad663f6b889427109e6.",
        "terminal_gate": "pypi_exact_file_signed_artifact_to_full_commit_provenance",
        "next_discriminator": "PyPI must expose exact-file signed provenance binding SHA-256 b509f646... to commit 7ac6d23d..., including the generated-C toolchain.",
    },
    {
        "frozen_index": 185,
        "domain": "PHYSICAL_ENGINEERING",
        "repository": "mit-psfc/disruption-py",
        "verdict": "REMAINS_CANNOT_CHECK",
        "residual": "SDIST_PROJECTION_TO_TAG_COMMIT_AUTHENTICATED_BUILD_PROVENANCE_CANNOT_CHECK",
        "new_evidence": "PyPI's official PEP 691 exact file object binds disruption_py-0.14.0.tar.gz to SHA-256 775f92dbcbd6d1523db241494998e4b0867d51a84236feb7accc86b63b033a19 but exposes provenance: null. This independently agrees with V10's exact Integrity and GitHub artifact-attestation 404s; no provider-native statement binds the projected sdist to commit dec5c58a3e3970bc6817f33efb615fea11057fce.",
        "terminal_gate": "pypi_exact_file_signed_projected_sdist_to_full_commit_provenance",
        "next_discriminator": "PyPI must expose exact-file signed provenance binding SHA-256 775f92db... to commit dec5c58..., including the tracked-ignored CSV inclusion state.",
    },
]

negative = {
    "schema_version": "orion.p4.exact-edge-lineage-authority.v11.negative-result-ledger",
    "identity": "P4.M6.JOSS.EXACT.EDGE.LINEAGE.AUTHORITY.V11.NEGATIVE.RESULTS",
    "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "predecessor_result_sha256": sha(V10 / "RESULT_V10.json"),
    "remaining_count": 4,
    "remaining_indices": [36, 91, 133, 185],
    "rows": rows,
    "noncompensatory_rule": "Authenticated subsets, matching Git trees, local Git cleanliness under ignored file-mode settings, local reconstruction, provider hash identity or absent provenance never compensate for the named terminal gate.",
}
(ROOT / "NEGATIVE_RESULT_LEDGER_V11.json").write_text(json.dumps(negative, indent=2, sort_keys=True) + "\n")

md = [
    "# V11 preserved negative-result ledger",
    "",
    "All four frozen residual identities remain `CANNOT_CHECK`. V11 adds sharper exact terminal evidence; it does not relabel ambiguity, absence, projection or subset equality as closure.",
    "",
    "| Index | Repository | Exact terminal | Next discriminator |",
    "|---:|---|---|---|",
]
for row in rows:
    md.append(f"| {row['frozen_index']} | `{row['repository']}` | `{row['terminal_gate']}` | {row['next_discriminator']} |")
(ROOT / "NEGATIVE_RESULT_LEDGER_V11.md").write_text("\n".join(md) + "\n")

evidence_paths = [
    V10 / "RESULT_V10.json",
    V10 / "SHA256SUMS",
    ROOT / "PROTOCOL_V11.json",
    ROOT / "PROTOCOL_FREEZE_RECEIPT_V11.json",
    ROOT / "PROBE_RECEIPT_V11.json",
    ROOT / "EDGE_36_PROVIDER_CORRECTION_V11.json",
    ROOT / "EDGE_91_EMBEDDED_HEAD_CONTENT_IDENTITY_V11.json",
    ROOT / "EDGE_91_NORMALIZED_MANIFESTS_V11.json",
    ROOT / "PYPI_SIMPLE_PROVENANCE_V11.json",
    ROOT / "NEGATIVE_RESULT_LEDGER_V11.json",
]
evidence = {}
for path in evidence_paths:
    name = path.name if path.parent == ROOT else str(path.relative_to(ROOT.parent.parent))
    evidence[name] = {"bytes": path.stat().st_size, "sha256": sha(path)}

result = {
    "schema_version": "orion.p4.exact-edge-lineage-authority.v11.result",
    "identity": "P4.M6.JOSS.EXACT.EDGE.LINEAGE.AUTHORITY.V11",
    "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "outcome_informed": True,
    "predecessor": {
        "identity": "P4.M6.JOSS.EXACT.EDGE.LINEAGE.AUTHORITY.V10",
        "result_sha256": sha(V10 / "RESULT_V10.json"),
        "sha256sums_sha256": sha(V10 / "SHA256SUMS"),
        "cumulative_exact_bridge": "76/80",
        "remaining_indices": [36, 91, 133, 185],
    },
    "preserved_v10_v10b_chronology": "The original frozen V10 index-199 target-specific discriminator failed; the separately frozen, outcome-informed V10B exact-content successor passed. V11 does not reinterpret either result.",
    "v11_closed_count": 0,
    "v11_closed_indices": [],
    "v11_remaining_count": 4,
    "v11_remaining_indices": [36, 91, 133, 185],
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
        "Same four frozen identities only; no evidence object is counted as a unit.",
        "V11 is explicitly outcome-informed and pre-frozen before its ten requests.",
        "Index 91 Git HEAD/tree authority is genuine but non-.git payload equality fails on 106 generated files and two mode bits.",
        "PyPI exact file hashes are integrity evidence, not artifact-to-commit provenance.",
        "No natural-pair, author-lineage, source-disjoint replication, custody, outcome, performance or superiority authority is added.",
    ],
    "next_discriminator": "Indices 36 and 91 require corrected checksum-bound provider archives or exact provider-native build receipts for the adverse payloads. Indices 133 and 185 require PyPI exact-file signed provenance to their full commits. Repeating current endpoints without a provider-state change has zero expected closure value.",
}
(ROOT / "RESULT_V11.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

results_md = [
    "# P4 exact-edge lineage/authority V11 results",
    "",
    "## Verdict",
    "",
    "V11 closes **0/4** remaining exact edges. The cumulative bridge stays **76/80**. The negative result is informative: every remaining edge now has a provider-state-change discriminator, so repeating the same requests is not an efficient next action.",
    "",
    "| Index | Repository | Verdict | Exact terminal |",
    "|---:|---|---|---|",
]
for row in rows:
    results_md.append(f"| {row['frozen_index']} | `{row['repository']}` | `{row['verdict']}` | `{row['terminal_gate']}` |")
results_md += ["", "## Per-edge findings", ""]
for row in rows:
    results_md += [f"### Index {row['frozen_index']} — `{row['repository']}`", "", row["new_evidence"], "", f"**Next discriminator:** {row['next_discriminator']}", ""]
results_md += [
    "## Scientific boundary",
    "",
    "No manuscript or claim-ledger headline changes: no exact edge closed. The bridge remains 76/80, and the programme remains `P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK`. Source integrity or exact-file hash evidence alone does not authorize natural pairs, lineage independence, replication, custody, outcomes, performance or superiority.",
]
(ROOT / "RESULTS_V11.md").write_text("\n".join(results_md) + "\n")

omitted = f"""# Omitted large artifacts — V11

The two index-91 TAR bodies were used transiently and are not retained. Complete normalized manifests and exact request receipts are retained.

| Artifact | Bytes | MD5 | SHA-256 |
|---|---:|---|---|
| Zenodo v1.0.0 archive | {e91['zenodo_archive']['bytes']:,} | `{e91['zenodo_archive']['md5']}` | `{e91['zenodo_archive']['sha256']}` |
| GitHub codeload `{e91['content_witness_revision']}` | {e91['github_codeload']['bytes']:,} | `{e91['github_codeload']['md5']}` | `{e91['github_codeload']['sha256']}` |

The 85,369,480-byte index-36 archive was not redownloaded because immutable preserved evidence already fails the second noncompensatory gate; V11 records the current provider metadata only. No private payload was used.
"""
(ROOT / "OMITTED_LARGE_ARTIFACTS_V11.md").write_text(omitted)

handoff = """# P4 exact-edge V11 handoff

- V10 predecessor: `76/80`; residual indices `36, 91, 133, 185`.
- V11: `0/4` closures; cumulative bridge remains `76/80`.
- Index 36: Zenodo and DataCite version remain null; preserved archive HEAD is tag 0.0.12, not publication 0.0.3.
- Index 91: embedded HEAD/tree and GitHub revision authenticate exactly, but the archive has 106 untracked compiled `.class` files and two executable-bit drifts versus codeload; exact payload equality fails.
- Indices 133/185: exact PyPI PEP 691 file hashes match, but `provenance` is null.
- No P4 manuscript or claim-ledger change is authorized because no edge closed.
- V10/V10B chronology is preserved; no pytest or repository CI was run.
"""
(ROOT / "HANDOFF_V11.md").write_text(handoff)

print(json.dumps({"closed": [], "remaining": [36, 91, 133, 185], "cumulative_exact_bridge": "76/80"}, sort_keys=True))
