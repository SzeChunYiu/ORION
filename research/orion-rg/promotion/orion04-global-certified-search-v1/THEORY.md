# Complete pseudo-Boolean encoding of the length-31 obstruction

## Object

Write `V=F_5^3` and let `m_g` be the multiplicity of `g` in a candidate sequence. The parent Wave-3 theorem permits the prospective restrictions

```text
m_0 = 0,
m_g in {0,1,2,4},
sum_g m_g = 31,
|{g:m_g>0}| >= 14.
```

The obstruction additionally satisfies

```text
sum_g m_g g = 0 in V
```

and contains no nonempty zero-sum submultiset of cardinality at most five.

## One-hot multiplicities

For each nonzero `g`, introduce binary variables `m1_g,m2_g,m4_g` with

```text
m1_g + m2_g + m4_g <= 1.
```

Then

```text
m_g = m1_g + 2 m2_g + 4 m4_g.
```

The exact threshold indicators are linear expressions:

```text
[m_g >= 1] = m1_g + m2_g + m4_g,
[m_g >= 2] = m2_g + m4_g,
[m_g >= 3] = m4_g,
[m_g >= 4] = m4_g.
```

Because the one-hot inequality is enforced, every displayed expression is binary on every feasible assignment.

## Length and total sum

Length is one equality. For each coordinate `j`, introduce five quotient bits `q_j,0,...,q_j,4` and impose

```text
sum_g coordinate_j(g) m_g = 5 sum_b 2^b q_j,b.
```

The left side lies in `[0,124]`, so equality itself limits the quotient to `[0,24]`; no separate upper bound is needed.

## Short-zero constraints

Let `T` be a nonzero zero-sum multiset of cardinality `2<=k<=5`. For every distinct point `g` occurring in `T`, let `c_T(g)` be its multiplicity. If any `c_T(g)=5`, then `T` is already impossible because `m_g<=4` and no constraint is needed. Otherwise define the exact threshold expression `a(g,c_T(g))` from the table above.

The candidate contains `T` exactly when all these threshold indicators equal one. Therefore the single inequality

```text
sum_{g in supp(T)} a(g,c_T(g)) <= |supp(T)| - 1
```

forbids precisely that submultiset.

## Complete enumeration

Encode points by their base-`p` coordinate integer and use the induced total order. For each `k`, choose a nondecreasing prefix

```text
x_1 <= ... <= x_{k-1}
```

of nonzero points. The zero-sum equation uniquely determines

```text
x_k = -(x_1+...+x_{k-1}).
```

Emit a constraint exactly when `x_k` is nonzero and `x_{k-1}<=x_k`. Every sorted nonzero zero-sum multiset has one and only one such prefix, so this is a bijective enumeration rather than sampled coverage.

## Rank-three normalization

An admissible support cannot lie in a rank-at-most-two subgroup: its length is 31, whereas the registered short-zero threshold for `C_5^2` is 13. Thus the support contains an independent triple. `GL(3,5)` sends that triple to `e1,e2,e3`, so requiring the standard basis in the support loses no orbit. Permuting the selected triple permits the additional order

```text
m(e1) >= m(e2) >= m(e3).
```

The generator encodes the order by threshold implications at levels two and four. No claim of a unique representative is needed; the condition only guarantees at least one representative of every orbit.

## Soundness and completeness theorem

**Theorem.** The registered full OPB instance is satisfiable if and only if a length-31 total-zero sequence over `C_5^3`, having no nonempty zero-sum subsequence of length at most five, exists.

**Proof.** From a sequence, choose an independent support triple, map it to the standard basis, order the triple by multiplicity, and set its one-hot variables. Length, support, and coordinate equalities hold. Every emitted short-zero inequality holds because the corresponding submultiset is absent.

Conversely, any feasible one-hot assignment defines multiplicities in `{0,1,2,4}`. The equalities give length 31 and total sum zero. The basis constraints give rank-three support and the support inequality preserves the parent lower bound. If a forbidden short zero existed, its sorted multiset would be emitted exactly once and all of its threshold indicators would be one, violating its inequality. Therefore no such submultiset exists. `square`

## Proof authority

The theorem proves that the instance represents the mathematical object. It does not prove the instance SAT or UNSAT. A positive UNSAT terminal additionally requires a complete proof checked by an independently pinned proof checker. A positive SAT terminal requires a concrete assignment checked by the standalone witness verifier. Missing proof bytes, a timeout, or a solver status line yields `CANNOT_CHECK`.
