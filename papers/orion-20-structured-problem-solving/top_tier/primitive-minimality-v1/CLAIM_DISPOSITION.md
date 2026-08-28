# Claim disposition — ORION20.PRIMITIVE_SUFFICIENCY_MINIMALITY.v1

Protocol and theory frozen at `051f578a0` before any outcome was read.
Terminal: **T3_PROMOTION_FAILS__NO_UNIQUE_MINIMUM**.
Status: **PROMOTION_STOPPED__RETURN_TO_BOUNDED_LANE**.

## Result

| | |
|---|---|
| affine codes (frozen basis) | 8 of 16 — `[0,3,5,6,9,10,12,15]` |
| admissible primitives | **`[8, 14]`** — AND and OR |
| minimal bases | `{8}` and `{14}` |
| **indispensable primitives** | **none** |
| minimum under registered order (popcount) | code `8`, **unique** |

`G_UNIQUE` holds. `G_INDISPENSABLE` **fails**. `G_DONOR` therefore fails by its frozen
operationalisation, which required *both*.

## Why indispensability fails — the exact mechanism

The committed template is `T_p(x,y,z) = p(x,y) ⊕ p(x,z) ⊕ p(y,z)`, and the target is
`majority3`.

For AND this is the classical identity `maj = xy ⊕ xz ⊕ yz`. For OR, write
`x ∨ y = x ⊕ y ⊕ xy`; then

    (x∨y) ⊕ (x∨z) ⊕ (y∨z) = (x⊕x) ⊕ (y⊕y) ⊕ (z⊕z) ⊕ (xy ⊕ xz ⊕ yz) = xy ⊕ xz ⊕ yz.

Each variable appears in exactly two of the three pairs, so the linear parts cancel and OR
lands on the same function as AND. **The template is blind to the affine difference between
AND and OR.** Two distinct non-affine primitives therefore realise the target, the minimal
bases are `{8}` and `{14}`, and their intersection is empty.

So the frozen expansion is *a* minimal expansion, not *the* minimal one. The registered
complexity order does single out AND uniquely — but that is a property of the **order**,
not a structural necessity of the problem, and certification of minimality was the only
candidate delta over the donor.

## The donor gate, and why it was decisive

The donor was named before the computation: Post's lattice (1941), the affine functions
forming a clone, and ANF degree deciding affineness. Sufficiency — that a non-affine
primitive is required and that AND supplies it — is entirely donor-owned.

`G_DONOR` was operationalised in advance to survive **only** on a unique minimum *together
with* a nonempty indispensable set, so that the expansion is provably the minimal
admissible one. With indispensability empty, nothing remains that a clone-theoretic reader
does not already hold.

Per #1649 the promotion **stops here**. ORION-20 returns to the bounded formal lane. No
second rescue cycle is started, and the 16-code vocabulary is **not** enlarged — #1649
explicitly forbids enlarging formula size or operators over an unchanged vocabulary as a
route to promotion, and doing so here would in any case not create indispensability.

## Prediction versus outcome

The protocol predicted `T2_PROMOTION_FAILS__ENTAILED_BY_DONOR`. The actual terminal is
`T3`. Both are unfavourable and both stop the promotion, but the mechanism differed from my
prediction: I expected the result to dissolve into classical sufficiency facts, and instead
it failed on a sharper and more specific point — the template's blindness to the AND/OR
affine difference. Recording that the prediction was right in class and wrong in mechanism
is part of the result.

## Controls

- **Z1** — the ANF test returned exactly 8 affine codes of 16.
- **Z2** — no affine primitive realises the target, so the expansion premise is not vacuous.
- **Z3** — a planted non-realising primitive is reported insufficient by the same test.
- **Z4** — the recomputed admissible set `[8, 14]` matches the **committed runner's own**
  selection logic exactly, and its selected code `8` is a minimiser. This packet quantified
  the frozen object rather than re-modelling it.

## What is NOT retracted

Nothing. The OCME non-vacuity results, the generated finite OCME evidence, and the
historical negative and donor-closed evidence stand exactly as frozen. This packet adds a
failed promotion attempt and its reason; it removes nothing.

## Authority

`MEASUREMENT_AND_PROOF_ONLY`. `scientific_authority_delta: NONE`. No submission authority.
Outcomes were read once.
