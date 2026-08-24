# P3 V4 source-native comparator research

**Audit time:** 2026-08-23T15:28:31Z  
**Authority:** outcome-blind source/interface research only. No new-family reference alignment, gold outcome, comparator result, performance table, test, build, or runtime was used.

## Result

Three exact slot candidates are now source-bound:

| V4 slot | Candidate | Exact source identity | Code licence | Identity terminal |
|---|---|---|---|---|
| K1 | AgreementMakerLight v3.2 | `AgreementMakerLight/AML-Project@d54a6650818d3474fe36090c2bc7dfe5bf4dfcb6` | Apache-2.0, licence SHA-256 `c71d239d…` | `PUBLIC_V4_K1_AML_IDENTITY_BOUND__HISTORICAL_RUNTIME_DEVIATION_REPLAY_REQUIRED` |
| K2 | LogMap 4.0 source | `ernestojimenezruiz/logmap-matcher@b3b57d0d8bfb5872bdffb49329d764acb4735713` | Apache-2.0, licence SHA-256 `6375b618…` | `PUBLIC_V4_K2_LOGMAP_IDENTITY_BOUND__SOURCE_BUILD_RUNTIME_AND_SELECTIVE_ADAPTER_UNEXECUTED` |
| K3 | BERTMap in DeepOnto 0.9.3 | `KRR-Oxford/DeepOnto@74ca8d47f01bad0b8739f19ee2c392bdf6d9c090` | Apache-2.0, licence SHA-256 `340ebaff…` | `PUBLIC_V4_K3_BERTMAP_IDENTITY_BOUND__NO_GOLD_ROUTE_EXISTS__ENVIRONMENT_MODEL_SEED_RUNTIME_AND_SELECTIVE_ADAPTER_UNEXECUTED` |

The exact machine-readable identities, paper versions, licence hashes, entrypoints, native artifacts/errors, rights boundaries, and information/action/resource envelopes are in [COMPARATOR_RESEARCH.json](./COMPARATOR_RESEARCH.json).

This does **not** certify that these are performance winners. Performance inspection was forbidden, so the protocol word *strongest* remains unresolved:

`PUBLIC_V4_STRONGEST_COMPARATOR_SELECTION_CANNOT_CHECK__PERFORMANCE_WAS_OUT_OF_SCOPE`

No comparator is V4 execution-ready:

`PUBLIC_V4_COMPARATOR_IDENTITY_CANNOT_CHECK__EXACT_CANDIDATES_BOUND_BUT_STRONGEST_SELECTION_RUNTIME_FAMILY_SUPPORT_AND_INFORMATION_EQUIVALENT_SELECTIVE_ADAPTERS_UNFROZEN`

## The key semantic constraint

Ontology matchers normally emit **positive alignment rows**. That is not a complete binary GLUE/OBSTRUCTION decision rule.

For every frozen family-specific candidate pair:

1. A valid native **equivalence** row may become `{GLUE}` only under a pre-outcome-frozen relation, confidence, duplicate, parser, and success policy.
2. **Nonselection is never OBSTRUCTION.** It becomes `{GLUE,OBSTRUCTION}`.
3. Subsumption, relatedness, an unknown relation, a missing row, an empty artifact, an exception, or timeout does not prove obstruction.
4. `{OBSTRUCTION}` requires an independently machine-checkable input-native disjointness/contradiction certificate under the frozen reasoner profile.
5. Error, timeout, missing or partial artifact, or unsupported syntax is `CANNOT_CHECK`, never an empty alignment.

This enforces the same binary reference semantics and a complete family-specific scoring universe. Merely binding a runnable matcher is insufficient.

There is a second, logically prior blocker: comparator harm needs a **lawful explicitly exhaustive binary truth universe**. A positive-only or partial OAEI reference alignment does not make every absent cell an obstruction. A predecessor-only coordination receipt reports 1,399 GLUE assignments versus 116,515 assignments created as OBSTRUCTION from absence from positive reference cells. V4 forbids that join semantics; those 116,515 assignments cannot be reused as binary truth.

The parallel source-rights lane reports 0/7 eligible families. Its exact receipts are `SOURCE_FAMILY_RIGHTS.json` SHA-256 `8ebaf13247fb8ebf7e4aa14da925f6793290aa3bf29f100fbe36e0c7fcf5e3e8` and `SOURCE_FAMILY_RIGHTS.md` SHA-256 `6b9e5932539abffe77c8dffe99766f069c3b15e235b59d6c057901e88e535761`. No audited track metadata licenses reference absence as a negative label; Knowledge Graph and Common Knowledge Graph are explicitly partial. Therefore the family panel cannot freeze and comparator harm remains unavailable even if a runtime is reproduced:

`PUBLIC_V4_BINARY_REFERENCE_EXHAUSTIVITY_CANNOT_CHECK__POSITIVE_REFERENCE_ABSENCE_IS_NOT_OBSTRUCTION`

## K1 — AML v3.2

- Paper: *The AgreementMakerLight Ontology Matching System*, published ISWC 2013, [DOI 10.1007/978-3-642-41030-7_38](https://doi.org/10.1007/978-3-642-41030-7_38).
- Release identity: tag `v3.2`, commit `d54a6650818d3474fe36090c2bc7dfe5bf4dfcb6`.
- Release SHA-256: `7855c2d8efa131f012595313814a6466ad48f4e7ba26906c4f54801cd5a21f27`.
- JAR SHA-256: `a5b831a6c000e49aa4702b16486dabdf38e40bb68203a16a8019414fecc2ecf3`.
- Entrypoint: `java -jar AgreementMakerLight.jar -s SOURCE -t TARGET -o OUTPUT -a`.
- Named upstream runtime: Java 8.

The inherited V3 facts remain historical only: AML produced artifacts for 19/20 inputs, test 206 had a parser failure, and execution used OpenJDK 17.0.19 arm64 rather than Java 8. Those facts are **not** new performance evidence. A Java-8 identity replay and artifact validation are still required.

## K2 — LogMap, with LogMapLt sensitivity

- Paper: *LogMap: Logic-Based and Scalable Ontology Matching*, published ISWC 2011, [DOI 10.1007/978-3-642-25073-6_18](https://doi.org/10.1007/978-3-642-25073-6_18).
- Official source: [`ernestojimenezruiz/logmap-matcher`](https://github.com/ernestojimenezruiz/logmap-matcher), commit `b3b57d0d8bfb5872bdffb49329d764acb4735713`.
- Build: manually install the repository-named Google translation JAR dependency, then `mvn package` or `mvn clean install`; colocate `parameters.txt` and `java-dependencies` with `logmap-matcher-4.0.jar`.
- Eligible no-gold mode: `MATCHER`, never `EVALUATION`.
- Entrypoint: `java -Xms500M -Xmx25G -DentityExpansionLimit=10000000 --add-opens=java.base/java.lang=ALL-UNNAMED -jar logmap-matcher-4.0.jar MATCHER SOURCE_IRI TARGET_IRI OUTPUT_DIR false`.
- Native output: `logmap_mappings` files including OAEI RDF, with relation/direction/type/confidence.
- Error trap: the CLI catches `Exception` and prints help, so an adapter must validate the expected artifact; exit status alone is inadequate.

The official MELT wrapper is pinned at `ernestojimenezruiz/logmap-melt@e891cea083cf5660776a59cc1f06578acc8ca229`, but its POM uses `master-SNAPSHOT` and `openjdk:8-jre-alpine`. It is provenance, not a reproducible runtime until dependency and image digests are frozen.

LogMapLt is available from the same source with `LITE SOURCE TARGET OUTPUT_DIR`. Its paper identity is *LogMap family results for OAEI 2014* ([CEUR-WS Vol-1317 paper 4](https://ceur-ws.org/Vol-1317/oaei14_paper4.pdf)). It is a same-family sensitivity arm, not independent replication.

## K3 — BERTMap through maintained DeepOnto

- Primary paper: *BERTMap: A BERT-Based Ontology Alignment System*, [arXiv:2112.02682v4](https://arxiv.org/abs/2112.02682v4), [AAAI DOI 10.1609/aaai.v36i5.20510](https://doi.org/10.1609/aaai.v36i5.20510).
- Canonical paper repository: `KRR-Oxford/BERTMap@ce848402b40e2f9513bf2d004894d3f82635022c`.
- Official maintained implementation: `KRR-Oxford/DeepOnto@74ca8d47f01bad0b8739f19ee2c392bdf6d9c090`, package version 0.9.3. DeepOnto's companion paper is [DOI 10.3233/SW-243568](https://doi.org/10.3233/SW-243568).
- Install template: `pip install git+https://github.com/KRR-Oxford/DeepOnto.git@74ca8d47f01bad0b8739f19ee2c392bdf6d9c090`.
- Entrypoint: `python scripts/bertmap.py -s SOURCE -t TARGET -c FROZEN_CONFIG.yaml`.
- No-gold requirements: `known_mappings: null`, `auxiliary_ontos: []`, no automatic reference-based validation, and all thresholds/annotation properties/seeds/devices frozen.
- Native outputs: raw, extended, filtered, and repaired mapping TSVs, plus raw JSON, corpora, checkpoints, configuration and logs.

The default pretrained model can be bound as `emilyalsentzer/Bio_ClinicalBERT@d5892b39a4adaed74b92212a44081509db72f87b`. Its card licence is MIT; licence SHA-256 is `9e8f4211…`, and `pytorch_model.bin` is 435,778,770 bytes with LFS SHA-256 `a18c4c26…`. It must be materialized locally at that revision; a moving Hub name is not admissible.

BERTMap still needs a locked Python/JVM/PyTorch environment, deterministic seed/device policy, resource ceilings, a single predeclared output stage, family support, and end-to-end execution. Identity alone is not a result.

## Newer hybrid identity retained but not promoted

LogMapLLM is source-bound at `city-artificial-intelligence/logmap-llm@d26f8c262ca2b12651094c5223070bfd72387832`, Apache-2.0. Its paper is [arXiv:2508.08500v2](https://arxiv.org/abs/2508.08500v2) / [EACL 2026 long paper 110](https://aclanthology.org/2026.eacl-long.110/).

It is not promoted into K3 because the integrated repository is still a work-in-progress source pipeline rather than a locked package: provider, model revision, API terms, retention, token/dollar ceiling, concurrency, timeout/retries, and environment are not frozen. Its hosted-model priors and ontology-context prompts also are not information-equivalent to the other arms unless explicitly disclosed and given to candidate and ideal under the same manifest.

`PUBLIC_V4_LOGMAPLLM_SOURCE_IDENTITY_BOUND__WIP_INSTALL_PROVIDER_MODEL_COST_RIGHTS_AND_INFORMATION_EQUIVALENCE_CANNOT_CHECK`

## Not forced

No unique primary-paper-linked official repository/licence/entrypoint for a matcher called **Matcha** was established in this bounded audit. The name remains:

`PUBLIC_V4_MATCHA_PRIMARY_SOURCE_IDENTITY_CANNOT_CHECK`

MELT is separately bound as execution/controller infrastructure at `dwslab/melt@db893731fdf29371603847e3664dc18b80d45d4b`, MIT licence SHA-256 `6259170d…`, paper [DOI 10.1007/978-3-030-33220-4_17](https://doi.org/10.1007/978-3-030-33220-4_17). MELT transports and filters alignments; it does not itself certify GLUE or OBSTRUCTION.

## Exact next discriminator

Before opening any new-family reference alignment, freeze and hash:

1. family-specific binary candidate universes and relation normalization;
2. lawful explicitly exhaustive binary reference semantics—never fill an absent positive-reference cell as obstruction;
3. family syntax/support matrix for AML, LogMap and BERTMap;
4. dependency containers, Java/Python/GPU identities, model/resource bytes and licences;
5. timeout, retry, seed, device and resource ceilings;
6. native artifact parsers, completeness checks and one selected BERTMap output stage;
7. positive-only selective adapters with nonselection mapped to the full envelope;
8. the candidate/ideal information-equivalence manifest; and
9. every prediction digest before outcome custody is released.

Until then, comparator harm, coverage, noninferiority and superiority are all `CANNOT_CHECK`.
