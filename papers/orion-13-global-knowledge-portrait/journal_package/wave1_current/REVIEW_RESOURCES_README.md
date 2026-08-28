# ORION-13 SWJ review resources

This archive supports the bounded structured-mapping claim in *Coordinate-Governed Mapping of Source-Local Scientific Projections*.

## Reproduce the headline

From the root of this extracted archive with Python 3.11 or later:

```text
python scripts/verify_confirmatory_independent.py --check
python manuscript/generate_tables.py
```

The verifier uses only Python's standard library and imports no ORION package code. It checks both frozen case-archive hashes, independently computes the candidate and two comparator decisions, recomputes the paired 10,000-resample bootstrap intervals with the registered seed, and compares them with the frozen analysis.

## Scope

The archive establishes only the 32-case confirmatory mapping result. It does not establish raw-text extraction, an expert atlas, downstream scientific utility, superiority over current integration systems, universal coordinate necessity, or external/cross-host replication.

## Contents

The archive includes the two frozen case sets and their manifests, confirmatory protocol and analysis, source registry, structurally separate verifier and receipt, table generator, and the R0 receipt-identity correction. Paths inside the ZIP reproduce repository-relative identities.
