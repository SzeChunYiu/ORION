# P13 — Responsibility-Carrying State

**Stable ID:** ORION-P13  
**Paper issue:** #666  
**RCS interface track:** #668  
**Programme:** #670

## Canonical manuscript

`MANUSCRIPT.md` is the current peer-review manuscript. Its historical P13A/P13B sections remain part of the audit trail, but the current top-tier scientific object is supported by later real-data, verifier-backed, donor-complete and certificate-transport studies.

## Active claim authority

The machine-rebuilt authority chain, in force order:

- `P13A_OUTCOME_ENTAILMENT_ADJUDICATION_V1.json` — historical adjudication; terminal `P13A_EMPIRICAL_SAFETY_COST_AUTHORITY_WITHHELD` (the self-scored zero-harm endpoint can never authorize empirical superiority).
- `P13_ACTIVE_CLAIM_AUTHORITY_V2.json` — active authority for the P13B leaf; active terminal `P13_CONTROLLED_AUTHENTICATED_CERTIFICATE_AUTHORITY_SUPPORTED`, retained unchanged.
- `P13_ACTIVE_CLAIM_AUTHORITY_V3.json` — extends V2 with the composed P13C leaf, terminal `P13C_COMPOSED_SAFETY_EFFICACY_SUPPORTED` (registered composed finite world; zero authenticated unsafe reuses; every scheduled corruption rejected; external validation forbidden). V2 remains the active authority for its own leaf.

## Current scientific state

### 1. Historical outcome-entailment correction

P13A remains a valid execution record, but its original zero-harm safety endpoint is not independent evidence: the RCS action and the primary harm label were both derived from the same certificate support bit. `P13A_OUTCOME_ENTAILMENT_ADJUDICATION_V1.json` permanently withholds that empirical safety-superiority interpretation.

P13B repairs that immediate defect with certificate-independent gold and live corruption opportunities. It establishes controlled authenticated-certificate behavior but remains a locally authored finite-world result.

### 2. Real responsibility-shift evidence

The top-tier programme moves beyond the original finite world. On the real digits responsibility-shift study, RCS preserves the always-raw accuracy while reducing raw reads by **48.4375%** over **17,970** episodes. This is the real-data anchor that the historical P13A/P13B story lacked.

### 3. Verifier-backed semantic/epoch shift

On the frozen CNF certificate study:

- RCS: **24/24** verifier-correct;
- always raw: **24/24**;
- confidence/provenance-only: **12/24**;
- RCS reduces raw literal reads by **44.44%** relative to always raw;
- a structurally independent implementation agrees.

This provides a qualitatively distinct verifier-backed domain and explicit certificate revocation/reopen behavior.

### 4. Donor-complete provenance-tiered baseline — authoritative

`top_tier/P13_D2_DONOR_BASELINE_RESULT_RECEIPT_V1.md` binds the strongest demand-graded provenance-tiered donor family on 48 frozen CNF episodes.

- `D2_CORE` and `D2_PLUS`: **36/48** verifier-correct, each committing **12 unsupported reuses** under responsibility change with current provenance;
- `RCS` and `COMPOSED`: **48/48**, zero unsupported reuse;
- `COMPOSED` mean literal reads: **5.0** versus donor **6.25**;
- `ALWAYS_RAW`: 48/48 ceiling;
- two implementations agree and byte replay is stable.

The earned statement is not "provenance is bad". It is that provenance currency and responsibility support are distinct coordinates: a record can be current/provenanced yet no longer support the responsibility being asked of it.

### 5. Drift-bounded certificate transport — authoritative

`top_tier/P13_CERT_TRANSPORT_RESULT_RECEIPT_V1.md` binds 60 frozen certificate-transport cases: 20 REDUNDANT, 20 CONFLICTING and 20 MIXED.

- `CONDITIONAL_DRIFT_BOUNDED`: **60/60** verifier-correct, **0 unsound transports**, **0 needless re-issues**;
- `UNCONDITIONAL`: **40 unsound transports**;
- `SIGNATURE_ONLY`: **20 needless re-issues** on redundant drift;
- `ALWAYS_RE_ISSUE`: exact but more expensive on the redundant stratum (12.0 versus 8.0 for the conditional rule);
- an independent implementation agrees.

This turns reopen semantics from a static contract into a tested transport rule: certificates may survive bounded redundant drift, must be revoked/rechecked under conflicting drift, and should not be reissued merely because a signature or epoch changed when the justification remains valid.

## Strongest paper-level claim

> **Scientific state reuse is responsibility-relative, not provenance-relative.** Across a real-data responsibility shift and a verifier-backed certificate domain, responsibility-carrying state preserves correctness while avoiding unnecessary raw recovery. On the frozen donor-complete CNF comparison, provenance-tiered memory remains vulnerable to unsupported reuse when the responsibility changes despite current provenance, whereas RCS is exact; and on a separate drift grid, a responsibility-aware conditional certificate-transport rule is exact while unconditional transport is unsound and signature-only transport is unnecessarily conservative.

This is a bounded cross-domain claim. It is not universal authority over arbitrary semantic drift or all research-agent workflows.

## Current top-tier blocker

For the demonstrated real-data + verifier-backed responsibility-relative reuse headline, the remaining work is mostly publication/external-breadth closure rather than another basic mechanism experiment.

Additional science is required only if the final headline claims broader scope:

- real research/workflow deployment with externally determined responsibilities;
- non-CNF formula classes;
- adversarially chosen semantic drift;
- evaluator/evidence-source changes not represented by the current clause-diff transport model;
- real-data replication of the donor-complete D2 arm.

Do **not** add those experiments merely to increase benchmark count if the manuscript stays within the earned cross-domain scope.

## Manuscript integration rule

The final manuscript should retain P13A's outcome-entailment failure as a methodological correction, summarize P13B briefly, and make the real digits result, verifier-backed responsibility shift, donor-complete D2 comparison and drift-bounded certificate transport the main empirical arc.

Manuscript-facing integration notes are in `top_tier/P13_TOP_TIER_MANUSCRIPT_INTEGRATION_2026-08-23.md`.

## Core artifacts

- `MANUSCRIPT.md`
- `CLAIM_EVIDENCE_LEDGER.md`
- `PEER_REVIEW_READINESS.md`
- `P13A_OUTCOME_ENTAILMENT_ADJUDICATION_V1.json`
- `P13B_AUTHENTICATED_CERTIFICATE_CORRUPTION_RESULT_V1.json`
- `top_tier/P13_D2_DONOR_BASELINE_RESULT_RECEIPT_V1.md`
- `top_tier/P13_CERT_TRANSPORT_RESULT_RECEIPT_V1.md`
- real responsibility-shift and verifier-backed responsibility receipts under `top_tier/`

## Explicit nonclaims

No universal safety guarantee, no safety-critical deployment authority, no claim that provenance alone is useless, no arbitrary-semantic-drift transport theorem, and no real-agent superiority without a separately governed real-workflow study. `COMPOSED` is decision-equivalent to `RCS` on the frozen D2 grid by construction; the composition claim is cost-dominance over donor arms, not superiority over RCS itself.
