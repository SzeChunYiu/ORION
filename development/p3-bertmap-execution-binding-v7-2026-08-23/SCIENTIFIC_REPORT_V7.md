# P3 BERTMap execution binding V7

## Terminal

`P3_V7_BERTMAP_PAPER_SOURCE_AND_DEPENDENCY_CONSTRUCTOR_COMPATIBILITY_BOUND__CLOSED_FIVE_ARTIFACT_PARSER_BOUND__NONEMPTY_SOURCE_TABLE_READER_DEFECT_AND_FULL_NATIVE_SMOKE_CANNOT_CHECK__NATIVE_READINESS_TWO_OF_THREE__SCIENTIFIC_READINESS_ZERO_OF_THREE`

## Exact result

The exact paper/source bridge is bound: the canonical original repository at
`ce848402b40e2f9513bf2d004894d3f82635022c` says BERTMap is now maintained in
DeepOnto, and DeepOnto 0.9.3 at
`74ca8d47f01bad0b8739f19ee2c392bdf6d9c090` links both that repository and the
AAAI paper (DOI `10.1609/aaai.v36i5.20510`). Both root source layers are
Apache-2.0.

The V6 dependency failure is repaired **only at constructor level**. In a
hash-locked Python-3.10.20/macOS-arm64 compatibility island, exact versions
Transformers 4.46.3, Tokenizers 0.20.3, Accelerate 1.0.1 and Torch 2.5.1
imported, the `evaluation_strategy` signature existed, and the exact
`TrainingArguments` construction returned. The installed source hash is
`6c594e97c4dd930612ccba8fe763650ef91ae9d7e20b20d326017bf7cd06f237`. That keyword
is already deprecated in 4.46.3, so floating upgrades remain forbidden.

This is not a BERTMap run. DeepOnto was not imported, no JVM was started, and
no model, ontology, benchmark, paper `data.zip`, gold/reference alignment,
protected outcome, training, prediction, repair or scoring was opened or run.

## New downstream blocker

Pinned `src/deeponto/align/mapping.py` lines 119--151 iterates
`pandas.DataFrame.itertuples()` rows and then uses `dp["Score"]`. Such rows are
namedtuples; the synthetic nonempty source-semantic fixture returns
`TypeError: tuple indices must be integers or slices, not str`.
Therefore any nonempty raw TSV reaching `MappingRefiner` is conditionally
blocked. This defect was not patched: a repair requires a new source identity.

## Closed native artifact parser

`bertmap_native_parser_v7.py` passed 7/7
direct synthetic checks. It requires all five files, exact eligible source-key
coverage (including empty lists), JSON/TSV equivalence, universe guards,
finite `[0,1]` scores, raw retention, exact filtering, repaired-pair
containment and SHA-256 hashes. A complete zero-row artifact set passes;
absence is never obstruction. Parser pass has interface authority only.

## Readiness delta

| Axis | Before | After | Delta |
|---|---:|---:|---|
| BERTMap dependency keyword | CANNOT_CHECK | constructor-only PASS | repaired locally |
| BERTMap closed artifact parser | generic shape gate | source-native fail-closed parser | bound |
| Three-family native smoke | 2/3 | 2/3 | 0 |
| V5 scientific comparator readiness | 0/3 | 0/3 | 0 |
| BERTMap required artifacts | 0/5 | 0/5 | 0 |

## Rights boundary

The constructor island contains 26 installed distributions and all expose
some licence metadata. That is not a complete runtime SBOM. The pinned
DeepOnto tree contains 208 JAR entries (99,413,938 bytes), and the
original BERTMap tree contains 106 JAR entries (33,438,277 bytes).
Their component-level provenance/licences, the full Python/JVM closure, model,
generated artifacts, OAEI submodule and independent evaluation custody remain
unclosed. The original `data.zip` is a 2,017,453-byte blob described
as paper ontologies plus reference mappings; it was not opened and is excluded.

## Remaining blockers

1. freeze a separately identified repair for the nonempty table-reader defect;
2. bind the complete Python/JVM runtime and component-level rights/SBOM;
3. run one fresh isolated no-gold smoke and require all five files to pass the closed parser;
4. only then freeze independent, rights-valid evaluation custody.

Correctness, coverage, harm, transport, performance, superiority and top-tier
readiness remain `CANNOT_CHECK` / not established.
