# ORION-ORION-13 annotation handbook V1

**Status:** frozen before final gold labeling and before final model-output inspection.

## Purpose

The gold object is not a single `same/different` label. Scientific integration can fail because identity, construct, operationalization, temporal state, modality, attribution or representation conditions differ. Annotators therefore judge coordinates in a fixed order and may return `UNRESOLVED`; uncertainty must not be coerced into a merge.

## Annotation order

1. **Source identity first.** Verify document/version/span and text hash. Do not label from a paraphrase when the frozen source span is available.
2. **Referent.** Ask whether the two spans are about the same entity/event/object. Lexical sameness is not evidence of referent sameness; aliases may still denote the same referent.
3. **Construct.** Decide whether the scientific quantity/concept itself is the same, related-but-not-same, or different. Do not infer construct identity from measurement correlation alone.
4. **Measurement/operationalization.** Decide whether operational definitions are equivalent, conditionally transformable, non-equivalent, absent, or unresolved. Record required transformation/assumptions.
5. **Context.** Compare population/system, spatial/temporal state, experimental condition, scale and relevant boundary conditions.
6. **Polarity and modality.** Distinguish asserted opposition from differences such as `may`, `likely`, `under condition X`, or hypothesis/reporting language.
7. **Attribution and discourse.** Distinguish the authors' claim from a cited claim, background statement, limitation, speculation or reported disagreement.
8. **Mapping.** Only now label identity/equivalence/conditional transform/subsumption/association/no mapping. A high semantic similarity score is never sufficient by itself.
9. **Contradiction.** Label contradiction only when referent/construct/context are aligned enough for opposed claims to be comparable.
10. **Integration.** `GLUE_ALLOWED` requires a licensed mapping and explicit preservation conditions. Use `OBSTRUCTION` for a demonstrated incompatibility, `PLURAL_VIEW` when multiple legitimate non-collapsible views should coexist, and `UNRESOLVED` when evidence is insufficient.
11. **Recoverability target.** List the source and mapping coordinates that a global statement must expose or link back to for the case to count as recoverable.

## Special cases

### Same label, different thing
Prefer `referent=DIFFERENT`; do not let shared terminology induce a false merge.

### Same construct, different measurement
`construct=SAME` can coexist with `measurement=NON_EQUIVALENT`. This is a central target case, not an annotation contradiction.

### Apparently opposite results
First align population, time/state, operationalization, modality and attribution. If one source says an effect is possible and another says it is not established, that is not automatically an asserted contradiction.

### Transformable representations
Use `CONDITIONAL_TRANSFORM` and enumerate preservation conditions/non-preserved coordinates. Do not label `IDENTITY` merely because a conversion is possible.

### Expert disagreement
Use `UNRESOLVED` in the independent round and trigger the frozen adjudication policy. Never modify the source excerpt to make the case easier.

## Gold-authority rule

LLMs may assist with candidate extraction or annotation tooling, but an LLM-generated label cannot become final scientific gold solely because another LLM agrees. Final gold follows the independent human/domain-expert and adjudication policy.

## Agreement reporting

Report agreement separately for referent, construct, measurement, context, contradiction, mapping and integration verdict. A single aggregate agreement score may be reported secondarily but cannot hide a weak coordinate.
