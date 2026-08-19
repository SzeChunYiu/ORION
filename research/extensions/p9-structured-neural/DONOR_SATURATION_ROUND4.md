# P9 donor saturation — round 4 relational/epistemic pressure

Status: **MATERIAL CHANGE**.  This round used different search language from graph/sheaf/mechanism saturation: relational abstraction, systematic reasoning, epistemic-state GNNs, equality/identity generalisation, and relational bottlenecks.

This round resets the no-material-change saturation count to zero.

## Systematic Reasoning About Relational Domains With Graph Neural Networks

**Primary source:** Khalid & Schockaert, 2024, arXiv:2407.17396.

### Scientific essence

The paper revisits systematic relational reasoning with GNNs and argues that systematic generalisation can be achieved with the correct inductive bias.  Its central design move is explicitly to treat **node embeddings as epistemic states** and parameterise the GNN accordingly.  It also introduces a benchmark requiring aggregation of evidence from multiple relational paths and reports strong performance where considered neuro-symbolic alternatives fail.

### P9 consequence

This is a direct claim contraction. P9 may **not** claim any of the following as novel:

- that GNN hidden states can be interpreted/designed as epistemic states;
- that a GNN can systematically generalise in a relational reasoning domain when given an appropriate epistemic-state inductive bias;
- that multi-path evidence aggregation is uniquely ORION-specific.

### Disposition

`ADOPT + MANDATORY BASELINE` for any final relational/GNN experiment.

P9's residual must therefore use **more specific externally meaningful state structure** than generic epistemic node embeddings: typed evidence/support/defeat, explicit non-identifiability, mechanic candidates/contracts, local representation transport, negative-history scope, or another frozen coordinate that changes a protected outcome.

If a Khalid-Schockaert-style epistemic-state GNN solves the final relational task under matched information/resources, P9 strikes the architecture residual.

## Relational Inductive Bias / Relational Bottleneck

**Primary source:** Campbell & Cohen, 2024, arXiv:2402.18426.

### Scientific essence

A relational bottleneck focuses learning on relations among inputs rather than object-specific feature content. The reported experiments connect this bias to factorised/abstract representations, learning efficiency and compositional flexibility.

### P9 consequence

P9 cannot claim `remove surface/object content and focus on relations to improve abstraction/generalisation` as a novel principle.

### Disposition

`ADOPT relational-bottleneck pressure + BASELINE/ABLATION`.

The exact D1 `TYPED_RELATIONAL` comparator must be interpreted as an explicit relational inductive bias, not evidence of a new neural architecture. A final P9 contribution would require additional epistemic coordinates or a stronger task where ordinary relation equality/bottleneck features are insufficient.

## Equality / identity generalisation in non-symbolic networks

**Primary source:** Geiger, Carstensen, Frank & Potts, 2020, arXiv:2006.07968.

### Scientific essence

Non-symbolic neural networks can learn and generalise equality/identity relations, including hierarchical equality settings, when representations/training supply the needed structure.

### P9 consequence

P9 cannot argue that explicit candidate/context identity equality is inherently beyond ordinary neural learning. Candidate-id equality in M1 is a generic relation feature/diagnostic, not a novelty claim.

### Disposition

`CLAIM CONTRACTION`; no dedicated final baseline unless equality becomes load-bearing in the surviving benchmark.

## Round-4 impact on current P9 hypothesis

Before this round, a plausible residual was `learned reasoning over typed epistemic state`.

After this round that wording is still too broad. A defensible residual must instead look like:

> **evidence-bound reasoning over a versioned typed epistemic/mechanic representation where specific coordinates have prospectively demonstrated information or transfer value beyond generic relational/epistemic-state inductive biases.**

The D0 and D1 programmes are therefore diagnostic in exactly the right way:

- D0 asks which coordinates are information-identifying;
- M1 asks whether generic simple relational learners already exploit them;
- D1 asks whether an explicit coordinate-comparison bias transfers across a held-out procedural domain versus transcript/untyped/same-information serialization.

A strong D1 `TYPED_RELATIONAL` result alone would **not** establish neural novelty; it would support a bounded representation/inductive-bias result and would route future work to a harder residual.

## Saturation counter

- Round 3: material — binding + mechanistic/causal donors.
- Round 4: **material** — epistemic-state GNN + relational-bottleneck claim contraction.
- Consecutive no-material-change rounds after latest material change: **0/2**.

P9 donor saturation remains OPEN.
