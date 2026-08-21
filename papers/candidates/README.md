# ORION candidate-paper programme

This directory governs **prospective paper candidates**, not current flagship identities.

## Layout note (2026-08-21)

The candidate paper packages themselves — `paper-06-formal-epistemic-structures-and-mechanics/`, `paper-07-epistemic-navigation-open-worlds/`, `paper-08-epistemic-authority-autonomous-science/`, `paper-xx-executable-research-core/`, `paper-09-structured-epistemic-learning/`, `paper-xx-content-bound-math-evaluation/`, `paper-10-structured-problem-solving/`, and the shared P9/P10 lane `orion-learning-machine/` — now live directly under `papers/`. That is a directory move only: it does not promote any candidate to flagship identity, and every programme gate below still applies. This directory retains the shared cross-paper apparatus: the checkers (`checkers/`), the hostile review suite (`hostile_review_v1/`), the submission gate (`submission/`), the assumption-regression runner, the review/adjudication records, and the assumption-regression runner.

The q-lane candidates named in an earlier draft of this note — `paper-q1-tare-expressivity/`, `paper-q3-dual-instrument/`, `paper-q4-typed-state/`, `orion-q-recursive-recovery/` — are **not** here: the ORION-Q programme moved to its own top-level namespace as `../Q-paper-01-tare-expressivity/`, `../Q-paper-02-recursive-recovery/`, `../Q-paper-03-dual-instrument/` and `../Q-paper-04-typed-state/`. That namespace has its own numbering and its own issues, and is deliberately out of scope for the `P<n>-U` terminal adjudication in `src/orion/programme/`.

As of 2026-08-17, `papers/README.md` on `main` defines exactly five flagship papers. Nothing under `papers/candidates/` changes that publication identity rule. Promotion requires an explicit programme decision, novelty closure, prospective evidence, claim-ledger closure, and an integration PR that updates the canonical paper registry.

## Current candidates

| Candidate | Working title | Parent issue | Current authority |
|---|---|---:|---|
| P6 candidate | Formal Epistemic Structures and Mechanics | #332 / #333–#335 | PROPOSED / CANNOT_CHECK |
| P7 candidate | Epistemic Navigation in Open Worlds | #332 / #336–#338 | PROPOSED / CANNOT_CHECK |
| P8 candidate | A Theory of Epistemic Authority for Autonomous Science | #332 / #339–#341 | PROPOSED / CANNOT_CHECK |
| P9 candidate | Structured Epistemic Learning | #662 | `P9_BOUNDED_STRUCTURAL_LEARNING_SUPPORTED` / superiority terminal CANNOT_CHECK |
| P10 candidate | Structured Problem Solving | #663 | SUCCESSOR MANUSCRIPT / superiority terminal CANNOT_CHECK |

### P9 and P10 succession — 2026-08-21

The two rows above previously named *Executable Research Core* and *Content-Bound
Mathematical Evaluation* with "no issue yet". Both have since been superseded, and
both predecessor directories are **retained rather than removed**, because live
tests and other papers cite their results:

| Retired directory | Its own terminal | Why it is kept |
|---|---|---|
| `paper-xx-executable-research-core/` | `MERGED INTO P8/PROGRAMME`, no standalone manuscript | cited by `tests/unit/candidates/test_p9_p10_learning_machine.py`, by P8's benchmark companion, and by the `orion-learning-machine/` lane |
| `paper-xx-content-bound-math-evaluation/` | `TECHNICAL_NOTE_MERGED_INTO_P4_P8_PROGRAMME`, deliberately not a standalone paper | P10's predecessor evidence in the superiority ledger; cited by a live test and by the RSE wave-closure manifest |

This differs from the P1–P5 retirements in `../PAPER_ALIASES.md`, which were deleted
only because they "contained no independent manuscript content". These two hold
results, so the correct action is to label them, not to remove them.

The machine-readable form is `PAPER_DIRECTORIES` in
`src/orion/programme/superiority_terminals.py`, and `HC-SUP-STALE-PAPER-IDENTITY`
fails on any paper-numbered directory the registry does not know about.

## Shared gates

1. **Anti-overlap:** #343 must show a non-duplicative residual relative to P1–P5.
2. **Nearest work:** #318 assimilation + candidate-specific literature lane must saturate.
3. **Novelty authority:** #287 must authorize only the smallest surviving residual.
4. **Prospective falsification:** final benchmark/proof/evaluator identities must freeze before outcome access.
5. **Independent verification:** every promoted empirical positive routes through #283.
6. **Claim ledger:** #346 binds every headline statement to formal or empirical authority.
7. **Reproducibility:** #347 binds exact artifacts and deterministic replay/regeneration.
8. **Submission closure:** #344 refreshes literature within 14 days of submission; #345 selects venue only after the scientific object stabilizes.

## Programme thesis under test

The current five papers can be read as capability-specific epistemic transitions: reframing, searching/stopping, mapping/integration, asserting scientific authority, and self-modification. The candidates test whether there are publishable abstractions above those applications:

- P6 asks whether ORION mechanics admit a useful formal calculus of typed state transformations and recursive composition.
- P7 asks whether open-world research can be treated as navigation over an evolving epistemic topology, rather than fixed-space search.
- P8 asks whether the distinction between capability and authorization admits a reusable cross-capability authority calculus.
- P9 asks whether an agent can accumulate capability — mechanics, competence, contracts, retained failure — such that routing measurably improves while none of that accumulation becomes authority to act.
- P10 asks what must be content-bound for a mathematical claim to remain checkable, and what stays outside the evaluation harness entirely.

P9 and P10 entered the programme as a script bundle sharing one lane,
`orion-learning-machine/`, which still holds the framework, the experiments and the
committed results their predecessor directories cite. That paragraph described the
state before the succession recorded above: P9 now has a manuscript and a closure
receipt, and P10 has a merged bounded technical note plus a successor manuscript.

The original P10 headline remains a **null** — macros mined from real Lean source are
indistinguishable from shuffled tactic order — and is still recorded as the headline
rather than as a setback.

These are hypotheses, not novelty claims.
