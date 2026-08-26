# Mathematical Extensions R6 — Symmetry-Reduced Cross-Move Audits

Date: 2026-08-26

Canonical predecessors: `MANUSCRIPT_V3_PIPELINE.md`, `MATHEMATICAL_EXTENSIONS_R4.md`, and `MATHEMATICAL_EXTENSIONS_R5.md`

Status: rigorous theorem addendum with exhaustive finite fixtures. It closes the abstract audit method for product witnesses. It does not supply the missing production witness for the current compiler example.

## 1. Argument and boundary

R5 proved that independent product exactness can fail as soon as a legal cross-component move is added. The remaining practical question was how to audit a large, symmetric family of such moves without checking every instantiated rule separately.

This addendum proves that a product witness can be audited orbit by orbit under any symmetry group that fixes the witness and acts equivariantly on the rule system. A single representative then certifies every cross rule in its orbit. A hostile family of pair-deletion moves shows the sharp boundary: one bad orbit can collapse a `t`-component terminal witness from size `t` to size one.

The theorem reduces a finite production-rule audit. It does not replace the need to enumerate the actual production rule schemas or establish that the candidate component states are genuine production terminal witnesses.

## 2. Symmetric extended products

Let `P_i` be finite shortening systems with size functions `|.|_i`. Suppose `x_i` is terminal in `P_i`, with size `beta_i`. Let

`x=(x_1,...,x_t)`

be the product witness, of size

`|x|=sum_i beta_i`.

Let `P^+` contain all componentwise moves and a finite family `C` of cross-component shortening rules.

Let a finite group `Gamma` act on states and rules. Assume:

1. **state-size invariance:** `|gamma y|=|y|`;
2. **rule equivariance:** `y ->_r y'` if and only if `gamma y ->_{gamma r} gamma y'`;
3. **witness stability:** `gamma x=x` for every `gamma in Gamma`; and
4. **cross-rule closure:** `C` is a union of `Gamma`-orbits.

The third condition may be replaced by the stabilizer subgroup of `x`; only that subgroup is relevant to the local witness audit.

## 3. Orbit-representative theorem

**Theorem B11 (symmetry-reduced cross-move audit).**

Choose one representative from every `Gamma`-orbit in `C`. If no representative is applicable to `x`, then no cross-component rule in `C` is applicable to `x`. Consequently, `x` is terminal in `P^+`.

**Proof.** Assume some cross rule `r` is applicable to `x`. Let `r_0` be the selected representative of its orbit, so `r_0=gamma r` for some `gamma`. By equivariance,

`x ->_r y`

implies

`gamma x ->_{gamma r} gamma y`.

Witness stability gives `gamma x=x`, and `gamma r=r_0`. Thus `r_0` is applicable to `x`, contradicting the representative audit. Componentwise rules are also inapplicable because every `x_i` is terminal. Hence no shortening rule applies to `x`. ∎

**Corollary B12 (exact product lower witness).**

Under the hypotheses of Theorem B11,

`beta(P^+) >= sum_i beta_i`.

If the componentwise normalization argument still gives the matching upper bound for every state of `P^+`, then equality holds.

The upper-bound premise is separate. A terminal lower witness cannot certify a global normalization theorem that the cross rules may invalidate.

## 4. Audit compression

**Corollary B13 (orbit-count audit cost).**

The witness-local cross-rule audit requires one applicability check per orbit of the stabilizer of `x`, rather than one check per instantiated cross rule.

This is a finite proof-compression statement, not a claim about the asymptotic runtime of arbitrary compiler optimization. The useful quantity is the number of rule-schema orbits after all semantic side conditions are included.

## 5. Sharp hostile family

**Proposition B14 (symmetric pair-deletion collapse).**

For every `t>=2`, there are `t` component systems with terminal complexity one such that:

1. their independent product has terminal complexity `t`;
2. the symmetric group `S_t` acts transitively on all cross rules; and
3. adding that single rule orbit reduces terminal complexity to one.

**Proof.** Each component has an empty state and a one-token state `x_i`, with no component move reducing `x_i`. The independent product witness containing all `t` tokens is terminal, so its terminal complexity is `t`.

For every unordered pair `{i,j}`, add the cross rule that deletes both tokens whenever components `i` and `j` are occupied. The family is one `S_t`-orbit. Every state with at least two occupied components admits a pair deletion, while states with zero or one occupied component are terminal. The maximum terminal size is therefore one. ∎

This generalizes the two-component counterexample from R5. Symmetry makes the hostile family easier to audit, not less destructive.

## 6. Positive finite fixture

The R6 verifier also evaluates a four-component system with all six unordered cross-pair schemas but a side condition requiring one occupied and one empty component. At the all-occupied product witness, the single orbit representative is inapplicable; by Theorem B11, all six rules are inapplicable, and terminal complexity remains four.

Replacing the side condition by pair deletion makes the representative applicable and reduces terminal complexity to one. Exhaustive enumeration of all sixteen binary product states verifies both conclusions.

## 7. Production audit protocol

A production realization should now be checked in the following order.

1. Freeze one longest abstract component witness and its proposed production realization.
2. Enumerate every production rule schema that can touch more than one component, including shared auxiliaries, frame changes, global reconstruction, and cleanup rules.
3. Compute the stabilizer of the realized product witness, not merely the symmetry of the benchmark layout.
4. Partition the cross schemas into stabilizer orbits after semantic guards are included.
5. Check one representative from every orbit for applicability and shortening.
6. Independently replay the matching global normalization upper bound.

Disjoint qubit labels or disjoint input files do not establish independence if the production proof language contains a global rule.

## 8. Consequence for certificate waste

The certificate-waste vector from R5 remains a mathematically exact comparison of separately defined budgets. It becomes a production enumeration exponent only after:

- every component budget is realized in the production proof language;
- the product witness passes Theorem B11’s cross-move audit; and
- the production enumerator actually explores the declared labeled-support volume.

The orbit theorem makes the second gate finite and reviewable. It does not silently discharge the first or third gates.

## 9. Academic positioning

The paper’s strongest defensible form is now a theorem-and-audit paper about certificate composition, not a universal compiler speedup paper. The argument order should remain:

`abstract certificate budget -> exact product law -> cross-move failure -> symmetry-reduced audit -> production realization gate -> architecture-specific search consequence`.

Claims of a factor-five production certificate or an architecture-independent runtime lower bound remain outside the evidence.

## 10. Atomic status

- Symmetry-reduced cross-move theorem: `VERIFIED`.
- Orbit-count proof compression: `VERIFIED`.
- Symmetric pair-deletion collapse for all `t>=2`: `VERIFIED` constructively.
- Four-component positive and hostile fixtures: `FINITE_EXACT`.
- Exact abstract cyclic-axis budgets and waste constants: retained from R5.
- Factor-five production certificate: `UNRESOLVED`.
- Production cross-rule inventory: `MISSING_EXTERNAL_ARTIFACT`.
- Architecture-independent runtime claim: `NOT_CLAIMED`.

## 11. Remaining scientific frontier

The abstract composition theory has reached a clean stopping point. The next meaningful result must be a production witness plus a frozen cross-rule inventory. A successful orbit audit would convert the current conditional lower witness into a production theorem. A failed audit would be equally informative because it would identify the exact global rule responsible for collapsing the abstract certificate budget.
