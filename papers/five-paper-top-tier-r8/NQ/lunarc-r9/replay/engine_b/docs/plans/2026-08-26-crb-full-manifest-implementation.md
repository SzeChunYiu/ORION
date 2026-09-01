# CR-B full census manifest implementation plan

1. Add failing tests for the exact 98,622/230,983 denominators, contiguous
   partitions, deterministic matrix digest, hostile plan mutations, strict
   canonical candidate records, fail-closed materialization, and authority
   labels.
2. Implement the smallest standalone manifest/partition module needed by those
   tests without importing Engine-A generators or result files.
3. Generate the committed declaration, schema, and non-outcome receipt from the
   module; bind the new files in the Engine-B source manifest.
4. Run focused tests, all Engine-B tests, Ruff, compilation, source-manifest
   verification, and an independent partition arithmetic/hash audit.

