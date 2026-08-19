# ORION recursive discovery atoms — donor structural matrix V1

**Date:** 2026-08-19  
**Status:** first-wave primary-source structural research. Not literature saturation and not a novelty certificate.  
**Purpose:** decide what ORION should adopt, what should remain a strong baseline, and which candidate atoms should **not** be implemented yet.

## Reading rule

For every candidate atom, distinguish:

- **DONOR-OWNED STRUCTURE** — directly absorb/credit; remove ORION novelty language.
- **MANDATORY BASELINE** — must be present in any later bounded atom study if task mapping is faithful.
- **POSSIBLE RESIDUAL** — exact discriminator still untested.
- **IMPLEMENTATION DISPOSITION** — what may safely enter the framework now.

Historical success stories are morphology evidence only. They are never protected benchmark gold.

---

## A1 — epistemic tension / opportunity detection (#510)

### Close parents

- **AutoDiscovery: Open-ended Scientific Discovery via Bayesian Surprise** (Agarwal et al., arXiv:2507.00310). Open-ended scientific exploration is driven by Bayesian surprise and MCTS rather than a human-fixed question.
- **FirstResearch: Auditable Question Formation for LLM Scientific Discovery Agents** (Wang, arXiv:2607.05682). Its Research Question Certificate binds primitives, assumptions, mechanism, a tension/contradiction, falsifiable hypothesis, minimal decisive test, and failure-update rule.
- Existing model criticism / posterior predictive checking / uncertainty / MDL / anomaly detection families already own ordinary misfit, surprise, and inconsistency signals.
- Existing ORION #452/#459/#477 own responsibility, interface failure, and decision-relevant inquiry once a problem is already live.

### Adopt

- tension should be represented as a **structured hypothesis with witnesses, defeaters, discriminators, and downstream contracts**, not a scalar creativity/interestingness score;
- question formation and opportunity detection must expose a falsifier or decisive test when possible;
- surprise/uncertainty/MDL are mandatory simple parents.

### Residual to test

Can a structured detector find **zero-error material opportunities**—unification deficits, symmetry/invariance opportunities, counterfactual inconsistencies, cross-domain correspondence, or bounded derivational inefficiency—beyond surprise/uncertainty/MDL without flagging almost everything?

### Disposition

`IMPLEMENT_GENERIC_RECORD_ONLY` in PR #513. No learned/runtime tension detector is authorized before #510 freezes a benchmark.

---

## A2 — thought-experiment / counterfactual-experience synthesis (#511)

### Close parents

- **Active Inference AI Systems for Scientific Discovery** (Duraisamy, arXiv:2506.21329). Explicitly separates exploratory reasoning in imaginary/counterfactual spaces from later deterministic validation and allows temporary departure from incumbent physical constraints.
- **Model Discovery Agent** (Murphy, arXiv:2608.09696) and Bayesian experimental design parents already own active discriminating experiment selection inside declared scientific model structures.
- Counterexample-guided synthesis/learning already owns adversarial distinguishing examples within formal/program spaces.
- Zahavy, *LLMs Can't Jump*, motivates interactive controllable experience/world-model generation but does not by itself supply the complete experience-to-axiom mechanism.

### Adopt

- separate **experience synthesis** from theory generation;
- explicitly record which assumptions are relaxed and which remain fixed;
- register competing-hypothesis predictions before observing the outcome;
- simulation/physical/formal execution modes must remain distinguishable;
- novelty of a hypothetical world is not a discriminator by itself.

### Residual to test

Does frame/assumption manipulation produce useful discriminators in cases ordinary experiment design cannot identify under the same bound?

### Disposition

`IMPLEMENT_PROSPECTIVE_RECORD_ONLY` in PR #513. The current code scores only whether registered outcome sets are prospectively discriminating; it does not generate or validate thought experiments.

---

## A3 — concept / primitive invention (#512)

### Close parents

- **How are Scientific Concepts Birthed? Typing Rules of Concept Formation in Theoretical Physics Reasoning** (Aguilar & Aguirre, arXiv:2509.10740). Formalizes concept formation using cognitive typing rules such as distinction, property preservation, and concept change; composes them with algebraic/functional operations and reconstructs a historical path with typed program synthesis.
- **Abduction Without a Body?** (Farmer, arXiv:2608.02505). Representation-grounded Abduction Loop with motif extraction, canonicalization, cross-domain retrieval, identity-hypothesis generation, adversarial verification, and abstention.
- **Unlocking LLM Creativity in Science through Analogical Reasoning** (Shen, Druckmann & Zou, arXiv:2605.11258). Cross-domain relational analogy explicitly expands scientific solution generation and is empirically tested on biomedical tasks.
- Causal representation learning, abstraction learning, program synthesis, and latent-variable discovery are major parent fields.

### Adopt

- typed concept-transformation rules and type/semantic judgments are donor-owned structure;
- concept proposals must carry **structural semantics and correspondence**, not only prose or latent embeddings;
- analogy/correspondence is a mandatory parent pathway;
- concept formation and concept validation must remain separate.

### Residual to test

Can a system select/generate a transformation trace that makes a protected contract reachable under a frozen bound, preserves old-domain correspondence, predicts a hidden novel consequence, and outperforms M-open/abstraction/analogy parents on contamination-safe invented worlds?

### Disposition

`IMPLEMENT_PROPOSAL_RECORD_ONLY` in PR #513. `ConceptCandidate.v1` remains `PROPOSAL_ONLY`; no concept generator is integrated.

---

## A4 — analogy / correspondence generation (candidate child; not yet opened)

### Close parents

- Shen et al. 2605.11258 — explicit cross-domain relational analogy for scientific solution generation.
- Farmer 2608.02505 — cross-domain representational canonicalization/retrieval/identity abduction.
- **Beyond Input-Output: Rethinking Creativity through Design-by-Analogy in Human-AI Collaboration** (Li et al., arXiv:2602.09423) surveys design-by-analogy across the full creative process and multiple representation forms.
- P3 already owns source-local mapping/obstruction/plural-view validation, not generative analogy discovery.

### Adopt

Analogy is not an ORION novelty object. Any child must distinguish **generating a structurally useful correspondence** from retrieving a semantically nearby example or merely validating a supplied mapping.

### Possible residual

Evidence-bound generation of distant correspondences that unlock protected contracts while rejecting attractive false analogies, with P3-style obstruction/round-trip validation.

### Disposition

`DEFER_NEW_ATOM`. Route full donors through #454/#318 first.

---

## A5 — affordance / function / tool invention (candidate child; not yet opened)

### Close parents

- **Understanding Tool Discovery and Tool Innovation Using Active Inference** (Collis, Kinghorn & Buckley, arXiv:2311.03893). Explicitly distinguishes tool discovery from tool innovation and models affordances as hidden-state factors; a toy agent can invent a needed tool property by offline induction.
- Robotics affordance-relation literature already formalizes object-action-effect possibilities and generalization to unseen situations.
- Engineering/design theory and design-by-analogy are direct parents.

### Adopt

- `truth` and `function/affordance` cannot be collapsed into one validation coordinate;
- a tool can be scientifically familiar yet **functionally novel for the current agent/task**;
- discovery of an existing affordance and invention of a new artifact/property must be separated.

### Possible residual

A cross-domain epistemic affordance object with provenance, construction/prototype evidence, negative controls, and transfer beyond a toy active-inference tool setting.

### Disposition

`DEFER_NEW_ATOM`; do not implement generic `AFFORDANCE_JUMP` before strong parent absorption.

---

## A6 — question / conjecture / problem-taste generation (candidate child; not yet opened)

### Close parents

- AutoDiscovery 2507.00310 — autonomous question/hypothesis exploration using Bayesian surprise.
- FirstResearch 2607.05682 — structured auditable research-question certificate.
- **Mathematical conjecture generation using machine intelligence** (Mishra et al., arXiv:2306.07277) formalizes a conjecture space and generates inequalities using geometric structure/invariances.
- **LLM Framework for Discovering Major Mathematical Conjectures** (arXiv:2607.28632) proposes region search, reflective validation, and Lean checks for conjecture candidates; its stronger “problem taste” claims require independent pressure.
- Scientific hypothesis-generation literature is a mature parent field.

### Adopt

- question generation needs a structured relation to mechanism/tension/falsifier/test, not merely novelty ranking;
- scientific-question generation and **objective repair** (#288) are different operations;
- conjecture/question validity/significance cannot be self-scored by the proposer.

### Possible residual

Question generation that materially expands bounded downstream scientific reach and remains useful under human/protected validation, beyond surprise and structured-question certificates.

### Disposition

`DEFER_NEW_ATOM` pending #454 receipts and a discriminator.

---

## A7 — serendipity capture (candidate child; not yet opened)

### Close parent evidence

- **Serendipity in Science** (Nahm, Murciano-Goroff, Park & Funk, arXiv:2308.07519) exploits an exogenous library-shelving policy change and reports that unsought information exposure can affect later innovative publication, with openness moderating the effect.
- Recommender/information-discovery literature separately studies serendipity and unexpected usefulness.

### Adopt

Serendipity should be split into at least:

1. **unsought exposure**;
2. **recognition that the exposure is useful for a different contract/opportunity**;
3. downstream analogy/question/concept generation.

Do not call random exploration `serendipity` simply because something later works.

### Possible residual

A prepared-mind / structural-opportunity mechanism that recognizes useful off-objective information under bounded attention without exploding false opportunities.

### Disposition

`RESEARCH_ONLY / NO_CODE` until a falsifiable agent-level mechanism is clearer.

---

## A8 — operator / proof method / reusable mechanic invention (candidate child; P9/P10 overlap)

### Close parents

- **Stitch: Top-Down Synthesis for Library Learning** (Bowers et al., arXiv:2211.16605) synthesizes reusable abstractions from DSL programs.
- **LILO** (Grand et al., arXiv:2310.19791) iteratively synthesizes, compresses, and documents interpretable reusable libraries, combining LLM-guided synthesis with Stitch-style abstraction.
- DreamCoder and broader library learning / abstraction learning are mandatory parents.
- Collis et al. 2311.03893 pressures physical tool innovation.
- Current P9/P10 issues already own reusable mechanic learning and method-space invention experiments.

### Adopt

- learning a new reusable operator from repeated solution fragments is **not automatically a Jump**;
- compression/library growth can change bounded search reach even in a fixed language;
- method/operator novelty and usefulness remain external scientific coordinates.

### Possible residual

Operator invention triggered by a demonstrated **absence in the current operator closure**, rather than compression of already solved traces; requires a protected absent-operator benchmark and transfer.

### Disposition

`MAP_TO_P10/#427/#430`, not a parallel ORION core atom yet.

---

## A9 — conservative-but-transformative representation change

### Close parents

- Wang & Buehler 2606.01444 — representational-regime transitions and provenance transport.
- representation learning / abstraction / coordinate transformation / planning abstraction are mature parent fields.
- P3/P7 already own mapping, obstruction, closure/evidence transport under representation change.

### Key correction

Raw logical expressivity is too strong a universal discriminator. A conservative/definitionally equivalent representation may radically reduce derivation/search cost or expose invariants.

### Residual to test

Change in **resource-bounded reachability** under matched information, not “new language is more expressive.”

### Disposition

`USE_EXISTING P3/P7/P6 SUCCESSOR + #507 REACHABILITY WITNESSES`; no new module yet.

---

## A10 — meta-Jump / transformation-grammar revision

### Close parents

Library learning and reusable-module induction already revise the available operator library. Self-revising discovery systems revise scientific representational regimes. P9/P10 already explore learned mechanics and method-space expansion.

### Surviving hard question

Can the system identify that **its current transformation grammar itself is inadequate**, propose a genuinely new operator family that is absent from the registered closure, and earn it on fresh tasks without turning arbitrary code generation into “meta-Jump”? This is much narrower than generic self-modification.

### Disposition

`DEFER_TO_LAST RECURSION LEVEL`. It should not be implemented until lower-level operator studies can demonstrate a meaningful closure/absence witness.

---

## A11 — failure epistemology (#508/#509)

### Close parents

- failure-driven agent improvement, Reflexion-class learning, selective replay/continual memory, debugging/root-cause analysis, counterexample-guided synthesis, Bayesian/model criticism, and negative-result/replication literature all establish components.
- Sun et al. 2606.31270 explicitly converts failed computer-use trajectories into inference-time improvements.
- Trehan & Chopra 2601.03315 identify repeated autonomous-research failure modes including implementation drift, context degradation, premature success, and weak experimental taste.

### Adopt

- negative outcomes must be separated from causal/scoped failure knowledge;
- context compatibility and staleness are central because a route can become valid after representation/interface/objective change;
- failure can prune a branch **or** open a higher-order revision question.

### Residual to test

Does explicit scoped failure knowledge with `required_same` + `reopen_on_change` semantics reduce repeat dead ends without harmful negative transfer beyond raw failure summaries, selective replay, and causal diagnosis?

### Disposition

`IMPLEMENT_GENERIC SCOPED RECORD` in PR #513. No runtime policy advantage is claimed.

---

## Current atom-map consequence

After two initial research rounds, only three pilot atom proposal interfaces are implemented (#510–#512), plus generic recursive-study/failure infrastructure. The other candidate atoms are **not** converted into framework classes yet because strong parents already occupy much of their conceptual territory.

This is the intended ORION research discipline:

```text
candidate atom
-> primary-source structural parents
-> absorb / strike / baseline
-> bounded residual
-> only then code + prospective study
```

A smaller final discovery grammar is preferred over an ORION-branded synonym list.
