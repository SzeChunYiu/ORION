"""Outcome-blind structural validator for an R7 acquired source frame."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable, Mapping

FAMILIES = {
    "LATENT_OBJECTIVE",
    "CONTRADICTORY_OBJECTIVES",
    "WRONG_MEASUREMENT",
    "WRONG_REPRESENTATION",
    "WRONG_PROBLEM_BOUNDARY",
    "IMPLEMENTATION_OR_HARNESS_FAILURE",
    "EVIDENCE_SCARCITY",
    "NO_REFORMULATION_CONTROL",
}
DOMAINS = {
    "BIOMEDICAL_CLINICAL",
    "EARTH_ENVIRONMENTAL",
    "COMPUTATIONAL_SCIENTIFIC_SOFTWARE",
    "PHYSICAL_ENGINEERING",
}
PAIR_QUOTA = 6
UNRESOLVED_QUOTA = 16


def _identity_tokens(row: Mapping[str, Any]) -> set[str]:
    identity = row.get("source_identity")
    if not isinstance(identity, Mapping):
        return set()
    values: set[str] = set()
    for key in (
        "normalized_url",
        "doi",
        "stable_artifact_id",
        "title_first_author_year",
        "official_repository_identity",
        "shared_dataset_or_project_family",
    ):
        value = identity.get(key)
        if isinstance(value, str) and value.strip():
            values.add(f"{key}:{value.strip().casefold()}")
    return values


def _duplicates(rows: Iterable[Mapping[str, Any]]) -> list[str]:
    owners: dict[str, str] = {}
    errors: list[str] = []
    for row in rows:
        cluster = str(row.get("cluster_id", ""))
        for token in sorted(_identity_tokens(row)):
            prior = owners.get(token)
            if prior is not None and prior != cluster:
                errors.append(f"source identity {token} shared by {prior} and {cluster}")
            owners[token] = cluster
    return errors


def validate_source_frame(
    frame: Mapping[str, Any], *, excluded_identity_tokens: Iterable[str] = ()
) -> dict[str, Any]:
    errors: list[str] = []
    pairs = frame.get("pairs")
    unresolved = frame.get("unresolved")
    if not isinstance(pairs, list):
        pairs = []
        errors.append("pairs must be a list")
    if not isinstance(unresolved, list):
        unresolved = []
        errors.append("unresolved must be a list")

    all_rows = [row for row in [*pairs, *unresolved] if isinstance(row, Mapping)]
    if len(all_rows) != len(pairs) + len(unresolved):
        errors.append("every source row must be an object")

    clusters = [str(row.get("cluster_id", "")) for row in all_rows]
    if any(not cluster for cluster in clusters):
        errors.append("every source row requires cluster_id")
    duplicate_clusters = sorted(
        cluster for cluster, count in Counter(clusters).items() if cluster and count > 1
    )
    if duplicate_clusters:
        errors.append(f"duplicate source clusters: {duplicate_clusters}")
    errors.extend(_duplicates(all_rows))

    exclusions = {str(token).casefold() for token in excluded_identity_tokens}
    for row in all_rows:
        overlap = {token.casefold() for token in _identity_tokens(row)} & exclusions
        if overlap:
            errors.append(
                f"cluster {row.get('cluster_id')} overlaps excluded source identity: {sorted(overlap)}"
            )

    pair_cells: Counter[tuple[str, str]] = Counter()
    for row in pairs:
        if not isinstance(row, Mapping):
            continue
        family = str(row.get("family", ""))
        domain = str(row.get("domain", ""))
        if family not in FAMILIES:
            errors.append(f"cluster {row.get('cluster_id')} has invalid family {family}")
        if domain not in DOMAINS:
            errors.append(f"cluster {row.get('cluster_id')} has invalid domain {domain}")
        if family in FAMILIES and domain in DOMAINS:
            pair_cells[(family, domain)] += 1
        members = row.get("members")
        if not isinstance(members, Mapping) or set(members) != {"adverse", "control"}:
            errors.append(f"cluster {row.get('cluster_id')} lacks exact adverse/control members")
        query_ids = row.get("query_ids")
        if not isinstance(query_ids, list) or not query_ids:
            errors.append(f"cluster {row.get('cluster_id')} lacks acquisition query lineage")

    for cell in sorted((family, domain) for family in FAMILIES for domain in DOMAINS):
        if pair_cells[cell] != PAIR_QUOTA:
            errors.append(f"pair cell {cell} has {pair_cells[cell]} sources; expected {PAIR_QUOTA}")

    unresolved_domains: Counter[str] = Counter()
    for row in unresolved:
        if not isinstance(row, Mapping):
            continue
        domain = str(row.get("domain", ""))
        if domain not in DOMAINS:
            errors.append(f"cluster {row.get('cluster_id')} has invalid unresolved domain {domain}")
        else:
            unresolved_domains[domain] += 1
        query_ids = row.get("query_ids")
        if not isinstance(query_ids, list) or not query_ids:
            errors.append(f"cluster {row.get('cluster_id')} lacks acquisition query lineage")

    for domain in sorted(DOMAINS):
        if unresolved_domains[domain] != UNRESOLVED_QUOTA:
            errors.append(
                f"unresolved domain {domain} has {unresolved_domains[domain]} sources; "
                f"expected {UNRESOLVED_QUOTA}"
            )

    checks = {
        "exact_pair_count": len(pairs) == len(FAMILIES) * len(DOMAINS) * PAIR_QUOTA,
        "exact_unresolved_count": len(unresolved) == len(DOMAINS) * UNRESOLVED_QUOTA,
        "exact_pair_cell_quotas": all(
            pair_cells[(family, domain)] == PAIR_QUOTA
            for family in FAMILIES
            for domain in DOMAINS
        ),
        "exact_unresolved_domain_quotas": all(
            unresolved_domains[domain] == UNRESOLVED_QUOTA for domain in DOMAINS
        ),
        "unique_source_clusters": len(set(clusters)) == len(clusters),
        "source_family_disjointness": not _duplicates(all_rows),
        "no_errors": not errors,
    }
    return {
        "complete": all(checks.values()),
        "terminal": (
            "P1_R7_SOURCE_FRAME_COMPLETE"
            if all(checks.values())
            else "P1_R7_CANNOT_CHECK_SOURCE_UNIVERSE"
        ),
        "checks": checks,
        "errors": errors,
        "pair_cell_counts": {
            f"{family}::{domain}": pair_cells[(family, domain)]
            for family in sorted(FAMILIES)
            for domain in sorted(DOMAINS)
        },
        "unresolved_domain_counts": dict(sorted(unresolved_domains.items())),
    }

