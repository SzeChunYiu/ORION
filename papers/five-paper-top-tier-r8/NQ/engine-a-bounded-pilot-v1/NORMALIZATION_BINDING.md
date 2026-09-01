# Exact donor-normalization binding and local differential

> Binding terminal: `BOUND_MATHEMATICAL_NORMALIZATION`  
> Scientific/independence terminal: `CANNOT_CHECK`  
> Exposures: `EXPECTED_OUTCOME_EXPOSURE`,
> `ENGINE_B_EXPOSURE_IN_PRIOR_CONTEXT__CANNOT_CHECK`

This record binds the mathematical normalization declared by the frozen internal records. It
does **not** bind the full search grammar, reproduce the census, restore blindness, or create
scientific or publication authority.

## Frozen atoms

The exact subject object
`0c451e862a0eeddac7c673813c4dc499f134b088:development/orion-rg-davenport/X1F4_EXTREMAL_CLASSIFICATION_PROTOCOL_V1.md`
(blob `931a721c8748c28f894df6df56dbf50740c4277e`) states both required atoms:

1. the donor-normalized family consists exactly of rank-three multisets containing
   `e1,e2,e3` with `m(e1) <= m(e2) <= m(e3)`;
2. the class canonical form is the lexicographic minimum over ordered independent support
   triples, using the unique linear map sending the triple to `(e1,e2,e3)`.

Issue #916 fixes the equivalence action as `GL(3,5)` and sequence-position permutation. The
R8 manuscript calls the enumeration a basis and coordinate-permutation normalization.

## Contract

For a rank-three multiset `S` over `F_5^3`, define

\[
  \mathcal B_{\le}(S)=\{(b_1,b_2,b_3)\subseteq\operatorname{supp}(S):
  (b_1,b_2,b_3)	ext{ independent},
  m(b_1)\le m(b_2)\le m(b_3)\}.
\]

For `B in B_<=`, let `A_B` be the unique element of `GL(3,5)` with
`A_B(b_i)=e_i`. The declared donor slice is

\[
  N(S)=\{\operatorname{sort}(A_B S):B\in\mathcal B_{\le}(S)\},
\]

with equal image multisets deduplicated. Equal anchor multiplicities leave all corresponding
axis orders eligible; no unrecorded tie-break is imposed.

### Equivalence proof

Every constructed image contains the standard basis, and its anchor multiplicities equal the
source-basis multiplicities, hence satisfy the declared inequality. Conversely, let
`Y=gS` be any orbit image satisfying the pointwise donor predicate. Then
`B=(g^{-1}e1,g^{-1}e2,g^{-1}e3)` is an ordered independent support triple whose source
multiplicities satisfy the same inequality. Both `g` and `A_B` send `B` to the standard
basis, so uniqueness gives `g=A_B`; therefore `Y` is emitted. Thus the adapter is sound and
complete for the declared orbit slice.

## Crucial local differential

The frozen donor family is **not one representative per GL orbit**. It retains every distinct
orbit image satisfying the anchor condition. By contrast, local `canonical_multiset` returns
one lexicographic minimum per GL orbit. They serve different roles:

- `canonical_multiset(S)`: class key, one value per GL orbit;
- `declared_donor_images(S)`: complete donor-normalized slice of that orbit;
- `NormalizationWitness`: an ordered source basis binding each emitted image;
- `verify_normalization_witness`: primitive recomputation of basis membership, rank,
  multiplicity order, coordinate image, and pointwise predicate.

Given a complete duplicate-free archive containing exactly one local canonical representative
per GL class, the disjoint union of `declared_donor_images` over that archive is exactly the
donor-normalized family. This statement does not assert that such an archive exists here.

## Hostile and differential controls

The frozen binding receipt records:

- strictly ordered anchor multiplicities: one donor image;
- equal multiplicities plus a residual point: multiple retained images, proving the adapter
  does not silently collapse to one-per-orbit semantics;
- deterministic invertible-map and input-permutation round trips: zero mismatches;
- dependent, reversed-multiplicity, absent-support, truncated-image, and mutated-coordinate
  witnesses: zero hostile acceptances;
- wrong group and rank-deficient sources: rejected or empty as required.

See `DONOR_NORMALIZATION_CONTRACT.json`, `NORMALIZATION_BINDING_RECEIPT.json`, and the two
normalization JSON Schemas. Published full counts are absent from all test targets, stopping
rules, and tuning conditions.

## What remains blocked

The mathematical normalization is now bound. Execution remains invalid for the frozen full
claim because this tree still lacks a complete canonical class archive, target-scale resource
feasibility/checkpoint evidence for the proved augmentation grammar, the short-spectrum/D3
structural generators, and a complete donor-slice range manifest. No full census or LUNARC job was run.
