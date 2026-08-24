# P3 V9 negative-result ledger

## P3-V9-JAVA17-GUICE4-STRONG-ENCAPSULATION

- **Observed stage:** LogMap repair subprocess initialization, after four of five native artifacts existed.
- **Primary exception:** `java.lang.reflect.InaccessibleObjectException`.
- **Exact mechanism:** Guice 4.0 cglib reflects into `java.lang.ClassLoader.defineClass`; Java 17 denies the access because `java.base/java.lang` is not open to the unnamed module.
- **Consequence:** LogMap emits no `mappings_repaired_with_LogMap.tsv`; DeepOnto emits no `repaired_mappings.tsv`.
- **Not the cause:** V8 table-reader patch, model availability, ontology availability, network, or timeout.
- **Fast discriminator:** a separately frozen repair-only LogMap microgate with `--add-opens=java.base/java.lang=ALL-UNNAMED`, explicit child exit-code propagation, and no gold.
- **Candidate status:** `CANNOT_CHECK__NOT_EXECUTED`; V9 cannot be retried.

## P3-V9-DEEPONTO-RUN-JAR-EXIT-STATUS-NOT-PROPAGATED

`deeponto.utils.file_utils.run_jar` waits for the Java child but does not check or return its exit code. The later missing-file exception obscures the earlier Java cause. A successor should fail immediately on a nonzero LogMap exit. This is a diagnostic-quality repair, not a scientific change.

## Positive evidence retained

The single attempt completed JVM start, fine-tuning, prediction, extension, and filtering. The V8 `dp.Score` patch was exercised natively on the previously failing path. Four actual artifacts are retained with hashes in `NEGATIVE_RESULT_LEDGER_V9.json`. No row is interpreted as correct and no gold/reference was opened.
