# P3 V17 scientific report: immutable HermiT compatibility failure

V17 prospectively froze one BERTMap attempt on the provider-native OAEI 2004
test-103 source/target pair, the exact V12 model and thresholds, the V13 typed
decoder, the already frozen AML output, and a common evaluator that could not
open the gold alignment until both system outputs were frozen.

The outcome-blind public-document-IRI adapter passed semantic isomorphism and
froze a 36-by-36 named-class universe. Runtime preflight passed 30/30 checks.
The only native attempt ran for 89.887939583 seconds and exited before producing
any of the five required artifacts. No retry occurred.

Exact causal exception:

`java.lang.IllegalArgumentException: Non-simple property '<http://co4.inrialpes.fr/align/Contest/101/onto.rdf#isPartOf>' or its inverse appears in the cardinality restriction 'ObjectMaxCardinality(1 <http://co4.inrialpes.fr/align/Contest/101/onto.rdf#isPartOf> owl:Thing)'.`

HermiT rejects the historical combination of a transitive `isPartOf` property
with a maximum-cardinality restriction. The output directory remained empty,
the typed decoder did not run, the reference alignment was not semantically
opened, and common scoring was not authorized.

Exact terminal:

`P3_V17_BERTMAP_NATIVE_ATTEMPT_FAIL__NO_RETRY__COMMON_SCORING_NOT_AUTHORIZED`

V18 therefore tests only whether the exact pair supports the structural
reasoner and BERTMap-required annotation/asserted-taxonomy surface. V17 remains
immutable even though later successors use a different, explicitly identified
reasoner compatibility route.
