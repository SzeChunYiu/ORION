#!/usr/bin/env python3
"""Finite exact regression for ORION17.CROSS_BUCKET_EXPOSURE_IDENTITY.v1."""
from __future__ import annotations

import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "SUCCESSOR_PROTOCOL_V1.json"


def transitive_reads(n, edge_mask):
    reach = [{i} for i in range(n)]
    pairs = [(i, j) for i in range(n) for j in range(n) if i != j]
    for bit, (u, v) in enumerate(pairs):
        if (edge_mask >> bit) & 1:
            reach[u].add(v)
    changed = True
    while changed:
        changed = False
        for u in range(n):
            expanded = set(reach[u])
            for v in tuple(reach[u]):
                expanded |= reach[v]
            if expanded != reach[u]:
                reach[u] = expanded
                changed = True
    return reach


def instrument_false_retention(reads, buckets, changed):
    changed_buckets = {buckets[c] for c in changed}
    false = set()
    preserve = set()
    unnecessary = set()
    for m in range(len(reads)):
        invalid = bool(reads[m] & changed)
        keep = buckets[m] not in changed_buckets
        if keep:
            preserve.add(m)
            if invalid:
                false.add(m)
        elif not invalid:
            unnecessary.add(m)
    return false, preserve, unnecessary


def theorem_sets(reads, buckets, changed):
    changed_buckets = {buckets[c] for c in changed}
    false = {
        m
        for m in range(len(reads))
        if reads[m] & changed and buckets[m] not in changed_buckets
    }
    preserve = {m for m in range(len(reads)) if buckets[m] not in changed_buckets}
    unnecessary = {
        m
        for m in range(len(reads))
        if buckets[m] in changed_buckets and not (reads[m] & changed)
    }
    return false, preserve, unnecessary


def cross_pairs(reads, buckets):
    return {
        (m, c)
        for m in range(len(reads))
        for c in reads[m]
        if buckets[m] != buckets[c]
    }


def validate_protocol():
    p = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert p["schema_version"] == "orion17.cross-bucket-mechanism-successor.v1"
    assert p["identity"] == "ORION17.CROSS_BUCKET_MECHANISM_PROSPECTIVE.v1"
    assert p["status"] == "DESIGN_ONLY__NO_PROTECTED_OUTCOME_AUTHORITY"
    assert p["scientific_authority_delta"] == "NONE"
    assert p["parent_density_identity_terminal"] == "NO_DISCRIMINATION"
    assert p["source_semantics"]["git_blob_sha"] == "4531c2c0230070f8a8aaf49acabee6bce9633929"
    ids = [c["id"] for c in p["candidate_family"]]
    assert ids == ["C0_SAFE", "C1_MAX_EXPOSURE", "C2_TOTAL_EXPOSURE", "C3_EXPECTED_EXPOSURE"]
    assert p["corpus"]["exclude_historical_campaign_8"] is True
    assert p["corpus"]["exclude_rule_disagreement_v1_20"] is True
    assert p["corpus"]["package_root_must_be_normalized_before_protected_measurement"] is True
    assert p["protected_outcome"]["instrument_and_parameters_frozen_before_access"] is True
    assert p["protected_outcome"]["report_preserve"] is True
    assert p["protected_outcome"]["report_unnecessary_reopenings"] is True
    assert "no density threshold refit" in p["anti_leakage"]
    assert "no protected transition frequencies in C3 training weights" in p["anti_leakage"]
    assert "CANNOT_CHECK_MECHANISM__OUTCOME_CONSTANT" in p["terminals"]
    assert len(p["controls"]) >= 6


def main():
    systems = 0
    transitions = 0
    universal_checks = 0

    for n in range(1, 5):
        n_directed = n * (n - 1)
        for edge_mask in range(1 << n_directed):
            reads = transitive_reads(n, edge_mask)
            for buckets in itertools.product((0, 1), repeat=n):
                xpairs = cross_pairs(reads, buckets)
                all_sound = True
                for change_mask in range(1, 1 << n):
                    changed = {i for i in range(n) if (change_mask >> i) & 1}
                    observed = instrument_false_retention(reads, buckets, changed)
                    derived = theorem_sets(reads, buckets, changed)
                    assert observed == derived
                    false, preserve, _ = observed
                    if false:
                        all_sound = False

                    # One-bucket / all-buckets-changed degeneracy.
                    if {buckets[c] for c in changed} == set(buckets):
                        assert not preserve
                        assert not false
                    transitions += 1

                assert all_sound == (len(xpairs) == 0)
                universal_checks += 1

                # rho_max=0 iff X is empty; when positive a maximizing singleton
                # change must realize exactly that many false retentions.
                readers = []
                for c in range(n):
                    count = sum(1 for m in range(n) if c in reads[m] and buckets[m] != buckets[c])
                    readers.append(count)
                    false, _, _ = instrument_false_retention(reads, buckets, {c})
                    assert len(false) == count
                rho = max(readers)
                assert (rho == 0) == (len(xpairs) == 0)
                systems += 1

    validate_protocol()
    print(
        "ORION17_CROSS_BUCKET_EXPOSURE_IDENTITY_V1_PASS "
        f"graph_bucket_systems={systems} transitions={transitions} "
        f"universal_soundness_checks={universal_checks} protocol=PASS"
    )


if __name__ == "__main__":
    main()
