# AB hostile-review cross-audit and minimal safe integration

## Disposition

**Terminal:**
`AB_THEOREM_REPAIR_PARTIAL_PASS__T10_CONVENTION_REQUIRED`

Reviewed hostile-audit commit:
`82e94b19b9b79733bd5353cb433e48fe338e4423`, tree
`a81360e61b5c4bfed9a45009f419b77f01735a18`. Its scientific subject is
`0c451e862a0eeddac7c673813c4dc499f134b088`, tree
`dbf96cce53d21d25584479fb740473293fae75e0`.

The hostile audit is materially useful and most theorem dispositions survive.
Its proposed Theorem 10 repair is nevertheless incomplete. A nonempty source
alphabet does not ensure that any nonzero kernel sum is realized. For

\[
H=K=C_2,\qquad \phi=\mathrm{id},\qquad A=\{1\},\qquad
\ker(\phi)=\{0\},
\]

the alphabet is nonempty, but the realized nonzero-kernel alphabet is empty.
The manuscript must therefore define \(Z_\omega=0\), attained by the empty
kernel word, whenever no nonzero kernel sum is realized.

`MINIMAL_SAFE_INTEGRATION_PATCH.diff` adds that convention. It also contains
only the narrow repairs supported by this cross-audit and the primary-source
donor subtraction described below. It was exported from the detached review
worktree and passed `git apply --check` against the exact reviewed commit.

## Theorem-by-theorem ceiling

| Object | Cross-audit verdict | Safe interpretation |
|---|---|---|
| T1 | `PASS_WITH_STATED_BOUNDARIES` | Attainment, persistent sound deletion, and persistent dominance remain material. |
| T2 | `REPAIR_VALID` | Require at least one nonzero alphabet element so the terminal universe is nonempty. |
| T3 | `PASS_WITH_STATED_BOUNDARIES` | The complete move-map and direct irreducibility conditions are alternative bounded transfer certificates. |
| T4 | `PASS_WITH_STATED_BOUNDARIES` | Axis separation is material. |
| T5 | `PASS_WITH_STATED_BOUNDARIES` | Requires Cartesian feasibility, complete semantic support, and additive size. |
| Corollary 6 | `PASS_WITH_STATED_BOUNDARIES` | Numerical monotonicity is set-theoretic; soundness controls interpretation. |
| T7 | `PASS_WITH_STATED_BOUNDARIES` | Standard independent cyclic generators and exact orders are material. |
| Multiplicity form | `PASS_FINITE_REFORMULATION_ONLY` | Exact finite restatement only; no complexity conclusion. |
| T8 | `PASS_WITH_STATED_BOUNDARIES` | Requires a homomorphism and the exact realized image alphabet. |
| T9 | `REPAIR_VALID` | A nonempty source alphabet repairs the displayed atom maximum. |
| T10 | `REPAIR_INCOMPLETE` | The review must also cover an empty realized nonzero-kernel alphabet; the integration patch does so. |
| T11 | `PASS_WITH_STATED_BOUNDARIES` | Nonnegative `epsilon` is clarifying but redundant for the conclusion. |
| T12 | `REPAIR_VALID_WITH_WORDING_CORRECTION` | Require `delta>=0`, deletion-only descent without reactivation, and “support at most `z`.” |
| Pauli R8 | `PASS_BOUND_SEPARATE_GRAMMAR_ONLY` | No novelty, Q1, physical-resource, or journal-authority delta. |
| T13 | `PASS_INTERNAL_CALIBRATION_ONLY` | Complete destructive XOR grammar only; no external realization. |
| T14 | `REPAIR_VALID_FOR_BLOCKWISE_EXTENSION` | Fixed-budget asymptotic survives; blockwise multiplication needs a Cartesian-product enumerator with local budgets. |

## Primary-source donor absorption

Boyar, Matthews, and Peralta, *Logic Minimization Techniques with Applications
to Cryptology*, DOI `10.1007/s00145-012-9124-7`, gives a fixed linear
straight-line-program instance with unrestricted optimum four versus
cancellation-free optimum five and a factor-`3/2` lower bound for
cancellation-free methods. Find and Boyar, *Cancellation-Free Circuits in
Unbounded and Bounded Depth*, DOI `10.1016/j.tcs.2014.10.014`, proves
asymptotically larger cancellation-free versus unrestricted XOR-circuit gaps.
Exact cached PDF hashes are bound in `SOURCE_BINDINGS.json`.

Those sources absorb the broad claim that a stronger XOR/cancellation language
can strictly beat a restricted one. They do **not** faithfully realize AB.
A straight-line-program step adds `u xor v` while retaining reusable operands;
AB fusion removes both operands. No primary source audited here supplies a
bidirectional representation/move/terminal/cost map for that destructive
multiset grammar.

The R8 harness notes and search records are bound only as non-authoritative
provenance. They are not primary-source, novelty, mathematical, venue, or
journal authority.

## Preserved adverse boundaries

- QMAP remains `CANNOT_CHECK` as an AB external realization because its native
  moves are invertible, fixed-cardinality tableau transformations with an
  accumulating gate/depth cost.
- T13 remains an internal exact calibration.
- The Pauli replay remains a separately declared grammar.
- AB-specific external significance and novelty remain `CANNOT_CHECK`.
- No runtime, state-volume, hardware, physical-resource, Q1, journal, or
  top-tier inference is authorized.

