# Mechanics of mechanics

ORION treats every problem-solving step as a research object rather than a hidden implementation detail.

## Mechanic cell

For an atomic mechanic `i`, use the provisional typed object

\[
\mathcal C_i=(I_i,O_i,H_i,X_i,Y_i,A_i,F_i,\Lambda_i,J_i,U_i,R_i,\Phi_i,P_i,V_i,E_i,S_i),
\]

where:

- `I` — typed inputs and preconditions;
- `O` — typed outputs, including blocked/cannot-check outcomes;
- `H` — handoff schema to downstream mechanics;
- `X` — internal state;
- `Y` — directly observable variables and measurements;
- `A` — admissible actions/effectors;
- `F` — transition semantics;
- `Lambda` — invariants and hard constraints;
- `J` — objective and non-compensatory metric vector;
- `U` — uncertainty/calibration semantics;
- `R` — resource, cost and latency coordinates;
- `Phi` — failure signatures, falsifiers and diagnosis rules;
- `P` — persistence, provenance and identity contracts;
- `V` — verification and authority boundary;
- `E` — engineering reliability/concurrency/recovery/SLO contract;
- `S` — search-coverage, saturation and reopen semantics.

A general transition may be deterministic, stochastic or set-valued:

\[
F_i:X_i\times I_i\times A_i\to\mathcal P(X_i\times O_i).
\]

Observability is separate from state. A useful generic observation model is

\[
Y_i=h_i(X_i,\eta_i)+\epsilon_i,
\]

where `eta` records instrument/runtime state and `epsilon` records measurement noise or unresolved error.

## Metrics and downstream handoff

A step should not hide all quality/cost/reliability into one score. Its metric vector may include

\[
\mathbf m_i=(q_i,c_i,\ell_i,r_i,u_i,s_i,\ldots),
\]

for quality, coverage/cost, latency, reliability, uncertainty, safety or other step-specific coordinates. Hard gates remain non-compensatory. Scalar utility is allowed only where its calibration and tradeoff semantics are justified.

A handoff must name fields, schema, units, uncertainty, evidence/provenance and any authority that is permitted to transport. The downstream mechanic should not infer missing fields from prose.

## Mechanical question generation

`orion.mechanics.questioning` contains a fixed question-family registry. An incomplete cell mechanically emits questions such as:

- what numbers/signals can be observed here?
- what state is latent versus explicit?
- what mathematical relation maps input/action/state to output?
- what metric vector must be passed onward?
- what failure signatures and falsifiers distinguish bad behavior?
- what must be stored and what can be recomputed?
- what parent discipline treats this operation as a canonical problem?
- what would make apparent saturation false?

The question registry is deliberately independent of an LLM. An LLM or external tool can help answer the questions, but cannot silently omit them.

A universal envelope is not a step-specific answer. Generic verification, runtime observation, handoff, state, lifecycle, failure, mathematical and dependency plans are marked as provisional dimensions, so the corresponding mechanic question remains open until a step-specific contract or justified waiver replaces the baseline. Containment is not encoded as a dependency back-edge; external runtime contracts are stored separately from mechanic-to-mechanic prerequisites. This prevents scaffolding from silently manufacturing completeness or graph cycles.

The current measured frontier contains 59 reachable mechanics and 1,298 open typed questions: all 22 registered dimensions remain open for all 59 mechanics. Unknown child/dependency references and containment, dependency and mixed-edge cycle counts are all zero. This is an observed workload frontier, not evidence of scientific completeness or a target to inflate.

`orion.mechanics.research` mechanically turns prioritized open questions into provider-neutral `SearchQuery` objects. V0 uses a fixed auditable policy; later value-of-computation policies must beat it under frozen evaluation rather than replacing it by intuition.

## Recursion

Child mechanics receive the same audit grammar. Containment and execution-dependency graphs are audited separately and as a combined graph. A parent cannot be called bounded-ready while an unknown child, unknown dependency, containment cycle, dependency cycle or mixed-edge cycle remains hidden. This makes the workflow itself recursively inspectable.

## Boundary

A filled cell is ready for benchmarking, not automatically scientifically valid. Real performance, transfer, source coverage and verification remain empirical obligations.
