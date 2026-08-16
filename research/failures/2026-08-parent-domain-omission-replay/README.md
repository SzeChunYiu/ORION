# Parent-discipline omission replay — RAKL NLP / psychometrics episode

## Source identity

Historical workflow source:

`SzeChunYiu/RAKL@bd4ce50f48bbfd7d36e9a41ded9566f77d8105ca:skills/rakl-core/workflows/self-rakl.md`

The workflow explicitly required broad cross-domain search and materially different vocabulary, and it listed a finite minimum set of named discipline families. The named list included IR/databases, formal methods, KR, causal inference, software reliability, human factors and many others, but did **not** explicitly name computational linguistics/NLP or psychometrics/measurement science.

That observation alone does not establish that faithful function-only/cross-domain search could not have discovered those fields.

## Competing causes

- `H1 EXECUTION/ENFORCEMENT`: required heterogeneous routes existed but the original run did not execute them deeply enough.
- `H2 ROUTING`: the route family existed but was not activated for the language/measurement boundary.
- `H3 RETRIEVAL`: a suitable functional query was issued but the retriever/corpus missed the parent field.
- `H4 REPRESENTATION/FIXATION`: evidence was reachable/retrieved but the current problem representation did not recognize it as a parent discipline.
- `H5 NAMED_BASIS/ONTOLOGY GAP`: the finite bootstrap discipline basis biased exploration and omitted an important coordinate.
- `H6 STOPPING`: the run stopped before the search universe expanded.
- `H7 METHOD_BASIS GAP`: RAKL lacked any operation capable of discovering a parent discipline from functional correspondence.

## What the frozen evidence identifies

### Confirmed

1. **Named-basis omission:** the frozen Self-RAKL minimum list does not explicitly name computational linguistics or psychometrics.
2. **Historical trace gap:** the original query/retrieval/recognition trace needed to distinguish H1–H6 is not registered in ORION. Therefore the exact historical execution cause is `PARTIALLY_IDENTIFIED`, not guessed.
3. **A method-basis change is not required by the replay:** a generic functional-operation-signature -> externally sourced parent-discipline-profile matcher can recover the two historical targets without placing their names in the signatures.
4. **Fresh transfer:** the same matcher recovers three unrelated hidden parent fields from function signatures: information foraging, data integration and metrology.

### Not established

- that the original RAKL run faithfully executed every required route;
- that a faithful historical retriever would definitely have found NLP/psychometrics;
- that the finite named list was the sole cause;
- that current functional parent-domain matching guarantees open-world unknown-unknown recall.

## Minimum repair

`FunctionalOperationSignature` describes what an ORION mechanic actually does—operations, objects, failures and invariants—without discipline labels.

`ParentDisciplineProfile` is external knowledge about how a mature field studies a function. The discipline name is output metadata and is **not** used as a match feature.

`discover_parent_disciplines` ranks profiles by weighted functional correspondence. A candidate records whether the target label was lexically independent of the ORION signature and carries source evidence.

The repair is therefore not "remember NLP and psychometrics." It is:

`mechanic function/failure/invariants -> function-only/parent-domain search -> evidence-bound parent-domain profiles -> label-independent match -> new W/search direction`.

## Frozen replay

`src/orion/benchmarks/parent_domain_replay.py` freezes:

- historical target 1: scientific-language interpretation -> computational linguistics;
- historical target 2: benchmark/construct validity -> psychometrics;
- fresh target 1: route stopping/patch switching -> information foraging;
- fresh target 2: cross-source identity/schema matching -> data integration;
- fresh target 3: measurand/calibration/uncertainty/traceability -> metrology.

Acceptance:

- both historical fields absent from the named historical basis;
- both historical fields recovered by functional matching;
- no target label appears in the functional signature;
- all three fresh fields recovered with the same mechanism;
- no method-basis repair is required to solve the frozen cases;
- exact original historical cause remains explicitly blocked by missing trace evidence.

## Failure-learning conclusion

The correct learned rule is **not** "NLP and psychometrics must always be on the checklist."

It is:

> When an atomic ORION operation becomes important, derive a name-independent functional signature and challenge the search universe for mature fields that study those operations/failures/invariants. A finite named discipline basis is only a seed, never evidence of parent-domain closure.

A historical miss that lacks its query/retrieval trace remains causally unresolved rather than being rewritten after the fact.
