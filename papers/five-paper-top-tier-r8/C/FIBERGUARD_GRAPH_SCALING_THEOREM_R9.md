# FiberGuard Graph Scaling Theorem R9

Date: 2026-08-26

Status: analytic theorem candidate with independent finite controls. This note strengthens the graph-colouring lane of FiberGuard from a bounded six-vertex collision to an unbounded family for the frozen representation

\[
\Phi(G)=\bigl(\text{sorted degree sequence of }G,\;\#K_3(G)\bigr).
\]

The graph family used in the proof is donor mathematics. The paper-specific result is the exact collision theorem for the declared representation and target, together with its information-radius consequences.

## Donor input

For integers \(n\ge 2r\) and \(r\ge2\), the Häggkvist–Hell graph \(H_{n:r}\) has

\[
N_{n,r}=(n-r)\binom nr
\]

vertices, is regular of degree

\[
d_{n,r}=r\binom{n-r-1}{r-1},
\]

and is triangle-free. For every fixed \(r\ge2\), its chromatic number is unbounded as \(n\) grows. These facts are due to D. E. Roberson, “Häggkvist–Hell Graphs: A Class of Kneser-Colorable Graphs,” *Discrete Mathematics* 312 (2012), 837–853, DOI 10.1016/j.disc.2011.10.011; arXiv:1008.2199.

## Theorem C-R9.1 — unbounded exact fibers

Fix any \(r\ge2\). For every integer \(k\ge2\), there are two finite simple graphs \(B_k\) and \(X_k\) on the same number of vertices such that

\[
\Phi(B_k)=\Phi(X_k),
\qquad
\chi(B_k)=2,
\qquad
\chi(X_k)\ge k.
\]

Consequently the target diameter of a single \(\Phi\)-fiber is at least \(k-2\), and the global fiber diameter of \(\Phi\) for chromatic number is unbounded.

### Proof

Because \(\chi(H_{n:r})\) is unbounded for fixed \(r\), choose \(n=n(k,r)\) such that

\[
\chi(H_{n:r})\ge k.
\]

Write \(N=N_{n,r}\) and \(d=d_{n,r}\). Let

\[
X_k=H_{n:r}\sqcup H_{n:r}.
\]

Then \(X_k\) has \(2N\) vertices, is \(d\)-regular and triangle-free, and

\[
\chi(X_k)=\chi(H_{n:r})\ge k.
\]

Now construct a bipartite graph \(B_k\) with parts

\[
L=R=\mathbb Z/N\mathbb Z
\]

and edges

\[
i_L\sim(i+j)_R\qquad(0\le j<d).
\]

The Häggkvist–Hell graph is simple, so \(d\le N-1\); hence the displayed shifts are distinct. The graph \(B_k\) is therefore a simple \(d\)-regular bipartite graph on \(2N\) vertices. It has at least one edge and thus \(\chi(B_k)=2\). It is triangle-free.

Both graphs have the degree multiset consisting of \(2N\) copies of \(d\), and both have triangle count zero. Therefore

\[
\Phi(B_k)=((d,\ldots,d),0)=\Phi(X_k).
\]

Their chromatic numbers differ by at least \(k-2\). ∎

## Corollary C-R9.2 — exact representation lower bounds

For any method whose input is exactly \(\Phi(G)\):

1. the worst-case absolute error of every real-valued chromatic-number estimator is unbounded;
2. every exactly valid interval rule has unbounded worst-case width;
3. for every \(k\), a common output on the displayed fiber incurs absolute error at least \((k-2)/2\);
4. a randomized classifier of the Boolean property “the graph is bipartite” has worst-case error at least \(1/2\) on the displayed fiber.

Items 1–4 follow from the standard fiber-diameter/endpoint argument. The general minimax machinery is donor-owned optimal-recovery mathematics; the exact graph family supplies the nontrivial frozen-representation fibers.

## What this closes

- The graph-colouring `C-SCALING-FAMILY` blocker is analytically closed for unbounded target diameter under the exact R8 graph feature map.
- No disjoint-union assumption about chromatic additivity is hidden: chromatic number of a disjoint union is the maximum of component chromatic numbers.
- The construction is exact for all \(k\), not inferred from finite enumeration.

## What remains open

- The theorem does not show that these collisions occur frequently in production or public learned-optimizer corpora.
- It does not prove insufficiency for a model receiving richer graph features.
- It does not establish that the same scalable mechanism holds for the set-cover or 2-CNF feature maps.
- It does not by itself establish novelty; an exact-statement primary-source audit is still required.
- It does not establish operational benefit for abstention or routing; that remains an empirical decision-pipeline question.

## Finite controls

`cleanroom/fiberguard_graph_scaling_r9.py` independently constructs \(H_{n:2}\), its two-copy graph, and the matched circulant bipartite graph. It checks the exact feature equality, regularity, triangle-freeness, and exact chromatic numbers for \(n=4,5,6\). The finite rows give collision diameters \(0,1,2\), respectively. These computations protect the implementation and indexing; the all-size authority is the displayed proof plus the cited donor theorem.
