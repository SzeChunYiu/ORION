# Zenodo 10423427 schema-preflight incident

The source identity was frozen and the 53,881,052-byte body passed its exact MD5.
The intended next operation was to print a CSV header without parsing a data
row.  The file is actually tab-delimited and has no header.  Consequently the
first line printed by the preflight was a labeled record and exposed the literal
label `exclude` before the scientific protocol was frozen.

This cannot be undone or described as outcome-blind access.  The source is
already a public-label development corpus, but even that weaker authority must
preserve the access incident.  Any successor execution must:

1. record `outcome_blind_before_protocol=false`;
2. exclude the exact first raw line from every model, comparator and endpoint;
3. bind that exclusion by raw-line SHA-256 without printing the row again;
4. describe the result as public-label transport development, not confirmation,
   protected evidence, independent custody or multi-arena replication; and
5. freeze columns, arms, seeds, metrics and gates before parsing any remaining
   row.

No aggregate, model score or dataset-wide label count was observed in the
preflight.
