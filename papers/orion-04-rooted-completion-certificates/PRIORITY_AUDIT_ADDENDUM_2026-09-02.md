# ORION-04 priority-audit addendum — 2026-09-02 refresh

**Verdict: PARTIAL.** No retrieved source establishes \(D_4(C_5^3)=30\) or any
exact \(D_k(C_5^3)\). The **lower-bound half of the paper's formula is
published prior work** and must be (and now is) attributed in the manuscript.

## Load-bearing finding, independently verified

Freeze & Schmid, *Remarks on a generalization of the Davenport constant*,
Discrete Math. 310 (2010) 3373–3389 (arXiv:0905.4248), **Theorem 4.1**:
for \(G=C_{n_1}\oplus\cdots\oplus C_{n_r}\), \(s\in\mathbb N\setminus\{1\}\),
\(t\in[1,r]\) with \(s(s-1)/2\le r-t+1\),
\(\mathsf D_k(G)\ \ge\ \mathsf D^*(G)+s\lfloor n_t/2\rfloor+\delta+(k-2)n_r\),
where \(\delta=1\) iff \(n_t\) is odd. Instantiated at \(G=C_5^3\), \(s=3\),
\(t=1\) (hypothesis holds with equality \(3\le3\)), \(\delta=1\):
\(\mathsf D_k(C_5^3)\ \ge\ 13+6+1+5(k-2)\ =\ 5k+10\) for every \(k\ge2\).
The theorem statement, the \(\delta\) rule and the hypothesis were verified
against the full text (ar5iv render of arXiv:0905.4248) on 2026-09-02, not
against the abstract alone. Consequence: ORION-04's contribution is the
**matching upper bound** (tightness of the Freeze–Schmid bound for \(C_5^3\)
from \(k=2\) onward), not the corridor's lower line. The earlier
conditional-corridor manuscript
(`submission/Conditional_Davenport_Corridors_...tex`) already cited this
correctly; the V4 unconditional manuscript had dropped the attribution and is
now corrected.

## Why the exact value is plausibly open

- \(\eta(C_5^3)\) has no published exact value; Fan–Gao–Zhong, J. Number
  Theory 131 (2011) 1864–1874, prove \(s(C_5^3)=\eta(C_5^3)+4\) (Gao's
  conjecture for \(C_5^3\)) without determining either constant, so no exact
  \(D_k(C_5^3)\) follows from the known machinery
  (e.g. \(\mathsf D_k(G)\le (k-1)\exp(G)+\max\{\mathsf D(G),\eta(G)-\exp(G)\}\),
  Freeze–Schmid Remark 3.3).
- Zhong, *On the Inverse Problem of the k-th Davenport Constants for Groups
  of Rank 2* (arXiv:2503.21231; Combinatorica 2025) states computing or even
  bounding \(\mathsf D_k(G)\) remains difficult for elementary \(p\)-groups
  and records exact values only for rank \(\le 2\)
  (\(\mathsf D_k=n_1+kn_2-1\)), elementary 2-groups of rank \(\le 5\)
  (Freeze–Schmid; rank \(\le3\) Delorme–Ordaz–Quiroz, Discrete Math. 237
  (2001) 119–128), and \(C_3^3\).

## Nearest exact rank-three companion (referee comparison set)

\(C_3^3\): \(D_1=7\), \(D_2=11\), \(D_k=3k+6\) for \(k\ge3\)
(Bhowmik–Schlage-Puchta, *Davenport's constant for groups of the form
\(\mathbb Z_3+\mathbb Z_3+\mathbb Z_{3d}\)*, CRM Proc. Lecture Notes 43, AMS
2007, 307–326; recorded in Freeze–Schmid Remark 5.3). The Freeze–Schmid bound
\(3k+5\) is attained at \(k=2\) and strictly exceeded for \(k\ge3\) — the
opposite tightness regime from the \(C_5^3\) result, stated in the manuscript
as data.

## Search record

Vocabulary: generalized/k-th/k-wise Davenport constant, \(C_5^3\), \(C_p^3\),
elementary abelian rank three, zero-sum free, short zero-sum sequences,
\(\eta(G)\), \(s(G)\); author sweeps Gao, Geroldinger, Schmid, Halter-Koch,
Girard, Plagne, Tringali, Freeze, Fan, Zhong, Bhowmik, Schlage-Puchta;
2024–2026 sweep included Biswas–Mazumdar (arXiv:2402.09999) and Zhang
(arXiv:2310.05458) — classical \(\mathsf D\)/\(s_L\) invariants only, no
\(D_k\) for \(C_5^3\).

**`CANNOT_CHECK` (named, not claimed clear):** MathSciNet; zbMATH; paywalled
published versions where only arXiv versions were read (Freeze–Schmid read in
full via arXiv; Zhong via arXiv; Fan–Gao–Zhong via arXiv); the
Bhowmik–Schlage-Puchta CRM volume full text (values confirmed via
Freeze–Schmid's recording of them, not an end-to-end read).

## Consequences applied

1. `WAVE3_SCOPED_MANUSCRIPT_V4.md`: lower bound attributed to Freeze–Schmid
   Thm 4.1 in the abstract-adjacent statement, Section 1, and the novelty
   section; \(C_3^3\) contrast added; contribution reframed as tightness.
2. Routing (ORION-paper#49 A1): the JCTA-stretch case must lead with the
   upper-bound method and the \(p=3\)/\(p=5\) tightness-threshold contrast;
   the exact-value claim remains collision-free in searched sources.
3. No change to any computation, evidence artifact, or claim ledger number:
   this is attribution and framing only; the theorem and its authority chain
   are untouched.
