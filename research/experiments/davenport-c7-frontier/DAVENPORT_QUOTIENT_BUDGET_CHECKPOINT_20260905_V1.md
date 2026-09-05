# Davenport quotient-budget checkpoint — 2026-09-05 — V1

Status: **new structural proofs committed; full first corridor and generalized Davenport formula still open**.

This continuation starts from live `shadow/davenport-c7-frontier-20260903` at `7c2217e34bcee1a69469bc2541d2a13c86cea138`, which already includes the stronger work after the user's original `86f089ab` checkpoint. It was developed in this session's own checkout and branch `shadow/davenport-quotient-budget-20260905`.

The pre-work and pre-publication audits found the same 26 advertised Davenport branches. The paginated branch search was followed through its empty final page; the remote live branch still pointed to the reviewed starting commit. No other session's work was overwritten or reset. Publication identities are recorded separately in the accompanying receipt.

## 1. Main frontier advances

Write `p=2H+1>=7` and `m=3H+1`. The following statements concern the canonical maximal atoms and the inherited absence of nonempty zero-sums shorter than `m`, exactly as specified in their proof notes.

| Problem | New proved conclusion | Proof note |
|---|---|---|
| Rank-two type-two saturated boundary | No new value can have multiplicity `p-1`, at any positive light overlap | `A2_RANK2_SATURATED_BOUNDARY_FULL_ELIMINATION_V1.md` |
| Rank-two type-two `c=H-2` | Entire positive layer empty, for every prime | Same note, after `A2_RANK2_H_MINUS_TWO_RIGID_CUBE_REDUCTION_V1.md` |
| Rank-two type-two `c=H-3` | Entire positive layer empty, for every prime for which it exists | `A2_RANK2_H_MINUS_THREE_FULL_ELIMINATION_V1.md` |
| Rank-two type-one `p==3 (mod 4)` | Entire layer `c=(p+1)/4` empty, including unsaturated values | `A1_RANK2_QUOTIENT_BUDGET_AND_QUARTER_LAYER_ELIMINATION_V1.md` |
| Arbitrary rank-two type-two overlap defect | Entire layer empty whenever `2(H-c+1)` divides `p+1` | `A2_RANK2_MODULAR_SIGNATURE_AND_NEGATIVE_CLASS_ELIMINATION_V1.md` |

The previous whole-layer type-two result at `c=H-1` is retained and now has a shorter proof. Thus **three consecutive positive submaximal overlap layers, `H-1,H-2,H-3`, are empty**. The unsaturated top layer `c=H` is separate.

The intermediate rigid-cube reduction deliberately left a saturated endpoint open. It remains preserved as a historical proof advance; the later saturated-boundary theorem closes that endpoint. This is not an unresolved final claim in the current checkpoint.

## 2. The generalized structural form

The central advance is an exact positive budget for **every** quotient atomization, rather than a preferred scalar or factorization.

For type two, put `d=H-c>=1`, `R=x^r y^t`, and project the companion plane modulo the shared light line. For a quotient atom with actual length `ell_i` and canonical lifted sum `q_i s`, define `D_i=2q_i-ell_i`. Then

\[
\boxed{\sum_iq_i=p-c,\qquad
\sum_iD_i=d+1,\qquad 1\le D_i\le d.}
\]

There is no modular carry, and this holds throughout `1<=c<H` without an asymptotic restriction. The full parity-sensitive window applies to every proper quotient-zero part, including unions of atoms. See `A2_RANK2_EXACT_QUOTIENT_DEFECT_BUDGET_V1.md`.

There is also a second budget when `d^2<p`. With `a=d+1`, every atom has a positive signature `(D_i,h_i)` satisfying

\[
\boxed{
\sum_iD_i=\sum_i h_i=a,\quad
1\le D_i,h_i\le a-1,\quad
h_i p\equiv D_i\pmod{2a},\quad
\ell_i=\frac{h_ip+(a-1)D_i}{a}.}
\]

For fixed defect, this gives a normal form depending on the prime only through its residue modulo `2a`, together with the actual occurrence constraints. It is necessary, not an assertion that every formal signature is realizable. The negative residue class is excluded by a direct proof even when `d^2>=p`.

For type one and `c<H`, the same first-crossing principle gives

\[
\boxed{\sum_iq_i=p-c,\qquad
\sum_i(3q_i-\ell_i)=3H-2c+2,
\qquad 2\le3q_i-\ell_i\le3H-2c.}
\]

At `c=(p+1)/4`, the relation coefficient of this defect vanishes modulo `p`, while the permitted positive interval excludes multiples of `p`. That proves the new complete type-one layer.

These are generalized structural theorems. They are not the numerical all-prime, all-`k` Davenport formula.

## 3. Why atomization crosses the previous scalar barrier

The elementary theorem `CYCLIC_TWO_VALUE_RIGID_POWER_BOUND_V1.md` proves that if a two-value cyclic atom `Q=x^A y^B` is the only atomic divisor of `Q^k`, with `k>=2` and both total multiplicities below `p`, then

\[
k|Q|\le p+k-1.
\]

Equality forces one multiplicity of `Q` to be one and the other to be `(p-1)/k`. The proof constructs an explicit integer solution of `Ba-Ab=p` inside the occurrence rectangle when both multiplicities exceed one. No cyclic index theorem is needed for this rigid-power result.

Independently, `A2_ONE_MISSING_G_DONOR_INVERSE_CLASSIFICATION_V1.md` proves that the exact saturated-value inverse theorem remains valid with the actual rank-two donor `g^(p-2)`, rather than requiring `g^(p-1)`. The exceptional three-copy family and the four-copy `p=11` exception are retained, with their converses.

On a saturated rank-two row, the quotient window forces every relevant residue to be even. A modular progression therefore has no wrap, forcing the exact scalar-barrier form

\[
p=4rL+1,\qquad c=2rL+1-r.
\]

The smaller-donor inverse theorem then forces `y=(A,-A,1)`. The actual singleton `x` has a target fiber with

\[
w=p-2L-1,\qquad C=2L-1,
\]

so the original-donor depth envelope gives a zero-sum of length at most `p-1<m`. Thus the old scalar obstruction is overcome by mixed coordinate information, while the scalar-only obstruction itself remains correct.

## 4. Proof and dependency audit

The written proofs were checked by the producing researcher for properness of all quotient parts, every canonical representative, the sign and modulus of carries, all occurrence capacities, and the distinction between an atomization and rigidity. The inverse-extension audit checks each used certificate's `g` count and all exceptional prime/capacity cases. The cyclic exchange in the `H-3` proof checks the availability of the extra nonunit occurrence and the positivity of its remaining unit count.

The only external structural ingredients needed by the new complete type-two layer chain are the explicitly attributed Bernoulli-pairing theorem and, for one `H-3` residue class, the long cyclic-atom index theorem. Both were reopened in their primary sources:

- [Batyrev–Hofscheier, Proposition 1.8](https://arxiv.org/pdf/1004.3411).
- [Savchev–Chen, Section 5 and Proposition 10](https://arxiv.org/pdf/math/0602568).

The old `H-1` proof's Xia–Yuan splitting step and its Bhowmik–Halupczok–Schlage-Puchta multiplicity dependency are no longer required for that complete-layer conclusion through this new chain. Their earlier proofs and attribution remain preserved. No new prime, support-vector, or subsequence enumeration supplies any theorem authority.

Document checks cover local proof-reference existence, balanced display-math delimiters, accidental control characters, and clean diffs. Those checks validate the packet's integrity, not the mathematical conclusions. This is internal mathematical review, not an independent agent audit, external referee approval, or a novelty certificate.

## 5. Preserved failed routes

- A displayed power factorization does not imply that the power has only one atomic divisor; rigidity must be proved separately.
- A quotient atom's least-residue length formula cannot be applied silently to longer non-atomic parts. The saturated-boundary proof uses their coefficient relation and defect interval instead.
- The whole-new-value exchange at the cubic endpoint changes the maximal-atom length. It does not license a saturated maximal-quotient theorem. That failed route remains in the intermediate cube note.
- The scalar barrier remains an exact route obstruction and its companion relation remains atom-compatible. The mixed product is what the new proof excludes.
- The second signature weight is proved positive under `d^2<p`; this condition cannot be erased from its general statement. The negative congruence-class proof bypasses it directly.
- The prior global failures of greedy quotient atomization, unrestricted small-factor exchanges, and ordinary augmentation-degree arguments remain recorded in the first-principles checkpoint.

## 6. Exact remaining frontier

The rank-three exceptional `a=3` boundary was already completely eliminated on the starting live branch. The rank-three type-two saturated boundary was also already closed. The new rank-two saturation theorem now forces both ranks of the exceptional type-two support-six face to have **both new multiplicities at most `p-2`**.

Remaining local problems include the unsaturated rank-three type-two mixed-subsequence boundary, unsaturated rank-two type-two top overlap `c=H`, lower type-two layers outside the new and previously proved exclusions, and the other type-one high-overlap cases. Existing low-overlap and selector eliminations remain in force; this list does not reopen them.

Even complete resolution of those local cases would still leave the separate global first-failure, support, and factorization gates recorded in `DAVENPORT_FIRST_PRINCIPLES_CHECKPOINT_20260905_V1.md` and earlier frontier checkpoints.

**The full first corridor is not proved. Neither `D_3(C_7^3)` nor the full generalized Davenport formula is claimed.** The user requested proofs of everything; this checkpoint records substantial new proofs and the precise work that remains, rather than claiming that request is already mathematically fulfilled.
