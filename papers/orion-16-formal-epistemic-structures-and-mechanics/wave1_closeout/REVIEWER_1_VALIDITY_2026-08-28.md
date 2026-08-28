# Reviewer 1 — validity, formal methods and inference

## Posture

**Major revision; the current claims are not independently established.**

## Strengths

- The manuscript preserves the damaging discovery that the earlier propagation
  assertions were tautologies.
- It withdraws three quantities that could not discriminate the claimed
  theory.
- It states load-bearing assumptions and supplies countermodels when they are
  dropped.
- It keeps finite enumeration, theorem support and empirical authority
  separate in principle.

## Major concerns

### R1-16-001 — independent theorem review is absent

The general commutation, propagation and certificate-lifting results are
checked by programme-authored formalizations. The manuscript explicitly says
that independent proof review remains outstanding. The same programme also
designed the interpretation connecting the general theory to the bounded
model. **Resolution test:** an independent reviewer reconstructs every theorem
statement and proof obligation from the mathematical definitions, checks the
closure/rank axiomatisation and lift interpretation, and records either a clean
pass or exact corrections.

### R1-16-002 — trusted-base sufficiency is not reader-checkable

The exact theorem relies on a programme-authored kernel plus solver
cross-checks. The current prose names implementation modules rather than giving
a compact mathematical trusted-base argument. **Resolution test:** a standalone
proof appendix exposes all axioms, inference rules, residual hypotheses and the
translation used by the solver, with independent replay that does not import
the generating proof logic.

### R1-16-003 — current reproduction fails before theorem closure

The documented `make reproduce-v4` path stops because the first retained
negative/null-history row has a stale or missing source binding. Later checks
therefore did not execute in that clean run. **Resolution test:** repair by
adding a current binding without rewriting adverse history, then execute the
complete path in a clean environment.

## Boundary

The report does not refute the mathematical contribution. It finds that the
current evidence cannot support a verification-complete submission state.
