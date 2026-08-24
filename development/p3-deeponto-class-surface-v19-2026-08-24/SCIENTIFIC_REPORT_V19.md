# P3 V19 scientific report: outcome-blind DeepOnto class-surface adapter

V19 preserves V18's failure and tests only its causal runtime-surface
hypothesis. Each ontology is loaded with the structural reasoner. The gate
requires the raw `Ontology.owl_classes` dictionary to equal the earlier frozen
36-class role universe plus exactly `owl:Thing`; it then removes only that
built-in from the Python runtime dictionary. No ontology axiom is added,
removed or rewritten.

The preflight passed 10/10 checks. Both raw surfaces were exactly 37 classes,
both post-adapter surfaces were exactly the frozen 36 classes, and each
annotation index had exactly 36 keys: 33 non-empty local labels and three empty
external labels. Structural consistency, asserted parents, asserted children
and sibling groups all passed their frozen gates.

Exact terminal:

`P3_V19_DEEPONTO_BUILTIN_CLASS_SURFACE_PASS__OWL_THING_EXACTLY_REMOVED_FROM_RUNTIME_INDEX__EXACT_36_BY_36_MATCHER_UNIVERSE_AND_33_BY_33_NONEMPTY_LABEL_SURFACE__V20_BERTMAP_FREEZE_AUTHORIZED`

This positive result authorizes only the exact V20 compatibility entrypoint. It
does not establish matcher success, mapping quality, efficiency,
generalisation or superiority. No training, matching, reference access or
scoring occurred in V19.
