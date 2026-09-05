# Davenport first-principles checkpoint — 2026-09-05

Status: **five reviewed proof advances, including a complete new exceptional overlap layer; the global numerical conjecture remains open**.

## 1. Continuity and ownership

The continuation started from published live commit `a7ab107f76b99ceb7fda0c6a8285527d36be87ca`, tree `c66a8807809bd21a42ec3fe0cd5d3dafa0b5483c`. A fresh connected branch search, including its empty final page, and `git ls-remote --heads origin '*davenport*'` checked all 25 remote Davenport branches. Their heads were unchanged from the preceding audited continuation. No stronger unseen head was substituted or overwritten.

Work took place only in the session's own checkout on `shadow/davenport-first-principles-20260905`. The previous donor classifications and completed rank-three `a=3` and saturated `a=2` boundaries remain intact. The publication receipt records the new reviewed and remote commit identities separately.

## 2. The conceptual change

The global problem is now expressed using two elementary operations: merge occurrences into their sum, or split one occurrence into two summands. Neither operation presupposes a maximal atom, support four, a corridor, or saturation.

For a finite abelian group of exponent `n` and any integer `M>=0`, define `delta_n(B)=|B|-n z(B)`. The proved generalized criterion is

\[
\boxed{
\delta_n(B)\le M\text{ for all zero-sum }B
\iff
\text{every split of every }\delta_n=M\text{ block raises }z\text{ by one}.
}
\]

Every counterexample can itself be coarsened into a unit-excess core of length `nz+M+1`. At that core, a contraction losing `h` packing factors costs at least `nh+1` occurrences. The same bound holds for the total excess of any specified atom family whose imposition loses `h` factors. This proves simultaneous compatibility for contraction or atomic-excess budgets at most `n`.

The one-factor version belongs to the classical theory of unsplittable atoms; splitting itself is not a newly introduced operation. See [Chen's discussion and definition of unsplittability](https://math.colgate.edu/~integers/w18/w18.pdf). The higher-factor defect reductions here have direct proofs, with novelty and priority unclaimed.

See [the splitting and extraction theorem](GENERALIZED_SPLITTING_AND_CORE_EXTRACTION_V1.md), [the contraction normal form](MINIMAL_DEFECT_CORE_CONTRACTION_NORMAL_FORM_V1.md), and [the block and atom insertion laws](MINIMAL_DEFECT_CORE_INSERTABILITY_V1.md).

## 3. Exact quotient atomization

For any subgroup `H<=G`, write `B=KR`, with `K` containing the occurrences in `H`. Atomize the projection of `R` in all possible occurrence-respecting ways `P`, and let `K_P` retain `K` together with the lifted sums of those quotient atoms. Then

\[
\boxed{z_G(B)=\max_P z_H(K_P),}
\qquad
\boxed{\delta_n^G(B)=\min_P\left(\sum_{T\in P}(|T|-1)+\delta_n^H(K_P)\right).}
\]

The kernel uses the same slope `n`. These are exact identities; the rank-three target still requires bounding the minimum by `5(p-1)/2`.

The note preserves a prime-uniform family for which maximizing the number of quotient atoms loses `2L` ambient factors, with `L` arbitrary. A fixed or greedy quotient atomization is therefore insufficient. See [the quotient and carry theorem](QUOTIENT_CARRY_DEFECT_VARIATIONAL_FORM_V1.md).

## 4. Concrete frontier advance: an entire exceptional layer is closed

Put `p=2H+1>=7` and `m=3H+1`. For canonical type two,

\[
U=e_1^{p-1}e_2^{p-1}g^{p-2}s^2,
\qquad e_1+e_2=2(s-g),
\]

there is now **no** rank-two first-corridor companion

\[
\boxed{V=s^{H-1}x^r y^t,\qquad r+t=p+1,}
\]

for any positive allowed new multiplicities.

The proof projects `x^r y^t` modulo the shared light line and applies the depth inequality to every projected atom and its shared-term translate. It forces `p==1 (mod 8)`, even `r,t`, and a square `Q^2` for which `Q` is the only atomic divisor. A two-value cyclic splitting theorem and the long-atom index theorem then produce an index-one description. Unless one multiplicity of `Q` is one, an explicit shorter atom divides its square. The remaining `(r,t)=(2,p-1)` row is the previously eliminated endpoint.

This closes the whole layer, including unsaturated new values; the previous result closed only that endpoint. The new cyclic inputs are donor-owned and identified precisely in [the complete proof](A2_RANK2_PENULTIMATE_OVERLAP_FULL_ELIMINATION_V1.md).

## 5. Failed routes and remaining gaps

The following obstructions are retained with their exact scope:

- A rank-three four-direction circuit has a positive-gain exchange requiring all four source atoms; ambient rank alone does not imply a three-atom augmentation theorem.
- An arbitrary maximum quotient atomization can have arbitrarily poor kernel lifting. Kernel carry must be retained.
- The index-one theorem cannot be applied directly at length `(p+1)/2`; the separate two-support splitting lemma is essential.
- At `c=H`, the projected new-value sequence has length `p` and can itself be one cyclic atom. The penultimate-layer proof cannot force a proper quotient atom there.
- A maximal atom obtained by exchange need not have a saturated new value. The saturated-quotient theorem cannot be applied until that multiplicity is proved.

The full first corridor remains open. In particular, rank-three `a=2` still has unsaturated mixed-subsequence faces, and rank-two `a=1,2` still has high-overlap cases outside the proved layers. The global splitting property for higher-factor boundary blocks remains unproved. Neither `D_3(C_7^3)` nor the full all-prime, all-`k` formula is asserted.

## 6. Review receipts

The initial contraction mechanism was independently derived by the coordinator, inverse specialist, and proof auditor; their submitted notes were reviewed before commitment. The coordinator supplied and checked local core extraction, the exact splitting equivalence, the quotient variational identity, and the final penultimate-layer theorem. The last proof was checked by both its interval and antipodal-depth formulations, with its external hypotheses verified in primary mathematical papers. Its provenance is not described as an independent-agent audit.

No realization search or brute-force enumeration was run in this continuation. Whitespace checks apply to the committed changes; mathematical authority rests on the displayed proofs and explicitly attributed donor inputs.
