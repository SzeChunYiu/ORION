# ORION-03 current novelty subtraction — 2026-08-28

**Status:** publication-positioning audit only  
**scientific_authority_delta:** `NONE`

## Question

Does the current typed-authority manuscript retain a general formal novelty claim after subtracting truth maintenance, annotated/semiring Datalog provenance, minimal-support causality, and deletion robustness?

## Current nearest work checked

1. **Doyle, “A Truth Maintenance System,” Artificial Intelligence 12 (1979), 231–272.** Dependency-directed reason maintenance and revision of beliefs are donor-owned.
2. **Bourgaux, Bourhis, Peterfreund & Thomazo, “Revisiting Semiring Provenance for Datalog,” KR 2022.** Datalog annotations/provenance, including deletion behavior obtained by zeroing deleted-fact annotations, are donor-owned. DOI `10.24963/kr.2022/10`; arXiv `2202.10766`.
3. **Thapa & Staab, “Causality and Minimal Supports in Recursive Datalog,” arXiv:2607.16443 (2026).** Inclusion-minimal supports are organized as a hypergraph that determines actual causes, responsibility, and deletion robustness. This directly occupies much of the manuscript’s generic minimal-support/deletion territory.
4. **Thapa & Staab, “Causal Explanations for Stratified Datalog,” arXiv:2608.21141 (2026).** Shows that once negation is admitted, support-based monotonic reasoning no longer suffices; the present paper’s positive-conjunctive restriction is therefore a genuine scope boundary, not a missing implementation detail.

## Subtraction

The following remain **donor-owned and must not be sold as the paper’s novelty**:

- least-fixed-point evaluation of positive rules;
- derivation/proof-tree semantics as a generic reasoning device;
- annotation/provenance transfer in Datalog;
- minimal supports as the object underlying deletion robustness;
- dependency-directed revision/retraction in truth-maintenance systems.

`D2-C5` (unique minimal typed retraction) is mathematically correct in the registered finite powerset/cap model, but its generic minimality content is too close to established provenance/support/deletion machinery to carry a standalone broad-novelty claim. It should be presented as a **specialization/corollary inside the declared scientific license algebra**, not as a new general theory of minimal retraction.

## Residual contribution after subtraction

The defensible residual is narrower:

1. an explicit **scientific evidence-license vocabulary** whose labels distinguish theorem, finite exact, prospective, post-outcome, bounded-computation, and related authority classes;
2. **cap-preserving transfer** that makes nonpromotion machine-checkable — e.g. a post-outcome rule cannot manufacture prospective authority when its cap excludes it;
3. the typed retraction semantics instantiated on scientific records where preserving derivability while losing authority is operationally meaningful;
4. a reusable domain-agnostic evaluator implementing that specialization;
5. an external X.509 trust-store instantiation showing that the target obstruction is non-vacuous in third-party material.

This is a formal-methods/software artifact contribution built on donor mathematics, not a claim to have invented fixed points, provenance, minimal supports, or deletion robustness.

## Round-2 empirical boundary

The X.509 round-2 `M5` perfect precision/recall figures are **not empirical detector performance**. Because `M5` is definitionally the parent-authorized set and a hybrid is `v_union and not parent`, zero unsafe merges, zero needless rejections, and precision/recall 1.0 follow propositionally for any corpus.

The empirical content is instead:

- **46 hybrid tasks among 1,962** third-party OpenSSL trust-store merge tasks (~2.3%), establishing non-vacuity;
- method-dependent unsafe-merge / needless-rejection costs for the naive baselines;
- corpus checks `c3_violations = 0`, `c4_resurrections = 0`, and `c4_upstream_mirrors_ok = true`, which could have failed.

## Publication consequence

**Primary posture:** Journal of Automated Reasoning.  
**Fallback:** ACM Transactions on Computational Logic.

Do not pursue a security-venue or broad-AI superiority framing from these data. The X.509 material is an external instantiation, not a security threat-model result; the generic logical substrate is donor-owned.

### Stop rule

No further theory recursion is justified merely to make `D2-C5` sound more novel. The remaining work is manuscript integration, clean packaging, references/licence/archive, and external peer review.
