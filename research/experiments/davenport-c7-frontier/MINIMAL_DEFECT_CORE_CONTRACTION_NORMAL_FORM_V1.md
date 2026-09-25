# Minimal defect cores: contraction, joint compatibility, and descent — V1

Status: **proved first-principles conditional normal form; written proof reviewed by the coordinating researcher**. If a proposed uniform packing-defect bound fails, a smallest obstruction has defect exactly one above the threshold. Every contraction of cost at most the exponent preserves its full packing number, even when several disjoint bundles are contracted simultaneously. A smallest incompatible bundle contracts it to a quantitatively near-extremal block with one fewer factor.

These statements concern arbitrary zero-sum blocks over arbitrary finite abelian groups. They do not assume canonical atoms, small support, saturated values, an affine plane condition, or the existence of a particular companion. They do not prove the proposed rank-three Davenport bound.

## 1. Occurrence-level definitions

Let `G` be a finite abelian group of exponent `n>=2`. A sequence is regarded as a finite labeled multiset of term occurrences. Labels only distinguish resources; all sums are group sums.

For a zero-sum block `B`, let `z(B)` be its maximum number of pairwise disjoint nonempty zero-sum subsequences. Since `B` itself is zero-sum, a maximum packing partitions all its occurrences: a nonempty leftover would itself be another zero-sum. Every part of a maximum packing is an atom, since splitting one would increase the packing number.

Define

`delta_n(B)=|B|-n z(B)`.

Fix an integer threshold `M>=0`. A counterexample means a nonempty zero-sum `B` with `delta_n(B)>M`.

Let `T_1,...,T_s` be pairwise disjoint nonempty occurrence bundles in `B`. Their simultaneous contraction replaces each `T_i` by one distinguished occurrence with value `sigma(T_i)`. Write the contracted zero-sum block as `B/P`, and its contraction cost as

`d=sum_i (|T_i|-1)`.

Thus `|B/P|=|B|-d`. Identical group values among new and old occurrences cause no ambiguity because their labels remain distinguished.

A factorization of `B` is **compatible** with these bundles when every `T_i` is contained in one of its atomic factors. Different bundles may be contained in the same factor. This is a simultaneous condition, not a separate assertion that each bundle is compatible with a possibly different factorization.

## 2. Exact contraction/lifting identity

> **Lemma 1.** The packing number `z(B/P)` equals the largest number of zero-sum parts in a partition of `B` in which every contracted bundle is contained in one part. In particular,
>
> `z(B/P)<=z(B)`.

To lift a partition of the contracted block, replace each distinguished sum occurrence by all occurrences in its original bundle. This preserves each part's group sum, nonemptiness, disjointness, and coverage. Conversely, a partition respecting the bundles contracts to a zero-sum partition of the same cardinality. These operations are inverse at the level of labeled partitions.

If `z(B/P)=z(B)=m`, lifting a maximum partition gives `m` zero-sum parts of `B`. Each lifted part is automatically an atom: otherwise splitting it would produce more than `m` parts. Thus equality of packing numbers is exactly joint compatibility with a maximum atomic factorization.

> **Lemma 2.** Contracting two occurrences lowers the packing number by at most one.

Take a maximum atomic factorization before the contraction. If the two occurrences lie in one atom, contracting inside that part preserves the displayed number of zero-sum parts. If they lie in different atoms, merge those two parts and contract inside their union; this loses exactly one displayed part. Combined with Lemma 1, the packing loss is either zero or one.

No assertion that an individual lifted or contracted part remains an atom is needed unless its factorization is already known to be maximum.

## 3. A smallest counterexample has exactly unit excess

Assume counterexamples exist, and choose `B` with minimum cardinality among all of them. Write `m=z(B)` and `delta=delta_n(B)`.

Since `delta>M>=0`, one has `|B|>n`, so two occurrences can be contracted. For any such contraction `B'`, Lemma 1 gives

`delta_n(B')=|B|-1-n z(B')>=delta-1`.

Minimality implies `delta_n(B')<=M`. Thus `delta<=M+1`. Since the quantities are integers and `delta>M`, we obtain

`boxed{delta_n(B)=M+1,qquad |B|=mn+M+1.}`            (1)

This is a cardinality-minimal counterexample theorem; no induction over `m` is required.

## 4. Every cheap simultaneous contraction is compatible

For any positive contraction cost `d>=1`, set

`h=m-z(B/P)>=0`.

The contracted block is strictly shorter, so minimality and (1) give

`M+1-d+n h=delta_n(B/P)<=M`.

Equivalently,

`boxed{d>=n h+1.}`                                   (2)

This is an exact lower bound on the occurrence cost of losing `h` packing factors.

For `1<=d<=n`, inequality (2) forces `h=0`. Lemma 1 therefore yields:

> **Joint compatibility theorem.** In a cardinality-minimal defect counterexample, every family of disjoint bundles with total contraction cost at most `n` is simultaneously contained in some maximum atomic factorization.

In particular, every occurrence subset `T` with `|T|<=n+1` is contained in one atom of a maximum factorization. More strongly, any prescribed collection of pair identifications whose disjoint connected components have total cost at most `n` can be respected at once. Pairwise compatibility alone would not imply this simultaneous statement; the contraction-cost proof supplies it.

Every pair contraction has `d=1`, `h=0`; hence all such contractions land exactly on the critical line:

`|B'|=mn+M`, `z(B')=m`, `delta_n(B')=M`.              (3)

The original block is therefore surrounded by critical-line contraction blocks. These are genuine structural consequences of minimality, not assumptions about their support or classification.

## 5. Choosing the first failing level makes lower-line descent exact

For Davenport applications it is useful to choose the obstruction in a different, compatible order: first choose the least factorization number `m` for which a block has defect above `M`, and then choose a shortest such block at that level.

The proofs of Sections 3--4 still work. A contraction cannot increase `z`. If it decreases `z`, the least-level property bounds its defect by `M`; if it preserves `z=m`, the within-level cardinality minimality gives the same bound. Therefore (1)--(3) and the joint compatibility theorem remain valid for this choice as well.

Suppose a cost-`n+1` contraction loses a factor. Inequality (2) forces it to lose exactly one, and then

`z(B/P)=m-1`,

`|B/P|=(m-1)n+M`, `delta_n(B/P)=M`.                  (4)

The least-level choice establishes the upper bound `D_(m-1)(G)<= (m-1)n+M` in the zero-sum-block formulation. Since (4) itself attains it, the contracted block is an actual `D_(m-1)` extremizer. No unproved inverse classification of that extremizer is implied.

With merely global cardinality minimality, (4) still holds but should initially be described as a critical-line block. The conclusion that it is globally Davenport-extremal at level `m-1` requires the lower-level upper bound supplied by the least-level choice or by an independent theorem. This distinction prevents an unproved equality from entering through terminology.

## 6. Minimal incompatible bundles lose exactly one factor

Call a nonempty occurrence subset `T` incompatible if no maximum atomic factorization of `B` contains all of `T` in one factor. By Lemma 1, this is equivalent to

`z(B/T)<m`.

Suppose `T` is inclusion-minimal with this property. Choose an occurrence `g in T`. The proper subset `T\{g}` is compatible, so its contraction preserves `m`. Contracting that distinguished sum occurrence together with `g` is one further pair contraction, and gives exactly `B/T`. Lemma 2 and incompatibility force

`boxed{z(B/T)=m-1.}`                                 (5)

In particular, if `t=|T|`, then the joint compatibility theorem and (1) give

`t>=n+2`,

`delta_n(B/T)=M+n+2-t`.                              (6)

Thus a minimal incompatible bundle always yields a one-level descent. Its size measures the precise loss of defect from the target line.

## 7. The descent bundle has a global size bound

Assume `m>=2`. In any maximum factorization, choose one atom `U` and one occurrence `g` outside it. The bundle `U g` is incompatible: any atom containing it would contain the proper nonempty zero-sum `U`. Therefore an inclusion-minimal incompatible subset exists inside `U g`, giving

`n+2<=|T|<=D(G)+1`.                                  (7)

A sharper bound follows by choosing a shortest atom in a maximum factorization. Its length `s` satisfies

`s<=floor(|B|/m)=n+floor((M+1)/m)`.

Choose a globally minimum-cardinality incompatible bundle; it is inclusion-minimal and its size is at most `s+1`. Hence

`boxed{n+2<=t<=n+floor((M+1)/m)+1.}`                 (8)

Combining with (6) gives the controlled descent interval

`boxed{M+1-floor((M+1)/m)<=delta_n(B/T)<=M.}`          (9)

This is a quantitative reduction to a near-critical block of packing number `m-1`, before imposing a canonical-atom or saturated-support hypothesis.

The bound comes from an actual shortest atom and an actual outside occurrence; it is not a continuous averaging replacement for a missing subsequence.

## 8. What can a minimal incompatible bundle contain?

There are three exhaustive possibilities for an inclusion-minimal incompatible `T`:

1. `T` is zero-sum-free.
2. `T` is an atom that does not occur in any maximum factorization of `B`.
3. `T=U g`, where `U` is an atom occurring in a maximum factorization and `g` is one outside occurrence.

To prove completeness, suppose `T` contains a nonempty zero-sum `U`. If `U=T` and `T` has no proper zero-sum, this is case 2. Otherwise choose a proper such `U`. Every proper subset of `T` is compatible, so `U` is contained in an atom of a maximum factorization. Because `U` is already zero-sum, it must equal that atom. For any outside occurrence `g in T\U`, the subset `U g` is incompatible; minimality forces `T=U g`, giving case 3. If there is no nonempty zero-sum, this is case 1.

There is a strong length restriction on case 2. If an atom `A|B` is not insertable in a maximum factorization, then `z(B/A)<=m-2`; otherwise adjoining `A` would give a maximum factorization. Minimality applies to the proper zero-sum complement and yields

`M>=delta_n(B/A)>=M+1-|A|+2n`.

Therefore

`boxed{|A|>=2n+1.}`                                  (10)

Consequently, whenever the upper bound in (8) is at most `2n`, a globally smallest incompatible bundle cannot be case 2. The genuine alternatives are then a zero-sum-free bundle that cannot be cohabited, or an insertable atom with one outside occurrence. A geometric argument that rules out the former would require additional proof; it is not a consequence of the group rank alone.

## 9. Specialization to the rank-three target

For `G=C_p^3`, `p>=5`, take

`n=p`, `M=5(p-1)/2`.

The classical `D_1=3p-2` and proved donor-derived `D_2=2p+M` exclude defects above `M` at levels one and two. Thus a first failing level has `m>=3`. Choosing a shortest failure at that level gives

`|B|=mp+M+1`,

and all disjoint bundles of total contraction cost at most `p` are jointly compatible with a maximum factorization.

A globally smallest incompatible bundle has

`p+2<=t<=p+floor((5p-3)/(2m))+1<2p+1`,

and contracts the block to packing number `m-1` with defect in the interval

`M+1-floor((5p-3)/(2m))<=delta_p(B/T)<=M`.

Since `m>=3`, the strict upper size inequality follows from `(5p-3)/6<p`. Hence the noninsertable-atom alternative is excluded for this smallest bundle. No maximal-atom or low-support gate was assumed in deriving this conclusion.

At the first `p=7,m=3` face, for example, `M=15`, `|B|=37`, and

`9<=t<=13`,

while the contracted packing-two block has length `25,...,29` and defect `11,...,15`. At `t=9`, it is a genuine `D_2(C_7^3)=29` extremizer; at larger `t`, it belongs to a precisely stated near-extremal range. This does not identify its support or prove a reverse lifting augmentation.

The conceptual next interface is now explicit: classify the critical or near-critical contracted block together with the distinguished aggregate occurrence, and determine whether its proposed zero-sum-free or atom-plus-one expansion can remain packing-terminal. A theorem about that expansion would bridge the global problem to local donor structures; merely assuming that it has a saturated basis would not.

## 10. Preserved failed simplifications

1. Pairwise compatibility is weaker than simultaneous compatibility. The latter is proved here by the total-cost contraction argument and must not be inferred from independent pair factorizations.
2. A lifted maximum partition is atomic because otherwise it improves `z(B)`. Atomicity must not be presumed for arbitrary lifted partitions.
3. A critical-line contraction is globally Davenport-extremal only when the relevant lower-level upper bound has been supplied, as in Section 5.
4. A proposed normal form with at most two factors longer than the exponent is too strong: known short-free blocks can have maximum factorizations with four or more factors, every one longer than the exponent. The desired defect bound is a total packing statement, not a bound of two on the number of long factors.
5. The ordinary group algebra `F_p[C_p^3]` has augmentation-ideal nilpotency degree `3(p-1)+1`. Products of augmentation factors from the much longer candidate blocks already vanish, so the plain product forgets the packing count. Passing to a higher Noether or Rees filtration can encode packing, but its desired intercept bound must then be proved; it is not furnished by the original nilpotency statement alone.

The contraction and lifting proofs themselves require no external donor theorem. The rank-three numerical specialization uses the already recorded classical and `D_2` inputs. No generalized Davenport equality or full first-corridor theorem is asserted.

Internal audit: the coordinating researcher and inverse specialist independently derived the unit-excess and cheap-contraction mechanisms; the separate proof auditor also independently checked both mechanisms and the one-factor loss of a minimal incompatible bundle. The coordinator reviewed the final written proof, including labeled occurrence lifting, simultaneous rather than separate compatibility, the distinction between cardinality and least-level minimality, the trichotomy, the integer size bound, and the `p=7` descent interval. These are mathematical proof checks, not an exhaustive realization search. Novelty and priority remain `CANNOT_CHECK`.
