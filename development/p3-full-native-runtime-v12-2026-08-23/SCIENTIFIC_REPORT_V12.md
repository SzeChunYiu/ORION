# P3 full native runtime V12 scientific report

## Exact terminal

`P3_V12_SINGLE_FULL_NATIVE_ATTEMPT_PASS__DIRECT_LOGMAP_CHILD_EXIT_ZERO__FIVE_OF_FIVE_REGULAR_ARTIFACTS__OPTIONAL_WRAPPER_LEXICAL_SEMANTICS_FAIL__STRUCTURAL_PARSER_CANNOT_CHECK__NO_RETRY__NATIVE_READINESS_THREE_OF_THREE__SCIENTIFIC_READINESS_ZERO_OF_THREE`

## What V12 closed

The pre-execution identity gate passed **15/15** checks: the exact CPython 3.10.20 base binary; **126/126** V9 distribution identities and versions; the exact V8 `dp.Score` table-reader repair; **352/352** pinned source files before the explicit V12 runtime adapter; the exact V11 **90/90** LogMap manifest classpath; all six model files; both ontology inputs; OpenJDK 17.0.19; and the unchanged V7 universe manifest and parser.

Exactly one offline, no-gold DeepOnto/BERTMap attempt ran. It used no retry and finished in exactly **231.909885166 seconds** with native exit **0**. The fail-closed adapter exposed the effective LogMap command, inserted only `--add-opens=java.base/java.lang=ALL-UNNAMED`, observed the direct LogMap child exit **0**, and would have raised immediately on a nonzero child.

All five required artifacts are regular non-symlink files:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `raw_mappings.json` | 3,474 | `d72fc7a406183918339593bd69aa4c6ed9fedfbf4b5c544e712dc304cef553ce` |
| `raw_mappings.tsv` | 1,530 | `62fe4224cb12f53fa74a385011ebe3fd2ea90fd83c90aad008f8db4736368ae8` |
| `extended_mappings.tsv` | 1,530 | `62fe4224cb12f53fa74a385011ebe3fd2ea90fd83c90aad008f8db4736368ae8` |
| `filtered_mappings.tsv` | 1,530 | `62fe4224cb12f53fa74a385011ebe3fd2ea90fd83c90aad008f8db4736368ae8` |
| `repaired_mappings.tsv` | 1,946 | `694d281361f3bc73dfdc947ae1a864ddc56c8d0860a8fe518797fd5bfeb3b635` |

Exact native stdout and stderr are retained: stdout 21,916 bytes, SHA-256 `cbba681048ef39a1f413531e384e3853a34396538d3ff9cf20c53f9790314dae`; stderr 57,144 bytes, SHA-256 `26a995a0dbd0072e7919bc509a85e039d22abbb89c16ff6751147ee390b41f02`.

## Separately audited lexical failure

V12 did **not** normalize the repair output. The raw LogMap and final DeepOnto repaired row multisets are exactly equal, proving the downstream transport preserved the strings it received. However, all **16/16** source fields and **16/16** target fields contain `Optional.of(...)`; consequently **0/16** source and **0/16** target strings are exact members of the frozen ontology universes. The unchanged V7 parser therefore exited 2 with `CANNOT_CHECK_NATIVE_ARTIFACT_CONTRACT_FAILURE`: `repaired_mappings.tsv:2: source IRI is outside the frozen universe`.

Thus V12 closes the Java/runtime and five-artifact blockers, raising native execution readiness to **3/3**, while revealing a distinct lexical-semantics blocker. Scientific comparator readiness remains **0/3**. This is not mapping correctness, performance, harm, coverage, transport, superiority, or top-tier submission evidence.

## Cheapest distinct successor

Do not repeat fine-tuning or LogMap. Freeze a no-gold lexical-decoder microgate over the retained 16-row V12 artifacts. It must preserve the original rows, state the OWLAPI Optional grammar prospectively, require injective decoding and exact frozen-universe membership, and rerun only the unchanged V7 structural parser. Any decoder is a new successor identity, not a hidden V12 normalization.

## Runtime and reconstruction costs

- Exact model reconstruction: **27.594744458 seconds**.
- Exact V11 closure reconstruction was previously **7.148934500 seconds** and was reused by hash.
- V12 native attempt: **231.909885166 seconds**.

## Resource cleanup

After all receipts and native artifact hashes were frozen, V12 removed **4,337,898,769 nominal bytes** across 40,925 heavy reconstruction, environment, cache, and training-checkpoint files. The five required artifacts, raw LogMap outputs, configuration, corpora, native log, exact stdout/stderr, protocols, manifests, and receipts remain content-addressed. This cleanup did not rerun or alter the retained native results.
