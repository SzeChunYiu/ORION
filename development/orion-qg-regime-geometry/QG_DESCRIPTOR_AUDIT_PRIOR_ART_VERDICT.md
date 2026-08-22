# Hostile novelty check: "descriptor-completeness certificates via symmetry quotients"
Date 2026-08-22. Verdict: **KILLED** (conceptual claim). Residual: a small engineering/tooling note, not a theorem.

## 1. The trichotomy is the textbook classification of invariant statistics

Lehmann's **maximal invariant** (Testing Statistical Hypotheses, ch.6; Lehmann-Casella 3.1.7).
Verified verbatim in Hoff, Duke STAT 732 notes `invariance.pdf` (local: hoff_invariance.txt):

- Definition 8: u invariant iff u(gx)=u(x) for all g,x.            -> negation = regime (iii)
- Definition 9: y maximal invariant iff invariant AND
  y(x1)=y(x2) => x2 = g x1.                                        -> regime (i), verbatim
- Theorem 4: "A function u(x) is invariant iff it is a function of
  a maximal invariant y(x)."                                       -> regime (ii), verbatim
  (also Theorem 8: "Any invariant function is a function of the maximal invariant.")
- Notes state invariant functions are constant on orbits; a maximal invariant
  "identifies the orbits"; there is an exercise to draw how a maximal invariant
  PARTITIONS the sample space. The partition framing is explicit.

Theorem 4 IS the claim "an invariant-but-incomplete descriptor strictly coarsens the orbit
partition". Regime (i) IS Definition 9. Regime (iii) IS failing Definition 8.
Nothing conceptual is left. This is 1959 material.

## 2. The PROCEDURE (enumerate, compute partition, compare, count collisions) is routine

Balcilar et al., ICML 2021, "Breaking the Limits of Message Passing GNNs", arXiv:2106.04319.
graph8c = all 11,117 connected non-isomorphic 8-node graphs (= orbit reps under S_8, taken
from McKay's nauty lists). All 61M pairs compared; Table 1 reports UNDISTINGUISHED PAIRS:
  PPGN 0, GNNML3 0   <- regime (i) on that object space
  ChebNet 44, GIN 386, GAT 1828, GCN 4775, MLP 293K  <- regime (ii), loss quantified exactly
They even cite "the theoretical limit of the 1-WL test which is 312 pairs".
That is: compute D's partition, compare against the orbit partition, emit the exact gap.

Same protocol: Joshi et al. ICML 2023 (geometric GNNs, GWL); the `graph8c`/`sr25`/`EXP`
collision benchmarks are a standard expressivity instrument.

## 3. The exact partition/quotient statement is published

Pacini, Dong, Lepri, Santin, "Separation Power of Equivariant Neural Networks",
ICLR 2025, arXiv:2406.08966. Line 394-396 of the PDF:

  "...P is a partition of X, that may either combine several orbits from the orbit
   partition X = X_1 u ... u X_n into larger subsets, or coincide with the orbit
   partition itself."

= regimes (i) and (ii) as a formal characterization. Paper's stated contribution is
"a complete characterization of the inputs indistinguishable by models derived from a
given architecture", plus a refinement-lattice ("Q finer than P ... Q <= P") for
COMPARING separation powers. That is the "which quotient is my feature" question, solved
and published.

## 4. Invariant theory already owns the algebraic core

Derksen & Kemper, Computational Invariant Theory (Springer 2002/2015): **separating sets /
separating algebras**. S is separating if whenever some invariant separates x,y, some
element of S does. Kemper, "Separating Invariants", J. Symb. Comput. 2009: finite
separating subsets always exist; Noether degree bound holds for separating invariants in
any characteristic, giving an algorithm for finite groups.
KEY: for |G| < inf, invariants separate ALL orbits -> "complete" == "separating" exactly.
The orbit-closure subtlety (non-reductive/non-compact G) collapses in the finite case.
Blum-Smith & Villar, "Machine Learning and Invariant Theory", Notices AMS 70(8):1205-1213,
2023 (arXiv:2209.14991) already draws the ML <-> separating-invariants connection and
flags separating invariants as an active ML direction (their refs [9] Cahill-Iverson-
Mixon-Packer max filtering, [17] Dym-Gortler, [42] Olver moving frames).

## 5. Domain instances already audited

- Pozdnyakov, Willatt, Bartok, Ortner, Csanyi, Ceriotti, "Incompleteness of Atomic
  Structure Representations", PRL 125, 166001 (2020), arXiv:2001.11696 -- regime (ii)
  proven for 3-/4-body descriptors by explicit degenerate manifolds.
- Nigam, Pozdnyakov, Huguenin-Dumittan, Ceriotti, "Completeness of atomic structure
  representations", APL Mach. Learn. 2, 016110 (2024), arXiv:2302.14770 -- constructive
  complete descriptors.
- Widdowson & Kurlin, CVPR 2023 (arXiv:2303.15385) + PDD (MATCH 87:529, 2022):
  complete + continuous + polynomial-time computable isometry invariants; PDD separated
  all 660k+ CSD crystals. Explicitly the computable-complete-invariant business.
- Color refinement = coarsest equitable partition; the refinement LATTICE settles
  canonically "which quotient" (Tinhofer 1991, Godsil 1997, Ramana-Scheinerman-Ullman 1994).

## 6. Regime (iii) is also already instrumented

"Invariance error" is a routinely reported metric in the frame-averaging /
canonicalization literature: Puny et al. ICLR 2022 (Frame Averaging); Lin et al.
"Equivariance via Minimal Frame Averaging" arXiv:2406.07598 (reports invariance error as
a headline metric); Dym, Lawrence, Siegel arXiv:2402.16077 (impossibility of continuous
canonicalization; stabilizer lower-bounds frame size). Measuring how far a feature map is
from invariant is standard.

## 7. HOSTILE CHECKS ON THE WORKED EXAMPLE

### Check A -- orbit arithmetic. PASSES. Independently recomputed (orbits.py).
  positions only  S_2 wr S_3        |G| =  48 -> 220 orbits
  letters only    S_3 diagonal      |G| =   6 -> 715 orbits   <-- THIS is the 715
  FULL S_3 x (S_2 wr S_3)           |G| = 288 ->  54 orbits   <-- matches the 54 classes
The "715 reps" are representatives of the LETTER group's orbits, not the full group's.
The inference is nonetheless VALID: D invariant => D's partition coarsens the orbit
partition; |D-classes| = 54 = |orbits| forces equality for finite partitions. So the
"both refinement directions" conclusion stands. (Advisor's one-direction worry: resolved
by the cardinality match, which supplies the converse.)

### Check B -- is completeness by construction? LIKELY, BUT ONLY A DEFINITION READ SETTLES IT.
The full group is exactly "unlabel the letters (S_3 on {X,Y,Z}) AND unlabel the positions
(swap within blocks, permute blocks)". The descriptor is NAMED
"**unlabeled** one-active defect spectrum", and a "spectrum" is plausibly a multiset --
and a multiset over a permuted index set IS the canonical form for that permutation action.

BUT the name alone does NOT license the conclusion, and my own numbers show why:
unlabeling positions ONLY gives 220 classes; unlabeling letters ONLY gives 715. Neither is
54. Hitting 54 requires the descriptor to be canonical in BOTH factors JOINTLY, in exactly
the S_3 x (S_2 wr S_3) wreath structure. That is a stronger coincidence than "it has the
word unlabeled in its name" can explain. So this is a flag, not a finding.

Corroborating asymmetry (the best evidence, and it survives): the *bulk signature* is the
one NOT named "unlabeled", and it is precisely the one that fails invariance (regime iii).
Naming appears to track construction.

ACTION for team lead: read the literal definition of the spectrum. If it is a canonical
form / multiset in both factors jointly, the "apparently by accident" framing evaporates
and the finding is a bookkeeping observation. If it is canonical in only one factor and
still lands on 54, that IS a genuine coincidence worth recording.

## 8. The finite case does not need the machinery it borrows
Finite group on a finite set = union-find + partition comparison. No Groebner bases, no
separating-set theory, no orbit closures. The genuinely hard version (infinite groups,
continuous descriptors, orbit closures, Lipschitz-continuous complete invariants) is
exactly where Derksen-Kemper, Kurlin, and the chemistry-ML groups already live.

## 9. What survives (evaluated honestly, none of it strong)
(a) "Audit an existing descriptor rather than design a complete one" -- DEAD. Balcilar
    audits deployed models this way; Pozdnyakov audits deployed SOAP/power-spectrum;
    Pacini gives the general characterization theorem.
(b) "Quantify regime (iii), 168/715" -- DEAD as a concept. Invariance error is a standard
    reported metric. The number is a fact about your pipeline, not a method.
(c) "Symmetry group was never written down by the practitioners" -- THIN BUT NOT ZERO.
    The symmetry-DISCOVERY literature (LieGG, LieGAN, SymmetryLens, equivariance
    detection, arXiv:2503.03014 / 2410.05232) is overwhelmingly continuous/Lie and
    learning-based. An exact, finite-group, enumerate-and-certify audit that both infers
    the candidate group and certifies the regime is a tooling gap. It is an engineering
    note, not a theorem. Do not oversell.

## 10. Searched vs could-not-search
SEARCHED, found prior art: statistics (maximal invariants, via Hoff notes citing
Lehmann-Casella -- textbook, went to the statement directly since arXiv absence proves
nothing for 1959 material); GNN expressivity; equivariant-network separation power;
computational invariant theory / separating invariants; chemistry-ML descriptor
completeness; complete isometry invariants; color refinement / equitable partitions;
frame averaging / invariance error; symmetry discovery; QEC syndrome degeneracy.
COULD NOT SEARCH: Semantic Scholar API (HTTP 429 throughout, no key). Notices AMS PDF
returned 403 to WebFetch -- used the arXiv version (2209.14991) instead. Did not read
Derksen-Kemper or Lehmann primary texts directly (paywalled/print); relied on Hoff's
notes for verbatim theorem statements and on Kemper's own ISSAC tutorial + JSC paper
descriptions for separating invariants.

## 11. FEASIBILITY SCOPE (scoped, not run)

### Instance 1 -- graphs on <= 7 vertices (honest stress test)
Object space: 1044 unlabeled graphs on <=7 vertices (11,117 connected on 8).
Group: S_n on vertices; orbit partition = isomorphism classes.
FREE GROUND TRUTH: McKay's nauty lists (users.cecs.anu.edu.au/~bdm/data/graphs.html) are
already one representative per isomorphism class, so the orbit partition costs nothing.
Descriptors with known status: degree sequence (incomplete), adjacency spectrum
(incomplete -- smallest cospectral non-isomorphic pair at 5 vertices), 1-WL colour
histogram (incomplete on regular graphs), full WL-2.
To run the audit: evaluate D on all 1044 reps, bucket by value, compare bucket system to
the singleton partition of reps, count merged pairs. ~545k pairwise comparisons. Seconds.
CAVEAT: this is literally the Balcilar/Joshi experiment. Reproduces, does not extend.

### Instance 2 -- Steane [[7,1,3]] syndrome map (closest to the quantum instance)
Object space: Pauli errors mod phase, 4^7 = 16,384.
Group: stabilizer S, |S| = 2^6 = 64 (optionally also the code automorphism group
PGL(3,2), order 168, permuting the 7 qubits).
Descriptor: the 6-bit syndrome -> 2^6 = 64 classes.

Known closed-form answer, with the arithmetic made explicit so it is checkable:
  - syndrome map is a homomorphism onto F_2^6, so it has 64 fibres,
    each of size 16,384 / 64 = 256.
  - its kernel is the normalizer N(S) (= centralizer, for stabilizer groups),
    so |N(S)| = 256, and the trivial-syndrome fibre IS N(S). Consistent.
  - |N(S)| = |S| * |N(S)/S| = 64 * 4 = 256, with N(S)/S =~ P_1 the 4 logical
    classes {I, Xbar, Ybar, Zbar}.
  => Relative to the stabilizer action (errors equivalent mod S), each syndrome
     fibre contains exactly 256/64 = 4 classes. Loss factor = 4, exactly the
     logical group. That is regime (ii), globally.
  - Restricted to the correctable set (d = 3 => weight <= 1), there are
    1 + 3*7 = 22 errors including the identity, and these land in distinct
    syndrome cosets. That is regime (i), on that subset.

Cost: 16,384 x 64 = ~1M ops for the S-action; adding the 168 automorphisms ~176M, still
trivial, or use orbit-stabilizer.
VALUE: the answer is known in closed form, so this VALIDATES an audit tool rather than
discovering anything -- which is the right use. CAVEAT: QEC degeneracy is exactly this
statement and has been textbook since Shor 1995 / Gottesman 1997. Pre-solved.

## Bottom line
The idea is "maximal invariant statistic" plus "count the collisions", both standard.
Publish nothing on the concept. If the ORION-QG facts are useful, they are useful as
internal pipeline facts (and Check B may deflate even those), not as a research claim.
