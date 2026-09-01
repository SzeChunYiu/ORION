# Paper 02 — Open-World Scientific Knowledge Discovery

**Stable ID:** ORION-12  
**Status:** `PEER_REVIEW_READY` on the bounded methods / critical system-design claim. Matched external discovery superiority remains `CANNOT_CHECK` and is not claimed.

## Scoped claim

ORION studies scientific-literature discovery as a separate capability from synthesis. The candidate contribution is the combination of earned route independence, question-framed read memory, route-vs-task stopping, fail-closed coverage diagnostics and recall-first promotion against strong simple baselines.

## Claim, evidence, authority

One table, so a reader can see what is claimed, what backs it and what governs
it without reconstructing that from chronology. Packet and version history lives
in `JOURNAL_READINESS.md` and `JOURNAL_READINESS_V2.md`; it is not needed to
read the claims.

| Claim | Evidence | Authority |
| --- | --- | --- |
| Discovery is a separable capability from synthesis, and earned route independence with question-framed retrieval is the candidate contribution | scoped methods/system-design argument in this README and `JOURNAL_READINESS.md` | `PEER_REVIEW_READY` on the bounded methods/critical-system-design claim |
| ORION's routing and stopping beat a matched external comparator on discovery | four-arm TREC-COVID study, `external/P2_TREC_COVID_ARMS_V1.json`, 50 official topics under one matched budget | **Not established** — treated as post-hoc/descriptive because no separate pre-outcome record binds the exact rule; recall@100 is −0.0177 with bootstrap CI [−0.0273, −0.0091] and reads increase +175.7% |
| Multi-route exploration improves top-10 quality | same study: nDCG@10 +0.1488, bootstrap CI [+0.1010, +0.1995], ahead on 42/50 topics | nDCG@10 was not a gate criterion and cannot rescue the row above; it remains a favorable descriptive result, not evidence of overall superiority |
| ORION's own routing terminal on that corpus | two of five routes unavailable: CITATION has no earned seed, RESTRICTED no provider | `CANNOT_CHECK`, and the arm declines completeness on 50/50 topics where both baselines declare it |
| Scientific RAG, agentic literature search, systematic-review automation, capture-recapture | donor-owned; see the nearest-work boundary below | not claimed as novel |

The second and third rows are deliberately adjacent. A reader who takes the
nDCG gain as the headline would hide the adverse recall and cost results and
overstate a post-hoc comparison.

## Nearest-work boundary

Scientific RAG, agentic literature search, systematic-review automation and capture-recapture are not claimed as novel. The comparison now explicitly includes ResearchArena, AutoResearchBench, SAGE, MetaSyn, AgentSLR, OpenScholar and systematic-review/capture-recapture research.

See `research/paper-programme-v1/PAPER_02_OPEN_WORLD_DISCOVERY.md`, `NEAREST_WORK_ATLAS.md`, `JOURNAL_READINESS_AUDIT_2026-08-16.md`, and this directory's `JOURNAL_READINESS.md`.

## Falsifier V1

A complete-gold local retrieval world plus hostile route/coverage cases exercise the promotion contract. The suite requires a same-call lexical baseline, refuses independence for shared backends, refuses bounded unseen-population claims under zero overlap, deduplicates route re-encounters by content, rejects single-target pseudo-recall and keeps coverage diagnostics non-authoritative.

Evidence: `evidence/FALSIFIER_V1.md` and `research/paper-programme-v1/FLAGSHIP_FALSIFIER_RESULTS_V1.md`.

## External evidence boundary

- The 390-task complete-gold controlled mechanism campaign, MetaSyn probe, and bounded AutoResearchBench probes are archived with their exact authority limits.
- The V2 acquisition programme ended at `P2_V2_ACQUISITION_NOT_PROMOTED`; its valid final development candidate did not earn fresh confirmation.
- A structured OpenAIRE identity discriminator passed, but the subsequent matched Wide campaign failed its frozen transport gate and remains `P2_WIDE_EXTERNAL_CANNOT_CHECK`; all three Actions artifacts are mirrored before expiry.
- Official SAGE and matched multi-provider Deep superiority remain future-work reopen triggers.
- Unavailable routes, invalid transport, and resource censoring remain `OPEN/CANNOT_CHECK`, never evidence of absence or scientific zeros.

The ready paper claims governance semantics and bounded controlled mechanism evidence. It does not claim that ORION discovers more literature than simpler systems on the open web.

## Manuscript

`manuscript/ipm_submission.tex` is the current filing-science source. The
attributed arXiv adapter is generated from it, while the IP&M reviewer route
keeps the canonical anonymous CAS wrapper. `manuscript/main.tex` is a non-filing
long-form research record. The current upload objects and their checksums are in
`submission/publication-final-20260901/`; older packages are historical audit
evidence.
