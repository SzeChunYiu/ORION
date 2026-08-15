# Mechanics-of-mechanics V0 research packet

**Status:** `BOUNDED_READY_FOR_V0_SUBSTRATE / GENERAL_COMPLETENESS_OPEN`

## Development atoms

1. What is the minimum universal contract for one atomic problem-solving mechanic?
2. Which questions must be asked before such a mechanic can be considered specified enough to benchmark?
3. Which of those questions can be generated without an LLM?
4. What observations/metrics must a mechanic expose to downstream mechanics and diagnosis?
5. How should success/failure executions become reusable experience?
6. Under what evidence can recurrence become a reusable guard rather than a same-context story?
7. How does the same grammar recurse over the full ORION workflow?

## RAKL knowledge recovered

The V0 design reuses rather than reinvents several RAKL lineages, pinned to source commit `70f5f7c4a6771ffd1158765b42ac9f8aee8a270f`:

- `src/rakl/method_specs.py` — typed mechanic contracts;
- `src/rakl/problem_fibre.py` — atom-conditioned compilation of knowledge, tools, episodes and failures;
- `src/rakl/experience_substrate.py` and `experience_learning.py` — immutable episodes plus governed lesson transfer;
- `docs/design/orion_mechanics_multiscale_plan/02_MECHANICS_OF_MECHANICS_ARCHITECTURE.md` — deterministic deficiency diagnosis;
- `06_DATA_MODELS_AND_APIS.md` — typed mechanic/controller candidates.

RAKL's current engineering campaign is also a negative-history source: driving the system on real workflows exposed multiple defects that document inspection alone had not surfaced, and fixes were retained with regression tests rather than erasing the failed states.

## Parent-discipline routes

The development search deliberately sampled different conceptual parents:

- recursive systems engineering / requirements verification;
- autonomic computing and monitor-analyze-plan-execute knowledge loops;
- feedback/control theory for sensors, state, effectors, objectives, stability and performance;
- rational metareasoning/value of computation for allocating reasoning effort;
- case-based reasoning and experience-aided diagnosis for retrieval/reuse of prior episodes.

These routes converge on explicit interfaces, observations, state, actions, objectives, verification and experience. They do not establish that the current dimension registry is exhaustive.

## Saturation challenge

The V0 packet is ready only for implementing a deterministic substrate. General saturation remains open because at least these routes can still change the cell grammar:

- operations research and queueing for resource/capacity mechanics;
- reliability engineering / fault diagnosis / FMEA;
- software architecture and distributed systems for runtime contracts;
- psychometrics/metrology for measurement validity;
- scientific NLP for extracting mechanic evidence from prose;
- program synthesis/formal methods for executable contract construction.

Reopen if any parent introduces a decision-relevant mechanic dimension not expressible by the current cell, or if a live task needs an LLM merely to remember an audit question that should have been mechanical.
