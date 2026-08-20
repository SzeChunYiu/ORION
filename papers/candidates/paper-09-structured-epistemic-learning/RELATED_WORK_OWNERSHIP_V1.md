# P9 related-work ownership map V1

Purpose: bind every broad design idea the manuscript discusses to a donor family so the final paper cannot drift into novelty-by-rewording.

## Typed / graph structure

- **Graphormer** — Ying et al., arXiv:2106.05234: structural graph encodings inside a Transformer; P9 cannot claim that adding graph structure to Transformer attention is new.
- **Heterogeneous Graph Transformer** — Hu et al., arXiv:2003.01332: node/edge-type dependent attention; P9 cannot claim typed relation-aware attention as new.
- **GraphGPS** — Rampasek et al., arXiv:2205.12454: modular local message passing + global attention + structural/positional encodings; strong graph-representation floor.
- **Battaglia et al. graph networks** — arXiv:1806.01261: broad relational inductive-bias philosophy and graph-network framework; P9 cannot claim that structured entities/relations/rules are generally new ingredients for combinatorial reasoning.

## Local representations / transport / consistency

- **Knowledge Sheaves** — Gebhart, Hansen, Schrater, arXiv:2110.03789: local vector spaces and relation maps, approximate global sections and consistency constraints for knowledge graphs. P9 D0 GLUE/OBSTRUCTION language is not novelty merely because it resembles local-to-global consistency.
- **Neural Sheaf Diffusion** — Bodnar et al., arXiv:2202.04579: learnable sheaf structure/restriction maps and nontrivial diffusion. P9 cannot claim learnable local transport itself.

## Algorithmic / explicit computation

- **CLRS Algorithmic Reasoning Benchmark** — Velickovic et al., arXiv:2205.15659: neural execution/generalization over classical algorithms and explicit OOD algorithmic evaluation.
- **TransNAR** — Bounsi et al., arXiv:2406.09308: language Transformer combined with a graph neural algorithmic reasoner, with gains over Transformer-only baselines on CLRS-Text in and out of distribution. P9 cannot claim language-interface + structured reasoner as new.

## Reusable abstractions / mechanics

- **DreamCoder** — Ellis et al., arXiv:2006.08381: reusable symbolic abstractions/libraries learned with neural-guided program search.
- **LILO** — Grand et al., arXiv:2310.19791: iterative synthesis/compression/documentation of reusable program libraries, combining LLMs and Stitch-style abstraction learning.
- These donors own broad claims about learning reusable problem-solving abstractions. P9's bounded D0 mechanic tasks may only claim the exact information/failure-coordinate result they measure.

## Non-language latent reasoning

- **Coconut** — Hao et al., arXiv:2412.06769: recurrent continuous hidden-state reasoning without decoding every step to language. P9 A3 was closed not-load-bearing; no paper claim that reasoning outside language is new.

## Rule/entity binding

- **Neural Production Systems** — Goyal et al., arXiv:2103.01937: reusable rule templates dynamically bound to entities, sparse rule application, extrapolation in visual dynamics. P9 A9 deferred.
- Later Transformer variable-binding work further prevents any claim that an explicit dedicated binding module is required in general.

## Mechanism-centric scientific representations

- **Mechanistic World Models** — Posner, Lei, Schölkopf, arXiv:2607.12474: prediction is weaker than explanatory mechanism recovery; reusable mechanisms should organize scientific representation/computation/learning. P9 cannot claim `mechanism-centric scientific AI` broadly.
- P9 A10 causal/interventional work is deferred and cannot appear as experimental evidence.

## Compositional-generalization and serialization pressure

- **Lippl & Stachenfeld, ICLR 2025** — *When does compositional structure yield compositional generalization? A kernel theory.*: a structured representation alone is not sufficient; training-data statistics can induce memorization leak and shortcut bias. This directly limits any P9 inference from `typed structure exists` to `generalization follows`.
- **Uselis, Dittadi, Oh, ICLR 2026 submission** — *Necessary Conditions for Compositional Generalization in Visual Models*: representation factorization/geometry conditions for compositional generalization. Useful theoretical pressure, not P9 novelty.
- **PARSE**, arXiv:2605.06043: explicit relational composition for visual domain generalization. P9 cannot claim relational structure improves domain generalization broadly.
- **Graph-KV**, arXiv:2506.07334: structural attention masks can outperform flat sequence encoding on graph-structured text/RAG. P9 D1 therefore requires a same-information serialization control rather than merely `structure > flat sequence` rhetoric.
- **Lo et al., 2026 — *When 2D Tasks Meet 1D Serialization: On Serialization Friction in Structured Tasks*, arXiv:2604.27272**: explicitly studies a representational mismatch where the same underlying task entries remain present but load-bearing native relations become implicit under 1D serialization. This directly owns the general principle that preserving content does not imply preserving an equally usable representation. P9 may therefore not claim discovery of `same information, worse serialization`; its D1 residual is only the exact method-coordinate/whole-domain discriminator and its protected controls.

## Residual P9 candidate claim after subtraction

The only standalone residual currently allowed is the **combination**:

1. exact paired information-sufficiency/non-identifiability diagnostics over versioned epistemic/mechanic coordinates;
2. architecture-neutral simple-learning and explicit-inference first-right-of-refusal, so representation failure is separated from learning/computation failure;
3. exact whole-domain procedural method-coordinate transfer with reminted vocabulary, explicit unresolved states, protected multi-coordinate corruptions, and a same-information serialization control;
4. a recorded decision that model complexity is escalated only when the protected residual requires it.

Even this combination must survive final official results, independent replay, and a fresh post-result search. If it does not, the package becomes a technical benchmark note or no-standalone residual.
