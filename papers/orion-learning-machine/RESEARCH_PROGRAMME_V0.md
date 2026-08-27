# ORION Learning Machine Research Programme V0

**Status:** research programme / no publication claim authorized
**Date:** 2026-08-18
**Lane:** isolated sandbox research lane; does not modify the user's active ORION working tree

## Central hypothesis

ORION can treat existing human and machine solvers as sources of transferable problem-solving mechanics rather than competitors. It should reconstruct what each mechanic does, estimate its competence boundary from successes and failures, absorb it into a provenance-preserving common representation, compose mechanics across sources for unseen problems, and eventually propose new mechanics when the absorbed library cannot explain persistent residual failures.

## Five core papers

### LM-1 — Capability Absorption
**Working title:** *Learning From Solvers: Mechanic Reconstruction and Competence Boundaries for Problem Solving*

Primary hypothesis: a system can reconstruct transferable solver mechanics and predict their applicability/failure regions better than black-box solver identity or aggregate benchmark score.

Minimum evidence: heterogeneous solver corpus; success/failure traces; mechanic representation; held-out and shifted competence prediction; source-identity and provenance recovery; ablations; negative transfer tests.

### LM-2 — Structural Learning
**Working title:** *Learning the Structure of Mathematical Problem Solving from Verified and Failed Proof Trajectories*

Primary hypothesis: successful and unsuccessful proof trajectories admit reusable structural abstractions that transfer across theorem families better than tactic/token imitation alone.

Minimum evidence: proof-structure extraction; successful + failed trajectories; structure prediction/retrieval; transfer split by theorem family/source; proof-search baseline; ablations of failure history and structural coordinates.

### LM-3 — The Learning Machine
**Working title:** *The Learning Machine: Synthesizing Problem-Solving Structures from Absorbed Mechanics*

Primary hypothesis: learned composition of mechanics can outperform the best fixed mechanic/solver and black-box portfolio selection on fresh problems while remaining inspectable and provenance-bound.

Minimum evidence: typed solver-structure language; learned composer; execution engine; fixed-solver, portfolio-selector, search and program-synthesis baselines; fresh transfer; compute-normalized evaluation.

### LM-4 — Mechanic Invention
**Working title:** *From Residual Failure to New Method: Verified Invention of Problem-Solving Mechanics*

Primary hypothesis: persistent residual failures can trigger proposal of new reusable mechanics or abstractions that survive replay, fresh transfer, and protected verification.

Minimum evidence: frozen residual classes; invention gate; candidate mechanic generation; replay + fresh transfer; harmful/null variant retention; independent verification; proof that gains cannot be explained by extra compute/search alone.

### LM-5 — ORION-Math
**Working title:** *ORION-Math: Autonomous Frontier Mathematics by Absorption, Composition, Invention and Verification*

Primary hypothesis: the integrated system can make verified progress on frozen research-level mathematics by using the absorbed mechanic library and competence model, not merely a larger direct-generation budget.

Minimum evidence: contamination-controlled/open conjecture set; formal or independently checked outputs; provenance of absorbed methods; fixed-budget baselines; ablations of absorption, competence boundaries, composition and failure learning; expert review for mathematical significance.

## Conditional sixth paper

### LM-R — Solver Ecology / Dataset Paper
Only split this out if the corpus itself becomes a durable community resource.

Possible title: *A Mechanistic Competence Atlas of Mathematical Solvers*.

This is not justified merely by having logs. It needs broad solver coverage, reproducible traces, standardized problem features/mechanic annotations, competence-boundary labels, licenses, benchmark splits and demonstrated downstream value.

## Dependency order

LM-1 -> LM-2 -> LM-3 -> LM-4 -> LM-5

LM-1 and LM-2 may proceed partially in parallel. LM-5 cannot make an ORION-level frontier-math claim until LM-3/4 mechanics exist and pass protected fresh-transfer tests.

## Phase-0 falsifier already executed

A synthetic heterogeneous polynomial-root environment was built with complementary solver mechanics: rational-root enumeration, bisection, Newton iteration, companion-matrix roots and a high-cost symbolic fallback.

### V1
On IID holdout data the learned competence models were strong. Under distribution shift, the rational-root specialist's competence ROC-AUC collapsed to about 0.54 while the failure-aware schedule remained robust.

Diagnosis: coarse global problem features were insufficient to estimate a specialist mechanic's preconditions; the model had learned an unstable correlation with the training generator.

### Reopen and V2
Added cheap mechanic-specific diagnostic landmarkers (small-integer probe evidence) to the competence representation and reran the same hostile shift.

Result: rational-root competence ROC-AUC rose to about 0.98 under shift. The composite schedule retained the strongest solver's 95.7% solve ceiling with modeled effort around 22, versus about 58 for the strongest fixed general numeric solver and 129 for the symbolic verifier/fallback.

### Interpretation
This is implementation sanity evidence only. It does **not** validate the scientific claims of LM-1 or any paper. It does validate a concrete failure-learning loop and exposes a research requirement: competence boundaries may require mechanic-specific probes, not only static task metadata.

## Immediate next falsifiers

1. Replace synthetic competence boundaries with real open-source solvers on a public mathematical/algorithmic corpus.
2. Separate selection from composition: require multi-stage solutions where no individual solver can finish the task alone.
3. Hide solver identity and train on source-disjoint splits to test whether ORION learns mechanism rather than brand/source signatures.
4. Introduce adversarial distribution shifts designed to break cheap probe features.
5. Measure negative transfer: absorbed mechanics must sometimes be rejected.
6. Add provenance/recoverability: every selected mechanic must retain origin, evidence and transformation lineage.
7. Move to Lean once an isolated Lean toolchain is available; until then all formal-proof claims remain `CANNOT_CHECK`.

## Claim discipline

- A successful synthetic experiment is not evidence of frontier mathematical discovery.
- A generated proof is not accepted without formal or appropriate independent verification.
- Existing mechanisms are attributed and absorbed, not relabeled as ORION novelty.
- If a hypothesis fails, preserve the failure, identify the missing coordinate or competing explanation, freeze the repair hypothesis, and rerun fresh/hostile tests.
