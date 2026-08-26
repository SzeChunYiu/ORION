# P9-U-T4 successor freeze: the invariant-profile representation against the frozen format-prior attack class

Protocol id: `P9.D1T4S.INVARIANT_PROFILE_ROBUSTNESS`. Frozen 2026-08-24,
before any successor outcome was computed. §§1–9 are unchangeable after the
first successor result exists; a post-run disclosure appendix may be appended.

## 1. What this protocol is, and what it attacks

The frozen T4 campaign (`P9_U_T4_HOSTILE_ATTACK_RESULT_2026-08-21.json`)
ended in `T4_ATTACK_SUCCEEDED` on exactly one component:
`FP-2_SEMANTIC_ORBIT_INVARIANCE::TYPED_SERIALIZED_BAG` — the symbol-remint
semantic orbit moved 32 of 128 protected answers, 0.75 → 0.50. Every other
component passed or had no denominator.

This protocol registers the revival lane for that one component: a successor
representation, `TYPED_INVARIANT_PROFILE_BAG`, whose feature layer is
invariant under the frozen attack class by construction, plus the two
properties the frozen arm lacked and the defeat exposed:

- **R1 (invariance with a denominator).** The frozen guard goes
  `CANNOT_CHECK` when a transform changes nothing the arm can see; for a
  canonicalizing representation that is the expected verdict and cannot carry
  the claim. The claim is therefore measured one layer down, at the raw
  serialized token layer, with the frozen `GuardExercise`/`assess_guard`
  machinery: every protected case whose raw token multiset changed under the
  transform is an opportunity; every changed protected answer is a violation.
- **R2 (answer stability).** The one-stage attribution of the original defeat
  (`t4_defeat_diagnosis.py`, 2026-08-24) is `answer_determination_numerics`:
  the orbit is information-neutral (design matrices bitwise-equal up to one
  column permutation; renaming back reproduces the base fit bitwise), and on
  the *same* base feature dicts with no attack present, different multiclass
  solver families and pure column-order renamings each move 32 protected
  answers, with equal training fit, on a matrix with rank 88 of 150 columns
  and 318 duplicate column pairs. A successor whose features are identical
  but whose answers still flip across solver paths has not revived anything.
  Stability is therefore a first-class endpoint, not an appendix.

## 2. Claim scope, fixed now

`BOUNDED_D1_ONLY`, inherited verbatim from the frozen T4 freeze: whatever
this study returns is a statement about the D1 v1.2 classical-learner
benchmark on its 128-case held-out-domain protected split and about nothing
else. It licenses no statement about any language model, any scale, any
second model family, or the successor experiment of issue #618. It makes no
claim about any frozen arm other than `TYPED_SERIALIZED_BAG`'s defeat, and no
claim that the successor representation is a better learner — only that it is
a *stable and format-invariant* function of the same information.

## 3. The successor representation, fixed now

Module: `src/orion/study/p9/invariant_profile_representation.py`. Same
information source as `TYPED_SERIALIZED_BAG`: the typed serialized token
multiset and the sequence length. Nothing label-valued is read.

- **Corpus.** The train ∪ dev serialized-bag feature dicts of the dataset
  variant being run. No protected-split instance enters the corpus.
- **Initial colour** of a token `token:<path>=<value>`:
  `sha256("<path>|df=<df>")[:16]`, where `df` is the number of corpus
  instances containing the token. The raw value string never enters any
  colour.
- **Refinement.** `K = 2` Weisfeiler-Leman-style rounds. In each round, a
  token's new colour is
  `sha256("<old colour>|<canonical neighbourhood>")[:16]`, where the
  neighbourhood is the multiset of co-present token colours over corpus
  instances (the token itself excluded), canonically serialized as
  `",".join(sorted(f"{colour}x{count}"))`. Label-blind feasibility
  (2026-08-24, corpus structure only, no labels and no outcomes): 177 corpus
  tokens → 46 initial colours → 71 after round 1, stable through rounds 2–3.
  `K = 2` is one round beyond stabilization, chosen so that the colour
  partition is the stable one and not a truncation artifact.
- **Features.** `{"sequence_length": <n>}` plus `prof:<colour> = 1.0` for
  each distinct corpus token present. A token absent from the corpus maps to
  `prof:unseen:<path>`; such columns are zero on every training row by
  construction and are dropped by the vectorizer at transform time.
- **Invariance mechanism.** Under any injective renaming of value atoms,
  paths, document frequencies, counts and co-occurrence structure are
  unchanged, so every colour string is unchanged, so the feature dict is
  *bitwise identical* — not merely isomorphic. This was verified
  label-blind before the freeze on the frozen `BASE`/`SEMANTIC_ORBIT` pair
  at every `K ∈ {0,1,2,3}`.

What the representation gives up, stated now: value identity. Two tokens
with the same path and the same corpus statistics share a feature. That is
the point — value spelling is exactly the channel the frozen attack reminted
— and it is also a real information reduction relative to the raw bag,
charged to this protocol's performance endpoint rather than hidden.

## 4. Model grid, selection, execution path — frozen verbatim

`run_arm` from the frozen `hostile_representation_attacks` module, at its
public extension point `(dataset, dataset_id, arm_id, feature_fn)`: the
frozen `d1_experiment.model_specs()` grid, the frozen
`(-dev_accuracy, complexity_rank, config_id)` selection, the v1.2 runtime
adapter (`lbfgs` for logistic specs), the protected split untouched. The
frozen module's freeze-twin digest is re-verified inside the runner before
anything runs.

## 5. Batteries, registered now

### 5.1 Frozen battery re-run (verbatim functions, successor arm)

`run_arm` for `TYPED_INVARIANT_PROFILE_BAG` on all four frozen dataset
variants (`BASE`, `EQUAL_LENGTH`, `SEMANTIC_ORBIT`, `ORDER_PERMUTATION`),
rebuilt verbatim via `build_datasets()` with the shipped manifest digest
checked. The frozen `invariance_component` is invoked verbatim for
`FP-2_SEMANTIC_ORBIT_INVARIANCE::TYPED_INVARIANT_PROFILE_BAG` and
`FP-3_ORDER_REMINT_INVARIANCE::TYPED_INVARIANT_PROFILE_BAG`. The expected
verdict for both is `CANNOT_CHECK` (no feature change); that expectation is
recorded here and is *checked against*, not assumed — a non-`CANNOT_CHECK`
outcome is reported as found.

### 5.2 Companion raw-token guards (this protocol's R1)

For each of `SEMANTIC_ORBIT` and `ORDER_PERMUTATION`, and additionally for
`EQUAL_LENGTH` as an information-changing control:

- opportunities = the number of protected cases whose raw serialized token
  multiset differs between `BASE` and the variant;
- violations = the number of protected answers that differ between the
  successor's `BASE` and variant runs;
- verdict via the frozen `assess_guard(exercise, max_violation_rate=0.0)`.

The denominator is honest about the mechanism: the raw input changed on all
128 protected cases under the orbit, while the fitted canonical input is
bitwise unchanged — the guard measures whether the raw change reaches the
answers, which is precisely the claim. `raw_train_multisets_changed` is
recorded alongside.

### 5.3 Stability battery (this protocol's R2)

On the successor's `BASE` features, the full frozen selection loop is re-run
under each probe, and protected answers are compared to the protocol run:

- **solver family**: logistic specs fitted with `lbfgs` (the protocol path),
  `newton-cg`, and `sag` — same C, same `max_iter=2000`, same
  `random_state=2711`;
- **column order**: zero-padded key renamings inducing `identity`,
  `reversed`, and `seeded shuffle` (`numpy.random.default_rng(20260824)`)
  vocabulary orders; test-only keys absent from the train vocabulary keep
  their names (the vectorizer ignores them either way).

Probes are applied to the whole grid, so selection is probed too. Internal
consistency requirement: the `identity`/protocol probe must reproduce the
frozen `run_arm` answers exactly, or the battery reports a defect instead of
a verdict.

## 6. Endpoints and terminals, fixed now

- **E-INV (invariance)**: every companion guard in §5.2 holds with 0
  violations over its denominator (for `SEMANTIC_ORBIT` the denominator must
  be 128).
- **E-STAB (stability)**: every §5.3 probe changes 0 protected answers.
- **E-PERF (level)**: successor `BASE` accuracy ≥ 0.75 − 1/128 =
  0.7421875, and the arm is non-constant (more than one distinct protected
  prediction). 0.75 is the frozen campaign's recorded `TYPED_SERIALIZED_BAG`
  `BASE` accuracy; one case is the campaign's own resolution.

Terminals:

- `P9_T4_SUCCESSOR_REVIVED_STABLE` — E-INV ∧ E-STAB ∧ E-PERF.
- `P9_T4_SUCCESSOR_INVARIANT_BUT_LEVEL_NOT_RECOVERED` — E-INV ∧ E-STAB ∧
  ¬E-PERF. The published 0.75 is then attributed to solver-path numerics
  rather than to isomorphism-invariant structure; the lane closes
  CORRECTED with this protocol as the documented revival attempt.
- `P9_T4_SUCCESSOR_CANONICALIZATION_DEFECT` — ¬E-INV ∨ ¬E-STAB. The
  canonicalization or the stability fix failed on its own terms; no claim.

No terminal is reachable by tuning: `K`, the hash, the corpus, the probes,
the endpoints and the thresholds above are frozen by this document, and the
first execution's numbers are reported as produced.

## 7. Anti-tuning commitments

- The representation, guards, battery and endpoints are fixed by this freeze
  before the first successor outcome exists; the implementation commits
  precede the execution commit in the branch history.
- One execution. If a defect in the *implementation* (not the numbers) is
  found, the fix lands with a new dated freeze appendix stating what broke;
  numbers are never re-run under edited parameters.
- The frozen attack module, frozen protocol, frozen receipts and the D1
  v1.2 execution artifacts are read-only for this lane; only additive files
  under `src/orion/study/p9/`, this protocol directory, and the evidence
  directory are written.

## 8. Independent second checker

`src/orion/study/p9/invariant_profile_checker.py`, deliberately different
implementation: raw tokens re-derived from
`instance.model_payload(D1View.TYPED_SERIALIZED)["sequence"]` rather than
from the attack module's feature dicts; the base↔orbit correspondence
verified through the frozen `build_orbit_map` ground truth; the successor's
recorded feature dicts re-checked for bitwise base↔orbit equality; guard
denominators and violations recomputed from raw payloads and recorded
predictions; stability re-probed with a hand-built dense design matrix (no
`DictVectorizer`, no `Pipeline`) under `newton-cg` and a reversed column
order; the frozen module's twin digest re-verified. Agreement between runner
and checker is itself a reported outcome; disagreement is a defect, not a
tie to break.

## 9. What would falsify the revival

Any of: a non-zero violation in a §5.2 guard; any probe in §5.3 moving a
protected answer; the identity probe failing to reproduce the frozen
`run_arm`; the checker disagreeing with the runner on any guard number; or
the frozen module digest drifting. Each is reported as found, terminal
`P9_T4_SUCCESSOR_CANONICALIZATION_DEFECT` or the implementation-defect path
of §7, whichever applies.
