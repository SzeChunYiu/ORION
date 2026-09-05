# Type two: complete positive-congruence overlap layers — V1

Status: **proved prime-uniform whole-layer elimination**. Together with the existing negative class, this excludes both `p == +1` and `p == -1` modulo `2(H-c+1)`.

## 1. Hypotheses and theorem

Use the explicit **zero-sum** rank-two companion hypotheses of `A2_RANK2_EXACT_QUOTIENT_DEFECT_BUDGET_V1.md`:

\[
p=2H+1\ge7,
\quad 1\le c<H,
\quad a=H-c+1,
\quad R=x^r y^t,
\quad |R|=p+a-1,
\quad r,t\le p-1.
\]

Here `2≤a≤H`. Every cyclic quotient atom has a defect `1≤D≤a−1`, unique possible length

\[
\ell_D=[(a-1)Da^{-1}]_p,
\qquad \ell_D+D\equiv0\pmod2,
\]

and every atomic factorization has total defect `a`.

Assume

\[
\boxed{p\equiv1\pmod{2a}.}
\]

Write `p=2aL+1` with integer `L≥1`, and put `w=2L+1≥3`. Since `a^{-1}=−2L` modulo `p`,

\[
\ell_D=[wD]_p.
\]

Moreover

\[
0<wD\le(2L+1)(a-1)=p+a-2L-2<2p.
\]

The equality `wD=p` is impossible: `wD≡(a−1)Da^{-1}≠0` modulo `p`. Thus the canonical length is either `wD` or `wD−p`. Because both `w` and `p` are odd, the required parity `ell_D+D` even forbids the second alternative. Consequently every actual atom length is the ordinary multiple `wD` of `w≥3`.

The quotient contains atoms because it is nonempty zero-sum. Their length gcd is at least `w`, so the dichotomy in `TWO_VALUE_LATTICE_ATOMS_AND_LENGTH_GCD_DICHOTOMY_V1.md` forces a unique atomic divisor. Since `|R|>p`, its quotient is a rigid power. The established `CYCLIC_TWO_VALUE_RIGID_POWER_BOUND_V1.md` reduces every such type-two rigid power to a saturated new-value row, and `A2_RANK2_SATURATED_BOUNDARY_FULL_ELIMINATION_V1.md` eliminates that row. Hence this whole overlap layer is impossible.

> **Positive-class whole-layer theorem.** Under the canonical rank-two type-two hypotheses, every layer satisfying
>
> \[
> \boxed{2(H-c+1)\mid(p-1)}
> \]
>
> is empty. No square-root restriction on `H−c` is used.

Equivalently, for integers `a≥2,L≥1` with prime `p=2aL+1`, the layer `H=aL`, `c=a(L−1)+1` is excluded. Combined with the previously proved negative class, both congruences `p≡±1 (mod 2a)` are now eliminated whenever the overlap is in the stated range.

## 2. Review and boundary

The proof-audit and quotient-structure lanes independently checked the least-residue formula, the possible single wrap, parity, and the actual rigid-power dependency. The coordinating researcher reviewed the integration. The saturated-boundary dependency retains its separately attributed Bernoulli-pairing input. No condition `(H-c)^2<p` is required.

The other residue classes can have an atomic length spectrum of gcd one; they are not eliminated by this argument. The full first corridor and the generalized Davenport formula remain open.
