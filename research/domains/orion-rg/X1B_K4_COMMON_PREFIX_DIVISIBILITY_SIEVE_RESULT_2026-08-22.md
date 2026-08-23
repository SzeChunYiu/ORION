# X1-B k=4 — first-factor divisibility sieve is structurally vacuous

Parent: #900.
Frozen protocol: `X1B_K4_COMMON_PREFIX_DIVISIBILITY_SIEVE_PROTOCOL.md`.
Committed before successor reframe.

## Exact result

Testing all 124 nonzero `t in C_5^3` gives:

- surviving elements: **124/124**;
- surviving projective one-dimensional subgroups: **31/31**;
- intersection dimension with the seven-dimensional common-prefix `I^10` affine space: **7 for every t**.

Thus imposing divisibility by one factor `(1-X^t)` removes no degree of freedom.

## Structural explanation

Let `J_t=(1-X^t)` and quotient the group algebra by `J_t`. Since every nonzero t has order 5,

`F_5[C_5^3]/J_t ~= F_5[C_5^2]`.

The augmentation ideal of `F_5[C_5^2]` has top nonzero degree

`2*(5-1)=8`.

Therefore the image of `I^10` in the quotient is zero, so

`I^10 subset J_t`

for **every** nonzero t.

Hence every element of the already-enforced `I^10` prefix space is automatically divisible by every single group-algebra factor ideal. This is a filtration theorem, not an accidental feature of the selected affine solution.

## Consequence

Single-factor divisibility cannot distinguish genuine ten-factor products at this filtration depth. Successor work must use one of:

1. simultaneous/multiplicity-sensitive factorization information beyond principal-ideal membership;
2. explicit ten-term sequence existence;
3. the equivalent subset-sum avoidance condition forced by the three residual pair extensions;
4. higher-order data retained by actual quotients/preimages during recursive division, not membership in one ideal alone.

No factor witness or C15 theorem follows.