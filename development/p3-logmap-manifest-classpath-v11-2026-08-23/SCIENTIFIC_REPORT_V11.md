# P3 exact LogMap classpath and Java 17 repair microgate V11

## Exact terminal

`P3_V11_EXACT_V9_CLASSPATH_90_OF_90_PASS__JAVA17_ADD_OPENS_REPAIR_MICROGATE_PASS__DIRECT_CHILD_EXIT_ZERO__REGULAR_REPAIRED_MAPPING_OUTPUT_PRESENT__NO_RETRY__FULL_NATIVE_SUCCESSOR_AUTHORIZED`

## Result

V11 materially repaired V10's under-bound runtime. It reconstructed the exact LogMap 4.0 manifest classpath from `KRR-Oxford/DeepOnto@74ca8d47f01bad0b8739f19ee2c392bdf6d9c090`: **90/90** adjacent JARs, **25,337,399 bytes**, all matched the V9 Java-component SBOM. Fixed-closure reconstruction took exactly **7.148934500 seconds**.

After live re-verification of all 90 dependency hashes and the five frozen V9 launch identities, exactly one repair-only Java child ran with the sole candidate JVM delta `--add-opens=java.base/java.lang=ALL-UNNAMED`. It exited **0** in exactly **0.429009959 seconds**, used no retry, and produced the required regular non-symlink `mappings_repaired_with_LogMap.tsv`:

- 1,920 bytes; SHA-256 `8507d5de622b74b202a288b186e080afbea5dde55d056015a8cb72c5e472b2cf`;
- 16 tab-separated, three-field rows;
- exact stderr empty, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`;
- three additional regular LogMap outputs (`.owl`, `.rdf`, `.txt`) are hash-inventoried in the JSON receipt.

No DeepOnto/BERTMap training, prediction, full native rerun, gold/reference opening, protected outcome, or scientific scoring occurred.

## Claim boundary

This is positive **localized runtime and artifact-interface conformance**: with the exact V9 Java binary, LogMap JAR, 90-entry dependency closure, ontology inputs, and filtered mappings, the Java 17 module-opening directive allows the repair child to terminate normally and create the required artifact. It authorizes a separately frozen full native successor; it does not itself establish mapping correctness, performance, harm, coverage, transport, superiority, or top-tier readiness. The separate full successor must also propagate the LogMap child exit directly rather than permit DeepOnto's secondary missing-file exception to obscure a primary failure.

A lexical observation is retained without promotion: all 16 output source and target fields start with `Optional.of(...)`. That shape was outside the preregistered V11 success gate and is not adjudicated as correct or incorrect here; a full successor must preserve it as evidence rather than silently normalize it after outcome observation.

## Identity evidence

| Identity | SHA-256 |
|---|---|
| OpenJDK 17 `bin/java` | `7db0dd5c0c4dc931244875d0723783a32cc7912922e6aaac1dbb744bf8ae837f` |
| LogMap 4.0 main JAR | `e0b217156ffece911c472cc2cb2b25e7948b3c46801037e0161c3a752332d6a3` |
| source ontology | `c347f32626f6c5b3b782b2f6344bca5ac2282a701161d11f1e02a7422fef4d9e` |
| target ontology | `16bd34ec22c3d130b94257404fd60a112a3383d16255a67472e0c5e1518c5521` |
| V9 filtered mapping input | `6c12ab82c83e6d44149cb03f761880e8a23171d6fb73142225d49e1c6b0eafe4` |
| 90-entry closure preflight | `15f178b91595d6f17da79a1fd234be7a66f58a1cdec82d5af18a376bc2ca086c` |
| frozen V11 protocol | `a30bb13cc8bb6a4fb3551424eb8b2b02923ad72e92165603211e139d05ded027` |
