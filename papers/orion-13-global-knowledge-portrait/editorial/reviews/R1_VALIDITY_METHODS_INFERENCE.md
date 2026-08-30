# Reviewer 1 — validity, methods, and inference

**Blind review object:** PDF SHA-256 `b843d9ef8cd399c3e186e3a05edca582a2bd9de08f3c22d192b7187b42ac4c19` (8 pages)

**Recommendation:** major revision.

The paper asks a clean bounded question and reports the registered comparison, paired unit, interval, and adverse/null boundaries unusually clearly. The principal numerical result is internally consistent. Three validity statements nevertheless require repair.

## R1-M1 — “Disjoint” overstates independence

The manuscript calls the confirmatory set disjoint and says overlap is zero. The frozen replay record distinguishes zero case-ID overlap from two repeated source-locator--content-hash records. A reader could reasonably interpret “disjoint” as source-disjoint.

**Resolution test:** every headline use of “disjoint” is qualified as case-identifier-disjoint; Dataset and Limitations report the two recurring source records and state that the sets are not source-disjoint.

## R1-M2 — Existing receipt is not a separate implementation

The cited reproduction route calls the same public-reference analysis functions used to generate the frozen result. That is a deterministic regeneration, not a separately implemented evaluator.

**Resolution test:** either remove the separate-implementation claim or provide a verifier that imports no generating analysis/semantics code, recomputes case decisions and both paired intervals from the frozen cases, records its code identity, and states the same-custody boundary.

## R1-M3 — Empirical effect is polarity-localized

The prose attributes discrimination to polarity, modality, attribution, and context collectively. Inspection of the six disagreements with the flat comparator shows that every one is a polarity contrast. The other coordinates may be part of the mechanism but are not empirically supported by this holdout.

**Resolution test:** Abstract, Introduction, Methods, Results, Limitations, and Conclusion localize the observed effect to polarity and explicitly deny necessity or empirical-value claims for the other coordinates.

## Minor points

- Retain the exact-control abstention rate alongside its zero false-split rate.
- Keep zero ablation deltas visible and interpret them as missing comparison opportunity.
- Do not describe a same-repository replay as external replication.
