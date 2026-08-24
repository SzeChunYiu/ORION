# P3 V18 scientific report: preserved structural microgate failure

V18 was prospectively frozen after V17's HermiT exception and before any new
matcher, training, reference access or scoring. Its only authority was to load
the frozen source and target with `Ontology(path, reasoner_type="struct")`,
verify class/annotation surfaces, and exercise consistency and the asserted
parent, child and sibling operations required by BERTMap.

The preflight passed 10/10 checks. Both ontologies loaded, both structural
consistency calls returned `true`, all asserted taxonomy members stayed inside
the frozen 36-class role universes, and no exception occurred. The gate still
failed because its surface contract was wrong: DeepOnto exposed 37 class keys
per role rather than 36, and `build_annotation_index` materialised 37 keys
rather than the expected 33. No training, matching, reference access or scoring
occurred.

Exact terminal:

`P3_V18_STRUCTURAL_REASONER_COMPATIBILITY_FAIL__V19_BERTMAP_NOT_AUTHORIZED`

The result is not evidence that the structural reasoner is incompatible. It is
an exact failure of V18's runtime-surface assumptions. V19 therefore tests the
narrow causal discriminator: raw surface = frozen 36 classes plus exactly
`owl:Thing`, followed by an outcome-blind runtime-index-only removal.
