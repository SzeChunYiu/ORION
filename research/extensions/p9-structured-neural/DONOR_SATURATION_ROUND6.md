# P9 donor saturation — round 6 state abstraction / sufficiency pressure

Status: **MATERIAL CHANGE TO CLAIM/BASELINE MAP**.  Search vocabulary: task abstraction, sufficient state, bisimulation, preserved behavior, causal state abstraction.

## Building Minimal and Reusable Causal State Abstractions for Reinforcement Learning

**Primary source:** Wang et al., 2024, arXiv:2401.12497.

### Essence

Causal Bisimulation Modeling learns causal relationships in environment dynamics/rewards and derives minimal task-specific state abstractions retaining variables needed for a task; the causal dynamics model can be reused across tasks. The paper reports strong abstraction recovery/sample-efficiency results in its RL domains.

### P9 consequence

P9 may not claim the following as broad novelty:

- that a learned representation should retain only task-relevant variables;
- that causal structure can support reusable minimal state abstractions;
- that state abstraction can improve sample efficiency.

### Disposition

`ADOPT task-relevant-abstraction pressure + BASELINE` under A7/A10 if P9 later learns/selects state coordinates rather than receiving them explicitly.

The current D0/D1 programme does **not** yet learn the abstraction itself; it evaluates prospectively declared coordinate projections. Any future P9 claim about learned coordinate selection must compare against causal/bisimulation abstraction methods.

## Compositional Behavioral Semantics for State Abstraction in Reinforcement Learning

**Primary source:** Zhang, Luo & Baltieri, 2026, arXiv:2606.25357.

### Essence

Provides a compositional framework for behavioral structures under state abstraction, including preservation/transfer between abstract and concrete systems from local one-step semantics.

### P9 consequence

This strengthens the formal-donor boundary with P6/#463. P9 cannot claim `formal preservation-aware abstraction` broadly. P9's role, if any, is empirical learning/evaluation over already versioned structural coordinates; formal preservation semantics remain donor/P6 territory unless a distinct theorem is proved.

### Disposition

`FORMAL DONOR + CLAIM CONTRACTION`, primarily routed to #463/P6 and used as pressure on any P9 learned abstraction proposal.

## Round-6 impact

The candidate P9 residual narrows again:

> P9 may establish that particular **prospectively declared, evidence-bound ORION coordinates** are necessary/useful on frozen reasoning/transfer tasks, and may learn over them. It does not thereby own task-relevant state abstraction, causal sufficiency, bisimulation, or preservation theory.

If M1/D1 show simple models and exact inference exhaust the current discriminators, the correct terminal is to narrow/terminate neural-architecture claims rather than add complexity in search of novelty.

## Saturation counter

- Round 5: material — analogical cross-domain structural transfer.
- Round 6: **material** — causal/minimal state abstraction and preservation-theory pressure.
- Consecutive no-material-change rounds: **0/2**.

P9 saturation remains OPEN.
