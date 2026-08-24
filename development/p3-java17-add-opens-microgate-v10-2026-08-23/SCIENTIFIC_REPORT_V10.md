# P3 Java 17 `--add-opens` repair microgate V10

## Exact terminal

`P3_V10_JAVA17_ADD_OPENS_MICROGATE_CANNOT_CHECK__DIRECT_CHILD_EXIT_ONE__V9_MANIFEST_CLASSPATH_CLOSURE_ABSENT_AFTER_CLEANUP__NO_REGULAR_REPAIR_OUTPUT__NO_RETRY__FULL_NATIVE_SUCCESSOR_NOT_AUTHORIZED`

## One-attempt result

The single authorized **repair-only Java child** ran for exactly **0.133503125 seconds**. It received the sole candidate JVM delta `--add-opens=java.base/java.lang=ALL-UNNAMED`; no DeepOnto/BERTMap training, prediction, gold/reference opening, scientific scoring, retry, or full native rerun occurred. The direct child exited **1**. The required `mappings_repaired_with_LogMap.tsv` was absent, so the gate **failed** and no full native successor is authorized from V10.

Exact stdout and stderr are retained byte-for-byte as `JAVA_STDOUT_V10.log` and `JAVA_STDERR_V10.log`. Stderr is 567 bytes with SHA-256 `b2079700384a4a88eca82482aac88fca927a19bde98fcd7ec8a3aeb118d71be6`.

## Hash-bound V9 identity

All five launched identities matched the frozen V9 hashes before the child started:

| Identity | SHA-256 | Match |
|---|---|---:|
| OpenJDK 17 `bin/java` | `7db0dd5c0c4dc931244875d0723783a32cc7912922e6aaac1dbb744bf8ae837f` | yes |
| LogMap 4.0 main JAR | `e0b217156ffece911c472cc2cb2b25e7948b3c46801037e0161c3a752332d6a3` | yes |
| source ontology | `c347f32626f6c5b3b782b2f6344bca5ac2282a701161d11f1e02a7422fef4d9e` | yes |
| target ontology | `16bd34ec22c3d130b94257404fd60a112a3383d16255a67472e0c5e1518c5521` | yes |
| V9 filtered mapping input | `6c12ab82c83e6d44149cb03f761880e8a23171d6fb73142225d49e1c6b0eafe4` | yes |

The protocol also binds the V9 protocol, result, JDK manifest, Java-component SBOM, and 30/30 runtime-rights gate hashes.

## Exact failure adjudication

The immediate exception was `NoClassDefFoundError` for `org.semanticweb.owlapi.model.OWLOntologyCreationException`, caused by `ClassNotFoundException`. The exact LogMap main JAR is thin: its manifest names **90** relative `java-dependencies/...` entries. V9 cleanup had removed both `runtime/venv` and `runtime/source`; the V10 packet restored the exact main JAR, but **0/90** adjacent manifest-classpath entries were present. The child therefore stopped before reaching the V9 Guice reflective-access site.

Accordingly, this is a failed runtime-closure microgate and the efficacy of `--add-opens` remains **CANNOT_CHECK**. It is not evidence that the flag is ineffective, and it has no mapping-correctness, performance, harm, coverage, transport, superiority, or submission-readiness authority.

## Cheapest distinct successor

Before any further Java execution, reconstruct all 90 manifest-classpath entries at their exact relative paths and verify every file against the V9 Java-component SBOM. Freeze that verified closure as a new successor identity, then permit one repair-only Java child with the same exact V9 hashes and only the same `--add-opens` addition. A full native BERTMap run remains disallowed until such a microgate exits zero and produces the required regular non-symlink repair output. V10 itself is locked and is not retried.
