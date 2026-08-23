# Q1 self-contained proof insertion specification

This document identifies the mathematical content that must move from the
development protocol into the Q1 article. It is not a competing manuscript and
does not change the theorem.

## Definitions required before the theorem

Use local Pauli letters `I,X,Y,Z` modulo phase with local product, local
symplectic form, and Hamming support. For three ordered two-target blocks
`j in {A,B,C}` and branch `k in {0,1}`, define six nonzero frame Paulis
`R_jk` satisfying

```text
symp(R_j0,R_j1)=1  for each block j.
```

Define a Tag Pauli `S` and common labels `l0 != l1` satisfying

```text
symp(S,R_j0)=l0,
symp(S,R_j1)=l1
```

for all three blocks. State explicitly that no cross-block frame constraint is
present and that the Tag couples blocks only through these six labels.

For fixed relative permutations and central bits, define branch targets

```text
T_jk = P_{j,pi_j(k)} R_jk.
```

The exact raw-support objective is

```text
C = sum_j [4 w(R_j,nc) + 2 w(R_j,c)] - 18 + 2 w(S)
    + sum_{k in {0,1}} sum_q F3(T_Ak[q],T_Bk[q],T_Ck[q]),
```

where

```text
F3(a,b,c)=1                  if a=b=c!=I,
F3(a,b,c)=w(a)+w(b)+w(c)    otherwise.
```

Define the unrestricted optimum `C_DP` and the restricted optimum `C_2` in
which all six frames have support at most two. Only after proving equivalence
may the paper identify `C_2` with the implementation's support-two search.

## Theorem

For every qubit count, every six-target instance, every matching, every pair of
relative permutations, and every central-bit triple in the stated grammar,
there is an optimal feasible configuration in which every frame Pauli has
support at most two. Equivalently,

```text
C_DP = C_2.
```

The theorem is about this grammar and objective. It does not imply lower
physical width, depth, T count, fault-tolerant cost, or runtime.

## Lemma 1: zero-sum support subset

Fix a frame `R`, its partner `R_p`, and Tag `S`. For every
`q in supp(R)`, define

```text
alpha(q)=local_symp(R[q],R_p[q]),
beta(q)=local_symp(S[q],R[q]),
class(q)=(alpha(q),beta(q)) in F_2^2.
```

Because `symp(R,R_p)=1`, the alpha sum over `supp(R)` is odd.

**Claim.** If `w(R)>=3`, the support contains a nonempty proper subset `Q`
of size at most two with both alpha and beta sums zero.

**Proof.** A class `(0,0)` yields a singleton. Otherwise an equal-class pair
yields a zero-sum pair. If neither exists, all classes are distinct members of
`{(0,1),(1,0),(1,1)}`, so the support has size at most three. Size three forces
all three classes and hence even alpha sum, contradicting the odd alpha sum.
For support greater than three, distinctness is already impossible. Because
`|Q|<=2<w(R)`, `Q` is proper. QED.

State the selection rule—lowest `(0,0)` singleton, otherwise lowest equal pair—
only for executable determinism; the theorem does not depend on which valid
subset is selected.

## Lemma 2: feasibility-preserving exchange

Let `R'` be obtained by setting the letters of `R` on `Q` to identity and
leaving every other object unchanged. Then `R'` remains nonzero because `Q` is
proper. Moreover,

```text
symp(R',R_p)=symp(R,R_p)+sum_Q alpha=1,
symp(S,R')=symp(S,R)+sum_Q beta.
```

Thus anticommutation and the common Tag label are preserved; all other
acceptance constraints involve untouched Paulis. This is the wording that
removes the earlier ambiguity: **zero the selected zero-sum subset `Q`; do not
retain only `Q`, and do not remove its complement.** No Tag repair is needed.

## Lemma 3: local cost inequality

At a zeroed qubit, let `f` be the old nonidentity frame letter, `p` the target
letter, and `u,v` the other two block letters on the same branch. The frame
refund is `m in {2,4}`. The exact local change is

```text
Delta_q = F3(p,u,v)-F3(p f,u,v)-m.
```

The article must state that direct enumeration over

```text
f in {X,Y,Z};
partner, Tag, p, u, v in {I,X,Y,Z};
m in {2,4};
slot in {A,B,C}
```

contains 18,432 cases and has `Delta_q<=0` throughout. The partner and Tag
letters are swept because they define the class table even though they do not
enter the scalar inequality. The maximum F3 increase is two, so equality can
occur only for multiplier two.

Include either the complete finite table/certificate in the supplement or a
short independent case proof plus the exact exhaustive checker. Report the
domain count and zero violations in the article.

## Theorem proof by well-founded descent

Among all feasible configurations, choose one minimizing lexicographically

```text
(C, total frame support).
```

If a frame has support at least three, Lemma 1 provides `Q`; Lemma 2 produces a
feasible exchange; and Lemma 3 shows that cost does not increase while total
support decreases by at least one. This contradicts lexicographic minimality.
Therefore every frame in the selected optimum has support at most two. The
restricted and unrestricted optima are equal. Minimization over permutations,
central choices, and matchings preserves the equality. QED.

The final paragraph must prove, rather than merely cite, that the paper's
support-two mathematical family equals the implemented support-two search,
including the minimum-weight feasible Tag sweep.

## Sharpness at support two

For support two, odd alpha sum means exactly one qubit has `alpha=0`. A proper
zero-sum singleton exists exactly when that qubit also has `beta=0`. The four
failing ordered class pairs are the odd-alpha pairs in which the alpha-zero
qubit has beta one. These are precisely the patterns in which zeroing the
locally commuting qubit flips the Tag syndrome. Connect this algebraic boundary
to the exact support-one counterexample, with a proof that the restricted search
enumerates every support-at-most-one feasible configuration.

This sharpness result is a retained negative about support-one closure, not a
defect to hide.

## Independent proof review checklist

1. All objects and costs are defined without code names.
2. Every feasibility constraint is shown invariant under the exchange.
3. The local cost change lists every term that can move.
4. The 18,432-domain completeness follows from the definitions.
5. Lexicographic minimization is over a finite nonempty feasible set.
6. The support-two family is exactly the restricted implementation family.
7. The support-one witness establishes necessity, not only failure of one
   exchange rule.
8. The claim boundary excludes physical-resource and empirical superiority.
