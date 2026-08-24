# Public empirical-data binding audit for P1, P2, P3 and P5

**Date:** 2026-08-23

**Authority:** public-source metadata, licence and file-identity preflight only

**Excluded:** P4, manuscript edits, dataset-row inspection, protected outcomes,
empirical execution, pytest and CI

## Decision

Public data can materially improve the *substrate* of all four papers, but it
does not presently resolve any paper's registered empirical endpoint.

- **Paper-level empirical blockers closed:** **0/4**.
- **Paper-level empirical blockers still open:** **4/4**.
- **Actually closed:** immutable identities for several public sources; explicit
  content-class licences for some sources; several public label schemas; and one
  or more runnable donor toolkits per relevant task family.
- **Not closed:** eligibility for any registered wide panel, protected
  freshness/custody, a complete comparator family, or any prospective outcome.

The scientific terminal is:

`PUBLIC_SOURCE_SUBSTRATE_PARTIALLY_BOUND__NO_PAPER_LEVEL_EMPIRICAL_BLOCKER_CLOSED`

This is not a semantic retreat. It identifies the strongest public substrate
available online and makes the remaining gap sharper: public labels are usually
already visible, while the papers require protected decisions, fresh transfer,
owner-separated custody and endpoint-preserving comparator adapters.

## Exact endpoints audited

| paper | governing prospective endpoint | local authority |
|---|---|---|
| P1 | Minimal licensed scientific transition from noisy natural evidence, with protected recovery/utility, no excess broad rewrite, preservation and dependency-impact gates, versus nine arms in two source-disjoint waves (896 clusters). | `research/claim_expansion/p1/gpt_r7/R7A_MAXT_POWER_AMENDMENT_V2.json` |
| P2 | Paired task-world gold-recall success without false inclusion across four source-disjoint arenas under identical query/provider/budget/scoring exposure, independent obligation custody and three comparators (768 clusters). | `papers/paper-02-open-world-scientific-discovery/protocol/P2_TASK_WORLD_SUCCESSOR_V2.json` |
| P3 | Floor-adjusted avoidable false merge or downstream decision harm with nonzero referent, construct, measurement and temporal-context variation, raw-text attack, protected gold and four comparators (768 clusters). | `papers/paper-03-global-knowledge-portrait/protocol/P3_PARTIAL_IDENTIFICATION_SUCCESSOR_V1.json` |
| P5 | Correct minimal revision with preservation and protected fresh-transfer success across eight revision classes and eight domains, versus six arms with non-compensatory harm gates (768 clusters). | `papers/paper-05-self-orion/protocol/P5_WIDE_REVISION_LEVEL_SUCCESSOR_V1.json` |

The exact protocol payload hashes are recorded in
`PUBLIC_SOURCE_BINDINGS.json`; the local files are pinned again in
`SOURCE_REQUIREMENTS_SHA256SUMS`.

## P1: naturalistic transition transport

### Strongest public candidates

| source | bytes and licence | useful label | exact mismatch |
|---|---|---|---|
| [SWE-bench Multilingual at `846e647…`](https://huggingface.co/datasets/SWE-bench/SWE-bench_Multilingual/tree/846e647b9f33c0b51b739d005d13d85493c9af09) | One Parquet object pinned by LFS SHA-256; dataset card says MIT; 300 issue--PR tasks. | Natural issue, patch and unit-test transition in 41 repositories and nine languages. | Gold patch/test fields are public; no protected causal responsibility, minimal scientific layer, preservation/reopen authority, mixed-fibre eligibility, or non-software domains. |
| [Defects4J at `8c16da8…`](https://github.com/rjust/defects4j/tree/8c16da8230843cdc918eaf4ddb449637f02b83c6) | Commit/tree and MIT `license.txt` bytes pinned. | Reproducible buggy/fixed revisions and triggering tests; README reports 854 active bugs plus deprecated history. | Reproducible code repair is not a protected responsibility-to-scientific-transition label. |
| [PeerRead adapter at `53e1932…`](https://huggingface.co/datasets/allenai/peer_read/tree/53e19322c88bb01c1b0c6a61bde68bc2b1c3028e) | Builder/card pinned; licence is explicitly `unknown`; canonical repository has no root licence file at the pinned commit. | Reviews, histories and acceptance fields make it a plausible scientific-review modality. | Rights are `CANNOT_CHECK`, and acceptance/review is not minimal revision responsibility or authority gold. |

### What this closes

It closes only the claim that no pinned public real-world transition substrate
exists. It does **not** close P1's 896-cluster case frame, protected labels,
four-domain/provider/modality eligibility, two-wave custody, or nine lawful R7
comparator adapters. [SWE-agent at `3ea751c…`](https://github.com/SWE-agent/SWE-agent/tree/3ea751c087f32b16e039a2233dd6eefecef325d5)
is an MIT-licensed runnable issue solver, but its native interface is not R7's
dossier/action/responsibility terminal.

## P2: acquisition plus earned closure

### Strongest public candidates

| source | bytes and licence | useful label | exact mismatch |
|---|---|---|---|
| [SYNERGY Dataverse V1](https://doi.org/10.34894/HE6NAQ) | Released version 1.0; CC0-1.0; 144 provider-identified files with SHA-1 checksums. | Twenty-six systematic-review worlds, 169,288 works, inclusion labels and eligibility criteria; 26 `labels.csv` identities are bound. | Bounded screening pools are not live open-web route worlds; labels are public; provider exposure, route cost, future optionality and closure authority are absent. |
| [Zenodo `10423427`](https://zenodo.org/records/10423427) | CC BY 4.0; one 53,881,052-byte CSV pinned by MD5. | 25,540 deduplicated citation records labelled include/exclude by two reviewers for a physiotherapy review update. | One review is one bounded arena, not four source-disjoint open-world arenas or independent protected obligation custody. |
| [SciFact adapter at `1fe5466…`](https://huggingface.co/datasets/allenai/scifact/tree/1fe54665deee011033b2dd98db5752e0d586fdfb) | Builder/card pinned. Canonical source assigns claims/annotations CC BY 4.0, abstracts ODC-By 1.0 and code Apache-2.0, while the Hugging Face card says CC BY-NC 2.0. | Scientific claims, evidence documents and evidence labels; original test gold is provider-held. | Licence handling must be content-class specific; the S3 `latest` payload is not an immutable data revision; claim verification is not open-world acquisition/closure. |

The licence statements above come from the pinned canonical
[SciFact `LICENSE.md`](https://raw.githubusercontent.com/allenai/scifact/68b98a56d93e0f9da0d2aab4e6c3294699a0f72e/LICENSE.md)
and the pinned Hugging Face card. The difference is retained rather than
silently collapsed to the more permissive reading.

### What this closes

P2 now has concrete licensed naturalistic *bounded screening* sources and an
outcome-blind four-file SYNERGY preflight in
`MINIMAL_SAMPLING_MANIFESTS.json`. It also has a pinned Apache-2.0 runnable
[ASReview](https://github.com/asreview/asreview/tree/1788bc97ff5b5652dbe1e5b5ad5253bef1b03aef)
donor candidate. ASReview prioritizes and simulates screening; it does not
natively emit P2's three-valued task-closure authority or matched provider,
route and cost trace. Thus the four-arena paper endpoint remains open.

## P3: source-compatible portrait coverage and harm

### Strongest public candidates

| source | bytes and licence | useful label | exact mismatch |
|---|---|---|---|
| [CRAFT Shared Task 2019, Zenodo `3460908`](https://zenodo.org/records/3460908) | CC BY-NC-SA 3.0; training, test and evaluation-gold archives pinned by size and MD5. | Biomedical full text, ontology concept annotation, coreference tokens and separately packaged evaluation gold. | One biomedical corpus; gold is public; no four-domain/source-disjoint frame, all-four-coordinate opportunity audit, set-valued portrait envelope or downstream loss. |
| [SciREX at `7daad66…`](https://github.com/allenai/SciREX/tree/7daad660fe94f504433590b7a781cfabe1e179c6) | Apache-2.0 repository; the 7,318,844-byte release archive is HEAD-pinned at the commit with a strong HTTP ETag. | Method/metric/task/material/score relations and coreference over scientific papers. | Its README reports that about half of relations contain an entity with no retained mention; end-to-end observation coverage is therefore adverse. Underlying article-text rights still need a per-content-class audit. |
| [OAEI 2004 benchmark, Zenodo `15827226`](https://zenodo.org/records/15827226) | CC BY 4.0; 486,043-byte archive pinned by MD5. | Ontologies plus reference alignments. | Systematic alterations of one bibliographic seed are a useful control, not a naturalistic multi-domain raw-text atlas. |

### What this closes

P3 has a concrete licensed raw-text/concept/coreference source in one domain and
a licensed alignment control. It also has a pinned GPL-3.0
[OpenEA](https://github.com/nju-websoft/OpenEA/tree/b59e014153c27c7166d78475e3474c7e86a10be9)
toolkit containing general entity-alignment benchmarks and twelve representative
methods. None has P3's scientific-coordinate, set-valued, invalid/unresolved or
downstream-decision terminal. The 768-cluster coverage/harm endpoint remains
open, and SciREX's missing-mention fact becomes a preserved successor problem.

## P5: minimal revision plus protected fresh transfer

### Strongest public candidates

| source | bytes and licence | useful label | exact mismatch |
|---|---|---|---|
| [SWE-bench Multilingual `846e647…`](https://huggingface.co/datasets/SWE-bench/SWE-bench_Multilingual/tree/846e647b9f33c0b51b739d005d13d85493c9af09) | MIT card; 300-row Parquet object pinned by LFS SHA-256. | Real issue, gold patch, test patch and pass/fail test lists across languages/repositories. | Public gold and mainly implementation/execution repairs; no protected eight-class responsibility, same-symptom blocking, fresh transfer or harm. |
| [SWE-bench Verified `78f471b…`](https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified/tree/78f471bf655a3137b2e8a75af1501690ec009ec3) | 500-row Parquet object pinned by LFS SHA-256; current card has no licence field/tag. | Human-validated issue--PR tasks and runnable evaluation schema. | Dataset-byte rights are `CANNOT_CHECK`; gold patch/test fields are public; no self-revision label or protected fresh evaluator. |
| [Defects4J `8c16da8…`](https://github.com/rjust/defects4j/tree/8c16da8230843cdc918eaf4ddb449637f02b83c6) | MIT framework, pinned commit/tree. | Reproducible implementation failures and fixes. | Only a narrow revision class; public fixes; no transfer/harm or host authority. |
| [BugSwarm `2b276ac…`](https://github.com/BugSwarm/bugswarm/tree/2b276ac5c475bcc71c9d62384943206c7768408f) | BSD-3-Clause infrastructure; public API/Docker routes; no artifact body opened. | Real CI fail--pass pairs, useful for environment/execution cases. | Infrastructure licence does not settle every mined project/container byte; no protected causal revision label. |
| [BugsInPy `11c5f1e…`](https://github.com/soarsmu/BugsInPy/tree/11c5f1eea954a42132cfd06bf257766a7963e0fd) | Repository archive pinned; no root licence file at the pinned commit. | Buggy/fixed Python project versions. | Rights are `CANNOT_CHECK`; implementation-only labels; public fixes. |

### What this closes

It closes source identity for public implementation/execution strata and pins
one MIT fixed-agent baseline, SWE-agent. It does not supply even one protected
eight-class same-symptom block, a fresh-transfer/harm record, a final split or a
six-arm self-edit/self-evolution comparator family. Public benchmark gold cannot
be relabelled as protected freshness. P5's primary campaign remains unexecuted.

## Outcome-blind sampling boundary

`MINIMAL_SAMPLING_MANIFESTS.json` contains only provider file identities:

- P1: one SWE-bench Multilingual Parquet identity and the PeerRead adapter
  revision, with no row IDs;
- P2: four deterministically selected SYNERGY `labels.csv` file identities,
  selected from directory-label hashes without opening their contents;
- P3: the three CRAFT archive identities, the OAEI archive identity and the
  SciREX archive HEAD identity;
- P5: the two SWE-bench Parquet identities plus Defects4J and BugSwarm source
  revisions.

No dataset row, label value, issue, patch, test, archive body, Docker artifact
or protected result was opened by the collector. Public descriptive metadata
and schema fields were inspected. This protects the audit boundary but does not
create external custody.

## Required next bindings

1. **Rights owner:** bind issue/review/comment/attachment and underlying article
   text per content class; do not infer these rights from code or metadata
   licences.
2. **Eligibility custodian:** apply each paper's frozen eligibility rules and
   return only counts/exclusions. A zero cell remains a negative source-universe
   result.
3. **Protected-label owner:** commission or hold P1 transition-responsibility,
   P3 four-coordinate/envelope/downstream-loss and P5 eight-class/fresh-harm
   labels outside candidate write authority.
4. **Comparator owner:** freeze exact identities and terminal-preserving
   adapters. Native issue resolution, screening or entity alignment is not the
   corresponding paper endpoint.
5. **Freshness owner:** construct post-freeze or access-controlled splits;
   widely public gold can support development or contamination controls, not
   protected confirmatory outcomes.

## Artifacts

- `ONLINE_EVIDENCE_RECEIPTS.json` — official HTTP receipts, revisions, file
  identities, licence-byte hashes and dataset metadata.
- `PUBLIC_SOURCE_BINDINGS.json` — endpoint-by-endpoint binding matrix and exact
  closed/open classifications.
- `MINIMAL_SAMPLING_MANIFESTS.json` — outcome-blind file-identity selections.
- `NEGATIVE_RESULT_LEDGER.md` — recursively named adverse results and next
  discriminators.
- `collect_public_metadata.py` and `build_binding_artifacts.py` — deterministic
  metadata-only reconstruction.
