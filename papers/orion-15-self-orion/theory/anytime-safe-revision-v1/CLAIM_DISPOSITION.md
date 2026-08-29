# Claim disposition — SELF_ORION.ANYTIME_SAFE_REVISION.v1

**Terminal:** `ANYTIME_BAD_PROMOTION_CONTROL_PROVED__LONGITUDINAL_BENEFIT_UNTESTED`  
**Scientific authority delta:** `NONE`

## Closed by this packet

- Adaptive revision proposals and stopping remain familywise safe when protected gate tests
  are conditionally valid and their **predictable** per-gate/round alpha spend sums to at
  most the global alpha.
- No independence assumption across rounds or gates is required.
- Random/adaptive future spending is permitted when selected from legitimate prior
  information and fixed before the current protected outcome.
- A protected look spends its error budget even if the candidate is rejected; relabeling
  the same look cannot refund alpha.
- Reusing the full one-round alpha at every round is formally unsafe: under independent
  false passes, global error is `1-(1-alpha)^T > alpha` for every `T>1`.
- Hard retention/harm/authority gates remain non-compensatory; the theorem supplies no
  justification for collapsing them into a weighted benefit score.

## Still open

- Actual six-round or longer longitudinal execution.
- Statistical power and sample sizes needed for useful promotion.
- Whether three or more revisions can be safely promoted.
- Cumulative fresh-transfer benefit, model-family transfer and retention under real
  revision sequences.
- External evaluator/custody authority.
- Validity of any particular confidence-bound implementation until separately checked.

## Relation to existing ORION-15 evidence

This theorem is a successor safety primitive only. It does not re-score V3, V4, the
GLM-5.3 harvest, or any prior protected packet. Existing favourable and adverse evidence
retains its original identity and authority.

A future empirical protocol must bind the gate family, thresholds, protected split and
alpha schedule before opening each round's protected outcome.
