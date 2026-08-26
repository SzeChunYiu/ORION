# Introduction

Test-time computation has become an explicit design variable in modern reasoning systems. Systems allocate more tokens, samples, search nodes, verifier calls or iterative refinement to difficult instances. Recent work develops bandit, constrained-policy and learned adaptive allocation strategies, reinforcing a general lesson: uniform inference budgets waste computation when item difficulty is heterogeneous.

But difficulty itself has more than one source. Some tasks are difficult because the relevant structure is poorly exposed in the current representation. Others are difficult because substantial search or reasoning remains even after the right structure is visible. If a system spends all marginal budget on reasoning in an access-limited task, it reasons harder over the wrong state. If it spends all marginal budget on state construction in a reasoning-limited task, it repeatedly reorganizes information that was already accessible.

ORION-22 asks:

> **Under one matched total budget, when should a system spend computation changing state, when should it spend computation reasoning over state, and can a prospective policy learn or exploit the difference?**

The system is modeled as

`raw/current state -> optional state construction -> downstream reasoning/search -> verified outcome`.

The paper makes four contributions.

1. **Two-axis inference formulation.** State construction and downstream reasoning are symmetric budgeted actions rather than free preprocessing plus paid reasoning.
2. **A strict comparator contract.** The joint policy must beat both adaptive-state-only and adaptive-reasoning-only policies at identical total resources, not merely a fixed baseline.
3. **A comparator-capability correction.** The protected run is reported with a
   later hostile adjudication showing that signal count and permitted allocations
   varied together.
4. **An equal-action successor.** P12B holds the four actions and budget fixed,
   varies only visible signals, and reports family-block uncertainty.

P12A's superiority interpretation is withheld by its comparison-validity
adjudication. P12B supplies the stronger controlled contract: equal total
budget, equal action capability, and only then a variation in available
signals. The current bounded authority is the equal-action
signal-complementarity result.
   varied together; a capability-matched P12B is therefore required.

The historical result is intentionally controlled and exactly reproducible, but
its superiority interpretation is withheld by
`P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json`. Active terminal:
`P12A_SUPERIORITY_AUTHORITY_WITHHELD`. Its current value is to expose the stronger
contract a successor must satisfy: equal total budget, equal action capability,
and only then a variation in available signals.
