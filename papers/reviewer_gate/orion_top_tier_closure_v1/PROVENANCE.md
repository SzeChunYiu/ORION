# Provenance — ORION top-tier reviewer-gate closure contracts

## Why this was missing

Delivered as `~/Downloads/orion_01_25_top_tier_science_closure_gate_703b87d.zip`
and never committed. `papers/reviewer_gate/orion_top_tier_closure_v1` does not
exist on any ref of this repository.

Third instance of the same failure mode in one session, after ORION-04's
`orion_top_tier_promotion_bundle.zip` and the issue-#1701 gap-closure packet:
a delivered artifact sitting in a download directory, invisible to every
repository-scoped search.

## What it provides

Per-paper top-tier closure contracts across ORION 01–25, paired by file
(`ORION_01_03.md` … `ORION_24_25.md`). Each paper carries `BAND`,
`CURRENT_TOP_TIER_READY`, `BASELINE_PROMOTION_ALLOWED`, `IDENTITY`,
`HARD_RETRACTION`, `GAPS`, `NEXT_EVIDENCE`, `PRIMARY_ENDPOINTS`,
`EXTERNAL_STATUS` and `EXTERNAL_REPLICATION`.

`NEXT_EVIDENCE` is the operative field: it names concrete lettered moves per paper
rather than a generic "needs more work".

## Read this against the current namespace, not the old one

**These entries use pre-R0 paper identities.** Its `ORION-04` is titled
*"Meta-learning latent task structure"*, whereas current `papers/orion-04-*` is
*rooted completion certificates*. The R0 namespace unification (commit
`3a1a83178`, 2,734 renames) sits between this packet and current main.

So the numbering here **must not** be mapped one-to-one onto today's
`papers/orion-NN-*` directories without checking the alias registry. Any use of
this packet that assumes today's numbering will attribute gaps to the wrong paper.
Landing it makes the contracts auditable; it does not license that mapping.

## Authority

No ledger, terminal, manifest or `journal_package/` byte is changed. This commit
adds a previously uncommitted planning artifact and its provenance, nothing more.
