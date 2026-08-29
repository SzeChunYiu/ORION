# ORION top-tier evidence contract V1

**Assessed base:** `87e2bcb330d243b7062ddba1ca26e426632edeab`  
**Authority created here:** `NONE`

A top-tier target is a scientific design constraint, not a label.  For every
ORION paper, the stronger claim must satisfy all of the following before the
manuscript is upgraded.

## 1. Claim and novelty

1. State one central claim with explicit quantifiers, scope and falsifier.
2. Subtract the strongest primary-source donor result claim-by-claim.
3. Separate generic shared mathematics from the paper-specific contribution.
4. Demonstrate a material consequence: a new theorem boundary, constructive
   algorithm, real-system safety/cost gain, or prospectively predicted transfer.
5. A null, counterexample, tie, contamination event or `CANNOT_CHECK` terminal
   remains load-bearing and cannot be rewritten as support.

## 2. Formal work

- The theorem statement must be independent of production code.
- Every hidden separability, completeness, finiteness, independence and
  measurability assumption must be explicit.
- Use an implementation-independent checker or proof assistant where feasible.
- Exact enumeration establishes only the frozen finite universe unless a proof
  extends it.
- One valid counterexample defeats a universal claim.

## 3. Empirical work

Before outcome access, commit:

- `QUESTION.md`;
- protocol and expected terminals;
- immutable corpus/task/version manifest;
- inclusion/exclusion rules;
- information-, action- and budget-matched baselines;
- primary/co-primary endpoints, margins and stop rule;
- unit of inference and uncertainty plan;
- resource accounting and adverse/CANNOT_CHECK log format.

The dataset, project, organization, model family, authority or real system—not
its thousands of rows, folds, calls or fault cells—is usually the transfer unit.
A large within-system census cannot manufacture external replication.

## 4. Reproducibility and authority

- Pin source versions, native verifier commands, environments and content hashes.
- Serialize per-unit outcomes needed to test every headline control comparison.
- Independent reimplementation improves reproducibility but does not create an
  independent investigator, institution, trust domain or scientific authority.
- Cryptographic integrity, execution liveness and scientific validity are
  distinct endpoints.
- Missing authority or missing bytes end in `CANNOT_CHECK`, not an inferred pass.

## 5. Statistical discipline

- Match the analysis to the actual unit of inference and dependency structure.
- Use paired analyses for paired tasks and cluster/hierarchical summaries for
  folds, examples, commits or cases nested in a transfer unit.
- Register primary outcomes and multiplicity handling before outcomes.
- Report estimates and uncertainty; do not rely on a threshold alone.
- Never move margins, denominators, comparators, task membership or outcome
  definitions after inspection.

## 6. Editorial gate

A promotion is earned only when the stronger result is technically sound,
well-supported, reproducible, clearly differentiated from prior work, and
important beyond the frozen toy surface.  If the stronger discriminator fails,
the bounded paper returns immediately to its strongest defensible venue.  A
failed promotion attempt is not a failed bounded paper.
