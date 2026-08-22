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

## The lead this opens — and its immediate correction

X1-I originally pointed at the same survey's **Conjecture 4.9** as a fresh open
target. A prior-art check run *before* any work (X1-J,
`X1J_CONJECTURE_49_PRIOR_ART_MAP.md`) shows that framing was wrong too.

Conjecture 4.9 **is** Conjecture 1.1 of Gao & Zhuang, *Sequences not containing
long zero-sum subsequences*, European J. Combin. 27 (2006) 777–787. Such an `S`
is called a **normal sequence**. It has a twenty-year literature and is open only
in a narrow corner:

| case | source | status |
|---|---|---|
| `G` cyclic | Gao–Zhuang Thm 1.6(i) | proved |
| any `G`, `k <= min(6, p-1)` | Gao–Zhuang Thm 1.5 | proved |
| `C_p^r`, `p in {2,3,5,7}` | Gao–Zhuang Thm 1.6(iii) | proved |
| any `p`-group, `k in [1, p-1]` | Girard Thm 2.1 | proved |
| `C_p + H`, `H` any abelian `p`-group | Girard Cor 2.2 | proved — covers **all** elementary abelian `C_p^r`, every `p` |
| **all rank-two groups** `C_m + C_mn` | Girard Thm 2.5 + Property B (Reiher; Gao–Geroldinger–Grynkiewicz) | proved **unconditionally** |

**What is actually open:** `k >= p`, with `G` neither cyclic, nor rank `<= 2`,
nor of the form `C_p + H` — i.e. **rank `>= 3` with `n_1` composite**. The
smallest reachable target is `G = C_4^3` (`|G| = 64`, `D = 10`, `d = 9`) at
`k in {2,3}`.

And the hunt has a **shape** rather than being blind: Gao–Zhuang **Conjecture
5.3** is the precise obstruction — a zero-sum-free `W` with `|W| = D(G)-1` and
`v_g(W) = ord(g)-1` for some `g` with `ord(g) < n_1` would yield
`g^{ord(g)} W` as a counterexample to 4.9.

One gap is honestly open: Guan–Yuan–Zeng, *Normal sequences over finite abelian
groups*, JCTA 118 (2011) 1519–1524, is behind a paywall (403). Its abstract
mentions p-groups **or** rank-two groups, and it cannot be ruled out that it
settles all p-groups — which would remove `C_4^3` as a target. Recorded as
`CANNOT_CHECK_ACCESS`, not inferred either way.

Two name-collision traps were avoided and are worth recording: arXiv:2311.02387
concerns a *different* Gao–Zhuang conjecture (small Davenport constant of
**non-abelian** groups), and Girard–Schmid's "Conjecture 2.2" is a different Gao
conjecture about `eta`/EGZ constants.

Also noted from reading the primary text: the survey's essentiality example has a
typo — `v_g(S) = ord(g)-1` should read `v_g(T)`.

## Standing correction to X1-G

The X1-G document's "OPEN QUESTION — this is the one regularity that looks like a
theorem waiting for a proof" should be read as answered: it *is* a theorem, it was
already proved, and the census was rediscovering it. The census remains valid as
data; the framing was wrong.

## Authority

`mathematical_proposal: false` — nothing here is proposed as new.
`novelty_claim: false`. The contribution is verification and attribution.
