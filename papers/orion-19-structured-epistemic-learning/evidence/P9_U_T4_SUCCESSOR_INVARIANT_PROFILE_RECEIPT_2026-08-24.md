# ORION-19-U-T4 successor receipt: the format-prior defeat has a stable invariant successor

- **Date**: 2026-08-24
- **Gate addressed**: `ORION-19-U-T4-successor` (revival lane for the single succeeded component of the
  frozen T4 campaign, `FP-2_SEMANTIC_ORBIT_INVARIANCE::TYPED_SERIALIZED_BAG`)
- **Authority**: `NO_SCIENTIFIC_AUTHORITY_REPRESENTATION_REVIVAL_ONLY`, scope `BOUNDED_D1_ONLY`
  verbatim from the freeze. `ORION-19-U-T4` itself remains discharged-by-hostile-audit; this work does
  not un-defeat `TYPED_SERIALIZED_BAG` — that defeat stands, immutable.
- **Artifacts**
  - freeze `protocol/P9_U_T4_SUCCESSOR_INVARIANT_PROFILE_FREEZE_2026-08-24.md` + `.json`
    (`parameters_digest sha256:15cf1ce362df99f9bbcc13a275cdd899a35ea6cd0b07df3d0031348141e440aa`,
    committed pre-outcome)
  - result `evidence/P9_U_T4_SUCCESSOR_INVARIANT_PROFILE_RESULT_2026-08-24.json`
    (`result_digest sha256:676470f93eeaf6d9334c0e893e3e23192390da8cc95fe1069a7acbca9e4ba5e4`,
    exit 0)
  - independent check `evidence/P9_U_T4_SUCCESSOR_INVARIANT_PROFILE_INDEPENDENT_CHECK_2026-08-24.json`
    (`P9_T4_SUCCESSOR_SECOND_CHECKER_GREEN`, exit 0)
  - diagnosis `src/orion/study/p9/t4_defeat_diagnosis.py` (one-stage attribution, exit 0)
  - instruments `src/orion/study/p9/invariant_profile_representation.py`,
    `src/orion/study/p9/invariant_profile_battery.py`,
    `src/orion/study/p9/invariant_profile_checker.py`
  - environment: Python 3.13.12, scikit-learn 1.8.0, scipy 1.17.1, numpy 2.4.4,
    macOS-26.4 arm64
- **No existing ORION-19 result, receipt, protocol or evidence artifact is modified.** Only new files.
  The frozen attack module's freeze-twin digest was re-verified inside both the runner and the
  checker before anything ran.

---

## What was attributed first

The frozen defeat was re-derived, not trusted. `t4_defeat_diagnosis.py` (2026-08-24, exit 0)
returns the one-stage attribution **`answer_determination_numerics`**:

- the semantic orbit is information-neutral for `TYPED_SERIALIZED_BAG`: the design matrices are
  bitwise-equal up to one column permutation, and renaming the columns back reproduces the base
  fit bitwise;
- with **no attack present**, on the same base feature dicts, different multiclass solver
  families (`newton-cg`) and pure column-order renamings (reversed, seeded shuffle) each move
  exactly 32 of 128 protected answers, at equal training fit;
- the base design matrix has rank 88 of 150 columns, with 318 duplicate column pairs — the
  recorded 0.75 and the attacked 0.50 are two attractors of a non-identified optimum, and the
  orbit merely selects between them;
- 15 of 16 frozen cells reproduce in this environment; the one mismatch is the BASE cell of
  `TYPED_SERIALIZED_BAG` itself (recorded 0.75 with 2 distinct predictions; here 0.50 with 1),
  while the ORBIT cell reproduces exactly — the arm's answers were never pinned by its inputs.

The blind spot the frozen attack exploited: **the feature column key was the raw value spelling
of each token**, so an injective renaming both reorders columns and lets a rank-deficient
matrix settle on a different optimum with equal training fit.

## What ran

`TYPED_INVARIANT_PROFILE_BAG` (freeze §3): tokens keyed by isomorphism-invariant profile
colours — path + corpus document frequency, then K = 2 Weisfeiler-Leman refinement rounds over
co-occurrence — over the same information source as the raw bag (typed serialized token
multiset + sequence length; label-blind). Corpus = train ∪ dev of the variant being run.
Everything downstream ran through the frozen `run_arm` public extension point: frozen grid,
frozen `(-dev_accuracy, complexity_rank, config_id)` selection, v1.2 runtime adapter, frozen
`build_datasets()` with the shipped manifest digest `sha256:27752984…` re-verified.

### Verdict: `P9_T4_SUCCESSOR_REVIVED_STABLE` (exit 0)

| endpoint | measured |
|---|---|
| **E-INV** invariance | orbit raw-token guard **128 opportunities / 0 violations, PASS `HELD_UNDER_EXERCISE`**; equal-length control 48/0 PASS; all guard arithmetic recomputed identically by the independent checker |
| **E-STAB** stability | all 5 probes change **0 protected answers** (solvers lbfgs/newton-cg/sag; column orders identity/reversed/seeded-shuffle); identity probe reproduces frozen `run_arm` exactly |
| **E-PERF** level | BASE accuracy **0.75000** (= the frozen campaign's recorded raw-bag BASE level, floor 0.7421875), dev 0.95833, config `logistic-C0.1`, 2 distinct predictions, informedness 0.5 |

All four dataset variants (BASE, SEMANTIC_ORBIT, ORDER_PERMUTATION, EQUAL_LENGTH) select
`logistic-C0.1` and produce identical protected predictions and accuracies. The colouring:
177 corpus tokens → 71 colours; 72 train feature columns; the base and orbit colourings and
feature dicts are **bitwise identical**, not merely isomorphic.

## Why this is a revival and not a CORRECTED-with-failed-attempt

The original arm failed through two stacked properties: value spelling keyed the feature
columns (so a renaming perturbed the design matrix's column space), and the resulting matrix
was non-identified (rank 88/150), so equal-fit optima with different protected answers
coexisted and the solver path alone chose between them. The successor removes the first
property by construction — every colour is a function of path + corpus statistics + co-occurrence
structure, all invariant under injective renaming — and the battery then *measured* the second
property rather than assuming it: answers are unchanged under every probed solver family and
column order (5 probes, 0 moves) and under the checker's independent dense-matrix refits
(3 probes, 0 moves). An honest caveat recorded by the checker: the successor's train matrix is
itself rank 18 of 72, so what is identified is the *predictions*, not the weights; the stability
claim rests on the measured probes, not on full rank.

The cost is stated, not hidden: the profile colouring gives up value identity — tokens sharing
path and corpus statistics share one feature — an information reduction relative to the raw
bag, charged to E-PERF. E-PERF passed at exactly the recorded level anyway.

## Checker agreement

`invariant_profile_checker.py`, deliberately different implementation per freeze §8 — raw
tokens re-derived from `instance.model_payload(D1View.TYPED_SERIALIZED)["sequence"]`; base↔orbit
correspondence checked against the frozen `build_orbit_map` ground truth on raw payloads
(512 instances, 0 image failures); stability re-probed with a hand-built dense design matrix,
no `DictVectorizer`, no `Pipeline` (newton-cg and reversed order, 0 changed answers); guard
denominators and violations recomputed from raw payloads and recorded predictions (identical);
terminal logic re-derived from the artifact's own numbers (matches); frozen module twin digest
re-verified. All 8 checks green; disagreement would have been reported as a defect, not a tie.

## Non-claims

- `BOUNDED_D1_ONLY`: a statement about the D1 v1.2 classical-learner benchmark on its 128-case
  protected split and nothing else; no claim about any language model, any scale, any second
  model family, or issue #618.
- No claim about any frozen arm other than `TYPED_SERIALIZED_BAG`'s recorded defeat, which
  stands immutable.
- No claim that the successor is a better learner — only that it is a stable and
  format-invariant function of the same information.
- The frozen FP-2/FP-3 components re-run on the successor both return `CANNOT_CHECK` (no
  feature change for the guard to see), exactly as pre-registered; the invariance claim is
  carried by the companion raw-token guards with their 128-case denominator. Order-remint
  invariance at the raw layer has no denominator by construction (the transform is invisible
  to any token multiset; `P9_ORDER_PERMUTATION_IS_A_NOOP_2026-08-23.json` already records this
  for the frozen battery), so the successor's order-invariance is structural: its feature
  layer is a function of the multiset and length only.

## Disclosure appendix (2026-08-24, post-run, per freeze §7)

The battery module was executed twice. Between the two executions one output-shape extension
was added to the payload — per-case `gold` and `predictions` lists in the arms table — because
the independent checker's §8 commitments (guard arithmetic recomputed from recorded
predictions) require them. No parameter, probe, endpoint, threshold or number was touched:
both executions' terminal, endpoints, guard counts, stability counts, colouring statistics,
arms table numbers and `parameters_digest` are bitwise identical. The shipped result artifact
is the second execution's verbatim output. This appendix is the implementation-defect
disclosure path the freeze pre-registered; it is not a re-run under edited parameters.
