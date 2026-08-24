# P3 V21 scientific report: direct-IRI decoding and same-universe scoring

## Question

Can the immutable native BERTMap output from V20 be admitted through a
lossless typed interface and compared descriptively with the already frozen
AML output on the same public OAEI 2004 test-103 case?

## Preserved predecessors

- V17 is an immutable failed HermiT attempt. It produced no mappings because
  the historical ontology places a transitive `isPartOf` property in a maximum
  cardinality restriction.
- V18 is an immutable failed compatibility gate. Both structural reasoners
  loaded and returned consistency `true`, but the gate incorrectly expected
  the DeepOnto runtime class index to exclude `owl:Thing` and incorrectly
  expected only non-empty annotation keys.
- V19 passed a distinct outcome-blind runtime-index gate: each raw DeepOnto
  surface was exactly the frozen 36-class universe plus `owl:Thing`; removing
  only that built-in from `Ontology.owl_classes` left the exact 36-by-36
  matcher universe, 33 non-empty local label sets and three empty external
  label sets per role without changing ontology axioms.
- V20 then completed one native BERTMap run, emitted all five required
  artifacts, bound both class surfaces, and returned a direct LogMap child exit
  code of zero. Its inherited V13 optional-wrapper decoder rejected the output
  because the repaired table contains plain absolute IRIs. V20 therefore
  correctly withheld scoring.

No predecessor terminal is overwritten by V21.

## Frozen V21 interface

V21 copies and hashes the five immutable V20 artifacts. The decoder admits an
entity string only when all of the following hold:

1. the whole string matches the frozen absolute-IRI grammar;
2. the IRI is an exact member of the frozen source or target role universe;
3. observed source and target strings are injective; and
4. decoding is the identity transform—no trimming, substitution, wrapper
   removal, URL decoding, heuristic repair, row deletion or row addition.

The format diagnosis is post-matcher-output, but it occurred before semantic
access to the gold alignment. Because the transform is exact identity and
requires role-universe membership, it cannot choose mappings to improve a
score.

## Result

The typed interface passed on all 33 repaired rows. The unchanged structural
parser passed with 36/36 expected source keys, 33 repaired rows and all five
artifact identities bound. Only then did the already frozen evaluator open the
reference alignment.

The analysis unit is **one public OAEI 2004 test-103 case**. Pair cells are not
treated as independent samples, so no population estimand, confidence interval
or p value is reported.

| Estimand | System | Predicted | TP | FP | FN | Precision | Recall | F1 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Common class-to-class opportunity | AML 3.2 | 8 | 8 | 0 | 25 | 1 | 8/33 | 16/41 |
| Common class-to-class opportunity | BERTMap V20/V21 | 33 | 33 | 0 | 0 | 1 | 1 | 1 |
| Full equivalence-pair task | AML 3.2 | 46 | 8 | 38 | 83 | 4/23 | 8/91 | 16/137 |
| Full equivalence-pair task | BERTMap V20/V21 | 33 | 33 | 0 | 58 | 1 | 33/91 | 33/62 |

The exact finite-case F1 differences are `25/41` on the primary common-class
estimand and `3529/8494` on the full equivalence-pair estimand, both in favour
of BERTMap for this case.

## Claim boundary

This is a genuine positive **finite-case descriptive result**. It is not a
population result, current-SOTA claim, general superiority claim, protected
confirmation, source-disjoint replication or naturalistic transport result.
The full-task estimand remains visible: BERTMap predicts no property mappings,
so its full-task recall is `33/91`, not one.

Exact terminals:

- `P3_V21_DIRECT_IRI_TYPED_DECODER_PASS__FROZEN_V20_NATIVE_OUTPUT_SAME_UNIVERSE__COMMON_REFERENCE_SCORING_AUTHORIZED`
- `P3_V21_SAME_UNIVERSE_COMMON_SCORING_PASS__PRIMARY_COMMON_CLASS_PAIR_BERTMAP__ONE_PUBLIC_OAEI_CASE_DESCRIPTIVE_ONLY__NO_POPULATION_OR_GENERAL_SUPERIORITY_AUTHORITY`

## Next discriminator

V22 must freeze a source-disjoint, multi-case provider-native family before
opening its gold alignments; pin seeds, model and matcher revisions; preserve
both estimands; retain AML and a stronger current comparator where interfaces
permit; execute under independent custody; and require worst-case as well as
aggregate gates. Repeating test 103 or treating its 33 pair cells as 33
independent cases cannot close that bridge.
