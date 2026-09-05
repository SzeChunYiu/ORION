# Multiplicative half-interval stability from translation boundaries

Status: **proved elementary, prime-uniform inverse lemma**. This note supplies a bounded-hole replacement for exact half-interval invariance. No enumeration or external inverse theorem enters the proof.

Let `p=2H+1` be an odd prime, let `I={1,...,H}` in `F_p`, and let `gamma` be nonzero. Define

\[
d=|I\setminus\gamma I|=\tfrac12|I\mathbin\triangle\gamma I|.
\]

For a nonzero residue `z`, write `||z||_p=min([z]_p,[-z]_p)`.

## 1. Both the multiplier and its inverse are small

**Theorem.** One always has

\[
\boxed{\|\gamma\|_p\le 2d+1,
\qquad \|\gamma^{-1}\|_p\le 2d+1.}
\tag{1}
\]

The interval has an exact translation boundary:

\[
|I\mathbin\triangle(I+z)|=2\|z\|_p.
\tag{2}
\]

Indeed, a translate by a centered positive displacement `a<=H` has intersection of size `H-a` with `I`; the negative displacement has the same intersection size.

The symmetric-difference triangle inequality, translation invariance, and `|(gamma I) triangle (gamma I+gamma)|=|I triangle (I+1)|=2` give

\[
\begin{aligned}
|I\mathbin\triangle(I+\gamma)|
&\le |I\mathbin\triangle\gamma I|
 +|\gamma I\mathbin\triangle(\gamma I+\gamma)|
 +|(\gamma I+\gamma)\mathbin\triangle(I+\gamma)|\\
&=4d+2.
\end{aligned}
\]

Equation (2) proves the first inequality of (1). Multiplication by `gamma` shows `|I triangle gamma^{-1} I|=|I triangle gamma I|`, so the same argument proves the second.

## 2. A quantitative rigidity threshold

If

\[
d<H,\qquad p>(2d+1)^2+1,
\tag{3}
\]

then `gamma=1`.

For proof, take signed centered representatives `a,b` of `gamma,gamma^{-1}`. By (1), `|a|,|b|<=2d+1`. Their ordinary product satisfies `ab==1 (mod p)` and

\[
|ab-1|\le(2d+1)^2+1<p.
\]

Therefore `ab=1` as integers, which leaves `a=b=1` or `a=b=-1`. The latter would give `gamma=-1`, for which `I` and `-I` are disjoint and `d=H`, contrary to (3).

Equivalently, if `alpha,beta` are nonzero and

\[
J=\{j\in\mathbb F_p^*:[j\alpha]_p\le H,
                              [j\beta]_p\le H\},
\qquad |J|\le b<H,
\]

then

\[
\boxed{p>(2b+1)^2+1\quad\Longrightarrow\quad\alpha+\beta=0.}
\tag{4}
\]

To check the conversion, put `theta=beta/alpha`. Scaling the index gives `|J|=|I intersection theta^{-1} I|=|I intersection theta I|`. Since `-theta I` is the complement of `theta I` inside `F_p^*`,

`|I\setminus(-theta I)|=|J|`.

Apply (3) to `gamma=-theta` and `d=|J|`.

## 3. Exact scope

The threshold is sufficient; optimality is not claimed. Even below the threshold, the two centered bounds (1) remain valid restrictions on every possible multiplier. Thus the argument preserves information at the unresolved small endpoints instead of treating them as classified.

This is a statement about actual finite sets and their translation boundaries. It does not assume that a small symmetric difference is zero. The ordinary-product step is justified only by the strict inequality in (3).

The proof was checked locally for the translation formula, inverse symmetry, signed-product endpoint, and the conversion from an intersection to a symmetric difference. No separately tasked or external referee review is claimed.
