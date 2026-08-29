# Formal proof and algorithm audit

Date: 2026-08-28

## Scope audited

The audit covers the manuscript definitions, correction-exchange lemma, zero-sum-subset lemma, global support reduction, sharpness witness, ordered-pair count, active-union argument, shared-operator minimization and complexity bound. It does not assess physical resource value or novelty.

## Definition consistency

- Pauli phases are consistently removed only for support, commutation and factor-cost calculations.
- The local factor cost is `w(a)+w(b)+w(c)-2` exactly when all three letters are the same nonidentity Pauli.
- Every frame is nonidentity, each block pair anticommutes, and the shared syndrome is exactly `(1,0)` or `(0,1)` in every block.
- The complete normalized objective is the six frame charges `m*(w(A)-1)`, shared charge `2w(S)`, and two branchwise three-way correction factors per coordinate.
- The normalized frame charge subtracts the fixed raw baseline 18, so it preserves all optimizers and fixes the displayed absolute-cost convention.
- A central-frame coordinate refunds 2 support units and a noncentral coordinate refunds 4.
- The support restriction applies to each of the six frame Paulis; all target-order, central and label choices remain available.
- The paired-target instance is the base grammar. Searching all 15 pairings of six unpaired inputs is only a constant-size outer extension.
- A global branch swap quotients eight target orders to four relative orders; the heavier frame receives multiplier 2; and a minimum-weight compatible shared operator suffices. These reductions preserve the exact minimum.

## Correction-exchange lemma

Changing one correction letter from `pf` to `p` changes the ordinary nonidentity count by at most one. If no old three-way discount is destroyed, the factor-cost increase is at most one. If the old discount is destroyed, `pf` was nonidentity and equal to the other two letters; then `p` is either identity or another nonidentity letter, so the ordinary count cannot increase and the lost discount contributes at most two. Therefore the increase is at most 2. The standalone checker exhausts all 192 local cases and observes maximum 2.

**Decision:** valid for every affected branch and coordinate.

## Zero-sum-subset lemma

For each supported coordinate of frame `A`, the class records its local anticommutation contribution with `A'` and its shared-label contribution with `S`. A zero class gives a removable singleton. A repeated nonzero class gives a removable equal pair. If neither exists at support at least three, the only possible support-three multiset contains the three nonzero classes once each, whose first coordinates sum to zero, contradicting global anticommutation. At support greater than three, pigeonhole repetition already applies.

**Decision:** valid; the subset is nonempty and proper, with size at most two.

## Global support reduction

Removing the subset preserves frame-pair anticommutation and the shared-label syndrome. Properness preserves a nonidentity frame. At each removed coordinate, the frame refund is at least 2 and the correction increase is at most 2. The same shared operator remains feasible. Cost cannot increase, while total frame support strictly falls. Termination follows from a nonnegative integer measure. Family containment supplies the reverse optimum inequality.

**Decision:** the all-size support-two theorem follows for the declared grammar/objective.

## Sharpness audit

The reader-facing instance, with the qubit-0 letter written first, is

```text
(XI, XI), (XI, XI), (IX, IY).
```

The direct solver was independently rerun in this closeout. The support-two optimum is 5 with frame/shared/correction components 2/2/1, using frame pairs `(YI,XI)`, `(YI,XI)`, `(ZX,IY)`, shared operator `XI`, central choices `(0,0,0)` and label orientation `(1,0)`. All witness-verification predicates passed. Exhaustive support-one optimization returned 6 and all support-one witness checks passed.

The support-one search is complete over 12 ordered anticommuting one-coordinate pairs per block, their Cartesian cube, four relative target orders after global branch-swap symmetry, two label orientations and every minimum-weight compatible shared operator. Central assignments are minimized analytically; all of them tie when both frames have support one.

**Correction made during audit:** an intermediate prose draft misread mask-pair evidence as dense Pauli strings and wrote the third target pair incorrectly. The published source now uses `(IX,IY)`, which reproduces the exact 5-versus-6 result. No incorrect version is in the final PDF/package.

## Pair count and complexity

- Weight-one first frame: `2 + 2*3*(n-1) = 6n-4` partners.
- Weight-two first frame: 4 weight-one partners on active coordinates, 4 weight-two partners on identical support, and `12(n-2)` partners with one shared coordinate, totaling `12n-16`.
- Multiplying by first-frame counts gives `54n^3-108n^2+60n` ordered pairs.
- Anticommutation forces pair supports to overlap; a pair union has size at most 3 and three pair unions at most 9.
- Shared-operator letters outside that union affect no symplectic equation and add positive cost, so a minimum is confined to the union.
- The six syndromes give a 64-state dynamic program over at most nine coordinates.
- Six explicit `n`-qubit targets have `Theta(n)` Pauli-letter input length in the stated word-RAM representation.
- Three ordered-pair choices therefore cost `O(n^9)` after linear target preprocessing; storing the pair universe gives `O(n^3)` working memory.

**Decision:** the stated word-RAM upper bounds are valid as constructive exact-solvability bounds. No same-problem asymptotic improvement, lower bound, exponent optimality or measured acceleration follows.

## Proof terminal

`FORMAL_SCOPE_GREEN`

This is a same-project formal audit corroborated by executable checks, not external peer review or proof-assistant certification.
