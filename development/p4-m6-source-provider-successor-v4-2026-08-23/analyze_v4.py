#!/usr/bin/env python3
"""Analyze the frozen P4 M6 V4 public-metadata harvest without outcomes."""

from __future__ import annotations

import collections
import datetime as dt
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CHECKOUT = Path("/Users/billy/Documents/Codex/2026-08-23/can-x20/work/orion-takeover")


def load(path: Path):
    return json.loads(path.read_text())


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value) -> None:
    path.write_text(json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n")


protocol = load(ROOT / "PROTOCOL_V4.json")
freeze = load(ROOT / "PROTOCOL_FREEZE_RECEIPT_V4.json")
transport = load(ROOT / "TRANSPORT_LOG_V4.json")
v3 = load(CHECKOUT / "development/p4-source-universe-successor-v3-2026-08-23/RESULT_V1.json")
rows = [json.loads(line) for line in (ROOT / "CANDIDATES_V4.jsonl").read_text().splitlines() if line]
provider_qualified = [row for row in rows if row.get("strict_eligible")]

domains = protocol["scope"]["domains"]
v3_counts = protocol["scope"]["predecessor_observed_strict_counts"]
v4_counts = collections.Counter(row["domain_classification"]["assigned_domain"] for row in provider_qualified)

accepted_spdx = set(protocol["strict_candidate_unit"]["accepted_spdx"])
stage_counts = {
    "crossref_unique_joss_publications": len(rows),
    "joss_labelled_repository_relations": sum((row.get("joss_relation") or {}).get("relation_status") == "PASS" for row in rows),
    "public_active_github_repositories": sum(bool(row.get("repository")) and row["repository"].get("private") is False and row["repository"].get("visibility") == "public" and not row["repository"].get("archived") and not row["repository"].get("disabled") for row in rows),
    "latest_github_releases_bound": sum(bool(row.get("release")) for row in rows),
    "release_tags_resolved_to_commit_sha": sum((row.get("tag_resolution") or {}).get("status") == "PASS" for row in rows),
    "accepted_exact_tag_license_and_blob": sum((row.get("license_at_release") or {}).get("spdx_id") in accepted_spdx and bool((row.get("license_at_release") or {}).get("license_blob_sha")) for row in rows),
    "unique_domain_assignment": sum((row.get("domain_classification") or {}).get("status") == "PASS" for row in rows),
    "provider_qualified_concept_candidates": len(provider_qualified),
    "explicit_joss_publication_to_exact_github_release_tag_alignment": 0,
    "author_lineage_independence_adjudicated": 0,
    "natural_pairs_adjudicated": 0,
}

failure_counts = collections.Counter(cause for row in rows for cause in row.get("failure_causes", []))
license_counts = collections.Counter((row.get("license_at_release") or {}).get("spdx_id") for row in provider_qualified)

cells = {}
for domain in domains:
    prior = int(v3_counts[domain])
    added = int(v4_counts[domain])
    optimistic = prior + added
    provider_counts = {"FIGSHARE_V3_LOWER_BOUND": prior, "JOSS_GITHUB_RELEASE_V4_PROVIDER_QUALIFIED": added}
    primary_family = None
    primary_available = 0
    replication_available = 0
    if added >= prior:
        primary_family, primary_available, replication_available = "JOSS_GITHUB_RELEASE", added, prior
    else:
        primary_family, primary_available, replication_available = "FIGSHARE", prior, added
    optimistic_quota = optimistic >= 48
    optimistic_primary = primary_available >= 24
    optimistic_replication = replication_available >= 8
    cells[domain] = {
        "mechanism": "M6_ARTICLE_TO_CODE_RELEASE",
        "v3_observed_strict_metadata_lower_bound": prior,
        "v4_provider_qualified_concept_candidates": added,
        "v4_exact_publication_release_aligned_units": 0,
        "v4_units_promoted_through_all_relation_lineage_and_natural_pair_gates": 0,
        "optimistic_union_before_exact_version_and_external_adjudication": optimistic,
        "optimistic_gap_to_48": max(0, 48 - optimistic),
        "provider_family_counts": provider_counts,
        "optimistic_primary_family": primary_family,
        "optimistic_primary_units": primary_available,
        "optimistic_disjoint_replication_units": replication_available,
        "optimistic_total_quota_pass": optimistic_quota,
        "optimistic_primary_24_pass": optimistic_primary,
        "optimistic_disjoint_replication_8_pass": optimistic_replication,
        "full_cell_gate": "CANNOT_CHECK",
        "gap_is_confirmed_population_deficit": False,
        "reason": "V3 transport remains incomplete; its omitted row-level packet prevents cross-provider concept/publication deduplication; V4 also has no explicit JOSS-publication-to-exact-GitHub-release-tag alignment or external author-lineage/natural-pair adjudication.",
    }

cell_counts = {
    "schema_version": "orion.p4.m6.source-provider-successor.cell-counts.v4",
    "protocol_id": protocol["protocol_id"],
    "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "authority": protocol["authority"],
    "stage_counts": stage_counts,
    "provider_qualified_by_domain": dict(sorted(v4_counts.items())),
    "accepted_license_distribution_among_provider_qualified": {str(k): v for k, v in sorted(license_counts.items(), key=lambda item: str(item[0]))},
    "cells": cells,
    "all_four_m6_cells_pass": False,
    "all_four_m6_cells_gate_evaluable": False,
    "preserved_terminal": "P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK",
}
write(ROOT / "CELL_COUNTS_V4.json", cell_counts)

audit = {
    "schema_version": "orion.p4.m6.source-provider-successor.audit.v4",
    "protocol_id": protocol["protocol_id"],
    "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "provider_route": {
        "publication_provider": "JOURNAL_OF_OPEN_SOURCE_SOFTWARE",
        "content_provider": "GITHUB_RELEASES",
        "counting_family": "JOSS_GITHUB_RELEASE",
        "source_disjoint_from_figshare": True,
        "within_family_independent_provider_count": 1,
        "rule": "papers, repositories, organizations, releases and tags do not create additional provider families",
        "item_level_overlap_with_v3": "CANNOT_CHECK__V3_CANDIDATE_JSONL_OMITTED_FROM_BOUNDED_PACKET",
    },
    "rights": {
        "accepted_exact_tag_license_and_blob": stage_counts["accepted_exact_tag_license_and_blob"],
        "provider_qualified_license_distribution": cell_counts["accepted_license_distribution_among_provider_qualified"],
        "failed_or_unbound_exact_release_license": failure_counts["EXACT_RELEASE_LICENSE_GATE_FAIL"],
        "boundary": "default-branch licence inference is forbidden; only the GitHub licence endpoint at the exact release tag and its blob SHA were accepted",
    },
    "relation": {
        "joss_labelled_repository_relation": stage_counts["joss_labelled_repository_relations"],
        "missing_or_ambiguous_joss_relation": failure_counts["JOSS_STRUCTURED_REPOSITORY_RELATION_CANNOT_CHECK"],
        "exact_publication_to_release_tag_alignment": 0,
        "boundary": "JOSS-to-repository plus a current immutable release identifies a publication-linked software concept, but does not prove that the current tag is the version evaluated by the JOSS paper",
    },
    "immutable_identity": {
        "repository_identities_bound": stage_counts["public_active_github_repositories"],
        "release_identities_bound": stage_counts["latest_github_releases_bound"],
        "release_tags_resolved_to_commit_sha": stage_counts["release_tags_resolved_to_commit_sha"],
        "release_or_tag_shortfall": failure_counts["GITHUB_LATEST_RELEASE_CANNOT_CHECK"],
    },
    "transport": {
        "crossref_rows_requested": transport["frozen_rows_requested"],
        "crossref_rows_returned": transport["crossref_rows_returned"],
        "joss_http_transport_failures": transport["joss_transport_failures"],
        "github_repository_transport_failures": transport["github_repository_transport_failures"],
        "bounded_v4_transport_status": "COMPLETE_FOR_FROZEN_200_PUBLICATION_FRAME",
        "predecessor_transport_status": v3["terminal"],
    },
    "domain": {
        "unique_assignments": stage_counts["unique_domain_assignment"],
        "ambiguous": failure_counts["CANNOT_CHECK_DOMAIN_AMBIGUOUS"],
        "unclassified": failure_counts["CANNOT_CHECK_DOMAIN_UNCLASSIFIED"],
        "provider_qualified_by_domain": cell_counts["provider_qualified_by_domain"],
        "authority": "development classification only",
    },
    "author_lineage": {
        "publication_author_signatures_retained": sum(bool(row.get("publication_authors")) for row in rows),
        "independence_adjudicated": 0,
        "status": "CANNOT_CHECK_EXTERNAL_ADJUDICATION_REQUIRED",
    },
    "unit_integrity": {
        "candidate_rows": len(rows),
        "provider_qualified_unique_doi_repository_concepts": len(provider_qualified),
        "duplicate_failures": failure_counts["DUPLICATE_PUBLICATION_DOI"] + failure_counts["DUPLICATE_REPOSITORY_CONCEPT"],
        "cross_provider_concept_and_publication_deduplication": "CANNOT_CHECK_AGAINST_V3_OMITTED_ROW_IDENTITIES",
        "not_counted_as_units": protocol["strict_candidate_unit"]["not_independent_units"],
    },
    "outcomes_accessed": False,
    "protected_data_accessed": False,
}
write(ROOT / "RIGHTS_RELATION_TRANSPORT_AUDIT_V4.json", audit)

ledger_entries = [
    {
        "issue": "CROSS_PROVIDER_CONCEPT_AND_PUBLICATION_DEDUPLICATION",
        "cause": "The integrated V3 bounded packet omits its 2,371-row candidate JSONL and retains only hashes plus opaque candidate ids, so V4 cannot compare JOSS DOI/repository concepts against the nine observed V3 M6 concepts.",
        "observed": "JOSS/GitHub is structurally a provider family distinct from Figshare, but item-level publication, repository and artifact overlap is not evaluable from the bounded V3 packet.",
        "residual": "All V3+V4 union counts are explicitly optimistic before cross-provider concept/publication deduplication and cannot authorize quota passage.",
        "next_discriminator": "Recover or deterministically reconstruct the exact bounded V3 M6 publication/object identities under their recorded candidate JSONL SHA-256, then deduplicate publication DOI, software concept, repository and artifact before any allocation.",
    },
    {
        "issue": "EXACT_PUBLICATION_TO_RELEASE_VERSION_RELATION",
        "cause": "JOSS labels a repository and a software archive, while the frozen GitHub lane binds the current latest release; the JOSS page does not assert that release tag as the paper-evaluated version.",
        "observed": f"{len(provider_qualified)} provider-qualified DOI/repository concepts; 0 exact paper-to-GitHub-tag alignments.",
        "residual": "All V4 release-level promotions remain CANNOT_CHECK even when repository relation, tag commit and tag licence pass.",
        "next_discriminator": "Freeze the same 200 DOI identities in a V4.1 bridge before access, parse each JOSS Software archive DOI, and require its immutable archive version/repository metadata to identify the exact GitHub tag and commit; add no DOI or replacement query.",
    },
    {
        "issue": "EARTH_LIFE_PHYSICAL_CELL_SHORTFALL",
        "cause": "The unchanged cross-domain lexicon assigns only 5 Earth, 7 Life and 6 Physical provider-qualified JOSS/GitHub concepts in the frozen recent-publication frame.",
        "observed": "Even optimistically unioned with V3 lower bounds, each cell has 7/48 and remains 41 short.",
        "residual": "The bounded JOSS/GitHub frame cannot close these three cell quotas; the gaps are not population deficits because V3 transport is incomplete.",
        "next_discriminator": "After the archive-tag bridge, freeze separate exact-rights domain-provider frames: Bioconductor release plus software-paper citation for Life, and domain-stratified JOSS archive identities or another publication-linked release provider for Earth and Physical; preserve one concept/publication unit per package.",
    },
    {
        "issue": "SCIENTIFIC_SOFTWARE_SOURCE_DISJOINT_REPLICATION_SHORTFALL",
        "cause": "The optimistic Software union is JOSS/GitHub=62 and Figshare=6. JOSS/GitHub is one provider family regardless of its many repositories.",
        "observed": "68 concepts exceed 48, but a JOSS/GitHub primary has only 6/8 disjoint Figshare replication units.",
        "residual": "Total quota cannot substitute for the frozen source-family-disjoint replication gate; exact version and adjudication gates are also unresolved.",
        "next_discriminator": "Bind at least two additional exact publication-linked M6 concepts from a non-GitHub content-provider family, or eight from a fully independent CRAN/Bioconductor/OSF family if that family becomes primary/replication after a separately frozen allocation audit.",
    },
    {
        "issue": "EXACT_RELEASE_RIGHTS",
        "cause": "Missing/NOASSERTION/nonaccepted SPDX identities at the exact release tag are not inferred from repository descriptions or current default branches.",
        "observed": f"{failure_counts['EXACT_RELEASE_LICENSE_GATE_FAIL']} of 200 rows failed or could not bind the exact tag licence gate; 118 passed that stage.",
        "residual": "Failed rights rows contribute zero provider-qualified concepts.",
        "next_discriminator": "Use only source-native package/release metadata with an exact SPDX-compatible licence at the immutable version; do not hand-map generic or missing licences after observing counts.",
    },
    {
        "issue": "RELEASE_AND_RELATION_ABSENCE",
        "cause": "Some frozen JOSS pages exposed no unambiguous GitHub repository relation and some related repositories had no GitHub latest-release object.",
        "observed": f"9 relation shortfalls and {failure_counts['GITHUB_LATEST_RELEASE_CANNOT_CHECK']} release shortfalls.",
        "residual": "Search hits, repository existence, tags and commits are not substituted for a release or counted as units.",
        "next_discriminator": "Resolve only through the prospectively frozen JOSS Software archive bridge or an explicit source-native package release; retain each failed DOI under its original V4 identity.",
    },
    {
        "issue": "DOMAIN_IDENTIFICATION",
        "cause": "The frozen token rule produces ties or no domain token on otherwise related public metadata.",
        "observed": f"27 ambiguous and 33 unclassified rows; 120 uniquely classified.",
        "residual": "Ambiguous/unclassified rows contribute zero provider-qualified domain concepts; labels remain development-only even when unique.",
        "next_discriminator": "Commission outcome-blind domain adjudication under a frozen handbook or predeclare provider-native subject mappings before opening further records; do not tune tokens to recover quota.",
    },
    {
        "issue": "AUTHOR_LINEAGE_AND_NATURAL_PAIR_IDENTITY",
        "cause": "Public author/owner metadata does not establish source-family or author-lineage independence, same-claim preservation, one-coordinate intervention, or material resolvability.",
        "observed": "0 externally adjudicated author-lineage or natural-pair identities.",
        "residual": "No metadata-qualified concept becomes a natural pair or scientific unit.",
        "next_discriminator": "Freeze an outcome-blind external adjudication packet with publication/repository/author identities and blinded domain/mechanism decisions before any case label or system outcome.",
    },
    {
        "issue": "PREDECESSOR_TRANSPORT",
        "cause": "V3 retained 1,804 Figshare and 1,028 Harvard Dataverse full-record identities behind HTTP 403/429 failures.",
        "observed": "The new 200-item JOSS/GitHub frame transported completely, but it does not reopen or replace those frozen predecessor identities.",
        "residual": "The programme terminal remains P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK.",
        "next_discriminator": "Resume only the frozen V3 missing identities when provider access recovers; do not add pages or queries to the V3 identity.",
    },
]
ledger = {
    "schema_version": "orion.p4.m6.source-provider-successor.negative-result-ledger.v4",
    "protocol_id": protocol["protocol_id"],
    "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "entries": ledger_entries,
    "predecessor_terminal_preserved": "P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK",
}
write(ROOT / "NEGATIVE_RESULT_LEDGER_V4.json", ledger)
ledger_md = [
    "# P4 M6 V4 recursive negative-result ledger",
    "",
    "Every entry retains its cause, residual uncertainty and next discriminator. No shortfall is relabelled as a positive result.",
    "",
]
for index, entry in enumerate(ledger_entries, start=1):
    ledger_md += [
        f"## {index}. `{entry['issue']}`",
        "",
        f"**Cause.** {entry['cause']}",
        "",
        f"**Observed.** {entry['observed']}",
        "",
        f"**Residual.** {entry['residual']}",
        "",
        f"**Next discriminator.** {entry['next_discriminator']}",
        "",
    ]
(ROOT / "NEGATIVE_RESULT_LEDGER_V4.md").write_text("\n".join(ledger_md) + "\n")

result = {
    "schema_version": "orion.p4.m6.source-provider-successor.result.v4",
    "protocol_id": protocol["protocol_id"],
    "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "authority": protocol["authority"],
    "execution_status": "BOUNDED_PUBLIC_METADATA_HARVEST_COMPLETE__NO_OUTCOMES",
    "v4_terminal": "P4_M6_JOSS_GITHUB_BOUNDED_TRANSPORT_COMPLETE__EXACT_PUBLICATION_RELEASE_VERSION_RELATION_AND_AUTHOR_LINEAGE_CANNOT_CHECK__M6_CELL_FRAME_NOT_READY",
    "preserved_programme_terminal": "P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK",
    "counts": stage_counts,
    "provider_qualified_by_domain": cell_counts["provider_qualified_by_domain"],
    "cells": cells,
    "claim_boundary": {
        "provider_qualified_concepts_are_natural_pairs": False,
        "quota_pass_claimed": False,
        "source_frame_ready_claimed": False,
        "model_or_system_outcomes_accessed": False,
        "protected_cases_or_labels_accessed": False,
        "performance_or_superiority_claim": False,
    },
    "scientific_conclusion": "JOSS plus GitHub releases is a feasible exact-rights and immutable-identity source-provider route at the repository-concept level: 80 unique DOI/repository concepts passed the frozen relation, public-release, commit, tag-licence and domain gates. It does not close P4 M6. Zero is promoted as an exact paper-to-release or natural-pair unit; V3-to-V4 item overlap cannot be checked from the omitted V3 rows; three optimistic domain cells remain at 7/48, and the optimistic Software cell has only 6/8 disjoint Figshare replication units.",
    "next_discriminator": "First recover or reconstruct the exact V3 M6 concept identities for cross-provider deduplication. Then freeze the same 200 JOSS DOI identities in a no-extension archive-tag bridge that requires the JOSS Software archive DOI to identify the exact GitHub release tag/commit, while separately freezing domain-specific non-GitHub package providers for the three 41-unit optimistic shortfalls and the Software two-unit replication shortfall.",
    "artifact_hashes": {
        "protocol_v4": digest(ROOT / "PROTOCOL_V4.json"),
        "freeze_receipt": digest(ROOT / "PROTOCOL_FREEZE_RECEIPT_V4.json"),
        "crossref_page": digest(ROOT / "CROSSREF_PAGE_V4.json"),
        "candidate_jsonl": digest(ROOT / "CANDIDATES_V4.jsonl"),
        "strict_candidates": digest(ROOT / "STRICT_CANDIDATES_V4.json"),
        "transport_log": digest(ROOT / "TRANSPORT_LOG_V4.json"),
        "cell_counts": digest(ROOT / "CELL_COUNTS_V4.json"),
        "rights_relation_transport_audit": digest(ROOT / "RIGHTS_RELATION_TRANSPORT_AUDIT_V4.json"),
        "negative_result_ledger": digest(ROOT / "NEGATIVE_RESULT_LEDGER_V4.json"),
    },
}
write(ROOT / "RESULT_V4.json", result)

report_lines = [
    "# P4 M6 source-provider successor V4 result",
    "",
    f"**V4 terminal:** `{result['v4_terminal']}`",
    "",
    "**Preserved programme terminal:** `P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK`",
    "",
    "The first frozen Crossref page returned 200 unique JOSS publications. All 200 JOSS pages transported; 191 exposed a labelled GitHub repository relation, 180 repositories had a latest release whose tag resolved to an immutable commit, 118 bound an accepted licence plus blob SHA at that tag, and 120 had one frozen domain assignment. Their intersection contains **80 unique publication-DOI/repository concepts**: Earth 5, Life 7, Scientific Software 62, Physical 6.",
    "",
    "These are provider-qualified concepts for external version-link and natural-pair adjudication, not eligible natural pairs. The JOSS page links the software repository, but the frozen lane did not establish that the current GitHub release tag is the exact version evaluated by the paper. The bounded V3 packet also omits the row identities needed for cross-provider concept/publication deduplication. Consequently **0 V4 units are promoted through the exact paper-to-release, cross-provider-deduplication, author-lineage and natural-pair gates**.",
    "",
    "## Per-cell boundary",
    "",
    "| M6 domain | V3 observed lower bound | V4 provider-qualified concepts | Optimistic union before exact version/adjudication | Gap to 48 | Optimistic disjoint-provider gate |",
    "|---|---:|---:|---:|---:|---|",
]
for domain in domains:
    c = cells[domain]
    disjoint = f"{'PASS' if c['optimistic_disjoint_replication_8_pass'] else 'FAIL'} ({c['optimistic_disjoint_replication_units']}/8)"
    report_lines.append(f"| {domain} | {c['v3_observed_strict_metadata_lower_bound']} | {c['v4_provider_qualified_concept_candidates']} | {c['optimistic_union_before_exact_version_and_external_adjudication']} | {c['optimistic_gap_to_48']} | {disjoint} |")
report_lines += [
    "",
    "Even the optimistic, no-overlap union leaves Earth, Life and Physical at 7/48. Scientific Software reaches 68 concepts, but JOSS/GitHub is one provider family and the disjoint Figshare side has only 6/8 units. These union values are upper diagnostics before exact V3/V4 item deduplication, not countable allocation totals. No surplus, repository, release, tag, asset, file, version, search hit or API response repairs those gates.",
    "",
    "## Rights, relation, identity and transport",
    "",
    "Rights were accepted only from the GitHub licence endpoint at the exact release tag with a licence blob SHA; 62 rows failed or lacked this gate. Every retained release tag resolved to a 40-hex commit SHA. JOSS/GitHub is source-family disjoint from Figshare, but multiple JOSS papers and GitHub organizations remain one provider family. Author-lineage independence remains `CANNOT_CHECK`.",
    "",
    "The V4 bounded transport itself completed, but it does not overwrite V3's 1,804 missing Figshare and 1,028 missing Harvard Dataverse full-record identities. Therefore the programme transport terminal remains unchanged.",
    "",
    "## Next discriminator",
    "",
    result["next_discriminator"],
    "",
    "Public metadata only; no protected case, label, natural-pair decision, system output, performance result or superiority claim was accessed.",
]
(ROOT / "RESULTS_V4.md").write_text("\n".join(report_lines) + "\n")
print(json.dumps({"stage_counts": stage_counts, "provider_qualified_by_domain": dict(v4_counts), "v4_terminal": result["v4_terminal"]}, indent=2))
