# ORION-20 candidate — Content-Bound Mathematical Evaluation

**Status:** SCRIPTS AND RESULTS LANDED / HEADLINE RESULT IS A NULL / NO MANUSCRIPT / NOVELTY `CANNOT_CHECK`
**Shared lane:** `../orion-learning-machine/`

## Research question

When an agent claims a mathematical result, what has to be bound so the claim can be checked later — and what stays outside the evaluation harness entirely?

## Candidate contribution

`FrozenMathTask` (`../orion-learning-machine/framework/orion_learning_machine/math_eval.py`) is a content-bound evaluation subject: the task statement, its source, and the source revision hash together into `statement_sha256`, so an attempt is bound to the exact statement it answered and a later edit to the statement is detectable.

The module states its own limit: *"ORION-20 uses this as an evaluation harness only; theorem correctness and claim authority remain outside ORION-20."* The harness binds identity. It does not decide whether a proof is right.

`bind_verifier_receipt` attaches an external verifier's decision to an attempt without the harness adjudicating it — the same shape as ORION-14's protected evaluator boundary.

## Evidence that exists

### Phase 2A — macro mining on real Lean source (`../orion-learning-machine/results/PHASE2A_RESULTS.json`)

Run over a committed corpus of 7 Lean files from two donor repositories (`YuanheZ/lean-stat-learning-theory`, `auto-res/lean-rademacher`). Byte-identical on re-run.

| | Value |
|---|---|
| Mechanics absorbed | 11 |
| Mechanics attested by both donors | 6 |
| Macros mined | 12 |

**The headline is a null, and it should stay the headline:**

| Macro order | Observed | Shuffle mean | Shuffle SD | Empirical p(≥obs) |
|---|---|---|---|---|
| bigram | 5 | 5.632 | 1.204 | **0.829** |
| trigram | 1 | 0.644 | 0.748 | 0.500 |

Against a 1000-rep shuffle null, the mined bigram macros are **less** frequent than chance and the trigram result sits at p = 0.50. **Tactic-sequence macros mined from this corpus are not distinguishable from shuffled tactic order.**

That is a real negative result on real source, and it is the most informative thing in this lane. It says the macro-mining mechanic — which phase 1 shows working on synthetic tasks — does not transfer to this Lean corpus. Whether that is the mechanic, the corpus size (7 files), or the abstraction level is exactly the diagnosis worth running next.

### Phase 2B — goal effect: **cannot run**

`run_phase2b_goal_effect.py` requires `HF_MATHLIB_TACTICS_SAMPLE.json`, which is **not in the bundle**. This is `CANNOT_CHECK`, not a failure: the code exists, the data does not. No result is claimed for the goal-effect question.

## Ownership boundary

- **ORION-14** owns protected scientific-authority promotion and independent verification. ORION-20's `bind_verifier_receipt` defers to that boundary rather than replacing it.
- **ORION-18** owns the authority calculus.
- ORION-20's object is narrower than either: content-binding an evaluation subject so an attempt cannot be silently re-pointed at a different statement.

### Explicit nonclaims

ORION-20 does not claim novelty for autoformalization, Lean/Mathlib tooling, theorem-prover benchmarks, tactic prediction, premise selection, or proof-step evaluation. It makes no claim about the correctness of any theorem in the corpus.

## What does not exist yet

- **No manuscript**, no claim ledger, no `JOURNAL_READINESS.md`.
- **No nearest-work pass** — novelty is `CANNOT_CHECK`. The theorem-proving evaluation literature is large and unexamined here.
- **Corpus is 7 files from 2 repositories.** Far too small to support a general claim about Lean sources; it is adequate only for the null actually reported.
- **Phase 2B has no data**, so the goal-effect question is untested.
- **No verifier has been run.** `bind_verifier_receipt` is exercised by unit tests with synthetic receipts; no real Lean verification has been bound.

## A gap in the bundle's own closure claim

`VERIFY_LOCAL_CLOSURE.sh` asserts `manifest['authority'].startswith('LOCAL_CORE_COMPLETE')` and checks `closure_logs/FROZEN_SHA256SUMS.txt`. **Neither `CLOSURE_MANIFEST.json` nor `FROZEN_SHA256SUMS.txt` is in the bundle**, so the verify script cannot run and the `LOCAL_CORE_COMPLETE` authority it asserts is not verifiable from what was delivered. `SCRIPT_MANIFEST_SHA256.txt` *does* verify — 36/36 files — so the source is bound even though the closure claim is not.

## Reproduce

See `../orion-learning-machine/REPRODUCE.md`.
