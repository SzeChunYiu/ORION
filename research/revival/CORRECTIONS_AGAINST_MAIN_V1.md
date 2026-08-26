# Corrections against current main — revival programme V1

These facts override stale issue comments and the duplicate `REVIVAL_BACKLOG_V1.md` drafts on PRs #272 and #273. Authority is current `main`, not conversational memory.

Machine twin: `CORRECTIONS_V1.json`.

## P4 protected V2 is already PEER_REVIEW_READY

Evidence: `papers/orion-14-verified-scientific-discovery/evidence/protected_v2/PEER_REVIEW_READY_V2.md`.

The executed protected V2 campaign, typed panel, H1/H2 positives, H3 null, and independent headline reproduction are paper-local history. Issue #281 is a **new** follow-up on which protected evidence to acquire next. It must not rewrite frozen P4 V2, and it must not catalogue the executed battery as unrun.

## P1 H1 and H2 power requirements are distinct

Evidence: `papers/orion-11-recursive-epistemic-reconstruction/evidence/CLAIM_LEDGER_V1.md` and `src/orion/study/p1/precision_tier.py`.

| Hypothesis | Frozen margin | Required n (p=0.5 half-width) |
|---|---|---|
| H1 superiority | +0.05 | 385 |
| H2 non-inferiority | +0.02 | 2401 |

The H1 precision tier is TIER_B (required n of 385). That tier does **not** license the +0.02 non-inferiority hypothesis. Conflating those two n targets is a process error.

## Post-outcome margin relaxation is forbidden

A confirmatory revival may expand a predeclared sample or create a new immutable protocol. It may not widen a frozen margin after outcome access. Unreachable-at-planned-n is reported honestly (`UNDERPOWERED_AT_MAX_PLANNED_N` or equivalent), never margin-widened.

## P5 attribution is 21/24

Evidence: `papers/orion-15-self-orion/evidence/glm-5.2-attribution/report.json` (`correct_attributions`: 21, `incorrect_attributions`: 3, `total_cases`: 24).

Issue comments that treat the local attribution campaign as a perfect score are stale. The three errors are discriminator seeds for #282, not a completed transfer terminal.
