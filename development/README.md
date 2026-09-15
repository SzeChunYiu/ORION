# ORION development protocol

ORION development must use ORION's own epistemic principles as early as the bootstrap permits.

For a high-impact architecture/mechanic change, the default sequence is:

```text
DEVELOPMENT QUESTION
-> atomize into independently checkable fibers
-> recover incumbent RAKL/ORION mechanics and negative history
-> search relevant same-domain and parent-domain knowledge
-> reconstruct serious nearest-work donors as reusable structures
-> prove conservative embeddings before claiming an envelope
-> seek boundary/equivalence theorems or strict-separation witnesses against the strongest ideal donor product
-> deliberately challenge the current search vocabulary and discipline list
-> absorb and reconstruct a global picture
-> ask what saturation means for this exact development atom
-> ask how the search could be falsely flat
-> ask why an important domain or representation might still be missing
-> diagnose residuals / competing explanations
-> freeze the implementation hypothesis and tests
-> implement the smallest justified module
-> run known-answer + hostile tests
-> preserve failures
-> reopen research if the implementation exposes a new residual
```

Nearest work is not a citation perimeter. A strong donor must be absorbed into
the working theory: freeze its assumptions, reproduce its native result, prove
which judgments a conservative embedding preserves, and only then study the
added coordinates. An ideal information-matched donor product is the required
ceiling. Equality is a useful composition theorem; a strict residual requires a
registered separation witness and fresh falsification. Donor priority and every
historical negative remain explicit.

## High-impact implementation gate

`src/orion/development/protocol.py` makes the gate executable. A high-impact task is not ready for coding unless it has:

1. explicit atomic development questions;
2. a bounded saturation assessment over knowledge, search-universe, and formulation;
3. an explicit challenge to the saturation basis;
4. hypotheses for why prior searches could have missed relevant knowledge;
5. reopen triggers;
6. a frozen implementation hypothesis.

This is deliberately stronger than `I have read several papers`.

## Bootstrap exception

The initial commits that create the saturation/development gate necessarily precede the gate itself. They are recorded as bootstrap scaffolding, not evidence that the gate was already satisfied. Once the gate is executable and merged, new high-impact mechanics should fail closed when the development packet is missing.

## Modular code rule

Code is decomposed by information-hiding responsibility. Domain/core types, engine operators, provider ports, adapters, development governance, evaluation, and Self-ORION are separate packages. LLM/retrieval/vendor-specific code must not be embedded in the recursive solver.
