# P3 comparator-native preflight V6

## Terminal

`P3_V6_TWO_OF_THREE_NATIVE_SMOKE_READY__BERTMAP_PINNED_LOCK_API_INCOMPATIBILITY_CANNOT_CHECK__V5_SCIENTIFIC_READINESS_UNCHANGED_ZERO_OF_THREE`

## Direct result

| Slot | Native smoke | Required artifact gate | Mandatory qualification |
|---|---:|---:|---|
| AML v3.2 | PASS | 1/1 | Java 17 execution; upstream names Java 8 |
| LogMap 4.0 | PASS WITH GUARD | 1/1 primary RDF; mandatory TSV sidecar passed | Upstream RDF header duplicates ontology 1; row namespace guard passed |
| BERTMap / DeepOnto 0.9.3 | CANNOT_CHECK | 0/5 | Pinned Python-3.10 lock selects Transformers 4.51.3, incompatible with DeepOnto's `evaluation_strategy` keyword |

Thus **2/3** families are native-smoke ready. This is not three-family readiness.

## What the BERTMap failure establishes

The exact model revision and weight hash matched, the offline runtime loaded both 16-class ontologies, and input-derived corpora reached 108 training and 12 validation records. Before training, `TrainingArguments` rejected the keyword `evaluation_strategy`. No training, prediction, reference comparison, or performance scoring occurred; all five required mapping artifacts are absent. The only valid terminal is `CANNOT_CHECK_PINNED_DEPENDENCY_API_INCOMPATIBILITY`.

A separately frozen V7 successor changes only the dependency tuple to versions already co-present in the DeepOnto lock's older-Python branch. The 4.46.3 wheel was independently hashed and source-checked to contain the required keyword. That is a prospective discriminator, not a V7 result.

## Unchanged scientific boundary

V3, V4, and V5 terminals remain exactly preserved. In particular, V5 comparator scientific readiness remains **0/3**. Synthetic smoke rows are not correctness, coverage, harm, superiority, or transport evidence. Absence and nonselection are never obstruction.

## Evidence package

See `K1_AML_RESULT_V6.json`, `K2_LOGMAP_RESULT_V6.json`, `K3_BERTMAP_RESULT_V6.json`, `RUNTIME_MANIFEST_V6.json`, `NEGATIVE_RESULT_LEDGER_V6.*`, and `K3_V7_COMPATIBILITY_SUCCESSOR_PROTOCOL.json`. Temporary sources, models, dependencies, logs, and raw native/partial artifacts are deleted after bounded facts and hashes are retained.
