# AutoResearchBench Wide external probe — execution record

**Execution trigger:** 2026-08-16  
**Upstream benchmark commit:** `a46c9bfb8968786f73f0a6a5b365b5384cd0f96d`  
**Candidate:** ORION keyless public-arXiv probe  
**Scorer:** pinned `evaluate/evaluate_wide_search.py` with `--no-jina`

This commit intentionally triggers the one-shot `p2-autoresearchbench-wide-keyless` workflow. The workflow performs the benchmark decryption and gold split in the host lane, passes only `{task_id, question}` records into the candidate process, queries the public arXiv export API under the canonical three-second request gate, and evaluates the resulting candidate file with the pinned official Wide scorer.

This probe is not pre-labelled as a successful external result. The run outcome, including a poor or null score, must be archived unchanged before any interpretation is added here. It is also not promoted as the final full multi-provider ORION comparison: its declared scope is a credential-free external probe that tests the Wide contract without candidate access to gold.
