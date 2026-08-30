# The 400-row coordinate table is absent from the object store

**Terminal: `CANNOT_CHECK_ARTIFACT_ABSENT`.** No synthetic reconstruction.

#1701 asks that the original 400-row coordinate table be committed **if it can be
recovered from a frozen source**, and that `CANNOT_CHECK_ARTIFACT_ABSENT` be
retained if it cannot. This records the search that settles which.

## Why a new search was warranted

`theory/promotion-reduct-v1/RESULT.json` already carries a
`scope_gate_400_case_table` field, and its recorded scope is:

> `"search_scope": "WHOLE REPOSITORY, excluding .git"`

That is the working tree. A file deleted before the current commit is invisible to
it, and its listed candidates use pre-R0 paths
(`papers/orion-12-open-world-scientific-discovery/…`), so the search predates the
rename. Excluding `.git` is exactly the gap that concealed an orphaned subject
commit elsewhere in this repository, so history was searched here.

## What was searched

**Every blob in the local object store** between 5 KB and 3 MB — **12,828 blobs**.
The bounds are justified: 400 rows of decision coordinates cannot be under 5 KB,
and the artifact is a table rather than a corpus.

1. **Structures with 350–460 records.** 29 found. The only one with exactly **400**
   is `40422d1199a63849131ad9c19f8712ce32f92efc`,
   `research/orion-epistemic-state-v1/results/P2-DES-01/RAW_POLICY_OUTCOMES_V1.json`,
   schema `orion.p2-des-01.raw-policy-outcomes.v1`. Its columns are retrieval
   outcomes — `ndcg_at_10`, `recall_at_100_budget`, `topic_id`, `policy_id` — not
   promotion coordinates. **Wrong artifact.**

2. **Blobs carrying the reduct's own feature vocabulary** (`claims_new_primitive`,
   `known_composition`, `prior_art_found`, `req:NOVELTY`,
   `closed_world_new_method`, `novelty_unknown`, …). 12 blobs mention three or
   more. Every one is either Python source
   (`src/orion/transfer/v2/p4_method_authority.py`), a JUnit XML report, or a
   small bench. **None is a table.**

3. **Every historical version of the bench itself.**
   `METHOD_AUTHORITY_BENCH_V1.json` has **10 cases in every version** that exists
   (`3a1a83178`, `2bab2148f`). It was never a 400-case file.

4. **All 214 historical paths under ORION-14's tree**, filtered to 350–460 lines.
   One candidate, `figures/data/RESULTS_SUMMARY_V1.json` at 429 lines, which is a
   hypothesis summary with 13 attack families, not 400 rows.

A control confirms the line-count scan discriminates: the committed bench measures
196 lines and is correctly excluded from the 350–460 band.

## Scope limit, stated rather than glossed

The search covers the **local object store**. An object reachable only from a
branch that was deleted on the remote before this clone fetched it would not be
present — that failure mode is real and was observed elsewhere in this repository.
So this establishes the table is not in the history available here, not that it
never existed anywhere.

## Consequence

`CANNOT_CHECK_ARTIFACT_ABSENT` stands, and #1701's instruction is explicit that
this must not be repaired by synthetic reconstruction. It is also explicit that
this does not block filing. The reduct result in `promotion-reduct-v1` is computed
over the 10-case bench it names and is scoped to it; nothing here changes that
packet, whose `SOURCE_MANIFEST.json` seals its file list.
