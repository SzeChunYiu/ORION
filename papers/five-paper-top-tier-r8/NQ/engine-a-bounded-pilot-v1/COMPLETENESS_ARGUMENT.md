# Completeness argument and explicit gaps

## 1. Mathematical objects

Let `G = F_p^d`. An input sequence is `A=(a_1,...,a_n)` with repeated elements allowed.
A `k`-factor certificate is a tuple of nonempty, pairwise-disjoint index sets
`I_1,...,I_k` such that

\[
  \sum_{i\in I_j} a_i = 0 \quad (j=1,\ldots,k).
\]

Indices, not values, are assigned, so duplicate-heavy sequences retain correct multiplicity.

## 2. Per-input DP completeness

After processing the first `t` indices, a labelled assignment maps each processed index to
`unused` or one of `k` bins. A bin summary is `(u,s)`, where `u` records nonemptiness and
`s` is its partial sum. A DP key is the sorted tuple of all bin summaries. Sorting quotients
only the action of the symmetric group on indistinguishable bin names.

**Invariant.** After layer `t`, DP keys are exactly the bin-permutation orbits of all labelled
assignments of indices `0,...,t-1`; the retained payload reconstructs one assignment in each
reachable orbit.

- Base `t=0`: the unique assignment has all bins empty with zero sum.
- Step: index `t` is either unused or added to one existing bin. These are all possibilities.
  Assignments to bins with equal summaries are symmetric and therefore safely deduplicated.
  No other transition is removed.
- Induction gives the invariant for every layer.

The target key consists of `k` copies of `(used,0)`, exactly equivalent to `k` nonempty,
pairwise-disjoint zero-sum factors. Thus a recomputed target certificate proves a positive. If
all `n` layers finish and the target is absent, the invariant proves a negative for that input.
If a frontier resource limit interrupts any layer, no absence claim follows; the only terminal
is `CANNOT_CHECK_RESOURCE_BOUND`.

## 3. Canonicalization completeness under the locally declared group

For a multiset `S`, let `r` be the rank of its nonzero support and let `B(S)` be all ordered
`r`-tuples drawn from that support that form a basis of its span. For `B in B(S)`, express
each element in `B`-coordinates, pad with `d-r` trailing zeros, sort the coordinate multiset,
and call it `N_B(S)`. Define

\[
  C(S)=\min_{B\in B(S)} N_B(S).
\]

For any `g in GL(d,p)`, `B -> gB` is a bijection from `B(S)` to `B(gS)`, and coordinates
are preserved: `[gv]_{gB}=[v]_B`. Hence the candidate sets and minima agree, so
`C(gS)=C(S)`. Conversely, every candidate is obtained by an invertible linear map on the
span, extended to the ambient space. Therefore `C` chooses exactly one representative of
each orbit under the locally declared `GL(d,p)` action and sequence permutations.

## 4. Orderly raw-domain coverage

`combinations_with_replacement(G,n)` enumerates every length-`n` multiset over the finite
ordered group exactly once. Filtering on `S=C(S)` retains exactly one representative from
each local orbit. Coverage records bind the total raw-domain size, half-open raw interval,
number visited, number accepted, resume rank, and whether the full raw domain completed. A
slice or interrupted run is never labelled complete.

This is a mathematical completeness argument for the implemented raw enumerator. It is not a
claim of practical feasibility for the frozen full census.

## 5. Verification actually performed

- complete brute-force equality against a separate labelled-bin oracle on finite panels of
  `C_2`, `C_3`, and `C_2^2`;
- primitive arithmetic, rank, orbit invariance, idempotence, and tiny orderly-orbit controls;
- empty, singleton, duplicate-heavy, positive, negative, permutation, hostile-input, and
  certificate-mutation cases;
- deterministic manifest, schema, receipt-promotion, and tamper cases;
- permitted expected-outcome-exposed lower controls, including the two-but-not-three case.

## 6. Explicit completeness and authority gaps

1. **Normalization is bound, but enumeration semantics differ.** The frozen donor orbit slice is
   now formalized and machine-bound in `DONOR_NORMALIZATION_CONTRACT.json`. It retains every
   normalized image satisfying the ordered-anchor predicate; local `canonical_multiset` retains
   one lexicographic representative per GL orbit. `declared_donor_images` is the proved adapter,
   but no complete local class archive exists from which to expand the full donor family.
2. **Lossless augmentation is proved; target resources are not.**
   `CANONICAL_AUGMENTATION_PROOF.md` closes the construction-path, stabilizer-orbit, uniqueness,
   and hereditary-pruning obligations. Exhaustive small panels match the raw generator, but no
   target-scale resource bound, checkpoint partition, or complete class archive has been
   established. The full-execution terminal remains `NOT_EXECUTED__CANNOT_CHECK`; an interrupted bounded run emits `CANNOT_CHECK_RESOURCE_BOUND`.
3. **No frozen full census.** No full C5-cubed extremal archive, D3 extension census, or
   short-spectrum enumeration was run or accepted. Published expected counts were not used as
   tests, stopping rules, tuning targets, or acceptance criteria.
4. **No D3 reduction audit.** This tree does not prove that every length-25 obstruction has the
   enumerated core-plus-extension form, or that any proposed extension filter is lossless.
5. **No short-spectrum upper proof.** Per-input factorization completeness does not prove global
   nonexistence beyond a fully covered and correctly normalized generator.
6. **No independent status.** `ENGINE_B_EXPOSURE_IN_PRIOR_CONTEXT__CANNOT_CHECK` and
   `EXPECTED_OUTCOME_EXPOSURE` are permanent for this tree.
7. **No LUNARC/full-resource evidence.** No job was submitted and no resource envelope was
   widened. Any future limit exhaustion must remain `CANNOT_CHECK_RESOURCE_BOUND`.
8. **No publication-authority delta.** Tests, hashes, lower controls, and completeness arguments
   here do not establish novelty, peer review, D4, top-tier quality, or submission readiness.
