# P13 top-tier manuscript integration — 2026-08-23

This note is the manuscript-facing bridge from the historical P13A/P13B paper to the current responsibility-carrying-state evidence chain. It does not rewrite frozen outcomes and does not grant external deployment authority.

## One-sentence paper identity

**P13 studies when scientific state may be reused after the downstream responsibility or evidence regime changes.** Provenance tells where state came from; responsibility support tells what that state is still allowed to answer.

## Scientific arc the final paper should tell

### A. Keep the historical failure because it motivates the correct endpoint

P13A's original zero-unsafe-reuse endpoint is self-entailed: the reuse decision and harm label consume the same certificate support bit. Keep this as a first-class correction, not as an embarrassing appendix. It establishes why safe reuse must be graded against certificate-independent support.

P13B is the immediate controlled repair: independent gold plus live certificate-corruption opportunities. Summarize it briefly and then move to the stronger later evidence.

### B. Real-data responsibility shift

Use the digits study as the real-data anchor:

- 17,970 episodes;
- same predictive correctness as always-raw;
- 48.4375% fewer raw reads.

The point is not compression alone. The same stored state can be adequate for one responsibility and inadequate for another, and RCS uses the named responsibility to decide whether reuse remains authorized.

### C. Verifier-backed responsibility shift

Use the CNF semantic/epoch study as the exact second domain:

- RCS 24/24 verifier-correct;
- always-raw 24/24;
- confidence/provenance-only 12/24;
- RCS 44.44% fewer raw literal reads than always raw;
- two implementations agree.

This turns the paper from a learned-data result into a cross-domain mechanism with exact certificate semantics.

### D. Main donor discriminator — provenance is not responsibility

`P13_D2_DONOR_BASELINE_RESULT_RECEIPT_V1.md` should be the principal donor-comparison section.

Across 48 frozen CNF episodes:

| arm | verifier-correct | unsupported reuse | mean literal reads |
|---|---:|---:|---:|
| D2_CORE | 36/48 | 12 | 6.25 |
| D2_PLUS | 36/48 | 12 | 6.25 |
| RCS | 48/48 | 0 | 5.0 |
| COMPOSED | 48/48 | 0 | 5.0 |
| ALWAYS_RAW | 48/48 | 0 | 5.5 |

The strongest provenance-tiered donor remains current and demand-graded yet reuses unsupported state when the responsibility changes between checkpoints. RCS and COMPOSED are exact on this grid. This is the key conceptual separation:

> **provenance currency x responsibility support are two dimensions, not one.**

Do not describe the donor as generally unsafe. The result is bounded to the frozen between-checkpoint model and responsibility-change cells.

### E. Dynamic reuse — certificate transport across drift

`P13_CERT_TRANSPORT_RESULT_RECEIPT_V1.md` should follow the donor comparison.

Across 60 frozen cases:

| policy | verifier-correct | unsound transport | needless re-issue | mean reads |
|---|---:|---:|---:|---:|
| UNCONDITIONAL | 40/60 | 40 | 0 | 6.0 |
| SIGNATURE_ONLY | 60/60 | 0 | 20 | 11.333 |
| CONDITIONAL_DRIFT_BOUNDED | 60/60 | 0 | 0 | 10.0 |
| ALWAYS_RE_ISSUE | 60/60 | 0 | 20 | 11.333 |

On redundant drift, conditional transport costs 8.0 reads versus 12.0 for re-issue. The result shows why two naive policies fail in opposite directions: unconditional transport is unsound; signature/epoch equality is over-conservative. Responsibility-aware local verification gives a middle policy that is exact on the registered drift grid.

## Abstract replacement target

The final abstract should say, approximately:

> Reusing compact scientific state is usually governed by confidence, freshness or provenance. We argue that reuse is instead relative to the downstream responsibility. After retaining an earlier self-scored safety result as a methodological negative, we evaluate responsibility-carrying state on a real-data responsibility shift and a verifier-backed certificate domain. On digits, responsibility-aware reuse preserves always-raw correctness while reducing raw reads by 48.4%; on CNF shifts it is verifier-correct on 24/24 cases while confidence/provenance-only state is correct on 12/24. A donor-complete provenance-tiered memory comparison shows that current provenance does not prevent unsupported reuse after responsibility change (12/48 failures per donor arm), whereas responsibility-carrying state is 48/48. In a separate 60-case drift study, unconditional certificate transport is unsound in 40 cases and signature-only transport needlessly reissues 20 sound certificates, while a frozen local drift-bound rule is exact and cheaper than reissue on redundant drift. We claim bounded responsibility-relative certified reuse, not universal workflow safety.

## Introduction edits

1. Lead with the distinction between **where state came from** and **what responsibility it supports now**.
2. Use confidence/provenance/freshness as absorbed donor coordinates, not strawmen.
3. State the paper's higher-level question: when may a scientific certificate survive a responsibility or semantic transition without rereading raw evidence?
4. Move the old P14A/P13A history out of the opening contribution list and into a short "measurement correction" contribution.
5. Make the two current discriminators explicit: donor-complete responsibility change and drift-bounded certificate transport.

## Results section order

1. Formal responsibility-relative sufficiency.
2. Measurement correction: why P13A's zero-harm endpoint was self-entailed.
3. Brief P13B independent-gold repair.
4. Real digits responsibility shift.
5. Verifier-backed CNF responsibility/epoch shift.
6. **Donor-complete D2 comparison**.
7. **Drift-bounded certificate transport**.
8. Cost / reopen tradeoff and limitations.

## Sentences that must be removed or rewritten

Remove any sentence implying:

- P13A established empirical safety superiority;
- a valid signature or current provenance establishes responsibility support;
- zero unsafe reuse in the original self-scored benchmark is independent evidence;
- RCS dominates COMPOSED on the D2 grid (they are decision-equivalent there by construction);
- the clause-diff transport rule is uniquely correct or applies to arbitrary semantic change;
- real-agent or safety-critical deployment authority has been earned.

Retain all historical negative/adjudication records.

## Strongest authorized headline now

> Responsibility-relative support is not reducible to provenance currency: across real-data and verifier-backed shifts, RCS preserves correctness while avoiding unnecessary raw recovery; on a frozen donor-complete provenance-tiered comparison, donor arms make unsupported reuses after responsibility change while RCS is exact, and a separate drift-bounded transport rule is exact where unconditional and signature-only certificate policies fail in opposite directions.

## Optional strengthening — only if the headline needs it

Do not add more experiments merely to increase domain count. Add a new study only if the final claim explicitly requires one of these scopes:

- real research-agent/workflow responsibility labels;
- non-CNF formula classes;
- adversarial semantic drift;
- evaluator or evidence-source changes;
- real-data replication of the donor-complete D2 arm.

Otherwise these are follow-ups, not blockers.

## Submission-day checklist

- refresh nearest provenance-aware memory, signed-intent, certificate transport and agent-memory donors;
- integrate the D2 and transport receipts into `CLAIM_EVIDENCE_LEDGER.md` and the manuscript;
- reconcile P13/P15: P13 owns scientific responsibility support/reuse; P15 owns execution-integrity admission and attestation composition;
- reconcile P7/P13: P7 owns transport of closure across regimes; P13 owns reuse authority of state/certificates relative to responsibility;
- clean-environment replay of digits/CNF/D2/transport studies;
- regenerate all result tables directly from bound receipts;
- remove duplicated historical status/strongest-claim blocks in `MANUSCRIPT.md`;
- run clipping/content-binding audits;
- bind exact final manuscript, evidence, environment and PDF bytes.
