# Polished Titles and Abstracts R3

Date: 2026-08-25

Purpose: final title/abstract candidates produced after theorem verification and application calibration. These surfaces advertise only proved mathematics and keep unresolved production or exact-threshold claims out of the title.

## Paper A

### Proposed title

**Compositional and Robust Zero-Sum Normal Forms for Finite-Signature Optimization**

### Abstract

Many exact optimization problems attach a finite-group signature to each active coordinate and admit local edits that delete a zero-signature subconfiguration. The largest support that can survive such edits is then controlled not by the ambient group alone, but by the zero-sum-free invariant of the realized signature alphabet. We develop a compositional theory of this invariant and its induced normal forms. For alphabets separated across direct-sum axes, the invariant is exactly additive. Homomorphic images give certified lower obstructions, while a finite multiplicity formulation makes the alphabet constant an exact precomputable object. We also treat objectives outside the exact monotonicity cone: if each semantics-preserving deletion incurs a bounded event or per-coordinate defect, support still descends to the exact zero-sum-free budget with an explicit additive loss. Specializing the framework to the declared multi-Tag Pauli grammar recovers the binary-rank support cap and gives a quantitative degradation bound when Restore cost slightly exceeds the refund condition. The results support modular exact search, quotient-based diagnostics, and certified approximate normalization. They concern the frozen structural objective and do not by themselves imply circuit-depth, T-count, fidelity, or hardware improvements.

### One-sentence significance

A brittle one-instance deletion theorem becomes a compositional, exactly computable, and quantitatively robust normal-form theory.

### Keywords

zero-sum sequences; sparse normal forms; finite abelian groups; exact optimization; quantum compilation; certified approximation

## Paper B

### Proposed title

**Realization and Amplification of Support Certificates in Exact Optimization**

### Abstract

Support bounds used by exact optimizers can belong to different mathematical owners. An abstract shortening language may have a sharp terminal budget even when the corresponding production compiler has a smaller intrinsic optimum or additional transformations that destroy the abstract lower witness. We formalize this distinction. Terminal complexity is exactly additive for heterogeneous independent shortening systems, while intrinsic support is additive for independent compiler products only when component normalizations and optimum lower witnesses both exist. Our main result is a production-realization criterion: an abstract terminal budget transfers to a named production proof system precisely after establishing a sound representation, an all-instance normalization, a realizing production state, and nonreducibility under every rule in that system. We also prove monotonicity under proof-language strengthening and quantify the effect of a verified budget reduction on direct labeled-support enumeration: for fixed budget `B`, the state volume is `Theta(n^B)`, so lowering the certified budget from `B` to `K` removes a factor `Theta(n^(B-K))` in that architecture. The framework enables proof-carrying optimization and modular certificate composition while preventing abstract terminal examples from being reported as intrinsic compiler lower bounds without realization evidence.

### One-sentence significance

The paper supplies a checkable boundary between an elegant abstract support number and a production certificate that an exact solver may safely use and report.

### Keywords

certificate complexity; exact optimization; proof systems; support enumeration; realization; branch and bound

## Paper C

### Proposed title

**Exact Information Radii for Low-Order Representations in Combinatorial Compilation**

### Abstract

Compressed representations are routinely used to predict the value or structure of exact combinatorial optima, but their information loss is rarely quantified independently of the prediction algorithm. For a finite instance representation, we prove that the exact worst-case absolute error available from the representation alone is one half of the largest target diameter inside a representation fiber. The same fiber geometry yields the exact integer-output radius, shows that randomization cannot improve worst expected absolute loss, gives squared minimax risk equal to one quarter of the squared diameter, and determines the minimum width of an exactly valid uncertainty interval. Opposite optimizer properties inside one fiber further force randomized structural-classification error at least one half. We instantiate these general laws in a frozen Pauli partition model. Two scalable families have identical term counts, ordered weights, and complete labeled pair-gain matrices but different exact improvements and incompatible optimal block structure; a second parity construction remains indistinguishable through all prescribed proper interaction orders while its value gap grows without bound. By contrast, a four-index pair condition exactly decides unary optimality. Thus representation sufficiency is query-dependent: low-order information can determine one global decision while remaining provably inadequate for value and optimizer structure. The results provide exact controls for learned optimizers, adversarial benchmarks, and certified uncertainty.

### One-sentence significance

The manuscript turns indistinguishable compiler instances into exact, architecture-independent limits on prediction, uncertainty, and structural inference.

### Keywords

information-based complexity; minimax error; combinatorial optimization; low-order features; learned optimizers; uncertainty quantification

## Paper D

### Proposed title

**Authority Propagation Is Tractable, Minimum Refutation Is Hard**

### Abstract

Evidence, policy, and tool-derived claims often carry several forms of authority that propagate through conjunctive rules and must retract when supporting claims are directly refuted. We model this process by a positive, capped rule system with least-fixed-point semantics. Projecting onto a single license converts the set-valued semantics exactly into an ordinary Horn closure, yielding linear-time evaluation in the explicit rule-incidence size per license. We then characterize intervention. A target loses a license exactly when the direct-refutation set intersects every inclusion-minimal finite proof footprint for that target. Consequently, seed-only interventions are hitting sets of minimal seed supports. Selecting a smallest such intervention is NP-complete even in an acyclic graph with only seed-to-intermediate-to-target depth, although any proposed intervention remains linearly verifiable. Weighted refutation gives the corresponding weighted problem. The least-fixed-point choice is essential: unsupported positive cycles do not manufacture authority, whereas greatest-fixed-point semantics would admit spurious circular support. The framework separates inexpensive impact recomputation from difficult optimal intervention and suggests certified workflows for evidence retraction, regulatory provenance, multi-agent tool chains, and incident response. It tracks authority under declared rules rather than truth or legal compliance.

### One-sentence significance

A formally transparent provenance model exhibits a sharp computational boundary between evaluating current authority and choosing the cheapest evidence withdrawal that removes it.

### Keywords

least fixed point; Horn logic; provenance; retraction; hitting set; NP-completeness; trustworthy AI

## Non-quantum paper

### Proposed title

**A Property-C Boundary Theorem for Length-31 Zero-Sum Sequences in `C_5^3`**

### Abstract

Let `S` be a saturated, 5-short-free, total-zero sequence of length 31 in `C_5^3`, and let `H` be the subsequence formed by support points of multiplicity at least two. Previous reductions force all multiplicities into `{1,2,4}` and show that `H` spans the ambient group whenever `s+c_4<=24`, where `s` is support size and `c_4` counts fourfold support points. We resolve the first remaining boundary. On the diagonal `s+c_4=25`, the repeated subsequence has length 12. If it had rank at most two, rank one would contradict the cyclic Davenport bound, while the rank-two Property-C classification would force `H=T^4` for three distinct support points. The multiplicity equations then give the unique low-rank profile `(s,c_1,c_2,c_4)=(22,19,0,3)`. Hence every residual sequence with `s>=23` and `s+c_4<=25` has a full-rank repeated stratum. This closes the branches `(s,c_4)=(23,2),(24,1),(25,0)` and places every support-23 candidate in a repeated-basis normal form. The theorem advances the structural reduction for the four-wise Davenport problem and narrows exact orbit and atom-overlap analyses. It does not establish `C_0(31)` or the exact value of `D_4(C_5^3)`.

### One-sentence significance

A rank-two inverse theorem removes the first analytically silent multiplicity diagonal and forces every support-23 obstruction into a repeated full-rank basis regime.

### Keywords

zero-sum sequences; Property C; generalized Davenport constants; finite abelian groups; block monoids; inverse additive theory

## Editorial note on title selection

The titles intentionally avoid three unsupported implications:

1. Paper A does not claim production compiler advantage.
2. Paper B does not advertise the unresolved factor-five production separation.
3. The non-quantum paper does not announce an exact generalized-Davenport value.

Paper C and Paper D use broader application language only where the general theorem itself justifies it.