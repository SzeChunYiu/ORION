#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
V11 = ROOT.parent / "p4-exact-edge-lineage-authority-v11-2026-08-24"
PROTOCOL_SHA256 = "9bc43bfae807d3d69ac01696786987e0e7e583421dc0e77d1af3f22ef7bec1dd"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text())


def write_json(name: str, value: object) -> None:
    (ROOT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


protocol = load("PROTOCOL_V12.json")
freeze = load("PROTOCOL_FREEZE_RECEIPT_V12.json")
projection = load("JAR_PROJECTION_V12.json")
mode = load("MODE_AUTHORITY_V12.json")
probe = load("PROBE_RECEIPT_V12.json")
assert sha(ROOT / "PROTOCOL_V12.json") == freeze["protocol_sha256"] == PROTOCOL_SHA256
assert projection["exact"] is True
assert projection["expected_count"] == projection["observed_class_member_count"] == 106
assert projection["missing_count"] == projection["extra_count"] == projection["different_byte_count"] == 0
assert projection["class_major_version_counts"] == {"61": 106}
assert mode["both_paths_authoritative"] is False

compiler = {
    "schema_version": "orion.p4.exact-edge-build-provenance.v12.compiler-probe",
    "protocol_sha256": PROTOCOL_SHA256,
    "frozen_image": protocol["pinned_lawful_tooling"]["compiler_container"],
    "frozen_command": protocol["class_investigation"]["compiler_command"],
    "attempts": [
        {
            "step": "docker_pull_frozen_manifest",
            "returncode": 1,
            "exact_terminal": "failed to connect to the docker API at unix:///var/run/docker.sock; check if the path is correct and if the daemon is running: dial unix /var/run/docker.sock: connect: no such file or directory",
        },
        {
            "step": "start_docker_desktop",
            "returncode": 1,
            "exact_terminal": "Unable to find application named 'Docker'",
        },
        {
            "step": "lawful_disposable_colima_0.10.3_lima_2.2.0_first_start",
            "returncode": 1,
            "exact_terminal": "failed to download cache artifact: exit status 1; error starting vm: error at 'creating and starting': exit status 1",
        },
        {
            "step": "lawful_disposable_colima_second_start",
            "returncode": 1,
            "exact_terminal": "Failed to wait for the guest SSH server to become available, falling back to usernet forwarder; colima status: error retrieving current runtime: empty value; docker API: dial unix /var/run/docker.sock: connect: no such file or directory",
        },
        {
            "step": "lawful_disposable_colima_fresh_instance_after_cache_removal",
            "returncode": 1,
            "exact_terminal": "error getting qcow image: error during image download: write /Users/billy/Library/Caches/colima/caches/b0992ab88f5a3c0c436bbb3065c01466f20dc1dd0eb0a60299d410176f21a1c3.downloading: no space left on device",
            "filesystem_observation": "/dev/disk3s1s1 228Gi size, 12Gi used, 127Mi available, 99% capacity at the failed fresh-instance attempt",
        },
    ],
    "cleanup": "The disposable Colima/Lima formulae, VM state and Colima cache installed by V12 were removed; no persistent compiler runtime was left running.",
    "compiler_executed": False,
    "substitute_compiler_used": False,
    "fresh_class_outputs_observed": False,
    "source_compilation_exact": None,
    "verdict": "CANNOT_CHECK",
    "exact_terminal": "PINNED_COMPILER_RUNTIME_UNAVAILABLE_NO_BUILD_EXECUTED",
    "nonrepeating_discriminator": "Retry only after an available linux/arm64 OCI runtime and sufficient disposable disk exist, using the already frozen image manifest digest and command; otherwise obtain the provider signing contract. Do not substitute a compiler or repeat the same unavailable-runtime probe.",
}
write_json("COMPILER_PROBE_V12.json", compiler)

signing_contract = {
    "schema_version": "orion.p4.exact-edge-build-provenance.v12.provider-signing-contract",
    "contract_identity": "PAI_INDEX_91_ARCHIVE_BUILD_AND_MODE_AUTHORITY_V1",
    "purpose": "Narrow provider-native authority contract for the V12 residual only; it does not authorize scientific outcomes.",
    "acceptable_issuers": [
        "Zenodo record owner for record 20171460 through a provider-native signed provenance object",
        "NutritionalLungImmunity/PAI repository owner through a verifiable Sigstore/GitHub artifact attestation",
    ],
    "required_subjects": {
        "zenodo_archive_sha256": protocol["frozen_unit"]["zenodo_archive_sha256"],
        "zenodo_archive_bytes": protocol["frozen_unit"]["zenodo_archive_bytes"],
        "source_repository": "https://github.com/NutritionalLungImmunity/PAI",
        "source_revision": protocol["frozen_unit"]["content_witness_revision"],
        "source_tree": protocol["frozen_unit"]["content_witness_tree"],
        "source_manifest_sha256": protocol["source_freeze"]["source_manifest_sha256"],
        "tracked_jar_sha256": protocol["source_freeze"]["tracked_jar"]["sha256"],
        "archive_only_class_manifest_sha256": protocol["expected_archive_only_outputs"]["manifest_sha256"],
        "archive_only_class_count": 106,
        "cpp_PAIpp_exe": {
            "sha256": "23887c1ec55e689014298c8e276a4bafbfbd3ba9fbbb0e317505f33816c5f4d6",
            "required_archive_mode": "0755",
            "signed_revision_mode_to_explain": "100644",
        },
        "run_sh": {
            "sha256": "20464879ee7dfd8db06c1f7978488f8e78c021df6b97df530a86628835ca90d1",
            "required_archive_mode": "0755",
            "signed_revision_mode_to_explain": "100644",
        },
    },
    "required_predicates": [
        "State the exact compiler distribution, version, platform, digest and complete command that generated the 106 class files, or state that the tracked JAR is the authoritative byte source and identify its generating build.",
        "Bind the complete 106-output manifest; a subset or aggregate count is insufficient.",
        "State that cpp/PAIpp.exe and run.sh were deliberately released as mode 0755 in the exact checksum-bound archive, and explain the contradiction with the verified revision tree's 100644 modes.",
        "Bind the exact archive SHA-256, full revision and tree in the signed predicate.",
    ],
    "verification_gate": "Signature/issuer identity, subject digests, revision/tree, complete class manifest and both path-mode predicates must all verify. Gates are conjunctive and noncompensatory.",
    "alternative_provider_correction": "A replacement checksum-bound archive that exactly equals immutable revision aa021231... in every non-.git path, byte and executable bit also resolves the V12 residual without asserting build provenance for extra files.",
    "forbidden_inference": "Matching bytes, local compilation, a TAR header, README wording, a release title or repository commit signature alone does not satisfy this contract.",
}
write_json("AUTHOR_PROVIDER_SIGNING_CONTRACT_V12.json", signing_contract)

contract_md = f"""# P4 index-91 provider signing contract

This is the narrowest non-repeating contract for the remaining archive build/mode residual. It does not authorize scientific outcomes.

## Required signed subjects

- Zenodo archive: `{signing_contract['required_subjects']['zenodo_archive_sha256']}` ({signing_contract['required_subjects']['zenodo_archive_bytes']:,} bytes)
- Source revision/tree: `{signing_contract['required_subjects']['source_revision']}` / `{signing_contract['required_subjects']['source_tree']}`
- Tracked JAR: `{signing_contract['required_subjects']['tracked_jar_sha256']}`
- Complete 106-class manifest: `{signing_contract['required_subjects']['archive_only_class_manifest_sha256']}`
- `cpp/PAIpp.exe`: exact bytes plus deliberate archive mode `0755`, explaining signed-tree mode `100644`
- `run.sh`: exact bytes plus deliberate archive mode `0755`, explaining signed-tree mode `100644`

## Conjunctive predicate

The issuer must bind the exact compiler/build or authoritative tracked-JAR source, the full revision/tree, all 106 outputs, and both modes. Subset equality, matching bytes, README instructions, TAR metadata, a release title, or a commit signature alone is insufficient.

## Alternative correction

A replacement checksum-bound archive exactly equal to immutable revision `aa021231...` in every non-`.git` path, byte, and executable bit also resolves this residual.
"""
(ROOT / "AUTHOR_PROVIDER_SIGNING_CONTRACT_V12.md").write_text(contract_md)

tool_provenance = {
    "schema_version": "orion.p4.exact-edge-build-provenance.v12.tool-provenance",
    "protocol_sha256": PROTOCOL_SHA256,
    "jar_reader": protocol["pinned_lawful_tooling"]["jar_member_reader"],
    "compiler_image": protocol["pinned_lawful_tooling"]["compiler_container"],
    "compiler_probe": compiler,
    "network_client": "CPython urllib.request with GitHub API version 2022-11-28",
    "network_request_count": probe["network_request_count"],
    "rights_boundary": "PAI archive/revision rights were adjudicated MIT in immutable V11. Tool licensing permits the investigation but does not supply provider provenance.",
}
write_json("TOOL_PROVENANCE_V12.json", tool_provenance)

negative = {
    "schema_version": "orion.p4.exact-edge-build-provenance.v12.negative-result-ledger",
    "frozen_index": 91,
    "rows": [
        {
            "issue": "fresh_source_compilation_exactness",
            "observation": "The exact 106 archived class bytes project from the immutable-revision tracked JAR, but the prospectively pinned compiler did not execute because no OCI runtime was available and the lawful disposable runtime failed closed, finally on no space left on device.",
            "verdict": "CANNOT_CHECK",
            "next_discriminator": compiler["nonrepeating_discriminator"],
        },
        {
            "issue": "provider_native_class_build_provenance",
            "observation": "106/106 tracked-JAR class members match archive extras exactly, but no signed build predicate binds the JAR/classes to their generating compiler and source revision.",
            "verdict": "CANNOT_CHECK",
            "next_discriminator": "Satisfy AUTHOR_PROVIDER_SIGNING_CONTRACT_V12.json for the complete class manifest.",
        },
        {
            "issue": "two_archive_executable_mode_drifts",
            "observation": "GitHub histories and the validly signed current revision tree expose both paths as 100644; the archive has 0755. Exact archive/file attestation endpoints return 404, and the one GitHub release has no assets or predicate binding archive digest, revision, paths and modes.",
            "verdict": "CONTRADICTED_AND_CANNOT_CHECK_AUTHORITY",
            "next_discriminator": "Provider-correct the archive to the signed tree modes or sign the deliberate 0755 release predicate required by AUTHOR_PROVIDER_SIGNING_CONTRACT_V12.json.",
        },
    ],
}
write_json("NEGATIVE_RESULT_LEDGER_V12.json", negative)

results_md = f"""# P4 exact-edge build/provenance V12 results

## Verdict

V12 finds a **positive exact packaged-byte result** but closes **0** P4 edges. The cumulative bridge remains **76/80**, and index 91 remains `CANNOT_CHECK`.

## 106 archived Java class extras

The immutable GitHub revision tracks `java/jPAI.jar` at SHA-256 `{projection['tracked_jar']['sha256']}`. A prospectively frozen, read-only ZIP projection produced exactly **106** `.class` members. After prefixing them with `java/bin/`, the complete multiset equals all 106 Zenodo-archive-only class files: **0 missing, 0 extra, 0 different-byte**. All 106 class files have major version **61** (Java 17).

This is exact packaged-byte availability from the GitHub-authenticated tree, not fresh source compilation and not signed build provenance. The prospectively pinned `eclipse-temurin` 17.0.14+7 linux/arm64 image could not execute: Docker had no daemon/application, and the lawful disposable Colima route ultimately failed with exact terminal `no space left on device`. No substitute compiler and no pytest/CI were used.

## Two executable-mode drifts

GitHub path histories expose one introducing commit for each path. The introducing commit is unsigned; the current content-witness commit `aa021231...` has valid GitHub verification. Both provider trees record `cpp/PAIpp.exe` and `run.sh` as mode **100644**, whereas the checksum-bound archive TAR records both as **0755**. GitHub exact-subject attestation endpoints for the archive and both files return **404**. The one GitHub release has **0 assets** and no predicate binding the archive digest, revision, paths, or modes.

Therefore matching bytes do not establish authority. The archive mode changes are not merely unsigned; they contradict the validly signed revision tree and lack a signed release explanation.

## Closure gates

| Gate | Result |
|---|---|
| Complete tracked-JAR projection equals 106 archive extras | **PASS** |
| Fresh source compilation under the pinned toolchain | **CANNOT_CHECK** |
| Provider-native signed class build provenance | **FAIL** |
| `cpp/PAIpp.exe` archive mode 0755 has signed release authority | **FAIL** |
| `run.sh` archive mode 0755 has signed release authority | **FAIL** |
| Index 91 exact edge closes | **FAIL** |

## Next causal discriminator

Do not repeat the unavailable-runtime probe. Either (1) execute the already frozen linux/arm64 image digest once an OCI runtime and sufficient disposable disk exist, then require the provider signing contract even if bytes match; (2) obtain `AUTHOR_PROVIDER_SIGNING_CONTRACT_V12.json`, binding the exact archive, revision/tree, complete 106-output manifest, build identity, and both deliberate 0755 modes; or (3) provider-replace the checksum-bound archive with one exactly matching immutable revision `aa021231...`, including its signed 100644 modes.

## Scientific boundary

No natural-pair, author-lineage, source-disjoint replication, external custody, comparator outcome, performance, or superiority authority is added. No P4 manuscript or claim-ledger edit is authorized.
"""
(ROOT / "RESULTS_V12.md").write_text(results_md)

(ROOT / "OMITTED_LARGE_ARTIFACTS_V12.md").write_text(
    """# Omitted large artifacts — P4 V12

The checksum-bound Zenodo archive and immutable GitHub codeload were reacquired transiently, hash-checked, and removed after the packet-local manifests were produced.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Zenodo record 20171460 archive | 17,147,954 | `2a94e0ed7e61e18ea4135aa559d6a06a407adcabd84dbbc52ebface6bba5b407` |
| GitHub codeload `aa021231...` | 6,909,445 | `d43c827568d1acef62cea08990580a95ea5869f9eef4106fb3da8b941377e5af` |

No private payload was used. The failed disposable OCI runtime and its cache were removed.
"""
)

(ROOT / "HANDOFF_V12.md").write_text(
    """# P4 V12 handoff

- Scope: index 91 only; immutable V10/V11 preserved.
- Positive: tracked `java/jPAI.jar` projects exactly to all 106 archive-only classes (0 missing/extra/different; class major 61).
- Bounded compile: not executed; exact pinned runtime unavailable and disposable Colima route failed on disk space. No substitute was used.
- Modes: the validly signed current GitHub tree says 100644 for both files; Zenodo TAR says 0755; exact attestations are 404 and the release has no assets/provenance predicate.
- Verdict: 0 closures; cumulative P4 bridge remains 76/80.
- Next: use the frozen image only after runtime/disk changes, satisfy the provider signing contract, or obtain a corrected archive exactly matching the signed tree.
- No manuscript/claim-ledger edits, pytest, or repository CI.
"""
)

evidence_names = [
    "AUTHOR_PROVIDER_SIGNING_CONTRACT_V12.json",
    "AUTHOR_PROVIDER_SIGNING_CONTRACT_V12.md",
    "COMPILER_PROBE_V12.json",
    "HANDOFF_V12.md",
    "JAR_PROJECTION_V12.json",
    "MODE_AUTHORITY_V12.json",
    "NEGATIVE_RESULT_LEDGER_V12.json",
    "OMITTED_LARGE_ARTIFACTS_V12.md",
    "PROBE_RECEIPT_V12.json",
    "PROTOCOL_FREEZE_RECEIPT_V12.json",
    "PROTOCOL_V12.json",
    "RESULTS_V12.md",
    "SBOM_V12.json",
    "TOOL_PROVENANCE_V12.json",
]
evidence = {
    name: {"bytes": (ROOT / name).stat().st_size, "sha256": sha(ROOT / name)}
    for name in evidence_names
}
evidence["development/p4-exact-edge-lineage-authority-v11-2026-08-24/RESULT_V11.json"] = {
    "bytes": (V11 / "RESULT_V11.json").stat().st_size,
    "sha256": sha(V11 / "RESULT_V11.json"),
}

result = {
    "schema_version": "orion.p4.exact-edge-build-provenance.v12.result",
    "identity": protocol["identity"],
    "protocol_sha256": PROTOCOL_SHA256,
    "adjudicated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "frozen_index": 91,
    "v12_closed_count": 0,
    "v12_closed_indices": [],
    "v12_remaining_count": 1,
    "v12_remaining_indices": [91],
    "cumulative_exact_bridge": "76/80",
    "cumulative_exact_by_domain": {
        "EARTH_ENVIRONMENT": 5,
        "LIFE_BIOMEDICAL": 7,
        "PHYSICAL_ENGINEERING": 4,
        "SCIENTIFIC_SOFTWARE": 60,
    },
    "class_findings": {
        "tracked_jar_projection_exact": True,
        "expected_count": 106,
        "observed_count": 106,
        "missing_count": 0,
        "extra_count": 0,
        "different_byte_count": 0,
        "class_major_version_counts": {"61": 106},
        "fresh_source_compiler_executed": False,
        "fresh_source_compilation_exact": None,
        "provider_native_signed_build_provenance": False,
    },
    "mode_findings": {
        "archive_modes": {"cpp/PAIpp.exe": "0755", "run.sh": "0755"},
        "signed_current_revision_modes": {"cpp/PAIpp.exe": "100644", "run.sh": "100644"},
        "current_revision_signature_valid": True,
        "exact_subject_attestation_statuses": {
            "zenodo_archive": 404,
            "cpp/PAIpp.exe": 404,
            "run.sh": 404,
        },
        "github_release_count": 1,
        "github_release_asset_count": 0,
        "provider_native_signed_mode_authority": {
            "cpp/PAIpp.exe": False,
            "run.sh": False,
        },
    },
    "gates": {
        "complete_tracked_jar_projection_exact": True,
        "fresh_source_compilation_exact": False,
        "provider_native_signed_class_build_provenance": False,
        "cpp_PAIpp_exe_signed_archive_mode_authority": False,
        "run_sh_signed_archive_mode_authority": False,
        "all_index_91_closure_gates": False,
    },
    "verdict": "REMAINS_CANNOT_CHECK",
    "exact_terminal": "EXACT_JAR_PROJECTION_POSITIVE_BUT_PINNED_SOURCE_COMPILE_UNAVAILABLE_AND_SIGNED_REVISION_MODES_CONTRADICT_ARCHIVE_0755",
    "next_causal_discriminator": "Use the frozen compiler image only after OCI-runtime/disk availability changes, then require the provider signing contract; or provider-replace the checksum-bound archive so every non-.git path, byte and executable bit exactly equals the signed immutable revision.",
    "natural_pair_and_scientific_boundary": {
        "eligible_natural_pairs_added": 0,
        "author_lineage_adjudications_added": 0,
        "external_custody_added": False,
        "comparator_outcomes_accessed": False,
        "scientific_authority_granted": False,
        "programme_terminal": "P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK",
    },
    "pytest_run": False,
    "repository_ci_run": False,
    "manuscript_or_claim_ledger_modified": False,
    "evidence": evidence,
}
write_json("RESULT_V12.json", result)
print(
    json.dumps(
        {
            "jar_projection_exact": True,
            "closed": 0,
            "bridge": "76/80",
            "verdict": result["verdict"],
        },
        sort_keys=True,
    )
)
