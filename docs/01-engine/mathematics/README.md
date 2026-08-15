# Mathematical semantics of mechanics

ORION requires each mechanic to name a candidate mathematical family/relation, but it does not force every step into one universal formalism.

The current V0 families include set-valued relations, state machines, graphs/hypergraphs, partial orders, constraint systems, multi-objective optimization, information-selection problems, measurement models, hypothesis sets, similarity retrieval, dependency reachability, set-growth/fixed-point processes, stopping rules and content addressing.

## Safe fallback

Where stronger assumptions are not justified, a mechanic remains a typed set-valued relation or identified set. ORION must not invent:

- a probability distribution merely to compute expected utility;
- independence merely to simplify uncertainty;
- differentiability/convexity merely to use an optimizer;
- a scalar score that compensates for a failed hard invariant.

A candidate formalism therefore answers "what mathematical object are we currently using to reason about this step?" It does not establish that the formalism is adequate. A known/hostile/fresh case that requires an unrepresented distinction reopens the mechanic's mathematical coordinate.

## Current provisional mapping

FRAME mechanics are initially treated as constraint/obligation-graph problems; SEARCH as information-selection/frontier problems; ABSORB as set-valued typed transformations; RECONSTRUCT as compatibility/constraint-graph synthesis; DETECT as residual/constraint problems; DIAGNOSE as set-valued hypothesis/discriminator problems; REFRAME as governed transformation/multi-objective selection; REOPEN as dependency reachability; SATURATE as set-growth/fixed-point plus stopping; cross-cutting mechanics use partial-order, measurement, context-selection, case-retrieval or content-addressing formalisms as appropriate.

These mappings are research hypotheses, not final disciplinary ownership claims.
