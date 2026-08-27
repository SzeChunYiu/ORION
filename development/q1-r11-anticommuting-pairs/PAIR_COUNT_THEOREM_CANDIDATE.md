# Q1 R11 anticommuting-pair count and direct-solver theorem candidate

Date: 2026-08-27

Status: **NON-AUTHORITATIVE THEOREM CANDIDATE**. Child of #1518 / #1511. This note changes no existing Q1 theorem, application terminal, manuscript authority, or V1 freeze state.

Subject base: `main@6d2d1699be7b5dfc1dd8b2721829b908ff4fb3d8`.

## 1. Exact ordered anticommuting-pair count

Let `P_2(n)` be the phase-ignored, nonidentity `n`-qubit Pauli strings of support at most two. The existing Q1 note counts

`|P_2(n)| = 3 n + 9 C(n,2)`.

For ordered pairs `(R,R') in P_2(n)^2` with symplectic product one, define `B(n)`.

### Proposition candidate

`B(n) = 54 n^3 - 108 n^2 + 60 n`.

### Derivation

Condition on the support of the first Pauli `R`.

**Weight one.** There are `3n` choices for `R`. If its unique active qubit is `q`, then an anticommuting `R'` must contain `q` with one of the two locally anticommuting letters.

- weight-one `R'`: `2` choices;
- weight-two `R'`: choose the second qubit in `n-1` ways, the anticommuting letter at `q` in `2` ways, and its nonidentity letter on the other qubit in `3` ways.

Hence each weight-one `R` has `2 + 6(n-1) = 6n-4` ordered partners.

**Weight two.** There are `9 C(n,2)` choices for `R`, on support `{q,r}`.

- weight-one `R'`: choose `q` or `r` and one of the two locally anticommuting letters: `4` choices;
- weight-two `R'` on the same support: the two local symplectic bits must have odd parity, giving `2*1 + 1*2 = 4` assignments;
- weight-two `R'` with exactly one shared support qubit: choose which of `q,r` overlaps (`2`), the outside qubit (`n-2`), an anticommuting letter on the overlap (`2`), and any nonidentity outside letter (`3`), giving `12(n-2)`.

Thus each weight-two `R` has `4 + 4 + 12(n-2) = 12n-16` ordered partners.

Therefore

`B(n) = 3n(6n-4) + 9 C(n,2)(12n-16)`

which expands to

`B(n) = 54 n^3 - 108 n^2 + 60 n`.

The formula gives `6, 120, 666, 1968, 4350` for `n=1..5`; the companion verifier independently brute-forces the complete support-<=2 Pauli sets for those sizes.

## 2. Candidate consequence for the frozen R6M grammar

The existing all-`n` Q1 theorem gives an optimum with six frame Paulis of support <=2. The frozen grammar groups those six slots into three ordered anticommuting frame pairs. Therefore the number of **legal pairwise frame choices before cross-branch/Tag/target filtering** is at most

`B(n)^3 = Theta(n^9)`,

not the looser raw-slot bound `[3n + 9 C(n,2)]^6 = Theta(n^12)`.

This is already a strict exact combinatorial tightening of the current candidate-family corollary.

## 3. Runtime theorem candidate

The current theorem-upgrade note also states that, for a fixed frame tuple, a minimum-cost compatible shared Tag need not act outside the union of the six frame supports. Under support two, that union has at most 12 qubits; naive Tag enumeration is therefore bounded by `4^12`, independent of `n`.

This suggests the stronger fixed-grammar algorithmic statement:

> After `O(n)` preprocessing of the target six-tuple for each constant matching/permutation/central-choice configuration, an exact direct solver can enumerate the three legal ordered anticommuting frame pairs in `Theta(n^9)` candidates and evaluate each candidate using only the at-most-12 active coordinates plus a constant-size Tag search. Hence the frozen six-slot R6M optimization problem admits an `O(n^9)` direct exact algorithm up to grammar constants.

**This runtime statement is not yet authority.** Independent review must verify that candidate evaluation contains no hidden `n`-dependent unrestricted-DP call, global scan, or oracle and that every candidate-dependent Restore/support/Tag term can indeed be reduced to a precomputed outside-union baseline plus O(1) active-coordinate corrections.

If that locality check fails, the retained result is only the exact `Theta(n^9)` legal-frame-candidate count; a straightforward full-coordinate evaluator would instead give `O(n^10)` from the same pair count.

## 4. Required hostile review

Before any claim-ledger or manuscript promotion, independently attack all of:

1. the closed-form pair count, including `n=1` and `n=2` edge cases;
2. the claim that each of the three frame pairs is locally anticommuting in exactly the same frozen grammar as the support-two theorem;
3. Tag confinement to the six-frame support union;
4. constant matching/permutation/central-choice multiplicity;
5. outside-union candidate independence of every Restore/Tag/support objective contribution;
6. absence of an `n`-dependent hidden solver/oracle during candidate scoring;
7. a support-one sharpness control and at least one support-two optimum that needs the weight-two sector.

Registered dispositions for #1518 should remain one of:

- `Q1_R11_EXACT_O_N9_DIRECT_SOLVER_THEOREM`;
- `Q1_R11_PAIR_COUNT_ONLY__RUNTIME_HIDDEN_DEPENDENCY`;
- `Q1_R11_RUNTIME_THEOREM_COUNTEREXAMPLE`;
- `CANNOT_CHECK_FROZEN_GRAMMAR_EVALUATION_COST`.

## 5. Prior-art boundary

The pair-count derivation is elementary finite Pauli combinatorics and should not be sold as a standalone novelty claim. Current work includes bounded-locality algorithms for counting anticommuting pairs in supplied Pauli collections and strong exact synthesis methods for Clifford/CNOT/phase-polynomial circuits. The possible Q1 contribution is narrower: a **sharp theorem-induced exact search exponent for this frozen R6M grammar**, if the runtime-locality proof survives.

No physical-resource, hardware-speedup, generic-TARE, generic-Pauli-compilation, or complexity-lower-bound claim is authorized by this note.
