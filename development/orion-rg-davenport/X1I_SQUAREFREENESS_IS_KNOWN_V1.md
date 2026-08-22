# ORION-RG X1-I — the projective-squarefreeness conjecture is a published theorem

X1-G reported an unexplained regularity across two complete censuses (~41 billion
sequences) and raised it as a conjecture:

> Every maximal zero-sum-free sequence over `C_p^3` is projectively squarefree.

**It is a known theorem, for all `p` and all `r`.** Recording that plainly.

## The prior art

**Gao & Geroldinger, "Zero-sum problems in finite abelian groups: a survey",
Theorem 4.8**, verbatim from the source PDF:

> "Let `G` be a finite elementary p-group and `S ∈ F(G)` be a zero-sumfree
> sequence of length `|S| = d(G)`. Then `(g, h)` is independent for any two
> distinct elements `g, h ∈ supp(S)`."

For an elementary `p`-group, "`(g,h)` independent" is exactly "`g` and `h` are not
scalar multiples" — i.e. the support injects into `PG(r-1, p)`. Same statement,
stronger scope than the conjecture (all `r`, not just rank 3).

Verified by fetching the survey and reading Theorem 4.8 directly, not from a
search summary. This is the **fourth** claim in this programme killed by a
literature check.

## What actually survives, and its honest status

**An independent proof**, in
`research/orion-rg/X1I_PROJECTIVE_SQUAREFREENESS_PROOF_AND_VERIFICATION.txt`.
It proceeds via Olson's product identity `prod_{g in S}(1-[g]) = sum_{h in G}[h]`,
projection onto the group algebra of a single line, an order computation in the
chain ring `F_p[T]/(T^p)`, a sparsity lemma `ord_T(z) <= |supp(z)| - 1`, a
sandwich giving `|Sigma(A)| <= k+1`, and the rank-1 inverse theorem forcing the
coefficient multiset to be constant. We do **not** know whether this reproduces
the published proof; the survey states the theorem without displaying one, and we
did not obtain the original source. **No novelty is claimed for the argument.**

**A computational verification at unusual scale.** Complete censuses with zero
exceptions: `C_3^2` (72), `C_5^2` (8,400), `C_7^2` (333,648), `C_3^3` (69,264),
`C_5^3` (26,369 GL-classes = 39,147,296,000 sequences). The proof's *sharp
intermediate predictions* (`|Lambda| = p-1-k`, `|Sigma(A)| = k+1`,
`supp(b) = Lambda ∪ {0}`, `a*b = J`) were checked line-by-line on 196,799 lines at
`p=5` plus samples at `p=3,7`, with 0 failures. A census-independent exhaustive
search at `p=5` for a length-12 zero-sum-free multiset containing `{e1, 2e1}`
explored **5,247,890,587 nodes**, reached maximum length 11, and found none.

**One genuinely useful expository point (Appendix A).** The polynomial/Frobenius
method cannot see this theorem: passing to the associated graded ring replaces
`1-[g]` by the linear form `L_g`, and `L_{cu} = c·L_u`, so the top-degree identity
depends only on *which lines* are occupied, not on which point of each line. The
deciding information sits in the lower-order terms. That explains why the
regularity looked mysterious in the census.

## The lead this opens

The same survey states **Conjecture 4.9**, which is open:

> `G = C_{n_1} ⊕ ... ⊕ C_{n_r}`, `k ∈ [1, n_1 - 1]`, `S` of length `k + d(G)`
> with no zero-sum subsequence longer than `k`. Then `S = 0^k T` with `T`
> zero-sum-free.

That is a live target in the immediate neighbourhood of machinery this programme
already has, and unlike X1-I it is not already answered.

## Standing correction to X1-G

The X1-G document's "OPEN QUESTION — this is the one regularity that looks like a
theorem waiting for a proof" should be read as answered: it *is* a theorem, it was
already proved, and the census was rediscovering it. The census remains valid as
data; the framing was wrong.

## Authority

`mathematical_proposal: false` — nothing here is proposed as new.
`novelty_claim: false`. The contribution is verification and attribution.
