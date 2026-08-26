# Universal Rooted Completion Duality and Boolean Packing Certificates — R11

Date: 2026-08-26

Status: analytic strengthening of `MATCHING_CRITICAL_COMPLETION_R10.md` and `ATOMIC_FACTORIZATION_COMPLETION_R10.md`. The universal theorem below does **not** require a known generalized Davenport constant. The short-free and numerical `C_5^3` consequences still depend on the earlier completion lemma, and the specialization `D_3(C_5^3)=25` remains conditional on the proof-clean replay in issue #1383.

## Review lenses used in this tranche

The argument was developed and attacked through five independent roles:

1. **zero-sum combinatorist** — checks the packing and complement arguments;
2. **block-monoid factorization specialist** — checks atom/factorization language and sets-of-length boundaries;
3. **hypergraph matching specialist** — checks critical-vertex and induced-subinstance claims;
4. **exact-certificate engineer** — turns the proof into independently checkable source/completion receipts; and
5. **hostile novelty and authority reviewer** — prevents an elementary completion identity from being promoted as established novelty or as numerical `C_5^3` authority.

These are analysis roles, not external peer-review credentials.

## 1. Definitions

Let `G` be an abelian group and let `M` be a finite sequence over `G`. Write

`nu(M)`

for the maximum number of pairwise disjoint nonempty zero-sum subsequences of `M`.

Adjoin one **distinguished new occurrence**

`q = -sigma(M)`

and write

`S = M q`.

Thus `S` is total zero. The new occurrence remains distinguished even when another occurrence of the same group element already appears in `M`.

Let

`P = {A_1,...,A_k}`

be a maximum packing of `M`, where `k=nu(M)`. Its unmatched residue is

`R_P = M (A_1...A_k)^(-1)`.

A **rooted maximum factorization** of `S` is a maximum-length atom factorization

`S = A_q A_1...A_k`

in which the distinguished occurrence `q` lies in the root atom `A_q`.

All equalities are identities in the free abelian monoid of sequences. Occurrence-labelled implementations may distinguish repeated copies; quotient identities must then bind those occurrence labels.

## 2. Universal one-term completion theorem

### Theorem NQ-R11.1 — exact packing increment and rooted duality

For every finite sequence `M` over every abelian group:

1. `nu(S)=nu(M)+1`;
2. every maximum packing of `S` uses the distinguished occurrence `q`;
3. every maximum packing of `S` covers all of `S` and consists of atoms;
4. every maximum packing `P={A_1,...,A_k}` of `M` consists of atoms, its residue `R_P` is zero-sumfree, and `q R_P` is an atom; and
5. the map

   `Phi(P) = {q R_P, A_1,...,A_k}`

   is a bijection from maximum packings of `M` to rooted maximum atom factorizations of `S`.

#### Proof

Let `k=nu(M)` and choose a maximum packing `P={A_1,...,A_k}`.

Each `A_i` is an atom: if one factor split into two nonempty zero-sum subsequences, replacing it by those two factors would produce a packing of size `k+1` in `M`.

The residue `R_P` is zero-sumfree for the same reason. Since every `A_i` has sum zero,

`sigma(q R_P) = -sigma(M) + sigma(M) = 0`.

We claim that `q R_P` is an atom. A nonempty proper zero-sum divisor `Z` of `qR_P` cannot avoid `q`, because then `Z` is a zero-sum divisor of the zero-sumfree residue. If `Z` uses `q`, its nonempty complement in the total-zero sequence `qR_P` is a zero-sum divisor lying entirely in `R_P`, again a contradiction.

Hence

`S=(qR_P)A_1...A_k`

is a packing of size `k+1`, so `nu(S)>=k+1`.

Conversely, at most one factor in any disjoint packing of `S` can use the single distinguished occurrence `q`. Removing that factor leaves a packing entirely inside `M`, of size at most `k`. Thus `nu(S)<=k+1`, proving equality.

A maximum packing of `S` must use `q`; otherwise it would give `k+1` disjoint zero sums in `M`. It must also cover every occurrence of `S`: a nonempty uncovered complement of zero-sum factors in the total-zero sequence `S` is itself zero-sum and would extend the packing. Every factor is therefore atomic by the same splitting argument as above.

Now take a rooted maximum atom factorization

`S=A_q A_1...A_k`

with `q|A_q`. Deleting `A_q` leaves `k` disjoint zero-sum atoms in `M`, hence a maximum packing because `nu(M)=k`. The residue is exactly `A_q q^(-1)`, and it is zero-sumfree because `A_q` is an atom. This operation is inverse to `Phi`, establishing the bijection. ∎

### Corollary NQ-R11.2 — universal matching criticality

The distinguished completion occurrence is always matching-critical in the zero-sum hypergraph:

`nu(S)-nu(S q^(-1))=1`.

Every maximum matching of the zero-sum hypergraph of `S` covers `q`.

The generalized-Davenport assumptions in R10 are therefore unnecessary for the criticality statement itself. They remain necessary for the short-free and numerical search-space consequences used later.

### Corollary NQ-R11.3 — source packing count equals rooted factorization count

At the level of the declared sequence/occurrence semantics, the number of maximum source packings equals the number of rooted maximum atom factorizations of the completion. The completion-root length spectrum is exactly the maximum-packing residue-length spectrum shifted by one.

This is a certificate identity, not an efficient counting algorithm.

## 3. Hereditary Boolean packing lattice

### Theorem NQ-R11.4 — hereditary packing tightness

Let `P={A_1,...,A_k}` be a maximum packing of `M` with residue `R`. For every subset `I` of `{1,...,k}`, write

`A_I = product_(i in I) A_i`.

Then

`nu(A_I)=|I|`

and

`nu(R A_I)=|I|`.

Likewise, for every subset `J` of the `k+1` atoms in the corresponding rooted maximum factorization of `S`, the subproduct `A_J` satisfies

`nu(A_J)=|J|`.

#### Proof

The displayed factors give the lower bounds.

If `A_I` or `R A_I` admitted `|I|+1` disjoint zero sums, adjoining every unused factor `A_j` with `j notin I` would give at least `k+1` disjoint zero sums in `M`, contradicting maximality.

For a subproduct of the rooted maximum factorization of `S`, an extra factorization part could similarly be combined with all omitted atoms to give more than `k+1` factors in `S`. ∎

### Certificate consequence

A maximum source packing yields a Boolean lattice of exact induced packing values:

- `2^k` pure packed subproducts;
- `2^k` residue-plus-subproduct instances; and
- `2^(k+1)` completion-factor subproducts.

These values are mathematically redundant once the top-level maximality proof is trusted. They are nevertheless useful mutation-sensitive cross-checks across independent encodings. A verifier may reject a receipt whose global answer is correct but whose declared atom partition, residue, or occurrence mapping violates any lattice node.

For a prospective `C_5^3` D4 source with `k=3`, one rooted receipt provides 8 pure-source nodes, 8 residue-source nodes, and 16 completed-factor nodes.

## 4. Residue bounds under the short-free completion lemma

Assume additionally the R10 generalized-Davenport completion setting:

- `D_k(G)=N`;
- `|M|=N+t`;
- `nu(M)=k`; and
- the one-term completion `S=Mq` is `t`-short-free.

### Theorem NQ-R11.5 — exact residue interval

For every maximum packing of `M` with residue `R`,

`t <= |R| <= D(G)-1`.

Equivalently, the root atom satisfies

`t+1 <= |qR| <= D(G)`.

Every non-root atom in the corresponding maximum factorization of `S` lies in the same length interval.

#### Proof

The residue is zero-sumfree by Theorem NQ-R11.1, hence its length is at most `D(G)-1`. The root `qR` is a nonempty zero-sum atom in the `t`-short-free sequence `S`, so `|qR|>=t+1`, which gives `|R|>=t`. The same short-free lower bound and ordinary Davenport upper bound apply to every other atom. ∎

The theorem quantifies exactly how much of a source maximum packing can remain unmatched. It does not determine the residue structure.

## 5. Conditional rooted skeletons for `C_5^3`

This section is conditional on independently replayed authority for

`D_3(C_5^3)=25`.

For a hypothetical length-30 source obstruction to four disjoint zero sums, the R10 completion has:

- `t=5`;
- completion length 31;
- ordinary Davenport constant `D(C_5^3)=13`;
- three source packing atoms; and
- a zero-sumfree residue of length 5 through 12.

The root atom therefore has length 6 through 13. The other three atom lengths lie in `[6,13]` and, together with the root length, sum to 31.

### Theorem NQ-R11.6 — 31 rooted length skeletons

The complete rooted length partition consists of the following eight residue classes and 31 rooted skeletons:

| residue `|R|` | root atom `|qR|` | sorted lengths of the three avoiding atoms |
|---:|---:|---|
| 5 | 6 | `(6,6,13)`, `(6,7,12)`, `(6,8,11)`, `(6,9,10)`, `(7,7,11)`, `(7,8,10)`, `(7,9,9)`, `(8,8,9)` |
| 6 | 7 | `(6,6,12)`, `(6,7,11)`, `(6,8,10)`, `(6,9,9)`, `(7,7,10)`, `(7,8,9)`, `(8,8,8)` |
| 7 | 8 | `(6,6,11)`, `(6,7,10)`, `(6,8,9)`, `(7,7,9)`, `(7,8,8)` |
| 8 | 9 | `(6,6,10)`, `(6,7,9)`, `(6,8,8)`, `(7,7,8)` |
| 9 | 10 | `(6,6,9)`, `(6,7,8)`, `(7,7,7)` |
| 10 | 11 | `(6,6,8)`, `(6,7,7)` |
| 11 | 12 | `(6,6,7)` |
| 12 | 13 | `(6,6,6)` |

Forgetting which atom contains the distinguished completion occurrence collapses these 31 rooted cases to the 11 unrooted atom-length multisets in R10.

#### Proof

The residue interval is Theorem NQ-R11.5. For each fixed root length `r+1`, enumerate sorted triples in `[6,13]^3` whose sum is `31-(r+1)`. The table is the complete integer enumeration. ∎

### Search-partition warning

The 31 rows define a complete **cover** of rooted certificates. They are a disjoint partition of source candidates only after a canonical maximum-packing/rooted-factorization selector is frozen. A source can have multiple maximum packings and therefore multiple rooted factorizations. Duplicate discovery is harmless for UNSAT completeness, but a coverage manifest may not count duplicates as distinct source subjects.

## 6. Proof-certificate architecture

A rooted source certificate should bind:

1. the source sequence `M` and distinguished completion occurrence `q=-sigma(M)`;
2. a maximum source packing `A_1,...,A_k`;
3. the exact residue `R=M(A_1...A_k)^(-1)`;
4. zero-sum and atom checks for every `A_i`;
5. a zero-sumfree certificate for `R`;
6. the root-atom identity `A_q=qR` and atom check;
7. the completed factorization `S=A_qA_1...A_k`;
8. a proof that no `k+1` packing exists in `M` (equivalently no `k+2` factorization exists in `S`);
9. all declared Boolean-lattice induced values; and
10. occurrence-level quotient and coverage identities.

For UNSAT or census work, an independent verifier should rebuild `q`, `R`, every induced subject, and every factorization identity from bytes rather than trust solver labels.

### Source-first exact search

For the post-#1383 D4 programme, a complete source-first search may enumerate

`M = R A_1 A_2 A_3`

under the rooted length table, with `R` zero-sumfree and each `A_i` an atom, then set `q=-sigma(M)` and verify that `qR` is an atom. This is complete because every genuine source obstruction has at least one maximum packing and hence one rooted factorization.

The local conditions alone do **not** rule out a crossing fourth zero sum in `M`. Exact source maximality remains a required SAT/UNSAT or matching certificate.

## 7. Relationship to the proof-clean D2/D3 replay

The universal Theorems NQ-R11.1–NQ-R11.4 may be used only as post-generation consistency checks in the proof-clean replay of issue #1383 unless they were included in its prospectively frozen source packet.

The conditional `C_5^3` rooted table in Section 5 assumes `D_3=25` and therefore must not prune, accept, or partition the computation whose purpose is to independently establish that value.

Its intended computational use is the subsequent D4/source-lift programme, including issue #1384, after the D3 authority gate closes.

## 8. Prior-art and novelty boundary

The following are donor-owned:

- free-abelian-monoid sequence notation, zero-sum atoms, block monoids, and sets of factorization lengths;
- the ordinary and generalized Davenport constants;
- inverse `D_k` questions and rank-two structural results;
- generic hypergraph matchings and matching criticality; and
- the elementary fact that a maximum packing leaves no additional zero-sum factor.

The targeted search performed for this tranche did not locate the exact rooted maximum-packing/rooted-factorization bijection or its Boolean induced-subinstance receipt. That absence is not a novelty certificate. A factorization-theory specialist must search monographs and non-indexed inverse-zero-sum literature before any novelty claim.

The conservative residual is computational and structural: the universal one-term completion identity is made explicit as a source/completion certificate duality, then specialized into a rooted residue spectrum and a redundant Boolean packing lattice for independently checkable computer-assisted proofs.

## 9. Verification

`verify_rooted_completion_duality_r11.py` uses occurrence-labelled sequences and checks:

- all 585 sequences in complete multiset panels through length 8 in `C_2`, length 7 in `C_3`, and length 6 in `C_4` and `C_2^2`;
- 1,170 independent Bell-partition packing-number oracle comparisons;
- 2,746 exact source-packing/rooted-factorization bijections;
- 19,434 atom checks;
- 5,492 residue zero-sumfree checks;
- 85,624 hereditary lattice values;
- 300 generated rank-three `C_5^3` controls through length 9; and
- the exact 31 rooted and 11 unrooted conditional length skeleton counts.

The analytic proof owns the universal theorem. Finite checks are mutation-sensitive corroboration, not all-size authority.

## 10. Peer-review gates

Before top-tier submission, require:

1. independent proof reconstruction of NQ-R11.1–NQ-R11.5;
2. a structurally independent packing/factorization verifier;
3. specialist novelty adjudication against inverse generalized-Davenport and block-monoid literature;
4. proof-clean release of `D_2(C_5^3)`, `D_3(C_5^3)`, and the short-zero-sum spectrum under issue #1383;
5. source-level D4 execution with rooted and non-rooted partitions agreeing on coverage;
6. explicit duplicate/canonicalization accounting for multiple maximum packings;
7. retained SAT, UNSAT, disagreement, proof-check failure, and resource-exhaustion terminals; and
8. manuscript language that keeps `D_4(C_5^3)` open unless the source-level gate actually closes.

Internal exact computation, green CI, or this universal theorem does not establish external novelty, independent reproduction, `D_3=25`, `D_4=30`, or journal authority.
