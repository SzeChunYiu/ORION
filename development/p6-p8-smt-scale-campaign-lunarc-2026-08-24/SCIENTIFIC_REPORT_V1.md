# P6/P7/P8 SMT calculi executed above CI scale on LUNARC

## Why this run exists

All three CI jobs install `.[dev,candidates]` and **never** the `proofs` extra, so `z3`
is absent and every theorem test degrades to a skip. `pyproject.toml`'s own comment
predicts the consequence: *a suite that silently skips them reports "no theorem failed"
for "no theorem was checked."* These calculi had never been executed in CI.

They need **no credentials, no model and no external benchmark data** — they are
self-contained formal verifications over the repository's own calculi, which is exactly
the shape that suits a batch scheduler.

## Result

`z3 5.1.0`, Python 3.11.5, LUNARC compute nodes, SLURM array `3534164`, repo head `59b103f`.

| paper | calculus | scale | CI default | theorems | agreement |
|---|---|---|---|---:|---|
| P6 | separation | node-count 6 | 5 | 5 PROVED | 31,104/31,104 frame-respecting |
| P6 | separation | node-count 7 | 5 | 5 PROVED | 172,928/172,928 frame-respecting |
| P7 | composition | 5,000 trials | 120 (**42×**) | 18 PROVED | 5,072/5,072 agree, both verdicts exercised |
| P7 | composition | 20,000 trials | 120 (**167×**) | 18 PROVED | 20,072/20,072 agree, both verdicts exercised |
| P8 | authority | 20,000 trials | 400 (**50×**) | 10 PROVED | 20,000/20,000 agree, 2,723 authorised |
| P8 | authority | 100,000 trials | 400 (**250×**) | 10 PROVED | 100,000/100,000 agree, 13,416 authorised |

**33 distinct theorems. Zero disagreements at any scale.**

For P6 the parameter moves only from 5 to 7, but the instantiation space it induces grows
combinatorially — 31,104 then 172,928 frame-respecting instantiations, every one checked.
Reporting the parameter multiple alone would understate it; reporting the instantiation
count is the honest measure.

`both verdicts exercised: True` matters as much as the agreement counts. It means the
differential test is not vacuous — both the positive and the negative outcome occurred, so
the agreement is not the artefact of a degenerate predicate. That is the failure mode that
killed P4's H3 metric, where a saturated statistic made eleven systems indistinguishable.

## What this does NOT close

No checkbox on #1086 is ticked by this run, and it should not be read as ticking one:

- **P8 — "Execute actual type-distinct native systems and ideal typed-product baseline."**
  This is calculus verification, not native system execution.
- **P8 — "Cover every ordered cross-system pair with clean and hostile cases."**
  Differential trials are not cross-system pairs.
- **P7 — "Use >=2 non-retrieval domains and >=50 transitions/domain."**
  SMT trials are not domains.

## Boundary

Strengthens the formal-verification evidence behind P6, P7 and P8 by executing their
calculi far beyond any scale previously run. Establishes no empirical result, no external
validation and no cross-system coverage.

## Still running when this was written

`p6.reopening_calculus_smt` at node-count 6, 7 and 8. Its default is 4; the search grows
exponentially, and those three tasks had not converged. Their absence here is a statement
about elapsed time, not about their outcome.
