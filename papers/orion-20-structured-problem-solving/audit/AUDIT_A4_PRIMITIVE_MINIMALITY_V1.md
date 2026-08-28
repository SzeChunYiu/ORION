# A4 — Primitive minimality

`scientific_authority_delta = NONE` · detail file for
[`../THEOREM_PROOF_AUDIT_V1.md`](../THEOREM_PROOF_AUDIT_V1.md)

**Statement audited** (`PAPER_THEOREM_PACKAGES_V1.md:451-453`, proof
`PAPER_THEOREM_PROOFS_V1.md:239`): an expansion is inclusion-minimal when
removing any new primitive loses at least one protected new-reach target.
Cost-minimality is separately price-vector relative.

**Precise enough to be false?** Yes. The proof is a correct one-line
argument for inclusion-minimality of a *set* of added primitives: if a
primitive could be removed without losing a protected target it was
redundant, contradicting minimality.

---

## G-9 (major) — the manuscript states a different theorem than the one proved

`TOP_TIER_DYNAMIC_EPISTEMIC_MANUSCRIPT_V1.md:22` reads: "every **strictly
weaker registered edit** must fail for primitive minimality."

That quantifies over a *strength preorder on single edits*, not over
subsets of a set of primitives. The preorder is never defined; "strictly
weaker" is never given a meaning; and the proof of P10-T4 does not
establish it. The two notions coincide only under assumptions nobody has
written down.

Further, under set inclusion the studies' minimality is **vacuous**: both
add exactly **one** primitive, and with a one-element set, removing it
necessarily loses everything.

## G-10 (moderate, verified by recomputation) — the minimality rule is inert or near-inert

- **Setting B:** *[recomputed]* the `min_complexity_rank` tie-break **never
  fires**. Exactly one candidate (CUBE) passes the exactness test, so
  selection is fully determined before minimality is consulted. Ranks are
  frozen at `generated_ocme_cases_v1.json:33-37`.
- **Setting A:** *[recomputed]* `min_truth_table_hamming_weight`
  discriminates between exactly two survivors, codes 8 (weight 1) and 14
  (weight 3). That is a genuine but two-way tie-break.

Primitive minimality is therefore *defined* by the paper and *satisfied* by
the studies, but never tested against a case where a non-minimal edit could
have won.

## G-11 (moderate) — minimality is relative to an experimenter-supplied order

Both notions depend on a complexity order chosen by the experimenter:
`complexity_rank` at `generated_ocme_cases_v1.json:33-37`, Hamming weight
at `:18`. The formal package acknowledges the relativisation
("cost-minimality is separately price-vector relative",
`PAPER_THEOREM_PACKAGES_V1.md:453`). The manuscript headline does not carry
it. A different registered order can select a different "minimal"
primitive, and nothing in the corpus argues the chosen orders are
canonical.

## Degenerate cases

| Case | Handled? |
|---|---|
| Single primitive added | Vacuously minimal — see G-9; this is the actual situation in both studies |
| Two primitives, one redundant | Not exercised anywhere |
| Ties under the registered order | Setting A resolves by integer truth-table code; deterministic |
| Empty edit (no primitive) | Not addressed |
