# ORION-03 — venue positioning

**Authority:** positioning only · `scientific_authority_delta = NONE` · submission authority `false`

Closes the positioning half of the Wave-2 box "Independent reproduction and final
JAR/TOCL-style positioning". The reproduction half is addressed by
`packages/typed-merge-evaluator/`.

## What the paper actually claims after the round-2 correction

The claim ledger R2 is the binding statement. Everything below is positioning on top
of it, not an extension of it.

**Formal core (PROVEN):** a positive conjunctive license calculus with a finite least
fixed point (D2-C1); authorization iff a finite untainted proof tree carries the claim
through every seed and cap (D2-C2); unsupported cycles stay bottom while seeded cycles
propagate (D2-C3); added refutations can only remove licenses (D2-C4); typed retraction
is uniquely minimal and well-founded (D2-C5); post-outcome rules cannot manufacture
prospective authority when the cap excludes it (D2-C6).

**Explicitly subtracted (D2-C8, DONOR-OWNED):** least fixed points, semiring
provenance, minimal supports and deletion robustness are **not** claimed as new. This
subtraction is load-bearing for venue fit and must survive into the cover letter.

**Not claimed:** arbitrary negation, probability or inconsistency (D2-C9, OPEN).
**Forbidden:** broad human-science usability (D2-C10) — no user study, no
cross-institution deployment.

## What the empirical sections may and may not be used for

`ROUND2_METRIC_STATUS_FINDING.md` establishes that the round-2
`precision = recall = 1.0` figures are **analytic identities** given
`m5_decision_equals_parent_authorization: true`, not measurements. They must not appear
in an abstract, a results table, or a cover letter as detector performance.

What the empirical work does support, and what the positioning should lead with:

1. **The obstruction is non-vacuous in deployed material.** 46 hybrid tasks in 1,962
   real X.509 trust-store merge tasks (~2.3 %), on third-party OpenSSL 3.6.4 test
   certificates with 268 digest-bound files. The formal object describes something that
   actually occurs.
2. **The naive baselines pay measurably different prices.** In `PARITY_PARTITION`:
   `M1_FLAT_UNION` 4 unsafe merges; `M2_INTERSECTION` and `M3_REJECT_ALL` 63 needless
   rejections each; `M4_OURS_B` 14. These vary by method and by family, so they carry
   genuine empirical content.
3. **Non-trivial invariants hold on the corpus**: `c3_violations = 0`,
   `c4_resurrections = 0`, `c4_upstream_mirrors_ok = true` — checks that could have
   failed.

## Venue fit

**Primary: Journal of Automated Reasoning (JAR).**
The paper's centre of gravity is a proof-carrying authorization semantics with a
uniqueness-and-minimality result for retraction, instantiated in two independent
implementations. JAR routinely carries calculi of this shape together with their
mechanisation, and it accommodates a paper whose empirical part is an existence-and-cost
demonstration rather than a benchmark win. The round-2 correction is survivable here
precisely because the contribution is the calculus, not detector performance.

**Fallback: ACM Transactions on Computational Logic (TOCL).**
TOCL fits if reviewers judge the contribution to be primarily the fixed-point/proof-tree
semantics and the retraction-minimality theorem, with the domain instantiations as
illustration. The fallback is a genuine change of emphasis, not a lower-effort
resubmission: under TOCL framing the X.509 material becomes an appendix-level
instantiation rather than a co-equal empirical section.

**Why not a security venue.** The X.509 material is real, but the paper makes no
attack, no threat model and no security claim — D2-C10 forbids deployment claims. A
security venue would read the trust-store work as the contribution and find it thin.
Positioning it there would invite exactly the misreading the round-2 correction exists
to prevent.

## The paragraph that has to be right

The audience question a JAR reviewer will ask is *what does this calculus decide that a
Datalog-provenance or truth-maintenance account does not already decide?* The honest
answer, and the one the paper must make explicit rather than imply: the **typed
retraction operator** and its uniqueness-and-minimality result (D2-C5), together with
D2-C6's statement that post-outcome rules cannot manufacture prospective authority. The
least-fixed-point machinery underneath is donor-owned and is credited as such.

If a reviewer shows that D2-C5 follows directly from an existing minimal-support or
deletion-robustness result, the paper's residual contribution collapses to the two
domain instantiations. That is the single most likely fatal review, and the novelty
audit should target it before submission rather than after.

## Status of the remaining package items

| item | status |
|---|---|
| Reusable evaluator | DONE — `packages/typed-merge-evaluator/`, 32 tests |
| External non-ORION domain | DONE — third-party OpenSSL 3.6.4 certs, 268 digests re-verified |
| Independent reproduction | DONE — committed round-1 and round-2 verdicts re-derived |
| Primary venue selected | DONE — JAR |
| Fallback venue selected | DONE — TOCL |
| Round-2 reframe applied to manuscript | **OPEN** — recorded in `ROUND2_METRIC_STATUS_FINDING.md`, not yet applied |
| Novelty audit targeting D2-C5 | **OPEN** — named above as the decisive pre-submission check |
| Submission manifest, cover letter, licence | **OPEN** |

The CLOSE-WHEN box stays open: the reframe must be applied and the D2-C5 novelty
question answered before the formal claim and the application form one coherent paper.
