# Q1-A R9 Phase-2 registered-proof comparison

## Phase ordering receipt

Phase 1 was locally committed as `dcf642b091f4a11fcaa97f583cb9e0598c883777` before the registered proof content was added to the sparse checkout or read. That commit contains the independent theorem reconstruction, dependency DAG, exact two-qubit sharpness enumerator, tests, and Phase-1 machine receipt.

Phase 2 then opened frozen registered proof:

- path: `papers/Q-paper-01-tare-expressivity/HUMAN_PROOF_R6S_2026-08-22.md`;
- Git blob: `a22754e8afef0e9914b75b37f0aee673ccd2ca95`;
- SHA-256: `ad4f3704cfac4569b74725cb8608ed5f5ba88b847d2d8a2820b3e184d9d1dae6`.

No registered ORION-Q solver, canonicalizer, support checker, or result receipt was read. The comparison is proof-to-proof only.

## Typed terminal

`PROOF_RECONSTRUCTED_EQUIVALENT`

This terminal is limited to the claim-ledger-owned frozen statement: exact optimum equality under the R6M three-block shared-one-bit-Tag grammar and its exact support-count objective, plus the sharp uniform threshold `kappa_R6M=2`. It does not import the registered proof's strongest wording into the claim ledger and does not confer external independence, novelty, production-resource meaning, or journal authority.

## Comparison order and first disagreement

Comparison order was fixed as: (1) theorem quantifiers and terminal; (2) local deletion-signature lemma; (3) feasibility preservation; (4) local Restore inequality; (5) objective descent; (6) global termination/equality; and (7) sharpness.

### First disagreement: `D01_CLAIM_QUANTIFIER_STRENGTH`

- **Independent Phase 1:** states the frozen ledger claim existentially: every admitted instance has at least one exact optimum with frame support at most two.
- **Registered proof:** starts with the stronger pointwise normal form: every feasible configuration can be transformed without increasing cost to frame support at most two.
- **Adjudication:** no effect on the frozen ledger claim. Both prove exact optimum equality. The stronger pointwise wording is not promoted into the ledger by this internal audit. The independent local exchanges appear sufficient to derive it, but Phase 1 deliberately terminated at the ledger-owned quantifier.

This is preserved as the first disagreement rather than aligning the Phase-1 theorem statement after registered-proof access.

## Node-by-node comparison

| ID | Independent Phase-1 node | Registered proof | Relation | Effect on frozen ledger claim |
|---|---|---|---|---|
| `D01` | Exact-optimum existence (`U1`) | Nonincreasing transform of every feasible configuration (Theorem) | registered wording stronger | none |
| `D02` | Proper zero-sum deletion has size at most **3** (`L2`) | Proper zero-sum deletion has size at most **2** (Lemma B) | registered lemma stronger | none; both give a proper support-reducing exchange and the objective bound is coordinate-additive |
| `D03` | Two-bit signature `([R,Q],[R,S])` | Class `(alpha,beta)=([R,R'],[S,R])` | equivalent up to symmetric Pauli commutation notation | none |
| `D04` | Arbitrary change of one Restore donor raises `F3` by at most 2 (`L4`) | Specific zeroing-induced change `p f -> p` raises `F3` by at most 2 (Lemma E) | independent local inequality stronger | none |
| `D05` | Preserve nonidentity, partner parity, Tag parity, assignment, central branch, other blocks (`L3`) | Same parity and nonidentity preservation; all other grammar constraints unchanged (section 4) | equivalent | none |
| `D06` | `Delta C <= -(m-2)|D|<=0` (`L5`) | `Delta C <= sum(2-m)<=0` (section 5) | algebraically equivalent | none |
| `D07` | Iterate from an exact optimum until all supports are at most two (`L6`) | Same descent plus both restricted/unrestricted inequalities (section 6) | equivalent on ledger claim | none |
| `D08` | Fresh explicit n=2 targets and independent exact enumeration: `5<6` (`W1`--`W2`) | Refers to exact R6O support-one counterexample `5<6` without listing the target words (section 7) | same numerical sharpness; evidence path structurally different | none; external validation still absent |

### Why the deletion-cardinality disagreement is nonmaterial

Phase 1 used the universally valid but looser observation that among any three signatures, a zero, a duplicate pair, or the three distinct nonzero classes supplies a zero-sum subset; the last case is proper only when more support remains. The registered proof adds a pigeonhole step: with support greater than three, a nonzero class must repeat, and with support exactly three the three-distinct case contradicts odd partner parity. Thus size at most two is valid.

A Phase-2 regression enumerates signature sequences of lengths three through seven and confirms the largest minimum proper deletion size under odd partner parity is two. That finite regression is a hostile check, not the all-size proof; the registered pigeonhole/parity argument provides the all-size step.

## Sharpness evidence comparison

The Phase-1 lower witness is independently explicit:

- targets `A=(ZI,XZ)`, `B=(IX,IZ)`, `C=(IZ,IZ)`;
- unrestricted two-qubit optimum `5`;
- support-at-most-one optimum `6`;
- support zero infeasible;
- exact clean-room min-plus enumeration with duplicate targets, central-choice ties, target-permutation ties, and all phase-free two-qubit Paulis admitted.

The registered proof cites the same cost gap through R6O but does not expose target words. No registered result receipt was opened, so identity of the concrete registered witness beyond the stated costs is `CANNOT_CHECK`. Equality of numerical costs is agreement, not evidence independence.

## Hostile controls and residual boundaries

- A changed registered-proof byte fails the SHA-256 binding.
- Removing odd partner parity revives the full-triple-only zero-sum control and breaks the proper deletion lemma.
- Reducing a frame multiplier below two breaks the objective exchange.
- Adding a deleted-letter feasibility predicate, amplitude-dependent target admission, a phase-sensitive semantic rule, simultaneous multi-frame repair, or Tag repair creates `SCOPE_MISMATCH` unless proved separately.
- Production-resource conversion, physical architecture, novelty, external quantum review, and journal authority all remain `CANNOT_CHECK`.
- The lower-witness enumeration is internal clean-room corroboration. It is not external independent validation.
