# Lossless canonical-augmentation and pruning proof

> Engineering terminal: `CANONICAL_AUGMENTATION_SMALL_DOMAIN_EQUIVALENCE_PASS`  
> Full-execution terminal: `NOT_EXECUTED__CANNOT_CHECK`  
> Independence terminal: `CANNOT_CHECK`

The proof below concerns the implemented finite grammar. It does not claim that the frozen
full target fits the allocated resources, reproduce a census, restore independence, or change
scientific or publication authority.

## 1. Objects and canonical parent

Let `Gamma=GL(d,p)` act on finite multisets over `G=F_p^d`. Let `C(S)` be the exact local
canonical form already proved invariant and complete under this action. For nonempty `S`, set

\[
  P(S)=Cigl(C(S)\setminus\{\max C(S)\}igr),
\]

where one occurrence of the lexicographically largest element is deleted. Because `C` depends
only on the orbit, `P` is an invariant map from a child orbit to a unique parent orbit.

## 2. Exact stabilizer extension orbits

Let canonical parent `Q` span the first `r` coordinate axes, denoted `W`. Choose a reference
ordered basis `R` from `supp(Q)`. Any intrinsic automorphism of `W` preserving `Q` is uniquely
determined by the ordered independent support tuple to which it sends `R`. The implementation
enumerates every such tuple, constructs the induced linear map, and retains it exactly when
the mapped multiset equals `Q`.

This is complete: a true stabilizer maps `R` to an enumerated independent support tuple. It is
sound: every retained map is invertible on `W` and passes exact multiset equality. The retained
actions therefore give the exact stabilizer orbits on elements of `W`.

If `r<d`, all elements outside `W` form one additional orbit. To see this, write two outside
elements as `w+u` and `w'+u'` relative to `W` and a complement. A block map fixing `W`
pointwise can choose an invertible quotient map sending `u` to `u'` and a complement-to-`W`
shear sending `u` to the required difference `w'-w`. This subgroup preserves `Q` and maps the
first outside element to the second. Thus the inside stabilizer orbits plus one outside orbit
are exactly all extension orbits.

## 3. Canonical construction path

Assume level `n-1` contains exactly one canonical representative of every admissible orbit.
For each parent `Q`, select one element from every exact stabilizer orbit, form `Q+x`,
canonicalize it, and retain the child only if its canonical parent is `Q`. Store retained
children in a set keyed by canonical form.

### Soundness

Every output is a canonical multiset. It has the declared parent, and all configured exact
constraints return `ALLOW`. Set insertion makes duplicate canonical forms impossible.

### Completeness

Let child orbit `X` be admissible, with canonical representative `T=C(X)`. Delete the declared
maximum occurrence and let `Q=P(T)`. Heredity makes `Q` admissible, so induction supplies `Q`
at the preceding level. An isomorphism mapping the deleted submultiset to `Q` sends the deleted
element to some `x`, hence `Q+x` lies in `X`. The stabilizer orbit of `x` has a selected
representative `r`; applying that stabilizer sends `Q+x` to `Q+r`, still in `X`. Canonicalizing
therefore produces `T`, and `P(T)=Q` passes the acceptance test. No child orbit is dropped.

If multiple canonical augmentation edges reach `T`, canonical set insertion collapses them.
Thus the completed level contains exactly one representative per admissible orbit. The empty
level is the base case, proving the claim for every completed length.

## 4. Lossless pruning

Two predicates are permitted:

1. no nonempty zero sum of size at most a declared cutoff;
2. no `k` pairwise-disjoint nonempty zero sums.

Both are hereditary under deletion. The first is decided by exact weight-indexed subset-sum
DP; the second by the exact multi-bin factorization DP. Therefore every parent on the canonical
path of an admissible target is also admissible, satisfying the induction above. No rank,
donor-normalization, outcome-count, heuristic score, or empirical frequency is used as a
prefix prune.

A factor-state or candidate-edge limit aborts before committing a partial level. Coverage then
reports `CANNOT_CHECK_RESOURCE_BOUND`, `levels_completed` remains the previous full level, and
`records` refuses access. Partial absence can never become a global negative.

## 5. Exhaustive equivalence evidence

The raw generator remains an independent small-domain oracle: it enumerates every multiset and
filters by the same exact canonical form. Frozen controls compare complete record tuples and
digests, not merely counts. They cover unpruned C2, C2-squared, C2-cubed, C3-squared,
C5-squared, and C5-cubed panels plus short-zero-sum and no-two-factor profiles.

The largest tractable ambient panel exhausts all 333,375 raw length-three multisets of
C5-cubed. Both routes return the same 20 canonical records with identical SHA-256
`4de1ffc69d855e58f7f05fd11778dc3e46aca058ccd69b362f0a7b24a7766a10`; augmentation evaluates
50 extension edges. This is engineering scaling evidence, not extrapolated full-census
authority. Across every frozen panel, mismatches and duplicated output orbits are zero.

Independent hostile controls enumerate the entire small `GL(2,2)` stabilizer and obtain the
same extension-orbit partition as the support-basis implementation. Rank-deficient outside
span coverage, noncanonical parents, malformed profiles, partial-edge limits, factor-state
limits, canonical-parent ancestry, and output uniqueness are also checked.

## 6. Remaining resource and scientific boundary

The algorithmic completeness proof is closed. Resource feasibility at the frozen target is
not: no complete length-19 class archive, donor-slice manifest, short-spectrum run, or D3
extension run exists here. Target-scale memory, checkpoint partitioning, and wall-time remain
`CANNOT_CHECK_RESOURCE_BOUND` until bounded previews justify a frozen job without changing the
scientific grammar. No full census or LUNARC job was launched.
