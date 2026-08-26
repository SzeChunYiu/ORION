# ORION-12 credential-free external probe trigger — 2026-08-16

This commit intentionally starts two result-bearing external campaigns from the same tested branch head:

1. **AutoResearchBench Wide** — 400 released Wide tasks, host-only benchmark decryption/gold split, candidate access restricted to `{task_id, question}`, public arXiv retrieval, pinned official Wide set scorer.
2. **MetaSyn ID-only** — 86 released test reviews, host-only label stripping, candidate access restricted to public protocol fields, pinned MetaSyn BM25 retrieval plus predeclared deterministic protocol screening, pinned official ID-only evaluator.

Neither campaign is pre-labelled successful. Results, including null or poor performance and transport failures, must be archived unchanged before manuscript interpretation. Both are declared credential-free external probes rather than substitutes for the final full multi-provider ORION superiority comparison.
