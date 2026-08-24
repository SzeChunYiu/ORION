# P3 Optional-wrapper typed decoder V13

## Exact terminal

`P3_V13_TYPED_OPTIONAL_DECODER_PASS__SIXTEEN_OF_SIXTEEN_EXACT_ROLE_UNIVERSE_MEMBERS__INJECTIVE__TWELVE_OF_TWELVE_ADVERSARIAL_MICROCASES_PASS__UNCHANGED_V7_STRUCTURAL_PARSER_PASS__RAW_V12_UNCHANGED`

## Result

V13 used only the retained **16** V12 repaired rows and the frozen source/target universes. It performed no download, training, LogMap, Java, DeepOnto, native rerun, retry, gold/reference access, protected-outcome access, or scientific scoring. Total decoder-plus-parser runtime was exactly **0.033283000 seconds**; the unchanged V7 parser used **0.031007000 seconds**.

The decoder is not arbitrary string stripping. Its anchored typed grammar accepts only:

`Optional.of(<ontology-IRI>)<fragment>`

where the ontology IRI and fragment contain no whitespace, nested parentheses, or second fragment; decoding is exactly `ontology_iri + fragment`; and the result must be an exact member of the correct role-specific frozen universe. No trimming, case folding, substring replacement, URL decoding, or heuristic mutation is permitted.

## Gates passed

- **12/12** frozen adversarial microcases passed, including malformed constructors, missing delimiters, nesting, embedded fragments, empty/multiple fragments, whitespace, unknown members, and cross-role members.
- **16/16** real source strings and **16/16** real target strings decoded to exact role-specific universe members.
- Source and target decoding were independently injective.
- The separate decoded artifact is 1,530 bytes, SHA-256 `c67ee88d541013f41984b239f9cdeaebdcd81573f2080d8af24c7688207dd0f3`.
- The unchanged V7 structural parser exited **0** with `STRUCTURAL_NATIVE_ARTIFACT_CONTRACT_PASS`; all five row counts are 16.
- The original V12 repaired artifact remained byte-identical before and after, SHA-256 `694d281361f3bc73dfdc947ae1a864ddc56c8d0860a8fe518797fd5bfeb3b635`. A byte-identical copy is retained separately in V13.

## Claim boundary

V13 closes the exact lexical-interface blocker exposed by V12 and establishes structural five-artifact conformance for the separately decoded artifact. It does not retroactively alter V12, and it does not establish mapping truth, correctness, performance, harm, coverage, transport, superiority, or top-tier readiness. Scientific comparator readiness remains **0/3** until a separately authorized empirical evaluation opens the appropriate reference evidence.

## Efficient next use

Any downstream integration must use this exact typed grammar, exact universe-membership gate, and injectivity gate as an explicit receipted adapter while retaining the original wrapped rows. There is no reason to repeat BERT fine-tuning or LogMap merely to reproduce this 16-row lexical transformation.
