# ORION-QG QG-34 — exact adaptive probe tree above joint bulk+spectrum summaries

Date: 2026-08-22
Issue: SzeChunYiu/ORION#924
Parent programme: #740
Direct earned parent: QG-32 #911.

## Status

**PROSPECTIVE ADAPTIVE FRONTIER. FROZEN BEFORE ANY ADAPTIVE DEPTH OUTCOME.**

QG-32 certifies that five fixed indexed probes `[18,68,101,181,139]` suffice after the exact joint bulk+spectrum summaries, but explicitly withholds fixed-minimum and adaptive-tree authority.

QG-34 asks:

> If each next indexed probe may depend on prior exact probe outcomes, what is the exact minimum worst-case number of additional probes required to identify the 715-way indexed local-response state once the joint bulk+spectrum class is known?

No depth is predicted.

## Frozen universe

Reconstruct independently from QG-32 generic primitives:
- 715 orbit representatives;
- 384 indexed response coordinates;
- 92 joint bulk+spectrum classes with size histogram `{1:7,2:22,3:6,4:6,6:25,8:2,12:14,24:8,48:2}`;
- exact integer response matrix `K[o,p]`.

Each initial joint class is a state `S`. For a probe `p`, outcomes partition `S` by exact equality of `K[o,p]`.

## Exact minimax definition

`D(S)=0` for `|S|<=1`.

For non-singleton `S`:

`D(S)=1+min_p max_v D({o in S: K[o,p]=v})`,

ignoring probes that do not split `S`.

Primary object:

`D_* = max_{S in initial joint classes} D(S)`.

## Production exact method

For every initial class:
1. encode subsets as local integer bitmasks;
2. precompute probe outcome masks and collapse probes inducing identical full-class partitions;
3. use memoized depth-feasibility `CAN(S,d)` for `d=0..4`;
4. use only sound pruning: singleton terminal, no-depth terminal, response-arity information bound, duplicate restricted partitions, and child-size capacity under the class's maximum response arity;
5. if no `d<=4` succeeds, use QG-32's already-certified five fixed probes as the constructive `d<=5` upper bound;
6. record the first exact successful depth and canonical first successful probe choices.

Serialize:
- exact depth for all 92 initial classes;
- depth histogram by class and by orbit mass;
- worst depth and worst-class indices/sizes;
- a canonical complete policy tree for the first worst class;
- DP call/cache/prune statistics.

## Independent generic verification

Generic ORION must reconstruct the response matrix from the phase-free F2^2/F3 primitives without importing QG-34 production results, encode states as sorted tuples/frozensets rather than local integer masks, and independently recompute the minimum depth for every initial class using a distinct probe ordering and memo layout.

It must also replay the serialized worst-class policy and verify:
- every internal probe splits its state;
- every edge is labeled by the exact response value;
- every leaf contains exactly one orbit;
- path depth never exceeds the claimed class depth;
- no depth smaller than the claimed depth is feasible for each class.

## Native ORION-Q authority

May authorize only:
- exact adaptive minimax depth on the frozen 715-orbit / 92-summary-class observation problem;
- exact class-depth histogram;
- the serialized adaptive policy as a domain-specific active-verification operator.

Must keep false:
- fixed-probe minimum unless separately earned by QG-32c;
- adaptive-vs-fixed minimum advantage unless an exact fixed minimum is separately bound;
- full finite-n optimum identification depth;
- hardware measurement minimum;
- global state minimality;
- novelty authority;
- physical quantum advantage.

If `D_* < 5`, QG-34 may state only `ADAPTIVE_DEPTH_BELOW_QG32_CERTIFIED_FIXED_BASIS_LENGTH`; this is not an adaptivity-vs-optimal-fixed separation until an exact fixed minimum is independently earned.

## Workflow

Require:
- production/generic/native GREEN;
- deterministic byte-identical production replay;
- self-consistent depth/policy tamper rejected by generic verifier;
- hard authority-boundary assertion.

## Honest terminals

- `QG34_EXACT_MINIMAX_ADAPTIVE_PROBE_DEPTH_MACHINE_CHECKED`
- `QG34_ADAPTIVE_POLICY_UPPER_BOUND_ONLY`
- `QG34_CANNOT_CHECK`

## Donor subtraction

Decision-tree minimization, active feature acquisition and minimax identification are donor methods. Candidate value is only the exact TARE-specific post-summary identification tree and its scoped ORION-Q active-verification consequence.