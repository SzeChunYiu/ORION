# P6-U GPT-R1 academic-paper-skills and framework audit

Date: 2026-08-20
Parent: #654
Base: `main@5ba828e9ff1e36636b3919f05031f0daffa33db7`

## Donor subtraction
Verified change-impact analysis, regression proof selection (iCoq/piCoq), incremental build/proof checking, dependency tracking, provenance and certificate invalidation are donor-owned. Palmskog, Celik & Gligoric formally verify dependency-graph change impact analysis in Coq and integrate it with proof selection/build tooling; iCoq/piCoq demonstrate fine-grained proof dependency selection. P6 novelty cannot be "recheck only affected nodes".

The surviving target is scientific responsibility-relative exactness: semantic support rather than mere reachability, alternative supports, representation/compiler state, responsibility changes, exact revocation/recovery and preservation of unaffected certificates across heterogeneous scientific objects.

## Reviewer 1 — theorem validity
- P6-R1-01: graph reachability is insufficient unless every edge is semantically load-bearing. Blocking: yes.
- P6-R1-02: uniqueness of a minimal set can fail with alternative equivalent revalidation actions. State theorem over a minimal equivalence class or define action semantics. Blocking: yes.
- P6-R1-03: exact minimality is impossible with incomplete hidden support. The theorem must state support-completeness/observability conditions and a safe over-approximation result otherwise. Blocking: yes.

## Reviewer 2 — prior work
- Generic CIA, regression proof selection and incremental verification are mature donors.
- The residual is a unified scientific semantics of support/responsibility/revocation spanning evidence, code, data, models, analyses, claims and compiled states.
- Existing 155 restorations / 1,055 strict-subset failures are finite witnesses, not theorem authority.

## Reviewer 3 — reproducibility/formalization
- Every theorem statement/assumption must be machine checked; examples cannot substitute for proof.
- Countermodels must be versioned and retained even after a stronger theorem succeeds.
- Empirical cost claims require real workflow units and matched restored-standing endpoints; revalidation actions, not repeated timing runs, determine scientific n.

## Framework consistency
The repository already carries dependency/reopen/protected-step verification substrate and the finite P6 evidence. Core `REOPEN.v1`, higher-order mechanic footprints, dependency/certificate structures and responsibility-aware state are consistent with the intended theorem. The manuscript is deliberately above current runtime: no registry object currently certifies a universal exact-minimal revalidation set for arbitrary scientific workflows.

Verdict: `CONSISTENT_AS_PROSPECTIVE_EXTENSION`.

## Negative-to-positive formal programme — Minimal Revalidation Closure (MRC)
MRC treats each counterexample as one of: hidden support, spurious support, alternative support, action-equivalence ambiguity, cycle/fixed-point issue, representation-only invalidation, responsibility change, evaluator-semantic change or non-realizability.

For each class:
1. freeze the countermodel;
2. identify the missing semantic primitive or prove it is information-theoretically unavailable;
3. strengthen the theorem with the minimal necessary condition, not an ad hoc exception;
4. prove soundness, minimality/equivalence-class minimality, unaffected conservativity and revocation;
5. recover the old finite result as a corollary;
6. test real-system cost savings.

If exactness is impossible without hidden support knowledge, the positive result is a sharp impossibility/lower-bound theorem plus the minimal additional information needed to regain exactness—not a false exactness claim.

## Broad terminal
`GENERAL_MINIMAL_SCIENTIFIC_REVALIDATION_THEOREM` requires machine-checked general statements, retained countermodels, finite predecessor corollary and prospective multi-domain savings with no false validity increase.
