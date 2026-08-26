# ORION-03 figure contract — V3

## Figure 1 — Frontier decision benchmark lifecycle

**Reader question:** What is new about the measurement protocol?

Visual sequence:

`unresolved scientific frontier`
→ `freeze exact evidence + scorer rule`
→ parallel `Instrument A` / `Instrument B`
→ freeze decisions
→ derive `AGREE / PARTIAL / DISAGREE / CANNOT_CHECK`
→ **later scientific work occurs**
→ bind resolving evidence
→ score each frozen decision `ALIGNED / MISALIGNED / UNRESOLVED / INVALIDATED_ITEM`.

The time boundary between decision freeze and resolving evidence must be visually dominant.

**Must not imply:** agreement is an alignment score or that the instruments are statistically independent.

## Figure 2 — Shared versus distinct instrument surfaces

Two-column architecture diagram using the manuscript table:

**Shared:** repository evidence, receipt substrate, project vocabulary, non-authority semantics.

**Distinct:** host/LLM-guided research loop versus typed non-LLM campaign control; implicit versus explicit manifest hypothesis vocabulary; different decision machinery and failure surfaces.

A shared-bias band should span both columns to make the independence limitation visible rather than buried in prose.

## Figure 3 — V0 lifecycle and later resolution

Show only the one-item demonstration:

- freeze: post-R6O unresolved regime-characterization question;
- A decision: regime characterization primary, support-two closure complementary;
- B decision: regime characterization, revision withheld;
- pre-outcome relation: `AGREE` on primary move;
- later evidence: R6P finite support-two closure + R6Q finite regime predicate;
- per-instrument score under the frozen rule: `ALIGNED`.

Caption must state `N=1; demonstration only` prominently.

## Figure 4 / systems panel — Invalid-content recovery

Optional main-text systems panel or Supplementary figure:

`valid outer receipt + invalid task content`
→ strict parser failure
→ `HOST_CAPABILITY_FAILED`
→ reason-bound archive preserves old bytes
→ request identity becomes pending
→ corrected result accepted.

Use this to explain benchmark temporal identity, not to imply sandbox/security guarantees.

## Table 1 — Comparison with existing evaluation patterns

Use `RELATED_WORK_AND_BENCHMARK_MATRIX_V3.md` as the source. Keep the distinguishing columns factual: ground-truth timing, communication, agreement-as-score, deferred scoring, unresolved-state handling.
