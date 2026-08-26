# P2 corrected AutoResearchBench external probe rerun — 2026-08-16

This rerun follows the released-bundle partition correction: the pinned decrypted AutoResearchBench bundle contains an explicit `type` field with 600 `deep` and 400 `wide` records, while both task families use list-valued `arxiv_id` fields. Candidate custody remains gold-blind.

The Wide lane runs the credential-free pinned official set scorer over the 400 released Wide tasks. The Deep lane freezes one 600-task public-arXiv candidate output, evaluates the predeclared 540-scorable exact-ID deviation, then builds the host-owned official title-judge input after candidate freeze. The pinned official Deep title judge runs only if repository-configured OpenAI-compatible judge authority is available; otherwise the workflow emits an explicit `CANNOT_CHECK` blocker artifact.

Neither lane is promoted to full multi-provider ORION superiority. They are bounded external probes used to close evaluator, adapter, and external-evidence gaps without crossing candidate/gold custody boundaries.
