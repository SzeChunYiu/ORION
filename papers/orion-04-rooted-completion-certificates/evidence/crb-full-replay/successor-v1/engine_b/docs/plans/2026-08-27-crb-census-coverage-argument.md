# CR-B census coverage argument (both declared scopes)

This document is the coverage argument whose SHA-256 digest is bound into
every `CoverageDeclaration.v1` emitted by `crb_census.py`.  It argues that
the enumeration covers exactly the declared universes, that every prune is
sound, and that every decision procedure is exact.  It consumes no Engine-A
artifact: the two frozen public denominators (98,622 and 230,983) enter only
as preregistered expected counts, enforced fail-closed.

## Public facts used (as stated, not re-derived)

- `D_1(C_5^3) = 13` (Olson constant, donor fact on the frozen record).
- `D_2(C_5^3) = 20` (frozen machine-checked result; upper bound route only).
- Lemma A: a k-disjoint-free multiset of length L has every zero-sum
  sub-multiset Z satisfying `|Z| > L - D_{k-1}`; otherwise the complement
  (length >= D_{k-1}) contains a zero-sum disjoint from Z.
- Multiplicity cap 4: five equal nonzero elements are themselves a zero-sum
  of length 5, inside every prune window used here.

## Group encoding

Elements are encoded `v = 25*x + 5*y + z` for `(x,y,z) in C_5^3`; the fixed
basis is `{e1=1, e2=5, e3=25}`; nonzero elements are 1..124.  All arithmetic
runs through the engine_b addition/negation tables, which the fixture suite
round-trip-validates elementwise.

## Scope NQ_D2_NORMALIZED_LENGTH_19

Universe: length-19 multisets over nonzero elements with no two disjoint
nonempty zero-sum sub-multisets, whose support contains the fixed basis with
`1 <= m(e1) <= m(e2) <= m(e3) <= 4` (the frozen public normalization; every
record is one normalized multiset, orbit reduction is NOT performed).

1. Partition: the 20 ordered multiplicity triples times the 121 possible
   first non-basis elements times the possible second non-basis index form
   147,620 disjoint (triple, first, second) shards.  Every multiset in the
   universe has at least 19 - 12 = 7 non-basis elements, so it fixes exactly
   one triple and one nondecreasing (first, second) index pair and is
   enumerated exactly once; every enumeration path yields exactly one
   multiset in the universe.  The second-level sharding exists for load
   balance across the 48 LUNARC workers; it changes neither the universe
   nor the record order class.
2. Depth prune (sound): by Lemma A with k=2 and D_1=13, a two-disjoint-free
   length-19 multiset has no zero-sum of length <= 6.  The DFS therefore
   rejects any extension creating a zero-sum of length <= 6.  Rejecting v at
   a node rejects only sequences containing the current prefix plus v, which
   all contain that zero-sum; completeness over the universe is preserved.
3. Exact predicate (incremental, no leaf adjudication): alongside the
   weighted reach board the state carries two pair views, `r1` (sums of
   nonempty sub-multisets) and `r2` (unordered pairs of sums realized by
   two DISJOINT nonempty sub-multisets).  Adding a fresh position may add it
   to either side of an old pair or start a new side paired with any old
   complete sub-multiset, so every stored pair is realized by genuinely
   disjoint sub-multisets (soundness), and every disjoint pair is stored by
   the time its last element is inserted (completeness, by induction on the
   insertion order; the base cases are the `(v, s)` pairs created from
   `r1`).  The multiset contains two disjoint nonempty zero sums exactly
   when the packed pair (0, 0) is stored, so the DFS rejects those branches
   and every surviving length-19 leaf IS a witness by construction.  The
   two-bin factorization SAT encoding is NOT used in the census; it is a
   cross-validation instrument in the test suite (pair DP versus SAT versus
   brute force on random multisets, plus the frozen witness).
4. Capacity bound (sound prune): elements are partitioned into 31
   projective lines {g, 2g, 3g, 4g}.  For each still-allowed value v the
   multiplicity cap is the largest initial run j of further copies with no
   -(j*v) reachable by at most 6-j prefix elements (a longer run would close
   a zero-sum of length <= 6 regardless of what else is added later).  A
   whole line then holds at most `_MAXLINE[cap(g)][cap(2g)][cap(3g)][cap(4g)]`
   further elements, the maximum over admissible multiplicity vectors whose
   sub-count combinations never close a zero-sum of length <= 6 along that
   line alone (aggregating the full vector is required: g and 2g can
   coexist, so a single-value cap is not sound -- the frozen record's
   recorded defect and repair document exactly this).  A node whose length
   plus the 31 line maxima cannot reach 19 is pruned without losing any
   witness.  A cheap gate skips the computation whenever at least
   `remaining` distinct lines are still live, since each live line
   contributes at least one element to the bound.
5. Count: the stream must contain exactly 98,622 records; any other count
   raises before any stream is written.
6. Record order: (triple, first index, second index) shard order, then
   depth-first discovery order inside a shard; ordinals are assigned in
   this order.

## Scope NQ_D3_STRUCTURED_LENGTH_25

Universe: pairs (C, A) where C is a D2 witness record and A is a 6-element
zero-sum multiset such that C + A has no zero-sum of length <= 5.  One
record per pair, no deduplication across pairs.

1. Necessity of the filter: by Lemma A with k=3 and D_2=20, a
   three-disjoint-free length-25 multiset has every zero-sum of length
   > 25 - 20 = 5.  The census therefore admits exactly the pairs whose union
   has no zero-sum <= 5.  This is a necessary condition for the
   three-disjoint predicate; the census does NOT claim it sufficient and
   does NOT execute the predicate (required_bins=3 records are adjudicated
   by the execution phase).
2. Enumeration: A is built in nondecreasing order with the final element
   forced to negate the running partial sum, so sum(A) = 0 exactly and every
   6-element zero-sum multiset appears once in this canonical order.  A
   candidate v is skipped when -v is reachable with <= 4 elements of the
   current prefix (adding v would close a zero-sum of length <= 5); every
   transition rejects a state whose weight-1..5 reach gains a zero.  A
   witness C with its own zero-sum <= 5 hosts no admissible pair and is
   skipped after being scanned.
3. Count: the stream must contain exactly 230,983 records, else fail closed.
4. Record order: witness ordinal order, then extension depth-first order.

## Independence and honest limits

- No Engine-A module, canonicalized candidate list, forbidden set, orbit
  manifest, or aggregate result is imported or read; the generator reads
  only the public group tables, the two frozen denominators, and the frozen
  partition plan identities.
- The state representation (sorted byte-value sum sets translated by
  per-element value permutations, with the disjoint-pair view carried over
  packed unordered integer pairs) and the leaf decision (the exact pair DP
  above) are independent implementations relative to the Engine-A
  shift-permuted bitboard enumerators: the prunes are independently
  re-derived from the same public group laws and frozen donor facts, not
  ported code.  The two-bin factorization SAT encoding is used by the
  execution phase (per-record UNSAT certificates) and as a cross-validation
  instrument in the test suite; it plays no role in enumeration.
- `normalization_completeness` stays CANNOT_CHECK: the m1<=m2<=m3 basis
  normalization is taken as the frozen public definition of the census
  universe; GL(3,5) orbit reduction is not performed, so
  `orbit_completeness` is NOT_CLAIMED and `orbit_key_sha256` groups
  identical multisets rather than orbits.
- `matrix_witness_sha256` binds each record to the digest-addressed GL(3,5)
  matrix manifest; it is a binding, not an orbit computation.
- Byte completeness: each scope ships a canonical JSONL sequence stream, a
  coverage declaration binding this document's digest, an input manifest
  binding both by bytes, a candidate stream with per-record digests, and the
  frozen 4,096-record shard layout materialized from it.
