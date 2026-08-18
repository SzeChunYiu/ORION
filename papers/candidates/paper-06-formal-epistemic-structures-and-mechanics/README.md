# P6 candidate — Formal Epistemic Structures and Mechanics

**Status:** PROPOSED / `CANNOT_CHECK` for distinct publishable novelty.

**Parent:** #332. Theory #333. Literature #334. Evaluation #335. Anti-overlap #343.

## Research question

Can the structural ideas already present in ORION—typed epistemic state, mechanic cells, obligations, authority bounds, dependencies, recursive audit, and selective reopening—be given a compact formal semantics that yields nontrivial properties, executable checks, or transfer value beyond P1's application-specific reconstruction paper?

## Candidate contribution

A typed mechanic is tentatively represented as an object with:

- readable and writable epistemic coordinates;
- preconditions and evidence obligations;
- transition semantics;
- emitted claims/obligations;
- authority bounds and forbidden mutations;
- failure/abstention terminals;
- provenance and dependency effects;
- composition rules with other mechanics;
- optional recursive self-audit semantics.

The candidate paper would study well-formed composition, mutation locality, non-escalation, dependency-scoped invalidation/reopening, provenance preservation, and bounded recursion/fixed-point conditions.

## Ownership boundary

P1 currently owns mechanic-cell and recursive-audit theory inside Recursive Epistemic Reconstruction. P6 is publishable only if #343 identifies a formal object/property/evaluation that is not merely a more abstract description of P1.

### Explicit nonclaims

P6 does **not** currently claim novelty for belief revision, dynamic epistemic logic, modular cognitive architectures, state machines, dependency graphs, provenance, reflection, failure attribution, typed process systems, or recursive reasoning individually.

## First nearest-work pressure

The initial literature pass already identifies direct parent domains: dynamic epistemic logic/action models; AGM and iterated belief revision; hyperintensional/incomplete-information revision; separation/dynamic logics; cognitive architectures for language agents; recent mechanism-level agent-architecture reviews; failure-attribution/debugging systems; planning/replanning work.

The hostile novelty question is therefore narrow:

> Is there a prior formalism that already couples typed failure/obligation responsibility to explicit read/write authority over epistemic coordinates, dependency-scoped reopening, and recursively composable mechanic contracts?

Until #334 answers that, novelty remains `CANNOT_CHECK`.

## Planned evidence

P6 must not stop at notation. #335 requires bounded theorem/checker artifacts, counterexamples, executable correspondence to selected ORION mechanics, and at least one discriminating comparison against an alternative formalization.

## Working manuscript

See `manuscript/DRAFT.md`. The abstract is intentionally written as a proposed research programme rather than a positive novelty claim.
