# P9 causal intervention diagnostic protocol V1

**Programme:** #977  
**Purpose:** test whether failures can be diagnosed prospectively by one-coordinate intervention response rather than final confidence/accuracy alone.

## Core rule

For each task, freeze a base system and three intervention classes:

- `INFORMATION`: add genuinely missing semantic task information;
- `ACCESSIBILITY`: preserve semantic information but repair the representation/interface presented to the frozen downstream access class;
- `COMPUTATION`: preserve information and representation but add a registered downstream computation/inference procedure.

On a development/probe split, run all three interventions under a deterministic resource ledger. The diagnostic predicts the **lowest-cost intervention reaching the frozen quality target**; if none reaches target, predict `CANNOT_CHECK`.

On a disjoint protected split, run all interventions again. The protected causal gold is recomputed independently using the same target/cost rule. Diagnosis is correct only if the development prediction equals the protected causal gold.

This avoids assigning gold diagnosis labels from task names or post-hoc narrative.

## Generic comparator

`UNCERTAINTY_ESCALATE_COMPUTE` represents a common generic failure heuristic: when base quality is below target, spend downstream compute/model capacity. It always predicts `COMPUTATION`; when base quality already meets target it predicts `NO_INTERVENTION`.

P9 must beat this heuristic on diagnosis accuracy and false compute-escalation rate.

## Domain A — non-synthetic handwritten digits

Use `sklearn.datasets.load_digits()` with scikit-learn `1.7.1` and a deterministic train/probe/protected split stratified by the ten digit labels.

Two frozen tasks:

### D-A — accessibility intervention

- responsibility: ten-class digit identity;
- base representation: coordinate-wise cubic bijection of standardized 64-pixel state;
- frozen access class: multinomial logistic regression;
- INFORMATION: no extra semantic information is added (identity/no-op; cost 8 units);
- ACCESSIBILITY: exact cube-root inverse repair before the same logistic access class; cost 2 units;
- COMPUTATION: RBF SVC on the cubic representation; cost 12 units.

Quality target: protected/probe accuracy `>= 0.965`.

### D-I — information intervention

- responsibility: ten-class digit identity;
- base representation: one scalar total pixel intensity, standardized from training data;
- INFORMATION: restore the full native standardized 64-pixel state to the same logistic access class; cost 8 units;
- ACCESSIBILITY: deterministic monotone rescaling of the one-scalar representation only; cost 2 units;
- COMPUTATION: RBF SVC on the one-scalar representation; cost 12 units.

Quality target: accuracy `>= 0.95`.

These costs are abstract registered intervention units used only to choose among interventions that meet quality; raw model/state resource measurements are also reported separately.

## Domain B — exact executable affine-state tasks

Generate disjoint development and protected instances from frozen integer seeds. Exact verifier accuracy is the endpoint.

### B-I — missing information

Task target is parity of four hidden bits. Base exposes only the first three bits.

- INFORMATION: add the fourth bit; registered exact parity computation then applies; cost 4;
- ACCESSIBILITY: bijectively remap the first three visible bits only; cost 2;
- COMPUTATION: exhaustive deterministic computation over the visible three bits only; cost 8.

Quality target: exact accuracy `1.0` across the protected truth-table family. Missing fourth-bit collisions make computation/accessibility unable to close the information ceiling.

### B-A — accessibility

Base exposes a bijective two-bit encoding `(a, a XOR b)` while responsibility is recover `b` through a frozen **linear/affine Boolean readout**.

- INFORMATION: no extra information/no-op; cost 4;
- ACCESSIBILITY: exact inverse transform `(a,z)->(a,a XOR z)` then affine projection to `b`; cost 2;
- COMPUTATION: a registered nonlinear XOR computation over the encoded coordinates; cost 8.

Both access repair and computation can close quality; the frozen cost rule should prefer accessibility.

### B-C — computation

Base exposes a length-3 chain of affine maps `(s_i,o_i)` and input `x`; responsibility is the final transported value. The representation already exposes every local map and no information is missing.

- INFORMATION: no-op; cost 4;
- ACCESSIBILITY: serialize/reorder the same local maps without composing them; frozen simple readout remains unable to produce the final value; cost 2;
- COMPUTATION: exact affine composition followed by evaluation; cost 8.

Quality target: exact accuracy `1.0`. Only the computation intervention is registered to close the task.

## Split chronology

Digits:

- train: model/compiler fitting;
- probe: diagnostic intervention selection;
- protected: final diagnostic scoring.

Use `train_test_split(..., random_state=20260901, stratify=y)` for 60% train / 40% remainder, then split remainder 50/50 with `random_state=20260902` into probe/protected.

Executable domain:

- development seed range: `9100..9199`;
- protected seed range: `9900..9999`.

## Resource ledger

Report for every intervention:

- semantic information dimension/count;
- representation dimension;
- deterministic transformation touches;
- fitted parameter or support-vector coordinate count where applicable;
- explicit computation operation count;
- registered intervention cost used for selection;
- quality on probe/protected.

No intervention is considered “matched” merely because its registered cost is lower; cost is used only after it reaches the frozen quality target.

## Primary endpoints

- diagnostic accuracy across the five task families;
- per-domain diagnostic accuracy;
- false compute-escalation rate;
- protected quality after applying predicted intervention;
- regret in registered intervention cost relative to protected causal gold;
- causal-gold stability from probe to protected;
- resource vectors for all interventions;
- deterministic replay.

## Positive terminal

`P9_CAUSAL_DIAGNOSTIC_V1_SUPPORTED` requires:

- diagnostic accuracy at least `4/5` task families;
- accuracy strictly above `UNCERTAINTY_ESCALATE_COMPUTE`;
- diagnostic accuracy `1.0` on the three exact executable families;
- at least one digits task correctly diagnosed;
- false compute escalation at least 50% lower than the generic heuristic;
- applying the predicted intervention reaches the frozen protected quality target whenever protected causal gold is not `CANNOT_CHECK`;
- mean registered-cost regret <= 1.0 unit;
- every protected intervention cell reported;
- deterministic replay.

A positive supports a bounded cross-domain causal diagnostic for deciding whether to add information, repair accessibility or add computation. It does not claim a universal LLM diagnostic, and it cannot erase the protected Qwen scaling negative.
