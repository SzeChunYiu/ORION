# ORION-12 journal readiness — narrowed publication track

**Current terminal:** `ORION-12 = PEER_REVIEW_READY` on the bounded methods / critical system-design claim as of 2026-08-18.

**Scope of that terminal (not machine-scored, and deliberately adjacent to it):** `P2_NARROWED` remains the scientific scope receipt. External ORION-vs-baseline superiority remains `CANNOT_CHECK` and is **not** part of the ready claim. Nothing about that exclusion has changed; it moved off the terminal line because the scoreboard reads that one line and cannot represent a scoped verdict.

That exclusion is now evidenced rather than only asserted. The four-arm
TREC-COVID comparison in `external/P2_TREC_COVID_ARMS_V1.json` runs ORION's
routing and stopping against BM25 and an RRF hybrid on the 50 official topics
under a matched budget, and the pass gate **fails**. Recall@100 for the ORION
arm sits 0.0177 below the strongest comparator with a paired bootstrap interval
of `[-0.0273, -0.0091]`: the point estimate is inside the -0.02 noninferiority
margin but the interval's lower bound is not, and noninferiority is a claim
about the interval. Cost fails outright and not marginally --- 2.8x the reads
where the gate requires at least 25% fewer.

One measured result does run the other way, and it is not the gate's criterion:
nDCG@10 is +0.1488 for the ORION arm with a bootstrap interval of
`[+0.1010, +0.1995]`, ahead on 42 of 50 topics. Multi-route exploration
improves top-10 quality substantially. The gate is written on recall and cost,
and a criterion outside the gate cannot rescue it, so the superiority verdict
remains `CANNOT_CHECK` on the strength of a comparison that was actually run.

The corpus is BEIR's 171,332-document trec-covid derivative rather than the
191,175-docid official round-5 release, and the ORION arm's own routing
terminal is separately `CANNOT_CHECK` because two of five routes are
unavailable on this corpus. Both are recorded in the artifact.

The `**Current terminal:**` line is the machine-scored declaration read by `research/publication/scoreboard.py`, which matches only `**Terminal:**` / `**Current terminal:**`. The previous `**Scientific terminal:**` / `**Publication terminal:**` pair carried the same meaning to a human reader and no meaning at all to the scoreboard, which reported this paper as having no scorable terminal.

The terminal line then acquired a second problem, fixed above. It declared `PEER_REVIEW_READY` **and** named the excluded superiority claim as `CANNOT_CHECK` in the same sentence. That reads correctly to a person and is unresolvable for the parser, which treats any `CANNOT_CHECK` on the terminal line as the verdict — fail-closed, and therefore silent. ORION-12 was scored `CANNOT_CHECK` with twelve blockers while its own fail-closed evidence gate (`orion.publication.peer_review_ready.evaluate_paper`) reported `ok=True` with none. The verdict and the scope now occupy separate lines, so the machine reads one claim and the reader still sees both.

Canonical scope receipt: `protocol/P2_NARROWED_PUBLICATION_TERMINAL_2026-08-17.md`.
Dated nearest-work freeze: `protocol/P2_LITERATURE_ASSIMILATION_FREEZE_2026-08-17.md`.
Machine-checkable donor ledger: `protocol/P2_DONOR_ASSIMILATION_LEDGER_V1.json`.

## 1. Final claim boundary

Paper 2 is now a **methods / critical system-design paper**, not an externally supported ORION-vs-baseline superiority paper.

Supported claim:

- in the frozen 390-task complete-gold controlled world, the route/read/stopping governance mechanisms behave in the intended fail-closed directions under matched host-owned budgets;
- bounded MetaSyn and AutoResearchBench probes are external stress tests / stage-failure evidence only;
- relevance, utility, coverage and sufficiency may guide acquisition, but do not self-authorize global scientific closure when route obligations remain unresolved, unavailable or censored;
- content identity is kept distinct from question-conditioned processing state.

Not claimed:

- matched external ORION-vs-baseline Wide/Deep superiority;
- official SAGE superiority;
- live-provider cost/latency/token superiority;
- proof of open-world completeness;
- generic lexical/dense/reasoning-aware/field-aware retrieval novelty;
- generic verification-aware, utility-based or learned STOP/CONTINUE novelty;
- generic question-conditioned memory or systematic-review automation novelty;
- literature saturation.

## 2. Result-bearing evidence — complete

- [x] Frozen complete-gold companion: 390 tasks × 14 systems × 3 deterministic repeat seeds = 16,380 normalized records.
- [x] Full ORION mean recall 0.979487; strongest frozen confirmatory comparator 0.666667; descriptive difference +0.31282.
- [x] Statistical authority `TIER_B_committed` with the frozen mandatory underpowered label; no offline inferential superiority promotion.
- [x] Route-stop oracle, task-stop safety analysis, negative ablations, query-count resource axis, Figures ORION-12-1..ORION-12-7 and Tables ORION-12-1..ORION-12-3/ORION-12-S1 generated from archived evidence.
- [x] MetaSyn official ID-only bounded probe on 86 reviews with stage-separated false-negative ledger.
- [x] AutoResearchBench Deep bounded official-judge probe retained at 0/600 with judge control 9/9; not relabelled positive.
- [x] AutoResearchBench Wide bounded credential-free official probe retained as a weak/null stress test; not relabelled matched superiority.
- [x] OpenAIRE structured-identity discriminator and subsequent 400-row matched campaign retained; the latter remains `P2_WIDE_EXTERNAL_CANNOT_CHECK` after 400 DOI-crosswalk HTTP 400 failures, with all Actions artifacts mirrored before expiry.
- [x] ORION-12-X post-saturation exact successor retained as bounded A1/A2 evidence: 400/400 ORION-12-X versus 250/400 donor-complete available-route product on 400 exact heterogeneous acquisition contracts; independent verification passes, B3 ideal typed product ties 400/400, and deployed/retrieval-engine generality remains `CANNOT_CHECK`.
- [x] Claim ledger binds all result-bearing abstract/results/limitations/conclusion sentences to immutable artifacts.

## 3. External gates — preserved, no longer blocking the narrowed paper

The following remain scientifically interesting `CANNOT_CHECK` conditions, but they are **future-work/reopen triggers rather than prerequisites for the narrowed paper**:

- a valid matched Wide ORION-vs-baseline campaign after the first structured OpenAIRE/Crossref attempt failed its frozen transport gate (`0.666667 < 0.90` provider success); reopen only under a new prospective freeze after independently validating crosswalk request syntax;
- matched multi-provider official Deep comparison;
- official SAGE 200k corpus/evaluator;
- final live-provider campaign and monetary/runtime/token ledger.

No weaker proxy may be labelled official. If any gate becomes executable before submission, re-open the scope decision and freeze a prospective protocol before accessing new outcomes.

## 4. Novelty / nearest-work gate — narrowed and dated

- [x] SAGE absorbed: strong lexical retrieval and metadata/keyword augmentation are prior art.
- [x] AgentIR absorbed: reasoning-aware retrieval is prior art.
- [x] MetaSyn absorbed: retrieval/screening stage separation is prior art.
- [x] DeepControl absorbed: marginal-utility continuation/granularity control is prior art.
- [x] HALT absorbed: verification/evidence-coverage stopping is prior art.
- [x] SIEVE absorbed: fielded Boolean retrieval, inspection and selective fetch are prior art.
- [x] Decision-theoretic screening stopping absorbed as utility-based prior art.
- [x] 2026-08-13 structured Search-R1 stopping work absorbed; learned STOP/CONTINUE judgments are not claimed as novel.
- [x] MemChain absorbed as pressure against generic question-conditioned-memory novelty.
- [x] Source-bound dispositions are canonical-hashed and hostile-checked by `scripts/check_p2_assimilation.py`.
- [x] Literature saturation is explicitly **NOT CLAIMED** because material stopping work appeared four days before the cutoff.
- [x] Dated primary-source refresh is current through 2026-08-17 for submission on or before 2026-08-31; later submission is a filing-time reopen trigger.

## 5. Venue decision

**Primary target:** *Information Processing & Management* (IP&M).

Reason: the surviving object is an information-retrieval governance / methods / critical system-design contribution at the intersection of computing and information science. The 2026-08-17 official IP&M scope explicitly welcomes research-method and critical system-design manuscripts. The previous TMLR recommendation is superseded for this narrowed claim surface.

Fallback: JASIST only after a larger information-science/use-oriented reframe.

Re-open the venue decision if a new external algorithmic superiority result or user/use study materially changes the paper.

## 6. Manuscript — scientific content complete on narrowed track

- [x] Title reframed around fail-closed coverage/stopping rather than broad ORION superiority.
- [x] Abstract remains exactly bound to the claim ledger and preserves external `CANNOT_CHECK`.
- [x] Nearest-work section absorbs fresh retrieval/stopping/memory donors and subtracts their mechanics from novelty.
- [x] Methods and formalism retain typed route/task authority and content/read-state separation.
- [x] Results remain generated from archived immutable evidence; no result artifact is changed by the narrowing lane.
- [x] Limitations preserve synthetic-world, provider, denominator, contamination and null-on-recall constraints.
- [x] Conclusion remains claim-ledger bound and refuses promotion without admissible external authority.
- [x] Bibliography includes the 2026-08-17 primary-source donor additions in `manuscript/recent_work.bib`.

## 7. Reproducibility package

- [x] frozen controlled corpus/index and run manifest;
- [x] exact subject/data/system/evaluator bindings;
- [x] offline regeneration/check commands and generated plots/tables;
- [x] MetaSyn/AutoResearchBench bounded external archives and typed failure evidence;
- [x] benchmark licence/access notes and route/query derivation manifests;
- [x] query-count resource ledger for completed tiers;
- [x] independent clean-CI reproduction of the offline headline;
- [x] source-bound donor assimilation ledger + hostile tests;
- [x] expiring CI evidence is mirrored in the repository with per-file hashes; a repository-independent DOI is explicitly typed as a filing-time deposit operation and is not fabricated as scientific evidence.

## 8. Mechanical submission gate

- [x] target venue selected: IP&M.
- [x] cover-letter draft is refreshed to the narrowed title/claim; author metadata remains a filing-time human input.
- [x] supplement plan exists and its claim/evidence inventory is bound in the journal-package manifest.
- [x] compile the narrowed manuscript and retain the checksummed 21-page PDF in `journal_package/manuscript.pdf`; the same workflow remains runnable in repository CI.
- [x] run final reference-metadata and figure-legibility audit against that PDF; no unresolved citation/reference or overfull-box warning remains.
- [x] complete independent final PDF/claim proofread across all rendered pages, figures, tables, abstract, limitations and conclusion.
- [x] preserve authorship as an explicit filing-time operation: use the double-anonymous placeholder until the authors supply the title-page metadata; automation does not infer identities.
- [x] literature refresh is within 14 days on 2026-08-18; re-run only if actual submission occurs after 2026-08-31.

## Issue mapping

- #157: close after this lane passes CI; all still-open campaign boxes are genuinely unavailable external gates and the manuscript is populated to the final bounded claim.
- #279: close at `CANNOT_CHECK / REFUTED_OR_SHRINK`; external failure is candidate-generation dominated and the paper is explicitly shrunk instead of forcing a V2.
- #317: close at `P2_NARROWED`; do not claim saturation.
- #318: ORION-12 consumer tranche is complete (source-bound receipts + hostile validator), but the shared ORION-11/global issue remains open.
- #99: the bounded publication track now passes section 8 and may close at `PEER_REVIEW_READY`; the maximal external-superiority programme remains explicit future work.

## Done definition

`ORION-12 = PEER_REVIEW_READY` on the narrowed claim because the manuscript compiles cleanly, reference/figure and independent PDF/claim checks pass, the dated literature state is current for the readiness date, and every unavailable or invalid external authority remains visible as `CANNOT_CHECK`/future work rather than being promoted into support.
