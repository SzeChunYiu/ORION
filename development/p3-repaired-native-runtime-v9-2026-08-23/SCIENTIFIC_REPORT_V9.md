# P3 repaired native runtime V9 scientific report

## Exact terminal

`P3_V9_COMPLETE_RUNTIME_RIGHTS_PASS__SINGLE_NATIVE_ATTEMPT_REACHED_FOUR_OF_FIVE_ARTIFACTS__LOGMAP_JAVA17_GUICE4_MODULE_ACCESS_CANNOT_CHECK__NO_RETRY__NATIVE_READINESS_TWO_OF_THREE__SCIENTIFIC_READINESS_ZERO_OF_THREE`

## What V9 closed

The prospective protocol remained frozen at SHA-256 `7e5eac0b04988cf936a9517043e63f8599866d215e1c5b3537fb47271d87f2e8`. The complete runtime and component-rights gate passed **30/30** checks before execution. The one authorized offline native attempt started OpenJDK 17.0.19, completed BERT fine-tuning, global mapping prediction, mapping extension, and mapping filtering in 241.890 wall seconds. It produced four regular native artifacts: `raw_mappings.json`, `raw_mappings.tsv`, `extended_mappings.tsv`, and `filtered_mappings.tsv`.

The V8 `dp.Score` repair received stronger native evidence: a nonempty, truthy-threshold refinement path completed without the prior `TypeError`. This is source/runtime evidence only, not mapping correctness.

## Exact unresolved native failure

The LogMap repair subprocess failed under Java 17 before creating its repair output. Its exact causal exception was `java.lang.reflect.InaccessibleObjectException`: Guice 4.0 cglib attempted reflective access to `ClassLoader.defineClass`, while `java.base/java.lang` was not open to the unnamed module. The packet binds LogMap 4.0, OWLAPI 4.1.3, and Guice 4.0; Guice was built with JDK 1.7 and LogMap with JDK 1.8. DeepOnto then attempted to open the absent `mappings_repaired_with_LogMap.tsv`, causing a secondary `FileNotFoundError`.

Therefore `repaired_mappings.tsv` is absent, the unchanged frozen V7 parser returns `CANNOT_CHECK_NATIVE_ARTIFACT_CONTRACT_FAILURE`, and the five-artifact contract does not pass. No retry or post-result patch was made.

## Most efficient recursive repair

Do **not** spend another full training run to rediscover this Java-only failure. Freeze a new, repair-only no-gold microgate first, with the same content-addressed Java/JAR/input identities and only the standard Java 17 directive:

`--add-opens=java.base/java.lang=ALL-UNNAMED`

That successor must require the LogMap child exit code to propagate directly and require its output as a regular non-symlink file. The flag is a precisely localized candidate, not yet a verified repair. Only after the microgate passes should a separately frozen full native successor run. V9 itself remains immutable and is never retried.

## Readiness and claim boundary

| Axis | Before | After |
|---|---:|---:|
| Complete runtime rights | open | 30/30 PASS |
| Required actual artifacts | 0/5 | 4/5 |
| Native smoke readiness | 2/3 | 2/3 |
| Scientific comparator readiness | 0/3 | 0/3 |

No gold/reference alignment or protected outcome was opened, and no correctness, performance, harm, coverage, transport, or superiority score was computed. V9 is not top-tier submission evidence; it is a sharply localized native-runtime result plus an efficient successor design.
