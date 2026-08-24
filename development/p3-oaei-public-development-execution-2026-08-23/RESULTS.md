# P3 OAEI public-development execution results

**Frozen scored identity:** `P3.PUBLIC.OAEI.CONFLICT_PRESERVING.DEV.V2`  
**Authority:** `PUBLIC_ONE_SEED_FAMILY_DESCRIPTIVE_DEVELOPMENT_ONLY`  
**Primary terminal:** `PUBLIC_CANDIDATE_UNIVERSE_INVALID`  
**Protected/frozen-768 authority:** `CANNOT_CHECK`

## Executive scientific result

V1 failed before public-gold access because local-fragment matching produced 2,153 ambiguous case keys and one AML pair lay outside the explicit-declaration signature. That adverse identity is preserved; no V1 result exists. V2 repaired document-aware IRI matching, added an input-only class-position signature closure, froze 68,187 cases and 477,309 predictions, and achieved zero AML/case ambiguities and zero AML pairs outside its pre-gold universe.

After the V2 freeze, the public OAEI reference join failed the candidate-universe gate: frozen recall was `0.930962343096` (`1335/1434` reference cells under the frozen definition). The P3 candidate also failed the envelope gate with coverage `0.995541672166` (304 failures). Therefore the exact terminal is **`PUBLIC_CANDIDATE_UNIVERSE_INVALID`**, not a positive empirical result.

The candidate nevertheless showed a non-promotable descriptive harm pattern: candidate-minus-AML mean floor-adjusted harm was negative in all three frozen regimes. This is a research lead only because both mandatory validity gates failed.

## Frozen full-census metrics

| System | Precision | Recall | F1 | Exact | Unresolved | Envelope coverage | Harm R1 | Harm R2 | Harm R3 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `AML_V3_2_AUTO_SOURCE_NATIVE` | 0.941463 | 0.289139 | 0.442407 | 0.927831 | 0.059234 | 0.987065 | 0.027744 | 0.029151 | 0.078076 |
| `FLAT_LABEL_EQUALITY_V1` | 0.790134 | 0.707865 | 0.746740 | 0.990599 | 0.000000 | 0.990599 | 0.009401 | 0.024125 | 0.032279 |
| `TOKEN_JACCARD_FORCED_V1` | 0.737828 | 0.737828 | 0.737828 | 0.989734 | 0.000000 | 0.989734 | 0.010266 | 0.030798 | 0.030798 |
| `AML_OR_LABEL_FORCED_V1` | 0.797837 | 0.718352 | 0.756011 | 0.933022 | 0.059234 | 0.992257 | 0.022552 | 0.036807 | 0.039271 |
| `AML_AND_LABEL_FORCED_V1` | 0.948787 | 0.263670 | 0.412661 | 0.927406 | 0.059234 | 0.986640 | 0.028169 | 0.029283 | 0.080496 |
| `P3_CONFLICT_PRESERVING_WRAPPER_V1` | 0.948787 | 0.263670 | 0.412661 | 0.924120 | 0.071421 | 0.995542 | 0.022314 | 0.023428 | 0.039032 |
| `P3_INFORMATION_EQUIVALENT_IDEAL_V1` | 0.948787 | 0.263670 | 0.412661 | 0.924120 | 0.071421 | 0.995542 | 0.022314 | 0.023428 | 0.039032 |

## Candidate minus AML

- Exact-rate delta: `-0.003710384677`
- Unresolved-rate delta: `0.012187073782`
- Harm deltas: `[-0.005429920659, -0.005723231701, -0.039043366038]`
- Information-equivalent ideal tie: `True`
- Candidate-universe recall gate: `False`
- Candidate envelope-coverage gate: `False`

## Failure anatomy

- Envelope failures: `304` = `285` missed GLUE plus `19` false GLUE.
- Failures by target: `105:3`, `201:76`, `202:91`, `204:9`, `205:55`, `222:1`, `223:8`, `301:26`, `302:19`, `303:6`, `304:10`.
- Reference cells: `1434` total; `35` used `<` or `>` and were not expressible under the frozen binary join; `64` equivalence pairs were unmapped; test `105` had no reference member.
- AML test `206` remained unparsable; all 19 successful AML outputs passed byte-identical replay.
- One seed family means no inferential authority.

## Interpretation boundary

This execution supports only a public, one-family development diagnosis: preserving conflict lowered the frozen harm functional descriptively, but the agreement-to-point rule and the evaluation universe were both falsified. It does **not** support P3 comparative superiority, a PLURAL or temporal claim, protected confirmation, the frozen 768-cluster study, or any top-tier general claim.

## Next discriminators

1. Enumerate referent candidates across construct types and close the input-only signature over property-valued positions.
2. Treat missing reference panels and non-expressible `<`/`>` relations as `CANNOT_CHECK`, never as closed-world obstruction.
3. Replace agreement-to-point with a predeclared structure-aware evidence-adequacy rule that must attain envelope coverage 1.0 and tie an information-equivalent ideal.
4. Validate the repaired rule on multiple untouched ontology families; OAEI 2004 remains development-only.
