# General-formalism checkpoint for `D_k(C_p^3)` — V1

Status: **research checkpoint with proved reductions and exact bounded receipts**. No claim that the final defect inequality has been proved.

## Expert-lens convergence

The four active lenses now agree on one object.

1. **Additive/factorization lens:** replace the family of questions in `k` by the defect envelope `max_B(|B|-p z(B))`.
2. **Affine-semigroup lens:** delete pure `p`-blocks to enter a finite Apéry box; atoms are Hilbert-basis columns and defect is minimum excess cost.
3. **Graver lens:** a counterexample is exactly an above-threshold factorization terminal under every positive-gain conformal move.
4. **Geometry/coding lens:** shortest or first-level cores are `p`-short-zero-free, so projective-direction and plane deficits constrain the bounded positive codeword before atom or move enumeration.

## Exact formalism

For `G=C_p^3`, `p>=5`, put

`M_p=(5p-5)/2`.

Then the proposed formula

`D_k(G)=kp+M_p` for every `k>=2`

is equivalent to the single global inequality

`|B|-p z(B)<=M_p`

for every zero-sum block `B`.

It is also equivalent to absence of a `p`-short-zero-free box factorization whose minimum atom-excess cost is larger than `M_p`, or equivalently an above-threshold factorization with no applicable positive-gain Graver move.

See `PACKING_DEFECT_CORE_FORMALISM_V1.md`.

## First-counterexample shell

If the formula first fails at factorization length `m`, write the overshoot as `q>=1` and a maximum atomic factorization as `U_1...U_m`. With `e_i=|U_i|-p`, every proper atom subproduct is controlled by a lower-level Davenport value. Consequently

`q<=e_i<=2p-2`,

`sum e_i=M_p+q`,

and

`(m-1)q<=M_p`.

Thus both `m` and `q` lie in a finite arithmetic shell before any group vectors are generated.

At `p=7`, independent recursive and multiplicity-vector checkers give exactly 322 raw shells, with the corrected distribution beginning `m=3:63`, `m=4:64`. Zhang's `s_{<=12}=26` plus the six exact `(m,q)=(3,1)` corridors reduce the cover to 301 signatures.

See `PACKING_DEFECT_MINIMAL_CORE_SIGNATURES_V1.md`.

## Existing `C_7^3` closures inside the formalism

A length-37 packing obstruction is the `(p,m,q)=(7,3,1)` slice. The campaign has already eliminated:

- every support-seven realization;
- every support-eight realization with one doubled projective direction;
- the binary-cube support;
- all scalar choices outside the line-fiber avoidance grammar in the two maximal-atom corridors.

The smallest geometric residual is support eight on eight distinct projective directions, over the existing 347 surviving projective classes after the Property-C deficit filter.

## Missing theorem

The remaining general theorem can be stated without reference to `k`:

> Every `p`-short-zero-free positive bounded kernel vector over `C_p^3` with terminal atom-excess cost above `(5p-5)/2` admits a positive-gain conformal decomposition move.

A proof may proceed by showing that deficit incidence forces one of a bounded family of local projective configurations and that each configuration supplies either

- a short/medium zero-sum insertion whose complement retains the required packing length;
- a two-atom refactorization detected by restricted subsums;
- a coding-theoretic support split; or
- an explicit positive Graver move.

## Next exact discriminator

The next bounded computation should not enumerate arbitrary zero-sum sequences. It should take each surviving support-eight Type-A projective class, enumerate only positive box kernels compatible with the `(7,3,1)` excess signatures, and ask for a positive-gain move or a four-block conformal split. Any survivor must be retained as a complete primitive-core certificate, including its projective class, scalar lift, multiplicity vector, optimal factorization and failed move list.

## Claim boundary

The general formalism is found and exact. The central inequality is still a theorem target. No novelty, priority, open-status or global Davenport-value assertion is authorized by this checkpoint.