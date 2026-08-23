# P10 native-state incremental-value protocol V1

Status: **FROZEN BEFORE NEW OUTCOMES**

Frozen: 2026-08-20

## 1. Scientific question

P10 already has a prospectively frozen, deterministic positive source-transfer result on the exact Mathlib corpus: under leave-top-module-out evaluation, a first-order tactic-family Markov predictor reaches 0.3842 accuracy versus 0.2796 for the pooled unigram baseline, a difference of 0.1046 with a top-module bootstrap 95% interval of approximately [0.0863, 0.1223]. The existing result is not reopened or retuned here.

This extension asks a narrower and stronger question:

> On the same held-out top-level-module boundary, does native Lean proof-state and proof-dependency structure explain additional next-action predictability beyond the already-positive tactic-history transfer baseline?

A positive answer would support a larger P10 residual than source recurrence alone. A null answer leaves the existing source-transfer claim intact and forbids a state/mechanism claim.

## 2. Locked subject

The subject remains the revision-bound P10 Mathlib corpus and native environment already named by the candidate package:

- Mathlib commit: `e72c1e277f31441626621f7d0c7207862fc25569`
- Lean toolchain: `leanprover/lean4:v4.34.0-rc1`
- corpus: the 457 files in `MATHLIB_CORPUS_V2_MANIFEST.json`
- transfer population: all recognized theorem/lemma tactic trajectories from the V2.1 source projection
- primary split: leave one top-level Mathlib module out, exactly as in V2.1

No file, module, theorem, transition, seed, threshold, or feature family may be removed after inspecting the new outcome except by a failure rule frozen below.

## 3. Prior evidence is locked, not a tuning set

The V2.1 result is prior evidence and the comparator. It may not be used to choose new state-feature thresholds, regularization, model family, module exclusions, or success cutoffs. The primary comparator is the exact V2.1 first-order Markov prediction defined by `benchmark/run_mathlib_transfer_v2_1.py`.

The following are prohibited:

- choosing a feature family because it happens to make the primary test positive;
- reporting only modules with positive deltas;
- changing the held-out boundary after outcome inspection;
- replacing the locked Markov comparator with a weaker baseline;
- treating a source-text proxy as a native Lean proof state;
- using theorem or module identity as a predictive feature;
- using future proof steps, final proof text, or held-out-module statistics in a test feature;
- promoting exploratory secondary endpoints to the primary claim.

## 4. Expert review roles

The tranche is reviewed under four independent roles.

1. **Methods/reproducibility reviewer** — checks chronology, subject identity, deterministic extraction, split purity, uncertainty, and exact regeneration.
2. **Lean/mathlib reviewer** — checks that recorded states and dependencies are native Lean objects rather than source-text surrogates and that the runtime matches the frozen subject.
3. **Hostile integrity reviewer** — attempts module-identity leakage, theorem-family leakage, future-step leakage, parser contamination, receipt substitution, and post-outcome selection attacks.
4. **Publication/claims reviewer** — permits only the highest claim whose preregistered gate passes and requires explicit retention of null/negative secondary results.

Any reviewer may block claim escalation.

## 5. Extraction contract

### 5.1 Native state receipt

For every eligible tactic transition, the extractor must bind at least:

- subject theorem identity and source digest;
- exact Mathlib revision and Lean version;
- pre-tactic pretty-printed goal state digest;
- local-context summary derived from the native state;
- tactic-family label used by the existing P10 projection;
- verifier/extractor command and exit status;
- stdout/stderr or structured-trace digest sufficient to detect substitution.

If the native extractor cannot encode a transition unambiguously, that transition is marked `UNAVAILABLE` by a deterministic rule. It is not silently reconstructed from future source text.

### 5.2 State features

The preregistered state-only feature families are:

- goal-head/operator signature;
- number of goals;
- local-context cardinality;
- multiset/count summary of local hypothesis head constructors/types;
- presence/count summary of equality, conjunction/disjunction, implication/function, existential/universal, arithmetic/algebraic, and proposition/type-class shapes when deterministically derivable from the native expression tree;
- stable expression-size/depth buckets with bucket boundaries fixed from syntax, not outcome quantiles.

Names of files, modules, theorem declarations, namespaces, and source paths are forbidden as predictive inputs.

### 5.3 Dependency features

The preregistered dependency family is a local proof-dependence summary available at the pre-tactic state only. It may include counts and anonymized structural signatures of accessible premises/local hypotheses and tactic-dependence edges. Premise names are not model features; dependency identity may be used only to construct leakage-safe structural summaries.

A TacMiner-style tactic-dependence graph comparator may be implemented if its graph is derivable without access to held-out labels or future proof steps. If faithful TDG reconstruction is unavailable, this arm must report `CANNOT_CHECK`; a weaker proxy may be exploratory but cannot discharge the strong-baseline gate.

## 6. Models and comparators

All models are intentionally simple so the test concerns information content rather than model scale.

- **B0 — unigram:** exact V2.1 pooled training next-action majority baseline.
- **B1 — tactic-history:** exact V2.1 first-order tactic-family Markov baseline conditioned on current tactic family.
- **B2 — state-only:** regularized multinomial linear classifier over the frozen native-state features.
- **B3 — tactic-history + state:** the same classifier family over B1 history indicator(s) plus native-state features.
- **B4 — tactic-history + state + dependency:** B3 plus the frozen leakage-safe dependency summaries.
- **B5 — TacMiner-class comparator:** faithful tactic-dependence-graph baseline when implementable on the exact corpus; otherwise `CANNOT_CHECK`, which blocks the largest standalone novelty claim but does not erase B1-B4 results.

Regularization values are fixed to a small a-priori grid `{0.01, 0.1, 1.0, 10.0}` and selected *inside each training fold only* by nested leave-one-training-module-out log loss. No held-out module is consulted during selection.

## 7. Primary endpoint

The primary endpoint is the pooled leave-top-module-out accuracy difference:

`accuracy(B4) - accuracy(B1)`

computed over the exact set of transitions for which B4 has a valid prospectively defined native-state receipt. B1 is recomputed on that identical receipt-eligible transition set as well as reported on the full V2.1 set.

Primary success requires all of:

1. observed pooled difference `> 0`;
2. top-module block-bootstrap 95% interval lower bound `> 0`;
3. at least 60% of evaluable held-out modules have non-negative B4-B1 accuracy delta;
4. paired multiclass log loss for B4 is lower than B1 on the same transitions;
5. all leakage, mutation, and label-shuffle controls below pass.

The effect size is reported in percentage points with the interval; statistical significance alone is insufficient.

## 8. Secondary endpoints

Reported regardless of sign:

- B2-B0, B3-B1, and B4-B3 accuracy deltas;
- paired log-loss deltas;
- top-k action accuracy for k in `{2, 3}`;
- per-module transition counts and deltas;
- state/dependency feature availability rate;
- calibration/Brier-style multiclass score when probabilities are available;
- coverage and performance stratified by proof-state size buckets fixed in advance;
- faithful B5 comparisons, if B5 is checkable.

No secondary endpoint can replace the primary endpoint after outcomes are seen.

## 9. Negative and hostile controls

The implementation must include all of the following.

1. **Label shuffle:** within each training fold, shuffle next-action labels with fixed seeds. It must not reproduce the observed primary lift systematically.
2. **Module-identity attack:** train an explicit attacker to predict top-level module from the retained feature vector. High attack accuracy relative to a declared majority baseline triggers hostile review; direct identity/path/name features are a hard failure.
3. **Future-step mutation:** replace a post-state/future tactic in the raw trace while holding the pre-tactic receipt fixed. Pre-tactic features must remain unchanged.
4. **Receipt substitution:** swap theorem/source/runtime identity while retaining feature bytes. Binding verification must fail.
5. **Statement/source mutation:** the existing P10 mutation philosophy applies; changed statement/revision/source identities must not validate as the frozen subject.
6. **Near-duplicate/family audit:** report normalized theorem-statement or structural-signature duplication across train/test modules. Any discovered leakage mechanism must be either removed by a frozen deterministic equivalence rule applied symmetrically to all folds or declared as a blocker; outcome-guided removals are forbidden.

## 10. Missingness and fail-closed rules

Native tracing failure is an observed property and must be reported. The primary analysis uses only transitions whose eligibility is determined without looking at the predicted action or correctness outcome. If fewer than 80% of V2.1 transitions are receipt-eligible, the native-state claim is `CANNOT_CHECK` unless a reviewer accepts a prospectively explainable ecosystem limitation; the existing V2.1 source-transfer claim remains unchanged.

A runtime mismatch, corpus-digest mismatch, extractor crash with partial silent output, or inability to prove train/test split purity is a hard `INVALID`, not a negative scientific result.

## 11. Claim ladder

The publication reviewer must choose the highest rung whose entire gate passes.

### R0 — existing positive transfer

Allowed now:

> Coarse tactic-family proof behavior transfers across held-out top-level Mathlib modules: on the frozen V2.1 corpus, a first-order tactic-history model improves next-action accuracy over a pooled unigram baseline by 0.1046, with a positive module-bootstrap interval.

This is a source-projection claim, not a proof-state or prover-success claim.

### R1 — native-state incremental signal

Allowed only if the primary endpoint passes:

> Native Lean proof-state/dependency structure adds cross-module next-action information beyond transferable tactic history on the frozen Mathlib subject.

### R2 — robust structural transfer

Allowed only if R1 passes and B3 and B4 improvements survive the required controls with non-pathological module heterogeneity:

> The transferable regularity is not explained solely by coarse tactic recurrence; it is partly associated with native proof-state structure and leakage-safe dependency summaries.

No causal wording such as “state causes tactic choice” is permitted.

### R3 — standalone novelty against strong nearest work

Allowed only if a faithful TacMiner-class graph/state comparator is run on the identical subject/split and the P10 contribution remains materially distinct and empirically non-dominated on its declared endpoint. This rung additionally requires a frozen nearest-work table covering LeanDojo/ReProver, TacMiner, and any materially closer work found before manuscript freeze.

## 12. Nearest-work anchors frozen for this protocol

The protocol is motivated, not outcome-tuned, by two established nearest-work directions:

- LeanDojo / ReProver: proof-state and premise-aware learning/evaluation in Lean, including leakage-aware/challenging splits. Primary reference: Yang et al., *LeanDojo: Theorem Proving with Retrieval-Augmented Language Models*, NeurIPS 2023, arXiv:2306.15626.
- TacMiner: tactic-dependence graphs for discovering reusable tactic structure across proofs. Primary reference: Xin et al., *Automated Discovery of Tactic Libraries for Interactive Theorem Proving*, arXiv:2503.24036 (2025).

A literature refresh is mandatory before any R3 manuscript freeze because nearest work can change.

## 13. Reproducibility outputs required before peer review

At minimum:

- immutable protocol digest;
- extractor/runtime/corpus receipts;
- exact transition manifest or content-addressed equivalent;
- machine-readable per-fold and per-module predictions;
- primary and secondary metric JSON;
- bootstrap samples or deterministic sample digest plus regeneration code;
- negative-control distributions;
- hostile mutation receipts;
- environment/dependency lock;
- one-command or mechanically enumerated regeneration path;
- claim-disposition receipt selecting R0/R1/R2/R3 without manual discretion.

## 14. Terminal discipline

A positive result is maximized by earning the highest rung, not by changing the rung after seeing outcomes. All nulls, regressions, unavailable arms, and hostile failures remain in the record. The existing V2.1 positive transfer result is preserved regardless of the outcome of this extension.