# Paper II falsifier V1

Local deterministic evidence is frozen in `research/paper-programme-v1/FLAGSHIP_FALSIFIER_RESULTS_V1.md`.

**Local status:** PASS at branch commit `8a8a7feed588363f8e2cd820d3399a33b7af3074`, CI run `31933432314`.

The suite uses a complete-gold local retrieval world plus hostile route/coverage cases. It verifies recall-first comparison against the built-in lexical baseline, conservative route-independence, content-level re-encounter deduplication, refusal of zero-overlap population estimates, refusal of single-target pseudo-recall, and the non-authoritative status of coverage diagnostics.

**External status:** `CANNOT_CHECK`. ResearchArena/AutoResearchBench/MetaSyn-style wide/deep evaluations with frozen provider trajectories and matched lexical/one-pass baselines remain required.
