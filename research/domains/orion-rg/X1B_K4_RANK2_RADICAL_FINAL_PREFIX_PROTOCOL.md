# X1-B k=4 — prospective final prefix protocol for R2R-11 and R2R-12

Parent: #900.
Reduction: `X1B_K4_RANK2_RADICAL_CENSUS_AND_CONTAINMENT_RESULT_2026-08-22.md`.

## Evidence status

**PROSPECTIVE FROZEN DISCRIMINATOR.** No length-10 existence result for R2R-11 or R2R-12 has been computed before this packet is committed.

## Frozen forbidden sets

Use the canonical `GL(3,5)` representatives encoded by group index `25x+5y+z`.

### R2R-11

`(0,1,2,5,6,10,25,26,46,65,111)`

### R2R-12

`(0,1,2,5,6,10,25,26,30,34,53,107)`

Both contain zero.

## Exact question

For each class determine whether there exists a ten-term sequence T over `F_5^3` such that every nonempty subset sum of T avoids the frozen forbidden set.

## Primary enumeration

Use the already proved exact illegal-state quotient

`I(T)=F-Sigma_0(T)`

with transition

`I(Tx)=I(T) union (I(T)-x)`.

Enumerate the terms in one fixed nondecreasing ordering of the 124 nonzero group elements. At fixed depth and identical I, the proved minimum-last dominance may retain only the smallest reachable last index.

No `GL(3,5)` stabilizer normalization is assumed unless separately audited before outcome.

## Confirmation

- A YES requires an explicit ten-term witness and primitive subset-sum replay.
- A NO intended for theorem use requires an independent verifier that does not use the layerwise state merging/minimum-last dominance.

## Scientific interpretation

- NO for both R2R-11 and R2R-12 eliminates all remaining rank-2 radical realizations.
- Since the rank-3 branch is already independently eliminated, that would close the complete k=4 residual interface.
- A YES is a finite block-sum obstruction only; it does not constitute a 43-term C15 counterexample and restores original-index realization.

## Authority boundary

Even if k=4 closes, `D(C_15^3)=43` still requires the separately developed k=3 branch to receive its canonical harness/independent proof receipt and then a full proof assembly audit.