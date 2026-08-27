# ORION-01 R11 Round-1 interpretation: contextual guard missing

## Terminal

```text
CANNOT_CHECK_MOVE_COMPLETENESS
```

This is an adverse scientific result, not a software-only failure and not a
null realized-gap result.

## What the prospective study found

The pinned PyZX source inventory is recoverable exactly: twelve automatic
state-mutating macro operations are called directly or transitively by
`full_reduce`, all sixteen load-bearing source files match their frozen
digests, and each one-entry registry omission is rejected by the AST audit.

That inventory is nevertheless **not a sound freely reorderable production
language under only the callable guards**. The 74th prospectively ordered input
word is

```text
H0, H0, H0
```

Starting from its public `Circuit.to_graph()` representation, the registered
prefix

```text
pivot_boundary_simp -> copy_simp -> to_gh
```

preserves the dense two-qubit linear map including scalar. A second registered
`pivot_boundary_simp` invocation is accepted and reduces the registered
resource from `(0,3,5)` to `(0,2,3)`, but changes the linear map even up to a
nonzero scalar. The predecessor and successor have SHA-256 identities

```text
fc217397673f7daf78672942239dfbb0c4596e5e07a3ff892b9003a0d60353c0
102babf6392e6d16136d262f967d49990a4075db36c39823b148de124ace038d
```

The matrix residual has maximum absolute entry `0.707106781187` and Frobenius
norm `1.53073372946`. This is not a rounding-only scalar discrepancy.

## Correct boundary

The counterexample does **not** show that the production `full_reduce`
scheduler is unsound. On the same input, the unmodified entry point preserves
the dense map including scalar. It shows that the scheduler context is a
load-bearing guard: the twelve callable operations cannot be detached from
their control-flow preconditions and then freely reordered as a sound complete
grammar.

Therefore neither a realized certificate gap nor the predeclared complete-
domain null is authorized. The run stops at its frozen semantics gate rather
than deleting the rule, narrowing the corpus, switching to equality-up-to-
scalar after seeing the result, or silently adding a scheduler context.

## Round accounting

This genuinely prospective public subject consumes ORION-01 Round 1 as
`ADVERSE_CANNOT_CHECK`. The same incomplete macro language may not be relabeled
as Round 2. ORION-01 remains scientifically open with two distinct rounds
available.

Round 2 must either:

1. use a public finite language whose stateful scheduler/context guards are
   source-complete and independently enumerable; or
2. switch to a scientifically distinct public grammar.

It must preserve this counterexample and may not retrofit `PYZX.FR.07` out of
the Round-1 registry.

## Authority ceiling

Established locally: one deterministic bounded counterexample to the proposed
free-reordering realization map at the pinned source commit.

Not established: generic PyZX unsoundness, a flaw in scheduled
`full_reduce`, all-PyZX or all-ZX completeness, a certificate gap, a bounded
null over 4681 words, compiler optimality or speedup, physical value, external
novelty, journal authority, or submission readiness.
