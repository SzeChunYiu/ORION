# Local science repairs V3

**Repository:** `SzeChunYiu/ORION`  
**Reviewed head:** `703b87db22dce3981f13b407b56f4a656310632f`  
**Date:** 2026-08-29  
**Authority:** exact correction text and migration instructions only; applying a repair must follow the target paper's content-binding and freeze rules.

These repairs close contradictions, overclaims and missing boundary language that can be fixed from current committed evidence. They do not invent external outcomes. Where a manuscript or ledger is hash-pinned, the text below should first land as a governed successor/corrigendum and then be integrated with a complete rebind of every affected manifest and PDF.

## 1. ORION-01 — replace stale package-status rows

**Problem.** `JOURNAL_PACKAGE_STATUS_V1.md` states that no PDFs or build paths exist. At the reviewed head, `journal_package_A/SUBMISSION_MANIFEST.json` and `journal_package_B/SUBMISSION_MANIFEST.json` each record a committed review PDF and package build/verification path. The old status remains useful historical evidence but is no longer current on those rows.

**Replacement status paragraph:**

> **Current package correction (2026-08-29).** Both split-paper journal packages now contain committed review renders and package verification paths. These renders close the earlier “no PDF/no build path” condition only at review-package scope. The manifests record an engine substitution for the committed review render and retain as open: a clean-environment filing build, final template conversion, immutable archive/DOI, licence and author declarations, and external independent proof/novelty review. `submission_authority`, `top_tier_authority` and `external_independent_proof_review` remain false. No production-realization or registry-completeness claim changes.

**Required implementation.** Add a superseding addendum rather than editing the frozen science manuscripts. Bind the A/B manifest and PDF hashes in the addendum.

## 2. ORION-02 — distinguish structural independence from external independence

**Problem.** A second language/checker improves implementation confidence but remains same-owner and cannot close external reproduction.

**Required sentence:**

> The Rust checker is structurally independent of the Python implementation and provides cross-language corroboration of the registered finite claims. It is not an external replication: subject selection, scientific interpretation and release authority remain inside the same programme.

Place this sentence wherever “independent” first appears in the abstract, results summary and availability statement.

## 3. ORION-09 — make the stopped promotion a main result

**Problem.** The latest invariant is mathematically true but operationally vacuous: it never fires and does not predict the observed fibre failures. A paper that leaves this only in history risks implying a live universal-transfer path.

**Replacement conclusion paragraph:**

> The failed transfer is structural but not captured by the proposed capacity invariant. Fibre purity exactly characterizes binary separability under the registered representation; the capacity condition is unreachable on the tested alphabet and therefore adds no predictive content. We retain the theorem as a negative result and stop the universal transfer claim. Compilation-regime geometry remains family-specific: useful laws can coexist with explicit mixed-fibre counterexamples to a shared low-order predictor.

No second rescue cycle under the same identity should be opened.

## 4. ORION-11 — retraction guard

**Problem.** A stale branch nearly removed the later R4 retraction because a claim-ID-only comparison treated rows with changed statuses as identical.

**Mandatory abstract/results guard:**

> A faithful ordered-search comparator matches ORION on both registered components. We therefore withdraw the comparative mechanism-necessity reading while retaining the bounded v2.2.4 mechanical result. The result establishes conformance on the frozen mechanical world family; it does not establish superiority over the named parent systems, model-general reconstruction, or open-ended scientific benefit.

**Mandatory merge check.** Compare the full tuple `(claim_id, claim_text, status, boundary, evidence)` for every ledger row. A matching claim ID is not evidence that the authority state is unchanged. Fail any adoption that deletes `RETRACTED`, `NOT_SUPPORTED`, `CANNOT_CHECK`, the R4 terminal, or `CLAIM_RETRACTION_LEDGER_V1.md`.

## 5. ORION-12 — prevent metric rescue

**Problem.** The TREC-COVID arm improves nDCG@10 but fails the preregistered recall/cost gate. A venue-facing summary can easily cherry-pick the positive metric.

**Required result sentence:**

> Multi-route exploration improved top-10 ranking quality on the frozen TREC-COVID comparison, but the registered external-discovery superiority gate was not met: recall@100 and read cost failed their prespecified requirements. The nDCG@10 gain was not a gate criterion and does not rescue the superiority claim.

TREC-COVID is outcome-exposed and cannot serve as a fresh confirmation set.

## 6. ORION-14 — absent-row and CANNOT_CHECK guard

**Problem.** The optional reduct for the 400-case successor cannot be computed from committed rows; only aggregate counts are present. The smaller bench also proves that collapsing unknown prior-art status into “not found” destroys the target relation.

**Required statement:**

> The exact 400-case aggregate result remains active, but a minimal-feature reduct over those cases is not currently reproducible because the per-case table is not committed. No reduct is claimed for that object. On the separately committed ten-case authority bench, `CANNOT_CHECK` is load-bearing: treating an unexecuted prior-art search as a negative result removes every sufficient feature set.

Do not synthesize 400 rows from counts or from manuscript prose.

## 7. ORION-16 — migrate orphan-prone commit pins

**Problem.** Several content manifests name subject commits that can become unreachable after squash merge. The checker then degrades the strongest subject-commit comparison to `CANNOT_CHECK`, even when content digests remain sound. A self-including manifest also creates an endless one-commit-stale pin.

**Migration design:**

1. Keep per-file cryptographic digests as the primary release identity.
2. Put the manifest itself outside its own `bound_files`, or use a Merkle/root manifest whose root is signed after content fixation.
3. Bind a durable tag/release object or archive DOI rather than an ephemeral pre-squash commit.
4. Make unresolved subject identity a failing release gate, not a silent non-failing `CANNOT_CHECK`, while preserving `CANNOT_CHECK` as the scientific statement.
5. Record old orphaned pins as historical custody facts; do not rewrite them as if they had resolved.

This is a release-contract migration, not new ORION-16 science.

## 8. ORION-18 — correct the 169 multiplicity claim

**Problem.** The current science manuscript still contains abstract/theorem language suggesting 169 semantically heterogeneous donor-pair successes. The later mechanized interpretation shows the loop ignores both donor labels; 169 is multiplicity of one registered profile, and several wrong operators reproduce that count.

**Replacement abstract paragraph:**

> We prove a non-amplifying scientific-authority calculus and interpret registered donor hops into its delegation premises. In the historical finite harness, the 13×13 donor loop replays one donor-invariant composition profile: its 169 successful labels are multiplicity, not evidence for 169 semantically distinct integrations. The stronger evidence is an exact composition-soundness check over 36,864 representative pairs, standing for 9,437,184 state pairs, with zero unsound pairs and sensitivity to every registered wrong composition operator. A separate 20-case real-evidence study shows specification conformance across four domains, but its gold remains same-programme. External scientific adjudication and integration with a real deployed-style donor stack remain open.

**Replacement theorem label:**

> **Registered abstraction composition, not heterogeneous-breadth theorem.** Under the registered donor-invariant abstraction, compatible/narrowed or explicitly bridged authority composes and unbridged widening blocks. This demonstrates the composition law of the abstraction; it does not establish 169 semantically distinct donor interfaces.

**Required removal.** Remove “complete 13×13 heterogeneous donor-pair product” and any breadth claim inferred from the count alone. Promote the common-mode-gold non-identifiability theorem to the main limitations/result boundary.

## 9. ORION-19 — replacement abstract core

**Problem.** Historical representation-superiority language is fragile under semantics-preserving symbol reminting. The causal diagnosis and corrected resource ledger are the stronger current identity.

**Replacement abstract core:**

> Scientific-system failures can arise from missing semantic information, inaccessible representation, insufficient computation, or missing method coverage. We prospectively evaluate a frozen intervention selector across five task families. It identifies the registered failure location on four of five families versus one of five for generic compute escalation, produces zero false compute escalations versus four, and retains the remaining threshold-transport cell as `CANNOT_CHECK`. The conclusion survives a corrected eight-coordinate resource ledger that charges representation transforms, fitted state and inference touches. A historical typed-versus-serialized margin is not used as evidence: a semantics-preserving global symbol reminting changes that comparator's answers, so the margin is retired as format-prior sensitive. The supported result is bounded causal diagnosis under explicit resource accounting, not universal representation or model-size superiority.

All tables should distinguish confirmatory causal cells, retained null/negative cells, protocol-invalid history and retrospective mechanism diagnosis.

## 10. ORION-20 — enforce prospective-only language

**Problem.** The protocol names four public domains and minimum task counts, but the per-task enumeration, comparators, custody and results are absent.

**Mandatory front-page box:**

> **No empirical result exists under this protocol.** H1–H6 are `PROSPECTIVE_NOT_EXECUTED`. The named domains and counts are design commitments, not acquired or evaluated samples. No accuracy, discovery, transfer, cost or superiority statement may be written until task identities, baselines, evaluator custody and a bound result receipt exist.

A result table may show only `NOT_EXECUTED`/`CANNOT_CHECK`; zeroes would falsely imply measurement.

## 11. ORION-22 — one-shot public campaign and no P12C

**Problem.** The repository contains an unexecuted public stop/go protocol but no P12C result. The earlier allocator is broken under price and distribution shift.

**Mandatory sentence:**

> The public-data stop/go successor is frozen but not executed. No P12C empirical artifact or terminal exists. It will be executed once under the committed symmetric menus and stop rule; a failed gate will be published as the terminal rather than triggering same-identity retuning. The original q-greedy allocator's price- and distribution-shift failures remain active boundaries.

Reject any manuscript or ledger reference to a P12C result unless the referenced path and content hash exist.

## 12. ORION-23 — preserve the self-scoring correction

**Problem.** P13A's zero-harm label is entailed by the same support bit used by the policy. Later evidence is stronger, but the historical methodological correction must remain central.

**Required chronology sentence:**

> P13A is retained as an outcome-entailment failure: its self-scored safety endpoint cannot authorize empirical safety superiority. P13B repairs the immediate scoring defect, and the paper's main evidence is the later real digits responsibility shift, verifier-backed CNF comparison, donor-complete D2 study and drift-bounded certificate transport.

Do not hide P13A or pool it with independent-outcome studies.
