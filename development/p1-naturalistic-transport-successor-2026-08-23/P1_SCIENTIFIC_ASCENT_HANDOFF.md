# P1 scientific-ascent handoff: typed responsibility licensing

**Date:** 2026-08-23  
**Lane:** `work/lane-handoffs/p1-naturalistic-transport/`  
**Main checkout:** read-only  
**Tests/builds/Git mutations:** none  
**Case text or result rows opened:** none  
**Panel execution:** not authorized and not run

## Bounded outcome

P1's widest defensible contribution is **typed
responsibility-to-authority licensing**: diagnosis, a successful intervention
and the scientific layer that evidence licenses changing are different objects.
The transition envelope represents that relation. Exact factorization, Bayes
deficiency, controlled-state frontiers, transcript separation and
rectangularity support the relation but do not supply separate generic novelty
or naturalistic authority.

The public-source lane found a large metadata universe, not a valid case panel.
The exact terminal is:

`P1_NATURALISTIC_PUBLIC_PANEL_CANNOT_CHECK_RIGHTS_OR_CONSTRUCT_VALIDITY`

This terminal is a scientific result about the current design boundary. It is
not an empirical zero and it does not narrow or overwrite the target claim.

## Prospectively frozen source feasibility

`SOURCE_FEASIBILITY_PROTOCOL_V1.json` was written before any Europe PMC search
request. It freezes:

- the provider cutoff and exact REST/OA routes;
- the five publication-type count queries;
- count-only response disposal;
- per-content-class licence admission;
- relation identity, exclusion, canonical-family deduplication and deterministic
  source-disjoint wave rules;
- forbidden titles, abstracts, filenames, URLs, headings and action tokens;
- six source-native typed terminals;
- donor-complete and information-equivalent controls; and
- fail-closed metadata and case-feasibility terminals.

The frozen source-native terminals are:

1. `KEEP_OR_REPAIR_REPORTING`;
2. `REVISE_MEASUREMENT_OR_DATA`;
3. `REVISE_METHOD_OR_ANALYSIS`;
4. `WITHDRAW_CLAIM_OR_CONCLUSION`;
5. `WITHDRAW_ARTIFACT_FULL_RETRACTION`; and
6. `UNRESOLVED`.

They are not silently coerced into the older seven R7A action handles. A total,
semantics-preserving adapter is a noncompensatory future gate.

## Count-only Europe PMC census

`run_metadata_counts.py` loaded the frozen protocol and queried Europe PMC with
`resultType=idlist`, `pageSize=1`, `format=json`, `synonym=false`. The client
extracted `hitCount` and request metadata only. The returned `resultList` was not
inspected, printed or persisted.

| frozen query | hit count |
|---|---:|
| OA + PMC `Published Erratum` | 93,796 |
| OA + PMC `Correction` | 105,342 |
| OA + PMC `Retraction of Publication` | 17,360 |
| OA + PMC `Retracted Publication` | 18,056 |
| OA + PMC `Expression of Concern` | 1,516 |

The sum of notice classes is not deduplicated and is not a pair count. The count
terminal is:

`P1_NATURALISTIC_PUBLIC_METADATA_CANDIDATES_PRESENT__CASE_FEASIBILITY_UNDETERMINED`

Exact case-level facts remain zero by design: 0 relations assessed, 0
rights-admissible pairs, 0 eligible source clusters, 0 system outputs and 0
protected scores.

## Source-rights and construct audit

### Europe PMC / PMC

This is the strongest prospective source. Official documentation binds a
rights-permitting OA subset, article-specific licence checking, the official
REST/OA/OAI/FTP/Cloud/BioC retrieval routes and a prohibition on arbitrary
systematic scraping. The PMC OA service can return per-PMCID licence and
retraction metadata without fetching article content.

The protocol automatically admits CC0, CC BY and CC BY-SA variants compatible
with the intended transformed release. It excludes ND, NC, custom and missing
licences absent exact rights-owner permission. Both the original and notice,
plus every excerpt or supplement, must pass. An explicit provider-native
original-notice relation is mandatory; title similarity is insufficient.

### Crossref Retraction Watch

- repository: `https://gitlab.com/crossref/retraction-watch-data`;
- observed head: `7bb2ced143b764974c53c6c61abfdd2379f5307d`;
- CSV blob: `40a049f02044fab8286c0304fd296bf1fa2cb8ca`;
- CSV SHA-256: `ceaab201d728dfcf9929ec1e229acd2ad88c650c847ec922ba9ffe831e366abb`;
- exact size: 65,984,968 bytes;
- 71,944 data rows, counted without displaying or retaining fields;
- README generation date: 2026-08-21.

The initial rights probe was adverse: the GitLab project licence and Crossref
DOI licence fields were `null`, and no repository licence file resolved. A later
official Crossref metadata-retrieval page supplied the controlling evidence: its
licensing table explicitly lists the **Retraction Watch database as CC0**.
`SOURCE_RIGHTS_AMENDMENT_V1.json` preserves both observations and supersedes the
earlier `CANNOT_CHECK_RETRACTION_WATCH_DATASET_REUSE_LICENSE` subterminal for CSV
metadata fields only.

The CC0 binding does not cover publisher/author abstracts, article or notice
full text, attachments, supplements, linked pages or Retraction Watch blog
posts. No row field was displayed or inspected. The pinned CSV is now the best
lawful development backbone, but public curated labels, post-event reasons,
memorization, update-family duplication, correction undercoverage and absent
independent custody still block a result-bearing panel.

The next source-specific freeze may be named
`P1.RW.CC0.NATURALISTIC.DEVELOPMENT.V1` as a subprotocol of the existing
licensing-relation/transport successors. It must use connected update families,
keep every update/reason/notes/identifier field evaluator-side, require at least
20 lineage-disjoint registered source families in any promoted action cell,
model their dependence explicitly, and reserve a protected future-update wave.
It must not become a new claim identity that overwrites the
existing successors.

### OpenAlex

The documentation states that the complete metadata dataset is CC0 and exposes
`is_retracted`, derived from Retraction Watch. It also exposes `erratum`, with
documented low coverage. This is suitable for bibliographic cross-checking, not
for responsibility or typed minimal-transition gold. Predicting retraction from
title/abstract would test retrospective risk prediction rather than licensing.

### Zenodo metadata candidates

Five exact metadata records were inspected before the freeze; files were not
downloaded. All five declare CC BY 4.0:

`14783213`, `14921712`, `15185273`, `18768427`, `20478570`.

They remain metadata candidates only. A deposit licence does not establish the
rights of upstream Retraction Watch-derived fields, and most appear to contain
labels or indexes rather than raw noisy notice evidence. File-level schema,
provenance, leakage and typed-action preflight remains required.

## Why the metadata abundance is not yet the missing top-tier result

The decisive unit is an admissible **source-family cluster**, not a search hit.
Every case still needs all of the following:

1. rights-cleared original and notice bytes;
2. explicit source-native relation identity;
3. independent typed minimal-transition adjudication;
4. a noisy view that retains the scientific discriminator after all explicit
   action, heading, title, filename, URL and publication-type cues are removed;
5. a natural same-family control or a prospectively defensible matched control;
6. byte-identical information/actions/resources for a relation-ablated donor;
7. an information-equivalent donor that is required to tie;
8. source-disjoint waves and changed semantic host;
9. owner-separated case, gold, scoring and result-verification custody.

Failure of any item is `CANNOT_CHECK`, never an imputed positive result.

## Manuscript-ready dominant-claim patch

`P1_DOMINANT_CLAIM_MANUSCRIPT.patch` is a unified, unapplied patch over seven P1
files. A dry-run applies cleanly to the current shared checkout. It:

- retitles the paper around typed responsibility licensing;
- replaces the abstract's generic five-peer hierarchy with one dominant
  science-specific claim and an explicit authority ladder;
- classifies the factorization/POMDP/rectangularity results as analytic support;
- preserves the exact 2,882-world and 400-contract positives at their proper
  mechanical authority;
- makes the 1/48 broad predecessor, 32/66 singleton rules and 33/66 blind
  shortcut explicit adverse results;
- preserves the information-equivalent 400/400 tie; and
- leaves naturalistic, model-general and external authority undetermined.

`P1_CLAIM_HIERARCHY_FAILURE_V1.md` records the authority-drift failure, cause,
residual and next discriminator without inventing a redundant successor.

## Cooperation boundary with the Claude Code task

The supplied Claude Code task was inspected read-only. Its visible latest state
was archived and out of usage credits; it reports active local-blocker/PR work
across P1--P15. No message, unarchive, branch edit or external side effect was
performed. To avoid clobbering that work, this lane changed only isolated
handoff artifacts and supplies an unapplied patch with current-context guards.

## Exact blockers for integration

1. Retraction Watch CSV metadata rights are now CC0-bound, but linked article,
   abstract, notice, attachment and blog content rights remain separate.
2. Public curated labels, post-event reason codes, memorization risk and
   update-family duplication block direct use as causal-responsibility gold.
3. Europe PMC count abundance is not a rights-admissible pair census.
4. Original-notice relations and article-specific licences are unassessed.
5. No protected typed-action gold or anti-leak candidate view exists.
6. Source-native typed actions do not yet have a total semantics-preserving R7A
   terminal adapter.
7. No natural same-family controls or frozen matched donors exist.
8. R7A candidate/external adapters remain unbound.
9. No changed semantic host or owner-separated custody is bound.
10. The historical leak, singleton and blind-responder negatives remain active.
11. Even a successful locally executed panel would be development evidence only.

## Integration order

1. Review and apply `P1_DOMINANT_CLAIM_MANUSCRIPT.patch` only from a clean,
   drift-checked integration lane.
2. Obtain an owner-bound rights/relation census using the frozen protocol.
3. Report exact exclusion counts and zero cells before opening case text.
4. If the noncompensatory gates pass, freeze source-family IDs, hashes, typed gold
   rules, leak tests, donors, adapters, hosts and custody before any execution.
5. Otherwise retain
   `P1_NATURALISTIC_PUBLIC_PANEL_CANNOT_CHECK_RIGHTS_OR_CONSTRUCT_VALIDITY` and
   treat the failed gate as the next research problem.
