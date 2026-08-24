#!/usr/bin/env python3
"""Fail-closed adjudication of the ten frozen P4 V8 identity rows."""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
V7 = HERE.parent / "p4-unresolved-identity-v7-2026-08-23" / "IDENTITY_RESOLUTION_ROWS_V7.jsonl"
PROTOCOL = HERE / "PROTOCOL_V8.json"
PROVIDER = HERE / "PROVIDER_PROBE_RECEIPT_V8.json"
SWH199 = HERE / "SWH_199_PROBE_RECEIPT_V8.json"
OUT_JSON = HERE / "FINAL_IDENTITY_RESOLUTION_V8.json"
OUT_MD = HERE / "FINAL_IDENTITY_RESOLUTION_V8.md"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def request_url(obj: dict | None) -> str | None:
    return (obj or {}).get("url")


def main() -> None:
    clock = time.monotonic()
    started_at = now()
    protocol = json.loads(PROTOCOL.read_text())
    provider = json.loads(PROVIDER.read_text())
    swh199 = json.loads(SWH199.read_text())
    wanted = {target["frozen_index"] for target in protocol["scope"]["targets"]}
    v7_rows = {}
    for line in V7.read_text().splitlines():
        row = json.loads(line)
        if row.get("frozen_index") in wanted:
            v7_rows[row["frozen_index"]] = row
    probes = {probe["frozen_index"]: probe for probe in provider["probes"]}

    decisions = {
        36: {
            "verdict": "REMAINS_CANNOT_CHECK",
            "identity_method": None,
            "gate_updates": {
                "accepted_archive_software_rights": True,
                "public_transport_receipted": True,
            },
            "residual": "EXACT_ARCHIVE_VERSION_DOI_RELATION_AND_ARCHIVE_ROOT_TO_TAG_COMMIT_IDENTITY_CANNOT_CHECK",
            "next_discriminator": "Provider-native correction or immutable child metadata must bind the frozen concept DOI to version 0.0.3 and the deposited root to commit 069ab4f56d100d765d46c594ac1b06add7e49f9e; the current child description says 0.0.12 and the embedded 0.0.3 ref is historical rather than the archive HEAD.",
            "finding": "The checksum-verified archive supplies Apache-2.0 rights and an embedded historical refs/tags/0.0.3 edge, but Zenodo exposes no unique provider version match and describes the child as JOSS accepted version 0.0.12.",
        },
        59: {
            "verdict": "RESOLVED_SAME_IDENTITY",
            "identity_method": "V7_EXACT_ARCHIVE_MANIFEST_EQUALS_IMMUTABLE_COMMIT_ARCHIVE_MANIFEST_PLUS_V8_ARCHIVE_LICENSE_BYTE_EQUALS_EXACT_COMMIT_LICENSE",
            "gate_updates": {"accepted_archive_software_rights": True},
            "residual": None,
            "next_discriminator": None,
            "finding": "The checksum-verified exact archive contains Apache-2.0 LICENSE bytes whose SHA-256 equals the license bytes fetched at exact commit 944d2763a4f67b266beaf427a912ba1d2ac298be; this closes the sole V7 gate.",
        },
        91: {
            "verdict": "REMAINS_CANNOT_CHECK",
            "identity_method": None,
            "gate_updates": {},
            "residual": "ARCHIVE_TO_COMMIT_AUTHENTICATED_IDENTITY_CANNOT_CHECK",
            "next_discriminator": "An authoritative provider relation or archive provenance record must name exact commit 9fa30e9f405de4446c792bd59cb7c5a4bb7ecb59, or provider archive content must exactly equal that immutable commit tree.",
            "finding": "The checksum-verified archive has MIT rights, but its embedded Git provenance names other full commits and does not name the accepted v1.0.0 commit.",
        },
        108: {
            "verdict": "RESOLVED_SAME_IDENTITY",
            "identity_method": "PROVIDER_CHECKSUM_VERIFIED_ARCHIVE_EMBEDS_EXACT_GIT_TAG_REF_AND_FETCH_HEAD_TO_ACCEPTED_FULL_COMMIT",
            "gate_updates": {"archive_to_commit_content_or_authenticated_origin_identity": True},
            "residual": None,
            "next_discriminator": None,
            "finding": "The checksum-verified archive embeds .git/refs/tags/v0.3.3.4 with exactly 1e831e074ae465956b66305df029bfcd286afe9f and FETCH_HEAD repeats that exact tag-to-origin edge; BSD-3-Clause rights are present at archive and commit.",
        },
        133: {
            "verdict": "REMAINS_CANNOT_CHECK",
            "identity_method": None,
            "gate_updates": {},
            "residual": "ARCHIVE_TO_COMMIT_AUTHENTICATED_IDENTITY_CANNOT_CHECK",
            "next_discriminator": "The provider must expose an authenticated full revision edge to 7ac6d23d504404c4004faad663f6b889427109e6 or exact provider archive content must equal that immutable commit tree.",
            "finding": "MIT archive rights are confirmed, but no full commit or tag provenance occurs in the exact archive and the prior normalized manifests did not match.",
        },
        165: {
            "verdict": "REMAINS_CANNOT_CHECK",
            "identity_method": None,
            "gate_updates": {"accepted_archive_software_rights": True},
            "residual": "ARCHIVE_TO_COMMIT_AUTHENTICATED_IDENTITY_CANNOT_CHECK",
            "next_discriminator": "The provider must expose an authenticated full revision edge to b52a049f685af3fc849359673c4ac183e7ccc5d3 or exact provider archive content must equal that immutable commit tree.",
            "finding": "The 106 MB checksum-verified provider archive embeds an accepted MIT LICENSE, repairing archive rights, but it contains no exact commit provenance.",
        },
        185: {
            "verdict": "REMAINS_CANNOT_CHECK",
            "identity_method": None,
            "gate_updates": {},
            "residual": "EXACT_TAG_TO_FULL_COMMIT_AND_ARCHIVE_TO_COMMIT_IDENTITY_CANNOT_CHECK",
            "next_discriminator": "A source-native restored v0.14.0 ref/release or provider-authenticated metadata must disclose its full immutable commit; only then can exact commit rights and archive identity be bound.",
            "finding": "The exact archive is public and contains MIT rights, but the source-native v0.14.0 release endpoint is absent and the archive contains no immutable commit marker.",
        },
        190: {
            "verdict": "REMAINS_CANNOT_CHECK",
            "identity_method": None,
            "gate_updates": {},
            "residual": "EXACT_TAG_TO_FULL_COMMIT_AND_ARCHIVE_TO_COMMIT_IDENTITY_CANNOT_CHECK",
            "next_discriminator": "A source-native restored 1.1.0 ref/release or provider-authenticated metadata must disclose its full immutable commit; only then can exact commit rights and archive identity be bound.",
            "finding": "The exact archive is public and contains MIT rights plus a version-bearing CITATION.cff, but the source-native 1.1.0 release endpoint is absent and no full commit occurs in archive provenance.",
        },
        196: {
            "verdict": "RESOLVED_SAME_IDENTITY",
            "identity_method": "DATACITE_HASVERSION_UNIQUE_ZENODO_V1.1.0_CHILD_PLUS_V7_QUALIFIED_SWHID_DIRECTORY_EQUALS_GIT_COMMIT_ROOT_TREE",
            "gate_updates": {
                "exact_frozen_archive_version_doi_relation": True,
                "archive_to_commit_content_or_authenticated_origin_identity": True,
                "accepted_archive_software_rights": True,
                "public_transport_receipted": True,
            },
            "residual": None,
            "next_discriminator": None,
            "finding": "DataCite binds concept DOI 10.5281/zenodo.19141362 by HasVersion to the unique Zenodo V1.1.0 child 10.5281/zenodo.19141363; its checksum-verified archive retains the qualified SWH path already proven equal to commit ba11b623cebc5d042f7bbe6c23b1f48c5d71c27f root tree, and MIT LICENSE bytes equal the exact-commit license.",
        },
        199: {
            "verdict": "REMAINS_CANNOT_CHECK",
            "identity_method": None,
            "gate_updates": {},
            "residual": "EXACT_TAG_TO_FULL_COMMIT_AND_ARCHIVE_TO_COMMIT_IDENTITY_CANNOT_CHECK",
            "next_discriminator": "Software Heritage or the source provider must expose a full revision edge for the archived 0f8b2db prefix and bind v0.13.4 to it; the current authenticated SWH release terminates at a directory, not a revision.",
            "finding": "The checksum-verified archive contains MIT rights and a path suffix 0f8b2db, but GitHub reports no commit for that prefix and the exact SWH anchor is a synthetic Zenodo release targeting directory ba731454bcc111627e810d5f3782af88c718e8f9 rather than a full revision.",
        },
    }

    rows = []
    for index in sorted(wanted):
        base = v7_rows[index]
        probe = probes[index]
        analysis = probe.get("archive_transport_retry_analysis") or {}
        decision = decisions[index]
        gates = dict(base["gates"])
        gates.update(decision["gate_updates"])
        archive_request = probe.get("archive_transport_retry") or {}
        license_candidates = [
            {
                "path": item.get("member_path"),
                "spdx": item.get("detected_spdx"),
                "sha256": item.get("member_sha256"),
            }
            for item in analysis.get("license_candidates", [])
            if item.get("accepted_spdx")
        ]
        exact_commit_license = probe.get("exact_commit_license") or {}
        URLs = [
            request_url(archive_request),
            request_url((probe.get("source_native_release") or {}).get("request")),
            request_url(exact_commit_license.get("request")),
        ]
        if index in {36, 196}:
            URLs.append(request_url((probe.get("datacite_frozen_doi") or {}).get("request")))
        if index == 199:
            URLs.append(request_url(swh199.get("request")))
        repaired_gates = sorted(
            gate for gate, value in gates.items() if value and not base["gates"].get(gate, False)
        )
        unresolved_gates = sorted(gate for gate, value in gates.items() if not value)
        resolved = decision["verdict"] == "RESOLVED_SAME_IDENTITY"
        if resolved and unresolved_gates:
            raise RuntimeError(f"resolved row {index} retains false gates: {unresolved_gates}")
        rows.append(
            {
                "frozen_index": index,
                "repository": base["repository"],
                "publication_doi": base["publication_doi"],
                "archive_doi": base["archive_doi"],
                "publication_version": (base.get("joss_review_evidence") or {}).get("version_field"),
                "accepted_exact_tag_commit": base.get("accepted_exact_tag_commit"),
                "verdict": decision["verdict"],
                "finding": decision["finding"],
                "accepted_identity_method": decision["identity_method"],
                "repaired_gates": repaired_gates,
                "gates_v8": gates,
                "residual": decision["residual"],
                "next_discriminator": decision["next_discriminator"],
                "archive_transport": {
                    "url": archive_request.get("url"),
                    "http_status": archive_request.get("http_status"),
                    "body_bytes": archive_request.get("body_bytes"),
                    "body_md5": archive_request.get("body_md5"),
                    "body_sha256": archive_request.get("body_sha256"),
                    "provider_checksum": probe.get("archive_transport_retry_provider_checksum"),
                    "provider_checksum_verified": probe.get("archive_transport_retry_checksum_verified"),
                    "started_at": archive_request.get("started_at"),
                    "finished_at": archive_request.get("finished_at"),
                },
                "archive_license_candidates": license_candidates,
                "exact_full_commit_hits": analysis.get("exact_full_commit_hits", []),
                "exact_tag_provenance_hits": analysis.get("exact_tag_provenance_hits", []),
                "exact_commit_license": exact_commit_license or None,
                "authoritative_urls": [url for url in URLs if url],
                "v7_row_sha256": probe["v7_row_line_sha256"],
            }
        )

    repaired = [row for row in rows if row["verdict"] == "RESOLVED_SAME_IDENTITY"]
    remaining = [row for row in rows if row["verdict"] != "RESOLVED_SAME_IDENTITY"]
    adjudication_runtime = round(time.monotonic() - clock, 6)
    measured_runtime = round(
        provider["runtime_seconds"]
        + provider["archive_transport_retry"]["runtime_seconds"]
        + swh199["runtime_seconds"]
        + adjudication_runtime,
        6,
    )
    receipt = {
        "schema_version": "orion.p4.unresolved-identity-final-adjudication.v8",
        "authority": protocol["authority"],
        "scope": {
            "frozen_target_count": len(rows),
            "replacement_archives": False,
            "replacement_publications": False,
            "broad_harvest": False,
            "unit_inflation": False,
        },
        "started_at": started_at,
        "finished_at": now(),
        "runtime": {
            "provider_pass_seconds": provider["runtime_seconds"],
            "archive_transport_retry_seconds": provider["archive_transport_retry"]["runtime_seconds"],
            "swh_199_probe_seconds": swh199["runtime_seconds"],
            "adjudication_seconds": adjudication_runtime,
            "total_measured_execution_seconds": measured_runtime,
        },
        "inputs": {
            "protocol": {"path": PROTOCOL.name, "sha256": sha256_file(PROTOCOL)},
            "provider_receipt": {"path": PROVIDER.name, "sha256": sha256_file(PROVIDER)},
            "swh_199_receipt": {"path": SWH199.name, "sha256": sha256_file(SWH199)},
            "v7_rows": {"path": str(V7), "sha256": sha256_file(V7)},
        },
        "summary": {
            "repaired_same_identity_count": len(repaired),
            "repaired_indices": [row["frozen_index"] for row in repaired],
            "remaining_cannot_check_count": len(remaining),
            "remaining_indices": [row["frozen_index"] for row in remaining],
            "exact_archive_transport_pass_count": sum(
                row["archive_transport"]["http_status"] == 200
                and row["archive_transport"]["provider_checksum_verified"] is True
                for row in rows
            ),
        },
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")

    lines = [
        "# P4 unresolved identity targeted pass V8",
        "",
        f"- Frozen targets: **{len(rows)}**",
        f"- Repaired to `RESOLVED_SAME_IDENTITY`: **{len(repaired)}** — {', '.join(map(str, receipt['summary']['repaired_indices']))}",
        f"- Remaining fail-closed: **{len(remaining)}** — {', '.join(map(str, receipt['summary']['remaining_indices']))}",
        f"- Provider archives fetched and checksum-verified: **{receipt['summary']['exact_archive_transport_pass_count']}/{len(rows)}**",
        f"- Total measured execution runtime: **{measured_runtime:.6f} s**",
        "- Scope: exact frozen targets only; no replacements, proxies, broad harvesting, or unit inflation.",
        "",
        "## Adjudication",
        "",
        "| Index | Repository | Verdict | Repaired gate(s) | Exact residual / next discriminator |",
        "|---:|---|---|---|---|",
    ]
    for row in rows:
        repaired_text = ", ".join(f"`{gate}`" for gate in row["repaired_gates"]) or "—"
        residual = "Closed" if not row["residual"] else f"`{row['residual']}`. {row['next_discriminator']}"
        lines.append(
            f"| {row['frozen_index']} | `{row['repository']}` | `{row['verdict']}` | {repaired_text} | {residual} |"
        )
    lines.extend(
        [
            "",
            "## Closed identity chains",
            "",
            "- **59 PSD:** exact version DOI/archive + V7 immutable-commit manifest equality + V8 Apache-2.0 archive license bytes equal exact-commit license bytes.",
            "- **108 FAIRLinked:** checksum-verified provider archive embeds `refs/tags/v0.3.3.4 -> 1e831e074ae465956b66305df029bfcd286afe9f` and matching origin `FETCH_HEAD`; archive and commit rights are BSD-3-Clause.",
            "- **196 SEPARATE:** DataCite `HasVersion` binds the concept DOI to unique Zenodo child `10.5281/zenodo.19141363` version `V1.1.0`; V7 SWH-directory/Git-tree equality binds the archive to commit `ba11b623cebc5d042f7bbe6c23b1f48c5d71c27f`; MIT license bytes match.",
            "",
            "## Evidence receipts",
            "",
            f"- `{PROTOCOL.name}` — `{sha256_file(PROTOCOL)}`",
            f"- `{PROVIDER.name}` — `{sha256_file(PROVIDER)}`",
            f"- `{SWH199.name}` — `{sha256_file(SWH199)}`",
            f"- `{OUT_JSON.name}` — written from the frozen gates and receipts above",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(
        "P4_V8_FINAL_ADJUDICATION_COMPLETE__"
        f"REPAIRED={len(repaired)}__REMAINING={len(remaining)}__"
        f"TOTAL_MEASURED_RUNTIME_SECONDS={measured_runtime:.6f}"
    )


if __name__ == "__main__":
    main()
