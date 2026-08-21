# ORION-QN VS1 S1A implementation packet v1

Status: **FROZEN BEFORE RESULT-BEARING S1A CODE/OUTCOMES**  
Programme: `SzeChunYiu/ORION#734`  
Parent protocol: `research/extensions/orion-qn/VS1_P6_P2_P4_LOCAL_SIMULATION_PROTOCOL_V1.md`  
Frozen programme base: `d7312bc7fda4a84490acbc8b7964904fbedb3a93`  
Implementation lane: `shadow/orion-qn-q0-q1-foundation`

## 1. Atomic research question

For the frozen S1A single-marked finite search family, can ORION-QN execute a genuine Grover circuit on a pinned local simulator, return a candidate through an actual computational-basis measurement path, independently re-check that candidate against the original classical predicate, and issue only the bounded `QUANTUM_QUERY_ADVANTAGE_ONLY` terminal when the same-information query comparison supports it?

The target is **not** local wall-clock speedup and not a physical-QPU claim.

## 2. Pinned simulator environment

Result-bearing GitHub Actions must install exactly:

```text
Python 3.12
qiskit==2.5.1
qiskit-aer==0.17.2
```

These versions are frozen before S1A result aggregation. Any backend/package drift reopens the `QBackendIdentity` receipt and cannot silently reuse prior results.

Backend identity:

```text
backend_family = qiskit-aer
backend_name = AerSimulator
method = statevector
noise_model = none
execution_mode = LOCAL_SIMULATION
```

Simulator runtime is engineering evidence only.

## 3. Frozen size ladder

Exactly the parent protocol ladder:

```text
n = 3, 4, 5, 6, 7, 8, 9, 10
N = 2^n
```

No result-bearing larger `n` is added in this packet.

## 4. Frozen subject generator

For every `n`:

1. include marked index `0`;
2. include marked index `N-1`;
3. create `random.Random(734000 + n)`;
4. sample without replacement exactly six indices from `range(1, N-1)`;
5. sort the six sampled indices;
6. subject order is `[0, N-1] + sorted(sample)`.

For `n=3`, the six interior positions exhaust the interior set. This still gives eight distinct cases.

Case identity:

```text
S1A-n{n}-case{case_index}-marked{marked_index}
```

No case may be removed because its result is inconvenient.

## 5. Grover iteration rule

For one marked item in `N` candidates:

```text
theta = asin(1 / sqrt(N))
p_r = sin((2*r + 1) * theta)^2
```

Choose the integer `r >= 0` that maximizes `p_r` among the two nearest integers to:

```text
pi / (4*theta) - 1/2
```

Tie-break toward the smaller `r`.

The implementation must independently recompute the analytic probability rather than trusting a simulator-provided PASS flag.

## 6. Oracle semantics

The admitted classical predicate is exactly:

```text
f(x) = 1 iff x == marked_index
```

The quantum phase oracle must be constructed from that declared `marked_index` and may not inspect an evaluator-only answer field.

The circuit must record one oracle call per Grover iteration. The diffusion operator is not relabeled as an oracle call.

This packet permits a direct known-answer circuit construction because S1A is a semantic/query-model fixture. It does **not** permit treating direct hidden-gold matrix construction as an end-to-end resource baseline.

## 7. Measurement and retry contract

Result-bearing candidate selection uses actual computational-basis measurement, not `statevector.argmax`.

For each case:

```text
max_attempts = 5
attempt seed = 73400000 + n*1000 + case_index*10 + attempt_index
shots per attempt = 1
```

After every measured candidate:

1. decode the measured bit string to an integer;
2. independently call the original classical predicate;
3. if it passes, stop and return the candidate;
4. if it fails, run a fresh circuit attempt under the next frozen seed;
5. after five failed attempts, retain the failure as a result; do not substitute the known marked index.

Quantum query coordinates for the result-bearing execution are therefore:

```text
oracle_calls = grover_iterations * measured_attempts
verification_predicate_calls = measured_attempts
measurement_shots = measured_attempts
```

The verification predicate calls are reported separately and are not silently added to or removed from the Grover oracle-query coordinate.

## 8. Exact probability conformance

Separately from candidate selection, execute an exact statevector simulation of the pre-measurement circuit.

Require:

```text
abs(simulated_marked_probability - analytic_marked_probability) <= 1e-10
normalization_error <= 1e-10
```

This is semantic simulator verification, not physical-QPU evidence.

## 9. Classical baselines

### C1 ordered exhaustive

Scan `x = 0,1,...,N-1` until the predicate passes.

Record exact predicate calls `marked_index + 1`.

### C2 random without replacement

For each case use:

```text
random.Random(73500000 + n*1000 + case_index)
```

Shuffle `range(N)` once and scan until marked item is reached. Record exact calls.

The random order is frozen independently of the quantum measurement seeds.

## 10. Query-advantage adjudication

Per case, no positive terminal is forced. Per `n`, compute the mean across all eight frozen cases of:

- quantum oracle calls;
- C1 predicate calls;
- C2 predicate calls.

A size-level S1A result may emit `QUANTUM_QUERY_ADVANTAGE_ONLY` only when:

```text
mean_quantum_oracle_calls < mean_C1_calls
and
mean_quantum_oracle_calls < mean_C2_calls
```

and all semantic/access/measurement/P4 reconstruction gates are green.

Otherwise use `QUANTUM_FEASIBLE_NO_ADVANTAGE` for that size if the circuit is semantically valid.

The campaign-level report must preserve every size-level terminal; it may not average away a small-size classical win.

## 11. Independent P4 reconstruction

The reconstruction path receives serialized case records and independently verifies at least:

- case identity matches `n`, `N`, case index and marked index;
- returned candidate is in range;
- returned candidate satisfies the declared predicate;
- Grover iteration count equals the frozen analytic rule;
- oracle-call count equals `iterations * attempts`;
- measurement shots equal attempts;
- analytic probability is recomputable from `N` and iterations;
- statevector probability residual is within tolerance;
- backend identity matches this packet;
- evidence mode is `LOCAL_SIMULATION`;
- no terminal exceeds the Q1 local-simulation claim ceiling.

The reconstructor may not import an executor-authored `passed=true` field.

## 12. Harness execution

The result-bearing CI lane must execute S1A through `orion-research-harness` local `PYTHON` capability with process tools explicitly enabled.

Required chain:

```text
ResearchWorkspace.initialize(..., allow_process_tools=True)
-> deterministic PYTHON capability request
-> orion-harness-local result receipt
-> stdout JSON campaign result
-> independent reconstruction
-> uploaded workspace + report artifacts
```

The local process receipt must preserve `sandboxed: false` exactly as the harness reports it. That field is an orchestration/security fact, not a scientific defect.

The harness request/result digest binds the executed code payload to the result; it is tamper evidence, not a cryptographic signature or independent scientific review.

## 13. Current-literature hostile boundary absorbed before implementation

Current donor evidence sharpens the test:

- Brehm & Weggemans, *Quantum* 10, 1975 (2026), show that practical Grover/backtracking advantage in structured k-SAT can collapse when problem structure and T-count are included. This blocks any inference from S1A unstructured query advantage to structured/end-to-end discovery advantage.
- Li et al., arXiv:2605.21380 (2026), explicitly treat quantum-oracle resource modelling/optimization as a first-class problem. This reinforces the later S3 rule that coherent oracle construction cannot be hidden behind a unit-cost query abstraction.
- Prokop, Wallden & Joseph, arXiv:2402.13895, give concrete Grover-oracle resource accounting for SVP, again separating the generic square-root query result from implementation cost.

Therefore S1A is deliberately a semantic/query-model tranche. S2-S4 remain mandatory even if every S1A size earns a query-only terminal.

## 14. Hostile RED cases for this implementation

At minimum tests must fail closed for:

1. candidate selected by maximum statevector amplitude instead of measurement;
2. wrong marked item encoded in the oracle;
3. executor record claims fewer oracle calls than `iterations * attempts`;
4. backend version/identity mismatch;
5. tampered analytic probability;
6. candidate does not satisfy original predicate;
7. a local-simulation result attempts projected-FT or end-to-end physical terminal;
8. classical baseline uses a different marked item/problem identity;
9. five failed measured attempts are replaced by hidden known answer;
10. harness process receipt is omitted from a claimed harness execution.

## 15. Claim ceiling

This packet can support only:

```text
QUANTUM_QUERY_ADVANTAGE_ONLY
QUANTUM_FEASIBLE_NO_ADVANTAGE
CLASSICAL_PARENT_SUFFICIENT
CANNOT_CHECK_ACCESS_MODEL
INVALID_COMPARISON
```

It cannot support physical speedup, projected FT advantage, novelty, P8 authority, or publication readiness.
