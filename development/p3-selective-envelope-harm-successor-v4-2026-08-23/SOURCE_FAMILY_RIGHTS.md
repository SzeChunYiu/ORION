# P3 V4 source-family provenance, rights, and public-panel feasibility

**Protocol:** `P3.PUBLIC.OAEI.SELECTIVE.ENVELOPE.HARM.SUCCESSOR.DEV.V4`  
**Audit:** `P3.V4.SOURCE.FAMILY.RIGHTS.METADATA_ONLY.2026-08-23`  
**Cutoff:** 2026-08-23T15:26:29Z  
**Authority:** public-development source feasibility only; not legal advice and not confirmatory evidence.

## Outcome-blind boundary

This audit opened official landing pages, licence/README metadata, Git reference identities, and selected archive **HTTP HEAD** metadata only. It did **not** open any OAEI reference alignment, relation value, gold label, ontology entity body, KG/data payload, matcher output, or task outcome. It did not execute a matcher.

A crucial negative constraint is preserved: corpus-level variation in source names, ontology/KG families, languages, or referent identifiers is **not** evidence that comparable cases exercise both binary outcomes. Within-case binary separability remains `CANNOT_CHECK` for all seven candidates because metadata alone does not establish it.

## Decision

| Quantity | Result |
|---|---:|
| Candidate OAEI track families audited | 7 |
| Official track-page identities bound | 7 |
| Track pages containing a literal `license`/`licence` token | 0/7 |
| Track pages containing a literal `checksum`/`sha256` token | 0/7 |
| Explicit reference-alignment licences bound | 0/7 |
| Published cryptographic dataset checksums bound | 0/7 |
| Families satisfying the complete V4 source gate | **0/7** |
| Minimum independent families required | 3 |

The source-lineage **upper bound** is five after two definite collapses: Anatomy/LargeBio share NCI Thesaurus, and MultiFarm is a translation derivative of Conference/OntoFarm. Five is not an eligibility or independence claim. Rights, immutable bytes, exact releases, within-case separability, and gold-construction independence are unresolved.

**Terminal:** `PUBLIC_V4_SOURCE_RIGHTS_CANNOT_CHECK__PUBLIC_V4_SOURCE_FAMILY_DISJOINT_REPLICATION_CANNOT_CHECK`

**Panel terminal:** `P3_V4_PROSPECTIVE_SOURCE_FAMILY_DISJOINT_PUBLIC_PANEL_CANNOT_FREEZE__ZERO_OF_SEVEN_FULL_RIGHTS_IMMUTABILITY_RECORDS`

## Decisive binary-semantics gate

V4 forbids transporting V3's closed-world convention. In the already-open V3 predecessor—not in any new family—`p3_cross_construct_successor.py` lines 526–535 assigned `OBSTRUCTION` whenever a pair was inside the reference entity domains but absent from the positive equivalence/nonexpressible cells. The inherited public join receipt therefore contains 1,399 `GLUE` versus 116,515 absence-derived `OBSTRUCTION` cases. This is a semantic construction, not source-grounded negative truth.

For V4, absence may count as `OBSTRUCTION` only when authoritative pre-outcome metadata declares the reference **exhaustive over the frozen candidate universe** and declares absence a valid binary negative. **Zero of seven** audited track pages does so. Conference's “complete alignment space” refers to the 21 ontology-pair test cases among seven ontologies, not exhaustive entity-pair labels. Knowledge Graph and CommonKG explicitly describe partial gold, making closed-world absence especially invalid. All seven therefore have `binary_obstruction_semantics = CANNOT_CHECK` independently of the rights blockers.

**Semantics terminal:** `PUBLIC_V4_BINARY_OBSTRUCTION_SEMANTICS_CANNOT_CHECK`

## Family matrix

| Candidate | Official release identity and advertised scope | Input rights | Reference rights / immutable bytes | Dependence | Comparator runtime feasibility | Terminal |
|---|---|---|---|---|---|---|
| Anatomy | OAEI 2025; `anatomy_track` / `anatomy_track-default`; 2 ontologies, 1 task | Current MA and NCIt OBO editions advertise CC BY 4.0, but the OAEI archive is not mapped to those exact upstream revisions | No explicit reference licence; no published cryptographic archive checksum; HTTP ETag only | Shares NCI with LargeBio; one fixed pair gives no family replication | MELT/TDRS adapter path declared; execution and budget not verified | `PUBLIC_V4_SOURCE_RIGHTS_CANNOT_CHECK` |
| Conference | OAEI 2025; `conference` / `conference-v1`; 16 ontologies, 7 in crisp reference, 21 reference cases, 120 possible pairs | OAEI and OntoFarm pages provide no explicit ontology-collection licence | No reference licence; “cite the paper” is not a licence; no cryptographic checksum | One OntoFarm collection despite heterogeneous source inspirations; parent of MultiFarm | MELT/TDRS path declared; small-scale execution plausible but unverified | `PUBLIC_V4_SOURCE_RIGHTS_CANNOT_CHECK` |
| MultiFarm | OAEI 2025; `multifarm` / `[pair-language]-v2`; page advertises 45 language pairs and 25 alignments per pair | Mannheim page permits scientific use in prose but gives no standard redistribution/modification licence and contains a legacy permission warning for raw translations | No reference licence or byte digest; no direct 2025 archive identity | Translations of seven OntoFarm seeds; languages/pairs are not independent families; collapse with Conference | MELT/TDRS path declared; exact release and 45-suite cost unverified | `PUBLIC_V4_SOURCE_RIGHTS_CANNOT_CHECK` |
| LargeBio | Legacy OAEI 2015; `largebio`; 3 source ontologies, 6 base small/whole tasks plus flagged variants; current OAEI says Bio-ML supersedes it | Current FMA advertises CC BY 3.0 and NCIt CC BY 4.0, but legacy snapshot mapping is absent; SNOMED CT requires licensing | UMLS reference requires an individual licence/UTS account and carries source-vocabulary restrictions; no archive digest | All tasks share ontologies/UMLS construction; shares NCI with Anatomy | Legacy SEALS coordinate; whole tasks are very large; current runtime and entitlements unresolved | `PUBLIC_V4_SOURCE_RIGHTS_CANNOT_CHECK` |
| Biodiv | OAEI 2025; 4 ontologies, 2 references: ENVO–SWEET and NCBI Taxonomy–TAXREF-LD | Current upstream metadata: ENVO CC0, SWEET CC0, OBO NCBITaxon CC0, TAXREF-LD CC BY 3.0 France; none is mapped to exact OAEI bundle revisions | Reference licences absent; bundle has no checksum and advertised URL returned HTTP 404 | Two metadata-distinct source pairs may be future clusters, but the frozen candidate is one track and exact provenance is absent | Page claims MELT support but gives no suite/version coordinate; archive is unavailable | `PUBLIC_V4_SOURCE_RIGHTS_CANNOT_CHECK` |
| Knowledge Graph | OAEI 2025; `knowledgegraph` / `v4`; `TrackRepository.Knowledgegraph.V4`; 8 table-listed KGs, 5 cases, 497,607 advertised instances | Per-wiki Fandom content and DBkWik-derived-dump rights are not bound at exact revisions | Expert schema gold and External-links instance gold have no explicit licence; no dataset checksum | Three franchise clusters share Fandom hosting, DBpedia extraction, and OAEI gold construction | MELT path declared; instance+schema scale is high; resource envelope unverified | `PUBLIC_V4_SOURCE_RIGHTS_CANNOT_CHECK` |
| Common Knowledge | Last listed OAEI 2023; `commonkg`; NELL–DBpedia v1 and YAGO–Wikidata v1/full+small | Exact upstream KG revisions are not named; both primary linked repositories lack a root licence at pinned default heads | Reference licences and release checksums absent | Small YAGO–Wikidata is nested in full; DBpedia/YAGO/Wikidata share world-knowledge/Wikipedia lineage | MELT path declared; up to 5.15M advertised YAGO instances; budget unverified | `PUBLIC_V4_SOURCE_RIGHTS_CANNOT_CHECK` |

## Exact release and availability receipts

The archive bytes were not downloaded. These are non-cryptographic HTTP HEAD observations only:

- Anatomy: `https://oaei.ontologymatching.org/2025/anatomy/anatomy-dataset.zip` — 200, 329,860 bytes, ETag `"6920bb78-50884"`, Last-Modified `Fri, 21 Nov 2025 19:20:24 GMT`.
- Conference inputs: `https://oaei.ontologymatching.org/2025/conference/data/conference.zip` — 200, 55,387 bytes, ETag `"6920bb78-d85b"`.
- Conference reference: `https://oaei.ontologymatching.org/2025/conference/data/reference-alignment.zip` — 200, 16,852 bytes, ETag `"6920bb78-41d4"`.
- LargeBio: `https://oaei.ontologymatching.org/2015/largebio/LargeBio_dataset_oaei2015.zip` — 200, 17,046,198 bytes, ETag `"69e24df3-1041ab6"`.
- Biodiv: `https://upload.uni-jena.de/data/68b028e813c9c3.77183112/biodiv.zip` — **404** at the audit cutoff.

An HTTP ETag is not accepted as a provider-published cryptographic identity. MultiFarm and the two KG tracks expose repository/version coordinates rather than a provider-published SHA-256 in their track pages.

## Rights findings by input/reference

### Anatomy

The exact OAEI snapshot-to-upstream link is missing. Current upstream metadata is encouraging but does not by itself license the unidentified archive/reference bytes:

- Adult Mouse Anatomy: `https://obofoundry.org/ontology/ma.html`, CC BY 4.0; current repository head `5cd7d03b30c520c1ef535faf747c9e6344307eea`.
- NCIt OBO edition: `https://obofoundry.org/ontology/ncit.html`, CC BY 4.0; current repository head `c410c6f4cbff2b7b08645d539a295bed82bd100b`.
- The reference page attributes creation/improvement but contains no explicit reference-alignment licence.

### Conference and MultiFarm

Conference inputs have heterogeneous inspirations (web, tool, insider) but are one OntoFarm collection. The OntoFarm page at `http://owl.vse.cz/ontofarm/` yielded no explicit licence. Conference’s citation request does not grant reuse rights for the reference archive.

The MultiFarm source page at `https://web.informatik.uni-mannheim.de/multifarm/` says the dataset can be used for scientific purposes. This limited prose is not a complete standard licence for redistribution/modification, and the same historical page warns against using then-unfinished raw translations without permission. MultiFarm is explicitly derived from OntoFarm, so neither languages nor language pairs add source-family replication.

### LargeBio

LargeBio is not an unrestricted public panel:

- FMA current upstream metadata: CC BY 3.0, but the 2015 OAEI snapshot is unidentified.
- NCIt current upstream metadata: CC BY 4.0, but the 2015 OAEI snapshot is unidentified.
- SNOMED International states that licensing/registration applies and charges can apply outside member territories: `https://www.snomed.org/get-snomed`.
- NLM states that UMLS licences are issued to individuals, a UTS account is required, and redistribution/source-vocabulary restrictions apply: `https://www.nlm.nih.gov/databases/umls.html`.

The UMLS-derived reference cannot be treated as open merely because the legacy OAEI archive is reachable.

### Biodiv

Current upstream licence metadata is identifiable:

- ENVO — CC0 1.0; current head `a2455d1a77e46bb8a664d65a157166b539269042`.
- SWEET — CC0 1.0; current head `db60c8ddb1b781fbadae176f69286a2cdd5099a0`.
- OBO NCBITaxon — CC0 1.0; current head `91117dcdde2ab5219d9a7ef786e89468337cb761`.
- TAXREF-LD — CC BY 3.0 France; current head `7cc1614eb22fec028ac5f1891d5b52d5f67f4d0e`.

But the OAEI page does not name the bundled upstream versions, the two reference licences are absent, and its current archive link is dead. Thus even the best upstream-rights candidate cannot be frozen.

### Knowledge Graph and Common Knowledge

Knowledge Graph v4 is reproducibly named at the MELT coordinate level, but exact per-wiki content rights, DBkWik derived-dump rights, expert schema-gold rights, and instance-gold rights are not bound. The track’s partial-gold declaration is a scoring caveat, not a licence.

CommonKG links two GitHub repositories:

- `https://github.com/OmaimaFallatah/KG_GoldeStandard` at `c2b9f8903e11f5cffa353dfdad3e8685fb04d631`.
- `https://github.com/OmaimaFallatah/YagoWikiData` at default HEAD `081f4af7c445f29b5bb3f6b35b26293982f5774d` (an additional `main` ref exists at `1547e850f7ee2986ad406e640559dc94e8539381`).

Neither pinned default head exposes a root `LICENSE*`; neither has a provider-published dataset checksum. Known upstream terms cannot be transported to unidentified derived subsets and gold alignments without exact version/attribution receipts.

## Family-disjointness graph

Definite collapses:

1. `OAEI_ANATOMY` ↔ `OAEI_LARGEBIO`: shared NCI Thesaurus, plus common biomedical lineage.
2. `OAEI_CONFERENCE` → `OAEI_MULTIFARM`: MultiFarm is a systematic translation derivative of OntoFarm.
3. CommonKG `yago-wikidata-v1-small` is nested within `yago-wikidata-v1` and has zero extra replication value.

Unresolved, not credited as independent:

- Biodiv’s ENVO–SWEET and NCBI–TAXREF-LD pairs are source-distinct in metadata, but the frozen protocol names one track family and exact references/releases are missing.
- Knowledge Graph’s Star Wars, Marvel, and Star Trek groups share platform, extractor, and gold-construction process.
- CommonKG’s two pairs use overlapping world-knowledge lineages; the track does not supply an independence design.
- Knowledge Graph and CommonKG use different named sources, but independence of their outcome-generating processes is not established by landing-page metadata.

## Runtime feasibility boundary

MELT itself is source-available at `https://github.com/dwslab/melt`, audited HEAD `db893731fdf29371603847e3664dc18b80d45d4b`, MIT licence SHA-256 `6259170d9437ff0c01c2441c5ba08b032c6e98bb4db90f31de295c27054e64cd`.

An OAEI suite coordinate establishes only an adapter path. It does not establish lawful byte access, source-native comparator compatibility, time/memory completion, or the V4 same-information interface. Anatomy/Conference are plausibly small-to-moderate; MultiFarm repeats 45 language suites; LargeBio, Biodiv taxonomy, Knowledge Graph, and CommonKG require explicit high-resource envelopes. No comparator was run here.

## Metadata byte receipts

These SHA-256 values identify only the metadata/licence pages retrieved at the cutoff—not dataset bytes:

| Metadata | URL | SHA-256 |
|---|---|---|
| OAEI 2025 campaign | `https://oaei.ontologymatching.org/2025/` | `32257493783d8b1882e8e4cc27134643d58ffb2d92637d32eeb326fce81ca1cc` |
| Anatomy 2025 | `https://oaei.ontologymatching.org/2025/anatomy/index.html` | `343757752ffa22843418ae49a11015867938f99410a4060b509b0d4f4bd5d349` |
| Conference 2025 | `https://oaei.ontologymatching.org/2025/conference/index.html` | `697a21c9d3317bffb65b9dc47ff18f1da308019832bf16219fae7e00c7ac3dbb` |
| MultiFarm 2025 | `https://oaei.ontologymatching.org/2025/multifarm/index.html` | `bb822022298fdd170b59e8027361bd8193c02cccf47469d125b6a59fce5e3201` |
| MultiFarm source page | `https://web.informatik.uni-mannheim.de/multifarm/` | `aea5acefdf37f79bd9b48e526987d332eb62c9a420020759c01f1917bdcfe009` |
| OntoFarm page | `http://owl.vse.cz/ontofarm/` | `b268a3789454b57417e2d72eeeb0b4cff60da13de47d9eead7f2a145c8b9ef96` |
| LargeBio 2015 | `https://oaei.ontologymatching.org/2015/largebio/` | `b400c23516ddd955d5fe055e6d11505a98697d3ce47ec03e051c9ae3810e321c` |
| Biodiv 2025 | `https://oaei.ontologymatching.org/2025/biodiv/index.html` | `69fb45264593daf2dc55e98695dcb80555b92c3494196b4fb113492b8bbcb1c5` |
| Knowledge Graph 2025 | `https://oaei.ontologymatching.org/2025/knowledgegraph/index.html` | `07ebb8e7e55d23ac068e39511ffb9db0fadf82c6b2d4ede760d8ade40d000c83` |
| CommonKG 2023 | `https://oaei.ontologymatching.org/2023/commonKG/index.html` | `1b5bd7791dca6cd191a19df75c60f4c76929cf794f4f9825705bf2c6def2067c` |
| MA OBO metadata | `https://obofoundry.org/ontology/ma.html` | `44e2e29aa6de3ece01f23363630fae33aadb910d9cb6c32f4e7307d37e283b03` |
| NCIt OBO metadata | `https://obofoundry.org/ontology/ncit.html` | `81eba8cb5f3fefba48e4e3ebbf76350bd188fdcd3dcccf49605b1082bec4e0db` |
| FMA OBO metadata | `https://obofoundry.org/ontology/fma.html` | `2dae236e1bac8da2cbf62d33ffde2c17af5d9bcec018f6440a1ef7ed520b04af` |
| ENVO OBO metadata | `https://obofoundry.org/ontology/envo.html` | `057670ec1c84947fffdf7e0bab60b625632aa82f102e9daaa81f5a1a489127c8` |
| NCBITaxon OBO metadata | `https://obofoundry.org/ontology/ncbitaxon.html` | `54184a999a7c1a6aebba413509478716854a7a5514e17c3c8f4bfeef439925d2` |
| SWEET CC0 licence bytes | `https://raw.githubusercontent.com/ESIPFed/sweet/master/LICENSE` | `8da08cd0b610f92886cf7fe0f137c4ba6bacefc8185b5add37e3ba540e286756` |
| TAXREF-LD README/licence metadata | `https://raw.githubusercontent.com/frmichel/taxref-ld/master/README.md` | `a475d9ce4f4f43c0341edf23a5d15a658cec97171626b7ef0e38d44621f3fb70` |
| UMLS licence/access page | `https://www.nlm.nih.gov/databases/umls.html` | `aba832cd75916fae0c2143d057a92911ae3cb973b28d75afb30d336923471707` |
| SNOMED access/licensing page | `https://www.snomed.org/get-snomed` | `80a41b91b60d51c6b8a2946d00a9339bd29766239bf895e29ed888d5991afbc7` |
| MELT MIT licence bytes | `https://raw.githubusercontent.com/dwslab/melt/master/LICENSE` | `6259170d9437ff0c01c2441c5ba08b032c6e98bb4db90f31de295c27054e64cd` |

## Exact remediation needed before any reference access

1. Obtain provider-published or independently computed **pre-outcome** SHA-256 values for every selected input and reference artifact.
2. Bind each OAEI ontology/KG byte set to an exact upstream version and its licence/attribution obligations.
3. Obtain explicit reuse permission for every reference alignment and derived bundle; do not infer it from public downloadability or citation prose.
4. Freeze source-lineage clusters that collapse shared ontologies, translations, nested subsets, and shared gold construction.
5. Obtain authoritative per-family metadata that the reference is exhaustive over the frozen candidate universe and that absence is a valid negative; otherwise `OBSTRUCTION` remains `CANNOT_CHECK`.
6. Freeze lawful MELT/SEALS coordinates or local bundles plus comparator time, memory, tool, error, and timeout policies.
7. Freeze the candidate universe and predictions before opening any new-family reference artifact.
8. Only after those receipts exist may the lane inspect whether a family actually supplies binary-scorable cases, both outcomes within comparable strata, nontriviality, coverage, or harm.

Until then, no positive V4 source-family or performance claim is licensed.
